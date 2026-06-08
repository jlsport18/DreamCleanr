from __future__ import annotations

import argparse
import fcntl
import json
import logging
import sys
import traceback
import webbrowser
from pathlib import Path
from typing import Any, Dict

log = logging.getLogger(__name__)

from . import __version__
from .license import activate as _activate_license, check_pro, get_license_info, deactivate as _deactivate_license
from .core import (
    DEFAULT_RETENTION_COUNT,
    build_cleanup_report,
    capture_snapshot,
    default_report_dir,
    human_bytes,
    plan_cleanup,
    apply_actions,
    now_iso,
    prune_history_files,
    prune_rotated_logs,
    reclaim_ceiling,
)


_PRO_BUY_URL = "https://buy.stripe.com/eVqbJ29JcfWT7nue5R93y0v"


def _print_max_gate() -> None:
    """Developer mode (`--mode max`) is a Pro feature — hard-gated."""
    print(
        "⛔ Developer mode (--mode max) is a Sweep Pro feature.\n"
        "   It targets Xcode DerivedData, node_modules, Docker, and AI model caches.\n"
        f"   Unlock it: {_PRO_BUY_URL}\n"
        "   Then run: sweep license activate --key SWEEP-... --email you@example.com\n"
        "   Running 'balanced' mode instead.",
        file=sys.stderr,
    )


def _print_schedule_nag() -> None:
    """Scheduled cleaning works on Community, with an upsell nag."""
    print(
        "💡 Scheduled cleaning installed. Sweep Pro removes this notice and unlocks\n"
        f"   developer mode. Upgrade: {_PRO_BUY_URL}",
        file=sys.stderr,
    )


def _actions_caused_state_change(actions) -> bool:
    """True if any action mutated host state (deleted disk / terminated proc /
    unloaded model). Per issue #8 — skip the duplicate-snapshot rescan when
    nothing happened.

    Excludes: planned (dry-run), kept (preview-only), blocked, failed,
    missing, skipped — none of those touched disk or RAM.
    """
    successful = {"deleted", "terminated", "unloaded"}
    return any(action.result in successful for action in actions)


def _print_ceiling(snapshot: Dict[str, Any], stream) -> None:
    try:
        ceiling = reclaim_ceiling(snapshot)
    except Exception:  # display is non-critical — never let it break a cleanup run
        log.exception("reclaim_ceiling failed; skipping ceiling display")
        return
    print(
        f"DreamCleanr can reclaim up to {human_bytes(ceiling['ram_bytes'])} RAM "
        f"and {human_bytes(ceiling['disk_bytes'])} disk right now.",
        file=stream,
    )
    for source in ceiling["ram_sources"][:5]:
        tag = "  (reversible)" if source.get("reversible") else ""
        print(f"  RAM   {source['source']}  ~{human_bytes(source['bytes'])}  → {source['action']}{tag}", file=stream)
    for source in ceiling["disk_sources"][:3]:
        print(f"  disk  {source['source']}  ~{human_bytes(source['bytes'])}", file=stream)


def _planned_deletions(actions: list) -> list:
    """Actions that would actually delete/terminate (not preview-gated)."""
    return [a for a in actions if a.details.get("apply_allowed", True)]


def _confirm_apply(actions: list, mode: str, use_trash: bool = False) -> bool:
    deletions = _planned_deletions(actions)
    mem = [a for a in deletions if a.target_type == "memory"]
    paths = [a for a in deletions if a.target_type not in {"process", "memory"}]
    procs = sum(1 for a in deletions if a.target_type == "process")
    disk_total = sum(a.bytes_reclaimed for a in paths)
    ram_total = sum(a.bytes_reclaimed for a in mem)
    verb = "trash" if use_trash else "delete"
    print(f"DreamCleanr will apply {len(deletions)} action(s) in '{mode}' mode:")
    for action in mem[:10]:
        print(f"  unload    {action.target}  (~{human_bytes(action.bytes_reclaimed)} RAM)  (reversible)")
    for action in paths[:20]:
        label = action.details.get("label", action.target)
        print(f"  {verb:<9} {label}  (~{human_bytes(action.bytes_reclaimed)})")
    if len(paths) > 20:
        print(f"  … and {len(paths) - 20} more path(s)")
    if procs:
        print(f"  terminate {procs} stale process(es)")
    if use_trash:
        print("Paths go to the macOS Trash (restore from Finder); empty the Trash to reclaim space.")
    reclaim = f"~{human_bytes(disk_total)} disk"
    if ram_total:
        reclaim += f" + ~{human_bytes(ram_total)} RAM"
    print(f"Estimated reclaim: {reclaim}")
    try:
        answer = input("Proceed? [y/N] ").strip().lower()
    except EOFError:
        return False
    return answer in {"y", "yes"}


