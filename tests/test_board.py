"""P102c: the state of both boards in a dozen lines, and the day-close (docs/2026-10-05-session-status-design.md)."""

import contextlib
import datetime as dt
import io
import os
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ itself: suite_temp, however the suite is run
import suite_temp  # noqa: E402,F401  P172: this process's temp folder, removed at exit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import board  # noqa: E402

TODAY = dt.date(2026, 10, 7)
BODY = "### Needed by\n\nthe PO\n\n### Value proven by\n\nx\n"


def node(number, title, status, changed="2026-10-05T10:00:00Z", labels=("story",), waiting=None, since=None, slice_="team tools",
         parent=None, parent_closed=False):
    values = [{"name": status, "updatedAt": changed, "field": {"name": "Status"}},
              {"name": slice_, "updatedAt": changed, "field": {"name": "Slice"}}, {}]
    if waiting:
        values.append({"name": waiting, "updatedAt": changed, "field": {"name": "Waiting on"}})
    if since:
        values.append({"date": since, "field": {"name": "Waiting since"}})
    return {"content": {"number": number, "title": title, "body": BODY, "repository": {"name": "spark"},
                        "labels": {"nodes": [{"name": label} for label in labels]},
                        "parent": {"number": parent, "closed": parent_closed} if parent else None},
            "fieldValues": {"nodes": values}}


def project(*nodes):
    return {"id": "P", "items": {"totalCount": len(nodes), "nodes": list(nodes)}, "statusUpdates": {"nodes": []}}


# R2.6 says since when it waits on the PO: since P146 the gate names a Waiting on with no Waiting since, and this is the
# board whose limits hold (the status and the close read the gate's verdict). A wait nobody dated is its own card, in
# the one test that needs it.
SPARK = board.to_items(project(
    node(26, "P102c — The state in view", "Build", "2026-10-05T10:00:00Z"),
    node(24, "P102 — The tools chore", "Build", labels=("epic",)),
    node(32, "P103 — The process documented", "Ready"),
    node(18, "P97 — Store 1c", "Ready"),
    node(15, "R2.6 — A fourth cold test", "Idea", waiting="the PO", since="2026-10-05"),
    {"content": {}, "fieldValues": {"nodes": []}}))
BIN = board.to_items(project(node(1, "B1 — Identify the audio module", "Idea", waiting="the PO", since="2026-09-25")))
# Spark's four cards in flight are the cap (P146); a fifth, flying on the bin's board, breaks it.
SPARK_AT_THE_CAP = board.to_items(project(node(1, "P1 — a", "Discovery"), node(2, "P2 — b", "Design"),
                                          node(3, "P3 — c", "Build"), node(4, "P4 — d", "Review")))
BIN_FIFTH = board.to_items(project(node(19, "B19 — e", "Build")))


class FixedToday(dt.date):
    """A `date` whose today() is 2026-10-09, patched in for board.dt in the tests that drive main()."""

    @classmethod
    def today(cls):
        return cls(2026, 10, 9)


