"""
Proof that the three outcomes are one definition, and that every script answers in them.

    python3 -m unittest discover -s tests
"""

import importlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import outcomes  # noqa: E402

#: Every script that exits with the three-way answer, and the local word it uses for "no".
SCRIPTS = {
    "check_all": "EXIT_PROBLEMS", "check_spine": "EXIT_PROBLEMS",
    "check_bom": "EXIT_PROBLEMS", "check_footprints": "EXIT_PROBLEMS", "check_physics": "EXIT_PROBLEMS",
    "emit_footprint": "EXIT_PROBLEMS", "assign_pins": "EXIT_IMPOSSIBLE", "init_project": "EXIT_NOTHING_TO_DO",
    "check_vendor_pins": "EXIT_MISMATCH", "mutate": "EXIT_ESCAPED", "boards": "EXIT_INVALID",
    "parts": "EXIT_INVALID",
}


class ThreeOutcomesTest(unittest.TestCase):
    def test_the_codes_are_zero_one_two_and_distinct(self):
        self.assertEqual((outcomes.EXIT_OK, outcomes.EXIT_PROBLEMS, outcomes.EXIT_COULD_NOT_RUN), (0, 1, 2))

    def test_every_status_word_has_its_code(self):
        self.assertEqual(outcomes.EXIT_FOR[outcomes.COULD_NOT_RUN], outcomes.EXIT_COULD_NOT_RUN)
        self.assertEqual(set(outcomes.EXIT_FOR), {outcomes.OK, outcomes.PROBLEMS, outcomes.COULD_NOT_RUN})

    def test_the_two_maps_are_each_other_reversed(self):
        # Five scripts wrote EXIT_FOR inline and two wrote its inverse; P42 gave both one home,
        # so a mutation that breaks the round trip must be caught here or nowhere.
        self.assertEqual(set(outcomes.STATUS_FOR), {0, 1, 2})
        for status, code in outcomes.EXIT_FOR.items():
            self.assertEqual(outcomes.STATUS_FOR[code], status)
        for code, status in outcomes.STATUS_FOR.items():
            self.assertEqual(outcomes.EXIT_FOR[status], code)

    def test_the_rule_itself(self):
        # The expression six scripts used to restate, one of them wrongly (P34).
        self.assertEqual(outcomes.status_of(), outcomes.OK)
        self.assertEqual(outcomes.status_of(unchecked=["a rail nobody stated"]), outcomes.COULD_NOT_RUN)
        self.assertEqual(outcomes.status_of(problems=["a short"]), outcomes.PROBLEMS)
        self.assertEqual(outcomes.status_of(problems=["a short"], unchecked=["and one unread"]), outcomes.PROBLEMS)

    def test_the_answer_a_check_hands_back(self):
        self.assertEqual(outcomes.answer(), {"status": outcomes.OK, "problems": [], "unchecked": []})
        self.assertEqual(outcomes.answer(unchecked=["x"])["status"], outcomes.COULD_NOT_RUN)
        self.assertNotIn("unmeasured", outcomes.answer())
        self.assertEqual(outcomes.answer(unmeasured=["a current nobody took"])["unmeasured"], ["a current nobody took"])

    def test_every_script_answers_in_the_one_vocabulary(self):
        for name, no in SCRIPTS.items():
            module = importlib.import_module(name)
            self.assertIs(module.EXIT_OK, outcomes.EXIT_OK, name)
            self.assertEqual(getattr(module, no), outcomes.EXIT_PROBLEMS, name)
            if hasattr(module, "EXIT_COULD_NOT_RUN"):
                self.assertEqual(module.EXIT_COULD_NOT_RUN, outcomes.EXIT_COULD_NOT_RUN, name)


class OneUpwardWalkTest(unittest.TestCase):
    def test_the_walk_is_nearest_first_and_ends_at_the_root(self):
        import boards
        walked = boards.walk_up(ROOT / "scripts")
        self.assertEqual(walked[0], (ROOT / "scripts").resolve())
        self.assertEqual(walked[1], ROOT.resolve())
        self.assertEqual(walked[-1], Path(walked[-1].anchor))


if __name__ == "__main__":
    unittest.main()
