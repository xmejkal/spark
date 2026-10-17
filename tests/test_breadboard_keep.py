"""
The next build keeps a person's moves (P273, #309): a part moved in breadboard.json stays where it was put across a
rebuild after a requirements change, or the build names it and says why.

    python3 -m unittest tests.test_breadboard_keep
"""

import json
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
import check_spine  # noqa: E402

DATA = ROOT / "tests" / "data" / "breadboard"
FULL = DATA / "button-light-xiao"
BUTTON_ONLY = DATA / "button-only-xiao"
LED_ONLY = DATA / "led-only-xiao"
GEOMETRY = breadboard_drawing.WokwiGeometry.load()
PITCH_PX = GEOMETRY.data["breadboard"]["pitch"]


def new_project(variant):
    """A copy of one fixture, in a scratch folder."""
    project = Path(tempfile.mkdtemp()) / "xiao"
    shutil.copytree(FULL, project)
    change_requirements(project, variant)
    return project


def change_requirements(project, variant):
    """The project as if its requirements changed and it was built again: the variant's requirements and circuit."""
    shutil.copy(variant / "requirements.json", project / "requirements.json")
    shutil.rmtree(project / "dist")
    shutil.copytree(variant / "dist", project / "dist")


def build(project):
    with mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()}):
        return breadboard.write(project / "requirements.json", project / "breadboard.md")


def diagram(project):
    return json.loads((project / "breadboard.json").read_text())


def part(project, part_id):
    return next(one for one in diagram(project)["parts"] if one["id"] == part_id)


def edit(project, change):
    """What a person does in the editor: change the diagram's file."""
    drawn = diagram(project)
    change(drawn)
    (project / "breadboard.json").write_text(json.dumps(drawn, indent=2) + "\n")


def move(part_id, dx=0.0, dy=0.0):
    def change(drawn):
        found = next(one for one in drawn["parts"] if one["id"] == part_id)
        found["left"] = round(found["left"] + dx, 3)
        found["top"] = round(found["top"] + dy, 3)
    return change


def place_of(project, part_id):
    found = part(project, part_id)
    return found["left"], found["top"], found.get("rotate", 0)


def holes_of(project, part_id):
    """{Wokwi pin: Hole} of one part as the diagram holds it."""
    found = part(project, part_id)
    shape = GEOMETRY.part(found["type"])
    turned = breadboard_drawing.rotate(shape["pins"], shape["center"], found.get("rotate", 0))
    return {pin: GEOMETRY.hole_at(found["left"] + x, found["top"] + y) for pin, (x, y) in turned.items()}


def put_led(project, hole_a):
    """Move the LED so its pin A is over a hole (its pin C then lies one column to the left)."""
    pins = GEOMETRY.part("wokwi-led")["pins"]
    edit(project, lambda drawn: next(one for one in drawn["parts"] if one["id"] == "LedRed5mm")
         .update(left=round(hole_a.x - pins["A"][0], 3), top=round(hole_a.y - pins["A"][1], 3)))


def codes(written):
    return {one.subject: one.code for one in written.not_kept}


class ThreeCasesTest(unittest.TestCase):
    def test_a_a_moved_part_survives_a_requirements_change(self):
        project = new_project(BUTTON_ONLY)
        build(project)
        edit(project, move("TactileButton", dx=4 * PITCH_PX))
        moved = place_of(project, "TactileButton")
        change_requirements(project, FULL)
        written = build(project)
        self.assertEqual(place_of(project, "TactileButton"), moved)
        self.assertEqual(written.not_kept, [])
        self.assertEqual({one["id"] for one in diagram(project)["parts"]},
                         {"bb1", "board", "TactileButton", "LedRed5mm", "R1"})
        self.assertEqual(len(diagram(project)["connections"]), 4)

    def test_b_a_moved_part_the_circuit_lost_is_named(self):
        project = new_project(FULL)
        build(project)
        edit(project, move("LedRed5mm", dx=2 * PITCH_PX))
        edit(project, move("R1", dx=2 * PITCH_PX))
        change_requirements(project, BUTTON_ONLY)
        written = build(project)
        self.assertEqual(codes(written), {"LedRed5mm": "not-in-circuit",
                                          "R1": "not-in-circuit"})
        self.assertEqual({one["id"] for one in diagram(project)["parts"]}, {"bb1", "board", "TactileButton"})

    def test_c_a_moved_part_that_cannot_stay_is_named_and_placed_fresh(self):
        project = new_project(FULL)
        build(project)
        fresh = place_of(project, "LedRed5mm")
        edit(project, move("LedRed5mm", dy=-500))
        written = build(project)
        self.assertEqual(codes(written), {"LedRed5mm": "pin-off-holes"})
        self.assertEqual(place_of(project, "LedRed5mm"), fresh)
        self.assertIn("pin", written.not_kept[0].why)


