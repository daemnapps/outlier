#!/usr/bin/env python3
"""email-teardown's own tests. stdlib only, no network, no model — the model is
a stub handed to the runner. Everything is written under a TEMP workspace
(`AI_WORKSPACE`): a made-up brand in a temp `brands/`, runs in a temp `runs/`.
The real `runs/` and `brands/` are never touched.

    python3 email-teardown/tests/test_email_teardown.py
"""
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent / "tools"
REAL = next(d for d in HERE.parents if (d / "components").is_dir() and (d / "brands").is_dir())

WS = Path(tempfile.mkdtemp(prefix="email-teardown-test-"))
(WS / "brands" / "testbrand" / "email").mkdir(parents=True)
(WS / "brands" / "testbrand" / "email" / "simple.json").write_text(json.dumps(
    {"logo": {"alt": "Test Brand Co"}, "furniture": ["shop the range", "our promise", "gear"]}))
os.symlink(REAL / "components", WS / "components")
os.environ["AI_WORKSPACE"] = str(WS)

sys.path.append(str(TOOLS))
import paths as P                # noqa: E402
import furniture as F            # noqa: E402
import elements_label as L       # noqa: E402
import gates as G                # noqa: E402
import run as R                  # noqa: E402

SOURCE = """# A subject line

- preview: A preview line

---

[LINK] [IMAGE alt=Test Brand Co] https://img.example/logo.png -> https://example.com/

Hi {{ first_name }}, this is the opening line of the message.

[LINK] [IMAGE alt=A headline inside a picture. [GET IT NOW]] https://img.example/hero.png -> https://example.com/p

[LINK] [IMAGE alt=Shop the range] https://img.example/nav.png -> https://example.com/all

[LINK] [IMAGE alt=Gear] https://img.example/gear.png -> https://example.com/gear

[LINK] [IMAGE alt=Custom] https://img.example/fb.png -> https://www.facebook.com/example

No longer want to receive these emails? {% unsubscribe %}
"""

RECORD = """# THE MESSAGE

**THE BLOCKS, IN ORDER**
B1 copy: "Hi {{ first_name }}, this is the opening line of the message." [D1]
(furniture — see F2)

# PAGE FURNITURE

F1 logo row — "Test Brand Co"
F2 navigation row — "Shop the range", "Gear"

# SOURCE DEFECTS

D1 — "Hi {{ first_name }}," — broken merge tag — meant a first name

# STRIP

```STRIP
{"furniture_words": ["Shop the range", "Gear", "Test Brand Co"],
 "defects": [{"id": "D1", "quote": "Hi {{ first_name }},", "meant": "a greeting by first name"}]}
```
"""

CONSTRUCT = """# CONSTRUCT

**THE MOVES**
1. Greets the reader as one person before anything is asked. [SLOT: greeting]

**THE SEQUENCE LOGIC** — the greeting buys the first line.

**LOAD-BEARING** — the single ask.

**LEFT OUT:** F1, F2, D1
"""


def labels_answer(**over):
    E = L.library()
    ids = {L.key(el, a): E.rows(el, a)[0]["id"] for el, a in L.LISTS}
    ids.update(over)
    return "```ELEMENTS\n" + json.dumps(
        {k: ({"id": v, "why": "B1 does it", "proposed": None} if isinstance(v, str) else v)
         for k, v in ids.items()}) + "\n```"


class Stub:
    """The model, stubbed: answers by which step's prompt it was handed."""
    def __init__(self, record=RECORD, labels=None, construct=CONSTRUCT):
        self.record, self.labels, self.construct = record, labels or labels_answer(), construct
        self.calls, self.prompts = [], {}

    def __call__(self, prompt, model):
        step = ("tear2" if "```ELEMENTS" in prompt else "tear3" if "# CONSTRUCT" in prompt else "tear1")
        self.calls.append((step, model))
        self.prompts[step] = prompt
        return 0, {"tear1": self.record, "tear2": self.labels, "tear3": self.construct}[step], ""


class Base(unittest.TestCase):
    def setUp(self):
        self.src = WS / "source.md"
        self.src.write_text(SOURCE)
        self.said = []
        shutil.rmtree(WS / "runs", ignore_errors=True)

    def run_it(self, *extra, stub=None, label="t1"):
        return R.main([str(self.src), "--brand", "testbrand", "--label", label, *extra],
                      runner=stub or Stub(), echo=self.said.append)

    def out(self, label="t1"):
        return WS / "runs" / "email-teardown" / "testbrand" / label


class Workspace(Base):
    def test_everything_resolves_inside_the_temp_workspace(self):
        self.assertEqual(P.REPO, WS)
        self.assertEqual(P.record_dir("testbrand", "x"), WS / "runs" / "email-teardown" / "testbrand" / "x")
        self.assertNotIn(str(REAL / "runs"), str(P.RECORDS))


