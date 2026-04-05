from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from . import __version__
from .core import build_cleanup_report, capture_snapshot, default_report_dir, plan_cleanup
from .reporting import write_html
from .scheduler import LABEL, launch_agent_path

SERVER_NAME = "dreamcleanr"
LATEST_PROTOCOL_VERSION = "2025-11-25"
SUPPORTED_PROTOCOL_VERSIONS = [
    LATEST_PROTOCOL_VERSION,
    "2025-06-18",
    "2025-03-26",
    "2024-11-05",
    "2024-10-07",
]


class McpProtocolError(Exception):
    def __init__(self, code: int, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


ToolHandler = Callable[[Dict[str, Any]], Dict[str, Any]]


def _text_result(text: str, structured: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "content": [
            {
                "type": "text",
                "text": text,
            }
        ]
    }
    if structured is not None:
        result["structuredContent"] = structured
    return result


def _tool_schema() -> Dict[str, Dict[str, Any]]:
    return {
        "scan": {
            "description": "Capture a DreamCleanr machine snapshot without changing state.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["safe", "balanced", "max"],
                        "default": "balanced",
                    }
                },
                "additionalProperties": False,
            },
            "annotations": {
                "title": "DreamCleanr Scan",
                "readOnlyHint": True,
                "openWorldHint": False,
            },
        },
        "clean_preview": {
            "description": "Preview a cleanup plan and receipt without deleting anything.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["safe", "balanced", "max"],
                        "default": "balanced",
                    },
                    "scope": {
                        "type": "string",
                        "enum": ["all", "processes", "storage"],
                        "default": "all",
                    },
                },
                "additionalProperties": False,
            },
            "annotations": {
                "title": "DreamCleanr Preview Cleanup",
                "readOnlyHint": True,
                "openWorldHint": False,
            },
        },
        "report_render": {
            "description": "Render an HTML cleanup receipt from the latest or specified DreamCleanr JSON report.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "input": {"type": "string"},
                    "html_out": {"type": "string"},
                },
                "additionalProperties": False,
            },
            "annotations": {
                "title": "DreamCleanr Render Report",
                "readOnlyHint": True,
                "openWorldHint": False,
            },
        },
        "schedule_status": {
            "description": "Inspect the DreamCleanr launch agent and current scheduled cleanup state.",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
            "annotations": {
                "title": "DreamCleanr Schedule Status",
                "readOnlyHint": True,
                "openWorldHint": False,
            },
        },
        "schedule_preview": {
            "description": "Preview the launchd configuration DreamCleanr would install for nightly cleanup.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "hour": {"type": "integer", "default": 4},
                    "minute": {"type": "integer", "default": 30},
                    "mode": {
                        "type": "string",
                        "enum": ["safe", "balanced", "max"],
                        "default": "balanced",
                    },
                    "retention_count": {"type": "integer", "default": 21},
                },
                "additionalProperties": False,
            },
            "annotations": {
                "title": "DreamCleanr Schedule Preview",
                "readOnlyHint": True,
                "openWorldHint": False,
            },
        },
    }


def _tool_list() -> list[dict[str, Any]]:
    specs = _tool_schema()
    return [
        {
            "name": name,
            "description": spec["description"],
            "inputSchema": spec["inputSchema"],
            "annotations": spec["annotations"],
        }
        for name, spec in specs.items()
    ]


