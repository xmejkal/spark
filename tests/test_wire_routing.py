"""
The wires around the parts (P953, #1359): each jumper of the drawn breadboard on tracks between the holes, never over
a part's body (scripts/spark/breadboard/wire_routing.py).

    python3 -m unittest tests.test_wire_routing
"""

import os
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

from spark.breadboard import board_marks, breadboard_scene, drawing, sheet, svg_diagram, wire_pills, wire_routing  # noqa: E402
from spark.breadboard.spacing import BodyBox  # noqa: E402

DATA = ROOT / "tests" / "data" / "breadboard"
#: The walk's fixture and those of the golden sheets with a picture (the rebuild's runs as its golden only).
FIXTURES = ("walk-c6", "button-light-xiao", "button-light", "epaper")
NS = {"svg": "http://www.w3.org/2000/svg"}
#: Half the white under-stroke, in px: how far a wire reaches either side of its line.
HALF_STROKE = wire_pills.WIRE_SIZES_PX.under_stroke / 2


def routed(fixture):
    """(layout, its BodyBoxes, its TrackRouting) of one fixture, planned in process with an empty store."""
    with mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()}):
        layout = sheet._plan_layout(sheet._read_build(DATA / fixture / "requirements.json"))
    bodies = [BodyBox.of(part, layout.geometry.part(part.type)) for part in layout.parts]
    marks = board_marks.BoardMarks(layout.geometry.surface, board_marks.BoardPalette.load().sizes, breadboard_scene.PxLabelMeasure(7))
    return layout, bodies, wire_routing.TrackJumperRouter.routing(layout, marks.obstacles(bodies))


def pieces(points):
    return list(zip(points, points[1:]))


def trimmed(points, by):
    """The points with the first and the last piece cut by `by` px at the hole: the half pitch out of each hole, which
    the planner's hole may put beside a body."""
    def toward(start, end):
        length = abs(end[0] - start[0]) + abs(end[1] - start[1])
        share = min(by, length) / length if length else 0
        return (start[0] + (end[0] - start[0]) * share, start[1] + (end[1] - start[1]) * share)
    points = list(points)
    points[0], points[-1] = toward(points[0], points[1]), toward(points[-1], points[-2])
    return points


def touches(piece, box, by):
    (x1, y1), (x2, y2) = piece
    return (min(x1, x2) - by < box.right and max(x1, x2) + by > box.left and min(y1, y2) - by < box.bottom
            and max(y1, y2) + by > box.top)


