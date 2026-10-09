"""
P102a: the spark project's open items name what needs them, sit on a slice, and respect the WIP limits.

P146 (the PO, 2026-10-06 evening, after the first day at the cap of 3): every working stage takes 2 — Discovery 2,
Design 2, Build 2 and Review 2 — Ready stays at 5, and at most 4 cards are in flight; an epic counts in Discovery and
Design, where it is the work itself, and from Build on its stories carry the limit; a task under its story never counts,
and a task with no parent story is a card of its own. Each limit is pinned from both sides: a board at the limit
passes, and one card over it is named. The numbers are written out here, never read from the module (W2,
test_self_confirmation).
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import check_backlog  # noqa: E402

BODY = "### Needed by\n\n%s\n\n### Value proven by\n\nx\n\n### Proof\n\n_No response_\n"
IN_FLIGHT_SAYS = "at most 4: finish one before starting another"


def item(number, status="Ready", slice_="10 The store", needed="the PO's walking skeleton", labels=("story",), parent=None,
         repository="xmejkal/spark"):
    return {"status": status, "slice": slice_, "labels": list(labels), "parent": parent,
            "content": {"number": number, "title": "P%d — x" % number, "body": BODY % needed, "repository": repository}}


class TheBacklogCheckTest(unittest.TestCase):
    def test_a_well_formed_board_has_no_problems(self):
        self.assertEqual(check_backlog.problems([item(1, "Build"), item(2, "Review"), item(3), item(4, "Done")]), [])

    def test_a_board_at_the_flight_cap_with_a_full_ready_passes(self):
        # Two in Discovery (its limit) and one each in Design and Build — 4 in flight, the cap — and Ready at 5: three
        # limits reached at once, none broken. One more card in any working stage would be a fifth in flight.
        in_flight = [item(1, "Discovery"), item(2, "Discovery"), item(3, "Design"), item(4, "Build")]
        ready = [item(n) for n in (5, 6, 7, 8, 9)]
        self.assertEqual(check_backlog.problems(in_flight + ready), [])

    def test_an_item_with_no_needed_by_is_named(self):
        for empty in ("", "_No response_", "   "):
            with self.subTest(empty=empty):
                self.assertEqual(check_backlog.problems([item(7, needed=empty)]),
                                 ["#7 P7 — x: no `Needed by` — W14: an item names the design that needs it"])

    def test_an_item_on_no_slice_is_named(self):
        self.assertEqual(check_backlog.problems([item(8, slice_=None)]), ["#8 P8 — x: on no slice of the story map"])

    def test_a_second_item_in_build_passes_and_a_third_is_named_with_all_three(self):
        self.assertEqual(check_backlog.problems([item(1, "Build"), item(2, "Build")]), [])
        self.assertEqual(check_backlog.problems([item(1, "Build"), item(2, "Build"), item(3, "Build")]),
                         ["Build holds 3 (#1, #2, #3) — its limit is 2: finish one before starting another"])

    def test_a_second_item_in_review_passes_and_a_third_is_named(self):
        self.assertEqual(check_backlog.problems([item(1, "Review"), item(2, "Review")]), [])
        self.assertEqual(check_backlog.problems([item(1, "Review"), item(2, "Review"), item(3, "Review")]),
                         ["Review holds 3 (#1, #2, #3) — its limit is 2: finish one before starting another"])

    def test_a_second_item_in_discovery_passes_and_a_third_is_named(self):
        self.assertEqual(check_backlog.problems([item(1, "Discovery"), item(2, "Discovery")]), [])
        self.assertEqual(check_backlog.problems([item(1, "Discovery"), item(2, "Discovery"), item(3, "Discovery")]),
                         ["Discovery holds 3 (#1, #2, #3) — its limit is 2: finish one before starting another"])

    def test_a_second_item_in_design_passes_and_a_third_is_named(self):
        self.assertEqual(check_backlog.problems([item(1, "Design"), item(2, "Design")]), [])
        self.assertEqual(check_backlog.problems([item(1, "Design"), item(2, "Design"), item(3, "Design")]),
                         ["Design holds 3 (#1, #2, #3) — its limit is 2: finish one before starting another"])

    def test_a_full_ready_column_says_the_po_moves_one_back(self):
        self.assertEqual(check_backlog.problems([item(n) for n in (1, 2, 3, 4, 5, 6)]),
                         ["Ready holds 6 (#1, #2, #3, #4, #5, #6) — its limit is 5: the PO moves one back to Idea"])

    def test_a_card_in_each_working_stage_is_four_in_flight_the_cap_and_passes(self):
        self.assertEqual(check_backlog.problems([item(1, "Discovery"), item(2, "Design"), item(3, "Build"),
                                                 item(4, "Review")]), [])

    def test_five_in_flight_is_too_many_even_with_no_stage_over_its_limit(self):
        self.assertEqual(check_backlog.problems([item(1, "Discovery"), item(2, "Discovery"), item(3, "Design"),
                                                 item(4, "Build"), item(5, "Review")]),
                         ["5 in flight (#1, #2, #3, #4, #5) — " + IN_FLIGHT_SAYS])

    def test_an_epic_in_discovery_or_design_is_the_work_and_counts(self):
        # An epic and two stories: the epic's place is what puts the stage over its limit of 2.
        self.assertEqual(check_backlog.problems([item(1, "Discovery", labels=("epic",)), item(2, "Discovery"),
                                                 item(3, "Discovery")]),
                         ["Discovery holds 3 (#1, #2, #3) — its limit is 2: finish one before starting another"])
        self.assertEqual(check_backlog.problems([item(4, "Design", labels=("epic",)), item(5, "Design"),
                                                 item(6, "Design")]),
                         ["Design holds 3 (#4, #5, #6) — its limit is 2: finish one before starting another"])

    def test_an_epic_in_discovery_counts_toward_the_flight_cap(self):
        # The case the counting rule was made for: P136 and P94, epics in Discovery, were the uncounted third and
        # fourth. The epic here is the fifth card; left uncounted, the board would read as four in flight and pass.
        self.assertEqual(check_backlog.problems([item(1, "Discovery", labels=("epic",)), item(2, "Discovery"),
                                                 item(3, "Design"), item(4, "Build"), item(5, "Review")]),
                         ["5 in flight (#1, #2, #3, #4, #5) — " + IN_FLIGHT_SAYS])

    def test_an_epic_in_ready_is_not_counted_there(self):
        # The PO's words taken literally: an epic counts in Discovery and Design; Ready is a queue, not work.
        self.assertEqual(check_backlog.problems([item(n) for n in (1, 2, 3, 4, 5)] + [item(6, labels=("epic",))]), [])

    def test_an_epic_in_build_or_review_rides_on_its_stories(self):
        # An epic and two stories: counted, the epic would be a third card and break the limit of 2.
        self.assertEqual(check_backlog.problems([item(1, "Build", labels=("epic",)), item(2, "Build"),
                                                 item(3, "Build")]), [])
        self.assertEqual(check_backlog.problems([item(4, "Review", labels=("epic",)), item(5, "Review"),
                                                 item(6, "Review")]), [])

    def test_counts_is_the_one_rule_the_status_shares(self):
        self.assertEqual([check_backlog.counts(e) for e in (item(1, "Discovery", labels=("epic",)),
                                                            item(2, "Build", labels=("epic",)),
                                                            item(3, "Build", labels=("task",), parent=1), item(4, "Build"))],
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
        task = item(2, "Build", needed="", slice_=None, labels=("task",), parent=1)
        self.assertEqual(check_backlog.problems([item(1, "Build"), task]), [])

    def test_a_task_with_no_parent_story_counts_as_a_card(self):
        orphan = item(9, "Build", labels=("task",), parent=None)
        self.assertTrue(check_backlog.counts(orphan))
        said = check_backlog.problems([item(1, "Build"), item(2, "Build"), orphan])
        self.assertEqual(said, ["Build holds 3 (#1, #2, #9) — its limit is 2: finish one before starting another"])

    def test_a_task_under_its_story_rides_on_it(self):
        self.assertFalse(check_backlog.counts(item(9, "Build", labels=("task",), parent=1)))
        self.assertEqual(check_backlog.problems([item(1, "Build"), item(2, "Build"), item(9, "Build", labels=("task",), parent=1)]), [])

    def test_a_parentless_task_is_judged_on_needed_by_and_slice_like_a_card(self):
        said = check_backlog.problems([item(9, "Ready", labels=("task",), parent=None, slice_="", needed="")])
        self.assertEqual(said, ["#9 P9 — x: no `Needed by` — W14: an item names the design that needs it",
                                "#9 P9 — x: on no slice of the story map"])

    def test_parents_asks_each_task_s_own_repository_in_one_call(self):
        asked = []
        def run(args, **kwargs):
            asked.append(args)
            return mock.Mock(stdout=json.dumps({"data": {"r0": {"t9": {"parent": {"number": 1}}},
                                                         "r1": {"t9": {"parent": None}, "t4": {"parent": {"number": 2}}}}}))
        tasks = [("xmejkal/spark", 9), ("xmejkal/sisuo-brain-transplant", 9), ("xmejkal/sisuo-brain-transplant", 4)]
        with mock.patch.object(check_backlog.subprocess, "run", run):
            found, why = check_backlog.parents(tasks)
        self.assertEqual((found, why), ({("xmejkal/spark", 9): 1, ("xmejkal/sisuo-brain-transplant", 9): None,
                                         ("xmejkal/sisuo-brain-transplant", 4): 2}, None))
        self.assertEqual(len(asked), 1)
        query = " ".join(asked[0])
        self.assertIn('r0: repository(owner: "xmejkal", name: "spark") { t9: issue(number: 9) { parent { number } } }', query)
        self.assertIn('r1: repository(owner: "xmejkal", name: "sisuo-brain-transplant") { t9: issue(number: 9) { parent { number } } '
                      't4: issue(number: 4) { parent { number } } }', query)

    def test_parents_asks_nobody_when_there_are_no_tasks(self):
        def run(args, **kwargs):
            raise AssertionError("gh was asked about no tasks at all")
        with mock.patch.object(check_backlog.subprocess, "run", run):
            self.assertEqual(check_backlog.parents([]), ({}, None))

    def test_parents_offline_says_why(self):
        def run(args, **kwargs):
            raise FileNotFoundError("gh")
        with mock.patch.object(check_backlog.subprocess, "run", run):
            self.assertEqual(check_backlog.parents([("xmejkal/spark", 9)]), ({}, "FileNotFoundError"))

    def test_parents_answered_with_errors_and_no_data_says_why(self):
        def run(args, **kwargs):
            return mock.Mock(stdout=json.dumps({"data": None, "errors": [{"message": "Could not resolve to an Issue"}]}))
        with mock.patch.object(check_backlog.subprocess, "run", run):
            self.assertEqual(check_backlog.parents([("xmejkal/spark", 9)]), ({}, "TypeError"))

    def test_parents_with_no_answer_for_a_task_is_not_read_as_parentless(self):
        # A task GitHub did not answer for has an unknown parent, not none: reading it as none would count it as a card.
        for answer, named in (({"r0": {}}, "KeyError"), ({"r0": {"t9": None}}, "TypeError")):
            with self.subTest(answer=answer):
                def run(args, **kwargs):
                    return mock.Mock(stdout=json.dumps({"data": answer}))
                with mock.patch.object(check_backlog.subprocess, "run", run):
                    self.assertEqual(check_backlog.parents([("xmejkal/spark", 9)]), ({}, named))

    def said(self, run):
        """main()'s exit code and what it printed, with gh answered by `run`."""
        with mock.patch.object(check_backlog.subprocess, "run", side_effect=run), mock.patch("sys.stdout") as out:
            code = check_backlog.main()
        return code, "".join(call.args[0] for call in out.write.call_args_list)

    def board_answering(self, items, parents):
        """
        A gh that lists the spark project holding `items` — as gh prints them, with no `parent` — and answers the parents
        query with `parents` (raised when it is an exception). Returns it with the commands it was asked, as text.
        """
        asked = []

        def run(args, **kwargs):
            asked.append(" ".join(args))
            if "graphql" in args:
                if isinstance(parents, Exception):
                    raise parents
                return mock.Mock(stdout=json.dumps(parents))
            if "item-list" in args:
                return mock.Mock(stdout=json.dumps({"items": [{k: v for k, v in e.items() if k != "parent"} for e in items]}))
            return mock.Mock(stdout=json.dumps({"projects": [{"number": 2, "title": "spark"}]}))
        return run, asked

    def test_main_asks_for_each_open_task_s_parent_and_a_task_under_its_story_rides_on_it(self):
        items = [item(1, "Build"), item(2, "Build"), item(9, "Build", labels=("task",)), item(8, "Done", labels=("task",))]
        run, asked = self.board_answering(items, {"data": {"r0": {"t9": {"parent": {"number": 1}}}}})
        code, printed = self.said(run)
        self.assertEqual(code, 0)
        self.assertIn("  backlog: 3 open, the limits hold", printed)
        self.assertNotIn("could not be read", printed)
        questions = [command for command in asked if "graphql" in command]
        self.assertEqual(len(questions), 1)
        self.assertIn('r0: repository(owner: "xmejkal", name: "spark") { t9: issue(number: 9)', questions[0])
        self.assertNotIn("t8:", questions[0])

    def test_main_counts_a_task_the_answer_gives_no_parent_as_a_card(self):
        items = [item(1, "Build"), item(2, "Build"), item(9, "Build", labels=("task",))]
        run, _ = self.board_answering(items, {"data": {"r0": {"t9": {"parent": None}}}})
        code, printed = self.said(run)
        self.assertEqual(code, 1)
        self.assertIn("    Build holds 3 (#1, #2, #9) — its limit is 2: finish one before starting another", printed)

    def test_main_asks_each_task_s_own_repository_and_keeps_one_number_in_two_apart(self):
        # Issue numbers are per repository: #9 of spark has a parent and rides, #9 of the bin has none and is a card.
        items = [item(1, "Build"), item(2, "Build"), item(9, "Build", labels=("task",)),
                 item(9, "Build", labels=("task",), repository="xmejkal/sisuo-brain-transplant")]
        run, asked = self.board_answering(items, {"data": {"r0": {"t9": {"parent": {"number": 1}}}, "r1": {"t9": {"parent": None}}}})
        code, printed = self.said(run)
        self.assertEqual(code, 1)
        self.assertIn("    Build holds 3 (#1, #2, #9) — its limit is 2: finish one before starting another", printed)
        question = next(command for command in asked if "graphql" in command)
        self.assertIn('r0: repository(owner: "xmejkal", name: "spark")', question)
        self.assertIn('r1: repository(owner: "xmejkal", name: "sisuo-brain-transplant")', question)

    def test_parents_unread_counts_tasks_as_riding_and_says_so(self):
        # The list was read and the parents were not (the GraphQL call fails): a could-not-look, said with its cause, and
        # the push is let through — the task counted as riding, or Build would hold three.
        items = [item(1, "Build"), item(2, "Build"), item(9, "Build", labels=("task",))]
        run, _ = self.board_answering(items, subprocess.TimeoutExpired("gh", 60))
        code, printed = self.said(run)
        self.assertEqual(code, 0)
        self.assertIn("  backlog: 3 open, the limits hold", printed)
        self.assertIn("  backlog: tasks' parent stories could not be read (TimeoutExpired) — every task counted as riding on a story",
                      printed)

    def test_unread_parents_do_not_hide_a_broken_limit(self):
        items = [item(1, "Build"), item(2, "Build"), item(3, "Build"), item(9, "Build", labels=("task",))]
        run, _ = self.board_answering(items, subprocess.TimeoutExpired("gh", 60))
        code, printed = self.said(run)
        self.assertEqual(code, 1)
        self.assertIn("    Build holds 3 (#1, #2, #3) — its limit is 2: finish one before starting another", printed)
        self.assertIn("tasks' parent stories could not be read (TimeoutExpired)", printed)

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
