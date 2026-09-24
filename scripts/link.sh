#!/usr/bin/env bash
# Link each skill in this repo into the user-level skill directories that Claude Code and Codex read:
#   ~/.agents/skills/<name>  Codex, and other clients that follow the ~/.agents/skills convention
#   ~/.claude/skills/<name>  Claude Code, which does not read ~/.agents/skills
# The links point back into this working tree, so an edit made from either tool is an edit to the repo.
# A real directory, or a link that points somewhere else, is never replaced; it is reported instead.
#
# Usage: scripts/link.sh [--check] [--prune]
#   --check  report only; exit 1 if a link is missing, blocked or dangling
#   --prune  remove links in those directories that point into this repo but whose skill is gone
set -euo pipefail

repo=$(cd "$(dirname "$0")/.." && pwd -P)
check=0
prune=0
for arg in "$@"; do
  case $arg in
    --check) check=1 ;;
    --prune) prune=1 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

# Skills named in this file (one per line, # for comments) are linked for Codex only.
exclude_file="$repo/scripts/claude-exclude.txt"
claude_excluded() {
  [ -f "$exclude_file" ] && grep -vE '^[[:space:]]*(#|$)' "$exclude_file" | grep -Fxq "$1"
}

# Both target directories sit two levels below $HOME, so the link is relative when the repo is under $HOME.
home=$(cd "$HOME" && pwd -P)
case $repo in
  "$home"/*) base="../../${repo#"$home"/}/skills" ;;
  *) base="$repo/skills" ;;
esac

status=0

link_one() { # $1 = target directory, $2 = skill name
  local dir=$1 name=$2
  local want="$base/$name" path="$dir/$name" have
  if [ -L "$path" ]; then
    have=$(readlink "$path")
    if [ "$have" = "$want" ]; then
      echo "ok        $path"
    else
      echo "BLOCKED   $path -> $have (points elsewhere)"
      status=1
    fi
    return
  fi
  if [ -e "$path" ]; then
    echo "BLOCKED   $path (a real directory or file is in the way)"
    status=1
    return
  fi
  if [ "$check" -eq 1 ]; then
    echo "MISSING   $path"
    status=1
    return
  fi
  mkdir -p "$dir"
  ln -s "$want" "$path"
  echo "linked    $path -> $want"
}

for skill in "$repo"/skills/*/; do
  name=$(basename "$skill")
  [ -f "$skill/SKILL.md" ] || continue
  link_one "$HOME/.agents/skills" "$name"
  if claude_excluded "$name"; then
    echo "skipped   $HOME/.claude/skills/$name (listed in scripts/claude-exclude.txt)"
  else
    link_one "$HOME/.claude/skills" "$name"
  fi
done

for dir in "$HOME/.agents/skills" "$HOME/.claude/skills"; do
  [ -d "$dir" ] || continue
  for path in "$dir"/*; do
    [ -L "$path" ] || continue
    target=$(readlink "$path")
    case $target in "$base"/*) ;; *) continue ;; esac
    [ -e "$path" ] && continue
    if [ "$prune" -eq 1 ] && [ "$check" -eq 0 ]; then
      rm "$path"
      echo "pruned    $path"
    else
      echo "DANGLING  $path -> $target (rerun with --prune to remove)"
      status=1
    fi
  done
done

exit "$status"
