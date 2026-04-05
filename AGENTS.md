# DreamCleanr Agent Guide

## Product Truth

- DreamCleanr is `AI workflow hygiene for macOS`.
- Keep the public story `grounded-MVP`: never market planned cleanup capabilities as if they already ship.
- Keep monetization `open-core premium`:
  - `Community`: free
  - `Pro`: one-time premium macOS shell later
  - `Team`: later, after repeated small-team demand
- Keep DreamCleanr `local-first`, `preview-first`, and `GitHub-first`.
- Do not add backend dependency, billing flows, or App Store-specific implementation work unless the task explicitly requires it.
- Treat future-commercial docs, Figma-ready specs, lifecycle experiments, and pricing experiments as internal planning surfaces until they are intentionally promoted into shipped product work.

## Canonical Docs

- Product strategy: [DREAMCLEANR_MASTER_STRATEGY.md](DREAMCLEANR_MASTER_STRATEGY.md)
- DreamCleanr skill registry: [DREAMCLEANR_SKILLS.md](DREAMCLEANR_SKILLS.md)
- Feature specs: [FEATURE_SPECS.md](FEATURE_SPECS.md)
- Growth and launch: [GROWTH_LAUNCH_PLAYBOOK.md](GROWTH_LAUNCH_PLAYBOOK.md)
- Native shell plan: [MACOS_SHELL_PLAN.md](MACOS_SHELL_PLAN.md)
- Test and debug playbook: [TEST_AND_DEBUG.md](TEST_AND_DEBUG.md)
- GitHub sync and release playbook: [GITHUB_SYNC_AND_RELEASE.md](GITHUB_SYNC_AND_RELEASE.md)
- Launch version playbook: [LAUNCH_VERSION_PLAYBOOK.md](LAUNCH_VERSION_PLAYBOOK.md)
- Future commercial incubation: [COMMERCIAL_BACKEND_ARCHITECTURE.md](COMMERCIAL_BACKEND_ARCHITECTURE.md), [AUTH_BILLING_ENTITLEMENTS_SPEC.md](AUTH_BILLING_ENTITLEMENTS_SPEC.md), [ANALYTICS_AND_KPI_PLAN.md](ANALYTICS_AND_KPI_PLAN.md), [MRR_ROADMAP.md](MRR_ROADMAP.md)
- Compliance posture: [COMPLIANCE.md](COMPLIANCE.md), [PRIVACY.md](PRIVACY.md), [SECURITY.md](SECURITY.md), [TERMS.md](TERMS.md)

## Working Rules

- Prefer repo-owned skills under `codex-skills/` and sync them with `scripts/install_codex_skills.sh`.
- Run DreamCleanr work in a strict loop:
  1. plan one small slice
  2. build only that slice
  3. verify it with the smallest meaningful checks
  4. sync the affected canonical docs
  5. then re-plan from the latest repo state
- Give each slice one lead skill and one support pod before editing.
- Keep write boundaries clean:
  - public site and pricing surfaces
  - strategy, roadmap, and monetization docs
  - native-shell planning docs
  - compliance/governance docs
  - core Python engine and MCP runtime
- Do not mix public site, runtime, governance, and strategy work in the same slice unless the slice genuinely spans them.
- Preserve trust signals:
  - no fake testimonials
  - no fake checkout or billing flow
  - no misleading structured data
  - no public subscription, hosted-account, or advanced-detector claims unless they are actually shipped
- Keep future features clearly labeled as `planned`, `coming next`, or `early access`.
- Reject a slice if local verification shows the copy or UI overclaims current product capability.
- Treat GitHub as the sync surface once a slice is green.

## Slice Cadence

- `Slice 0 / Strategy System`
  - lead: `dreamcleanr-strategy-analysis-operator`
  - support pod: Strategy Intelligence Pod
  - surfaces: canonical strategy and rollup docs
- `Slice 1 / Skill System`
  - lead: `skill-creator`
  - support pod: Skill System Pod
  - surfaces: `codex-skills/`, `AGENTS.md`, `DREAMCLEANR_SKILLS.md`, `scripts/install_codex_skills.sh`
- `Slice 2 / Conversion Surfaces`
  - lead: `dreamcleanr-growth-launch-operator`
  - support pod: Growth Surface Pod
  - surfaces: `site/`, `README.md`, pricing copy
- `Slice 3 / Commercial And Onboarding Specs`
  - lead: `dreamcleanr-growth-launch-operator`
  - support pod: Market/Pricing Pod
  - surfaces: onboarding, outreach, investor, and future-commercial docs
- `Slice 4 / Product Moat`
  - lead: `dreamcleanr-native-shell-engineer`
  - support pod: Product Moat Pod
  - surfaces: native-shell and feature-spec docs
- `Slice 5 / Governance And Collection`
  - lead: `dreamcleanr-governance-compliance-operator`
  - support pod: Governance Pod
  - surfaces: GitHub-first interest capture and compliance alignment
- `Slice 6 / Final Verification`
  - lead: `daytrading-regression-guard`
  - support pod: Governance Pod
  - surfaces: validation, release-surface checks, and sync readiness
- `Slice 7 / Commercial Incubation`
  - lead: `dreamcleanr-commercial-architecture-operator`
  - support pod: Commercial Incubation Pod
  - surfaces: future-only backend, billing, auth, analytics, and MRR docs
- `Slice 8 / Release And Launch`
  - lead: `dreamcleanr-release-launch-operator`
  - support pod: Release And Launch Pod
  - surfaces: test/debug docs, GitHub sync docs, release docs, launch docs

## Current Product Boundaries

- Current strengths: Docker, Claude, Codex, safe cache cleanup, receipts, MCP integration, scheduled cleanup, detector visibility across broader AI/dev surfaces, active project signals, latest-summary contract, and admin export surfaces.
- Current gaps: project-aware safe-delete logic for Python and Node environments, guided cleanup for Ollama, LM Studio, and Hugging Face caches, deeper Git/LFS policy logic, richer IDE workspace intelligence, productized macOS shell packaging, iPhone/iPad app targets, and real small-team rollout support.
- Future-commercial concepts like monthly or yearly billing, live team dashboards, account-based onboarding, and hosted analytics remain planning-only.
- iPhone and iPad remain `companion` surfaces only; do not position DreamCleanr as a generic device cleaner.
