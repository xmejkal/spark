"""
The next build keeps a jumper and a resistor a person moved (P287, #340): the spike's cases b, b2, b3 and c, and a moved
resistor. A moved jumper keeps its holes and route when it joins two rows the new layout joins; else the build names it.

    python3 -m unittest tests.test_breadboard_keep_jumpers
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite_temp  # noqa: E402,F401

import test_breadboard_keep as base  # noqa: E402
from test_breadboard_keep import (BUTTON_ONLY, FULL, LED_ONLY, PITCH_PX, build, change_requirements, codes,  # noqa: E402
                                  diagram, edit, move, new_project, part, place_of)

ROUTE = ["v-20", "h40"]


def wires(project):
    return diagram(project)["connections"]


def row_pairs(project):
    """The pairs of rows the jumpers join, as the diagram holds them."""
    return sorted(sorted(end.split(":")[1].split(".")[0] for end in wire[:2]) for wire in wires(project))


def change_wire(project, index, one=None, other=None, route=None):
    """What a person does in the editor: move one end of a jumper, or give it a route."""
    def change(drawn):
        wire = drawn["connections"][index]
        wire[0] = one or wire[0]
        wire[1] = other or wire[1]
        wire[3] = wire[3] if route is None else route
    edit(project, change)


def wire_between(project, one_row, other_row):
    """The (index, jumper) joining two rows."""
    for index, wire in enumerate(wires(project)):
        if sorted(end.split(":")[1].split(".")[0] for end in wire[:2]) == sorted([one_row, other_row]):
            return index, wire
    raise AssertionError("no jumper between %s and %s in %s" % (one_row, other_row, wires(project)))


def built_full():
    project = new_project(FULL)
    build(project)
    return project


class MovedJumperTest(unittest.TestCase):
    def test_b_a_jumper_moved_within_its_row_keeps_its_hole_and_route(self):
        project = built_full()
        change_wire(project, 1, other="bb1:14t.b", route=ROUTE)
        change_requirements(project, BUTTON_ONLY)
        written = build(project)
        self.assertEqual(codes(written), {"LedRed5mm": "not-in-circuit", "R1": "not-in-circuit"})
        self.assertEqual(wire_between(project, "6b", "14t")[1], ["bb1:6b.j", "bb1:14t.b", "gold", ROUTE])

    def test_b2_a_jumper_moved_to_another_row_the_new_circuit_joins_is_kept(self):
        project = built_full()
        index, wire = wire_between(project, "8b", "17b")
        change_wire(project, index, other="bb1:12t.c")
        change_requirements(project, BUTTON_ONLY)
        written = build(project)
        self.assertEqual(wire_between(project, "8b", "12t")[1][:2], ["bb1:8b.j", "bb1:12t.c"])
        self.assertEqual(codes(written), {"LedRed5mm": "not-in-circuit", "R1": "not-in-circuit"})

    def test_b3_a_jumper_moved_to_a_row_nothing_holds_is_named_and_the_planned_one_drawn(self):
        project = built_full()
        change_wire(project, 1, other="bb1:15t.a")
        written = build(project)
        self.assertEqual(codes(written), {"jumper 6b.j-15t.a": "rows-not-joined"})
        self.assertIn("rows 6b and 15t", written.not_kept[0].why)
        self.assertEqual(wire_between(project, "6b", "14t")[1][:2], ["bb1:6b.j", "bb1:14t.a"])

    def test_c_a_jumper_the_new_circuit_does_not_join_is_named_and_a_moved_one_it_joins_is_kept(self):
        project = built_full()
        for part_id in ("LedRed5mm", "R1"):
            edit(project, move(part_id, dx=2 * PITCH_PX))
        change_wire(project, wire_between(project, "4b", "24b")[0], other="bb1:26b.f")
        change_wire(project, wire_between(project, "8b", "17b")[0], other="bb1:19b.g")
        moved = {one: place_of(project, one) for one in ("LedRed5mm", "R1")}
        change_requirements(project, LED_ONLY)
        written = build(project)
        self.assertEqual({one: place_of(project, one) for one in moved}, moved)
        self.assertEqual(codes(written), {"jumper 4b.j-26b.f": "rows-not-joined",
                                          "TactileButton": "not-in-circuit"})
        self.assertEqual(wire_between(project, "8b", "19b")[1][:2], ["bb1:8b.j", "bb1:19b.g"])

    def test_a_jumper_moved_onto_a_hole_a_part_holds_is_named(self):
        project = built_full()
        change_wire(project, 1, other="bb1:14t.e")
        written = build(project)
        self.assertEqual(codes(written), {"jumper 6b.j-14t.e": "hole-taken"})
        self.assertEqual(wire_between(project, "6b", "14t")[1][:2], ["bb1:6b.j", "bb1:14t.a"])

    def test_a_jumper_moved_under_the_board_body_is_named(self):
        project = built_full()
        covered = base.breadboard_drawing.FirstFitPartPlacement(base.GEOMETRY)._covered(
            base.GEOMETRY.part("board-xiao-esp32-c6"), 90, part(project, "board")["left"],
            part(project, "board")["top"], base.holes_of(project, "board"))
        under = next(hole for hole in covered if hole.group.startswith("6b"))
        change_wire(project, 1, one="bb1:" + under.name)
        self.assertEqual(codes(build(project)), {"jumper %s-14t.a" % under.name: "hole-taken"})

    def test_a_jumper_written_the_other_way_round_keeps_its_direction_and_route(self):
        project = built_full()
        edit(project, lambda drawn: drawn["connections"].__setitem__(
            1, [drawn["connections"][1][1], drawn["connections"][1][0], drawn["connections"][1][2], ROUTE]))
        self.assertEqual(build(project).not_kept, [])
        self.assertEqual(wires(project)[1], ["bb1:14t.a", "bb1:6b.j", "blue", ROUTE])

    def test_two_earlier_jumpers_on_one_pair_of_rows_keep_the_first(self):
        project = built_full()
        edit(project, lambda drawn: drawn["connections"].append(["bb1:6b.h", "bb1:14t.c", "blue", []]))
        change_wire(project, 1, other="bb1:14t.b")
        written = build(project)
        self.assertEqual(wire_between(project, "6b", "14t")[1][:2], ["bb1:6b.j", "bb1:14t.b"])
        self.assertEqual(codes(written), {"jumper 6b.h-14t.c": "rows-not-joined"})
        self.assertEqual(len(wires(project)), 4)

    def test_a_connection_to_a_part_pin_is_named(self):
        project = built_full()
        edit(project, lambda drawn: drawn["connections"].append(["board:D8", "LedRed5mm:A", "green", []]))
        self.assertEqual(codes(build(project)), {"jumper board:D8-LedRed5mm:A": "jumper-not-on-board"})
        self.assertEqual(len(wires(project)), 4)

    def test_a_connection_with_no_route_is_read(self):
        project = built_full()
        edit(project, lambda drawn: drawn["connections"][1].pop())
        self.assertEqual(build(project).not_kept, [])

    def test_a_missing_connections_key_keeps_the_parts(self):
        project = built_full()
        edit(project, lambda drawn: drawn.pop("connections"))
        edit(project, move("TactileButton", dx=2 * PITCH_PX))
        moved = place_of(project, "TactileButton")
        self.assertEqual(build(project).not_kept, [])
        self.assertEqual(place_of(project, "TactileButton"), moved)

    def test_a_connection_that_is_not_a_list_of_strings_makes_the_file_unreadable(self):
        project = built_full()
        edit(project, lambda drawn: drawn["connections"].append([1, 2]))
        self.assertEqual(codes(build(project)), {"breadboard.json": "unreadable"})

    def test_a_route_that_is_not_a_list_of_strings_makes_the_file_unreadable(self):
        project = built_full()
        change_wire(project, 1, route="v-20")
        self.assertEqual(codes(build(project)), {"breadboard.json": "unreadable"})


class EscapedMutantsTest(unittest.TestCase):
    """Tests the mutation table's first run found missing (P287)."""

    def test_a_jumper_not_kept_takes_a_free_hole_beside_a_kept_one(self):
        project = built_full()
        edit(project, lambda drawn: drawn["connections"].pop(2))
        index, _ = wire_between(project, "12t", "17b")
        change_wire(project, index, other="bb1:17b.g")
        self.assertEqual(build(project).not_kept, [])
        self.assertEqual(wire_between(project, "12t", "17b")[1][:2], ["bb1:12t.a", "bb1:17b.g"])
        self.assertEqual(wire_between(project, "8b", "17b")[1][:2], ["bb1:8b.j", "bb1:17b.h"])

    def test_a_jumper_moved_to_an_empty_row_beyond_the_last_part_is_drawn_again_without_a_name(self):
        project = built_full()
        change_wire(project, 1, other="bb1:28t.a")
        self.assertEqual(build(project).not_kept, [])
        self.assertEqual(wire_between(project, "6b", "14t")[1][:2], ["bb1:6b.j", "bb1:14t.a"])

    def test_a_jumper_into_a_row_held_by_a_part_that_could_not_stay_is_explained_by_that_part(self):
        project = built_full()
        # R1 turned the other way with its pin 2 still in the LED's row: its pin 1 lies in the button's row
        edit(project, lambda drawn: next(one for one in drawn["parts"] if one["id"] == "R1")
             .update(rotate=0, left=round(part(project, "R1")["left"] - 58.8, 3)))
        index, _ = wire_between(project, "12t", "17b")
        change_wire(project, index, other="bb1:18b.h")
        self.assertEqual(codes(build(project)), {"R1": "row-shared"})

    def test_when_the_kept_plan_has_no_room_a_moved_jumper_is_named_no_room(self):
        project = built_full()
        change_wire(project, 1, other="bb1:14t.b")
        with base.mock.patch.object(base.breadboard_keep.KeepMovesFirstFitPartPlacement, "place",
                                    side_effect=base.breadboard_drawing.NotDrawn("no room")):
            written = build(project)
        self.assertEqual(codes(written), {"jumper 6b.j-14t.b": "no-room"})


