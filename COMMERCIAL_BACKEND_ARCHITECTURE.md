# DreamCleanr Commercial Backend Architecture

`future incubation track`

This document describes the backend and monorepo layout DreamCleanr could adopt later if the product proves recurring cloud, entitlement, or team-management value. It is not the current shipping architecture.

## Current Product Truth

DreamCleanr currently remains:

- local-first
- GitHub-first
- preview-first
- free at the core
- one-time Pro later as a premium macOS shell
- Team later, after repeated demand

No runtime backend work belongs in the current release plan.

## Why This Exists

Keep the future option explicit so the repo can later support:

- auth
- billing
- entitlements
- analytics ingest
- feature flags
- team rollout support
- optional metadata sync

The architecture only makes sense if those needs become real.

## Recommended Future Monorepo Structure

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
└── .github/workflows/
```

## Future Backend Modules

### `apps/api`

Own:

- auth
- billing
- entitlements
- analytics ingest
- feature flags
- user and device metadata

Suggested backend stack later:

- FastAPI
- PostgreSQL
- Redis if queueing or caching is needed

### `apps/worker`

Own:

- Stripe webhook post-processing
- lifecycle emails
- daily metric aggregation
- feature-flag sync

### `apps/desktop`

Own:

- local scan engine
- permissions
- cleanup execution
- UI wrappers for the local engine

### `apps/web`

Own:

- marketing site
- pricing
- docs
- waitlist or early-access surfaces

### `packages/shared-schemas`

Own:

- billing schemas
- entitlement schemas
- analytics event schemas

### `packages/analytics-events`

Own:

- canonical event names
- properties shared by api, worker, and desktop

## First API Ship List

If DreamCleanr ever turns this on, ship these first:

1. `health`
2. `auth`
3. `checkout`
4. `portal`
5. `webhook`
6. `entitlements`
7. `analytics ingest`

Ship order should stay minimal and revenue-oriented.

## Design Rules

- never upload filenames by default
- keep file contents local
- upload only aggregate metadata unless opt-in is explicit
- keep destructive cleanup local on device
- let the backend decide billing and experiments, not file deletion

## Deployment Shape

Later environments can be split by purpose:

- `dev`
- `staging`
- `prod`

Later infrastructure could include:

- Terraform for cloud resources
- Docker Compose for local emulation
- Kubernetes only if scale justifies it

## Non-Goals For The Current Phase

- no runtime backend service
- no auth service
- no billing service
- no Stripe SDK
- no feature-flag system
- no analytics SDK
- no team dashboard

