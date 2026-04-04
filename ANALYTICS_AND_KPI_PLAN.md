# DreamCleanr Analytics And KPI Plan

Status: `future incubation track`

This plan defines the future analytics model if DreamCleanr later activates commercial cloud services. It does not authorize analytics SDKs or ingestion in the current release.

## Analytics Principles

- file analysis stays local
- filenames stay local by default
- ingest only coarse metadata needed for product and business decisions
- keep analytics optional and privacy-aligned

## Future Event List

- `scan_started`
- `scan_completed`
- `recoverable_gb_found`
- `free_cleanup_executed`
- `paywall_viewed`
- `checkout_started`
- `checkout_completed`
- `weekly_active_device`
- `feature_used_auto_optimize`

## Event Payload Rules

- include user or anonymous install identifier only when needed
- include device identifier only when needed
- include coarse numeric or categorical properties
- avoid project names, filenames, and raw file paths by default

## Minimum KPI Dashboard

Track weekly:

- installs
- first scan completion rate
- average GB found
- free cleanup rate
- paywall viewed rate
- checkout started rate
- checkout completed rate
- monthly to annual mix
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

- first scan completed
- free action completed
- paywall viewed without conversion
- paid onboarding completed

Current DreamCleanr should not add this infrastructure in the `v0.3.3` release.
