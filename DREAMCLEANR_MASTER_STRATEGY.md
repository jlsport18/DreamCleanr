# DreamCleanr Master Strategy

Last updated: `2026-04-05`

This is DreamCleanr's canonical internal strategy document. It replaces drift across older strategy summaries and should be treated as the source of truth for product direction, monetization, and the next native build lane.

This doc is maintained through the repo-owned `$dreamcleanr-strategy-analysis-operator` workflow, which packages DreamCleanr's 12-section master prompt into a reusable strategy-refresh system instead of leaving it as one-off prompt text.

Related phase-2 docs:

- [DREAMCLEANR_SKILLS.md](DREAMCLEANR_SKILLS.md)
- [FEATURE_SPECS.md](FEATURE_SPECS.md)
- [GROWTH_LAUNCH_PLAYBOOK.md](GROWTH_LAUNCH_PLAYBOOK.md)
- [MACOS_SHELL_PLAN.md](MACOS_SHELL_PLAN.md)
- [ONBOARDING_CONVERSION_SPEC.md](ONBOARDING_CONVERSION_SPEC.md)
- [FIGMA_READY_UI_BRIEF.md](FIGMA_READY_UI_BRIEF.md)
- [CREATOR_OUTREACH.md](CREATOR_OUTREACH.md)
- [INVESTOR_PITCH_DECK.md](INVESTOR_PITCH_DECK.md)
- [TEST_AND_DEBUG.md](TEST_AND_DEBUG.md)
- [GITHUB_SYNC_AND_RELEASE.md](GITHUB_SYNC_AND_RELEASE.md)
- [LAUNCH_VERSION_PLAYBOOK.md](LAUNCH_VERSION_PLAYBOOK.md)
- [MARKET_RESEARCH_MEMO.md](MARKET_RESEARCH_MEMO.md)
- [COMMERCIAL_BACKEND_ARCHITECTURE.md](COMMERCIAL_BACKEND_ARCHITECTURE.md)
- [AUTH_BILLING_ENTITLEMENTS_SPEC.md](AUTH_BILLING_ENTITLEMENTS_SPEC.md)
- [ANALYTICS_AND_KPI_PLAN.md](ANALYTICS_AND_KPI_PLAN.md)
- [MRR_ROADMAP.md](MRR_ROADMAP.md)
- [STRIPE_COMMERCIAL_ARCHITECTURE.md](STRIPE_COMMERCIAL_ARCHITECTURE.md)
- [CLOUD_ARCHITECTURE_FUTURE.md](CLOUD_ARCHITECTURE_FUTURE.md)

## Operator-Pack Integration Rule

DreamCleanr's deeper operator pack stays modular:

- canonical product and monetization truth lives here and in the strategy rollups
- future commercial backend, auth, analytics, and MRR work live in the incubation docs only
- richer onboarding, Figma, and launch systems live in their dedicated modular docs

Do not collapse these into a single founder memo, and do not treat future-commercial planning as a strategic pivot away from the current local-first product.

## 1. Product Overview

### What DreamCleanr does today

DreamCleanr is a `local-first`, `trust-first` macOS cleanup tool for AI-heavy and developer-heavy machines.

The current shipped product:

- classifies `Docker`, `Claude`, and `Codex` process trees as active, background, stale, or protected
- prunes safe storage targets like `uv`, `trunk`, `Library/Caches`, `gradle`, `npm`, and `npx` caches
- keeps high-risk state outside default auto-delete, including Docker VM storage, the Claude VM bundle, `~/.codex`, and `~/.claude`
- adds read-only detector visibility for Python, Node, Hugging Face, Ollama, LM Studio, Git/LFS, and IDE support roots in receipts and MCP scan output
- captures active Git-backed project signals so future cleanup can distinguish live workspaces from cold artifact stores
- writes local JSON and HTML cleanup receipts
- installs balanced-safe scheduled cleanup through `launchd`
- exposes a local MCP server for Claude, Codex, and VS Code

The current implementation baseline is grounded in:

