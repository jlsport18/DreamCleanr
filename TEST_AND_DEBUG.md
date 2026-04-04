# DreamCleanr Test And Debug Playbook

This is the current-phase operator playbook for validating, debugging, and fixing DreamCleanr safely.

## Decision

DreamCleanr stays `local-first`, `preview-first`, and `GitHub-first`.

That means:

- validate locally before leaning on CI
- treat public-copy truth as a release gate
- debug the smallest failing surface first
- rerun the full matrix before merge or tag

## Local Test Order

Run checks in this order:

1. `python3 -m unittest discover -s tests -p 'test_*.py' -v`
2. `python3 -m compileall dreamcleanr tests scripts`
3. `node --check site/app.js`
4. `zsh -n scripts/install_codex_skills.sh scripts/install.sh scripts/update.sh`
5. render the sample cleanup report
6. validate DreamCleanr skills with `quick_validate.py`

## Public-Truth Checks

Before merge or release, search public surfaces for drift:

- no live `$19/month Pro`
- no `cancel anytime`
- no fake checkout
- no fake testimonials
- no live backend, auth, or analytics claims
- no live Python, Node, Ollama, Hugging Face, or LM Studio support claims

Check:

- `site/`
- `README.md`
- launch docs
- pricing docs
- release notes

## Debug Order

### If unit tests fail

- reproduce the exact failing test locally
- fix the smallest code or fixture issue
- rerun the failing test or test file
- rerun the full unit suite

### If compile or syntax checks fail

- fix syntax or import issues first
- rerun only the failing compile or shell check
- then rerun the full local test order

### If site or public-surface checks fail

- inspect the affected HTML, asset path, or text claim
- verify local links and asset existence
- fix copy drift before chasing visual polish

### If release or deploy checks fail

- inspect the specific workflow surface:
  - `CI`
  - `Pages`
  - `Pages Verify`
  - `Release`
  - `Install Smoke`
  - `Operations Health`
- reproduce the failing step locally when possible
- fix the specific release surface, then rerun local validation

## Stop Conditions

Do not merge or tag if:

- local tests are red
- public copy overclaims current capability
- release or install docs contradict current behavior
- version and changelog are out of sync

## Full Phase-Close Matrix

- local test order above passes
- DreamCleanr skills validate
- site links resolve
- release docs reflect current workflows
- current product truth remains intact
