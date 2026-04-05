# DreamCleanr GitHub Sync And Release

This is the operator flow for branch, commit, PR, merge, tag, release, and deploy work in DreamCleanr.

## Branching Rule

Use a short-lived phase branch for non-trivial work.

Default for this operator-pack release:

- `phase/master-prompt-operator-pack`

## Commit Cadence

Create one commit per finished slice.

Recommended commit shapes:

- `skills: add DreamCleanr operator-system roles`
- `docs: add operator playbooks and incubation specs`
- `strategy: integrate master prompt and launch system`
- `release: prepare 0.3.4 engine-and-apple release`

## PR And Merge Rules

1. push the phase branch to `origin`
2. open a PR into `main`
3. wait for `CI`
4. if site-facing content changed, confirm `Pages` and `Pages Verify` after merge
5. merge only after public-truth checks pass

Preferred PR flow:

- use `gh pr create` and `gh pr merge` when authenticated
- if `gh` is unavailable, use the GitHub web UI from the pushed branch

## Main Sync Rule

- `main` is the shipping branch
- GitHub Pages deploys from `main`
- version tags are cut from merged `main`
- recurring governance and business tracker issues stay open and should be labeled `tracker`

Do not tag from a feature branch.

## Release Cut Flow

1. merge the green PR into `main`
2. pull the updated `main` locally
3. confirm version files and `CHANGELOG.md`
4. create annotated tag `vX.Y.Z`
5. push `main`
6. push the tag
7. verify `Release` publishes expected assets

## Release Assets To Verify

- wheel
- sdist
- sample cleanup report
- `scripts/install.sh`
- `scripts/update.sh`

## Deploy And Post-Release Verification

After merge:

- verify `Pages`
- verify `Pages Verify`

After tag:

- verify `Release`
- verify `Install Smoke`
- verify `Operations Health`
- verify `releases/latest`
- rerun governance and business review workflows so tracker-excluded queue counts stay current

## Hotfix Rule

If a release issue is found after launch:

1. reproduce locally
2. cut the smallest safe hotfix branch from `main`
3. rerun the same validation order
4. merge and tag the next patch release
