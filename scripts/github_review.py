#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


def iso_to_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def days_since(value: str) -> int:
    return (datetime.now(timezone.utc) - iso_to_datetime(value)).days


def api_request(
    repo: str,
    path: str,
    *,
    token: Optional[str] = None,
    method: str = "GET",
    body: Optional[Dict[str, Any]] = None,
) -> Any:
    url = f"https://api.github.com/repos/{repo}{path}"
    payload = None if body is None else json.dumps(body).encode("utf-8")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "dreamcleanr-governance-review",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, data=payload, headers=headers, method=method)
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def issue_comment_request(
    repo: str,
    issue_number: int,
    token: str,
    body: str,
) -> Any:
    return api_request(
        repo,
        f"/issues/{issue_number}/comments",
        token=token,
        method="POST",
        body={"body": body},
    )


def ensure_issue(repo: str, token: Optional[str], title: str, labels: Iterable[str]) -> Optional[int]:
    if not token:
        return None
    issues = api_request(repo, "/issues?state=open&per_page=100", token=token)
    for issue in issues:
        if issue.get("title") == title and "pull_request" not in issue:
            return int(issue["number"])

    created = api_request(
        repo,
        "/issues",
        token=token,
        method="POST",
        body={"title": title, "labels": list(labels)},
    )
    return int(created["number"])


def fetch_site_status(url: str) -> str:
    try:
        request = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(request) as response:
            return str(response.status)
    except urllib.error.HTTPError as exc:
        return str(exc.code)


def fetch_governance_summary(repo: str) -> Dict[str, Any]:
    latest_release = api_request(repo, "/releases/latest")
    workflow_runs = api_request(repo, "/actions/runs?per_page=10")
    issues = api_request(repo, "/issues?state=open&per_page=100")
    pulls = api_request(repo, "/pulls?state=open&per_page=100")

    open_issues = [issue for issue in issues if "pull_request" not in issue]
    stale_issues = [issue for issue in open_issues if days_since(issue["created_at"]) >= 14]
    dependabot_pulls = [pull for pull in pulls if pull.get("user", {}).get("login") == "app/dependabot"]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "latest_release": {
            "tag": latest_release["tag_name"],
            "published_at": latest_release["published_at"],
            "age_days": days_since(latest_release["published_at"]),
            "asset_count": len(latest_release.get("assets", [])),
        },
        "workflow_runs": [
            {
                "name": run["name"],
                "status": run["status"],
                "conclusion": run.get("conclusion"),
                "event": run["event"],
            }
            for run in workflow_runs.get("workflow_runs", [])
        ],
        "issues": {
            "open_count": len(open_issues),
            "stale_count": len(stale_issues),
            "stale_titles": [issue["title"] for issue in stale_issues[:10]],
        },
        "dependabot": {
            "open_pr_count": len(dependabot_pulls),
            "titles": [pull["title"] for pull in dependabot_pulls[:10]],
        },
        "public_surface": {
            "site_status": fetch_site_status("https://jlsport18.github.io/DreamCleanr/"),
            "latest_release_status": fetch_site_status("https://github.com/jlsport18/DreamCleanr/releases/latest"),
            "latest_asset_status": fetch_site_status(
                "https://github.com/jlsport18/DreamCleanr/releases/latest/download/dreamcleanr-latest-py3-none-any.whl"
            ),
            "install_script_status": fetch_site_status(
                "https://raw.githubusercontent.com/jlsport18/DreamCleanr/main/scripts/install.sh"
            ),
            "update_script_status": fetch_site_status(
                "https://raw.githubusercontent.com/jlsport18/DreamCleanr/main/scripts/update.sh"
            ),
        },
    }


def fetch_business_summary(repo: str) -> Dict[str, Any]:
    releases = api_request(repo, "/releases?per_page=20")
    issues = api_request(repo, "/issues?state=open&per_page=100")
    release_downloads = []
    total_downloads = 0
    for release in releases:
        downloads = sum(asset.get("download_count", 0) for asset in release.get("assets", []))
        total_downloads += downloads
        release_downloads.append(
            {
                "tag": release["tag_name"],
                "published_at": release["published_at"],
                "asset_downloads": downloads,
            }
        )

    open_issues = [issue for issue in issues if "pull_request" not in issue]
    install_friction = [
        issue
        for issue in open_issues
        if any(label["name"] in {"distribution", "launch", "maintenance"} for label in issue.get("labels", []))
    ]
    monetization = [
        issue
        for issue in open_issues
        if any(label["name"] in {"monetization", "market-research"} for label in issue.get("labels", []))
    ]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "release_downloads": release_downloads,
        "total_downloads": total_downloads,
        "install_friction": {
            "count": len(install_friction),
            "titles": [issue["title"] for issue in install_friction[:10]],
        },
        "monetization_queue": {
            "count": len(monetization),
            "titles": [issue["title"] for issue in monetization[:10]],
        },
        "monetization_readiness": {
            "green_install_channel": total_downloads >= 0,
            "open_distribution_issues": len(install_friction),
            "open_monetization_issues": len(monetization),
        },
    }


