# DreamCleanr Market Research Memo

Last updated: `2026-05-25`

This memo supports [MONETIZATION_PLAN.md](MONETIZATION_PLAN.md) and [MARKET_STRATEGY.md](MARKET_STRATEGY.md).

---

## 2026-05-25 Refresh

This refresh supplements — does not replace — the `2026-04-05` memo that follows
below. The earlier memo only benchmarks consumer Mac cleaners
(CleanMyMac/DaisyDisk/Hazel/OnyX). This refresh adds (a) market sizing, (b) the
**developer-tool** competitors that are DreamCleanr's actual nearest neighbors,
(c) the distribution reality for a tool that needs Full Disk Access, and (d)
three pricing/GTM **deltas** that are flagged as explicit decisions for the
operator rather than silent changes to the canonical strategy.

### Bottom line

The canonical decision — **open-core, free CLI, one-time Pro, later Team,
local-first, no subscription dependency** — is **validated** by current market
data. Keep it. The refresh sharpens *how* to execute it, not *whether*.

### Market sizing (was missing entirely)

- ~47.2M developers worldwide (SlashData, early 2025); ~36.5M professional.
- macOS ≈ 30–33% of developers (Stack Overflow 2024) → **~10–14M macOS devs**.
- 76% of developers use or plan to use AI tools; 62% actively (SO 2024).
- **Local-LLM curve is the wedge:** Ollama ~170K GitHub stars, monthly model
  downloads grew from ~100K (Q1 2023) to ~52M (Q1 2026); a single Ollama model
  cache can exceed 20 GB. Apple Silicon (>80% of Mac devs) and its unified
  memory are *why* local-LLM dev concentrated on Mac — making Mac the correct
  beachhead, not a limitation.
- **SAM:** even 5–10% of ~12M Mac devs running local AI/containers/heavy builds
  = **0.6–1.2M high-pain users**, and that pool is growing with the local-LLM
  curve. A 1–2% one-time-Pro conversion is a real indie-to-small-team business.

### The competitor set the old memo missed (developer tools)

DreamCleanr's nearest neighbors are **not** CleanMyMac — they are free,
single-purpose, often-unsigned dev utilities. This is where the real wedge is:

| Tool | Price | Scope | Why DreamCleanr beats it |
|---|---|---|---|
| `npkill` (9.2K★) | Free OSS | `node_modules` only | DreamCleanr unifies node + Docker + AI caches + agent logs with a safety net |
| DevCleaner for Xcode | Free (MAS) | Xcode DerivedData/sims only | Not AI/container aware; no modes, no MCP |
| `dev-cleaner` | Free OSS | Xcode/Flutter/Gradle/npm | **Closest analog** — but no AI-model-cache focus, no safe/balanced/max, no MCP, unsigned |
| `docker system prune` | Free (built-in) | Docker only, manual | DreamCleanr orchestrates it inside a project-safe, receipted flow |

**The gap:** no tool unifies AI model caches (Ollama/HF/llama.cpp) + container
layers + dependency stores + build outputs + **AI-agent session logs**
(Claude Code/Cursor/Codeium/Codex) with project protection, dry-run default,
modes, and an MCP server. Today a dev hand-assembles the above and gets no
safety net. Most OSS competitors ship **unsigned** binaries that trip
Gatekeeper — a notarized DreamCleanr is a concrete trust edge.

### Distribution reality: Mac App Store is structurally closed

A cleaner needs broad filesystem reach; the App Sandbox **cannot** grant Full
Disk Access, so the Mac App Store is not an option. This **confirms** the
current direct-distribution model (signed Developer ID + notarization, served
via GitHub Releases). Marketing must reassure users about the one-time
Gatekeeper "downloaded from the internet" step. Note this also bounds the
roadmap's iPhone/iPad companion: it can be a *receipts/status viewer*, never the
cleaner itself.

### Sharpened GTM (top 3)

1. **MCP server is the distribution wedge — lead with it.** "Claude Code /
   Cursor can clean your disk" is a demo no competitor has, and it is the
   feature MacPaw structurally will not build. Ship a one-line
   `claude mcp add dreamcleanr`.
2. **Homebrew on day one.** `brew install dreamcleanr` is table stakes for a dev
   CLI and a channel the incumbent cannot use. *(Delta — see below.)*
3. **Show HN with a specific number** ("recovered 80 GB of Ollama caches Mac
   cleaners miss") → Product Hunt 2–4 weeks later → dev newsletters (TLDR,
   Bytes, Console).

### Three deltas flagged for explicit operator decision

These differ from the canonical docs. They are **proposals**, not applied
changes — the canonical strategy stays as-is until the operator chooses.

