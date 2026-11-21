"""
The drawn breadboard as one scene (P969, #1388): everything a view draws, each thing with its place, made once by
the scene maker before any view, and the pills and captions placed through a label measure
(scripts/spark/breadboard/breadboard_scene.py).

    python3 -m unittest tests.test_breadboard_scene
    python3 tests/test_breadboard_scene.py --rough     # prints the walk's scene as rough text
"""

import hashlib
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

from spark.breadboard import breadboard_scene, sheet, svg_diagram, wire_routing  # noqa: E402

DATA = ROOT / "tests" / "data" / "breadboard"
NS = {"svg": "http://www.w3.org/2000/svg"}
#: Wokwi's half pitch, in px: one cell of the scene's grid.
HALF_PITCH = 4.8


def planned(fixture):
    """The layout of one fixture, planned in process with an empty store."""
    with mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()}):
        return sheet._plan_layout(sheet._read_build(DATA / fixture / "requirements.json"))


class CountingJumperRouter(wire_routing.JumperRouter):
    """The track router, counting the times it routes a layout."""

    def __init__(self):
        self.calls = 0

    def route(self, layout, obstacles):
        self.calls += 1
        return wire_routing.TrackJumperRouter().route(layout, obstacles)


class CellLabels(breadboard_scene.LabelMeasure):
    """A view that writes one character a cell: a pill is its words and two cells for its number, one cell high; a
    caption is one cell high and a cell a character wide."""

    def pill(self, words):
        return (len(words) + 2) * HALF_PITCH, HALF_PITCH

    def caption(self, words):
        return HALF_PITCH, len(words) * HALF_PITCH


def rough_text(scene):
    """The scene as plain text, one character a cell of its grid: '.' a hole, '#' a part's body, '-' and '|' a wire's
    runs and '+' its bends, ':' a dashed wire, and each jumper's step at its pill's cell."""
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
    for jumper in scene.jumpers:
        for cell, character in wire_cells(jumper):
            put(cell, character)
    for jumper in scene.jumpers:
        u, v = grid.cell(jumper.pill.x, jumper.pill.y)
        for index, character in enumerate(str(jumper.jumper.step)):
            put((u + index, v), character)
    return "\n".join("".join(row).rstrip() for row in rows)


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


def walk_scene(router=None):
    return breadboard_scene.BreadboardSceneMaker(router=router).make(planned("walk-c6"))


class TheSceneTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.router = CountingJumperRouter()
        cls.scene = walk_scene(cls.router)
        cls.rough = rough_text(cls.scene)

    def test_the_walk_is_routed_once_and_drawn_in_today_s_bytes(self):
        # (1) the scene is made once, before any view: the rough view and the picture read it, and nothing routes again
        text = svg_diagram.SvgBreadboardDiagram().draw(self.scene)
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
            alone = rough_text(self.scene._replace(jumpers=(jumper,))).split("\n")
            u, v = grid.cell(jumper.pill.x, jumper.pill.y)
            pill = {(u + index, v) for index in range(len(str(jumper.jumper.step)))}
            drawn = {alone[v - grid.low[1]][u - grid.low[0]] for (u, v), _ in wire_cells(jumper) if (u, v) not in pill}
            with self.subTest(step=jumper.jumper.step):
                self.assertEqual(drawn, {":"} if jumper.path.fallback else {"-", "|", "+"})

    def test_the_scene_holds_the_board_its_parts_and_its_wires_in_layout_order(self):
        layout = self.scene.layout
        self.assertEqual([part.part.id for part in self.scene.parts], [part.id for part in layout.parts])
        self.assertEqual([jumper.jumper for jumper in self.scene.jumpers], list(layout.jumpers))
        self.assertEqual(self.scene.board, self.scene.marks.box())
        self.assertEqual(self.scene.wire_notes(), ["wires 6, 7, 10 and 11 bend more than 4 times to go around the parts "
                                                   "and are drawn dashed"])


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
        root = ElementTree.fromstring(svg_diagram.SvgBreadboardDiagram().draw(scene))
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

    def test_the_px_measure_is_the_svg_s_pill_and_caption(self):
        measure = breadboard_scene.PxLabelMeasure(7)
        width, height = measure.pill("SDI to D11")
        self.assertAlmostEqual(width, 9.6 + 3.6 + 3.57 * 10)
        self.assertEqual(height, 9.6)
        size, width = measure.caption("FireBeetle")
        self.assertEqual(size, 7)
        self.assertAlmostEqual(width, (0.55 * 10 + 0.5) * 7)


if __name__ == "__main__":
    if sys.argv[1:] == ["--rough"]:
        print(rough_text(walk_scene()))
    else:
        unittest.main()