- [dreamcleanr/core.py](dreamcleanr/core.py)
- [dreamcleanr/cli.py](dreamcleanr/cli.py)
- [dreamcleanr/reporting.py](dreamcleanr/reporting.py)
- [README.md](README.md)

### Target audience segments

| Segment | Current pain | Why DreamCleanr fits |
|---|---|---|
| AI engineers | local models, Docker, caches, broken disk headroom, noisy helper processes | DreamCleanr already protects AI tool state better than a generic cleaner |
| ML researchers | large artifacts, repeated experiments, model/data cache sprawl | DreamCleanr can evolve into safe cache and environment intelligence |
| Indie hackers | one overloaded Mac, too many toolchains, no ops team | local-first, low-maintenance, inspectable workflow |
| Startup teams | inconsistent local machine health, reproducibility drift, support burden | future Team policy packs and reporting can solve this without backend-heavy infra |

### Core value proposition

DreamCleanr should be positioned as:

> The cleanup and optimization layer for AI and developer workflows on macOS.

## Master-Prompt Operating Rule

When DreamCleanr strategy is refreshed, use the 12-section master-prompt flow owned by `$dreamcleanr-strategy-analysis-operator`:

1. product overview
2. technical strength analysis
3. weaknesses and technical risks
4. AI/dev ecosystem gap analysis
5. opportunity map
6. feature roadmap
7. monetization strategy
8. advertising and affiliate strategy
9. business development strategy
10. make-money-at-scale strategy
11. technical architecture recommendations
12. execution plan

That workflow must stay grounded in:

- current repo truth
- current product boundaries
- explicit separation between shipped, planned, and future-incubation systems
- modular docs that absorb design depth, launch systems, and commercial planning without broadening public product claims

The core value stack is:

- `Speed`: reclaim disk and remove stale helper noise quickly
- `Efficiency`: keep heavy AI/dev machines usable without broad manual cleanup
- `Automation`: schedule safe cleanup and generate receipts automatically
- `Resource optimization`: reduce workflow drag caused by containers, caches, and stale runtime leftovers

## 2. Technical Strength Analysis

### What DreamCleanr already does well

| Current strength | Evidence in product | Why it matters |
|---|---|---|
| Safe file-system cleanup | safe cache paths and protected-state rules in `core.py` | trust is the hardest part of this category |
| Docker-aware cleanup | Docker process roles, engine inventory, and prune logic already exist | Docker is a core pain point for AI/dev Macs |
| Claude/Codex awareness | active-vs-stale classification and protected support roots exist today | strong niche differentiation versus generic cleaners |
| Detector visibility layer | read-only detector registry now feeds receipts and MCP scan output for broader dev ecosystems | expands the moat without overclaiming cleanup support |
| Project-signal safety layer | Git-backed Python, Node, Git/LFS, and IDE workspaces can now be observed as active project signals | creates a safer bridge from visibility into later guided cleanup |
| Preview-first workflow | cleanup plans and receipts are first-class | makes the tool auditable and safer |
| Receipt-first reporting | HTML and JSON receipts already exist | creates explainability and future premium UX leverage |
| GitHub-first distribution | release, install-smoke, governance, and Pages are already live | low-maintenance and globally distributable |

### macOS-native advantages

DreamCleanr is strongest on macOS because:

- it can target the exact cache and support paths used by common Mac AI/dev tooling
- it can integrate with `launchd` for low-friction scheduling
- it can eventually ship a high-quality native shell on top of an already-stable local engine

### Performance benefits for LLM workflows

DreamCleanr already helps LLM-heavy workflows indirectly by:

- reclaiming local disk headroom
- reducing stale helper-process noise
- protecting high-value AI state while still cleaning safe cache layers

Its next leap is not generic “faster computer” marketing. It is deeper developer workload awareness.

## 3. Weaknesses And Technical Risks

### Current weaknesses

