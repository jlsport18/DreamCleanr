# DreamCleanr Stripe Commercial Architecture

This document records a future billing architecture option. It is not the current DreamCleanr business model and it does not authorize runtime Stripe work in this phase.

## Current Commercial Truth

Today DreamCleanr is:

- `Community`: free
- `Pro`: later one-time premium macOS shell
- `Team`: later pilot

This repo does not currently ship:

- Stripe checkout
- subscription accounts
- webhook-driven entitlements
- paid feature gating

## Why Keep This Document

The commercial path may expand later if DreamCleanr adds:

- Team billing
- optional cloud services
- recurring premium automation that justifies subscriptions

Until then, this is planning material only.

## Future Subscription Reference Model

This section captures the exact pricing structure requested for a later SaaS option.

### Product 1: DreamCleanr Pro

- `$19/month`
- `$149/year`

### Product 2: DreamCleanr Team

- `$49/month per seat`

This is a future option, not the canonical current pricing model.

## Stripe Product Map

| Stripe product | Stripe price | Status |
|---|---|---|
| DreamCleanr Pro | monthly recurring | future option only |
| DreamCleanr Pro | yearly recurring | future option only |
| DreamCleanr Team | monthly recurring, per seat | future option only |

## Required Backend Surfaces

If DreamCleanr ever turns on Stripe, it will need:

- account identity layer
- checkout-session creation endpoint
- webhook verification endpoint
- entitlement storage
- billing-portal or subscription-management path

Suggested stack later:

- FastAPI or Node backend
- PostgreSQL for subscriptions and entitlements
- Redis only if caching or queueing becomes necessary

## Checkout Session Example

Future reference only:

```javascript
const stripe = require("stripe")(process.env.STRIPE_SECRET_KEY);

app.post("/create-checkout-session", async (req, res) => {
  const { priceId } = req.body;

  const session = await stripe.checkout.sessions.create({
    mode: "subscription",
    payment_method_types: ["card"],
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: "https://yourapp.com/success",
    cancel_url: "https://yourapp.com/cancel"
  });

  res.json({ url: session.url });
});
```

## Webhook Example

Future reference only:

```javascript
app.post("/webhook", express.raw({ type: "application/json" }), (req, res) => {
  const event = req.body;

  if (event.type === "checkout.session.completed") {
    const session = event.data.object;

    // Save subscription state
    // Activate paid entitlements
  }

  res.sendStatus(200);
});
```

## Feature Gating Model

Future reference only:

```javascript
if (user.plan === "pro") {
  enableFullCleanup();
  enableAutoOptimize();
} else {
  limitCleanupTo10GB();
}
```

This exact gating style is not appropriate for current DreamCleanr public messaging because the repo does not currently ship paid entitlements or artificial free-tier cleanup caps.

## Upgrade Trigger Concepts

Future Stripe-based triggers could include:

- user reaches a future premium workflow limit
- user wants automated optimization beyond the free product scope
- user wants team policy or admin features

Do not add these triggers to the live product until the premium value is real and the commercial architecture exists.

## Privacy And Compliance Notes

- keep file analysis local
- never upload file contents for billing
- limit server-side data to identity, billing, and coarse metadata if cloud surfaces ever exist
- align public pricing and checkout language with actual runtime capability

## Explicit Non-Goals For This Phase

- no Stripe SDK installation
- no checkout button
- no webhook endpoint
- no customer database
- no live subscription marketing

Canonical monetization remains documented in [MONETIZATION_PLAN.md](MONETIZATION_PLAN.md).
