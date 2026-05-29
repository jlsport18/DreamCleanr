# Memory-first reclaim + re-tiered safety, faster scans, Trash net, smart caches

## Summary

A multi-part upgrade toward a memory-first dev-AI cleaner:

- **Memory-first (new primary function):** honest `vm_stat` RAM baseline (inactive/cached
  labeled kernel-managed, never counted as "wasted"), `ollama ps` loaded-model detection, and a
  **"maximum reclaimable" ceiling** surfaced as the first CLI line — *"can reclaim up to X RAM and
  Y disk right now"* — as a sum of **named, verb-bearing sources** (never an unattributed total).
- **Re-tiered safety:** the broad `~/Library/Caches` sweep moved out of the default `balanced`
  (and the unattended daily job) into `max`-only; `safe` is now a true preview; interactive
  `--apply` confirms while scripted/scheduled runs proceed (installed LaunchAgent keeps working).
- **Faster scans** (parallel `du`), **Trash safety net** (`--trash`, default-on for `max`,
  restorable via Finder), and **smart caches** (model_data never auto-deleted; regenerable caches
  reclaimed in max, active-project-guarded).
- Fixes: broken README `--dry-run` example, symlink-safe deletes, honest receipt totals, and
  `parse_size_to_bytes` ("40GB" parsed as 0).

No cleaning power was removed — it was re-characterized and made safer + reversible.

No cleaning capability was removed — it was re-tiered.

## Linked strategy (in-repo brief surrogate)

- `DREAMCLEANR_MASTER_STRATEGY.md` — "doesn't break workflows" + reversibility moat.
- `MARKET_RESEARCH_MEMO.md` — dev-safety depth as the differentiator.
- Full analysis: `audit-runs/2026-05-25/raw/mode-tiering-analysis.md`.

## Changelog (one ticket → one commit)

| Commit | Severity | Files | Tests |
| --- | --- | --- | --- |
| `feat(core): re-tier aggressive deletions to max-only; safe is preview` | Critical | `core.py`, `test_core.py` | +2 (`library_sweep_is_max_only`, `safe_mode_is_preview_only`) |
| `feat(cli): confirm before destructive --apply; require --yes when non-interactive` | Critical | `cli.py`, `scheduler.py`, `test_cli.py` | +3 (refuse / yes-skips / decline-preview) |
| `docs: fix broken --dry-run example; document cleanup tiers` | High | `README.md` | n/a |
| `fix(cli): confirm only for interactive --apply` | Critical | `cli.py`, `README.md` | (revises gate to not break installed scheduler) |
| `security(core): guard termination against PID reuse` | High | `core.py`, `test_core.py` | +2 |
| `feat(cli): exclusive run lock` | Medium | `cli.py`, `test_cli.py` | +1 |
| `test(models): assert to_dict field parity` | Medium | `test_distribution.py` | +1 |
| `perf(core): parallelize path sizing for faster scans` | High | `core.py`, `test_core.py` | +1 |
| `feat(cli): macOS Trash safety net for deletes` | High | `core.py`, `cli.py`, `README.md`, tests | +4 |
| `feat(core): smart model-cache reclaim (surface + regenerable-only)` | High | `core.py`, `models.py`, `reporting.py`, `test_core.py` | +4 |
| `feat(core): memory-first reclaim — vm_stat + loaded-model + ceiling` | High | `core.py`, `cli.py`, `test_core.py` | +5 |

## Verification

- [x] `python -m unittest discover -s tests` → **56 pass** (was 33).
- [x] Real scan on this Mac: surfaces 885 MB node regenerable cache ("safe to clear in max"); Ollama/HF model data surfaced for review, never auto-deleted; HTML report renders with new fields.
- [x] `compileall` clean.
- [x] `clean --mode balanced` previews (the corrected README command).
- [x] Interactive `--apply` prompts; non-interactive `--apply` proceeds — **no regression for the installed daily LaunchAgent** (verified this Mac's plist lacks `--yes`; the gate no longer requires it).
- [x] No new dependencies; no network calls; pure-Python stdlib only.
- [x] Did **not** run a real `--apply` deletion on the dev machine (only `safe`/dry-run).

## Open questions (human judgment)

- **Reversibility (QUAR-1):** add quarantine-with-restore? Trade-off: immediate space vs. a
  recoverable TTL window. Recommended default-on for `max` only.
- **Scheduled default tier:** keep daily job on `balanced` (now safe)? Users wanting the deep
  sweep can `schedule install --mode max`.
- **Model-cache cleanup (MODEL-1):** the biggest reclaim (HF/Ollama, 20GB+) is still
  visibility-only — green-light building it?

## Not in this PR
Native macOS app dimensions (APFS staging, Sparkle, StoreKit, sandbox/helper, …) are roadmap
build tickets — see `backlog/DEFER.md`. A faithful native audit needs a real Strategic Brief
in `docs/strategy/`.