class OtherEditsTest(unittest.TestCase):
    def test_a_rebuild_with_no_move_names_nothing_and_writes_the_same_bytes(self):
        project = new_project(FULL)
        build(project)
        first = (project / "breadboard.json").read_bytes()
        written = build(project)
        self.assertEqual(written.not_kept, [])
        self.assertEqual((project / "breadboard.json").read_bytes(), first)

    def test_a_first_build_has_no_earlier_diagram_to_name(self):
        project = new_project(FULL)
        self.assertEqual(build(project).not_kept, [])

    def test_a_moved_part_stays_when_the_requirements_did_not_change(self):
        project = new_project(FULL)
        build(project)
        edit(project, move("TactileButton", dx=2 * PITCH_PX))
        moved = place_of(project, "TactileButton")
        self.assertEqual(build(project).not_kept, [])
        self.assertEqual(place_of(project, "TactileButton"), moved)

    def test_a_changed_wokwi_type_is_named(self):
        project = new_project(FULL)
        build(project)
        edit(project, lambda drawn: next(one for one in drawn["parts"] if one["id"] == "TactileButton")
             .update(type="wokwi-slide-switch"))
        self.assertEqual(codes(build(project)), {"TactileButton": "type-changed"})
        self.assertEqual(part(project, "TactileButton")["type"], "wokwi-pushbutton")

    def test_a_turn_that_is_not_a_quarter_turn_is_named(self):
        project = new_project(FULL)
        build(project)
        edit(project, lambda drawn: next(one for one in drawn["parts"] if one["id"] == "LedRed5mm")
             .update(rotate=45))
        self.assertEqual(codes(build(project)), {"LedRed5mm": "turn-unknown"})
        self.assertNotIn("rotate", part(project, "LedRed5mm"))

    def test_a_part_moved_onto_a_hole_another_part_holds_is_named_and_the_first_in_the_file_wins(self):
        project = new_project(FULL)
        build(project)
        led = part(project, "LedRed5mm")
        target = holes_of(project, "TactileButton")["1.l"]
        # the LED's pin A (the right one) goes on the button's pin hole
        put_led(project, target)
        before = place_of(project, "TactileButton")
        written = build(project)
        self.assertEqual(place_of(project, "TactileButton"), before)
        self.assertEqual(codes(written), {"LedRed5mm": "hole-taken"})
        self.assertEqual(place_of(project, "LedRed5mm")[:2], (led["left"], led["top"]))

    def test_a_part_moved_into_a_row_another_part_holds_is_named(self):
        project = new_project(FULL)
        build(project)
        button = holes_of(project, "TactileButton")
        taken = {hole.name for held in ("TactileButton", "LedRed5mm", "board") for hole in holes_of(project, held).values()}
        beside = next(hole for hole in GEOMETRY.surface.holes if hole.group == button["1.l"].group
                      and hole.name not in taken)
        put_led(project, beside)
        self.assertEqual(codes(build(project)), {"LedRed5mm": "row-shared"})

    def test_a_part_whose_body_covers_a_hole_another_part_holds_is_named(self):
        project = new_project(FULL)
        build(project)
        board = part(project, "board")
        shape = GEOMETRY.part(board["type"])
        covered = breadboard_drawing.FirstFitPartPlacement(GEOMETRY)._covered(
            shape, board["rotate"], board["left"], board["top"], holes_of(project, "board"))
        under = next((one, two) for one in covered for two in covered
                     if abs(two.x - one.x - PITCH_PX) < 0.5 and one.y == two.y)
        # the LED goes first in the file, with both pins under the board's body: the board must be refused
        put_led(project, under[1])
        edit(project, lambda drawn: drawn["parts"].insert(1, drawn["parts"].pop(
            next(i for i, one in enumerate(drawn["parts"]) if one["id"] == "LedRed5mm"))))
        self.assertEqual(codes(build(project)), {"board": "hole-taken"})

    def test_a_kept_part_far_right_leaves_room_for_a_new_part(self):
        project = new_project(BUTTON_ONLY)
        build(project)
        edit(project, move("TactileButton", dx=14 * PITCH_PX))
        moved = place_of(project, "TactileButton")
        change_requirements(project, FULL)
        written = build(project)
        self.assertEqual(place_of(project, "TactileButton"), moved)
        self.assertEqual(written.not_kept, [])
        self.assertIsNotNone(part(project, "LedRed5mm"))

    def test_when_the_kept_plan_has_no_room_the_fresh_plan_is_drawn_and_the_move_is_named(self):
        project = new_project(BUTTON_ONLY)
        build(project)
        edit(project, move("TactileButton", dx=12 * PITCH_PX))
        moved = place_of(project, "TactileButton")
        change_requirements(project, FULL)
        with mock.patch.object(breadboard_keep.KeepMovesFirstFitPartPlacement, "place",
                               side_effect=breadboard_drawing.NotDrawn("no room")):
            written = build(project)
        self.assertEqual(codes(written), {"TactileButton": "no-room"})
        self.assertNotEqual(place_of(project, "TactileButton"), moved)

    def test_a_resistor_is_never_kept_and_is_named_when_its_place_differs(self):
        project = new_project(FULL)
        build(project)
        edit(project, move("R1", dy=-2 * PITCH_PX))
        written = build(project)
        self.assertEqual(codes(written), {"R1": "resistor-not-kept"})

    def test_an_unreadable_earlier_file_is_named_and_the_build_goes_on(self):
        project = new_project(FULL)
        (project / "breadboard.json").write_text("{not json")
        written = build(project)
        self.assertEqual(codes(written), {"breadboard.json": "unreadable"})
        self.assertIn("LedRed5mm", {one["id"] for one in diagram(project)["parts"]})

    def test_an_earlier_diagram_on_another_breadboard_is_named_not_kept(self):
        project = new_project(FULL)
        build(project)
        edit(project, lambda drawn: drawn["parts"][0].update(type="wokwi-breadboard"))
        self.assertEqual(codes(build(project)), {"breadboard.json": "unreadable"})

    def test_every_code_has_a_message(self):
        self.assertEqual(set(breadboard_keep.MESSAGES), set(breadboard_keep.CODES))
        self.assertEqual(len(breadboard_keep.CODES), len(set(breadboard_keep.CODES)))

    def test_the_picture_shows_the_kept_place(self):
        project = new_project(FULL)
        build(project)
        edit(project, move("TactileButton", dx=2 * PITCH_PX))
        build(project)
        svg = (project / "breadboard.svg").read_text()
        self.assertIn("translate(%s " % _px(part(project, "TactileButton")["left"]), svg)


