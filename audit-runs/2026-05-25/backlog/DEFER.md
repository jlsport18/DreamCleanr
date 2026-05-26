# Deferred — next runs

## Shipped since this file was first written
- **QUAR-1 → done, lightweight.** Replaced the custom staging/TTL system with the macOS
  Trash net (C, `--trash`), per the "lightweight" north star. Native APFS staging stays NAT-1.
- **MODEL-1 → partially done.** Smart *surfacing* (model_data vs regenerable, staleness,
  reclaimable estimate, recommendation) shipped + regenerable-cache reclaim in max (A).

## High-value, do next (in the Python CLI — fastest ROI)

- **MODEL-2 — Per-tool model pruning.** The remaining wedge: GC *within* model stores —
  Hugging Face old revisions/unused blobs (`huggingface-cli delete-cache` semantics), Ollama
  orphaned layers/old tags. Per-tool cache-structure logic; deferred deliberately (deleting a
  20GB in-use model is the worst regression). Surfaced today as "review."
- **PERF-1 — Batch PID re-verify.** ROBUST-1's `process_args` shells out `ps -p` per process
  in apply; reuse the single `ps -axo` from `list_processes` if the stale list ever grows.
- **WEB-1 — Soft-404 fix.** `dreamcleanr.jonlynchfinancial.com` returns 200+homepage for every
  unknown path → set CF Pages `not_found_handling` to "404 page". Separate project; needs
  dashboard/API; portfolio deploy-risk — do deliberately.

## Medium

- **CFG-1** user config file (custom protected/safe paths, per-family flags).

## Native macOS app (NAT-1…NAT-10) — roadmap, not this quarter's CLI work

Deferred because the native side is an 887-LOC SwiftUI prototype (real code — 42 types: 1
actor, 4 classes, 22 funcs, 15 structs across `apple/Sources` + `macos/DreamCleanrMenubar`),
not a shipping app; these are greenfield build tickets, not defects. A faithful native audit
must read those Swift sources (this run inferred scope from the package layout + READMEs).
Sequence: NAT-5 (zero-network audit, cheap) →
NAT-9 (instrument) → NAT-2 (sandbox+helper) → NAT-1/QUAR-1 (staging) → NAT-3 (Sparkle) →
NAT-7/NAT-8 (catalog + StoreKit) → NAT-4/NAT-6/NAT-10 (surfaces, Universal 2, FSEvents).
**Prerequisite for a faithful native audit: an actual Strategic Brief in `docs/strategy/`.**

## Pricing/GTM (operator decisions, not code)

- Day-one Homebrew tap (recommended) · Team price $99/yr-per-5 vs $199 · optional $19/yr on
  Pro (recommended defer — conflicts with one-time stance). From `MARKET_RESEARCH_MEMO.md`.
