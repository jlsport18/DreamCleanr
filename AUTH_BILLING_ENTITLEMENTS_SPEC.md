# DreamCleanr Auth, Billing, And Entitlements Spec

Status: `future incubation track`

This spec defines future API and entitlement behavior if DreamCleanr ever enables commercial cloud services.

## Auth Model

Recommended auth surfaces:

- GitHub OAuth primary
- magic-link fallback
- JWT access token plus refresh token

### Future auth endpoints

- `POST /auth/github/start`
- `GET /auth/github/callback`
- `POST /auth/refresh`
- `POST /auth/logout`

## Billing Model

These are future-only billing endpoints, not current runtime work.

### Future billing endpoints

- `POST /billing/checkout-session`
- `POST /billing/customer-portal`
- `POST /billing/webhook/stripe`
- `GET /billing/subscription`

## Entitlements

Entitlements are the future control layer for paid features.

Example payload:

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

## Database Tables

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

## Guardrails

- billing decides access, not cleanup safety
- destructive actions remain local even if paid entitlements exist
- no file contents uploaded for auth, billing, or entitlement checks
- current DreamCleanr public pricing remains unchanged until a commercial decision is made
