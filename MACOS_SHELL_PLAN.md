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

### 4. Shared contract for the future companion

- stable receipt/history schema
- paired status summary
- no backend-heavy sync requirement in the first phase

## Technical boundaries

- reuse the current Python engine and JSON/HTML outputs
- do not fork cleanup logic into a second native implementation
- keep the native layer focused on presentation, orchestration, and guided presets
- preserve preview-first behavior and protected-state guarantees

## Sequencing

1. stabilize detector registry and category-level observability
2. define shared receipt/history contract
3. finalize onboarding and frame structure in [ONBOARDING_CONVERSION_SPEC.md](ONBOARDING_CONVERSION_SPEC.md) and [FIGMA_READY_UI_BRIEF.md](FIGMA_READY_UI_BRIEF.md)
4. build premium macOS shell
5. only then design the iPhone/iPad companion against the shared contract
