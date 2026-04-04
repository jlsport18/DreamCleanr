---
name: dreamcleanr-toolchain-intelligence-engineer
description: Plan and implement DreamCleanr's toolchain-aware cleanup intelligence for Docker, Python, Node, Hugging Face, Ollama, LM Studio, Git/LFS, VS Code, and JetBrains. Use when DreamCleanr needs detector registry design, project-aware cleanup safety, safe-to-delete logic, artifact-family visibility, cache intelligence, or ecosystem-specific cleanup planning.
---

# DreamCleanr Toolchain Intelligence Engineer

## Overview

Design DreamCleanr's detector registry and safe-clean intelligence so the product can expand beyond Docker, Claude, and Codex without breaking active developer workflows.

## Use This Skill

- Read [DREAMCLEANR_MASTER_STRATEGY.md](../../DREAMCLEANR_MASTER_STRATEGY.md) and [FEATURE_SPECS.md](../../FEATURE_SPECS.md) first.
- Confirm whether a requested capability is `shipped`, `partial`, or `planned` before proposing public-facing language.
- When demo copy or investor material is involved, explicitly mark which categories can appear as current versus future-only.
- Treat current product truth as:
  - strong in Docker, Claude, Codex, safe cache cleanup, receipts, MCP, and scheduled cleanup
  - weak or absent in Python env awareness, Node workspace awareness, Ollama, LM Studio, Hugging Face, Git/LFS, and IDE workspace intelligence

## Core Workflow

1. Identify the ecosystem surface being discussed: Docker, Python, Node, local LLM, Hugging Face, Git/LFS, or IDEs.
2. Define what DreamCleanr needs first:
   - observability only
   - safe candidate detection
   - guided cleanup
   - premium workflow
3. Preserve trust boundaries:
   - prefer read-only visibility before deletion
   - prefer project-aware rules before broad cleanup
   - do not auto-delete active project state
4. Map the work into one of these outputs:
   - detector-registry design
   - feature spec
   - safety policy
   - runtime implementation plan
   - demo-category truth table

## Product Boundaries

- Never market planned toolchain support as already shipped.
- Public site demos may show future detectors only inside clearly labeled `coming next` or `future detectors` sections.
- Keep future detector work modular by ecosystem rather than one giant cleanup rule set.
- Prefer category-level visibility and confidence scoring before destructive automation.
- Keep iPhone/iPad out of scope here except where a shared receipt/history contract matters.

## Good Deliverables

- detector registry interface sketches
- safe-delete decision criteria
- ecosystem-specific storage maps
- feature rollout order for Python, Node, local LLM, Hugging Face, Git/LFS, and IDE support
- truth tables for shipped versus planned categories used in marketing or onboarding demos

## Avoid

- generic “clean everything” logic
- advice that bypasses protected-state rules
- backend-heavy designs for local machine cleanup
