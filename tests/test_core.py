from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from dreamcleanr.core import (
    apply_actions,
    annotate_detector_findings,
    classify_process_role,
    classify_processes,
    gather_detector_findings,
    gather_project_signals,
    parse_elapsed_to_seconds,
    parse_size_to_bytes,
    plan_cleanup,
    prune_history_files,
    summarize_family,
)
from dreamcleanr.models import CleanupAction, DockerInventory, ProcessRecord


def proc(pid: int, ppid: int, etime: str, cpu: float, rss: int, command: str, args: str) -> ProcessRecord:
    record = ProcessRecord(
        pid=pid,
        ppid=ppid,
        etime=etime,
        elapsed_seconds=parse_elapsed_to_seconds(etime),
        cpu_percent=cpu,
        mem_percent=0.1,
        rss_kb=rss,
        command=command,
        args=args,
    )
    classify_process_role(record)
    return record


class CoreTests(unittest.TestCase):
    def test_parse_elapsed(self) -> None:
        self.assertEqual(parse_elapsed_to_seconds("05:10"), 310)
        self.assertEqual(parse_elapsed_to_seconds("1:05:10"), 3910)
        self.assertEqual(parse_elapsed_to_seconds("2-01:00:00"), 176400)

    def test_parse_size_to_bytes_handles_multichar_units(self) -> None:
        self.assertEqual(parse_size_to_bytes("40 GB"), 40 * 1024 ** 3)
        self.assertEqual(parse_size_to_bytes("5.5GB"), int(5.5 * 1024 ** 3))
        self.assertEqual(parse_size_to_bytes("512MB"), 512 * 1024 ** 2)
        self.assertEqual(parse_size_to_bytes("100B"), 100)

    def test_docker_active_backend_vs_stale_probe(self) -> None:
        processes = [
            proc(57788, 1, "06:00:00", 0.0, 1200, "/Applications/Do", "/Applications/Docker.app/Contents/MacOS/com.docker.backend"),
            proc(57859, 57788, "06:00:00", 0.0, 900, "/Applications/Do", "/Applications/Docker.app/Contents/MacOS/com.docker.virtualization --disk /Users/test/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw"),
            proc(36402, 1240, "01:05:25", 0.0, 200, "/bin/zsh", "/bin/zsh -c docker system df 2>/dev/null || true"),
            proc(36640, 36402, "01:05:11", 0.0, 180, "docker", "docker info"),
        ]
        by_pid = {p.pid: p for p in processes}
        with patch("dreamcleanr.core.run_command", return_value={"ok": True, "timed_out": False, "returncode": 0, "stdout": "{}", "stderr": ""}):
            summary = {"docker": summarize_family("docker", processes, by_pid, {99999})}
        self.assertEqual(summary["docker"]["state"], "active")
        self.assertIn("docker_system_prune", summary["docker"]["allowed_actions"])
        self.assertIn("raw_vm_delete", summary["docker"]["blocked_actions"])
        classify_processes(processes, summary)
        by_pid = {p.pid: p for p in processes}
        self.assertEqual(by_pid[57788].classification, "ACTIVE_PRIMARY")
        self.assertEqual(by_pid[57859].classification, "ACTIVE_PRIMARY")
        self.assertEqual(by_pid[36402].classification, "STALE_CLI")
        self.assertEqual(by_pid[36640].classification, "STALE_CLI")

    def test_codex_updater_only_is_background(self) -> None:
        processes = [
            proc(1232, 1, "00:20:00", 0.0, 80, "/Applications/Co", "/Applications/Codex.app/Contents/Frameworks/Sparkle.framework/Versions/B/Autoupdate com.openai.codex /Users/test"),
        ]
        by_pid = {p.pid: p for p in processes}
        summary = {"codex": summarize_family("codex", processes, by_pid, {99999})}
        self.assertEqual(summary["codex"]["state"], "background_only")
        classify_processes(processes, summary)
        self.assertEqual(processes[0].classification, "BACKGROUND_ONLY")

    def test_claude_vscode_cli_is_active(self) -> None:
        processes = [
            proc(
                3039,
                1187,
                "00:10:00",
                0.0,
                1200,
                "/Users/test",
                "/Users/test/.vscode/extensions/anthropic.claude-code-2.1.85-darwin-arm64/resources/native-binary/claude --output-format stream-json --mcp-config {}",
            )
        ]
        by_pid = {p.pid: p for p in processes}
        summary = {"claude": summarize_family("claude", processes, by_pid, {99999})}
        self.assertEqual(summary["claude"]["state"], "active")
        self.assertIn("prune_vm", summary["claude"]["blocked_actions"])

    def test_docker_probe_and_interactive_cli_are_separated(self) -> None:
        probe = proc(36640, 36402, "01:05:11", 0.0, 180, "docker", "docker info")
        interactive = proc(36641, 36402, "00:01:20", 0.1, 180, "docker", "docker run alpine sh")
        self.assertEqual(probe.role, "docker_cli_probe")
        self.assertEqual(interactive.role, "docker_cli")

    def test_codex_crashpad_without_active_root_is_background_only(self) -> None:
        processes = [
            proc(
                2234,
                1,
                "00:40:00",
                0.0,
                96,
                "/Applications/Co",
                "/Applications/Codex.app/Contents/Frameworks/Codex Helper.app/Contents/MacOS/crashpad_handler --database=/Users/test/Library/Application Support/Codex/Crashpad",
            )
        ]
        by_pid = {p.pid: p for p in processes}
        summary = {"codex": summarize_family("codex", processes, by_pid, {99999})}
        classify_processes(processes, summary)
        self.assertEqual(processes[0].classification, "BACKGROUND_ONLY")

    def test_docker_engine_inventory_promotes_active_state_without_primary_process_match(self) -> None:
        inventory = DockerInventory(
            engine_available=True,
            engine_state="reachable",
            reclaimable_summary={"running_containers": 1, "exited_containers": 2, "dangling_images": 0, "volumes": 1, "networks": 1},
        )
        summary = summarize_family("docker", [], {}, {99999}, docker_inventory=inventory)
        self.assertEqual(summary["state"], "active")
        self.assertEqual(summary["recommended_action"], "docker_system_prune")

    def test_safe_mode_preview_actions_do_not_apply(self) -> None:
        snapshot = {
            "process_summary": {
                "docker": {"recommended_action": "protect_only"},
                "claude": {"recommended_action": "protect_only"},
                "codex": {"recommended_action": "protect_only"},
            },
        }
        actions = [
            CleanupAction(
                target="36640",
                target_type="process",
                family="docker",
                classification="STALE_CLI",
                result="planned",
                bytes_reclaimed=180 * 1024,
                reason="preview only",
                details={"apply_allowed": False},
            )
        ]
        applied = apply_actions(snapshot, actions, dry_run=False)
        self.assertEqual(applied[0].result, "kept")

    def test_gather_detector_findings_reports_observed_roots(self) -> None:
        with TemporaryDirectory() as tmpdir:
            home = Path(tmpdir)
            python_root = home / ".cache" / "pip"
            python_root.mkdir(parents=True)
            ollama_root = home / "Library" / "Application Support" / "Ollama"
            ollama_root.mkdir(parents=True)

            def fake_du(path: Path) -> int:
                if path == ollama_root:
                    return 5 * 1024 ** 3
                if path == python_root:
                    return 2 * 1024 ** 3
                return 0

            with patch("dreamcleanr.core.du_bytes", side_effect=fake_du):
                findings = gather_detector_findings(home=home)

        self.assertEqual([item["key"] for item in findings], ["ollama", "python"])
        self.assertEqual(findings[0]["status"], "observed")
        self.assertFalse(findings[0]["cleanup_ready"])
        self.assertEqual(findings[0]["path_count"], 1)
        self.assertEqual(findings[0]["total_bytes"], 5 * 1024 ** 3)
        self.assertEqual(findings[1]["observed_paths"][0]["path"], str(python_root))

    def test_gather_project_signals_detects_active_repo_markers(self) -> None:
        with TemporaryDirectory() as tmpdir:
            home = Path(tmpdir)
            repo = home / "Projects" / "sample-app"
            repo.mkdir(parents=True)
            (repo / ".git").mkdir()
            (repo / "pyproject.toml").write_text("[project]\nname='sample'\n", encoding="utf-8")
            (repo / "package.json").write_text('{"name":"sample"}\n', encoding="utf-8")
            (repo / ".vscode").mkdir()

            processes = [
                proc(7001, 1, "00:08:00", 0.0, 128, "python3", f"python3 {repo / 'manage.py'}"),
                proc(7002, 1, "00:05:00", 0.0, 128, "node", f"node {repo / 'scripts' / 'build.js'}"),
            ]
            signals = gather_project_signals(processes, home=home)

        self.assertEqual(len(signals), 1)
        self.assertEqual(signals[0]["root"], str(repo))
        self.assertIn("python", signals[0]["toolchains"])
        self.assertIn("node", signals[0]["toolchains"])
        self.assertIn("ide", signals[0]["toolchains"])
        self.assertEqual(signals[0]["source_process_count"], 2)

    def test_annotate_detector_findings_marks_active_project_guards(self) -> None:
        findings = [
            {"key": "python", "title": "Python", "status": "observed", "total_bytes": 1, "path_count": 1, "cleanup_ready": False, "notes": "Visibility only."},
            {"key": "ollama", "title": "Ollama", "status": "observed", "total_bytes": 1, "path_count": 1, "cleanup_ready": False, "notes": "Visibility only."},
        ]
        project_signals = [
            {
                "root": "/Users/test/Projects/sample-app",
                "toolchains": ["git", "python"],
                "markers": ["pyproject.toml"],
                "source_process_count": 1,
                "families": ["other"],
            }
        ]
        annotated = annotate_detector_findings(findings, project_signals)
        self.assertEqual(annotated[0]["safety_state"], "guarded_by_active_projects")
        self.assertEqual(annotated[0]["active_project_count"], 1)
        self.assertEqual(annotated[1]["safety_state"], "visibility_only")

    def test_path_delete_trash_moves_instead_of_destroying(self) -> None:
        from dreamcleanr.core import path_delete

        with TemporaryDirectory() as tmpdir:
            home = Path(tmpdir)
            trash = home / ".Trash"
            victim = home / "regenerable-cache"
            victim.mkdir()
            (victim / "blob").write_text("data", encoding="utf-8")
            with patch("dreamcleanr.core._trash_dir", return_value=trash):
                path_delete(victim, trash=True)
            self.assertFalse(victim.exists())
            self.assertTrue((trash / "regenerable-cache" / "blob").exists())  # recoverable

    def test_path_delete_hard_delete_removes(self) -> None:
        from dreamcleanr.core import path_delete

        with TemporaryDirectory() as tmpdir:
            victim = Path(tmpdir) / "cache"
            victim.mkdir()
            path_delete(victim, trash=False)
            self.assertFalse(victim.exists())

    def test_du_bytes_many_parallel_sizes_and_dedups(self) -> None:
        from dreamcleanr.core import du_bytes_many

        calls = []

        def fake(path: Path) -> int:
            calls.append(str(path))
            return 100

        with patch("dreamcleanr.core.du_bytes", side_effect=fake):
            result = du_bytes_many([Path("/a"), Path("/b"), Path("/a")])
        self.assertEqual(result, {"/a": 100, "/b": 100})
        self.assertEqual(len(calls), 2)  # deduped before sizing

    def test_apply_blocks_terminate_when_pid_identity_changed(self) -> None:
        snapshot = {"process_summary": {fam: {"protected_library_caches": []} for fam in ("claude", "codex")}}
        action = CleanupAction(
            target="4242", target_type="process", family="docker",
            classification="STALE_CLI", result="planned", bytes_reclaimed=1024,
            reason="stale", details={"args": "docker info", "apply_allowed": True},
        )
        with patch("dreamcleanr.core.process_args", return_value="/usr/bin/some-unrelated-binary --foo"):
            applied = apply_actions(snapshot, [action], dry_run=False)
        self.assertEqual(applied[0].result, "blocked")
        self.assertIn("reused", applied[0].reason)

    def test_apply_marks_already_exited_process_terminated(self) -> None:
        snapshot = {"process_summary": {fam: {"protected_library_caches": []} for fam in ("claude", "codex")}}
        action = CleanupAction(
            target="4242", target_type="process", family="docker",
            classification="STALE_CLI", result="planned", bytes_reclaimed=0,
            reason="stale", details={"args": "docker info", "apply_allowed": True},
        )
        with patch("dreamcleanr.core.process_args", return_value=None):
            applied = apply_actions(snapshot, [action], dry_run=False)
        self.assertEqual(applied[0].result, "terminated")

    def test_plan_cleanup_library_sweep_is_max_only(self) -> None:
        snapshot = {
            "processes": [],
            "process_summary": {
                fam: {"state": "inactive", "recommended_action": "protect_only"}
                for fam in ("docker", "claude", "codex")
            },
        }
        with patch("dreamcleanr.core.du_bytes", return_value=0):
            balanced = plan_cleanup(snapshot, mode="balanced")
            aggressive = plan_cleanup(snapshot, mode="max")
        balanced_labels = {a.details.get("label") for a in balanced}
        max_labels = {a.details.get("label") for a in aggressive}
        # Regenerable dev caches stay in the standard tier...
        self.assertIn("uv_cache", balanced_labels)
        self.assertIn("npm_cache", balanced_labels)
        # ...but the wholesale ~/Library/Caches sweep is aggressive-only.
        self.assertNotIn("library_caches", balanced_labels)
        self.assertIn("library_caches", max_labels)

    def test_plan_cleanup_safe_mode_is_preview_only(self) -> None:
        snapshot = {
            "processes": [],
            "process_summary": {
                fam: {"state": "inactive", "recommended_action": "protect_only"}
                for fam in ("docker", "claude", "codex")
            },
        }
        with patch("dreamcleanr.core.du_bytes", return_value=0):
            safe = plan_cleanup(snapshot, mode="safe")
        self.assertTrue(safe, "safe mode should still surface a preview of standard actions")
        self.assertTrue(
            all(not action.details.get("apply_allowed", True) for action in safe),
            "every safe-mode action must be preview-only (apply_allowed=False)",
        )
        self.assertNotIn("library_caches", {a.details.get("label") for a in safe})

    def test_detector_findings_carry_reclaim_metadata(self) -> None:
        with TemporaryDirectory() as tmpdir:
            home = Path(tmpdir)
            (home / ".cache" / "pip").mkdir(parents=True)
            (home / ".ollama").mkdir(parents=True)
            with patch("dreamcleanr.core.du_bytes", return_value=1024):
                findings = gather_detector_findings(home=home)
        by_key = {f["key"]: f for f in findings}
        self.assertEqual(by_key["ollama"]["reclaim_policy"], "model_data")
        self.assertEqual(by_key["ollama"]["reclaimable_bytes"], 0)  # models never auto-reclaimed
        self.assertEqual(by_key["python"]["reclaim_policy"], "regenerable")
        self.assertEqual(by_key["python"]["reclaimable_bytes"], 1024)  # pip_cache is regenerable
        self.assertIsNotNone(by_key["python"]["last_touched_days"])

    def _detector_snapshot(self, finding: dict) -> dict:
        return {
            "processes": [],
            "process_summary": {
                fam: {"state": "inactive", "recommended_action": "protect_only"}
                for fam in ("docker", "claude", "codex")
            },
            "detector_findings": [finding],
        }

    def test_plan_cleanup_max_reclaims_stale_regenerable_detector_cache(self) -> None:
        finding = {
            "key": "python", "reclaim_policy": "regenerable", "safety_state": "visibility_only",
            "last_touched_days": 30,
            "observed_paths": [{"label": "pip_cache", "path": "/Users/x/.cache/pip", "size_bytes": 100}],
        }
        snapshot = self._detector_snapshot(finding)
        with patch("dreamcleanr.core.du_bytes", return_value=100):
            max_actions = plan_cleanup(snapshot, mode="max")
            balanced = plan_cleanup(snapshot, mode="balanced")
        self.assertIn("python:pip_cache", {a.details.get("label") for a in max_actions})
        self.assertNotIn("python:pip_cache", {a.details.get("label") for a in balanced})

    def test_plan_cleanup_max_skips_guarded_fresh_and_model_data(self) -> None:
        def finding(**overrides):
            base = {
                "key": "python", "reclaim_policy": "regenerable", "safety_state": "visibility_only",
                "last_touched_days": 30,
                "observed_paths": [{"label": "pip_cache", "path": "/Users/x/.cache/pip", "size_bytes": 100}],
            }
            base.update(overrides)
            return base

        for case in (
            finding(safety_state="guarded_by_active_projects"),  # active project guard
            finding(last_touched_days=2),                        # too fresh
            finding(reclaim_policy="model_data"),                # downloaded models
        ):
            with patch("dreamcleanr.core.du_bytes", return_value=100):
                actions = plan_cleanup(self._detector_snapshot(case), mode="max")
            self.assertNotIn("python:pip_cache", {a.details.get("label") for a in actions})

    def test_plan_cleanup_max_skips_detector_path_overlapping_library_sweep(self) -> None:
        overlapping = str(Path.home() / "Library" / "Caches" / "pip")
        finding = {
            "key": "python", "reclaim_policy": "regenerable", "safety_state": "visibility_only",
            "last_touched_days": 30,
            "observed_paths": [{"label": "pip_cache", "path": overlapping, "size_bytes": 100}],
        }
        with patch("dreamcleanr.core.du_bytes", return_value=100):
            actions = plan_cleanup(self._detector_snapshot(finding), mode="max")
        labels = {a.details.get("label") for a in actions}
        self.assertIn("library_caches", labels)        # wholesale sweep present
        self.assertNotIn("python:pip_cache", labels)    # overlapping path not double-planned

    def test_capture_memory_state_parses_vm_stat(self) -> None:
        from dreamcleanr.core import capture_memory_state

        vm = (
            "Mach Virtual Memory Statistics: (page size of 16384 bytes)\n"
            "Pages free: 100.\nPages active: 200.\nPages inactive: 50.\n"
            "Pages wired down: 300.\nPages occupied by compressor: 25.\n"
        )

        def fake_run(cmd, timeout=5):
            if cmd[0] == "sysctl":
                return {"ok": True, "timed_out": False, "returncode": 0, "stdout": str(16384 * 1000), "stderr": ""}
            if cmd[0] == "vm_stat":
                return {"ok": True, "timed_out": False, "returncode": 0, "stdout": vm, "stderr": ""}
            return {"ok": False, "timed_out": False, "returncode": 1, "stdout": "", "stderr": ""}

        with patch("dreamcleanr.core.run_command", side_effect=fake_run):
            state = capture_memory_state()
        self.assertTrue(state["available"])
        self.assertEqual(state["wired_bytes"], 300 * 16384)
        self.assertEqual(state["used_bytes"], (300 + 200 + 25) * 16384)  # inactive excluded
        self.assertEqual(state["inactive_bytes"], 50 * 16384)  # reported, not counted as used

    def test_list_loaded_models_parses_ollama_ps(self) -> None:
        from dreamcleanr.core import list_loaded_models

        out = (
            "NAME            ID    SIZE     PROCESSOR    UNTIL\n"
            "llama3:70b      abc   40 GB    100% GPU     4 minutes from now\n"
            "qwen2:7b        def   5.5 GB   100% CPU     Forever\n"
        )
        with patch("dreamcleanr.core.shutil.which", return_value="/usr/local/bin/ollama"), patch(
            "dreamcleanr.core.run_command",
            return_value={"ok": True, "timed_out": False, "returncode": 0, "stdout": out, "stderr": ""},
        ):
            models = list_loaded_models()
        self.assertEqual([m["name"] for m in models], ["llama3:70b", "qwen2:7b"])
        self.assertEqual(models[0]["size_bytes"], 40 * 1024 ** 3)
        self.assertEqual(models[0]["action"], "ollama stop llama3:70b")
        self.assertTrue(models[0]["reversible"])

    def test_list_loaded_models_empty_without_ollama(self) -> None:
        from dreamcleanr.core import list_loaded_models

        with patch("dreamcleanr.core.shutil.which", return_value=None):
            self.assertEqual(list_loaded_models(), [])

    def test_reclaim_ceiling_sums_only_named_actionable_sources(self) -> None:
        from dreamcleanr.core import reclaim_ceiling

        snapshot = {
            "processes": [
                {"classification": "STALE_CLI", "family": "docker", "pid": 5, "rss_kb": 1024},
                {"classification": "ACTIVE_PRIMARY", "family": "claude", "pid": 6, "rss_kb": 9999},
            ],
            "loaded_models": [{"name": "llama3", "size_bytes": 8 * 1024 ** 3, "action": "ollama stop llama3"}],
            "storage_records": [
                {"label": "uv_cache", "classification": "SAFE_CACHE", "size_bytes": 2048},
                {"label": "library_cache:foo", "classification": "SAFE_CACHE", "size_bytes": 999},  # child → skipped
                {"label": "claude_home", "classification": "PROTECTED_STATE", "size_bytes": 500},  # protected → skipped
            ],
            "detector_findings": [
                {"key": "node", "reclaimable_bytes": 4096, "safety_state": "visibility_only"},
                {"key": "python", "reclaimable_bytes": 100, "safety_state": "guarded_by_active_projects"},  # guarded
            ],
        }
        ceiling = reclaim_ceiling(snapshot)
        self.assertEqual(ceiling["ram_bytes"], 1024 * 1024 + 8 * 1024 ** 3)  # stale proc + model (active excluded)
        self.assertEqual(ceiling["disk_bytes"], 2048 + 4096)  # uv + node; child/protected/guarded excluded

    def test_plan_cleanup_max_unloads_loaded_models(self) -> None:
        snapshot = {
            "processes": [],
            "process_summary": {fam: {"state": "inactive", "recommended_action": "protect_only"} for fam in ("docker", "claude", "codex")},
            "loaded_models": [{"name": "llama3", "size_bytes": 8 * 1024 ** 3, "action": "ollama stop llama3"}],
        }
        with patch("dreamcleanr.core.du_bytes", return_value=0):
            max_actions = plan_cleanup(snapshot, mode="max")
            balanced = plan_cleanup(snapshot, mode="balanced")
        mem = [a for a in max_actions if a.target_type == "memory"]
        self.assertEqual(len(mem), 1)
        self.assertEqual(mem[0].target, "llama3")
        self.assertEqual(mem[0].bytes_reclaimed, 8 * 1024 ** 3)
        self.assertTrue(mem[0].details["reversible"])
        self.assertEqual([a for a in balanced if a.target_type == "memory"], [])  # max-only

    def test_apply_unloads_model_via_command(self) -> None:
        snapshot = {"process_summary": {fam: {"protected_library_caches": []} for fam in ("claude", "codex")}}
        action = CleanupAction(
            target="llama3", target_type="memory", family="ollama", classification="LOADED_MODEL",
            result="planned", bytes_reclaimed=8 * 1024 ** 3, reason="r",
            details={"apply_allowed": True, "action": "ollama stop llama3"},
        )
        captured = {}

        def fake_run(cmd, timeout=5):
            captured["cmd"] = cmd
            return {"ok": True, "timed_out": False, "returncode": 0, "stdout": "", "stderr": ""}

        with patch("dreamcleanr.core.run_command", side_effect=fake_run):
            applied = apply_actions(snapshot, [action], dry_run=False)
        self.assertEqual(applied[0].result, "unloaded")
        self.assertEqual(captured["cmd"], ["ollama", "stop", "llama3"])

    def test_build_cleanup_report_separates_ram_and_disk(self) -> None:
        from dreamcleanr.core import build_cleanup_report

        before = {"run_id": "r", "started_at": "s", "host_disk_used_bytes": 1000, "processes": [],
                  "protected_items": [], "manual_review_items": [], "process_summary": {}}
        after = {"finished_at": "f", "host_disk_used_bytes": 1000}
        actions = [
            CleanupAction(target="x", target_type="path", family="system", classification="SAFE_CACHE", result="deleted", bytes_reclaimed=5000, reason="r", details={}),
            CleanupAction(target="llama3", target_type="memory", family="ollama", classification="LOADED_MODEL", result="unloaded", bytes_reclaimed=8 * 1024 ** 3, reason="r", details={}),
            CleanupAction(target="123", target_type="process", family="docker", classification="STALE_CLI", result="terminated", bytes_reclaimed=2 * 1024 * 1024, reason="r", details={}),
        ]
        report = build_cleanup_report(before, after, actions, mode="max", dry_run=False)
        self.assertEqual(report.storage_reclaimed_bytes, 5000)  # disk only — RAM not conflated
        expected_mem_mb = round((8 * 1024 ** 3 + 2 * 1024 * 1024) / (1024 * 1024), 2)
        self.assertEqual(report.memory_reclaimed_estimate_mb, expected_mem_mb)  # model + process

    # Regression tests for PR #30 review (Gemini HIGH + Codex P2): the
    # storage/memory accounting must exclude actions that didn't actually
    # happen, AND trashed paths shouldn't count as freed disk.
    def test_build_cleanup_report_excludes_blocked_failed_planned(self) -> None:
        from dreamcleanr.core import build_cleanup_report
        before = {"run_id": "r", "started_at": "s", "host_disk_used_bytes": 1000, "processes": [],
                  "protected_items": [], "manual_review_items": [], "process_summary": {}}
        after = {"finished_at": "f", "host_disk_used_bytes": 1000}
        actions = [
            # Should NOT count toward any reclaim total
            CleanupAction(target="a", target_type="path",    family="x", classification="C", result="blocked",  bytes_reclaimed=1000, reason="r", details={}),
            CleanupAction(target="b", target_type="path",    family="x", classification="C", result="failed",   bytes_reclaimed=2000, reason="r", details={}),
            CleanupAction(target="c", target_type="path",    family="x", classification="C", result="missing",  bytes_reclaimed=4000, reason="r", details={}),
            CleanupAction(target="d", target_type="path",    family="x", classification="C", result="kept",     bytes_reclaimed=8000, reason="r", details={}),
            CleanupAction(target="e", target_type="process", family="x", classification="C", result="blocked",  bytes_reclaimed=1 * 1024 ** 2, reason="r", details={}),
            CleanupAction(target="f", target_type="memory",  family="x", classification="C", result="blocked",  bytes_reclaimed=4 * 1024 ** 3, reason="r", details={}),
            # SHOULD count
            CleanupAction(target="g", target_type="path",    family="x", classification="C", result="deleted",  bytes_reclaimed=500, reason="r", details={}),
        ]
        report = build_cleanup_report(before, after, actions, mode="max", dry_run=False)
        self.assertEqual(report.storage_reclaimed_bytes, 500)
        self.assertEqual(report.memory_reclaimed_estimate_mb, 0.0)
        self.assertEqual(report.processes_trimmed, 0)
        self.assertEqual(report.objects_pruned, 1)

    def test_build_cleanup_report_excludes_trashed_paths_from_disk(self) -> None:
        """Trashing moves to ~/.Trash on the same volume — disk isn't freed."""
        from dreamcleanr.core import build_cleanup_report
        before = {"run_id": "r", "started_at": "s", "host_disk_used_bytes": 1000, "processes": [],
                  "protected_items": [], "manual_review_items": [], "process_summary": {}}
        after = {"finished_at": "f", "host_disk_used_bytes": 1000}
        actions = [
            CleanupAction(target="t", target_type="path", family="x", classification="C", result="deleted",
                          bytes_reclaimed=12345, reason="r", details={"trashed": True}),
            CleanupAction(target="r", target_type="path", family="x", classification="C", result="deleted",
                          bytes_reclaimed=999, reason="r", details={}),
        ]
        report = build_cleanup_report(before, after, actions, mode="max", dry_run=False)
        self.assertEqual(report.storage_reclaimed_bytes, 999)  # trashed excluded
        self.assertEqual(report.objects_pruned, 2)  # both still count as "trimmed" objects

    # Process-fixture coverage per issue #1 — updater + crashpad +
    # Docker-engine-only states. Pins the new families and roles.

    def test_classify_generic_crashpad_handler(self) -> None:
        # Generic crashpad helper that isn't bundled with claude/codex
        # should land in the crashpad family, not be misattributed.
        record = proc(901, 1, "00:30:00", 0.0, 120, "crashpad_handler",
                      "/Library/Application Support/SomeApp/crashpad_handler --database=/tmp/x")
        self.assertEqual(record.family, "crashpad")
        self.assertEqual(record.role, "crashpad")

    def test_classify_claude_crashpad_stays_in_claude(self) -> None:
        # Cross-product crashpad rule must NOT steal claude's own helpers.
        record = proc(902, 1, "00:30:00", 0.0, 120, "crashpad_handler",
                      "/Applications/Claude.app/Contents/Frameworks/Claude Helper/crashpad_handler --database=/tmp/x")
        self.assertEqual(record.family, "claude")
        self.assertEqual(record.role, "crashpad")

    def test_classify_sparkle_updater(self) -> None:
        record = proc(910, 1, "00:00:30", 0.0, 80, "Sparkle",
                      "/Library/Sparkle.app/Contents/MacOS/Sparkle --updater")
        self.assertEqual(record.family, "updater")
        self.assertEqual(record.role, "sparkle")

    def test_classify_macos_softwareupdate(self) -> None:
        record = proc(911, 1, "00:00:30", 0.0, 80, "softwareupdate",
                      "/usr/sbin/softwareupdate --install --recommended")
        self.assertEqual(record.family, "updater")
        self.assertEqual(record.role, "macos_softwareupdate")

    def test_classify_shipit_updater(self) -> None:
        record = proc(912, 1, "00:00:30", 0.0, 80, "ShipIt",
                      "/Applications/Foo.app/Contents/Frameworks/ShipIt /tmp/shipit-state.plist")
        self.assertEqual(record.family, "updater")
        self.assertEqual(record.role, "shipit")

    def test_classify_microsoft_autoupdate(self) -> None:
        record = proc(913, 1, "00:00:30", 0.0, 80, "msupdate",
                      "/Library/Application Support/Microsoft AutoUpdate/MAU.app/Contents/MacOS/Microsoft AutoUpdate")
        self.assertEqual(record.family, "updater")
        self.assertEqual(record.role, "msupdate")

    def test_classify_google_software_update(self) -> None:
        record = proc(914, 1, "00:00:30", 0.0, 80, "GoogleSoftwareUpdate",
                      "/Library/Google/GoogleSoftwareUpdate/GoogleSoftwareUpdate.bundle/Contents/Resources/GoogleSoftwareUpdateAgent.app/Contents/MacOS/GoogleSoftwareUpdateAgent")
        self.assertEqual(record.family, "updater")
        self.assertEqual(record.role, "google_software_update")

    def test_classify_docker_engine_only_no_containers(self) -> None:
        # Docker daemon up + no containers — still docker family, classified
        # by role; summarize_family handles the engine-only state via the
        # docker_inventory hint.
        processes = [
            proc(57788, 1, "06:00:00", 0.0, 1200, "/Applications/Do",
                 "/Applications/Docker.app/Contents/MacOS/com.docker.backend"),
            proc(57859, 57788, "06:00:00", 0.0, 900, "/Applications/Do",
                 "/Applications/Docker.app/Contents/MacOS/com.docker.virtualization --disk /tmp/Docker.raw"),
        ]
        by_pid = {p.pid: p for p in processes}
        # Empty inventory = engine is up but nothing to clean
        from dreamcleanr.models import DockerInventory
        empty_inv = DockerInventory(engine_available=True, engine_state="reachable")
        with patch("dreamcleanr.core.run_command",
                   return_value={"ok": True, "timed_out": False, "returncode": 0, "stdout": "{}", "stderr": ""}):
            summary = summarize_family("docker", processes, by_pid, {99999}, docker_inventory=empty_inv)
        # The two backend processes still classify
        self.assertGreaterEqual(len(summary["matches"]), 2)

    def test_build_cleanup_report_dry_run_counts_planned(self) -> None:
        from dreamcleanr.core import build_cleanup_report
        before = {"run_id": "r", "started_at": "s", "host_disk_used_bytes": 1000, "processes": [],
                  "protected_items": [], "manual_review_items": [], "process_summary": {}}
        after = {"finished_at": "f", "host_disk_used_bytes": 1000}
        actions = [
            CleanupAction(target="a", target_type="path",    family="x", classification="C", result="planned", bytes_reclaimed=100, reason="r", details={}),
            CleanupAction(target="b", target_type="process", family="x", classification="C", result="planned", bytes_reclaimed=200, reason="r", details={}),
        ]
        report = build_cleanup_report(before, after, actions, mode="max", dry_run=True)
        # planned counts toward _trimmed/_pruned (estimates), but NOT toward
        # the byte totals — bytes only count when actions actually run.
        self.assertEqual(report.storage_reclaimed_bytes, 0)
        self.assertEqual(report.memory_reclaimed_estimate_mb, 0.0)
        self.assertEqual(report.processes_trimmed, 1)
        self.assertEqual(report.objects_pruned, 1)

    def test_prune_history_files_keeps_most_recent_artifacts(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for idx in range(4):
                path = root / f"report-20260328T00000{idx}.json"
                path.write_text(str(idx), encoding="utf-8")
            removed = prune_history_files(root, keep=2)
            remaining = sorted(path.name for path in root.glob("report-*.json"))
            self.assertEqual(len(removed), 2)
            self.assertEqual(len(remaining), 2)


if __name__ == "__main__":
    unittest.main()
