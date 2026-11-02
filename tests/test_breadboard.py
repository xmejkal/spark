"""
The breadboard sheet (P191, #143): from the board that was built, what to put on a breadboard and how to wire it, in
the board's printed labels and the parts' legs.

The fixture is the journey's button-and-LED project as built on 2026-10-11: its requirements, and the parts, ports,
traces and nets of its built circuit (tests/data/breadboard/button-light/README.md).

    python3 -m unittest tests.test_breadboard
"""

import contextlib
import io
import json
import os
import re
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

import breadboard  # noqa: E402

FIXTURE = ROOT / "tests" / "data" / "breadboard" / "button-light"


def a_copy():
    """The fixture project in a folder of its own, so a run may write its sheet there."""
    project = Path(tempfile.mkdtemp()) / "button-light"
    shutil.copytree(FIXTURE, project)
    return project


def in_store(home):
    return mock.patch.dict(os.environ, {"SPARK_HOME": str(home)})


def point_lines(text):
    """The numbered lines of the sheet's Points section: one per connection point (the steps are numbered too)."""
    section = text.split("### Points", 1)[1].split("\n## ", 1)[0]
    return [line for line in section.splitlines() if re.match(r"^\d+\. ", line)]


class TheSheetTest(unittest.TestCase):
    def setUp(self):
        self.project = a_copy()
        self.home = Path(tempfile.mkdtemp())
        with in_store(self.home):
            self.text = breadboard.sheet(self.project / "requirements.json")

    def connections(self):
        return point_lines(self.text)

    def test_each_point_of_the_built_circuit_is_one_line(self):
        # Four points: D3 with the button (the board's internal pull-up holds it, P204), ground with the button and the
        # LED's cathode, A5 with the LED resistor, and the LED resistor's other end with the anode.
        self.assertEqual(len(self.connections()), 4, self.text)

    def test_a_point_names_the_board_s_printed_label_and_every_part_on_it(self):
        d3 = next(line for line in self.connections() if "board D3" in line)
        self.assertIn("TactileButton A", d3)
        self.assertNotIn("pull-up", d3, "P204: the board's internal pull-up, no resistor")
        a5 = next(line for line in self.connections() if "board A5" in line)
        self.assertIn("R1 (330Ω in series with LedRed5mm A), end 1", a5)

    def test_the_board_s_ground_pads_are_one_point(self):
        grounds = [line for line in self.connections() if "board GND" in line]
        self.assertEqual(len(grounds), 1, self.text)
        self.assertNotRegex("\n".join(self.connections()), r"GND\d")
        self.assertIn("LedRed5mm K", grounds[0])
        self.assertEqual(len(re.findall(r"GND\d", self.text)), 3, "the pad GND uses, and the two doubtful ones, once each")

    def test_the_sheet_reads_as_recorded(self):
        # P412: the whole sheet of a board drawn from its record, word for word; regenerate it only on purpose
        self.assertEqual(self.text, (FIXTURE / "breadboard.expected.md").read_text())

    def test_a_leg_the_record_describes_is_named(self):
        self.assertIn("LedRed5mm A (the anode, the longer leg)", self.text)
        self.assertIn("LedRed5mm K (the cathode, the shorter leg", self.text)
        self.assertIn("a meter on continuity", self.text, "how to find a button's joined pair")

    def test_the_parts_list_names_the_board_each_part_and_each_resistor_with_its_purpose(self):
        self.assertIn("DFRobot FireBeetle 2 ESP32-S3", self.text)
        self.assertNotIn("10kΩ", self.text, "P204: the button uses the board's internal pull-up")
        self.assertIn("TactileButton A has no resistor: the firmware must pull it up", self.text)
        self.assertIn("| 1 | 330Ω resistor, through-hole | R1 in series with LedRed5mm A |", self.text)
        self.assertIn("so a board pin always gets a", self.text, "the board covers the rows beside its pins")
        self.assertIn("a breadboard and jumper wires", self.text)
        self.assertIn("| qty | part | for | have |", self.text)


