"""
The library's XIAO ESP32-C6 record builds a button and an LED (P278, #314).

Its power, power pads, Wokwi power pins, documents and physical facts come from the record that was checked at the bench
(`tests/data/breadboard/button-light-xiao/boards/xiao-esp32-c6-fresh.json`, P229), and the facts both records state
agree, but the regulator's rating and its datasheet, read in P346 (READ_AFTER_THE_BENCH_RECORD).

    python3 -m unittest tests.test_xiao_record
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite_temp  # noqa: E402,F401
from suite_runs import slow  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.records import board_records, store  # noqa: E402
from spark.design import loader, power_rails  # noqa: E402
from spark.checks import physics_check  # noqa: E402

SHIPPED = json.loads((ROOT / "boards" / "xiao-esp32-c6.json").read_text())
FRESH = json.loads((ROOT / "tests" / "data" / "breadboard" / "button-light-xiao" / "boards"
                    / "xiao-esp32-c6-fresh.json").read_text())

# The regulator's rating and its datasheet were read in P346, after the P229 bench record, so the fixture lacks them.
READ_AFTER_THE_BENCH_RECORD = {"power": "regulator_3v3_a", "documents": "sgm6029-datasheet-rev-a-1"}
SGM6029_SHA256 = "79d7e25abc3acfd18ab9c394e082663e07dc169151b4bfe0314c13510ced63e0"


@slow("a real build of the library XIAO with a button and an LED, 3 tests, 5.8 s on 2026-10-26")
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
    def test_power_equals_the_fresh_record_but_for_the_facts_of_the_board_s_own_power_parts(self):
        self.assertIsNone(FRESH["power"][READ_AFTER_THE_BENCH_RECORD["power"]]["value"])
        own = ("charger", "regulator", "battery_input")
        read_later = READ_AFTER_THE_BENCH_RECORD["power"]
        self.assertEqual({name: fact for name, fact in SHIPPED["power"].items() if name not in own + (read_later,)},
                         {name: fact for name, fact in FRESH["power"].items() if name != read_later})
        self.assertEqual(sorted(set(SHIPPED["power"]) - set(FRESH["power"])), sorted(own))
        self.assertEqual(SHIPPED["power"]["io_volts"]["value"], 3.3)

    def test_power_pads_equal_the_fresh_record(self):
        self.assertEqual(SHIPPED["power_pads"], FRESH["power_pads"])

    def test_wokwi_power_pins_equal_the_fresh_record_and_name_every_power_pad(self):
        self.assertEqual(SHIPPED["wokwi_power_pins"], FRESH["wokwi_power_pins"])
        self.assertLessEqual(set(SHIPPED["power_pads"]), set(SHIPPED["wokwi_power_pins"]))

    def test_documents_equal_the_fresh_record_but_the_p346_datasheet_each_with_a_url_and_a_sha256(self):
        read_later = READ_AFTER_THE_BENCH_RECORD["documents"]
        self.assertNotIn(read_later, FRESH["documents"])
        self.assertEqual({name: one for name, one in SHIPPED["documents"].items() if name != read_later},
                         FRESH["documents"])
        for name, document in SHIPPED["documents"].items():
            self.assertTrue(document["url"].startswith("https://"), name)
            self.assertRegex(document["sha256"], r"^[0-9a-f]{64}$", name)

    def test_every_cite_in_the_record_names_a_kept_document(self):
        def cites(node, where=""):
            if isinstance(node, dict):
                if isinstance(node.get("cites"), dict):
                    yield where, node["cites"]["document"]
                for key, value in node.items():
                    yield from cites(value, where + "." + key)
        found = list(cites(SHIPPED))
        self.assertGreaterEqual(len(found), 5)
        for where, document in found:
            self.assertIn(document, SHIPPED["documents"], where)

    def test_physical_equals_the_fresh_record_except_the_footprint_module_name(self):
        left = {k: v for k, v in SHIPPED["physical"].items() if "footprint_module" not in k}
        right = {k: v for k, v in FRESH["physical"].items() if "footprint_module" not in k}
        self.assertEqual(left, right)
        self.assertEqual(SHIPPED["physical"]["footprint_module"], "XIAO-ESP32-C6-SMD")

    def test_the_buttons_name_a_silkscreen_and_a_place_and_cite_the_photo_note(self):
        buttons = SHIPPED["physical"]["buttons"]
        self.assertEqual((buttons["boot"]["silkscreen"], buttons["reset"]["silkscreen"]), ("B", "R"))
        self.assertIn("top right", buttons["boot"]["place"])
        self.assertIn("top left", buttons["reset"]["place"])
        self.assertTrue(buttons["seen_from"])
        self.assertIn("2026-10-19-p213b2-xiao-buttons.md", SHIPPED["physical"]["//buttons"])

    def test_the_header_pins_equal_in_both_records(self):
        for name, gpio in SHIPPED["pins"].items():
            self.assertEqual(FRESH["pins"][name], gpio, name)

    def test_fresh_adds_only_tx_and_rx_which_pad_aliases_reach(self):
        self.assertEqual(set(FRESH["pins"]) - set(SHIPPED["pins"]), {"TX", "RX"})
        self.assertEqual((SHIPPED["physical"]["pad_aliases"]["TX"], SHIPPED["physical"]["pad_aliases"]["RX"]), ("D6", "D7"))


class TheRegulatorIsRatedFromItsMakersDatasheetTest(unittest.TestCase):
    def test_the_3v3_rating_is_one_amp_verified_from_the_sgm6029_datasheet(self):
        fact = SHIPPED["power"]["regulator_3v3_a"]
        self.assertEqual(fact["value"], 1.0)
        self.assertIs(fact["verified"], True)
        self.assertEqual(fact["cites"], {"document": "sgm6029-datasheet-rev-a-1",
                                         "at": "Recommended Operating Conditions, page 3"})
        self.assertIn("0.7A", fact["source"])
        self.assertIn("VIN < 2.3V", fact["source"])
        document = SHIPPED["documents"]["sgm6029-datasheet-rev-a-1"]
        self.assertEqual(document["sha256"], SGM6029_SHA256)
        self.assertEqual(document["version"], "Rev. A.1, November 2022")
        self.assertEqual(document["file"], "SGM6029.pdf")  # the name the kept file sits under: sources/<sha256>/<file>
        self.assertTrue(document["url"].startswith("https://www.sg-micro.com/"))
        self.assertNotIn("access_token", document["url"])

    def test_the_walks_button_and_led_on_the_library_xiao_leave_the_3v3_rail_nothing_to_say(self):
        with tempfile.TemporaryDirectory() as scratch:
            folder = Path(scratch) / "project"
            folder.mkdir()
            requirements = folder / "requirements.json"
            requirements.write_text(json.dumps(
                {"board": "xiao-esp32-c6", "parts": ["tactile-button", "led-red-5mm"]}))
            with mock.patch.dict(os.environ, {"SPARK_HOME": str(Path(scratch) / "home")}):
                found = store.records("boards", board_records.LIBRARY, project=folder)
                self.assertEqual(found["xiao-esp32-c6"][0], "library")
                made = loader.load(requirements)
                loads = power_rails.rail_loads(made.parts, made.board)
        self.assertAlmostEqual(loads["V33"]["amps"], 0.354)
        self.assertTrue(loads["V33"]["complete"])
        self.assertEqual(physics_check.check_rail_supply(loads), [])


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
        self.assertEqual(board_records.validate(SHIPPED, path), [])

    def test_the_fab_gate_finds_no_problem_in_the_library_xiao(self):
        path = ROOT / "boards" / "xiao-esp32-c6.json"
        self.assertEqual(board_records.validate(SHIPPED, path, for_fab=True), [])


if __name__ == "__main__":
    unittest.main()
