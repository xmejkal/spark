"""P724: RecordKind, the Strategy each kind of record is validated by: the shared checks, its rules in order, stop_after and owed."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.records.record_kind import RecordKind, Validation  # noqa: E402

PATH = Path("/nowhere/x.json")


def first_problems(record, validation):
    return ["first"]


def second_problems(record, validation):
    return ["second"]


def quiet_problems(record, validation):
    return []


def seen_problems(record, validation):
    """The validation a rule is given, as one problem, so a test reads it."""
    return [validation]


class RecordKindTest(unittest.TestCase):
    def kind(self, rules, stop_after=()):
        return RecordKind("thing", 1, ("schema", "id"), rules, stop_after)

    def test_a_record_that_holds_has_no_problem(self):
        self.assertEqual(self.kind([quiet_problems]).validate({"schema": 1, "id": "x"}, PATH), [])

    def test_the_shared_checks_come_first_then_each_rule_in_order(self):
        self.assertEqual(self.kind([second_problems, first_problems]).validate({"schema": 2}, PATH),
                         ["schema is 2, but this code understands only 1", "missing required key 'id'",
                          "second", "first"])

    def test_a_rule_in_stop_after_that_finds_a_problem_is_the_last_to_run(self):
        self.assertEqual(self.kind([first_problems, second_problems], stop_after=(first_problems,))
                         .validate({"schema": 1, "id": "x"}, PATH), ["first"])

    def test_a_rule_in_stop_after_that_finds_nothing_lets_the_next_run(self):
        self.assertEqual(self.kind([quiet_problems, second_problems], stop_after=(quiet_problems,))
                         .validate({"schema": 1, "id": "x"}, PATH), ["second"])

    def test_an_owed_key_skips_its_shared_check(self):
        kind = self.kind([])
        self.assertEqual(kind.validate({}, PATH, owed=("schema", "id")), [])
        self.assertEqual(kind.validate({}, PATH, owed=("schema",)), ["missing required key 'id'"])
        self.assertEqual(kind.validate({"schema": 2}, PATH, owed=("id",)), ["schema is 2, but this code understands only 1"])

    def test_each_rule_is_given_the_path_the_owed_keys_and_for_fab(self):
        found = self.kind([seen_problems]).validate({"schema": 1, "id": "x"}, PATH, owed=("id",), for_fab=True)
        self.assertEqual(found, [Validation(PATH, ("id",), True)])


if __name__ == "__main__":
    unittest.main()