class TheBuildSaysItTest(unittest.TestCase):
    def test_keep_breadboard_carries_each_name_as_a_move_not_kept_entry(self):
        project = new_project(FULL)
        build(project)
        edit(project, move("LedRed5mm", dy=-500))
        stages = [check_spine.Stage("build", check_spine.OK, "built")]
        with mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()}):
            kept = check_spine.keep_breadboard(project / "requirements.json", project, stages)
        named = [entry for entry in kept if entry["did"] == "move not kept"]
        self.assertEqual(len(named), 1)
        self.assertIn("LedRed5mm", named[0]["line"])
        self.assertEqual(named[0]["file"], str(project / "breadboard.json"))

    def test_the_command_prints_each_name_on_stderr(self):
        import io
        from contextlib import redirect_stderr, redirect_stdout
        project = new_project(FULL)
        build(project)
        edit(project, move("LedRed5mm", dy=-500))
        errors = io.StringIO()
        with mock.patch.dict(os.environ, {"SPARK_HOME": tempfile.mkdtemp()}), redirect_stderr(errors), \
                redirect_stdout(io.StringIO()):
            self.assertEqual(breadboard.main([str(project / "requirements.json")]), breadboard.EXIT_OK)
        self.assertIn("LedRed5mm", errors.getvalue())
        self.assertIn("its pin", errors.getvalue())


def _px(value):
    return str(int(value)) if value == int(value) else str(value)


if __name__ == "__main__":
    unittest.main()
