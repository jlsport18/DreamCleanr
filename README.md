# DreamCleanr

DreamCleanr is a lightweight macOS cleanup tool focused on AI and developer noise:

- classifies `Docker`, `Claude`, and `Codex` processes as active or stale
- separates active engine state from leftover probe or helper chains
- prunes safe cache and Docker noise without touching protected AI state
- generates a self-contained HTML report plus canonical JSON summary
- installs a daily `launchd` job for balanced-safe cleanup

## CLI

```bash
python -m dreamcleanr scan
python -m dreamcleanr clean --dry-run
python -m dreamcleanr clean --apply --mode balanced
python -m dreamcleanr report --input ~/Library/Logs/DreamCleanr/reports/latest.json
python -m dreamcleanr schedule install
python -m dreamcleanr schedule uninstall
```

## Safety defaults

- auto-trims only stale helper and stale CLI probe processes
- protects active `Codex` and `Claude` cache roots
- never auto-deletes `~/.codex`, `~/.claude`, the Claude VM bundle, or Docker raw VM storage
- treats risky state as `manual review`

## Output

DreamCleanr writes timestamped JSON and HTML reports to:

`~/Library/Logs/DreamCleanr/reports`
