from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Dict, List

from .core import human_bytes

_CSS = """
<style>
  :root{
    --paper:#f7f4ec;
    --ink:#202124;
    --muted:#6f766f;
    --line:#ddd5c8;
    --sea:#4f9d84;
    --sand:#c7933d;
    --coral:#c66a59;
    --card:#fffcf5;
  }
  *{box-sizing:border-box}
  body{margin:0;font-family:ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:linear-gradient(180deg,#faf7f0 0%,#f3efe6 100%);color:var(--ink)}
  .page{max-width:1080px;margin:0 auto;padding:24px}
  .topbar{display:flex;justify-content:space-between;align-items:flex-start;gap:18px;padding:18px 20px;background:rgba(255,255,255,.7);border:1px solid rgba(221,213,200,.9);backdrop-filter:blur(10px);border-radius:22px}
  .title{font-size:2rem;font-weight:800;letter-spacing:-.03em}
  .subtitle{color:var(--muted);margin-top:6px}
  .chips{display:flex;gap:10px;flex-wrap:wrap}
  .chip{padding:8px 12px;border-radius:999px;border:1px solid var(--line);background:#fff;font-size:.82rem;font-weight:700}
  .chip.preview{color:var(--sand);border-color:rgba(199,147,61,.35);background:rgba(199,147,61,.08)}
  .chip.applied{color:var(--sea);border-color:rgba(79,157,132,.35);background:rgba(79,157,132,.08)}
  .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin-top:18px}
  .card{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:18px;box-shadow:0 8px 28px rgba(0,0,0,.04)}
  .label{font-size:.78rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);font-weight:800}
  .value{font-size:1.9rem;font-weight:800;margin-top:8px}
  .subvalue{margin-top:6px;color:var(--muted);font-size:.92rem}
  .section{margin-top:22px}
  .section h2{font-size:1rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin:0 0 10px}
  .storage-bar{margin-top:14px;background:#ece4d6;border-radius:999px;height:14px;overflow:hidden;position:relative}
  .storage-before,.storage-after{height:100%;border-radius:999px}
  .storage-before{background:rgba(199,147,61,.35)}
  .storage-after{position:absolute;left:0;top:0;background:linear-gradient(90deg,var(--sea),#72b59f)}
  .legend{display:flex;justify-content:space-between;color:var(--muted);font-size:.86rem;margin-top:8px}
  .stack{display:grid;gap:10px}
  .row{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(100px,.5fr) 1fr auto;gap:12px;align-items:center;background:rgba(255,255,255,.65);border:1px solid var(--line);border-radius:14px;padding:12px 14px}
  .bar{height:8px;background:#ece4d6;border-radius:999px;overflow:hidden}
  .bar span{display:block;height:100%;background:linear-gradient(90deg,var(--sea),#79b7a2)}
  .row .name{font-weight:700;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .size{font-variant-numeric:tabular-nums;color:var(--ink);font-weight:700}
  .badge{padding:6px 10px;border-radius:999px;font-size:.76rem;font-weight:800;border:1px solid var(--line);background:#fff}
  .badge.deleted,.badge.terminated{color:var(--sea)}
  .badge.planned,.badge.kept{color:var(--sand)}
  .badge.blocked,.badge.failed{color:var(--coral)}
  .badge.review,.badge.skipped{color:var(--muted)}
  details{margin-top:14px;background:rgba(255,255,255,.55);border:1px solid var(--line);border-radius:14px;padding:12px 14px}
  summary{cursor:pointer;font-weight:700}
  pre{white-space:pre-wrap;word-break:break-word;font-size:.84rem;color:#334;background:#fff;padding:12px;border-radius:12px;border:1px solid var(--line);max-height:360px;overflow:auto}
</style>
"""


def _badge(text: str, klass: str) -> str:
    return f'<span class="badge {html.escape(klass)}">{html.escape(text)}</span>'


def _card(label: str, value: str, subvalue: str) -> str:
    return (
        '<div class="card">'
        f'<div class="label">{html.escape(label)}</div>'
        f'<div class="value">{html.escape(value)}</div>'
        f'<div class="subvalue">{html.escape(subvalue)}</div>'
        '</div>'
    )


