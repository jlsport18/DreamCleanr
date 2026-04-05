from __future__ import annotations

import json
import unittest
from argparse import Namespace
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from dreamcleanr import __version__
from dreamcleanr.cli import build_parser, command_clean, command_export


class CliTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
