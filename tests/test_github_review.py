from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "github_review.py"
SPEC = importlib.util.spec_from_file_location("github_review", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
github_review = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(github_review)


class GithubReviewTests(unittest.TestCase):
    def test_fetch_business_summary_excludes_tracker_threads(self) -> None:
        releases = [
            {
                "tag_name": "v0.3.3",
                "published_at": "2026-04-04T17:00:14Z",
                "assets": [{"name": "dreamcleanr-0.3.3-py3-none-any.whl", "download_count": 9}],
            }
        ]
        issues = [
            {"title": "Package DreamCleanr as a turnkey MCP tool for Claude, Codex, and VS Code", "labels": [{"name": "distribution"}]},
            {"title": "Define DreamCleanr pricing, packaging, and conversion experiments", "labels": [{"name": "monetization"}]},
            {"title": "DreamCleanr Governance Review Tracker", "labels": [{"name": "maintenance"}, {"name": "governance"}, {"name": "tracker"}]},
            {"title": "DreamCleanr Business And Architecture Review", "labels": [{"name": "monetization"}, {"name": "tracker"}]},
        ]

        with patch.object(github_review, "api_request", side_effect=[releases, issues]):
            summary = github_review.fetch_business_summary("jlsport18/DreamCleanr")

        self.assertEqual(summary["total_downloads"], 9)
        self.assertEqual(summary["install_friction"]["count"], 1)
        self.assertEqual(summary["install_friction"]["titles"], ["Package DreamCleanr as a turnkey MCP tool for Claude, Codex, and VS Code"])
        self.assertEqual(summary["monetization_queue"]["count"], 1)
        self.assertEqual(summary["monetization_queue"]["titles"], ["Define DreamCleanr pricing, packaging, and conversion experiments"])
        self.assertEqual(summary["trackers"]["count"], 2)

    def test_render_business_markdown_reports_tracker_threads(self) -> None:
        summary = {
            "generated_at": "2026-04-05T00:00:00+00:00",
            "total_downloads": 66,
            "release_downloads": [{"tag": "v0.3.3", "asset_downloads": 9, "published_at": "2026-04-04T17:00:14Z"}],
            "trackers": {"count": 2, "titles": ["DreamCleanr Governance Review Tracker", "DreamCleanr Business And Architecture Review"]},
            "install_friction": {"count": 1, "titles": ["Package DreamCleanr as a turnkey MCP tool for Claude, Codex, and VS Code"]},
            "monetization_queue": {"count": 1, "titles": ["Define DreamCleanr pricing, packaging, and conversion experiments"]},
            "monetization_readiness": {
                "green_install_channel": True,
                "open_distribution_issues": 1,
                "open_monetization_issues": 1,
            },
        }

        markdown = github_review.render_business_markdown(summary)

        self.assertIn("Recurring tracker threads excluded", markdown)
        self.assertIn("## Tracker Threads", markdown)
        self.assertIn("DreamCleanr Governance Review Tracker", markdown)


if __name__ == "__main__":
    unittest.main()
