"""P738: data/fact-needs.json names a real reader for every fact it lists, and FactNeeds answers by kind and by fact."""

import importlib
import inspect
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.records.fact_needs import FactNeed, FactNeeds, READS, WILL_READ  # noqa: E402

NEEDS = FactNeeds.from_file()
CARD = re.compile(r"P\d+")


def consumer_of(need):
    """The module or class a row names, imported; a class is the last segment of a module path."""
    try:
        return importlib.import_module(need.consumer)
    except ModuleNotFoundError:
        module, _, attr = need.consumer.rpartition(".")
        return getattr(importlib.import_module(module), attr)


class EveryRowIsWellFormedTest(unittest.TestCase):
    def test_every_row_has_a_kind_a_fact_a_consumer_and_a_known_status(self):
        for need in NEEDS.rows:
            with self.subTest(row=need):
                self.assertTrue(need.kind and need.fact_path and need.consumer)
                self.assertIn(need.status, (READS, WILL_READ))
                if need.reads:
                    self.assertIsNone(need.card, "a consumer that reads today names no card")
                else:
                    self.assertTrue(CARD.fullmatch(need.card or ""), "a will-read row names the card that makes it read")


class EveryConsumerExistsTest(unittest.TestCase):
    def test_every_consumer_imports(self):
        for need in NEEDS.rows:
            with self.subTest(row=need):
                self.assertIsNotNone(consumer_of(need), "the file names a consumer that does not exist: %r" % (need,))

    def test_a_consumer_that_reads_today_names_the_fact_in_its_source(self):
        for need in (need for need in NEEDS.rows if need.reads):
            with self.subTest(row=need):
                self.assertIn('"%s"' % need.fact_name, inspect.getsource(consumer_of(need)),
                              "%s says it reads %s and its source does not name it" % (need.consumer, need.fact_path))


class FactNeedsAnswerTest(unittest.TestCase):
    def test_by_kind(self):
        self.assertEqual(len(NEEDS.of_kind("module")), 5)
        self.assertEqual(NEEDS.of_kind("board"), [])

    def test_by_the_write_key_of_an_open_fact_exactly(self):
        self.assertEqual([need.consumer for need in NEEDS.of_fact("body_mm")],
                         ["spark.design.board_components", "spark.design.need_requirements"])
        self.assertEqual(NEEDS.of_fact("physical"), [], "a block's write key is the block, and its rows are per key")
        self.assertEqual(NEEDS.of_fact("facts.x"), [])

    def test_a_need_knows_its_fact_name_and_its_envelope_entry(self):
        need = FactNeed("module", "physical.header", "spark.x.Y", WILL_READ, "P734")
        self.assertEqual((need.fact_name, need.reads), ("header", False))
        self.assertEqual(need.to_dict(), {"consumer": "spark.x.Y", "status": "will read", "card": "P734"})


if __name__ == "__main__":
    unittest.main()
