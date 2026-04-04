# DreamCleanr Compliance Posture

Last updated: `2026-04-04`

## Decision

DreamCleanr should continue as a `local-first, GitHub-first, low-maintenance` product while it hardens its compliance surfaces ahead of any native App Store launch.

## Current Compliance Surfaces

DreamCleanr now maintains:

- `PRIVACY.md`
- `SECURITY.md`
- `TERMS.md`
- public website policy pages for privacy, security, terms, and support
- GitHub-first release, health, governance, and business review automation

## Core Product Posture

DreamCleanr is designed to minimize compliance complexity by default:

- no required DreamCleanr account system
- no always-on backend
- no default hosted telemetry
- no default sale or sharing of user data
- no device-wide destructive cleanup on platforms that do not allow it

## Apple And App Store Readiness

For a future iPhone or iPad launch, DreamCleanr should assume the following:

- App Store builds need a public privacy policy URL and an in-app privacy link
- App privacy disclosures in App Store Connect must match the actual data flows of the shipping build
- if a future app supports account creation, account deletion must also be supported inside the app
- if a future iOS app unlocks digital features inside the app, App Store in-app purchase rules will apply

## Current Gaps Closed In This Phase

This phase closes the main policy gaps that would otherwise slow future distribution:

- public privacy policy URL
- public security policy URL
- public terms-of-use URL
- public support URL
- documented iOS boundary and readiness plan

## Remaining Gaps Before iOS Submission

Before any App Store submission, DreamCleanr still needs:

- a real native iPhone or iPad companion build
- app-specific privacy labels based on that exact build
- support copy and screenshots tailored to the native app
- a clear decision on Apple standard EULA vs custom EULA
- a final monetization choice that respects App Store payment rules

## Working Rule

Do not position DreamCleanr’s future iOS app as a generic device-wide cleaner.

The compliant and differentiated path is a premium companion for DreamCleanr users on Mac: receipts, visibility, guidance, and optional paired control, not unsupported system-wide cleanup claims.
