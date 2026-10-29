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

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

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


class APadsLabelIsWrittenAsTextTest(unittest.TestCase):
    def test_a_label_with_a_quote_stays_inside_its_string(self):
        # P87's attribute half: each header label is written into `portHints={["…"]}`, and a label no pin of the board
        # names (D-, D+, RST) is held to no name rule — the FireBeetle's own D- and D+ are no names — so it is written as a
        # string literal, escaped, the one way a quote in it cannot end the string
        board = firebeetle()
        crafted = 'RST"]} onClick={() => globalThis.x = 1} portHints={["'
        for row, labels in board["physical"]["header_order"].items():
            if not row.startswith("//"):
                board["physical"]["header_order"][row] = [crafted if label == "RST" else label for label in labels]
        text = emit_footprint.render(board)
        self.assertIn("portHints={[%s]}" % json.dumps(crafted), text)
        self.assertNotIn('portHints={["%s"]}' % crafted, text)
        self.assertIn('portHints={["D-"]}', text, "an ordinary label is written as it always was")


class TheFootprintsCommentsStayCommentsTest(unittest.TestCase):
    def test_a_line_break_in_the_board_s_id_never_leaves_the_comment(self):
        # concern 1: the footprint's first line names the board file in a `//` comment, which a line break ends
        board = firebeetle()
        board["id"] = 'firebeetle2-esp32s3\nexport const injected = "FOOTPRINT-INJECTED" //'
        text = emit_footprint.render(board)
        self.assertIn("FOOTPRINT-INJECTED", text)
        self.assertEqual([line for line in text.splitlines() if "FOOTPRINT-INJECTED" in line and not line.startswith("//")], [])


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
        self.assertEqual([field for field, _ in gaps], ["physical.header_order"])
        self.assertTrue(gaps[0][1], gaps)  # a gap that is not derivable carries its note

    def test_a_board_with_no_header_geometry_is_refused(self):
        board = self._render_without("header")
        gaps = emit_footprint._missing(board["physical"], board["physical"].get("header"))
        self.assertEqual([field for field, _ in gaps], ["physical.header"])

    def test_the_distance_to_the_first_pad_is_required(self):
        # It was prose in a comment until 2026-09-25, so nothing could read it and the pads could
        # not be tied to the outline at all.
        board = self._render_without("header", "first_pad_from_edge_mm")
        gaps = emit_footprint._missing(board["physical"], board["physical"]["header"])
        self.assertEqual(gaps, [("physical.header.first_pad_from_edge_mm", "")])

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

    def test_a_library_board_with_no_header_geometry_is_refused_rather_than_guessed(self):
        # The XIAO's file once recorded no header geometry at all (P121); a board that lacks it must come out as could-not-run.
        from board_library import library_without
        file = library_without("physical.header") / "xiao-esp32-c6.json"
        board = json.loads(file.read_text())
        self.assertTrue(emit_footprint.footprint_gaps(board))
        self.assertEqual(emit_footprint.footprint_gaps(json.loads((ROOT / "boards" / "xiao-esp32-c6.json").read_text())), [])


