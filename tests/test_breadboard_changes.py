"""
A rebuild lists what to change on the bench (P300, #366): the steps of the last sheet against the steps of this one.

    python3 -m unittest tests.test_breadboard_changes
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite_temp  # noqa: E402,F401

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import breadboard_changes as changes  # noqa: E402
from breadboard_steps import BOARD, PART, RESISTOR, BreadboardSteps, End, StepColors, StepPoint  # noqa: E402


def board(label):
    return End(BOARD, "board", "board " + label, "board " + label, label)


def pin(part, name, leg=""):
    return End(PART, part, "%s %s" % (part, name), "%s %s%s" % (part, name, " (%s)" % leg if leg else ""), name)


def resistor(tag, number, job, value="330Ω"):
    return End(RESISTOR, tag, "%s end %d" % (tag, number), "%s (%s %s), end %d" % (tag, value, job, number),
               str(number), job, value)


def seated(placed, points):
    return BreadboardSteps(placed, points).anchored()


def colors_of(steps):
    """The color of each jumper step, as the sheet would show it."""
    return {number: StepColors().color(number) for number, one in enumerate(steps, 1) if one.jumper}


LED_K = "the cathode"
ONE_LED = seated(["board", "TactileButton", "LedRed5mm"], [
    StepPoint([board("D8"), resistor("R1", 1, "in series with LedRed5mm A")], None, False),
    StepPoint([board("D10"), pin("TactileButton", "A")], None, False),
    StepPoint([board("GND"), pin("LedRed5mm", "K", LED_K), pin("TactileButton", "B")], None, False),
    StepPoint([pin("LedRed5mm", "A"), resistor("R1", 2, "in series with LedRed5mm A")], None, False),
])
#: The same circuit with a second LED and its resistor: the lines come from a real rebuild (button + LED, then a second
#: LED), steps 4 to 14 of its sheet.
TWO_LEDS = seated(["board", "TactileButton", "LedRed5mm", "LedGreen5mm"], [
    StepPoint([board("D8"), resistor("R1", 1, "in series with LedRed5mm A")], None, False),
    StepPoint([board("D9"), resistor("R2", 1, "in series with LedGreen5mm A")], None, False),
    StepPoint([board("D10"), pin("TactileButton", "A")], None, False),
    StepPoint([board("GND"), pin("LedGreen5mm", "K", LED_K), pin("LedRed5mm", "K", LED_K),
               pin("TactileButton", "B")], None, False),
    StepPoint([pin("LedGreen5mm", "A"), resistor("R2", 2, "in series with LedGreen5mm A")], None, False),
    StepPoint([pin("LedRed5mm", "A"), resistor("R1", 2, "in series with LedRed5mm A")], None, False),
])


def record_of(steps, earlier=None, drawn=()):
    return changes.WiringRecord.from_build(steps, colors_of(steps), earlier, drawn)


def lines_between(before, after, colors=True):
    """The lines from one build to the next; with colors=False neither sheet had a drawing."""
    earlier = record_of(before) if colors else changes.WiringRecord.from_build(before, {}, None, ())
    found = changes.changes_between(earlier, after, colors_of(after) if colors else {})
    return [changes.ChangeList().line(one) for one in found]


class SecondLedTest(unittest.TestCase):
    def test_adding_a_second_led_lists_what_to_put_and_which_jumpers_move(self):
        self.assertEqual(lines_between(ONE_LED, TWO_LEDS), [
            "Put LedGreen5mm in the breadboard.",
            "Put R2 end 1 in a free row.",
            "Run a magenta jumper from board D9 to the row of R2 end 1.",
            "Run a gold jumper from the row of LedRed5mm K to the row of LedGreen5mm K.",
            "Put R2 end 2 in the row of LedGreen5mm A.",
            "Move the purple jumper from board GND: it now goes to the row of LedGreen5mm K "
            "(it went to the row of LedRed5mm K).",
            "Move the magenta jumper from the row of TactileButton B: it now goes to the row of LedGreen5mm K "
            "(it went to the row of LedRed5mm K).",
        ])

    def test_a_circuit_built_again_unchanged_lists_nothing(self):
        self.assertEqual(lines_between(TWO_LEDS, TWO_LEDS), [])

    def test_taking_the_second_led_away_lists_what_to_take_out_with_the_colors_of_its_sheet(self):
        self.assertEqual(lines_between(TWO_LEDS, ONE_LED), [
            "Take out LedGreen5mm.",
            "Take out R2 end 1.",
            "Take out the magenta jumper from board D9 to the row of R2 end 1.",
            "Take out the gold jumper from the row of LedRed5mm K to the row of LedGreen5mm K.",
            "Take out R2 end 2.",
            "Move the orange jumper from board GND: it now goes to the row of LedRed5mm K "
            "(it went to the row of LedGreen5mm K).",
            "Move the green jumper from the row of TactileButton B: it now goes to the row of LedRed5mm K "
            "(it went to the row of LedGreen5mm K).",
        ])

    def test_codes_decide_not_words(self):
        found = changes.changes_between(record_of(ONE_LED), TWO_LEDS, colors_of(TWO_LEDS))
        self.assertEqual([one.code for one in found], ["added"] * 5 + ["rerouted"] * 2)


class ResistorTest(unittest.TestCase):
    def circuit(self, value, first="R1", second="R2"):
        return seated(["board", "Led"], [
            StepPoint([board("D8"), resistor(first, 1, "in series with Led A", value)], None, False),
            StepPoint([board("D9"), resistor(second, 1, "pull-up on Btn A")], None, False),
            StepPoint([pin("Led", "A"), resistor(first, 2, "in series with Led A", value)], None, False),
            StepPoint([pin("Btn", "A"), resistor(second, 2, "pull-up on Btn A")], None, False),
        ])

    def test_a_new_value_on_the_same_job_is_one_changed_line(self):
        self.assertEqual(lines_between(self.circuit("330Ω"), self.circuit("1kΩ")),
                         ["Swap R1, 330Ω, for a 1kΩ resistor in the same rows."])

    def test_a_resistor_that_renumbers_is_no_change(self):
        self.assertEqual(lines_between(self.circuit("330Ω"), self.circuit("330Ω", first="R2", second="R1")), [])


class JumperTest(unittest.TestCase):
    def test_a_board_jumper_from_a_free_row_to_a_part_row_is_one_reroute(self):
        before = seated(["board"], [StepPoint([board("D8"), board("D9")], None, False)])
        after = seated(["board", "Btn"], [StepPoint([board("D8"), board("D9"), pin("Btn", "A")], None, False)])
        found = changes.changes_between(record_of(before), after, colors_of(after))
        self.assertEqual([(one.code, one.name) for one in found if one.name == "board D8"],
                         [("rerouted", "board D8")])
        self.assertNotIn("removed", [one.code for one in found])


class BenchColorTest(unittest.TestCase):
    def test_a_kept_jumper_keeps_the_color_the_person_wired_across_two_rebuilds(self):
        first = record_of(ONE_LED)
        second = changes.WiringRecord.from_build(TWO_LEDS, colors_of(TWO_LEDS), first, ())
        # the GND jumper was purple on the first sheet and is orange on the second; the bench still has purple
        gnd = next(one for one in second.steps if one.key == (BOARD, "board GND"))
        self.assertEqual(gnd.color, "purple")
        removed = changes.changes_between(second, ONE_LED, colors_of(ONE_LED))
        line = next(changes.ChangeList().line(one) for one in removed if one.name == "board GND")
        self.assertTrue(line.startswith("Move the purple jumper from board GND"), line)

    def test_no_color_is_named_when_the_sheet_showed_none(self):
        found = lines_between(ONE_LED, TWO_LEDS, colors=False)
        self.assertIn("Run a jumper from board D9 to the row of R2 end 1.", found)
        self.assertIn("Move the jumper from board GND: it now goes to the row of LedGreen5mm K "
                      "(it went to the row of LedRed5mm K).", found)


class RecordTest(unittest.TestCase):
    def test_the_record_is_read_back_as_it_was_written(self):
        path = Path(tempfile.mkdtemp()) / changes.WiringRecord.FILE_NAME
        record = record_of(TWO_LEDS, drawn=[("8b.j", "17b.g")])
        path.write_text(json.dumps(record.to_dict()))
        again = changes.WiringRecord.read(path)
        self.assertEqual(again.steps, record.steps)
        self.assertEqual(again.drawn_jumpers, {frozenset(("8b.j", "17b.g"))})
        self.assertIsNone(again.why_unread)

    def test_no_file_is_no_record(self):
        self.assertIsNone(changes.WiringRecord.read(Path(tempfile.mkdtemp()) / "none.json"))

    def test_a_file_that_is_not_a_record_says_why(self):
        path = Path(tempfile.mkdtemp()) / "wiring-record.json"
        path.write_text("{not json")
        again = changes.WiringRecord.read(path)
        self.assertTrue(again.why_unread)
        self.assertEqual(again.steps, [])
        path.write_text(json.dumps({"steps": [{"key": 3}], "drawn_jumpers": []}))
        self.assertTrue(changes.WiringRecord.read(path).why_unread)


if __name__ == "__main__":
    unittest.main()
