# Sweep Pro Monetization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Sweep Pro purchasable and enforceable — replace the currently-bypassable
symmetric licence with offline Ed25519 verification, wire the gate to `clean --apply` and
`schedule`, and deliver keys from a Stripe webhook.

**Architecture:** The wheel ships only an Ed25519 **public** key and a vendored
pure-Python verifier. A Cloudflare Pages Function signs `{email, order_id, issued_at}`
with the private key after Stripe checkout and emails the licence via Resend. The CLI
verifies locally — no network call at runtime, no server in the hot path.

**Tech Stack:** Python 3.11+ (stdlib only), pytest, Cloudflare Pages Functions
(JavaScript), Stripe, Resend.

**Spec:** `docs/superpowers/specs/2026-08-31-sweep-monetization-design.md`

## Global Constraints

- **`dependencies = []` in `pyproject.toml` MUST remain empty.** The verifier is vendored
  pure-Python. Adding `cryptography`, `pynacl`, or any runtime dependency is a design
  violation. Task 4 adds a test that enforces this.
- **Python floor is `>=3.11`** (`requires-python` in `pyproject.toml`). Do not use syntax
  newer than 3.11.
- **Price is `$6.99` one-time.** Never write `$4.99`, `$29`, `$24`, `$49`, `$29.99`, or
  `$49.99` in any copy this plan touches.
- **Licence file is `~/.sweep_license`, mode `0o600`.** This path already exists in
  `dreamcleanr/license.py`; keep it so existing installs are not orphaned.
- **Both `sweep` and `dreamcleanr` entry points must keep working** — `[project.scripts]`
  already maps both to `dreamcleanr.cli:main`.
- **Never commit the Ed25519 private key.** It lives only in a Cloudflare secret and the
  operator's password manager.
- **Free tier keeps `scan`, `clean` dry-run, and `report`.** Gating those is out of scope.

---

### Task 1: Vendored Ed25519 verifier

Replaces the symmetric HMAC scheme, under which anyone can mint keys — proven by calling
`generate_key("attacker@example.com")` from the shipped package and having `_verify_key`
return `True`.

**Files:**
- Create: `dreamcleanr/_ed25519.py`
- Test: `tests/test_ed25519.py`

**Interfaces:**
- Consumes: nothing (stdlib only)
- Produces: `verify(public_key: bytes, signature: bytes, message: bytes) -> bool`
  — `public_key` is 32 bytes, `signature` is 64 bytes. Returns `False` on any malformed
  input rather than raising.

- [ ] **Step 1: Write the failing test**

Test vector 2 from RFC 8032 §7.1.

```python
# tests/test_ed25519.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_ed25519.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'dreamcleanr._ed25519'`

- [ ] **Step 3: Write minimal implementation**

```python
# dreamcleanr/_ed25519.py
"""Pure-Python Ed25519 signature verification (RFC 8032).

Verify-only, stdlib-only. Vendored deliberately: `pyproject.toml` declares
`dependencies = []`, and a tool whose pitch is reclaiming disk space should not
install a ~10MB compiled crypto wheel to check a licence.

Signing lives server-side (Cloudflare Worker), where dependencies are free.
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
    # Reject points not on the curve.
    if (-x * x + y * y - 1 - _D * x * x * y * y) % _P != 0:
        return None
    return p


def _equal(p, q) -> bool:
    x1, y1, z1, _ = p
    x2, y2, z2, _ = q
    return (x1 * z2 - x2 * z1) % _P == 0 and (y1 * z2 - y2 * z1) % _P == 0


def verify(public_key: bytes, signature: bytes, message: bytes) -> bool:
    """Return True only if `signature` is a valid Ed25519 signature.

    Never raises: malformed input returns False.
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_ed25519.py -q`
Expected: PASS — 10 passed

- [ ] **Step 5: Commit**

```bash
git add dreamcleanr/_ed25519.py tests/test_ed25519.py
git commit -m "feat: vendored pure-Python Ed25519 verifier

Verify-only, stdlib-only, so pyproject dependencies stay empty.
Validated against RFC 8032 section 7.1 test vector 2."
```

---

### Task 2: Replace the licence scheme with Ed25519

**Files:**
- Modify: `dreamcleanr/license.py` (replace lines 30–75, the HMAC key derivation and
  `generate_key`/`_verify_key`)
- Test: `tests/test_license.py`

