---
name: dreamcleanr-release-launch-operator
description: Run DreamCleanr's testing, debugging, commit, PR, tag, release, deploy, and launch operations end to end. Use when DreamCleanr needs test/debug sequencing, branch and commit rules, GitHub sync, Pages verification, GitHub Release flow, Product Hunt or founder-launch prep, or post-release verification and hotfix handling.
---

# DreamCleanr Release Launch Operator

## Overview

Own DreamCleanr's release-and-launch operating system so testing, GitHub sync, deploy, release, and launch execution are repeatable and decision-complete.

## Use This Skill

- Read [../../TEST_AND_DEBUG.md](../../TEST_AND_DEBUG.md), [../../GITHUB_SYNC_AND_RELEASE.md](../../GITHUB_SYNC_AND_RELEASE.md), [../../LAUNCH_VERSION_PLAYBOOK.md](../../LAUNCH_VERSION_PLAYBOOK.md), [../../RELEASE_CHECKLIST.md](../../RELEASE_CHECKLIST.md), and [../../FINAL_DEPLOYMENT_REPORT.md](../../FINAL_DEPLOYMENT_REPORT.md) first when they exist.
- Read [references/release-surface-map.md](references/release-surface-map.md) before operating on release or deploy work.
- Keep release execution aligned with the current DreamCleanr deployment model:
  - `main` drives Pages
  - `v*` tags drive GitHub Releases

## Core Workflow

1. Validate locally before touching GitHub release surfaces.
2. Keep branch, commit, and merge behavior explicit.
3. Verify Pages, Release, Install Smoke, and Operations Health after each release cut.
4. Use grounded launch copy that matches the shipped product and pricing model.

## Release Rules

- Do not cut a tag until local checks pass.
- Do not merge if public copy overclaims current capability.
- Do not publish launch content that implies live subscriptions, fake checkout, or live unshipped detector support.
- Keep launch-day comms, release notes, and GitHub release text aligned.

## Good Deliverables

- test/debug playbooks
- branch and PR rules
- release cut checklists
- deploy and post-release verification steps
- launch-day copy and hotfix triage flows

## Avoid

- skipping verification because CI will catch it later
- mixing public launch promises with future-only commercial architecture
- release flows that depend on undocumented local knowledge
