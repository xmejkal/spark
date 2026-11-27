"""
The drawn breadboard as one scene (P969, #1388): everything a view draws, each thing with its place, made once by
the scene maker before any view, and the pills, captions and pad labels placed through a label measure; each part's
pad states and its line of the note (scripts/spark/breadboard/breadboard_scene.py). The sheet makes the scene once, and
both drawings and its colour line read it (P969 PR 4).

    python3 -m unittest tests.test_breadboard_scene
    python3 tests/test_breadboard_scene.py --rough     # prints the walk's scene as rough text
"""

import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ElementTree
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite_temp  # noqa: E402,F401

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.breadboard import board_marks, breadboard_scene, drawing, label_measure, part_pictures, sheet, svg_diagram, wire_routing, wiring_steps  # noqa: E402
from spark.breadboard.spacing import BodyBox  # noqa: E402

DATA = ROOT / "tests" / "data" / "breadboard"
NS = {"svg": "http://www.w3.org/2000/svg"}
#: Wokwi's half pitch, in px: one cell of the scene's grid.
HALF_PITCH = 4.8


def planned(fixture):
    """The layout of one fixture, planned in process with an empty store."""
    with mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()}):
        return sheet._plan_layout(sheet._read_build(DATA / fixture / "requirements.json"))


class CountingTrackJumperRouter(wire_routing.TrackJumperRouter):
    """The track router, counting the times it routes a layout: given to the maker and to the renderer, it sees a route
    in either."""

    def __init__(self):
        self.calls = 0

    def route(self, layout, obstacles):
        self.calls += 1
        return super().route(layout, obstacles)


class CellLabels(label_measure.LabelMeasure):
    """A view that writes one character a cell: a pill is its words and two cells for its number, one cell high; a
    caption is one cell high and a cell a character wide; a pad's label starts the next cell from its pad, its letters
    on the pad's line; a board's mark on its cell's line, with no drop."""

    def pill(self, words):
        return (len(words) + 2) * HALF_PITCH, HALF_PITCH

    def caption(self, words):
        return HALF_PITCH, len(words) * HALF_PITCH

    def pad_label(self):
        return HALF_PITCH, 0

    def mark_drop(self, size):
        return 0


class NotedPictures(part_pictures.PictogramPartPictures):
    """spark's pictograms, with a note on the board's picture, as a kept picture that no maker shows gets one."""

    NOTE = "FireBeetle 2 ESP32-C6: kept picture not shown (no frame)"

    def picture(self, wokwi_type, record=None):
        picture = super().picture(wokwi_type, record)
        return picture._replace(note=self.NOTE) if isinstance(record, dict) and "c6" in record.get("id", "") else picture


#: The rough view's character of a pad in use and of a free pad.
ROUGH_PADS = {"used": "@", "free": "o"}


def rough_text(scene):
    """The scene as plain text, one character a cell of its grid: '.' a hole, '#' a part's body, each pad label's first
    letter at its place on the sheet, '@' a pad in use and 'o' a free one, '-' and '|' a wire's runs and '+' its bends,
    ':' a dashed wire, and each jumper's step at its pill's cell; then the note's lines."""
    grid = scene.grid
    rows = [[" "] * (grid.high[0] - grid.low[0] + 1) for _ in range(grid.high[1] - grid.low[1] + 1)]

    def put(cell, character):
        rows[cell[1] - grid.low[1]][cell[0] - grid.low[0]] = character

    for hole in scene.layout.geometry.surface.holes:
        put(grid.cell(hole.x, hole.y), ".")
    for part in scene.parts:
        (left, top), (right, bottom) = grid.cell(part.body.left, part.body.top), grid.cell(part.body.right, part.body.bottom)
        for u in range(left, right + 1):
            for v in range(top, bottom + 1):
                put((u, v), "#")
        for label in part.labels:
            put(grid.cell(*label.at), label.word[0])
        for pin, hole in part.part.holes.items():
            put(grid.cell(hole.x, hole.y), ROUGH_PADS[part.pads[pin]])
    for jumper in scene.jumpers:
        for cell, character in wire_cells(jumper):
            put(cell, character)
    for jumper in scene.jumpers:
        u, v = grid.cell(jumper.pill.x, jumper.pill.y)
        for index, character in enumerate(str(jumper.jumper.step)):
            put((u + index, v), character)
    return "\n".join(["".join(row).rstrip() for row in rows] + scene.notes())


