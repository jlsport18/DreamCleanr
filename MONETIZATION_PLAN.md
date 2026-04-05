# DreamCleanr Monetization Plan

Canonical source: [DREAMCLEANR_MASTER_STRATEGY.md](DREAMCLEANR_MASTER_STRATEGY.md)

Supporting docs:

- [site/pricing.html](site/pricing.html)
- [MACOS_SHELL_PLAN.md](MACOS_SHELL_PLAN.md)
- [COMMERCIAL_BACKEND_ARCHITECTURE.md](COMMERCIAL_BACKEND_ARCHITECTURE.md)
- [AUTH_BILLING_ENTITLEMENTS_SPEC.md](AUTH_BILLING_ENTITLEMENTS_SPEC.md)
- [ANALYTICS_AND_KPI_PLAN.md](ANALYTICS_AND_KPI_PLAN.md)
- [MRR_ROADMAP.md](MRR_ROADMAP.md)
- [STRIPE_COMMERCIAL_ARCHITECTURE.md](STRIPE_COMMERCIAL_ARCHITECTURE.md)
- [CLOUD_ARCHITECTURE_FUTURE.md](CLOUD_ARCHITECTURE_FUTURE.md)

## Decision

DreamCleanr stays `open-core premium`.

This rollup stays subordinate to [DREAMCLEANR_MASTER_STRATEGY.md](DREAMCLEANR_MASTER_STRATEGY.md) and its `$dreamcleanr-strategy-analysis-operator` workflow.

That means:

- keep the current CLI, MCP, receipts, and scheduling free
- monetize convenience, visibility, and policy later
- keep ads and affiliates secondary
- avoid backend-heavy billing or telemetry in the current phase

## Package Defaults

| Package | Default price | Role |
|---|---:|---|
| Community | Free | Trust-building and distribution engine |
| Pro | `$29` intro / `$49` standard one-time | Premium macOS shell and convenience layer |
| Team Pilot | `$199/year` up to 5 Macs | Policy and rollout value for small teams |

## Monetization Rules

- Do not paywall the safety-first cleanup engine early
- Do not launch Pro before the macOS shell makes life materially easier
- Do not launch Team before repeated team demand exists
- If a future iPhone/iPad app unlocks digital features in-app, use App Store-compliant purchase flows

## What Gets Monetized

Good paid lanes:

- premium native shell
- guided cleanup and environment-aware recommendations
- richer history, reporting, and team policy packs

Bad paid lanes right now:

- subscription pressure on the core CLI
- cloud dashboards
- ad clutter in cleanup flows
- backend dependence just to justify pricing
- a fake public checkout before Pro exists

## Pricing Model Alternatives

### Current canonical

- `Community`: free
- `Pro`: one-time later
- `Team`: later pilot

### Future optional

- recurring Team pricing
- optional recurring automation or hosted services only if DreamCleanr later adds real cloud value
- all such work stays in the incubation docs until the canonical strategy intentionally changes

### Rejected for now

- live subscription-first Pro
- public Stripe checkout before the premium shell exists
- forcing a backend dependency into the current local-first product
