# DreamCleanr Product-Line Build Plan — macOS + Server Edition

Two products, one honest engine philosophy. Drafted 2026-05-26.

## Shared engine principles (non-negotiable, carried from the macOS work)

1. **Recon before act.** Always scan/map first; never act without a reviewed plan.
2. **Named, actionable accounting.** Every reclaim figure is a *source + a verb* — never an
   unattributed "X GB wasted." (Trust is the brand; HN will hammer aggregates.)
3. **Scoped & guarded.** Never touch what's out of scope. macOS = protected-state +
   active-project guard. Server = operator-assigned **zones** (see below).
4. **Reversible by default.** Prefer stop/quarantine/Trash over destroy. Hard-delete only
   the regenerable; never the expensive-to-refetch (models, other tenants' data).
5. **Honest about memory.** Inactive/cached RAM is kernel-managed, not "wasted." Zombies
   hold ~no memory (process-table hygiene, *not* a RAM win — don't market it as one).
   `purge` is a manual suggestion, never auto-run.
6. **Lightweight & fast.** Stdlib-first, no phone-home deps, parallel sizing, skip-clean
   when a tool/binary is absent.

---

## Product 1 — DreamCleanr (macOS) — enhance the current CLI

Status: shipped this session — re-tiering, Trash net, smart caches, **memory-first
measurement + reclaim ceiling**. Remaining roadmap:

- **MEM-ACT (next):** execute the memory verbs the ceiling already surfaces —
  `ollama stop <model>` (reversible, highest-wow), stop idle running containers
  (`docker stats --no-stream`; confirm-gated, reversible via `docker start`). Never auto-`purge`.
- **Process hygiene (honest):** detect zombies (state `Z`) and report the *parent* to
  signal/restart — framed as hygiene, not memory reclaim. Surface idle high-RAM apps
  (rss + low CPU) for review.
- **Advanced file cleanup (the dev wedge — huge, regenerable):** Xcode `DerivedData`,
  old simulators & device-support, dead-project `node_modules`/`.venv`/`target`/`build`,
  `__pycache__`, broken symlinks, orphaned app-support of uninstalled apps, old crash
  reports & rotated logs, stale installer `.dmg`s. All guarded by active-project signals;
  all via the Trash net.
- **Then:** SwiftUI menu-bar shell over the CLI (live RAM-pressure widget = the Memory
  Guardian Pro surface); MODEL-2 per-tool model pruning (HF revisions / Ollama orphans).

---

## DreamCleanr Server Edition — a NEW adjacent project (`dreamcleanr-server`)

> Products 2 & 3 below are **one new project, separate from the macOS CLI repo** — its own
> repo `dreamcleanr-server` (own releases, own README, own chatbot). It **shares the engine
> philosophy** and the `snapshot → plan → confirm → apply → receipt` architecture; a shared
> core can be extracted into a small library once both stabilize. v1 (getupsoft) and the
> commercial SSH edition are sequential **phases of this one adjacent project**, not separate
> codebases.

## Product 2 — Server Edition v1 (Developer Server) — **GetUpSoft Ubuntu-first**

Target v1: the operator's **Ubuntu server on GetUpSoft** (multi-tenant — the operator's
projects *and* other people's run here). The defining requirement, in the operator's words:
*"assign areas not to touch… focus on where my projects are hosted, leave the other guys'
projects alone — a recon then selection capability, to focus in on a zone."*

### The core flow: Recon → Select → Scoped Reclaim

**Phase A — RECON (read-only topology map).** Discover, attribute, never touch:
- processes (RSS/CPU/owner), `systemd` services, listening ports;
- Docker/Podman: containers (running/idle/stopped), images (dangling/unused), volumes,
  networks, **compose project labels** (`com.docker.compose.project`) and owners;
- disk by path & owner (`du` parallelized), RAM by process/cgroup, swap pressure;
- "who owns what": map paths/containers/services → tenant (by user, dir prefix, compose
  project, or label). Output a **topology report** the operator reviews.
- **Unattributed is a top-line recon section.** Raw `docker run` containers (no compose
  label), `root`-owned processes, files under shared dirs — surface these prominently so the
  operator resolves attribution *before* zoning. Unknown = untouchable (denylist-first), but
  it must be loud, not silently skipped.

**Phase B — ZONE SELECTION (the safety core).** Operator assigns scope explicitly:
- **Include zones** (e.g. `/srv/jlfg/**`, compose projects `leadgen|mymca|merchantpulse`,
  user `jlfg`) and **exclude zones** (everything else — *other tenants*).
- **Denylist-first invariant:** anything not in an include zone is untouchable. This is the
  server analog of macOS protected-state — the one rule that can never be violated.
- Zones persist in a config (`/etc/dreamcleanr/zones.yaml` or `~/.dreamcleanr/zones.yaml`),
  versioned, with a `recon → propose zones → operator confirms` bootstrap.

**Phase C — SCOPED RECLAIM (within the selected zone only, dry-run default, confirm to apply).**
Every action must be *scope-able per target* — system-wide commands are banned (they hit
other tenants):
- **Containers/compute:** stop idle in-zone containers — *idle ≠ low CPU* on a server (a web
  server is 0% between requests). Detect idle via **no open listener ports + no recent
  request-log activity + operator-tagged `ephemeral: true`** in the zone config. `docker prune`
  only with `--filter label=com.docker.compose.project=<in-zone>` (never bare). Remove
  dangling images/volumes *owned by in-zone projects only*. Reversible (stop≠remove; re-pull).
- **RAM/allocation efficiency:** flag over-provisioned mem/CPU `limits/reservations` in-zone;
  **recommend rightsizing, never auto-apply.**
- **Disk:** in-zone build/CI-runner caches (work dirs + action caches + Docker layer caches —
  **the highest-yield win on getupsoft's self-hosted runners**), in-zone `~/.cache`, rotated
  app logs. **journald only per in-zone unit** (`--vacuum-size --unit=<unit>`), never global.
  **Package caches (apt/pip system) are host-level** — separate explicit confirmation, never
  folded into a zone run (they're shared across tenants).
- **Database storage (surface-only):** Postgres/Supabase WAL bloat, dead tuples, unused
  indexes — **recommend** operator-run `VACUUM`/`REINDEX`; **never auto-VACUUM.** High value
  for the JLFG stack, zero risk while advisory.
- **Process hygiene:** zombie reap (signal parent), stale in-zone helpers.
- **Topology efficiency report:** idle services, duplicate stacks, consolidation candidates,
  "reclaimable RAM/compute/disk in <zone>" — the same named-source ceiling, server-scale.

### Architecture (v1, lightweight)
- Python, stdlib-first; runs **on** getupsoft (over Tailscale/SSH). One-shot CLI first
  (`dreamcleanr-server recon` / `select` / `clean --zone <z>`), reusing the macOS engine's
  classification/ceiling/reversibility patterns. Docker via CLI/socket; systemd via `systemctl`.
- Reuses: snapshot→plan→confirm→apply→receipt; the named ceiling; quarantine/Trash analog
  (`docker stop` and a staging dir for files); the dry-run-default + confirm gate.
- Later: agent/daemon + scheduled "guardian"; multi-host fleet dashboard.

### Safety invariants (server)
- **Zone isolation is a code-level kill switch, not prose.** Every `apply` path takes a zone
  object and asserts `target ∈ zone.include AND target ∉ zone.exclude` before *any* subprocess.
  A CI test — *"given zones X/Y, no action targets outside X"* — gates every release.
- **Linux has no Trash → reversibility = snapshots.** Before any destructive action, verify a
  recent filesystem/backup snapshot exists (ZFS/Btrfs/Restic/Borg); refuse or loudly warn if
  not. That's the honest server reversibility story.
- Dry-run default; explicit `--apply` + confirm; reversible-first (stop≠remove).
- Never stop a serving container/service (idle = no listener + no recent requests + operator
  `ephemeral` tag + confirm + operator sees the named list first).
- Never touch other tenants' data, ever — the catastrophic regression to design out.

### Monetization (Server Edition is the recurring-revenue play)
- Servers accrue cruft *continuously* → genuine recurring value (unlike one-time desktop cleanup).
- Tiers: per-server one-time (parity w/ desktop Pro) → **per-node Guardian subscription**
  (scheduled scoped reclaim + RAM/disk-pressure alerts) → **fleet dashboard** (multi-host
  topology + reclaim across a cluster) → Enterprise (policy, RBAC, audit).
- Wow/viral asset: *"DreamCleanr Server reclaimed 38 GB RAM and 210 GB disk in zone `jlfg`
  — and didn't touch the other 6 tenants."* Named sources + zone-safety = the trust+wow combo.

---

---

## Product 3 — DreamCleanr Server (Commercial) — server-agnostic, multi-host, **over SSH**

After the getupsoft v1 proves the engine, productize it to run across *any* self-hosted
server — **agentless, over SSH** (Ansible-style: connect, run the recon/reclaim engine
remotely, collect the receipt; nothing to install on the target → "lightweight, download
only if needed" carries over).

- **Architecture:** an inventory of hosts (SSH targets, jump hosts, Tailscale ok); push the
  stdlib engine over SSH (or run via a transient venv), execute recon/plan/apply remotely,
  stream named-source receipts back. Per-host zones; fleet view aggregates.
- **Trust model changes sharply once it's a product** (v1 getupsoft = single trusted operator;
  commercial = many operators/servers): the **zone config becomes an attack surface** (a
  malicious/erroneous config could target the wrong paths). Required from day one of the
  commercial tier: **signed zone configs, RBAC, full audit log of every action, least-priv SSH
  (dedicated key, no root unless a step needs it + justified), and a hard dry-run-first gate.**
- **Reuse:** the same engine, ceiling, denylist-first kill switch, snapshot-reversibility check
  — now executed remotely per host.
- **Monetization:** per-node Guardian subscription + fleet dashboard (this is the recurring,
  scalable revenue — cruft accrues on every server continuously).

## Go-to-Market — riding the self-hosted resurgence (sysadmin-grade)

The self-hosted comeback is a **trust** resurgence (control over cost / data / deplatforming),
not a cleaner resurgence. So lead with **safety, not cleanup**: every infra tool says "we make
it easy" — DreamCleanr Server says **"we make it safe to clean what's already yours."** Different
category. Vocabulary: *survey, attribute, scope, reclaim, attest* — not clean/free/boost (that's
CleanMyMac's lexicon). Position as a **hygiene companion for your self-hosted stack.**

**The receipt is the marketing.** Dogfood it: a post — *"What I reclaimed on my own getupsoft
box, and what I refused to touch"* — with the real receipt (named sources, the unattributed
section, the zones config, the snapshot check) beats any landing copy. r/selfhosted reads
receipts, not slogans.

**Moves, in payoff order:**
1. **Recon-only free tier, forever.** Read-only `recon` = zero-risk wedge; every recon is a
   qualified install; self-discovery of unattributed cruft is the hook to paid scoped reclaim.
2. **The differentiated receipt line:** *"Reclaimed X GB in zone `jlfg`. Other tenants (6):
   untouched. Snapshot verified before apply."* `apt autoremove` / CleanMyMac cannot say this.
3. **Channels in order:** r/selfhosted → lobste.rs → Hacker News — dogfood receipt + zones config
   + source link; no corporate marketing.
4. **Distribute through the toolchain they already run:** Coolify (highest momentum now),
   Yunohost, Cosmos, Dokploy — a post-deploy hook running recon weekly + posting the receipt to
   Discord/Matrix beats ten landing pages.
5. **`docker-compose.dreamcleanr.yml` one-liner:** paste, set `ZONE_INCLUDE`, `up`, get a receipt.
6. **Weekly "Server Hygiene Report" email** (first free): the recurring lever — debt visibly
   accrues week-over-week; subscribers pay to stop watching it grow.

**Refuse (on brand):** no GB leaderboards/gamification; no telemetry by default (zero-network
carries from macOS); no auto-update on apply (pin versions, operator upgrades); no "we'll fix it
for you" (recommendations only on rightsizing/indexes/journald — the operator is the operator).

**Pricing nuance (self-hosted ICP):** they pay one-time for *a CLI they run*, monthly for *a
service that runs on their behalf.* So the **recurring product is the managed/scheduled Guardian +
weekly receipt** — never the CLI itself (they'll mirror a CLI from GitHub).

**Threat model to spell out** (sysadmins read these, not marketing): *"compromised SSH key signs a
malicious zone config"* → defended by signed configs + per-host audit log + dry-run-first +
snapshot-verification gate + the denylist-first scope assertion. Even a bad config can't act
without the operator confirming a named, scope-asserted plan.

**Receipt format = share mechanic (build day one):** top-line **"Untouched zones (N)"** and
**"Snapshot verified: yes/no"**, plus a `--report-format markdown` flag so the receipt pastes
straight into a Reddit comment or GitHub issue.

**Positioning lines (each backed by an engine behavior):**
- "Recon-first. Zone-scoped. Reversible. The cleaner that refuses to touch what isn't yours."
- "Self-hosted is freedom. DreamCleanr Server is the hygiene that keeps it that way."
- "Your `docker system prune` doesn't know which compose project is yours. We do."
- "It checks for a snapshot before it runs the destructive step. Because you would."

## Sequencing
1. Land the open macOS PR (#30).
2. **MEM-ACT** (macOS memory verbs — `ollama stop`, idle-container stop).
3. **Server Edition RECON (read-only) on getupsoft — start right after MEM-ACT.** Recon is the
   longest-lead-time learning (topology map + attribution edge cases inform everything). Build
   macOS advanced file cleanup (DerivedData/dead-deps) **in parallel** — they don't conflict.
4. Server Edition v1: zone-select → scoped reclaim MVP (getupsoft, trusted single-operator).
5. **Product 3 — commercial server-agnostic over SSH** (adds signing/RBAC/audit/fleet).
6. Guardian (scheduled) across editions; menu-bar GUI; MODEL-2.

## Honesty hazards to design out (so marketing never overpromises)
- Zombies are hygiene, not a RAM win. · Inactive RAM isn't reclaimable. · Rightsizing is a
  recommendation, not an auto-edit. · Server reclaim must be zone-locked — "we cleaned the
  server" without "only your zone" is the trust-killer. · Every claim maps to an engine
  function (keep the claim↔engine table per product).
