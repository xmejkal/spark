# The state in view, and the day-close (P102c) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (recommended here) or superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every Claude Code session started in the PO's project folders opens with the state of both boards, and each
working day ends with a dated close posted as a status update on the spark board (P102c, issue #26).

**Architecture:** One team tool, `tools/board.py`, with two verbs, `status` and `close`.
- Its pure core turns GitHub's answers into lines and verdicts, and is tested offline.
- Its thin `gh` layer makes one GraphQL query per board, plus REST calls for pull requests and commits.
- It reuses `check_backlog.problems()` for the limit verdict.
- A `SessionStart` hook in the PO's own `~/.claude/settings.json` runs `status`, but only in the folders it names.

**Tech Stack:** Python 3 standard library, `gh` (the PO's login), GitHub GraphQL and REST through `gh api`, `unittest`,
`tools/mutate.py`.

**Spec:** `docs/2026-10-05-session-status-design.md` (approved by the PO, 2026-10-05).

## Global Constraints

- Branch `p102c-session-status`, PR #34 (`Closes #26`). The PO merges.
- **GitHub's GraphQL budget** is 5,000 points an hour, shared by everything that uses the PO's login; it was exhausted
  once on 2026-10-05. So the tool makes exactly one GraphQL query per board for `status`, and uses REST for pull
  requests and commits.
- No token is stored. Nothing is posted without `--dry-run` being shown first, the first time (the proof).
- The hook goes into the PO's user settings only with his yes, and the exact entry is shown first. No personal path
  goes into the repository.
- `status` never fails a session. Offline, or if `gh` errors, it prints `board: skipped — <why>` and exits 0.
- Mutation tables only for verdicts (P72's cut): the missing-close rule, the refusal of a second close, and the at-risk
  choice.
- **Tests stay offline:** every `gh` call sits behind `gather()` and `_gh()`, so tests feed literal data.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`, and their numbers come only from
  output already shown (W13).
- **The card follows the work:**
  - P102c moves to Build when Task 1 starts;
  - to Review when the proof is posted;
  - to Done after the merge.

## Review Focus

1. **A session started outside the PO's folders** must print nothing. Test: Task 1 (`inside`).
2. **The first day ever,** with no close yet, must flag only the last working day, never every day in history. Test:
   Task 1 (`missing_close`).
3. **A status update made by hand on the board,** with no start date, must not break `status`. Test: Task 2
   (`closes_from`).
4. **An item that is a pull request or a draft on the board** must be skipped, not crash. Test: Task 1 (`to_items`).
5. **Closing the same day twice,** for instance on a retry, must be refused, with the date of the first close. Test:
   Task 2.

---

## File structure

| file | responsibility |
| --- | --- |
| `tools/board.py` (new) | `status` and `close`; the pure core and the thin `gh` layer |
| `tests/test_board.py` (new) | the core's tests, offline |
| `tests/mutations/p102c-board.json` (new) | the verdicts' mutation table |
| `~/.claude/settings.json` (the PO's, not the repository) | the `SessionStart` hook |

---

### Task 1: The core — items, ages, what waits, the missing close, the status lines

**Files:** Create `tools/board.py` and `tests/test_board.py`.

**Interfaces:**
- Produces:
  - `to_items(project) -> [item]`: items in the shape `check_backlog` reads, plus `"status_changed"`, `"waiting on"`,
    `"waiting since"` and `"content"]["repo"]`;
  - `age(iso, today) -> int`;
  - `in_flight(items, today) -> [str]`;
  - `waiting(items, today) -> [str]`;
  - `ready(items) -> [str]`;
  - `missing_close(work_days, close_days, today) -> date | None`;
  - `status_lines(boards, prs, closes, work_days, today) -> [str]`;
  - `inside(cwd, dirs) -> bool`.

- [ ] **Step 1: Failing tests** — `tests/test_board.py`:

```python
"""P102c: the state of both boards in a dozen lines, and the day-close (docs/2026-10-05-session-status-design.md)."""

import datetime as dt
import sys
import tempfile
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2.** Run `python3 -m unittest discover -s tests -t tests -p 'test_board.py'`. Expected: an ERROR,
  `No module named 'board'`.
- [ ] **Step 3: Implement** the core of `tools/board.py`:

```python
#!/usr/bin/env python3
"""
The state of the work at every session start, and the day-close (P102c; docs/2026-10-05-session-status-design.md).

    board.py status [--when-in DIR ...]          # both boards in a dozen lines; nothing outside the named folders
    board.py close [--date D] [--dry-run] LINE|- # the day-close, as a status update on the spark board

It reads the boards through the PO's own gh login and stores nothing: one GraphQL query per board (GitHub allows 5,000
GraphQL points an hour, shared with everything else), REST for pull requests and commits.
"""

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_backlog  # noqa: E402

OWNER = "xmejkal"
#: Each board: its name in the status, its project number, the repository it holds (P102a's spec §2).
BOARDS = (("spark", 2, "spark"), ("bin", 1, "sisuo-brain-transplant"))
#: More days than this waiting on the PO is named (the weekly look, P102a's spec §3).
WAIT_TOO_LONG = 3
TRIAL_CHECK = "2026-11-02"


def to_items(project):
    """The board's issues in the shape check_backlog reads, with when each card's Status last changed."""
    items = []
    for node in project["items"]["nodes"]:
        content = node.get("content") or {}
        if "number" not in content or "repository" not in content:
            continue  # a draft or a pull request on the board is no backlog item
        item = {"labels": [label["name"] for label in content["labels"]["nodes"]],
                "content": {"number": content["number"], "title": content["title"], "body": content.get("body") or "",
                            "repo": content["repository"]["name"]}}
        for value in node["fieldValues"]["nodes"]:
            name = ((value or {}).get("field") or {}).get("name", "").lower()
            if name:
                item[name] = value.get("name", value.get("date"))
                if name == "status":
                    item["status_changed"] = value.get("updatedAt")
        items.append(item)
    return items


def age(iso, today):
    """Whole days from an ISO date or timestamp to today."""
    return (today - dt.date.fromisoformat(iso[:10])).days


def _short(item):
    return "%s (#%s)" % (item["content"]["title"].split(" — ")[0], item["content"]["number"])


def in_flight(items, today):
    """The cards in a working stage, with their stage and days there — epics and tasks ride on their stories."""
    return ["%s %s %d d" % (i["status"], _short(i), age(i["status_changed"], today)) for i in items
            if i.get("status") in check_backlog.IN_FLIGHT and not {"epic", "task"} & set(i["labels"])]


def waiting(items, today):
    """The cards waiting on the PO, with since when; more than WAIT_TOO_LONG days is marked."""
    said = []
    for i in items:
        if i.get("waiting on") != "the PO" or i.get("status") == "Done":
            continue
        since = i.get("waiting since")
        if since:
            days = age(since, today)
            said.append("%s since %s, %d d%s" % (_short(i), since, days, " !" if days > WAIT_TOO_LONG else ""))
        else:
            said.append(_short(i))
    return said


def ready(items):
    """The Ready column in the board's own order, which is the PO's (W11)."""
    return [_short(i) for i in items if i.get("status") == "Ready"]


def missing_close(work_days, close_days, today):
    """The last working day before today when no close covers it, or None (only that day: a restart needs one line)."""
    last = max((day for day in work_days if day < today), default=None)
    if last is not None and (not close_days or max(close_days) < last):
        return last
    return None


def inside(cwd, dirs):
    """Whether cwd lies within one of dirs."""
    here = Path(cwd).resolve()
    return any(here == Path(d).expanduser().resolve() or Path(d).expanduser().resolve() in here.parents for d in dirs)


def _boards_join(boards, each, today):
    return [("" if name == "spark" else name + " ") + said for name, items in boards for said in each(items, today)]


def status_lines(boards, prs, closes, work_days, today):
    """
    The status, both boards: boards [(name, items)], prs [(repo, number, title, draft)], closes [(date, first line)],
    work_days {date}.
    """
    spark = dict(boards)["spark"]
    verdict = check_backlog.problems(spark)
    lines = ["spark — %d open, %s · trial check %s" % (sum(1 for i in spark if i.get("status") != "Done"),
                                                        "the limits hold" if not verdict else "%d problem(s)" % len(verdict),
                                                        TRIAL_CHECK)]
    lines += ["  ! " + sentence for sentence in verdict]
    lines.append("  in flight: " + (", ".join(_boards_join(boards, in_flight, today)) or "nothing"))
    lines.append("  waits on the PO: " + (", ".join(_boards_join(boards, waiting, today)) or "nothing"))
    lines.append("  Ready: " + (", ".join(ready(spark)) or "empty — the PO refills it"))
    lines.append("  open PRs: " + (", ".join("%s #%s %s%s" % (repo, number, title[:48], " (draft)" if draft else "")
                                             for repo, number, title, draft in prs) or "none"))
    if closes:
        day, line = max(closes)
        lines.append("  last close %s: %s" % (day.isoformat(), line))
    gap = missing_close(work_days, {day for day, _ in closes}, today)
    if gap:
        lines.append("  ! the day of %s has no close — write it first" % gap.isoformat())
    return lines
```

- [ ] **Step 4.** Run the Step 2 command, then the suite. Expected: PASS; the suite `OK`.
- [ ] **Step 5.** Commit:
  `P102c: board.py's core — items with their ages, what waits on the PO, Ready in order, the missing close, the status lines`
  (trailer). Move P102c to Build when this task starts.

---

### Task 2: The `gh` layer, `status`, and `close`

**Files:** Modify `tools/board.py` and `tests/test_board.py`. Create `tests/mutations/p102c-board.json`.

**Interfaces:**
- Consumes everything Task 1 produced.
- Produces:
  - `closes_from(project) -> [(date, first line)]`;
  - `close_update(line, boards, close_days, day, today) -> (status, body)`, which raises `ValueError` for a day
    already closed;
  - `gather(today) -> (boards, prs, closes, work_days, project_id)`;
  - `main(argv) -> int`.

- [ ] **Step 1: Failing tests**, appended to `TheCoreTest`:

```python
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
```

  Add `import contextlib`, `import io` and `from unittest import mock` at the top of `tests/test_board.py`.
- [ ] **Step 2.** Run the Step 2 command of Task 1. Expected: these six tests ERROR, because `closes_from`,
  `close_update`, `main` and `gather` do not exist yet.
- [ ] **Step 3: Implement**, appended to `tools/board.py`:

```python
QUERY = """query($login:String!,$number:Int!){user(login:$login){projectV2(number:$number){id
 items(first:100){nodes{content{... on Issue{number title body repository{name} labels(first:10){nodes{name}}}}
  fieldValues(first:20){nodes{
   ... on ProjectV2ItemFieldSingleSelectValue{name updatedAt field{... on ProjectV2FieldCommon{name}}}
   ... on ProjectV2ItemFieldDateValue{date field{... on ProjectV2FieldCommon{name}}}}}}}
 statusUpdates(last:20){nodes{startDate status body}}}}}"""
POST = ("mutation($p:ID!,$d:Date!,$s:ProjectV2StatusUpdateStatus!,$b:String!){createProjectV2StatusUpdate("
        "input:{projectId:$p,startDate:$d,status:$s,body:$b}){statusUpdate{id}}}")


def closes_from(project):
    """The board's day-closes: (start date, first line), skipping updates made by hand with no start date."""
    said = []
    for update in project["statusUpdates"]["nodes"]:
        if update.get("startDate"):
            lines = (update.get("body") or "").strip().splitlines()
            said.append((dt.date.fromisoformat(update["startDate"]), lines[0] if lines else ""))
    return said


def close_update(line, boards, close_days, day, today):
    """(status, body) of a day's close: at risk when a limit breaks or the PO has been waited on too long; one a day."""
    if day in close_days:
        raise ValueError("%s is closed already — one close a day" % day.isoformat())
    spark = dict(boards)["spark"]
    waits = _boards_join(boards, waiting, today)
    risky = bool(check_backlog.problems(spark)) or any(w.endswith("!") for w in waits)
    body = "\n\n".join([line.strip(), "in flight: " + (", ".join(_boards_join(boards, in_flight, today)) or "nothing"),
                        "waits on the PO: " + (", ".join(waits) or "nothing")])
    return ("AT_RISK" if risky else "ON_TRACK"), body


def _gh(*args):
    done = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=60)
    if done.returncode:
        raise RuntimeError((done.stderr.strip().splitlines() or ["gh failed"])[0])
    return json.loads(done.stdout) if done.stdout.strip() else None


def gather(today):
    """Both boards, their open PRs, the spark board's closes, and the working days since the last close."""
    boards, closes, project_id = [], [], None
    for name, number, repo in BOARDS:
        project = _gh("api", "graphql", "-f", "query=" + QUERY, "-F", "login=" + OWNER, "-F", "number=%d" % number)
        project = project["data"]["user"]["projectV2"]
        boards.append((name, to_items(project)))
        if name == "spark":
            project_id, closes = project["id"], closes_from(project)
    since = max((day for day, _ in closes), default=today - dt.timedelta(days=14)).isoformat()
    work_days, prs = set(), []
    for name, _, repo in BOARDS:
        for commit in _gh("api", "repos/%s/%s/commits?sha=main&per_page=100&since=%sT00:00:00Z" % (OWNER, repo, since)):
            when = dt.datetime.fromisoformat(commit["commit"]["author"]["date"].replace("Z", "+00:00"))
            work_days.add(when.astimezone().date())
        prs += [(name, pr["number"], pr["title"], pr["draft"]) for pr in _gh("api", "repos/%s/%s/pulls?state=open" % (OWNER, repo))]
    return boards, prs, closes, work_days, project_id


def main(argv=None):
    parser = argparse.ArgumentParser(description="The state of the work, and the day-close (P102c).")
    verbs = parser.add_subparsers(dest="verb", required=True)
    verbs.add_parser("status").add_argument("--when-in", nargs="+", metavar="DIR")
    close = verbs.add_parser("close")
    close.add_argument("line", help="the day's one line, or - to read it from stdin")
    close.add_argument("--date", help="the day to close, YYYY-MM-DD (default: today)")
    close.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if args.verb == "status" and args.when_in and not inside(os.getcwd(), args.when_in):
        return 0
    today = dt.date.today()
    try:
        boards, prs, closes, work_days, project_id = gather(today)
    except (OSError, subprocess.SubprocessError, RuntimeError, ValueError, KeyError, TypeError) as unreachable:
        print("board: skipped — %s" % unreachable)
        return 0 if args.verb == "status" else 1
    if args.verb == "status":
        print("\n".join(status_lines(boards, prs, closes, work_days, today)))
        return 0
    day = dt.date.fromisoformat(args.date) if args.date else today
    try:
        state, body = close_update(sys.stdin.read() if args.line == "-" else args.line, boards,
                                   {d for d, _ in closes}, day, today)
    except ValueError as refused:
        print("close: refused — %s" % refused)
        return 1
    print("close %s (%s):\n%s" % (day.isoformat(), state, body))
    if args.dry_run:
        print("(dry run — nothing posted)")
        return 0
    _gh("api", "graphql", "-f", "query=" + POST, "-f", "p=" + project_id, "-f", "d=" + day.isoformat(),
        "-f", "s=" + state, "-f", "b=" + body)
    print("posted on the spark board")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4.** Run Task 1's Step 2 command, then the suite. Expected: PASS; the suite `OK`.
- [ ] **Step 5: Mutation table** `tests/mutations/p102c-board.json`:

```json
[
 {"file": "tools/board.py", "name": "every past day counts as missing", "find": "    if last is not None and (not close_days or max(close_days) < last):\n", "replace": "    if last is not None:\n"},
 {"file": "tools/board.py", "name": "today counts as a working day to close", "find": "for day in work_days if day < today", "replace": "for day in work_days if day <= today"},
 {"file": "tools/board.py", "name": "a day can be closed twice", "find": "    if day in close_days:\n", "replace": "    if False:\n"},
 {"file": "tools/board.py", "name": "waiting too long is not at risk", "find": "or any(w.endswith(\"!\") for w in waits)", "replace": "or False"},
 {"file": "tools/board.py", "name": "a broken limit is not at risk", "find": "risky = bool(check_backlog.problems(spark)) or", "replace": "risky = False or"},
 {"file": "tools/board.py", "name": "status shows outside the named folders", "find": "and not inside(os.getcwd(), args.when_in):", "replace": "and False:"}
]
```

  Run `python3 tools/mutate.py tests/mutations/p102c-board.json`, in the foreground, with a 600000 ms timeout.
  Expected: every mutation caught. Then run `--anchors`: clean.
- [ ] **Step 6: Live, read-only.** From `~/Development/smartbin-local`, run
  `python3 ~/Development/spark/tools/board.py status --when-in ~/Development/spark ~/Development/smartbin-local`.
  Expected:
  - the status lines, with P102c in Build, B1 waiting since 2026-09-25, and #34 among the open PRs;
  - a "no close" line for the last working day, since no close has been written yet.

  If GitHub's rate limit refuses, the output is `board: skipped — …`, which is also correct: wait for the reset and
  run it again.
- [ ] **Step 7.** Commit:
  `P102c: board.py status and close — one GraphQL query per board, the day-close as a status update, refused twice a day, at risk when the PO waits too long`
  (trailer).

---

### Task 3: The hook, the proof, the first close

- [ ] **Step 1: Show the PO the exact entry,** to be merged into `~/.claude/settings.json` (under `hooks`):

```json
{"SessionStart": [{"hooks": [{"type": "command",
  "command": "python3 ~/Development/spark/tools/board.py status --when-in ~/Development/spark ~/Development/smartbin-local"}]}]}
```

  With his yes, write it with the `update-config` skill (user settings), keeping every key already there.
- [ ] **Step 2: Proof.**
  - Run the hook's command from `~/Development/smartbin-local` and from `/tmp`: the status, then nothing.
  - Run `board.py close - --dry-run` with the day's line on stdin, written to a file with the Write tool and read by
    redirection, never typed on a command line. Show the PO the output.
  - With his yes, run it without `--dry-run` for today.
  - Run `status` again: `last close <today>: <the line>`.
- [ ] **Step 3: The board.** P102c moves to Review. Its issue gets the proof's output as a comment.
- [ ] **Step 4: Review.** One fresh reviewer on the most capable model reads the branch. Important findings get one fix
  pass. Push; the PO merges PR #34 (`Closes #26`); P102c moves to Done.
