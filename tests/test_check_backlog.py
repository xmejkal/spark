"""
P102a: the spark project's open items name what needs them, sit on a slice, and respect the WIP limits.

P146 (the PO, 2026-10-06): the limits are Discovery 1, Design 1, Ready 5, Build 1 and Review 1, with at most 3 in
flight; an epic counts in Discovery and Design, where it is the work itself, and from Build on its stories carry the
limit; a task never counts. Each limit is pinned from both sides: a board at the limit passes, and one card over it is
named. The numbers are written out here, never read from the module (W2, test_self_confirmation).
"""

import json
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import check_backlog  # noqa: E402

BODY = "### Needed by\n\n%s\n\n### Value proven by\n\nx\n\n### Proof\n\n_No response_\n"
IN_FLIGHT_SAYS = "at most 3: one in the session, one with agents in the background, one waiting"


def item(number, status="Ready", slice_="10 The store", needed="the PO's walking skeleton", labels=("story",)):
    return {"status": status, "slice": slice_, "labels": list(labels),
            "content": {"number": number, "title": "P%d — x" % number, "body": BODY % needed}}


class TheBacklogCheckTest(unittest.TestCase):
    def test_a_well_formed_board_has_no_problems(self):
        self.assertEqual(check_backlog.problems([item(1, "Build"), item(2, "Review"), item(3), item(4, "Done")]), [])

    def test_a_board_at_the_flight_cap_with_a_full_ready_passes(self):
        # One each in Discovery, Design and Build — 3 in flight, the cap — and Ready at 5: as many limits reached as a
        # board can reach at once (Review's would make a fourth in flight), none broken.
        board = [item(1, "Discovery"), item(2, "Design"), item(3, "Build")] + [item(n) for n in (4, 5, 6, 7, 8)]
        self.assertEqual(check_backlog.problems(board), [])

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

    def test_a_second_item_in_review_is_named(self):
        self.assertEqual(check_backlog.problems([item(1, "Review"), item(2, "Review")]),
                         ["Review holds 2 (#1, #2) — its limit is 1: finish one before starting another"])

    def test_a_second_item_in_discovery_is_named(self):
        self.assertEqual(check_backlog.problems([item(1, "Discovery"), item(2, "Discovery")]),
                         ["Discovery holds 2 (#1, #2) — its limit is 1: finish one before starting another"])

    def test_a_full_ready_column_says_the_po_moves_one_back(self):
        self.assertEqual(check_backlog.problems([item(n) for n in (1, 2, 3, 4, 5, 6)]),
                         ["Ready holds 6 (#1, #2, #3, #4, #5, #6) — its limit is 5: the PO moves one back to Idea"])

    def test_four_in_flight_is_too_many_even_one_per_stage(self):
        self.assertEqual(check_backlog.problems([item(1, "Discovery"), item(2, "Design"), item(3, "Build"),
                                                 item(4, "Review")]),
                         ["4 in flight (#1, #2, #3, #4) — " + IN_FLIGHT_SAYS])

    def test_an_epic_in_discovery_or_design_is_the_work_and_counts(self):
        self.assertEqual(check_backlog.problems([item(1, "Discovery", labels=("epic",)), item(2, "Discovery")]),
                         ["Discovery holds 2 (#1, #2) — its limit is 1: finish one before starting another"])
        self.assertEqual(check_backlog.problems([item(3, "Design", labels=("epic",)), item(4, "Design")]),
                         ["Design holds 2 (#3, #4) — its limit is 1: finish one before starting another"])

    def test_an_epic_in_discovery_counts_toward_the_flight_cap(self):
        # The case the limits were raised for: P136 and P94, epics in Discovery, were the uncounted third and fourth.
        self.assertEqual(check_backlog.problems([item(1, "Discovery", labels=("epic",)), item(2, "Design"),
                                                 item(3, "Build"), item(4, "Review")]),
                         ["4 in flight (#1, #2, #3, #4) — " + IN_FLIGHT_SAYS])

    def test_an_epic_in_ready_is_not_counted_there(self):
        # The PO's words taken literally: an epic counts in Discovery and Design; Ready is a queue, not work.
        self.assertEqual(check_backlog.problems([item(n) for n in (1, 2, 3, 4, 5)] + [item(6, labels=("epic",))]), [])

    def test_an_epic_in_build_or_review_rides_on_its_stories(self):
        self.assertEqual(check_backlog.problems([item(1, "Build", labels=("epic",)), item(2, "Build")]), [])
        self.assertEqual(check_backlog.problems([item(3, "Review", labels=("epic",)), item(4, "Review")]), [])

    def test_counts_is_the_one_rule_the_status_shares(self):
        self.assertEqual([check_backlog.counts(e) for e in (item(1, "Discovery", labels=("epic",)),
                                                            item(2, "Build", labels=("epic",)),
                                                            item(3, "Build", labels=("task",)), item(4, "Build"))],
                         [True, False, False, True])

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
