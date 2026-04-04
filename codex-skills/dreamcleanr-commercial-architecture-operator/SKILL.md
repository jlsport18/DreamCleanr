---
name: dreamcleanr-commercial-architecture-operator
description: Plan DreamCleanr's future-only commercial and backend architecture for auth, billing, entitlements, analytics, feature flags, API surfaces, KPI dashboards, MRR models, and monorepo layout. Use when DreamCleanr needs FastAPI, Stripe, Postgres, Redis, entitlements, analytics ingest, subscriptions, MRR, or backend repo structure planning without changing the current local-first product truth.
---

# DreamCleanr Commercial Architecture Operator

## Overview

Own DreamCleanr's future commercial incubation track so backend, billing, analytics, and MRR planning can move forward without mutating the current shipping model.

## Use This Skill

- Read [../../STRIPE_COMMERCIAL_ARCHITECTURE.md](../../STRIPE_COMMERCIAL_ARCHITECTURE.md), [../../CLOUD_ARCHITECTURE_FUTURE.md](../../CLOUD_ARCHITECTURE_FUTURE.md), [../../MONETIZATION_PLAN.md](../../MONETIZATION_PLAN.md), and [../../DREAMCLEANR_MASTER_STRATEGY.md](../../DREAMCLEANR_MASTER_STRATEGY.md) first.
- Read [references/incubation-boundaries.md](references/incubation-boundaries.md) before proposing any commercial or backend path.
- Keep every output labeled as `future incubation track` unless the canonical strategy has changed.

## Core Workflow

1. Confirm the current shipping product remains local-first and GitHub-first.
2. Separate what belongs in current release/launch work from what belongs in future-commercial incubation.
3. Specify future backend modules, APIs, entitlements, analytics, and KPI systems only at the planning level.
4. Tie MRR math and paid-roadmap sequencing back to actual DreamCleanr product layers.

## Architecture Rules

- Do not propose runtime backend work as part of current release slices.
- Do not replace one-time Pro shell strategy with live subscriptions in public surfaces.
- Treat FastAPI, Postgres, Redis, Stripe, auth, analytics, and feature flags as future only.
- Keep destructive actions local on-device even in future commercial plans.

## Good Deliverables

- future backend repo structures
- auth and entitlement specs
- analytics event plans and KPI dashboards
- MRR pathways and pricing-mix analysis
- incubation-stage API ship lists

## Avoid

- silently pivoting DreamCleanr into SaaS-first execution
- mixing current pricing with future subscription options
- recommending server-side collection of sensitive filenames or file contents
