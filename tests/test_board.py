"""P102c: the state of both boards in a dozen lines, and the day-close (docs/2026-10-05-session-status-design.md)."""

import contextlib
import datetime as dt
import io
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


def node(number, title, status, changed="2026-10-05T10:00:00Z", labels=("story",), waiting=None, since=None, slice_="team tools"):
    values = [{"name": status, "updatedAt": changed, "field": {"name": "Status"}},
              {"name": slice_, "updatedAt": changed, "field": {"name": "Slice"}}, {}]
    if waiting:
        values.append({"name": waiting, "updatedAt": changed, "field": {"name": "Waiting on"}})
    if since:
        values.append({"date": since, "field": {"name": "Waiting since"}})
    return {"content": {"number": number, "title": title, "body": BODY, "repository": {"name": "spark"},
                        "labels": {"nodes": [{"name": label} for label in labels]}},
            "fieldValues": {"nodes": values}}


def project(*nodes):
    return {"id": "P", "items": {"nodes": list(nodes)}, "statusUpdates": {"nodes": []}}


SPARK = board.to_items(project(
    node(26, "P102c — The state in view", "Build", "2026-10-05T10:00:00Z"),
    node(24, "P102 — The tools chore", "Build", labels=("epic",)),
    node(32, "P103 — The process documented", "Ready"),
    node(18, "P97 — Store 1c", "Ready"),
    node(15, "R2.6 — A fourth cold test", "Idea", waiting="the PO"),
    {"content": {}, "fieldValues": {"nodes": []}}))
BIN = board.to_items(project(node(1, "B1 — Identify the audio module", "Idea", waiting="the PO", since="2026-09-25")))


class TheCoreTest(unittest.TestCase):
    def test_items_carry_status_slice_waiting_and_when_status_changed(self):
        first = SPARK[0]
        self.assertEqual((first["status"], first["slice"], first["status_changed"], first["content"]["number"]),
                         ("Build", "team tools", "2026-10-05T10:00:00Z", 26))
        self.assertEqual((BIN[0]["waiting on"], BIN[0]["waiting since"]), ("the PO", "2026-09-25"))

    def test_a_board_item_that_is_not_an_issue_is_skipped(self):
        self.assertEqual(len(SPARK), 5)

    def test_in_flight_names_stage_item_and_age_and_leaves_epics_out(self):
        self.assertEqual(board.in_flight(SPARK, TODAY), ["Build P102c (#26) 2 d"])

    def test_waiting_on_the_po_says_since_when_and_marks_more_than_three_days(self):
        self.assertEqual(board.waiting(BIN, TODAY), ["B1 (#1) since 2026-09-25, 12 d !"])
        self.assertEqual(board.waiting(SPARK, TODAY), ["R2.6 (#15)"])

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
            "  waits on the PO: R2.6 (#15), bin B1 (#1) since 2026-09-25, 12 d !",
            "  Ready: P103 (#32), P97 (#18)",
            "  open PRs: spark #34 P102c: the state in view (draft)",
            "  last close 2026-10-05: P102a merged; P102c designed",
            "  ! the day of 2026-10-06 has no close — write it first"])

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
        crowded = SPARK + board.to_items(project(node(27, "P102d — Proofs", "Build")))
        state, _ = board.close_update("two in Build", [("spark", crowded)], set(), TODAY, TODAY)
        self.assertEqual(state, "AT_RISK")

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
        with mock.patch.object(board, "gather", return_value=([("spark", SPARK)], [], [], set(), "P")), \
                mock.patch.object(board, "_gh") as gh, contextlib.redirect_stdout(out):
            self.assertEqual(board.main(["close", "P102c built", "--dry-run"]), 0)
        self.assertFalse(gh.called)
        self.assertIn("dry run", out.getvalue())


if __name__ == "__main__":
    unittest.main()
