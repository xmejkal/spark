"""
The drawn breadboard (P267, #300): the sheet's steps planned into holes on Wokwi's half breadboard, and written as a
Wokwi diagram. The geometry is the one measured in Wokwi (docs/discovery/2026-10-16-p267-wokwi-holes/).

    python3 -m unittest tests.test_breadboard_layout
"""

import collections
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

from spark.breadboard import sheet  # noqa: E402
from spark.breadboard import drawing_catalog  # noqa: E402
from spark.breadboard import drawing  # noqa: E402
from spark.breadboard import wiring_steps  # noqa: E402
from spark.breadboard import part_shape  # noqa: E402
from spark.breadboard import rails  # noqa: E402
from spark.breadboard import spacing  # noqa: E402
from spark.breadboard.drawing import HoleLedger, NotDrawnError, WokwiGeometry, rotate  # noqa: E402
from spark.breadboard.breadboard_scene import BreadboardSceneMaker  # noqa: E402

XIAO = ROOT / "tests" / "data" / "breadboard" / "button-light-xiao"
RECORD_BOARD = ROOT / "tests" / "data" / "breadboard" / "button-light"
GEOMETRY = WokwiGeometry.load()


def in_store():
    return mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()})


def xiao_read():
    with in_store():
        return sheet._read_build(XIAO / "requirements.json")


def drawing_text(requirements_path):
    """The Wokwi diagram's text as the sheet writes it: the planned layout's scene, made by the sheet's maker."""
    return drawing.WokwiBreadboardDiagram().text(sheet.SCENE_MAKER.make(sheet._plan_layout(sheet._read_build(requirements_path))))


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


class TheJumperColorsTest(unittest.TestCase):
    """P947: a jumper's color says what it carries: red for power, black for ground, gray when no record says, and each
    signal the next color of its own list, in step order."""

    def test_power_is_red_ground_black_and_a_role_not_known_gray(self):
        self.assertEqual(wiring_steps.JumperColors().of({3: "power", 4: "signal", 8: "ground", 9: "unknown"}),
                         {3: "red", 4: "green", 8: "black", 9: "gray"})

    def test_signals_take_the_colors_in_their_own_order_and_wrap_after_the_last(self):
        colors = wiring_steps.JumperColors().of({number: "signal" for number in range(3, 10)} | {5: "ground"})
        self.assertEqual([colors[n] for n in (3, 4, 6, 7, 8, 9)], ["green", "blue", "purple", "orange", "magenta", "cyan"])
        wrapped = wiring_steps.JumperColors().of({number: "signal" for number in range(1, 9)})
        self.assertEqual((wrapped[7], wrapped[8]), ("green", "blue"))

    def test_no_signal_is_red_black_or_gray_and_neighbouring_signals_differ(self):
        colors = wiring_steps.JumperColors().of({number: "signal" for number in range(1, 20)})
        self.assertFalse({"red", "black", "gray"} & set(colors.values()))
        self.assertTrue(all(colors[n] != colors[n + 1] for n in range(1, 19)))


class TheSheetNamesTheWireColorsTest(unittest.TestCase):
    """P947: the e-paper sheet's color line, the picture's wires and the wiring record name one color per jumper."""

    def test_the_line_the_svg_and_the_record_agree(self):
        import shutil
        project = Path(tempfile.mkdtemp()) / "epaper"
        shutil.copytree(EPAPER, project)
        with in_store():
            sheet.write(project / "requirements.json", project / "breadboard.md")
        text = (project / "breadboard.md").read_text()
        self.assertIn("Each jumper has the color of what it carries, red for power, black for ground and another color "
                      "for each signal: 3 red, 4 red, 5 green, 6 blue, 7 purple, 8 orange, 9 black, 10 black, 11 magenta, "
                      "12 cyan.", text)  # P953: power and ground through the rails, one jumper per end
        record = json.loads((project / "wiring-record.json").read_text())
        self.assertEqual([step["color"] for step in record["steps"]][2:], ["red", "red", "green", "blue", "purple",
                                                                         "orange", "black", "black", "magenta", "cyan"])
        svg = (project / "breadboard.svg").read_text()
        # P953 PR 4a: the picture draws a red and a black wire in the palette's hex
        self.assertIn('stroke="#d0202a" stroke-width="2.2"', svg)
        self.assertIn('stroke="#20262b" stroke-width="2.2"', svg)

    def test_a_role_not_known_is_said_so(self):
        with in_store():
            read = sheet._read_build(EPAPER / "requirements.json")
        planned = sheet._plan_once(read)
        jumpers = [jumper._replace(role="unknown") if jumper.step == 4 else jumper for jumper in planned.layout.jumpers]
        layout = planned.layout._replace(jumpers=jumpers)
        planned = planned._replace(layout=layout, scene=sheet.SCENE_MAKER.make(layout))
        self.assertIn("3 red, 4 gray (role not known), 5 green,",
                      sheet.sheet(EPAPER / "requirements.json", read=read, planned=planned))


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
        with self.assertRaisesRegex(NotDrawnError, "hole 1t.a is taken by board D0") as refused:
            ledger.claim(hole, "LedRed5mm A")
        self.assertEqual((refused.exception.code, refused.exception.subject), ("planner_fault", "1t.a"))

    def test_a_free_group_lies_right_of_the_column_it_is_given(self):
        self.assertEqual(HoleLedger(GEOMETRY.surface).claim_free_group(5, "a jumper").column, 6)

    def test_a_full_group_and_a_full_board_are_refused(self):
        ledger = HoleLedger(GEOMETRY.surface)
        for _ in range(5):
            ledger.claim_free_hole("1t", "a jumper")
        with self.assertRaisesRegex(NotDrawnError, "row 1t has no free hole") as full_row:
            ledger.claim_free_hole("1t", "a jumper")
        for _ in range(59):
            ledger.claim_free_group(0, "a part")
        with self.assertRaisesRegex(NotDrawnError, "no free row left") as full_board:
            ledger.claim_free_group(0, "one more")
        self.assertEqual((full_row.exception.code, full_row.exception.subject), ("row_full", "1t"))
        self.assertEqual((full_board.exception.code, full_board.exception.subject), ("no_hole_left", "one more"))


class TheXiaoLayoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.read = xiao_read()
        cls.layout = sheet._plan_layout(cls.read)

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
        catalog = drawing_catalog.describe_parts(self.read, GEOMETRY)
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

    def test_each_jumper_step_has_one_wire_in_the_color_of_its_role(self):
        seated = list(self.read.steps.anchored())
        jumper_steps = [number for number, one in enumerate(seated, 1)
                        if one.act == wiring_steps.JOIN and one.subject.kind != wiring_steps.RESISTOR]
        self.assertEqual([jumper.step for jumper in self.layout.jumpers], jumper_steps)
        drawn = json.loads(drawing.WokwiBreadboardDiagram().text(BreadboardSceneMaker().make(self.layout)))
        roles = {jumper.step: jumper.role for jumper in self.layout.jumpers}
        self.assertEqual([wire[2] for wire in drawn["connections"]],
                         [wiring_steps.JumperColors().of(roles)[number] for number in jumper_steps])
        self.assertEqual(roles[jumper_steps[0]], "signal")

    def test_one_empty_column_parts_the_board_s_body_from_the_next_part(self):
        # The board's pins are in columns 3 to 9 and its body covers 10; column 11 stays empty, so the button is in 12.
        board, button = self.layout.parts[0], self.layout.parts[1]
        self.assertEqual(max(hole.column for hole in board.holes.values()), 9)
        self.assertEqual(min(hole.column for hole in button.holes.values()), 12)

    def test_the_same_build_gives_the_same_bytes(self):
        once = drawing.WokwiBreadboardDiagram().text(BreadboardSceneMaker().make(self.layout))
        self.assertEqual(once, drawing.WokwiBreadboardDiagram().text(BreadboardSceneMaker().make(sheet._plan_layout(xiao_read()))))

    def test_the_drawing_keeps_the_bytes_wokwi_showed(self):
        # The screenshot in docs/discovery/2026-10-16-p267-wokwi-holes/ shows exactly these bytes (P267, PR #303).
        # A refactor must not move a part by a rounding step: P270 changes the units inside, never the file.
        with in_store():
            text = drawing_text(XIAO / "requirements.json")
        self.assertEqual(hashlib.sha256(text.encode()).hexdigest(),
                         # P953: the three ground jumpers go to the bottom - rail (bn.6, bn.14, bn.10); no part moved
                         "51af5c2905f30b678888b241a52dd115a7a7ad142cde56ce2929b6498b0cb528")

    def test_every_hole_named_exists_on_a_half_board(self):
        drawn = json.loads(drawing.WokwiBreadboardDiagram().text(BreadboardSceneMaker().make(self.layout)))
        names = {"bb1:" + hole.name for hole in GEOMETRY.surface.holes}
        for wire in drawn["connections"]:
            self.assertLessEqual(set(wire[:2]), names)


def record_inputs(read, surface=None, board=None):
    """(geometry, catalog) for a board drawn from its record on the full-size surface, as the build gives the planner;
    `board` is a changed copy of the build's board record, `surface` another breadboard."""
    board = board or read.built.board
    part_px, _ = part_shape.find_part_px(board)
    geometry = GEOMETRY.with_part(board["wokwi_part_type"], part_px).with_surface(surface or drawing.Surface.load_full())
    return geometry, drawing_catalog.describe_parts(read, GEOMETRY)


class TheGeometryCopiesTest(unittest.TestCase):
    def test_with_part_returns_a_copy_and_leaves_the_original_alone(self):
        before = json.dumps(GEOMETRY.data, sort_keys=True)
        copied = GEOMETRY.with_part("board-x", {"size": [1, 1], "center": [0, 0], "covers_holes": False, "pins": {}})
        self.assertEqual(copied.part("board-x")["size"], [1, 1])
        self.assertIsNot(copied, GEOMETRY)
        self.assertEqual(json.dumps(GEOMETRY.data, sort_keys=True), before)
        with self.assertRaises(NotDrawnError) as refused:
            GEOMETRY.part("board-x")
        self.assertEqual((refused.exception.code, refused.exception.subject), ("no_pin_position", "board-x"))

    def test_with_surface_returns_a_copy_with_other_holes(self):
        full = drawing.Surface.load_full()
        copied = GEOMETRY.with_surface(full)
        self.assertEqual((copied.surface.type, GEOMETRY.surface.type), ("spark-breadboard-full", "wokwi-breadboard-half"))
        self.assertEqual((len(full.terminal), full.rails, full.pitch), (630, ["tp", "tn", "bp", "bn"], 9.6))
        self.assertEqual(len(GEOMETRY.surface.terminal), 300)


class TheRecordBoardLayoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with in_store():
            cls.read = sheet._read_build(RECORD_BOARD / "requirements.json")
        cls.geometry, cls.catalog = record_inputs(cls.read)
        cls.layout = drawing.BreadboardPlanner(cls.geometry, cls.catalog).plan(cls.read.steps)

    def test_the_board_sits_in_rows_b_and_i_so_a_and_j_stay_free(self):
        board = self.layout.parts[0]
        self.assertEqual(board.id, "board")
        self.assertEqual({hole.name.split(".")[1] for hole in board.holes.values()}, {"b", "i"})
        self.assertEqual((min(h.column for h in board.holes.values()), max(h.column for h in board.holes.values())), (6, 23))

    def test_the_layout_holds_the_geometry_it_was_planned_on(self):
        self.assertIs(self.layout.geometry, self.geometry)
        self.assertEqual(self.layout.breadboard, "spark-breadboard-full")

    def test_every_pin_lies_within_1_5_px_of_its_hole(self):
        for part in self.layout.parts:
            part_px = self.geometry.part(part.type)
            turned = rotate(part_px["pins"], part_px["center"], part.rotate)
            for pin, hole in part.holes.items():
                x, y = turned[pin]
                self.assertLessEqual(abs(part.left + x - hole.x), 1.5, (part.id, pin))
                self.assertLessEqual(abs(part.top + y - hole.y), 1.5, (part.id, pin))

    def test_a_jumper_in_a_board_pin_s_row_takes_the_free_hole_beside_the_body(self):
        # the body covers the holes toward the gap, so the one hole a pin keeps is the far one: row a or row j
        board_groups = {hole.group for hole in self.layout.parts[0].holes.values()}
        ends = [hole for jumper in self.layout.jumpers for hole in (jumper.one, jumper.other) if hole.group in board_groups]
        self.assertGreaterEqual(len(ends), 1)
        self.assertEqual({hole.name.split(".")[1] for hole in ends} - {"a", "j"}, set())

    def test_five_jumpers_and_the_same_bytes_twice(self):
        # P953: ground goes through the - rail, one jumper per end (it was 4, the LED's K row holding the point)
        self.assertEqual(len(self.layout.jumpers), 5)
        again = drawing.BreadboardPlanner(*record_inputs(self.read)).plan(self.read.steps)
        self.assertEqual(again._replace(geometry=None), self.layout._replace(geometry=None))

    def test_one_hole_fewer_refuses_the_board(self):
        # a and j are taken everywhere but columns 44 to 61, which the board fills exactly; take one more a or j
        # hole in the middle of them and the pin there has no free hole left. (P953's review: a body may not reach past
        # the board's last column, so the board's USB end, two columns past its last pin, ends in column 63.)
        geometry, catalog = record_inputs(self.read)
        placement = drawing.FirstFitPartPlacement(geometry)

        def place(also_taken):
            ledger = HoleLedger(geometry.surface)
            for hole in geometry.surface.terminal:
                if hole.name.split(".")[1] in "aj" and (not 44 <= hole.column <= 61 or hole.name in also_taken):
                    ledger.claim(hole, "taken")
            return placement.place("board", catalog["board"], ledger)

        self.assertEqual(min(h.column for h in place(()).holes.values()), 44)
        for taken in ("53t.a", "53b.j"):
            with self.subTest(taken=taken), self.assertRaises(NotDrawnError) as refused:
                place((taken,))
            self.assertEqual((refused.exception.code, refused.exception.subject), ("no_hole_left", "board"))

    def test_a_pull_up_through_a_second_resistor_draws_with_the_leg_in_the_jumper_s_row(self):
        # D3 pulled up to 3V3 by R2, run in memory: the resistor's leg joins the row of the jumper from D3, and never the
        # row of the board's own D3 pin, so that pin keeps its one free hole for the jumper
        points = list(self.read.steps.points)
        d3 = next(i for i, point in enumerate(points) if any(end.name == "board D3" for end in point.ends))
        first = wiring_steps.End(wiring_steps.RESISTOR, "R2", "R2 end 1", "R2, end 1", "1", "pull-up on", "10kΩ")
        second = wiring_steps.End(wiring_steps.RESISTOR, "R2", "R2 end 2", "R2, end 2", "2", "pull-up on", "10kΩ")
        points[d3] = wiring_steps.StepPoint(points[d3].ends + [first], None, False)
        points.append(wiring_steps.StepPoint(
            [wiring_steps.End("board", wiring_steps.THE_BOARD, "board 3V3", "board 3V3", "3V3"), second],
            None, False))
        steps = wiring_steps.BreadboardSteps(self.read.steps.placed, points)
        catalog = dict(self.catalog, R2=drawing.DrawnPart("wokwi-resistor", {"value": "10000"}, {"1": "1", "2": "2"}))
        layout = drawing.BreadboardPlanner(self.geometry, catalog).plan(steps)
        board_groups = {hole.group for hole in layout.parts[0].holes.values()}
        resistor = next(part for part in layout.parts if part.id == "R2")
        self.assertEqual({hole.group for hole in resistor.holes.values()} & board_groups, set())
        self.assertGreaterEqual(len(layout.jumpers), 3)

    def test_a_board_whose_rows_are_an_inch_apart_is_refused(self):
        # 25.4 mm is ten pitches, so the pins land in rows b and j and no row beside them is free
        board = json.loads(json.dumps(self.read.built.board))
        board["physical"]["header"]["row_spacing_mm"] = 25.4
        board["physical"]["width_mm"] = 27.94
        with self.assertRaises(NotDrawnError) as refused:
            drawing.BreadboardPlanner(*record_inputs(self.read, board=board)).plan(self.read.steps)
        self.assertEqual((refused.exception.code, refused.exception.subject), ("no_hole_left", "board"))

    def test_a_30_column_surface_fits_the_button_and_refuses_the_led(self):
        full = json.loads((ROOT / "data" / "breadboards.json").read_text())["full"]
        thirty = drawing.Surface(dict(full, columns=30))
        with self.assertRaises(NotDrawnError) as refused:
            drawing.BreadboardPlanner(*record_inputs(self.read, thirty)).plan(self.read.steps)
        self.assertEqual((refused.exception.code, refused.exception.subject), ("no_hole_left", "LedRed5mm"))
        placed = drawing.BreadboardPlanner(*record_inputs(self.read)).plan(self.read.steps).parts
        button = next(part for part in placed if part.id == "TactileButton")
        # P953: the board's body ends in 25 and four columns stay free, so the button's body starts in 30
        self.assertEqual((min(h.column for h in button.holes.values()), max(h.column for h in button.holes.values())), (31, 33))