def wire_cells(jumper):
    """(cell, character) of each cell a jumper's way passes, its bends last."""
    cells, dashed = jumper.cells, bool(jumper.path.fallback)
    found = []
    for (u1, v1), (u2, v2) in zip(cells, cells[1:]):
        across = v1 == v2
        for u in range(min(u1, u2), max(u1, u2) + 1):
            for v in range(min(v1, v2), max(v1, v2) + 1):
                found.append(((u, v), ":" if dashed else "-" if across else "|"))
    return found + [(cell, ":" if dashed else "+") for cell in cells[1:-1]]


def runs(jumper, grid):
    """{cell: character} of a jumper's way, read from its own px points: '-' on a run across a row, '|' on a run along
    a column, '+' at a bend; ':' on each of them when the wire is dashed."""
    dashed, found = bool(jumper.path.fallback), {}
    points = jumper.path.points
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        assert y1 == y2 or x1 == x2, ((x1, y1), (x2, y2))  # a run lies across a row or along a column
        (u1, v1), (u2, v2) = grid.cell(x1, y1), grid.cell(x2, y2)
        cells = [(u, v1) for u in range(min(u1, u2), max(u1, u2) + 1)] if y1 == y2 else \
            [(u1, v) for v in range(min(v1, v2), max(v1, v2) + 1)]
        found.update({cell: ":" if dashed else "-" if y1 == y2 else "|" for cell in cells})
    found.update({grid.cell(x, y): ":" if dashed else "+" for x, y in points[1:-1]})
    return found


def walk_scene(router=None):
    return breadboard_scene.BreadboardSceneMaker(router=router).make(planned("walk-c6"))


class TheSceneTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.router = CountingTrackJumperRouter()
        cls.scene = walk_scene(cls.router)
        cls.rough = rough_text(cls.scene)

    def test_the_walk_is_routed_once_and_drawn_in_today_s_bytes(self):
        # (1) the scene is made once, before any view: the rough view and the picture read it, and nothing routes again,
        # in the maker, which holds the counting router, or in the renderer, which holds no router since P969 PR 4
        text = svg_diagram.SvgBreadboardDiagram().text(self.scene)
        self.assertIn("#", self.rough)
        self.assertEqual(self.router.calls, 1)
        self.assertEqual(hashlib.sha256(text.encode()).hexdigest(),
                         "940cd77812d30b39c4ac104657248e3c9929fa43f5bafdf07496215e0a465884")  # main 1b1e8e0a's picture

    def test_each_jumper_s_step_is_at_its_pill_and_the_dashed_wires_are_dotted(self):
        # (2) the rough view places nothing: each step at its pill's cell, as the scene placed it
        rows = self.rough.split("\n")
        grid = self.scene.grid
        for jumper in self.scene.jumpers:
            u, v = grid.cell(jumper.pill.x, jumper.pill.y)
            step = str(jumper.jumper.step)
            with self.subTest(step=step):
                self.assertEqual(rows[v - grid.low[1]][u - grid.low[0]:u - grid.low[0] + len(step)], step)
        self.assertEqual(sorted(jumper.jumper.step for jumper in self.scene.jumpers if jumper.path.fallback), [6, 7, 10, 11])
        for jumper in self.scene.jumpers:
            # each wire alone, so no other wire covers it: its characters are those of its own runs and bends
            alone = rough_text(self.scene._replace(jumpers=(jumper,))).split("\n")
            u, v = grid.cell(jumper.pill.x, jumper.pill.y)
            pill = {(u + index, v) for index in range(len(str(jumper.jumper.step)))}
            expected = {cell: character for cell, character in runs(jumper, grid).items() if cell not in pill}
            with self.subTest(step=jumper.jumper.step):
                self.assertEqual({cell: alone[cell[1] - grid.low[1]][cell[0] - grid.low[0]] for cell in expected}, expected)

    def test_the_scene_holds_its_parts_and_its_wires_in_layout_order(self):
        layout = self.scene.layout
        self.assertEqual([part.part.id for part in self.scene.parts], [part.id for part in layout.parts])
        self.assertEqual([jumper.jumper for jumper in self.scene.jumpers], list(layout.jumpers))
        self.assertEqual(self.scene.wire_notes(), ["wires 6, 7, 10 and 11 bend more than 4 times to go around the parts "
                                                   "and are drawn dashed"])


    def test_the_rough_view_gets_the_pad_states_the_pad_labels_and_the_note_from_the_scene(self):
        # (6) P969 PR 3b: a view that draws no picture still gets every pad's state, every label and every warning
        rows, grid = self.rough.split("\n"), self.scene.grid
        states = []
        for part in self.scene.parts:
            for pin, hole in part.part.holes.items():
                u, v = grid.cell(hole.x, hole.y)
                with self.subTest(part=part.part.id, pin=pin):
                    self.assertEqual(rows[v - grid.low[1]][u - grid.low[0]], ROUGH_PADS[part.pads[pin]])
                states.append(part.pads[pin])
        self.assertEqual(set(states), {"used", "free"})
        self.assertEqual(rows[-3:], ["DFRobot FireBeetle 2 ESP32-C6: pads, row side and USB end not verified.",
                                     "MH-ET LIVE 2.9 Inch E-paper Module: pads and header side not verified.",
                                     "wires 6, 7, 10 and 11 bend more than 4 times to go around the parts and are drawn dashed"])
        for part in self.scene.parts:
            pins = {grid.cell(hole.x, hole.y) for hole in part.part.holes.values()}
            for label in part.labels:
                # each label alone, so no other label covers it: its first letter at its place on the sheet
                alone = rough_text(self.scene._replace(jumpers=(), parts=(part._replace(labels=(label,)),))).split("\n")
                u, v = grid.cell(*label.at)
                with self.subTest(part=part.part.id, pad=label.pad):
                    self.assertNotIn((u, v), pins)
                    self.assertEqual(alone[v - grid.low[1]][u - grid.low[0]], label.word[0])

    def test_each_pad_label_lies_by_its_pad_on_the_sheet_and_reads_bottom_to_top(self):
        # its place on the sheet is its place in the part's frame, turned with the part: within a pitch of its pad's hole
        labels = 0
        for part in self.scene.parts:
            for label in part.labels:
                hole = part.part.holes[label.pad]
                with self.subTest(part=part.part.id, pad=label.pad):
                    self.assertLessEqual(max(abs(label.at[0] - hole.x), abs(label.at[1] - hole.y)), 2 * HALF_PITCH)
                    self.assertIn((part.part.rotate + label.place.rotate) % 360, (0, 270))
                labels += 1
        self.assertEqual(labels, 32 + 8)
        self.assertEqual([part.part.rotate for part in self.scene.parts], [90, 0])  # the board is turned

    def test_the_maker_says_each_picture_s_note_with_no_picture_drawn(self):
        # the maker makes each part's picture from the pictures it is given, so a picture's note reaches every view
        scene = breadboard_scene.BreadboardSceneMaker(pictures=NotedPictures()).make(self.scene.layout)
        self.assertEqual(scene.notes()[0], "DFRobot FireBeetle 2 ESP32-C6: pads, row side and USB end not verified. "
                                           "FireBeetle 2 ESP32-C6: kept picture not shown (no frame)")
        self.assertEqual(scene.parts[0].picture.note, NotedPictures.NOTE)