class DryRun(Base):
    def test_spends_nothing_and_writes_nothing(self):
        stub = Stub()
        before = sorted(p.name for p in WS.iterdir())
        self.assertEqual(self.run_it("--dry-run", stub=stub), 0)
        self.assertEqual(stub.calls, [])
        self.assertEqual(sorted(p.name for p in WS.iterdir()), before)      # no runs/ made
        text = "\n".join(self.said)
        self.assertIn("would file  runs/email-teardown/testbrand/t1/", text)
        self.assertIn("0 model calls", text)
        for tier_model in ("reads", "checks", "designs"):
            self.assertIn(f"({tier_model})", text)

    def test_names_what_is_missing(self):
        code = R.main([str(WS / "nope.md"), "--brand", "nobrand", "--dry"], runner=Stub(), echo=self.said.append)
        self.assertEqual(code, 1)
        text = "\n".join(self.said)
        self.assertIn("not on file", text)
        self.assertIn("`nobrand` is not a brand folder", text)
        self.assertIn("testbrand", text)                                    # the real ones are named

    def test_there_is_no_default_brand(self):
        with self.assertRaises(SystemExit):
            R.main([str(self.src), "--dry-run"], runner=Stub(), echo=self.said.append)


class FullRun(Base):
    def test_files_the_run_and_passes_every_gate(self):
        stub = Stub()
        self.assertEqual(self.run_it(stub=stub), 0)
        self.assertEqual([c[0] for c in stub.calls], ["tear1", "tear2", "tear3"])
        out = self.out()
        for f in ("tear1--record.md", "tear1--sent.md", "tear2--labels.md", "tear3--construct.md",
                  "tear3--sent.md", "elements.json", "strip.json", "run.json", "check.json"):
            self.assertTrue((out / f).is_file(), f)
        check = json.loads((out / "check.json").read_text())
        self.assertEqual({g: v["result"] for g, v in check.items()},
                         {"inputs": "pass", "copy": "pass", "elements": "pass"})
        run = json.loads((out / "run.json").read_text())
        self.assertEqual((run["tool"], run["brand"], run["state"]), ("email-teardown", "testbrand", "filed"))
        self.assertEqual(set(run["elements"]["labels"]), {"format/email", "template/email", "framework/all"})

    def test_tiers_not_model_ids_pick_the_model(self):
        stub = Stub()
        self.run_it(stub=stub)
        sys.path.append(str(P.RUN_KIT))
        from run_kit import model as M
        self.assertEqual([m for _, m in stub.calls], [M.TIERS["reads"], M.TIERS["checks"], M.TIERS["designs"]])
        stub2 = Stub()
        self.run_it("--model", "one-model", stub=stub2, label="t2")
        self.assertEqual({m for _, m in stub2.calls}, {"one-model"})

    def test_the_brand_words_come_from_the_brand_file_and_later_steps_never_see_furniture(self):
        stub = Stub()
        self.run_it(stub=stub)
        self.assertIn("shop the range, our promise, gear", stub.prompts["tear1"])
        self.assertIn("its alt text is a standing furniture word", stub.prompts["tear1"])
        for step in ("tear2", "tear3"):
            self.assertNotIn("Shop the range", stub.prompts[step])
            self.assertIn("Items set aside: F1, F2", stub.prompts[step])

    def test_a_finished_run_is_reused_and_a_changed_source_is_read_again(self):
        self.run_it()
        again = Stub()
        self.assertEqual(self.run_it(stub=again), 0)
        self.assertEqual(again.calls, [])
        self.src.write_text(SOURCE + "\nOne more line.\n")
        changed = Stub()
        self.run_it(stub=changed)
        self.assertEqual([c[0] for c in changed.calls], ["tear1", "tear2", "tear3"])

    def test_rerun_from_a_step(self):
        self.run_it()
        stub = Stub()
        self.run_it("--rerun-from", "tear3", stub=stub)
        self.assertEqual([c[0] for c in stub.calls], ["tear3"])


