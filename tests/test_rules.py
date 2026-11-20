import unittest
from devin_hub.rules import review


class RuleTests(unittest.TestCase):
    def event(self, kind, payload):
        return {"id": "e1", "node_id": "mac", "project_id": "demo",
                "kind": kind, "payload": payload}

    def test_failed_test(self):
        alerts = review(self.event("test.result", {"passed": False, "suite": "unit"}))
        self.assertEqual(alerts[0]["rule"], "failed_test")

    def test_successful_test(self):
        self.assertEqual(review(self.event("test.result", {"passed": True})), [])

    def test_dependency_and_schema(self):
        alerts = review(self.event("git.diff", {
            "changed_files": ["package.json", "db/migrations/001_init.sql"]
        }))
        self.assertEqual({a["rule"] for a in alerts}, {"dependency_change", "schema_change"})

    def test_nonzero_exit(self):
        alerts = review(self.event("shell.exit", {"exit_code": 2}))
        self.assertEqual(alerts[0]["severity"], "medium")

    def test_string_exit_code_is_not_interpreted(self):
        self.assertEqual(review(self.event("shell.exit", {"exit_code": "2"})), [])


if __name__ == "__main__":
    unittest.main()
