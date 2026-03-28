from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional


LABEL = "io.dreamcleanr.cleanup"


def launch_agent_path() -> Path:
    return Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"


def write_launch_agent(
    *,
    repo_root: Path,
    output_dir: Path,
    hour: int,
    minute: int,
    mode: str,
    retention_count: int,
) -> Path:
    plist_path = launch_agent_path()
    plist_path.parent.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = output_dir / "launchd.stdout.log"
    stderr_path = output_dir / "launchd.stderr.log"
    python_exe = sys.executable
    latest_json = output_dir / "latest.json"
    plist_path.write_text(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>{LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>{python_exe}</string>
    <string>-m</string>
    <string>dreamcleanr</string>
    <string>clean</string>
    <string>--apply</string>
    <string>--mode</string>
    <string>{mode}</string>
    <string>--output-dir</string>
    <string>{output_dir}</string>
    <string>--retention-count</string>
    <string>{retention_count}</string>
    <string>--json-out</string>
    <string>{latest_json}</string>
  </array>
  <key>WorkingDirectory</key>
  <string>{repo_root}</string>
  <key>StandardOutPath</key>
  <string>{stdout_path}</string>
  <key>StandardErrorPath</key>
  <string>{stderr_path}</string>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>{hour}</integer>
    <key>Minute</key>
    <integer>{minute}</integer>
  </dict>
  <key>ProcessType</key>
  <string>Background</string>
</dict>
</plist>
""",
        encoding="utf-8",
    )
    return plist_path


def install_launch_agent(plist_path: Path) -> None:
    subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}", str(plist_path)], check=False, capture_output=True, text=True)
    subprocess.run(["launchctl", "bootstrap", f"gui/{os.getuid()}", str(plist_path)], check=True)
    subprocess.run(["launchctl", "enable", f"gui/{os.getuid()}/{LABEL}"], check=False, capture_output=True, text=True)


def uninstall_launch_agent() -> Optional[Path]:
    plist_path = launch_agent_path()
    if plist_path.exists():
        subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}", str(plist_path)], check=False, capture_output=True, text=True)
        plist_path.unlink()
        return plist_path
    return None
