"""Sweep Pro license key system — Ed25519, offline, zero-dependency.

A license key is an **Ed25519 signature** over the buyer's email address.
Only the holder of the private signing seed (the operator / the Stripe webhook)
can produce a key; anyone can verify one offline against the embedded public key.
This replaces the previous HMAC scheme, whose signing secret defaulted to a
public constant — making every key trivially forgeable.

Key format: SWEEP-{BASE32(ed25519_signature)}  (uppercase, '=' padding stripped)

Key generation (operator issuance tool / Stripe webhook, needs the private seed):
    SWEEP_SIGNING_KEY=<hex seed>  python -c "from dreamcleanr.license import generate_key; print(generate_key('buyer@example.com'))"

Key validation (CLI on activate; runtime gate) — no secret required, fully offline:
    from dreamcleanr.license import activate, check_pro
    activate(key="SWEEP-...", email="buyer@example.com")  # writes ~/.sweep_license
    is_pro = check_pro()

Pro features unlocked by a valid key:
  - Developer mode (`clean --mode max`: Xcode DerivedData, node_modules, Docker, AI caches)
  - Scheduled cleaning without the upsell nag
  - HTML report branding removed
  - Priority support tier

Signing material is NEVER shipped: the wheel contains only the public key and the
pure-Python verifier. The private seed lives in the operator's secret store and is
injected via SWEEP_SIGNING_KEY only on the signing side (see scripts/issue_license.py
and the Stripe webhook). tests/test_distribution.py enforces this.
"""
from __future__ import annotations

import base64
import binascii
import json
import os
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

from . import _ed25519

# ── Embedded public verification key ─────────────────────────────────────────
# Generated 2026-06-08; private seed held in the operator secret store as
# SWEEP_SIGNING_KEY. Rotating the key = embed a new public key + release.
_PUBLIC_KEY_B64 = "o7bygX7IMXr2vHvcq2WFuPXNJmDjQfWQr6hMj9v7760="
_PUBLIC_KEY: bytes = base64.b64decode(_PUBLIC_KEY_B64)

# Domain-separation prefix: signatures are bound to this product + scheme version,
# so a key minted under this seed for another purpose can never be replayed here.
# The Stripe webhook (B) MUST sign exactly `_SIGN_CONTEXT + lower(email)`.
_SIGN_CONTEXT = b"sweep-pro-license-v1:"

_KEY_PREFIX = "SWEEP-"
_LICENSE_FILE = Path.home() / ".sweep_license"


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _message(email: str) -> bytes:
    return _SIGN_CONTEXT + _normalize_email(email).encode()


# ── Key generation (signing side only — needs the private seed) ──────────────


def _load_signing_seed() -> bytes:
    """Return the 32-byte private seed from SWEEP_SIGNING_KEY, or raise."""
    raw = os.environ.get("SWEEP_SIGNING_KEY", "").strip()
    if not raw:
        raise RuntimeError(
            "SWEEP_SIGNING_KEY is not set. License signing is an operator/server "
            "operation; the shipped client can only verify keys, never mint them."
        )
    try:
        seed = bytes.fromhex(raw)
    except ValueError as exc:
        raise RuntimeError("SWEEP_SIGNING_KEY must be a 32-byte hex seed.") from exc
    if len(seed) != _ed25519.SEED_SIZE:
        raise RuntimeError(f"SWEEP_SIGNING_KEY must be {_ed25519.SEED_SIZE} bytes (hex).")
    # Fail closed if the configured seed does not match the embedded public key —
    # otherwise we would happily mint keys that no released client can verify.
    if _ed25519.publickey(seed) != _PUBLIC_KEY:
        raise RuntimeError(
            "SWEEP_SIGNING_KEY does not match the embedded public key. Refusing to "
            "sign keys that clients cannot verify."
        )
    return seed


def generate_key(email: str) -> str:
    """Mint a Pro license key for `email`. Requires the private seed (server-side).

    Deterministic: the same email always yields the same key.
    """
    seed = _load_signing_seed()
    sig = _ed25519.sign(_message(email), seed, _PUBLIC_KEY)
    encoded = base64.b32encode(sig).decode().rstrip("=")
    return f"{_KEY_PREFIX}{encoded}"


# ── Key validation (verify side — offline, no secret) ────────────────────────


# Scope note: Ed25519 closes key *forgery* — without the private seed, nobody can
# mint a valid key for their email. It does not make Pro un-pirateable: check_pro()
# is a readable client-side check that a determined user can patch out. That is
# inherent to offline licensing for an indie tool and is an accepted trade-off.
# (The reference verifier also does not reject non-canonical S, so a key holder can
# derive variant valid signatures for the same email — no forgery impact.)
@lru_cache(maxsize=256)
def _verify_key(key: str, email: str) -> bool:
    """Return True iff `key` is a valid Pro signature for `email`. Never raises.

    Cached: Ed25519 verify is ~hundreds of ms in pure Python, and a single CLI
    run checks the gate at several points. Cache key is (key, email), so a fresh
    activation (new key) or deactivation (file gone) naturally bypasses the cache.
    """
    if not key.startswith(_KEY_PREFIX):
        return False
    body = key[len(_KEY_PREFIX):].upper()
    body += "=" * (-len(body) % 8)  # restore base32 padding
    try:
        sig = base64.b32decode(body)
    except (binascii.Error, ValueError):
        return False
    if len(sig) != _ed25519.SIGNATURE_SIZE:
        return False
    return _ed25519.verify(sig, _message(email), _PUBLIC_KEY)


# ── Activation (writes ~/.sweep_license) ─────────────────────────────────────


def activate(key: str, email: str) -> None:
    """Validate and store a license key locally.

    Raises ValueError with a human-readable message if the key is invalid.
    """
    key = key.strip().upper()
    email = _normalize_email(email)

    if not email or "@" not in email:
        raise ValueError("Please provide the email address you used to purchase Sweep.")

    if not _verify_key(key, email):
        raise ValueError(
            "License key not valid for that email address.\n"
            "Double-check both values match your Stripe receipt.\n"
            "Need help? Email support@jonlynchfinancial.com"
        )

    record = {
        "key": key,
        "email": email,
        "activated_at": datetime.now(timezone.utc).isoformat(),
        "tier": "pro",
    }
    _LICENSE_FILE.write_text(json.dumps(record, indent=2))
    _LICENSE_FILE.chmod(0o600)


# ── Runtime check (fast path) ────────────────────────────────────────────────


def check_pro() -> bool:
    """Return True if a valid Pro license is installed on this machine."""
    if not _LICENSE_FILE.exists():
        return False
    try:
        record = json.loads(_LICENSE_FILE.read_text())
        key = record.get("key", "")
        email = record.get("email", "")
        return bool(key and email and _verify_key(key, email))
    except Exception:
        return False


def get_license_info() -> dict | None:
    """Return the license record dict if valid, else None."""
    if not _LICENSE_FILE.exists():
        return None
    try:
        record = json.loads(_LICENSE_FILE.read_text())
        if _verify_key(record.get("key", ""), record.get("email", "")):
            return record
    except Exception:
        pass
    return None


def deactivate() -> bool:
    """Remove the license file. Returns True if it existed."""
    if _LICENSE_FILE.exists():
        _LICENSE_FILE.unlink()
        return True
    return False
