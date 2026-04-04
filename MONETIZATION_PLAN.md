# DreamCleanr Monetization Plan

## Decision

DreamCleanr monetizes as a `trust-first, GitHub-first, low-maintenance` product.

That means:

- keep the current core free and easy to install from GitHub
- monetize convenience and packaging later, not the safety-first cleanup engine
- avoid backend billing infrastructure in this phase
- use GitHub-native signals before making stronger pricing moves

## Product Packaging

| Package | Default price | Contents | Launch gate |
|---|---:|---|---|
| Community | Free | CLI, local MCP, scheduled cleanup, JSON and HTML receipts, GitHub install/update path | Shipped now |
| Pro | `$29` intro / `$49` standard one-time | macOS shell, guided setup, richer receipt browsing, integration helpers, eventual iPhone/iPad companion access | Only after a real convenience layer ships |
| Team Pilot | `$199/year` up to 5 Macs | policy presets, rollout guidance, admin-friendly exports, bounded support | Only after Pro is stable and governance stays healthy for a full monthly cycle |

## What Stays Free

The following remain in the free core:

- safe local cleanup engine
- preview-first workflow
- report generation
- local MCP access
- scheduled cleanup
- install, update, safety, and support docs

Charging for the core too early would weaken trust before DreamCleanr has enough market proof.

## Monetization Gates

### Gate 1: keep core free until distribution is proven

Do not launch paid packaging until all of the following are true:

- release-based install and update paths are stable
- `install-smoke.yml` and `ops-health.yml` are green across multiple release cycles
- the public site and release docs stay low-friction
- issue volume shows recurring workflow value, not only curiosity
- there is visible demand for convenience rather than basic cleanup logic

### Gate 2: launch Pro only when convenience is real

Do not charge for Pro until at least one of these exists:

- native macOS shell
- guided install and integration wizard
- materially smoother setup and update flow than the GitHub-only experience
- richer local report history and browsing experience

### Gate 3: launch Team only when repeated organizational demand appears

Do not introduce Team until there is evidence such as:

- repeated requests for multi-Mac rollout guidance
- demand for safer standardized cleanup policies
- requests for admin-friendly exports or rollout summaries

## Revenue Model

### Phase 1: free GitHub-first distribution

Primary goals:

- trust
- install growth
- workflow fit

Monetization during this phase:

- keep Community free
- optionally enable GitHub Sponsors or lightweight donations
- no hard paywall

### Phase 2: one-time Pro product

Primary goal:

- monetize convenience without changing the architecture

Preferred delivery:

- paid macOS shell or companion installer
- optional iPhone/iPad companion only after the Mac-side premium value is already clear
- merchant-of-record checkout instead of custom billing
- downloadable local software, not a hosted dashboard

If DreamCleanr later unlocks digital features directly inside an iPhone or iPad app, that build should use App Store-compliant in-app purchase instead of a separate licensing workaround.

For App Store planning, DreamCleanr should assume Apple Developer Program enrollment and App Store economics are part of the launch cost model. The current Apple Developer Program is `99 USD` per membership year, and Apple’s App Store Small Business Program currently advertises a reduced `15%` commission on paid apps and in-app purchases for eligible developers.

### Phase 3: selective Team offering

Primary goal:

- sell rollout and policy value to small teams without building enterprise infrastructure

Preferred delivery:

- policy bundles
- deployment guidance
- exportable reports
- bounded priority support

## Go-To-Market Sequence

1. SEO and GitHub discovery first
2. developer and AI workflow communities second
3. package-manager discoverability third
4. native shell monetization after convenience demand is validated

## GitHub-Native Business Intelligence

DreamCleanr should use GitHub-native signals first:

- release asset download counts
- issue volume and install-friction issues
- recurring support themes
- governance and business review artifacts

Do not add hosted analytics, accounts, or billing infrastructure in this phase.

## Low-Maintenance Business Rules

- no user accounts
- no cloud sync requirement
- no seat metering
- no license server
- no always-on backend
- no paid feature that depends on live ops to keep working

Good paid lanes:

- downloadable local software
- setup convenience
- policy packs
- bounded priority support

Bad paid lanes for now:

- usage-based pricing
- forced subscriptions for the core CLI
- cloud dashboards
- managed cleanup execution
- enterprise-heavy procurement workflows

## Near-Term Actions

1. Keep Community free while the GitHub-first install/update channel hardens.
2. Finish install-smoke, governance, and business review automation before any billing work.
3. Research Homebrew and PyPI as acquisition channels, not as monetization prerequisites.
4. Revisit Pro pricing only after the macOS shell or another real convenience layer ships.