**Interfaces:**
- Consumes: `dreamcleanr._ed25519.verify(public_key, signature, message) -> bool`
- Produces:
  - `PUBLIC_KEY: bytes` (32 bytes)
  - `parse_key(key: str) -> dict | None` — returns `{"e": email, "o": order_id,
    "t": issued_at_epoch_int}` when the signature verifies, else `None`
  - `check_pro() -> bool` — unchanged name, now backed by Ed25519
  - `activate(key: str) -> dict` — **signature change**: the old `activate(key, email)`
    took an email; the email now comes from inside the signed payload. Raises
    `ValueError` on an invalid key.
  - `get_license_info() -> dict | None`, `deactivate() -> bool` — unchanged names

`generate_key()` is **removed** from the shipped package. Key minting moves server-side.
Leaving it in is what made the old scheme forgeable.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_license.py
import base64
import json
import pytest
from dreamcleanr import license as lic

# Test keypair — NOT the production key. Generated once for fixtures.
TEST_PUB = bytes.fromhex("d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a")


def _make_key(payload: dict, sig: bytes) -> str:
    p = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).rstrip(b"=")
    s = base64.urlsafe_b64encode(sig).rstrip(b"=")
    return f"SWEEP-{p.decode()}.{s.decode()}"


def test_parse_key_rejects_garbage():
    assert lic.parse_key("not-a-key") is None
    assert lic.parse_key("") is None
    assert lic.parse_key("SWEEP-onlyonepart") is None


def test_parse_key_rejects_bad_signature(monkeypatch):
    monkeypatch.setattr(lic, "PUBLIC_KEY", TEST_PUB)
    key = _make_key({"e": "a@b.com", "o": "cs_test_1", "t": 1}, b"\x00" * 64)
    assert lic.parse_key(key) is None


def test_check_pro_false_when_no_file(monkeypatch, tmp_path):
    monkeypatch.setattr(lic, "_LICENSE_FILE", tmp_path / ".sweep_license")
    assert lic.check_pro() is False


def test_check_pro_false_when_file_corrupt(monkeypatch, tmp_path):
    f = tmp_path / ".sweep_license"
    f.write_text("{not json")
    monkeypatch.setattr(lic, "_LICENSE_FILE", f)
    assert lic.check_pro() is False


def test_activate_rejects_invalid_key(monkeypatch, tmp_path):
    monkeypatch.setattr(lic, "_LICENSE_FILE", tmp_path / ".sweep_license")
    with pytest.raises(ValueError):
        lic.activate("SWEEP-bogus.bogus")


def test_generate_key_is_gone():
    # The old symmetric scheme shipped a key generator, which made every
    # licence forgeable. It must not come back.
    assert not hasattr(lic, "generate_key")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_license.py -q`
Expected: FAIL — `AttributeError: module 'dreamcleanr.license' has no attribute 'parse_key'`,
and `test_generate_key_is_gone` fails because `generate_key` still exists.

- [ ] **Step 3: Write minimal implementation**

Replace the block from `# Signing secret` through the end of `_verify_key` in
`dreamcleanr/license.py` with:

```python
import base64
import json
import time
from pathlib import Path

from ._ed25519 import verify as _ed_verify

# Ed25519 PUBLIC key. Safe to ship — it can only verify, never sign.
# Replace with the real value from Task 3's keygen before releasing.
PUBLIC_KEY = bytes.fromhex(
    "0000000000000000000000000000000000000000000000000000000000000000"
)

_KEY_PREFIX = "SWEEP-"
_LICENSE_FILE = Path.home() / ".sweep_license"


def _b64d(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def parse_key(key: str) -> dict | None:
    """Return the signed payload if `key` verifies, else None. Never raises."""
    try:
        if not key or not key.startswith(_KEY_PREFIX):
            return None
        body = key[len(_KEY_PREFIX):]
        payload_b64, _, sig_b64 = body.partition(".")
        if not payload_b64 or not sig_b64:
            return None
        payload_raw = _b64d(payload_b64)
        if not _ed_verify(PUBLIC_KEY, _b64d(sig_b64), payload_raw):
            return None
        data = json.loads(payload_raw)
        if not isinstance(data, dict) or "e" not in data:
            return None
        return data
    except Exception:
        return None


def activate(key: str) -> dict:
    """Verify and persist a licence. Raises ValueError if the key is invalid."""
    data = parse_key(key)
    if data is None:
        raise ValueError("That licence key is not valid.")
    record = {"key": key, "email": data["e"], "order": data.get("o"),
              "activated_at": int(time.time())}
    _LICENSE_FILE.write_text(json.dumps(record, indent=2))
    _LICENSE_FILE.chmod(0o600)
    return record


def check_pro() -> bool:
    """True only if a stored licence verifies right now. Never raises."""
    info = get_license_info()
    return info is not None


def get_license_info() -> dict | None:
    try:
        if not _LICENSE_FILE.exists():
            return None
        record = json.loads(_LICENSE_FILE.read_text())
        data = parse_key(record.get("key", ""))
        if data is None:
            return None
        return {"email": data["e"], "order": data.get("o"),
                "activated_at": record.get("activated_at")}
    except Exception:
        return None


def deactivate() -> bool:
    if _LICENSE_FILE.exists():
        _LICENSE_FILE.unlink()
        return True
    return False
```

