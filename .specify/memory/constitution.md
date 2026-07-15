# DreamCleanr Constitution

## Core Principles

### I. Never Touch What Isn't Yours
DreamCleanr classifies processes and storage as active, background, stale, or protected before ever proposing a reclaim. Protected AI state (live Docker, Claude, Codex sessions) is never pruned. When classification is ambiguous, the safe default is to leave it alone and surface it for the user to decide, not to guess toward reclaiming more space.

### II. Reversible By Default
Every cleanup action produces a one-page receipt describing exactly what was reclaimed and why it was classified as safe. A user reading the receipt should be able to understand and, where feasible, undo what happened — this is not a "trust the tool" black box.

### III. Read-Only Detection, Gated Action
Detector visibility (scanning Python, Node, Hugging Face, Ollama, LM Studio, Git/LFS, IDE support roots) is read-only and safe to run freely. Actually pruning anything is a separate, explicitly-gated step — detection finding something is never itself authorization to remove it.

### IV. Don't Break Active Workflows
Live Docker engine state, active Git-backed project signals, and running AI tool sessions are detected and excluded from cleanup targets, not merely deprioritized. A cleanup that silently disrupts an in-progress build or session is a correctness failure, not an acceptable tradeoff for reclaimed space.

## Cross-Portfolio Guardrails
<!-- Shared across JLFG's product portfolio (see pillar-os's CLAUDE.md, the portfolio orchestrator) -->

No production deploy, DNS change, key rotation, or data deletion without an explicit approval step. No unsubstantiated comparative claims about competing cleanup tools without a dated, cited source.

## Governance

This constitution documents DreamCleanr's design intent as stated in its own README and product description; it is a first draft, expected to be refined via a proper interactive `/speckit-constitution` session with deeper codebase-specific detail (exact classification heuristics, the safe-target allowlist/denylist) than a README alone can ground. It supersedes ad-hoc judgment calls on the four points above.

**Version**: 1.0.0 | **Ratified**: 2026-07-15 | **Last Amended**: 2026-07-15
