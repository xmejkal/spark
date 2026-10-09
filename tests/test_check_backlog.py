"""
P102a: the spark project's open items name what needs them, sit on a slice, and respect the WIP limits.

P146 (the PO, 2026-10-06 evening, after the first day at the cap of 3): every working stage takes 2 — Discovery 2,
Design 2, Build 2 and Review 2 — Ready stays at 5, and at most 4 cards are in flight; an epic counts in Discovery and
Design, where it is the work itself, and from Build on its stories carry the limit; a task under its story never counts,
and a task with no parent story is a card of its own. Each limit is pinned from both sides: a board at the limit
passes, and one card over it is named. The numbers are written out here, never read from the module (W2,
test_self_confirmation).

P146 (docs/2026-10-06-process-design.md, the skeptic pass's item 6): a card is asked for its Needed by and its slice
from Ready on — the commitment — not in Idea, Discovery or Design, which decide whether to build. Pinned from both
sides, with the stages written out: a card in Idea, Discovery or Design with neither passes, and a card in Ready, Build
or Review without one is named — an epic that holds no place in a limit (counts()) among them. A card with no Status,
or a stage the gate does not know, is treated like Idea.

P146 (docs/2026-10-06-process-design.md, "Asks to you"): a card that waits on someone carries Waiting on and Waiting
since, and a Waiting on with no Waiting since is named — in any open stage, Idea included, since a wait is no
commitment-stage question, and whoever is waited on (the PO, Petr). A Done card's stale wait is not judged.

P146 (docs/2026-10-06-process-design.md, decision 4): the expedite lane — on the PO's word only, one card at a time,
labelled `expedite`. It lets a working stage, and the flight, hold one over their limit — Ready never, the expedite enters
Build — and the gate fails on two. Pinned from both sides: one over passes and two over is named; two labelled cards are
named and get no extra place; a Done card keeps its label and is not counted; the extra place is its own stage's alone;
a card with no labels key is no lane and no crash; an expedite epic in Build, which holds no place there (counts()),
lends nothing; and a Ready that holds one over its limit is named, expedite or not.

P146 (docs/2026-10-06-process-design.md, §1: "The bin's desk cards count in the same three. A bench session is your
hands, so it sits outside them"): the bin's board is read for three things. Its cards in a working stage fly in the same
total as spark's — a task under its story rides on it, an epic counts only in Discovery and Design, a Done card is out,
and a card labelled `bench` sits outside — the expedite lane is one lane across both boards, and a card that waits on
someone is asked since when there too, as on spark's. They fill none of spark's stages and are asked for no Needed by or
slice, and a sentence names them `bin #12`, apart from spark's #12. A bin board that could not be read is said, with its
cause, and spark's cards are counted alone: never a silent pass and never a failed push. One that was read is said too,
in the summary line, with its open count.
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
         repository="xmejkal/spark", waiting=None, since=None):
    return {"status": status, "slice": slice_, "labels": list(labels), "parent": parent,
            "waiting on": waiting, "waiting since": since,
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

    def test_an_idea_card_needs_no_slice_and_no_needed_by_yet(self):
        self.assertEqual(check_backlog.problems([item(3, "Idea", slice_="", needed="")]), [])

    def test_a_card_in_discovery_or_design_needs_no_slice_and_no_needed_by_yet(self):
        # Idea, Discovery and Design decide whether to build; the PO's order into Ready is what commits (the spec).
        for stage in ("Discovery", "Design"):
            with self.subTest(stage=stage):
                self.assertEqual(check_backlog.problems([item(3, stage, slice_="", needed="")]), [])

    def test_a_card_with_no_status_or_an_unknown_stage_is_not_judged_like_an_idea_card(self):
        # Only a stage from the commitment on is asked; a card the board places nowhere the gate knows is not named.
        for status in (None, "Parked"):
            with self.subTest(status=status):
                self.assertEqual(check_backlog.problems([item(3, status, slice_="", needed="")]), [])

    def test_a_ready_card_with_no_slice_is_named(self):
        self.assertEqual(check_backlog.problems([item(3, "Ready", slice_="")]), ["#3 P3 — x: on no slice of the story map"])

    def test_a_card_in_build_or_review_is_judged(self):
        for stage in ("Build", "Review"):
            with self.subTest(stage=stage):
                self.assertEqual(check_backlog.problems([item(3, stage, needed="")]),
                                 ["#3 P3 — x: no `Needed by` — W14: an item names the design that needs it"])

    def test_an_epic_that_holds_no_place_in_a_limit_is_still_asked_for_a_needed_by_and_a_slice(self):
        # counts() says what a limit holds, not whom the two sentences are asked of: an epic in Ready, Build or Review
        # holds no place, and is asked for both like every card from Ready on.
        for stage in ("Ready", "Build", "Review"):
            with self.subTest(stage=stage):
                self.assertEqual(check_backlog.problems([item(6, stage, labels=("epic",), slice_="", needed="")]),
                                 ["#6 P6 — x: no `Needed by` — W14: an item names the design that needs it",
                                  "#6 P6 — x: on no slice of the story map"])

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

    def test_one_expedite_may_take_a_stage_one_over_its_limit(self):
        rushed = item(9, "Build", labels=("story", "expedite"))
        self.assertEqual(check_backlog.problems([item(1, "Build"), item(2, "Build"), rushed]), [])

    def test_a_stage_two_over_its_limit_fails_even_with_an_expedite(self):
        rushed = item(9, "Build", labels=("story", "expedite"))
        said = check_backlog.problems([item(1, "Build"), item(2, "Build"), item(3, "Build"), rushed])
        self.assertEqual(said, ["Build holds 4 (#1, #2, #3, #9) — its limit is 2: finish one before starting another"])

    def test_two_expedites_are_named(self):
        said = check_backlog.problems([item(1, "Build", labels=("story", "expedite")), item(2, "Review", labels=("story", "expedite"))])
        self.assertEqual(said, ["2 cards labelled expedite (#1, #2) — one at a time, on the PO's word"])

    def test_an_expedite_lets_five_fly(self):
        cards = [item(1, "Discovery"), item(2, "Design"), item(3, "Build"), item(4, "Review"), item(9, "Build", labels=("story", "expedite"))]
        self.assertEqual(check_backlog.problems(cards), [])

    def test_an_expedite_epic_in_build_is_not_the_work_and_allows_nothing(self):
        epic = item(9, "Build", labels=("epic", "expedite"))
        said = check_backlog.problems([item(1, "Build"), item(2, "Build"), item(3, "Build"), epic])
        self.assertEqual(said, ["Build holds 3 (#1, #2, #3) — its limit is 2: finish one before starting another"])

    def test_two_expedites_in_one_stage_get_no_extra_place(self):
        # The allowance is for exactly one: with two the gate names the lane AND holds the stage to its limit.
        said = check_backlog.problems([item(1, "Build"), item(2, "Build", labels=("story", "expedite")),
                                       item(3, "Build", labels=("story", "expedite"))])
        self.assertEqual(said, ["2 cards labelled expedite (#2, #3) — one at a time, on the PO's word",
                                "Build holds 3 (#1, #2, #3) — its limit is 2: finish one before starting another"])

    def test_an_expedite_lends_its_own_stage_the_extra_place_and_no_other(self):
        # The expedite sits in Build; Review, with three, is still over its limit of 2.
        said = check_backlog.problems([item(1, "Review"), item(2, "Review"), item(3, "Review"),
                                       item(9, "Build", labels=("story", "expedite"))])
        self.assertEqual(said, ["Review holds 3 (#1, #2, #3) — its limit is 2: finish one before starting another"])

    def test_a_done_card_keeps_its_label_and_is_not_counted_as_an_expedite(self):
        # A label stays on a card when it is Done: the lane must free up, or the second expedite would fail for good.
        finished = item(1, "Done", labels=("story", "expedite"))
        self.assertEqual(check_backlog.problems([finished, item(2, "Build", labels=("story", "expedite"))]), [])

    def test_a_card_with_no_labels_key_is_not_an_expedite_and_not_a_crash(self):
        # counts() reads a missing "labels" as none; the lane must too, or one unlabelled card stops every push.
        bare = item(1, "Build")
        del bare["labels"]
        self.assertEqual(check_backlog.problems([bare, item(2, "Build")]), [])

    def test_an_expedite_lends_ready_no_place(self):
        # The expedite enters Build (the spec's table): a working stage may hold it one over its limit, Ready never may.
        cards = [item(1), item(2), item(3), item(4), item(5), item(9, labels=("story", "expedite"))]
        self.assertEqual(check_backlog.problems(cards),
                         ["Ready holds 6 (#1, #2, #3, #4, #5, #9) — its limit is 5: the PO moves one back to Idea"])

    def test_the_bin_s_cards_in_flight_count_in_the_same_total(self):
        spark = [item(1, "Discovery"), item(2, "Design"), item(3, "Build"), item(4, "Review")]
        bin_cards = [item(19, "Build")]
        said = check_backlog.problems(spark, bin_items=bin_cards)
        self.assertEqual(said, ["5 in flight (#1, #2, #3, #4, bin #19) — at most 4: finish one before starting another"])

    def test_the_bin_s_cards_do_not_fill_spark_s_stages(self):
        said = check_backlog.problems([item(1, "Build"), item(2, "Build")], bin_items=[item(19, "Build")])
        self.assertEqual(said, [])

    def test_the_bin_s_board_unread_counts_spark_alone(self):
        self.assertEqual(check_backlog.problems([item(1, "Build")], bin_items=None), [])

    def test_the_bin_s_cards_outside_a_working_stage_or_riding_on_a_story_do_not_fly(self):
        # Spark's four are the cap. Not one of the bin's six is a fifth: a card in Idea, Ready or Done is no work in flight,
        # neither is one with no Status, a task under its story rides on it, and an epic in Build is its stories' (counts()).
        spark = [item(1, "Discovery"), item(2, "Design"), item(3, "Build"), item(4, "Review")]
        bin_cards = [item(20, "Idea"), item(21, "Ready"), item(22, "Done"), item(23, None),
                     item(24, "Build", labels=("task",), parent=19), item(25, "Build", labels=("epic",))]
        self.assertEqual(check_backlog.problems(spark, bin_items=bin_cards), [])

    def test_the_bin_s_cards_are_asked_for_no_needed_by_and_no_slice(self):
        # Needed by and the slice are spark's: the gate asks them of spark's cards only.
        self.assertEqual(check_backlog.problems([], bin_items=[item(19, "Ready", slice_=None, needed="")]), [])

    def test_a_bin_expedite_lends_the_flight_its_one_extra_place(self):
        spark = [item(1, "Discovery"), item(2, "Design"), item(3, "Build"), item(4, "Review")]
        self.assertEqual(check_backlog.problems(spark, bin_items=[item(19, "Build", labels=("story", "expedite"))]), [])

    def test_a_bin_expedite_lends_none_of_spark_s_stages_a_place(self):
        said = check_backlog.problems([item(1, "Build"), item(2, "Build"), item(3, "Build")],
                                      bin_items=[item(19, "Build", labels=("story", "expedite"))])
        self.assertEqual(said, ["Build holds 3 (#1, #2, #3) — its limit is 2: finish one before starting another"])

    def test_one_expedite_on_each_board_is_two_and_both_are_named(self):
        said = check_backlog.problems([item(1, "Build", labels=("story", "expedite"))],
                                      bin_items=[item(19, "Review", labels=("story", "expedite"))])
        self.assertEqual(said, ["2 cards labelled expedite (#1, bin #19) — one at a time, on the PO's word"])

    def test_two_expedites_in_the_flight_across_both_boards_get_no_extra_place(self):
        spark = [item(1, "Discovery"), item(2, "Design"), item(3, "Build", labels=("story", "expedite")), item(4, "Review")]
        said = check_backlog.problems(spark, bin_items=[item(19, "Build", labels=("story", "expedite"))])
        self.assertEqual(said, ["2 cards labelled expedite (#3, bin #19) — one at a time, on the PO's word",
                                "5 in flight (#1, #2, #3, #4, bin #19) — at most 4: finish one before starting another"])

    def test_a_done_bin_card_keeps_its_label_and_is_not_counted_as_an_expedite(self):
        finished = item(19, "Done", labels=("story", "expedite"))
        self.assertEqual(check_backlog.problems([item(1, "Build", labels=("story", "expedite"))], bin_items=[finished]), [])

    def test_the_bin_s_fifth_card_flies_in_every_working_stage_and_so_does_an_epic_in_discovery(self):
        spark = [item(1, "Discovery"), item(2, "Design"), item(3, "Build"), item(4, "Review")]
        fifths = [item(19, "Discovery"), item(19, "Design"), item(19, "Build"), item(19, "Review"),
                  item(19, "Discovery", labels=("epic",))]
        for fifth in fifths:
            with self.subTest(status=fifth["status"], labels=fifth["labels"]):
                self.assertEqual(check_backlog.problems(spark, bin_items=[fifth]),
                                 ["5 in flight (#1, #2, #3, #4, bin #19) — at most 4: finish one before starting another"])

    def test_a_bench_card_of_the_bin_sits_outside_the_flight_total(self):
        # The spec §1: "A bench session is your hands, so it sits outside them" — the labelled card alone, not the bin's others.
        spark = [item(1, "Discovery"), item(2, "Design"), item(3, "Build"), item(4, "Review")]
        bench = item(19, "Build", labels=("story", "bench"))
        self.assertEqual(check_backlog.problems(spark, bin_items=[bench]), [])
        self.assertEqual(check_backlog.problems(spark, bin_items=[bench, item(20, "Build")]),
                         ["5 in flight (#1, #2, #3, #4, bin #20) — at most 4: finish one before starting another"])

    def test_the_bin_s_undated_wait_is_named_apart_from_spark_s(self):
        said = check_backlog.problems([item(3, "Discovery", waiting="the PO")], bin_items=[item(19, "Idea", waiting="the PO")])
        self.assertEqual(said, ["#3 P3 — x: waits on the PO since nobody knows — set Waiting since",
                                "bin #19 P19 — x: waits on the PO since nobody knows — set Waiting since"])

    def test_the_bin_s_undated_wait_is_named_in_every_open_stage(self):
        # As on spark's board a wait is no commitment-stage question: a card with no Status, or a stage the gate does not
        # know, is named like the rest.
        for status in (None, "Idea", "Discovery", "Design", "Ready", "Build", "Review", "Parked"):
            with self.subTest(status=status):
                self.assertEqual(check_backlog.problems([], bin_items=[item(19, status, waiting="the PO")]),
                                 ["bin #19 P19 — x: waits on the PO since nobody knows — set Waiting since"])

    def test_a_dated_wait_on_the_bin_passes_and_a_done_or_riding_card_s_wait_is_not_judged(self):
        bin_cards = [item(19, "Idea", waiting="the PO", since="2026-10-06"), item(20, "Done", waiting="the PO"),
                     item(21, "Build", labels=("task",), parent=19, waiting="the PO")]
        self.assertEqual(check_backlog.problems([], bin_items=bin_cards), [])

    def test_a_done_item_is_not_judged_again(self):
        self.assertEqual(check_backlog.problems([item(5, "Done", needed="", slice_=None)]), [])

    def test_done_and_idea_carry_no_limit(self):
        self.assertEqual(check_backlog.problems([item(n, "Done") for n in range(9)] + [item(20 + n, "Idea") for n in range(9)]), [])

    def test_the_recorded_board_reads(self):
        # The answer gh printed when the board was migrated keeps every limit, and every card from Ready on has its Needed
        # by and slice. Its one wait — #15, on the PO — was never dated: the rule that names an undated wait (P146) is
        # newer than the recording, so the recording stays as gh printed it and the gate names that wait and nothing else.
        # (It is also real gh output, and `waiting on` is the key it prints.)
        items = json.loads((ROOT / "tests" / "data" / "p102a-items.json").read_text())["items"]
        self.assertTrue(items)
        self.assertEqual(check_backlog.problems(items),
                         ["#15 R2.6 — A fourth cold test: waits on the PO since nobody knows — set Waiting since"],
                         "the board as migrated keeps every limit; only its undated wait is named")

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

    def test_a_parent_matters_for_tasks_only_a_story_under_its_epic_still_counts(self):
        stories = [item(n, "Build", parent=24) for n in (1, 2, 3)]
        self.assertEqual([check_backlog.counts(story) for story in stories], [True, True, True])
        self.assertEqual(check_backlog.problems(stories),
                         ["Build holds 3 (#1, #2, #3) — its limit is 2: finish one before starting another"])

    def test_a_story_under_its_epic_is_still_judged_on_needed_by(self):
        self.assertEqual(check_backlog.problems([item(4, parent=24, needed="")]),
                         ["#4 P4 — x: no `Needed by` — W14: an item names the design that needs it"])

    def test_a_parentless_task_is_judged_on_needed_by_and_slice_like_a_card(self):
        said = check_backlog.problems([item(9, "Ready", labels=("task",), parent=None, slice_="", needed="")])
        self.assertEqual(said, ["#9 P9 — x: no `Needed by` — W14: an item names the design that needs it",
                                "#9 P9 — x: on no slice of the story map"])

    def test_a_wait_with_no_since_is_named(self):
        self.assertEqual(check_backlog.problems([item(3, "Discovery", waiting="the PO")]),
                         ["#3 P3 — x: waits on the PO since nobody knows — set Waiting since"])

    def test_a_dated_wait_passes_and_any_waited_on_name_is_checked(self):
        self.assertEqual(check_backlog.problems([item(3, "Discovery", waiting="the PO", since="2026-10-06")]), [])
        self.assertEqual(check_backlog.problems([item(3, "Discovery", waiting="Petr")]),
                         ["#3 P3 — x: waits on Petr since nobody knows — set Waiting since"])

    def test_a_done_card_s_stale_wait_is_not_judged(self):
        self.assertEqual(check_backlog.problems([item(3, "Done", waiting="the PO")]), [])

    def test_an_undated_wait_is_named_in_every_open_stage_not_only_from_ready_on(self):
        # Unlike Needed by and the slice, a wait is no commitment-stage question: the recorded board's one wait (#15)
        # sits in Idea. A card with no Status, or a stage the gate does not know, is named like the rest.
        for status in (None, "Idea", "Discovery", "Design", "Ready", "Build", "Review", "Parked"):
            with self.subTest(status=status):
                self.assertEqual(check_backlog.problems([item(3, status, waiting="the PO")]),
                                 ["#3 P3 — x: waits on the PO since nobody knows — set Waiting since"])

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

    def test_parents_that_gh_printed_as_non_json_says_why(self):
        def run(args, **kwargs):
            return mock.Mock(stdout="gh: HTTP 502 Bad Gateway")
        with mock.patch.object(check_backlog.subprocess, "run", run):
            self.assertEqual(check_backlog.parents([("xmejkal/spark", 9)]), ({}, "JSONDecodeError"))

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

    def board_answering(self, items, parents, bin_cards=()):
        """
        A gh that lists the spark project (number 2) holding `items` and the bin's (number 1) holding `bin_cards` — as gh
        prints them, with no `parent` — and answers the parents query with `parents`. Each of the three is raised when it
        is an exception. Returns it with the commands it was asked, as text.
        """
        asked = []

        def run(args, **kwargs):
            asked.append(" ".join(args))
            if "graphql" in args:
                answer = parents
            elif "item-list" in args:
                cards = items if args[args.index("item-list") + 1] == "2" else bin_cards
                answer = cards if isinstance(cards, Exception) else {"items": [{k: v for k, v in e.items() if k != "parent"}
                                                                               for e in cards]}
            else:
                answer = {"projects": [{"number": 2, "title": "spark"}, {"number": 1, "title": "the bin"}]}
            if isinstance(answer, Exception):
                raise answer
            return mock.Mock(stdout=json.dumps(answer))
        return run, asked

    def test_main_asks_for_each_open_task_s_parent_and_a_task_under_its_story_rides_on_it(self):
        items = [item(1, "Build"), item(2, "Build"), item(9, "Build", labels=("task",)), item(8, "Done", labels=("task",))]
        run, asked = self.board_answering(items, {"data": {"r0": {"t9": {"parent": {"number": 1}}}}})
        code, printed = self.said(run)
        self.assertEqual(code, 0)
        self.assertIn("  backlog: 3 open, the limits hold; the bin: 0 open", printed)
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
        self.assertIn("  backlog: 3 open, the limits hold; the bin: 0 open", printed)
        self.assertIn("  backlog: tasks' parent stories could not be read (TimeoutExpired) — every task counted as riding on a story",
                      printed)

    def test_a_task_item_missing_its_repository_or_number_is_unread_not_a_traceback(self):
        # The gate must never stop a push by failing itself: data it cannot use is a could-not-look, said with its cause.
        cases = (("no repository", lambda content: content.pop("repository"), "AttributeError"),
                 ("a None repository", lambda content: content.update(repository=None), "AttributeError"),
                 ("a repository with no owner", lambda content: content.update(repository="spark"), "ValueError"),
                 ("no number", lambda content: content.pop("number"), "TypeError"))
        for name, damage, cause in cases:
            with self.subTest(name):
                task = item(9, "Build", labels=("task",))
                damage(task["content"])
                run, _ = self.board_answering([item(1, "Build"), item(2, "Build"), task], {"data": {}})
                code, printed = self.said(run)
                self.assertEqual(code, 0)
                self.assertIn("  backlog: 3 open, the limits hold; the bin: 0 open", printed)
                self.assertIn("tasks' parent stories could not be read (%s) — every task counted as riding on a story" % cause, printed)

    def test_unread_parents_do_not_hide_a_broken_limit(self):
        items = [item(1, "Build"), item(2, "Build"), item(3, "Build"), item(9, "Build", labels=("task",))]
        run, _ = self.board_answering(items, subprocess.TimeoutExpired("gh", 60))
        code, printed = self.said(run)
        self.assertEqual(code, 1)
        self.assertIn("    Build holds 3 (#1, #2, #3) — its limit is 2: finish one before starting another", printed)
        self.assertIn("tasks' parent stories could not be read (TimeoutExpired)", printed)

    def test_fetch_reads_both_boards_and_asks_every_open_task_s_parent_in_one_call(self):
        bin_repository = "xmejkal/sisuo-brain-transplant"
        spark_cards = [item(1, "Build"), item(2, "Build", labels=("task",))]
        bin_cards = [item(19, "Build", repository=bin_repository), item(20, "Build", labels=("task",), repository=bin_repository)]
        answer = {"data": {"r0": {"t2": {"parent": {"number": 1}}}, "r1": {"t20": {"parent": {"number": 19}}}}}
        run, asked = self.board_answering(spark_cards, answer, bin_cards)
        with mock.patch.object(check_backlog.subprocess, "run", side_effect=run):
            items, bin_items, why, bin_why = check_backlog.fetch()
        self.assertEqual((why, bin_why), (None, None))
        self.assertEqual([(e["content"]["number"], e["parent"]) for e in items], [(1, None), (2, 1)])
        self.assertEqual([(e["content"]["number"], e["parent"]) for e in bin_items], [(19, None), (20, 19)])
        questions = [command for command in asked if "graphql" in command]
        self.assertEqual(len(questions), 1)
        self.assertIn('r0: repository(owner: "xmejkal", name: "spark") { t2: issue(number: 2)', questions[0])
        self.assertIn('r1: repository(owner: "xmejkal", name: "sisuo-brain-transplant") { t20: issue(number: 20)', questions[0])

    def test_fetch_keeps_spark_s_items_when_the_bin_s_board_cannot_be_listed(self):
        run, _ = self.board_answering([item(1, "Build")], {"data": {}}, subprocess.TimeoutExpired("gh", 60))
        with mock.patch.object(check_backlog.subprocess, "run", side_effect=run):
            items, bin_items, why, bin_why = check_backlog.fetch()
        self.assertEqual(([e["content"]["number"] for e in items], bin_items, why, bin_why), ([1], None, None, "TimeoutExpired"))

    def listing_only_spark(self):
        """A gh whose project list holds spark's project and not the bin's."""
        def run(args, **kwargs):
            if "item-list" in args:
                return mock.Mock(stdout=json.dumps({"items": [item(1, "Build")]}))
            return mock.Mock(stdout=json.dumps({"projects": [{"number": 2, "title": "spark"}]}))
        return run

    def test_fetch_says_when_the_project_list_has_no_bin_project(self):
        with mock.patch.object(check_backlog.subprocess, "run", side_effect=self.listing_only_spark()):
            items, bin_items, why, bin_why = check_backlog.fetch()
        self.assertEqual(([e["content"]["number"] for e in items], bin_items, why, bin_why),
                         ([1], None, None, "no project titled 'the bin' under xmejkal"))

    def test_main_says_when_the_bin_s_board_was_not_read(self):
        run, _ = self.board_answering([item(1, "Build")], {"data": {}}, subprocess.TimeoutExpired("gh", 60))
        code, printed = self.said(run)
        self.assertEqual(code, 0)
        self.assertIn("  backlog: 1 open, the limits hold\n", printed)
        self.assertIn("  backlog: the bin's board could not be read (TimeoutExpired) — its cards in flight were not counted",
                      printed)

    def test_main_says_when_the_project_list_has_no_bin_project(self):
        code, printed = self.said(self.listing_only_spark())
        self.assertEqual(code, 0)
        self.assertIn("  backlog: 1 open, the limits hold\n", printed)
        self.assertIn("  backlog: the bin's board could not be read (no project titled 'the bin' under xmejkal) — "
                      "its cards in flight were not counted", printed)

    def test_the_summary_says_how_many_of_the_bin_s_cards_are_open(self):
        # Said when the bin was read, as the note is said when it was not: a Done card is no open card.
        run, _ = self.board_answering([item(1, "Build")], {"data": {}}, [item(19, "Build"), item(20, "Idea"), item(21, "Done")])
        code, printed = self.said(run)
        self.assertEqual(code, 0)
        self.assertIn("  backlog: 1 open, the limits hold; the bin: 2 open\n", printed)

    def test_main_says_nothing_of_the_bin_when_its_board_was_read(self):
        run, _ = self.board_answering([item(1, "Build")], {"data": {}}, [item(19, "Build")])
        code, printed = self.said(run)
        self.assertEqual(code, 0)
        self.assertIn("  backlog: 1 open, the limits hold; the bin: 1 open", printed)
        self.assertNotIn("could not be read", printed)

    def test_an_unread_bin_board_does_not_hide_a_broken_limit(self):
        run, _ = self.board_answering([item(1, "Build"), item(2, "Build"), item(3, "Build")], {"data": {}},
                                      subprocess.TimeoutExpired("gh", 60))
        code, printed = self.said(run)
        self.assertEqual(code, 1)
        self.assertIn("    Build holds 3 (#1, #2, #3) — its limit is 2: finish one before starting another", printed)
        self.assertIn("the bin's board could not be read (TimeoutExpired)", printed)

    def test_main_counts_the_bin_s_cards_in_flight_and_a_bin_task_under_its_story_rides_on_it(self):
        bin_repository = "xmejkal/sisuo-brain-transplant"
        spark_cards = [item(1, "Discovery"), item(2, "Design"), item(3, "Build"), item(4, "Review")]
        bin_cards = [item(19, "Build", repository=bin_repository), item(20, "Build", labels=("task",), repository=bin_repository)]
        run, _ = self.board_answering(spark_cards, {"data": {"r0": {"t20": {"parent": {"number": 19}}}}}, bin_cards)
        code, printed = self.said(run)
        self.assertEqual(code, 1)
        self.assertIn("  backlog: 4 open, 1 problem(s); the bin: 2 open", printed)
        self.assertIn("    5 in flight (#1, #2, #3, #4, bin #19) — at most 4: finish one before starting another", printed)
        self.assertNotIn("could not be read", printed)

    def test_unread_parents_leave_the_bin_s_tasks_riding_too(self):
        spark_cards = [item(1, "Discovery"), item(2, "Design"), item(3, "Build"), item(4, "Review")]
        bin_cards = [item(20, "Build", labels=("task",), repository="xmejkal/sisuo-brain-transplant")]
        run, _ = self.board_answering(spark_cards, subprocess.TimeoutExpired("gh", 60), bin_cards)
        code, printed = self.said(run)
        self.assertEqual(code, 0)
        self.assertIn("  backlog: 4 open, the limits hold; the bin: 1 open", printed)
        self.assertIn("tasks' parent stories could not be read (TimeoutExpired)", printed)

    def test_a_spark_board_that_cannot_be_listed_skips_the_look_and_passes(self):
        run, _ = self.board_answering(subprocess.TimeoutExpired("gh", 60), {"data": {}})
        code, printed = self.said(run)
        self.assertEqual(code, 0)
        self.assertIn("  backlog: skipped — gh or the network could not be reached (TimeoutExpired)", printed)

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
