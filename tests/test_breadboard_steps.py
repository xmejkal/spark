import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from breadboard_steps import BOARD, PART, RESISTOR, BreadboardSteps, End, StepPoint  # noqa: E402


def board(label):
    return End(BOARD, "board", "board " + label, "board " + label)


def pin(part, name, leg=""):
    return End(PART, part, "%s %s" % (part, name), "%s %s%s" % (part, name, " (%s)" % leg if leg else ""))


def resistor(tag, number):
    return End(RESISTOR, tag, "%s end %d" % (tag, number), "%s (330Ω in series with Led A), end %d" % (tag, number))


#: The button-and-LED circuit: A5 to the resistor, D3 to the button, ground to the LED and the button, LED to resistor.
BUTTON_LIGHT = BreadboardSteps(["Btn", "Led"], [
    StepPoint([board("A5"), resistor("R1", 1)], None, False),
    StepPoint([board("D3"), pin("Btn", "A")], None, False),
    StepPoint([board("GND"), pin("Led", "K"), pin("Btn", "B")], None, False),
    StepPoint([pin("Led", "A", 'the "long" leg'), resistor("R1", 2)], None, False),
])


class TheStepsTest(unittest.TestCase):
    def test_each_part_goes_in_first_then_one_connection_per_step(self):
        steps = BUTTON_LIGHT.list_steps()
        self.assertEqual(steps[:2], ["1. Put Btn in the breadboard, each pin in its own row.",
                                     "2. Put Led in the breadboard, each pin in its own row."])
        # Two places, a resistor end placed as its point's anchor, then each point's other ends: 1 + 1 + 2 + 1.
        self.assertEqual(len(steps), 2 + 1 + 1 + 1 + 2 + 1, steps)

    def test_a_board_pin_gets_a_jumper_to_the_row_of_a_part_pin(self):
        self.assertIn("4. Run a jumper from board A5 to the row of R1 end 1.", BUTTON_LIGHT.list_steps())
        self.assertIn("5. Run a jumper from board D3 to the row of Btn A.", BUTTON_LIGHT.list_steps())

    def test_a_part_pin_is_the_anchor_before_a_resistor_end(self):
        steps = BUTTON_LIGHT.list_steps()
        self.assertIn("8. Put R1 (330Ω in series with Led A), end 2, in the row of Led A.", steps)
        self.assertIn("7. Run a jumper from the row of Btn B to the row of Led K.", steps)

    def test_a_point_of_a_board_pin_and_a_resistor_places_the_resistor_in_a_free_row(self):
        self.assertIn("3. Put R1 (330Ω in series with Led A), end 1, in a free row.", BUTTON_LIGHT.list_steps())

    def test_on_a_rail_every_part_pin_runs_a_jumper_and_a_resistor_end_goes_in(self):
        steps = BreadboardSteps(["Btn"], [
            StepPoint([board("GND"), pin("Btn", "B"), resistor("R1", 2)], None, True)]).list_steps()
        self.assertEqual(steps[1:], ["2. Run a jumper from board GND to a free rail. Mark it GND.",
                                     "3. Run a jumper from the row of Btn B to the GND rail.",
                                     "4. Put R1 (330Ω in series with Led A), end 2, in the GND rail."])

    def test_a_supply_from_off_the_board_has_its_own_step(self):
        steps = BreadboardSteps(["Inlet", "Driver"], [
            StepPoint([pin("Inlet", "VCC"), pin("Driver", "VCC")], "MOTOR6V", False)]).list_steps()
        self.assertEqual(steps[2:], [
            "3. Run a jumper from the row of Driver VCC to the row of Inlet VCC.",
            "4. Connect the MOTOR6V supply, from off the board, to the row of Inlet VCC. Check its voltage first "
            "(Before you power it)."])


class TheDiagramTest(unittest.TestCase):
    def setUp(self):
        self.diagram = BUTTON_LIGHT.draw_mermaid()

    def test_every_joining_step_is_one_edge_with_its_number(self):
        edges = re.findall(r'---\|"(\d+)"\|', self.diagram)
        self.assertEqual(edges, ["4", "5", "6", "7", "8"])

    def test_every_end_is_a_quoted_node_in_its_component_s_box(self):
        self.assertIn('subgraph g1["board"]\n    n1["board A5"]', self.diagram)
        nodes = re.findall(r'^\s*(\S+)\["', self.diagram, re.M)
        self.assertTrue(all(re.fullmatch(r"[ng]\d+", node) for node in nodes), nodes)
        self.assertEqual(len([node for node in nodes if node.startswith("n")]), 9)

    def test_a_double_quote_in_a_label_never_ends_it(self):
        diagram = BreadboardSteps([], [StepPoint([board("D3"), pin('Led "x"', "A")], None, False)]).draw_mermaid()
        self.assertIn('n2["Led #quot;x#quot; A"]', diagram)

    def test_a_rail_and_a_supply_are_nodes(self):
        diagram = BreadboardSteps(["Inlet"], [
            StepPoint([pin("Inlet", "GND"), pin("Inlet", "VCC")], "VBUS", True)]).draw_mermaid()
        self.assertIn('["VBUS rail"]', diagram)
        self.assertIn('["VBUS supply"]', diagram)
        self.assertTrue(diagram.startswith("```mermaid\nflowchart LR\n") and diagram.endswith("\n```"))


if __name__ == "__main__":
    unittest.main()
