"""
P957 (#1365): a pour short that tsci reports is measured on the circuit's own copper. The fixture is reduced from the
walk P934's build of its FireBeetle 2 ESP32-C6 board (tsci 0.0.2600): the board, pour 39, the MOSI trace and the error
tsci wrote, though the trace keeps 0.5124 mm from the pour. Each case moves or swaps one piece of it; the numbers are
literals.
"""

import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.build.pour_contact import PourContact  # noqa: E402

WALK = json.loads((ROOT / "tests" / "data" / "pour-contact" / "c6-epaper-mosi.json").read_text())
WORDS = ("Copper pour pcb_copper_pour_39 (GND) shorts to trace[.Mcu > port.MOSI, .Epaper2in9BwrMhEtLive > port.pin3] "
         "(source_trace_1_0) on top (accidental copper contact)")


def walk(**swap):
    """A copy of the walk's four elements, each one `swap` names (board, pour, trace, error) changed by its function."""
    elements = copy.deepcopy(WALK)
    for element in elements:
        role = {"pcb_board": "board", "pcb_copper_pour": "pour", "pcb_trace": "trace"}.get(element["type"], "error")
        if role in swap:
            swap[role](element)
    return elements


def error_of(circuit):
    return next(element for element in circuit if element["type"] == "pcb_placement_error")


def moved_down(by):
    def move(pour):
        for ring in [pour["brep_shape"]["outer_ring"]] + pour["brep_shape"]["inner_rings"]:
            for vertex in ring["vertices"]:
                vertex["y"] -= by
    return move


def square(x0, y0, x1, y1):
    return {"vertices": [{"x": x0, "y": y0}, {"x": x1, "y": y0}, {"x": x1, "y": y1}, {"x": x0, "y": y1}]}


def holed_pour(*holes):
    """The pour as a 200 mm square with `holes` (squares) cut out of it."""
    def swap(pour):
        pour["brep_shape"] = {"outer_ring": square(-100, -100, 100, 100), "inner_rings": list(holes)}
    return swap


def wire(x, y, width=0.15, layer="top"):
    return {"route_type": "wire", "x": x, "y": y, "width": width, "layer": layer}


def routed(*points):
    def swap(trace):
        trace["route"] = list(points)
    return swap


class TheWalksShortIsMeasuredTest(unittest.TestCase):
    def test_the_walks_short_is_dropped_with_its_gap(self):
        circuit = walk()
        self.assertEqual(error_of(circuit)["message"], WORDS)
        self.assertAlmostEqual(PourContact(circuit).measured(error_of(circuit)), 0.5124, places=4)
        kept, notes = PourContact(circuit).disproved([error_of(circuit)])
        self.assertEqual(kept, [])
        self.assertEqual(notes, ["a pour short tsci reported is dropped: pcb_copper_pour_39 and source_trace_1_0 on top are "
                                 "0.5124 mm apart, at least the board's clearance of 0.1 mm"])

    def test_a_gap_below_the_boards_clearance_is_kept(self):
        circuit = walk(pour=moved_down(0.5))
        self.assertAlmostEqual(PourContact(circuit).measured(error_of(circuit)), 0.0124, places=4)
        self.assertEqual(PourContact(circuit).disproved([error_of(circuit)]), ([error_of(circuit)], []))

    def test_the_bar_is_the_boards_own_clearance(self):
        circuit = walk(board=lambda board: board.update(min_trace_to_pad_edge_clearance=0.6))
        self.assertEqual(PourContact(circuit).disproved([error_of(circuit)]), ([error_of(circuit)], []))

    def test_a_real_contact_is_kept(self):
        circuit = walk(pour=moved_down(0.6))
        self.assertLessEqual(PourContact(circuit).measured(error_of(circuit)), 0)
        self.assertEqual(PourContact(circuit).disproved([error_of(circuit)]), ([error_of(circuit)], []))


#: A straight 5 mm trace, and the pour as a square with a hole of 1 mm round it (0.925 mm from the trace's edge).
STRAIGHT = routed(wire(0, 0), wire(5, 0))
HOLE = holed_pour(square(-1, -1, 6, 1))


class ContainmentAndRingsTest(unittest.TestCase):

    def test_a_trace_wholly_inside_the_pour_is_a_contact(self):
        circuit = walk(pour=holed_pour(), trace=STRAIGHT)
        self.assertLessEqual(PourContact(circuit).measured(error_of(circuit)), 0)
        self.assertEqual(PourContact(circuit).disproved([error_of(circuit)]), ([error_of(circuit)], []))

    def test_a_trace_in_a_hole_of_the_pour_is_measured_to_the_holes_edge(self):
        circuit = walk(pour=HOLE, trace=STRAIGHT)
        self.assertAlmostEqual(PourContact(circuit).measured(error_of(circuit)), 0.925, places=6)
        self.assertEqual(PourContact(circuit).disproved([error_of(circuit)])[0], [])

    def test_a_trace_crossing_the_holes_edge_is_a_contact(self):
        circuit = walk(pour=holed_pour(square(-1, -1, 3, 1)), trace=STRAIGHT)
        self.assertLessEqual(PourContact(circuit).measured(error_of(circuit)), 0)


