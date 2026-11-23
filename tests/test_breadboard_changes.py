"""
A rebuild lists what to change on the bench (P300, #366): the steps of the last sheet against the steps of this one.

    python3 -m unittest tests.test_breadboard_changes
"""

import datetime
import json
import os
import resource
import signal
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite_temp  # noqa: E402,F401

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from spark.breadboard import bench_changes as changes  # noqa: E402
from spark.build import build_record  # noqa: E402
from spark.breadboard.wiring_steps import BOARD, PART, RESISTOR, BreadboardSteps, End, StepPoint  # noqa: E402

#: Input colors, one per step number, that wrap after the last: the bench changes name whatever color a sheet gave.
COLORS = ("red", "orange", "gold", "green", "cyan", "blue", "purple", "magenta")


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
    return {number: COLORS[(number - 1) % len(COLORS)] for number, one in enumerate(steps, 1) if one.jumper}


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
    return changes.WiringLog.from_build(steps, colors_of(steps), earlier, drawn)


def lines_between(before, after, colors=True):
    """The lines from one build to the next; with colors=False neither sheet had a drawing."""
    earlier = record_of(before) if colors else changes.WiringLog.from_build(before, {}, None, ())
    found = changes.changes_between(earlier, after, colors_of(after) if colors else {})
    return [changes.ChangeList().line(one) for one in found]


class SecondLedTest(unittest.TestCase):
    def test_adding_a_second_led_lists_what_to_put_and_which_jumpers_move(self):
        # a real rebuild gives these lines. The new jumper from D9 was magenta, like the button jumper that moves, so it
        # names no color
        self.assertEqual(lines_between(ONE_LED, TWO_LEDS), [
            "Put LedGreen5mm in the breadboard.",
            "Put R2 end 1 (in series with LedGreen5mm A) in a free row.",
            "Run a jumper from board D9 to the row of R2 end 1 (in series with LedGreen5mm A).",
            "Run a gold jumper from the row of LedRed5mm K to the row of LedGreen5mm K.",
            "Put R2 end 2 (in series with LedGreen5mm A) in the row of LedGreen5mm A.",
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
            "Take out R2, 330Ω in series with LedGreen5mm A.",
            "Take out the magenta jumper from board D9 to the row of R2 end 1 (in series with LedGreen5mm A).",
            "Take out the gold jumper from the row of LedRed5mm K to the row of LedGreen5mm K.",
            "Move the orange jumper from board GND: it now goes to the row of LedRed5mm K "
            "(it went to the row of LedGreen5mm K).",
            "Move the green jumper from the row of TactileButton B: it now goes to the row of LedRed5mm K "
            "(it went to the row of LedGreen5mm K).",
        ])

    def test_codes_decide_not_words(self):
        found = changes.changes_between(record_of(ONE_LED), TWO_LEDS, colors_of(TWO_LEDS))
        self.assertEqual([one.code for one in found], ["added"] * 5 + ["rerouted"] * 2)

    def test_a_removed_resistor_is_one_line_not_one_for_each_end(self):
        found = changes.changes_between(record_of(TWO_LEDS), ONE_LED, colors_of(ONE_LED))
        self.assertEqual([one.name for one in found if one.kind == "resistor"], ["R2"])


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
        found = changes.changes_between(record_of(self.circuit("330Ω")), self.circuit("1kΩ"), {})
        self.assertEqual([one.code for one in found], ["swapped"])

    def test_a_leg_that_goes_to_another_row_is_moved_not_run_like_a_jumper(self):
        before = seated(["board", "Led", "Other"], [
            StepPoint([pin("Led", "A"), resistor("R1", 2, "in series with Led A")], None, False)])
        after = seated(["board", "Led", "Other"], [
            StepPoint([pin("Other", "A"), resistor("R1", 2, "in series with Led A")], None, False)])
        self.assertEqual(lines_between(before, after), [
            "Move R1 end 2 (in series with Led A): it now goes to the row of Other A "
            "(it went to the row of Led A)."])

    def test_a_supply_that_goes_to_another_row_has_its_own_words(self):
        before = seated(["Btn", "Led"], [StepPoint([pin("Btn", "A"), pin("Led", "A")], "VBUS", False)])
        after = seated(["Btn", "Led"], [StepPoint([pin("Led", "A"), pin("Btn", "A")], "VBUS", False)])
        self.assertIn("Connect the VBUS supply to the row of Led A instead of the row of Btn A.",
                      lines_between(before, after))

    def test_a_resistor_that_changes_its_job_reads_differently_on_the_two_halves_of_a_move(self):
        before = seated(["board"], [StepPoint([board("D8"), resistor("R1", 1, "in series with Led A")], None, False)])
        after = seated(["board"], [StepPoint([board("D8"), resistor("R1", 1, "pull-up on Led A")], None, False)])
        move = next(line for line in lines_between(before, after) if line.startswith("Move the"))
        self.assertEqual(move, "Move the gold jumper from board D8: it now goes to the row of R1 end 1 (pull-up on Led A) "
                               "(it went to the row of R1 end 1 (in series with Led A)).")

    def test_a_value_is_said_with_the_article_it_is_spoken_with(self):
        for value, article in (("330Ω", "a"), ("820Ω", "an"), ("8.2kΩ", "an"), ("1kΩ", "a"), ("18Ω", "an"),
                               ("180Ω", "a"), ("11kΩ", "an"), ("10kΩ", "a")):
            with self.subTest(value=value):
                line = changes.ChangeList().line(changes.WiringChange("swapped", "resistor", "R1", None, "1Ω", value, ""))
                self.assertEqual(line, "Swap R1, 1Ω, for %s %s resistor in the same rows." % (article, value))

    def test_a_color_is_said_with_the_article_it_is_spoken_with(self):
        for color, article in (("orange", "an"), ("red", "a"), ("blue", "a")):
            with self.subTest(color=color):
                line = changes.ChangeList().line(changes.WiringChange("added", "jumper", "board D8", color, "", "x", ""))
                self.assertEqual(line, "Run %s %s jumper from board D8 to x." % (article, color))

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


