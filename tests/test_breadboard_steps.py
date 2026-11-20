import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from spark.breadboard.wiring_steps import (BOARD, PART, RESISTOR, BreadboardSteps, End, MermaidDiagram, NumberedList,  # noqa: E402
                              StepPoint, role_of, wiring)
from spark.breadboard import drawing, sheet  # noqa: E402
from spark.design import board_components  # noqa: E402

EPAPER = Path(__file__).resolve().parent / "data" / "breadboard" / "epaper"


def epaper_ends():
    """{end name: End} of the e-paper fixture's points, as the build reads them."""
    with mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()}):
        read = sheet._read_build(EPAPER / "requirements.json")
    return read, {end.name: end for point in read.steps.points for end in point.ends}


def board(label):
    return End(BOARD, "board", "board " + label, "board " + label, label)


def pin(part, name, leg=""):
    return End(PART, part, "%s %s" % (part, name), "%s %s%s" % (part, name, " (%s)" % leg if leg else ""), name)


def resistor(tag, number):
    return End(RESISTOR, tag, "%s end %d" % (tag, number), "%s (330Ω in series with Led A), end %d" % (tag, number),
               str(number))


def numbered(placed, points):
    return NumberedList().render(BreadboardSteps(placed, points))


def diagram(placed, points):
    return "\n".join(MermaidDiagram().render(BreadboardSteps(placed, points)))


#: The button-and-LED circuit: A5 to the resistor, D3 to the button, ground to the LED and the button, LED to resistor.
BUTTON_LIGHT = (["board", "Btn", "Led"], [
    StepPoint([board("A5"), resistor("R1", 1)], None, False),
    StepPoint([board("D3"), pin("Btn", "A")], None, False),
    StepPoint([board("GND"), pin("Led", "K"), pin("Btn", "B")], None, False),
    StepPoint([pin("Led", "A", 'the "long" leg'), resistor("R1", 2)], None, False),
])


class TheStepsTest(unittest.TestCase):
    def setUp(self):
        self.steps = numbered(*BUTTON_LIGHT)

    def test_the_board_and_each_part_go_in_first(self):
        self.assertEqual(self.steps[:3], ["1. Put the board in the breadboard, each pin in its own row.",
                                          "2. Put Btn in the breadboard, each pin in its own row.",
                                          "3. Put Led in the breadboard, each pin in its own row."])

    def test_then_one_connection_per_step_in_order(self):
        self.assertEqual(self.steps[3:], [
            "4. Put R1 (330Ω in series with Led A), end 1, in a free row.",
            "5. Run a jumper from board A5 to the row of R1 end 1.",
            "6. Run a jumper from board D3 to the row of Btn A.",
            "7. Run a jumper from board GND to the row of Led K.",
            "8. Run a jumper from the row of Btn B to the row of Led K.",
            "9. Put R1 (330Ω in series with Led A), end 2, in the row of Led A."])

    def test_on_a_rail_every_part_pin_runs_a_jumper_and_a_resistor_end_goes_in(self):
        steps = numbered([], [StepPoint([board("GND"), pin("Btn", "B"), resistor("R1", 2)], None, True)])
        self.assertEqual(steps, ["1. Run a jumper from board GND to a free rail. Mark it GND.",
                                 "2. Run a jumper from the row of Btn B to the GND rail.",
                                 "3. Put R1 (330Ω in series with Led A), end 2, in the GND rail."])

    def test_a_rail_with_no_board_pad_and_no_supply_is_marked_by_its_first_end(self):
        steps = numbered([], [StepPoint([pin("Btn", "B"), pin("Led", "K")], None, True)])
        self.assertEqual(steps[0], "1. Run a jumper from the row of Btn B to a free rail. Mark it Btn B.")

    def test_a_supply_from_off_the_board_has_its_own_step(self):
        steps = numbered([], [StepPoint([pin("Inlet", "VCC"), pin("Driver", "VCC")], "MOTOR6V", False)])
        self.assertEqual(steps, [
            "1. Run a jumper from the row of Driver VCC to the row of Inlet VCC.",
            "2. Connect the MOTOR6V supply, from off the board, to the row of Inlet VCC. Check its voltage first "
            "(Before you power it)."])

    def test_a_supply_on_a_rail_marks_the_rail(self):
        steps = numbered([], [StepPoint([pin("Inlet", "VCC"), pin("Driver", "VCC")], "VBUS", True)])
        self.assertEqual(steps[0], "1. Run a jumper from the row of Inlet VCC to a free rail. Mark it VBUS.")
        self.assertIn("to the VBUS rail. Check its voltage first", steps[-1])

    def test_two_board_pads_meet_in_a_free_row_never_pad_to_pad(self):
        steps = numbered([], [StepPoint([board("D3"), board("D4")], None, False)])
        self.assertEqual(steps, ["1. Run a jumper from board D3 to a free row.",
                                 "2. Run a jumper from board D4 to the row of the jumper from board D3."])


