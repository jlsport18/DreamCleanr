"""Licence verification tests.

These sign real licences with a throwaway keypair so the positive path is
exercised, not just rejections. The production private key never appears here —
it exists only as a Cloudflare secret.
"""

import base64
import hashlib
import json

import pytest

from dreamcleanr import _ed25519 as ed
from dreamcleanr import license as lic

# ── Test-only Ed25519 signing (the shipped package verifies but never signs) ──

_TEST_SEED = bytes(range(32))


def _encode_point(p) -> bytes:
    x, y, z, _ = p
    zi = pow(z, ed._P - 2, ed._P)
    x, y = x * zi % ed._P, y * zi % ed._P
    return (y | ((x & 1) << 255)).to_bytes(32, "little")


def _secret_scalar(seed: bytes) -> int:
    h = bytearray(hashlib.sha512(seed).digest()[:32])
    h[0] &= 248
    h[31] &= 127
    h[31] |= 64
    return int.from_bytes(h, "little")


def _public_key(seed: bytes) -> bytes:
    return _encode_point(ed._scalarmult(ed._B, _secret_scalar(seed)))


def _sign(seed: bytes, msg: bytes) -> bytes:
    h = hashlib.sha512(seed).digest()
    a = _secret_scalar(seed)
    pub = _encode_point(ed._scalarmult(ed._B, a))
    r = int.from_bytes(hashlib.sha512(h[32:] + msg).digest(), "little") % ed._L
    big_r = _encode_point(ed._scalarmult(ed._B, r))
    k = int.from_bytes(hashlib.sha512(big_r + pub + msg).digest(), "little") % ed._L
    s = (r + k * a) % ed._L
    return big_r + s.to_bytes(32, "little")


TEST_PUB = _public_key(_TEST_SEED)


def _b64(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def make_key(email="buyer@example.com", order="cs_test_123", issued=1735689600):
    payload = json.dumps({"e": email, "o": order, "t": issued}, separators=(",", ":")).encode()
    return f"SWEEP-{_b64(payload)}.{_b64(_sign(_TEST_SEED, payload))}"


@pytest.fixture(autouse=True)
def _use_test_key(monkeypatch, tmp_path):
    monkeypatch.setattr(lic, "PUBLIC_KEY", TEST_PUB)
    monkeypatch.setattr(lic, "_LICENSE_FILE", tmp_path / ".sweep_license")


# ── The signing helper must itself be sound, or every test below is vacuous ──


def test_helper_produces_signatures_the_verifier_accepts():
    payload = b'{"e":"x@y.z"}'
    assert ed.verify(TEST_PUB, _sign(_TEST_SEED, payload), payload) is True


# ── parse_key ────────────────────────────────────────────────────────────────


def test_parse_key_accepts_a_validly_signed_licence():
    data = lic.parse_key(make_key())
    assert data == {"e": "buyer@example.com", "o": "cs_test_123", "t": 1735689600}


@pytest.mark.parametrize("bad", ["", "not-a-key", "SWEEP-onlyonepart", "SWEEP-.", "WRONG-a.b"])
def test_parse_key_rejects_malformed(bad):
    assert lic.parse_key(bad) is None


def test_parse_key_rejects_tampered_payload():
    key = make_key(email="buyer@example.com")
    payload_b64, _, sig_b64 = key[len("SWEEP-"):].partition(".")
    forged = json.dumps({"e": "attacker@evil.com", "o": "x", "t": 1}, separators=(",", ":")).encode()
    assert lic.parse_key(f"SWEEP-{_b64(forged)}.{sig_b64}") is None


def test_parse_key_rejects_signature_from_a_different_key():
    payload = json.dumps({"e": "a@b.c", "o": "1", "t": 1}, separators=(",", ":")).encode()
    other_seed = bytes(range(1, 33))
    assert lic.parse_key(f"SWEEP-{_b64(payload)}.{_b64(_sign(other_seed, payload))}") is None


# ── activate / check_pro / get_license_info / deactivate ─────────────────────


def test_activate_then_check_pro():
    assert lic.check_pro() is False
    lic.activate(make_key())
    assert lic.check_pro() is True
    assert lic.get_license_info()["email"] == "buyer@example.com"


def test_activate_sets_file_mode_600():
    lic.activate(make_key())
    assert oct(lic._LICENSE_FILE.stat().st_mode)[-3:] == "600"


def test_activate_rejects_invalid_key():
    with pytest.raises(ValueError):
        lic.activate("SWEEP-bogus.bogus")
    assert lic.check_pro() is False


def test_check_pro_false_when_file_corrupt():
    lic._LICENSE_FILE.write_text("{not json")
    assert lic.check_pro() is False


def test_check_pro_false_when_stored_key_no_longer_verifies():
    """A licence file hand-edited to a forged key must not grant Pro."""
    lic.activate(make_key())
    record = json.loads(lic._LICENSE_FILE.read_text())
    record["key"] = "SWEEP-forged.forged"
    lic._LICENSE_FILE.write_text(json.dumps(record))
    assert lic.check_pro() is False


def test_deactivate():
    lic.activate(make_key())
    assert lic.deactivate() is True
    assert lic.check_pro() is False
    assert lic.deactivate() is False


# ── The regression that motivated this whole change ──────────────────────────


def test_generate_key_is_gone():
    """The old symmetric scheme shipped a key generator whose signing key
    derived from a literal in the source, so anyone could mint valid licences.
    It must not come back."""
    assert not hasattr(lic, "generate_key")
