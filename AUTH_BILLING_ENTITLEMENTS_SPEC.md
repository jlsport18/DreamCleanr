# DreamCleanr Auth, Billing, And Entitlements Spec

Status: `future incubation track`

This spec defines future API and entitlement behavior if DreamCleanr ever enables commercial cloud services. It does not authorize auth, billing, or hosted entitlements in the current product phase.

## Boundary

Current DreamCleanr remains:

- local-first
- GitHub-first for distribution
- free at the core
- one-time-Pro-first for the premium macOS shell later

Future auth, billing, and entitlements exist only to support optional commercial services if that track is activated later.

## Auth Model

Recommended future identity stack:

- GitHub OAuth primary
- magic-link fallback
- short-lived JWT access token
- long-lived refresh token scoped per device

Recommended behavior:

- create a device-scoped session after GitHub OAuth or magic-link completion
- rotate refresh tokens on refresh
- revoke refresh tokens on logout
- keep entitlement reads device-safe and read-only from the client perspective

### Future auth endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/auth/github/start` | start GitHub OAuth flow |
| `GET` | `/auth/github/callback` | complete GitHub OAuth and mint session |
| `POST` | `/auth/magic-link/start` | request fallback email sign-in |
| `POST` | `/auth/magic-link/verify` | verify link token and mint session |
| `POST` | `/auth/refresh` | rotate access and refresh tokens |
| `POST` | `/auth/logout` | revoke current device session |
| `GET` | `/auth/session` | return current user and session summary |

## Billing Model

These endpoints are future-only and do not imply current public checkout.

### Future billing endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/billing/checkout-session` | create Stripe checkout for future paid plans |
| `POST` | `/billing/customer-portal` | open Stripe customer portal |
| `POST` | `/billing/webhook/stripe` | receive Stripe webhook events |
| `GET` | `/billing/subscription` | return current subscription summary |

## Entitlements

Entitlements are the future control layer for paid features. They decide access to guided UX and hosted services, not cleanup safety.

### Future entitlement endpoint

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/entitlements/current` | return resolved plan and feature access for current device/user |

### Example entitlement payload

```json
{
  "plan": "pro",
  "source": "stripe_subscription",
  "features": {
    "full_cleanup": true,
    "auto_optimize": true,
    "weekly_reports": true,
    "history_browser": true,
    "max_free_gb_cleanup": null,
    "team_dashboard": false
  },
  "updated_at": "2026-04-04T00:00:00Z"
}
```

## Feature Flags And Experiments

Future feature-flag behavior:

- feature flags gate experiments and staged UX
- entitlements gate paid access
- experiments never override safety boundaries

Recommended future endpoint:

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/feature-flags/current` | return active feature flags and experiment assignments |

## Recommended Database Tables

### `users`

- `id`
- `email`
- `github_id`
- `created_at`
- `last_seen_at`

### `devices`

- `id`
- `user_id`
- `os_version`
- `app_version`
- `device_name`
- `last_seen_at`

### `subscriptions`

- `id`
- `user_id`
- `stripe_customer_id`
- `stripe_subscription_id`
- `plan`
- `status`
- `current_period_end`

### `entitlements`

- `id`
- `user_id`
- `feature_key`
- `enabled`
- `source`
- `updated_at`

### `feature_flags`

- `id`
- `flag_key`
- `variant`
- `active`
- `rollout_rule`

### `analytics_events`

- `id`
- `user_id`
- `device_id`
- `event_name`
- `properties_json`
- `created_at`

### `experiments`

- `id`
- `key`
- `variant`
- `active`

### `experiment_assignments`

- `id`
- `experiment_id`
- `user_id`
- `device_id`
- `variant`
- `assigned_at`

## Guardrails

- billing decides access, not cleanup safety
- destructive actions remain local even if paid entitlements exist
- filenames and file contents stay local by default
- current DreamCleanr public pricing remains unchanged until a commercial decision is made
- no auth or billing implementation belongs in the current release slice
