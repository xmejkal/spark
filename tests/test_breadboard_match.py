"""
The drawing check (P279, #317): the build names each end the drawn breadboard joins differently from circuit.json's
points, and says nothing when they match. The defects are planted in the fixture's layout, because the planner and
P273's keep step never draw them.

    python3 -m unittest tests.test_breadboard_match
"""

import contextlib
import io
import os
import shutil
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
import breadboard_drawing  # noqa: E402
import breadboard_keep  # noqa: E402
import breadboard_steps  # noqa: E402
import check_spine  # noqa: E402
from breadboard_drawing import Jumper, WokwiGeometry  # noqa: E402
from breadboard_match import JOINED_TO_OTHER, JOINED_TO_UNUSED, NOT_JOINED, DrawnNets  # noqa: E402

XIAO = ROOT / "tests" / "data" / "breadboard" / "button-light-xiao"
GEOMETRY = WokwiGeometry.load()
HOLES = {hole.name: hole for hole in GEOMETRY.surface.holes}


def in_store():
    return mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()})


def with_jumpers(layout, *pairs, drop=()):
    """The layout with the jumpers of step numbers in `drop` taken out and one jumper added per pair of hole names."""
    kept = [jumper for jumper in layout.jumpers if jumper.step not in drop]
    return layout._replace(jumpers=kept + [Jumper(HOLES[one], HOLES[other], 99) for one, other in pairs])


def moved(layout, step, other):
    """The layout with the far end of one step's jumper in another hole."""
    return layout._replace(jumpers=[jumper._replace(other=HOLES[other]) if jumper.step == step else jumper
                                    for jumper in layout.jumpers])


class TheCheckTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with in_store():
            cls.read = breadboard._read_build(XIAO / "requirements.json")
        cls.layout = breadboard._plan_layout(cls.read)
        cls.catalog = breadboard._describe_parts(cls.read, GEOMETRY)
        cls.points = cls.read.steps.points

    def differences(self, layout, points=None):
        return DrawnNets(layout, GEOMETRY).differences(self.points if points is None else points, self.catalog)

    def test_the_planned_layout_joins_the_points_and_nothing_is_said(self):
        self.assertEqual(self.differences(self.layout), [])

    def test_a_jumper_into_another_row_names_the_end_it_left(self):
        # step 5 joins board D8 (row 4b) to R1 end 1 (row 24b); its far end now lands in an empty row
        found = self.differences(moved(self.layout, 5, "29b.f"))
        self.assertEqual([(one.code, one.subject) for one in found], [(NOT_JOINED, "R1 end 1")])
        self.assertEqual(found[0].why, "R1 end 1 is not joined to board D8 in the drawing")

    def test_a_jumper_between_two_points_rows_is_a_short_named_once(self):
        # rows 24b (board D8 · R1 end 1) and 18b (LED A · R1 end 2) are two points
        found = self.differences(with_jumpers(self.layout, ("24b.j", "18b.j")))
        self.assertEqual([one.code for one in found], [JOINED_TO_OTHER])
        # the later point's end that lands in the earlier net is named, beside the earlier point's end
        self.assertEqual(found[0].why, "LedRed5mm A is joined to board D8 in the drawing, and they are two points")

    def test_a_wire_on_the_button_s_other_side_joins_its_contact(self):
        # 1.r (row 14b) is one contact with 1.l (row 14t, TactileButton A); a wire from it to the LED's row shorts them
        found = self.differences(with_jumpers(self.layout, ("14b.j", "18b.i")))
        self.assertEqual([one.code for one in found], [JOINED_TO_OTHER])

    def test_a_point_joined_to_a_pin_no_point_names_is_a_short(self):
        # row 17b holds GND (LED K); the board's 5V pad is in no point
        board = next(part for part in self.layout.parts if part.id == breadboard_steps.THE_BOARD)
        five = board.holes["5V"]
        beside = next(hole.name for hole in HOLES.values() if hole.group == five.group and hole.name != five.name)
        found = self.differences(with_jumpers(self.layout, ("17b.i", beside)))
        self.assertEqual([(one.code, one.why) for one in found],
                         [(JOINED_TO_UNUSED, "board GND is joined to board 5V in the drawing, which no point names")])

    def test_an_end_s_group_is_the_free_row_its_setup_jumper_took(self):
        board = next(part for part in self.layout.parts if part.id == breadboard_steps.THE_BOARD)
        end = breadboard_steps.End("board", board.id, "board D8", "board D8", "D8")
        placed = {board.id: board}
        self.assertEqual(breadboard_drawing.end_group(end, placed, self.catalog, {"board D8": "28t"}), "28t")
        self.assertEqual(breadboard_drawing.end_group(end, placed, self.catalog), board.holes["D8"].group)

    def test_board_pads_joined_through_a_free_row_match_and_a_moved_setup_jumper_does_not(self):
        named = {end.pin for point in self.points for end in point.ends if end.component == breadboard_steps.THE_BOARD}
        board = next(part for part in self.layout.parts if part.id == breadboard_steps.THE_BOARD)
        one, other = [pin for pin in board.holes if pin not in named and pin in self.catalog[board.id].pins][:2]
        ends = [breadboard_steps.End("board", board.id, "board " + pin, "board " + pin, pin)
                for pin in (one, other)]
        point = [breadboard_steps.StepPoint(ends, None, None)]
        rows = [board.holes[pin].group for pin in (one, other)]
        joined = with_jumpers(self.layout, (rows[0] + ".a", "28t.a"), (rows[1] + ".a", "28t.b"))
        self.assertEqual(self.differences(joined, point), [])
        apart = with_jumpers(self.layout, (rows[0] + ".a", "28t.a"), (rows[1] + ".a", "30t.b"))
        self.assertEqual([(found.code, found.subject) for found in self.differences(apart, point)],
                         [(NOT_JOINED, "board " + other)])


