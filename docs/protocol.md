# Wire protocol v0.1

The current service exposes:

| Verb | Path | Authentication | Response |
|---|---|---|---|
| GET | `/healthz` | none | `{"status":"ok"}` |
| POST | `/v1/events` | Bearer token | accepted, duplicate, alerts |
| GET | `/v1/alerts` | Bearer token | most recent 50 alerts |

Example event:

```json
{
  "id": "event-001",
  "node_id": "mac-dev",
  "project_id": "demo",
  "kind": "test.result",
  "payload": {"suite": "unit", "passed": false}
}
```

Supported kinds: `git.diff`, `git.commit`, `shell.exit`, `test.result`, `ide.diagnostic`. All four identity fields must use 1–128 safe characters: letters, digits, underscore, dot, colon or dash (first character must be alphanumeric). The payload must be an object. Maximum request size: 64 KiB.

`POST` response: HTTP 201 for a new event, HTTP 200 for a repeated event ID. Duplicate events are not re-reviewed or added to history. This is an event-ID deduplication contract, not a guarantee of exactly-once delivery across the network.

```bash
curl -X POST http://127.0.0.1:8765/v1/events \
  -H "Authorization: Bearer $DEVIN_HUB_TOKEN" \
  -H "Content-Type: application/json" \
  --data-binary @examples/event.json
```

Alert bodies carry `rule`, `severity`, `summary`, `evidence`, and `suggested_action`. They are suggestions and should not automatically block development.

## Future version

Add authenticated node identity, sequence numbers, producer time, repository coordinates, tracing IDs, ack/retry policy, event retention, and schema-version negotiation before implementing durable cross-device transport.