class TheDiagramTest(unittest.TestCase):
    def setUp(self):
        self.diagram = diagram(*BUTTON_LIGHT)

    def test_every_joining_step_is_one_edge_with_its_number(self):
        self.assertEqual(re.findall(r'---\|"(\d+)"\|', self.diagram), ["5", "6", "7", "8", "9"])
        self.assertIn('n2 ---|"6"| n6', self.diagram, "board D3 to Btn A")

    def test_every_end_is_a_quoted_node_in_its_component_s_box(self):
        self.assertIn('subgraph g1["board"]\n    n1["board A5"]', self.diagram)
        nodes = re.findall(r'^\s*(\S+)\["', self.diagram, re.M)
        self.assertTrue(all(re.fullmatch(r"[ng]\d+", node) for node in nodes), nodes)
        self.assertEqual(len([node for node in nodes if node.startswith("n")]), 9)

    def test_a_double_quote_in_a_label_never_ends_it(self):
        self.assertIn('n2["Led #quot;x#quot; A"]', diagram([], [StepPoint([board("D3"), pin('Led "x"', "A")], None,
                                                                          False)]))

    def test_a_rail_and_a_supply_are_nodes(self):
        drawn = diagram([], [StepPoint([pin("Inlet", "GND"), pin("Inlet", "VCC")], "VBUS", True)])
        self.assertIn('["VBUS rail"]', drawn)
        self.assertIn('["VBUS supply"]', drawn)
        self.assertTrue(drawn.startswith("```mermaid\nflowchart LR\n") and drawn.endswith("\n```"))


class TheShortNamesTest(unittest.TestCase):
    """P945: a step and a line before power call a part by a short name: the instance name the requirements give, else
    the record's short_name when no other part is called the same, else the component name."""

    def test_a_record_s_short_name_names_the_part(self):
        self.assertEqual(board_components.short_names([{"id": "epaper-2in9", "short_name": "e-paper"}]),
                         {"Epaper2in9": "e-paper"})

    def test_the_instance_name_wins_over_the_short_name(self):
        part = {"id": "epaper-2in9", "short_name": "e-paper", "_instance": "Screen"}
        self.assertEqual(board_components.short_names([part]), {"Screen": "Screen"})

    def test_two_parts_called_the_same_keep_their_component_names(self):
        parts = [{"id": "epaper-2in9", "short_name": "screen"}, {"id": "oled-1in3", "short_name": "screen"},
                 {"id": "led-red", "short_name": "led"}]
        self.assertEqual(board_components.short_names(parts),
                         {"Epaper2in9": "Epaper2in9", "Oled1in3": "Oled1in3", "LedRed": "led"})

    def test_a_short_name_an_instance_already_has_goes_to_the_instance(self):
        parts = [{"id": "epaper-2in9", "short_name": "Screen"}, {"id": "oled-1in3", "_instance": "Screen"}]
        self.assertEqual(board_components.short_names(parts), {"Epaper2in9": "Epaper2in9", "Screen": "Screen"})

    def test_no_short_name_keeps_the_component_name(self):
        self.assertEqual(board_components.short_names([{"id": "led-red-5mm", "name": "Red LED, 5 mm"}]),
                         {"LedRed5mm": "LedRed5mm"})

    def test_the_place_step_and_the_diagram_box_say_the_short_name(self):
        steps = BreadboardSteps(["board", "Epaper2in9"], [StepPoint([board("D3"), pin("e-paper", "CS")], None, False)],
                                {"Epaper2in9": "e-paper"})
        self.assertEqual(NumberedList().render(steps)[1], "2. Put e-paper in the breadboard, each pin in its own row.")
        self.assertIn('  subgraph g2["e-paper"]', MermaidDiagram().render(BreadboardSteps(
            ["board"], [StepPoint([board("D3"), End(PART, "Epaper2in9", "e-paper CS", "e-paper CS", "CS")], None, False)],
            {"Epaper2in9": "e-paper"})))


class ThePrintedLabelTest(unittest.TestCase):
    """P947: a step names a module's pin by the label its record says is printed beside it, so the step and the part
    read the same."""

    def test_a_pin_with_a_printed_label_is_named_by_it(self):
        _, ends = epaper_ends()
        self.assertTrue({"e-paper D/C", "e-paper Reset", "e-paper Busy"} <= set(ends), sorted(ends))
        self.assertFalse({"e-paper DC", "e-paper RESET", "e-paper BUSY"} & set(ends), sorted(ends))
        self.assertEqual(ends["e-paper Busy"].words,
                         "e-paper Busy (back up, header at the top: the right end pin, above the label Busy)")

    def test_a_pin_with_no_printed_label_keeps_its_name(self):
        _, ends = epaper_ends()
        self.assertEqual((ends["e-paper CS"].words, ends["e-paper SDI"].words, ends["e-paper GND"].words),
                         ("e-paper CS", "e-paper SDI", "e-paper GND"))

    def test_the_pin_stays_the_catalog_key(self):
        read, ends = epaper_ends()
        self.assertEqual(ends["e-paper D/C"].pin, "DC")
        _, catalog = sheet._drawing_inputs(read)
        self.assertEqual(drawing.end_pin(ends["e-paper D/C"], catalog), "D/C")

    def test_the_step_says_the_printed_label(self):
        read, _ = epaper_ends()
        self.assertIn("4. Run a jumper from board A5 to the row of e-paper D/C.", NumberedList().render(read.steps))


