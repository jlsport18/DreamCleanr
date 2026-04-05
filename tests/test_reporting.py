from __future__ import annotations

import unittest

from pathlib import Path
from tempfile import TemporaryDirectory

from dreamcleanr.reporting import build_receipt_summary, build_team_export, render_html, write_team_csv


class ReportingTests(unittest.TestCase):
    def test_render_html_contains_key_sections(self) -> None:
        report = {
            "finished_at": "2026-03-28T05:00:00Z",
            "mode": "balanced",
            "dry_run": True,
            "storage_reclaimed_bytes": 5 * 1024 ** 3,
            "storage_before_bytes": 100 * 1024 ** 3,
            "storage_after_bytes": 100 * 1024 ** 3,
            "actions": [
                {
                    "target": "/Users/test/.cache/uv",
                    "result": "planned",
                    "bytes_reclaimed": 1234,
                    "family": "system",
                }
            ],
            "protected_items": [{"label": "claude_vm_bundle"}],
            "manual_review_items": [{"label": "docker_raw"}],
            "family_summaries": {
                "docker": {
                    "state": "active",
                    "recommended_action": "docker_system_prune",
                    "process_counts": {"stale": 2},
                    "inventory_counts": {"running_containers": 1, "exited_containers": 3},
                },
                "claude": {
                    "state": "active",
                    "recommended_action": "protect_only",
                    "process_counts": {"stale": 0},
                    "inventory_counts": {},
                },
                "codex": {
                    "state": "active",
                    "recommended_action": "protect_only",
                    "process_counts": {"stale": 0},
                    "inventory_counts": {},
                },
            },
            "snapshot": {
                "host_disk_total_bytes": 200 * 1024 ** 3,
                "host_disk_free_bytes": 20 * 1024 ** 3,
                "storage_records": [
                    {
                        "label": "docker_vm_data",
                        "classification": "REVIEW_VM",
                        "size_bytes": 10 * 1024 ** 3,
                    }
                ],
                "process_summary": {
                    "docker": {"state": "active", "recommended_action": "docker_system_prune"},
                    "claude": {"state": "active", "recommended_action": "protect_only"},
                    "codex": {"state": "active", "recommended_action": "protect_only"},
                },
                "detector_findings": [
                    {
                        "key": "python",
                        "title": "Python environments and caches",
                        "status": "observed",
                        "total_bytes": 4 * 1024 ** 3,
                        "path_count": 2,
                        "cleanup_ready": False,
                        "notes": "Visibility only for pip, pyenv, conda, and virtualenv roots.",
                        "safety_state": "guarded_by_active_projects",
                        "active_project_count": 1,
                    }
                ],
                "project_signals": [
                    {
                        "root": "/Users/test/Projects/sample-app",
                        "toolchains": ["git", "python", "ide"],
                        "markers": ["pyproject.toml", ".vscode"],
                        "source_process_count": 2,
                        "families": ["other"],
                    }
                ],
            },
        }
        html = render_html(report)
        self.assertIn("DreamCleanr", html)
        self.assertIn("Family Status", html)
        self.assertIn("Observed Developer Surfaces", html)
        self.assertIn("guarded by active projects", html)
        self.assertIn("Active Project Signals", html)
        self.assertIn("Removed Or Planned", html)
        self.assertIn("Protected", html)
        self.assertIn("Manual Review", html)
        self.assertIn("Why It Was Safe", html)

    def test_build_receipt_summary_extracts_shell_ready_fields(self) -> None:
        report = {
            "run_id": "abc123",
            "finished_at": "2026-03-28T05:00:00Z",
            "mode": "balanced",
            "dry_run": True,
            "storage_reclaimed_bytes": 1024,
            "processes_trimmed": 2,
            "objects_pruned": 3,
            "family_summaries": {
                "docker": {
                    "state": "active",
                    "recommended_action": "docker_system_prune",
                    "process_counts": {"stale": 1},
                    "bytes_reclaimed": 512,
                }
            },
            "snapshot": {
                "host_disk_free_bytes": 2048,
                "storage_records": [
                    {"label": "uv_cache", "family": "system", "classification": "SAFE_CACHE", "size_bytes": 4096}
                ],
                "detector_findings": [
                    {
                        "key": "python",
                        "title": "Python environments and caches",
                        "total_bytes": 8192,
                        "path_count": 2,
                        "safety_state": "guarded_by_active_projects",
                        "active_project_count": 1,
                    }
                ],
                "project_summary": {"active_project_count": 1, "toolchain_counts": {"python": 1}},
                "project_signals": [
                    {
                        "root": "/Users/test/Projects/sample-app",
                        "toolchains": ["git", "python"],
                        "markers": ["pyproject.toml"],
                        "source_process_count": 1,
                        "families": ["other"],
                    }
                ],
            },
        }
        summary = build_receipt_summary(report)
        self.assertEqual(summary["summary_version"], 1)
        self.assertEqual(summary["run_id"], "abc123")
        self.assertEqual(summary["family_overview"]["docker"]["stale"], 1)
        self.assertEqual(summary["detector_overview"][0]["safety_state"], "guarded_by_active_projects")
        self.assertEqual(summary["project_summary"]["active_project_count"], 1)
        self.assertEqual(summary["top_storage_targets"][0]["label"], "uv_cache")

    def test_build_team_export_and_csv(self) -> None:
        report = {
            "run_id": "team123",
            "finished_at": "2026-03-28T05:00:00Z",
            "mode": "balanced",
            "dry_run": True,
            "storage_reclaimed_bytes": 1024,
            "processes_trimmed": 0,
            "objects_pruned": 0,
            "family_summaries": {
                "docker": {
                    "state": "active",
                    "recommended_action": "docker_system_prune",
                    "process_counts": {"stale": 1},
                    "bytes_reclaimed": 512,
                }
            },
            "snapshot": {
                "host_disk_free_bytes": 2048,
                "storage_records": [{"label": "uv_cache", "family": "system", "classification": "SAFE_CACHE", "size_bytes": 4096}],
                "detector_findings": [
                    {
                        "key": "python",
                        "title": "Python environments and caches",
                        "total_bytes": 8192,
                        "path_count": 2,
                        "safety_state": "guarded_by_active_projects",
                        "active_project_count": 1,
                    }
                ],
                "project_summary": {"active_project_count": 1, "toolchain_counts": {"python": 1}},
                "project_signals": [],
            },
        }
        export = build_team_export(report)
        self.assertEqual(export["export_version"], 1)
        self.assertEqual(export["policy_flags"]["detectors_guarded_by_projects"], ["python"])
        with TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "team.csv"
            write_team_csv(export, output)
            content = output.read_text(encoding="utf-8")
        self.assertIn("section,key,label,value,notes", content)
        self.assertIn("detector,python,Python environments and caches,8192,guarded_by_active_projects", content)


if __name__ == "__main__":
    unittest.main()
