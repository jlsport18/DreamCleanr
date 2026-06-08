"""Correctness anchor for the vendored pure-Python Ed25519.

RFC 8032 §7.1 test vectors are the ground truth: matching `publickey`, `sign`, and
`verify` byte-for-byte proves the Python-3 port of the reference math is correct.
We additionally assert the failure modes that bite license systems: a verifier that
accidentally returns True, or raises instead of returning False.
"""
from __future__ import annotations

import unittest

from dreamcleanr import _ed25519 as ed

# RFC 8032 §7.1 (Ed25519, pure): (secret seed, public key, message, signature) hex.
RFC_VECTORS = [
    (
        "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60",
        "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a",
        "",
        "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b",
    ),
    (
        "4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb",
        "3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c",
        "72",
        "92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da085ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00",
    ),
    (
        "c5aa8df43f9f837bedb7442f31dcb7b166d38535076f094b85ce3a2e0b4458f7",
        "fc51cd8e6218a1a38da47ed00230f0580816ed13ba3303ac5deb911548908025",
        "af82",
        "6291d657deec24024827e69c3abe01a30ce548a284743a445e3680d7db5ac3ac18ff9b538d16f290ae67f760984dc6594a7c15e9716ed28dc027beceea1ec40a",
    ),
    (
        "833fe62409237b9d62ec77587520911e9a759cec1d19755b7da901b96dca3d42",
        "ec172b93ad5e563bf4932c70e1245034c35467ef2efd4d64ebf819683467e2bf",
        "ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a2192992a274fc1a836ba3c23a3feebbd454d4423643ce80e2a9ac94fa54ca49f",
        "dc2a4459e7369633a52b1bf277839a00201009a3efbf3ecb69bea2186c26b58909351fc9ac90b3ecfdfbc7c66431e0303dca179c138ac17ad9bef1177331a704",
    ),
]


class RFC8032Tests(unittest.TestCase):
    def test_publickey_matches_rfc(self) -> None:
        for sk, pk, _, _ in RFC_VECTORS:
            self.assertEqual(ed.publickey(bytes.fromhex(sk)).hex(), pk)

    def test_sign_matches_rfc(self) -> None:
        for sk, pk, msg, sig in RFC_VECTORS:
            produced = ed.sign(bytes.fromhex(msg), bytes.fromhex(sk), bytes.fromhex(pk))
            self.assertEqual(produced.hex(), sig)

    def test_verify_accepts_rfc(self) -> None:
        for _, pk, msg, sig in RFC_VECTORS:
            self.assertTrue(ed.verify(bytes.fromhex(sig), bytes.fromhex(msg), bytes.fromhex(pk)))


class RejectionTests(unittest.TestCase):
    """Every malformed/forged input must return False, never raise."""

    def setUp(self) -> None:
        _, pk, msg, sig = RFC_VECTORS[2]
        self.pk = bytes.fromhex(pk)
        self.msg = bytes.fromhex(msg)
        self.sig = bytes.fromhex(sig)
        self.other_pk = bytes.fromhex(RFC_VECTORS[1][1])

    def test_tampered_message_rejected(self) -> None:
        self.assertFalse(ed.verify(self.sig, self.msg + b"x", self.pk))

    def test_wrong_public_key_rejected(self) -> None:
        self.assertFalse(ed.verify(self.sig, self.msg, self.other_pk))

    def test_zero_signature_rejected(self) -> None:
        self.assertFalse(ed.verify(b"\x00" * 64, self.msg, self.pk))

    def test_bitflip_in_signature_rejected(self) -> None:
        bad = bytearray(self.sig)
        bad[0] ^= 0x01
        self.assertFalse(ed.verify(bytes(bad), self.msg, self.pk))

    def test_wrong_length_inputs_return_false_not_raise(self) -> None:
        self.assertFalse(ed.verify(b"short", self.msg, self.pk))
        self.assertFalse(ed.verify(self.sig, self.msg, b"shortpk"))
        self.assertFalse(ed.verify(b"", self.msg, self.pk))


class RoundTripTests(unittest.TestCase):
    def test_generated_keypair_round_trips(self) -> None:
        seed = bytes(range(32))  # deterministic, no os.urandom dependence
        pk = ed.publickey(seed)
        for msg in (b"", b"hello@example.com", bytes(range(200))):
            sig = ed.sign(msg, seed, pk)
            self.assertEqual(len(sig), 64)
            self.assertTrue(ed.verify(sig, msg, pk))
            self.assertFalse(ed.verify(sig, msg + b"!", pk))


if __name__ == "__main__":
    unittest.main()
