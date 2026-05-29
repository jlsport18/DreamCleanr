# Strategic Audit — Scope (2026-05-25)

- **REPO_PATH:** `/Users/jonathanlynch/DreamCleanr` (org `jlsport18`, not the prompt's `/Users/jonathanlynch/dev/dreamcleanr` / `jlynch18`, which do not exist).
- **BRIEF (surrogate):** in-repo strategy docs — `DREAMCLEANR_MASTER_STRATEGY.md`, `MARKET_RESEARCH_MEMO.md`, `FEATURE_SPECS.md`, `ROADMAP.md`, `MONETIZATION_PLAN.md`, `MACOS_SHELL_PLAN.md`. No formal `docs/strategy/DreamCleanr_Strategic_Brief.docx` exists.
- **Branch:** `learnings/2026-05-25-strategic-audit` (no push — human reviews and ships).

## Detected stack (reality vs. the master prompt's assumptions)

The master prompt audits a **native Swift/macOS app** (Xcode, App Sandbox, SMAppService, Sparkle 2, StoreKit 2, APFS `clonefile` staging, App Intents, Universal 2). The repo is **not that yet**:

| Component | Reality |
| --- | --- |
| Shipping product | **Python CLI** — `dreamcleanr/` (2,706 LOC), `pip`/wheel, `dreamcleanr` console script, launchd plist. Released as v0.3.6. |
| Native | **887 LOC SwiftUI *prototype*** — `macos/DreamCleanrMenubar` (a frontend *over* the CLI), `apple/` shared+companion SPM packages, `ios/` README-only stub. **No `.xcodeproj`, no `.entitlements`.** |
| Tests | `tests/` (Python `unittest`), 38 tests, run in CI on a self-hosted runner. |

### Consequence for the audit
The 10 native dimensions (APFS staging, SMAppService helper, Sparkle, StoreKit, Universal 2, …) describe an app that is at prototype stage. Auditing the Python CLI against them returns "absent" for almost all — that is **roadmap, not defects**. So this run:

- **Audits the real surface** (the Python CLI engine + the SwiftUI prototype) for genuine defects and improvements.
- **Ships** the Critical/High CLI safety + correctness fixes (see `backlog/SHIP_THIS_RUN.md`).
- **Defers** the native-app dimensions to a sequenced build backlog (`backlog/DEFER.md`), citing the in-repo strategy docs.

The operator steer for this run: *keep all cleaning power; re-characterize aggressive deletions into the `max` tier instead of removing them; keep the default fast.*