class TheCoreTest(unittest.TestCase):
    def test_items_carry_status_slice_waiting_and_when_status_changed(self):
        first = SPARK[0]
        self.assertEqual((first["status"], first["slice"], first["status_changed"], first["content"]["number"]),
                         ("Build", "team tools", "2026-10-05T10:00:00Z", 26))
        self.assertEqual((BIN[0]["waiting on"], BIN[0]["waiting since"]), ("the PO", "2026-09-25"))

    def test_a_board_item_that_is_not_an_issue_is_skipped(self):
        self.assertEqual(len(SPARK), 5)

    def test_in_flight_names_stage_item_and_age_and_leaves_an_epic_in_build_out(self):
        self.assertEqual(board.in_flight(SPARK, TODAY), ["Build P102c (#26) 2 d"])

    def test_in_flight_shows_an_epic_in_discovery_or_design_but_not_in_build_and_never_a_task_under_its_story(self):
        # P146: the status counts as the check does (check_backlog.counts), so it cannot hide what the gate counts. The
        # story sits under its epic (parent 24) and still counts: a parent changes how a task counts, and nothing else.
        crowded = board.to_items(project(node(70, "P136 — Full circuit checks", "Discovery", labels=("epic",)),
                                         node(71, "P100 — The flows", "Design", labels=("epic",)),
                                         node(24, "P102 — The tools chore", "Build", labels=("epic",)),
                                         node(29, "P102e — A discovery skill", "Build", parent=24),
                                         node(31, "P102e step one", "Build", labels=("task",), parent=29)))
        self.assertEqual(board.in_flight(crowded, TODAY),
                         ["Discovery P136 (#70) 2 d", "Design P100 (#71) 2 d", "Build P102e (#29) 2 d"])

    def test_items_carry_a_task_s_parent_story(self):
        items = board.to_items(project(node(9, "T9 — x", "Build", labels=("task",), parent=1), node(10, "T10 — y", "Build", labels=("task",))))
        self.assertEqual([i.get("parent") for i in items], [1, None])

    def test_a_task_under_a_closed_story_is_a_card_of_its_own_in_the_flight(self):
        # The same rule as the gate's (check_backlog.open_parent): a finished story carries nothing, so its task counts.
        items = board.to_items(project(node(29, "P102e — A story", "Build"),
                                       node(31, "P102e step one", "Build", labels=("task",), parent=29, parent_closed=True),
                                       node(32, "P102e step two", "Build", labels=("task",), parent=29)))
        self.assertEqual([i["parent"] for i in items], [None, None, 29])
        self.assertEqual(board.in_flight(items, TODAY), ["Build P102e (#29) 2 d", "Build P102e step one (#31) 2 d"])

    def test_in_flight_counts_a_parentless_task_as_a_card(self):
        items = board.to_items(project(node(10, "T10 — y", "Build", labels=("task",))))
        self.assertEqual(board.in_flight(items, dt.date(2026, 10, 9)), ["Build T10 (#10) 4 d"])

    def test_waiting_on_the_po_says_since_when_and_marks_more_than_three_days(self):
        self.assertEqual(board.all_waiting([("spark", BIN)], TODAY), ["B1 (#1) since 2026-09-25, 12 d !"])
        self.assertEqual(board.all_waiting([("spark", SPARK)], TODAY), ["R2.6 (#15) since 2026-10-05, 2 d"])
        undated = board.to_items(project(node(16, "R2.7 — A wait nobody dated", "Idea", waiting="the PO")))
        self.assertEqual(board.all_waiting([("spark", undated)], TODAY), ["R2.7 (#16)"])

    def test_waits_are_listed_oldest_first_and_an_undated_one_last(self):
        items = board.to_items(project(node(1, "A — x", "Discovery", waiting="the PO", since="2026-10-07"),
                                       node(2, "B — y", "Idea", waiting="the PO", since="2026-10-01"),
                                       node(3, "C — z", "Idea", waiting="the PO")))
        self.assertEqual(board.all_waiting([("spark", items)], dt.date(2026, 10, 9)),
                         ["B (#2) since 2026-10-01, 8 d !", "A (#1) since 2026-10-07, 2 d", "C (#3)"])

    def test_a_wait_on_anyone_is_listed_and_a_finished_card_s_is_not(self):
        # Task 4's rule: a card that waits on someone (any name) is asked since when; the list shows every open one.
        items = board.to_items(project(node(1, "A — x", "Idea", waiting="Anna", since="2026-10-07"),
                                       node(2, "B — y", "Done", waiting="the PO", since="2026-10-01"),
                                       node(3, "C — z", "Idea")))
        self.assertEqual(board.all_waiting([("spark", items)], dt.date(2026, 10, 9)), ["A (#1) on Anna since 2026-10-07, 2 d"])

    def test_a_wait_on_someone_other_than_the_po_says_who_dated_or_not(self):
        # The line is headed "waits on the PO:" and lists every open wait; a wait on Anna must not read as the PO's.
        items = board.to_items(project(node(1, "A — x", "Idea", waiting="Anna", since="2026-10-01"),
                                       node(2, "B — y", "Idea", waiting="the PO", since="2026-10-01"),
                                       node(16, "R2.7 — A wait nobody dated", "Idea", waiting="Anna")))
        self.assertEqual(board.all_waiting([("spark", items)], dt.date(2026, 10, 9)),
                         ["A (#1) on Anna since 2026-10-01, 8 d !", "B (#2) since 2026-10-01, 8 d !", "R2.7 (#16) on Anna"])

    def test_ready_down_to_two_is_said_and_three_is_not(self):
        two = board.to_items(project(node(1, "A — x", "Ready"), node(2, "B — y", "Ready")))
        three = board.to_items(project(node(1, "A — x", "Ready"), node(2, "B — y", "Ready"), node(3, "C — z", "Ready")))
        lines_two = board.status_lines([("spark", two), ("bin", [])], [], [], set(), dt.date(2026, 10, 9))
        lines_three = board.status_lines([("spark", three), ("bin", [])], [], [], set(), dt.date(2026, 10, 9))
        self.assertIn("  ! Ready is down to 2 — propose an order for the PO", lines_two)
        self.assertFalse(any("Ready is down" in line for line in lines_three))

    def test_an_empty_ready_keeps_its_own_line(self):
        lines = board.status_lines([("spark", []), ("bin", [])], [], [], set(), dt.date(2026, 10, 9))
        self.assertIn("  Ready: empty — the PO refills it", lines)
        self.assertFalse(any("Ready is down" in line for line in lines))

    def test_an_undated_wait_reaches_the_status_and_puts_the_close_at_risk(self):
        items = board.to_items(project(node(16, "R2.7 — A wait nobody dated", "Idea", waiting="the PO")))
        lines = board.status_lines([("spark", items), ("bin", [])], [], [], set(), dt.date(2026, 10, 9))
        self.assertIn("spark — 1 open, 1 problem(s) · trial check 2026-11-02", lines)
        self.assertIn("  ! #16 R2.7 — A wait nobody dated: waits on the PO since nobody knows — set Waiting since", lines)
        status, _ = board.close_update("x", [("spark", items), ("bin", [])], set(), dt.date(2026, 10, 9), dt.date(2026, 10, 9))
        self.assertEqual(status, "AT_RISK")

    def test_the_flight_line_names_the_card_that_holds_the_expedite_lane(self):
        spark = board.to_items(project(node(1, "P1 — a", "Build", labels=("story", "expedite")), node(2, "P2 — b", "Design")))
        self.assertEqual(board.in_flight(spark, TODAY), ["Build P1 (#1) 2 d (expedite)", "Design P2 (#2) 2 d"])
        lines = board.status_lines([("spark", spark), ("bin", [])], [], [], set(), TODAY)
        self.assertIn("  in flight: Build P1 (#1) 2 d (expedite), Design P2 (#2) 2 d", lines)

    def test_a_bench_session_is_listed_and_marked_though_the_flight_total_leaves_it_out(self):
        # Four cards are the cap; the bin's bench card is a fifth in the list and not in the count, on purpose
        # (check_backlog.BENCH: the PO's own hands sit outside the limits), so the line says why the two differ.
        bench = board.to_items(project(node(7, "B7 — c", "Build", labels=("bench",))))
        lines = board.status_lines([("spark", SPARK_AT_THE_CAP), ("bin", bench)], [], [], set(), TODAY)
        self.assertEqual(lines[:2], [
            "spark — 4 open, the limits hold · trial check 2026-11-02",
            "  in flight: Discovery P1 (#1) 2 d, Design P2 (#2) 2 d, Build P3 (#3) 2 d, Review P4 (#4) 2 d, bin Build B7 (#7) 2 d (bench)"])

    def test_a_card_that_is_the_expedite_and_a_bench_session_shows_both_marks(self):
        both = board.to_items(project(node(1, "P1 — a", "Build", labels=("story", "expedite", "bench"))))
        self.assertEqual(board.in_flight(both, TODAY), ["Build P1 (#1) 2 d (expedite) (bench)"])

    def test_the_waits_of_both_boards_are_listed_together_oldest_first_and_an_undated_one_last(self):
        # The spec: the status prints every wait, oldest first — not each board's own list one after the other.
        undated = board.to_items(project(node(16, "B16 — A wait nobody dated", "Idea", waiting="the PO")))
        self.assertEqual(board.all_waiting([("spark", SPARK), ("bin", undated + BIN)], TODAY),
                         ["bin B1 (#1) since 2026-09-25, 12 d !", "R2.6 (#15) since 2026-10-05, 2 d", "bin B16 (#16)"])

    def test_the_close_lists_the_waits_of_both_boards_oldest_first_too(self):
        _, body = board.close_update("x", [("spark", SPARK), ("bin", BIN)], set(), TODAY, TODAY)
        self.assertEqual(body.split("\n\n")[2],
                         "waits on the PO: bin B1 (#1) since 2026-09-25, 12 d !, R2.6 (#15) since 2026-10-05, 2 d")

    def status_from_main(self, items, closes, days):
        """What `status` prints on 2026-10-09 for spark's `items`, and the work_days mock; `days` are the days with a commit."""
        out = io.StringIO()
        shown = types.SimpleNamespace(date=FixedToday, timedelta=dt.timedelta)
        with mock.patch.object(board, "dt", shown), \
                mock.patch.object(board, "gather", return_value=([("spark", items), ("bin", [])], [], closes, "P")), \
                mock.patch.object(board, "work_days", side_effect=lambda dirs, since: {d for d in days if d >= since}) as git, \
                contextlib.redirect_stdout(out):
            self.assertEqual(board.main(["status"]), 0)
        return out.getvalue().splitlines(), git

    def epic_with_an_appetite(self, changed):
        """An epic in Discovery whose card carries an Appetite of 3 — a number field the board holds as process data."""
        epic = node(5, "E — x", "Discovery", changed=changed, labels=("epic",))
        epic["fieldValues"]["nodes"].append({"number": 3, "field": {"name": "Appetite"}})
        return board.to_items(project(epic))

    def test_the_status_says_nothing_of_an_appetite(self):
        # The PO, 2026-10-09 (Q5 on #80): the appetite is process data he sets and reads on the board — spark does not
        # read it. Five working days since the epic's stage began, against an Appetite of 3, and no line names it.
        days = {dt.date(2026, 10, 1), dt.date(2026, 10, 2), dt.date(2026, 10, 6), dt.date(2026, 10, 8), dt.date(2026, 10, 9)}
        lines, _ = self.status_from_main(self.epic_with_an_appetite("2026-10-01T09:00:00Z"), [(dt.date(2026, 10, 8), "closed")], days)
        self.assertIn("  in flight: Discovery E (#5) 8 d", lines)
        self.assertEqual([line for line in lines if "appetite" in line.lower()], [])

    def test_the_working_days_are_read_from_the_last_close(self):
        # Only a day with no close needs the working days, and it lies after the newest close: an epic's stage that began
        # before it, Appetite or not, does not widen the read; with no close yet, two weeks are read.
        epic = self.epic_with_an_appetite("2026-10-01T09:00:00Z")
        closes = [(dt.date(2026, 10, 1), "older"), (dt.date(2026, 10, 5), "closed")]
        lines, git = self.status_from_main(epic, closes, {dt.date(2026, 10, 2), dt.date(2026, 10, 6), dt.date(2026, 10, 9)})
        self.assertIn("  ! the day of 2026-10-06 has no close — write it first", lines)
        self.assertEqual(git.call_args.args[1], dt.date(2026, 10, 5))
        _, git = self.status_from_main(epic, [], set())
        self.assertEqual(git.call_args.args[1], dt.date(2026, 9, 25))

    def test_ready_keeps_the_board_s_order(self):
        self.assertEqual(board.ready(SPARK), ["P103 (#32)", "P97 (#18)"])

    def test_a_missing_close_is_the_last_working_day_before_today_only(self):
        days = {dt.date(2026, 10, 1), dt.date(2026, 10, 5), dt.date(2026, 10, 7)}
        self.assertEqual(board.missing_close(days, set(), TODAY), dt.date(2026, 10, 5))
        self.assertIsNone(board.missing_close(days, {dt.date(2026, 10, 5)}, TODAY))
        self.assertIsNone(board.missing_close({dt.date(2026, 10, 7)}, set(), TODAY), "today's work is not closed yet")

    def test_inside_is_true_only_within_the_named_folders(self):
        root = Path(tempfile.mkdtemp())
        (root / "spark" / "docs").mkdir(parents=True)
        (root / "other").mkdir()
        self.assertTrue(board.inside(root / "spark" / "docs", [str(root / "spark")]))
        self.assertFalse(board.inside(root / "other", [str(root / "spark")]))

    def test_the_status_lines(self):
        lines = board.status_lines([("spark", SPARK), ("bin", BIN)], [("spark", 34, "P102c: the state in view", True)],
                                   [(dt.date(2026, 10, 5), "P102a merged; P102c designed")], {dt.date(2026, 10, 6)}, TODAY)
        self.assertEqual(lines, [
            "spark — 5 open, the limits hold · trial check 2026-11-02",
            "  in flight: Build P102c (#26) 2 d",
            "  waits on the PO: bin B1 (#1) since 2026-09-25, 12 d !, R2.6 (#15) since 2026-10-05, 2 d",
            "  Ready: P103 (#32), P97 (#18)",
            "  ! Ready is down to 2 — propose an order for the PO",
            "  open PRs: spark #34 P102c: the state in view (draft)",
            "  last close 2026-10-05: P102a merged; P102c designed",
            "  ! the day of 2026-10-06 has no close — write it first"])

    def test_the_status_counts_the_bin_s_cards_in_the_same_flight_total(self):
        lines = board.status_lines([("spark", SPARK_AT_THE_CAP), ("bin", BIN_FIFTH)], [], [], set(), TODAY)
        self.assertEqual(lines[:3], [
            "spark — 4 open, 1 problem(s) · trial check 2026-11-02",
            "  ! 5 in flight (#1, #2, #3, #4, bin #19) — at most 4: finish one before starting another",
            "  in flight: Discovery P1 (#1) 2 d, Design P2 (#2) 2 d, Build P3 (#3) 2 d, Review P4 (#4) 2 d, bin Build B19 (#19) 2 d"])

    def test_the_status_says_when_the_bin_board_was_not_given(self):
        lines = board.status_lines([("spark", SPARK)], [], [], set(), TODAY)
        self.assertIn("  ! the bin's board could not be read (no bin board was given) — its cards were not counted or checked", lines)
        both = board.status_lines([("spark", SPARK), ("bin", BIN)], [], [], set(), TODAY)
        self.assertFalse(any("could not be read" in line for line in both))

    def test_the_bin_s_undated_wait_reaches_the_status_and_puts_the_close_at_risk(self):
        undated = board.to_items(project(node(16, "B16 — A wait nobody dated", "Idea", waiting="the PO")))
        lines = board.status_lines([("spark", SPARK), ("bin", undated)], [], [], set(), TODAY)
        self.assertEqual(lines[0], "spark — 5 open, 1 problem(s) · trial check 2026-11-02")
        self.assertIn("  ! bin #16 B16 — A wait nobody dated: waits on the PO since nobody knows — set Waiting since", lines)
        state, _ = board.close_update("x", [("spark", SPARK), ("bin", undated)], set(), TODAY, TODAY)
        self.assertEqual(state, "AT_RISK")

    def test_closes_skip_an_update_made_by_hand_with_no_start_date(self):
        made = {"statusUpdates": {"nodes": [{"startDate": "2026-10-05", "status": "ON_TRACK", "body": "P102a merged\n\nin flight: …"},
                                           {"startDate": None, "status": "AT_RISK", "body": "by hand"}]}}
        self.assertEqual(board.closes_from(made), [(dt.date(2026, 10, 5), "P102a merged")])

    def test_a_day_closed_already_is_refused_with_its_date(self):
        with self.assertRaisesRegex(ValueError, "2026-10-06 is closed already"):
            board.close_update("x", [("spark", SPARK), ("bin", BIN)], {dt.date(2026, 10, 6)}, dt.date(2026, 10, 6), TODAY)

    def test_a_close_is_at_risk_when_the_po_is_waited_on_too_long_or_a_limit_breaks(self):
        state, body = board.close_update("P102c built", [("spark", SPARK), ("bin", BIN)], set(), TODAY, TODAY)
        self.assertEqual(state, "AT_RISK", "B1 has waited 12 days")
        self.assertEqual(body.split("\n\n")[0], "P102c built")
        state, _ = board.close_update("P102c built", [("spark", SPARK)], set(), TODAY, TODAY)
        self.assertEqual(state, "ON_TRACK")

    def test_a_close_is_at_risk_when_a_limit_breaks_even_with_no_one_waiting(self):
        # Build's limit is 2 (P146): SPARK holds one card in Build, so a second is the limit and a third breaks it.
        at_the_limit = SPARK + board.to_items(project(node(27, "P102d — Proofs", "Build")))
        state, _ = board.close_update("two in Build", [("spark", at_the_limit)], set(), TODAY, TODAY)
        self.assertEqual(state, "ON_TRACK")
        crowded = at_the_limit + board.to_items(project(node(28, "P102e — A discovery skill", "Build")))
        state, _ = board.close_update("three in Build", [("spark", crowded)], set(), TODAY, TODAY)
        self.assertEqual(state, "AT_RISK")

    def test_a_close_is_at_risk_when_the_bin_s_cards_break_the_flight_total(self):
        # The close reads the verdict the status prints (the session-status design: no second rule).
        state, _ = board.close_update("five in flight", [("spark", SPARK_AT_THE_CAP), ("bin", BIN_FIFTH)], set(), TODAY, TODAY)
        self.assertEqual(state, "AT_RISK")
        state, _ = board.close_update("four in flight", [("spark", SPARK_AT_THE_CAP), ("bin", [])], set(), TODAY, TODAY)
        self.assertEqual(state, "ON_TRACK")

    def test_status_offline_says_why_and_exits_zero(self):
        out = io.StringIO()
        with mock.patch.object(board, "gather", side_effect=RuntimeError("could not resolve host")), contextlib.redirect_stdout(out):
            self.assertEqual(board.main(["status"]), 0)
        # W1: a look that could not be made is could-not-run; `skipped` is a check nobody asked for (P146 council, C4).
        self.assertEqual(out.getvalue(), "board: could-not-run — could not resolve host\n")

    def test_status_outside_the_named_folders_prints_nothing(self):
        out = io.StringIO()
        with mock.patch.object(board, "gather") as gather, contextlib.redirect_stdout(out):
            self.assertEqual(board.main(["status", "--when-in", tempfile.mkdtemp()]), 0)
        self.assertEqual((out.getvalue(), gather.called), ("", False))

    def test_a_close_that_cannot_read_the_boards_says_could_not_run_posts_nothing_and_fails(self):
        out = io.StringIO()
        logged_out = RuntimeError("gh: To get started with GitHub CLI, please run: gh auth login")
        with mock.patch.object(board, "gather", side_effect=logged_out), mock.patch.object(board, "_gh") as gh, \
                contextlib.redirect_stdout(out):
            self.assertEqual(board.main(["close", "P102c built"]), 1)
        self.assertFalse(gh.called)
        self.assertEqual(out.getvalue(), "board: could-not-run — gh: To get started with GitHub CLI, please run: gh auth login\n")

    def test_close_dry_run_posts_nothing(self):
        out = io.StringIO()
        with mock.patch.object(board, "gather", return_value=([("spark", SPARK)], [], [], "P")), \
                mock.patch.object(board, "_gh") as gh, contextlib.redirect_stdout(out):
            self.assertEqual(board.main(["close", "P102c built", "--dry-run"]), 0)
        self.assertFalse(gh.called)
        self.assertIn("dry run", out.getvalue())


