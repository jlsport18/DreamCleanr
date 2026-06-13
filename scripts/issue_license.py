#!/usr/bin/env python3
"""Operator-side Sweep Pro license issuance tool.

NOT shipped in the wheel (lives outside the `dreamcleanr` package). Requires the
private signing seed, supplied via the SWEEP_SIGNING_KEY env var or read from the
operator secret store at ~/.config/jlfg/secrets.local.json.

This is the manual issuance path that lets the keystone land atomically with a way
to actually mint keys; the Stripe webhook (functions/api/stripe-webhook.js) is the
automated equivalent and MUST sign the identical message (see dreamcleanr.license).

Usage:
    python scripts/issue_license.py buyer@example.com
    SWEEP_SIGNING_KEY=<hex> python scripts/issue_license.py buyer@example.com
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Import from the in-repo package without installing it.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Path to the operator secret store file. Holds only the location — the signing
# seed value lives inside the file and is never logged.
STORE_PATH = Path.home() / ".config" / "jlfg" / "secrets.local.json"


def _ensure_seed_in_env() -> None:
    if os.environ.get("SWEEP_SIGNING_KEY", "").strip():
        return
    if STORE_PATH.exists():
        try:
            data = json.loads(STORE_PATH.read_text())
        except json.JSONDecodeError:
            data = {}
        seed = data.get("SWEEP_SIGNING_KEY", "").strip()
        if seed:
            os.environ["SWEEP_SIGNING_KEY"] = seed


def main(argv: list[str]) -> int:
    if len(argv) != 2 or "@" not in argv[1]:
        print("usage: issue_license.py <buyer-email>", file=sys.stderr)
        return 2
    _ensure_seed_in_env()
    from dreamcleanr.license import generate_key  # imported after seed is in env

    email = argv[1]
    try:
        key = generate_key(email)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        print(
            "Set SWEEP_SIGNING_KEY (hex seed) or add it to "
            f"{STORE_PATH}.",
            file=sys.stderr,
        )
        return 1
    print(key)
    print(f"  email: {email.strip().lower()}", file=sys.stderr)
    print("  activate: sweep license activate --key {} --email {}".format(key, email.strip().lower()), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
