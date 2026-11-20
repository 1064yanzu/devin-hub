import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from devin_hub.api import make_handler, validate
from devin_hub.store import Store


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Store(str(Path(self.temp.name) / "hub.sqlite3"))
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(self.store, "secret"))
        self.worker = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.worker.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.worker.join(timeout=3)
        self.store.close()
        self.temp.cleanup()

    def call(self, path, method="GET", payload=None, authorized=True):
        headers = {"Content-Type": "application/json"}
        if authorized:
            headers["Authorization"] = "Bearer secret"
        data = json.dumps(payload).encode() if payload is not None else None
        req = Request(f"http://127.0.0.1:{self.server.server_port}{path}",
                      data=data, method=method, headers=headers)
        try:
            with urlopen(req, timeout=3) as resp:
                return resp.status, json.load(resp)
        except HTTPError as e:
            return e.code, json.load(e)

    def test_health(self):
        status, body = self.call("/healthz", authorized=False)
        self.assertEqual((status, body["status"]), (200, "ok"))

    def test_auth_required(self):
        status, _ = self.call("/v1/alerts", authorized=False)
        self.assertEqual(status, 401)

    def test_ingest_alert_and_idempotency(self):
        event = {"id": "event-1", "node_id": "mac", "project_id": "app",
                 "kind": "test.result", "payload": {"passed": False}}
        status, body = self.call("/v1/events", "POST", event)
        self.assertEqual(status, 201)
        self.assertEqual(len(body["alerts"]), 1)
        status, body = self.call("/v1/events", "POST", event)
        self.assertEqual(status, 200)
        self.assertTrue(body["duplicate"])
        _, body = self.call("/v1/alerts")
        self.assertEqual(len(body["alerts"]), 1)

    def test_invalid_event(self):
        event = {"id": "../bad", "node_id": "mac", "project_id": "app",
                 "kind": "test.result", "payload": {}}
        status, _ = self.call("/v1/events", "POST", event)
        self.assertEqual(status, 400)

    def test_reject_unknown_kind(self):
        with self.assertRaises(ValueError):
            validate({"id": "a", "node_id": "mac", "project_id": "app",
                      "kind": "remote.execute", "payload": {}})


if __name__ == "__main__":
    unittest.main()
