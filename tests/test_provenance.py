"""P389: provenance.fact_problems, the one rule a part record and a board record check a fact by."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import provenance  # noqa: E402


class ReadValueTest(unittest.TestCase):
    def test_read_value_gives_a_fact_s_value_along_its_path(self):
        record = {"power": {"io_volts": {"value": 3.3, "verified": True, "source": "page 4"}}}
        self.assertEqual(provenance.read_value(record, "power", "io_volts"), 3.3)
        self.assertEqual(provenance.read_value({"a": {"value": 0}}, "a"), 0)

    def test_a_bare_value_on_the_path_is_the_value(self):
        self.assertEqual(provenance.read_value({"power": {"io_volts": 3.3}}, "power", "io_volts"), 3.3)
        self.assertEqual(provenance.read_value({"power": {"io_volts": "high"}}, "power", "io_volts"), "high")

    def test_a_missing_key_or_no_record_is_none(self):
        self.assertIsNone(provenance.read_value({"power": {}}, "power", "io_volts"))
        self.assertIsNone(provenance.read_value({"power": 3}, "power", "io_volts", "deeper"))
        self.assertIsNone(provenance.read_value(None, "power", "io_volts"))
        self.assertIsNone(provenance.read_value([], "power"))


class FactProblemsTest(unittest.TestCase):
    def test_a_fact_with_its_value_verified_flag_and_source_holds(self):
        self.assertEqual(provenance.fact_problems("facts.a", {"value": 3, "verified": True, "source": "page 4"}), [])

    def test_each_missing_key_is_one_problem(self):
        self.assertEqual(
            provenance.fact_problems("facts.a", {}),
            ["facts.a has no 'value' — a number with no provenance is an opinion",
             "facts.a has no 'verified' — a number with no provenance is an opinion",
             "facts.a has no 'source' — a number with no provenance is an opinion"])

    def test_a_verified_fact_with_no_value_is_one_problem(self):
        self.assertEqual(provenance.fact_problems("facts.a", {"value": None, "verified": True, "source": "s"}),
                         ["facts.a is marked verified but has no value"])

    def test_an_unverified_value_with_no_reason_is_one_problem(self):
        self.assertEqual(
            provenance.fact_problems("facts.a", {"value": 3, "verified": False, "source": "s"}),
            ["facts.a is an unverified value with no why_it_matters; say what depends on it or do not carry the number"])

    def test_an_unverified_value_with_a_reason_holds(self):
        self.assertEqual(provenance.fact_problems(
            "facts.a", {"value": 3, "verified": False, "source": "s", "why_it_matters": "sizes the sprite"}), [])

    def test_an_unverified_fact_with_no_value_needs_no_reason(self):
        self.assertEqual(provenance.fact_problems("facts.a", {"value": None, "verified": False, "source": "s"}), [])

    def test_a_verified_flag_that_is_no_bool_and_a_source_that_is_no_words_are_one_problem_each(self):
        # P374: a bench result is `verified` true or false and names a source; "yes" and "" are neither.
        good = {"value": 3, "verified": True, "source": "bench, 2026-10-29, meter, Petr"}
        cases = [({"verified": "yes"}, "facts.a has verified 'yes', but it must be true or false"),
                 ({"verified": 1}, "facts.a has verified 1, but it must be true or false"),
                 ({"source": ""}, "facts.a has source '', but it must be words that say where the value came from"),
                 ({"source": "  "}, "facts.a has source '  ', but it must be words that say where the value came from"),
                 ({"source": None}, "facts.a has source None, but it must be words that say where the value came from")]
        for change, sentence in cases:
            with self.subTest(change=change):
                self.assertEqual(provenance.fact_problems("facts.a", dict(good, **change)), [sentence])

    def test_a_fact_that_is_no_object_is_one_problem(self):
        for fact in ("s", 3, None, ["value"], True):
            with self.subTest(fact=fact):
                self.assertEqual(provenance.fact_problems("facts.a", fact),
                                 ["facts.a is %r, but it is an object" % (fact,)])


def joystick(**overrides):
    """A record shaped like the joystick module: facts, a pin order read from a page nobody checked, and a guessed outline."""
    record = {"id": "x-joy", "pin_order": ["GND", "VCC", "X"], "pin_order_proof": {"verified": False, "source": "a photo"},
              "body_mm": {"width": 34, "height": 26, "verified": False, "source": "a guess from the photo",
                          "why_it_matters": "whether the module fits the board", "cites": ["page 2"]},
              "facts": {"runs_at_3v3": {"value": True, "verified": False, "source": "the maker's page",
                                        "why_it_matters": "the supply rail"},
                        "supply_range_v": {"value": [3, 5], "verified": True, "source": "bench"}}}
    return dict(record, **overrides)


class ListUnverifiedFactsTest(unittest.TestCase):
    def test_a_guessed_outline_is_listed_with_its_pair_its_why_its_source_and_where_it_goes_back(self):
        rows = provenance.list_unverified_facts({"body_mm": {"width": 34, "height": 26, "verified": False, "source": "a guess",
                                                             "why_it_matters": "the fit", "cites": ["page 2"]}})
        self.assertEqual(rows, [{"fact": "body_mm", "assumed": {"width": 34, "height": 26}, "why_it_matters": "the fit",
                                 "source": "a guess", "write": "body_mm"}])

    def test_a_verified_outline_and_a_block_with_no_verified_are_not_listed(self):
        for body in ({"width": 34, "height": 26, "verified": True, "source": "bench"}, {"width": 34, "height": 26}):
            with self.subTest(body=body):
                self.assertEqual(provenance.list_unverified_facts({"body_mm": body}), [])

    def test_the_facts_come_first_then_the_pin_order_then_the_outline_each_with_its_write_key(self):
        record = joystick()
        record["facts"]["odd"] = 5  # a bare value where a fact belongs: nobody checked it
        rows = provenance.list_unverified_facts(record)
        self.assertEqual([(row["fact"], row["write"]) for row in rows],
                         [("runs_at_3v3", "facts.runs_at_3v3"), ("odd", "facts.odd"), ("pin_order", "pin_order_proof"),
                          ("body_mm", "body_mm")])
        self.assertEqual(rows[1]["assumed"], 5)
        self.assertEqual(rows[2]["assumed"], ["GND", "VCC", "X"])
        self.assertEqual(rows[2]["why_it_matters"], "a pin order read wrong reverses a supply or swaps a signal")

    def test_a_facts_that_is_no_object_is_one_row_with_no_write_key_and_never_a_traceback(self):
        rows = provenance.list_unverified_facts(joystick(facts=5))
        self.assertEqual([(row["fact"], row["write"]) for row in rows], [("facts", None)])
        self.assertIn("repair the file by hand", rows[0]["why_it_matters"])
        self.assertEqual(provenance.list_unverified_facts({}), [])


class ListEntryProblemsTest(unittest.TestCase):
    GOOD = {"value": 3.3, "verified": True, "source": "bench, 2026-10-29, meter on the owned board, Petr Smejkal"}

    def test_a_good_entry_has_no_problem_and_a_nothing_is_the_callers_to_refuse(self):
        self.assertEqual(provenance.list_entry_problems({"runs_at_3v3": self.GOOD}, {"other": self.GOOD}), [])
        self.assertEqual(provenance.list_entry_problems({"runs_at_3v3": self.GOOD}, None), [])
        for nothing in (None, {}, []):
            self.assertEqual(provenance.list_entry_problems(nothing, [1]), [])

    def test_entries_that_are_no_object_give_one_problem(self):
        self.assertEqual(provenance.list_entry_problems([self.GOOD], {}), ["facts is [%r], but it is an object of facts" % self.GOOD])

    def test_a_name_outside_lowercase_letters_digits_and_underscores_is_one_problem(self):
        for name in ("Bad Name", "line\nbreak", "ünï", "a-b"):
            with self.subTest(name=name):
                self.assertEqual(provenance.list_entry_problems({name: self.GOOD}, {}),
                                 ["%r is no fact name: use lowercase letters, digits and underscores" % name])

    def test_a_held_facts_that_is_no_object_is_one_problem_to_repair_by_hand(self):
        self.assertEqual(provenance.list_entry_problems({"a": self.GOOD}, ["x"]),
                         ["the record's own facts is ['x'], but it is an object — repair the file by hand first"])


if __name__ == "__main__":
    unittest.main()