class QuietTest(unittest.TestCase):
    def test_a_requirements_change_names_no_jumper_nobody_moved(self):
        project = built_full()
        change_requirements(project, BUTTON_ONLY)
        self.assertEqual(codes(build(project)), {"LedRed5mm": "not-in-circuit", "R1": "not-in-circuit"})

    def test_a_rebuild_after_a_jumper_edit_names_nothing_and_writes_the_same_bytes(self):
        project = built_full()
        change_wire(project, 1, other="bb1:14t.b", route=ROUTE)
        self.assertEqual(build(project).not_kept, [])
        first = (project / "breadboard.json").read_bytes()
        self.assertEqual(build(project).not_kept, [])
        self.assertEqual((project / "breadboard.json").read_bytes(), first)
        self.assertEqual(wires(project)[1][:2], ["bb1:6b.j", "bb1:14t.b"])

    def test_a_kept_jumper_joins_the_rows_the_plan_joins(self):
        plain = new_project(FULL)
        build(plain)
        project = built_full()
        change_wire(project, 1, other="bb1:14t.b", route=ROUTE)
        build(project)
        self.assertEqual(row_pairs(project), row_pairs(plain))
        self.assertEqual([wire[2] for wire in wires(project)], [wire[2] for wire in wires(plain)])

    def test_a_kept_jumper_stays_at_its_place_in_the_list(self):
        project = built_full()
        change_wire(project, 2, other="bb1:17b.h")
        build(project)
        self.assertEqual(wires(project)[2][:3], ["bb1:8b.j", "bb1:17b.h", "purple"])


