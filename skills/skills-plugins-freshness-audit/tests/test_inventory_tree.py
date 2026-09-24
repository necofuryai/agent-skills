from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "inventory_tree.py"


def run_inventory(root: Path, *extra_args: str) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, str(SCRIPT), str(root), *extra_args],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


class InventoryTreeTest(unittest.TestCase):
    def test_identical_trees_at_different_roots_have_identical_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            parent = Path(temporary_directory)
            roots = [parent / "first", parent / "second"]
            for root in roots:
                root.mkdir()
                (root / "nested").mkdir()
                (root / "nested" / "SKILL.md").write_bytes(b"same\n")
                os.symlink("nested/SKILL.md", root / "entrypoint")

            self.assertEqual(
                run_inventory(roots[0], "--hash-content"),
                run_inventory(roots[1], "--hash-content"),
            )

    def test_directory_permission_is_diagnostic_not_tree_content(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            nested = root / "nested"
            nested.mkdir()
            (nested / "SKILL.md").write_text("same\n")

            initial = run_inventory(root, "--hash-content")
            nested.chmod(0o700)
            changed_permission = run_inventory(root, "--hash-content")

            self.assertEqual(initial["tree_sha256"], changed_permission["tree_sha256"])
            initial_nested = next(
                entry for entry in initial["entries"] if entry["path"] == "nested"
            )
            changed_nested = next(
                entry
                for entry in changed_permission["entries"]
                if entry["path"] == "nested"
            )
            self.assertNotEqual(initial_nested["mode"], changed_nested["mode"])

    def test_inventory_is_deterministic_and_preserves_comparison_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "bin").mkdir()
            executable = root / "bin" / "audit.sh"
            executable.write_bytes(b"#!/bin/sh\nprintf ok\\n\n")
            executable.chmod(0o755)
            (root / "SKILL.md").write_bytes(b"---\nname: fixture\n---\n")
            os.symlink("SKILL.md", root / "entrypoint")
            (root / ".git").mkdir()
            (root / ".git" / "HEAD").write_text("ref: refs/heads/main\n")

            first = run_inventory(root, "--hash-content")
            second = run_inventory(root, "--hash-content")

            self.assertEqual(first, second)
            self.assertEqual(first["root"], ".")
            entries = {entry["path"]: entry for entry in first["entries"]}
            self.assertEqual(
                list(entries), ["SKILL.md", "bin", "bin/audit.sh", "entrypoint"]
            )
            self.assertNotIn(".git", entries)
            self.assertEqual(entries["bin/audit.sh"]["type"], "file")
            self.assertEqual(entries["bin/audit.sh"]["git_mode"], "100755")
            self.assertEqual(
                entries["SKILL.md"]["content_sha256"],
                hashlib.sha256(b"---\nname: fixture\n---\n").hexdigest(),
            )
            self.assertEqual(entries["entrypoint"]["type"], "symlink")
            self.assertEqual(entries["entrypoint"]["symlink_target"], "SKILL.md")
            self.assertFalse(entries["entrypoint"]["symlink_broken"])
            self.assertEqual(
                entries["entrypoint"]["content_sha256"],
                hashlib.sha256(b"SKILL.md").hexdigest(),
            )

    def test_content_mode_symlink_and_exclusion_changes_affect_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            content = root / "SKILL.md"
            content.write_text("one\n")
            os.symlink("SKILL.md", root / "alias")
            ignored = root / "generated"
            ignored.mkdir()
            (ignored / "noise").write_text("first\n")

            initial = run_inventory(
                root, "--hash-content", "--exclude-name", "generated"
            )
            (ignored / "noise").write_text("second\n")
            ignored_change = run_inventory(
                root, "--hash-content", "--exclude-name", "generated"
            )
            self.assertEqual(initial, ignored_change)

            content.write_text("two\n")
            content_change = run_inventory(
                root, "--hash-content", "--exclude-name", "generated"
            )
            self.assertNotEqual(initial["tree_sha256"], content_change["tree_sha256"])

            content.chmod(0o755)
            mode_change = run_inventory(
                root, "--hash-content", "--exclude-name", "generated"
            )
            self.assertNotEqual(
                content_change["tree_sha256"], mode_change["tree_sha256"]
            )

            (root / "alias").unlink()
            os.symlink("missing", root / "alias")
            link_change = run_inventory(
                root, "--hash-content", "--exclude-name", "generated"
            )
            self.assertNotEqual(mode_change["tree_sha256"], link_change["tree_sha256"])
            alias = next(
                entry for entry in link_change["entries"] if entry["path"] == "alias"
            )
            self.assertEqual(alias["symlink_target"], "missing")
            self.assertTrue(alias["symlink_broken"])

    def test_content_hashing_requires_opt_in_and_skips_sensitive_names(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "SKILL.md").write_text("instructions\n")
            (root / ".env").write_text("SECRET=value\n")

            metadata_only = run_inventory(root)
            metadata_entries = {
                entry["path"]: entry for entry in metadata_only["entries"]
            }
            self.assertEqual(metadata_only["content_policy"], "metadata-only")
            self.assertFalse(metadata_only["content_complete"])
            self.assertEqual(metadata_only["unhashed_file_count"], 2)
            self.assertIsNone(metadata_entries["SKILL.md"]["content_sha256"])
            self.assertEqual(
                metadata_entries["SKILL.md"]["content_status"], "metadata-only"
            )

            hashed = run_inventory(root, "--hash-content")
            hashed_entries = {entry["path"]: entry for entry in hashed["entries"]}
            self.assertEqual(hashed_entries["SKILL.md"]["content_status"], "hashed")
            self.assertEqual(
                hashed_entries[".env"]["content_status"],
                "skipped-sensitive-name",
            )
            self.assertIsNone(hashed_entries[".env"]["content_sha256"])
            self.assertFalse(hashed["content_complete"])
            self.assertEqual(hashed["unhashed_file_count"], 1)

            explicitly_allowed = run_inventory(
                root,
                "--hash-content",
                "--allow-content-path",
                ".env",
            )
            allowed_entries = {
                entry["path"]: entry for entry in explicitly_allowed["entries"]
            }
            self.assertEqual(allowed_entries[".env"]["content_status"], "hashed")
            self.assertIsNotNone(allowed_entries[".env"]["content_sha256"])
            self.assertTrue(explicitly_allowed["content_complete"])
            self.assertEqual(explicitly_allowed["unhashed_file_count"], 0)

    def test_compound_sensitive_names_and_sensitive_directories_are_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            references = root / "skills" / "sentry-fix-stack-traces" / "references"
            references.mkdir(parents=True)
            (references / "auth-token.md").write_text("placeholder-only\n")
            private_notes = root / "secrets" / "notes.md"
            private_notes.parent.mkdir()
            private_notes.write_text("placeholder-only\n")
            (root / "SKILL.md").write_text("safe instructions\n")

            result = run_inventory(root, "--hash-content")
            entries = {entry["path"]: entry for entry in result["entries"]}
            for relative_path in (
                "skills/sentry-fix-stack-traces/references/auth-token.md",
                "secrets/notes.md",
            ):
                self.assertEqual(
                    entries[relative_path]["content_status"],
                    "skipped-sensitive-name",
                )
                self.assertIsNone(entries[relative_path]["content_sha256"])
            self.assertEqual(entries["SKILL.md"]["content_status"], "hashed")
            self.assertFalse(result["content_complete"])
            self.assertEqual(result["unhashed_file_count"], 2)

    def test_explicit_content_skip_is_checked_before_hashing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "SKILL.md").write_text("safe instructions\n")
            (root / "unexpected-sensitive-reference.md").write_text(
                "placeholder-only\n"
            )

            result = run_inventory(
                root,
                "--hash-content",
                "--skip-content-path",
                "unexpected-sensitive-reference.md",
            )
            entries = {entry["path"]: entry for entry in result["entries"]}
            self.assertEqual(
                entries["unexpected-sensitive-reference.md"]["content_status"],
                "skipped-explicit-path",
            )
            self.assertIsNone(
                entries["unexpected-sensitive-reference.md"]["content_sha256"]
            )
            self.assertFalse(result["content_complete"])

            for extra_args in (
                ("--skip-content-path", "missing.md"),
                (
                    "--skip-content-path",
                    "unexpected-sensitive-reference.md",
                    "--allow-content-path",
                    "unexpected-sensitive-reference.md",
                ),
            ):
                completed = subprocess.run(
                    [sys.executable, str(SCRIPT), str(root), "--hash-content", *extra_args],
                    capture_output=True,
                    text=True,
                )
                self.assertNotEqual(completed.returncode, 0)
                self.assertEqual(completed.stdout, "")


if __name__ == "__main__":
    unittest.main()
