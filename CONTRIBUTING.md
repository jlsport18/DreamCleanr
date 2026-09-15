# Contributing

## Local Development

```bash
./scripts/bootstrap.sh
source .venv/bin/activate
python -m unittest discover -s tests -p "test_*.py" -v
```

## Release Smoke

Before tagging a release:

```bash
python -m compileall dreamcleanr
python -m unittest discover -s tests -p "test_*.py" -v
python -m dreamcleanr report --input reports/sample-cleanup-report.json --html-out /tmp/dreamcleanr-sample.html
node --check site/app.js
```

## Safety Rules

- Do not auto-delete `~/.codex`, `~/.claude`, Docker raw VM storage, or the Claude VM bundle.
- Keep scheduled cleanup on balanced-safe defaults.
- Treat new process classifications conservatively until they have fixture coverage.
- When a process or path classification is ambiguous, default to `protect_only` and list the item under manual review in the receipt. Never resolve ambiguity toward reclaiming more space.

  Known gap as of 2026-09-15: the code does not enforce the manual-review half of this rule, and only partly follows the `protect_only` half. In `dreamcleanr/core.py`, `manual_review_items` (returned by `gather_storage_records` and stored by `capture_snapshot`) receives only `REVIEW_VM` storage records, and only two paths are classified that way: `docker_vm_data` and `docker_raw`. No process or family classification is ever added to it. A process that matches no rule in `classify_processes` falls back to `ACTIVE_HELPER` with the reason "conservative protection fallback" and is not listed for review. A family's `recommended_action` from `summarize_family` renders in `dreamcleanr/reporting.py` (`render_html`) under "Family Status" and "Why It Was Safe", never under "Manual Review". Some medium-confidence family states recommend removal actions instead of `protect_only`: docker `active` with the daemon reachable but no primary process recommends `docker_system_prune`, docker `residual_data_only` recommends `confirm_raw_vm_delete`, and claude `residual_data_only` recommends `prune_cache`. Either add process and family fallbacks to `manual_review_items`, or reword this rule; follow-up: not yet filed.
