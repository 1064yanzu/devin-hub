# Architecture

## Scope

The current implementation covers event ingestion -> persistence -> deterministic rules -> alert retrieval. It intentionally avoids pretending to be a fully autonomous coding assistant.

```text
Mac / Windows (CLI git-scan / example event)
               |
               | HTTP + bearer token, private/loopback only
               v
        Mini PC / HTTP hub
               |
       schema validation
               |
      +--------+---------+
      |                  |
   SQLite            rule engine
  events            (pure Python)
      |                  |
      +--------+---------+
               |
          SQLite alerts
               |
         GET /v1/alerts
               |
    terminal / future UI adapters
```

## Design choices

1. **Metadata first:** The Git collector sends file paths/branch metadata; source code is not uploaded by default.
2. **Rule before model:** Known signals (failed tests, dependency/migration changes) can be detected reproducibly.
3. **Central history:** SQLite stores immutable ingested events and associated alerts, keyed by an idempotency ID.
4. **Explicit boundaries:** No automatic patching, remote command execution, device discovery, LSP, or agent reasoning.

## Intended next-stage topology

The Mini PC will act as a coordinator and durable event store. Each workstation will run a lightweight agent with bounded permissions. Tailscale can supply an encrypted private overlay; gRPC streaming is a candidate real-time transport; NATS JetStream is a candidate for disconnected clients and replay. Their roles need to be justified by measured latency and failure cases before implementation.

## Cross-device conflict model (planned)

To detect real incompatibilities, future events need repository identity, commit SHA, branch, affected public interfaces, test result hashes and provenance. Comparing filenames is *not* enough to establish a conflict. An alert should contain a reproducible counterexample or a failing contract test.

## Decision review (planned)

Combine explicit user-approved project goals, documented architecture decisions, static analysis, and test evidence. An LLM can explain or hypothesize, but warnings need clear evidence and a way to mark false positives.
