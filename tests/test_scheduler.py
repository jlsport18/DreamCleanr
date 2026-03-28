from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from dreamcleanr.scheduler import write_launch_agent


class SchedulerTests(unittest.TestCase):
    def test_write_launch_agent_includes_retention_count(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            plist_path = root / "io.dreamcleanr.cleanup.plist"
            with patch("dreamcleanr.scheduler.launch_agent_path", return_value=plist_path):
                written = write_launch_agent(
                    repo_root=root,
                    output_dir=root / "reports",
                    hour=4,
                    minute=30,
                    mode="balanced",
                    retention_count=14,
                )
            content = written.read_text(encoding="utf-8")
            self.assertIn("--retention-count", content)
            self.assertIn("<string>14</string>", content)


if __name__ == "__main__":
    unittest.main()