class RailTest(unittest.TestCase):
    BEFORE = seated(["board", "A", "B"], [StepPoint([board("GND"), pin("A", "K"), pin("B", "K")], None, False)])
    AFTER = seated(["board", "A", "B", "C"], [StepPoint([board("GND"), pin("A", "K"), pin("B", "K"), pin("C", "K")],
                                                        None, True)])

    def test_the_line_that_marks_a_rail_comes_first_even_when_a_user_is_first_in_step_order(self):
        lines = lines_between(self.BEFORE, self.AFTER)
        self.assertEqual(lines[0].split(":")[1].strip(), "it now goes to a free rail, which you mark GND "
                                                         "(it went to the row of A K).")
        self.assertIn("Put C in the breadboard.", lines[1:])

    def test_only_the_first_line_marks_the_rail_and_the_record_keeps_the_mark_apart_from_the_words(self):
        steps = [one for one in changes.describe(self.AFTER) if one.anchor and one.anchor[0] == "rail"]
        self.assertEqual([one.marks for one in steps], ["GND", "", "", ""])
        self.assertEqual({one.to for one in steps}, {"the GND rail"})
        lines = lines_between(self.BEFORE, self.AFTER)
        self.assertEqual(sum("mark GND" in line for line in lines), 1)
        self.assertTrue(any("it now goes to the GND rail" in line for line in lines))

    def test_a_jumper_taken_off_a_rail_does_not_say_to_mark_it(self):
        lines = lines_between(self.AFTER, self.BEFORE)
        self.assertTrue(all("mark" not in line for line in lines), lines)
        self.assertIn("Take out the magenta jumper from the row of C K to the GND rail.", lines)