| Weakness | Current state | Risk |
|---|---|---|
| Python env cleanup is not project-aware yet | visibility-only roots exist for venv/conda/pip/poetry, but no safe guided cleanup | still misses one of the biggest dev pain areas |
| Node workspace awareness is still shallow | visibility-only store roots exist, but no workspace or lockfile intelligence | misses a major developer pain area |
| Local LLM cleanup remains visibility-first | Ollama and LM Studio roots are observable, but model-safe cleanup is not implemented | still missing a fast-growing AI workflow surface |
| Hugging Face support is observability-only | HF cache roots are detectable, but cleanup logic is not yet live | leaves major ML disk consumption only partially modeled |
| Git/LFS project awareness is still early | Git-backed activity signals exist, but repo-safe cleanup decisions are not modeled yet | cannot yet make project-aware safety decisions |
| Limited observability UX | receipts exist, but no interactive heatmap or disk explorer | weaker premium feel and lower “aha” factor |

### Technical risks

- over-cleaning around active projects if future detector logic is naive
- permission friction if DreamCleanr expands too aggressively into system-adjacent cleanup
- scope drift into generic Mac cleanup instead of staying specific to AI/dev workflows
- App Store confusion if DreamCleanr later markets itself as a device-wide iPhone cleaner instead of a Mac-first companion ecosystem

## 4. Gap Analysis Across The AI/Dev Ecosystem

| Ecosystem | Current support | Gap | Strategic importance |
|---|---|---|---|
| Docker | strong | deeper image/container/volume guidance, project-aware pruning | critical |
| Kubernetes | none | kube context/cache/log intelligence | medium |
| Python | visibility + active project signals | `venv`, `conda`, `poetry`, pip cache, active project detection | critical |
| Node | visibility + active project signals | `npm`, `pnpm`, `yarn`, `node_modules`, monorepo awareness | critical |
| Local LLM stacks | visibility-only | Ollama and LM Studio cache/model awareness | critical |
| Git and LFS | visibility + active project signals | active repo detection, large artifact tracking, stale clone cleanup | high |
| Hugging Face | visibility-only | HF hub and dataset cache awareness | high |
| IDEs | visibility + active project signals | VS Code workspace intelligence and JetBrains cache/workspace awareness | high |

### Hugging Face-specific note

Hugging Face’s official docs currently describe:

- `~/.cache/huggingface/hub` as the default Hub cache
- `~/.cache/huggingface/datasets` as a datasets cache path

DreamCleanr should treat these as high-value, ML-specific storage surfaces and make them inspectable before they become automatically reclaimable.

### Missing platform capabilities

DreamCleanr currently lacks:

- disk usage visualization by artifact family
- predictive cleanup or “safe to delete” scoring
- workflow awareness based on active repos and toolchains
- workload-specific cleanup presets

## 5. Opportunity Map

### Short-term quick wins

| Opportunity | Description | Revenue impact | Technical complexity | Differentiation | Package |
|---|---|---:|---:|---:|---|
| AI dev cleanup presets | presets like `LLM Dev Mode` and `Low Storage Emergency` | medium | low | medium | Community |
| Dev artifact disk map | show disk use by Docker, Python, Node, AI models, HF caches | high | medium | high | Community |
| Safe “free 20GB” actions | one-click guided recommendations with preview and receipt | high | medium | high | Pro |

### Mid-term opportunities

| Opportunity | Description | Revenue impact | Technical complexity | Differentiation | Package |
|---|---|---:|---:|---:|---|
| Environment-aware cleanup | understand active repos and environments before deletion | high | high | high | Pro |
| HF and LLM cache intelligence | make ML storage surfaces visible and safely manageable | high | medium | high | Community |
| Better automation | scheduled cleanup with stronger summaries and policy presets | medium | medium | medium | Community / Pro |

### Long-term opportunities

| Opportunity | Description | Revenue impact | Technical complexity | Differentiation | Package |
|---|---|---:|---:|---:|---|
| Premium macOS shell | native shell for observability, history, and guided actions | very high | high | very high | Pro |
| Paired iPhone/iPad companion | mobile receipts, status, and paired control | high | high | high | Pro |
| Team policy packs | multi-machine rollout and policy/reporting guidance | high | medium | high | Team |

## 6. Feature Development Roadmap

### Must-have features