MOTOR = ROOT / "tests" / "data" / "breadboard" / "motor"
XIAO = ROOT / "tests" / "data" / "breadboard" / "button-light-xiao"


class TheMotorExampleTest(unittest.TestCase):
    """The journey's motor example: four resistors, two of them on 3V3 and two on ground, and a crowded ground."""

    def setUp(self):
        self.project = Path(tempfile.mkdtemp()) / "motor"
        shutil.copytree(MOTOR, self.project)
        with in_store(Path(tempfile.mkdtemp())):
            self.text = breadboard.sheet(self.project / "requirements.json")
        self.wiring = point_lines(self.text)

    def test_every_resistor_end_is_on_the_sheet_once(self):
        # Five reviewers found it: two pull-ups on 3V3 printed as one end, so one was never wired.
        for tag in ("R1", "R2"):
            for end in ("end 1", "end 2"):
                with self.subTest(resistor=tag, end=end):
                    found = sum(len(re.findall(r"\b%s \([^)]*\), %s\b" % (tag, end), line)) for line in self.wiring)
                    self.assertEqual(found, 1, self.text)

    def test_the_points_read_as_before_the_steps_came(self):
        # Held here, not regenerated: the six points of the motor sheet as P191 wrote them, before P202.
        self.assertEqual([line.split(" (")[0].split(" ·")[0] for line in self.wiring],
                         ["1. board A5", "2. board D3", "3. board D11", "4. board D12", "5. board GND",
                          "6. JstPh2PowerInlet VCC"])
        self.assertEqual(self.wiring[0], "1. board A5 · L9110sModule AIB · R2 (10kΩ pull-down on L9110sModule AIB), end 1")
        self.assertTrue(self.wiring[5].endswith("· the MOTOR6V supply, from off the board, not part of the parts list"))

    def test_the_sheet_reads_as_recorded(self):
        # The refuter: five probe mutations escaped every assertion of a line's parts. The whole sheet, word for word,
        # read and checked against the built circuit on 2026-10-11; regenerate it only on purpose.
        self.assertEqual(self.text, (MOTOR / "breadboard.expected.md").read_text())

    def test_a_supply_from_off_the_board_is_named_where_it_is_wired_listed_and_checked_before_power(self):
        # The refuter's blocker: the inlet's line never said what feeds it, and a 12 V pack is in the module's range.
        supply = next(line for line in self.wiring if "JstPh2PowerInlet VCC" in line)
        self.assertIn("the MOTOR6V supply, from off the board", supply)
        self.assertIn("what feeds MOTOR6V", self.text)
        self.assertIn("MOTOR6V comes from off the board, and this sheet does not say its voltage", self.text)

    def test_identical_parts_are_totalled(self):
        self.assertIn("| 2 | 6x6 mm tactile push button | BtnMode, BtnOpen |", self.text)
        self.assertIn("| 2 | 10kΩ resistor, through-hole |", self.text)

    def test_a_point_with_more_ends_than_a_breadboard_row_says_to_use_a_rail(self):
        ground = next(line for line in self.wiring if "board GND" in line)
        self.assertIn("rail", ground)

    def test_before_power_it_names_the_conflict_the_warnings_and_the_pins_that_must_not_float(self):
        self.assertIn("## Before you power it", self.text)
        self.assertIn("CONFLICT", self.text)
        self.assertIn("parts.py --show l9110s-module", self.text)
        self.assertIn("L9110sModule BIA", self.text)
        self.assertIn("must not float", self.text)


class TheXiaoExampleTest(unittest.TestCase):
    """Button-light on the XIAO C6 (P267): the fixture the drawn breadboard reads, with the project's own board."""

    def test_its_steps_read_as_built(self):
        with in_store(Path(tempfile.mkdtemp())):
            text = breadboard.sheet(XIAO / "requirements.json")
        steps = [line for line in text.split("### Steps", 1)[1].split("### Diagram", 1)[0].splitlines()
                 if re.match(r"^\d+\. ", line)]
        self.assertEqual(len(steps), 9, text)
        self.assertEqual(steps[4], "5. Run a jumper from board D8 to the row of R1 end 1.")
        self.assertEqual(steps[5], "6. Run a jumper from board D10 to the row of TactileButton A.")


