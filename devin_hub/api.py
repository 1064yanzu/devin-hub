"""Tiny HTTP ingestion API. Intended for loopback/private deployments."""

from __future__ import annotations

import hmac
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .rules import review
from .store import Store

ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
KINDS = {"git.diff", "git.commit", "shell.exit", "test.result", "ide.diagnostic"}
MAX_BODY = 64 * 1024


def validate(event: object) -> dict:
    if not isinstance(event, dict):
        raise ValueError("Expected JSON object")
    for field in ("id", "node_id", "project_id", "kind"):
        value = event.get(field)
        if not isinstance(value, str) or not ID_PATTERN.fullmatch(value):
            raise ValueError(f"Invalid {field}")
    if event["kind"] not in KINDS:
        raise ValueError("Unsupported event kind")
    if not isinstance(event.get("payload"), dict):
        raise ValueError("payload must be an object")
    return event


def make_handler(store: Store, token: str):
    class Handler(BaseHTTPRequestHandler):
        def send_json(self, status: int, obj: object):
            raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(raw)

        def authorized(self) -> bool:
            provided = self.headers.get("Authorization", "")
            return hmac.compare_digest(provided, "Bearer " + token)

        def do_GET(self):
            if self.path == "/healthz":
                return self.send_json(200, {"status": "ok"})
            if not self.authorized():
                return self.send_json(401, {"error": "unauthorized"})
            if self.path == "/v1/alerts":
                return self.send_json(200, {"alerts": store.list_alerts()})
            self.send_json(404, {"error": "not_found"})

        def do_POST(self):
            if not self.authorized():
                return self.send_json(401, {"error": "unauthorized"})
            if self.path != "/v1/events":
                return self.send_json(404, {"error": "not_found"})
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if size <= 0 or size > MAX_BODY:
                    return self.send_json(413, {"error": "invalid_body_size"})
                raw = self.rfile.read(size)
                event = validate(json.loads(raw.decode("utf-8")))
                alerts = review(event)
                inserted = store.add_event(event, alerts)
                self.send_json(201 if inserted else 200, {
                    "accepted": True, "duplicate": not inserted,
                    "alerts": alerts if inserted else [],
                })
            except (ValueError, UnicodeError, json.JSONDecodeError) as exc:
                self.send_json(400, {"error": "invalid_event", "detail": str(exc)})
            except Exception:
                self.send_json(500, {"error": "internal_error"})

        def log_message(self, format, *args):
            # Avoid logging auth headers or potentially sensitive payloads.
            return

    return Handler


def serve(host: str, port: int, db_path: str, token: str):
    if not token:
        raise ValueError("DEVIN_HUB_TOKEN must be set")
    store = Store(db_path)
    server = ThreadingHTTPServer((host, port), make_handler(store, token))
    print(f"Devin Hub listening on http://{host}:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        store.close()
