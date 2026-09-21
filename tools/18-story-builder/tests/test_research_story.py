#!/usr/bin/env python3
"""research-story's tests. Stdlib only, no network, no model.

    python3 story-builder/tests/test_research_story.py

Everything runs in a temp workspace: its own brands/ (one made-up brand) and
its own runs/, with components/ linked in read-only. The real runs/ and brands/
are never written. The one model call is replaced by a stub.
"""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent
REAL = next(d for d in TOOL.parents if (d / "components").is_dir() and (d / "brands").is_dir())
BRAND = "testbrand"
ROW = "I hid it for years under long sleeves and my husband never noticed a thing"

TMP = Path(tempfile.mkdtemp(prefix="research-story-test-"))
(TMP / "brands" / "_TEMPLATE").mkdir(parents=True)
shutil.copyfile(REAL / "brands" / "_TEMPLATE" / "story.md", TMP / "brands" / "_TEMPLATE" / "story.md")
os.symlink(REAL / "components", TMP / "components")
bank = TMP / "brands" / BRAND / "core-avatars" / "the-reader" / "language"
bank.mkdir(parents=True)
(bank / "reviews.json").write_text(json.dumps({"entries": [
    {"id": "t-001", "text": ROW, "status": "active", "speaker": "customer", "funnel": "customer",
     "source": {"type": "review", "name": "A reader"}}]}))
os.environ["AI_WORKSPACE"] = str(TMP)
sys.path.append(str(TOOL / "machine"))
import build  # noqa: E402
import story_gates as G  # noqa: E402

BLOCK = "\n".join(f"{s}: open" for s in build.lint_story.SLOTS[:-1]).replace(
    "STORIES: open", "STORIES: the-sleeves") + "\nconfirmed by: open"


def draft(story_quote=ROW, loose=""):
    return f"""# The story

## The story block

```
{BLOCK}
```

## The lesson this file comes from

Started from the bank. {loose}

## The stories

### the-sleeves — "{story_quote}"

- **Beats:** hid it → the turn → the after
- **Teller:** the reader
- **Fits:** open
- **Receipts:** "{story_quote}" (reviews.json)

## The tellers

open

## How a run uses this

open

## Where it lives in the chains

open

## Receipts

- the bank

## Open

- The block is declared, not confirmed.
"""


def tree():
    return sorted(str(p.relative_to(TMP)) for d in ("brands", "runs") for p in (TMP / d).rglob("*"))


