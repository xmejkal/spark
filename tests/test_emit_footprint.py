"""
Proof that a generated footprint is the real module, and that a guessed one is never written.

A wrong footprint is the most expensive artefact this plugin can produce. Everything else it gets
wrong shows up as a build error or a check failure; a footprint whose pads are in the wrong place
builds clean, routes clean, passes every rule, and is discovered when the module will not seat on
a board that has already been paid for.

So there are two kinds of test here, and both are load-bearing:

  * the geometry is compared against a footprint that was produced independently — by a separate
    script, from DFRobot's own dimension drawing, and hand-checked — so "it matches itself" is
    not available as a way to pass;
  * every fact the generator cannot derive has a test that it REFUSES rather than invents.

    python3 -m unittest discover -s tests
"""

import copy
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import emit_footprint  # noqa: E402

#: Produced by `tools/generate-firebeetle-footprint.py` in the smart-bin project, from DFRobot's
#: published dimension drawing, and checked by hand against the module. It is the only independent
#: witness to this geometry that exists, which is why the comparison is worth having even though
#: the file lives outside this repository.
REFERENCE = Path(__file__).resolve().parents[2] / "smartbin-local" / "FireBeetle2Esp32S3.tsx"

PAD = re.compile(
    r'portHints=\{\["([^"]+)"\]\}\s*pcbX="([-\d.]+)mm"\s*pcbY="([-\d.]+)mm"\s*'
    r'outerDiameter="([\d.]+)mm"\s*holeDiameter="([\d.]+)mm"')


def pads_in(text):
    return [(m.group(1), float(m.group(2)), float(m.group(3)), float(m.group(4)), float(m.group(5)))
            for m in PAD.finditer(text)]


def firebeetle():
    return json.loads((ROOT / "boards" / "firebeetle2-esp32s3.json").read_text())


class TheHoleIsSizedForThePinTest(unittest.TestCase):
    """
    The defect this whole script exists to avoid. The board file records the vendor's 0.9 mm
    drill, which is their finished hole for their own obround pad — copying it produces 32 holes
    a header pin will not go into, and a board nobody can assemble.
    """

    def test_the_hole_admits_a_header_pin_after_plating(self):
        finished = emit_footprint.hole_diameter_mm() - 2 * emit_footprint.PLATING_THICKNESS_MM
        self.assertGreaterEqual(finished, emit_footprint.HEADER_PIN_DIAGONAL_MM)

    def test_the_vendors_drill_is_not_used(self):
        # Stated as its own test because it is the one number a careful person would copy.
        vendor = firebeetle()["physical"]["header"]["drill_mm"]
        self.assertNotAlmostEqual(emit_footprint.hole_diameter_mm(), vendor, places=3)

    def test_the_pad_leaves_enough_copper_around_the_hole(self):
        hole = emit_footprint.hole_diameter_mm()
        ring = (emit_footprint.pad_diameter_mm(hole) - hole) / 2
        self.assertGreaterEqual(ring, 0.25)

    def test_the_generated_file_says_why_it_differs_from_the_drawing(self):
        # Somebody comparing this against the vendor PDF will find a disagreement and needs to
        # know it was deliberate, not a units bug.
        text = emit_footprint.render(firebeetle())
        self.assertIn("NOT the 0.9 mm on the vendor drawing", text)


class ItMatchesAnIndependentlyMadeFootprintTest(unittest.TestCase):
    @unittest.skipUnless(REFERENCE.is_file(), "the hand-checked reference is not on this machine")
    def test_every_pad_agrees_with_the_hand_checked_footprint(self):
        generated = pads_in(emit_footprint.render(firebeetle()))
        reference = pads_in(REFERENCE.read_text())
        self.assertEqual(len(generated), len(reference))
        for made, known in zip(generated, reference):
            self.assertEqual(made[0], known[0])
            for mine, theirs in zip(made[1:], known[1:]):
                self.assertAlmostEqual(mine, theirs, places=3)