EPAPER = ROOT / "tests" / "data" / "breadboard" / "epaper"


def epaper_inputs(read):
    """(geometry, catalog) of the e-paper fixture as the build gives the planner: the module's part_px from its physical
    block, the header on the back, 8 pads 2.54 mm apart, the first 34.5 mm from the left edge seen from the back, half
    a pitch from the top edge. Its labels are the printed ones, so the pin DC is the pad D/C (P945)."""
    return sheet._drawing_inputs(read)


class AModuleDrawnFromItsRecordTest(unittest.TestCase):
    """P945: the walk's e-paper, whose record has a physical block and no Wokwi part, through the real planner beside the
    FireBeetle on the full breadboard."""

    @classmethod
    def setUpClass(cls):
        with in_store():
            cls.read = sheet._read_build(EPAPER / "requirements.json")
        cls.geometry, cls.catalog = epaper_inputs(cls.read)
        cls.layout = drawing.BreadboardPlanner(cls.geometry, cls.catalog).plan(cls.read.steps)
        cls.module = next(part for part in cls.layout.parts if part.id == "Epaper2in9BwrMhEtLive")

    def test_its_8_holes_lie_on_one_letter_one_pitch_apart_seen_from_the_front(self):
        holes = self.module.holes
        self.assertEqual(len(holes), 8)
        # P953: a tall module takes the outermost row, so its body hangs off the board's bottom edge
        self.assertEqual({hole.name.split(".")[1] for hole in holes.values()}, {"j"})
        # seen from the front, the back's left end (VCC) is on the right, and Busy is on the left
        order = sorted(holes, key=lambda pin: holes[pin].x)
        self.assertEqual(order, ["Busy", "Reset", "D/C", "CS", "SCLK", "SDI", "GND", "VCC"])
        xs = [holes[pin].x for pin in order]
        self.assertEqual({round(right - left, 3) for left, right in zip(xs, xs[1:])}, {9.6})

    def test_the_pin_dc_finds_its_printed_pad_d_c(self):
        end = next(end for point in self.read.steps.points for end in point.ends if end.component == "Epaper2in9BwrMhEtLive"
                   and end.pin == "DC")
        self.assertEqual(drawing.end_pin(end, self.catalog), "D/C")
        self.assertEqual(drawing.end_group(end, {part.id: part for part in self.layout.parts}, self.catalog),
                         self.module.holes["D/C"].group)

    def test_each_pin_s_group_keeps_a_free_hole_for_its_jumper(self):
        groups = {hole.group for hole in self.module.holes.values()}
        ends = {hole.group for jumper in self.layout.jumpers for hole in (jumper.one, jumper.other)}
        self.assertEqual(groups, ends & groups)
        self.assertEqual(len(groups), 8)

    def test_the_catalog_maps_each_pin_to_its_printed_pad_and_the_geometry_knows_the_module(self):
        drawn = self.catalog["Epaper2in9BwrMhEtLive"]
        self.assertEqual((drawn.type, drawn.pins["DC"], drawn.pins["RESET"], drawn.pins["VCC"]),
                         ("spark-module-epaper-2in9-bwr-mh-et-live", "D/C", "Reset", "VCC"))
        self.assertEqual(self.geometry.part(drawn.type)["labels"], "into-body")
        self.assertEqual(self.catalog.undrawn, {})

    def test_the_sheet_writes_the_picture_and_no_wokwi_diagram(self):
        import shutil
        project = Path(tempfile.mkdtemp()) / "epaper"
        shutil.copytree(EPAPER, project)
        with in_store():
            written = sheet.write(project / "requirements.json", project / "breadboard.md")
        self.assertEqual([path.name for path, _ in written.drawings], ["breadboard.svg"])
        self.assertEqual([(one.path.name, one.code) for one in written.not_written], [("breadboard.json", "no_wokwi_part")])


WALK = ROOT / "tests" / "data" / "breadboard" / "walk-c6"


def planned(fixture):
    """The layout the build plans for one fixture of tests/data/breadboard, with an empty store."""
    with in_store():
        return sheet._plan_layout(sheet._read_build(fixture / "requirements.json"))