class SignedRailTest(unittest.TestCase):
    """P953: power and ground go through the rails, so a rebuild of a project wired before tells the person once to move
    each such jumper, and says the rail's sign."""

    def test_an_old_ground_jumper_is_moved_to_a_minus_rail_once(self):
        # today's XIAO sheet, rebuilt: its ground point was a row, now it is a - rail
        from spark.breadboard import sheet, wiring_steps
        with mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()}):
            read = sheet._read_build(Path(__file__).resolve().parent / "data" / "breadboard" / "button-light-xiao"
                                     / "requirements.json")
        now = read.steps.anchored()
        before = wiring_steps.BreadboardSteps(read.steps.placed, [point._replace(rail=False) for point in read.steps.points],
                                              read.steps.shorts).anchored()
        earlier = record_of(before)
        lines = changes.ChangeList().render(changes.changes_between(earlier, now, colors_of(now)))
        self.assertEqual([line for line in lines if "rail" in line], [
            "Move the purple jumper from board GND: it now goes to a free - rail, which you mark GND (it went to the row of "
            "LedRed5mm K).",
            "Run a jumper from the row of LedRed5mm K to the GND rail.",
            "Move the magenta jumper from the row of TactileButton B: it now goes to the GND rail (it went to the row of "
            "LedRed5mm K)."])
        again = changes.WiringLog.from_build(now, colors_of(now), earlier, ())
        self.assertEqual(changes.changes_between(again, now, colors_of(now)), [])

    def test_a_pull_down_leg_put_in_the_rail_before_is_no_change(self):
        # P960: the leg's step is a jumper from its row to the rail now. A record whose step put the leg in the rail
        # itself joins the same point, so a rebuild lists no change.
        now = seated(["board", "Btn"], [
            StepPoint([board("GND"), pin("Btn", "B"), resistor("R1", 2, "pull-down on Btn A", "10kΩ")], None, True),
            StepPoint([pin("Btn", "A"), resistor("R1", 1, "pull-down on Btn A", "10kΩ")], None, False)])
        leg = next(one for one in changes.describe(now) if one.key == ("resistor", "pull-down on Btn A", "2"))
        self.assertEqual((leg.kind, leg.source), ("jumper", "the row of R1 end 2 (pull-down on Btn A)"))
        before = [one._replace(jumper=False) if one.act == "join" and one.subject.name == "R1 end 2" else one for one in now]
        earlier = record_of(before)
        self.assertEqual([(one.kind, one.source) for one in earlier.steps if one.key == leg.key],
                         [("leg", "R1 end 2 (pull-down on Btn A)")])
        self.assertEqual(changes.changes_between(earlier, now, colors_of(now)), [])

    def test_an_old_record_with_no_sign_keeps_the_free_rail_words(self):
        path = Path(tempfile.mkdtemp()) / "wiring-record.json"
        step = {"key": ["board", "board GND"], "anchor": ["rail", "GND"], "kind": "jumper", "source": "board GND",
                "to": "the GND rail", "tag": "", "value": "", "job": "", "color": "black", "marks": "GND"}
        path.write_text(json.dumps({"steps": [step], "drawn_jumpers": []}))
        old = changes.WiringLog.read(path)
        self.assertEqual((old.why_unread, old.steps[0].sign), (None, ""))
        change = changes.WiringChange("rerouted", "jumper", "board GND", "black", "the row of A K", "the GND rail", "GND")
        self.assertEqual(changes.ChangeList().line(change), "Move the black jumper from board GND: it now goes to a free "
                                                            "rail, which you mark GND (it went to the row of A K).")
        self.assertIn("a free - rail, which you mark GND", changes.ChangeList().line(change._replace(sign="-")))


class RemoveAndSwapTest(unittest.TestCase):
    def test_a_take_out_comes_before_a_swap_in_one_rebuild(self):
        before = seated(["board", "Led", "Old"], [
            StepPoint([board("D8"), resistor("R1", 1, "in series with Led A", "330Ω")], None, False),
            StepPoint([pin("Led", "A"), resistor("R1", 2, "in series with Led A", "330Ω")], None, False),
            StepPoint([board("D9"), pin("Old", "A")], None, False)])
        after = seated(["board", "Led"], [
            StepPoint([board("D8"), resistor("R1", 1, "in series with Led A", "1kΩ")], None, False),
            StepPoint([pin("Led", "A"), resistor("R1", 2, "in series with Led A", "1kΩ")], None, False)])
        found = changes.changes_between(record_of(before), after, colors_of(after))
        self.assertEqual([one.code for one in found], ["removed", "removed", "swapped"])
        self.assertEqual(lines_between(before, after)[-1], "Swap R1, 330Ω, for a 1kΩ resistor in the same rows.")


