#!/usr/bin/env python3
"""Generate the Ed25519 keypair for Sweep Pro licences. Run ONCE.

The PUBLIC key is printed — paste it into dreamcleanr/license.py PUBLIC_KEY.
It can only verify, never sign, so it is safe to ship and safe to display.

The PRIVATE key is written to a mode-600 file and never printed, so it cannot
end up in a terminal transcript, CI log, or screen recording. Move it into the
Cloudflare secret SWEEP_LICENSE_PRIVATE_KEY and a password manager, then delete
the file.

    python3 scripts/gen_license_keypair.py [--out PATH]
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import os
import secrets
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dreamcleanr import _ed25519 as ed  # noqa: E402


def _encode_point(p) -> bytes:
    x, y, z, _ = p
    zi = pow(z, ed._P - 2, ed._P)
    x, y = x * zi % ed._P, y * zi % ed._P
    return (y | ((x & 1) << 255)).to_bytes(32, "little")


def public_from_seed(seed: bytes) -> bytes:
    h = bytearray(hashlib.sha512(seed).digest()[:32])
    h[0] &= 248
    h[31] &= 127
    h[31] |= 64
    return _encode_point(ed._scalarmult(ed._B, int.from_bytes(h, "little")))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        default=str(Path.home() / "sweep-license-private-key.txt"),
        help="Where to write the private key (mode 600).",
    )
    args = ap.parse_args()

    out = Path(args.out)
    if out.exists():
        print(f"REFUSING to overwrite existing {out}", file=sys.stderr)
        print("Generating a new keypair invalidates every licence already sold.", file=sys.stderr)
        return 1

    seed = secrets.token_bytes(32)
    pub = public_from_seed(seed)

    out.write_text(base64.b64encode(seed).decode() + "\n")
    os.chmod(out, 0o600)

    print("PUBLIC KEY — paste into dreamcleanr/license.py PUBLIC_KEY:")
    print(f'    "{pub.hex()}"')
    print()
    print(f"PRIVATE KEY written to: {out}  (mode 600, NOT printed)")
    print("  1. wrangler pages secret put SWEEP_LICENSE_PRIVATE_KEY < that file")
    print("  2. store a copy in your password manager")
    print("  3. shred the file:  rm -P " + str(out))
    print()
    print("Losing the private key means you can never issue another licence.")
    print("Rotating it invalidates every licence already sold.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
