# Re-tier aggressive cleanup + close CLI safety gaps

## Summary

Re-characterizes DreamCleanr's cleanup tiers so the **default (`balanced`) and the unattended
daily job stay fast but conservative**, while preserving every bit of cleaning power in `max`.
The broad `~/Library/Caches` sweep — which previously ran in the default tier *and* even in
`safe` — is now `max`-only. `safe` is now a true preview (never deletes), and destructive
`--apply` now requires confirmation (or `--yes` for the scheduled job). Also fixes a broken
README example, makes deletes symlink-safe, and stops receipts overstating reclaimed bytes.

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

## Verification

- [x] `python -m unittest discover -s tests` → **38 pass** (was 33).
- [x] `compileall` clean.
- [x] `clean --mode balanced` previews (the corrected README command).
- [x] `--apply` without `--yes` in a non-interactive shell **refuses, writes nothing**.
- [x] No new dependencies; no network calls; pure-Python stdlib only.
- [x] Did **not** run `--apply --yes` on the dev machine (would delete real caches).

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
