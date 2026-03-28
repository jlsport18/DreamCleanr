from __future__ import annotations

import argparse
import json
import sys
import traceback
import webbrowser
from pathlib import Path
from typing import Any, Dict

from . import __version__
from .core import (
    DEFAULT_RETENTION_COUNT,
    build_cleanup_report,
    capture_snapshot,
    default_report_dir,
    plan_cleanup,
    apply_actions,
    now_iso,
    prune_history_files,
    prune_rotated_logs,
)
from .reporting import write_html
from .scheduler import install_launch_agent, uninstall_launch_agent, write_launch_agent


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _latest_paths(output_dir: Path) -> Dict[str, Path]:
    return {
        "before": output_dir / "latest-before.json",
        "after": output_dir / "latest-after.json",
        "report": output_dir / "latest.json",
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


def command_clean(args: argparse.Namespace) -> int:
    dry_run = not args.apply
    output_dir = Path(args.output_dir) if args.output_dir else default_report_dir()
    output_dir.mkdir(parents=True, exist_ok=True)
    latest = _latest_paths(output_dir)

    try:
        before = capture_snapshot(mode=args.mode)
        planned_actions = plan_cleanup(before, mode=args.mode)
        if args.scope == "processes":
            planned_actions = [action for action in planned_actions if action.target_type == "process"]
        elif args.scope == "storage":
            planned_actions = [action for action in planned_actions if action.target_type != "process"]
        actions = apply_actions(before, planned_actions, dry_run=dry_run)
        after = capture_snapshot(mode=args.mode)
        report = build_cleanup_report(before, after, actions, mode=args.mode, dry_run=dry_run)
        report_dict = report.to_dict()

        run_id = report.run_id
        timestamp = now_iso().replace(":", "").replace("-", "")

        before_path = output_dir / f"before-{timestamp}-{run_id}.json"
        after_path = output_dir / f"after-{timestamp}-{run_id}.json"
        report_path = Path(args.json_out) if args.json_out else output_dir / f"report-{timestamp}-{run_id}.json"
        html_path = Path(args.html_out) if args.html_out else output_dir / f"report-{timestamp}-{run_id}.html"

        _write_json(before_path, before)
        _write_json(after_path, after)
        _write_json(report_path, report_dict)
        _write_json(latest["before"], before)
        _write_json(latest["after"], after)
        _write_json(latest["report"], report_dict)
        write_html(report_dict, html_path)
        write_html(report_dict, latest["html"])

        removed_reports = prune_history_files(output_dir, keep=args.retention_count)
        removed_logs = prune_rotated_logs(output_dir)

        print(f"Run ID: {run_id}")
        print(f"Before snapshot: {before_path}")
        print(f"After snapshot:  {after_path}")
        print(f"Report JSON:     {report_path}")
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

    clean = subparsers.add_parser("clean", help="Scan, classify, clean, and report.")
    clean.add_argument("--mode", choices=["safe", "balanced", "max"], default="balanced")
    clean.add_argument("--scope", choices=["all", "processes", "storage"], default="all")
    clean.add_argument("--apply", action="store_true", help="Apply cleanup actions instead of dry-run preview.")
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

    return parser


def main(argv: Any = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
