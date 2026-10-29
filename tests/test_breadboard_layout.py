"""
The drawn breadboard (P267, #300): the sheet's steps planned into holes on Wokwi's half breadboard, and written as a
Wokwi diagram. The geometry is the one measured in Wokwi (docs/discovery/2026-10-16-p267-wokwi-holes/).

    python3 -m unittest tests.test_breadboard_layout
"""

import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite_temp  # noqa: E402,F401

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import breadboard  # noqa: E402
import breadboard_catalog  # noqa: E402
import breadboard_drawing  # noqa: E402
import breadboard_steps  # noqa: E402
from breadboard_drawing import HoleLedger, NotDrawn, WokwiGeometry, rotate  # noqa: E402

XIAO = ROOT / "tests" / "data" / "breadboard" / "button-light-xiao"
GEOMETRY = WokwiGeometry.load()


def in_store():
    return mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()})


def xiao_read():
    with in_store():
        return breadboard._read_build(XIAO / "requirements.json")


class TheTurnTest(unittest.TestCase):
    def test_a_turn_of_90_gives_the_pins_wokwi_drew(self):
        # Read from the editor's pin overlays with the part at (100, 100), turned 90 degrees.
        shape = GEOMETRY.part("board-xiao-esp32-c6")
        turned = rotate(shape["pins"], shape["center"], 90)
        for pin, at in [("D0", (59.365, 15.418)), ("D7", (1.765, 72.4))]:
            self.assertEqual(tuple(_rounded(v) for v in turned[pin]), at, pin)
        for pin, at in [("1.l", (45, -9)), ("2.r", (26, 58))]:
            got = rotate(GEOMETRY.part("wokwi-pushbutton")["pins"], [33.5, 24.5], 90)[pin]
            self.assertEqual(tuple(_rounded(v) for v in got), at, pin)

    def test_a_turned_led_gives_the_pins_wokwi_drew(self):
        # The refuter: the LED is 40 wide and 50 high, so it turns about (20, 25); Wokwi drew A at (3, 30) turned 90.
        shape = GEOMETRY.part("wokwi-led")
        turned = rotate(shape["pins"], shape["center"], 90)
        self.assertEqual({pin: tuple(_rounded(v) for v in at) for pin, at in turned.items()},
                         {"A": (3, 30), "C": (3, 20)})

    def test_four_turns_come_back_and_two_are_a_half_turn(self):
        shape = GEOMETRY.part("wokwi-resistor")
        for degrees in (0, 360):
            self.assertEqual(rotate(shape["pins"], shape["center"], degrees), {k: tuple(v) for k, v in shape["pins"].items()})
        half = rotate(shape["pins"], shape["center"], 180)
        self.assertAlmostEqual(half["1"][0], 59)
        self.assertAlmostEqual(half["2"][0], 0.2)
        self.assertEqual(rotate(rotate(shape["pins"], shape["center"], 90), shape["center"], 90), half)
        self.assertNotEqual(rotate(shape["pins"], shape["center"], 270), rotate(shape["pins"], shape["center"], 90))


def _rounded(value):
    """A turned position as the file holds it: rounded once, at the end."""
    return round(value, 3)


class TheStepColorsTest(unittest.TestCase):
    def test_step_one_is_the_palette_s_first_and_step_nine_wraps_to_it(self):
        colors = breadboard_steps.StepColors()
        self.assertEqual([colors.color(n) for n in (1, 2, 8, 9)], ["red", "orange", "magenta", "red"])


class TheBreadboardTest(unittest.TestCase):
    def test_the_half_board_has_300_holes_in_rows_of_five_and_four_rails_of_25(self):
        self.assertEqual(len(GEOMETRY.surface.terminal), 300)
        rows = {}
        for hole in GEOMETRY.surface.holes:
            rows.setdefault(hole.group, []).append(hole)
        self.assertEqual({len(holes) for row, holes in rows.items() if row not in GEOMETRY.surface.rails}, {5})
        self.assertEqual({len(rows[rail]) for rail in GEOMETRY.surface.rails}, {25})

    def test_a_column_is_tried_nearest_the_gap_first_and_below_it_before_above(self):
        # The tech lead (P270): ranked by letter, never by float distance, whose ties in mm would move a part.
        first_column = [hole.name.rsplit(".", 1)[1] for hole in GEOMETRY.surface.by_gap[:10]]
        self.assertEqual(first_column, list("fegdhcibja"))

    def test_measured_holes_lie_where_wokwi_drew_them(self):
        found = {hole.name: (round(hole.x, 3), round(hole.y, 3)) for hole in GEOMETRY.surface.holes}
        for name, at in {"1t.a": (26, 51), "15t.c": (160.4, 70.2), "30b.j": (304.4, 156.6), "tp.1": (34, 12.3),
                         "tp.25": (302.8, 12.3), "tn.1": (34, 22.3), "bp.1": (34, 186.3), "bn.1": (34, 196.3)}.items():
            self.assertEqual(found[name], at, name)


