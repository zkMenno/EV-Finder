"""Tests for scripts/gate_guard.py (T-121). Run: python3 -m unittest discover -s scripts/tests"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gate_guard as g  # noqa: E402

CFG = g.load_config((Path(__file__).resolve().parents[2] / "config" / "gate-files.yaml").read_text())


class Matcher(unittest.TestCase):
    def test_globs(self):
        self.assertTrue(g.matches(".github/workflows/ci.yml", [".github/workflows/**"]))
        self.assertTrue(g.matches("AGENTS.md", ["**/AGENTS.md"]))
        self.assertTrue(g.matches("apps/web/AGENTS.md", ["**/AGENTS.md"]))
        self.assertTrue(g.matches("pipeline/ev_pipeline/qa/qa_thresholds.yaml", ["pipeline/**/qa*.yaml"]))
        self.assertTrue(g.matches("apps/web/playwright.config.ts", ["**/playwright.config.*"]))
        self.assertFalse(g.matches("apps/web/src/app/page.tsx", CFG["gate_files"]))
        self.assertFalse(g.matches("docs/spec/launch-scope.md", CFG["gate_files"]))

    def test_config_parses(self):
        self.assertIn(CFG["mode"], {"off", "observe", "enforce"})
        self.assertEqual(CFG["escape_label"], "gate-ok")
        self.assertIn("REVIEW.md", CFG["gate_files"])
        self.assertIn("\\.skip\\(", CFG["weakening_patterns"])


class Judge(unittest.TestCase):
    def j(self, changed, deleted=(), added=None, body="", labels=()):
        return g.judge(list(changed), list(deleted), added or {}, CFG, body, list(labels))

    def test_gate_only_is_fine(self):
        self.assertEqual(self.j(["REVIEW.md", ".github/workflows/ci.yml"]).problems, [])

    def test_code_only_is_fine(self):
        self.assertEqual(self.j(["apps/web/src/a.ts"]).problems, [])

    def test_mixed_is_flagged(self):
        v = self.j(["apps/web/src/a.ts", "apps/web/playwright.config.ts"])
        self.assertEqual(len(v.problems), 1)
        self.assertIn("Split the gate change", v.problems[0])

    def test_escape_label(self):
        self.assertEqual(self.j(["apps/web/src/a.ts", "AGENTS.md"], labels=["gate-ok"]).problems, [])

    def test_deleted_test_needs_marker(self):
        self.assertEqual(len(self.j(["pipeline/tests/test_x.py"], deleted=["pipeline/tests/test_x.py"]).problems), 1)
        self.assertEqual(self.j(["pipeline/tests/test_x.py"], deleted=["pipeline/tests/test_x.py"],
                                body="Test-change: replaced by test_y").problems, [])

    def test_skip_and_sleep_flagged(self):
        added = {"apps/web/e2e/hero.spec.ts": ["  test.skip('flaky', () => {})"],
                 "pipeline/tests/test_a.py": ["    time.sleep(2)"]}
        self.assertEqual(len(self.j(list(added), added=added).problems), 2)

    def test_skip_outside_tests_ignored(self):
        added = {"apps/web/src/list.ts": ["items.skip(1)"]}
        self.assertEqual(self.j(list(added), added=added).problems, [])



class Marker(unittest.TestCase):
    def test_template_comment_is_not_a_marker(self):
        from gate_guard import has_marker
        body = '<!-- If you removed a test, add a line starting "Test-change:" with the reason. -->'
        self.assertFalse(has_marker(body, "Test-change:"))
        self.assertFalse(has_marker("Test-change:", "Test-change:"))
        self.assertTrue(has_marker(body + "\nTest-change: flaky fixture replaced", "Test-change:"))


if __name__ == "__main__":
    unittest.main()