class TheBuildSaysItTest(unittest.TestCase):
    """A planted layout reaches the sheet, stderr and the kept entries; the files are still written, exit 0."""

    def setUp(self):
        self.project = Path(tempfile.mkdtemp()) / "xiao"
        shutil.copytree(XIAO, self.project)
        with in_store():
            layout = breadboard._plan_layout(breadboard._read_build(XIAO / "requirements.json"))
        self.planted = moved(layout, 5, "29b.f")
        self.plan = mock.patch.object(breadboard, "_plan_layout", return_value=self.planted)
        self.plan.start()
        self.addCleanup(mock.patch.stopall)

    def test_the_sheet_and_stderr_name_it_and_the_drawing_is_still_written(self):
        stderr = io.StringIO()
        with in_store(), contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(io.StringIO()):
            code = breadboard.main([str(self.project / "requirements.json")])
        self.assertEqual(code, breadboard.EXIT_OK)
        self.assertIn("drawing differs: R1 end 1 is not joined to board D8 in the drawing", stderr.getvalue())
        sheet = (self.project / "breadboard.md").read_text()
        self.assertIn("The drawing does not join the points the same way: R1 end 1 is not joined to board D8 in the "
                      "drawing. Wire from the steps above.", sheet)
        self.assertTrue((self.project / "breadboard.json").is_file())

    def test_two_differences_give_the_first_and_a_count_on_the_sheet(self):
        both = moved(self.planted, 6, "30b.f")
        with in_store(), mock.patch.object(breadboard, "_plan_layout", return_value=both):
            written = breadboard.write(self.project / "requirements.json", self.project / "breadboard.md")
        self.assertEqual([one.subject for one in written.differs], ["R1 end 1", "TactileButton A"])
        self.assertIn("in the drawing, and 1 more. Wire from the steps above.",
                      (self.project / "breadboard.md").read_text())

    def test_a_kept_layout_is_checked_not_the_fresh_one(self):
        self.plan.stop()  # the first build plans for real, so the second one keeps its layout
        with in_store():
            breadboard.write(self.project / "requirements.json", self.project / "breadboard.md")
        keep = breadboard_keep.KeepMovesJumperPlacement.place_jumpers

        def keep_then_move(placement, layout, ledger):
            return moved(keep(placement, layout, ledger), 5, "29b.f")

        with in_store(), mock.patch.object(breadboard_keep.KeepMovesJumperPlacement, "place_jumpers", keep_then_move):
            written = breadboard.write(self.project / "requirements.json", self.project / "breadboard.md")
        self.assertEqual([(one.code, one.subject) for one in written.differs], [(NOT_JOINED, "R1 end 1")])

    def test_the_kept_entry_carries_its_code(self):
        with in_store():
            kept = check_spine.keep_breadboard(self.project / "requirements.json", self.project,
                                               [check_spine.Stage("build", check_spine.OK)])
        differs = [entry for entry in kept if entry["did"] == "drawing differs"]
        self.assertEqual([(entry["code"], entry["subject"]) for entry in differs], [(NOT_JOINED, "R1 end 1")])
        self.assertEqual(differs[0]["line"], "drawing differs: R1 end 1 is not joined to board D8 in the drawing")


if __name__ == "__main__":
    unittest.main()
