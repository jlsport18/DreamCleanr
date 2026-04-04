# DreamCleanr Privacy Policy

Last updated: `2026-04-04`

DreamCleanr is built to be `local-first` and `preview-first`.
The product is designed to inspect cleanup candidates on your device, generate receipts on your device, and avoid shipping user state to a hosted backend by default.

This policy applies to:

- the DreamCleanr macOS CLI
- the local DreamCleanr MCP server
- the DreamCleanr public website
- future DreamCleanr companion apps to the extent they link back to this policy until a platform-specific policy replaces or supplements it

## What DreamCleanr Collects

DreamCleanr does **not** operate a mandatory hosted account system today.

The software may access or inspect the following categories of local data on your machine in order to perform cleanup planning and reporting:

- local process lists and process metadata
- selected cache, log, and storage paths on your device
- optional local schedule state written through `launchd`
- optional Docker CLI metadata when Docker is installed
- local DreamCleanr receipt files generated on your machine

DreamCleanr is intentionally conservative around protected AI and developer state.

## What DreamCleanr Does Not Upload By Default

By default, DreamCleanr does **not** upload the following to a DreamCleanr-hosted service:

- process inventories
- cleanup reports
- device identifiers
- local session history from `~/.codex` or `~/.claude`
- authentication tokens, API keys, or secrets from developer tools
- protected application-support directories that DreamCleanr is designed to avoid deleting

DreamCleanr also does not include first-party telemetry or third-party analytics SDKs in the current GitHub-first product.

## Limited Network Requests

Current DreamCleanr builds may make limited outbound requests when you explicitly use features that depend on public distribution surfaces, such as:

- checking GitHub Releases for the latest installable version
- downloading DreamCleanr release artifacts
- loading the public DreamCleanr site or raw install/update scripts from GitHub-hosted surfaces

Those requests are handled by the relevant third-party platform, such as GitHub or Apple, under that platform’s own privacy terms.

## Public Website

The public DreamCleanr site is informational and provides download, policy, and support guidance.

DreamCleanr’s current public site is intended to be static and low-data:

- no required login
- no mandatory analytics
- no hidden telemetry layer

If analytics, crash reporting, or support tooling are added in the future, this policy will be updated before that change becomes the default user experience.

## Data Use

When DreamCleanr processes local data, it does so for narrow product purposes:

- identifying stale helpers, safe cleanup candidates, and protected state
- generating preview plans and cleanup receipts
- installing or removing the local cleanup schedule when you ask it to
- validating or updating the DreamCleanr installation through GitHub release surfaces

DreamCleanr is not designed to sell user data or build advertising profiles.

## Retention And Deletion

DreamCleanr writes local reports to:

- `~/Library/Logs/DreamCleanr/reports`

Those reports are retained locally according to the product’s configured history rules. You can remove them by deleting the report directory or uninstalling DreamCleanr’s local schedule.

DreamCleanr does not currently retain user accounts or user profiles on a DreamCleanr-operated backend because there is no such backend in the current product phase.

## Your Choices

You can control DreamCleanr’s local footprint by:

- running preview-only cleanups instead of apply mode
- uninstalling the local schedule with `dreamcleanr schedule uninstall`
- deleting local receipt files from the DreamCleanr reports directory
- removing local MCP integration files from Claude, Codex, or VS Code
- uninstalling DreamCleanr from your machine

## Protected State

DreamCleanr intentionally avoids auto-deleting high-risk or identity-bearing state such as:

- `~/.codex`
- `~/.claude`
- the Claude VM bundle
- Docker raw VM storage
- active Codex and Claude support roots when those families are live

## Third Parties

The current DreamCleanr product depends on infrastructure or distribution surfaces operated by third parties such as:

- GitHub, for repository hosting, releases, downloads, and the public site
- Apple, if and when DreamCleanr later ships through Apple platform distribution or App Store surfaces

If a future DreamCleanr platform build adds third-party analytics, crash reporting, payments, or support vendors, DreamCleanr will disclose those additions before making them part of the default product path.

## Future App Store Builds

If DreamCleanr launches a native iPhone or iPad companion app, DreamCleanr will update this policy and the app’s App Store privacy details to reflect the exact data categories and platform behaviors in that build.

## Contact And Requests

For general questions, use the public DreamCleanr support surface or repository issue tracker.

For sensitive security matters, follow the private reporting guidance in `SECURITY.md`.