class TheLedgerTest(unittest.TestCase):
    def test_a_taken_hole_is_refused_and_named(self):
        ledger = HoleLedger(GEOMETRY.surface)
        hole = GEOMETRY.surface.terminal[0]
        ledger.claim(hole, "board D0")
        with self.assertRaisesRegex(NotDrawn, "hole 1t.a is taken by board D0"):
            ledger.claim(hole, "LedRed5mm A")

    def test_a_free_group_lies_right_of_the_column_it_is_given(self):
        self.assertEqual(HoleLedger(GEOMETRY.surface).claim_free_group(5, "a jumper").column, 6)

    def test_a_full_group_and_a_full_board_are_refused(self):
        ledger = HoleLedger(GEOMETRY.surface)
        for _ in range(5):
            ledger.claim_free_hole("1t", "a jumper")
        with self.assertRaisesRegex(NotDrawn, "row 1t has no free hole"):
            ledger.claim_free_hole("1t", "a jumper")
        for _ in range(59):
            ledger.claim_free_group(0, "a part")
        with self.assertRaisesRegex(NotDrawn, "no free row left"):
            ledger.claim_free_group(0, "one more")


class TheXiaoLayoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read = xiao_read()
        cls.layout = breadboard._plan_layout(cls.read)

    def test_every_pin_lies_within_the_tolerance_of_its_hole(self):
        for part in self.layout.parts:
            shape = GEOMETRY.part(part.type)
            turned = rotate(shape["pins"], shape["center"], part.rotate)
            for pin, hole in part.holes.items():
                x, y = turned[pin]
                self.assertLessEqual(abs(part.left + x - hole.x), 1.5, (part.id, pin))
                self.assertLessEqual(abs(part.top + y - hole.y), 1.5, (part.id, pin))

    def test_the_board_straddles_the_gap_turned(self):
        board = self.layout.parts[0]
        self.assertEqual((board.id, board.rotate), ("board", 90))
        self.assertEqual({hole.group[-1] for hole in board.holes.values()}, {"t", "b"})

    def test_no_row_holds_the_ends_of_two_points(self):
        # Each row's ends, by point: a part pin, a resistor leg, and each jumper's two ends (the refuter: jumper ends
        # count too). The button's two pins of one contact sit in two rows, so each row still holds one point.
        point_of = {}
        for number, point in enumerate(self.read.steps.points):
            for end in point.ends:
                point_of[end.name] = number
        catalog = breadboard_catalog.describe_parts(self.read, GEOMETRY)
        rows = {}
        for part in self.layout.parts:
            pins = {wokwi: name for name, wokwi in catalog[part.id].pins.items()}
            for pin, hole in part.holes.items():
                end = next((e for p in self.read.steps.points for e in p.ends
                            if e.component == part.id and e.pin == pins.get(pin)), None)
                rows.setdefault(hole.group, set()).add(point_of[end.name] if end else (part.id, pin))
        seated = list(self.read.steps.anchored())
        for jumper in self.layout.jumpers:
            point = point_of[seated[jumper.step - 1].subject.name]
            for hole in (jumper.one, jumper.other):
                rows.setdefault(hole.group, set()).add(point)
        for row, held in rows.items():
            self.assertEqual(len(held), 1, (row, held))

    def test_each_jumper_step_has_one_wire_in_its_step_s_color(self):
        seated = list(self.read.steps.anchored())
        jumper_steps = [number for number, one in enumerate(seated, 1)
                        if one.act == breadboard_steps.JOIN and one.subject.kind != breadboard_steps.RESISTOR]
        self.assertEqual([jumper.step for jumper in self.layout.jumpers], jumper_steps)
        drawn = json.loads(breadboard_drawing.WokwiBreadboardDiagram().text(self.layout))
        self.assertEqual([wire[2] for wire in drawn["connections"]],
                         [breadboard_steps.StepColors().color(number) for number in jumper_steps])

    def test_one_empty_column_parts_the_board_s_body_from_the_next_part(self):
        # The board's pins are in columns 3 to 9 and its body covers 10; column 11 stays empty, so the button is in 12.
        board, button = self.layout.parts[0], self.layout.parts[1]
        self.assertEqual(max(hole.column for hole in board.holes.values()), 9)
        self.assertEqual(min(hole.column for hole in button.holes.values()), 12)

    def test_the_same_build_gives_the_same_bytes(self):
        once = breadboard_drawing.WokwiBreadboardDiagram().text(self.layout)
        self.assertEqual(once, breadboard_drawing.WokwiBreadboardDiagram().text(breadboard._plan_layout(xiao_read())))

    def test_the_drawing_keeps_the_bytes_wokwi_showed(self):
        # The screenshot in docs/discovery/2026-10-16-p267-wokwi-holes/ shows exactly these bytes (P267, PR #303).
        # A refactor must not move a part by a rounding step: P270 changes the units inside, never the file.
        with in_store():
            text = breadboard.drawing(XIAO / "requirements.json")
        self.assertEqual(hashlib.sha256(text.encode()).hexdigest(),
                         "cf3f8e5384d50a1d496be66784679810f8932b1576566ca6f8a9d8f59646c32d")

    def test_every_hole_named_exists_on_a_half_board(self):
        drawn = json.loads(breadboard_drawing.WokwiBreadboardDiagram().text(self.layout))
        names = {"bb1:" + hole.name for hole in GEOMETRY.surface.holes}
        for wire in drawn["connections"]:
            self.assertLessEqual(set(wire[:2]), names)


