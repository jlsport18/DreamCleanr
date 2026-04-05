# DreamCleanr macOS Shell Plan

DreamCleanr’s next moat is a premium macOS shell on top of the current local engine.

Related docs:

- [ONBOARDING_CONVERSION_SPEC.md](ONBOARDING_CONVERSION_SPEC.md)
- [FIGMA_READY_UI_BRIEF.md](FIGMA_READY_UI_BRIEF.md)
- [IOS_APP_STORE_READINESS.md](IOS_APP_STORE_READINESS.md)

## Goal

Turn the current trustworthy CLI + MCP + receipt engine into a fast, premium, low-maintenance native experience.

## Product shape

- SwiftUI app shell on macOS
- wraps the existing local DreamCleanr engine rather than replacing it
- reads and renders local receipt/history artifacts
- provides guided presets and safer browsing of cleanup impact
- stays local-first and does not require a backend
- owns the real install -> scan -> first win -> upgrade flow once the shell exists

## Design inputs

Build the shell from these inputs:

- [ONBOARDING_CONVERSION_SPEC.md](ONBOARDING_CONVERSION_SPEC.md) for the real install -> scan -> upgrade sequence
- [FIGMA_READY_UI_BRIEF.md](FIGMA_READY_UI_BRIEF.md) for file pages, frame sizes, tokens, IA, and export-ready assets

The shell should absorb the richer operator-pack design system without drifting into generic SaaS chrome.

## Core capabilities

### 1. Receipt and history browser

- show latest and prior cleanup runs
- explain removed, protected, and manual-review items clearly
- highlight trends like repeated cache growth or recurring stale helpers

### 2. Guided cleanup presets

- `Balanced`
- `Low Storage Emergency`
- future workload presets such as `LLM Dev Mode`

### 2.5. Real onboarding flow

- first-run scan with real local data
- visible protected-state explanation
- first-win receipt review
- premium upsell only after value is visible

### 3. Native observability

- category-based disk visibility
- detector-family summaries
- clear distinction between current capability and future detector support
- dashboard IA shaped around hero metric, category breakdown, smart recommendations, weekly trends, and history

### 3.5. UI system

- sidebar navigation for Dashboard, Scan, Auto Optimize, History, Settings, and Upgrade
- top bar with product identity, health narrative, and future account slot only if commercial work is later approved
- component system for metric cards, category cards, chart strips, review rows, and upgrade panels
- export-ready screenshot surfaces for website, Product Hunt, X, and Open Graph assets

### 4. Shared contract for the future companion

- stable receipt/history schema
- paired status summary
- no backend-heavy sync requirement in the first phase

## Technical boundaries

- reuse the current Python engine and JSON/HTML outputs
- do not fork cleanup logic into a second native implementation
- keep the native layer focused on presentation, orchestration, and guided presets
- preserve preview-first behavior and protected-state guarantees
- treat monthly/yearly pricing toggles, live subscription gating, and team dashboards as future commercial concepts only until the strategy changes

## Sequencing

1. stabilize detector registry and category-level observability
2. define shared receipt/history contract
3. finalize onboarding and frame structure in [ONBOARDING_CONVERSION_SPEC.md](ONBOARDING_CONVERSION_SPEC.md) and [FIGMA_READY_UI_BRIEF.md](FIGMA_READY_UI_BRIEF.md)
4. build premium macOS shell
5. only then design the iPhone/iPad companion against the shared contract
