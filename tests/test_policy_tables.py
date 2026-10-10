"""Pin the data-driven tables in core.py and the family action-policy matrix.

These tests exist because an earlier refactor sweep (PR #48) hoisted static
family policies into a dict but left the lookup *after* the catch-all
``elif family == "docker"`` branch, silently changing docker
``residual_data_only`` from ``confirm_raw_vm_delete`` to ``protect_only`` while
the full suite stayed green. The matrix below makes that class of
branch-ordering regression fail loudly.
"""
from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from dreamcleanr import core
from dreamcleanr.core import plan_cleanup, summarize_family
from dreamcleanr.models import ProcessRecord


def _proc(pid: int, family: str, role: str) -> ProcessRecord:
    return ProcessRecord(
        pid=pid, ppid=1, etime="1:00", elapsed_seconds=60, cpu_percent=0.0,
        mem_percent=0.0, rss_kb=1, command="x", args="x", family=family, role=role,
    )


# (family, process scenario, protected paths exist) ->
#     (state, recommended_action, allowed_actions, blocked_actions)
# Captured from origin/main @ 9d78aeb; any change here is a behaviour change.
_POLICY_MATRIX = {
    ("docker", "none", False): ("inactive", "protect_only", [], ["raw_vm_delete"]),
    ("docker", "none", True): ("residual_data_only", "confirm_raw_vm_delete", ["confirm_raw_vm_delete"], []),
    ("docker", "weak", False): ("cli_only", "protect_only", [], ["raw_vm_delete"]),
    ("docker", "weak", True): ("cli_only", "protect_only", [], ["raw_vm_delete"]),
    ("docker", "primary", False): ("active", "protect_only", ["docker_system_prune"], ["raw_vm_delete"]),
    ("docker", "primary", True): ("active", "protect_only", ["docker_system_prune"], ["raw_vm_delete"]),
    ("claude", "none", False): ("inactive", "prune_cache", ["prune_cache"], []),
    ("claude", "none", True): ("residual_data_only", "prune_cache", ["prune_cache", "prune_vm"], []),
    ("claude", "weak", False): ("background_only", "protect_only", [], []),
    ("claude", "weak", True): ("background_only", "protect_only", [], []),
    ("claude", "primary", False): ("active", "protect_only", [], ["prune_cache", "prune_vm"]),
    ("claude", "primary", True): ("active", "protect_only", [], ["prune_cache", "prune_vm"]),
    ("codex", "none", False): ("inactive", "protect_only", [], []),
    ("codex", "none", True): ("residual_data_only", "protect_only", [], []),
    ("codex", "weak", False): ("background_only", "protect_only", [], ["prune_cache", "prune_support_root"]),
    ("codex", "weak", True): ("background_only", "protect_only", [], ["prune_cache", "prune_support_root"]),
    ("codex", "primary", False): ("active", "protect_only", [], ["prune_cache", "prune_support_root"]),
    ("codex", "primary", True): ("active", "protect_only", [], ["prune_cache", "prune_support_root"]),
}


class PolicyTableTests(unittest.TestCase):
    def test_standard_tier_keys_exist_in_safe_cache_paths(self) -> None:
        for key, reason in core._STANDARD_TIER_CACHES:
            self.assertIn(key, core.SAFE_CACHE_PATHS)
            self.assertTrue(reason)

    def test_protected_state_record_keys_exist_in_protected_state_paths(self) -> None:
        for key, family, classification, notes in core._PROTECTED_STATE_RECORDS:
            self.assertIn(key, core.PROTECTED_STATE_PATHS)
            self.assertIn(classification, {"REVIEW_VM", "PROTECTED_STATE"})
            self.assertTrue(notes)

    def test_plan_cleanup_emits_every_standard_tier_cache_in_order(self) -> None:
        snapshot = {
            "processes": [],
            "process_summary": {
                fam: {"state": "inactive", "recommended_action": "protect_only"}
                for fam in ("docker", "claude", "codex")
            },
        }
        with TemporaryDirectory() as tmp:
            fake = {k: Path(tmp) / k for k in core.SAFE_CACHE_PATHS}
            for path in fake.values():
                path.mkdir()
            with patch.dict(core.SAFE_CACHE_PATHS, fake), patch("dreamcleanr.core.du_bytes", return_value=1):
                actions = plan_cleanup(snapshot, mode="balanced")
        labels = [a.details.get("label") for a in actions]
        expected = [key for key, _ in core._STANDARD_TIER_CACHES]
        self.assertEqual([label for label in labels if label in expected], expected)

    def test_family_policy_matrix_is_unchanged(self) -> None:
        with TemporaryDirectory() as tmp:
            present = {k: Path(tmp) / "present" / k for k in core.PROTECTED_STATE_PATHS}
            absent = {k: Path(tmp) / "absent" / k for k in core.PROTECTED_STATE_PATHS}
            for path in present.values():
                path.mkdir(parents=True)
            for (family, scenario, paths_exist), expected in _POLICY_MATRIX.items():
                role_table = {"primary": core._PRIMARY_ROLES, "weak": core._WEAK_ROLES}.get(scenario)
                procs = [] if role_table is None else [_proc(10, family, sorted(role_table[family])[0])]
                with self.subTest(family=family, scenario=scenario, paths_exist=paths_exist):
                    with patch.dict(core.PROTECTED_STATE_PATHS, present if paths_exist else absent):
                        summary = summarize_family(family, procs, {p.pid: p for p in procs}, {99999})
                    self.assertEqual(
                        (summary["state"], summary["recommended_action"],
                         summary["allowed_actions"], summary["blocked_actions"]),
                        expected,
                    )


if __name__ == "__main__":
    unittest.main()
