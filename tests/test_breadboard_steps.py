import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from breadboard_steps import (BOARD, PART, RESISTOR, BreadboardSteps, End, MermaidDiagram, NumberedList,  # noqa: E402
                              StepPoint)


def board(label):
    return End(BOARD, "board", "board " + label, "board " + label)


def pin(part, name, leg=""):
    return End(PART, part, "%s %s" % (part, name), "%s %s%s" % (part, name, " (%s)" % leg if leg else ""))


def resistor(tag, number):
    return End(RESISTOR, tag, "%s end %d" % (tag, number), "%s (330Ω in series with Led A), end %d" % (tag, number))


def numbered(placed, points):
    return NumberedList().render(BreadboardSteps(placed, points))


def diagram(placed, points):
    return "\n".join(MermaidDiagram().render(BreadboardSteps(placed, points)))


#: The button-and-LED circuit: A5 to the resistor, D3 to the button, ground to the LED and the button, LED to resistor.
BUTTON_LIGHT = (["the board", "Btn", "Led"], [
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


if __name__ == "__main__":
    unittest.main()