def _acquire_run_lock(output_dir: Path):
    """Non-blocking exclusive lock so a manual run and the scheduled job don't
    apply concurrently to the same report dir. Returns the held handle or None."""
    lock_path = output_dir / ".dreamcleanr.lock"
    handle = open(lock_path, "w")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        handle.close()
        return None
    return handle


def _release_run_lock(handle) -> None:
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    finally:
        handle.close()
from .reporting import build_receipt_summary, build_team_export, write_html, write_team_csv
from .scheduler import install_launch_agent, uninstall_launch_agent, write_launch_agent


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _latest_paths(output_dir: Path) -> Dict[str, Path]:
    return {
        "before": output_dir / "latest-before.json",
        "after": output_dir / "latest-after.json",
        "report": output_dir / "latest.json",
        "summary": output_dir / "latest-summary.json",
        "html": output_dir / "latest.html",
        "failure": output_dir / "latest-failure.json",
    }


def _failure_payload(exc: Exception, mode: str, dry_run: bool) -> Dict[str, Any]:
    return {
        "run_id": now_iso().replace(":", "").replace("-", ""),
        "finished_at": now_iso(),
        "mode": mode,
        "dry_run": dry_run,
        "error": {
            "type": exc.__class__.__name__,
            "message": str(exc),
            "traceback": traceback.format_exc(),
        },
    }


def command_scan(args: argparse.Namespace) -> int:
    snapshot = capture_snapshot(mode=args.mode)
    _print_ceiling(snapshot, sys.stderr)  # human summary on stderr; stdout stays pure JSON
    payload = snapshot
    if args.json_out:
        _write_json(Path(args.json_out), payload)
    else:
        print(json.dumps(payload, indent=2))
    return 0


