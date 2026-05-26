# DreamCleanr — Branding & Market Analysis (memory-first reposition)

Grounded in what the engine can now honestly claim (see the claim↔engine table), the
in-repo `MARKET_RESEARCH_MEMO.md`, and the operator steer: *memory cleanup is the
primary function; keep a "maximum" ceiling to show how much could be reclaimed.*

## 1. Positioning shift — memory-first, primary-among-equals

Disk cleaning is commodity ("yet another Mac cleaner"). The differentiated, unowned
category is **showing AI developers what their tools cost in RAM and shutting down what
they're not using.** Recommendation: lead the copy and the receipt with **memory**;
keep **disk** prominent (still real $ + bundled-receipt wow). Do **not** demote disk.

Why memory wins as the hook:
- The pain is **attributable** (a loaded Ollama model is 8–40 GB resident; the Docker
  VM reserves GBs; idle Electron AI helpers add up) and **recurring** (the helpers
  re-grow the debt daily → recurring-revenue justification).
- It's **visible and dramatic**: `ollama stop` can drop 12–40 GB in one command,
  reversible. That is the demo GIF.

## 2. The wow asset — the attributable ceiling

Headline (CLI first line + receipt header), e.g.:
`DreamCleanr can reclaim up to 23.4 GB RAM and 45 GB disk right now.`
followed by a **named, verb-bearing breakdown** (real engine output):
```
RAM   Ollama model 'llama3:70b' resident in RAM   ~40.0GB  → ollama stop llama3:70b  (reversible)
RAM   idle docker process (pid 812)               ~1.2GB   → terminate
disk  node cache                                  ~844.4MB → trash/delete
```

**Non-negotiable honesty rules (already enforced in code):**
- Never aggregate unattributed bytes ("14 GB wasted"). Every line is a source + a verb. *(reclaim_ceiling sums only named sources.)*
- Inactive/cached memory is **reported but never counted** as reclaimable (kernel reuses it). *(capture_memory_state separates `inactive_bytes` from `used_bytes`.)*
- Downloaded models are **surfaced for review, never auto-deleted.** *(reclaim_policy=model_data.)*
- `purge` is mentioned as a **manual** command only — never auto-run (needs sudo; kernel reuses what it frees).

## 3. Competitor gap (the moat statement)

| Tool | Disk | RAM | AI-aware (models/containers) | Reversible | Read-only? |
| --- | --- | --- | --- | --- | --- |
| CleanMyMac / commercial cleaners | ✅ | partial | ❌ | ❌ | no |
| Activity Monitor | — | shows | ❌ | — | **read-only** |
| `npkill` / `DevCleaner` | one tool | ❌ | ❌ | ❌ | no |
| **DreamCleanr** | ✅ | ✅ | ✅ models + containers + caches | ✅ Trash net | acts w/ confirm |

*Nobody* unifies dev-AI-aware **RAM + disk + containers** with a **safety net**. That row is the pitch.

## 4. Claim ↔ engine truth table (brand-truth audit — never claim what we can't back)

| Marketing claim | Backed by |
| --- | --- |
| "See exactly what your AI tools cost in RAM" | `capture_memory_state` + `list_loaded_models` + `reclaim_ceiling` |
| "Reclaim up to N GB RAM right now" | `reclaim_ceiling.ram_sources` (named) |
| "Unload idle models, keep them on disk" | `ollama stop` action (reversible); models never deleted |
| "Knows your 40 GB model is an asset, not a cache" | `reclaim_policy=model_data` (surfaced, never auto-deleted) |
| "Won't touch caches tied to an active project" | project-signal guard (`safety_state=guarded_by_active_projects`) |
| "Reversible — restore from Trash" | `--trash` net (default on for max) |
| "Fast" | parallelized `du_bytes_many` scan |
| **Not yet claimable** (DEFER): "prunes unused model revisions" | needs MODEL-2 (per-tool GC) — say "review", not "prune" |

## 5. ICP voice (method, not fabricated quotes)

Validate copy against how AI devs *actually* phrase the pain before finalizing — sweep
`r/LocalLLaMA`, HN local-LLM threads, X/`ollama ate my ram`. Echo their words. Working
hypotheses to confirm: "Ollama is eating my RAM", "Docker Desktop reserves half my
memory", "why is my Mac swapping". (These are directions to verify, not citations.)

## 6. Pricing implication — the recurring-value answer

The classic objection: *"why pay monthly for a one-time cleanup?"* Memory answers it:
the AI helpers re-grow the RAM debt **daily**.
- **Free:** scan + the ceiling number + manual reclaim (the wow, ungated — drives virality).
- **Pro (one-time, per the no-subscription stance) OR low recurring:** the **Memory Guardian** — scheduled monitoring, auto-unload models idle > N days, RAM-pressure alerts, menu-bar live widget. This is the genuinely recurring value if/when a subscription is introduced.
- Team/Enterprise: fleet policies + reporting (later).

## 7. CTA slogans (each rests on a real engine claim)

Principle: name the tool, position vs Activity Monitor, brand the safety net, quantify with the real receipt.
- **"Ollama eating your RAM? Reclaim it in one command."** *(ollama stop)*
- **"Activity Monitor shows what's running. DreamCleanr stops what isn't."** *(classification + reclaim)*
- **"Knows your models are 40 GB. Won't delete them."** *(model_data policy)*
- **"Reclaimed 23 GB — without touching your work."** *(ceiling + active-project guard)*
- **"Your AI tools are holding 18 GB hostage. Here's the list."** *(named ram_sources)*
- **"Free the RAM. Keep the models. Undo anything."** *(trash net + reversible unload)*

(Finalize with real numbers from the user's own machine — specificity is the share trigger.)

## 8. Branding moves + what a full market analysis must examine

- **Don't rename** ("DreamCleanr"): rename ROI is negative now (SEO, installs, chatbot, JLFG portfolio entry). Reposition the **tagline + receipt**, not the name. Tagline e.g. *"The memory & disk reclaimer for AI developers."*
- A full analysis should produce: (a) ICP voice corpus (above), (b) the competitor gap chart kept current, (c) this claim↔engine table as a permanent brand-truth gate, (d) a pricing test of one-time vs Memory-Guardian recurring, (e) a viral-loop measurement (receipt shares → installs).
- **Next research step:** live ICP-voice sweep + a landing-page rewrite that leads with the RAM ceiling and the named breakdown.