class TheRoutesTest(unittest.TestCase):
    """The done-when of P953's PR 2 on the walk and every golden's fixture."""

    @classmethod
    def setUpClass(cls):
        cls.routed = {fixture: routed(fixture) for fixture in FIXTURES}

    def each_path(self):
        for fixture, (layout, bodies, routing) in self.routed.items():
            for jumper in layout.jumpers:
                yield fixture, layout, bodies, jumper, routing.paths[jumper.step]

    def test_every_jumper_has_a_path_or_a_fallback(self):
        for fixture, (layout, _, routing) in self.routed.items():
            self.assertEqual(sorted(routing.paths), sorted(jumper.step for jumper in layout.jumpers), fixture)
            self.assertGreaterEqual(len(routing.paths), 4, fixture)

    def test_no_segment_touches_a_part_body(self):
        for fixture, _, bodies, jumper, path in self.each_path():
            with self.subTest(fixture=fixture, step=jumper.step):
                pitch = 9.6
                touched = [(piece, box) for piece in pieces(trimmed(path.points, pitch / 2)) for box in bodies
                           if touches(piece, box, HALF_STROKE)]
                self.assertEqual(touched, [])

    def test_each_path_starts_and_ends_on_its_holes(self):
        for fixture, _, _, jumper, path in self.each_path():
            with self.subTest(fixture=fixture, step=jumper.step):
                self.assertEqual((path.points[0], path.points[-1]), ((round(jumper.one.x, 3), round(jumper.one.y, 3)),
                                                                     (round(jumper.other.x, 3), round(jumper.other.y, 3))))

    def test_no_wire_has_more_than_4_bends_and_a_dashed_one_more_than_4_and_at_most_8(self):
        for fixture, _, _, jumper, path in self.each_path():
            with self.subTest(fixture=fixture, step=jumper.step):
                self.assertEqual(path.bends, len(path.points) - 2)
                if path.fallback:
                    self.assertEqual((path.fallback, path.bends > 4, path.bends <= 8), ("bends", True, True))
                else:
                    self.assertLessEqual(path.bends, 4)

    def test_every_segment_is_straight_and_after_its_first_half_pitch_lies_on_a_track_or_its_hole_s_column(self):
        for fixture, layout, _, jumper, path in self.each_path():
            surface = layout.geometry.surface
            half, x0, y0 = surface.pitch / 2, min(h.x for h in surface.terminal), min(surface.letters_y.values())
            with self.subTest(fixture=fixture, step=jumper.step):
                for (x1, y1), (x2, y2) in pieces(trimmed(path.points, half)):
                    self.assertTrue(x1 == x2 or y1 == y2)
                    if y1 == y2 and x1 != x2:
                        self.assertEqual(round((y1 - y0) / half) % 2, 1, y1)
                    elif y1 != y2 and x1 not in (round(jumper.one.x, 3), round(jumper.other.x, 3)):
                        self.assertEqual(round((x1 - x0) / half) % 2, 1, x1)

    def test_no_wire_passes_over_a_hole(self):
        for fixture, layout, _, jumper, path in self.each_path():
            holes = [(hole.x, hole.y) for hole in layout.geometry.surface.holes
                     if (hole.x, hole.y) not in ((jumper.one.x, jumper.one.y), (jumper.other.x, jumper.other.y))]
            with self.subTest(fixture=fixture, step=jumper.step):
                over = [hole for piece in pieces(path.points) for hole in holes if touches(piece, BodyBox(*hole, *hole), 1)]
                self.assertEqual(over, [])

    def test_no_two_wires_share_a_segment(self):
        for fixture, (layout, _, routing) in self.routed.items():
            with self.subTest(fixture):
                drawn = [(step, piece) for step, path in routing.paths.items() for piece in pieces(path.points)]
                shared = [(a, b) for index, (a, one) in enumerate(drawn) for b, other in drawn[index + 1:]
                          if a != b and _overlap(one, other) > 0.01]
                self.assertEqual(shared, [])

    def test_crossings_are_right_angles_a_pitch_from_every_bend_and_end(self):
        for fixture, (layout, _, routing) in self.routed.items():
            pitch = layout.geometry.surface.pitch
            with self.subTest(fixture):
                for step, path in routing.paths.items():
                    for other, path2 in routing.paths.items():
                        if step == other:
                            continue
                        for crossing in _crossings(path.points, path2.points):
                            corners = list(path.points) + list(path2.points)
                            self.assertGreaterEqual(min(abs(crossing[0] - x) + abs(crossing[1] - y) for x, y in corners),
                                                    pitch - 0.01, (step, other, crossing))

    def test_no_wire_kept_to_the_rules_passes_beside_another_jumper_s_end(self):
        # an end's dot is 8 px wide: a wire half a pitch from it would touch it and look joined
        for fixture, layout, _, jumper, path in self.each_path():
            if path.fallback:
                continue
            ends = [(hole.x, hole.y) for other in layout.jumpers if other.step != jumper.step for hole in (other.one, other.other)]
            with self.subTest(fixture=fixture, step=jumper.step):
                near = [end for piece in pieces(path.points) for end in ends if touches(piece, BodyBox(*end, *end), 4.81)]
                self.assertEqual(near, [])

    def test_the_walk_s_result_is_pinned(self):
        # 7 wires around the parts with at most 4 bends, 4 dashed; none over a body (it was 7 before P953). P953 PR 3:
        # power and ground go through the rails, so the five rail wires (3, 4, 5, 8, 9) keep the rules and the four
        # dashed are signals (they were 7, 8, 9 and 11 of 9, now 6, 7, 10 and 11 of 11)
        _, _, routing = self.routed["walk-c6"]
        self.assertEqual({step: path.fallback for step, path in routing.paths.items()},
                         {3: "", 4: "", 5: "", 8: "", 9: "", 12: "", 13: "", 6: "bends", 7: "bends", 10: "bends",
                          11: "bends"})

    def test_the_xiao_s_wire_7_is_no_longer_dashed_as_ground_goes_to_the_rail(self):
        # before P953 PR 3 its wire 7 (board GND to the LED's K row) was dashed: its end lay between a body and another
        # end. Now board GND, the LED's K and the button's B each run to the bottom - rail, and every wire keeps the rules.
        _, _, routing = self.routed["button-light-xiao"]
        self.assertEqual({step: path.fallback for step, path in routing.paths.items()},
                         {5: "", 6: "", 7: "", 8: "", 9: ""})

    def test_the_other_fixtures_results_are_pinned(self):
        # each dashed wire's end lies between bodies or other ends, where 4 bends do not reach it
        # P953 PR 3: ground on the button-light goes to the - rail and no wire is dashed (its 7 was); the e-paper's
        # dashed are signals (they were 4 and 8 of 3 to 10, now 5, 11 and 12 of 3 to 12)
        self.assertEqual({step: path.fallback for step, path in self.routed["button-light"][2].paths.items()},
                         {5: "", 6: "", 7: "", 8: "", 9: ""})
        self.assertEqual({step: path.fallback for step, path in self.routed["epaper"][2].paths.items()},
                         {3: "", 4: "", 6: "", 7: "", 8: "", 9: "", 10: "", 5: "bends", 11: "bends", 12: "bends"})

    def test_no_search_is_cut_short_by_its_budget(self):
        # a search the budget stops returns no way as a search with no way does; the largest that found one took 47497
        self.assertEqual({fixture: routing.cut_short for fixture, (_, _, routing) in self.routed.items()},
                         {fixture: 0 for fixture in FIXTURES})

    def test_the_walk_routes_within_its_budget_of_states(self):
        # the states the searches took, in place of seconds: 233824 on 2026-11-20
        self.assertLessEqual(self.routed["walk-c6"][2].expanded, 300000)


