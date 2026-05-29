# Mode-Tiering Analysis — should deletions move from standard → aggressive?

**Question (operator):** "Do we need to move some deletions into the more aggressive
version and out of the standard?" + "I like how fast it cleans up my Mac, so I don't
want major deletions removed — re-characterize as more aggressive instead."

**Answer: Yes — re-tier, don't remove.** One deletion (the wholesale `~/Library/Caches`
sweep) had a blast radius far wider than the product's "AI/dev hygiene that doesn't break
workflows" positioning, and it ran in the *default* tier and the *unattended daily job*.
Moving it to `max` keeps the capability, makes the default safe, and costs no speed.

## Before (as shipped in v0.3.6)

| Action | safe | balanced (default) | max | Risk |
| --- | --- | --- | --- | --- |
| Stale process trim | preview | apply | apply | Low |
| Regenerable dev caches (uv, npm, npx, Gradle, trunk) | **delete** | delete | delete | Low (regenerate) |
| Docker prune (stopped/dangling/build cache) | — | apply | apply | Low |
| **Wholesale `~/Library/Caches`** (every non-AI app's cache) | **delete** | **delete** | delete | **High — broad** |
| Claude/Codex support caches (when inactive) | — | — | delete | Medium |

Two problems: (1) the broad `~/Library/Caches` sweep ran in `balanced` **and the daily
launchd job** (`clean --apply --mode balanced`) — every app's cache wiped nightly,
including running non-AI apps; (2) `safe` still deleted caches on `--apply` — "safe" in
name only.

## After (this run)

| Action | safe | balanced (default) | max (aggressive) | Notes |
| --- | --- | --- | --- | --- |
| Stale process trim | preview | apply | apply | unchanged |
| Regenerable dev caches | **preview** | apply | apply | safe no longer deletes |
| Docker prune | preview | apply | apply | now previewable in safe |
| **Wholesale `~/Library/Caches`** | — | — | **apply** | **moved to max** |
| Claude/Codex support caches | — | — | apply | unchanged |

`safe` = "show me exactly what the standard tier would clean, touch nothing."
`balanced` = the fast, low-blast-radius default (dev caches + Docker + stale procs).
`max` = balanced + the broad sweeps you run deliberately.

## Why these placements

- **Regenerable dev caches stay standard.** uv/npm/npx/Gradle/trunk re-download on demand;
  clearing them is the canonical safe win and the bulk of routine reclaim for AI devs. Kept
  in `balanced`. (`core.py` `SAFE_CACHE_PATHS`.)
- **Docker prune stays standard.** It only removes *stopped* containers, *dangling* images,
  and build cache, and only when the daemon is reachable and no primary engine process is
  active (`summarize_family`). Safe and high-yield.
- **`~/Library/Caches` wholesale → max.** `remove_unprotected_library_caches` deletes *every*
  child except the protected AI basenames — i.e. the caches of every other app, some of which
  may be running. That is legitimate aggressive behavior, but it must be a deliberate `max`
  choice, not the default and not the nightly job.
- **App support caches stay max.** Chromium/Electron `Cache`/`GPUCache` dirs for Claude/Codex
  are only swept when the family is inactive — already gated, keep in `max`.

## Speed note (addresses "I like how fast it cleans up")

Re-tiering changes *which tier* runs an action, not *how* it runs — the operations and their
speed are identical. The default reclaims slightly less by design; run `--mode max` for the
full sweep. The actual deletion path is unchanged (immediate `rmtree`/`unlink`), so there is
no new latency.

## The open trade-off (deferred): reversibility vs. immediate space

The brief's #1 moat is a reversible **staging window** (7-day Free / 30-day Pro). The CLI
hard-deletes today. A quarantine-with-restore (`mv` to a staging dir, fast) would make even
`max` recoverable — but quarantining delays *actual* space reclamation until purge, which
conflicts with "I want the GB back now." Recommended resolution (see DEFER QUAR-1): default
hard-delete for `balanced` (space now), optional `--quarantine` + `restore`/`purge`, and
default-on quarantine for `max` only (where blast radius is highest). This is the bridge to
the native app's APFS `clonefile` staging bin.
