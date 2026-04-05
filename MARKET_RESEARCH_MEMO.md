# DreamCleanr Market Research Memo

Last updated: `2026-04-05`

This memo supports [MONETIZATION_PLAN.md](MONETIZATION_PLAN.md) and [MARKET_STRATEGY.md](MARKET_STRATEGY.md).

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
