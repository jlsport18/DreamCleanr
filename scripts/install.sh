#!/usr/bin/env bash
set -euo pipefail

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required to install DreamCleanr." >&2
  exit 1
fi

if command -v pipx >/dev/null 2>&1; then
  pipx install "git+https://github.com/jlsport18/DreamCleanr.git"
  exit 0
fi

python3 -m pip install --user --upgrade pip
python3 -m pip install --user "git+https://github.com/jlsport18/DreamCleanr.git"

echo "Installed DreamCleanr with pip. You may need to ensure your user bin directory is on PATH."
