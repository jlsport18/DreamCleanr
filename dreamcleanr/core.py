from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import time
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .models import CleanupAction, CleanupReport, DockerInventory, ProcessRecord, StorageRecord

FAMILIES = ("docker", "claude", "codex")
REPORT_ROOT = Path.home() / "Library" / "Logs" / "DreamCleanr" / "reports"
DEFAULT_RETENTION_COUNT = 21
DEFAULT_LOG_RETENTION_COUNT = 5
STALE_PROCESS_MIN_ELAPSED_SECONDS = 300
STALE_PROCESS_MAX_CPU_PERCENT = 1.0

PROTECTED_STATE_PATHS = {
    "codex_home": Path.home() / ".codex",
    "claude_home": Path.home() / ".claude",
    "codex_support": Path.home() / "Library" / "Application Support" / "Codex",
    "claude_support": Path.home() / "Library" / "Application Support" / "Claude",
    "claude_vm_bundle": Path.home() / "Library" / "Application Support" / "Claude" / "vm_bundles" / "claudevm.bundle",
    "docker_vm_data": Path.home() / "Library" / "Containers" / "com.docker.docker" / "Data" / "vms",
    "docker_raw": Path.home() / "Library" / "Containers" / "com.docker.docker" / "Data" / "vms" / "0" / "data" / "Docker.raw",
}

SAFE_CACHE_PATHS = {
    "uv_cache": Path.home() / ".cache" / "uv",
    "trunk_cache": Path.home() / ".cache" / "trunk",
    "library_caches": Path.home() / "Library" / "Caches",
    "gradle_cache": Path.home() / ".gradle" / "caches",
    "npm_cache": Path.home() / ".npm" / "_cacache",
    "npx_cache": Path.home() / ".npm" / "_npx",
}

CLAUDE_LIBRARY_CACHE_BASENAMES = [
    "claude-cli-nodejs",
    "com.anthropic.claudefordesktop",
    "com.anthropic.claudefordesktop.ShipIt",
]
CODEX_LIBRARY_CACHE_BASENAMES = ["com.openai.codex"]

CLAUDE_SUPPORT_CACHE_DIRS = [
    "Cache",
    "Code Cache",
    "GPUCache",
    "DawnGraphiteCache",
    "DawnWebGPUCache",
]
CODEX_SUPPORT_CACHE_DIRS = [
    "Cache",
    "Code Cache",
    "GPUCache",
    "DawnGraphiteCache",
    "DawnWebGPUCache",
]

DOCKER_PROBE_SNIPPETS = (
    "docker info",
    "docker ps",
    "docker system df",
    "docker image ls",
    "docker volume ls",
    "docker network ls",
    "docker context ls",
)