def body_columns(layout):
    """[(part id, first column, last column)] of each part's body, left to right."""
    spans = []
    for part in layout.parts:
        columns = spacing.BodyBox.of(part, layout.geometry.part(part.type)).columns(layout.geometry.surface)
        spans.append((part.id, columns[0], columns[-1]))
    return sorted(spans, key=lambda span: span[1])


class TheSpaceBetweenPartsTest(unittest.TestCase):
    """P953 (#1359): the PO's "leave space in between elements": at least 4 free columns between two part bodies, a tall
    module hanging off the outer edge of the breadboard, and a sheet that says so when the board is too full."""

    @classmethod
    def setUpClass(cls):
        cls.walk = planned(WALK)
        cls.epaper = next(part for part in cls.walk.parts if part.id == "Epaper2in9BwrMhEtLive")

    def test_the_body_box_of_a_turned_part_is_its_four_corners_turned(self):
        part_px = {"size": [40, 10], "center": [20, 5], "pins": {}}
        flat = drawing.PlacedPart("x", "t", {}, 100, 50, 0, {})
        self.assertEqual(tuple(spacing.BodyBox.of(flat, part_px)), (100, 50, 140, 60))
        turned = flat._replace(rotate=90)
        self.assertEqual(tuple(spacing.BodyBox.of(turned, part_px)), (115, 35, 125, 75))
        self.assertEqual(spacing.BodyBox(100, 0, 130, 10).columns(GEOMETRY.surface), [9, 10, 11])

    def test_no_two_bodies_are_closer_than_4_free_columns(self):
        # a resistor whose leg sits in the row of the part it joins is one block with that part, so it is left out
        for fixture in (WALK, RECORD_BOARD):
            layout = planned(fixture)
            groups = collections.Counter(hole.group for part in layout.parts for hole in part.holes.values())
            joined = {part.id for part in layout.parts if any(groups[hole.group] > 1 for hole in part.holes.values())
                      and part.type == "wokwi-resistor"}
            spans = [span for span in body_columns(layout) if span[0] not in joined]
            with self.subTest(fixture=fixture.name):
                self.assertGreaterEqual(len(spans), 2)
                for (one, _, last), (other, first, _) in zip(spans, spans[1:]):
                    self.assertGreaterEqual(first - last - 1, 4, (one, other))

    def test_a_resistor_joined_to_a_part_keeps_that_part_s_space(self):
        # R1's leg is in the LED's row; turned the other way it would fill the free columns after the button
        spans = {part: (first, last) for part, first, last in body_columns(planned(RECORD_BOARD))}
        self.assertGreaterEqual(spans["R1"][0] - spans["TactileButton"][1] - 1, 4)

    def test_a_body_that_reaches_left_of_its_pins_keeps_the_space(self):
        # the refuter's numbers: the C6's body covers columns 2 to 25, so the e-paper's body starts at 30, and its first
        # pin (Busy) is 13 columns right of that, in 42. Its body ends 4 px short of column 63.
        self.assertEqual(body_columns(self.walk), [("board", 2, 25), ("Epaper2in9BwrMhEtLive", 30, 62)])
        self.assertEqual((self.epaper.holes["Busy"].column, self.epaper.holes["VCC"].column), (42, 49))

    def test_a_tall_module_hangs_off_the_outer_edge_and_covers_no_terminal_hole_above_its_row(self):
        # its header is half a pitch from its body's edge, so the body covers row j beside its pins and no row above
        surface = self.walk.geometry.surface
        box = spacing.BodyBox.of(self.epaper, self.walk.geometry.part(self.epaper.type))
        self.assertEqual({hole.name.split(".")[1] for hole in self.epaper.holes.values()}, {"j"})
        self.assertGreater(box.bottom, max(hole.y for hole in surface.holes))
        under = {hole.name.split(".")[1] for hole in surface.terminal
                 if box.left < hole.x < box.right and box.top < hole.y < box.bottom}
        self.assertEqual(under, {"j"})

    def test_a_board_with_two_rows_of_pins_keeps_its_place_across_the_gap(self):
        board = self.walk.parts[0]
        self.assertEqual({hole.name.split(".")[1] for hole in board.holes.values()}, {"b", "i"})

    def test_the_rail_holes_under_a_body_are_taken_and_do_not_refuse_its_place(self):
        # a rail hole has no column (0), so "past the last part" never refuses it (the refuter's defect)
        geometry, catalog = sheet._drawing_inputs(self._read())
        ledger = HoleLedger(geometry.surface)
        placed = drawing.FirstFitPartPlacement(geometry).place("Epaper2in9BwrMhEtLive", catalog["Epaper2in9BwrMhEtLive"],
                                                               ledger, after=29)
        rails = sorted(int(name.split(".")[1]) for name, by in ledger.taken.items()
                       if name.startswith(("bp.", "bn.")) and by == "Epaper2in9BwrMhEtLive, which covers it")
        self.assertEqual(placed.holes["Busy"].column, 42)
        # rail hole n lies in column n + 1 + (n - 1) // 5, so holes 25 to 50 of both bottom rails lie in columns 30 to 60
        self.assertEqual((len(rails) // 2, rails[0], rails[-1]), (26, 25, 50))

    def test_all_end_holes_of_one_header_are_in_one_row_unless_taken(self):
        groups = {hole.group for hole in self.epaper.holes.values()}
        ends = [hole for jumper in self.walk.jumpers for hole in (jumper.one, jumper.other) if hole.group in groups]
        rows = collections.Counter(hole.name.split(".")[1] for hole in ends)
        # P953: VCC's two jumpers (3V3 and 3V3_2) go to the + rail now, so each pin's row holds one end, in row f
        self.assertEqual(dict(rows), {"f": 8})

    def test_two_jumpers_into_one_row_take_the_hole_toward_their_other_end(self):
        # the jumper from row a takes the upper hole and the one from row j the lower, so their legs never overlap: the
        # walk's two jumpers into the e-paper's VCC before P953, handed the wrong holes; a rail's holes are not handed out
        holes = {hole.name: hole for hole in drawing.Surface.load_full().holes}
        jumpers = [drawing.Jumper(holes["7b.j"], holes["49b.f"], 3), drawing.Jumper(holes["11t.a"], holes["49b.g"], 4),
                   drawing.Jumper(holes["9b.j"], holes["bp.7"], 5), drawing.Jumper(holes["12t.a"], holes["bp.3"], 6)]
        ends = {jumper.step: (jumper.one.name, jumper.other.name) for jumper in spacing.ends_toward_their_runs(jumpers)}
        self.assertEqual(ends, {3: ("7b.j", "49b.g"), 4: ("11t.a", "49b.f"), 5: ("9b.j", "bp.7"), 6: ("12t.a", "bp.3")})

    def test_a_full_breadboard_places_the_part_closer_and_says_so(self):
        full = json.loads((ROOT / "data" / "breadboards.json").read_text())["full"]
        with in_store():
            read = sheet._read_build(RECORD_BOARD / "requirements.json")
        # on 40 columns the button still keeps its 4 columns from the board, and the LED does not: it goes in by the old
        # rule, 2 columns after the button's last pin
        layout = drawing.BreadboardPlanner(*record_inputs(read, drawing.Surface(dict(full, columns=40)))).plan(read.steps)
        self.assertEqual(layout.crowded, ("LedRed5mm",))
        with in_store():
            crowded = sheet.sheet(RECORD_BOARD / "requirements.json", read=read,
                                  planned=sheet.PlannedLayout(layout, None, [], layout, (), sheet.SCENE_MAKER.make(layout)))
            spaced = sheet.sheet(RECORD_BOARD / "requirements.json", read=read, planned=sheet._planned_alone(read))
        self.assertEqual(crowded.count("The parts are closer than 4 columns because the breadboard is full."), 1)
        self.assertNotIn("closer than", spaced)

    def test_a_body_that_would_reach_past_the_board_s_last_column_is_named_crowded_or_refused(self):
        # the review of PR #1369: only the body's left side was checked, so on a shorter board the e-paper's body lay past
        # the board's right end, and nothing said so. Its spaced place needs 63 columns: on 60 it goes in by the old
        # rule, named crowded and on the board; on 58 no place is left and the plan refuses it.
        full = json.loads((ROOT / "data" / "breadboards.json").read_text())["full"]
        read = self._read()
        geometry, catalog = sheet._drawing_inputs(read)
        for columns in (60, 58):
            surface = drawing.Surface(dict(full, columns=columns))
            planner = drawing.BreadboardPlanner(geometry.with_surface(surface), catalog)
            with self.subTest(columns=columns):
                if columns == 58:
                    with self.assertRaises(NotDrawnError) as refused:
                        planner.plan(read.steps)
                    self.assertEqual((refused.exception.code, refused.exception.subject),
                                     ("no_hole_left", "Epaper2in9BwrMhEtLive"))
                    continue
                layout = planner.plan(read.steps)
                epaper = next(part for part in layout.parts if part.id == "Epaper2in9BwrMhEtLive")
                box = spacing.BodyBox.of(epaper, layout.geometry.part(epaper.type))
                self.assertEqual(layout.crowded, ("Epaper2in9BwrMhEtLive",))
                self.assertLessEqual(box.right, max(hole.x for hole in surface.terminal) + surface.pitch / 2)

    def test_a_free_row_for_a_jumper_lies_right_of_the_space_or_by_the_old_rule_when_none_is_left(self):
        geometry = GEOMETRY.with_surface(drawing.Surface.load_full())
        room = spacing.BodySpacing(geometry)
        room.after, room.close = 50, 40
        self.assertEqual(room.free_after(HoleLedger(geometry.surface)), 50)
        room.after = 63  # no column lies right of the last one
        self.assertEqual(room.free_after(HoleLedger(geometry.surface)), 40)

    def _read(self):
        with in_store():
            return sheet._read_build(WALK / "requirements.json")


class TheRailSeatingTest(unittest.TestCase):
    """P953: power and ground go through the rails. A point's mark takes the rail of its sign on the side that holds most
    of its ends, and each of its ends runs a jumper to a free hole of that rail that no part's body lies over."""

    #: Every fixture the planner draws.
    DRAWN = (WALK, XIAO, RECORD_BOARD, EPAPER)

    @classmethod
    def setUpClass(cls):
        cls.layouts = {fixture.name: planned(fixture) for fixture in cls.DRAWN}

    def rail_jumpers(self, name):
        return {jumper.step: (jumper.one.name, jumper.other.name) for jumper in self.layouts[name].jumpers
                if not jumper.other.column}

    def test_power_takes_the_plus_rail_of_the_side_of_most_ends(self):
        surface = drawing.Surface.load_full()
        self.assertEqual(rails.RailSeating(surface).group("3V3", "+", ["b", "t", "b"]), "bp")
        # the walk: board 3V3 in row j, 3V3_2 in row a, the e-paper's VCC in row j: all three to the bottom + rail
        walk = self.rail_jumpers("walk-c6")
        self.assertEqual({step: one.split(".")[0] for step, (_, one) in walk.items()},
                         {3: "bp", 4: "bp", 5: "bp", 8: "bn", 9: "bn"})

    def test_a_tie_takes_the_first_end_s_side(self):
        surface = drawing.Surface.load_full()
        self.assertEqual(rails.RailSeating(surface).group("3V3", "+", ["t", "b"]), "tp")
        self.assertEqual(rails.RailSeating(surface).group("GND", "-", ["b", "t"]), "bn")
        # the e-paper fixture: board 3V3 in row a, the e-paper's VCC in row f, so the top + rail
        self.assertEqual({one.split(".")[0] for _, one in self.rail_jumpers("epaper").values()}, {"tp", "tn"})

    def test_a_second_power_mark_takes_the_other_side(self):
        seating = rails.RailSeating(drawing.Surface.load_full())
        self.assertEqual([seating.group("3V3", "+", ["b"]), seating.group("5V", "+", ["b"]),
                          seating.group("GND", "-", ["t"])], ["bp", "tp", "tn"])

    def test_a_third_power_mark_is_not_drawn_yet(self):
        seating = rails.RailSeating(drawing.Surface.load_full())
        seating.group("3V3", "+", ["b"])
        seating.group("5V", "+", ["t"])
        self.assertIsNone(seating.group("VBAT", "+", ["b"]))
        # the planner says so by name: the XIAO on a half board whose only rails are + rails, so GND has none
        read = xiao_read()
        surface = drawing.Surface(dict(GEOMETRY.data["breadboard"], rails_y={"tp": 12.3, "bp": 186.3}))
        planner = drawing.BreadboardPlanner(GEOMETRY.with_surface(surface), drawing_catalog.describe_parts(read, GEOMETRY))
        with self.assertRaises(NotDrawnError) as refused:
            planner.plan(read.steps)
        self.assertEqual(str(refused.exception), "GND goes on a free - rail, and none is left")
        self.assertEqual((refused.exception.code, refused.exception.subject), ("not_drawn_yet", "GND"))

    def test_each_rail_end_has_a_jumper_to_a_free_rail_hole(self):
        # each rail hole a jumper takes is taken once, and no part's body lies over it or within half a pitch of it
        # (the walk after PR 1: rail holes under a body)
        for name, layout in self.layouts.items():
            with self.subTest(name):
                rails = [jumper.other for jumper in layout.jumpers if not jumper.other.column]
                self.assertTrue(rails)
                self.assertEqual(len({hole.name for hole in rails}), len(rails))
                half = layout.geometry.surface.pitch / 2
                for part in layout.parts:
                    box = spacing.BodyBox.of(part, layout.geometry.part(part.type))
                    under = [hole.name for hole in rails if box.left - half < hole.x < box.right + half
                             and box.top - half < hole.y < box.bottom + half]
                    self.assertEqual(under, [], part.id)
        self.assertEqual(self.rail_jumpers("walk-c6"), {3: ("7b.j", "bp.5"), 4: ("11t.a", "bp.9"), 5: ("49b.f", "bp.23"),
                                                        8: ("9b.j", "bn.7"), 9: ("48b.f", "bn.23")})

    def test_a_rail_hole_reads_top_plus_rail_hole_n(self):
        self.assertEqual(drawing.hole_label(drawing.Hole("tp.3", 0, 0, "tp", 0)), "top + rail, hole 3")
        self.assertEqual(drawing.hole_label(drawing.Hole("bn.12", 0, 0, "bn", 0)), "bottom - rail, hole 12")
        with in_store():
            read = sheet._read_build(WALK / "requirements.json")
        holes = drawing.StepHoles.of(self.layouts["walk-c6"], read.steps)
        self.assertEqual(holes.get(3), "from j7 to bottom + rail, hole 5")

    def test_a_resistor_leg_on_a_rail_is_not_drawn_yet(self):
        # FirstFitPartPlacement pins a resistor's leg in a row of holes only, so a leg on a rail is refused by name
        read = xiao_read()
        ground = next(point for point in read.steps.points if point.rail)
        leg = next(end for point in read.steps.points for end in point.ends if end.name == "R1 end 2")
        points = [point for point in read.steps.points if point is not ground and leg not in point.ends]
        steps = wiring_steps.BreadboardSteps(read.steps.placed, points + [ground._replace(ends=ground.ends + [leg])])
        planner = drawing.BreadboardPlanner(GEOMETRY, drawing_catalog.describe_parts(read, GEOMETRY))
        with self.assertRaisesRegex(NotDrawnError, "R1 has a leg on the GND rail") as refused:
            planner.plan(steps)
        self.assertEqual((refused.exception.code, refused.exception.subject), ("not_drawn_yet", "R1"))

    def test_drawn_nets_are_empty_on_every_fixture(self):
        for fixture in self.DRAWN:
            with self.subTest(fixture.name), in_store():
                planned_once = sheet._plan_once(sheet._read_build(fixture / "requirements.json"))
                self.assertEqual((planned_once.stopped, planned_once.differs), (None, []))


class AModuleWithNoDrawingFactTest(unittest.TestCase):
    """P945: a module with neither a Wokwi part nor a physical block stops the drawing, and names its record."""

    def test_the_refusal_names_the_component_and_the_record(self):
        with in_store():
            read = sheet._read_build(EPAPER / "requirements.json")
        del read.built.parts[0]["physical"]
        geometry, catalog = sheet._drawing_inputs(read)
        self.assertEqual(catalog.undrawn, {"Epaper2in9BwrMhEtLive": "epaper-2in9-bwr-mh-et-live"})
        with self.assertRaisesRegex(NotDrawnError, "nothing says how to draw Epaper2in9BwrMhEtLive: its record has no "
                                                   "Wokwi part and no physical block") as refused:
            drawing.BreadboardPlanner(geometry, catalog).plan(read.steps)
        self.assertEqual((refused.exception.code, refused.exception.subject, refused.exception.record),
                         ("no_drawing_fact", "Epaper2in9BwrMhEtLive", "epaper-2in9-bwr-mh-et-live"))

    def test_a_physical_block_that_lacks_a_field_stops_the_plan_by_that_field(self):
        with in_store():
            read = sheet._read_build(EPAPER / "requirements.json")
        del read.built.parts[0]["physical"]["header"]["face"]
        planned = sheet._plan_once(read)
        self.assertEqual((planned.stopped.code, planned.stopped.subject), ("no_header_fact", "physical.header.face"))


class TheWokwiLineNamesTheCauseTest(unittest.TestCase):
    """P947: the line that says why no Wokwi diagram is written names each drawn part that Wokwi has no part for, the
    board or a module, by the name the picture gives it."""

    def test_the_e_paper_names_the_board_and_the_module(self):
        with in_store():
            read = sheet._read_build(EPAPER / "requirements.json")
        layout = drawing.BreadboardPlanner(*epaper_inputs(read)).plan(read.steps)
        refused = drawing.WokwiBreadboardDiagram().why_not_written(layout)
        self.assertEqual((refused.code, refused.subject, refused.why),
                         ("no_wokwi_part", None, "Wokwi has no part for the board and e-paper"))

    def test_the_firebeetle_alone_names_the_board(self):
        with in_store():
            read = sheet._read_build(RECORD_BOARD / "requirements.json")
        layout = drawing.BreadboardPlanner(*record_inputs(read)).plan(read.steps)
        self.assertEqual(drawing.WokwiBreadboardDiagram().why_not_written(layout).why,
                         "Wokwi has no part for the board")

    def test_a_wokwi_board_with_a_module_drawn_from_its_record_names_the_module_alone(self):
        geometry = GEOMETRY.with_part("spark-module-x", {"wokwi_part": False, "name": "e-paper", "pins": {}})
        geometry = geometry.with_part("spark-module-y", {"wokwi_part": False, "pins": {}})
        parts = [drawing.PlacedPart("board", "board-xiao-esp32-c6", {}, 0, 0, 0, {}),
                 drawing.PlacedPart("Epaper", "spark-module-x", {}, 0, 0, 0, {}),
                 drawing.PlacedPart("Led", "wokwi-led", {}, 0, 0, 0, {}),
                 drawing.PlacedPart("Sensor", "spark-module-y", {}, 0, 0, 0, {})]
        layout = drawing.BreadboardLayout("wokwi-breadboard-half", parts, [], geometry)
        self.assertEqual(drawing.WokwiBreadboardDiagram().why_not_written(layout).why,
                         "Wokwi has no part for e-paper and Sensor")
        self.assertIsNone(drawing.WokwiBreadboardDiagram().why_not_written(
            drawing.BreadboardLayout("wokwi-breadboard-half", [parts[0], parts[2]], [], geometry)))

    def test_the_sheet_says_the_same_cause(self):
        with in_store():
            read = sheet._read_build(EPAPER / "requirements.json")
        self.assertIn("There is no Wokwi diagram: Wokwi has no part for the board and e-paper. Use the picture.",
                      sheet.sheet(EPAPER / "requirements.json", read=read, planned=sheet._planned_alone(read)))


class EachStepNamesItsHolesTest(unittest.TestCase):
    """P945: the step list names the holes each step uses in the planned layout, read as a person reads a breadboard."""

    def test_the_e_paper_s_steps_name_their_holes_in_the_order_the_step_runs(self):
        with in_store():
            read = sheet._read_build(EPAPER / "requirements.json")
        layout = drawing.BreadboardPlanner(*epaper_inputs(read)).plan(read.steps)
        lines = wiring_steps.NumberedList().render(read.steps, drawing.StepHoles.of(layout, read.steps))
        self.assertEqual(lines[:5], [
            "1. Put the board in the breadboard, each pin in its own row. Holes: b6 to b23, i10 to i23.",
            "2. Put e-paper in the breadboard, each pin in its own row. Holes: j42 to j49.",
            "3. Run a jumper from board 3V3 to a free + rail. Mark it 3V3. Holes: from a7 to top + rail, hole 5.",
            "4. Run a jumper from the row of e-paper VCC (back up, header at the top: the left end pin, above the label "
            "VCC) to the 3V3 rail. Holes: from f49 to top + rail, hole 40.",
            "5. Run a jumper from board A5 to the row of e-paper D/C. Holes: from j14 to f44."])
        self.assertEqual(len(lines), 12)  # P953: power and ground go through the rails, one jumper per end
        self.assertTrue(all(" Holes: " in line for line in lines))

    def test_a_resistor_s_setup_and_its_joined_leg_name_their_holes(self):
        read = xiao_read()
        layout = drawing.BreadboardPlanner(GEOMETRY, drawing_catalog.describe_parts(read, GEOMETRY)).plan(read.steps)
        holes = drawing.StepHoles.of(layout, read.steps)
        resistor = next(part for part in layout.parts if part.id == "R1")
        seated = list(read.steps.anchored())
        for number, step in enumerate(seated, 1):
            if step.act == "setup" and step.subject.kind == "resistor":  # the leg the step puts in, not both
                self.assertEqual(holes.get(number), drawing.hole_label(resistor.holes[step.subject.pin]))
            if step.act == "join" and step.subject.kind == "resistor":
                self.assertEqual(holes.get(number), drawing.hole_label(resistor.holes[step.subject.pin]))
        self.assertTrue(any(step.subject.kind == "resistor" for step in seated if step.act in ("setup", "join")))

    def test_a_range_covers_only_neighbouring_columns(self):
        holes = [drawing.Hole(name, 0, 0, name.split(".")[0], int(name.split("t")[0]))
                 for name in ("14t.e", "12t.e", "12t.j", "14t.j", "15t.j", "16t.j")]
        self.assertEqual(drawing.StepHoles._span(holes), "e12, e14, j12, j14 to j16")

    def test_a_hole_reads_letter_then_column_and_a_rail_by_its_side_and_sign(self):
        self.assertEqual(drawing.hole_label(drawing.Hole("41t.e", 0, 0, "41t", 41)), "e41")
        # P953: a rail hole reads as a person finds it (it was its Wokwi name, tp.3); a rail of no known name keeps it
        self.assertEqual(drawing.hole_label(drawing.Hole("tp.3", 0, 0, "tp", 0)), "top + rail, hole 3")
        self.assertEqual(drawing.hole_label(drawing.Hole("xr.3", 0, 0, "xr", 0)), "xr.3")

    def test_with_no_layout_the_steps_read_as_before(self):
        read = xiao_read()
        self.assertEqual(wiring_steps.NumberedList().render(read.steps, None), wiring_steps.NumberedList().render(read.steps))
        self.assertFalse(any(" Holes: " in line for line in wiring_steps.NumberedList().render(read.steps)))


class AnOldDrawingTest(unittest.TestCase):
    def test_write_removes_a_drawing_an_earlier_build_left_when_this_one_cannot_be_drawn(self):
        import shutil
        project = Path(tempfile.mkdtemp()) / "motor"
        shutil.copytree(ROOT / "tests" / "data" / "breadboard" / "motor", project)
        (project / "breadboard.json").write_text("{}")
        with in_store():
            written = sheet.write(project / "requirements.json", project / "breadboard.md")
        self.assertEqual(written.drawings, [])
        # the board is drawn from its record now, so the plan stops at the module nothing says how to draw (P691)
        self.assertEqual([(one.path.name, one.code, one.subject) for one in written.not_written],
                         [("breadboard.json", "no_drawing_fact", "L9110sModule"),
                          ("breadboard.svg", "no_drawing_fact", "L9110sModule")])
        self.assertFalse((project / "breadboard.json").exists())


class ABoardWhoseRecordLacksAFactIsRefusedWithItsCodeTest(unittest.TestCase):
    def test_write_says_which_field_is_missing_for_each_drawing_and_writes_neither(self):
        import shutil
        project = Path(tempfile.mkdtemp()) / "headerless"
        shutil.copytree(RECORD_BOARD, project)
        board = json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())
        del board["physical"]["header"]
        (project / "boards").mkdir(exist_ok=True)
        (project / "boards" / "firebeetle2-esp32s3.json").write_text(json.dumps(board))
        (project / "boards" / "active.json").write_text(json.dumps({"schema": 1, "board": "firebeetle2-esp32s3"}))
        (project / "breadboard.svg").write_text("<svg/>")
        with in_store():
            written = sheet.write(project / "requirements.json", project / "breadboard.md")
        self.assertEqual([(one.path.name, one.code, one.subject) for one in written.not_written],
                         [("breadboard.json", "no_header_fact", "physical.header"), ("breadboard.svg", "no_header_fact", "physical.header")])
        self.assertEqual(written.drawings, [])
        self.assertFalse((project / "breadboard.svg").exists())


class AXiaoBuildOverAnOldDrawingTest(unittest.TestCase):
    def test_a_board_drawn_from_its_record_removes_an_old_breadboard_json_and_names_no_move_not_kept(self):
        import shutil
        project = Path(tempfile.mkdtemp()) / "fire"
        shutil.copytree(RECORD_BOARD, project)
        # an earlier XIAO build left this one behind; the new build does not write a Wokwi diagram
        with in_store():
            shutil.copy(XIAO / "requirements.json", project / "requirements.json")
            shutil.copytree(XIAO / "dist", project / "dist", dirs_exist_ok=True)
            shutil.copytree(XIAO / "boards", project / "boards", dirs_exist_ok=True) if (XIAO / "boards").exists() else None
            sheet.write(project / "requirements.json", project / "breadboard.md")
        self.assertTrue((project / "breadboard.json").is_file())
        shutil.rmtree(project / "dist")
        shutil.copytree(RECORD_BOARD / "dist", project / "dist")
        shutil.copy(RECORD_BOARD / "requirements.json", project / "requirements.json")
        shutil.rmtree(project / "boards", ignore_errors=True)
        with in_store():
            written = sheet.write(project / "requirements.json", project / "breadboard.md")
        self.assertEqual(written.not_kept, [])
        self.assertEqual([one.code for one in written.not_written], ["no_wokwi_part"])
        self.assertFalse((project / "breadboard.json").exists())
        self.assertTrue((project / "breadboard.svg").is_file())


class OnePlanPerWriteTest(unittest.TestCase):
    def test_the_sheet_and_every_drawing_come_from_one_plan(self):
        # The tech lead (P270): the sheet planned the layout a second time, so its color line could differ from the
        # drawing's wires.
        import shutil
        project = Path(tempfile.mkdtemp()) / "xiao"
        shutil.copytree(XIAO, project)
        with in_store(), mock.patch.object(sheet, "_plan_layout", wraps=sheet._plan_layout) as planned:
            written = sheet.write(project / "requirements.json", project / "breadboard.md")
        self.assertEqual(planned.call_count, 1)
        self.assertEqual([path.name for path, _ in written.drawings],
                         [renderer.FILE_NAME for renderer in sheet.DRAWING_RENDERERS])


class WhatIsNotDrawnTest(unittest.TestCase):
    def test_a_rail_with_no_sign_is_said_not_drawn(self):
        # P953: power and ground are drawn on their rails; a signal point with too many ends for a row is not, yet
        read = xiao_read()
        rail = wiring_steps.StepPoint(read.steps.points[0].ends, None, True)
        steps = wiring_steps.BreadboardSteps(read.steps.placed, [rail] + read.steps.points[1:])
        planner = drawing.BreadboardPlanner(GEOMETRY, drawing_catalog.describe_parts(read, GEOMETRY))
        with self.assertRaisesRegex(NotDrawnError, "goes on a rail, and a rail with no sign is not drawn yet") as refused:
            planner.plan(steps)
        self.assertEqual(refused.exception.code, "not_drawn_yet")
        self.assertIn(refused.exception.subject, str(refused.exception))

    def test_a_supply_from_off_the_board_is_said_not_drawn(self):
        # The refuter: a supply step was skipped without a word, so the drawing lacked a wire the sheet has.
        read = xiao_read()
        last = read.steps.points[-1]
        supplied = wiring_steps.StepPoint(last.ends, "VBAT", False)
        steps = wiring_steps.BreadboardSteps(read.steps.placed, read.steps.points[:-1] + [supplied])
        planner = drawing.BreadboardPlanner(GEOMETRY, drawing_catalog.describe_parts(read, GEOMETRY))
        with self.assertRaisesRegex(NotDrawnError, "the VBAT supply comes from off the board") as refused:
            planner.plan(steps)
        self.assertEqual((refused.exception.code, refused.exception.subject), ("not_drawn_yet", "VBAT"))

    def test_a_resistor_that_joins_a_later_resistor_s_row_waits_for_it(self):
        # The correctness lens: R2 is set up first, but its other leg joins R1's row, which R1 places later.
        read = xiao_read()
        board_d8 = next(end for point in read.steps.points for end in point.ends if end.name == "board D8")
        led_a = next(end for point in read.steps.points for end in point.ends if end.name == "LedRed5mm A")

        def leg(tag, number):
            return wiring_steps.End(wiring_steps.RESISTOR, tag, "%s end %d" % (tag, number),
                                        "%s, end %d" % (tag, number), str(number))

        points = [wiring_steps.StepPoint([board_d8, leg("R2", 1)], None, False),
                  wiring_steps.StepPoint([leg("R1", 1), leg("R2", 2)], None, False),
                  wiring_steps.StepPoint([led_a, leg("R1", 2)], None, False)]
        steps = wiring_steps.BreadboardSteps(read.steps.placed, points)
        catalog = drawing_catalog.describe_parts(read, GEOMETRY)
        catalog["R2"] = catalog["R1"]
        layout = drawing.BreadboardPlanner(GEOMETRY, catalog).plan(steps)
        self.assertLessEqual({"R1", "R2"}, {part.id for part in layout.parts})

    def leg(self, tag, number):
        return wiring_steps.End(wiring_steps.RESISTOR, tag, "%s end %d" % (tag, number),
                                    "%s, end %d" % (tag, number), str(number))

    def end_named(self, read, name):
        return next(end for point in read.steps.points for end in point.ends if end.name == name)

    def test_a_resistor_whose_both_legs_join_rows_is_said_not_drawn(self):
        read = xiao_read()
        points = [wiring_steps.StepPoint([self.end_named(read, "LedRed5mm A"), self.leg("R1", 1)], None, False),
                  wiring_steps.StepPoint([self.end_named(read, "TactileButton A"), self.leg("R1", 2)], None, False)]
        planner = drawing.BreadboardPlanner(GEOMETRY, drawing_catalog.describe_parts(read, GEOMETRY))
        with self.assertRaisesRegex(NotDrawnError, "both ends of R1 join other rows") as refused:
            planner.plan(wiring_steps.BreadboardSteps(read.steps.placed, points))
        self.assertEqual((refused.exception.code, refused.exception.subject), ("not_drawn_yet", "R1"))

    def test_a_resistor_with_no_leg_joined_goes_right_of_the_parts(self):
        read = xiao_read()
        points = [wiring_steps.StepPoint([self.end_named(read, "board D8"), self.leg("R1", 1)], None, False),
                  wiring_steps.StepPoint([self.end_named(read, "board D10"), self.leg("R1", 2)], None, False)]
        layout = drawing.BreadboardPlanner(GEOMETRY, drawing_catalog.describe_parts(read, GEOMETRY)).plan(
            wiring_steps.BreadboardSteps(read.steps.placed, points))
        parts = {part.id: part for part in layout.parts}
        last = max(hole.column for part in layout.parts if part.id != "R1" for hole in part.holes.values())
        self.assertGreater(min(hole.column for hole in parts["R1"].holes.values()), last + 1)

    def test_a_part_with_no_wokwi_drawing_is_named(self):
        read = xiao_read()
        catalog = drawing_catalog.describe_parts(read, GEOMETRY)
        del catalog["LedRed5mm"]
        with self.assertRaisesRegex(NotDrawnError, "nothing says how to draw LedRed5mm: its record has no Wokwi part "
                                                   "and no physical block") as refused:
            drawing.BreadboardPlanner(GEOMETRY, catalog).plan(read.steps)
        self.assertEqual((refused.exception.code, refused.exception.subject), ("no_drawing_fact", "LedRed5mm"))

    def test_a_pin_with_no_position_an_end_with_no_pin_and_an_unplaced_part_are_coded(self):
        """P691: each refusal carries its code and subject, so an agent never reads the sentence."""
        geometry = GEOMETRY.with_part("board-x", {"size": [1, 1], "center": [0, 0], "covers_holes": False, "pins": {}})
        end = wiring_steps.End("part", "X", "X 9", "X, pin 9", "9")
        catalog = {"X": drawing.DrawnPart("board-x", {}, {"9": "P9"})}
        for refuse, expected in (
                (lambda: drawing.FirstFitPartPlacement(geometry).place("X", catalog["X"], HoleLedger(geometry.surface)),
                 ("no_pin_position", "board-x")),
                (lambda: drawing.end_pin(end, {"X": drawing.DrawnPart("board-x", {}, {})}), ("no_wokwi_pin", "X 9")),
                (lambda: drawing.end_group(end, {}, catalog), ("planner_fault", "X 9"))):
            with self.subTest(expected=expected), self.assertRaises(NotDrawnError) as refused:
                refuse()
            self.assertEqual((refused.exception.code, refused.exception.subject), expected)

    def test_a_resistor_that_joins_a_row_never_placed_is_a_planner_fault(self):
        read = xiao_read()
        joined = wiring_steps.StepPoint([self.leg("R2", 1), self.leg("R1", 1)], None, False)
        step = next(step for step in wiring_steps.BreadboardSteps([], [joined]).anchored()
                    if step.act == wiring_steps.JOIN)
        planner = drawing.BreadboardPlanner(GEOMETRY, drawing_catalog.describe_parts(read, GEOMETRY))
        with self.assertRaisesRegex(NotDrawnError, "R1 joins a row that is never placed") as refused:
            planner._place_resistors([step], {}, HoleLedger(GEOMETRY.surface), 1)
        self.assertEqual((refused.exception.code, refused.exception.subject), ("planner_fault", "R1"))

    def test_a_resistor_value_is_in_ohms(self):
        self.assertEqual([drawing_catalog.to_ohms(v) for v in ("330Ω", "10kΩ", "4.7kΩ", "1MΩ", "")],
                         ["330", "10000", "4700", "1000000", ""])


if __name__ == "__main__":
    unittest.main()
