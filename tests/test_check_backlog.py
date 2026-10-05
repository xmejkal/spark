"""P102a: the spark project's open items name what needs them, sit on a slice, and respect the WIP limits."""

import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import check_backlog  # noqa: E402

BODY = "### Needed by\n\n%s\n\n### Value proven by\n\nx\n\n### Proof\n\n_No response_\n"


def item(number, status="Ready", slice_="10 The store", needed="the PO's walking skeleton", labels=("story",)):
    return {"status": status, "slice": slice_, "labels": list(labels),
            "content": {"number": number, "title": "P%d — x" % number, "body": BODY % needed}}


class TheBacklogCheckTest(unittest.TestCase):
    def test_a_well_formed_board_has_no_problems(self):
        self.assertEqual(check_backlog.problems([item(1, "Build"), item(2, "Review"), item(3), item(4, "Done")]), [])

    def test_an_item_with_no_needed_by_is_named(self):
        for empty in ("", "_No response_", "   "):
            with self.subTest(empty=empty):
                self.assertEqual(check_backlog.problems([item(7, needed=empty)]),
                                 ["#7 P7 — x: no `Needed by` — W14: an item names the design that needs it"])

    def test_an_item_on_no_slice_is_named(self):
        self.assertEqual(check_backlog.problems([item(8, slice_=None)]), ["#8 P8 — x: on no slice of the story map"])

    def test_a_second_item_in_build_is_named_with_both(self):
        self.assertEqual(check_backlog.problems([item(1, "Build"), item(2, "Build")]),
                         ["Build holds 2 (#1, #2) — its limit is 1: finish one before starting another"])

    def test_three_in_flight_is_too_many_even_one_per_stage(self):
        self.assertEqual(check_backlog.problems([item(1, "Discovery"), item(2, "Build"), item(3, "Review")]),
                         ["3 in flight (#1, #2, #3) — at most 2: one being worked, one waiting"])

    def test_an_epic_carries_no_limit_its_stories_do(self):
        self.assertEqual(check_backlog.problems([item(1, "Build", labels=("epic",)), item(2, "Build")]), [])

    def test_a_done_item_is_not_judged_again(self):
        self.assertEqual(check_backlog.problems([item(5, "Done", needed="", slice_=None)]), [])

    def test_done_and_idea_carry_no_limit(self):
        self.assertEqual(check_backlog.problems([item(n, "Done") for n in range(9)] + [item(20 + n, "Idea") for n in range(9)]), [])

    def test_the_recorded_board_reads(self):
        items = json.loads((ROOT / "tests" / "data" / "p102a-items.json").read_text())["items"]
        self.assertTrue(items)
        self.assertEqual(check_backlog.problems(items), [], "the board as migrated keeps every limit")

    def test_a_body_with_windows_line_endings_reads_as_filled(self):
        crlf = item(1)
        crlf["content"]["body"] = crlf["content"]["body"].replace("\n", "\r\n")
        self.assertEqual(check_backlog.problems([crlf]), [])

    def test_a_task_rides_on_its_story(self):
        task = item(2, "Build", needed="", slice_=None, labels=("task",))
        self.assertEqual(check_backlog.problems([item(1, "Build"), task]), [])

    def said(self, run):
        """main()'s exit code and what it printed, with gh answered by `run`."""
        with mock.patch.object(check_backlog.subprocess, "run", side_effect=run), mock.patch("sys.stdout") as out:
            code = check_backlog.main()
        return code, "".join(call.args[0] for call in out.write.call_args_list)

    def test_offline_the_gate_says_why_and_passes(self):
        def run(*args, **kwargs):
            raise FileNotFoundError("gh")
        code, printed = self.said(run)
        self.assertEqual(code, 0)
        self.assertIn("skipped", printed)
        self.assertIn("FileNotFoundError", printed)

    def test_a_missing_project_fails_the_gate_and_says_so(self):
        def run(*args, **kwargs):
            return mock.Mock(stdout=json.dumps({"projects": [{"number": 1, "title": "the bin"}]}))
        code, printed = self.said(run)
        self.assertEqual(code, 1)
        self.assertIn("no project titled 'spark'", printed)


if __name__ == "__main__":
    unittest.main()
