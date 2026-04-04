# DreamCleanr Auth, Billing, And Entitlements Spec

`future incubation track`

This document captures a future commercial system for DreamCleanr. It does not describe current runtime behavior.

## Current Product Truth

DreamCleanr is currently:

- Community free
- Pro later as a one-time premium macOS shell
- Team later
- local-first and GitHub-first

Do not use this spec to justify live backend billing work in the current release plan.

## Future Auth Model

Recommended future auth options:

- GitHub OAuth
- magic-link fallback
- JWT access and refresh tokens

### Suggested Endpoints

- `POST /auth/github/start`
- `GET /auth/github/callback`
- `POST /auth/refresh`
- `POST /auth/logout`

## Future Billing Model

If DreamCleanr later needs recurring billing, define billing as a separate service boundary.

### Suggested Endpoints

- `POST /billing/checkout-session`
- `POST /billing/customer-portal`
- `POST /billing/webhook/stripe`
- `GET /billing/subscription`

### Subscription Options To Model Later

- Pro monthly
- Pro yearly
- Team per seat

Those are future options only. They do not change current pricing.

## Entitlements Model

Entitlements should be the source of truth for paid access, not the billing provider itself.

### Example Entitlement Payload

```json
{
  "plan": "pro",
  "features": {
    "full_cleanup": true,
    "auto_optimize": true,
    "weekly_reports": true,
    "max_free_gb_cleanup": null,
    "team_dashboard": false
  }
}
```

### Entitlement Rules

- use feature-level flags instead of one giant boolean
- keep the cleanup engine local even when entitlements are remote
- do not ship server-side destructive cleanup
- keep feature names human-readable and stable

## Stripe Webhook Responsibilities

Future webhook processing should:

- verify the event
- persist subscription state
- sync entitlements
- trigger lifecycle jobs
- ignore non-billing noise

## Suggested Data Model

### `users`

- id
- email
- github_id
- created_at
- last_seen_at

### `devices`

- id
- user_id
- os_version
- app_version
- device_name
- last_seen_at

### `subscriptions`

- id
- user_id
- stripe_customer_id
- stripe_subscription_id
- plan
- status
- current_period_end

### `entitlements`

- id
- user_id
- feature_key
- enabled
- source

### `analytics_events`

- id
- user_id
- device_id
- event_name
- properties_json
- created_at

### `experiments`

- id
- key
- variant
- active

## Safety Rules

- never upload file contents by default
- keep destructive actions local on device
- let backend systems decide billing, not cleanup
- treat analytics as coarse metadata unless explicit opt-in exists

