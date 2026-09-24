#!/usr/bin/env python3
"""Emit a deterministic JSON inventory for a local directory tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path
from typing import Any


DEFAULT_EXCLUDES = frozenset({".DS_Store", ".git", ".hg", ".svn", "__pycache__"})
SENSITIVE_BASENAMES = frozenset(
    {
        ".env",
        ".envrc",
        "credentials",
        "credentials.json",
        "id_ed25519",
        "id_rsa",
        "private_key",
        "secrets",
        "secrets.json",
        "token",
        "tokens.json",
    }
)
SENSITIVE_SUFFIXES = (".key", ".p12", ".pem", ".pfx")
SENSITIVE_NAME_WORDS = frozenset(
    {"credential", "credentials", "secret", "secrets", "token", "tokens"}
)
CHUNK_SIZE = 1024 * 1024


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def entry_type(mode: int) -> str:
    if stat.S_ISREG(mode):
        return "file"
    if stat.S_ISDIR(mode):
        return "directory"
    if stat.S_ISLNK(mode):
        return "symlink"
    if stat.S_ISFIFO(mode):
        return "fifo"
    if stat.S_ISSOCK(mode):
        return "socket"
    if stat.S_ISBLK(mode):
        return "block-device"
    if stat.S_ISCHR(mode):
        return "character-device"
    return "unknown"


def git_mode(mode: int) -> str | None:
    if stat.S_ISREG(mode):
        return "100755" if mode & 0o111 else "100644"
    if stat.S_ISDIR(mode):
        return "040000"
    if stat.S_ISLNK(mode):
        return "120000"
    return None


def sensitive_name(relative_path: str) -> bool:
    for component in Path(relative_path).parts:
        name = component.casefold()
        if (
            name in SENSITIVE_BASENAMES
            or name.startswith(".env.")
            or name.endswith(SENSITIVE_SUFFIXES)
        ):
            return True
        words = re.split(r"[-_.]+", name)
        if any(word in SENSITIVE_NAME_WORDS for word in words):
            return True
        if any(
            words[index : index + 2] in (["private", "key"], ["api", "key"])
            for index in range(len(words) - 1)
        ):
            return True
    return False


def describe(
    path: Path,
    relative_path: str,
    mode: int,
    *,
    hash_content: bool,
    allowed_content_paths: set[str],
    skipped_content_paths: set[str],
) -> dict[str, Any]:
    kind = entry_type(mode)
    target: str | None = None
    content_hash: str | None = None
    content_status: str | None = None
    symlink_broken: bool | None = None

    if kind == "file":
        if not hash_content:
            content_status = "metadata-only"
        elif relative_path in skipped_content_paths:
            content_status = "skipped-explicit-path"
        elif sensitive_name(relative_path) and relative_path not in allowed_content_paths:
            content_status = "skipped-sensitive-name"
        else:
            content_hash = sha256_file(path)
            content_status = "hashed"
    elif kind == "symlink":
        target = os.readlink(path)
        content_hash = hashlib.sha256(os.fsencode(target)).hexdigest()
        content_status = "link-target-hashed"
        symlink_broken = not path.exists()

    return {
        "content_sha256": content_hash,
        "content_status": content_status,
        "git_mode": git_mode(mode),
        "mode": f"{stat.S_IMODE(mode):04o}",
        "path": relative_path,
        "symlink_broken": symlink_broken,
        "symlink_target": target,
        "type": kind,
    }


def inventory(
    root: Path,
    excluded_names: set[str],
    *,
    hash_content: bool,
    allowed_content_paths: set[str],
    skipped_content_paths: set[str],
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []

    def walk(directory: Path, relative_directory: Path) -> None:
        try:
            children = sorted(os.scandir(directory), key=lambda item: item.name)
        except OSError as error:
            raise RuntimeError(f"cannot scan {directory}: {error}") from error

        for child in children:
            if child.name in excluded_names:
                continue

            path = Path(child.path)
            relative = (relative_directory / child.name).as_posix()
            try:
                metadata = child.stat(follow_symlinks=False)
            except OSError as error:
                raise RuntimeError(f"cannot stat {path}: {error}") from error

            entries.append(
                describe(
                    path,
                    relative,
                    metadata.st_mode,
                    hash_content=hash_content,
                    allowed_content_paths=allowed_content_paths,
                    skipped_content_paths=skipped_content_paths,
                )
            )
            if stat.S_ISDIR(metadata.st_mode):
                walk(path, relative_directory / child.name)

    walk(root, Path())
    return entries


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Emit a deterministic JSON inventory without following symlinks."
    )
    parser.add_argument("root", type=Path, help="directory to inventory")
    parser.add_argument(
        "--exclude-name",
        action="append",
        default=[],
        metavar="NAME",
        help="exclude an additional basename anywhere in the tree (repeatable)",
    )
    parser.add_argument(
        "--hash-content",
        action="store_true",
        help="hash regular-file content after a metadata-only preflight",
    )
    parser.add_argument(
        "--allow-content-path",
        action="append",
        default=[],
        metavar="RELATIVE_PATH",
        help=(
            "hash one exact relative path even when its name looks sensitive; "
            "requires explicit authorization for that file and purpose"
        ),
    )
    parser.add_argument(
        "--skip-content-path",
        action="append",
        default=[],
        metavar="RELATIVE_PATH",
        help="skip hashing one exact regular file found during metadata preflight",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.absolute()
    if not root.is_dir():
        print(f"error: root is not a directory: {args.root}", file=sys.stderr)
        return 2

    excluded_names = set(DEFAULT_EXCLUDES) | set(args.exclude_name)
    allowed_content_paths = {Path(path).as_posix() for path in args.allow_content_path}
    skipped_content_paths = {Path(path).as_posix() for path in args.skip_content_path}
    if (allowed_content_paths or skipped_content_paths) and not args.hash_content:
        print("error: content-path options require --hash-content", file=sys.stderr)
        return 2
    if allowed_content_paths & skipped_content_paths:
        print("error: a path cannot be both allowed and skipped", file=sys.stderr)
        return 2
    try:
        if skipped_content_paths:
            metadata_entries = inventory(
                root,
                excluded_names,
                hash_content=False,
                allowed_content_paths=set(),
                skipped_content_paths=set(),
            )
            regular_files = {
                entry["path"] for entry in metadata_entries if entry["type"] == "file"
            }
            missing = skipped_content_paths - regular_files
            if missing:
                print(
                    "error: skipped content paths are not regular files: "
                    + ", ".join(sorted(missing)),
                    file=sys.stderr,
                )
                return 2
        entries = inventory(
            root,
            excluded_names,
            hash_content=args.hash_content,
            allowed_content_paths=allowed_content_paths,
            skipped_content_paths=skipped_content_paths,
        )
    except (OSError, RuntimeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    # Compare the fields represented by a Git tree plus explicit link health.
    # Raw POSIX directory permissions are diagnostic output, not tracked content.
    comparison_entries = [
        {
            key: entry[key]
            for key in (
                "content_sha256",
                "content_status",
                "git_mode",
                "path",
                "symlink_broken",
                "symlink_target",
                "type",
            )
        }
        for entry in entries
    ]
    canonical_entries = json.dumps(
        comparison_entries, ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")
    result = {
        "algorithm": "sha256",
        "content_complete": all(
            entry["type"] != "file" or entry["content_status"] == "hashed"
            for entry in entries
        ),
        "content_policy": "hash-content" if args.hash_content else "metadata-only",
        "entries": entries,
        "entry_count": len(entries),
        "excluded_names": sorted(excluded_names),
        "root": ".",
        "schema_version": 4,
        "skipped_content_paths": sorted(skipped_content_paths),
        "tree_sha256": hashlib.sha256(canonical_entries).hexdigest(),
        "unhashed_file_count": sum(
            entry["type"] == "file" and entry["content_status"] != "hashed"
            for entry in entries
        ),
    }
    json.dump(result, sys.stdout, ensure_ascii=True, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
