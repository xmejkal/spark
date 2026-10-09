"""P102c: the state of both boards in a dozen lines, and the day-close (docs/2026-10-05-session-status-design.md)."""

import contextlib
import datetime as dt
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import board  # noqa: E402

TODAY = dt.date(2026, 10, 7)
BODY = "### Needed by\n\nthe PO\n\n### Value proven by\n\nx\n"


def node(number, title, status, changed="2026-10-05T10:00:00Z", labels=("story",), waiting=None, since=None, slice_="team tools",
         parent=None):
    values = [{"name": status, "updatedAt": changed, "field": {"name": "Status"}},
              {"name": slice_, "updatedAt": changed, "field": {"name": "Slice"}}, {}]
    if waiting:
        values.append({"name": waiting, "updatedAt": changed, "field": {"name": "Waiting on"}})
    if since:
        values.append({"date": since, "field": {"name": "Waiting since"}})
    return {"content": {"number": number, "title": title, "body": BODY, "repository": {"name": "spark"},
                        "labels": {"nodes": [{"name": label} for label in labels]},
                        "parent": {"number": parent} if parent else None},
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

    def test_in_flight_counts_a_parentless_task_as_a_card(self):
        items = board.to_items(project(node(10, "T10 — y", "Build", labels=("task",))))
        self.assertEqual(board.in_flight(items, dt.date(2026, 10, 9)), ["Build T10 (#10) 4 d"])

    def test_waiting_on_the_po_says_since_when_and_marks_more_than_three_days(self):
        self.assertEqual(board.waiting(BIN, TODAY), ["B1 (#1) since 2026-09-25, 12 d !"])
        self.assertEqual(board.waiting(SPARK, TODAY), ["R2.6 (#15) since 2026-10-05, 2 d"])
        undated = board.to_items(project(node(16, "R2.7 — A wait nobody dated", "Idea", waiting="the PO")))
        self.assertEqual(board.waiting(undated, TODAY), ["R2.7 (#16)"])

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
            "  waits on the PO: R2.6 (#15) since 2026-10-05, 2 d, bin B1 (#1) since 2026-09-25, 12 d !",
            "  Ready: P103 (#32), P97 (#18)",
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
        self.assertIn("  ! the bin's board could not be read (no bin board was given) — its cards in flight were not counted", lines)
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
        self.assertEqual(out.getvalue(), "board: skipped — could not resolve host\n")

    def test_status_outside_the_named_folders_prints_nothing(self):
        out = io.StringIO()
        with mock.patch.object(board, "gather") as gather, contextlib.redirect_stdout(out):
            self.assertEqual(board.main(["status", "--when-in", tempfile.mkdtemp()]), 0)
        self.assertEqual((out.getvalue(), gather.called), ("", False))

    def test_close_dry_run_posts_nothing(self):
        out = io.StringIO()
        with mock.patch.object(board, "gather", return_value=([("spark", SPARK)], [], [], "P", [])), \
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
        self.assertIn("parent{number}", board.QUERY)

    def test_a_board_read_short_says_how_many_it_holds(self):
        held = project(node(1, "P1 — x", "Ready"))
        held["items"]["totalCount"] = 130
        self.assertEqual(board.unread("spark", held), "the spark board holds 130 items; status read the first 1")
        self.assertIsNone(board.unread("spark", project(node(1, "P1 — x", "Ready"))))

    def test_the_status_names_what_it_could_not_read(self):
        lines = board.status_lines([("spark", SPARK)], [], [], set(), TODAY, ["the spark board holds 130 items"])
        self.assertIn("  ! the spark board holds 130 items", lines)

    def test_a_silent_network_skips_the_status_in_seconds(self):
        out = io.StringIO()
        stalled = subprocess.TimeoutExpired(["gh"], board.STATUS_TIMEOUT)
        with mock.patch.object(board.subprocess, "run", side_effect=stalled) as run, contextlib.redirect_stdout(out):
            self.assertEqual(board.main(["status"]), 0)
        self.assertEqual(run.call_args.kwargs["timeout"], board.STATUS_TIMEOUT)
        self.assertLessEqual(board.STATUS_TIMEOUT, 10)
        self.assertEqual(out.getvalue(), "board: skipped — gh did not answer in %d s\n" % board.STATUS_TIMEOUT)

    def test_working_days_are_commits_on_any_branch_in_the_named_folders(self):
        root = Path(tempfile.mkdtemp())
        own = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}

        def git(*args, when=None):
            dated = {"GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when} if when else {}
            subprocess.run(["git", "-C", str(root), "-c", "user.email=t@t", "-c", "user.name=t", *args],
                           check=True, capture_output=True, env=dict(own, **dated))
        git("init", "-q")
        git("commit", "-q", "--allow-empty", "-m", "before", when="2026-09-20T12:00:00")
        git("commit", "-q", "--allow-empty", "-m", "on main", when="2026-10-03T12:00:00")
        git("checkout", "-q", "-b", "work")
        git("commit", "-q", "--allow-empty", "-m", "on a branch only", when="2026-10-05T12:00:00")
        git("checkout", "-q", "-")
        # A hook's GIT_DIR must not steer the read to another repository (the P105 leak).
        with mock.patch.dict(os.environ, {"GIT_DIR": tempfile.mkdtemp()}):
            days = board.work_days([str(root), tempfile.mkdtemp()], dt.date(2026, 10, 1))
        self.assertEqual(days, {dt.date(2026, 10, 3), dt.date(2026, 10, 5)})

    def test_status_says_skipped_whatever_breaks(self):
        out = io.StringIO()
        with mock.patch.object(board, "gather", return_value=([("spark", SPARK)], [], [], "P", [])), \
                mock.patch.object(board, "status_lines", side_effect=AttributeError("'NoneType' object has no attribute 'get'")), \
                contextlib.redirect_stdout(out):
            self.assertEqual(board.main(["status"]), 0)
        self.assertEqual(out.getvalue(), "board: skipped — 'NoneType' object has no attribute 'get'\n")


if __name__ == "__main__":
    unittest.main()