class MovedResistorTest(unittest.TestCase):
    def test_a_resistor_moved_along_its_rows_keeps_its_place(self):
        project = built_full()
        edit(project, move("R1", dy=PITCH_PX))
        moved = place_of(project, "R1")
        self.assertEqual(build(project).not_kept, [])
        self.assertEqual(place_of(project, "R1"), moved)

    def test_a_resistor_and_its_jumper_moved_together_are_both_kept(self):
        project = built_full()
        edit(project, move("R1", dy=PITCH_PX))
        change_wire(project, 0, other="bb1:24b.i")
        moved = place_of(project, "R1")
        self.assertEqual(build(project).not_kept, [])
        self.assertEqual(place_of(project, "R1"), moved)
        self.assertEqual(wires(project)[0][:2], ["bb1:4b.j", "bb1:24b.i"])

    def test_a_resistor_whose_joined_pin_left_its_row_is_named_and_placed_again(self):
        project = built_full()
        before = place_of(project, "R1")
        edit(project, move("LedRed5mm", dx=2 * PITCH_PX))
        written = build(project)
        self.assertEqual(codes(written), {"R1": "pin-off-row"})
        self.assertNotEqual(place_of(project, "R1"), before)
        self.assertIn("pin 2", written.not_kept[0].why)

    def test_a_resistor_off_every_hole_is_named(self):
        project = built_full()
        edit(project, move("R1", dy=-500))
        self.assertEqual(codes(build(project)), {"R1": "pin-off-holes"})

    def test_a_resistor_whose_other_pin_is_in_a_row_a_part_holds_is_named(self):
        project = built_full()
        # turned the other way with its pin 2 still in the LED's row, its pin 1 lies in the row the button holds
        edit(project, lambda drawn: next(one for one in drawn["parts"] if one["id"] == "R1")
             .update(rotate=0, left=round(part(project, "R1")["left"] - 58.8, 3)))
        self.assertEqual(codes(build(project)), {"R1": "row-shared"})

    def test_a_resistor_that_is_not_in_the_new_circuit_is_named_not_in_circuit(self):
        project = built_full()
        edit(project, move("R1", dy=PITCH_PX))
        change_requirements(project, BUTTON_ONLY)
        self.assertEqual(codes(build(project)).get("R1"), "not-in-circuit")


if __name__ == "__main__":
    unittest.main()