class AnOldDrawingTest(unittest.TestCase):
    def test_write_removes_a_drawing_an_earlier_build_left_when_this_one_cannot_be_drawn(self):
        import shutil
        project = Path(tempfile.mkdtemp()) / "motor"
        shutil.copytree(ROOT / "tests" / "data" / "breadboard" / "motor", project)
        (project / "breadboard.json").write_text("{}")
        with in_store():
            written = breadboard.write(project / "requirements.json", project / "breadboard.md")
        self.assertEqual(written.drawings, [])
        self.assertIn("no Wokwi pin positions", written.why)
        self.assertFalse((project / "breadboard.json").exists())


class OnePlanPerWriteTest(unittest.TestCase):
    def test_the_sheet_and_every_drawing_come_from_one_plan(self):
        # The tech lead (P270): the sheet planned the layout a second time, so its color line could differ from the
        # drawing's wires.
        import shutil
        project = Path(tempfile.mkdtemp()) / "xiao"
        shutil.copytree(XIAO, project)
        with in_store(), mock.patch.object(breadboard, "_plan_layout", wraps=breadboard._plan_layout) as planned:
            written = breadboard.write(project / "requirements.json", project / "breadboard.md")
        self.assertEqual(planned.call_count, 1)
        self.assertEqual([path.name for path, _ in written.drawings],
                         [renderer.FILE_NAME for renderer in breadboard.DRAWING_RENDERERS])


