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

## Canonical Docs

- Product strategy: [DREAMCLEANR_MASTER_STRATEGY.md](DREAMCLEANR_MASTER_STRATEGY.md)
- DreamCleanr skill registry: [DREAMCLEANR_SKILLS.md](DREAMCLEANR_SKILLS.md)
- Feature specs: [FEATURE_SPECS.md](FEATURE_SPECS.md)
- Growth and launch: [GROWTH_LAUNCH_PLAYBOOK.md](GROWTH_LAUNCH_PLAYBOOK.md)
- Native shell plan: [MACOS_SHELL_PLAN.md](MACOS_SHELL_PLAN.md)
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
- Keep future features clearly labeled as `planned`, `coming next`, or `early access`.
- Reject a slice if local verification shows the copy or UI overclaims current product capability.
- Treat GitHub as the sync surface once a slice is green.

## Slice Cadence

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

## Current Product Boundaries

- Current strengths: Docker, Claude, Codex, safe cache cleanup, receipts, MCP integration, scheduled cleanup.
- Current gaps: Python env awareness, Node workspace awareness, Ollama, LM Studio, Hugging Face cache intelligence, Git/LFS awareness, JetBrains/VS Code workspace intelligence, project-aware safe-delete logic.
- iPhone and iPad remain `companion` surfaces only; do not position DreamCleanr as a generic device cleaner.
