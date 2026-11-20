"""
The chip table (P809): `data/chips.json` holds each chip's `adc2_used_by_wifi`, cited to a kept ESP-IDF file, and
`chip_table` reads it as RECORDED or NONE_RECORDED. P813: the ESP32-C3 also holds `adc2_oneshot_supported` (false), cited
to the kept adc_oneshot.rst, and `adc2_gpio` (its ADC2 pin), cited to its adc_channel.h, which is not yet kept.
"""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

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
            for name in ("adc2_used_by_wifi", "adc2_oneshot_supported", "adc2_gpio"):
                if name not in facts and name != "adc2_used_by_wifi":
                    continue
                with self.subTest(chip=chip, fact=name):
                    fact = facts[name]
                    if name == "adc2_gpio":
                        self.assertTrue(isinstance(fact["value"], list) and fact["value"]
                                        and all(type(gpio) is int for gpio in fact["value"]), fact["value"])
                    else:
                        self.assertIn(fact["value"], (True, False, None))
                    self.assertIn(fact["cites"]["document"], self.held["documents"])
                    self.assertTrue(fact["cites"]["at"])
            self.assertLessEqual(set(facts), {"adc2_used_by_wifi", "adc2_oneshot_supported", "adc2_gpio"}, chip)

    def test_a_chip_whose_adc2_oneshot_is_unsupported_names_its_adc2_pins(self):
        for chip, facts in self.held["chips"].items():
            if facts.get("adc2_oneshot_supported", {}).get("value") is False:
                with self.subTest(chip=chip):
                    self.assertIsNotNone(chip_table.load().adc2_gpio(chip))

    def test_the_c3_facts_are_the_sources(self):
        held = {chip: {name: fact["value"] for name, fact in facts.items() if name != "adc2_used_by_wifi"}
                for chip, facts in self.held["chips"].items()}
        self.assertEqual({chip: facts for chip, facts in held.items() if facts},
                         {"esp32c3": {"adc2_oneshot_supported": False, "adc2_gpio": [5]}})
        self.assertEqual(chip_table.load().adc2_oneshot_supported("esp32c3"),
                         chip_table.ChipFact(outcomes.RECORDED, False))
        self.assertEqual(chip_table.load().adc2_gpio("esp32c3"), (5,))

    def test_the_shipped_values_are_the_sources(self):
        values = {chip: facts["adc2_used_by_wifi"]["value"] for chip, facts in self.held["chips"].items()}
        self.assertEqual(values, {"esp32": True, "esp32s2": True, "esp32s3": True, "esp32c3": None, "esp32p4": False,
                                  "esp32c2": False, "esp32c5": False, "esp32c6": False, "esp32c61": False,
                                  "esp32h2": False})

    def test_load_reads_the_shipped_table(self):
        self.assertEqual(chip_table.load().adc2_used_by_wifi("esp32s3"), chip_table.ChipFact(outcomes.RECORDED, True))

    def test_the_documents_and_citations_meet_the_records_rule(self):
        self.assertEqual(record_kind.document_problems(self.held), [])


class TheLookupTest(unittest.TestCase):
    """A fact read is RECORDED with its value; a chip the table lacks, a null or a chip that is no string, NONE_RECORDED."""

    TABLE = chip_table.ChipTable.from_dict({
        "yes": {"adc2_used_by_wifi": {"value": True}},
        "no": {"adc2_used_by_wifi": {"value": False}},
        "open": {"adc2_used_by_wifi": {"value": None}},
    })

    def test_a_recorded_fact_gives_its_value(self):
        self.assertEqual(self.TABLE.adc2_used_by_wifi("yes"), chip_table.ChipFact(outcomes.RECORDED, True))
        self.assertEqual(self.TABLE.adc2_used_by_wifi("no"), chip_table.ChipFact(outcomes.RECORDED, False))

    def test_no_fact_is_none_recorded(self):
        for chip in ("open", "absent", 5, None):
            with self.subTest(chip=chip):
                self.assertEqual(self.TABLE.adc2_used_by_wifi(chip), chip_table.ChipFact(outcomes.NONE_RECORDED))

    def test_adc2_oneshot_supported_is_read_as_adc2_used_by_wifi_is(self):
        table = chip_table.ChipTable.from_dict({
            "no": {"adc2_oneshot_supported": {"value": False}},
            "open": {"adc2_oneshot_supported": {"value": None}},
            "other": {"adc2_used_by_wifi": {"value": False}},
        })
        self.assertEqual(table.adc2_oneshot_supported("no"), chip_table.ChipFact(outcomes.RECORDED, False))
        for chip in ("open", "other", "absent", 5, None):
            with self.subTest(chip=chip):
                self.assertEqual(table.adc2_oneshot_supported(chip), chip_table.ChipFact(outcomes.NONE_RECORDED))

    def test_adc2_gpio_is_a_tuple_of_numbers_or_none_for_no_fact(self):
        table = chip_table.ChipTable.from_dict({
            "two": {"adc2_gpio": {"value": [5, 6]}},
            "open": {"adc2_gpio": {"value": None}},
            "odd": {"adc2_gpio": {"value": [5, "6"]}},
            "flag": {"adc2_gpio": {"value": [True]}},
            "word": {"adc2_gpio": {"value": "5"}},
            "other": {"adc2_used_by_wifi": {"value": True}},
        })
        self.assertEqual(table.adc2_gpio("two"), (5, 6))
        for chip in ("open", "odd", "flag", "word", "other", "absent", 5, None):
            with self.subTest(chip=chip):
                self.assertIsNone(table.adc2_gpio(chip))

    def test_the_table_cannot_be_changed(self):
        with self.assertRaises(TypeError):
            self.TABLE.chips["yes"] = {}


if __name__ == "__main__":
    unittest.main()
