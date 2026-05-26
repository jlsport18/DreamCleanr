# DreamCleanr Strategic Backlog — 2026-05-25

Sorted by severity, then effort (XS→L). Evidence cites real files. "Brief" = in-repo
strategy docs (see SCOPE.md). Native-app tickets are **roadmap** (the app is an 887-LOC
prototype), not defects.

## Critical

| ID | Title | Eff | Evidence | Note |
| --- | --- | --- | --- | --- |
| TIER-1 | Move wholesale `~/Library/Caches` sweep to `max` | XS | `core.py` `plan_cleanup`, `remove_unprotected_library_caches` | Default+daily job wiped every app's cache. **Shipped.** |
| TIER-2 | Make `safe` mode preview-only | XS | `core.py` `plan_cleanup` | `safe --apply` used to delete caches. **Shipped.** |
| GATE-1 | Confirm before `--apply`; require `--yes` non-interactive | S | `cli.py` `command_clean`, `scheduler.py` | No prompt before destructive apply. **Shipped.** |

## High

| ID | Title | Eff | Evidence | Note |
| --- | --- | --- | --- | --- |
| DOC-1 | Fix broken `--dry-run` example + document tiers | XS | `README.md:81` | argparse rejects `--dry-run`. **Shipped.** |
| SAFE-1 | Symlink-safe deletes | XS | `core.py` `path_delete` | rmtree on symlinked dir raised; could follow links out of tree. **Shipped.** |
| ROBUST-1 | Re-verify PID identity before SIGTERM | S | `core.py` `apply_actions`/`terminate_process` | Snapshot→apply gap; recycled PID could kill an unrelated process. Defer. |
| MODEL-1 | Make HF/Ollama detectors cleanup-capable (age/size aware) | M | `core.py` `detector_registry` (`cleanup_ready=False`) | The market wedge (20GB+ model caches) is currently visibility-only. Defer. |
| QUAR-1 | Quarantine-with-restore (reversibility moat) | M | `core.py` `path_delete`; Brief §moats | Hard-delete today; staging bin is the brief's #1 moat + bridge to native APFS staging. Defer. |
| WEB-1 | Fix site-wide soft-404 on dreamcleanr.jonlynchfinancial.com | XS | live: any unknown path → 200+homepage | CF Pages `not_found_handling`=SPA. Separate project; needs dashboard. Defer. |

## Medium

| ID | Title | Eff | Evidence | Note |
| --- | --- | --- | --- | --- |
| RCPT-1 | Stop receipts inflating reclaimed bytes | XS | `core.py` `build_cleanup_report` | `max(host-delta, planned)` overstated. **Shipped** (bundled into TIER commit). |
| ROBUST-2 | Run lock to prevent concurrent destructive runs | S | `scheduler.py` + `cli.py` | Scheduled + manual run can overlap on same paths. Defer. |
| ROBUST-3 | Field-parity test for `CleanupReport.to_dict` | XS | `models.py:133` | Hand-maintained dict; add-a-field-forget risk. Defer. |
| CFG-1 | User config: custom protected/safe paths, per-family flags | M | everything hardcoded in `core.py` | Power-dev ICP will want to extend detectors. Defer. |

## Native macOS app — roadmap (build plan, not defects)

The brief's vision; the native side is a SwiftUI prototype over the CLI. Sequenced:

| ID | Title | Eff | Brief § |
| --- | --- | --- | --- |
| NAT-1 | APFS `clonefile` staging bin (depends QUAR-1) | L | reversibility moat |
| NAT-2 | App Sandbox + Hardened Runtime + SMAppService helper | L | engineering/security |
| NAT-3 | Sparkle 2 (EdDSA, self-hosted appcast) + notarization | M | distribution |
| NAT-4 | App Intents + Menu Bar Extra + Widgets | M | integration/polish |
| NAT-5 | Zero-network dependency audit (no analytics SDKs; MetricKit) | S | zero-network moat |
| NAT-6 | Universal 2 binary + macOS 13+ deployment target | M | performance |
| NAT-7 | Profile DSL + signed, versioned catalog (Cloud Profile Catalog) | L | $5/mo tier |
| NAT-8 | StoreKit 2 receipt validation + tier gating | M | monetization ladder |
| NAT-9 | OSSignpost instrumentation + perf targets (§4.1) | S | performance |
| NAT-10 | FSEvents incremental scan (full→diff) | M | performance |
