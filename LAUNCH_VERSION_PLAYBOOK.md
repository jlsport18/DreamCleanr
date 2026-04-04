# DreamCleanr Launch Version Playbook

This playbook ties release prep, launch copy, deploy verification, and post-launch handling into one operator flow.

## Current Target

Planned operator-system release:

- `v0.3.3`

Use the next patch version instead if the package version has already advanced by the time release prep begins.

## Release Scope

This release packages:

- master-prompt strategy workflow
- new DreamCleanr operator skills
- release, launch, and debug playbooks
- future-commercial incubation docs
- expanded launch and copy-test content

This release does not package:

- runtime backend work
- live Stripe or auth
- subscription-first pricing
- new detector support that is not already implemented

## Release Prep

Before tagging:

- bump version in `dreamcleanr/__init__.py`
- bump version in `pyproject.toml`
- update `CHANGELOG.md`
- confirm README, pricing, and launch docs match shipped truth

## Launch Content Pack

Finalize before release notes are published:

- GitHub release summary
- Product Hunt tagline and first comment
- founder launch thread
- short launch tweets
- Reddit post angle

All launch content must stay grounded in current shipped surfaces.

## Deployment Gates

After merge to `main`:

- `Pages` green
- `Pages Verify` green

After pushing `v0.3.3`:

- `Release` green
- `Install Smoke` green
- `Operations Health` green

## Post-Launch Checklist

- homepage returns `200`
- pricing page returns `200`
- `releases/latest` returns `200`
- wheel asset resolves
- install and update scripts resolve
- release notes read cleanly for public users

## Hotfix Loop

If launch-day feedback surfaces a real issue:

1. log the issue in GitHub
2. decide whether it is:
   - copy-only
   - docs-only
   - release-surface
   - runtime bug
3. fix the smallest safe surface
4. rerun validation
5. cut the next patch if a released artifact is affected