def tool_scan(arguments: Dict[str, Any]) -> Dict[str, Any]:
    mode = str(arguments.get("mode", "balanced"))
    snapshot = capture_snapshot(mode=mode)
    summary = {
        family: {
            "state": data["state"],
            "recommended_action": data["recommended_action"],
            "stale": data.get("process_counts", {}).get("stale", 0),
        }
        for family, data in snapshot.get("process_summary", {}).items()
    }
    detectors = {
        item["key"]: {
            "title": item["title"],
            "status": item["status"],
            "total_bytes": item["total_bytes"],
            "path_count": item["path_count"],
            "cleanup_ready": item["cleanup_ready"],
            "safety_state": item.get("safety_state", "visibility_only"),
            "active_project_count": item.get("active_project_count", 0),
        }
        for item in snapshot.get("detector_findings", [])
    }
    projects = {
        "summary": snapshot.get("project_summary", {}),
        "signals": snapshot.get("project_signals", []),
    }
    text = (
        f"DreamCleanr scan complete in {mode} mode. "
        f"Free space: {snapshot['host_disk_free_bytes']} bytes. "
        f"Docker={summary.get('docker', {}).get('state', 'n/a')}, "
        f"Claude={summary.get('claude', {}).get('state', 'n/a')}, "
        f"Codex={summary.get('codex', {}).get('state', 'n/a')}."
    )
    if detectors:
        observed = ", ".join(item["title"] for item in snapshot.get("detector_findings", [])[:3])
        text += f" Observed additional developer surfaces: {observed}."
    project_count = int(snapshot.get("project_summary", {}).get("active_project_count", 0))
    if project_count:
        text += f" Active project signals: {project_count}."
    return _text_result(text, {"snapshot": snapshot, "summary": summary, "detectors": detectors, "projects": projects})


def tool_clean_preview(arguments: Dict[str, Any]) -> Dict[str, Any]:
    mode = str(arguments.get("mode", "balanced"))
    scope = str(arguments.get("scope", "all"))
    before = capture_snapshot(mode=mode)
    actions = plan_cleanup(before, mode=mode)
    if scope == "processes":
        actions = [action for action in actions if action.target_type == "process"]
    elif scope == "storage":
        actions = [action for action in actions if action.target_type != "process"]
    report = build_cleanup_report(before, before, actions, mode=mode, dry_run=True).to_dict()
    text = (
        f"DreamCleanr preview prepared in {mode} mode with scope={scope}. "
        f"Processes trimmed: {report['processes_trimmed']}. "
        f"Objects planned: {report['objects_pruned']}."
    )
    return _text_result(text, report)


def tool_report_render(arguments: Dict[str, Any]) -> Dict[str, Any]:
    input_path = Path(arguments.get("input") or default_report_dir() / "latest.json").expanduser()
    if not input_path.exists():
        raise McpProtocolError(-32602, f"Report JSON not found: {input_path}")
    report = json.loads(input_path.read_text(encoding="utf-8"))
    html_out = Path(arguments.get("html_out") or input_path.with_suffix(".html")).expanduser()
    write_html(report, html_out)
    return _text_result(
        f"DreamCleanr HTML report rendered to {html_out}",
        {"input": str(input_path), "html_out": str(html_out)},
    )


def _launchctl_status() -> str:
    plist = launch_agent_path()
    if not plist.exists():
        return "not_installed"
    rc = os.system(f'launchctl print "gui/{os.getuid()}/{LABEL}" >/dev/null 2>&1')
    return "loaded" if rc == 0 else "installed_unloaded"


def tool_schedule_status(_: Dict[str, Any]) -> Dict[str, Any]:
    plist = launch_agent_path()
    output_dir = default_report_dir()
    payload = {
        "label": LABEL,
        "launch_agent_path": str(plist),
        "exists": plist.exists(),
        "status": _launchctl_status(),
        "latest_report": str(output_dir / "latest.json"),
        "latest_html": str(output_dir / "latest.html"),
    }
    return _text_result(
        f"DreamCleanr schedule status: {payload['status']}. LaunchAgent path: {payload['launch_agent_path']}.",
        payload,
    )


def tool_schedule_preview(arguments: Dict[str, Any]) -> Dict[str, Any]:
    hour = int(arguments.get("hour", 4))
    minute = int(arguments.get("minute", 30))
    mode = str(arguments.get("mode", "balanced"))
    retention_count = int(arguments.get("retention_count", 21))
    payload = {
        "label": LABEL,
        "hour": hour,
        "minute": minute,
        "mode": mode,
        "retention_count": retention_count,
        "command": ["dreamcleanr", "clean", "--apply", "--mode", mode, "--retention-count", str(retention_count)],
    }
    return _text_result(
        f"DreamCleanr would schedule a {mode} cleanup at {hour:02d}:{minute:02d} with retention_count={retention_count}.",
        payload,
    )


