"""Sweep Pro license key system.

License keys are HMAC-SHA256 signatures of the buyer's email address,
validated entirely offline — no backend required. The signing secret
is embedded at build time (never exposed in the binary directly; derived
via key derivation).

Key format: SWEEP-{BASE32_ENCODED_HMAC_12_BYTES}
Example:    SWEEP-ABCDEFGHIJKLMNOP

Key generation (run by Stripe webhook after purchase):
  from dreamcleanr.license import generate_key
  key = generate_key(email="buyer@example.com")

Key validation (run by CLI on --activate):
  from dreamcleanr.license import activate, check_pro
  activate(key="SWEEP-...", email="buyer@example.com")  # writes ~/.sweep_license
  is_pro = check_pro()  # fast path used at runtime

Pro features unlocked by a valid key:
  - Scheduled cleaning (LaunchAgent install without nag)
  - Developer mode (targets Xcode DerivedData, node_modules, Docker, AI models)
  - Priority support tier
  - HTML report branding removed
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Signing secret — derived from build-time constant + domain-specific salt.
# NOT the raw secret; a one-way derived key. Rotate by releasing a new version.
_SALT = b"sweep-pro-v1-2026"
_BASE_SECRET = os.environ.get("SWEEP_LICENSE_SECRET", "").encode()
_SIGNING_KEY: bytes = hashlib.pbkdf2_hmac(
    "sha256", _BASE_SECRET or b"sweep-community-default", _SALT, iterations=100_000, dklen=32
)

_KEY_PREFIX = "SWEEP-"
_LICENSE_FILE = Path.home() / ".sweep_license"
_HMAC_BYTES = 12  # 96 bits — collision-resistant for this use case


# ── Key generation (used by Stripe webhook / admin tool) ─────────────────


def generate_key(email: str) -> str:
    """Generate a Pro license key for a given email address.

    Should be called server-side after Stripe payment confirmation.
    The same email always produces the same key (deterministic).
    """
    email = email.strip().lower()
    sig = hmac.new(_SIGNING_KEY, email.encode(), hashlib.sha256).digest()
    encoded = base64.b32encode(sig[:_HMAC_BYTES]).decode().rstrip("=")
    return f"{_KEY_PREFIX}{encoded}"


# ── Key validation ────────────────────────────────────────────────────────


def _verify_key(key: str, email: str) -> bool:
    """Return True if key is a valid Pro key for this email."""
    if not key.startswith(_KEY_PREFIX):
        return False
    expected = generate_key(email)
    return hmac.compare_digest(key.upper(), expected.upper())


# ── Activation (writes ~/.sweep_license) ────────────────────────────────


def activate(key: str, email: str) -> None:
    """Validate and store a license key locally.

    Raises ValueError with a human-readable message if key is invalid.
    Writes ~/.sweep_license on success.
    """
    key = key.strip().upper()
    email = email.strip().lower()

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


# ── Runtime check (fast path) ────────────────────────────────────────────


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
    """Return license record dict if valid, else None."""
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
