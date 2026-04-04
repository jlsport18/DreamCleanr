# DreamCleanr MVP Launch Plan

Current release-ops companions:

- [TEST_AND_DEBUG.md](TEST_AND_DEBUG.md)
- [GITHUB_SYNC_AND_RELEASE.md](GITHUB_SYNC_AND_RELEASE.md)
- [LAUNCH_VERSION_PLAYBOOK.md](LAUNCH_VERSION_PLAYBOOK.md)

## Decision

DreamCleanr MVP launches as:

- a public Python CLI package and GitHub release
- a local MCP tool for Claude, Codex, and VS Code
- a public branded download site
- a mobile-friendly report and install surface

Native iOS/iPad and macOS shell apps remain the next product lane, not a blocker for MVP launch.

## Delivery Pods

### Core Reliability Pod

- Lead: `daytrading-regression-guard`
- Support: `daytrading-swarm-harness-engineer`
- Acceptance: CI stays green, scheduled cleanup remains safe-by-default, and release builds stay reproducible.

### MCP Distribution Pod

- Lead: `daytrading-broker-mcp-integrator`
- Support: `daytrading-quant-architect`
- Acceptance: DreamCleanr can be added as a local MCP server for Claude, Codex, and VS Code with preview-first defaults.

### Brand and Site Pod

- Lead: `daytrading-creative-brain-ux`
- Support: `frontend-skill`, `daytrading-frontend-design`
- Acceptance: The public site communicates value in under 30 seconds and gives one clear install path per surface.

### Launch Automation Pod

- Lead: `daytrading-swarm-harness-engineer`
- Support: `platform-governance-supervisor`
- Acceptance: Releases, downloads, and the public site require minimal short-term maintenance after launch.

### Release And Launch Pod

- Lead: `dreamcleanr-release-launch-operator`
- Support: `daytrading-regression-guard`, `dreamcleanr-growth-launch-operator`
- Acceptance: Testing, tag, release, deploy, and launch-day comms are documented and repeatable.

### Market Intelligence Pod

- Lead: `daytrading-market-research-agent`
- Support: `daytrading-weekly-review-agent`
- Acceptance: Monetization research starts after the MVP distribution lanes are live and measurable.

## Final MVP Gates

- Public repo or equivalent public download surface exists
- Tagged GitHub release includes wheel, source tarball, and sample report
- Public landing page is live and links to install/download paths
- Claude, Codex, and VS Code integration examples are documented and tested
- Safety docs, contribution docs, and issue backlog are live

## Long-Term Maintenance Defaults

- Keep the runtime local-first and preview-first
- Prefer GitHub Actions and static hosting over custom servers
- Avoid mandatory managed backends unless usage data proves the need
- Keep monetization research, analytics, and native shells as separate follow-on lanes