class BenchColorTest(unittest.TestCase):
    def test_a_kept_jumper_keeps_the_color_the_person_wired_across_two_rebuilds(self):
        first = record_of(ONE_LED)
        second = changes.WiringLog.from_build(TWO_LEDS, colors_of(TWO_LEDS), first, ())
        # the GND jumper was purple on the first sheet and is orange on the second; the bench still has purple
        gnd = next(one for one in second.steps if one.key == (BOARD, "board GND"))
        self.assertEqual(gnd.color, "purple")
        removed = changes.changes_between(second, ONE_LED, colors_of(ONE_LED))
        line = next(changes.ChangeList().line(one) for one in removed if one.name == "board GND")
        self.assertTrue(line.startswith("Move the purple jumper from board GND"), line)

    def test_no_color_is_named_when_the_sheet_showed_none(self):
        found = lines_between(ONE_LED, TWO_LEDS, colors=False)
        self.assertIn("Run a jumper from board D9 to the row of R2 end 1 (in series with LedGreen5mm A).", found)
        self.assertIn("Move the jumper from board GND: it now goes to the row of LedGreen5mm K "
                      "(it went to the row of LedRed5mm K).", found)


class BaseKeptTest(unittest.TestCase):
    """The base is the steps of the last sheet whose wiring differs from this one, with the time of that sheet (P875)."""

    def test_another_wiring_makes_the_earlier_sheet_the_base(self):
        first = changes.WiringLog.from_build(ONE_LED, colors_of(ONE_LED), None, (), "t1")
        second = changes.WiringLog.from_build(TWO_LEDS, colors_of(TWO_LEDS), first, (), "t2")
        self.assertIsNone(first.base)
        self.assertEqual((second.at, second.base), ("t2", changes.SheetBase(first.steps, "t1")))

    def test_the_same_wiring_carries_the_base_on(self):
        first = changes.WiringLog.from_build(ONE_LED, colors_of(ONE_LED), None, (), "t1")
        second = changes.WiringLog.from_build(TWO_LEDS, colors_of(TWO_LEDS), first, (), "t2")
        third = changes.WiringLog.from_build(TWO_LEDS, colors_of(TWO_LEDS), second, (), "t3")
        self.assertEqual((third.at, third.base), ("t3", changes.SheetBase(first.steps, "t1")))

    def test_a_first_wiring_built_twice_has_no_base(self):
        first = changes.WiringLog.from_build(ONE_LED, colors_of(ONE_LED), None, (), "t1")
        self.assertIsNone(changes.WiringLog.from_build(ONE_LED, colors_of(ONE_LED), first, (), "t2").base)

    def test_the_base_is_read_back_as_it_was_written(self):
        path = Path(tempfile.mkdtemp()) / changes.WiringLog.FILE_NAME
        first = changes.WiringLog.from_build(ONE_LED, colors_of(ONE_LED), None, (), "2026-03-04T10:32:00+01:00")
        second = changes.WiringLog.from_build(TWO_LEDS, colors_of(TWO_LEDS), first, (), "2026-03-05T11:47:00+01:00")
        path.write_text(json.dumps(second.to_dict()))
        again = changes.WiringLog.read(path)
        self.assertEqual((again.at, again.base), (second.at, second.base))

    def test_a_record_with_no_time_and_no_base_is_read_as_one_with_neither(self):
        path = Path(tempfile.mkdtemp()) / changes.WiringLog.FILE_NAME
        path.write_text(json.dumps({key: value for key, value in record_of(ONE_LED).to_dict().items() if key not in ("at", "base")}))
        again = changes.WiringLog.read(path)
        self.assertEqual((again.at, again.base, again.why_unread), (None, None, None))

    def test_a_time_that_is_no_time_is_a_record_that_cannot_be_read(self):
        path = Path(tempfile.mkdtemp()) / changes.WiringLog.FILE_NAME
        path.write_text(json.dumps(dict(record_of(ONE_LED).to_dict(), at="yesterday")))
        self.assertTrue(changes.WiringLog.read(path).why_unread)

    def test_the_heading_names_the_time_or_says_none_is_known(self):
        self.assertEqual(changes.ChangeList().heading("2026-03-04T10:32:00+01:00"),
                         "Changes since the sheet spark wrote on " + datetime.datetime(2026, 3, 4, 10, 32, tzinfo=datetime.timezone(
                             datetime.timedelta(hours=1))).astimezone().strftime("%Y-%m-%d %H:%M"))
        self.assertEqual(changes.ChangeList().heading(None), "Changes since an earlier sheet spark wrote (spark did not note when)")


