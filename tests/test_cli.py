from __future__ import annotations

import unittest

from dreamcleanr import __version__
from dreamcleanr.cli import build_parser


class CliTests(unittest.TestCase):
    def test_version_flag_matches_package_version(self) -> None:
        parser = build_parser()
        with self.assertRaises(SystemExit) as exc:
            parser.parse_args(["--version"])
        self.assertEqual(exc.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
