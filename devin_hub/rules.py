"""Deterministic checks. These are heuristics, not AI code reviews."""

from __future__ import annotations

from pathlib import PurePosixPath


def review(event: dict) -> list[dict]:
    kind = event["kind"]
    payload = event.get("payload", {})
    alerts: list[dict] = []

    def add(rule: str, severity: str, summary: str, evidence: str, action: str):
        alerts.append({
            "rule": rule,
            "severity": severity,
            "summary": summary,
            "evidence": evidence,
            "suggested_action": action,
        })

    if kind == "test.result" and payload.get("passed") is False:
        add("failed_test", "high", "Test suite reported a failure",
            f"test.result passed=false; suite={str(payload.get('suite', 'unknown'))[:120]}",
            "Inspect failed tests and reproduce the failure before merging.")

    if kind == "shell.exit":
        status = payload.get("exit_code")
        if type(status) is int and status != 0:
            add("shell_failure", "medium", "A command exited unsuccessfully",
                f"shell.exit exit_code={status}",
                "Review the command output locally; do not upload shell secrets.")

    if kind in {"git.diff", "git.commit"}:
        paths = payload.get("changed_files", [])
        if isinstance(paths, list):
            paths = [p.replace("\\", "/") for p in paths if isinstance(p, str)][:500]
            dependencies = [
                p for p in paths if PurePosixPath(p).name in {
                    "package.json", "package-lock.json", "pnpm-lock.yaml",
                    "yarn.lock", "poetry.lock", "uv.lock", "requirements.txt",
                    "Cargo.lock", "go.mod", "go.sum", "Gemfile.lock",
                }
            ]
            migrations = [
                p for p in paths
                if any(segment in {"migrations", "migration"} for segment in PurePosixPath(p).parts)
                or PurePosixPath(p).name in {"schema.prisma", "schema.sql"}
            ]
            if dependencies:
                add("dependency_change", "medium", "Dependency manifest or lockfile changed",
                    "Changed paths: " + ", ".join(dependencies[:8]),
                    "Verify lockfile consistency and run dependency/install tests.")
            if migrations:
                add("schema_change", "medium", "Database schema or migration files changed",
                    "Changed paths: " + ", ".join(migrations[:8]),
                    "Check backwards compatibility, migration order, and rollback plan.")
    return alerts
