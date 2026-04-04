# DreamCleanr Analytics And KPI Plan

`future incubation track`

This document describes the future analytics surface for DreamCleanr. It is not part of the current GitHub-first, local-first product.

## Current Product Truth

DreamCleanr currently ships without a mandatory backend analytics layer.

That is intentional. The current product should continue to work locally without hosted telemetry.

## Why This Exists

If DreamCleanr later adds cloud features or team workflows, the analytics system should already know what to measure:

- activation
- retention
- cleanup effectiveness
- paid conversion
- team adoption

## Event Model

Track only coarse, product-useful events.

### Core Events

- `scan_started`
- `scan_completed`
- `recoverable_gb_found`
- `free_cleanup_executed`
- `paywall_viewed`
- `checkout_started`
- `checkout_completed`
- `weekly_active_device`
- `feature_used_auto_optimize`

### Optional Future Events

- `onboarding_step_completed`
- `pro_interest_submitted`
- `team_invite_sent`
- `team_policy_applied`
- `feature_flag_exposed`

## Analytics Rules

- do not log filenames by default
- do not upload file contents
- keep payloads coarse and non-sensitive
- separate product analytics from support telemetry
- limit analytics to what is needed for pricing and product decisions

## KPI Dashboard

Future KPI surfaces should answer:

- how many installs activate
- how much space the product finds
- how much free cleanup actually happens
- how often people return
- where users hit the paywall
- how many users convert
- what keeps teams retained

### Minimum Dashboard Views

1. Acquisition
2. Activation
3. Cleanup value
4. Conversion
5. Retention
6. Team usage

## Metrics To Track Weekly

- installs
- scan completion percent
- average GB found
- free cleanup percent
- paywall viewed percent
- checkout started percent
- checkout completed percent
- monthly to annual mix
- 30-day paid retention
- referral rate

## Lifecycle Reporting

If DreamCleanr later adds lifecycle messaging, analytics should support:

- onboarding completion
- day 2 nudge
- day 5 nudge
- weekly summary
- upgrade prompt

## Non-Goals For The Current Phase

- no analytics SDK in the current product
- no mandatory telemetry
- no filename logging
- no content logging
- no hosted dashboard requirement before the product needs it

