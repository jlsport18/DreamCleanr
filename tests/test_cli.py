from __future__ import annotations

import json
import unittest
from argparse import Namespace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

from dreamcleanr import __version__
from dreamcleanr.cli import _actions_caused_state_change, build_parser, command_clean, command_export
from dreamcleanr.models import CleanupAction


class _StubReport:
    run_id = "runGATE"

    def to_dict(self) -> dict:
        return {"run_id": "runGATE"}


def _deletion_action() -> CleanupAction:
    return CleanupAction(
        target="/tmp/dreamcleanr-test-cache",
        target_type="path",
        family="system",
        classification="SAFE_CACHE",
        result="planned",
        bytes_reclaimed=10,
        reason="test",
        details={"label": "uv_cache", "apply_allowed": True},
    )


def _apply_args(tmpdir: str, yes: bool, mode: str = "balanced", trash=None) -> Namespace:
    return Namespace(
        mode=mode,
        apply=True,
        yes=yes,
        trash=trash,
        output_dir=tmpdir,
        json_out=None,
        html_out=None,
        retention_count=21,
        open=False,
        scope="all",
    )


class CliTests(unittest.TestCase):
    # Issue #8 — _actions_caused_state_change drives the "skip the
    # duplicate after-snapshot" optimization. Contract: returns True iff
    # at least one action actually mutated host state.

    def test_actions_caused_state_change_true_on_deletion(self) -> None:
        actions = [CleanupAction(target="x", target_type="path", family="f",
                                 classification="C", result="deleted",
                                 bytes_reclaimed=1, reason="r", details={})]
        self.assertTrue(_actions_caused_state_change(actions))

    def test_actions_caused_state_change_true_on_termination(self) -> None:
        actions = [CleanupAction(target="123", target_type="process", family="f",
                                 classification="C", result="terminated",
                                 bytes_reclaimed=1, reason="r", details={})]
        self.assertTrue(_actions_caused_state_change(actions))

    def test_actions_caused_state_change_false_on_dry_run_planned(self) -> None:
        actions = [
            CleanupAction(target="x", target_type="path", family="f",
                          classification="C", result="planned",
                          bytes_reclaimed=1, reason="r", details={}),
            CleanupAction(target="y", target_type="path", family="f",
                          classification="C", result="kept",
                          bytes_reclaimed=1, reason="r", details={}),
        ]
        self.assertFalse(_actions_caused_state_change(actions))

    def test_actions_caused_state_change_false_when_all_blocked_failed(self) -> None:
        actions = [
            CleanupAction(target="a", target_type="path", family="f",
                          classification="C", result="blocked",
                          bytes_reclaimed=1, reason="r", details={}),
            CleanupAction(target="b", target_type="path", family="f",
                          classification="C", result="failed",
                          bytes_reclaimed=1, reason="r", details={}),
            CleanupAction(target="c", target_type="path", family="f",
                          classification="C", result="missing",
                          bytes_reclaimed=1, reason="r", details={}),
        ]
        self.assertFalse(_actions_caused_state_change(actions))

    def test_actions_caused_state_change_false_on_empty(self) -> None:
        self.assertFalse(_actions_caused_state_change([]))

    def test_version_flag_matches_package_version(self) -> None:
        parser = build_parser()
        with self.assertRaises(SystemExit) as exc:
            parser.parse_args(["--version"])
        self.assertEqual(exc.exception.code, 0)

    def test_command_clean_writes_latest_summary_artifact(self) -> None:
        snapshot = {
            "run_id": "snap123",
            "started_at": "2026-04-04T00:00:00Z",
            "finished_at": "2026-04-04T00:00:01Z",
            "mode": "balanced",
            "host_disk_total_bytes": 100,
            "host_disk_used_bytes": 80,
            "host_disk_free_bytes": 20,
            "processes": [],
            "process_summary": {
                "docker": {"state": "inactive", "recommended_action": "protect_only", "process_counts": {"stale": 0}},
                "claude": {"state": "inactive", "recommended_action": "protect_only", "process_counts": {"stale": 0}},
                "codex": {"state": "inactive", "recommended_action": "protect_only", "process_counts": {"stale": 0}},
            },
            "storage_records": [],
            "detector_findings": [],
            "project_signals": [],
            "project_summary": {"active_project_count": 0, "toolchain_counts": {}},
            "protected_items": [],
            "manual_review_items": [],
            "docker_inventory": {},
        }
        report = {
            "run_id": "run123",
            "started_at": "2026-04-04T00:00:00Z",
            "finished_at": "2026-04-04T00:00:02Z",
            "mode": "balanced",
            "dry_run": True,
            "storage_before_bytes": 80,
            "storage_after_bytes": 80,
            "storage_reclaimed_bytes": 0,
            "memory_before_estimate_mb": 0.0,
            "memory_after_estimate_mb": 0.0,
            "memory_reclaimed_estimate_mb": 0.0,
            "processes_scanned": 0,
            "processes_trimmed": 0,
            "objects_pruned": 0,
            "protected_items": [],
            "manual_review_items": [],
            "family_summaries": {
                "docker": {"state": "inactive", "recommended_action": "protect_only", "process_counts": {"stale": 0}, "inventory_counts": {}, "actions": 0, "bytes_reclaimed": 0, "results": {}},
                "claude": {"state": "inactive", "recommended_action": "protect_only", "process_counts": {"stale": 0}, "inventory_counts": {}, "actions": 0, "bytes_reclaimed": 0, "results": {}},
                "codex": {"state": "inactive", "recommended_action": "protect_only", "process_counts": {"stale": 0}, "inventory_counts": {}, "actions": 0, "bytes_reclaimed": 0, "results": {}},
                "system": {"state": "n/a", "recommended_action": "protect_only", "process_counts": {}, "inventory_counts": {}, "actions": 0, "bytes_reclaimed": 0, "results": {}},
            },
            "actions": [],
            "snapshot": snapshot,
        }

        class StubReport:
            def __init__(self, payload: dict[str, object]) -> None:
                self.run_id = str(payload["run_id"])
                self._payload = payload

            def to_dict(self) -> dict[str, object]:
                return self._payload

        args = Namespace(
            mode="balanced",
            apply=False,
            output_dir=None,
            json_out=None,
            html_out=None,
            retention_count=21,
            open=False,
            scope="all",
        )
        with TemporaryDirectory() as tmpdir:
            args.output_dir = tmpdir
            with patch("dreamcleanr.cli.capture_snapshot", side_effect=[snapshot, snapshot]), patch(
                "dreamcleanr.cli.plan_cleanup", return_value=[]
            ), patch("dreamcleanr.cli.apply_actions", return_value=[]), patch(
                "dreamcleanr.cli.build_cleanup_report", return_value=StubReport(report)
            ):
                result = command_clean(args)
            self.assertEqual(result, 0)
            latest_summary = Path(tmpdir) / "latest-summary.json"
            self.assertTrue(latest_summary.exists())
            payload = json.loads(latest_summary.read_text(encoding="utf-8"))
            self.assertEqual(payload["summary_version"], 1)
            self.assertEqual(payload["run_id"], "run123")

    def test_command_export_writes_team_artifacts(self) -> None:
        report = {
            "run_id": "team123",
            "finished_at": "2026-04-04T00:00:02Z",
            "mode": "balanced",
            "dry_run": True,
            "storage_reclaimed_bytes": 0,
            "processes_trimmed": 0,
            "objects_pruned": 0,
            "family_summaries": {
                "docker": {"state": "inactive", "recommended_action": "protect_only", "process_counts": {"stale": 0}, "bytes_reclaimed": 0}
            },
            "snapshot": {
                "host_disk_free_bytes": 20,
                "storage_records": [],
                "detector_findings": [],
                "project_summary": {"active_project_count": 0, "toolchain_counts": {}},
                "project_signals": [],
            },
        }
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            input_path = root / "report.json"
            input_path.write_text(json.dumps(report), encoding="utf-8")
            args = Namespace(input=str(input_path), json_out=None, csv_out=None)
            result = command_export(args)
            self.assertEqual(result, 0)
            self.assertTrue((root / "report-team-export.json").exists())
            self.assertTrue((root / "report-team-export.csv").exists())


    def test_clean_apply_noninteractive_proceeds_without_prompt(self) -> None:
        # Scripted / scheduled runs (no TTY) apply without prompting — this is
        # what keeps an already-installed LaunchAgent working after upgrade.
        apply_mock = MagicMock(return_value=[])
        confirm_mock = MagicMock(return_value=True)
        with TemporaryDirectory() as tmpdir:
            args = _apply_args(tmpdir, yes=False)
            with patch("dreamcleanr.cli.capture_snapshot", return_value={}), patch(
                "dreamcleanr.cli.plan_cleanup", return_value=[_deletion_action()]
            ), patch("dreamcleanr.cli.apply_actions", apply_mock), patch(
                "dreamcleanr.cli.build_cleanup_report", return_value=_StubReport()
            ), patch("dreamcleanr.cli.build_receipt_summary", return_value={}), patch(
                "dreamcleanr.cli.write_html"
            ), patch("dreamcleanr.cli._confirm_apply", confirm_mock), patch(
                "sys.stdin.isatty", return_value=False
            ):
                result = command_clean(args)
        self.assertEqual(result, 0)
        confirm_mock.assert_not_called()
        self.assertFalse(apply_mock.call_args.kwargs["dry_run"])

    def test_clean_apply_with_yes_skips_confirmation(self) -> None:
        apply_mock = MagicMock(return_value=[])
        confirm_mock = MagicMock(return_value=True)
        with TemporaryDirectory() as tmpdir:
            args = _apply_args(tmpdir, yes=True)
            with patch("dreamcleanr.cli.capture_snapshot", return_value={}), patch(
                "dreamcleanr.cli.plan_cleanup", return_value=[_deletion_action()]
            ), patch("dreamcleanr.cli.apply_actions", apply_mock), patch(
                "dreamcleanr.cli.build_cleanup_report", return_value=_StubReport()
            ), patch("dreamcleanr.cli.build_receipt_summary", return_value={}), patch(
                "dreamcleanr.cli.write_html"
            ), patch("dreamcleanr.cli._confirm_apply", confirm_mock):
                result = command_clean(args)
        self.assertEqual(result, 0)
        confirm_mock.assert_not_called()
        self.assertFalse(apply_mock.call_args.kwargs["dry_run"])

    def test_trash_defaults_on_for_max_off_for_balanced(self) -> None:
        for mode, expected_trash in (("max", True), ("balanced", False)):
            apply_mock = MagicMock(return_value=[])
            with TemporaryDirectory() as tmpdir:
                args = _apply_args(tmpdir, yes=True, mode=mode)
                with patch("dreamcleanr.cli.capture_snapshot", return_value={}), patch(
                    "dreamcleanr.cli.plan_cleanup", return_value=[_deletion_action()]
                ), patch("dreamcleanr.cli.apply_actions", apply_mock), patch(
                    "dreamcleanr.cli.build_cleanup_report", return_value=_StubReport()
                ), patch("dreamcleanr.cli.build_receipt_summary", return_value={}), patch(
                    "dreamcleanr.cli.write_html"
                ), patch("dreamcleanr.cli.check_pro", return_value=True):
                    command_clean(args)
            self.assertEqual(apply_mock.call_args.kwargs["trash"], expected_trash, f"mode={mode}")

    def test_max_mode_downgrades_to_balanced_without_pro(self) -> None:
        apply_mock = MagicMock(return_value=[])
        with TemporaryDirectory() as tmpdir:
            args = _apply_args(tmpdir, yes=True, mode="max")
            with patch("dreamcleanr.cli.capture_snapshot", return_value={}) as snap, patch(
                "dreamcleanr.cli.plan_cleanup", return_value=[_deletion_action()]
            ) as plan, patch("dreamcleanr.cli.apply_actions", apply_mock), patch(
                "dreamcleanr.cli.build_cleanup_report", return_value=_StubReport()
            ), patch("dreamcleanr.cli.build_receipt_summary", return_value={}), patch(
                "dreamcleanr.cli.write_html"
            ), patch("dreamcleanr.cli.check_pro", return_value=False):
                command_clean(args)
        # Free users are silently downgraded: dev-mode is Pro-gated.
        self.assertEqual(args.mode, "balanced")
        self.assertEqual(snap.call_args.kwargs["mode"], "balanced")
        self.assertEqual(plan.call_args.kwargs["mode"], "balanced")
        self.assertFalse(apply_mock.call_args.kwargs["trash"])  # balanced default

    def test_no_trash_flag_overrides_max_default(self) -> None:
        apply_mock = MagicMock(return_value=[])
        with TemporaryDirectory() as tmpdir:
            args = _apply_args(tmpdir, yes=True, mode="max", trash=False)
            with patch("dreamcleanr.cli.capture_snapshot", return_value={}), patch(
                "dreamcleanr.cli.plan_cleanup", return_value=[_deletion_action()]
            ), patch("dreamcleanr.cli.apply_actions", apply_mock), patch(
                "dreamcleanr.cli.build_cleanup_report", return_value=_StubReport()
            ), patch("dreamcleanr.cli.build_receipt_summary", return_value={}), patch(
                "dreamcleanr.cli.write_html"
            ), patch("dreamcleanr.cli.check_pro", return_value=True):
                command_clean(args)
        self.assertFalse(apply_mock.call_args.kwargs["trash"])

    def test_clean_apply_skipped_when_report_dir_locked(self) -> None:
        import fcntl

        apply_mock = MagicMock(return_value=[])
        with TemporaryDirectory() as tmpdir:
            holder = open(Path(tmpdir) / ".dreamcleanr.lock", "w")
            fcntl.flock(holder.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            try:
                args = _apply_args(tmpdir, yes=True)
                with patch("dreamcleanr.cli.capture_snapshot", return_value={}), patch(
                    "dreamcleanr.cli.plan_cleanup", return_value=[_deletion_action()]
                ), patch("dreamcleanr.cli.apply_actions", apply_mock):
                    result = command_clean(args)
            finally:
                holder.close()
        self.assertEqual(result, 0)
        apply_mock.assert_not_called()

    def test_clean_apply_decline_falls_back_to_preview(self) -> None:
        apply_mock = MagicMock(return_value=[])
        with TemporaryDirectory() as tmpdir:
            args = _apply_args(tmpdir, yes=False)
            with patch("dreamcleanr.cli.capture_snapshot", return_value={}), patch(
                "dreamcleanr.cli.plan_cleanup", return_value=[_deletion_action()]
            ), patch("dreamcleanr.cli.apply_actions", apply_mock), patch(
                "dreamcleanr.cli.build_cleanup_report", return_value=_StubReport()
            ), patch("dreamcleanr.cli.build_receipt_summary", return_value={}), patch(
                "dreamcleanr.cli.write_html"
            ), patch("sys.stdin.isatty", return_value=True), patch(
                "dreamcleanr.cli._confirm_apply", return_value=False
            ):
                result = command_clean(args)
        self.assertEqual(result, 0)
        self.assertTrue(apply_mock.call_args.kwargs["dry_run"])


if __name__ == "__main__":
    unittest.main()
