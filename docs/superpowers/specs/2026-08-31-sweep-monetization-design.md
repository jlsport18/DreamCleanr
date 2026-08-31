# Sweep Pro monetization — design

Date: 2026-08-31
Status: approved for implementation planning

## Problem

Sweep/DreamCleanr works end to end and has real usage (124 downloads of the v0.3.6
wheel), but it cannot take money. Verified 2026-08-31 by installing the published wheel
into a clean venv and exercising it:

- **There is no checkout link anywhere.** The landing page and quickstart both advertise
  "Buy Sweep Pro — $29 one-time", but the only hrefs behind those CTAs are the in-page
  anchor `#pro` and an obfuscated mailto. No Stripe/Paddle/Gumroad/LemonSqueezy URL
  exists on either page. A customer who decides to buy has no way to do so.
- **There is no licensing code in the shipped package.** All 8 `.py` files were searched
  for `licen`, `activat`, `stripe`, `entitle`, `paywall`, `subscription`, `payment`,
  `upgrade` — zero hits each. `clean --apply` and `schedule`, both advertised as Pro,
  are ungated.
- The page shows five different prices: $24, $29, $49, $29.99, $49.99.
- The CTA says "Download free for Mac →" but no release (v0.3.2–v0.3.6) has ever
  contained a `.dmg`. The product is a CLI.

The free path itself is healthy and is not the problem: public repo, `install.sh` returns
200 anonymously, wheel installs clean, `scan` produces a real snapshot, `clean` dry-runs
and renders a 29KB HTML report.

## Decision: what Pro buys

**Pro gates `clean --apply` and `schedule` — features that already work today.**

Free keeps `scan`, the dry-run preview, and the HTML report. That matches the existing
"Scan free. Pay only to clean." positioning without building anything new, so revenue can
start in days rather than after a feature-build phase.

Explicitly **not** chosen: gating the advertised-but-unbuilt developer-mode targets
(Xcode DerivedData, node_modules, Docker image layers, AI model caches). `core.py`
mentions only `docker`; the rest do not exist. Gating them would put a build phase before
the revenue phase. They remain a later addition to Pro at the same price.

## Decision: offline signed licenses

License validation is **offline**. An Ed25519 signature is verified locally; no network
call is made at runtime.

Rejected: an online key-check endpoint. It requires an always-up Worker plus KV, adds a
network dependency to a *local disk-cleaning tool*, and its failure mode is paying
customers being locked out when the endpoint is unavailable. At $4.99 that operating
burden exceeds the revenue it protects.

The threat model at this price is "someone shares a key." That is accepted. Anyone
willing to defeat a signature check was never a customer.

### Deliberately superseding the existing spec

`AUTH_BILLING_ENTITLEMENTS_SPEC.md` proposes GitHub OAuth, magic-link fallback,
short-lived JWTs, per-device refresh-token rotation, and hosted entitlement reads. That
document is marked `future incubation track` and states it "does not authorize auth,
billing, or hosted entitlements in the current product phase."

**This design intentionally does not follow it.** That stack costs more to build and
operate than a $4.99 one-time purchase can return. The one element retained is its
product philosophy — *local-first, GitHub-first, free at the core, one-time Pro.*

This paragraph exists so the decision is not re-litigated in a later session.

## Constraint: the wheel must stay dependency-free

`pyproject.toml` declares `dependencies = []`. For a tool whose pitch is reclaiming disk
space, installing a compiled ~10MB `cryptography` wheel to check a licence would be
self-defeating, and it would weaken the `pip install --user` path on machines without
build tooling.

**Therefore: pure-Python Ed25519 verification, vendored into the package (~60 lines,
verify-only).** Signing happens server-side in the Worker, where dependencies are free.
`dependencies = []` must remain true after this work — treat any addition as a design
violation.

## Architecture

```
Stripe Checkout  ──webhook──▶  Cloudflare Pages Function
(existing project)              stripe-webhook.js
                                      │ signs {email, order_id, issued_at}
                                      │ with Ed25519 PRIVATE key (CF secret)
                                      ▼
                                  Resend  ──email──▶  customer
                                                          │  licence string
                                                          ▼
                                              dreamcleanr activate <key>
                                                          │ verifies with PUBLIC key
                                                          │ (constant in the wheel)
                                                          ▼
                                            ~/.config/dreamcleanr/license
                                                          │
                            ┌─────────────────────────────┴──────────────┐
                            ▼                                            ▼
                   cli.py:186  dry_run = not args.apply          schedule command
                   (gate here)                                   (gate here)
```

### Components

**1. Licence format.** `SWEEP-<base64url(payload)>.<base64url(signature)>` where payload
is compact JSON `{"e": email, "o": order_id, "t": issued_at}`. Human-pasteable, single
line, no PII beyond the purchase email.

**2. `dreamcleanr/licensing.py`** (new, no third-party imports)
- `verify(key: str) -> Licence | None` — Ed25519 verify against the embedded public key
- `load() -> Licence | None` — read `~/.config/dreamcleanr/license`, verify, cache in-process
- `is_pro() -> bool`
- Embedded `PUBLIC_KEY` constant.

