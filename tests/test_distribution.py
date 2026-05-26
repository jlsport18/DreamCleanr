from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

import dreamcleanr


ROOT = Path(__file__).resolve().parents[1]


class VersionConsistencyTests(unittest.TestCase):
    def test_package_version_matches_pyproject(self) -> None:
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        match = re.search(r'(?m)^version = "([^"]+)"', pyproject)
        self.assertIsNotNone(match, "could not find version in pyproject.toml")
        assert match is not None  # narrow type for readers/type-checkers
        self.assertEqual(
            dreamcleanr.__version__,
            match.group(1),
            "dreamcleanr.__version__ must match pyproject.toml version so installed "
            "artifacts do not self-report a stale version (regression guard for the "
            "0.3.5 release that shipped __version__='0.3.4').",
        )

    def test_cleanup_report_stamps_tool_version(self) -> None:
        # Receipts must record which build produced them, so a support ticket
        # carrying a report JSON is traceable to a version.
        from dataclasses import fields

        from dreamcleanr.models import CleanupReport

        defaults = {f.name: f.default for f in fields(CleanupReport)}
        self.assertEqual(defaults["tool_version"], dreamcleanr.__version__)


class DistributionSurfaceTests(unittest.TestCase):
    def test_mcp_integration_configs_use_local_server_entrypoint(self) -> None:
        claude = json.loads((ROOT / "integrations" / "claude-mcp.json").read_text(encoding="utf-8"))
        vscode = json.loads((ROOT / "integrations" / "vscode-mcp.json").read_text(encoding="utf-8"))
        codex = (ROOT / "integrations" / "codex-mcp.toml").read_text(encoding="utf-8")

        self.assertEqual(claude["mcpServers"]["dreamcleanr"]["command"], "python3")
        self.assertEqual(claude["mcpServers"]["dreamcleanr"]["args"], ["-m", "dreamcleanr.mcp_server"])
        self.assertEqual(vscode["servers"]["dreamcleanr"]["command"], "python3")
        self.assertEqual(vscode["servers"]["dreamcleanr"]["args"], ["-m", "dreamcleanr.mcp_server"])
        self.assertIn('[mcp_servers.dreamcleanr]', codex)
        self.assertIn('command = "python3"', codex)
        self.assertIn('args = ["-m", "dreamcleanr.mcp_server"]', codex)

    def test_search_and_distribution_pages_are_indexed(self) -> None:
        sitemap = (ROOT / "site" / "sitemap.xml").read_text(encoding="utf-8")
        self.assertIn("/mcp-setup.html", sitemap)
        self.assertIn("/faq.html", sitemap)
        self.assertIn("/compare-cleanmymac.html", sitemap)

    def test_new_public_pages_stay_grounded(self) -> None:
        mcp_setup = (ROOT / "site" / "mcp-setup.html").read_text(encoding="utf-8")
        faq = (ROOT / "site" / "faq.html").read_text(encoding="utf-8")
        comparison = (ROOT / "site" / "compare-cleanmymac.html").read_text(encoding="utf-8")

        self.assertIn("dreamcleanr.mcp_server", mcp_setup)
        self.assertIn("DreamCleanr FAQ", faq)
        self.assertIn("coming next", faq.lower())
        self.assertIn("DreamCleanr vs CleanMyMac", comparison)
        self.assertIn("one-time", comparison.lower())
        self.assertNotIn("$19/month", comparison)


if __name__ == "__main__":
    unittest.main()
