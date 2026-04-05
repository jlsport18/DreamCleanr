# Release Checklist

Use this checklist before cutting the next DreamCleanr release tag.

## 1. Product And Docs

- confirm README install and update instructions still match the shipped installer and updater
- confirm the public site still reflects the current product boundaries and policy surfaces
- confirm `CHANGELOG.md` includes the release-facing highlights
- confirm privacy, security, terms, and support pages still match the shipped behavior

## 2. Package Metadata

- confirm `dreamcleanr/__init__.py` version matches `pyproject.toml`
- confirm package URLs still point at live public surfaces
- confirm CLI entry points still work

## 3. Local Verification

- run `python3 -m unittest discover -s tests -p 'test_*.py' -v`
- run `python3 -m compileall dreamcleanr tests scripts`
- run `node --check site/app.js`
- run `zsh -n scripts/install_codex_skills.sh scripts/install.sh scripts/update.sh`
- render the sample cleanup report
- validate all DreamCleanr repo-owned skills with `quick_validate.py`
- confirm public-copy truth checks pass

## 4. GitHub Automation

- confirm `CI` is green on the intended head
- confirm `Pages` is green if site-facing content changed
- confirm `Pages Verify` is green after site changes
- confirm `Operations Health` is green on the intended head
- confirm `Install Smoke` is green if install/update surfaces changed
- confirm recurring tracker issues are labeled `tracker` and excluded from actionable queue counts

## 5. Release Cut

- create the version tag from the intended commit
- push the tag and verify `release.yml` publishes the wheel, sdist, sample report, install script, and update script
- verify the latest release page resolves
- confirm release notes and launch copy match current shipped capability

## 6. Post-Release Verification

- verify the public site still returns `200`
- verify `releases/latest` returns `200`
- verify raw `scripts/install.sh` and `scripts/update.sh` return `200`
- verify the latest wheel asset resolves
- verify the release notes read cleanly for public users
- rerun governance and business review workflows so queue counts reflect the just-published release