1. **Homebrew timing.** Canonical lists package managers as a *later* (#4)
   distribution priority. Recommendation: **move Homebrew to day-one.** It is
   free distribution, needs no backend or paid shell, and is how you
   out-distribute CleanMyMac to the dev audience. Low risk, high leverage.
2. **Team seat price.** Canonical = `$199/yr` per 5 Macs (~$40/seat).
   Competitive data suggests **~$99/yr per 5 (~$19/seat)** converts better for
   bottom-up team adoption, with the value framed as TB/quarter reclaimed across
   a fleet **plus SSD-longevity** (repeated multi-GB AI-cache overwrite causes
   real write-amplification/wear — a concrete IT/CFO argument). Decision: hold
   $199 for higher ACV vs. drop to ~$99 for faster land-and-expand.
3. **Optional annual on Pro.** Canonical is one-time-only and explicitly rejects
   subscription. Research suggests offering **$29 one-time (12 mo of updates)
   *or* $19/yr** as a funding mechanism for ongoing detection-rule maintenance
   (Ollama/HF/agent paths churn). ⚠️ This partially conflicts with the
   "one-time first, no subscription" stance and with the
   `test_distribution.py` guard that asserts the comparison page stays
   "one-time" and excludes monthly pricing. If adopted, message it as
   "one-time, or pay-yearly for continuous updates" and update the guard
   deliberately. Recommendation: **defer** until the premium shell ships; the
   one-time lane is the right launch.

### Top risk (unchanged but worth stating)

MacPaw bolts an "AI Dev Caches" module onto CleanMyMac (1–2 quarters out — they
own the engine, signing, brand). Moat = dev-safety depth (project/lockfile
awareness, agent-session protection) + MCP integration, none of which is their
ICP. Defensibility comes from *depth on AI-dev safety + breadth across all dev
bloat + agent integration*, not from generic cleanup claims.

### New sources (2026-05-25)

- SlashData developer population: https://www.slashdata.co/post/global-developer-population-trends-2025-how-many-developers-are-there
- Stack Overflow 2024 AI survey: https://survey.stackoverflow.co/2024/ai/
- Ollama repo (stars/downloads): https://github.com/ollama/ollama
- npkill: https://github.com/voidcosmos/npkill
- xcode-dev-cleaner (DevCleaner): https://github.com/vashpan/xcode-dev-cleaner
- dev-cleaner: https://github.com/jemishavasoya/dev-cleaner
- Docker pruning docs: https://docs.docker.com/engine/manage-resources/pruning/
- Setapp revenue distribution: https://docs.setapp.com/docs/distributing-revenue
- App Sandbox / Full Disk Access constraints: https://www.appcoda.com/mac-app-sandbox/
- macOS developer statistics: https://www.techlila.com/macos-developer-statistics/

---

It is intentionally grounded in official vendor sources and keeps DreamCleanr's current strategy intact:

- `Community` stays free
- `Pro` stays a later one-time premium macOS shell
- `Team` stays later
- no hosted-account or live subscription dependency is introduced in the current shipping product

## Research Question

Where should DreamCleanr sit in the macOS cleanup market if it wants to stay trustworthy for AI and developer workflows while still creating a credible paid lane later?

## Competitor Snapshot

| Product | Packaging signal | What it does well | Strategic takeaway for DreamCleanr |
|---|---|---|---|
| CleanMyMac | official store supports monthly, annual, and one-time purchase options; support docs explicitly describe both subscription and one-time plans | broad consumer polish, general Mac maintenance, strong commercial packaging | DreamCleanr should not try to out-generic CleanMyMac; it should stay narrower and more developer-specific |
| DaisyDisk | one-time purchase, no recurring payments, lifetime license, up to 5 personal Macs | disk visualization, clarity, low-friction one-time utility purchase | validates that a simple one-time utility lane can work when the value is obvious and the scope is focused |
| Hazel | one-time licensing with single-user, family, and upgrade paths; volume licensing available for institutions | powerful file automation and long-tail power-user loyalty | shows that automation depth and rule-based workflows can justify paid utility software without forcing subscriptions |
| OnyX | free download utility with maintenance depth and version-per-macOS support | trust with power users, broad maintenance coverage, no paywall | proves that free utilities set a high trust bar; DreamCleanr must win through safety, workflow specificity, and convenience rather than basic maintenance claims |

## Official Source Notes

### CleanMyMac

- MacPaw's store currently presents monthly, annual, and one-time purchase paths, plus multi-device options and feature-plan tiers.
- MacPaw's purchase-options knowledge base explicitly states that CleanMyMac offers both one-time purchase and subscription, and that subscriptions include future major-version upgrades while one-time licenses are tied to the purchased major version.
- Strategic read: broad packaging flexibility helps CleanMyMac monetize a wide market, but it also pushes the product into a broader commercial-maintenance lane than DreamCleanr needs right now.

### DaisyDisk

- DaisyDisk's official pricing page says the license is a one-time purchase, not a subscription.
- The current pricing page states a `$9.99` lifetime license with no recurring payments, minor updates included, and use on up to 5 personal Macs.
- Strategic read: one-time utility pricing can stay compelling when the job-to-be-done is extremely legible and the trust model is simple.

### Hazel

- Noodlesoft's store currently lists Hazel 6 at `$42`, Hazel 6 Family Pack at `$65`, and Hazel 6 Upgrade at `$20`.
- Noodlesoft's license guidance says a single-user Hazel license allows use on up to two machines, a family pack covers up to five people or machines, and upgrades are only required for new major versions.
- Strategic read: a one-time utility can still create expansion paths through family packs, upgrades, and institution-friendly volume licensing.

### OnyX

- Titanium Software positions OnyX as a multifunction utility for verification, cleaning, maintenance, customization, and database/index rebuilding.
- The official site says OnyX has been developed so Mac users can use it freely and supports a distinct version for each major macOS release.
- Strategic read: the free-maintenance lane is crowded with trusted utilities, so DreamCleanr should avoid competing on "free generic maintenance" alone.

## What This Means For DreamCleanr

### Recommended position

DreamCleanr should live between DaisyDisk and Hazel strategically, not between CleanMyMac and Setapp.

That means:

- keep the current cleanup engine, receipts, MCP, and scheduling free
- monetize convenience and workflow-specific trust later
- keep the paid lane one-time first, not subscription first
- use GitHub, MCP, and AI-developer specificity as differentiators that broader consumer tools do not own

### Recommended package table

| Package | Price direction | What belongs here |
|---|---|---|
| Community | Free | CLI, MCP server, receipts, scheduling, preview-first cleanup, Docker/Claude/Codex safety defaults |
| Pro | `$29` intro / `$49` standard one-time | premium macOS shell, guided cleanup flows, richer history, polished storage views, safer recommendations, native convenience |
| Team | later pilot | exports, policy packs, rollout guidance, small-team coordination value once repeated demand exists |

### What should stay free

- the local CLI
- the local MCP server
- receipts and exportable artifacts
- scheduling
- trust-first cleanup for the currently shipped safe surfaces

### What should become paid later

- the polished macOS shell
- guided environment-aware cleanup workflows
- deeper historical views and insight surfaces
- team-policy and rollout conveniences once the Team lane is justified

## Trust And Support Comparison

### CleanMyMac risk for DreamCleanr

CleanMyMac is broader, more mature, and more polished commercially. Competing head-on would pull DreamCleanr toward generic claims, broader maintenance scope, and a more support-heavy commercial promise.

### DreamCleanr advantage

DreamCleanr can stay:

- more local-first
- more transparent
- more GitHub-native
- more trustworthy for Docker, Claude, Codex, and AI-heavy machines

That is a better fit for a founder-led, low-hosting-cost utility business.

## Recommended Experiments

Keep the experiment set small, low-cost, and GitHub-first.

### Safe experiments to run now

1. Public CTA and message tests on the static site
   - homepage hero angle
   - MCP setup CTA prominence
   - FAQ and comparison-page internal-link placement
2. Pro-interest issue-template demand capture
   - capture workflow, premium-value signal, team context, and price sensitivity
3. Packaging-message tests
   - "free core, paid convenience"
   - "one-time Pro shell later"
   - "Team later only if demand repeats"

### Experiments to avoid for now

- live checkout
- hosted accounts
- subscription pressure on the free engine
- backend-heavy activation funnels

## Risks By Packaging Model

### One-time Pro

Pros:

- matches the utility category better
- easier to trust
- lower support expectations than a recurring SaaS promise
- consistent with DreamCleanr's local-first product reality

Risks:

- revenue comes in spikes instead of smooth MRR
- requires real convenience value at launch
- upgrade cadence must stay credible

### Freemium plus subscription

Pros:

- cleaner MRR story
- easier to model recurring revenue

Risks:

- would overpromise hosted value that DreamCleanr does not ship today
- adds pricing friction before the premium shell exists
- creates pressure to add backend infrastructure for monetization rather than product truth

## Recommendation

Stay with the current plan:

- free Community distribution
- later one-time Pro shell
- later Team pilot

DreamCleanr should earn the right to stronger pricing only after the premium shell is materially easier than the CLI and the Team lane has evidence behind it.

## Sources

- CleanMyMac store: https://macpaw.com/store/cleanmymac
- CleanMyMac purchase options: https://macpaw.com/support/cleanmymac/knowledgebase/purchase-options
- DaisyDisk pricing and licensing: https://daisydiskapp.com/support/pricing/
- Hazel store: https://store.noodlesoft.com/
- Hazel license types: https://www.noodlesoft.com/kb/what-are-the-different-types-of-hazel-licenses/
- OnyX official page: https://titanium-software.fr/en/onyx.html
