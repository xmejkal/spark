"""
The one rule that counts a build with no simulation as done (P977, P1008, P1207), `spark.flow.no_model`: a build whose
one stopped stage is the simulation, because Wokwi has no model of the board. An old record ended that stage
could-not-run, and a new one ends it skipped. Both count. Any other skip, stop or missing code does not.
    python3 -m unittest tests.test_no_model
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from spark.flow.no_model import stops_only_for_no_model  # noqa: E402


def record(*stages):
    return {"stages": [dict(zip(("name", "status", "code"), stage)) for stage in stages]}


BOARD = ("board", "ok", None)


class TheNoModelRuleTest(unittest.TestCase):

    def test_an_old_record_whose_simulation_could_not_run_for_no_wokwi_model_counts(self):
        self.assertTrue(stops_only_for_no_model(record(BOARD, ("simulation", "could-not-run", "board_not_in_wokwi"))))

    def test_a_new_record_whose_simulation_is_skipped_for_no_wokwi_model_counts(self):
        self.assertTrue(stops_only_for_no_model(record(BOARD, ("simulation", "skipped", "board_not_in_wokwi"))))

    def test_a_simulation_skipped_because_every_part_is_skipped_does_not_count(self):
        self.assertFalse(stops_only_for_no_model(record(BOARD, ("simulation", "skipped", "every_part_skipped"))))

    def test_an_old_record_with_no_code_does_not_count(self):
        self.assertFalse(stops_only_for_no_model(record(BOARD, ("simulation", "could-not-run", None))))

    def test_a_second_stopped_stage_does_not_count(self):
        self.assertFalse(stops_only_for_no_model(record(("board", "problems", "design_not_built"),
                                                        ("simulation", "skipped", "board_not_in_wokwi"))))

    def test_a_record_with_no_stages_or_no_record_does_not_count(self):
        self.assertEqual([stops_only_for_no_model(given) for given in ({}, {"stages": None}, None, {"done": True})],
                         [False, False, False, False])


if __name__ == "__main__":
    unittest.main()