class TheGridTest(unittest.TestCase):
    def test_each_point_s_cell_lies_within_half_a_cell_of_it(self):
        # (3) on the XIAO, whose rail holes lie a third of a cell off the grid (on the walk every point is on it)
        scene = breadboard_scene.BreadboardSceneMaker().make(planned("button-light-xiao"))
        grid = scene.grid
        self.assertEqual(grid.step, HALF_PITCH)
        off = 0
        for jumper in scene.jumpers:
            self.assertEqual(len(jumper.cells), len(jumper.path.points))
            for (x, y), cell in zip(jumper.path.points, jumper.cells):
                with self.subTest(step=jumper.jumper.step, point=(x, y)):
                    px, py = grid.point(cell)
                    self.assertLessEqual(max(abs(px - x), abs(py - y)), HALF_PITCH / 2)
                    off += (px, py) != (x, y)
        self.assertGreater(off, 0)

    def test_the_grid_holds_every_cell_the_scene_draws(self):
        scene = walk_scene()
        grid = scene.grid
        cells = [cell for jumper in scene.jumpers for cell in jumper.cells]
        cells += [grid.cell(jumper.pill.x, jumper.pill.y) for jumper in scene.jumpers]
        cells += [grid.cell(part.caption.x, part.caption.y) for part in scene.parts]
        for u, v in cells:
            self.assertTrue(grid.low[0] <= u <= grid.high[0] and grid.low[1] <= v <= grid.high[1], (u, v))


class TheMakerTest(unittest.TestCase):
    def test_the_module_loads_with_no_picture_code(self):
        # (4) the scene is made with no picture: importing its maker loads no svg_diagram
        code = ("import sys; sys.path.insert(0, sys.argv[1]); import spark.breadboard.breadboard_scene; "
                "print('spark.breadboard.svg_diagram' in sys.modules)")
        run = subprocess.run([sys.executable, "-c", code, str(ROOT / "scripts")], capture_output=True, text=True,
                             env={**os.environ, "SPARK_HOME": tempfile.mkdtemp()})
        self.assertEqual((run.stdout.strip(), run.returncode), ("False", 0), run.stderr)

    def test_the_lane_router_chosen_on_the_maker_draws_its_lanes(self):
        # (5) the router is swapped on the maker, outside any renderer
        layout = planned("epaper")
        scene = breadboard_scene.BreadboardSceneMaker(router=wire_routing.LaneJumperRouter()).make(layout)
        lanes = wire_routing.LaneJumperRouter().route(layout, None)
        self.assertEqual({jumper.jumper.step: jumper.path for jumper in scene.jumpers}, lanes)
        root = ElementTree.fromstring(svg_diagram.SvgBreadboardDiagram().text(scene))
        for step, path in lanes.items():
            drawn = root.find("svg:g[@data-step='%d']" % step, NS).find("svg:path", NS).get("d")
            self.assertEqual(drawn, "M" + "L".join("%s %s" % point for point in path.points), step)

    def test_the_maker_places_the_pills_and_captions_through_its_measure(self):
        # another view's measure moves the labels: the maker, not the renderer, places them
        layout = planned("walk-c6")
        px = breadboard_scene.BreadboardSceneMaker().make(layout)
        cells = breadboard_scene.BreadboardSceneMaker(measure=CellLabels()).make(layout)
        for jumper in cells.jumpers:
            pill = jumper.pill
            self.assertEqual((pill.width, pill.height), ((len(pill.words) + 2) * HALF_PITCH, HALF_PITCH))
        for part in cells.parts:
            caption = part.caption
            self.assertEqual((caption.size, caption.width), (HALF_PITCH, len(caption.words) * HALF_PITCH))
        self.assertNotEqual([(one.pill.x, one.pill.y) for one in cells.jumpers],
                            [(one.pill.x, one.pill.y) for one in px.jumpers])
        self.assertNotEqual([(one.caption.x, one.caption.y) for one in cells.parts],
                            [(one.caption.x, one.caption.y) for one in px.parts])

    def test_the_maker_places_the_pad_labels_through_its_measure(self):
        # P969 PR 3b: another view's measure moves the pad labels: each starts a cell from its pad, on the pad's line
        layout = planned("walk-c6")
        px = breadboard_scene.BreadboardSceneMaker().make(layout)
        cells = breadboard_scene.BreadboardSceneMaker(measure=CellLabels()).make(layout)
        offsets = {}
        for part in cells.parts:
            part_px = layout.geometry.part(part.part.type)
            for label in part.labels:
                x, y = part_px["pins"][label.pad]
                offsets.setdefault(part_px["labels"], set()).add((round(abs(label.place.x - x), 6), round(abs(label.place.y - y), 6)))
        self.assertEqual(offsets, {"beside": {(HALF_PITCH, 0)}, "into-body": {(0, HALF_PITCH)}})
        self.assertNotEqual([label.place for part in cells.parts for label in part.labels],
                            [label.place for part in px.parts for label in part.labels])

    def test_the_px_measure_is_the_svg_s_pill_and_caption(self):
        measure = label_measure.PxLabelMeasure(7)
        width, height = measure.pill("SDI to D11")
        self.assertAlmostEqual(width, 9.6 + 3.6 + 3.57 * 10)
        self.assertEqual(height, 9.6)
        size, width = measure.caption("FireBeetle")
        self.assertEqual(size, 7)
        self.assertAlmostEqual(width, (0.55 * 10 + 0.5) * 7)
        self.assertEqual(measure.pad_label(), (5, 2))


