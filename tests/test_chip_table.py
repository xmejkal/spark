"""
The chip table (P809): `data/chips.json` holds each chip's `adc2_used_by_wifi`, cited to a kept ESP-IDF file, and
`chip_table` reads it as RECORDED or NONE_RECORDED. P813: the ESP32-C3 also holds `adc2_oneshot_supported` (false), cited
to the kept adc_oneshot.rst, and `adc2_gpio` (its ADC2 pin), cited to its kept adc_channel.h. P990: the ESP32, the S3
and the C6 hold their radios, each true and cited to the chip's kept soc_caps.h, and `radios` reads them. P1013: the same
three hold `wifi_band`, cited to a page of the chip's datasheet, and `wifi_band` reads it.
"""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parents[1]
#: The radio facts a chip may hold (P990), the names the table's rows use.
RADIOS = ("wifi", "bluetooth_le", "ieee802154")
#: The datasheet each chip's `wifi_band` cites (P1013).
DATASHEETS = {"esp32": "esp32-datasheet-v5-3", "esp32s3": "esp32-s3-datasheet-v2-2", "esp32c6": "esp32-c6-datasheet-v1-5"}
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
            for name in ("adc2_used_by_wifi", "adc2_oneshot_supported", "adc2_gpio", "wifi_band"):
                if name not in facts and name != "adc2_used_by_wifi":
                    continue
                with self.subTest(chip=chip, fact=name):
                    fact = facts[name]
                    if name == "adc2_gpio":
                        self.assertTrue(isinstance(fact["value"], list) and fact["value"]
                                        and all(type(gpio) is int for gpio in fact["value"]), fact["value"])
                    elif name == "wifi_band":
                        self.assertTrue(isinstance(fact["value"], str) and fact["value"].strip(), fact["value"])
                    else:
                        self.assertIn(fact["value"], (True, False, None))
                    self.assertIn(fact["cites"]["document"], self.held["documents"])
                    self.assertTrue(fact["cites"]["at"])
            self.assertLessEqual(set(facts), {"adc2_used_by_wifi", "adc2_oneshot_supported", "adc2_gpio",
                                              "wifi_band", *RADIOS}, chip)

    def test_a_chip_whose_adc2_oneshot_is_unsupported_names_its_adc2_pins(self):
        for chip, facts in self.held["chips"].items():
            if facts.get("adc2_oneshot_supported", {}).get("value") is False:
                with self.subTest(chip=chip):
                    self.assertIsNotNone(chip_table.load().adc2_gpio(chip))

    def test_the_c3_facts_are_the_sources(self):
        held = {chip: {name: fact["value"] for name, fact in facts.items()
                       if name not in ("adc2_used_by_wifi", "wifi_band") and name not in RADIOS}
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

    def test_the_shipped_radios_are_the_sources(self):
        table = chip_table.load()
        self.assertEqual({chip: table.radios(chip) for chip in self.held["chips"] if table.radios(chip)},
                         {"esp32": ("wifi", "bluetooth_le"), "esp32s3": ("wifi", "bluetooth_le"),
                          "esp32c6": ("wifi", "bluetooth_le", "ieee802154")})

    def test_each_radio_fact_is_true_and_cites_its_chips_soc_caps_line(self):
        for chip, facts in self.held["chips"].items():
            for name in RADIOS:
                if name in facts:
                    with self.subTest(chip=chip, radio=name):
                        self.assertIs(facts[name]["value"], True)
                        self.assertEqual(facts[name]["cites"]["document"], "esp-idf-soc-caps-v5-5-1-" + chip)
                        self.assertRegex(facts[name]["cites"]["at"], r"^line \d+: SOC_")

    def test_the_radio_documents_are_the_kept_files(self):
        documents = self.held["documents"]
        self.assertEqual({key: (documents[key]["sha256"], documents[key]["file"]) for key in
                          ("esp-idf-soc-caps-v5-5-1-esp32", "esp-idf-soc-caps-v5-5-1-esp32s3", "esp-idf-soc-caps-v5-5-1-esp32c6")},
                         {"esp-idf-soc-caps-v5-5-1-esp32": ("45e1fb7f6c226d07229613e0cabcbc67034913a454c9fed7178743255620b394",
                                                            "esp-idf-v5.5.1-esp32-soc_caps.h"),
                          "esp-idf-soc-caps-v5-5-1-esp32s3": ("25ff368906aaee06e77022aa50227a2ab7c9b4739da1f34c48f64c87052925a4",
                                                              "esp-idf-v5.5.1-esp32s3-soc_caps.h"),
                          "esp-idf-soc-caps-v5-5-1-esp32c6": ("43e1668e045daf9b419fff29c4c647d8f48b065b744a48a2ffebfaf8bb358169",
                                                              "esp-idf-v5.5.1-esp32c6-soc_caps.h")})

    def test_the_shipped_wifi_bands_are_the_sources(self):
        table = chip_table.load()
        self.assertEqual({chip: table.wifi_band(chip) for chip in self.held["chips"] if table.wifi_band(chip)},
                         {"esp32": "2.4 GHz", "esp32s3": "2.4 GHz", "esp32c6": "2.4 GHz"})

    def test_each_wifi_band_cites_a_page_of_its_chips_datasheet_and_the_chip_has_wifi(self):
        self.assertEqual({chip for chip, facts in self.held["chips"].items() if "wifi_band" in facts}, set(DATASHEETS))
        for chip, facts in self.held["chips"].items():
            if "wifi_band" in facts:
                with self.subTest(chip=chip):
                    self.assertEqual(facts["wifi_band"]["cites"]["document"], DATASHEETS[chip])
                    self.assertTrue(facts["wifi_band"]["cites"]["at"].startswith("page "), facts["wifi_band"]["cites"]["at"])
                    self.assertIs(facts["wifi"]["value"], True)

    def test_the_band_documents_are_the_kept_datasheets(self):
        documents = self.held["documents"]
        self.assertEqual({key: (documents[key]["sha256"], documents[key]["version"]) for key in DATASHEETS.values()},
                         {"esp32-datasheet-v5-3": ("a7917e6b47528c9dcab06837a49d452e582751335797db879f1cf2d17cd29adf", "5.3"),
                          "esp32-s3-datasheet-v2-2": ("2d5a7cb7fd559d8d972bd88db32669c0196d23f22d7afaafb0f63d099b589a3f", "2.2"),
                          "esp32-c6-datasheet-v1-5": ("372a5b42b2900c83ef4309149c8835e9ae2d1be19244995bf2fb83af4dc5edf1", "1.5")})

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

    def test_radios_gives_the_true_radio_facts_in_table_order(self):
        table = chip_table.ChipTable.from_dict({
            "c": {"ieee802154": {"value": True}, "adc2_used_by_wifi": {"value": True}, "wifi": {"value": True}},
            "odd": {"wifi": {"value": None}, "bluetooth_le": {"value": False}, "ieee802154": {"value": "yes"}},
            "one": {"wifi": {"value": 1}, "bluetooth_le": {}, "ieee802154": True},
        })
        self.assertEqual(table.radios("c"), ("wifi", "ieee802154"))
        for chip in ("odd", "one", "absent", 5, None):
            with self.subTest(chip=chip):
                self.assertEqual(table.radios(chip), ())

    def test_wifi_band_gives_a_band_in_words_or_none_for_no_fact(self):
        table = chip_table.ChipTable.from_dict({
            "two": {"wifi_band": {"value": "2.4 GHz"}},
            "open": {"wifi_band": {"value": None}},
            "empty": {"wifi_band": {"value": ""}},
            "blank": {"wifi_band": {"value": "  "}},
            "number": {"wifi_band": {"value": 5}},
            "flag": {"wifi_band": {"value": True}},
            "bare": {"wifi_band": {}},
        })
        self.assertEqual(table.wifi_band("two"), "2.4 GHz")
        for chip in ("open", "empty", "blank", "number", "flag", "bare", "absent", None):
            with self.subTest(chip=chip):
                self.assertIsNone(table.wifi_band(chip))

    def test_the_table_cannot_be_changed(self):
        with self.assertRaises(TypeError):
            self.TABLE.chips["yes"] = {}


if __name__ == "__main__":
    unittest.main()
