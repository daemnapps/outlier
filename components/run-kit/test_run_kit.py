#!/usr/bin/env python3
"""python3 test_run_kit.py — stdlib unittest, no network, no model call."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_kit import model, paths, pool, prompts          # noqa: E402
from run_kit.stage import DRY, Chain                     # noqa: E402

STEPS = [{"key": "stage1", "name": "Read", "tier": "reads", "label": "record"},
         {"key": "stage2", "name": "Write", "tier": "designs", "label": "draft", "depends": ["stage1"]}]


class Kit(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.pr = self.tmp / "prompts"
        self.pr.mkdir()
        (self.pr / "stage1-read-v1-x.md").write_text("Read this: {source}")
        (self.pr / "stage2-write-v2-x.md").write_text("OLD {record}")
        (self.pr / "stage2-write-v10-x.md").write_text("Write from: {record}")
        self.calls = []

    def runner(self, reply="ok"):
        def r(prompt, m):
            self.calls.append((m, prompt))
            return 0, reply, ""
        return r

    def chain(self, **kw):
        return Chain("tool", "brand", "label", self.tmp / "run", self.pr, STEPS,
                     echo=lambda *_: None, **kw)

    def test_v10_beats_v2(self):
        self.assertEqual(prompts.latest(self.pr, "stage2").name, "stage2-write-v10-x.md")

    def test_unfilled_field_is_refused(self):
        with self.assertRaises(prompts.PromptError):
            prompts.fill("needs {this} and {that}", {"this": 1})

    def test_dry_run_spends_nothing(self):
        c = self.chain(dry=True, runner=self.runner())
        self.assertEqual(c.run("stage1", source="s"), DRY)
        self.assertEqual(self.calls, [])
        self.assertTrue((self.tmp / "run" / "stage1--sent.md").is_file())

    def test_dry_run_still_refuses_unfilled(self):
        with self.assertRaises(prompts.PromptError):
            self.chain(dry=True).run("stage1")

    def test_tiers_and_escalation(self):
        self.assertEqual(model.pick("reads", 10)[0], model.TIERS["reads"])
        self.assertEqual(model.pick("reads", model.SMALL_WINDOW_CHARS + 1)[0], model.TIERS["designs"])
        self.assertEqual(model.pick("reads", 10, forced="m")[0], "m")

    def test_rerun_keeps_done_steps_and_invalidates_dependents(self):
        c = self.chain(runner=self.runner("first"))
        rec = c.run("stage1", source="s")
        c.run("stage2", record=rec)
        self.assertEqual(len(self.calls), 2)
        c2 = self.chain(runner=self.runner("second"))
        c2.run("stage1", source="s")
        c2.run("stage2", record=rec)
        self.assertEqual(len(self.calls), 2, "nothing changed — both steps are kept")
        (self.pr / "stage1-read-v2-x.md").write_text("Read this, again: {source}")
        c3 = self.chain(runner=self.runner("third"))
        c3.run("stage1", source="s")
        c3.run("stage2", record="x")
        self.assertEqual(len(self.calls), 4, "stage1's prompt changed, so stage2 (which reads it) reruns too")

    def test_rerun_from(self):
        c = self.chain(runner=self.runner())
        c.run("stage1", source="s"); c.run("stage2", record="r")
        c2 = self.chain(runner=self.runner(), rerun_from="stage2")
        c2.run("stage1", source="s"); c2.run("stage2", record="r")
        self.assertEqual(len(self.calls), 3)

    def test_usage_limit_is_its_own_error(self):
        def r(p, m):
            return 1, "You've hit your monthly spend limit · your weekly usage limit resets", ""
        with self.assertRaises(model.UsageLimit):
            model.call("x", "m", runner=r)

    def test_bad_answer_is_not_retried(self):
        n = []
        def r(p, m):
            n.append(1)
            return 1, "", "invalid request"
        with self.assertRaises(model.StageFailed):
            model.call("x", "m", runner=r, wait=0)
        self.assertEqual(len(n), 1)

    def test_transient_is_retried(self):
        n = []
        def r(p, m):
            n.append(1)
            return (1, "", "503 overloaded") if len(n) < 3 else (0, "fine", "")
        self.assertEqual(model.call("x", "m", runner=r, wait=0), "fine")
        self.assertEqual(len(n), 3)

    def test_paths_find_the_repo(self):
        self.assertTrue((paths.repo() / "brands").is_dir())
        self.assertTrue(paths.component("run-kit").is_dir())

    def test_pool_stops_on_usage_limit_and_survives_a_failure(self):
        def fn(label, payload):
            if payload == "boom":
                raise ValueError("broke")
            return payload
        out = pool.run_all([("a", 1), ("b", "boom")], fn, workers=2)
        self.assertEqual(out["a"], ("done", 1))
        self.assertEqual(out["b"][0], "failed")


if __name__ == "__main__":
    unittest.main(verbosity=1)