def command_report(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    output_path = Path(args.html_out) if args.html_out else input_path.with_suffix(".html")
    report = json.loads(input_path.read_text(encoding="utf-8"))
    write_html(report, output_path)
    print(f"Wrote HTML report: {output_path}")
    if args.open:
        webbrowser.open(output_path.as_uri())
    return 0


def command_export(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    report = json.loads(input_path.read_text(encoding="utf-8"))
    export = build_team_export(report)
    json_out = Path(args.json_out) if args.json_out else input_path.with_name(f"{input_path.stem}-team-export.json")
    csv_out = Path(args.csv_out) if args.csv_out else input_path.with_name(f"{input_path.stem}-team-export.csv")
    _write_json(json_out, export)
    write_team_csv(export, csv_out)
    print(f"Wrote team export JSON: {json_out}")
    print(f"Wrote team export CSV:  {csv_out}")
    return 0


def command_clean(args: argparse.Namespace) -> int:
    dry_run = not args.apply
    pro = check_pro()
    if args.mode == "max" and not pro:
        _print_max_gate()
        args.mode = "balanced"
    output_dir = Path(args.output_dir) if args.output_dir else default_report_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    latest = _latest_paths(output_dir)

    lock_handle = None
    if not dry_run:
        lock_handle = _acquire_run_lock(output_dir)
        if lock_handle is None:
            print(
                "Another DreamCleanr apply is in progress for this report dir; skipping.",
                file=sys.stderr,
            )
            return 0

    try:
        before = capture_snapshot(mode=args.mode)
        _print_ceiling(before, sys.stdout)  # lead with the wow number
        planned_actions = plan_cleanup(before, mode=args.mode)
        if args.scope == "processes":
            planned_actions = [action for action in planned_actions if action.target_type == "process"]
        elif args.scope == "storage":
            planned_actions = [action for action in planned_actions if action.target_type != "process"]

        # Trash (restorable) vs hard-delete. Default: on for the aggressive max
        # tier, off for balanced (regenerable caches free space immediately).
        use_trash = args.trash if getattr(args, "trash", None) is not None else (args.mode == "max")
        if not dry_run and _planned_deletions(planned_actions):
            # Interactive runs confirm before deleting. Scripted / scheduled runs
            # (no TTY) are intentional automation and proceed — this preserves an
            # already-installed LaunchAgent. --yes skips the prompt explicitly.
            if not getattr(args, "yes", False) and sys.stdin.isatty():
                if not _confirm_apply(planned_actions, args.mode, use_trash):
                    print("Aborted — running a preview instead; no changes made.")
                    dry_run = True
        actions = apply_actions(before, planned_actions, dry_run=dry_run, trash=use_trash)

        # Issue #8: skip the duplicate-snapshot cost when nothing actually
        # changed. In dry-run mode AND when no action mutated state
        # (all blocked/failed/skipped/kept), the after snapshot would be
        # identical to before — re-use it and stamp a fresh finished_at.
        # Saves ~half the wall-clock time on dry-run flows (the second
        # capture_snapshot is the largest single cost per profiling on
        # issue #8: balanced scan ~29s, full apply path ~56s).
        if dry_run or not _actions_caused_state_change(actions):
            after = dict(before)
            after["finished_at"] = now_iso()
        else:
            after = capture_snapshot(mode=args.mode)
        report = build_cleanup_report(before, after, actions, mode=args.mode, dry_run=dry_run)
        report_dict = report.to_dict()

        run_id = report.run_id
        timestamp = now_iso().replace(":", "").replace("-", "")

        before_path = output_dir / f"before-{timestamp}-{run_id}.json"
        after_path = output_dir / f"after-{timestamp}-{run_id}.json"
        report_path = Path(args.json_out) if args.json_out else output_dir / f"report-{timestamp}-{run_id}.json"
        summary_path = output_dir / f"summary-{timestamp}-{run_id}.json"
        html_path = Path(args.html_out) if args.html_out else output_dir / f"report-{timestamp}-{run_id}.html"
        summary_dict = build_receipt_summary(report_dict)

        _write_json(before_path, before)
        _write_json(after_path, after)
        _write_json(report_path, report_dict)
        _write_json(summary_path, summary_dict)
        _write_json(latest["before"], before)
        _write_json(latest["after"], after)
        _write_json(latest["report"], report_dict)
        _write_json(latest["summary"], summary_dict)
        write_html(report_dict, html_path, pro=pro)
        write_html(report_dict, latest["html"], pro=pro)

        removed_reports = prune_history_files(output_dir, keep=args.retention_count)
        removed_logs = prune_rotated_logs(output_dir)

        print(f"Run ID: {run_id}")
        print(f"Before snapshot: {before_path}")
        print(f"After snapshot:  {after_path}")
        print(f"Report JSON:     {report_path}")
        print(f"Summary JSON:    {summary_path}")
        print(f"Report HTML:     {html_path}")
        if removed_reports:
            print(f"Pruned history:  {len(removed_reports)} old artifact files")
        if removed_logs:
            print(f"Pruned logs:     {len(removed_logs)} rotated log files")
        if args.open:
            webbrowser.open(html_path.as_uri())
        return 0
    except Exception as exc:  # pragma: no cover - runtime safety
        timestamp = now_iso().replace(":", "").replace("-", "")
        failure = _failure_payload(exc, mode=args.mode, dry_run=dry_run)
        failure_path = output_dir / f"failure-{timestamp}.json"
        _write_json(failure_path, failure)
        _write_json(latest["failure"], failure)
        prune_history_files(output_dir, keep=args.retention_count)
        print(f"DreamCleanr clean failed: {exc}", file=sys.stderr)
        print(f"Failure report: {failure_path}", file=sys.stderr)
        return 1
    finally:
        if lock_handle is not None:
            _release_run_lock(lock_handle)


def command_schedule_install(args: argparse.Namespace) -> int:
    repo_root = Path(__file__).resolve().parent.parent
    output_dir = Path(args.output_dir) if args.output_dir else default_report_dir()
    plist_path = write_launch_agent(
        repo_root=repo_root,
        output_dir=output_dir,
        hour=args.hour,
        minute=args.minute,
        mode=args.mode,
        retention_count=args.retention_count,
    )
    install_launch_agent(plist_path)
    print(f"Installed LaunchAgent: {plist_path}")
    if not check_pro():
        _print_schedule_nag()
    return 0


def command_schedule_uninstall(_: argparse.Namespace) -> int:
    removed = uninstall_launch_agent()
    if removed:
        print(f"Removed LaunchAgent: {removed}")
    else:
        print("No LaunchAgent installed.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dreamcleanr")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Capture a machine-readable process and storage snapshot.")
    scan.add_argument("--mode", choices=["safe", "balanced", "max"], default="balanced")
    scan.add_argument("--json-out", help="Write snapshot JSON to a file.")
    scan.set_defaults(func=command_scan)

    report = subparsers.add_parser("report", help="Render a self-contained HTML report from a cleanup JSON report.")
    report.add_argument("--input", required=True, help="Path to cleanup report JSON.")
    report.add_argument("--html-out", help="Write HTML report to a file.")
    report.add_argument("--open", action="store_true", help="Open the HTML report in the default browser.")
    report.set_defaults(func=command_report)

    export = subparsers.add_parser("export", help="Write admin-friendly team export artifacts from a cleanup JSON report.")
    export.add_argument("--input", required=True, help="Path to cleanup report JSON.")
    export.add_argument("--json-out", help="Write team export JSON to a file.")
    export.add_argument("--csv-out", help="Write team export CSV to a file.")
    export.set_defaults(func=command_export)

    clean = subparsers.add_parser("clean", help="Scan, classify, clean, and report.")
    clean.add_argument("--mode", choices=["safe", "balanced", "max"], default="balanced")
    clean.add_argument("--scope", choices=["all", "processes", "storage"], default="all")
    clean.add_argument("--apply", action="store_true", help="Apply cleanup actions instead of dry-run preview.")
    clean.add_argument("--yes", "-y", action="store_true", help="Skip the interactive confirmation prompt before --apply.")
    clean.add_argument("--trash", dest="trash", action="store_true", default=None, help="Move deleted items to the macOS Trash (restorable) instead of removing them. Default: on for --mode max.")
    clean.add_argument("--no-trash", dest="trash", action="store_false", help="Hard-delete to reclaim space immediately, even in --mode max.")
    clean.add_argument("--output-dir", help="Directory for JSON and HTML reports.")
    clean.add_argument("--json-out", help="Write cleanup report JSON to a specific file.")
    clean.add_argument("--html-out", help="Write cleanup report HTML to a specific file.")
    clean.add_argument("--retention-count", type=int, default=DEFAULT_RETENTION_COUNT, help="How many timestamped runs to keep.")
    clean.add_argument("--open", action="store_true", help="Open the HTML report in the default browser.")
    clean.set_defaults(func=command_clean)

    schedule = subparsers.add_parser("schedule", help="Install or remove the macOS LaunchAgent.")
    schedule_subparsers = schedule.add_subparsers(dest="schedule_command", required=True)

    install = schedule_subparsers.add_parser("install", help="Install the DreamCleanr LaunchAgent.")
    install.add_argument("--hour", type=int, default=4)
    install.add_argument("--minute", type=int, default=30)
    install.add_argument("--mode", choices=["safe", "balanced", "max"], default="balanced")
    install.add_argument("--output-dir", help="Directory for scheduled JSON and HTML reports.")
    install.add_argument("--retention-count", type=int, default=DEFAULT_RETENTION_COUNT)
    install.set_defaults(func=command_schedule_install)

    uninstall = schedule_subparsers.add_parser("uninstall", help="Remove the DreamCleanr LaunchAgent.")
    uninstall.set_defaults(func=command_schedule_uninstall)

    # ── License subcommands ──────────────────────────────────────────────
    license_cmd = subparsers.add_parser("license", help="Manage your Sweep Pro license.")
    license_sub = license_cmd.add_subparsers(dest="license_command", required=True)

    activate_cmd = license_sub.add_parser("activate", help="Activate a Sweep Pro license key.")
    activate_cmd.add_argument("--key", required=True, help="License key from your receipt (SWEEP-...).")
    activate_cmd.add_argument("--email", required=True, help="Email address used to purchase Sweep Pro.")
    activate_cmd.set_defaults(func=command_license_activate)

    status_cmd = license_sub.add_parser("status", help="Show current license status.")
    status_cmd.set_defaults(func=command_license_status)

    deactivate_cmd = license_sub.add_parser("deactivate", help="Remove the license from this machine.")
    deactivate_cmd.set_defaults(func=command_license_deactivate)

    return parser


def command_license_activate(args: Any) -> int:
    try:
        _activate_license(key=args.key, email=args.email)
        print("✅ Sweep Pro activated. Welcome to the Pro tier.")
        print("   Developer mode, scheduled cleaning, and priority support are now unlocked.")
        return 0
    except ValueError as exc:
        print(f"❌ Activation failed: {exc}", file=sys.stderr)
        return 1


def command_license_status(args: Any) -> int:
    info = get_license_info()
    if info:
        print(f"✅ Sweep Pro — active")
        print(f"   Email:        {info.get('email', '?')}")
        print(f"   Activated:    {info.get('activated_at', '?')[:10]}")
        print(f"   Tier:         {info.get('tier', 'pro').upper()}")
    else:
        print("ℹ️  Sweep Community (free)")
        print("   Purchase Sweep Pro at: https://buy.stripe.com/eVqbJ29JcfWT7nue5R93y0v")
        print("   Then run: sweep license activate --key SWEEP-... --email you@example.com")
    return 0


def command_license_deactivate(args: Any) -> int:
    removed = _deactivate_license()
    if removed:
        print("License removed from this machine.")
    else:
        print("No license found on this machine.")
    return 0


def main(argv: Any = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
