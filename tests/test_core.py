from __future__ import annotations

import unittest
from unittest.mock import patch

from dreamcleanr.core import classify_process_role, classify_processes, parse_elapsed_to_seconds, summarize_family
from dreamcleanr.models import ProcessRecord


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


if __name__ == "__main__":
    unittest.main()
