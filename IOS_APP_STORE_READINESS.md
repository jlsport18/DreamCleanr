# DreamCleanr iOS App Store Readiness

Last updated: `2026-04-04`

Canonical source: [DREAMCLEANR_MASTER_STRATEGY.md](DREAMCLEANR_MASTER_STRATEGY.md)

Supporting docs:

- [MACOS_SHELL_PLAN.md](MACOS_SHELL_PLAN.md)
- [MONETIZATION_PLAN.md](MONETIZATION_PLAN.md)

## Decision

DreamCleanr should move toward the App Store only as a `premium companion` to the Mac product, not as a generic iPhone system cleaner.

## Why

Apple’s current App Review and platform rules make this boundary important:

- apps must be self-contained and may not read or write data outside their designated container area
- app privacy disclosures must accurately describe real data handling
- app metadata must be accurate and not make unverifiable claims
- digital feature unlocks inside the app are generally expected to use App Store in-app purchase

That means DreamCleanr’s current real moat is not “clean your entire iPhone better than everyone else.”
It is:

- safe AI and developer workflow hygiene on Mac
- receipt-first transparency
- low-maintenance, local-first trust
- a future premium companion experience across Apple devices

## Recommended iOS Product Shape

The first iPhone and iPad app should be `DreamCleanr Companion`.

It should do these things well:

- show the latest DreamCleanr receipts in a polished mobile-native format
- show protected items, manual-review items, and cleanup history clearly
- show the paired Mac’s last-run status and schedule status
- offer optional remote preview or remote run-request flows only after the Mac-side shell and pairing model are mature
- surface privacy, support, and safety guidance in-app

It should **not** launch as:

- a fake “device boost” app
- a system-wide cleaner that claims to delete data from other apps arbitrarily
- a bait-and-switch weekly-subscription photo cleaner with no real DreamCleanr connection

## Market Positioning

The iOS cleaner category is already crowded with photo cleaners and aggressive subscription utilities.

DreamCleanr should not try to win by copying those products.

Its premium angle should be:

- `the calm, trustworthy companion for people who already use DreamCleanr on Mac`
- `fast, clean, light, efficient, slick, premium`
- `less hype, more visibility, more control`

## Launch Gates

Before starting TestFlight or App Store submission, DreamCleanr should have:

1. a polished macOS shell or companion layer that makes Pro value obvious
2. stable shared report/history schemas
3. public privacy, security, terms, and support URLs
4. a clear App Store privacy-label draft based on the exact app design
5. a monetization path that respects App Store payment rules

The build order is fixed:

1. premium macOS shell first
2. shared receipt/history and pairing contract second
3. iPhone/iPad companion after the Mac-side premium value is proven

## Suggested Next Build Sequence

1. Finish compliance and public policy surfaces
2. Build the macOS shell and premium local report browser
3. Stabilize pairing and history contracts
4. Design the iPhone and iPad companion in SwiftUI
5. Run closed TestFlight once the companion is meaningfully differentiated

## Reference Standards

- Apple App Review Guidelines: https://developer.apple.com/app-store/review/guidelines/
- Apple App Privacy Details: https://developer.apple.com/app-store/app-privacy-details/
- Apple Standard EULA: https://www.apple.com/legal/internet-services/itunes/dev/stdeula/
- Apple membership and App Store Small Business references: https://developer.apple.com/support/compare-memberships/
