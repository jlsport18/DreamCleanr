# DreamCleanr Figma-Ready UI Brief

This is the implementation-ready UI brief for future design work. It is not a claim that these screens already ship.

## Product Frame

DreamCleanr is `AI workflow hygiene for macOS`.

The interface should feel:

- calm
- technical
- premium without looking like a generic optimizer
- conservative about destructive actions
- Mac-native first, not SaaS-dashboard first

## Visual Direction

- Dark-first
- Dense but readable
- High contrast with warm gold and cool teal accents
- Typography that feels Mac-native and developer-friendly

Recommended stack:

- Primary UI type: `SF Pro Display` or `Avenir Next`
- Monospace: `SF Mono`

If a marketing-only export needs broader web parity, `Inter` can be used in that export layer only. It should not replace the native-shell baseline.

## Foundations

### Core tokens

| Token | Value | Use |
|---|---|---|
| `bg/base` | `#08101D` | app chrome |
| `bg/soft` | `#101C32` | panels and grouped surfaces |
| `bg/elevated` | `#172742` | emphasized cards and modals |
| `text/primary` | `#F9F6EF` | main copy |
| `text/secondary` | `#D7E0E8` | subheads and support copy |
| `text/muted` | `#B6C4D2` | supporting copy |
| `accent/teal` | `#75E0C0` | primary action |
| `accent/gold` | `#F7C46B` | labels and premium highlights |
| `accent/amber` | `#FFB463` | warning or storage pressure states |
| `accent/red` | `#FF7B72` | destructive or blocked states |
| `line/default` | `rgba(255,255,255,0.12)` | borders |

### Typography

- H1: `48 / 56 / 700`
- H2: `32 / 40 / 700`
- H3: `24 / 32 / 600`
- Body LG: `18 / 28 / 400`
- Body MD: `16 / 24 / 400`
- Body SM: `14 / 20 / 400`
- Label: `12 / 16 / 600`
- Metric Mono: `SF Mono 14 / 20 / 600`

### Spacing, radius, and elevation

- spacing scale: `4, 8, 12, 16, 24, 32, 40, 48, 64`
- card radius: `16`
- modal radius: `20`
- pill radius: `999`
- elevation 1: `0 8 24 rgba(0,0,0,0.24)`
- elevation 2: `0 16 40 rgba(0,0,0,0.32)`

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

## Core Frame Sizes

### App frames

- desktop app main: `1440 x 960`
- sidebar app state: `1440 x 960`
- modal: `560 x 640`

### Website frames

- website desktop: `1440 x 4200`
- website tablet: `834 x 3200`
- website mobile: `390 x 2800`

## App Layout Spec

### Sidebar

- width: `240`
- items:
  - Dashboard
  - Scan
  - Auto Optimize
  - History
  - Settings
  - Upgrade

### Top bar

- height: `72`
- elements:
  - product logo
  - device health narrative or summary
  - account menu slot for future-only commercial concept work

### Dashboard sections

1. hero metric
2. recoverable storage categories
3. smart recommendations
4. weekly trend
5. upgrade teaser

## Component Inventory

### Buttons

Variants:

- Primary
- Secondary
- Ghost
- Danger

States:

- Default
- Hover
- Pressed
- Disabled
- Loading

### Cards

Variants:

- metric card
- category card
- recommendation card
- pricing or comparison card

### Inputs

- email input
- search field
- protected folder picker
- dropdown
- toggle
- slider

### Data visualization

- recoverable GB metric tile
- storage category bar
- weekly savings chart
- system health ring or narrative equivalent

### Paywall elements

- locked feature row
- comparison table
- savings callout badge
- annual pricing toggle as future commercial concept only

## Required Screens

### Onboarding 1

Headline:

**Your Mac wasn't built for AI workflows.**

Sub:

DreamCleanr surfaces Docker sprawl, cache noise, stale helper residue, and protected AI state without pretending everything is safe to delete.

CTA:

- `Start Smart Scan`
- `See sample scan`

### Onboarding 2

- live scan state with animated categories and counter
- protected-state callout visible early

### Onboarding 3

Results reveal:

- recoverable total
- category list
- protected-state rail
- free-action CTA
- premium shell preview panel

### Dashboard

- large recoverable storage number
- `Preview Cleanup` and `Run Cleanup` actions
- breakdown list
- health narrative
- recommendations

### Scan detail

- tabs for Docker, cache/logs, stale helpers, protected state, and future detector families
- safe, risky, and review labels
- preview and clean action where the current product actually supports it

### Paywall

- headline
- value stack
- free versus Pro comparison
- CTA ladder
- FAQ accordion

Any monthly/yearly toggle, seat comparison, or hosted-team element must be labeled `future commercial concept only`.

### Settings

- schedule toggle
- preset selection
- protected folder review
- report retention
- safety explanation blocks

### Analytics

- reclaimed space over time
- repeated growth categories
- cleanup streaks
- protected-state patterns

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
- commercial concepts like annual pricing, seat-based dashboards, or hosted accounts must be explicitly marked as future-only

## Handoff Notes

- The future macOS shell is the first paid moat
- The iPhone/iPad companion comes later and should reuse the same receipt/history vocabulary
- Pair this brief with:
  - [ONBOARDING_CONVERSION_SPEC.md](ONBOARDING_CONVERSION_SPEC.md)
  - [MACOS_SHELL_PLAN.md](MACOS_SHELL_PLAN.md)