TIMESTAMPED_REPORT_GLOBS = (
    "before-*.json",
    "after-*.json",
    "report-*.json",
    "report-*.html",
    "failure-*.json",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def human_bytes(num: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(num)
    for unit in units:
        if value < 1024.0 or unit == units[-1]:
            return f"{int(value)}B" if unit == "B" else f"{value:.1f}{unit}"
        value /= 1024.0
    return f"{num}B"


def parse_size_to_bytes(text: str) -> int:
    raw = (text or "").strip().upper().replace("IB", "B")
    if not raw:
        return 0
    raw = raw.replace(" ", "")
    units = {
        "B": 1,
        "KB": 1024,
        "MB": 1024 ** 2,
        "GB": 1024 ** 3,
        "TB": 1024 ** 4,
    }
    for unit, scale in units.items():
        if raw.endswith(unit):
            number = raw[: -len(unit)]
            try:
                return int(float(number) * scale)
            except ValueError:
                return 0
    try:
        return int(float(raw))
    except ValueError:
        return 0


def parse_elapsed_to_seconds(value: str) -> int:
    if not value:
        return 0
    days = 0
    time_part = value
    if "-" in value:
        day_part, time_part = value.split("-", 1)
        days = int(day_part)
    parts = [int(part) for part in time_part.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0)
    hours, minutes, seconds = parts[-3:]
    return days * 86400 + hours * 3600 + minutes * 60 + seconds


def has_any_token(text: str, tokens: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(token in lowered for token in tokens)


def is_docker_probe_command(args: str) -> bool:
    lowered = args.lower()
    return any(snippet in lowered for snippet in DOCKER_PROBE_SNIPPETS)


def run_command(command: List[str], timeout: int = 5) -> Dict[str, Any]:
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "timed_out": True,
            "returncode": None,
            "stdout": "",
            "stderr": "",
        }
    return {
        "ok": proc.returncode == 0,
        "timed_out": False,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def du_bytes(path: Path) -> int:
    if not path.exists():
        return 0
    result = run_command(["/usr/bin/du", "-sk", str(path)], timeout=10)
    if not result["ok"] or not result["stdout"].strip():
        return 0
    try:
        return int(result["stdout"].split()[0]) * 1024
    except (IndexError, ValueError):
        return 0


def list_processes() -> List[ProcessRecord]:
    result = run_command(
        [
            "ps",
            "-axo",
            "pid=,ppid=,etime=,%cpu=,%mem=,rss=,comm=,args=",
        ],
        timeout=5,
    )
    if not result["ok"]:
        return []

    processes: List[ProcessRecord] = []
    for line in result["stdout"].splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 7)
        if len(parts) < 8:
            continue
        try:
            pid = int(parts[0])
            ppid = int(parts[1])
            etime = parts[2]
            cpu_percent = float(parts[3])
            mem_percent = float(parts[4])
            rss_kb = int(parts[5])
            command = parts[6]
            args = parts[7]
        except ValueError:
            continue
        processes.append(
            ProcessRecord(
                pid=pid,
                ppid=ppid,
                etime=etime,
                elapsed_seconds=parse_elapsed_to_seconds(etime),
                cpu_percent=cpu_percent,
                mem_percent=mem_percent,
                rss_kb=rss_kb,
                command=command,
                args=args,
            )
        )
    return processes


def classify_process_role(record: ProcessRecord) -> None:
    args = record.args.lower()
    command = record.command.lower()

    if any(token in args for token in ("dreamcleanr", "analyze-system-data", "prune-system-data", "ai-system-cleanup")):
        record.family = "self"
        record.role = "self"
        return
    if any(token in args for token in ("grep", "egrep", "pgrep")) or command.endswith("/ps"):
        record.family = "self"
        record.role = "probe"
        return

    if has_any_token(
        args,
        (
            "/applications/docker.app/contents/",
            "com.docker.backend",
            "com.docker.virtualization",
            "com.docker.vmnetd",
            "docker-sandbox daemon",
            "docker-agent.sock",
            "docker.raw",
            "com.docker.socket",
            "com.docker.build",
        ),
    ):
        record.family = "docker"
        if "com.docker.vmnetd" in args:
            record.role = "vmnetd"
        elif "com.docker.virtualization" in args or "docker.raw" in args:
            record.role = "virtualization"
        elif "com.docker.backend" in args and " services" not in args and " fork" not in args:
            record.role = "backend"
        elif "com.docker.backend services" in args:
            record.role = "backend_service"
        elif "docker-sandbox daemon" in args:
            record.role = "sandbox"
        else:
            record.role = "docker_helper"
        return
    if command == "docker" or args.startswith("docker ") or " docker " in args:
        record.family = "docker"
        record.role = "docker_cli_probe" if is_docker_probe_command(args) else "docker_cli"
        return
    if command.endswith("/zsh") and "docker" in args:
        record.family = "docker"
        record.role = "shell_docker_probe" if is_docker_probe_command(args) else "shell_docker_session"
        return

    if has_any_token(
        args,
        (
            "/applications/codex.app/contents/macos/codex",
            "codex helper",
            "codex helper (renderer)",
            "/resources/codex app-server",
            "openai.chatgpt-",
            "com.openai.codex",
            "crashpad_handler",
        ),
    ):
        record.family = "codex"
        if "crashpad_handler" in args:
            record.role = "crashpad"
        elif "/applications/codex.app/contents/macos/codex" in args:
            record.role = "codex_app"
        elif "codex helper (renderer)" in args:
            record.role = "renderer"
        elif "codex helper" in args:
            record.role = "helper"
        elif "/resources/codex app-server" in args or "openai.chatgpt-" in args:
            record.role = "cli_service"
        elif "sparkle" in args or "updater" in args:
            record.role = "updater"
        else:
            record.role = "codex_helper"
        return

    if has_any_token(
        args,
        (
            "/applications/claude.app/contents/",
            "claudefordesktop",
            "anthropic.claude-code-",
            "/resources/native-binary/claude",
            "claude --output-format",
            "--mcp-config",
            "crashpad_handler",
        ),
    ):
        record.family = "claude"
        if "crashpad_handler" in args and "claude" in args:
            record.role = "crashpad"
        elif "/applications/claude.app/contents/macos/claude" in args:
            record.role = "claude_app"
        elif "claude helper (renderer)" in args:
            record.role = "renderer"
        elif "claude helper" in args:
            record.role = "helper"
        elif "shipit" in args:
            record.role = "shipit"
        else:
            record.role = "vscode_cli"
        return


def ancestor_chain(pid: int, by_pid: Dict[int, ProcessRecord]) -> List[ProcessRecord]:
    chain: List[ProcessRecord] = []
    seen = set()
    current = by_pid.get(pid)
    while current and current.pid not in seen:
        seen.add(current.pid)
        chain.append(current)
        current = by_pid.get(current.ppid)
    return chain


def summarize_family(
    family: str,
    processes: List[ProcessRecord],
    by_pid: Dict[int, ProcessRecord],
    self_pids: Iterable[int],
    docker_inventory: Optional[DockerInventory] = None,
) -> Dict[str, Any]:
    self_pid_set = set(self_pids)
    matches: List[Dict[str, Any]] = []
    ignored_matches: List[Dict[str, Any]] = []
    active_primary_pids: List[int] = []
    roles = set()

    strong_roles = {
        "docker": {"vmnetd", "backend", "backend_service", "virtualization", "sandbox", "docker_helper"},
        "claude": {"claude_app", "vscode_cli"},
        "codex": {"codex_app", "helper", "renderer", "cli_service"},
    }[family]
    weak_roles = {
        "docker": {"docker_cli", "docker_cli_probe", "shell_docker_probe", "shell_docker_session"},
        "claude": {"shipit", "crashpad"},
        "codex": {"updater", "crashpad"},
    }[family]
    primary_roles = {
        "docker": {"vmnetd", "backend", "virtualization"},
        "claude": {"claude_app", "vscode_cli"},
        "codex": {"codex_app", "cli_service"},
    }[family]

    for record in processes:
        if record.family != family:
            continue
        if record.pid in self_pid_set or record.ppid in self_pid_set or record.role in {"self", "probe"}:
            ignored_matches.append(
                {
                    "pid": record.pid,
                    "reason": "self_match",
                    "role": record.role,
                    "args_excerpt": record.args[:180],
                }
            )
            continue
        strength = "weak"
        if record.role in strong_roles:
            strength = "strong"
        elif record.role in weak_roles:
            strength = "medium"
        matches.append(
            {
                "pid": record.pid,
                "ppid": record.ppid,
                "role": record.role,
                "strength": strength,
                "comm": record.command,
                "args_excerpt": record.args[:180],
            }
        )
        roles.add(record.role)
        if record.role in primary_roles:
            active_primary_pids.append(record.pid)

    paths_present = {}
    if family == "docker":
        paths_present["vm_data"] = PROTECTED_STATE_PATHS["docker_vm_data"].exists()
        paths_present["docker_raw"] = PROTECTED_STATE_PATHS["docker_raw"].exists()
    elif family == "claude":
        paths_present["vm_bundle"] = PROTECTED_STATE_PATHS["claude_vm_bundle"].exists()
        paths_present["support_root"] = PROTECTED_STATE_PATHS["claude_support"].exists()
    elif family == "codex":
        paths_present["support_root"] = PROTECTED_STATE_PATHS["codex_support"].exists()

    daemon_state = "n/a"
    inventory_counts: Dict[str, int] = {}
    if family == "docker" and docker_inventory is not None:
        daemon_state = docker_inventory.engine_state
        inventory_counts = dict(docker_inventory.reclaimable_summary)

    if active_primary_pids:
        state = "active"
        confidence = "high"
    elif family == "docker" and daemon_state == "reachable":
        state = "active"
        confidence = "medium"
    elif any(role in weak_roles for role in roles):
        state = "background_only" if family in {"claude", "codex"} else "cli_only"
        confidence = "medium"
    elif any(paths_present.values()):
        state = "residual_data_only"
        confidence = "medium"
    else:
        state = "inactive"
        confidence = "high"

    if family == "docker" and state == "active":
        allowed_actions = ["docker_system_prune"]
        blocked_actions = ["raw_vm_delete"]
        recommended_action = "docker_system_prune" if daemon_state == "reachable" else "protect_only"
        if active_primary_pids:
            reason = "backend, virtualization, or daemon-backed engine activity observed"
        else:
            reason = "Docker daemon responded even though no primary app process was classified"
    elif family == "docker" and state == "residual_data_only":
        allowed_actions = ["confirm_raw_vm_delete"]
        blocked_actions = []
        recommended_action = "confirm_raw_vm_delete"
        reason = "VM data exists without active engine processes"
    elif family == "docker":
        allowed_actions = []
        blocked_actions = ["raw_vm_delete"]
        recommended_action = "protect_only"
        reason = "Only CLI or background Docker evidence was observed"
    elif family == "claude" and state == "active":
        allowed_actions = []
        blocked_actions = ["prune_cache", "prune_vm"]
        recommended_action = "protect_only"
        reason = "Claude desktop or CLI integration is active"
    elif family == "claude" and state in {"inactive", "residual_data_only"}:
        allowed_actions = ["prune_cache"]
        if paths_present.get("vm_bundle"):
            allowed_actions.append("prune_vm")
        blocked_actions = []
        recommended_action = "prune_cache"
        reason = "Claude state exists without active processes"
    elif family == "codex" and state == "active":
        allowed_actions = []
        blocked_actions = ["prune_cache", "prune_support_root"]
        recommended_action = "protect_only"
        reason = "Codex desktop or app-server tree is active"
    elif family == "codex" and state == "background_only":
        allowed_actions = []
        blocked_actions = ["prune_cache", "prune_support_root"]
        recommended_action = "protect_only"
        reason = "Only updater or crash-style background Codex processes remain"
    else:
        allowed_actions = []
        blocked_actions = []
        recommended_action = "protect_only"
        reason = f"{family} is inactive or not observed"

    protected_library_caches: List[str] = []
    if family == "claude" and state in {"active", "background_only", "cli_only"}:
        protected_library_caches = CLAUDE_LIBRARY_CACHE_BASENAMES
    elif family == "codex" and state in {"active", "background_only"}:
        protected_library_caches = CODEX_LIBRARY_CACHE_BASENAMES

    return {
        "state": state,
        "daemon_state": daemon_state,
        "confidence": confidence,
        "roles": sorted(roles),
        "allowed_actions": allowed_actions,
        "blocked_actions": blocked_actions,
        "recommended_action": recommended_action,
        "reason": reason,
        "matches": matches,
        "ignored_matches": ignored_matches,
        "paths_present": paths_present,
        "protected_library_caches": protected_library_caches,
        "active_primary_pids": active_primary_pids,
        "inventory_counts": inventory_counts,
    }


def classify_processes(processes: List[ProcessRecord], family_summaries: Dict[str, Dict[str, Any]]) -> None:
    by_pid = {process.pid: process for process in processes}
    active_primary_pids = {
        family: set(summary.get("active_primary_pids", []))
        for family, summary in family_summaries.items()
    }

    for record in processes:
        if record.family in {"self", "other"}:
            if record.family == "self":
                record.classification = "IGNORED"
            else:
                record.classification = "OTHER"
            continue

        family = record.family
        state = family_summaries[family]["state"]
        chain = ancestor_chain(record.ppid, by_pid)
        chain_pids = {proc.pid for proc in chain}
        has_active_parent = bool(chain_pids & active_primary_pids[family])
        stale_signal = (
            record.elapsed_seconds >= STALE_PROCESS_MIN_ELAPSED_SECONDS
            and record.cpu_percent <= STALE_PROCESS_MAX_CPU_PERCENT
        )

        if record.role in {"vmnetd", "backend", "virtualization", "claude_app", "vscode_cli", "codex_app", "cli_service"}:
            record.classification = "ACTIVE_PRIMARY"
            record.reasons.append("primary runtime role")
        elif has_active_parent and state == "active":
            record.classification = "ACTIVE_HELPER"
            record.reasons.append("active parent chain")
        elif record.role in {"docker_cli_probe", "shell_docker_probe"} and stale_signal:
            record.classification = "STALE_CLI"
            record.reasons.append("old docker probe chain with low activity")
        elif record.role in {"updater", "shipit", "crashpad"} and not has_active_parent:
            record.classification = "BACKGROUND_ONLY"
            record.reasons.append("background updater or crash handler without active root")
        elif record.role in {"helper", "renderer", "docker_helper", "sandbox", "backend_service"} and not has_active_parent and stale_signal:
            record.classification = "STALE_HELPER"
            record.reasons.append("helper without active root and low activity")
        elif record.role in {"docker_cli", "shell_docker_session"}:
            record.classification = "BACKGROUND_ONLY"
            record.reasons.append("interactive or non-probe docker CLI preserved conservatively")
        elif state in {"background_only", "cli_only"}:
            record.classification = "BACKGROUND_ONLY"
            record.reasons.append(f"{family} state is {state}")
        else:
            record.classification = "ACTIVE_HELPER"
            record.reasons.append("conservative protection fallback")


def attach_classification_counts(processes: List[ProcessRecord], family_summaries: Dict[str, Dict[str, Any]]) -> None:
    for family in FAMILIES:
        family_processes = [process for process in processes if process.family == family]
        family_summaries[family]["process_counts"] = {
            "total": len(family_processes),
            "active_primary": sum(1 for process in family_processes if process.classification == "ACTIVE_PRIMARY"),
            "active_helper": sum(1 for process in family_processes if process.classification == "ACTIVE_HELPER"),
            "background_only": sum(1 for process in family_processes if process.classification == "BACKGROUND_ONLY"),
            "stale": sum(1 for process in family_processes if process.classification in {"STALE_CLI", "STALE_HELPER"}),
        }


def gather_storage_records(family_summaries: Dict[str, Dict[str, Any]]) -> Tuple[List[StorageRecord], List[StorageRecord], List[StorageRecord]]:
    records: List[StorageRecord] = []
    protected: List[StorageRecord] = []
    manual: List[StorageRecord] = []

    def add_record(label: str, path: Path, family: str, classification: str, notes: str) -> None:
        if not path.exists():
            return
        record = StorageRecord(
            label=label,
            path=str(path),
            family=family,
            classification=classification,
            size_bytes=du_bytes(path),
            notes=notes,
        )
        records.append(record)
        if classification == "PROTECTED_STATE":
            protected.append(record)
        elif classification == "REVIEW_VM":
            manual.append(record)

    for label, path in SAFE_CACHE_PATHS.items():
        add_record(label, path, "system", "SAFE_CACHE", "Regenerable cache or developer artifact.")

    add_record("docker_vm_data", PROTECTED_STATE_PATHS["docker_vm_data"], "docker", "REVIEW_VM", "Docker VM storage requires explicit review.")
    add_record("docker_raw", PROTECTED_STATE_PATHS["docker_raw"], "docker", "REVIEW_VM", "Raw Docker disk image should not be auto-deleted.")
    add_record("claude_vm_bundle", PROTECTED_STATE_PATHS["claude_vm_bundle"], "claude", "PROTECTED_STATE", "Claude VM bundle stays protected by default.")
    add_record("codex_home", PROTECTED_STATE_PATHS["codex_home"], "codex", "PROTECTED_STATE", "Codex home state is never auto-deleted.")
    add_record("claude_home", PROTECTED_STATE_PATHS["claude_home"], "claude", "PROTECTED_STATE", "Claude home state is never auto-deleted.")
    add_record("codex_support", PROTECTED_STATE_PATHS["codex_support"], "codex", "PROTECTED_STATE", "Codex application support contains sessions and state.")
    add_record("claude_support", PROTECTED_STATE_PATHS["claude_support"], "claude", "PROTECTED_STATE", "Claude application support contains sessions and state.")

    library_caches = SAFE_CACHE_PATHS["library_caches"]
    for basename in CLAUDE_LIBRARY_CACHE_BASENAMES + CODEX_LIBRARY_CACHE_BASENAMES:
        path = library_caches / basename
        if path.exists():
            family = "claude" if "anthropic" in basename or "claude" in basename else "codex"
            classification = "PROTECTED_STATE" if basename in family_summaries.get(family, {}).get("protected_library_caches", []) else "SAFE_CACHE"
            add_record(f"library_cache:{basename}", path, family, classification, "Protected if the owning app family is active.")

    for dirname in CLAUDE_SUPPORT_CACHE_DIRS:
        path = PROTECTED_STATE_PATHS["claude_support"] / dirname
        if path.exists():
            classification = "SAFE_CACHE" if family_summaries["claude"]["state"] in {"inactive", "residual_data_only"} else "PROTECTED_STATE"
            add_record(f"claude_support_cache:{dirname}", path, "claude", classification, "Claude support cache directory.")

    for dirname in CODEX_SUPPORT_CACHE_DIRS:
        path = PROTECTED_STATE_PATHS["codex_support"] / dirname
        if path.exists():
            classification = "SAFE_CACHE" if family_summaries["codex"]["state"] == "inactive" else "PROTECTED_STATE"
            add_record(f"codex_support_cache:{dirname}", path, "codex", classification, "Codex support cache directory.")

    return records, protected, manual


def list_docker_inventory() -> DockerInventory:
    info_result = run_command(["docker", "info", "--format", "{{json .}}"], timeout=3)
    engine_state = "reachable" if info_result["ok"] else "timed_out" if info_result["timed_out"] else "unreachable"
    inventory = DockerInventory(engine_available=info_result["ok"], engine_state=engine_state)
    if info_result["timed_out"]:
        inventory.timed_out_commands.append("docker info")
    elif info_result["ok"]:
        try:
            inventory.info = json.loads(info_result["stdout"].strip())
        except json.JSONDecodeError:
            inventory.raw_text["docker_info"] = info_result["stdout"]

    def json_lines(command: List[str], timeout: int, field: str) -> List[Dict[str, Any]]:
        result = run_command(command, timeout=timeout)
        if result["timed_out"]:
            inventory.timed_out_commands.append(" ".join(command[:3]))
            return []
        if not result["ok"]:
            return []
        rows: List[Dict[str, Any]] = []
        for line in result["stdout"].splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                inventory.raw_text[field] = result["stdout"]
                return []
        return rows

    inventory.containers = json_lines(["docker", "ps", "-a", "--format", "{{json .}}"], 4, "containers")
    inventory.dangling_images = json_lines(
        ["docker", "image", "ls", "--filter", "dangling=true", "--format", "{{json .}}"],
        4,
        "images",
    )
    inventory.volumes = json_lines(["docker", "volume", "ls", "--format", "{{json .}}"], 4, "volumes")
    inventory.networks = json_lines(["docker", "network", "ls", "--format", "{{json .}}"], 4, "networks")
    system_df = run_command(["docker", "system", "df", "-v"], timeout=6)
    if system_df["timed_out"]:
        inventory.timed_out_commands.append("docker system df")
    elif system_df["ok"]:
        inventory.raw_text["system_df"] = system_df["stdout"]

    running_containers = 0
    exited_containers = 0
    for row in inventory.containers:
        state = str(row.get("State", "")).lower()
        status = str(row.get("Status", "")).lower()
        if state == "running" or status.startswith("up "):
            running_containers += 1
        else:
            exited_containers += 1

    inventory.reclaimable_summary = {
        "running_containers": running_containers,
        "exited_containers": exited_containers,
        "dangling_images": len(inventory.dangling_images),
        "volumes": len(inventory.volumes),
        "networks": len(inventory.networks),
    }
    return inventory


def capture_snapshot(mode: str = "balanced") -> Dict[str, Any]:
    started_at = now_iso()
    run_id = uuid.uuid4().hex[:12]
    disk = shutil.disk_usage(str(Path.home()))
    processes = list_processes()
    for process in processes:
        classify_process_role(process)
    by_pid = {process.pid: process for process in processes}
    current_pid = os.getpid()
    docker_inventory = list_docker_inventory()
    family_summaries = {
        family: summarize_family(
            family,
            processes,
            by_pid,
            {current_pid, os.getppid()},
            docker_inventory=docker_inventory if family == "docker" else None,
        )
        for family in FAMILIES
    }
    classify_processes(processes, family_summaries)
    attach_classification_counts(processes, family_summaries)
    storage_records, protected_items, manual_review_items = gather_storage_records(family_summaries)

    return {
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": now_iso(),
        "mode": mode,
        "host_disk_total_bytes": disk.total,
        "host_disk_used_bytes": disk.used,
        "host_disk_free_bytes": disk.free,
        "processes": [process.to_dict() for process in processes],
        "process_summary": family_summaries,
        "storage_records": [record.to_dict() for record in storage_records],
        "protected_items": [record.to_dict() for record in protected_items],
        "manual_review_items": [record.to_dict() for record in manual_review_items],
        "docker_inventory": docker_inventory.to_dict(),
    }


def protected_library_cache_basenames(snapshot: Dict[str, Any]) -> List[str]:
    protected: List[str] = []
    for family in ("claude", "codex"):
        protected.extend(snapshot["process_summary"][family].get("protected_library_caches", []))
    return sorted(set(protected))


def family_summary_from_actions(
    snapshot: Dict[str, Any],
    actions: List[CleanupAction],
) -> Dict[str, Dict[str, Any]]:
    summary: Dict[str, Dict[str, Any]] = {}
    for family in ("docker", "claude", "codex", "system"):
        family_actions = [action for action in actions if action.family == family]
        process_summary = snapshot.get("process_summary", {}).get(family, {})
        summary[family] = {
            "state": process_summary.get("state", "n/a"),
            "recommended_action": process_summary.get("recommended_action", "protect_only"),
            "process_counts": process_summary.get("process_counts", {}),
            "inventory_counts": process_summary.get("inventory_counts", {}),
            "actions": len(family_actions),
            "bytes_reclaimed": sum(action.bytes_reclaimed for action in family_actions),
            "results": {
                result: sum(1 for action in family_actions if action.result == result)
                for result in {"planned", "deleted", "blocked", "kept", "skipped", "missing", "failed", "terminated"}
            },
        }
    return summary


def plan_cleanup(snapshot: Dict[str, Any], mode: str = "balanced") -> List[CleanupAction]:
    actions: List[CleanupAction] = []
    processes = [ProcessRecord(**item) for item in snapshot["processes"]]
    for process in processes:
        if process.classification not in {"STALE_CLI", "STALE_HELPER"}:
            continue
        if mode == "safe":
            actions.append(
                CleanupAction(
                    target=str(process.pid),
                    target_type="process",
                    family=process.family,
                    classification=process.classification,
                    result="planned",
                    bytes_reclaimed=process.rss_kb * 1024,
                    reason="Would terminate stale helper or CLI probe process in balanced or max mode.",
                    details={
                        "pid": process.pid,
                        "args": process.args,
                        "elapsed_seconds": process.elapsed_seconds,
                        "apply_allowed": False,
                    },
                )
            )
            continue
        actions.append(
            CleanupAction(
                target=str(process.pid),
                target_type="process",
                family=process.family,
                classification=process.classification,
                result="planned",
                bytes_reclaimed=process.rss_kb * 1024,
                reason="Stale helper or CLI probe process with low activity and no active parent chain.",
                details={
                    "pid": process.pid,
                    "args": process.args,
                    "elapsed_seconds": process.elapsed_seconds,
                    "apply_allowed": True,
                },
            )
        )

    def safe_delete_action(label: str, path: Path, family: str, reason: str) -> None:
        actions.append(
            CleanupAction(
                target=str(path),
                target_type="path",
                family=family,
                classification="SAFE_CACHE",
                result="planned",
                bytes_reclaimed=du_bytes(path),
                reason=reason,
                details={"label": label, "apply_allowed": True},
            )
        )

    safe_delete_action("uv_cache", SAFE_CACHE_PATHS["uv_cache"], "system", "Regenerable uv cache.")
    safe_delete_action("trunk_cache", SAFE_CACHE_PATHS["trunk_cache"], "system", "Regenerable trunk cache.")
    safe_delete_action("gradle_cache", SAFE_CACHE_PATHS["gradle_cache"], "system", "Regenerable Gradle cache.")
    safe_delete_action("npm_cache", SAFE_CACHE_PATHS["npm_cache"], "system", "Regenerable npm cache.")
    safe_delete_action("npx_cache", SAFE_CACHE_PATHS["npx_cache"], "system", "Regenerable npx cache.")
    safe_delete_action("library_caches", SAFE_CACHE_PATHS["library_caches"], "system", "Remove unprotected library caches.")

    process_summary = snapshot["process_summary"]
    if mode in {"balanced", "max"} and process_summary["docker"]["recommended_action"] == "docker_system_prune":
        actions.append(
            CleanupAction(
                target="docker_system_prune",
                target_type="docker",
                family="docker",
                classification="SAFE_CACHE",
                result="planned",
                bytes_reclaimed=0,
                reason="Prune stopped containers, dangling images, and build cache via Docker daemon.",
                details={
                    "apply_allowed": True,
                    "inventory_counts": process_summary["docker"].get("inventory_counts", {}),
                },
            )
        )

    if mode == "max":
        claude_state = process_summary["claude"]["state"]
        codex_state = process_summary["codex"]["state"]
        if claude_state in {"inactive", "residual_data_only"}:
            for dirname in CLAUDE_SUPPORT_CACHE_DIRS:
                path = PROTECTED_STATE_PATHS["claude_support"] / dirname
                safe_delete_action(f"claude_support_cache:{dirname}", path, "claude", "Claude support cache while inactive.")
        if codex_state == "inactive":
            for dirname in CODEX_SUPPORT_CACHE_DIRS:
                path = PROTECTED_STATE_PATHS["codex_support"] / dirname
                safe_delete_action(f"codex_support_cache:{dirname}", path, "codex", "Codex support cache while inactive.")

    return actions


def path_delete(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


def prune_history_files(output_dir: Path, keep: int = DEFAULT_RETENTION_COUNT) -> List[str]:
    removed: List[str] = []
    if keep < 1 or not output_dir.exists():
        return removed
    for pattern in TIMESTAMPED_REPORT_GLOBS:
        matches = sorted(output_dir.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True)
        for path in matches[keep:]:
            path.unlink(missing_ok=True)
            removed.append(path.name)
    return removed


def prune_rotated_logs(output_dir: Path, keep: int = DEFAULT_LOG_RETENTION_COUNT) -> List[str]:
    removed: List[str] = []
    if keep < 0 or not output_dir.exists():
        return removed
    for stem in ("launchd.stdout.log", "launchd.stderr.log"):
        matches = sorted(output_dir.glob(f"{stem}.*"), key=lambda item: item.stat().st_mtime, reverse=True)
        for path in matches[keep:]:
            path.unlink(missing_ok=True)
            removed.append(path.name)
    return removed


def remove_unprotected_library_caches(protected_basenames: List[str]) -> int:
    cache_root = SAFE_CACHE_PATHS["library_caches"]
    if not cache_root.exists():
        return 0
    reclaimed = 0
    for child in cache_root.iterdir():
        if child.name in protected_basenames:
            continue
        reclaimed += du_bytes(child)
        path_delete(child)
    return reclaimed


def terminate_process(pid: int) -> bool:
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return True
    except PermissionError:
        return False
    time.sleep(0.4)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        return True
    except PermissionError:
        return False
    time.sleep(0.2)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    return False


def apply_actions(
    snapshot: Dict[str, Any],
    actions: List[CleanupAction],
    dry_run: bool,
) -> List[CleanupAction]:
    protected_caches = protected_library_cache_basenames(snapshot)
    applied: List[CleanupAction] = []
    for action in actions:
        realized = CleanupAction(**asdict(action))
        if dry_run:
            realized.result = "planned"
            applied.append(realized)
            continue

        try:
            if not action.details.get("apply_allowed", True):
                realized.result = "kept"
                realized.reason = "This action is preview-only in safe mode."
                applied.append(realized)
                continue
            if action.target_type == "process":
                pid = int(action.target)
                success = terminate_process(pid)
                realized.result = "terminated" if success else "blocked"
                if not success:
                    realized.reason = "Process could not be terminated safely."
            elif action.target_type == "path":
                path = Path(action.target)
                if action.target.endswith("Library/Caches"):
                    realized.bytes_reclaimed = remove_unprotected_library_caches(protected_caches)
                    realized.result = "deleted"
                elif path.exists():
                    realized.bytes_reclaimed = du_bytes(path)
                    path_delete(path)
                    realized.result = "deleted"
                else:
                    realized.result = "missing"
            elif action.target_type == "docker":
                if snapshot["process_summary"]["docker"]["recommended_action"] != "docker_system_prune":
                    realized.result = "blocked"
                    realized.reason = "Docker daemon state did not allow safe prune."
                else:
                    for command in (
                        ["docker", "container", "prune", "-f"],
                        ["docker", "image", "prune", "-f"],
                        ["docker", "builder", "prune", "-f"],
                    ):
                        run_command(command, timeout=10)
                    realized.result = "deleted"
            else:
                realized.result = "skipped"
        except Exception as exc:  # pragma: no cover - defensive fallback
            realized.result = "failed"
            realized.reason = f"{action.reason} ({exc})"
        applied.append(realized)
    return applied


def build_cleanup_report(
    before_snapshot: Dict[str, Any],
    after_snapshot: Dict[str, Any],
    actions: List[CleanupAction],
    mode: str,
    dry_run: bool,
) -> CleanupReport:
    storage_before = before_snapshot["host_disk_used_bytes"]
    storage_after = after_snapshot["host_disk_used_bytes"]
    planned_bytes = sum(action.bytes_reclaimed for action in actions)
    storage_reclaimed = planned_bytes if dry_run else max(storage_before - storage_after, planned_bytes)

    memory_before = sum(item["rss_kb"] for item in before_snapshot["processes"]) / 1024.0
    memory_reclaimed = sum(action.bytes_reclaimed for action in actions if action.target_type == "process") / (1024.0 * 1024.0)
    memory_after = max(0.0, memory_before - memory_reclaimed)

    processes_trimmed = sum(1 for action in actions if action.target_type == "process" and action.result in {"planned", "terminated"})
    objects_pruned = sum(1 for action in actions if action.target_type != "process" and action.result in {"planned", "deleted"})

    return CleanupReport(
        run_id=before_snapshot["run_id"],
        started_at=before_snapshot["started_at"],
        finished_at=after_snapshot["finished_at"],
        mode=mode,
        dry_run=dry_run,
        storage_before_bytes=storage_before,
        storage_after_bytes=storage_after,
        storage_reclaimed_bytes=storage_reclaimed,
        memory_before_estimate_mb=round(memory_before, 2),
        memory_after_estimate_mb=round(memory_after, 2),
        memory_reclaimed_estimate_mb=round(memory_reclaimed, 2),
        processes_scanned=len(before_snapshot["processes"]),
        processes_trimmed=processes_trimmed,
        objects_pruned=objects_pruned,
        protected_items=before_snapshot["protected_items"],
        manual_review_items=before_snapshot["manual_review_items"],
        family_summaries=family_summary_from_actions(before_snapshot, actions),
        actions=actions,
        snapshot=before_snapshot,
    )


def default_report_dir() -> Path:
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    return REPORT_ROOT