class Case(unittest.TestCase):
    calls = 0

    def setUp(self):
        Case.calls = 0
        self.reply = draft()
        self._model = build.call_model

        def stub(sent, raw, prompt_name):
            Case.calls += 1
            Path(raw).write_text(self.reply)
            return "stub-model"
        build.call_model = stub
        story = TMP / "brands" / BRAND / "story.md"
        if story.exists():
            story.unlink()

    def tearDown(self):
        build.call_model = self._model
        G.ARC_FRAMEWORK = "story-testimonial"

    def run_build(self, *args):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = build.main(["--brand", BRAND, *args])
        return code, buf.getvalue()

    def run_dir(self, label):
        return TMP / "runs" / "research-story" / BRAND / label

    def test_works_in_the_temp_workspace_only(self):
        self.assertEqual(build.WS, TMP)
        self.assertNotEqual(build.WS, REAL)

    def test_dry_run_is_free_and_writes_nothing(self):
        before = tree()
        code, out = self.run_build("--dry-run", "--label", "free")
        self.assertEqual(code, 0)
        self.assertEqual(Case.calls, 0)
        self.assertEqual(tree(), before)
        self.assertIn(f"runs/research-story/{BRAND}/free", out)
        self.assertIn("nothing written", out)

    def test_old_dry_flag_still_files_the_prompt_and_spends_nothing(self):
        code, _ = self.run_build("--dry", "--label", "old-dry")
        self.assertEqual((code, Case.calls), (0, 0))
        self.assertTrue((self.run_dir("old-dry") / "stage2--sent.md").is_file())
        self.assertIn(ROW, (self.run_dir("old-dry") / "stage2--sent.md").read_text())

    def test_no_brand_is_an_error_never_a_default(self):
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            build.main([])
        with self.assertRaises(SystemExit):
            build.main(["--brand", "no-such-brand", "--dry-run"])

    def test_a_clean_build_files_the_record_and_hands_off(self):
        code, _ = self.run_build("--label", "clean")
        d = self.run_dir("clean")
        self.assertEqual((code, Case.calls), (0, 1))
        for name in ("run.json", "check.json", "stage2--sent.md", "stage2--draft.md", "stage3--verify.json",
                     "stage4--lint.txt", "deliverable/story.md"):
            self.assertTrue((d / name).is_file(), name)
        check = json.loads((d / "check.json").read_text())
        self.assertEqual({g: check[g]["result"] for g in check},
                         {"inputs": "pass", "elements": "pass", "copy": "pass"})
        run = json.loads((d / "run.json").read_text())
        self.assertEqual((run["tool"], run["brand"], run["status"]), ("research-story", BRAND, "done"))
        self.assertTrue(run["wrote_brand_story"])
        self.assertTrue((TMP / "brands" / BRAND / "story.md").is_file())

    def test_an_existing_story_is_never_overwritten(self):
        story = TMP / "brands" / BRAND / "story.md"
        story.write_text("the owner's own file\n")
        code, _ = self.run_build("--label", "keep")
        self.assertEqual(code, 0)
        self.assertEqual(story.read_text(), "the owner's own file\n")

    def test_a_demoted_story_still_passes_as_it_always_did(self):
        self.reply = draft(story_quote="She never said this line at all")
        code, _ = self.run_build("--label", "demoted")
        self.assertEqual(code, 0)
        story = (TMP / "brands" / BRAND / "story.md").read_text()
        self.assertIn("the-sleeves (open)", story)
        self.assertIn("demoted by the story builder's check", story)

    def test_a_quote_left_standing_unchecked_is_held(self):
        self.reply = draft(loose='As one reader put it, "nobody ever told me this was treatable".')
        code, out = self.run_build("--label", "loose")
        d = self.run_dir("loose")
        self.assertEqual(code, 2)
        check = json.loads((d / "check.json").read_text())
        self.assertEqual(check["copy"]["result"], "HELD")
        self.assertIn("nobody ever told me", check["copy"]["problems"][0])
        self.assertIn("HELD at the copy gate", out)
        self.assertTrue((d / "deliverable" / "story.md").is_file())
        self.assertFalse((TMP / "brands" / BRAND / "story.md").exists())
        self.assertTrue(json.loads((d / "run.json").read_text())["status"].startswith("HELD"))

    def test_a_broken_shape_is_held(self):
        self.reply = draft().replace("## The tellers\n\nopen\n\n", "")
        code, _ = self.run_build("--label", "shape")
        self.assertEqual(code, 2)
        self.assertFalse((TMP / "brands" / BRAND / "story.md").exists())

    def test_an_unknown_framework_is_refused_before_anything_is_spent(self):
        G.ARC_FRAMEWORK = "not-a-real-frame"
        code, out = self.run_build("--label", "bad-frame")
        self.assertEqual((code, Case.calls), (2, 0))
        check = json.loads((self.run_dir("bad-frame") / "check.json").read_text())
        self.assertEqual(check["elements"]["result"], "HELD")
        self.assertIn("story-testimonial", check["elements"]["problems"][0])   # the real ids are named
        dry_code, dry_out = self.run_build("--dry-run", "--label", "bad-frame-2")
        self.assertEqual(dry_code, 2)
        self.assertIn("WOULD HOLD", dry_out)

    def test_the_real_library_holds_the_arc(self):
        self.assertEqual(G.elements_problems(), [])

    def test_a_used_label_is_refused_under_the_new_name_and_the_old(self):
        self.run_build("--dry", "--label", "taken")
        with self.assertRaises(SystemExit):
            build.main(["--brand", BRAND, "--label", "taken"])
        (TMP / "runs" / "story-builder" / BRAND / "taken-before").mkdir(parents=True)
        with self.assertRaises(SystemExit):
            build.main(["--brand", BRAND, "--label", "taken-before"])

    def test_nothing_is_put_first_on_the_path(self):
        for f in (TOOL / "machine").glob("*.py"):
            self.assertNotIn("sys.path.insert(", f.read_text(), f.name)

    def test_the_old_command_still_works(self):
        before = tree()
        r = subprocess.run([sys.executable, str(TOOL / "build.py"), "--brand", BRAND, "--dry-run"],
                           capture_output=True, text=True, env={**os.environ, "AI_WORKSPACE": str(TMP)})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("runs/research-story/", r.stdout)
        self.assertEqual(tree(), before)


if __name__ == "__main__":
    try:
        unittest.main(exit=False)
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
