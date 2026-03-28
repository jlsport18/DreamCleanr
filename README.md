# DreamCleanr

DreamCleanr is a lightweight macOS cleanup tool for AI and developer noise. It is designed to reclaim space and trim stale helper processes without breaking active Docker, Claude, or Codex workflows.

DreamCleanr currently:

- classifies `Docker`, `Claude`, and `Codex` processes as active, background, stale, or protected
- separates active Docker engine state from stale CLI probe chains and orphaned helpers
- prunes safe storage targets while keeping protected AI state and risky VM artifacts out of scheduled cleanup
- generates a self-contained HTML receipt plus canonical JSON output
- installs a daily `launchd` job for balanced-safe cleanup with bounded report retention

## Install

The easiest local install path is `pipx`:

```bash
pipx install git+https://github.com/jlsport18/DreamCleanr.git
```

If you prefer a repo checkout:

```bash
git clone https://github.com/jlsport18/DreamCleanr.git
cd DreamCleanr
./scripts/bootstrap.sh
```

## CLI

```bash
dreamcleanr scan --mode balanced
dreamcleanr clean --dry-run --mode balanced
dreamcleanr clean --apply --mode balanced
dreamcleanr report --input ~/Library/Logs/DreamCleanr/reports/latest.json
dreamcleanr schedule install --mode balanced
dreamcleanr schedule uninstall
```

## Safety defaults

- auto-trims only stale helper and stale CLI probe processes
- keeps interactive Docker CLI sessions and updater/crashpad-style background helpers conservative by default
- protects active `Codex` and `Claude` cache roots
- never auto-deletes `~/.codex`, `~/.claude`, the Claude VM bundle, or Docker raw VM storage
- keeps scheduled cleanup on a balanced-safe profile with canonical `latest.*` artifacts and bounded history

## Output

DreamCleanr writes timestamped reports and canonical latest artifacts to:

`~/Library/Logs/DreamCleanr/reports`

Key files:

- `latest-before.json`
- `latest-after.json`
- `latest.json`
- `latest.html`
- `latest-failure.json` on runtime errors

## Release Surface

- CI lives in `.github/workflows/ci.yml`
- Tagged releases build a wheel and source distribution, then generate a sample HTML cleanup receipt
- Sample output lives in `reports/sample-cleanup-report.json`
- Near-term roadmap lives in `ROADMAP.md`