class WhereThePadsGoTest(unittest.TestCase):
    def setUp(self):
        self.placed = emit_footprint.pads(firebeetle())

    def test_all_32_pads_are_placed(self):
        self.assertEqual(len(self.placed), 32)

    def test_the_two_rows_sit_a_row_spacing_apart(self):
        xs = sorted({x for _, x, _, in [(a, b, c) for a, b, c in self.placed]})
        self.assertAlmostEqual(xs[1] - xs[0], firebeetle()["physical"]["header"]["row_spacing_mm"])

    def test_both_rows_start_flush_at_the_same_edge(self):
        by_row = {}
        for label, x, y in self.placed:
            by_row.setdefault(x, []).append(y)
        firsts = [ys[0] for ys in by_row.values()]
        self.assertAlmostEqual(firsts[0], firsts[1])

    def test_pads_are_one_pitch_apart_and_run_away_from_that_edge(self):
        pitch = firebeetle()["physical"]["header"]["pitch_mm"]
        by_row = {}
        for label, x, y in self.placed:
            by_row.setdefault(x, []).append(y)
        for ys in by_row.values():
            for before, after in zip(ys, ys[1:]):
                self.assertAlmostEqual(before - after, pitch)

    def test_the_label_order_is_the_boards_own(self):
        # If this drifts, every trace still connects — to the wrong pad.
        expected = firebeetle()["physical"]["header_order"]["row_18"]
        self.assertEqual([label for label, _, _ in self.placed[:18]], expected)


class WhatItWillNotInventTest(unittest.TestCase):
    """
    Each of these is a fact that cannot be derived from the others. A generator that fills one in
    produces a footprint that looks finished and is wrong, which is the failure this plugin exists
    to prevent.
    """

    def _render_without(self, *path):
        board = copy.deepcopy(firebeetle())
        target = board["physical"]
        for key in path[:-1]:
            target = target[key]
        del target[path[-1]]
        return board

    def test_a_board_with_no_header_order_is_refused(self):
        board = self._render_without("header_order")
        gaps = emit_footprint._missing(board["physical"], board["physical"]["header"])
        self.assertTrue(any("header_order" in g for g in gaps), gaps)

    def test_a_board_with_no_header_geometry_is_refused(self):
        board = self._render_without("header")
        gaps = emit_footprint._missing(board["physical"], board["physical"].get("header"))
        self.assertTrue(gaps)

    def test_the_distance_to_the_first_pad_is_required(self):
        # It was prose in a comment until 2026-09-25, so nothing could read it and the pads could
        # not be tied to the outline at all.
        board = self._render_without("header", "first_pad_from_edge_mm")
        gaps = emit_footprint._missing(board["physical"], board["physical"]["header"])
        self.assertIn("physical.header.first_pad_from_edge_mm", gaps)

    def test_a_pad_order_that_disagrees_with_the_pin_count_is_refused(self):
        # The dangerous shape: 17 labels for 18 pads places every pad after the gap one pitch
        # wrong, and the file still looks complete.
        board = copy.deepcopy(firebeetle())
        board["physical"]["header_order"]["row_18"].pop()
        with self.assertRaises(ValueError) as caught:
            emit_footprint.pads(board)
        self.assertIn("17", str(caught.exception))

    def test_a_row_count_that_disagrees_with_the_pad_order_is_refused(self):
        board = copy.deepcopy(firebeetle())
        board["physical"]["header"]["pins"] = [18]
        with self.assertRaises(ValueError):
            emit_footprint.pads(board)

    def test_the_real_second_board_is_refused_rather_than_guessed(self):
        # The XIAO's file records no header geometry at all. This is not a hypothetical: it is
        # the other board the plugin ships, and it must come out as could-not-run.
        xiao = json.loads((ROOT / "boards" / "xiao-esp32-c6.json").read_text())
        physical = xiao.get("physical") or {}
        self.assertTrue(emit_footprint._missing(physical, physical.get("header")))


class TheCommandLineTest(unittest.TestCase):
    def test_a_board_that_cannot_be_generated_exits_could_not_run(self):
        self.assertEqual(emit_footprint.main(["--board", "xiao-esp32-c6", "--json"]),
                         emit_footprint.EXIT_COULD_NOT_RUN)

    def test_a_missing_board_exits_could_not_run(self):
        self.assertEqual(emit_footprint.main(["--board", "no-such-board", "--json"]),
                         emit_footprint.EXIT_COULD_NOT_RUN)

    def test_the_real_board_exits_ok(self):
        self.assertEqual(emit_footprint.main(["--board", "firebeetle2-esp32s3", "--json"]),
                         emit_footprint.EXIT_OK)


if __name__ == "__main__":
    unittest.main()