def _overlap(one, other):
    (ax1, ay1), (ax2, ay2) = one
    (bx1, by1), (bx2, by2) = other
    if ay1 == ay2 == by1 == by2:
        return min(max(ax1, ax2), max(bx1, bx2)) - max(min(ax1, ax2), min(bx1, bx2))
    if ax1 == ax2 == bx1 == bx2:
        return min(max(ay1, ay2), max(by1, by2)) - max(min(ay1, ay2), min(by1, by2))
    return 0


def _crossings(points, others):
    """The points where a piece across of one path meets a piece along a column of the other, inside both."""
    found = []
    for (ax1, ay1), (ax2, ay2) in pieces(points):
        for (bx1, by1), (bx2, by2) in pieces(others):
            if ay1 == ay2 and bx1 == bx2 and min(ax1, ax2) < bx1 < max(ax1, ax2) and min(by1, by2) < ay1 < max(by1, by2):
                found.append((bx1, ay1))
            if ax1 == ax2 and by1 == by2 and min(bx1, bx2) < ax1 < max(bx1, bx2) and min(ay1, ay2) < by1 < max(ay1, ay2):
                found.append((ax1, by1))
    return found


class TheFallbackTest(unittest.TestCase):
    """A jumper with no way around the parts: never drawn over a part, and the note says so (UX 3.4)."""

    def test_a_walled_end_is_not_drawn_and_the_note_says_so(self):
        layout, bodies, _ = routed("button-light-xiao")
        jumper = next(one for one in layout.jumpers if one.step == 5)
        wall = BodyBox(jumper.other.x - 12, jumper.other.y - 12, jumper.other.x + 12, jumper.other.y + 12)
        marks = board_marks.BoardMarks(layout.geometry.surface, board_marks.BoardPalette.load().sizes, breadboard_scene.PxLabelMeasure(7))
        routing = wire_routing.TrackJumperRouter.routing(layout, marks.obstacles(bodies + [wall]))
        self.assertEqual(routing.paths[5], wire_routing.JumperPath((), 0, "no_way"))

        class Walled(wire_routing.JumperRouter):
            def route(self, layout, obstacles):
                return routing.paths

        root = ElementTree.fromstring(svg_diagram.SvgBreadboardDiagram().text(
            breadboard_scene.BreadboardSceneMaker(router=Walled()).make(layout)))
        group = root.find("svg:g[@data-step='5']", NS)
        self.assertEqual((len(group.findall("svg:path", NS)), len(group.findall("svg:circle", NS))), (0, 2))
        # P953 PR 4b: a note line is found by its class, in the grid text's grey
        notes = [text.text for text in root.iter("{http://www.w3.org/2000/svg}text") if text.get("class") == "note"]
        # P953 PR 3: the XIAO has no dashed wire now (its 7 was), so the note names only the walled wire
        self.assertEqual(notes, ["wire 5 finds no way around the parts and is not drawn"])

    def test_a_dashed_wire_is_dashed_in_its_colour_only(self):
        # P953 PR 3: the XIAO has no dashed wire now (its 7 was), so the walk's dashed wire 6 and its solid wire 3
        layout, _, _ = routed("walk-c6")
        root = ElementTree.fromstring(svg_diagram.SvgBreadboardDiagram().text(breadboard_scene.BreadboardSceneMaker().make(layout)))
        under, color = root.find("svg:g[@data-step='6']", NS).findall("svg:path", NS)
        self.assertEqual((under.get("stroke-dasharray"), color.get("stroke-dasharray")), (None, "4 2"))
        self.assertIsNone(root.find("svg:g[@data-step='3']", NS).findall("svg:path", NS)[1].get("stroke-dasharray"))

    def test_the_lane_router_is_still_a_strategy(self):
        layout, _, _ = routed("epaper")
        paths = wire_routing.LaneJumperRouter().route(layout, None)
        self.assertEqual({path.bends for path in paths.values()}, {2})
        self.assertIn("M", svg_diagram.SvgBreadboardDiagram().text(
            breadboard_scene.BreadboardSceneMaker(router=wire_routing.LaneJumperRouter()).make(layout)))


