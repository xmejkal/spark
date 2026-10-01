"""
P46: the numbers a fab house could change live in one file, and every script reads that file.

These are the tests for the defect class, not for the values: that a table has ONE home rather
than two copies, that the ring a generator draws is the ring a checker demands plus a margin
rather than a second literal, and that a project's own process reaches both.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import check_footprints  # noqa: E402
import check_physics  # noqa: E402
import copper  # noqa: E402
import emit_board  # noqa: E402
import emit_footprint  # noqa: E402
import fab  # noqa: E402


class TheDataIsInTheFileNotInTheCodeTest(unittest.TestCase):
    def test_the_file_is_real_and_says_what_it_holds(self):
        raw = json.loads(fab.FILE.read_text())
        self.assertEqual(raw["schema"], 1)
        self.assertIn("boundary", "".join(raw))
        self.assertTrue(set(fab.DATA) >= {"process", "parts"})

    def test_every_number_carries_its_prose(self):
        # The comments that were deleted from the scripts had to land somewhere, or this trades a
        # duplicated number for an unexplained one (W16).
        raw = json.loads(fab.FILE.read_text())
        for section in ("process", "parts"):
            explained = {name[2:] for name in raw[section] if name.startswith("//")}
            unexplained = sorted(set(fab.DATA[section]) - explained)
            # min_via_pad_mm is explained by its sibling's note, which names both.
            self.assertEqual(unexplained, ["min_via_pad_mm"] if section == "process" else [])

    def test_no_script_restates_a_number_the_file_holds(self):
        # The defect itself: a literal here and a literal there, agreeing only by luck.
        for name, literal in (("package_power_w", "0.063"), ("header_pin_side_mm", "0.64"),
                              ("min_annular_ring_mm", "0.25"), ("min_via_hole_mm", "0.3")):
            for script in sorted((ROOT / "scripts").glob("*.py")):
                with self.subTest(number=name, script=script.name):
                    self.assertNotIn("= %s\n" % literal, script.read_text(),
                                     "%s is stated in code again" % name)


class OneTableNotTwoCopiesTest(unittest.TestCase):
    def test_both_checkers_judge_by_the_same_package_ratings(self):
        # They were two separate dicts. A package added to one was missing from the other and
        # nothing said so.
        self.assertIs(check_footprints.PACKAGE_POWER_W, check_physics.PACKAGE_POWER_W)

    def test_the_generator_and_the_checker_agree_about_vias(self):
        self.assertEqual((emit_board.VIA_HOLE_MM, emit_board.VIA_PAD_MM),
                         (fab.process("min_via_hole_mm"), fab.process("min_via_pad_mm")))


class TheRingIsArithmeticNotProseTest(unittest.TestCase):
    """
    The pair that could not disagree by accident and did by design.

    `check_footprints` demanded 0.25 mm and `emit_footprint` drew 0.35, related by a sentence in
    a comment. Raise the checker's minimum and the generator kept drawing the old ring — emitting
    footprints that fail the very check they were drawn for.
    """

    STRICTER = {"fabrication": {"min_annular_ring_mm": 0.45}}

    def test_the_drawn_ring_is_the_recommended_ring_plus_the_margin(self):
        # P57: the checker FAILS only under the absolute minimum now, but a generator drawing a
        # new pad aims at what the board house recommends, with margin — never at the bare minimum.
        self.assertAlmostEqual(fab.annular_ring_to_draw_mm(),
                               fab.process("recommended_annular_ring_mm")
                               + fab.process("annular_ring_margin_mm"))

    def test_a_project_minimum_stricter_than_the_recommendation_is_what_gets_drawn(self):
        self.assertAlmostEqual(fab.annular_ring_to_draw_mm(self.STRICTER),
                               0.45 + fab.process("annular_ring_margin_mm"))

    def test_raising_the_minimum_moves_the_pad_the_generator_draws(self):
        hole = emit_footprint.hole_diameter_mm()
        self.assertGreater(emit_footprint.pad_diameter_mm(hole, self.STRICTER),
                           emit_footprint.pad_diameter_mm(hole))

    def test_the_default_still_reproduces_the_hand_checked_footprint(self):
        # 1.00 mm hole, 1.70 mm pad, measured against a footprint made independently.
        hole = emit_footprint.hole_diameter_mm()
        self.assertEqual((hole, emit_footprint.pad_diameter_mm(hole)), (1.0, 1.7))

    def test_a_pad_drawn_for_the_default_fails_a_stricter_project(self):
        # The two halves meeting: what the generator drew, judged by what a project demands.
        hole = emit_footprint.hole_diameter_mm()
        pad = emit_footprint.pad_diameter_mm(hole)
        circuit = [{"type": "pcb_plated_hole", "shape": "circle",
                    "hole_diameter": hole, "outer_diameter": pad, "pcb_component_id": "c1"}]
        self.assertEqual(check_footprints.check_annular_rings(circuit), [])
        self.assertTrue(check_footprints.check_annular_rings(circuit, self.STRICTER),
                        "a stricter process accepted a pad drawn for a looser one")


class AProjectsOwnProcessReachesEveryRuleTest(unittest.TestCase):
    def test_a_stated_number_beats_the_default(self):
        self.assertEqual(fab.process("min_via_hole_mm", {"fabrication": {"min_via_hole_mm": 0.5}}), 0.5)

    def test_a_rules_file_that_states_nothing_falls_back(self):
        for rules in (None, {}, {"fabrication": {}}, {"fabrication": {"min_via_hole_mm": None}}):
            with self.subTest(rules=rules):
                self.assertEqual(fab.process("min_via_hole_mm", rules), fab.DATA["process"]["min_via_hole_mm"])

    def test_a_part_fact_is_nobodys_to_override(self):
        # An 0603 dissipates what an 0603 dissipates. There is deliberately no rules argument.
        self.assertEqual(fab.part("package_power_w")["0603"], 0.1)

    def test_the_command_line_carries_it_all_the_way_through(self):
        work = Path(tempfile.mkdtemp())
        circuit = work / "circuit.json"
        hole = emit_footprint.hole_diameter_mm()
        circuit.write_text(json.dumps([
            {"type": "pcb_plated_hole", "shape": "circle", "hole_diameter": hole,
             "outer_diameter": emit_footprint.pad_diameter_mm(hole), "pcb_component_id": "c1"}]))
        rules = work / "rules.json"
        rules.write_text(json.dumps({"fabrication": {"min_annular_ring_mm": 0.45}}))
        self.assertEqual(check_footprints.main([str(circuit)]), check_footprints.EXIT_OK)
        self.assertEqual(check_footprints.main([str(circuit), "--rules", str(rules)]),
                         check_footprints.EXIT_PROBLEMS)

    def test_a_rules_file_that_is_not_there_is_could_not_run_not_a_pass(self):
        # W1: asking for a process nobody could read must never answer "fine".
        work = Path(tempfile.mkdtemp())
        circuit = work / "circuit.json"
        circuit.write_text("[]")
        self.assertEqual(check_footprints.main([str(circuit), "--rules", str(work / "gone.json")]),
                         check_footprints.EXIT_COULD_NOT_RUN)

    def test_copper_takes_its_thickness_from_the_file(self):
        self.assertEqual(copper.COPPER_THICKNESS_MM, fab.process("copper_thickness_mm"))


if __name__ == "__main__":
    unittest.main()
