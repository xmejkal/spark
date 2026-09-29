"""
The one piece of this plugin that can be checked against a table in a handbook.

`copper.py` exists because two things needed the same formula and did not have it. `check_physics`
judged a board by IPC-2221; `emit_board` sized nothing at all and emitted the router's 0.15 mm
default everywhere, including on an RC car whose traction rail carries 2.9 A. When the generator
finally learned to size a trace it did so by reaching into the checker with `importlib` — one copy
of the formula, and a module reaching into another by file path, which is untestable.

Now it is arithmetic on numbers with no imports, no I/O and no state. That is what makes these
tests worth anything: they compare against published figures rather than against the
implementation's own opinion.

    python3 -m unittest discover -s tests
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import copper  # noqa: E402


class AgainstPublishedFiguresTest(unittest.TestCase):
    """
    Checked against the numbers IPC-2221 calculators agree on, not against this implementation.

    A test that restates the formula proves only that the code computes what it computes. These
    are the figures every trace-width table gives for 1 oz copper on an external layer.
    """

    def test_a_tenth_of_a_millimetre_carries_about_half_an_amp(self):
        # ~0.45 A at 10 C rise is the standard figure for 0.1 mm / 4 mil, 1 oz, external.
        self.assertAlmostEqual(copper.current_capacity_a(0.1, 10), 0.45, delta=0.06)

    def test_a_quarter_millimetre_carries_about_an_amp(self):
        self.assertAlmostEqual(copper.current_capacity_a(0.25, 10), 0.89, delta=0.12)

    def test_one_millimetre_carries_a_couple_of_amps(self):
        self.assertAlmostEqual(copper.current_capacity_a(1.0, 10), 2.36, delta=0.3)

    def test_a_hotter_rise_carries_more(self):
        # The direction matters more than the value: allowing a 20 C rise buys current.
        self.assertGreater(copper.current_capacity_a(1.0, 20), copper.current_capacity_a(1.0, 10))

    def test_width_and_capacity_are_inverses(self):
        # The property that makes the pair trustworthy, and the one a second copy of the formula
        # would break the moment somebody edited one of them.
        for current in (0.2, 0.6, 1.5, 3.0, 10.0):
            with self.subTest(current=current):
                width = copper.width_for_current_mm(current, 10)
                self.assertAlmostEqual(copper.current_capacity_a(width, 10), current, places=6)


class WhatToAskTheRouterForTest(unittest.TestCase):
    def test_a_rail_the_default_already_carries_asks_for_nothing(self):
        # None means "the default is enough". Emitting a thickness there would be a NARROWER
        # number dressed as a decision — the IPC minimum for 0.5 A is 0.12 mm, under the router's
        # own default and at the edge of what a cheap process etches.
        self.assertIsNone(copper.width_to_emit_mm(0.3))

    def test_a_rail_the_default_cannot_carry_asks_for_more(self):
        wanted = copper.width_to_emit_mm(2.9)
        self.assertIsNotNone(wanted)
        self.assertGreater(wanted, copper.MIN_TRACE_WIDTH_MM)

    def test_what_it_asks_for_is_wider_than_the_bare_minimum(self):
        # IPC gives the width at which a trace REACHES the rise; etching eats into it and a
        # router necks where it must fit. Asking at the limit lands under it.
        self.assertGreater(copper.width_to_emit_mm(2.9), copper.width_for_current_mm(2.9, 10))

    def test_the_result_actually_carries_the_current_it_was_asked_about(self):
        # The end-to-end property. If this fails, a generated board passes its own checker by
        # luck rather than by construction.
        for current in (0.8, 1.2, 2.9, 5.0):
            with self.subTest(current=current):
                self.assertGreaterEqual(
                    copper.current_capacity_a(copper.width_to_emit_mm(current), 10), current)

    def test_a_current_nobody_stated_asks_for_nothing(self):
        for missing in (None, 0, -1, "lots"):
            with self.subTest(value=missing):
                self.assertIsNone(copper.width_to_emit_mm(missing))


class ANeckIsNotATraceTest(unittest.TestCase):
    """
    The measurement that justified this distinction, on a real generated board.

    Asking the router for 1.50 mm produced 86 segments at 1.50 mm and six at 1.20 mm — and those
    six were between 0.12 mm and 0.85 mm LONG, each the last step into a 1.2 mm pad. Judging them
    by a formula for long uniform traces called a correctly sized 2.9 A rail unbuildable, and the
    remedy it printed ("widen this net") was for a trace already wide enough.
    """

    def test_a_long_run_is_what_gets_judged(self):
        self.assertEqual(copper.sustained_width_mm([(1.5, 20.0), (1.2, 0.3)]), 1.5)

    def test_the_narrowest_LONG_run_wins_not_the_widest(self):
        self.assertEqual(copper.sustained_width_mm([(1.5, 20.0), (0.8, 5.0)]), 0.8)

    def test_a_net_that_is_all_necks_sustains_nothing(self):
        # None, so the caller decides. It must not silently become "fine".
        self.assertIsNone(copper.sustained_width_mm([(1.2, 0.3), (1.2, 0.12)]))

    def test_necks_are_reported_rather_than_dropped(self):
        # A constriction at a pad is REAL — it just belongs to the pad, which is a footprint
        # question. Losing it entirely would trade a false alarm for a blind spot.
        found = copper.necks([(1.5, 20.0), (1.2, 0.3), (1.2, 0.12)])
        self.assertEqual(len(found), 2)

    def test_a_segment_with_no_length_is_not_counted_as_a_run(self):
        # The last point of a route has no following point, so no length. Treating that as a long
        # run would judge the board by a number that was never measured.
        self.assertIsNone(copper.sustained_width_mm([(1.2, None)]))


class TheGeneratorAndTheCheckerAgreeTest(unittest.TestCase):
    """The whole reason this module exists, stated as an assertion."""

    def test_what_the_generator_asks_for_passes_what_the_checker_demands(self):
        import check_physics
        for current in (0.7, 1.2, 2.9, 4.5):
            with self.subTest(current=current):
                asked = copper.width_to_emit_mm(current)
                self.assertGreaterEqual(check_physics.trace_current_capacity_a(asked, 10), current)

    def test_both_modules_use_one_formula_not_two_copies(self):
        import check_physics
        self.assertIs(check_physics.trace_current_capacity_a, copper.current_capacity_a)
        self.assertIs(check_physics.width_for_current_mm, copper.width_for_current_mm)


if __name__ == "__main__":
    unittest.main()
