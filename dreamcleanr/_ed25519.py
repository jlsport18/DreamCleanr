"""Vendored pure-Python Ed25519 (RFC 8032) — zero runtime dependencies.

This is a faithful Python 3 port of the public-domain reference implementation
published by the Ed25519 authors (Bernstein, Duif, Lange, Schwabe, Yang) at
https://ed25519.cr.yp.to/python/ed25519.py and mirrored in RFC 8032 Appendix A.

Why vendored: Sweep promises "no telemetry, no dependencies". The Python stdlib
has no asymmetric-signature verify, and both `cryptography` and `pynacl` are
heavy C-extension deps that would break that promise. The reference math is small
and we anchor its correctness on the RFC 8032 test vectors (see tests/test_ed25519.py).

The math (`inv`, `xrecover`, `edwards`, `scalarmult`, `Hint`, `checkvalid`) is the
reference algorithm unchanged. Only two things differ from the Python-2 original:
  1. modular exponentiation uses the stdlib builtin `pow(b, e, m)` (identical result,
     vastly faster) instead of the recursive `expmod`;
  2. byte (de)serialisation uses Python-3 `int.to_bytes`/`int.from_bytes` instead of
     the original `chr`/`ord` string handling.
Both are validated bit-for-bit by the RFC vectors.

On the client, only `verify()` is ever used and it runs fully offline. Signing
(`publickey`, `sign`) is used only by the operator-side issuance tool and the
server-side webhook-equivalent; the shipped product never holds a private seed.

This implementation is NOT side-channel hardened. That is acceptable here: the
client only verifies (public-key operation, no secret), and signing happens on a
trusted operator machine at low frequency.
"""
from __future__ import annotations

import hashlib

# ── Curve / field constants (RFC 8032 §5.1) ─────────────────────────────────
b = 256
q = 2 ** 255 - 19  # field prime
l = 2 ** 252 + 27742317777372353535851937790883648493  # group order

SEED_SIZE = 32       # Ed25519 private seed
PUBLIC_SIZE = 32     # encoded public point
SIGNATURE_SIZE = 64  # R (32) || S (32)


def _sha512(m: bytes) -> bytes:
    return hashlib.sha512(m).digest()


def _expmod(base: int, e: int, m: int) -> int:
    # The reference defines a recursive square-and-multiply; the stdlib builtin
    # computes the identical modular exponentiation in C. Kept as a named helper
    # so the call sites below read verbatim against the reference.
    return pow(base, e, m)


def _inv(x: int) -> int:
    return _expmod(x, q - 2, q)


d = -121665 * _inv(121666) % q
_I = _expmod(2, (q - 1) // 4, q)


def _xrecover(y: int) -> int:
    xx = (y * y - 1) * _inv(d * y * y + 1)
    x = _expmod(xx, (q + 3) // 8, q)
    if (x * x - xx) % q != 0:
        x = (x * _I) % q
    if x % 2 != 0:
        x = q - x
    return x


_By = 4 * _inv(5)
_Bx = _xrecover(_By)
B = [_Bx % q, _By % q]  # base point


def _edwards(P, Q):
    x1, y1 = P[0], P[1]
    x2, y2 = Q[0], Q[1]
    x3 = (x1 * y2 + x2 * y1) * _inv(1 + d * x1 * x2 * y1 * y2)
    y3 = (y1 * y2 + x1 * x2) * _inv(1 - d * x1 * x2 * y1 * y2)
    return [x3 % q, y3 % q]


def _scalarmult(P, e: int):
    if e == 0:
        return [0, 1]
    Q = _scalarmult(P, e // 2)
    Q = _edwards(Q, Q)
    if e & 1:
        Q = _edwards(Q, P)
    return Q


def _bit(h: bytes, i: int) -> int:
    return (h[i // 8] >> (i % 8)) & 1


def _encodeint(y: int) -> bytes:
    return y.to_bytes(b // 8, "little")


def _encodepoint(P) -> bytes:
    x, y = P[0], P[1]
    val = (y % (1 << 255)) | ((x & 1) << (b - 1))
    return val.to_bytes(b // 8, "little")


def _decodeint(s: bytes) -> int:
    return int.from_bytes(s, "little")


def _isoncurve(P) -> bool:
    x, y = P[0], P[1]
    return (-x * x + y * y - 1 - d * x * x * y * y) % q == 0


def _decodepoint(s: bytes):
    y = int.from_bytes(s, "little") & ((1 << (b - 1)) - 1)
    x = _xrecover(y)
    if (x & 1) != _bit(s, b - 1):
        x = q - x
    P = [x, y]
    if not _isoncurve(P):
        raise ValueError("decoding point that is not on curve")
    return P


def _secret_scalar(h: bytes) -> int:
    return 2 ** (b - 2) + sum(2 ** i * _bit(h, i) for i in range(3, b - 2))


def _Hint(m: bytes) -> int:
    h = _sha512(m)
    return sum(2 ** i * _bit(h, i) for i in range(2 * b))


# ── Public API ──────────────────────────────────────────────────────────────


def publickey(seed: bytes) -> bytes:
    """Derive the 32-byte public key from a 32-byte private seed."""
    if len(seed) != SEED_SIZE:
        raise ValueError(f"seed must be {SEED_SIZE} bytes, got {len(seed)}")
    h = _sha512(seed)
    a = _secret_scalar(h)
    A = _scalarmult(B, a)
    return _encodepoint(A)


def sign(message: bytes, seed: bytes, public_key: bytes | None = None) -> bytes:
    """Return the 64-byte Ed25519 signature of `message` under `seed`."""
    if len(seed) != SEED_SIZE:
        raise ValueError(f"seed must be {SEED_SIZE} bytes, got {len(seed)}")
    h = _sha512(seed)
    a = _secret_scalar(h)
    pk = public_key if public_key is not None else _encodepoint(_scalarmult(B, a))
    r = _Hint(h[b // 8:b // 4] + message)
    R = _scalarmult(B, r)
    S = (r + _Hint(_encodepoint(R) + pk + message) * a) % l
    return _encodepoint(R) + _encodeint(S)


def checkvalid(signature: bytes, message: bytes, public_key: bytes) -> None:
    """Raise ValueError if `signature` is not valid for `message`/`public_key`."""
    if len(signature) != SIGNATURE_SIZE:
        raise ValueError("signature length is wrong")
    if len(public_key) != PUBLIC_SIZE:
        raise ValueError("public-key length is wrong")
    R = _decodepoint(signature[0:b // 8])
    A = _decodepoint(public_key)
    S = _decodeint(signature[b // 8:b // 4])
    h = _Hint(_encodepoint(R) + public_key + message)
    if _scalarmult(B, S) != _edwards(R, _scalarmult(A, h)):
        raise ValueError("signature does not pass verification")


def verify(signature: bytes, message: bytes, public_key: bytes) -> bool:
    """Return True iff `signature` is a valid Ed25519 signature. Never raises."""
    try:
        checkvalid(signature, message, public_key)
        return True
    except Exception:
        return False