class ElementsGate(Base):
    def test_an_unknown_label_is_refused_with_the_real_ids_named(self):
        stub = Stub(labels=labels_answer(**{"format/email": "made-up-format"}))
        self.assertEqual(self.run_it(stub=stub), 2)
        self.assertEqual([c[0] for c in stub.calls], ["tear1", "tear2"])       # the construct never ran
        check = json.loads((self.out() / "check.json").read_text())
        self.assertEqual(check["elements"]["result"], "HELD")
        real = L.library().rows("format", "email")[0]["id"]
        self.assertIn(real, check["elements"]["problems"][0])
        rec = json.loads((self.out() / "elements.json").read_text())
        self.assertEqual(rec["refused"][0]["id"], "made-up-format")
        self.assertNotIn("format/email", rec["labels"])

    def test_none_fits_is_recorded_as_a_proposed_row_never_written_to_the_library(self):
        before = (REAL / "components" / "elements" / "library" / "template.email.json").read_bytes()
        stub = Stub(labels=labels_answer(**{"template/email": {
            "id": "none-fits", "why": "THE WEIGHT: all words sit inside pictures",
            "proposed": "picture-stack — The picture stack — the whole message carried in stacked pictures"}}))
        self.assertEqual(self.run_it(stub=stub), 0)
        run = json.loads((self.out() / "run.json").read_text())
        self.assertTrue(run["elements"]["proposed"]["template/email"].startswith("picture-stack"))
        self.assertEqual((REAL / "components" / "elements" / "library" / "template.email.json").read_bytes(), before)

    def test_none_fits_without_a_proposed_row_is_held(self):
        stub = Stub(labels=labels_answer(**{"template/email": {"id": "none-fits", "why": "x", "proposed": None}}))
        self.assertEqual(self.run_it(stub=stub), 2)


class CopyGate(Base):
    def held(self, construct):
        self.assertEqual(self.run_it(stub=Stub(construct=construct)), 2)
        check = json.loads((self.out() / "check.json").read_text())
        self.assertEqual(check["copy"]["result"], "HELD")
        return " | ".join(check["copy"]["problems"])

    def test_furniture_words_in_the_construct_hold_it(self):
        self.assertIn("shop the range", self.held(CONSTRUCT.replace("the single ask", "the Shop the Range strip")))

    def test_the_senders_frame_in_the_construct_holds_it(self):
        self.assertIn("footer", self.held(CONSTRUCT.replace("the single ask", "the footer carries the ask")))

    def test_a_carried_defect_or_merge_tag_holds_it(self):
        why = self.held(CONSTRUCT.replace("the single ask", 'opens "Hi {{ first_name }}," flat'))
        self.assertIn("source defect (D1)", why)
        self.assertIn("merge tag", why)

    def test_an_unfilled_note_holds_it(self):
        self.assertIn("UNFILLED", self.held(CONSTRUCT.replace("the single ask", "[UNFILLED: no proof]")))

    def test_a_record_without_its_labelled_parts_is_held_before_anything_else_is_spent(self):
        stub = Stub(record="Here is a summary of the email, all in one run.")
        self.assertEqual(self.run_it(stub=stub), 2)
        self.assertEqual([c[0] for c in stub.calls], ["tear1"])
        problems = json.loads((self.out() / "check.json").read_text())["copy"]["problems"]
        self.assertTrue(any("PAGE FURNITURE" in p for p in problems))
        self.assertTrue(any("STRIP" in p for p in problems))

    def test_one_word_furniture_entries_are_not_swept_as_english(self):
        self.assertEqual(F.construct_problems(CONSTRUCT.replace("the single ask", "the reader shifts gear"),
                                              {"furniture_words": ["Gear"], "defects": []}, "testbrand"), [])


class Scan(Base):
    def test_the_free_scan_finds_furniture_and_damage(self):
        found = F.scan(SOURCE, "testbrand")
        whys = {f["why"] for f in found["furniture"]}
        self.assertEqual(len(found["furniture"]), 5)
        self.assertIn("links to a social platform", whys)
        self.assertIn("unsubscribe / address / legal line", whys)
        self.assertEqual([d["quote"] for d in found["defects"]], ["{{ first_name }}"])   # the footer tag is not damage

    def test_a_brand_with_nothing_on_file_has_no_words_of_its_own(self):
        self.assertEqual(F.brand_words("nobody")[1], [])

    def test_an_html_email_is_reduced_to_the_same_lines(self):
        f = WS / "e.html"
        f.write_text('<html><head><style>p{}</style></head><body><p>Hello there</p>'
                     '<a href="https://example.com/p"><img alt="A headline" src="https://img.example/h.png"></a></body></html>')
        text = F.load(f)
        self.assertIn("Hello there", text)
        self.assertIn("[LINK] [IMAGE alt=A headline] https://img.example/h.png -> https://example.com/p", text)
        self.assertNotIn("p{}", text)


class NoBrandInTheTool(unittest.TestCase):
    def test_no_brand_name_in_the_new_code_or_prompts(self):
        brands = [p.name for p in (REAL / "brands").iterdir() if p.is_dir() and not p.name.startswith(("_", "."))]
        files = [TOOLS / n for n in ("run.py", "furniture.py", "gates.py", "elements_label.py", "paths.py")]
        files += sorted((HERE.parent / "prompts").glob("tear*.md"))
        for f in files:
            low = f.read_text().lower()
            for b in brands:
                self.assertNotIn(b.lower(), low, f"{f.name} names the brand {b}")


def tearDownModule():
    shutil.rmtree(WS, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=1)
