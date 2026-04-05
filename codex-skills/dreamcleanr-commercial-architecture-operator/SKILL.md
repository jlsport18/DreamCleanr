---
name: dreamcleanr-commercial-architecture-operator
description: Plan DreamCleanr's future-only commercial and backend architecture for auth, billing, entitlements, analytics, feature flags, API surfaces, KPI dashboards, MRR models, and monorepo layout. Use when DreamCleanr needs FastAPI, Stripe, Postgres, Redis, entitlements, analytics ingest, subscriptions, MRR, or backend repo structure planning without changing the current local-first product truth.
---

# DreamCleanr Commercial Architecture Operator

## Overview

Own DreamCleanr's future commercial incubation track so backend, billing, analytics, and MRR planning can move forward without mutating the current shipping model.

## Use This Skill

- Read [../../COMMERCIAL_BACKEND_ARCHITECTURE.md](../../COMMERCIAL_BACKEND_ARCHITECTURE.md), [../../AUTH_BILLING_ENTITLEMENTS_SPEC.md](../../AUTH_BILLING_ENTITLEMENTS_SPEC.md), [../../ANALYTICS_AND_KPI_PLAN.md](../../ANALYTICS_AND_KPI_PLAN.md), [../../MRR_ROADMAP.md](../../MRR_ROADMAP.md), [../../STRIPE_COMMERCIAL_ARCHITECTURE.md](../../STRIPE_COMMERCIAL_ARCHITECTURE.md), [../../CLOUD_ARCHITECTURE_FUTURE.md](../../CLOUD_ARCHITECTURE_FUTURE.md), [../../MONETIZATION_PLAN.md](../../MONETIZATION_PLAN.md), and [../../DREAMCLEANR_MASTER_STRATEGY.md](../../DREAMCLEANR_MASTER_STRATEGY.md) first.
- Read [references/incubation-boundaries.md](references/incubation-boundaries.md) before proposing any commercial or backend path.
- Keep every output labeled as `future incubation track` unless the canonical strategy has changed.

## Core Workflow

1. Confirm the current shipping product remains local-first and GitHub-first.
2. Separate what belongs in current release/launch work from what belongs in future-commercial incubation.
3. Specify the future repo tree, backend modules, APIs, auth flows, entitlements, feature flags, analytics, and KPI systems only at the planning level.
4. Tie MRR math, annual-versus-monthly scenarios, and team-seat concepts back to actual DreamCleanr product layers.
5. Mark any recurring pricing, lifecycle email, portal, or experiment framework as future-only unless the canonical strategy explicitly changes.

## Architecture Rules

- Do not propose runtime backend work as part of current release slices.
- Do not replace one-time Pro shell strategy with live subscriptions in public surfaces.
- Treat FastAPI, Postgres, Redis, Stripe, auth, analytics, and feature flags as future only.
- Keep destructive actions local on-device even in future commercial plans.
- Never treat the proposed monorepo layout as an approved migration of the current shipping repo.

## Good Deliverables

- future backend repo structures adapted to DreamCleanr's SwiftUI-first product direction
- auth, billing, entitlement, and feature-flag specs
- database table definitions and future payload contracts
- analytics event plans, KPI dashboards, experiment models, and lifecycle triggers
- MRR pathways, pricing-mix analysis, and channel/offer scenarios
- incubation-stage API ship lists

## Avoid

- silently pivoting DreamCleanr into SaaS-first execution
- mixing current pricing with future subscription options
- recommending server-side collection of sensitive filenames or file contents
- implying that backend identity, Stripe, analytics, or hosted entitlements already exist in the shipping product
