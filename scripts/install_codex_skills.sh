#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="$REPO_ROOT/codex-skills"
TARGET_ROOT="${CODEX_HOME:-$HOME/.codex}/skills"

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "DreamCleanr skill source directory not found: $SOURCE_DIR" >&2
  exit 1
fi

mkdir -p "$TARGET_ROOT"

installed=0

for skill_dir in "$SOURCE_DIR"/*; do
  [[ -d "$skill_dir" ]] || continue
  skill_name="$(basename "$skill_dir")"

  if [[ ! -f "$skill_dir/SKILL.md" ]]; then
    echo "Skipping $skill_name: missing SKILL.md" >&2
    continue
  fi

  target_dir="$TARGET_ROOT/$skill_name"
  rm -rf "$target_dir"
  mkdir -p "$target_dir"
  cp -R "$skill_dir"/. "$target_dir"/
  installed=$((installed + 1))
  echo "Installed $skill_name -> $target_dir"
done

echo "Installed $installed DreamCleanr skill(s) into $TARGET_ROOT"
