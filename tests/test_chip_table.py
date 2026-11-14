"""
The chip table (P809): `data/chips.json` holds each chip's `adc2_used_by_wifi`, cited to a kept ESP-IDF file, and
`chip_table` reads it as RECORDED or NOT_CHECKED.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from spark.core import outcomes  # noqa: E402
from spark.records import chip_table  # noqa: E402
from spark.records import record_kind  # noqa: E402


class TheShippedTableTest(unittest.TestCase):
    """Each chip's fact is true, false or null, and cites a document the table keeps."""

    def setUp(self):
        self.held = json.loads(chip_table.FILE.read_text())

    def test_each_fact_is_a_bool_or_null_with_a_citation(self):
        for chip, facts in self.held["chips"].items():
            with self.subTest(chip=chip):
                fact = facts["adc2_used_by_wifi"]
                self.assertIn(fact["value"], (True, False, None))
                self.assertIn(fact["cites"]["document"], self.held["documents"])
                self.assertTrue(fact["cites"]["at"])

    def test_the_documents_and_citations_meet_the_records_rule(self):
        self.assertEqual(record_kind.document_problems(self.held), [])


class TheLookupTest(unittest.TestCase):
    """A fact read is RECORDED with its value; a chip the table lacks, a null or a chip that is no string, NOT_CHECKED."""

    TABLE = chip_table.ChipTable.from_dict({
        "yes": {"adc2_used_by_wifi": {"value": True}},
        "no": {"adc2_used_by_wifi": {"value": False}},
        "open": {"adc2_used_by_wifi": {"value": None}},
    })

    def test_a_recorded_fact_gives_its_value(self):
        self.assertEqual(self.TABLE.adc2_used_by_wifi("yes"), chip_table.ChipFact(outcomes.RECORDED, True))
        self.assertEqual(self.TABLE.adc2_used_by_wifi("no"), chip_table.ChipFact(outcomes.RECORDED, False))

    def test_no_fact_is_not_checked_with_its_why(self):
        for chip in ("open", "absent", 5, None):
            with self.subTest(chip=chip):
                fact = self.TABLE.adc2_used_by_wifi(chip)
                self.assertEqual((fact.state, fact.value), (outcomes.NOT_CHECKED, None))
                self.assertIn(repr(chip), fact.why)

    def test_the_table_cannot_be_changed(self):
        with self.assertRaises(TypeError):
            self.TABLE.chips["yes"] = {}


if __name__ == "__main__":
    unittest.main()
