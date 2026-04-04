# DreamCleanr Future Cloud Architecture

This is a future-state architecture document. It does not authorize backend work in the current phase.

## Decision

DreamCleanr stays `local-first` by default.

Any future cloud layer must remain optional and justify its own complexity. The current product does not need cloud infrastructure to deliver core cleanup value.

## Current State

Today DreamCleanr runs as:

- local CLI
- local MCP server
- local receipts
- local scheduling

There is no current backend for:

- accounts
- billing
- sync
- analytics ingestion
- team dashboards

## Why A Cloud Layer Might Exist Later

Only add cloud infrastructure if DreamCleanr needs:

- paid team management
- cross-machine policy handling
- optional metadata sync
- billing and entitlement storage
- hosted update of models or recommendations that cannot stay local

## Canonical Architecture

### Client

- macOS CLI and future macOS shell remain the primary product
- iPhone/iPad companion later consumes shared receipt/history contracts

### Local Engine

- file scanning
- cleanup planning
- policy decisions
- receipt generation

These stay local.

### Optional Cloud Layer

Possible stack later:

- FastAPI or Node service
- PostgreSQL for accounts, entitlements, and team state
- Redis only if async jobs or caching become necessary
- Stripe for future billing
- GitHub login or another lightweight auth layer

## Privacy Model

- file contents stay local
- cleanup decisions stay local by default
- server-side data should be limited to identity, billing, and coarse metadata if cloud features ever exist
- do not upload sensitive project files just to create dashboards

## Analytics Model

If DreamCleanr later adds analytics, prefer:

- install events
- feature activation
- coarse reclaim totals
- Pro-interest and conversion events

Avoid:

- file-name logging
- content upload
- verbose machine telemetry that is not necessary

## Phased Rollout

1. local-only product
2. optional GitHub-first early access and feedback collection
3. optional billing/entitlements if premium runtime features require it
4. optional team dashboard and policy layer

## Non-Goals In This Phase

- no backend service
- no auth
- no Stripe runtime code
- no analytics SDK
- no sync infrastructure

Pair this document with:

- [MONETIZATION_PLAN.md](MONETIZATION_PLAN.md)
- [STRIPE_COMMERCIAL_ARCHITECTURE.md](STRIPE_COMMERCIAL_ARCHITECTURE.md)
- [MACOS_SHELL_PLAN.md](MACOS_SHELL_PLAN.md)