class WhatIsNotDrawnTest(unittest.TestCase):
    def test_a_rail_is_said_not_drawn(self):
        read = xiao_read()
        rail = breadboard_steps.StepPoint(read.steps.points[0].ends, None, True)
        steps = breadboard_steps.BreadboardSteps(read.steps.placed, [rail] + read.steps.points[1:])
        planner = breadboard_drawing.BreadboardPlanner(GEOMETRY, breadboard_catalog.describe_parts(read, GEOMETRY))
        with self.assertRaisesRegex(NotDrawn, "goes on a rail, and rails are not drawn yet"):
            planner.plan(steps)

    def test_a_supply_from_off_the_board_is_said_not_drawn(self):
        # The refuter: a supply step was skipped without a word, so the drawing lacked a wire the sheet has.
        read = xiao_read()
        last = read.steps.points[-1]
        supplied = breadboard_steps.StepPoint(last.ends, "VBAT", False)
        steps = breadboard_steps.BreadboardSteps(read.steps.placed, read.steps.points[:-1] + [supplied])
        planner = breadboard_drawing.BreadboardPlanner(GEOMETRY, breadboard_catalog.describe_parts(read, GEOMETRY))
        with self.assertRaisesRegex(NotDrawn, "the VBAT supply comes from off the board"):
            planner.plan(steps)

    def test_a_resistor_that_joins_a_later_resistor_s_row_waits_for_it(self):
        # The correctness lens: R2 is set up first, but its other leg joins R1's row, which R1 places later.
        read = xiao_read()
        board_d8 = next(end for point in read.steps.points for end in point.ends if end.name == "board D8")
        led_a = next(end for point in read.steps.points for end in point.ends if end.name == "LedRed5mm A")

        def leg(tag, number):
            return breadboard_steps.End(breadboard_steps.RESISTOR, tag, "%s end %d" % (tag, number),
                                        "%s, end %d" % (tag, number), str(number))

        points = [breadboard_steps.StepPoint([board_d8, leg("R2", 1)], None, False),
                  breadboard_steps.StepPoint([leg("R1", 1), leg("R2", 2)], None, False),
                  breadboard_steps.StepPoint([led_a, leg("R1", 2)], None, False)]
        steps = breadboard_steps.BreadboardSteps(read.steps.placed, points)
        catalog = breadboard_catalog.describe_parts(read, GEOMETRY)
        catalog["R2"] = catalog["R1"]
        layout = breadboard_drawing.BreadboardPlanner(GEOMETRY, catalog).plan(steps)
        self.assertLessEqual({"R1", "R2"}, {part.id for part in layout.parts})

    def leg(self, tag, number):
        return breadboard_steps.End(breadboard_steps.RESISTOR, tag, "%s end %d" % (tag, number),
                                    "%s, end %d" % (tag, number), str(number))

    def end_named(self, read, name):
        return next(end for point in read.steps.points for end in point.ends if end.name == name)

    def test_a_resistor_whose_both_legs_join_rows_is_said_not_drawn(self):
        read = xiao_read()
        points = [breadboard_steps.StepPoint([self.end_named(read, "LedRed5mm A"), self.leg("R1", 1)], None, False),
                  breadboard_steps.StepPoint([self.end_named(read, "TactileButton A"), self.leg("R1", 2)], None, False)]
        planner = breadboard_drawing.BreadboardPlanner(GEOMETRY, breadboard_catalog.describe_parts(read, GEOMETRY))
        with self.assertRaisesRegex(NotDrawn, "both ends of R1 join other rows"):
            planner.plan(breadboard_steps.BreadboardSteps(read.steps.placed, points))

    def test_a_resistor_with_no_leg_joined_goes_right_of_the_parts(self):
        read = xiao_read()
        points = [breadboard_steps.StepPoint([self.end_named(read, "board D8"), self.leg("R1", 1)], None, False),
                  breadboard_steps.StepPoint([self.end_named(read, "board D10"), self.leg("R1", 2)], None, False)]
        layout = breadboard_drawing.BreadboardPlanner(GEOMETRY, breadboard_catalog.describe_parts(read, GEOMETRY)).plan(
            breadboard_steps.BreadboardSteps(read.steps.placed, points))
        parts = {part.id: part for part in layout.parts}
        last = max(hole.column for part in layout.parts if part.id != "R1" for hole in part.holes.values())
        self.assertGreater(min(hole.column for hole in parts["R1"].holes.values()), last + 1)

    def test_a_part_with_no_wokwi_drawing_is_named(self):
        read = xiao_read()
        catalog = breadboard_catalog.describe_parts(read, GEOMETRY)
        del catalog["LedRed5mm"]
        with self.assertRaisesRegex(NotDrawn, "nothing says how to draw LedRed5mm in Wokwi"):
            breadboard_drawing.BreadboardPlanner(GEOMETRY, catalog).plan(read.steps)

    def test_a_resistor_value_is_in_ohms(self):
        self.assertEqual([breadboard_catalog.to_ohms(v) for v in ("330Ω", "10kΩ", "4.7kΩ", "1MΩ", "")],
                         ["330", "10000", "4700", "1000000", ""])


if __name__ == "__main__":
    unittest.main()
