#!/usr/bin/env bash
set -euo pipefail

REPO="${DREAMCLEANR_REPO:-jlsport18/DreamCleanr}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required to update DreamCleanr." >&2
  exit 1
fi

resolve_asset_url() {
  python3 - "$REPO" "${DREAMCLEANR_ASSET_URL:-}" <<'PY'
import json
import re
import sys
import urllib.request

repo = sys.argv[1]
override = sys.argv[2]

if override:
    print(override)
    raise SystemExit(0)

with urllib.request.urlopen(f"https://api.github.com/repos/{repo}/releases/latest") as response:
    payload = json.load(response)

assets = payload.get("assets", [])
patterns = [
    re.compile(r"^dreamcleanr-.*-py3-none-any\.whl$"),
    re.compile(r"^dreamcleanr-.*\.tar\.gz$"),
]

for pattern in patterns:
    for asset in assets:
        name = asset.get("name", "")
        if pattern.match(name):
            print(asset["browser_download_url"])
            raise SystemExit(0)

raise SystemExit("Unable to resolve a DreamCleanr release asset from the latest GitHub release.")
PY
}

ASSET_URL="$(resolve_asset_url)"
echo "Updating DreamCleanr from: $ASSET_URL"

if [ "${DREAMCLEANR_DISABLE_PIPX:-0}" != "1" ] && command -v pipx >/dev/null 2>&1; then
  pipx install --force "$ASSET_URL"
  echo "Updated DreamCleanr with pipx."
  exit 0
fi

python3 -m pip install --user --upgrade pip
python3 -m pip install --user --upgrade "$ASSET_URL"

echo "Updated DreamCleanr with pip. You may need to ensure your user bin directory is on PATH."