Then delete any now-unused `hmac` / `hashlib` / `os` imports and the `_SALT`,
`_BASE_SECRET`, `_SIGNING_KEY`, `_HMAC_BYTES` constants.

Update `command_license_activate` in `dreamcleanr/cli.py:383` to call `activate(key)` with
one argument and print `record["email"]`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_license.py tests/test_cli.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add dreamcleanr/license.py dreamcleanr/cli.py tests/test_license.py
git commit -m "feat!: replace forgeable HMAC licence with Ed25519 verification

The old scheme derived its signing key from a literal shipped in the
source, so generate_key() let anyone mint valid keys. Removed the
generator from the package; signing is now server-side only."
```

---

### Task 3: Generate the production keypair

**Files:**
- Create: `scripts/gen_license_keypair.py`
- Modify: `dreamcleanr/license.py` (the `PUBLIC_KEY` constant)

**Interfaces:**
- Consumes: `dreamcleanr._ed25519`
- Produces: a hex public key for `license.py`, and a base64 private key for the Cloudflare
  secret `SWEEP_LICENSE_PRIVATE_KEY`.

This task is operational, not test-driven — its output is a key, not behaviour.

- [ ] **Step 1: Write the generator**

```python
# scripts/gen_license_keypair.py
"""Generate the Ed25519 keypair for Sweep Pro licences. Run ONCE.

The private key must go straight into the Cloudflare secret and a password
manager. It must never be committed, pasted into chat, or written to the repo.
"""
import base64
import secrets
import sys

sys.path.insert(0, ".")
from dreamcleanr import _ed25519 as ed  # noqa: E402
import hashlib


def public_from_private(seed: bytes) -> bytes:
    h = bytearray(hashlib.sha512(seed).digest()[:32])
    h[0] &= 248
    h[31] &= 127
    h[31] |= 64
    a = int.from_bytes(h, "little")
    p = ed._scalarmult(ed._B, a)
    x, y, z, _ = p
    zi = pow(z, ed._P - 2, ed._P)
    x, y = x * zi % ed._P, y * zi % ed._P
    out = bytearray((y | ((x & 1) << 255)).to_bytes(32, "little"))
    return bytes(out)


seed = secrets.token_bytes(32)
pub = public_from_private(seed)
print("PUBLIC  (paste into dreamcleanr/license.py PUBLIC_KEY):")
print(f'    "{pub.hex()}"')
print()
print("PRIVATE (Cloudflare secret SWEEP_LICENSE_PRIVATE_KEY — store in 1Password, never commit):")
print(f"    {base64.b64encode(seed).decode()}")
```

- [ ] **Step 2: Run it once and capture the output**

Run: `python3 scripts/gen_license_keypair.py`
Expected: two keys printed. **Store the private key in a password manager immediately.**

- [ ] **Step 3: Paste the public key into `license.py`**

Replace the zero-filled `PUBLIC_KEY` placeholder from Task 2 with the printed hex value.

- [ ] **Step 4: Verify a round trip**

Sign a test payload with the private key using any Ed25519 tool, then confirm
`parse_key()` accepts it. Expected: `parse_key` returns the payload dict.

- [ ] **Step 5: Commit (public key only)**

```bash
git add scripts/gen_license_keypair.py dreamcleanr/license.py
git commit -m "feat: production Ed25519 public key + keypair generator