TOOL_HANDLERS: Dict[str, ToolHandler] = {
    "scan": tool_scan,
    "clean_preview": tool_clean_preview,
    "report_render": tool_report_render,
    "schedule_status": tool_schedule_status,
    "schedule_preview": tool_schedule_preview,
}


def _read_message() -> Optional[Dict[str, Any]]:
    content_length: Optional[int] = None
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        if line in (b"\r\n", b"\n"):
            break
        header = line.decode("utf-8").strip()
        if ":" not in header:
            continue
        name, value = header.split(":", 1)
        if name.lower() == "content-length":
            content_length = int(value.strip())
    if content_length is None:
        raise McpProtocolError(-32700, "Missing Content-Length header")
    body = sys.stdin.buffer.read(content_length)
    if not body:
        return None
    try:
        return json.loads(body.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise McpProtocolError(-32700, f"Invalid JSON: {exc}") from exc


def _write_message(payload: Dict[str, Any]) -> None:
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    sys.stdout.buffer.write(f"Content-Length: {len(raw)}\r\n\r\n".encode("utf-8"))
    sys.stdout.buffer.write(raw)
    sys.stdout.buffer.flush()


def _response(request_id: Any, result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result,
    }


def _error_response(request_id: Any, code: int, message: str) -> Dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": code,
            "message": message,
        },
    }


def _handle_initialize(params: Dict[str, Any]) -> Dict[str, Any]:
    requested_version = str(params.get("protocolVersion", LATEST_PROTOCOL_VERSION))
    protocol_version = requested_version if requested_version in SUPPORTED_PROTOCOL_VERSIONS else LATEST_PROTOCOL_VERSION
    return {
        "protocolVersion": protocol_version,
        "capabilities": {
            "tools": {},
        },
        "serverInfo": {
            "name": SERVER_NAME,
            "version": __version__,
        },
    }


def _handle_tools_call(params: Dict[str, Any]) -> Dict[str, Any]:
    name = params.get("name")
    if not isinstance(name, str) or name not in TOOL_HANDLERS:
        raise McpProtocolError(-32602, f"Unknown tool: {name}")
    arguments = params.get("arguments") or {}
    if not isinstance(arguments, dict):
        raise McpProtocolError(-32602, "Tool arguments must be an object")
    return TOOL_HANDLERS[name](arguments)


def handle_request(message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    method = message.get("method")
    request_id = message.get("id")
    params = message.get("params") or {}

    if method == "notifications/initialized":
        return None
    if method == "ping":
        return _response(request_id, {})
    if method == "initialize":
        return _response(request_id, _handle_initialize(params))
    if method == "tools/list":
        return _response(request_id, {"tools": _tool_list()})
    if method == "tools/call":
        return _response(request_id, _handle_tools_call(params))
    raise McpProtocolError(-32601, f"Method not found: {method}")


def main() -> int:
    while True:
        try:
            message = _read_message()
            if message is None:
                return 0
            response = handle_request(message)
            if response is not None:
                _write_message(response)
        except McpProtocolError as exc:
            request_id = None
            try:
                request_id = message.get("id") if isinstance(message, dict) else None
            except Exception:
                request_id = None
            _write_message(_error_response(request_id, exc.code, exc.message))
        except Exception as exc:  # pragma: no cover - defensive protocol safety
            request_id = None
            try:
                request_id = message.get("id") if isinstance(message, dict) else None
            except Exception:
                request_id = None
            _write_message(_error_response(request_id, -32000, f"DreamCleanr MCP server error: {exc}"))


if __name__ == "__main__":
    raise SystemExit(main())