class ThePointRoleTest(unittest.TestCase):
    """P947: what a point carries is read from the records' rail facts, never from a pin's name: a board pad's rail in
    the board's power_pads, a part pin's rail in its record's power list."""

    def test_each_end_holds_its_record_s_rail(self):
        _, ends = epaper_ends()
        self.assertEqual({name: ends[name].power_rail for name in ("board 3V3", "board GND", "board A5", "e-paper VCC",
                                                                    "e-paper GND", "e-paper D/C")},
                         {"board 3V3": "logic", "board GND": "ground", "board A5": "", "e-paper VCC": "logic",
                          "e-paper GND": "ground", "e-paper D/C": ""})

    def test_power_ground_and_signal_points(self):
        _, ends = epaper_ends()
        self.assertEqual(role_of([ends["board 3V3"], ends["e-paper VCC"]]), "power")
        self.assertEqual(role_of([ends["board GND"], ends["e-paper GND"]]), "ground")
        self.assertEqual(role_of([ends["board A5"], ends["e-paper D/C"]]), "signal")

    def test_one_end_on_a_rail_decides_whatever_the_other_says(self):
        _, ends = epaper_ends()
        self.assertEqual(role_of([ends["board GND"], pin("Btn", "A")]), "ground")
        self.assertEqual(role_of([pin("Btn", "A"), ends["e-paper VCC"]]), "power")
        self.assertEqual(role_of([ends["board GND"], pin("Btn", "A")._replace(power_rail=None)]), "ground")

    def test_an_end_whose_record_says_nothing_makes_the_role_not_known(self):
        _, ends = epaper_ends()
        self.assertEqual(role_of([ends["board A5"], pin("Btn", "A")._replace(power_rail=None)]), "unknown")

    def test_a_pin_named_gnd_or_vcc_with_no_rail_fact_is_a_signal(self):
        read, _ = epaper_ends()
        record = dict(read.built.parts[0], power=[{"pin": "SCLK", "rail": "logic", "direction": "in"}])
        _, steps = wiring(read.built.board, read.circuit, [record], read.resistors, sheet.BOARD_COMPONENT)
        ends = {end.name: end for point in steps.points for end in point.ends}
        self.assertEqual((ends["e-paper GND"].power_rail, ends["e-paper VCC"].power_rail), ("", ""))
        self.assertEqual(ends["e-paper SCLK"].power_rail, "logic")

    def test_a_record_with_no_power_list_says_nothing(self):
        read, _ = epaper_ends()
        record = {key: value for key, value in read.built.parts[0].items() if key != "power"}
        _, steps = wiring(read.built.board, read.circuit, [record], read.resistors, sheet.BOARD_COMPONENT)
        ends = {end.name: end for point in steps.points for end in point.ends}
        self.assertEqual((ends["e-paper GND"].power_rail, ends["e-paper D/C"].power_rail), (None, None))

    def test_a_board_port_that_matches_no_power_pad_is_a_signal_and_a_board_with_none_says_nothing(self):
        read, _ = epaper_ends()
        _, steps = wiring(read.built.board, read.circuit, read.built.parts, read.resistors, sheet.BOARD_COMPONENT)
        ends = {end.name: end for point in steps.points for end in point.ends}
        self.assertEqual((ends["board MO"].power_rail, ends["board SCK"].power_rail), ("", ""))
        board = {key: value for key, value in read.built.board.items() if key != "power_pads"}
        _, steps = wiring(board, read.circuit, read.built.parts, read.resistors, sheet.BOARD_COMPONENT)
        ends = {end.name: end for point in steps.points for end in point.ends}
        self.assertEqual((ends["board 3V3"].power_rail, ends["board MO"].power_rail), (None, None))

    def test_the_role_reaches_each_step_and_each_drawn_jumper(self):
        read, _ = epaper_ends()
        seated = read.steps.anchored()
        self.assertEqual([one.role for one in seated], [None, None] + ["power", "signal", "signal", "signal", "signal",
                                                                       "ground", "signal", "signal"])
        with mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()}):
            layout = sheet._plan_layout(read)
        self.assertEqual({jumper.step: jumper.role for jumper in layout.jumpers if jumper.role != "signal"},
                         {3: "power", 8: "ground"})


if __name__ == "__main__":
    unittest.main()
