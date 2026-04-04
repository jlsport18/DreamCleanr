# Security Policy

Last updated: `2026-04-04`

## Supported Versions

DreamCleanr is GitHub-first and release-driven.

Security and safety fixes are prioritized for:

- the latest tagged release
- the current `main` branch when it is ahead of the latest release

Older releases may not receive fixes if a newer safe release path is available.

## Reporting A Vulnerability

Do **not** open a public issue for:

- credential leaks
- unsafe deletion paths
- protected-state bypasses
- destructive cleanup bugs
- update-chain or release-chain tampering concerns

Instead:

- use GitHub Security Advisories if available
- or contact the maintainer privately if a private contact path is available

Include:

- affected release or commit
- operating system version
- exact reproduction steps
- whether the issue is preview-only, apply-mode, installer, updater, MCP, or schedule related

## Security And Safety Principles

DreamCleanr’s core security posture is intentionally conservative:

- preview-first behavior stays the default
- destructive cleanup is narrow and explicit
- protected Claude, Codex, and Docker VM state must never be auto-deleted by default
- update/install paths should be stable, inspectable, and GitHub-release based
- new cleanup targets require regression coverage before release
- local-first operation is preferred over backend dependency

## Supply Chain And Release Integrity

The current supported delivery surfaces are:

- GitHub repository
- GitHub Releases
- GitHub Pages

DreamCleanr does not currently operate a separate update server or always-on control plane.

## Safe Use Guidance

To use DreamCleanr safely:

- start with preview mode
- review cleanup receipts before broadening deletion scope
- keep DreamCleanr updated through the documented release/update path
- avoid modifying protected-state rules unless you fully understand the risk

## Future Native Apps

If DreamCleanr later ships native macOS or iOS applications, platform-specific security controls, entitlement limits, and App Store review requirements will be added to this policy or a supplementary security document.
