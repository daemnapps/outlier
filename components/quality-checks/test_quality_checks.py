#!/usr/bin/env python3
"""python3 test_quality_checks.py — stdlib unittest, no network, no model."""
import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import quality_checks as Q   # noqa: E402

BANK = "## the-set — The Set\n- Price: **$49.99**, was $59.99\n\n## other — Other\n- Price: **$10.00**\n"


class Checks(unittest.TestCase):
    def test_a_price_the_bank_does_not_sell_is_caught(self):
        block = Q.offer_block(BANK, "the-set")
        self.assertEqual(Q.price_check("Two for $99.99", block, "the-set")[0][:7], "$99.99 ")
        self.assertEqual(Q.price_check("Just $49.99, was $59.99", block), [])
        self.assertNotIn("$10.00", block, "one offer's block never leaks the next offer's price")

    def test_49_and_49_00_are_one_price(self):
        self.assertEqual(Q.price_check("only $49", "## x — X\n- Price: **$49.00**"), [])

    def test_a_price_with_no_offer_is_caught(self):
        self.assertTrue(Q.price_check("only $5", ""))

    def test_unfilled(self):
        self.assertTrue(Q.unfilled_check("hello [the handoff — UNFILLED: x]"))
        self.assertEqual(Q.unfilled_check("clean"), [])

    def test_check_block(self):
        t = '```CHECK\n{"facts":[{"quote":"scrub","problem":"WRONG","files_say":"serum"}],"chops":[],"typos":[{"quote":"uy","fix":"Buy"}]}\n```'
        self.assertEqual(len(Q.read_check_block(t)), 2)
        self.assertTrue(Q.read_check_block("no block"))

    def test_elements(self):
        self.assertEqual(Q.elements_check({("framework", "all"): "pas"}), [])
        self.assertTrue(Q.elements_check({("format", "video"): "not-a-real-format"}))

    def test_hold_writes_and_stops(self):
        d = Path(tempfile.mkdtemp())
        self.assertTrue(Q.hold("copy", [], d))
        with self.assertRaises(Q.Held):
            Q.hold("delivery", ["wrong price"], d)
        state = json.loads((d / "check.json").read_text())
        self.assertEqual(state["copy"]["result"], "pass")
        self.assertEqual(state["delivery"]["result"], "HELD")


if __name__ == "__main__":
    unittest.main(verbosity=1)
