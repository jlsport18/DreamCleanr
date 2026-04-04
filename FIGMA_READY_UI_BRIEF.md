# DreamCleanr Figma-Ready UI Brief

This is the implementation-ready UI brief for future design work. It is not a claim that these screens already ship.

## Product Frame

DreamCleanr is `AI workflow hygiene for macOS`.

The interface should feel:

- calm
- technical
- premium without looking like a generic optimizer
- conservative about destructive actions

## Visual Direction

- Dark-first
- Dense but readable
- High contrast with warm gold and cool teal accents
- Typography that feels Mac-native and developer-friendly

Recommended stack:

- Primary UI type: `SF Pro Display` or `Avenir Next`
- Monospace: `SF Mono`

## Core Tokens

These map to the current site language and can seed a Figma variable set later.

| Token | Value | Use |
|---|---|---|
| `bg/base` | `#08101D` | app chrome |
| `bg/soft` | `#101C32` | panels and grouped surfaces |
| `text/primary` | `#F9F6EF` | main copy |
| `text/muted` | `#B6C4D2` | supporting copy |
| `accent/teal` | `#75E0C0` | primary action |
| `accent/gold` | `#F7C46B` | labels and risk-aware highlights |
| `line/default` | `rgba(255,255,255,0.12)` | borders |

## File Structure

Recommended Figma file pages:

1. `00 Cover`
2. `01 Foundations`
3. `02 Components`
4. `03 Onboarding`
5. `04 App Dashboard`
6. `05 Scan Flow`
7. `06 Paywall`
8. `07 Settings`
9. `08 Website Landing`
10. `09 Marketing Assets`
11. `10 Prototype`

## Figma Pages

Create these pages:

1. `Onboarding`
2. `Dashboard`
3. `Scan`
4. `Paywall`
5. `Settings`
6. `Analytics`

## Frame Structure

### Core frame sizes

- desktop app main: `1440 x 960`
- modal: `560 x 640`
- website desktop: `1440 x 4200`
- website tablet: `834 x 3200`
- website mobile: `390 x 2800`

### Page 1: Onboarding

Frames:

- `Onboarding / Hook`
- `Onboarding / Live Scan`
- `Onboarding / Results`
- `Onboarding / First Win`
- `Onboarding / Upgrade`

Key modules:

- headline block
- sample/live scan meter
- reclaimable breakdown cards
- protected-state callout
- install CTA
- Pro early-access prompt

### Page 2: Dashboard

Frames:

- `Dashboard / Overview`
- `Dashboard / Dense`
- `Dashboard / Empty State`

Key modules:

- reclaimable space hero metric
- action bar: `Preview Cleanup`, `Run Cleanup`, `Schedule`, `View Receipt`
- category cards by artifact family
- health narrative, not a vague magic score
- latest receipt summary

### Page 3: Scan

Frames:

- `Scan / Running`
- `Scan / Results`
- `Scan / Review Required`

Key modules:

- progress indicator
- category event feed
- surfaced storage total
- reclaimable total
- protected items rail

### Page 4: Paywall

Frames:

- `Paywall / Soft`
- `Paywall / Comparison`

Key modules:

- value recap
- Pro shell benefits
- free vs Pro comparison
- early-access or purchase CTA depending on product stage

### Page 5: Settings

Frames:

- `Settings / General`
- `Settings / Safety`
- `Settings / Scheduling`

Key modules:

- schedule toggle
- preset selection
- protected folder review
- report retention
- safety explanation blocks

### Page 6: Analytics

Frames:

- `Analytics / Weekly`
- `Analytics / Trends`

Key modules:

- reclaimed space over time
- repeated growth categories
- cleanup streaks
- protected-state patterns

## Component Inventory

- top app bar
- sidebar or split navigation
- metric hero
- artifact category card
- protected-state badge
- action pill button
- receipt summary card
- trend strip
- review-required list row
- code/config snippet card for MCP setup

## Export-Ready Marketing Assets

Prepare reusable frames for:

- X post image `1600 x 900`
- Product Hunt gallery `1270 x 760`
- Open Graph `1200 x 630`
- app screenshot `1440 x 900`
- comparison chart `1600 x 1200`

## UX Rules

- show value before asking for money
- show what is protected as clearly as what is reclaimable
- keep core actions within one or two clicks
- make `preview` feel as important as `clean`
- never let the UI imply future detector support is live

## Data Display Rules

- `GB reclaimed` can be live only when backed by a real scan
- `health score` is optional and should be narrative-first, not gimmick-first
- future concept frames may use sample numbers only when clearly marked as conceptual

## Handoff Notes

- The future macOS shell is the first paid moat
- The iPhone/iPad companion comes later and should reuse the same receipt/history vocabulary
- Pair this brief with:
  - [ONBOARDING_CONVERSION_SPEC.md](ONBOARDING_CONVERSION_SPEC.md)
  - [MACOS_SHELL_PLAN.md](MACOS_SHELL_PLAN.md)