def _top_offenders(snapshot: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
    records = list(snapshot.get("storage_records", []))
    records.sort(key=lambda item: item.get("size_bytes", 0), reverse=True)
    return records[:limit]


def _top_actions(actions: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
    ranked = sorted(actions, key=lambda item: item.get("bytes_reclaimed", 0), reverse=True)
    return ranked[:limit]


def _group_counts(actions: List[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for action in actions:
        counts[action["result"]] = counts.get(action["result"], 0) + 1
    return counts


def render_html(report: Dict[str, Any]) -> str:
    snapshot = report["snapshot"]
    actions = report["actions"]
    dry_run = report["dry_run"]
    outcome_label = "Estimated Reclaimable" if dry_run else "Reclaimed"
    state_chip = _badge("Preview", "preview") if dry_run else _badge("Applied", "applied")
    largest = _top_offenders(snapshot, 1)
    largest_label = largest[0]["label"] if largest else "No major opportunities"
    protected_items = report.get("protected_items", [])
    manual_review = report.get("manual_review_items", [])
    top_offenders = _top_offenders(snapshot)
    top_actions = _top_actions(actions)
    counts = _group_counts(actions)

    used_before = report["storage_before_bytes"]
    used_after = report["storage_after_bytes"]
    total = max(snapshot.get("host_disk_total_bytes", used_before + 1), 1)
    before_pct = max(1.0, min(100.0, (used_before / total) * 100.0))
    after_pct = max(1.0, min(100.0, (used_after / total) * 100.0))
    max_offender = max([item.get("size_bytes", 0) for item in top_offenders] + [1])

    cards = [
        _card(outcome_label, human_bytes(report["storage_reclaimed_bytes"]), largest_label),
        _card("Free Space Now", human_bytes(snapshot.get("host_disk_free_bytes", 0)), "Live disk headroom after scan"),
        _card("Actions", str(len(actions)), f"{counts.get('deleted', 0) + counts.get('terminated', 0)} applied or {counts.get('planned', 0)} planned"),
        _card("Deferred Risks", str(len(manual_review)), "High-value items left for manual review"),
    ]

    rows = []
    for item in top_offenders:
        width = max(4, min(100, int((item.get("size_bytes", 0) / max_offender) * 100)))
        rows.append(
            '<div class="row">'
            f'<div class="name">{html.escape(item["label"])}</div>'
            f'<div class="size">{human_bytes(item["size_bytes"])}</div>'
            f'<div class="bar"><span style="width:{width}%"></span></div>'
            f'{_badge(item["classification"].replace("_", " ").title(), "review" if "PROTECTED" in item["classification"] or "REVIEW" in item["classification"] else "planned")}'
            '</div>'
        )

    action_rows = []
    for action in top_actions:
        action_rows.append(
            '<div class="row">'
            f'<div class="name">{html.escape(action["target"])}</div>'
            f'<div class="size">{human_bytes(action["bytes_reclaimed"])}</div>'
            '<div class="bar"><span style="width:100%"></span></div>'
            f'{_badge(action["result"].replace("_", " ").title(), action["result"])}'
            '</div>'
        )

    protected_strip = []
    for item in protected_items[:6]:
        protected_strip.append(_badge(item["label"], "kept"))
    for item in manual_review[:4]:
        protected_strip.append(_badge(item["label"], "review"))

    why_safe = []
    for family in ("docker", "claude", "codex"):
        summary = snapshot.get("process_summary", {}).get(family, {})
        why_safe.append(
            '<div class="row">'
            f'<div class="name">{family.title()}</div>'
            f'<div class="size">{summary.get("state", "n/a")}</div>'
            '<div class="bar"><span style="width:100%"></span></div>'
            f'{_badge(summary.get("recommended_action", "protect_only").replace("_", " ").title(), "review")}'
            '</div>'
        )

    raw_actions = json.dumps(actions, indent=2)
    raw_snapshot = json.dumps(snapshot.get("process_summary", {}), indent=2)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>DreamCleanr Cleanup Receipt</title>
  {_CSS}
</head>
<body>
  <div class="page">
    <div class="topbar">
      <div>
        <div class="title">DreamCleanr</div>
        <div class="subtitle">Cleanup receipt generated {html.escape(report['finished_at'])}</div>
      </div>
      <div class="chips">
        {_badge(report['mode'].title(), 'review')}
        {state_chip}
      </div>
    </div>

    <div class="grid">{''.join(cards)}</div>

    <div class="card section">
      <h2>Storage Before vs After</h2>
      <div class="storage-bar">
        <div class="storage-before" style="width:{before_pct:.1f}%"></div>
        <div class="storage-after" style="width:{after_pct:.1f}%"></div>
      </div>
      <div class="legend">
        <span>Before: {human_bytes(used_before)}</span>
        <span>After: {human_bytes(used_after)}</span>
      </div>
    </div>

    <div class="section">
      <h2>Biggest Wins</h2>
      <div class="stack">{''.join(rows) or '<div class="card">No significant storage targets found.</div>'}</div>
    </div>

    <div class="section">
      <h2>What Happened</h2>
      <div class="grid">
        {_card('Deleted', str(counts.get('deleted', 0) + counts.get('terminated', 0)), 'Applied removals and terminated stale processes')}
        {_card('Previewed', str(counts.get('planned', 0)), 'Safe opportunities identified in dry run')}
        {_card('Blocked', str(counts.get('blocked', 0)), 'Protection rule prevented removal')}
        {_card('Kept', str(counts.get('kept', 0)), 'Protected items intentionally preserved')}
      </div>
      <div class="stack">{''.join(action_rows) or '<div class="card">No cleanup actions were needed.</div>'}</div>
    </div>

    <div class="section">
      <h2>Left Alone On Purpose</h2>
      <div class="card">{' '.join(protected_strip) or 'No protected items were recorded.'}</div>
    </div>

    <div class="section">
      <h2>Why It Was Safe</h2>
      <div class="stack">{''.join(why_safe)}</div>
    </div>

    <details>
      <summary>Full action log</summary>
      <pre>{html.escape(raw_actions)}</pre>
    </details>

    <details>
      <summary>Process safety summary</summary>
      <pre>{html.escape(raw_snapshot)}</pre>
    </details>
  </div>
</body>
</html>"""


def write_html(report: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_html(report), encoding="utf-8")
