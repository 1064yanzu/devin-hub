# devin-hub

**A local-first, event-driven prototype for a personal multi-device development hub.**

Devin Hub explores a practical idea: a Mini PC can keep track of development events from a Mac and Windows workstation, preserve context, and warn about actionable risks *without waiting for a chat prompt*.

> **Status: experimental MVP.** The runnable implementation is a small Python standard-library HTTP service, SQLite event store, deterministic rules, and a Git metadata collector. Tailscale, NATS JetStream, gRPC, IDE integrations, cross-device reasoning, and LLM review are **planned integrations**, not implemented features. No performance, security, or reliability claims have been benchmarked.

## What runs today

- Authenticated `POST /v1/events` ingestion with an idempotent event ID.
- SQLite event and alert history.
- Evidence-based checks for failed tests, unsuccessful shell commands, changed dependency manifests, and schema/migration edits.
- `git-scan` that sends **file paths and branch metadata only** (not code contents).
- `alerts` command for retrieving warnings, a sample event generator, and automated tests.
- A versioned event contract and architecture/security documentation.

## Quick start

Requires Python **3.11+** and Git; no third-party Python packages.

```bash
git clone https://github.com/1064yanzu/devin-hub.git
cd devin-hub
export DEVIN_HUB_TOKEN="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
python -m devin_hub server
```

Open a second terminal in the same environment:

```bash
export DEVIN_HUB_TOKEN="<the same value as in the server terminal>"
python -m devin_hub send-example --node mac-dev --project demo
python -m devin_hub alerts
python -m unittest discover -s tests -v
```

To scan a real working tree (paths/metadata only):

```bash
python -m devin_hub git-scan --path . --node mac-dev --project devin-hub
```

Set `DEVIN_HUB_URL` (default `http://127.0.0.1:8765`) on a client machine. The server binds to loopback by default; do not expose the unauthenticated or unencrypted endpoint to a public network. Use a private encrypted transport and access restrictions for multi-device setups.

## Repository map

| Path | Purpose |
| --- | --- |
| `devin_hub/` | Runnable ingestion API, event rules, SQLite store, and CLI |
| `tests/` | Unit and end-to-end API tests |
| `examples/` | Sample event and local configuration reference |
| `docs/architecture.md` | Components, data flow, decisions, and trade-offs |
| `docs/protocol.md` | Event payload and API contract |
| `docs/security.md` | Threat model and safe deployment defaults |
| `docs/roadmap.md` | MVP-to-agent milestones with acceptance criteria |
| `.github/workflows/ci.yml` | Standard-library unit tests on GitHub Actions |
| `agent-hub.yaml` | **Design reference**, not yet loaded by the Python runtime |

## Current boundary

The hub produces **rule-based warnings**, not judgments about whether a developer made a mistake. For semantic reasoning, multi-machine context correlation, IDE feedback, desktop notifications, or autonomous patches, see [the roadmap](docs/roadmap.md). Contributions are welcome, especially tests and reproducible issue reports.

Licensed under MIT.