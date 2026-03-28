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
        structured = response["result"]["structuredContent"]
        self.assertEqual(structured["summary"]["docker"]["state"], "active")
        self.assertEqual(structured["summary"]["docker"]["stale"], 1)

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