Private key is stored only as a Cloudflare secret; it is not in this repo."
```

---

### Task 4: Wire the gate

The missing piece — `check_pro()` exists today but nothing calls it, so even the old
licence was never enforced.

**Files:**
- Modify: `dreamcleanr/cli.py:186` (`command_clean`) and the schedule handlers at
  `cli.py:360`/`363`
- Test: `tests/test_gate.py`

**Interfaces:**
- Consumes: `dreamcleanr.license.check_pro() -> bool`
- Produces: no new public API.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_gate.py
import argparse
import pytest
from dreamcleanr import cli


def _clean_args(**kw):
    base = dict(apply=True, output_dir=None, scope="all", mode="safe",
                json_out=None, yes=True)
    base.update(kw)
    return argparse.Namespace(**base)


def test_apply_without_licence_degrades_to_dry_run(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(cli.license, "check_pro", lambda: False)
    called = {}
    monkeypatch.setattr(cli, "apply_actions",
                        lambda *a, **k: called.setdefault("ran", True))
    rc = cli.command_clean(_clean_args(output_dir=str(tmp_path)))
    assert rc == 0, "must not error — the user still gets their dry-run"
    assert "ran" not in called, "apply_actions must NOT run without a licence"
    assert "6.99" in capsys.readouterr().out


def test_apply_with_licence_is_allowed(monkeypatch, tmp_path):
    monkeypatch.setattr(cli.license, "check_pro", lambda: True)
    args = _clean_args(output_dir=str(tmp_path))
    # Should reach the apply path rather than returning early.
    assert cli._requires_pro_or_downgrade(args) is True


def test_schedule_install_refuses_without_licence(monkeypatch, capsys):
    monkeypatch.setattr(cli.license, "check_pro", lambda: False)
    rc = cli.command_schedule_install(argparse.Namespace())
    assert rc != 0
    assert "6.99" in capsys.readouterr().out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_gate.py -q`
Expected: FAIL — `AttributeError: module 'dreamcleanr.cli' has no attribute '_requires_pro_or_downgrade'`

- [ ] **Step 3: Write minimal implementation**

Add near the top of `dreamcleanr/cli.py`:

```python
from . import license

UPGRADE_MESSAGE = (
    "\n  Sweep Pro is required to apply changes.\n"
    "  Your dry-run report above is complete and free to keep.\n\n"
    "  Unlock cleaning + scheduling — $6.99 once, no subscription:\n"
    "      https://sweep.jonlynchfinancial.com/#pro\n\n"
    "  Already bought it?  sweep license activate <YOUR-KEY>\n"
)


def _requires_pro_or_downgrade(args) -> bool:
    """True if the privileged action may proceed.

    When unlicensed we deliberately do NOT error: the user keeps their
    dry-run report and sees how to upgrade.
    """
    if license.check_pro():
        return True
    args.apply = False
    print(UPGRADE_MESSAGE)
    return False
```

In `command_clean`, replace line 186 (`dry_run = not args.apply`) with:

```python
    if args.apply:
        _requires_pro_or_downgrade(args)
    dry_run = not args.apply
```

In `command_schedule_install`, add as the first statement:

```python
    if not license.check_pro():
        print(UPGRADE_MESSAGE)
        return 1
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_gate.py tests/test_cli.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add dreamcleanr/cli.py tests/test_gate.py
git commit -m "feat: gate clean --apply and schedule behind Sweep Pro

Unlicensed --apply degrades to dry-run and exits 0 rather than failing,
so the user keeps the report they already generated."
```

---

### Task 5: Dependency guard

**Files:**
- Test: `tests/test_distribution.py` (existing file — append)

**Interfaces:** none.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_distribution.py
import tomllib
from pathlib import Path


def test_runtime_dependencies_stay_empty():
    """Sweep must install nothing extra.

    A disk-cleaning tool that pulls a ~10MB compiled crypto wheel to check a
    licence undermines its own pitch, and breaks `pip install --user` on
    machines without build tooling. The Ed25519 verifier is vendored instead.
    """
    data = tomllib.loads(Path("pyproject.toml").read_text())
    assert data["project"]["dependencies"] == [], (
        "dependencies must stay empty — vendor it or do without"
    )