| Feature | Description | Revenue impact | Technical complexity | Differentiation | Package |
|---|---|---:|---:|---:|---|
| Detector registry | modular detectors for Docker, Python, Node, local LLM stacks, HF, Git, and IDEs | high | high | high | Community |
| Project-aware cleanup safety | never recommend destructive cleanup against clearly active repos/toolchains | very high | high | very high | Community |
| Artifact-family disk visualization | show what categories are taking space before cleanup | high | medium | high | Community |

### High-ROI features

| Feature | Description | Revenue impact | Technical complexity | Differentiation | Package |
|---|---|---:|---:|---:|---|
| Safe-to-delete confidence scoring | explainability layer for why something is safe to reclaim | high | high | very high | Pro |
| One-click optimization modes | `LLM Dev Mode`, `Low Storage Emergency`, future workload profiles | medium | medium | high | Community / Pro |
| Better receipts and history | pre/post summaries, impact deltas, trend views | high | medium | medium | Pro |

### Innovative / market-dominating features

| Feature | Description | Revenue impact | Technical complexity | Differentiation | Package |
|---|---|---:|---:|---:|---|
| Project-aware rollback/snapshots | restore confidence for aggressive cleanup workflows | high | very high | very high | Pro |
| Predictive performance alerts | warn before disk/storage conditions degrade developer velocity | high | high | high | Pro |
| Paired shell + mobile model | macOS shell plus iPhone/iPad companion using shared receipts/history | very high | high | very high | Pro |

## 7. Monetization Strategy

### Core business model

DreamCleanr should stay `open-core premium`.

| Package | Default price | What it includes |
|---|---:|---|
| Community | Free | CLI, MCP, receipts, scheduled cleanup, GitHub-first install/update |
| Pro | `$29` intro / `$49` standard one-time | premium macOS shell, guided cleanup, richer history and insights, integration helpers |
| Team | `$199/year` pilot for up to 5 Macs | policy packs, admin reporting, rollout guidance, multi-machine support |

### Why this monetization model wins

- The category is trust-sensitive. Free core builds credibility.
- The paid layer should sell convenience, visibility, and policy, not basic deletion.
- A paid shell is more defensible than a gated CLI.
- Team value should come after workflow proof, not before.

## 8. Dev-Friendly Advertising And Affiliate Strategy

Advertising should remain secondary and subtle.

### Acceptable later monetization lanes

- affiliate links for cloud GPUs, storage, or AI infra tools
- native recommendations for adjacent dev tooling
- optional partner bundles with clearly marked placement

### What DreamCleanr should not do

- intrusive banner ads
- deceptive “boost your Mac” upsells
- cluttered sponsored placements inside safety-critical cleanup flows

If ads or affiliates are used later, keep them:

- outside core cleanup actions
- outside receipts
- clearly disclosed
- aligned to developer utility rather than generic consumer monetization

## 9. Business Development And Distribution Strategy

### Partnerships

- AI developer tools and model runtimes
- local dev infrastructure vendors
- IDE/workspace ecosystem players
- cloud GPU and AI infra partners

### Distribution priorities

1. GitHub discovery and open-source style trust
2. developer and AI workflow communities
3. SEO for high-intent cleanup and AI/dev queries
4. package-manager discoverability
5. native shell distribution after premium value is real

### Viral loops

- shareable “you reclaimed X GB safely” receipts
- comparative “where your AI/dev storage went” visuals
- premium shell screenshots that demonstrate order and trust, not gimmicks

## 10. Make-Money-At-Scale Strategy

DreamCleanr scales financially if it becomes:

- the default `day-one install` for heavy AI/dev Macs
- the trusted cleanup layer that does not break workflows
- the cleanest premium observability shell for local dev-machine hygiene

### LTV optimization

- monetize through one-time Pro convenience before considering recurring pricing
- later upsell Team only where policy/reporting demand exists
- avoid backend-heavy costs that force premature subscription pressure

### CAC reduction

- rely on organic GitHub discovery
- search capture for AI/dev cleanup intent
- community credibility and receipts as proof of value

### Ecosystem lock-in

The best lock-in is not hidden data. It is:

- stable local receipts/history
- trusted presets
- workflow-aware cleanup rules
- a shell and companion that make DreamCleanr easier than competitors to keep around

