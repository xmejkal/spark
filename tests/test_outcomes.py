"""
Proof that the three outcomes are one definition, and that every script answers in them.

    python3 -m unittest discover -s tests
"""

import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import outcomes  # noqa: E402

#: Every script that exits with the three-way answer, and the local word it uses for "no".
SCRIPTS = {
    "check_all": "EXIT_PROBLEMS", "check_spine": "EXIT_PROBLEMS", "check_firmware": "EXIT_PROBLEMS",
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