```

- [ ] **Step 2: Run test to verify it passes**

Run: `python3 -m pytest tests/test_distribution.py -q`
Expected: PASS (it guards the current state; it should be green from the start)

- [ ] **Step 3: Prove the guard actually fires**

Temporarily add `dependencies = ["cryptography"]` to `pyproject.toml`, re-run the test,
confirm it FAILS, then revert. A guard never seen to fail is not a guard.

- [ ] **Step 4: Commit**

```bash
git add tests/test_distribution.py
git commit -m "test: guard that runtime dependencies stay empty"
```

---

### Task 6: Stripe webhook signs and emails the licence

**Files:**
- Modify: `~/stripe-onetime-checkout/functions/api/stripe-webhook.js`
- Create: `~/stripe-onetime-checkout/functions/_lib/license.js`
- Test: `~/stripe-onetime-checkout/test/license.test.mjs`

**Interfaces:**
- Consumes: `SWEEP_LICENSE_PRIVATE_KEY` (base64 seed, Cloudflare secret) and
  `RESEND_API_KEY`
- Produces: a licence string of the exact shape Task 2's `parse_key` accepts:
  `SWEEP-<b64url(payload)>.<b64url(sig)>` where payload is
  `{"e":email,"o":order_id,"t":epoch_seconds}` with **no whitespace**.

- [ ] **Step 1: Write the failing test**

```javascript
// test/license.test.mjs
import { test } from "node:test";
import assert from "node:assert";
import { mintLicense } from "../functions/_lib/license.js";

const SEED_B64 = "3Ac5S8kZk1e4vI0Qm0m1Zk0m1Zk0m1Zk0m1Zk0m1Zk0="; // test seed only

test("mints a key in the SWEEP-payload.signature shape", async () => {
  const key = await mintLicense(SEED_B64, "buyer@example.com", "cs_test_123", 1735689600);
  assert.ok(key.startsWith("SWEEP-"), "must carry the SWEEP- prefix");
  const [payload, sig] = key.slice(6).split(".");
  assert.ok(payload && sig, "must have both payload and signature parts");
  const decoded = JSON.parse(Buffer.from(payload, "base64url").toString());
  assert.deepStrictEqual(decoded, { e: "buyer@example.com", o: "cs_test_123", t: 1735689600 });
});

