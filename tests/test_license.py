"""Sweep Pro licensing: Ed25519 issuance/verification, gating, and forge-resistance.

The crux regression these tests guard: the old HMAC scheme let anyone mint a valid
key because the signing secret defaulted to a public constant. The Ed25519 scheme
must make minting impossible without the private seed, while keeping verification
fully offline and deterministic.

Signing tests inject a *test* keypair (seed + matching embedded public key) so they
never depend on the production secret. One test additionally exercises the real
embedded public key against the operator seed when it is available locally; it skips
in CI where the seed is absent — proving (when run on the operator box) that the
embedded constant and the stored seed are the same pair.
"""
from __future__ import annotations

import json
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from dreamcleanr import _ed25519 as ed
from dreamcleanr import license as lic

# A fixed test keypair — independent of the production key.
_TEST_SEED = bytes(range(1, 33))
_TEST_PUBLIC = ed.publickey(_TEST_SEED)


class _LicenseTestBase(unittest.TestCase):
    """Isolate the license file and swap in a test signing keypair."""

    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self._orig_file = lic._LICENSE_FILE
        self._orig_pub = lic._PUBLIC_KEY
        self._orig_env = os.environ.get("SWEEP_SIGNING_KEY")
        lic._LICENSE_FILE = Path(self._tmp.name) / ".sweep_license"
        lic._PUBLIC_KEY = _TEST_PUBLIC
        os.environ["SWEEP_SIGNING_KEY"] = _TEST_SEED.hex()
        lic._verify_key.cache_clear()  # pubkey changed; drop stale verifications

    def tearDown(self) -> None:
        lic._LICENSE_FILE = self._orig_file
        lic._PUBLIC_KEY = self._orig_pub
        if self._orig_env is None:
            os.environ.pop("SWEEP_SIGNING_KEY", None)
        else:
            os.environ["SWEEP_SIGNING_KEY"] = self._orig_env
        lic._verify_key.cache_clear()
        self._tmp.cleanup()


class IssuanceTests(_LicenseTestBase):
    def test_generate_then_verify(self) -> None:
        key = lic.generate_key("Buyer@Example.com")
        self.assertTrue(key.startswith("SWEEP-"))
        self.assertTrue(lic._verify_key(key, "buyer@example.com"))

    def test_deterministic(self) -> None:
        self.assertEqual(lic.generate_key("a@b.com"), lic.generate_key("a@b.com"))

    def test_email_normalized_for_verify(self) -> None:
        key = lic.generate_key("a@b.com")
        self.assertTrue(lic._verify_key(key, "  A@B.COM  "))

    def test_key_for_one_email_invalid_for_another(self) -> None:
        key = lic.generate_key("alice@example.com")
        self.assertFalse(lic._verify_key(key, "bob@example.com"))


class ForgeResistanceTests(_LicenseTestBase):
    def test_cannot_sign_without_seed(self) -> None:
        os.environ.pop("SWEEP_SIGNING_KEY", None)
        with self.assertRaises(RuntimeError):
            lic.generate_key("attacker@example.com")

    def test_seed_must_match_embedded_public_key(self) -> None:
        os.environ["SWEEP_SIGNING_KEY"] = (bytes(range(32, 64))).hex()  # wrong seed
        with self.assertRaises(RuntimeError):
            lic.generate_key("x@y.com")

    def test_garbage_key_rejected(self) -> None:
        self.assertFalse(lic._verify_key("SWEEP-NOTBASE32!!!", "a@b.com"))
        self.assertFalse(lic._verify_key("SWEEP-AAAA", "a@b.com"))  # valid b32, wrong length
        self.assertFalse(lic._verify_key("not-a-key", "a@b.com"))
        self.assertFalse(lic._verify_key("", "a@b.com"))

    def test_old_hmac_format_key_rejected(self) -> None:
        # The legacy scheme emitted SWEEP-{16 base32 chars}; such keys must not verify.
        self.assertFalse(lic._verify_key("SWEEP-ABCDEFGHIJKLMNOP", "a@b.com"))

    def test_signature_for_wrong_keypair_rejected(self) -> None:
        # A signature minted under a different seed must fail under the embedded key.
        other_seed = bytes(range(64, 96))
        sig = ed.sign(lic._message("a@b.com"), other_seed, ed.publickey(other_seed))
        import base64
        forged = "SWEEP-" + base64.b32encode(sig).decode().rstrip("=")
        self.assertFalse(lic._verify_key(forged, "a@b.com"))


class ActivationTests(_LicenseTestBase):
    def test_activate_and_check_pro(self) -> None:
        self.assertFalse(lic.check_pro())
        key = lic.generate_key("buyer@example.com")
        lic.activate(key=key, email="buyer@example.com")
        self.assertTrue(lic.check_pro())
        info = lic.get_license_info()
        self.assertEqual(info["email"], "buyer@example.com")
        self.assertEqual(info["tier"], "pro")

    def test_activate_rejects_bad_key(self) -> None:
        with self.assertRaises(ValueError):
            lic.activate(key="SWEEP-BOGUS", email="buyer@example.com")
        self.assertFalse(lic.check_pro())

    def test_activate_requires_email(self) -> None:
        key = lic.generate_key("buyer@example.com")
        with self.assertRaises(ValueError):
            lic.activate(key=key, email="not-an-email")

    def test_deactivate(self) -> None:
        key = lic.generate_key("buyer@example.com")
        lic.activate(key=key, email="buyer@example.com")
        self.assertTrue(lic.check_pro())
        self.assertTrue(lic.deactivate())
        self.assertFalse(lic.check_pro())
        self.assertFalse(lic.deactivate())  # already gone

    def test_tampered_license_file_fails_closed(self) -> None:
        key = lic.generate_key("buyer@example.com")
        lic.activate(key=key, email="buyer@example.com")
        # Attacker swaps in a different email but keeps the (valid-for-other) key.
        lic._LICENSE_FILE.write_text(json.dumps({"key": key, "email": "attacker@evil.com", "tier": "pro"}))
        lic._verify_key.cache_clear()
        self.assertFalse(lic.check_pro())


class EmbeddedKeyTests(unittest.TestCase):
    """When the operator seed is present locally, prove it matches the shipped pubkey."""

    def test_embedded_public_key_matches_operator_seed(self) -> None:
        secrets = Path.home() / ".config" / "jlfg" / "secrets.local.json"
        if not secrets.exists():
            self.skipTest("operator secret store not present (expected in CI)")
        seed_hex = json.loads(secrets.read_text()).get("SWEEP_SIGNING_KEY", "")
        if not seed_hex:
            self.skipTest("SWEEP_SIGNING_KEY not configured")
        self.assertEqual(
            ed.publickey(bytes.fromhex(seed_hex)),
            lic._PUBLIC_KEY,
            "embedded public key does not match the operator's private seed — "
            "every issued license would fail verification",
        )


if __name__ == "__main__":
    unittest.main()
