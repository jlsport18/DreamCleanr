# DreamCleanr Commercial Backend Architecture

Status: `future incubation track`

This document defines a possible future commercial backend and monorepo structure for DreamCleanr. It is not the current shipping architecture, and it does not authorize a repo rewrite.

## Current Boundary

DreamCleanr currently ships as:

- local CLI
- local MCP server
- local receipts
- local scheduling
- GitHub-first distribution

No current runtime dependency exists on:

- backend APIs
- auth
- billing
- analytics ingestion
- team dashboards

## Future Commercial Goal

If DreamCleanr later proves recurring cloud value, the recommended architecture is:

- local-first cleanup engine remains canonical
- premium macOS shell remains the primary paid surface
- backend services handle identity, billing, entitlements, feature flags, experiments, analytics ingest, and lifecycle messaging
- destructive cleanup remains local on-device

This track exists to support future hosted value, not to replace the current `Community free / Pro one-time later / Team later` product direction.

## Recommended Future Monorepo Layout

If the future commercial track is activated, use an adapted monorepo layout like this:

```text
dreamcleanr/
├── apps/
│   ├── api/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── config.py
│   │   │   ├── deps.py
│   │   │   ├── middleware/
│   │   │   │   ├── auth.py
│   │   │   │   ├── logging.py
│   │   │   │   └── rate_limit.py
│   │   │   ├── routes/
│   │   │   │   ├── health.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── users.py
│   │   │   │   ├── billing.py
│   │   │   │   ├── entitlements.py
│   │   │   │   ├── analytics.py
│   │   │   │   ├── feature_flags.py
│   │   │   │   └── webhooks_stripe.py
│   │   │   ├── models/
│   │   │   │   ├── user.py
│   │   │   │   ├── subscription.py
│   │   │   │   ├── analytics_event.py
│   │   │   │   ├── device.py
│   │   │   │   └── feature_flag.py
│   │   │   ├── schemas/
│   │   │   │   ├── auth.py
│   │   │   │   ├── billing.py
│   │   │   │   ├── analytics.py
│   │   │   │   └── entitlements.py
│   │   │   ├── services/
│   │   │   │   ├── auth_service.py
│   │   │   │   ├── stripe_service.py
│   │   │   │   ├── entitlement_service.py
│   │   │   │   ├── analytics_service.py
│   │   │   │   ├── feature_flag_service.py
│   │   │   │   └── email_service.py
│   │   │   ├── db/
│   │   │   │   ├── base.py
│   │   │   │   ├── session.py
│   │   │   │   └── migrations/
│   │   │   └── utils/
│   │   │       ├── ids.py
│   │   │       ├── time.py
│   │   │       └── telemetry.py
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   ├── worker/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── jobs/
│   │   │   │   ├── process_stripe_events.py
│   │   │   │   ├── send_lifecycle_emails.py
│   │   │   │   ├── aggregate_daily_metrics.py
│   │   │   │   └── sync_feature_flags.py
│   │   │   └── queues/
│   │   │       └── redis.py
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   └── pyproject.toml
│   ├── macos-shell/
│   │   ├── Package.swift
│   │   ├── DreamCleanrShell.xcodeproj/
│   │   └── Sources/
│   │       └── DreamCleanrShell/
│   │           ├── App/
│   │           ├── Components/
│   │           ├── Screens/
│   │           ├── Services/
│   │           │   ├── APIClient.swift
│   │           │   ├── AuthClient.swift
│   │           │   ├── BillingClient.swift
│   │           │   ├── EntitlementsClient.swift
│   │           │   └── AnalyticsClient.swift
│   │           ├── LocalEngineBridge/
│   │           ├── Store/
│   │           ├── Types/
│   │           └── Utilities/
│   └── web/
│       ├── src/
│       │   ├── app/
│       │   ├── components/
│       │   ├── pages/
│       │   └── lib/
│       ├── public/
│       ├── package.json
│       └── next.config.js
├── packages/
│   ├── shared-schemas/
│   │   ├── analytics.schema.json
│   │   ├── billing.schema.json
│   │   ├── entitlements.schema.json
│   │   └── index.md
│   ├── design-tokens/
│   │   ├── colors.json
│   │   ├── spacing.json
│   │   ├── typography.json
│   │   └── package.json
│   └── analytics-events/
│       ├── src/
│       │   └── events.ts
│       └── package.json
├── infra/
│   ├── terraform/
│   │   ├── environments/
│   │   │   ├── dev/
│   │   │   ├── staging/
│   │   │   └── prod/
│   │   └── modules/
│   ├── docker-compose.yml
│   └── k8s/
├── scripts/
│   ├── bootstrap.sh
│   ├── seed_dev_data.py
│   └── release_desktop.sh
├── .github/
│   └── workflows/
│       ├── api-ci.yml
│       ├── desktop-ci.yml
│       ├── web-ci.yml
│       └── release.yml
├── docs/
│   ├── architecture.md
│   ├── api-spec.md
│   ├── billing-flows.md
│   ├── analytics-plan.md
│   └── threat-model.md
├── .env.example
├── pnpm-workspace.yaml
├── README.md
└── Makefile
```

Notes:

- This is a future option, not an approved migration.
- The user-provided `desktop` concept is adapted into `macos-shell/` to preserve DreamCleanr's SwiftUI-first direction.
- The current single-repo Python implementation remains the only approved shipping repo.

## Service Breakdown

### macOS shell

- local scan orchestration
- receipt/history browsing
- entitlement-aware premium UX later
- future API calls for auth, billing, entitlements, and analytics
- no destructive cleanup leaves the device

### API server

- health and readiness
- GitHub OAuth and magic-link auth
- billing checkout and customer portal
- Stripe webhook ingestion
- entitlements and feature flags
- analytics ingest
- experiments and lifecycle APIs

### Worker

- Stripe webhook post-processing
- lifecycle email fanout
- daily or weekly KPI aggregation
- feature-flag sync or experiment assignment jobs

### Shared packages

- schema contracts shared across API, web, and macOS shell
- analytics event registry
- design tokens for website and future native assets

## Core Backend Modules

### Auth

- GitHub OAuth primary
- magic-link fallback
- JWT access tokens plus refresh tokens
- device-aware session revocation

### Billing

- checkout session creation
- customer portal access
- Stripe webhook handling
- subscription and invoice state projection

### Entitlements

- canonical plan resolution
- feature gating
- free versus paid capability map
- future team-seat or org policy entitlements

### Analytics and experiments

- event ingestion
- experiment and feature-flag assignment
- KPI aggregation
- lifecycle trigger surfaces

## Recommended Backend Stack

- FastAPI for the API layer
- background worker runtime alongside Redis-backed queues only if needed
- PostgreSQL for users, devices, subscriptions, entitlements, analytics metadata, experiments, and flags
- Redis for queueing, transient caching, and worker coordination only

## Environment Topology

- `dev`: local compose stack for API, Postgres, and Redis
- `staging`: production-like environment for auth, billing, and webhooks
- `prod`: minimal commercial backend only after recurring value is proven

Do not create production cloud infrastructure until the business case exists.

## First API Ship List

If this future track is ever activated, ship in this order:

1. `GET /health`
2. auth
3. checkout session
4. customer portal
5. Stripe webhook
6. entitlements
7. analytics ingest

This sequence unlocks the smallest commercial loop without moving cleanup logic off the device.

## Hard Incubation Rules

- do not replatform the current shipping repo now
- do not move cleanup execution into the backend
- do not upload filenames or file contents by default
- do not make backend work part of the current product phase
- do not let recurring pricing concepts replace the current one-time Pro shell strategy in public surfaces
