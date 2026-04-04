# DreamCleanr Feature Specs

This is the engineering-facing feature spec set for DreamCleanr Phase 2. It stays grounded in what ships today and what is still planned.

## 1. AI Safe Clean Engine

- Current state: `partial`
- Package: `Community`
- Description: classify cleanup targets as safe, protected, or manual-review using process ownership, storage family, and product safety rules.
- Inputs: process tree data, known cache paths, Docker inventory, protected-state paths, schedule mode.
- Outputs: cleanup plan, protected-items list, manual-review list, JSON + HTML receipt.
- Safety boundary: never auto-delete protected Claude/Codex roots, Claude VM bundle, Docker raw VM storage, or high-risk state without an explicit future override.
- Revenue impact: high
- Technical complexity: medium

## 2. Docker Optimizer

- Current state: `partial`
- Package: `Community`
- Description: separate active Docker engine state from stale helper probes and reclaim safe Docker-adjacent noise conservatively.
- Inputs: process lineage, Docker inventory commands, local Docker support paths.
- Outputs: active/interactive/stale process roles, safe prune recommendations, receipt entries.
- Safety boundary: never treat live engine ownership as stale; keep raw VM/storage manual-review unless an explicit future destructive mode exists.
- Revenue impact: high
- Technical complexity: medium

## 3. Python Environment Cleaner

- Current state: `planned`
- Package: `Community` moving into `Pro` for guided actions
- Description: detect `venv`, `conda`, and `poetry` environments and distinguish active project state from reclaimable leftovers.
- Inputs: project roots, lockfiles, env directories, access recency, interpreter references.
- Outputs: environment inventory, safe candidates, project-aware warnings.
- Safety boundary: never recommend deleting clearly active or linked environments without project-aware confirmation.
- Revenue impact: very high
- Technical complexity: high

## 4. LLM Cache Manager

- Current state: `planned`
- Package: `Community`
- Description: make local model and cache surfaces visible across Hugging Face, Ollama, and LM Studio before DreamCleanr offers guided cleanup.
- Inputs: known cache/model paths, size scans, recency, optional tool-specific metadata.
- Outputs: model/cache inventory, size summaries, safe-review candidates.
- Safety boundary: start with observability first; do not auto-delete model stores in the first iteration.
- Revenue impact: very high
- Technical complexity: high

## 5. Disk Heatmap

- Current state: `planned`
- Package: `Community`
- Description: visualize disk usage by developer artifact family such as Docker, caches, models, environments, repos, and logs.
- Inputs: detector registry outputs, directory size summaries, receipt history.
- Outputs: category-level breakdowns for the site, CLI summaries, and future native shell.
- Safety boundary: read-only observability surface.
- Revenue impact: high
- Technical complexity: medium

## 6. Auto-Optimization Agent

- Current state: `partial`
- Package: `Community` with richer experience in `Pro`
- Description: run balanced-safe cleanup on a schedule and generate reliable before/after artifacts.
- Inputs: launchd schedule, cleanup mode, retention count, local logs directory.
- Outputs: scheduled run, latest receipt artifacts, failure artifact when something goes wrong.
- Safety boundary: scheduled mode stays balanced-safe only and never crosses protected-state rules.
- Revenue impact: medium
- Technical complexity: low

## Product-State Summary

| Feature family | Shipped now | Phase 2 target |
|---|---|---|
| Docker-aware cleanup | yes | deeper inventory and observability |
| Claude/Codex-aware protection | yes | keep as trust moat |
| Safe cache cleanup | yes | broaden only with detector intelligence |
| Receipts and scheduling | yes | richer history and premium browsing |
| Python / Node awareness | no | add detector registry first |
| Ollama / LM Studio / Hugging Face | no | start with visibility, then guided cleanup |
| Disk heatmap | no | build as observability-first surface |
| Native shell | no | Phase 2 premium moat |

## Public Demo Truth Table

Use this table for the homepage demo, launch copy, and investor-facing materials.

| Category | Allowed as current on the public site | Notes |
|---|---|---|
| Docker reclaimable layers | yes | grounded in current DreamCleanr strength |
| Safe cache and log noise | yes | grounded in current safe cleanup behavior |
| Stale helper residue | yes | grounded in current process cleanup behavior |
| Protected AI state | yes | must be framed as protected, not reclaimable |
| Python environments | no | teaser only until detector support exists |
| Node workspaces | no | teaser only until detector support exists |
| Hugging Face | no | teaser only until detector support exists |
| Ollama / LM Studio | no | teaser only until detector support exists |
| Project-aware cleanup safety | no | roadmap only until implementation exists |