test("normalises the email to lowercase", async () => {
  const key = await mintLicense(SEED_B64, "Buyer@Example.COM", "cs_1", 1);
  const decoded = JSON.parse(Buffer.from(key.slice(6).split(".")[0], "base64url").toString());
  assert.strictEqual(decoded.e, "buyer@example.com");
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ~/stripe-onetime-checkout && node --test test/license.test.mjs`
Expected: FAIL — cannot find module `../functions/_lib/license.js`

- [ ] **Step 3: Write minimal implementation**

```javascript
// functions/_lib/license.js
// Signs Sweep Pro licences with Ed25519 via WebCrypto (available in Workers).

function b64urlFromBytes(bytes) {
  return Buffer.from(bytes).toString("base64url");
}

// Build a PKCS#8 wrapper around the raw 32-byte Ed25519 seed so WebCrypto
// will import it. The prefix is the fixed ASN.1 header for Ed25519 keys.
function pkcs8FromSeed(seed) {
  const prefix = Buffer.from("302e020100300506032b657004220420", "hex");
  return Buffer.concat([prefix, Buffer.from(seed)]);
}

export async function mintLicense(privateKeyB64, email, orderId, issuedAt) {
  const seed = Buffer.from(privateKeyB64, "base64");
  const key = await crypto.subtle.importKey(
    "pkcs8", pkcs8FromSeed(seed), { name: "Ed25519" }, false, ["sign"]
  );
  const payload = JSON.stringify({
    e: String(email).trim().toLowerCase(),
    o: orderId,
    t: issuedAt,
  });
  const payloadBytes = new TextEncoder().encode(payload);
  const sig = await crypto.subtle.sign({ name: "Ed25519" }, key, payloadBytes);
  return `SWEEP-${b64urlFromBytes(payloadBytes)}.${b64urlFromBytes(new Uint8Array(sig))}`;
}
```

In `functions/api/stripe-webhook.js`, inside the `checkout.session.completed` branch:

```javascript
import { mintLicense } from "../_lib/license.js";

// ... after the event signature is verified:
const session = event.data.object;
const email = session.customer_details?.email || session.customer_email;
const licenseKey = await mintLicense(
  env.SWEEP_LICENSE_PRIVATE_KEY, email, session.id,
  Math.floor(Date.now() / 1000)
);

const res = await fetch("https://api.resend.com/emails", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${env.RESEND_API_KEY}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    // MUST stay on send.jonlynchfinancial.com: Resend signs
    // d=send.jonlynchfinancial.com and the domain's DMARC is adkim=s,
    // so an apex From would be rejected outright.
    from: "Sweep <noreply@send.jonlynchfinancial.com>",
    to: [email],
    subject: "Your Sweep Pro licence key",
    text: `Thanks for buying Sweep Pro.\n\nActivate it with:\n\n    sweep license activate ${licenseKey}\n\nThis key is yours forever — no subscription, no expiry.\n`,
  }),
});
if (!res.ok) {
  // Return 500 so Stripe retries rather than silently losing the licence.
  return new Response("licence email failed", { status: 500 });
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd ~/stripe-onetime-checkout && node --test test/`
Expected: PASS — including the existing `webhook.test.mjs` and `checkout.test.mjs`

- [ ] **Step 5: Verify a real key against the Python verifier**

Mint one with the **production** private key, then confirm the CLI accepts it:

```bash
python3 -c "
import sys; sys.path.insert(0,'.')
from dreamcleanr.license import parse_key
print(parse_key('SWEEP-...paste minted key...'))
"
```
Expected: prints the payload dict, not `None`. This is the one cross-language check that
proves the whole chain — do not skip it.

- [ ] **Step 6: Commit**

```bash
cd ~/stripe-onetime-checkout
git add functions/_lib/license.js functions/api/stripe-webhook.js test/license.test.mjs
git commit -m "feat: mint and email Ed25519 Sweep Pro licences on checkout"
```

---

### Task 7: Site copy — one price and a real checkout link

**Files:**
- Modify: `~/jlfg-marketing/dreamcleanr/index.html`,
  `~/jlfg-marketing/dreamcleanr/quickstart/index.html`

Work in a git worktree off `origin/main` — the `~/jlfg-marketing` working tree is on
`feat/forge-clerk-auth` with uncommitted changes and must not be deployed from.

**Interfaces:** none.

- [ ] **Step 1: Replace every price with $6.99**

The page currently shows `$24`, `$29`, `$49`, `$29.99`, and `$49.99`. All become `$6.99`.
"Buy Sweep Pro — $29 one-time" becomes "Buy Sweep Pro — $6.99 one-time".

- [ ] **Step 2: Point the buy CTA at the real checkout**

The `#pro` anchor becomes the deployed Stripe checkout URL. Verify no `href="#pro"`
remains on a button whose label contains "Buy".

- [ ] **Step 3: Make the Mac claim honest**

"Download free for Mac →" implies a GUI app; there is no `.dmg` in any release. Change to
"Install the macOS CLI →".

- [ ] **Step 4: Verify**

```bash
grep -oE '\$[0-9]+(\.[0-9]{2})?' dreamcleanr/index.html | sort -u
```
Expected: only `$6.99`.

- [ ] **Step 5: Commit**

```bash
git add dreamcleanr/index.html dreamcleanr/quickstart/index.html
git commit -m "copy: single \$6.99 price, real checkout link, honest macOS CLI framing"
```

---

## Deployment checklist (operator, not agent)

- [ ] Store the Ed25519 private key in a password manager
- [ ] `wrangler pages secret put SWEEP_LICENSE_PRIVATE_KEY`
- [ ] `wrangler pages secret put RESEND_API_KEY`
- [ ] `wrangler pages secret put STRIPE_WEBHOOK_SECRET`
- [ ] Create the $6.99 Stripe product **in test mode first**
- [ ] Deploy `stripe-onetime-checkout` (it has no git remote yet — create one)
- [ ] Register the webhook endpoint in Stripe
- [ ] End-to-end test purchase in test mode; confirm the email arrives and the key activates
- [ ] Switch to live keys
- [ ] Cut a release so users actually receive the gated build — **the gate does nothing
      until a new wheel ships**; the published v0.3.6 has no licensing at all
- [ ] Deploy the site copy cd-first via `jlfg-pages-deploy`

## Decisions still open

1. **Existing users.** 125 wheels are already out with `--apply` ungated. Grandfather
   them, or let the next release begin enforcing?
2. **Anonymous licences.** The payload carries the purchase email. Acceptable, or should
   it be order-id only for privacy-conscious developers?
