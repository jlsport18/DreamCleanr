# Changelog

All notable DreamCleanr release-facing changes should be tracked here.

## [Unreleased]

## [0.4.0] - unreleased (held until the purchase path is live)

### Security

- **License keys are now Ed25519 signatures, not forgeable HMACs.** The previous
  scheme signed the buyer's email with a secret that defaulted to a public
  constant (`sweep-community-default`), so anyone could mint a valid key for any
  email. Keys are now Ed25519 signatures that only the holder of the private
  signing seed can produce; the client embeds the public key and verifies offline.
  Verification is performed by a vendored, zero-dependency pure-Python Ed25519
  implementation (RFC 8032), anchored on the RFC test vectors. No telemetry, no
  new dependencies. Legacy HMAC-format keys no longer validate (none were ever
  issued — the purchase chain had not gone live).

### Added

- `check_pro()` is now enforced at the gate points it was always meant to guard:
  developer mode (`clean --mode max`) is Pro-only and downgrades free users to
  `balanced` with an upsell; `schedule install` shows an upsell nag for free
  users; the HTML report footer carries Community branding until Pro is active.
- Operator key-issuance tool (`scripts/issue_license.py`) — signs a key with the
  private seed from the operator secret store. Not shipped in the wheel.
- A distribution test that fails the build if any private-key material or the
  issuance tool ever lands inside the shipped package.

## [0.3.6] - 2026-05-25

### Fixed

- `dreamcleanr --version` (and the `__version__` attribute consumed by the
  MCP server and receipts) now reports the correct release version. The
  `0.3.5` release shipped with `dreamcleanr/__init__.py` still pinned to
  `0.3.4` because the version string was duplicated and only `pyproject.toml`
  was bumped, so installed `0.3.5` artifacts self-reported as `0.3.4`. The
  package version and `__version__` are now both `0.3.6`, and a new
  distribution test asserts they stay in lockstep so this cannot recur.

### Added

- Cleanup report JSON now stamps a `tool_version` field, so a receipt shared
  in a support request is traceable to the exact build that produced it
  (same traceability gap as the version-reporting bug above).

### Removed

- Dropped the vestigial `installer/DreamCleanr-0.3.5.pkg` stub (1.5 KB, no
  build script, referenced by nothing). The supported install path is the
  `scripts/install.sh` one-liner that resolves the latest signed wheel from
  GitHub Releases; the release workflow has never produced a `.pkg`.

## [0.3.5] - 2026-05-04

### Fixed

- `clean` no longer aborts with `FileNotFoundError` when an optional
  external binary (most commonly `docker`) is missing from `PATH`. The
  shared `run_command()` helper now catches `FileNotFoundError` and
  `PermissionError` and returns the same "ok=False" shape that the
  timeout branch produces, so the caller's existing
  `engine_state == "unreachable"` fallback fires as designed. Previously
  a fresh Mac without Docker Desktop would crash on every `dreamcleanr
  clean` invocation, including `--scope=storage` runs that don't need
  docker at all.

## [0.3.4] - 2026-04-05

### Added

- detector visibility for Python, Node, Hugging Face, Ollama, LM Studio, Git/LFS, and IDE support roots in receipts and MCP scan output
- active Git-backed project signals to keep future cleanup logic conservative around live Python, Node, Git/LFS, and IDE workspaces
- `latest-summary.json` and timestamped `summary-*.json` receipt-summary artifacts for future Apple-native consumers
- `dreamcleanr export` admin-friendly JSON and CSV exports for the future Team pilot lane
- a buildable Apple Swift package with shared receipt-summary models, a macOS shell prototype, and companion-facing SwiftUI views under `apple/`

### Polished

- aligned README, roadmap, feature specs, and strategy docs with shipped detector visibility and project-signal safety
- clarified native-shell and companion README guidance around the shared summary contract
- refreshed release-playbook references for the next patch release
- upgraded GitHub Actions checkout usage to `actions/checkout@v6` and tightened review workflow queue counting around recurring tracker issues
- added public MCP setup, FAQ, and comparison pages to reduce install friction and strengthen search-intent surfaces
- expanded GitHub-first monetization research and Pro-interest demand capture without introducing live checkout

### Verified

- Python test suite passes with detector, export, and reporting coverage
- `swift build --package-path apple` passes for the new Apple-side prototype package
- CLI, site, shell-script, and skill-validation checks remain green

## [0.3.3] - 2026-04-04

### Added

- repo-owned DreamCleanr operator skills for strategy analysis, future commercial architecture, and release-launch execution
- test/debug, GitHub sync/release, and versioned launch playbooks
- future-incubation docs for backend architecture, auth and entitlements, analytics and KPI planning, and MRR modeling
- expanded launch, onboarding, investor, and Figma-ready operator content

### Polished

- strengthened compliance and release-readiness surfaces for public distribution
- published public policy pages for privacy, security, terms, and support
- clarified the iPhone and iPad direction as a premium companion path instead of a generic cleaner-app lane
- improved package metadata for release consumers and tooling
- refreshed GitHub Actions versions and timeout hygiene for a cleaner release pipeline

### Verified

- CI, Pages, Pages Verify, and Operations Health all pass on the current public deployment
- public site and public policy URLs resolve successfully

## [0.3.2] - 2026-03-28

### Fixed

- stabilized release-based install and update verification
- verified release-asset install, public installer path, and upgrade path
- hardened the GitHub-first deployment and governance loop

## [0.3.1] - 2026-03-28

### Added

- final GitHub-first deployment and governance surfaces
- deployment architecture and monetization guidance

## [0.3.0] - 2026-03-28

### Launched

- public DreamCleanr MVP site
- local MCP surface for Claude, Codex, and VS Code
- release-driven CLI distribution with receipts and scheduling

## [0.2.x]

### Hardened

- active-vs-stale process classification for Docker, Claude, and Codex
- reporting, scheduling, and cleanup safety boundaries
