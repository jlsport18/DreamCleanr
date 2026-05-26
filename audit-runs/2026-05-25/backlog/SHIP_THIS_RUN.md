# Shipped this run — branch `learnings/2026-05-25-strategic-audit`

Scope: the shipping Python CLI's safety/correctness defects + the operator's re-tiering
steer. All low-risk, additive or safety-improving. No push (human reviews).

| ID | Severity | Commit | Tests |
| --- | --- | --- | --- |
| TIER-1 | Critical | `feat(core): re-tier aggressive deletions to max-only` | `test_plan_cleanup_library_sweep_is_max_only` |
| TIER-2 | Critical | (same commit) | `test_plan_cleanup_safe_mode_is_preview_only` |
| SAFE-1 | High | (same commit) | covered by symlink-safe `path_delete` |
| RCPT-1 | Medium | (same commit) | n/a (honest total = planned bytes) |
| GATE-1 | Critical | `feat(cli): confirm before destructive --apply` (+ `fix(cli)` follow-up) | `test_clean_apply_noninteractive_proceeds_without_prompt`, `_with_yes_skips_confirmation`, `_decline_falls_back_to_preview` |
| DOC-1 | High | `docs: fix broken --dry-run example` | n/a |
| ROBUST-1 | High | `security(core): guard termination against PID reuse` | `test_apply_blocks_terminate_when_pid_identity_changed`, `_marks_already_exited_process_terminated` |
| ROBUST-2 | Medium | `feat(cli): exclusive run lock` | `test_clean_apply_skipped_when_report_dir_locked` |
| ROBUST-3 | Medium | `test(models): assert to_dict field parity` | `test_cleanup_report_to_dict_covers_every_field` |
| B (perf) | High | `perf(core): parallelize path sizing` | `test_du_bytes_many_parallel_sizes_and_dedups` |
| C (trash) | High | `feat(cli): macOS Trash safety net` | `test_path_delete_trash_*`, `test_trash_defaults_*`, `test_no_trash_flag_*` |
| A (smart) | High | `feat(core): smart model-cache reclaim` | `test_detector_findings_carry_reclaim_metadata`, `test_plan_cleanup_max_*` (reclaim / skip guarded-fresh-model / overlap) |

**Result:** 51 tests pass (was 33). Verified on this Mac: real scan surfaces 885 MB
node regenerable cache ("safe to clear in max"); model_data (Ollama/HF) surfaced for
review, never auto-deleted; report renders cleanly with the new fields. `--version`=0.3.6. `clean --mode balanced` previews.
Interactive `--apply` prompts `[y/N]`; scripted/scheduled `--apply` (no TTY) proceeds, so an
**already-installed LaunchAgent keeps working** after upgrade (no `--yes` required).

**Net behavior change:** default `balanced` and the daily job no longer wipe all of
`~/Library/Caches` — that is now `max`-only. Nothing lost; run `--mode max` for the full sweep.
