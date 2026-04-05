# DreamCleanr Onboarding Conversion Spec

This is the source of truth for DreamCleanr's install-to-upgrade flow.

## Decision

Split the onboarding funnel into two surfaces:

- `Now`: a truthful marketing-site demo that explains the flow without pretending the browser is scanning the local machine
- `Later`: the real install -> scan -> first win -> upgrade flow inside the premium macOS shell

The upgrade target remains:

- `Community`: free and live
- `Pro`: one-time premium macOS shell later
- `Team`: later pilot

Do not convert this flow into monthly-subscription-first copy unless the commercial strategy changes at the canonical level.

## Goals

- deliver value understanding in under 60 seconds
- show clear ROI in reclaimed space, calmer workflows, and safer cleanup decisions
- create upgrade pressure through convenience and visibility, not through fake browser actions

## Product-Truth Rules

- The website demo must say it is a demo.
- The website must never imply that browser code is scanning local files.
- Current demo categories may only cover:
  - Docker reclaimable layers
  - safe cache and log noise
  - stale helper and probe residue
  - protected AI state held back from cleanup
- Python environments, Node workspaces, Hugging Face, Ollama, and LM Studio appear only as `coming next` detectors until support exists.
- The real upgrade moment is for the later one-time Pro shell, not a live SaaS paywall.

## Surface Split

| Surface | Purpose | Allowed behavior | Upgrade CTA |
|---|---|---|---|
| Marketing site demo | explain the product funnel and show sample outcomes | animated sample scan, sample numbers, clear demo labeling | `Join Pro Early Access`, `Download Free`, `See the Pricing Plan` |
| Free CLI / MCP today | actual current product entry | real local scan, cleanup preview, receipt generation, scheduling | none beyond the existing free product |
| Future macOS shell | real premium onboarding | real local scan, richer history, guided presets, native upsell | one-time Pro purchase later |

## Step Logic

### 1. First Open

- Headline: `Let's see what your AI stack is hiding...`
- Supporting copy: `Takes about 30 seconds in this sample flow. No browser files are scanned or deleted.`
- Primary CTA: `Start Smart Scan`
- Secondary CTA: `Skip to free install`

### 2. Live Scan

- use animated count-up and category reveals to build anticipation
- keep the unit either:
  - `sample machine footprint surfaced`
  - or `sample reclaimable space found`
- include protected-state visibility so the product feels conservative, not reckless

### 3. Results Reveal

- results should say what is safely reclaimable now from known-safe surfaces
- keep protected AI state visible in the breakdown
- show why DreamCleanr is different:
  - it separates reclaimable from protected
  - it does not collapse everything into one scary delete button

### 4. First Win

- do not use fake in-browser cleanup
- instead say:
  - `Start with a real local scan and a visible receipt.`
- Primary CTA: `Run your first local scan`
- Secondary CTA: `Read the sample receipt`

### 5. Upgrade Moment

- Headline: `Want guided cleanup, richer history, and premium workflows?`
- Supporting copy: remind the user that:
  - free CLI, MCP, receipts, and scheduling stay available today
  - premium value comes later through the native shell
- Primary CTA: `Join Pro Early Access`
- Secondary CTA: `See the Pricing Plan`

## Test Structure

Test one major variable at a time:

- headline angle
- CTA phrasing
- paywall timing
- free cleanup cap
- annual pricing emphasis

Only the first two are valid for current public surfaces. Paywall timing, free cleanup cap, and annual pricing emphasis are future native-shell or future commercial concepts only.

## Copy Test Variants

### Hero / Hook Variants

- Variant A, pain-focused:
  - Headline: `Your AI workflow is wasting space and slowing your Mac down.`
  - Subheadline: `DreamCleanr surfaces Docker sprawl, cache noise, stale helper residue, and protected AI state safely.`
  - CTA: `Start Smart Scan`
- Variant B, speed-focused:
  - Headline: `See reclaimable storage in under 60 seconds.`
  - Subheadline: `A trust-first cleanup flow for Docker-heavy and AI-heavy Macs.`
  - CTA: `Scan My Mac`
- Variant C, curiosity-focused:
  - Headline: `What is actually taking up space on your Mac?`
  - Subheadline: `See sample reclaimable space, protected AI state, and cleanup-safe surfaces without guessing.`
  - CTA: `Find Out Now`
- Variant D, category-creation:
  - Headline: `The cleanup layer for AI developer Macs.`
  - Subheadline: `DreamCleanr separates reclaimable storage from protected state instead of pushing a blind delete button.`
  - CTA: `See It In Action`

### Result-Screen Variants

- `You could safely reclaim meaningful space from known-safe surfaces right now.`
- `Here is reclaimable space DreamCleanr can surface without touching protected AI state.`
- `This is the storage you can get back without turning cleanup into a blind bet.`

### Paywall Variants

- `Want guided cleanup, richer history, and premium workflows?`
- `Unlock one-click guidance and better local visibility in the premium shell later.`
- `Free users recover space. Pro users recover time.`

### Upgrade Copy Variants

- `Don't leave safe cleanup and visibility on the table.`
- `Unlock guided cleanup in the premium shell later.`
- `One broken environment costs more than a trustworthy cleanup workflow.`

### Upgrade CTA Variants

- `Join Pro Early Access`
- `Unlock Guided Cleanup`
- `See the Premium Shell Plan`
- `Recover More With Pro Later`

Do not use:

- `Cancel anytime`
- live monthly subscription language
- fake personalized savings claims unless the current surface has real local data

## Current Versus Future Categories

| Category | Website demo now | Free product now | Future shell later |
|---|---|---|---|
| Docker reclaimable layers | yes | yes | yes |
| Safe cache and log noise | yes | yes | yes |
| Stale helper residue | yes | yes | yes |
| Protected AI state | yes | yes | yes |
| Python environments | teaser only | no | planned |
| Node workspace intelligence | teaser only | no | planned |
| Hugging Face visibility | teaser only | no | planned |
| Ollama / LM Studio visibility | teaser only | no | planned |
| Project-aware cleanup safety | teaser only | no | planned |

## Future-Only Concept Tests

These concepts may appear in native-shell mockups or future commercial docs only:

- monthly or yearly pricing emphasis
- seat or team dashboard framing
- checkout timing experiments
- cleanup-cap experiments tied to hosted entitlements

They are not current public-site behaviors.

## Upgrade Trigger Rules

- use the first real local scan and receipt as the trust-building moment
- use richer history, guided cleanup, and presets as the premium upsell
- do not gate basic safety or basic cleanup truth behind Pro

## Metrics To Watch Later

When the real macOS shell exists, track:

- install -> first scan completion
- first scan -> first cleanup preview
- first preview -> repeat usage
- free -> Pro interest
- Pro interest -> conversion once the shell is live

Until then, the site can track only coarse public-surface behavior if analytics are ever added later.

## Lifecycle Email Sequence

These are later lifecycle messages, not current product behavior.

### Day 0

- Subject: `You've still got storage left to recover`
- Body: `Your first scan surfaced reclaimable space on your Mac. DreamCleanr keeps the cleanup flow local, visible, and receipt-first so you can finish the job safely when you're ready.`

### Day 2

- Subject: `Docker is probably growing again`
- Body: `Containers, images, and cache layers pile up quickly. DreamCleanr is designed to surface what is reclaimable while leaving protected AI state and active workflows alone.`

### Day 5

- Subject: `Free up more space without touching active projects`
- Body: `Project-aware safety is the long-term differentiator. DreamCleanr's premium shell is being designed around guided cleanup, richer history, and safer workflow-aware visibility rather than blind deletion.`
