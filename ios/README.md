# DreamCleanr iOS Companion

Planned home for the SwiftUI iPhone and iPad companion experience.

The iOS product should:

- render the same DreamCleanr summary and receipt contract used on macOS
- act as a viewer, status, and optional remote-trigger surface only
- avoid any local cleanup logic that belongs in the Python core
- avoid pretending to be a device-wide iPhone cleaner, because that is not the real DreamCleanr moat

Recommended contract order:

- `latest-summary.json` for status cards, last-run state, and trend previews
- `latest.json` for detailed receipts and detector/project visibility
- `latest.html` as a shareable or support-friendly rendering fallback

Reusable companion-facing SwiftUI code now lives in:

- `apple/Sources/DreamCleanrCompanionKit/`
- `apple/Sources/DreamCleanrAppleShared/`

The repo still does not include a full Xcode iOS app project, but the shared contract and companion views are now present for that build lane.

Planned premium value:

- polished receipt browsing
- paired-Mac status and last-run visibility
- privacy and support surfaces that feel native and premium
- optional remote preview triggers once the Mac-side shell and pairing model are ready