class ViasAndOtherLayersTest(unittest.TestCase):
    def via(self, x, y, **diameter):
        return dict({"route_type": "via", "x": x, "y": y, "from_layer": "top", "to_layer": "bottom"}, **diameter)

    def test_a_via_whose_disk_reaches_the_pour_is_a_contact(self):
        for diameter in ({"via_diameter": 0.6}, {"outer_diameter": 0.6}):
            with self.subTest(diameter=diameter):
                trace = routed(wire(0, 0), wire(5, 0), self.via(5, 0.8, **diameter), wire(5, 0.8, layer="bottom"))
                circuit = walk(pour=HOLE, trace=trace)
                self.assertLessEqual(PourContact(circuit).measured(error_of(circuit)), 0)

    def test_a_via_far_from_the_pours_edge_is_measured_and_dropped(self):
        trace = routed(wire(0, 0), wire(2.5, 0), self.via(2.5, 0, via_diameter=0.6), wire(2.5, 0, layer="bottom"),
                       wire(2.5, 50, layer="bottom"))
        circuit = walk(pour=HOLE, trace=trace)
        self.assertAlmostEqual(PourContact(circuit).measured(error_of(circuit)), 0.7, places=6)
        self.assertEqual(PourContact(circuit).disproved([error_of(circuit)])[0], [])

    def test_a_wire_on_the_other_layer_is_not_the_pours_copper(self):
        trace = routed(wire(0, 0), wire(5, 0), wire(5, 0, layer="bottom"), wire(5, 50, layer="bottom"))
        circuit = walk(pour=HOLE, trace=trace)
        self.assertAlmostEqual(PourContact(circuit).measured(error_of(circuit)), 0.925, places=6)

    def test_a_through_pad_is_measured_as_its_stroke(self):
        through = {"route_type": "through_pad", "start": {"x": 5, "y": 0}, "end": {"x": 5, "y": 0.9}, "width": 0.15,
                   "start_layer": "top", "end_layer": "bottom"}
        circuit = walk(pour=HOLE, trace=routed(wire(0, 0), wire(5, 0), through))
        self.assertAlmostEqual(PourContact(circuit).measured(error_of(circuit)), 0.025, places=6)


class WhatCannotBeMeasuredIsKeptTest(unittest.TestCase):
    """Every input spark cannot measure keeps its error: None, never a guessed gap."""

    def test_a_short_to_a_pad_or_a_via_is_kept(self):
        for target in ("pcb_smtpad_3", "pcb_via_0", "pcb_plated_hole_7"):
            with self.subTest(target=target):
                circuit = walk(error=lambda error: error.update(message=WORDS.replace("source_trace_1_0", target)))
                self.assertIsNone(PourContact(circuit).measured(error_of(circuit)))
                self.assertEqual(PourContact(circuit).disproved([error_of(circuit)]), ([error_of(circuit)], []))

    def test_other_words_and_other_errors_are_kept(self):
        for error in ({"type": "pcb_placement_error", "message": WORDS.replace("shorts to", "touches")},
                      {"type": "pcb_placement_error", "message": WORDS.replace("on top", "on inner1")},
                      {"type": "pcb_placement_error"},
                      {"type": "pcb_trace_error", "message": WORDS},
                      {"type": "source_trace_not_connected_error", "selectors_not_found": [".Mcu > .MOSI"]}):
            with self.subTest(error=error):
                self.assertIsNone(PourContact(walk()).measured(error))
                self.assertEqual(PourContact(walk()).disproved([error]), ([error], []))

    def test_a_shape_spark_does_not_read_is_kept(self):
        def bulge(pour):
            pour["brep_shape"]["outer_ring"]["vertices"][3]["bulge"] = 0.5

        def no_width(trace):
            del trace["route"][2]["width"], trace["route"][3]["width"]
        for swap in ({"pour": bulge}, {"pour": lambda pour: pour.update(shape="rect")},
                     {"pour": lambda pour: pour["brep_shape"]["outer_ring"]["vertices"][0].update(x="-56.8")},
                     {"trace": no_width}, {"trace": lambda trace: trace["route"][1].update(route_type="arc")},
                     {"board": lambda board: board.pop("min_trace_to_pad_edge_clearance")},
                     {"board": lambda board: board.update(min_trace_to_pad_edge_clearance=True)}):
            with self.subTest(swap=swap):
                circuit = walk(**swap)
                self.assertEqual(PourContact(circuit).disproved([error_of(circuit)]), ([error_of(circuit)], []))

    def test_a_missing_or_twice_named_element_is_kept(self):
        circuit = walk()
        for elements in ([element for element in circuit if element["type"] != "pcb_trace"],
                         [element for element in circuit if element["type"] != "pcb_copper_pour"],
                         [element for element in circuit if element["type"] != "pcb_board"],
                         circuit + [element for element in circuit if element["type"] == "pcb_trace"]):
            with self.subTest(types=[element["type"] for element in elements]):
                self.assertEqual(PourContact(elements).disproved([error_of(circuit)]), ([error_of(circuit)], []))

    def test_the_pour_on_another_layer_than_the_words_is_kept(self):
        circuit = walk(pour=lambda pour: pour.update(layer="bottom"))
        self.assertEqual(PourContact(circuit).disproved([error_of(circuit)]), ([error_of(circuit)], []))


if __name__ == "__main__":
    unittest.main()