class AStaleOrFailedBuildIsRefusedTest(unittest.TestCase):
    def test_a_circuit_built_from_other_requirements_is_refused(self):
        project = a_copy()
        (project / "requirements.json").write_text(json.dumps(
            {"board": "firebeetle2-esp32s3", "parts": ["tactile-button", "led-red-5mm", "jst-ph-2-power-inlet"]}))
        with in_store(Path(tempfile.mkdtemp())), self.assertRaises(breadboard.NotBuilt) as said:
            breadboard.sheet(project / "requirements.json")
        self.assertIn("build again", str(said.exception))

    def test_a_board_swapped_without_a_rebuild_is_refused(self):
        # The refuter's probe: XIAO in the requirements, the FireBeetle's build still in dist/, and a sheet came out.
        project = a_copy()
        wanted = json.loads((project / "requirements.json").read_text())
        (project / "requirements.json").write_text(json.dumps(dict(wanted, board="xiao-esp32-c6")))
        with in_store(Path(tempfile.mkdtemp())), self.assertRaises(breadboard.NotBuilt) as said:
            breadboard.sheet(project / "requirements.json")
        self.assertIn("built from other requirements", str(said.exception))

    def test_a_build_that_recorded_nothing_is_refused(self):
        project = a_copy()
        (project / "dist" / "board" / "built-from.json").unlink()
        with in_store(Path(tempfile.mkdtemp())), self.assertRaises(breadboard.NotBuilt) as said:
            breadboard.sheet(project / "requirements.json")
        self.assertIn("records no finished build", str(said.exception))

    def test_a_failed_build_is_refused(self):
        project = a_copy()
        circuit = project / "dist" / "board" / "circuit.json"
        circuit.write_text(json.dumps(json.loads(circuit.read_text()) + [{"type": "source_trace_not_connected_error"}]))
        with in_store(Path(tempfile.mkdtemp())), self.assertRaises(breadboard.NotBuilt) as said:
            breadboard.sheet(project / "requirements.json")
        self.assertIn("the last build failed", str(said.exception))

    def test_a_circuit_that_is_not_a_list_of_elements_is_refused(self):
        project = a_copy()
        (project / "dist" / "board" / "circuit.json").write_text("{}")
        with in_store(Path(tempfile.mkdtemp())), self.assertRaises(breadboard.NotBuilt):
            breadboard.sheet(project / "requirements.json")


