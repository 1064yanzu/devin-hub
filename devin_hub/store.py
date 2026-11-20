"""SQLite persistence for events and alerts."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path


class Store:
    def __init__(self, db_path: str):
        if db_path != ":memory:":
            Path(db_path).expanduser().parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False, timeout=5)
        self.conn.execute("PRAGMA busy_timeout=5000")
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                received_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
                node_id TEXT NOT NULL,
                project_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                body TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL,
                severity TEXT NOT NULL,
                rule TEXT NOT NULL,
                body TEXT NOT NULL,
                FOREIGN KEY(event_id) REFERENCES events(id)
            );
        """)
        self.conn.commit()

    def add_event(self, event: dict, alerts: list[dict]) -> bool:
        with self.conn:
            result = self.conn.execute(
                "INSERT OR IGNORE INTO events(id,node_id,project_id,kind,body) VALUES (?,?,?,?,?)",
                (event["id"], event["node_id"], event["project_id"],
                 event["kind"], json.dumps(event, ensure_ascii=False)),
            )
            if result.rowcount == 0:
                return False
            self.conn.executemany(
                "INSERT INTO alerts(event_id,severity,rule,body) VALUES (?,?,?,?)",
                [(event["id"], a["severity"], a["rule"], json.dumps(a, ensure_ascii=False))
                 for a in alerts],
            )
        return True

    def list_alerts(self, limit: int = 50) -> list[dict]:
        rows = self.conn.execute(
            "SELECT id, event_id, body FROM alerts ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [{"id": row[0], "event_id": row[1], **json.loads(row[2])} for row in rows]

    def close(self):
        self.conn.close()
