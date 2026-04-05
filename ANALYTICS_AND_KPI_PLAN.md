# DreamCleanr Analytics And KPI Plan

Status: `future incubation track`

This plan defines the future analytics model if DreamCleanr later activates commercial cloud services. It does not authorize analytics SDKs, hosted telemetry, or ingestion in the current product phase.

## Analytics Principles

- file analysis stays local
- filenames and file paths stay local by default
- ingest only coarse metadata needed for product and business decisions
- keep analytics optional and privacy-aligned
- never let analytics drive destructive cleanup decisions

## Event Taxonomy

| Event | Trigger | Suggested properties | Privacy notes |
|---|---|---|---|
| `scan_started` | user starts a real scan | `surface`, `mode`, `detector_set`, `app_version` | no project names or file paths |
| `scan_completed` | scan finishes successfully | `surface`, `duration_ms`, `protected_item_count`, `reclaimable_gb` | aggregate counts only |
| `recoverable_gb_found` | reclaimable total is shown | `surface`, `reclaimable_gb`, `category_breakdown_summary` | category totals only |
| `free_cleanup_executed` | user completes a real free cleanup action | `surface`, `mode`, `gb_removed`, `receipt_written` | no file-level detail |
| `paywall_viewed` | future premium upsell is shown | `surface`, `offer_stage`, `context` | future-only event |
| `checkout_started` | user enters future paid checkout flow | `plan`, `billing_interval`, `surface` | future-only event |
| `checkout_completed` | future paid checkout succeeds | `plan`, `billing_interval`, `surface`, `source` | future-only event |
| `weekly_active_device` | device is active in a weekly window | `surface`, `app_version` | heartbeat only |
| `feature_used_auto_optimize` | user runs future automated cleanup | `surface`, `preset`, `schedule_type` | future-only event |

## Event Payload Rules

- include user or anonymous install identifier only when needed
- include device identifier only when needed
- include coarse numeric or categorical properties only
- avoid project names, filenames, raw paths, repo names, and prompt text by default

## Experiment Tracking

Future experiments should be limited to:

- headline and CTA variants
- onboarding sequencing
- premium upsell timing
- annual-versus-monthly emphasis only if recurring pricing is ever activated later

Recommended experiment surfaces:

- `experiment_assigned`
- `variant_viewed`
- `variant_converted`

Experiment systems must never:

- hide safety disclosures
- create fake urgency
- misrepresent detector support

## Minimum KPI Dashboard

Track these future commercial metrics weekly:

### Acquisition

- installs
- landing-page conversion
- source or channel mix

### Activation

- install -> first scan completion
- first scan -> result view
- result view -> first meaningful free action
- average GB found

### Monetization

- paywall viewed rate
- checkout started rate
- checkout completed rate
- monthly-to-annual mix if recurring pricing exists later

### Retention

- weekly active device
- repeat scan rate
- repeat cleanup rate
- 30-day paid retention
- referral rate

## North-Star Metrics By Stage

### Early validation

- install -> first scan
- first scan -> result view
- result view -> first meaningful action

### Paid validation

- free -> Pro interest
- Pro interest -> checkout started
- checkout started -> paid conversion

### Retention

- weekly active device
- repeat scan rate
- repeat cleanup rate
- paid retention

## Lifecycle Triggers

If lifecycle email is added later, use these trigger surfaces:

| Trigger | Future message angle |
|---|---|
| first scan completed | remind the user what reclaimable space was surfaced |
| first free action completed | reinforce that safe cleanup already produced value |
| paywall viewed without conversion | invite the user back to the premium shell or future commercial offer |
| paid onboarding completed | highlight automation, history, and future retention loops |

## Hard Boundary

- current DreamCleanr should not add hosted analytics infrastructure in the current product phase
- analytics remain optional even in future commercial builds
- the public site must not imply hidden telemetry or account requirements that do not exist
