import pytest

from dreamcleanr._ed25519 import verify

# RFC 8032 section 7.1, test vector 2 (1-octet message)
PUB = bytes.fromhex("3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c")
MSG = bytes.fromhex("72")
SIG = bytes.fromhex(
    "92a009a9f0d4cab8720e820b5f642540"
    "a2b27b5416503f8fb3762223ebdb69da"
    "085ac1e43e15996e458f3613d0f11d8c"
    "387b2eaeb4302aeeb00d291612bb0c00"
)


def test_accepts_valid_signature():
    assert verify(PUB, SIG, MSG) is True


def test_rejects_tampered_message():
    assert verify(PUB, SIG, b"\x73") is False


def test_rejects_tampered_signature():
    bad = bytearray(SIG)
    bad[0] ^= 0x01
    assert verify(PUB, bytes(bad), MSG) is False


def test_rejects_wrong_public_key():
    other = bytearray(PUB)
    other[0] ^= 0x01
    assert verify(bytes(other), SIG, MSG) is False


@pytest.mark.parametrize("sig", [b"", b"\x00" * 63, b"\x00" * 65])
def test_rejects_malformed_signature_length(sig):
    assert verify(PUB, sig, MSG) is False


@pytest.mark.parametrize("pub", [b"", b"\x00" * 31, b"\x00" * 33])
def test_rejects_malformed_public_key_length(pub):
    assert verify(pub, SIG, MSG) is False