class APadIsNamedAsItIsPrintedTest(unittest.TestCase):
    def test_never_a_pin_number(self):
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        for hints, label in ((["pin11", "MI", "11"], "MI"), (["pin18", "RST", "18"], "RST"), (["pin14", "GND1", "14"], "GND"),
                             (["pin4", "D3", "4"], "D3")):
            with self.subTest(hints=hints):
                self.assertEqual(breadboard.printed_label(board, {"name": hints[0], "port_hints": hints}), label)

    def test_a_signal_the_requirements_add_is_said_with_its_pin_though_nothing_is_wired(self):
        # The refuter: irrigation's STATUS_LED got pin MO and the sheet never said it.
        folder = Path(tempfile.mkdtemp())
        (folder / "requirements.json").write_text(json.dumps(
            {"board": "firebeetle2-esp32s3", "parts": ["tactile-button"], "signals": [{"name": "STATUS_LED", "needs": []}]}))
        with in_store(Path(tempfile.mkdtemp())):
            built = breadboard.design.load(folder / "requirements.json")
            said = breadboard._unwired(built.board, built)
        self.assertEqual(said, ["- STATUS_LED: board A5, nothing wired to it yet (the requirements add this signal)"])

    # --- MVP --- (P512, #708) the alias is read, not answered by the fallback
    def test_a_pin_label_is_named_by_its_printed_pad(self):
        xiao = json.loads((ROOT / "boards" / "xiao-esp32-c6.json").read_text())
        # TX and RX are aliases only: no pins key and no header label (review, refuter 1)
        for hints, label in ((["SDA"], "D4"), (["pin22", "SDA", "22"], "D4"), (["D4"], "D4"), (["TX"], "D6"),
                             (["pin16", "TX"], "D6"), (["RX"], "D7")):
            with self.subTest(hints=hints):
                self.assertEqual(breadboard.printed_label(xiao, {"name": hints[0], "port_hints": hints}), label)
        bare = {"pins": {"MOSI": 15}, "physical": {"pad_aliases": {"MOSI": "MO"}}}  # no header rows: the alias says MO
        self.assertEqual(breadboard.printed_label(bare, {"name": "IO15", "port_hints": ["IO15", "MO"]}), "MO")

    def test_a_signal_the_requirements_put_on_an_aliased_pin_is_said_with_its_pad(self):
        folder = Path(tempfile.mkdtemp())
        (folder / "requirements.json").write_text(json.dumps(
            {"board": "firebeetle2-esp32s3", "parts": ["tactile-button"],
             "signals": [{"name": "STATUS_LED", "pin": "MOSI", "needs": []}]}))
        with in_store(Path(tempfile.mkdtemp())):
            built = breadboard.design.load(folder / "requirements.json")
            said = breadboard._unwired(built.board, built)
        self.assertEqual(said, ["- STATUS_LED: board MO, nothing wired to it yet (the requirements add this signal)"])

    def test_a_board_pin_s_jumper_takes_a_hole_so_four_other_ends_need_a_rail(self):
        # Five holes a row; the jumper from the board pin takes one, so four others and the jumper fill it, five overfill.
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        circuit = [{"type": "source_component", "source_component_id": "mcu", "name": "Mcu"},
                   {"type": "source_port", "source_port_id": "d3", "source_component_id": "mcu", "name": "pin4",
                    "port_hints": ["pin4", "D3", "4"]}]
        for n in range(1, 6):
            circuit += [{"type": "source_component", "source_component_id": "c%d" % n, "name": "Part%d" % n},
                        {"type": "source_port", "source_port_id": "p%d" % n, "source_component_id": "c%d" % n, "name": "A"}]
        joined = {"type": "source_trace", "connected_source_port_ids": ["d3", "p1", "p2", "p3", "p4"]}
        self.assertNotIn("rail", breadboard._wiring(board, circuit + [joined], [], {})[0][0])
        joined["connected_source_port_ids"].append("p5")
        self.assertIn("join board D3 to a rail", breadboard._wiring(board, circuit + [joined], [], {})[0][0])

    def test_a_supply_s_wire_takes_a_hole_so_five_ends_and_a_supply_need_a_rail(self):
        circuit = [{"type": "source_net", "source_net_id": "n1", "name": "VBUS"}]
        for n in range(1, 6):
            circuit += [{"type": "source_component", "source_component_id": "c%d" % n, "name": "Part%d" % n},
                        {"type": "source_port", "source_port_id": "p%d" % n, "source_component_id": "c%d" % n, "name": "A"}]
        joined = {"type": "source_trace", "connected_source_port_ids": ["p1", "p2", "p3", "p4"],
                  "connected_source_net_ids": ["n1"]}
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        self.assertNotIn("rail", breadboard._wiring(board, circuit + [joined], [], {})[0][0])
        joined["connected_source_port_ids"].append("p5")
        self.assertIn("put these ends on one rail", breadboard._wiring(board, circuit + [joined], [], {})[0][0])

    def test_a_port_alone_on_a_supply_is_a_point_that_names_the_supply(self):
        circuit = [{"type": "source_component", "source_component_id": "c1", "name": "L9110sModule"},
                   {"type": "source_port", "source_port_id": "p1", "source_component_id": "c1", "name": "VCC"},
                   {"type": "source_net", "source_net_id": "n1", "name": "MOTOR6V"},
                   {"type": "source_trace", "connected_source_port_ids": ["p1"], "connected_source_net_ids": ["n1"]}]
        found = breadboard.points(circuit)
        self.assertEqual([(len(point.members), point.nets) for point in found], [(1, ["MOTOR6V"])])


