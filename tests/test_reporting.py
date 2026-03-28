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
            },
        }
        html = render_html(report)
        self.assertIn("DreamCleanr", html)
        self.assertIn("Family Status", html)
        self.assertIn("Removed Or Planned", html)
        self.assertIn("Protected", html)
        self.assertIn("Manual Review", html)
        self.assertIn("Why It Was Safe", html)


if __name__ == "__main__":
    unittest.main()
