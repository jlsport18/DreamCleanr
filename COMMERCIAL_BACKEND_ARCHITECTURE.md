# DreamCleanr Commercial Backend Architecture

Status: `future incubation track`

This document defines a possible future commercial backend and monorepo structure for DreamCleanr. It is not the current shipping architecture.

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

If DreamCleanr later proves recurring cloud value, the recommended commercial architecture is:

- local-first desktop client remains the cleanup engine
- backend handles auth, billing, entitlements, analytics ingest, feature flags, and team lifecycle
- destructive cleanup stays local on-device

## Recommended Monorepo Layout

```text
dreamcleanr/
├── apps/
│   ├── api/
│   ├── worker/
│   ├── desktop/
│   └── web/
├── packages/
│   ├── shared-schemas/
│   ├── design-tokens/
│   └── analytics-events/
├── infra/
│   ├── terraform/
│   ├── docker-compose.yml
│   └── k8s/
├── scripts/
├── docs/
└── README.md
```

## Service Breakdown

### Desktop client

- local scan engine
- local cleanup execution
- permissions handling
- receipt/history rendering
- future API calls for auth, billing, entitlements, and analytics

### API server

- auth
- billing
- entitlements
- analytics ingest
- feature flags
- lifecycle APIs

### Worker

- Stripe webhook post-processing
- lifecycle emails
- daily metrics aggregation
- feature-flag sync jobs

### Shared packages

- shared schemas
- analytics event definitions
- design tokens

## Recommended Backend Stack

- FastAPI or lightweight Node service
- PostgreSQL for users, subscriptions, entitlements, analytics metadata, experiments
- Redis for queues, caching, and worker coordination only if needed

## Shipping Order

If this future track is ever activated, ship in this order:

1. health
2. auth
3. billing checkout
4. billing portal
5. Stripe webhook
6. entitlements
7. analytics ingest

## Hard Incubation Rules

- do not replatform the current shipping repo now
- do not move cleanup execution into the backend
- do not upload filenames or file contents by default
- do not make backend work part of the current `v0.3.3` release