class StageWriteTest(unittest.TestCase):
    def test_a_stage_whose_own_write_fails_leaves_no_stage(self):
        folder = Path(tempfile.mkdtemp())
        store = changes.WiringLogStore(folder)
        was = signal.signal(signal.SIGXFSZ, signal.SIG_IGN)  # a file past the limit then fails with an OSError
        soft, hard = resource.getrlimit(resource.RLIMIT_FSIZE)
        resource.setrlimit(resource.RLIMIT_FSIZE, (10, hard))
        try:
            with self.assertRaises(OSError):
                store.stage(record_of(ONE_LED))
        finally:
            resource.setrlimit(resource.RLIMIT_FSIZE, (soft, hard))
            signal.signal(signal.SIGXFSZ, was)
        self.assertEqual(list(folder.iterdir()), [])


class StagedBytesTest(unittest.TestCase):
    def test_a_stage_made_from_data_holds_the_data_and_commits_it(self):
        folder = Path(tempfile.mkdtemp())
        staged = build_record.StagedFile.from_bytes(folder / "x.json.new", b"held")
        staged.make()
        self.assertEqual((folder / "x.json.new").read_bytes(), b"held")
        staged.commit(folder / "x.json")
        self.assertEqual(((folder / "x.json").read_bytes(), (folder / "x.json.new").exists()), (b"held", False))


class RecordTest(unittest.TestCase):
    def test_the_record_is_read_back_as_it_was_written(self):
        path = Path(tempfile.mkdtemp()) / changes.WiringLog.FILE_NAME
        record = record_of(TWO_LEDS, drawn=[("8b.j", "17b.g")])
        path.write_text(json.dumps(record.to_dict()))
        again = changes.WiringLog.read(path)
        self.assertEqual(again.steps, record.steps)
        self.assertEqual(again.drawn_jumpers, {frozenset(("8b.j", "17b.g"))})
        self.assertIsNone(again.why_unread)

    def test_a_record_is_written_whole_or_not_at_all(self):
        path = Path(tempfile.mkdtemp()) / changes.WiringLog.FILE_NAME
        store = changes.WiringLogStore(path.parent)
        store.commit(store.stage(record_of(ONE_LED)))
        earlier = path.read_text()
        with mock.patch.object(os, "replace", side_effect=OSError("disk")):
            with self.assertRaises(OSError):
                store.commit(store.stage(record_of(TWO_LEDS)))
        self.assertEqual(path.read_text(), earlier)

    def test_no_file_is_no_record(self):
        self.assertIsNone(changes.WiringLog.read(Path(tempfile.mkdtemp()) / "none.json"))

    def test_a_file_that_is_not_a_record_says_why(self):
        path = Path(tempfile.mkdtemp()) / "wiring-record.json"
        path.write_text("{not json")
        again = changes.WiringLog.read(path)
        self.assertTrue(again.why_unread)
        self.assertEqual(again.steps, [])
        path.write_text(json.dumps({"steps": [{"key": 3}], "drawn_jumpers": []}))
        self.assertTrue(changes.WiringLog.read(path).why_unread)


if __name__ == "__main__":
    unittest.main()
