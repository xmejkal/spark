"""
P464 (#632): the facts a stage needs and the record lacks are Findings with the code `missing_fact`, and a board takes
only an active level written as a fact.

    python3 -m unittest tests.test_missing_facts
"""

import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import missing_facts  # noqa: E402
from spark.core import outcomes  # noqa: E402

BENCH = {"value": 0, "verified": True, "source": "the bench"}


def levelless(**roles):
    """The shipped XIAO without the active level of both parts, then `roles` set over its pin_roles."""
    board = json.loads((ROOT / "boards" / "xiao-esp32-c6.json").read_text())
    for role in ("onboard_led", "onboard_button"):
        board["pin_roles"][role].pop("active_level")
    board["pin_roles"].update(roles)
    return board


class ListMissingFactsTest(unittest.TestCase):
    def test_two_are_missing_one_item_each_in_table_order(self):
        found = missing_facts.list_missing_facts(levelless())
        self.assertEqual([item.subject for item in found],
                         ["pin_roles.onboard_led.active_level", "pin_roles.onboard_button.active_level"])
        self.assertEqual({(item.severity, item.code) for item in found}, {(outcomes.COULD_NOT_RUN, "missing_fact")})
        self.assertIn("xiao-esp32-c6", found[0].fix)
        self.assertIn("--fact-set", found[0].fix)

    def test_one_is_missing(self):
        board = levelless()
        board["pin_roles"]["onboard_led"]["active_level"] = BENCH
        self.assertEqual([item.subject for item in missing_facts.list_missing_facts(board)], ["pin_roles.onboard_button.active_level"])

    def test_none_is_missing_for_the_boards_that_ship(self):
        for name in sorted(path.stem for path in (ROOT / "boards").glob("*.json") if path.name != "active.json"):
            with self.subTest(board=name):
                self.assertEqual(missing_facts.list_missing_facts(json.loads((ROOT / "boards" / (name + ".json")).read_text())), [])

    def test_a_part_with_labels_gives_one_item_for_the_role(self):
        board = levelless(onboard_led={"gpio": [1, 2], "labels": {"RED": 1, "GREEN": 2}, "note": "two LEDs"})
        self.assertEqual([item.subject for item in missing_facts.list_missing_facts(board)].count("pin_roles.onboard_led.active_level"), 1)

    def test_a_null_value_is_missing_and_a_bare_or_fact_level_is_not(self):
        for given, missing in ((None, True), ({"value": None, "verified": False, "source": "unknown"}, True), (0, False), (BENCH, False)):
            with self.subTest(given=given):
                board = levelless()
                board["pin_roles"]["onboard_led"]["active_level"] = given
                self.assertEqual("pin_roles.onboard_led.active_level" in [item.subject for item in missing_facts.list_missing_facts(board)], missing)

    def test_a_part_that_pins_py_gives_no_name_gives_no_item(self):
        board = levelless(onboard_led={"gpio": "15", "note": "x"}, onboard_button={"gpio": [3, 4], "note": "two buttons"})
        self.assertEqual(missing_facts.list_missing_facts(board), [])
        self.assertEqual(missing_facts.list_missing_facts({"pin_roles": "none"}), [])


class LevelWriteProblemsTest(unittest.TestCase):
    def test_a_level_as_a_fact_for_a_known_role_holds(self):
        self.assertEqual(missing_facts.level_write_problems({"pin_roles": {"onboard_led": {"active_level": BENCH}}}), [])

    def test_everything_else_is_refused(self):
        for given in ({"pin_roles": {"onboard_led": {"active_level": 0}}},
                      {"pin_roles": {"onboard_led": {"active_level": BENCH, "note": "x"}}},
                      {"pin_roles": {"onboard_display": {"active_level": BENCH}}},
                      {"pin_roles": {"onboard_led": {"active_level": BENCH}}, "name": "x"},
                      {"pin_roles": {}}, {"pin_roles": "x"}, {"name": "x"}):
            with self.subTest(given=copy.deepcopy(given)):
                self.assertTrue(missing_facts.level_write_problems(given))


if __name__ == "__main__":
    unittest.main()
