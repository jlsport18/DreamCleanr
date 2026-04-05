from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from dreamcleanr.mcp_server import handle_request


class McpServerTests(unittest.TestCase):
    def test_initialize_reports_server_info(self) -> None:
        response = handle_request(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {"protocolVersion": "2025-06-18"},
            }
        )
        assert response is not None
        self.assertEqual(response["result"]["protocolVersion"], "2025-06-18")
        self.assertEqual(response["result"]["serverInfo"]["name"], "dreamcleanr")

    def test_tools_list_contains_preview_tools(self) -> None:
        response = handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        assert response is not None
        tools = {tool["name"] for tool in response["result"]["tools"]}
        self.assertIn("scan", tools)
        self.assertIn("clean_preview", tools)
        self.assertIn("report_render", tools)
        self.assertIn("schedule_status", tools)
        self.assertIn("schedule_preview", tools)

    def test_scan_tool_returns_summary(self) -> None:
        snapshot = {
            "host_disk_free_bytes": 1234,
            "process_summary": {
                "docker": {"state": "active", "recommended_action": "docker_system_prune", "process_counts": {"stale": 1}},
                "claude": {"state": "active", "recommended_action": "protect_only", "process_counts": {"stale": 0}},
                "codex": {"state": "background_only", "recommended_action": "protect_only", "process_counts": {"stale": 0}},
            },
            "detector_findings": [
                {
                    "key": "python",
                    "title": "Python environments and caches",
                    "status": "observed",
                    "total_bytes": 4 * 1024 ** 3,
                    "path_count": 2,
                    "cleanup_ready": False,
                    "safety_state": "guarded_by_active_projects",
                    "active_project_count": 1,
                }
            ],
            "project_signals": [
                {
                    "root": "/Users/test/Projects/sample-app",
                    "toolchains": ["git", "python"],
                    "markers": ["pyproject.toml"],
                    "source_process_count": 1,
                    "families": ["other"],
                }
            ],
            "project_summary": {"active_project_count": 1, "toolchain_counts": {"git": 1, "python": 1}},
        }
        with patch("dreamcleanr.mcp_server.capture_snapshot", return_value=snapshot):
            response = handle_request(
                {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {"name": "scan", "arguments": {"mode": "balanced"}},
                }
            )
        assert response is not None
        text = response["result"]["content"][0]["text"]
        structured = response["result"]["structuredContent"]
        self.assertIn("Observed additional developer surfaces", text)
        self.assertIn("Active project signals: 1", text)
        self.assertEqual(structured["summary"]["docker"]["state"], "active")
        self.assertEqual(structured["summary"]["docker"]["stale"], 1)
        self.assertEqual(structured["detectors"]["python"]["status"], "observed")
        self.assertEqual(structured["detectors"]["python"]["safety_state"], "guarded_by_active_projects")
        self.assertEqual(structured["projects"]["summary"]["active_project_count"], 1)

    def test_report_render_writes_html(self) -> None:
        report = {
            "finished_at": "2026-03-28T10:00:00Z",
            "mode": "balanced",
            "dry_run": True,
            "storage_before_bytes": 100,
            "storage_after_bytes": 100,
            "storage_reclaimed_bytes": 0,
            "memory_reclaimed_estimate_mb": 0.0,
            "processes_trimmed": 0,
            "protected_items": [],
            "manual_review_items": [],
            "family_summaries": {},
            "snapshot": {
                "host_disk_free_bytes": 100,
                "host_disk_total_bytes": 200,
                "storage_records": [],
                "process_summary": {},
                "detector_findings": [],
                "project_signals": [],
                "project_summary": {"active_project_count": 0, "toolchain_counts": {}},
            },
            "actions": [],
        }
        with TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "report.json"
            html_out = Path(tmpdir) / "report.html"
            input_path.write_text(json.dumps(report), encoding="utf-8")
            response = handle_request(
                {
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "tools/call",
                    "params": {
                        "name": "report_render",
                        "arguments": {"input": str(input_path), "html_out": str(html_out)},
                    },
                }
            )
            assert response is not None
            self.assertTrue(html_out.exists())
            self.assertIn("DreamCleanr", html_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
