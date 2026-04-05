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