class AllWhite(wiring_steps.JumperColors):
    """A colour pick of its own: every wire white, a word no role gives."""

    def of(self, roles):
        return {number: "white" for number in sorted(roles)}


class TheSheetTest(unittest.TestCase):
    """P969 PR 4: the sheet makes the scene once, on the XIAO, and both drawings and its colour line read it."""

    @classmethod
    def setUpClass(cls):
        cls.requirements = DATA / "button-light-xiao" / "requirements.json"
        with mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()}):
            cls.read = sheet._read_build(cls.requirements)
            cls.planned = sheet._plan_once(cls.read)

    def test_the_sheet_routes_once_for_both_drawings(self):
        router = CountingTrackJumperRouter()
        paths = [(Path(tempfile.mkdtemp()) / renderer.FILE_NAME, renderer) for renderer in sheet.DRAWING_RENDERERS]
        scene, texts = sheet._texts(paths, paths, self.planned, breadboard_scene.BreadboardSceneMaker(router=router))
        self.assertEqual(router.calls, 1)
        self.assertIs(scene.layout, self.planned.layout)
        self.assertEqual(hashlib.sha256(texts[0].encode()).hexdigest(),
                         "0409ac7ab08ffcd862cb777be7c59764a3f35d2cf1b2a5362408d130556d2faf")  # the XIAO's Wokwi diagram
        self.assertTrue(texts[1].startswith("<svg"), texts[1][:40])

    def test_no_scene_is_made_when_no_drawing_is_drawn(self):
        router = CountingTrackJumperRouter()
        stopped = sheet.PlannedLayout(None, drawing.NotDrawnError("no room", drawing.NO_HOLE_LEFT), [])
        self.assertEqual(sheet._texts([], [], stopped, breadboard_scene.BreadboardSceneMaker(router=router)), (None, []))
        self.assertEqual(router.calls, 0)

    def test_the_diagram_and_the_sheet_s_colour_line_say_the_scene_s_colours(self):
        # the colours are picked once, in the scene: the Wokwi diagram and the sheet say its words, never their own
        scene = breadboard_scene.BreadboardSceneMaker(colors=AllWhite()).make(self.planned.layout)
        drawn = json.loads(drawing.WokwiBreadboardDiagram().text(scene))
        self.assertEqual({wire[2] for wire in drawn["connections"]}, {"white"})
        with mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()}):
            text = sheet.sheet(self.requirements, read=self.read, planned=self.planned._replace(scene=scene))
        line = next(line for line in text.splitlines() if "Each jumper has the color" in line)
        said = line.split("each signal: ", 1)[1].rstrip(".").split(", ")
        self.assertEqual(len(said), len(self.planned.layout.jumpers))
        self.assertTrue(all(one.split(" ")[1] == "white" for one in said), line)