## 11. Technical Architecture Recommendations

### Core architecture direction

Build DreamCleanr around four durable layers:

1. `Detector registry`
   - per-ecosystem detectors for Docker, Python, Node, local LLM stacks, Hugging Face, Git/LFS, and IDEs
2. `Policy engine`
   - project-aware rules for what is safe, review-only, or protected
3. `Receipt/history contract`
   - one shared JSON model for CLI, shell, and companion
4. `Presentation layer`
   - CLI today, premium macOS shell next, iPhone/iPad companion later

### Local vs cloud

- scanning, cleanup, and recommendation generation should remain local by default
- cloud processing is not needed for core value in this phase
- remote sync should be avoided until it clearly pays for its complexity
- any future backend work should follow [CLOUD_ARCHITECTURE_FUTURE.md](CLOUD_ARCHITECTURE_FUTURE.md) and remain optional

### Suggested interface directions

- a detector registry with family-specific adapters
- project-aware policy presets driven by active repos and toolchains
- a shared receipt/history schema reused across all surfaces
- an optional paired-device status model for the later mobile companion

## 12. Execution Plan

### Top 5 immediate actions

1. Keep [FEATURE_SPECS.md](FEATURE_SPECS.md) current as the engineering-facing moat and detector roadmap.
2. Use [GROWTH_LAUNCH_PLAYBOOK.md](GROWTH_LAUNCH_PLAYBOOK.md), [ONBOARDING_CONVERSION_SPEC.md](ONBOARDING_CONVERSION_SPEC.md), and the public pricing page to keep conversion surfaces grounded.
   Use the public MCP setup, FAQ, and comparison pages as the distribution and search-intent follow-through.
3. Define project-aware safety signals before expanding cleanup surfaces.
4. Build toward the premium shell through [MACOS_SHELL_PLAN.md](MACOS_SHELL_PLAN.md), [FIGMA_READY_UI_BRIEF.md](FIGMA_READY_UI_BRIEF.md), and a shared receipt/history contract.
5. Keep Community free while validating premium willingness-to-pay through shell prototypes and install behavior.

### Next 10 growth moves

1. Add Python environment detection
2. Add Node workspace detection
3. Add Hugging Face cache detection
4. Add local LLM cache detection
5. Add Git/LFS awareness
6. Add a visual storage map by developer artifact family
7. Add workload presets
8. Add safe-to-delete confidence scoring
9. Add a premium shell waitlist or early-access lane
10. Add partner-ready affiliate surfaces only after trust and usage are strong

### 90-day roadmap

#### Days 0-30

- detector registry spec
- Python, Node, Hugging Face, and LLM cache discovery
- better artifact visibility

#### Days 31-60

- project-aware cleanup safety
- workload presets
- stronger receipts and impact summaries

#### Days 61-90

- premium macOS shell prototype
- shell-ready shared history contract
- pricing and launch package validation for Pro
- keep any cloud or Stripe work architecture-only unless the monetization model materially changes

## Source Grounding

### Internal DreamCleanr grounding

- [dreamcleanr/core.py](dreamcleanr/core.py)
- [dreamcleanr/cli.py](dreamcleanr/cli.py)
- [dreamcleanr/models.py](dreamcleanr/models.py)
- [dreamcleanr/reporting.py](dreamcleanr/reporting.py)
- [README.md](README.md)

### External primary sources

- Apple App Review Guidelines: https://developer.apple.com/app-store/review/guidelines
- Apple account deletion guidance: https://developer.apple.com/support/offering-account-deletion-in-your-app/
- Apple membership comparison: https://developer.apple.com/support/compare-memberships/
- Hugging Face Hub cache docs: https://huggingface.co/docs/hub/local-cache
- Hugging Face cache management docs: https://huggingface.co/docs/huggingface_hub/main/guides/manage-cache
- CleanMyMac pricing: https://macpaw.com/en/store/cleanmymac
- DaisyDisk pricing: https://daisydiskapp.com/support/pricing/
- Hazel pricing: https://store.noodlesoft.com/
- Setapp pricing: https://setapp.com/pricing
