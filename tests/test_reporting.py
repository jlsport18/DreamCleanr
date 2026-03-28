from __future__ import annotations

import unittest

from dreamcleanr.reporting import render_html


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
                }
            ],
            "protected_items": [{"label": "claude_vm_bundle"}],
            "manual_review_items": [{"label": "docker_raw"}],
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
            },
        }
        html = render_html(report)
        self.assertIn("DreamCleanr", html)
        self.assertIn("Biggest Wins", html)
        self.assertIn("Left Alone On Purpose", html)
        self.assertIn("Why It Was Safe", html)


if __name__ == "__main__":
    unittest.main()