class TheFootprintStopIsSaidTwoWaysTest(unittest.TestCase):
    """
    P411: the same gaps are said as a list (the build, emit_board, the `stops_why` of --match and --audit) and as a line (one
    row among many), and a board whose parts disagree is told so in one sentence from one helper.
    """

    def test_a_board_that_is_no_object_lacks_all_of_it(self):
        self.assertEqual(emit_footprint.footprint_gaps([]), ["physical.header (no header geometry at all)"])
        self.assertEqual(emit_footprint.footprint_gaps(None), ["physical.header (no header geometry at all)"])

    def test_the_list_names_the_board_and_each_gap_with_its_note(self):
        board = firebeetle()
        del board["physical"]["header_order"], board["physical"]["width_mm"]
        self.assertEqual(emit_footprint.why_no_footprint(board),
                         "firebeetle2-esp32s3 cannot have a footprint generated — these are not recorded, and none of them can be "
                         "derived from the rest:\n  physical.width_mm\n  physical.header_order (which label is on which pad — not derivable)")
        self.assertIsNone(emit_footprint.why_no_footprint(firebeetle()))

    def test_the_geometry_gaps_leave_out_the_modules_name_and_the_footprint_gaps_keep_it(self):
        board = firebeetle()
        del board["physical"]["footprint_export"], board["physical"]["height_mm"]
        self.assertEqual(emit_footprint.geometry_gaps(board), ["physical.height_mm"])
        self.assertEqual(emit_footprint.footprint_gaps(board),
                         ["physical.height_mm", "physical.footprint_export (what the module should be called)"])
        self.assertEqual(emit_footprint.geometry_gaps(None), ["physical.header (no header geometry at all)"])

    def test_the_line_names_the_one_field_that_is_missing_without_its_note(self):
        board = firebeetle()
        del board["physical"]["header"]
        self.assertEqual(emit_footprint.footprint_stop_line(board),
                         "stops at the footprint stage (P121): its board file lacks physical.header")

    def test_the_line_counts_the_fields_and_names_the_first_when_more_are_missing(self):
        board = firebeetle()
        del board["physical"]["header_order"], board["physical"]["width_mm"]
        self.assertEqual(emit_footprint.footprint_stop_line(board),
                         "stops at the footprint stage (P121): its board file lacks 2 fields (first: physical.width_mm)")

    def test_the_line_is_none_for_a_board_that_builds_and_says_the_stage_for_no_board(self):
        self.assertIsNone(emit_footprint.footprint_stop_line(firebeetle()))
        self.assertEqual(emit_footprint.footprint_stop_line("not a board"),
                         "stops at the footprint stage (P121): its board file lacks physical.header")

    def test_a_pad_order_that_does_not_fit_the_pin_counts_is_a_disagreement(self):
        board = firebeetle()
        board["physical"]["header"]["pins"] = [18]
        self.assertEqual(emit_footprint.why_header_disagrees(board),
                         "the board definition disagrees with itself: physical.header.pins lists 1 rows and header_order has 2 (%s)"
                         % ", ".join(key for key in board["physical"]["header_order"] if not key.startswith("//")))
        self.assertIsNone(emit_footprint.why_header_disagrees(firebeetle()))

    def test_a_value_of_the_wrong_kind_is_a_disagreement_that_names_the_field(self):
        # boards.validate checks no header geometry: a pitch written as text reached `pads` and raised a TypeError
        for where, field, value, said in (("header", "pitch_mm", "2.54", "physical.header.pitch_mm is not a number"),
                                          ("header", "first_pad_from_edge_mm", True, "physical.header.first_pad_from_edge_mm is not a number"),
                                          ("header", "pins", 18, "physical.header.pins is not a list of whole numbers"),
                                          ("header", "pins", ["6", "6"], "physical.header.pins is not a list of whole numbers"),
                                          (None, "width_mm", "21", "physical.width_mm is not a number"),
                                          (None, "header_order", [1, 2], "physical.header_order is not an object with a list of labels for each row"),
                                          (None, "header_order", {"left": 5, "right": 5},
                                           "physical.header_order is not an object with a list of labels for each row")):
            with self.subTest(field=field, value=value):
                board = firebeetle()
                (board["physical"][where] if where else board["physical"])[field] = value
                self.assertEqual(emit_footprint.why_header_disagrees(board), "the board definition disagrees with itself: " + said)

    def test_nothing_is_said_of_a_disagreement_when_something_is_missing_or_the_board_is_no_object(self):
        board = firebeetle()
        del board["physical"]["header_order"]
        for given in (board, "not a board", None, []):
            with self.subTest(given=given):
                self.assertIsNone(emit_footprint.why_header_disagrees(given))

    def test_the_list_of_a_board_that_is_no_object_names_no_board(self):
        self.assertEqual(emit_footprint.why_no_footprint("not a board"),
                         "None cannot have a footprint generated — these are not recorded, and none of them can be derived from the "
                         "rest:\n  physical.header (no header geometry at all)")


class TheCommandLineTest(unittest.TestCase):
    def test_a_board_that_cannot_be_generated_exits_could_not_run(self):
        from board_library import library_without
        library = library_without("physical.header")
        self.assertEqual(emit_footprint.main(["--board", "xiao-esp32-c6", "--json", "--project", str(library.parent)]),
                         emit_footprint.EXIT_COULD_NOT_RUN)

    def test_a_board_that_disagrees_with_itself_exits_problems_in_its_own_words(self):
        # P411: a pitch written as text was a TypeError out of `main`, and the spine ran on to say nothing of why
        import contextlib
        import io
        from board_library import library_without
        library = library_without("physical.header.drill_mm")  # a copy of the library; the file is whole but for a fact `render` only quotes
        file = library / "xiao-esp32-c6.json"
        board = json.loads(file.read_text())
        board["physical"]["header"]["pins"] = 7
        file.write_text(json.dumps(board))
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = emit_footprint.main(["--board", "xiao-esp32-c6", "--project", str(library.parent)])
        self.assertEqual((code, err.getvalue()), (emit_footprint.EXIT_PROBLEMS,
                                                  "problems: the board definition disagrees with itself: physical.header.pins is not a list of whole numbers\n"))

    def test_a_missing_board_exits_could_not_run(self):
        self.assertEqual(emit_footprint.main(["--board", "no-such-board", "--json"]),
                         emit_footprint.EXIT_COULD_NOT_RUN)

    def test_the_real_board_exits_ok(self):
        self.assertEqual(emit_footprint.main(["--board", "firebeetle2-esp32s3", "--json"]),
                         emit_footprint.EXIT_OK)


if __name__ == "__main__":
    unittest.main()
