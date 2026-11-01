"""
P484 (#663): the board's own LED and button are wired parts in a board-only build's Wokwi diagram. The reader picks
the rows spark can wire, the converter input is read from the part records, the limits word a wired GPIO apart, and
the build runs the real converter bundle on Node (skipped without it).
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import boards  # noqa: E402
import breadboard  # noqa: E402
import check_spine  # noqa: E402
import onboard_parts  # noqa: E402
import store  # noqa: E402
from onboard_parts import OnboardPartReader  # noqa: E402

LED = {"id": "led-red-5mm", "onboard": "firebeetle2-esp32s3", "_instance": "onboard_led", "gpio": 21, "pin": "D13"}
BUTTON = {"id": "tactile-button", "onboard": "firebeetle2-esp32s3", "_instance": "onboard_button", "gpio": 47, "pin": "D14"}
WIRED_LED = ("the Wokwi stand-in has no LED on GPIO21, so spark wires Wokwi's LED to GPIO21 in its place: a passed run "
             "shows the level a scenario read on GPIO21, not a PWM duty or a brightness, nor that the board's own LED "
             "lights. Test it on the board.")
NOT_CHECKED = ("not checked: spark's store lacks the Wokwi definition that the board record names, its sha256 differs, or it "
               "does not parse")
WIRED_BUTTON = ("the Wokwi stand-in has no button on GPIO47, so spark wires Wokwi's pushbutton to GPIO47 in its place: a "
                "scenario presses that part, not the board's own button. Test it on the board.")
UNWIRED_BUTTON = ("the Wokwi part of firebeetle2-esp32s3 is a stand-in, where GPIO47 is a bare header pin with no onboard "
                  "LED or button, so spark knows no way for a scenario to press it. Test it on the board.")
DEVKIT = '{"pins": {"21": {"target": "GPIO21"}, "47": {"target": "GPIO47"}, "GND": {"target": "GND"}}}'


def firebeetle(**roles):
    """The shipped FireBeetle record, its pin_roles entries updated by `roles` ({role: {key: value}})."""
    board = boards.load(ROOT, "firebeetle2-esp32s3")
    for role, changes in roles.items():
        board["pin_roles"][role].update(changes)
    return board


class TheReaderPicksTheRowsSparkCanWireTest(unittest.TestCase):
    def test_the_firebeetle_gives_its_led_and_button_with_the_record_s_pin_keys(self):
        self.assertEqual(OnboardPartReader(firebeetle()).parts(), [LED, BUTTON])

    def test_a_board_that_is_no_stand_in_gives_none(self):
        self.assertEqual(OnboardPartReader(boards.load(ROOT, "xiao-esp32-c6")).parts(), [])
        self.assertEqual(OnboardPartReader(dict(firebeetle(), wokwi_is_stand_in="yes")).parts(), [])

    def test_a_level_the_part_is_not_wired_for_leaves_that_part_out(self):
        self.assertEqual(OnboardPartReader(firebeetle(onboard_led={"active_level": 0})).parts(), [BUTTON])
        self.assertEqual(OnboardPartReader(firebeetle(onboard_button={"active_level": True})).parts(), [LED])

    def test_a_level_given_as_a_fact_counts_and_a_missing_level_does_not(self):
        fact = {"value": 1, "verified": True, "source": "the bench"}
        self.assertEqual(OnboardPartReader(firebeetle(onboard_led={"active_level": fact})).parts(), [LED, BUTTON])
        board = firebeetle()
        del board["pin_roles"]["onboard_button"]["active_level"]
        self.assertEqual(OnboardPartReader(board).parts(), [LED])

    def test_a_row_on_two_gpios_or_on_no_header_pin_is_left_out(self):
        self.assertEqual(OnboardPartReader(firebeetle(onboard_led={"gpio": [21, 47]})).parts(), [BUTTON])
        self.assertEqual(OnboardPartReader(firebeetle(onboard_led={"gpio": [48]})).parts(), [BUTTON])

    def test_a_board_with_no_ground_pin_or_no_record_gives_none(self):
        self.assertEqual(OnboardPartReader(dict(firebeetle(), wokwi_power_pins={"3V3": "3V3.1"})).parts(), [])
        self.assertEqual(OnboardPartReader(None).parts(), [])

    def test_the_board_s_component_name_is_the_one_the_converter_matches(self):
        mapping = (ROOT / "tools" / "circuit-to-wokwi" / "lib" / "mapping.ts").read_text()
        self.assertIn('export const BOARD: PartMapping = {', mapping)
        board_block = mapping.split("export const BOARD: PartMapping = {", 1)[1].split("};", 1)[0]
        self.assertIn('match: "%s",' % breadboard.BOARD_COMPONENT, board_block)

    def test_every_wired_role_is_one_a_scenario_reaches(self):
        self.assertEqual(sorted(onboard_parts.ONBOARD_PARTS), sorted(role for role, spec in boards.ONBOARD_ROLES.items() if spec.scenario_verb))


class AWiredGpioHasItsOwnLimitTest(unittest.TestCase):
    def kept(self, board):
        """`board` with a hand-made devkit definition kept in the scratch store under its entry."""
        entry = board["documents"]["wokwi-board"]
        board["documents"]["wokwi-board"] = dict(entry, sha256=store.keep(DEVKIT.encode(), entry["file"]))
        return board

    def test_each_wired_gpio_says_what_its_part_stands_in_for(self):
        board = self.kept(firebeetle())
        said = boards.onboard_limits(board, onboard_parts.say_wired_gpios(OnboardPartReader(board).parts()))
        self.assertEqual(said, [("ONBOARD_LED (GPIO21)", WIRED_LED), ("ONBOARD_BUTTON (GPIO47)", WIRED_BUTTON)])

    def test_a_definition_not_in_the_store_says_not_checked_and_still_words_each_wired_gpio(self):
        board = firebeetle()  # the suite's scratch store holds no Wokwi definition
        said = boards.onboard_limits(board, onboard_parts.say_wired_gpios(OnboardPartReader(board).parts()))
        self.assertEqual(said, [("onboard GPIOs", NOT_CHECKED), ("ONBOARD_LED (GPIO21)", WIRED_LED),
                                ("ONBOARD_BUTTON (GPIO47)", WIRED_BUTTON)])
        self.assertEqual(boards.onboard_limits(board), [("onboard GPIOs", NOT_CHECKED)])

    def test_a_gpio_left_unwired_keeps_the_bare_header_pin_sentence(self):
        board = self.kept(firebeetle(onboard_button={"active_level": 1}))
        said = boards.onboard_limits(board, onboard_parts.say_wired_gpios(OnboardPartReader(board).parts()))
        self.assertEqual(said, [("ONBOARD_LED (GPIO21)", WIRED_LED), ("ONBOARD_BUTTON (GPIO47)", UNWIRED_BUTTON)])


class TheConverterInputComesFromThePartRecordsTest(unittest.TestCase):
    def test_the_netlist_wires_each_signal_pin_to_its_gpio_and_each_ground_pin_to_ground(self):
        files, why = onboard_parts.make_converter_input([LED, BUTTON], "GND1", ROOT)
        self.assertIsNone(why)
        self.assertEqual(files["wokwi-mapping.json"], {
            "onboard_led": {"wokwiType": "wokwi-led", "pins": {"A": "A", "K": "C"}, "attrs": {"color": "red"}},
            "onboard_button": {"wokwiType": "wokwi-pushbutton", "pins": {"A": "1.l", "B": "2.l"}, "attrs": {"color": "green"}}})
        self.assertEqual([[(member["componentId"], member["pinName"]) for member in net["members"]] for net in files["netlist.json"]["nets"]],
                         [[("Mcu", "D13"), ("onboard_led", "A")], [("Mcu", "D14"), ("onboard_button", "A")],
                          [("Mcu", "GND1"), ("onboard_led", "K"), ("onboard_button", "B")]])
        self.assertEqual([component["name"] for component in files["netlist.json"]["components"]], ["Mcu", "onboard_led", "onboard_button"])

    def test_a_record_that_lacks_a_ground_pin_or_is_missing_is_said_and_nothing_is_given(self):
        project = Path(tempfile.mkdtemp())
        (project / ".spark").mkdir()
        (project / "parts").mkdir()
        record = json.loads((ROOT / "parts" / "led-red-5mm.json").read_text())
        record["power"][0]["rail"] = "supply"
        (project / "parts" / "led-red-5mm.json").write_text(json.dumps(record))
        self.assertEqual(onboard_parts.make_converter_input([LED], "GND1", project),
                         (None, "the record for 'led-red-5mm' names no signal pin, ground pin or Wokwi part, so spark cannot wire onboard_led"))
        files, why = onboard_parts.make_converter_input([dict(LED, id="no-such-part")], "GND1", project)
        self.assertIsNone(files)
        self.assertTrue(why.startswith("no part called 'no-such-part'"), why)


class ABoardOnlyBuildWiresThemTest(unittest.TestCase):
    """The build runs the shipped converter bundle on Node for the FireBeetle; the XIAO needs no converter at all."""

    def build(self, board_id, workdir=None):
        workdir = workdir or Path(tempfile.mkdtemp())
        requirements = {"board": board_id, "parts": [], "board_only": True}
        (workdir / "requirements.json").write_text(json.dumps(requirements))
        return workdir, check_spine.run(requirements, workdir, toolchain=Path("/nonexistent/tsci"))

    def test_walk_3_s_requirements_give_the_led_and_the_button_wired_to_the_board(self):
        if not shutil.which("node"):
            self.skipTest("node is not installed")
        workdir, stages = self.build("firebeetle2-esp32s3")
        self.assertEqual((stages[-1].name, stages[-1].status), ("simulation", check_spine.OK), stages[-1].detail)
        self.assertTrue(stages[-1].detail.startswith("the board and its own onboard_led and onboard_button, 4 wire(s) in the diagram"))
        diagram = json.loads((workdir / "sim" / "diagram.json").read_text())
        self.assertEqual(diagram["author"], "generated from netlist.json")
        self.assertEqual([(part["id"], part["type"]) for part in diagram["parts"]],
                         [("mcu", "board-esp32-s3-devkitc-1"), ("onboard_led", "wokwi-led"), ("onboard_button", "wokwi-pushbutton")])
        self.assertEqual([connection[:2] for connection in diagram["connections"]],
                         [["mcu:21", "onboard_led:A"], ["mcu:47", "onboard_button:1.l"], ["mcu:GND.1", "onboard_led:C"],
                          ["mcu:GND.1", "onboard_button:2.l"], ["mcu:TX", "$serialMonitor:RX"], ["mcu:RX", "$serialMonitor:TX"]])

    def test_a_kept_diagram_is_merged_into_as_a_full_build_does(self):
        if not shutil.which("node"):
            self.skipTest("node is not installed")
        workdir = Path(tempfile.mkdtemp())
        kept = {"version": 1, "author": "me", "editor": "wokwi", "connections": [],
                "parts": [{"type": "wokwi-led", "id": "onboard_led", "top": 96, "left": 192, "attrs": {}}]}
        (workdir / "kept-diagram.json").write_text(json.dumps(kept))
        _, stages = self.build("firebeetle2-esp32s3", workdir)
        led = next(part for part in json.loads((workdir / "sim" / "diagram.json").read_text())["parts"] if part["id"] == "onboard_led")
        self.assertEqual((led["top"], led["left"]), (96, 192))
        self.assertIn("kept from your diagram: 1 part positions, 0 wire routes", stages[-1].detail)

    def test_no_node_is_the_converter_s_could_not_run_for_the_firebeetle_and_nothing_for_the_xiao(self):
        with mock.patch.dict(os.environ, {"PATH": str(Path(tempfile.mkdtemp()))}):
            _, stages = self.build("firebeetle2-esp32s3")
            workdir, alone = self.build("xiao-esp32-c6")
        self.assertEqual((stages[-1].name, stages[-1].status), ("simulation", check_spine.COULD_NOT_RUN))
        self.assertIn("node", stages[-1].detail)
        self.assertEqual((alone[-1].status, sorted(path.name for path in (workdir / "sim").iterdir())),
                         (check_spine.OK, ["WHAT-THIS-CANNOT-SHOW.md", "board.json", "diagram.json", "wokwi.toml"]))
        self.assertEqual(json.loads((workdir / "sim" / "diagram.json").read_text()),
                         {"version": 1, "author": "spark", "editor": "wokwi", "connections": [],
                          "parts": [{"type": "board-xiao-esp32-c6", "id": "mcu", "top": 0, "left": 0, "attrs": {}}]})


if __name__ == "__main__":
    unittest.main()