**3. `dreamcleanr activate` subcommand.** Takes the licence string, verifies, writes to
`~/.config/dreamcleanr/license` with mode `600`, prints the licensed email. A bad key
exits non-zero with a clear message. `activate --status` reports current state.

**4. Two gate points.**
- `cli.py:186` — where `dry_run = not args.apply` is computed. If `--apply` is requested
  without a valid licence: print the upgrade message, keep `dry_run = True`, exit 0. The
  user still gets their dry-run report; they are not left empty-handed.
- The `schedule` command — refuse install without a licence, exit non-zero.

`core.py:1648 apply_actions()` is **not** gated. Gating is a CLI-layer concern; keeping
core pure preserves testability and avoids a second enforcement path drifting from the
first.

**5. Checkout.** Reuse `~/stripe-onetime-checkout` — a Cloudflare Pages project that
already contains `functions/api/create-checkout-session.js`,
`functions/api/stripe-webhook.js`, `functions/_lib/stripe.js`, and tests for both. It has
no git remote and has never been deployed. Work needed: create the remote, add licence
signing to the webhook handler, wire Resend delivery, set secrets, deploy.

**6. Delivery.** Resend, which is confirmed working as of 2026-08-31. The `From:` **must**
remain `@send.jonlynchfinancial.com` — Resend signs `d=send.jonlynchfinancial.com` and the
domain's DMARC is `p=reject; adkim=s`, so an apex From would be rejected.

## Error handling

| Case | Behaviour |
|---|---|
| No licence file | `--apply` degrades to dry-run + upgrade message, exit 0 |
| Corrupt/forged licence | Treated as absent; same degrade path. Never crash. |
| Unreadable licence file (permissions) | Treated as absent; warn on stderr |
| `activate` with bad key | Clear error, exit 1, existing licence untouched |
| Webhook fires twice for one order | Same `order_id` → same signature; email may arrive twice. Acceptable. |
| Resend delivery fails | Webhook logs and returns 500 so Stripe retries |

Clock skew is not a factor: `issued_at` is recorded but licences do not expire.

## Testing

- **Unit:** `verify()` accepts a known-good licence, rejects tampered payload, tampered
  signature, truncated input, and empty string. Fixtures generated from a throwaway
  test keypair, not the production one.
- **Gate:** `--apply` without licence stays dry-run and exits 0; with licence, applies.
  `schedule` refuses without licence. Asserted on exit code *and* on whether
  `apply_actions` was called.
- **Dependency guard:** a test asserting `dependencies == []` in `pyproject.toml`, so a
  future contributor cannot quietly add one.
- **Webhook:** extend the existing `test/webhook.test.mjs` to assert a signed licence is
  produced for `checkout.session.completed` and that the signature verifies with the
  public key.
- **End-to-end (manual, once):** Stripe test-mode purchase → email arrives → paste key →
  `--apply` works.

## Copy and positioning changes

These are required for the product to be honest, and are **not** optional polish:

1. **One price: $4.99.** Remove $24 / $29 / $49 / $29.99 / $49.99. "Buy Sweep Pro — $29
   one-time" becomes $4.99.
2. **A real checkout link.** The `#pro` anchor must become the Stripe checkout URL.
3. **"Download free for Mac →"** must stop implying a GUI app. It is a macOS CLI; say so.
   Either ship the DMG the `dreamcleanr-mac-builder` job was built to produce, or change
   the words. This spec changes the words.
4. **Rebrand consistency** is out of scope here but noted: the binary is `dreamcleanr`,
   the package is `dreamcleanr`, and the HTML report says "DreamCleanr Cleanup Receipt",
   while the site says Sweep. Renaming the published command is a breaking change for
   existing users and deserves its own decision.

## Sequencing

**gate → checkout → copy.** Content and positioning work cannot start revenue while the
two blockers stand. Ryze-authored positioning and blog content is genuinely additive but
must follow, not lead — otherwise content activity reads as monetization progress when
no money can change hands.

## Out of scope

- Platform detection for "Mac only" — it is already a macOS CLI with a macOS LaunchAgent.
  That is a positioning change, not an engineering one.
- Refunds, licence revocation, seat management, subscriptions.
- The developer-mode cleanup targets.
- Renaming the `dreamcleanr` command to `sweep`.
- Shipping a `.dmg`.

## Open questions for the operator

1. **Which Stripe account and mode?** Prior sessions recorded a leaked `service_role`
   incident and the fact that a Stripe object ID does not encode test vs live. Confirm
   the account and start in **test mode**.
2. **Purchase email as the licence identity** — acceptable, or should the licence be
   anonymous (order_id only)? Anonymous is friendlier to privacy-conscious developers;
   email makes support and re-issue possible.
3. **Existing free users.** 124 wheels are already out with `--apply` ungated. Grandfather
   them, or let the next release start enforcing?
