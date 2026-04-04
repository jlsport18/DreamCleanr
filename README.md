# DreamCleanr

DreamCleanr is a lightweight macOS cleanup tool for AI and developer noise.

**Slogan:** `Clean while you sleep.`

DreamCleanr is designed to reclaim space, trim stale helper processes, and leave behind a one-page cleanup receipt without breaking active Docker, Claude, or Codex workflows.

DreamCleanr currently:

- classifies `Docker`, `Claude`, and `Codex` processes as active, background, stale, or protected
- separates active Docker engine state from stale CLI probe chains and orphaned helpers
- prunes safe storage targets while keeping protected AI state and risky VM artifacts out of scheduled cleanup
- generates a self-contained HTML receipt plus canonical JSON output
- installs a daily `launchd` job for balanced-safe cleanup with bounded report retention
- exposes a local MCP server for Claude, Codex, and VS Code
- ships with a public launch site under `site/`

Public site: `https://jlsport18.github.io/DreamCleanr/`

## Install

DreamCleanr is GitHub-first. The stable install and update paths are release-based and evergreen.

### Official install path

```bash
curl -fsSL https://raw.githubusercontent.com/jlsport18/DreamCleanr/main/scripts/install.sh | bash
```

The installer resolves the latest stable DreamCleanr wheel from GitHub Releases and uses `pipx` when available, otherwise `pip`.

### Latest release assets

```bash
open https://github.com/jlsport18/DreamCleanr/releases/latest
```

### Local checkout

```bash
git clone https://github.com/jlsport18/DreamCleanr.git
cd DreamCleanr
./scripts/bootstrap.sh
```

## Update

### One-shot updater

```bash
curl -fsSL https://raw.githubusercontent.com/jlsport18/DreamCleanr/main/scripts/update.sh | bash
```

The updater resolves the latest stable DreamCleanr wheel from GitHub Releases and applies it through `pipx` or `pip` automatically.

### Update a checkout

```bash
git pull --ff-only
./scripts/bootstrap.sh
```

## CLI

```bash
dreamcleanr --version
dreamcleanr scan --mode balanced
dreamcleanr clean --dry-run --mode balanced
dreamcleanr clean --apply --mode balanced
dreamcleanr report --input ~/Library/Logs/DreamCleanr/reports/latest.json
dreamcleanr schedule install --mode balanced
dreamcleanr schedule uninstall
dreamcleanr-mcp
```

## MCP Tool Surfaces

DreamCleanr can run as a local MCP server for AI tools that support local MCP integration.

- Claude config example: `integrations/claude-mcp.json`
- Codex config example: `integrations/codex-mcp.toml`
- VS Code config example: `integrations/vscode-mcp.json`

Current MCP tools:

- `scan`
- `clean_preview`
- `report_render`
- `schedule_status`
- `schedule_preview`

The MCP surface is preview-first. Destructive cleanup is intentionally not exposed by default.

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

## Public Launch Surface

- Brand assets live in `brand/`
- Public marketing/download site lives in `site/`
- MVP launch and operations guidance lives in `LAUNCH_PLAN.md`
- Market and pricing strategy lives in `MARKET_STRATEGY.md`
- Privacy and safety guidance live in `PRIVACY.md` and `SECURITY.md`
- Terms and acceptance guidance live in `TERMS.md`
- Compliance posture lives in `COMPLIANCE.md`
- iOS and App Store readiness guidance lives in `IOS_APP_STORE_READINESS.md`

## Public Policy URLs

- Privacy: `https://jlsport18.github.io/DreamCleanr/privacy.html`
- Security: `https://jlsport18.github.io/DreamCleanr/security.html`
- Terms: `https://jlsport18.github.io/DreamCleanr/terms.html`
- Support: `https://jlsport18.github.io/DreamCleanr/support.html`

## Next Product Phase

DreamCleanr’s next product phase is:

- a more polished macOS shell on top of the current local engine
- stronger compliance and policy surfaces
- an eventual iPhone and iPad companion app that acts as a premium viewer/controller, not a generic device-wide cleaner

## Release Surface

- CI lives in `.github/workflows/ci.yml`
- Install smoke verification lives in `.github/workflows/install-smoke.yml`
- Pages deployment lives in `.github/workflows/pages.yml`
- Daily operational health checks live in `.github/workflows/ops-health.yml`
- Weekly governance review lives in `.github/workflows/governance-review.yml`
- Monthly business and architecture review lives in `.github/workflows/business-review.yml`
- Tagged releases build a wheel and source distribution, then generate a sample HTML cleanup receipt
- Tagged releases publish versioned wheel and source artifacts plus install/update scripts
- Sample output lives in `reports/sample-cleanup-report.json`
- Deployment architecture guidance lives in `DEPLOYMENT_ARCHITECTURE.md`
- Final deployment verification and automation map live in `FINAL_DEPLOYMENT_REPORT.md`
- Monetization guidance lives in `MONETIZATION_PLAN.md`
- Near-term roadmap lives in `ROADMAP.md`
- Post-deploy Pages verification lives in `.github/workflows/pages-verify.yml`