class TheFinalReviewTest(unittest.TestCase):
    """The P102c final review: the newest closes, a short read said, offline in seconds, any branch, never a traceback."""

    def test_the_query_reads_the_newest_status_updates(self):
        # GitHub lists status updates newest first, so last:N would read the oldest N (C1).
        self.assertIn("statusUpdates(first:20,orderBy:{field:CREATED_AT,direction:DESC})", board.QUERY)

    def test_the_query_reads_each_issue_s_parent_story(self):
        # A task with no parent story is a card of its own (P146): the status must be told whose sub-issue each one is.
        self.assertIn("parent{number closed}", board.QUERY)

    def test_a_board_read_short_says_how_many_it_holds(self):
        held = project(node(1, "P1 — x", "Ready"))
        held["items"]["totalCount"] = 130
        self.assertEqual(board.unread("spark", held), "the spark board holds 130 items, 1 were read")
        self.assertIsNone(board.unread("spark", project(node(1, "P1 — x", "Ready"))))

    def test_a_silent_network_gives_up_on_the_status_in_seconds(self):
        out = io.StringIO()
        stalled = subprocess.TimeoutExpired(["gh"], board.STATUS_TIMEOUT)
        with mock.patch.object(board.subprocess, "run", side_effect=stalled) as run, contextlib.redirect_stdout(out):
            self.assertEqual(board.main(["status"]), 0)
        self.assertEqual(run.call_args.kwargs["timeout"], board.STATUS_TIMEOUT)
        self.assertLessEqual(board.STATUS_TIMEOUT, 10)
        self.assertEqual(out.getvalue(), "board: could-not-run — gh did not answer in %d s\n" % board.STATUS_TIMEOUT)

    def test_working_days_are_commits_on_any_branch_in_the_named_folders(self):
        root = Path(tempfile.mkdtemp())
        own = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}

        def git(*args, when=None):
            dated = {"GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when} if when else {}
            subprocess.run(["git", "-C", str(root), "-c", "user.email=t@t", "-c", "user.name=t", *args],
                           check=True, capture_output=True, env=dict(own, **dated))
        git("init", "-q")
        git("commit", "-q", "--allow-empty", "-m", "before", when="2026-09-20T12:00:00")
        # A date alone means "this time of day" to git, so a commit in the first minute of the first day was lost.
        git("commit", "-q", "--allow-empty", "-m", "first minute of the first day", when="2026-10-01T00:00:30")
        git("commit", "-q", "--allow-empty", "-m", "on main", when="2026-10-03T12:00:00")
        git("checkout", "-q", "-b", "work")
        git("commit", "-q", "--allow-empty", "-m", "on a branch only", when="2026-10-05T12:00:00")
        git("checkout", "-q", "-")
        # A hook's GIT_DIR must not steer the read to another repository (the P105 leak).
        with mock.patch.dict(os.environ, {"GIT_DIR": tempfile.mkdtemp()}):
            days = board.work_days([str(root), tempfile.mkdtemp()], dt.date(2026, 10, 1))
        self.assertEqual(days, {dt.date(2026, 10, 1), dt.date(2026, 10, 3), dt.date(2026, 10, 5)})

    def test_status_says_could_not_run_whatever_breaks(self):
        out = io.StringIO()
        with mock.patch.object(board, "gather", return_value=([("spark", SPARK)], [], [], "P")), \
                mock.patch.object(board, "status_lines", side_effect=AttributeError("'NoneType' object has no attribute 'get'")), \
                contextlib.redirect_stdout(out):
            self.assertEqual(board.main(["status"]), 0)
        self.assertEqual(out.getvalue(), "board: could-not-run — 'NoneType' object has no attribute 'get'\n")


class TheWholeBoardTest(unittest.TestCase):
    """
    P168 (#106): the status reads the whole board. GitHub hands a project's items over 100 a page, so the query pages
    with `after` until the last page, and a board whose pages held fewer items than it says it holds is could-not-run —
    the verdict line, never "the limits hold" over part of a board (W1). The numbers are written out here (W2).
    """

    def paged_gh(self, held, says=None):
        """
        A gh whose spark board (number 2) holds `held` cards in Idea and the bin's none, handed over 100 a page with the
        cursor the next page is asked `after`; `says` is the totalCount it claims when that is not `held`. Returns it with
        every (project number, after) it was asked. Pull requests: none.
        """
        asked = []
        cards = [node(n, "P%d — x" % n, "Idea") for n in range(1, held + 1)]

        def gh(*args, timeout=None):
            if "graphql" not in args:
                return []
            number = int(next(a for a in args if a.startswith("number=")).split("=")[1])
            after = next((a.split("=", 1)[1] for a in args if a.startswith("after=")), None)
            asked.append((number, after))
            held_here = cards if number == 2 else []
            start = int(after) if after else 0
            items = {"totalCount": len(held_here) if says is None else says, "nodes": held_here[start:start + 100],
                     "pageInfo": {"hasNextPage": start + 100 < len(held_here), "endCursor": str(start + 100)}}
            return {"data": {"user": {"projectV2": {"id": "P", "items": items, "statusUpdates": {"nodes": []}}}}}
        return gh, asked

    def test_the_query_pages_the_items(self):
        self.assertIn("items(first:100,after:$after){totalCount pageInfo{hasNextPage endCursor}", board.QUERY)
        self.assertIn("$after:String", board.QUERY)

    def test_a_board_of_101_items_is_read_whole_in_two_pages(self):
        gh, asked = self.paged_gh(101)
        with mock.patch.object(board, "_gh", gh):
            boards, _, _, _ = board.gather()
        self.assertEqual(len(dict(boards)["spark"]), 101)
        self.assertEqual([after for number, after in asked if number == 2], [None, "100"])

    def test_a_board_of_501_items_is_read_whole_in_six_pages_and_the_bin_s_in_one(self):
        gh, asked = self.paged_gh(501)
        with mock.patch.object(board, "_gh", gh):
            boards, _, _, _ = board.gather()
        self.assertEqual(len(dict(boards)["spark"]), 501)
        self.assertEqual([after for number, after in asked if number == 2], [None, "100", "200", "300", "400", "500"])
        self.assertEqual([after for number, after in asked if number == 1], [None])

    def test_the_status_counts_the_whole_board_as_open(self):
        gh, _ = self.paged_gh(101)
        out = io.StringIO()
        with mock.patch.object(board, "_gh", gh), mock.patch.object(board, "work_days", return_value=set()), \
                contextlib.redirect_stdout(out):
            self.assertEqual(board.main(["status"]), 0)
        self.assertEqual(out.getvalue().splitlines()[0], "spark — 101 open, the limits hold · trial check 2026-11-02")

    def test_a_board_whose_pages_held_fewer_than_it_holds_is_could_not_run_not_the_limits(self):
        # The last page came and 130 were promised: nothing of what was read is judged, and the status says the two numbers.
        gh, _ = self.paged_gh(1, says=130)
        out = io.StringIO()
        with mock.patch.object(board, "_gh", gh), contextlib.redirect_stdout(out):
            self.assertEqual(board.main(["status"]), 0)
        self.assertEqual(out.getvalue(), "board: could-not-run — the spark board holds 130 items, 1 were read\n")

    def test_a_close_over_a_board_read_in_part_is_could_not_run_and_posts_nothing(self):
        gh, asked = self.paged_gh(1, says=130)
        out = io.StringIO()
        with mock.patch.object(board, "_gh", gh), contextlib.redirect_stdout(out):
            self.assertEqual(board.main(["close", "x"]), 1)
        self.assertEqual(out.getvalue(), "board: could-not-run — the spark board holds 130 items, 1 were read\n")
        self.assertEqual(len(asked), 1)


class TheHelpTest(unittest.TestCase):
    """
    P146 council (C3): each verb's --help says what it prints or posts and how it exits — each claim read off the code:
    status prints the gate's verdict, the flight with its marks, the waits oldest first, Ready, the open PRs and the
    last close, and exits 0 whatever happens; close posts the day's one update, at risk on a problem or
    a wait past three days, and refuses a day already closed with exit 1.
    """

    def help_of(self, *verb):
        """What `board.py <verb> --help` prints, its whitespace folded — argparse wraps to the terminal's width."""
        fake_bin = Path(tempfile.mkdtemp())  # a gh that fails, first on PATH: a help that read a board would show it
        (fake_bin / "gh").write_text("#!/bin/sh\necho 'a help read a board' >&2\nexit 1\n")
        (fake_bin / "gh").chmod(0o755)
        done = subprocess.run([sys.executable, str(ROOT / "tools" / "board.py"), *verb, "--help"], capture_output=True,
                              text=True, timeout=60, env=dict(os.environ, PATH=str(fake_bin) + os.pathsep + os.environ.get("PATH", "")))
        self.assertEqual((done.returncode, done.stderr), (0, ""))
        return " ".join(done.stdout.split())

    def assert_says(self, said, phrases):
        for phrase in phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, said)

    def test_the_status_help_says_what_it_prints_and_that_it_always_exits_zero(self):
        self.assert_says(self.help_of("status"), (
            "print the state of both boards: the gate's verdict, the cards in flight (expedite and bench marked), every "
            "wait oldest first ('!' past three days), Ready", "open PRs, the last close",
            "always exits 0", "could-not-run", "--when-in"))

    def test_the_close_help_says_what_it_posts_when_it_is_at_risk_and_what_it_refuses(self):
        self.assert_says(self.help_of("close"), (
            "post the day's one status update to spark's board", "at risk when the gate finds a problem or a wait is older "
            "than three days", "refuses a day already closed (exit 1)", "--dry-run print the update and post nothing",
            "--date DATE the day to close, YYYY-MM-DD", "(default: today)"))

    def test_the_top_help_names_both_verbs_with_what_they_do(self):
        self.assert_says(self.help_of(), ("both boards", "status print the state of both boards",
                                          "close post the day's one status update to spark's board"))


if __name__ == "__main__":
    unittest.main()
