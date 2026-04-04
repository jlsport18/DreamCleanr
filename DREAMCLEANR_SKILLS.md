# DreamCleanr Skills Registry

This is the repo-owned registry for DreamCleanr skills. Skill source lives in `codex-skills/`. Install or refresh them into Codex with:

```bash
./scripts/install_codex_skills.sh
```

The installer copies only DreamCleanr skill folders into `${CODEX_HOME:-$HOME/.codex}/skills` and leaves unrelated skills untouched.

## DreamCleanr-Owned Skills

| Skill | Purpose | Trigger phrases | Write boundary | Owner pod | Current docs owned | Status |
|---|---|---|---|---|---|---|
| `dreamcleanr-strategy-analysis-operator` | Own the DreamCleanr master-prompt analysis workflow and keep the canonical strategy, roadmap, market, and monetization stack aligned to product truth. | `master prompt`, `strategy refresh`, `product analysis`, `monetization strategy`, `opportunity map`, `90-day roadmap`, `category dominance` | canonical strategy docs and rollups | Strategy Intelligence Pod | `DREAMCLEANR_MASTER_STRATEGY.md`, `MARKET_STRATEGY.md`, `MONETIZATION_PLAN.md`, `ROADMAP.md` | active |
| `dreamcleanr-commercial-architecture-operator` | Own future-only backend, billing, auth, entitlement, analytics, KPI, and MRR planning without changing the current local-first product model. | `FastAPI`, `Stripe`, `Postgres`, `Redis`, `entitlements`, `analytics ingest`, `feature flags`, `subscriptions`, `MRR`, `backend repo structure` | future-commercial architecture docs only | Commercial Incubation Pod | `COMMERCIAL_BACKEND_ARCHITECTURE.md`, `AUTH_BILLING_ENTITLEMENTS_SPEC.md`, `ANALYTICS_AND_KPI_PLAN.md`, `MRR_ROADMAP.md`, future-commercial docs | active |
| `dreamcleanr-release-launch-operator` | Own DreamCleanr testing, debugging, commit, PR, release, deploy, and launch execution. | `test`, `debug`, `verify`, `fix`, `polish`, `commit`, `push`, `deploy`, `launch`, `release`, `tag` | release, launch, debug, and deploy-ops docs | Release And Launch Pod | `TEST_AND_DEBUG.md`, `GITHUB_SYNC_AND_RELEASE.md`, `LAUNCH_VERSION_PLAYBOOK.md`, release ops docs | active |
| `dreamcleanr-toolchain-intelligence-engineer` | Plan and later implement toolchain-aware cleanup intelligence across Docker, Python, Node, local LLM stacks, Hugging Face, Git/LFS, and IDEs. | `project-aware cleanup`, `safe to delete`, `detector registry`, `Hugging Face cache`, `Ollama`, `LM Studio`, `Node`, `Python env`, `workspace awareness`, `shipped vs planned` | strategy docs, specs, later detector/runtime work | Product Moat Pod | `FEATURE_SPECS.md`, `DREAMCLEANR_MASTER_STRATEGY.md`, demo truth rules | active |
| `dreamcleanr-growth-launch-operator` | Own public copy, pricing surfaces, launch assets, onboarding demo messaging, creator outreach, Product Hunt/HN/Indie Hackers/X playbooks, and conversion messaging. | `landing page`, `pricing page`, `launch plan`, `Product Hunt`, `Hacker News`, `conversion`, `SEO copy`, `waitlist`, `onboarding demo`, `creator outreach`, `A/B copy`, `investor narrative` | site, pricing, launch docs, onboarding docs, README marketing copy | Growth Surface Pod | `GROWTH_LAUNCH_PLAYBOOK.md`, `ONBOARDING_CONVERSION_SPEC.md`, `CREATOR_OUTREACH.md`, `INVESTOR_PITCH_DECK.md`, public site copy | active |
| `dreamcleanr-native-shell-engineer` | Own the premium macOS shell plan, real future app onboarding, receipt/history browser, paired status model, Figma-ready native surface planning, and iPhone/iPad companion boundary. | `macOS shell`, `SwiftUI`, `receipt browser`, `native companion`, `paired control`, `history contract`, `Figma-ready`, `dashboard`, `settings`, `analytics` | native-shell docs, future `macos/` and `ios/` work, native UX specs | Native Shell Pod | `MACOS_SHELL_PLAN.md`, `FIGMA_READY_UI_BRIEF.md`, native portions of `ONBOARDING_CONVERSION_SPEC.md` | active |
| `dreamcleanr-governance-compliance-operator` | Own privacy, security, terms, release governance, GitHub-first interest capture, public trust surfaces, App Store-safe boundaries, and future billing/commercial guardrails. | `privacy policy`, `security policy`, `terms`, `governance`, `compliance`, `App Store`, `policy surfaces`, `early access`, `Stripe`, `billing boundaries`, `no fake checkout` | compliance docs, governance docs, safe public language, future commercial architecture docs | Governance Pod | `COMPLIANCE.md`, `IOS_APP_STORE_READINESS.md`, `STRIPE_COMMERCIAL_ARCHITECTURE.md`, `CLOUD_ARCHITECTURE_FUTURE.md`, GitHub-first collection surfaces | active |