class ASignalNothingTakesTest(unittest.TestCase):
    def test_the_sheet_says_each_signal_the_requirements_add_with_its_pin(self):
        project = a_copy()
        wanted = dict(json.loads((project / "requirements.json").read_text()), signals=[{"name": "BUZZER", "needs": []}])
        (project / "requirements.json").write_text(json.dumps(wanted))
        (project / "dist" / "board" / "built-from.json").write_text(json.dumps({"requirements": wanted}))
        with in_store(Path(tempfile.mkdtemp())):
            text = breadboard.sheet(project / "requirements.json")
        self.assertIn("Not wired:", text)
        self.assertRegex(text, r"- BUZZER: board \S+, nothing wired to it yet")


class WhatYouOwnTest(unittest.TestCase):
    def test_a_part_your_drawer_holds_for_this_project_is_yours_and_the_rest_to_get(self):
        project, home = a_copy(), Path(tempfile.mkdtemp())
        (home / "drawer").mkdir()
        (home / "drawer" / "firebeetle-2-esp32-s3.json").write_text(json.dumps(
            {"schema": 1, "label": "FireBeetle 2 ESP32-S3", "count": 1, "is": {"board": "firebeetle2-esp32s3"},
             "used_in": {"button-light": 1}}))
        (home / "projects.json").write_text(json.dumps({"button-light": str(project)}))
        with in_store(home):
            text = breadboard.sheet(project / "requirements.json")
        board = next(line for line in text.splitlines() if "DFRobot FireBeetle 2 ESP32-S3" in line and "|" in line)
        self.assertIn("yours", board)
        led = next(line for line in text.splitlines() if "L-7113ID" in line and "|" in line)
        self.assertIn("to get", led)

    def test_owned_but_not_held_here_reads_in_your_drawer_and_a_skipped_entry_is_not_yours(self):
        project, home = a_copy(), Path(tempfile.mkdtemp())
        (home / "drawer").mkdir()
        (home / "drawer" / "buttons.json").write_text(json.dumps(
            {"schema": 1, "label": "buttons", "count": 20, "is": {"part": "tactile-button"}}))
        (home / "drawer" / "old-led.json").write_text(json.dumps(
            {"schema": 1, "label": "an LED", "count": 1, "is": {"part": "led-red-5mm"}, "skip": "its leg broke off",
             "used_in": {"button-light": 1}}))
        (home / "projects.json").write_text(json.dumps({"button-light": str(project)}))
        with in_store(home):
            text = breadboard.sheet(project / "requirements.json")
        rows = {line.split("|")[2].strip(): line.split("|")[4].strip() for line in text.splitlines() if line.startswith("| ")}
        self.assertEqual(rows["6x6 mm tactile push button"], "in your drawer")
        self.assertEqual(rows["Kingbright L-7113ID 5 mm red LED"], "to get")
        self.assertEqual(rows["330Ω resistor, through-hole"], "to get", "the legend's blank means only: not on your list")


class TheCommandLineTest(unittest.TestCase):
    def run_main(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with in_store(Path(tempfile.mkdtemp())), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = breadboard.main(list(argv))
        return code, out.getvalue() + err.getvalue()

    def test_it_writes_the_sheet_into_the_project(self):
        project = a_copy()
        code, said = self.run_main(str(project / "requirements.json"))
        self.assertEqual(code, 0, said)
        self.assertIn("board D3", (project / "breadboard.md").read_text())
        self.assertIn("wrote", said)

    def test_an_out_that_cannot_be_written_could_not_run(self):
        project = a_copy()
        code, said = self.run_main(str(project / "requirements.json"), "--out", str(project / "no" / "such" / "x.md"))
        self.assertEqual(code, 2, said)
        self.assertNotIn("Traceback", said)

    def test_without_a_built_circuit_it_says_to_build_first(self):
        project = a_copy()
        shutil.rmtree(project / "dist")
        code, said = self.run_main(str(project / "requirements.json"))
        self.assertEqual(code, 2)
        self.assertIn("check_spine.py requirements.json --keep .", said)
        self.assertFalse((project / "breadboard.md").exists())


if __name__ == "__main__":
    unittest.main()
