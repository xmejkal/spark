"""P724: RecordKind, the Strategy each kind of record is validated by: the shared checks, its rules in order, stop_after and owed."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  (P172) this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from spark.core import outcomes  # noqa: E402
from spark.records.record_kind import Answer, RecordKind, Validation, _cannot, _problem  # noqa: E402

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


class AnAnswerBecomesAResultTest(unittest.TestCase):
    """P726: `Answer.to_result` carries a handler's answer onto the core with parts.py's text rules, and `from_result` is
    the way back for a handler that runs an Operation on the core (`--needs-drop`)."""

    def test_each_item_is_a_finding_with_its_code_and_a_step_round_trips(self):
        step = outcomes.step("show", ["--show", "thing"], "to read the thing")
        answer = Answer({"x": 1}, ["  a line"], problems=[_problem("thing", "is wrong", "mend it")],
                        unchecked=[_cannot("could not read", code="file_refused")], next=[step])
        result = answer.to_result()
        self.assertEqual([(f.severity, f.subject, f.code, f.sentence, f.fix) for f in result.findings],
                         [("problems", "thing", None, "is wrong", "mend it"), ("could-not-run", None, "file_refused", "could not read", None)])
        self.assertEqual(result.to_envelope("parts", "show")["next"], [step])
        self.assertEqual(result.lines, ["  a line", "  thing: is wrong", "  fix for thing: mend it", "  could not check: could not read",
                                        "  next: parts.py --show thing — to read the thing"])
        back = Answer.from_result(result)
        self.assertEqual((back.problems, back.unchecked, back.next, back.data), (answer.problems, answer.unchecked, answer.next, answer.data))

    def test_an_answer_with_no_lines_says_its_refusals_on_stderr_with_the_fix_only_when_there_is_one(self):
        result = Answer(unchecked=[_cannot("nosuch is no matcher"), _cannot("a store refused", "fix the store")]).to_result()
        self.assertEqual((result.lines, result.diagnostics), ([], ["parts.py: nosuch is no matcher", "parts.py: a store refused — fix the store"]))
        self.assertEqual(result.status(), "could-not-run")

    def test_a_control_character_in_a_line_is_guarded_and_the_envelope_keeps_it_raw(self):
        result = Answer({"name": "x\x1b[31m"}, ["  x\x1b[31m"]).to_result()
        self.assertEqual((result.lines, result.data["name"]), (["  x?[31m"], "x\x1b[31m"))

    def test_a_code_is_in_an_item_only_when_given(self):
        self.assertEqual(_problem("s", "t"), {"subject": "s", "sentence": "t", "fix": None})
        self.assertEqual(_cannot("t", code="c"), {"sentence": "t", "fix": None, "code": "c"})


if __name__ == "__main__":
    unittest.main()