## Generic Skills Mapped To DreamCleanr

| Existing skill | DreamCleanr use |
|---|---|
| `skill-creator` | Create and validate DreamCleanr repo-owned skills |
| `daytrading-swarm-orchestrator` | Prioritize DreamCleanr phases, pods, and sequencing |
| `daytrading-task-lock-coordinator` | Keep public copy, strategy docs, and runtime changes from colliding |
| `daytrading-frontend-design` | Build site surfaces and visual communication |
| `daytrading-creative-brain-ux` | Improve CTA flow, pricing psychology, and launch ergonomics |
| `daytrading-market-research-agent` | Analyze market, positioning, GTM, and pricing |
| `daytrading-quant-architect` | Shape system boundaries, detector registry, and native shell architecture |
| `platform-governance-supervisor` | Keep DreamCleanr GitHub-first and low-maintenance |
| `security-best-practices` | Review compliance and safe public security posture |
| `daytrading-regression-guard` | Run tests, validation, and release-surface checks |

## Pod And Subagent Map

| Pod | Lead skill | Support skills | Subagent lane |
|---|---|---|---|
| Strategy Intelligence Pod | `dreamcleanr-strategy-analysis-operator` | `daytrading-market-research-agent`, `daytrading-quant-architect`, `dreamcleanr-toolchain-intelligence-engineer` | `Fermat` |
| Commercial Incubation Pod | `dreamcleanr-commercial-architecture-operator` | `dreamcleanr-governance-compliance-operator`, `daytrading-quant-architect`, `platform-governance-supervisor` | `Gauss` |
| Release And Launch Pod | `dreamcleanr-release-launch-operator` | `daytrading-regression-guard`, `dreamcleanr-growth-launch-operator`, `platform-governance-supervisor` | `Kepler` |
| Skill System Pod | `skill-creator` | `daytrading-task-lock-coordinator`, `platform-governance-supervisor` | `Euler` |
| Growth Surface Pod | `dreamcleanr-growth-launch-operator` | `daytrading-frontend-design`, `daytrading-creative-brain-ux`, `daytrading-context-orientation-architect` | `Averroes` |
| Product Moat Pod | `dreamcleanr-toolchain-intelligence-engineer` | `daytrading-quant-architect`, `daytrading-regression-guard` | `Carver` |
| Native Shell Pod | `dreamcleanr-native-shell-engineer` | `daytrading-quant-architect`, `daytrading-frontend-design` | `Dirac` |
| Governance Pod | `dreamcleanr-governance-compliance-operator` | `platform-governance-supervisor`, `security-best-practices`, `daytrading-regression-guard` | `Ampere` |
| Market/Pricing Pod | `daytrading-market-research-agent` | `dreamcleanr-growth-launch-operator`, `platform-governance-supervisor` | `Fermat` |

## Plan-Build-Verify-Sync Loop

Use this loop for every DreamCleanr slice:

1. `Plan`
   - define one small slice only
   - lock scope, files, acceptance, and validation
   - assign one lead skill and one support pod
2. `Build`
   - edit only that slice's surfaces
   - keep runtime, marketing, and governance changes from colliding
3. `Verify`
   - run the smallest meaningful checks first
   - reject the slice if public copy overclaims current capability
4. `Sync`
   - update the affected canonical docs
   - sync repo-owned skills when skill content changes
   - push GitHub-facing progress only once the slice is green
5. `Re-plan`
   - choose the next slice from the current repo state, not stale planning text

## Current Execution-Pack Routing

| Work item | Lead skill | Support pod |
|---|---|---|
| Canonical master-prompt strategy refreshes | `dreamcleanr-strategy-analysis-operator` | Strategy Intelligence Pod |
| Future backend, Stripe, auth, analytics, and MRR planning | `dreamcleanr-commercial-architecture-operator` | Commercial Incubation Pod |
| Test/debug, release, deploy, and launch operations | `dreamcleanr-release-launch-operator` | Release And Launch Pod |
| Skill bundle and registry maintenance | `skill-creator` | Skill System Pod |
| Homepage onboarding demo and pricing flow | `dreamcleanr-growth-launch-operator` | Growth Surface Pod |
| Creator outreach, launch copy, and investor materials | `dreamcleanr-growth-launch-operator` | Market/Pricing Pod |
| Real future app onboarding and premium shell UX | `dreamcleanr-native-shell-engineer` | Native Shell Pod |
| Future Stripe/commercial architecture and trust guardrails | `dreamcleanr-governance-compliance-operator` | Governance Pod |
| Demo category truth and detector roadmap boundaries | `dreamcleanr-toolchain-intelligence-engineer` | Product Moat Pod |

## Install And Sync Workflow

1. Edit a skill under `codex-skills/<skill-name>/`.
2. Validate it with:
   ```bash
   python3 /Users/jonathanlynch/.codex/skills/.system/skill-creator/scripts/quick_validate.py codex-skills/<skill-name>
   ```
3. Sync all DreamCleanr skills into Codex:
   ```bash
   ./scripts/install_codex_skills.sh
   ```
4. Re-run the installer whenever repo-owned skill content changes.
