# DreamCleanr macOS Shell

Planned home for the SwiftUI menu bar shell.

The macOS shell should:

- read the canonical DreamCleanr `latest-summary.json`, `latest.json`, and `latest.html` outputs
- launch dry-run and balanced apply workflows through the Python CLI
- avoid duplicating cleanup logic or process classification rules

Recommended first-read contract:

- `latest-summary.json` for menu-bar and dashboard cards
- `latest.json` for deep drill-down and timeline inspection
- `latest.html` for human-readable receipt rendering and export

Prototype source now lives in:

- `apple/Sources/DreamCleanrShellPrototype/`
- `apple/Sources/DreamCleanrAppleShared/`

Build with:

```bash
swift build --package-path apple
```
