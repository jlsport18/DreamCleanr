---
name: dreamcleanr-native-shell-engineer
description: Plan and build DreamCleanr's premium macOS shell, shared receipt/history contract, paired status model, and future iPhone/iPad companion boundary. Use when DreamCleanr needs SwiftUI shell planning, native receipt browsing, premium preset workflows, or Apple-product sequencing that preserves the current local engine.
---

# DreamCleanr Native Shell Engineer

## Overview

Turn DreamCleanr's current local engine into a premium native macOS experience without duplicating cleanup logic or adding backend dependence.

## Use This Skill

- Read [MACOS_SHELL_PLAN.md](../../MACOS_SHELL_PLAN.md), [IOS_APP_STORE_READINESS.md](../../IOS_APP_STORE_READINESS.md), [DREAMCLEANR_MASTER_STRATEGY.md](../../DREAMCLEANR_MASTER_STRATEGY.md), and [ONBOARDING_CONVERSION_SPEC.md](../../ONBOARDING_CONVERSION_SPEC.md) first when they exist.
- Treat the macOS shell as the first paid moat.
- Treat iPhone/iPad as a later companion, not a generic device cleaner.

## Core Workflow

1. Start from the current Python engine and receipt outputs.
2. Design native surfaces that wrap the engine instead of reimplementing it.
3. Define shared interfaces first:
   - receipt/history contract
   - preset model
   - paired status summary
   - real app onboarding flow
4. Keep local-first and preview-first behavior intact.

## Native Product Rules

- The macOS shell sells convenience, visibility, and history, not a different cleanup engine.
- The real install -> scan -> free win -> upgrade funnel belongs in the future macOS shell, not in current browser copy.
- The iPhone/iPad app should consume shared report/state contracts later.
- Do not design backend-heavy sync as a prerequisite for the shell.
- Keep App Store policy boundaries in mind when discussing future mobile work.

## Good Deliverables

- SwiftUI architecture plans
- Figma-ready frame structures for onboarding, dashboard, scan, settings, paywall, and analytics
- receipt/history browsing models
- preset workflow designs
- pairing contract proposals

## Avoid

- a second cleanup implementation in Swift
- generic cleaner UI language
- promising remote destructive control before the pairing model is mature
- treating browser-demo metrics as native product truth