class TheTrackGridTest(unittest.TestCase):
    """The half-pitch grid: holes on even cells, tracks on odd lines, bodies and marks blocked half a pitch round."""

    @classmethod
    def setUpClass(cls):
        cls.surface = drawing.Surface.load_full()
        cls.marks = board_marks.BoardMarks(cls.surface, board_marks.BoardPalette.load().sizes, breadboard_scene.PxLabelMeasure(7))

    def grid(self, bodies=()):
        return wire_routing.TrackGrid(self.surface, self.marks.obstacles(bodies))

    def test_every_terminal_hole_is_an_even_cell_and_not_free(self):
        grid = self.grid()
        cells = {grid.cell(hole.x, hole.y) for hole in self.surface.terminal}
        self.assertEqual({(u % 2, v % 2) for u, v in cells}, {(0, 0)})
        self.assertFalse(any(grid.free(cell) for cell in cells))
        self.assertEqual(grid.point(grid.cell(35.6, 60.6)), (35.6, 60.6))

    def test_a_body_blocks_its_cells_and_those_less_than_half_a_pitch_round(self):
        grid = self.grid([BodyBox(100, 100, 120, 110)])
        self.assertEqual((grid.point((15, 11)), grid.point((14, 11))), ((98.0, 103.8), (93.2, 103.8)))
        self.assertFalse(grid.free((17, 11)))  # 107.6, inside
        self.assertFalse(grid.free((15, 11)))  # 2 px off its left edge
        self.assertTrue(grid.free((14, 11)))  # 6.8 px off it
        self.assertTrue(grid.free((15, 9)))  # 94.2, 5.8 px above its top

    def test_the_grid_reaches_left_of_column_1_and_past_the_numbers(self):
        grid = self.grid()
        self.assertLessEqual(grid.low[0], -5)
        self.assertLessEqual(grid.point(grid.low)[1], 3.0 - 2 * 9.6)  # above the top numbers
        self.assertGreaterEqual(grid.point(grid.high)[1], 204.6 + 2 * 9.6)  # below the bottom numbers
        self.assertTrue(grid.outside((-5, 11)))
        self.assertFalse(grid.outside((1, 11)))

    def test_the_letters_and_numbers_block_their_cells(self):
        grid = self.grid()
        self.assertFalse(grid.free(grid.cell(16.4, 51)))  # the letter a
        self.assertFalse(grid.free(grid.cell(64.4, 3)))  # the number 5 above
        self.assertTrue(grid.free(grid.cell(45.2, 3)))  # between 1 and 5

    def test_a_run_beside_a_rail_line_is_marked_and_the_gap_holds_3_tracks(self):
        grid = self.grid()
        self.assertTrue(grid.beside_a_line(grid.cell(40.4, 27.0)))  # 0.96 px from the - rail's line at 26.04
        self.assertFalse(grid.beside_a_line(grid.cell(40.4, 36.6)))
        gap = [v for v in range(grid.cell(0, 89.4)[1] + 1, grid.cell(0, 118.2)[1]) if v % 2]
        self.assertEqual(len(gap), 3)


if __name__ == "__main__":
    unittest.main()
