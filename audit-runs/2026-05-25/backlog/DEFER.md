# Deferred — next runs

## High-value, do next (in the Python CLI — fastest ROI)

- **QUAR-1 — Quarantine-with-restore.** The brief's #1 moat (reversibility) and the bridge
  to native APFS staging. Recommended shape: `--quarantine` flag (`mv` to a staging dir +
  `dreamcleanr restore`/`purge`), default-on for `max` only. *Open decision:* immediate space
  vs. recoverability TTL (7-day Free / 30-day Pro per brief).
- **MODEL-1 — Reclaim model caches (HF/Ollama).** The market wedge is 20GB+ of model/dataset
  caches that are currently *visibility-only* (`cleanup_ready=False`). Age- and reference-aware
  cleanup here is the single biggest reclaim the tool can't yet do.
- **ROBUST-1 — PID-identity re-verify before SIGTERM** (kill-the-right-process safety).
- **WEB-1 — Soft-404 fix.** `dreamcleanr.jonlynchfinancial.com` returns 200+homepage for every
  unknown path → set CF Pages `not_found_handling` to "404 page". Separate project; needs
  dashboard/API; portfolio deploy-risk — do deliberately.

## Medium

- **ROBUST-2** run lockfile · **ROBUST-3** to_dict field-parity test · **CFG-1** user config file.

## Native macOS app (NAT-1…NAT-10) — roadmap, not this quarter's CLI work

Deferred because the native side is an 887-LOC SwiftUI prototype, not a shipping app; these
are greenfield build tickets, not defects. Sequence: NAT-5 (zero-network audit, cheap) →
NAT-9 (instrument) → NAT-2 (sandbox+helper) → NAT-1/QUAR-1 (staging) → NAT-3 (Sparkle) →
NAT-7/NAT-8 (catalog + StoreKit) → NAT-4/NAT-6/NAT-10 (surfaces, Universal 2, FSEvents).
**Prerequisite for a faithful native audit: an actual Strategic Brief in `docs/strategy/`.**

## Pricing/GTM (operator decisions, not code)

- Day-one Homebrew tap (recommended) · Team price $99/yr-per-5 vs $199 · optional $19/yr on
  Pro (recommended defer — conflicts with one-time stance). From `MARKET_RESEARCH_MEMO.md`.