def render_governance_markdown(summary: Dict[str, Any]) -> str:
    lines = [
        "# DreamCleanr Governance Review",
        "",
        f"- Generated: `{summary['generated_at']}`",
        f"- Latest release: `{summary['latest_release']['tag']}` ({summary['latest_release']['age_days']} days old)",
        f"- Open issues: `{summary['issues']['open_count']}`",
        f"- Stale issues (14d+): `{summary['issues']['stale_count']}`",
        f"- Open Dependabot PRs: `{summary['dependabot']['open_pr_count']}`",
        "",
        "## Public Surface",
        "",
        f"- Site: `{summary['public_surface']['site_status']}`",
        f"- Latest release page: `{summary['public_surface']['latest_release_status']}`",
        f"- Latest wheel asset: `{summary['public_surface']['latest_asset_status']}`",
        f"- Install script: `{summary['public_surface']['install_script_status']}`",
        f"- Update script: `{summary['public_surface']['update_script_status']}`",
        "",
        "## Recent Workflow Runs",
        "",
    ]
    for run in summary["workflow_runs"][:8]:
        lines.append(f"- `{run['name']}` -> `{run['status']}` / `{run['conclusion']}` via `{run['event']}`")
    lines.extend(["", "## Stale Issues", ""])
    if summary["issues"]["stale_titles"]:
        lines.extend([f"- {title}" for title in summary["issues"]["stale_titles"]])
    else:
        lines.append("- None")
    if summary["dependabot"]["titles"]:
        lines.extend(["", "## Dependabot Queue", ""])
        lines.extend([f"- {title}" for title in summary["dependabot"]["titles"]])
    return "\n".join(lines) + "\n"


def render_business_markdown(summary: Dict[str, Any]) -> str:
    lines = [
        "# DreamCleanr Business And Architecture Review",
        "",
        f"- Generated: `{summary['generated_at']}`",
        f"- Total release-asset downloads: `{summary['total_downloads']}`",
        f"- Open install/distribution issues: `{summary['install_friction']['count']}`",
        f"- Open monetization issues: `{summary['monetization_queue']['count']}`",
        "",
        "## Release Trend",
        "",
    ]
    for release in summary["release_downloads"][:10]:
        lines.append(
            f"- `{release['tag']}` -> `{release['asset_downloads']}` downloads, published `{release['published_at']}`"
        )
    lines.extend(["", "## Install Friction Queue", ""])
    if summary["install_friction"]["titles"]:
        lines.extend([f"- {title}" for title in summary["install_friction"]["titles"]])
    else:
        lines.append("- None")
    lines.extend(["", "## Monetization Queue", ""])
    if summary["monetization_queue"]["titles"]:
        lines.extend([f"- {title}" for title in summary["monetization_queue"]["titles"]])
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Monetization Gates",
            "",
            f"- Evergreen install channel healthy: `{summary['monetization_readiness']['green_install_channel']}`",
            f"- Distribution issues still open: `{summary['monetization_readiness']['open_distribution_issues']}`",
            f"- Monetization/planning issues still open: `{summary['monetization_readiness']['open_monetization_issues']}`",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["governance", "business"])
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "jlsport18/DreamCleanr"))
    parser.add_argument("--output", required=True)
    parser.add_argument("--issue-title")
    parser.add_argument("--issue-label", action="append", default=[])
    parser.add_argument("--post-to-issue", action="store_true")
    args = parser.parse_args(argv)

    token = os.environ.get("GITHUB_TOKEN")
    if args.mode == "governance":
        summary = fetch_governance_summary(args.repo)
        markdown = render_governance_markdown(summary)
    else:
        summary = fetch_business_summary(args.repo)
        markdown = render_business_markdown(summary)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    output_path.with_suffix(".json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    if args.post_to_issue and args.issue_title:
        issue_number = ensure_issue(args.repo, token, args.issue_title, args.issue_label)
        if issue_number is not None:
            issue_comment_request(args.repo, issue_number, token, markdown)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