class TheLeftoversTest(unittest.TestCase):
    """P969 PR 4b: the scene gives its extent and each board's USB end, its marks take the maker's measure, and the
    picture draws them at the scene's sizes, so the picture computes none of them."""

    @classmethod
    def setUpClass(cls):
        cls.scene = walk_scene()

    def test_the_scene_gives_one_extent_box_that_the_grid_and_the_canvas_read(self):
        scene, extent = self.scene, self.scene.grid.extent
        held = [scene.marks.box()] + [part.body for part in scene.parts] + [part.caption.box() for part in scene.parts]
        held += [jumper.pill.box() for jumper in scene.jumpers]
        held += [BodyBox(x, y, x, y) for jumper in scene.jumpers for x, y in jumper.path.points]
        self.assertEqual(extent, BodyBox(min(box.left for box in held), min(box.top for box in held),
                                         max(box.right for box in held), max(box.bottom for box in held)))
        grid = scene.grid
        self.assertEqual(grid.low, (math.floor((extent.left - grid.x0) / grid.step), math.floor((extent.top - grid.y0) / grid.step)))
        self.assertEqual(grid.high, (math.ceil((extent.right - grid.x0) / grid.step), math.ceil((extent.bottom - grid.y0) / grid.step)))
        x, y, width, height = [float(n) for n in ElementTree.fromstring(
            svg_diagram.SvgBreadboardDiagram().text(scene)).get("viewBox").split()]
        self.assertAlmostEqual(x, extent.left - 19.2, places=3)
        self.assertAlmostEqual(y, extent.top - 19.2, places=3)
        self.assertAlmostEqual(x + width, extent.right + 19.2, places=2)
        self.assertAlmostEqual(y + height, extent.bottom + 19.2 + 9.6 * len(scene.notes()), places=2)

    def test_the_board_s_usb_end_is_marked_in_its_own_frame(self):
        # P969 revisions 28 and 31: UsbEnd, its box in the board's own frame, which the picture draws; its place on
        # the sheet had no reader, so it went (P974)
        board, module = self.scene.parts
        self.assertIsNone(module.usb_end)
        box = board.usb_end.box
        self.assertEqual((box.right - box.left, round(box.bottom - box.top, 6)), (34, 12))

    def test_the_picture_draws_the_marks_at_the_scene_s_sizes(self):
        # revision 21: a palette with other sizes given to the maker only; the picture keeps only its own colours
        own = board_marks.BoardPalette.load()
        scene = breadboard_scene.BreadboardSceneMaker(palette=board_marks.BoardPalette(
            own.colors, dict(own.sizes, rail_sign=17, gap_band=48))).make(self.scene.layout)
        root = ElementTree.fromstring(svg_diagram.SvgBreadboardDiagram().text(scene))
        signs = [text for text in root.iter("{%s}text" % NS["svg"]) if text.text in ("+", "−")]
        self.assertEqual({text.get("font-size") for text in signs}, {"17"})
        (band,) = [rect for rect in root.iter("{%s}rect" % NS["svg"]) if rect.get("fill") == own.colors["gap"]]
        self.assertEqual(float(band.get("height")), 48)
        self.assertAlmostEqual(float(band.get("y")) + 24, (89.4 + 118.2) / 2)  # about the middle of rows e and f

    def test_the_maker_gives_the_marks_its_measure(self):
        scene = breadboard_scene.BreadboardSceneMaker(measure=CellLabels()).make(self.scene.layout)
        for (_, row_y, *_), (_, _, baseline) in zip(scene.marks.rail_lines(), scene.marks.signs()):
            self.assertEqual(baseline, row_y)


if __name__ == "__main__":
    if sys.argv[1:] == ["--rough"]:
        print(rough_text(walk_scene()))
    else:
        unittest.main()
