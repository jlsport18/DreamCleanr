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

    def test_cleanup_report_to_dict_covers_every_field(self) -> None:
        # to_dict is hand-maintained; guard against adding a field and silently
        # dropping it from receipts/exports.
        from dataclasses import fields

        from dreamcleanr.models import CleanupReport

        report = CleanupReport(
            run_id="r", started_at="", finished_at="", mode="balanced", dry_run=True,
            storage_before_bytes=0, storage_after_bytes=0, storage_reclaimed_bytes=0,
            memory_before_estimate_mb=0.0, memory_after_estimate_mb=0.0, memory_reclaimed_estimate_mb=0.0,
            processes_scanned=0, processes_trimmed=0, objects_pruned=0,
            protected_items=[], manual_review_items=[], family_summaries={}, actions=[], snapshot={},
        )
        self.assertEqual(set(report.to_dict().keys()), {f.name for f in fields(CleanupReport)})


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


class SigningMaterialExclusionTests(unittest.TestCase):
    """The shipped package (packages=["dreamcleanr"]) must contain ONLY the public
    verifier — never a private seed or the issuance tool."""

    PKG = ROOT / "dreamcleanr"

    def test_issuance_tool_lives_outside_the_package(self) -> None:
        self.assertTrue((ROOT / "scripts" / "issue_license.py").exists())
        self.assertFalse((self.PKG / "issue_license.py").exists())

    def test_no_private_seed_hex_embedded_in_package(self) -> None:
        # A 32-byte Ed25519 seed serialises to a 64-char hex run. Guard against one
        # ever being pasted into a shipped module.
        seed_like = re.compile(r"(?<![0-9a-fA-F])[0-9a-fA-F]{64}(?![0-9a-fA-F])")
        offenders = []
        for path in self.PKG.rglob("*.py"):
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if seed_like.search(line):
                    offenders.append(f"{path.name}:{lineno}")
        self.assertEqual(offenders, [], f"possible private key material in wheel: {offenders}")

    def test_client_verifies_without_signing_secret(self) -> None:
        import os

        from dreamcleanr import license as lic

        saved = os.environ.pop("SWEEP_SIGNING_KEY", None)
        try:
            self.assertEqual(len(lic._PUBLIC_KEY), 32)
            # Verification needs no secret...
            self.assertFalse(lic._verify_key("SWEEP-BOGUS", "a@b.com"))
            # ...but minting must be impossible on a client with no seed.
            with self.assertRaises(RuntimeError):
                lic.generate_key("a@b.com")
        finally:
            if saved is not None:
                os.environ["SWEEP_SIGNING_KEY"] = saved


if __name__ == "__main__":
    unittest.main()
