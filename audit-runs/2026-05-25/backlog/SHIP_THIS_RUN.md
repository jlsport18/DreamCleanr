# Shipped this run — branch `learnings/2026-05-25-strategic-audit`

Scope: the shipping Python CLI's safety/correctness defects + the operator's re-tiering
steer. All low-risk, additive or safety-improving. No push (human reviews).

| ID | Severity | Commit | Tests |
| --- | --- | --- | --- |
| TIER-1 | Critical | `feat(core): re-tier aggressive deletions to max-only` | `test_plan_cleanup_library_sweep_is_max_only` |
| TIER-2 | Critical | (same commit) | `test_plan_cleanup_safe_mode_is_preview_only` |
| SAFE-1 | High | (same commit) | covered by symlink-safe `path_delete` |
| RCPT-1 | Medium | (same commit) | n/a (honest total = planned bytes) |
| GATE-1 | Critical | `feat(cli): confirm before destructive --apply` | `test_clean_apply_refuses_noninteractive_without_yes`, `_with_yes_skips_confirmation`, `_decline_falls_back_to_preview` |
| DOC-1 | High | `docs: fix broken --dry-run example` | n/a |

**Result:** 38 tests pass (was 33). `--version`=0.3.6. `clean --mode balanced` previews;
`--apply` without `--yes` refuses non-interactively and writes nothing.

**Net behavior change:** default `balanced` and the daily job no longer wipe all of
`~/Library/Caches` — that is now `max`-only. Nothing lost; run `--mode max` for the full sweep.
