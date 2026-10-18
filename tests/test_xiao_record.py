"""
The library's XIAO ESP32-C6 record builds a button and an LED (P278, #314).

Its power, power pads, Wokwi power pins, documents and physical facts come from the record that was checked at the bench
(`tests/data/breadboard/button-light-xiao/boards/xiao-esp32-c6-fresh.json`, P229), and the facts both records state
agree.

    python3 -m unittest tests.test_xiao_record
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite_temp  # noqa: E402,F401

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import boards  # noqa: E402

SHIPPED = json.loads((ROOT / "boards" / "xiao-esp32-c6.json").read_text())
FRESH = json.loads((ROOT / "tests" / "data" / "breadboard" / "button-light-xiao" / "boards"
                    / "xiao-esp32-c6-fresh.json").read_text())


class TheLibraryXiaoBuildsAButtonAndAnLedTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work = Path(tempfile.mkdtemp())
        (cls.work / "requirements.json").write_text(json.dumps(
            {"board": "xiao-esp32-c6", "parts": ["tactile-button", "led-red-5mm"]}))
        env = dict(os.environ, SPARK_HOME=str(cls.work / "home"))
        cls.result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_spine.py"), str(cls.work / "requirements.json"),
             "--keep", str(cls.work / "out"), "--json"],
            capture_output=True, text=True, env=env, cwd=cls.work)
        cls.said = json.loads(cls.result.stdout)

    def test_the_build_exits_0_with_every_stage_ok(self):
        self.assertEqual(self.result.returncode, 0, self.result.stdout[-1500:])
        self.assertEqual({stage["name"]: stage["status"] for stage in self.said["stages"]},
                         {name: "ok" for name in ("board", "schematic", "footprint", "build", "simulation")})

    def test_the_drawn_breadboard_is_written(self):
        drawn = json.loads((self.work / "out" / "breadboard.json").read_text())
        self.assertIn("board-xiao-esp32-c6", [one["type"] for one in drawn["parts"]])

    def test_the_pin_map_names_the_pull_the_button_needs_from_the_chips_pull_up(self):
        pins = (self.work / "out" / "firmware" / "pins.py").read_text()
        self.assertIn('BUTTON_PULL = "up"', pins)


class TheCopiedFactsEqualTheCheckedRecordTest(unittest.TestCase):
    def test_power_equals_the_fresh_record(self):
        self.assertEqual(SHIPPED["power"], FRESH["power"])
        self.assertEqual(SHIPPED["power"]["io_volts"]["value"], 3.3)

    def test_power_pads_equal_the_fresh_record(self):
        self.assertEqual(SHIPPED["power_pads"], FRESH["power_pads"])

    def test_wokwi_power_pins_equal_the_fresh_record_and_name_every_power_pad(self):
        self.assertEqual(SHIPPED["wokwi_power_pins"], FRESH["wokwi_power_pins"])
        self.assertLessEqual(set(SHIPPED["power_pads"]), set(SHIPPED["wokwi_power_pins"]))

    def test_documents_equal_the_fresh_record_each_with_a_url_and_a_sha256(self):
        self.assertEqual(SHIPPED["documents"], FRESH["documents"])
        for name, document in SHIPPED["documents"].items():
            self.assertTrue(document["url"].startswith("https://"), name)
            self.assertRegex(document["sha256"], r"^[0-9a-f]{64}$", name)

    def test_every_cite_in_power_names_a_kept_document(self):
        for fact, entry in SHIPPED["power"].items():
            cite = entry.get("cites")
            if cite:
                self.assertIn(cite["document"], SHIPPED["documents"], fact)

    def test_physical_equals_the_fresh_record_except_the_footprint_module_name(self):
        left = {k: v for k, v in SHIPPED["physical"].items() if "footprint_module" not in k}
        right = {k: v for k, v in FRESH["physical"].items() if "footprint_module" not in k}
        self.assertEqual(left, right)
        self.assertEqual(SHIPPED["physical"]["footprint_module"], "XIAO-ESP32-C6-SMD")

    def test_the_header_pins_equal_in_both_records(self):
        header = {name: gpio for name, gpio in SHIPPED["pins"].items()}
        for name, gpio in header.items():
            self.assertEqual(FRESH["pins"][name], gpio, name)

    def test_fresh_adds_only_tx_and_rx_which_pad_aliases_reach(self):
        self.assertEqual(set(FRESH["pins"]) - set(SHIPPED["pins"]), {"TX", "RX"})
        self.assertEqual((SHIPPED["physical"]["pad_aliases"]["TX"], SHIPPED["physical"]["pad_aliases"]["RX"]), ("D6", "D7"))


class TheFactsBothRecordsStateAgreeTest(unittest.TestCase):
    def test_deep_sleep_agrees(self):
        self.assertEqual(SHIPPED["deep_sleep"], FRESH["deep_sleep"])

    def test_adc_gpio_agrees_and_adds_no_pin_to_the_header(self):
        self.assertEqual(SHIPPED["adc_gpio"], FRESH["adc_gpio"])
        on_header = set(SHIPPED["pins"].values())
        self.assertEqual(sorted(set(SHIPPED["adc_gpio"]) & on_header), [0, 1, 2])

    def test_flash_mb_agrees(self):
        self.assertEqual((SHIPPED["flash_mb"], FRESH["flash_mb"]), (4, 4))

    def test_wake_capable_gpio_agrees(self):
        self.assertEqual(SHIPPED["wake_capable_gpio"], FRESH["wake_capable_gpio"])


class TheLibraryXiaoIsAValidBoardTest(unittest.TestCase):
    def test_validate_finds_no_problem(self):
        path = ROOT / "boards" / "xiao-esp32-c6.json"
        self.assertEqual(boards.validate(SHIPPED, path), [])

    def test_the_fab_gate_answers_as_before_for_the_library_xiao(self):
        path = ROOT / "boards" / "xiao-esp32-c6.json"
        self.assertEqual(boards.validate(SHIPPED, path, for_fab=True), [])


if __name__ == "__main__":
    unittest.main()
