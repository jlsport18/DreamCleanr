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
