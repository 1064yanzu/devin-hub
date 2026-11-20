"""Command-line interface: server, example, git scan, and alerts."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .api import serve


def hub_url() -> str:
    return os.environ.get("DEVIN_HUB_URL", "http://127.0.0.1:8765").rstrip("/")


def request(method: str, path: str, payload: dict | None = None) -> dict:
    token = os.environ.get("DEVIN_HUB_TOKEN")
    if not token:
        raise RuntimeError("Set DEVIN_HUB_TOKEN before using the API")
    raw = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(
        hub_url() + path, data=raw, method=method,
        headers={"Authorization": "Bearer " + token,
                 "Content-Type": "application/json"},
    )
    with urlopen(req, timeout=10) as response:
        return json.load(response)


def submit(event: dict) -> None:
    print(json.dumps(request("POST", "/v1/events", event), indent=2))


def git_output(path: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(path), *args], text=True, capture_output=True,
        timeout=15, check=True,
    )
    return proc.stdout.strip()


def scan(path: str, node: str, project: str) -> dict:
    root = Path(path).resolve()
    branch = git_output(root, "branch", "--show-current") or "detached"
    # Includes staged, unstaged, and untracked paths; no source code is uploaded.
    changed = set(filter(None, git_output(root, "diff", "--name-only", "HEAD").splitlines()))
    changed.update(filter(None, git_output(root, "ls-files", "--others", "--exclude-standard").splitlines()))
    changed = sorted(changed)[:500]
    return {
        "id": str(uuid.uuid4()),
        "node_id": node,
        "project_id": project,
        "kind": "git.diff",
        "payload": {"branch": branch, "changed_files": changed},
    }


def main():
    parser = argparse.ArgumentParser(description="Devin Hub local-first prototype")
    commands = parser.add_subparsers(dest="command", required=True)
    p_server = commands.add_parser("server", help="Start local HTTP hub")
    p_server.add_argument("--host", default="127.0.0.1")
    p_server.add_argument("--port", type=int, default=8765)
    p_server.add_argument("--db", default="./data/events.sqlite3")
    p_example = commands.add_parser("send-example", help="Send a synthetic failed-test event")
    p_example.add_argument("--node", default="mac-dev")
    p_example.add_argument("--project", default="demo")
    p_scan = commands.add_parser("git-scan", help="Send Git file-name metadata only")
    p_scan.add_argument("--path", default=".")
    p_scan.add_argument("--node", default="mac-dev")
    p_scan.add_argument("--project", default="demo")
    commands.add_parser("alerts", help="Print recorded alerts")
    args = parser.parse_args()

    try:
        if args.command == "server":
            serve(args.host, args.port, args.db, os.environ.get("DEVIN_HUB_TOKEN", ""))
        elif args.command == "send-example":
            submit({
                "id": str(uuid.uuid4()), "node_id": args.node,
                "project_id": args.project, "kind": "test.result",
                "payload": {"suite": "sample-tests", "passed": False},
            })
        elif args.command == "git-scan":
            submit(scan(args.path, args.node, args.project))
        elif args.command == "alerts":
            print(json.dumps(request("GET", "/v1/alerts"), indent=2))
    except (RuntimeError, ValueError, OSError, subprocess.CalledProcessError,
            subprocess.TimeoutExpired, URLError, HTTPError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
