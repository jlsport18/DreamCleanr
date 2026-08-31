"""Pure-Python Ed25519 signature verification (RFC 8032).

Verify-only, stdlib-only. Vendored deliberately: ``pyproject.toml`` declares
``dependencies = []``, and a tool whose pitch is reclaiming disk space should not
install a ~10MB compiled crypto wheel just to check a licence.

Signing lives server-side (Cloudflare Worker), where dependencies are free — and
keeping the signing half out of the shipped package is what makes licences
unforgeable. The previous HMAC scheme shipped its key generator, so anyone could
mint valid keys.

Validated against RFC 8032 section 7.1 test vector 2.
"""

import hashlib

_P = 2 ** 255 - 19
_L = 2 ** 252 + 27742317777372353535851937790883648493
_D = -121665 * pow(121666, _P - 2, _P) % _P
_I = pow(2, (_P - 1) // 4, _P)


def _x_recover(y: int) -> int:
    xx = (y * y - 1) * pow(_D * y * y + 1, _P - 2, _P)
    x = pow(xx, (_P + 3) // 8, _P)
    if (x * x - xx) % _P != 0:
        x = (x * _I) % _P
    if x % 2 != 0:
        x = _P - x
    return x


_BY = 4 * pow(5, _P - 2, _P) % _P
_BX = _x_recover(_BY)
_B = (_BX % _P, _BY % _P, 1, (_BX * _BY) % _P)


def _add(p, q):
    x1, y1, z1, t1 = p
    x2, y2, z2, t2 = q
    a = (y1 - x1) * (y2 - x2) % _P
    b = (y1 + x1) * (y2 + x2) % _P
    c = t1 * 2 * _D * t2 % _P
    dd = z1 * 2 * z2 % _P
    e, f, g, h = b - a, dd - c, dd + c, b + a
    return (e * f % _P, g * h % _P, f * g % _P, e * h % _P)


def _scalarmult(p, e: int):
    result = (0, 1, 1, 0)
    addend = p
    while e > 0:
        if e & 1:
            result = _add(result, addend)
        addend = _add(addend, addend)
        e >>= 1
    return result


def _decode_point(s: bytes):
    y = int.from_bytes(s, "little") & ((1 << 255) - 1)
    if y >= _P:
        return None
    sign = s[31] >> 7
    x = _x_recover(y)
    if x & 1 != sign:
        x = _P - x
    p = (x, y, 1, x * y % _P)
    # Reject points that are not actually on the curve.
    if (-x * x + y * y - 1 - _D * x * x * y * y) % _P != 0:
        return None
    return p


def _equal(p, q) -> bool:
    x1, y1, z1, _ = p
    x2, y2, z2, _ = q
    return (x1 * z2 - x2 * z1) % _P == 0 and (y1 * z2 - y2 * z1) % _P == 0


def verify(public_key: bytes, signature: bytes, message: bytes) -> bool:
    """Return True only if ``signature`` is a valid Ed25519 signature.

    Never raises: malformed input returns False. Callers gate privileged
    behaviour on this, so an exception path would be a bypass.
    """
    try:
        if len(signature) != 64 or len(public_key) != 32:
            return False
        a = _decode_point(public_key)
        r = _decode_point(signature[:32])
        if a is None or r is None:
            return False
        s = int.from_bytes(signature[32:], "little")
        if s >= _L:
            return False
        h = int.from_bytes(
            hashlib.sha512(signature[:32] + public_key + message).digest(), "little"
        ) % _L
        return _equal(_scalarmult(_B, s), _add(r, _scalarmult(a, h)))
    except Exception:
        return False
