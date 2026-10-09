# P146 — the process fits how we work: Implementation Plan (the rest, after tasks 1 and 1b)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The written process says how the team really works, and the rules a script can check are checked — the gate's remaining rules, the status's remaining lines, the role cards, the cadences, the W1–W21 cut, the Review-stage council rule — with the three guards the PO decided prepared for his one yes each.

**Architecture:** Part A changes the two scripts that already enforce the process (`tools/check_backlog.py`, the pre-push gate's board check, and `tools/board.py`, the session status and the day-close), one rule per task, test-first, each rule a sentence the gate prints. Part B rewrites the process documents from the accepted spec (`docs/2026-10-06-process-design.md`), one file per task, every claim checked against the code or a run. Part C prepares the three guards that live in the PO's own settings and on GitHub, as exact snippets he says yes to one by one; nothing in Part C changes a setting on its own. The bin's stale status pages are a separate, small PR in the bin's repository, with its council first.

**Tech Stack:** Python 3.9 (no new dependencies), `gh` (GraphQL and REST, read-only in the scripts), `unittest`, `tools/mutate.py` mutation tables, `tools/check_docs.py`, `tests/test_orphans.py`.

**Spec:** `docs/2026-10-06-process-design.md` — the proposal the PO accepted on 2026-10-06 (Task 1 commits it with his decisions marked), read together with spark issue #80's comments: the six decisions (2026-10-06 12:21), the limits of two per working stage and four in flight (2026-10-06 20:53), the two roles (2026-10-06 17:16), and the Review-stage rule (2026-10-08 10:53 and 10:54) — GitHub's times, UTC.

**Done before this plan:** task 1 (PR #91: Ready 5, in flight 3, epics counted in Discovery and Design) and task 1b (PR #92: every working stage takes 2, four in flight) — `tools/check_backlog.py` `LIMITS`, `MOST_IN_FLIGHT`, `counts()`, and both Board views' column limits (set by hand on 2026-10-06).

**As executed (2026-10-09, Part A):** The code and the commit messages are the authority; the plan's task texts below are the record of what was asked. Where they differ — **Task 2:** there is no `parents_read`; `fetch()` returns `(items, bin_items, why, bin_why)`; a parent nobody could ask is the sentinel `PARENT_UNREAD`; `parents(tasks)` takes `(repository, number)` pairs, answers keyed by the same pair, in one call (Task 6 widened `fetch()` to the four-tuple); and a closed parent reads as none (`open_parent()`), so its task counts as a card. **Task 4:** a riding task's wait date is asked too — "Done and riding cards were skipped" holds for Done only. **Task 3:** `JUDGED = ("Ready", "Build", "Review")`, the spec's commitment point — Idea, Discovery and Design are not judged for a Needed by or a slice. **Tasks 5 and 6:** the expedite count spans both boards and lends Ready nothing; a bin card labelled `bench` is left out of the flight total; the wait date is asked of every open card on both boards; a riding task labelled `expedite` beside its story is not a second rush (`rushed` leaves riding tasks out); the unread-bin line reads "…not counted or checked". **Task 8:** there is no `waiting()` — its callers were only its tests, and the status reads `all_waiting()`; `appetite_since()` widens the working-days window back to the oldest running appetite; `all_waiting()` merges both boards' waits, oldest first; the appetite clock runs from the epic's last stage change; and Review Focus 3's status half is superseded — the status lists every open wait, and one on someone other than the PO names who. Decision 5's flag was built in Task 8 and removed on 2026-10-09 by the PO's answer to question 5 ([#80](https://github.com/xmejkal/spark/issues/80#issuecomment-6077488115)): `appetite_spent()`, `appetite_since()`, the Appetite read and the widened window left `tools/board.py`, which reads the working days from the newest close again.

**As executed (2026-10-09, Part B and the council's fix round):** the same rule — the commits are the authority. **Task 10:** its review accepted nine departures from the task text (the review is kept outside the repository); its fix round added the close's at-risk rule as the code has it and the service level the PO accepted (5e4cbd3). **Task 11:** the roster has four agent rows, not two — `part-finder` and `datasheet-reader` ship too — beside the two role rows; W10 and W11 moved onto the PO's role card, and Task 12 points at it. **Task 12:** four wrong facts were found and corrected, each from its commit; W7's line count, now in W14, reads "~1,307" (the firmware lens's count, an estimate). **Task 13:** `DECISIONS.md`'s cautions fell under the spec's §4 order ("the stale lines 53–56 and 69 go") but deleted less than it: the deliberately red `make check` (shown false — the bin's is green) and the unverifiable "21 of 50" minutes, whose rule now sits on the PO's card in `TEAM.md`; the rest stays, dated; the spine table is a real `scripts/check_spine.py` run with tscircuit (`tsci 0.0.2621`, exit 0); W20's clause went into the README's Ready row. So question 6 below was withdrawn on #80 (the spec had answered it), and a new one took its place: `Closes` or `Refs #80`. **Task 14:** the proof line on #80 was corrected after the council: its first version claimed output the gate does not print. **Task 15:** the bin's pages are the bin's own PR, #24; B25, B26 and B28 are "open circuit faults, in Idea until the PO orders them", not "questions for the PO". **Part C**, by the PO's answers of 2026-10-09 ([#80](https://github.com/xmejkal/spark/issues/80#issuecomment-6081214370)): item 1, the launch hook, is not set (question 2, "Not yet"); item 2 is set on both repositories as the ruleset "main by PR only", and GitHub now deletes a merged pull request's branch on both (question 3); item 3 is set in his settings, as `Bash(wokwi-cli *)`, `Bash(make simulate *)` and `Bash(make simulate-all *)` (question 4); item 4, the Appetite field, was created earlier the same day on his answer to question 5, and nothing reads it. **The council** (the PO assistant, the user's journey, the tech lead, a documentation expert, then the refuter) found, and its fix round fixed before the merge: C1–C5 in the code (`check_backlog.py --help` explains the gate instead of running it; a could-not-run says `gh`'s own reason; `board.py`'s verbs carry help strings and say could-not-run, not skipped; "the card's closing comment" in `check_commit.py`) and D1–D16 in the documents (the PO's 2026-10-08 words quoted, not paraphrased; the spec's dated notes; GLOSSARY's process words; the developing guide's rules and outputs; this paragraph).

## Global Constraints

- **W2:** a test runs the thing; every quoted sentence in a test is a literal, never computed from the code's constants.
- **W3:** every new branch in `tools/` gets a row in a mutation table (`tests/mutations/p146-process.json`, created in Task 2; the row shape is `{"file", "name", "find", "replace"}` as in `tests/mutations/p146-wip-limits.json`), run in the foreground and read ("every mutation was caught"); before each commit `python3 tools/mutate.py --anchors tests/mutations/*.json` says every anchor present, once.
- **W13:** no count, size or verdict in a message, a page or a commit before its output was read.
- **W16:** a replacement deletes what it replaces, in the same commit; a moved or merged agreement leaves a dated one-line pointer under its old heading (the spec §3: "The numbers stay as they are, because 44 files cite them").
- **W1:** a check that could not look says so and never reads as passed — the offline gate prints could-not-run and lets the push through, which the spec names as the written exception.
- **The commit gate** before every push: `python3 tools/check_commit.py` (the suite, the anchors, the size line, the board) — run it with `TMPDIR=<the session's scratchpad>/commit-tmp` inline; the pre-push hook runs it again.
- **Documents:** `tools/check_docs.py` reads README, AGENTS and `docs/guide/` (anchors, names, the four forbidden strings of its `PERSONAL`: a home-directory path on macOS or on Linux, the macOS temporary-files root, and the bin's local folder name); `python3 -m unittest tests.test_orphans` reads `scrum/`; every page edited here passes both. No local path or session id in any committed file. The spec keeps dated amendments beside the original sentence, as it already does.
- **One PR closes #80** (Part A + Part B), after a council (the PO assistant, the user's journey, the tech lead, a documentation expert, then a refuter) and its fixes — the PO's rule of 2026-10-08. **The merge is the PO's**: Claude's `gh pr merge` is refused by the classifier (observed 2026-10-07 and 2026-10-08); the PR ends with a "ready to merge" comment.
- **The spec's numbers that the PO changed later** (2 per working stage, Ready 5, 4 in flight) replace the proposal's 1/5/3 wherever a page states them; the (D) marks and his words are quoted, never paraphrased.
- **Part B starts after PR #98 (P97) merges**, and begins with `git rebase origin/main` of `p146-process`: #98 touches `GLOSSARY.md`, `scrum/STORY_MAP.md`, `scrum/WORKING_AGREEMENTS.md` (W15's amendment), `docs/guide/*.md` and `README.md`, and Part B edits four of those files. Part A conflicts with nothing in #98.
- **Commit trailer:** the line the implementer's own harness attribution reminder gives; PR bodies end with `🤖 Generated with [Claude Code](https://claude.com/claude-code)`.
- **Never** `--no-verify`, never `sudo`, never a push by a subagent; the controller pushes.

## Review Focus

Five inputs the spec implies and no task's tests exercised before this plan named them; each now has its test in the owning task:

1. A board whose tasks' parents cannot be read (the GraphQL call fails while `item-list` succeeded): a task is counted as riding, and the gate SAYS the parents were not read — never a silent pass (Task 2).
2. A card labelled both `expedite` and `epic`, standing in Build: it is the work only in Discovery and Design, so in Build it does not count — and the expedite allowance applies to nothing there (Task 5).
3. *Waiting on* set to a value other than "the PO" (a typo, or "Petr"): the status lists only "the PO"; the gate's `Waiting since` rule applies to any non-empty *Waiting on* (Task 4).
4. The bin's board unreachable while spark's is reachable: the flight total counts spark's cards, says the bin's were not read, and passes (Task 6).
5. Ready holding exactly two cards against zero: two prints "Ready is down to 2", zero keeps "empty — the PO refills it", and neither line appears at three (Task 8).

---

## Part A — the gate and the status (`tools/`)

### Task 1: The spec travels with the plan

**Files:**
- Create: `docs/2026-10-06-process-design.md` (copied from the accepted proposal; already in the working tree, untracked)
- Modify: that file's header and three passages (below)

**Interfaces:**
- Produces: the spec every later task cites; its §1 stage table, §3 cut table and §4 document list are the authority for Part B.

- [ ] **Step 1: Replace the proposal's italic header with the spec's status**

In `docs/2026-10-06-process-design.md`, replace the first italic paragraph (lines 3–6, "*For the PO, 2026-10-06. Card P146 … Read-only: this file is the only thing written.*") with:

```markdown
*The process design of P146 (spark #80). Written as a proposal for the PO on 2026-10-06 from the four research reads
(R1 to R4), the three practice lenses and the board proposal of that day (kept outside the repository); **accepted by the
PO on 2026-10-06, 12:21**, every line as written, with the six decisions of §5 answered **(a) all three guards, (a),
(a), (a), (a), (a)** — his words are quoted on #80. **(D)** marks what he had decided on 2026-10-06 morning. Later
decisions are marked where they stand, with their date: the limits of two per working stage, Ready 5 and four in flight
(2026-10-06 evening); the two roles, a tech lead and a PO assistant (2026-10-06, 17:16); the Review-stage rule — a
council with a documentation expert before any PR, its fixes before the merge (2026-10-08); and that the merge is the
PO's, not Claude's (observed 2026-10-07 and 2026-10-08: the classifier refuses `gh pr merge` by Claude).*
```

- [ ] **Step 2: Mark the three places the later decisions changed**

In the §1 stage table, the `Discovery`, `Design`, `Build` and `Review` rows' limit cells read `1, epics count (D)` / `1 (D)`; append to each: ` — **2 since 2026-10-06 evening** (the PO: "2 everywhere, cap 4")`. The line `- At most 3 cards are in flight, Discovery to Review (D).` becomes `- At most 3 cards are in flight, Discovery to Review (D) — **4 since 2026-10-06 evening**.` In the `Review` row's "leaves when" cell, after `then Claude merges`, append ` — **amended 2026-10-08: then the PO merges; Claude posts "ready to merge" and stops** (the classifier refuses Claude's merge, 2026-10-07 and 2026-10-08)`. In the "Who does what" table, in Claude's **decides** cell, after `merging after a clean final review unless he reserves the card (his standing word)`, append ` (**amended 2026-10-08:** saying "ready to merge"; the merge itself is the PO's)`.

- [ ] **Step 3: Add the Review-stage rule as a dated paragraph at the end of §1's "Runs: reads, councils, reviews"**

```markdown
- **Added 2026-10-08 (the PO, on P97's PR):** before ANY pull request, bigger or smaller, a council runs on the open
  PR — the PO assistant, the user's journey and the tech lead, **plus a documentation expert**, then the refuter. The
  documentation lens checks that the pages are technically correct and readable, that the front page has a teaser with
  usage, code and agent-calling examples and a link to the detailed page, that every current page is still up to date,
  and that the help for agents and for humans (`--help`, `--describe`, the command pages, the guides) is right and
  complete — gaps, missing parts, changed things, wrong information, unclear text, **hallucinations above all**. Its
  findings are fixed before the merge, not only reported. First run: P158's council on PR #98, 2026-10-08.
```

- [ ] **Step 4: Check the docs tests still pass with the new file**

Run: `python3 -m unittest tests.test_orphans tests.test_docs 2>&1 | tail -3`
Expected: `OK` (the spec is in `docs/`, which the orphan test does not require to be linked; Task 10 links it from `scrum/README.md`).

- [ ] **Step 5: Commit**

```bash
git add docs/2026-10-06-process-design.md
git commit -m "P146: the accepted process design is the spec, with the PO's decisions marked where they stand"
```

### Task 2: A task with no parent story counts as a card

**Files:**
- Modify: `tools/check_backlog.py` (`counts()`, `problems()`, `fetch()`, a new `parents()`)
- Modify: `tools/board.py` (`QUERY`, `to_items()`)
- Test: `tests/test_check_backlog.py`, `tests/test_board.py`
- Create: `tests/mutations/p146-process.json`

**Interfaces:**
- Consumes: `check_backlog.counts(entry)`, `check_backlog.problems(items)`, `board.to_items(project)`.
- Produces: every item carries `"parent": <int> | None` when it is a task; `counts()` returns True for a task whose `parent` is None; `check_backlog.parents(numbers) -> ({number: parent_number_or_None}, why_or_None)`; `problems(items, bin_items=(), parents_read=True)` (the two new parameters are added here and used by Tasks 6 and this task).

- [ ] **Step 1: Write the failing tests**

In `tests/test_check_backlog.py`, extend `item()` with `parent=None` (`{"status": …, "slice": …, "labels": …, "parent": parent, "content": …}`), and add to `TheBacklogCheckTest`:

```python
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

    def test_parents_unread_counts_tasks_as_riding_and_says_so(self):
        said = check_backlog.problems([item(1, "Build"), item(2, "Build"), item(9, "Build", labels=("task",))], parents_read=False)
        self.assertEqual(said, ["tasks' parent stories could not be read — every task counted as riding on a story"])

    def test_parents_asks_github_once_for_all_tasks(self):
        asked = []
        def run(args, **kwargs):
            asked.append(args)
            return mock.Mock(stdout=json.dumps({"data": {"repository": {"t9": {"parent": {"number": 1}}, "t10": {"parent": None}}}}))
        with mock.patch.object(check_backlog.subprocess, "run", run):
            found, why = check_backlog.parents([9, 10])
        self.assertEqual((found, why), ({9: 1, 10: None}, None))
        self.assertEqual(len(asked), 1)
        self.assertIn("t9: issue(number: 9) { parent { number } }", " ".join(asked[0]))

    def test_parents_offline_says_why(self):
        def run(args, **kwargs):
            raise FileNotFoundError("gh")
        with mock.patch.object(check_backlog.subprocess, "run", run):
            self.assertEqual(check_backlog.parents([9]), ({}, "FileNotFoundError"))
```

In `tests/test_board.py`, add to `node()` a `parent=None` parameter that puts `"parent": {"number": parent} if parent else None` into the content, and:

```python
    def test_items_carry_a_task_s_parent_story(self):
        items = board.to_items(project(node(9, "T9 — x", "Build", labels=("task",), parent=1), node(10, "T10 — y", "Build", labels=("task",))))
        self.assertEqual([i.get("parent") for i in items], [1, None])

    def test_in_flight_counts_a_parentless_task_as_a_card(self):
        items = board.to_items(project(node(10, "T10 — y", "Build", labels=("task",))))
        self.assertEqual(board.in_flight(items, dt.date(2026, 10, 9)), ["Build T10 (#10) 4 d"])
```

- [ ] **Step 2: Run them to see them fail**

Run: `python3 -m unittest tests.test_check_backlog tests.test_board 2>&1 | tail -3`
Expected: `FAILED` — `counts()` returns False for every task; `problems()` takes no `parents_read`; `check_backlog.parents` does not exist; `to_items` sets no `parent`.

- [ ] **Step 3: Implement**

In `tools/check_backlog.py`:

```python
def counts(entry):
    """
    Whether an open card counts against the limits: a task rides on its story, so it does not count — unless it has no
    parent story at all, when it is a card of its own (P146); an epic counts only in Discovery and Design, where it is
    the work itself — from Build on, its stories carry the limit. board.py reads the same rule.
    """
    labels = entry.get("labels") or []
    if "task" in labels:
        return entry.get("parent") is None
    return "epic" not in labels or entry.get("status") in UPSTREAM


PARENTS_QUERY = "query { repository(owner: \"%s\", name: \"%s\") { %s } }"


def parents(numbers):
    """({task number: its parent issue's number or None}, None), or ({}, why) when GitHub could not be asked — one call."""
    if not numbers:
        return {}, None
    fields = " ".join("t%d: issue(number: %d) { parent { number } }" % (n, n) for n in numbers)
    try:
        answer = _gh("api", "graphql", "-f", "query=" + PARENTS_QUERY % (OWNER, TITLE, fields))
        found = answer["data"]["repository"]
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, TypeError) as unreachable:
        return {}, type(unreachable).__name__
    return {n: ((found.get("t%d" % n) or {}).get("parent") or {}).get("number") for n in numbers}, None
```

In `problems()`, the signature becomes `def problems(items, bin_items=(), parents_read=True):` (Task 6 fills in `bin_items`; for now it is accepted and ignored). Replace the `status == "Done" or "task" in …: continue` line with:

```python
        rides = "task" in (entry.get("labels") or []) and entry.get("parent") is not None
        if status == "Done" or rides:
            continue  # a riding task is its story's; a parentless one is judged like any card
```

Everything else in the loop stays as it is (an epic in Build is still judged on its Needed by and slice, as today). At the end, before `return said`, add:

```python
    if not parents_read and any("task" in (e.get("labels") or []) for e in items if e.get("status") != "Done"):
        said.insert(0, "tasks' parent stories could not be read — every task counted as riding on a story")
```

In `fetch()`, after the items are listed, look up the parents and attach them:

```python
    tasks = [e["content"]["number"] for e in items if "task" in (e.get("labels") or []) and e.get("status") != "Done"]
    found, why = parents(tasks)
    for entry in items:
        entry["parent"] = found.get(entry["content"]["number"])
    return items, None if why is None else "parents:" + why
```

and `main()` reads the second value: when it starts with `"parents:"`, call `problems(items, parents_read=False)`; a plain `None` means read. (Keep `fetch()`'s existing `(None, why)` returns for the unreachable cases.)

In `tools/board.py`, `QUERY`'s Issue fragment gains `parent{number}` after `labels(first:10){nodes{name}}`, and `to_items()` sets `"parent": (content.get("parent") or {}).get("number")` on each item.

- [ ] **Step 4: Run the tests**

Run: `python3 -m unittest tests.test_check_backlog tests.test_board 2>&1 | tail -3`
Expected: `OK`. Then the whole suite: `TMPDIR=<scratchpad>/docs-tmp python3 -m unittest discover -s tests -t tests 2>&1 | tail -3` → `OK`.

- [ ] **Step 5: Mutation rows**

Create `tests/mutations/p146-process.json` with:

```json
[
  {"file": "tools/check_backlog.py", "name": "P146: a parentless task rides again", "find": "        return entry.get(\"parent\") is None\n", "replace": "        return False\n"},
  {"file": "tools/check_backlog.py", "name": "P146: unread parents pass in silence", "find": "        said.insert(0, \"tasks' parent stories could not be read — every task counted as riding on a story\")\n", "replace": "        pass\n"},
  {"file": "tools/check_backlog.py", "name": "P146: parents are asked one by one", "find": "    fields = \" \".join(\"t%d: issue(number: %d) { parent { number } }\" % (n, n) for n in numbers)\n", "replace": "    fields = \"t%d: issue(number: %d) { parent { number } }\" % (numbers[0], numbers[0])\n"},
  {"file": "tools/board.py", "name": "P146: the status forgets a task's parent", "find": "\"parent\": (content.get(\"parent\") or {}).get(\"number\")", "replace": "\"parent\": None"}
]
```

Run: `TMPDIR=<scratchpad>/docs-tmp python3 tools/mutate.py tests/mutations/p146-process.json 2>&1 | tail -3`
Expected: `every mutation was caught, and the suite is green with the files restored`. Then `python3 tools/mutate.py --anchors tests/mutations/*.json` → every anchor present, once (the P102a row "an epic counts" in `tests/mutations/p102a-check-backlog.json` is DELETED in this task if it anchors the old `counts()` line — W16: not re-anchored — check with the anchors run and say so in the commit).

- [ ] **Step 6: Commit**

```bash
git add tools/check_backlog.py tools/board.py tests/test_check_backlog.py tests/test_board.py tests/mutations/p146-process.json tests/mutations/p102a-check-backlog.json
git commit -m "P146: a task with no parent story counts as a card, and the gate says when parents could not be read"
```

### Task 3: *Needed by* and a slice are required from Ready on, not in Idea

**Files:**
- Modify: `tools/check_backlog.py` (`problems()`)
- Test: `tests/test_check_backlog.py`; rows in `tests/mutations/p146-process.json`

**Interfaces:**
- Consumes: `problems(items, …)` from Task 2.
- Produces: the constant `JUDGED = ("Ready", "Build", "Review")` — the stages from the commitment on, where a card must carry *Needed by* and a slice (**ruled at review, 2026-10-09:** the spec's skeptic item 6 says "from Ready on, not from Discovery on", and Idea, Discovery and Design decide whether to build; the brief's first text, `("Ready",) + IN_FLIGHT`, is superseded).

- [ ] **Step 1: Write the failing tests**

```python
    def test_an_idea_card_needs_no_slice_and_no_needed_by_yet(self):
        self.assertEqual(check_backlog.problems([item(3, "Idea", slice_="", needed="")]), [])

    def test_a_ready_card_with_no_slice_is_named(self):
        self.assertEqual(check_backlog.problems([item(3, "Ready", slice_="")]), ["#3 P3 — x: on no slice of the story map"])

    def test_a_card_in_build_or_review_is_judged(self):
        for stage in ("Build", "Review"):
            with self.subTest(stage=stage):
                self.assertEqual(check_backlog.problems([item(3, stage, needed="")]),
                                 ["#3 P3 — x: no `Needed by` — W14: an item names the design that needs it"])
```

The existing `test_an_item_with_no_needed_by_is_named` and `test_an_item_on_no_slice_is_named` use `item(…)` whose default status is `Ready` — they still hold.

- [ ] **Step 2: Run them to see the first one fail**

Run: `python3 -m unittest tests.test_check_backlog -k idea_card 2>&1 | tail -3`
Expected: `FAILED` — the Idea card is named twice.

- [ ] **Step 3: Implement**

Add `JUDGED = ("Ready", "Build", "Review")  #: from the commitment on a card carries its Needed by and slice; in Idea, Discovery and Design it decides whether to build (P146, the spec's skeptic item 6)` under `IN_FLIGHT`, and in `problems()` wrap the two sentences: `if status in JUDGED:` — not `counts(entry) and …`, which would stop judging an epic in Ready, Build or Review (the stage count `by_stage` still takes every counting entry). A card with no Status or an unknown stage is not judged, like Idea; a test pins it.

- [ ] **Step 4: Run the tests, then the suite**

Expected: `OK`.

- [ ] **Step 5: Mutation rows** (append to `tests/mutations/p146-process.json`)

```json
  {"file": "tools/check_backlog.py", "name": "P146: an Idea card must have a slice again", "find": "JUDGED = (\"Ready\", \"Build\", \"Review\")", "replace": "JUDGED = (\"Idea\", \"Ready\", \"Build\", \"Review\")"},
  {"file": "tools/check_backlog.py", "name": "P146: Ready is not judged", "find": "JUDGED = (\"Ready\", \"Build\", \"Review\")", "replace": "JUDGED = (\"Build\", \"Review\")"},
  {"file": "tools/check_backlog.py", "name": "P146: Discovery is judged again", "find": "JUDGED = (\"Ready\", \"Build\", \"Review\")", "replace": "JUDGED = (\"Discovery\", \"Ready\", \"Build\", \"Review\")"}
```

Run the table; expected: every mutation caught.

- [ ] **Step 6: Commit**

```bash
git add tools/check_backlog.py tests/test_check_backlog.py tests/mutations/p146-process.json
git commit -m "P146: Needed by and a slice are asked of a card from Ready on — in Idea it is the PO's words, nothing more"
```

### Task 4: A *Waiting on* with no *Waiting since* fails the gate

**Files:**
- Modify: `tools/check_backlog.py` (`problems()`)
- Test: `tests/test_check_backlog.py`; rows

**Interfaces:**
- Consumes: the item-list JSON's keys for the two fields. **Confirm them first** with one read-only call: `gh project item-list 2 --owner xmejkal --format json --limit 500 | python3 -c "import json,sys; ks=set(); [ks.update(k for k in i if 'wait' in k.lower()) for i in json.load(sys.stdin)['items']]; print(sorted(ks))"` — expected `['waiting on', 'waiting since']` (gh lower-cases a field's name and keeps its spaces, as `slice` and `status` show). If it prints something else, use what it prints, and record the ruling in the ledger.
- Produces: the sentence `"%s: waits on %s since nobody knows — set Waiting since"`.

- [ ] **Step 1: Write the failing tests**

Extend `item()` with `waiting=None, since=None`, adding `"waiting on": waiting, "waiting since": since` to the dict (the keys as confirmed above), and:

```python
    def test_a_wait_with_no_since_is_named(self):
        self.assertEqual(check_backlog.problems([item(3, "Discovery", waiting="the PO")]),
                         ["#3 P3 — x: waits on the PO since nobody knows — set Waiting since"])

    def test_a_dated_wait_passes_and_any_waited_on_name_is_checked(self):
        self.assertEqual(check_backlog.problems([item(3, "Discovery", waiting="the PO", since="2026-10-06")]), [])
        self.assertEqual(check_backlog.problems([item(3, "Discovery", waiting="Petr")]),
                         ["#3 P3 — x: waits on Petr since nobody knows — set Waiting since"])

    def test_a_done_card_s_stale_wait_is_not_judged(self):
        self.assertEqual(check_backlog.problems([item(3, "Done", waiting="the PO")]), [])
```

- [ ] **Step 2: Run them to see them fail**

Expected: `FAILED` — nothing is said.

- [ ] **Step 3: Implement** — in `problems()`'s loop, at the loop's own indent, AFTER the whole `if status in JUDGED:` block (so an Idea card's wait is named too; Done and riding cards were skipped at the loop's top):

```python
        if entry.get("waiting on") and not entry.get("waiting since"):
            said.append("%s: waits on %s since nobody knows — set Waiting since" % (_name(entry), entry["waiting on"]))
```

- [ ] **Step 4: Run the tests and the suite** — expected `OK`.

- [ ] **Step 5: Mutation rows** — the two below, plus RESTORE verbatim the row "P146: a Done item is judged again" that Task 3 deleted as then-equivalent (`git show bbd8410:tests/mutations/p146-process.json` holds it); with the waiting check at the loop's indent, a Done card's stale wait would be named under that mutant, so `test_a_done_card_s_stale_wait_is_not_judged` catches it.

```json
  {"file": "tools/check_backlog.py", "name": "P146: an undated wait passes", "find": "        if entry.get(\"waiting on\") and not entry.get(\"waiting since\"):\n", "replace": "        if False:\n"},
  {"file": "tools/check_backlog.py", "name": "P146: a dated wait is named too", "find": "        if entry.get(\"waiting on\") and not entry.get(\"waiting since\"):\n", "replace": "        if entry.get(\"waiting on\"):\n"}
```

- [ ] **Step 6: Commit**

```bash
git add tools/check_backlog.py tests/test_check_backlog.py tests/mutations/p146-process.json
git commit -m "P146: a card that waits on someone says since when, or the gate names it"
```

### Task 5: At most one `expedite`, and it may take a stage one over its limit

**Files:**
- Modify: `tools/check_backlog.py` (`problems()`)
- Test: `tests/test_check_backlog.py`; rows

**Interfaces:**
- Produces: the label name `EXPEDITE = "expedite"`; the sentences `"%d cards labelled expedite (%s) — one at a time, on the PO's word"` and the existing limit sentences unchanged; an allowance of one over a stage's limit and over `MOST_IN_FLIGHT` when exactly one counting card among those held carries the label.

- [ ] **Step 1: Write the failing tests**

```python
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
```

- [ ] **Step 2: Run them to see them fail** — expected `FAILED` (the first says "Build holds 3").

- [ ] **Step 3: Implement**

Add `EXPEDITE = "expedite"  #: the one lane past a limit, on the PO's word only — one card at a time; it may take a stage one over, and the gate fails on two (decision 4)`. In `problems()`, before the stage loop:

```python
    rushed = [e for e in items if e.get("status") != "Done" and EXPEDITE in (e.get("labels") or [])]
    if len(rushed) > 1:
        said.append("%d cards labelled expedite (%s) — one at a time, on the PO's word"
                    % (len(rushed), ", ".join("#%s" % e["content"].get("number") for e in rushed)))

    def over(held, limit):
        allowance = 1 if sum(1 for e in held if EXPEDITE in (e.get("labels") or [])) == 1 else 0
        return len(held) > limit + allowance
```

and use `over(held, limit)` in place of `len(held) > limit`, and `over(flying, MOST_IN_FLIGHT)` in place of `len(flying) > MOST_IN_FLIGHT`. (`held` and `flying` hold only counting cards, so an expedite epic in Build is not among them.)

- [ ] **Step 4: Run the tests and the suite** — expected `OK`.

- [ ] **Step 5: Mutation rows**

```json
  {"file": "tools/check_backlog.py", "name": "P146: two expedites pass", "find": "    if len(rushed) > 1:\n", "replace": "    if len(rushed) > 2:\n"},
  {"file": "tools/check_backlog.py", "name": "P146: an expedite allows two over", "find": "        allowance = 1 if sum(1 for e in held if EXPEDITE in (e.get(\"labels\") or [])) == 1 else 0\n", "replace": "        allowance = 2 if sum(1 for e in held if EXPEDITE in (e.get(\"labels\") or [])) == 1 else 0\n"},
  {"file": "tools/check_backlog.py", "name": "P146: any number of expedites allow one over", "find": "        allowance = 1 if sum(1 for e in held if EXPEDITE in (e.get(\"labels\") or [])) == 1 else 0\n", "replace": "        allowance = 1 if sum(1 for e in held if EXPEDITE in (e.get(\"labels\") or [])) >= 1 else 0\n"}
```

- [ ] **Step 6: Commit**

```bash
git add tools/check_backlog.py tests/test_check_backlog.py tests/mutations/p146-process.json
git commit -m "P146: one expedite at a time, on the PO's word — it may take a stage one over its limit, and the gate fails on two"
```

### Task 6: The bin's cards in flight count in the same total

**Files:**
- Modify: `tools/check_backlog.py` (`fetch()`, `problems()`, `main()`), `tools/board.py` (`status_lines()`)
- Test: `tests/test_check_backlog.py`, `tests/test_board.py`; rows

**Interfaces:**
- Consumes, AS TASK 2 SHIPPED THEM (the brief's earlier text is superseded): `problems(items, bin_items=())` — no `parents_read`; `fetch()` returns `(items, why)` where `why`, when `items` came, is the parents' cause (the lookup failed and every open task's `parent` is the sentinel `PARENT_UNREAD`, the string `"unread"` — never read `parent` as a number); `parents(pairs)` takes `(repository, number)` pairs from each task's own `content["repository"]`, grouped per repository in ONE call; `main()` prints the parents note itself. `BOARDS` in `board.py` names the bin's project (number 1).
- Produces: `check_backlog.BIN_TITLE = "the bin"`; `fetch()` returns `(items, bin_items, why, bin_why)` — `bin_items` is `None` and `bin_why` the cause when the bin's board could not be read; **the bin's open tasks go into the SAME `parents()` call as spark's** (their `content["repository"]` is `xmejkal/sisuo-brain-transplant`), so a bin task under its story rides and does not inflate the flight total; **the expedite allowance applies to the working stages and the flight cap only, not to Ready** (ruled at Task 5's review: the spec's expedite enters Build; one condition in the stage loop — `over(held, limit)` becomes `over(held, limit) if stage in IN_FLIGHT else len(held) > limit`; a test: Ready holding 6 with an expedite among them is still named); **the expedite count (`rushed`, Task 5) spans both boards** — "one at a time, on the PO's word" holds across spark and the bin, and a bin card labelled `expedite` lends the flight its one extra place like a spark card does (a test: one expedite on each board → the "2 cards labelled expedite" sentence names `#N` and `bin #M`); the flight sentence names the bin's cards as `bin #N`; `main()` prints `"  backlog: the bin's board could not be read (%s) — its cards in flight were not counted" % bin_why`.

- [ ] **Step 1: Write the failing tests**

```python
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

    def test_main_says_when_the_bin_s_board_was_not_read(self):
        calls = {"n": 0}
        def run(args, **kwargs):
            calls["n"] += 1
            if "item-list" in args and "1" in args:
                raise subprocess.TimeoutExpired("gh", 60)
            if "item-list" in args:
                return mock.Mock(stdout=json.dumps({"items": [item(1, "Build")]}))
            if "graphql" in args:
                return mock.Mock(stdout=json.dumps({"data": {"repository": {}}}))
            return mock.Mock(stdout=json.dumps({"projects": [{"number": 2, "title": "spark"}, {"number": 1, "title": "the bin"}]}))
        code, printed = self.said(run)
        self.assertEqual(code, 0)
        self.assertIn("  backlog: the bin's board could not be read (TimeoutExpired) — its cards in flight were not counted", printed)
```

For `fetch()`, add a run that answers the project list `[{"number": 2, "title": "spark"}, {"number": 1, "title": "the bin"}]`, both item lists (spark's with a `task` under #1, the bin's with a `task` under bin #19) and ONE graphql answer that carries both repositories' aliases, and asserts `fetch()` returns both lists with the bin task's `parent` set and exactly one graphql call made; and one where the bin's `item-list` call raises `subprocess.TimeoutExpired("gh", 60)` → `bin_items is None`, `bin_why == "TimeoutExpired"`, spark's items still returned.

- [ ] **Step 2: Run them to see them fail** — expected `FAILED` (`TypeError` on `bin_items`, the two-list `fetch`).

- [ ] **Step 3: Implement**

In `check_backlog.py`: `BIN_TITLE = "the bin"  #: the bin's project; its working cards fly in the same total (the spec §1: "The bin's desk cards count in the same three")`. `fetch()` finds both project numbers from the one `project list` call and returns `(items, bin_items, why)`; a failure listing the bin's items yields `bin_items = None` (spark's items still returned). In `problems()`, `flying` becomes spark's counting in-flight cards plus `[e for e in (bin_items or []) if e.get("status") in IN_FLIGHT and counts(e)]`, named `"bin #%s"` in the sentence for the bin's entries (give each bin entry `entry["board"] = "bin"` in `fetch()`, and name by `("bin #%s" if e.get("board") == "bin" else "#%s") % number`). When `bin_items is None`, `problems()` counts spark's cards alone and says nothing — the saying is `main()`'s (as it already is for the parents note): `fetch()` returns the bin's failure as `bin_why`, and `main()` prints `"  backlog: the bin's board could not be read (%s) — its cards in flight were not counted" % bin_why` as an extra line, with the exit code unchanged (W1: said, never read as checked). `status_lines()` passes the same sentence in `notes` when the bin board was not read.

In `board.py`'s `status_lines()`: `verdict = check_backlog.problems(spark, bin_items=dict(boards).get("bin"))`.

- [ ] **Step 4: Run the tests and the suite** — expected `OK`.

- [ ] **Step 5: Mutation rows**

```json
  {"file": "tools/check_backlog.py", "name": "P146: the bin's cards do not fly", "find": "[e for e in (bin_items or []) if e.get(\"status\") in IN_FLIGHT and counts(e)]", "replace": "[]"},
  {"file": "tools/check_backlog.py", "name": "P146: an unread bin board passes in silence", "find": "could not be read (%s) — its cards in flight were not counted", "replace": "read; its cards counted"},
  {"file": "tools/board.py", "name": "P146: the status counts spark alone", "find": "verdict = check_backlog.problems(spark, bin_items=dict(boards).get(\"bin\"))", "replace": "verdict = check_backlog.problems(spark)"}
]
```

- [ ] **Step 6: Commit**

```bash
git add tools/check_backlog.py tools/board.py tests/test_check_backlog.py tests/test_board.py tests/mutations/p146-process.json
git commit -m "P146: the bin's cards in flight count in the same total, and an unread bin board is said, not assumed empty"
```

### Task 7: Offline, the gate prints could-not-run

**Files:**
- Modify: `tools/check_backlog.py` (`main()`)
- Test: `tests/test_check_backlog.py` (`test_offline_the_gate_says_why_and_passes`); a row

- [ ] **Step 1: Change the test to the spec's word**

```python
    def test_offline_the_gate_says_could_not_run_and_passes(self):
        def run(*args, **kwargs):
            raise FileNotFoundError("gh")
        code, printed = self.said(run)
        self.assertEqual(code, 0)
        self.assertIn("backlog: could-not-run — gh or the network could not be reached (FileNotFoundError); the limits were not checked", printed)
        self.assertNotIn("skipped", printed)
```

- [ ] **Step 2: Run it to see it fail** — expected `FAILED` ("skipped" is printed).

- [ ] **Step 3: Implement** — in `main()` (which since Task 6 unpacks `items, bin_items, why, bin_why = fetch()`; its `items is None` branch is the one to change): `print("  backlog: could-not-run — gh or the network could not be reached (%s); the limits were not checked" % why)`; the docstring's "says it could not look, and passes" stays true. The `tests/mutations/p102a-check-backlog.json` row that anchors the old "skipped" line, if any, is re-pointed to the new sentence.

- [ ] **Step 4: Run the tests and the suite** — expected `OK`; `python3 tools/check_commit.py` from a shell with `PATH` lacking `gh` is NOT run (it would need a changed PATH; the unit test covers it).

- [ ] **Step 5: Mutation row**

```json
  {"file": "tools/check_backlog.py", "name": "P146: offline reads as checked", "find": "could-not-run — gh or the network could not be reached", "replace": "the limits hold — gh or the network could not be reached"}
```

- [ ] **Step 6: Commit**

```bash
git add tools/check_backlog.py tests/test_check_backlog.py tests/mutations/p146-process.json tests/mutations/p102a-check-backlog.json
git commit -m "P146: offline, the gate says could-not-run — never that the limits hold"
```

### Task 8: The status lists every wait oldest first, says "Ready low" at two, and flags a spent appetite

**Files:**
- Modify: `tools/board.py` (`waiting()`, `status_lines()`, `QUERY`, `to_items()`, a new `appetite_spent()`)
- Test: `tests/test_board.py`; rows

**Interfaces:**
- Consumes: `status_lines()` as Task 6 left it (`tools/board.py` ~:134-156: it passes the bin's items to `problems()`, and adds the note "the bin's board could not be read (no bin board was given)" when the boards list has no `bin` — a status test that gives only spark's board sees that line, so the tests below give `("bin", [])` as they do); `item["parent"]` from Task 2 — in the status it is an int or None (the gate's sentinel `"unread"` never reaches `board.py`); the board field **Appetite** (a number field, working days, set by the PO on an epic when it enters Discovery — created in Part C, item 4; until it exists, `item.get("appetite")` is `None` and nothing is flagged). `QUERY` gains `... on ProjectV2ItemFieldNumberValue{number field{... on ProjectV2FieldCommon{name}}}` in `fieldValues`, and `to_items()` reads `value.get("name", value.get("date", value.get("number")))`.
- Produces: `READY_LOW = 2`; `appetite_spent(items, work_days, today) -> [str]`: for each epic with an appetite whose working days since its Status last changed into a working stage are ≥ the appetite, `"! <epic> appetite spent: N working days of M — ship what is Done, bet again, or drop it"`.

- [ ] **Step 1: Write the failing tests**

```python
    def test_waits_are_listed_oldest_first_and_an_undated_one_last(self):
        items = board.to_items(project(node(1, "A — x", "Discovery", waiting="the PO", since="2026-10-07"),
                                       node(2, "B — y", "Idea", waiting="the PO", since="2026-10-01"),
                                       node(3, "C — z", "Idea", waiting="the PO")))
        self.assertEqual(board.waiting(items, dt.date(2026, 10, 9)),
                         ["B (#2) since 2026-10-01, 8 d !", "A (#1) since 2026-10-07, 2 d", "C (#3)"])

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

    def test_a_spent_appetite_is_flagged_in_working_days(self):
        epic = board.to_items(project(node(5, "E — x", "Discovery", changed="2026-10-01T09:00:00Z", labels=("epic",), appetite=3)))
        worked = {dt.date(2026, 10, 1), dt.date(2026, 10, 2), dt.date(2026, 10, 3), dt.date(2026, 10, 6)}
        self.assertEqual(board.appetite_spent(epic, worked, dt.date(2026, 10, 9)),
                         ["! E (#5) appetite spent: 4 working days of 3 — ship what is Done, bet again, or drop it"])
        self.assertEqual(board.appetite_spent(epic, {dt.date(2026, 10, 1)}, dt.date(2026, 10, 9)), [])
```

(`node()` gains `appetite=None`, adding a `ProjectV2ItemFieldNumberValue` node `{"number": appetite, "field": {"name": "Appetite"}}` when given.)

- [ ] **Step 2: Run them to see them fail** — expected `FAILED`.

- [ ] **Step 3: Implement**

```python
UNDATED = "9999-12-31"  #: an undated wait sorts after every dated one
READY_LOW = 2  #: at two the PO is asked to order Ready (the spec's cadences: "Ready is down to two")


def waiting(items, today):
    """The cards waiting on someone, oldest first, with since when; more than WAIT_TOO_LONG days is marked."""
    said = []
    for i in items:
        if not i.get("waiting on") or i.get("status") == "Done":
            continue
        since = i.get("waiting since")
        if since:
            days = age(since, today)
            said.append((since, "%s since %s, %d d%s" % (_short(i), since, days, " !" if days > WAIT_TOO_LONG else "")))
        else:
            said.append((UNDATED, _short(i)))
    return [text for _, text in sorted(said)]


def appetite_spent(items, work_days, today):
    """One flag per epic whose appetite (working days, the board's Appetite field) is spent since its stage last changed."""
    flags = []
    for i in items:
        appetite, changed = i.get("appetite"), i.get("status_changed")
        if "epic" not in i.get("labels", []) or not isinstance(appetite, (int, float)) or not changed:
            continue
        start = dt.date.fromisoformat(changed[:10])
        spent = len({d for d in work_days if start <= d <= today})
        if spent >= appetite:
            flags.append("! %s appetite spent: %d working days of %g — ship what is Done, bet again, or drop it" % (_short(i), spent, appetite))
    return flags
```

In `in_flight()`, a card labelled `expedite` is marked: `"%s %s %d d%s" % (…, " (expedite)" if "expedite" in i.get("labels", []) else "")` — the status says who holds the lane (a test with one expedite card; a row dropping the mark). In `status_lines()`, after the in-flight line: `lines += ["  " + flag for flag in appetite_spent(spark, worked, today)]`; after the Ready line: `if 0 < len(ready(spark)) <= READY_LOW: lines.append("  ! Ready is down to %d — propose an order for the PO" % len(ready(spark)))`. (`waiting()` today lists only `"the PO"`; the spec's *Waiting on* is always the PO, so listing any non-empty value changes nothing for his board and matches Task 4's rule.)

- [ ] **Step 4: Run the tests and the suite** — expected `OK`.

- [ ] **Step 5: Mutation rows**

```json
  {"file": "tools/board.py", "name": "P146: waits lose their order", "find": "    return [text for _, text in sorted(said)]\n", "replace": "    return [text for _, text in said]\n"},
  {"file": "tools/board.py", "name": "P146: an undated wait sorts first", "find": "UNDATED = \"9999-12-31\"", "replace": "UNDATED = \"0000-01-01\""},
  {"file": "tools/board.py", "name": "P146: Ready low at three", "find": "READY_LOW = 2", "replace": "READY_LOW = 3"},
  {"file": "tools/board.py", "name": "P146: a spent appetite is not flagged", "find": "        if spent >= appetite:\n", "replace": "        if spent > appetite + 10:\n"},
  {"file": "tools/board.py", "name": "P146: the appetite counts calendar days", "find": "        spent = len({d for d in work_days if start <= d <= today})\n", "replace": "        spent = (today - start).days\n"}
```

(Each `find` must match the committed code once; the anchors run proves it.)

- [ ] **Step 6: Commit**

```bash
git add tools/board.py tests/test_board.py tests/mutations/p146-process.json
git commit -m "P146: the status lists waits oldest first, says when Ready is down to two, and flags an epic whose appetite is spent"
```

### Task 9: Part A's gate and push

- [ ] Run `TMPDIR=<scratchpad>/commit-tmp python3 tools/check_commit.py` and read its three lines (the suite, the anchors, the size, the board).
- [ ] The controller pushes `p146-process` (the pre-push hook runs the gate again) and opens a **draft** PR "P146: the process fits how we work — the gate's rules, the status's lines, the process documents" (Closes #80), body to be completed in Task 17.

---

## Part B — the process documents (after PR #98 merges; `git rebase origin/main` first)

Every task here: read the spec's §4 bullet for the file, make the change, run `python3 tools/check_docs.py` and `python3 -m unittest tests.test_orphans tests.test_docs`, commit. **A sentence that states what a script does is checked against the script or a run before it is written** (W13, W17); the PO's words are quoted from #80, never paraphrased.

### Task 10: `scrum/README.md` — one page that says how we work

**Files:** Modify `scrum/README.md` (129 lines today).

- [ ] **Step 1: The top paragraph** (lines 1–12) keeps its first sentence and gains the spec's "What it is" paragraph verbatim after it: *"We run a Kanban system that keeps Scrum's roles and commitments: the Product Owner, the Definition of Done, Value proven by and the retro. There are no sprints, no Scrum Master and no ceremonies. The Kanban Guide allows this: a team's working agreements are part of its definition of workflow."* Add the line: *"The design behind this page: [`docs/2026-10-06-process-design.md`](../docs/2026-10-06-process-design.md) (accepted by the PO on 2026-10-06)."*
- [ ] **Step 2: "The people"** (lines 14–24) becomes two lines: the three roles' names with a link to [`TEAM.md`](../scrum/TEAM.md)'s role cards, and the sentence "Petr is the Product Owner and that is not decorative…" kept.
- [ ] **Step 3: "The ceremonies"** (lines 42–55) is retitled **"The cadences, and what each one leaves"** and its table is replaced by the spec's cadences table (§1) — seven rows: each session start, when you stop (the day-close), Ready is down to two, an epic's last story is Done or its appetite is spent, once a week, 2026-11-02 — with "you" → "the PO". Keep the sentence "A ceremony that produces nothing is a status meeting" as "A cadence that leaves nothing did not happen."
- [ ] **Step 4: "The flow"** table (lines 62–70) gains the spec's *enters when* and *leaves when* columns, taking the spec's rows with the later decisions: limits 2 / 2 / 5 / 2 / 2; Build enters "pulled from the top of Ready, or an expedite; a story's plan runs with no second yes unless it widens the scope or goes past the allowance, and a chore or bug needs no plan yes (decision 6, 2026-10-06)", leaves "the plan's tasks are done, test-first, and the final review starts"; Review enters "a fresh final review on the most capable model", leaves "the council before the PR (the PO assistant, the user's journey, the tech lead, a documentation expert, then the refuter) has run and its fixes are in; the DoD green; the proof posted; **then the PO merges** on Claude's 'ready to merge'"; Done enters "the work is where it is used (merged, or installed when there is no PR), and *Value proven by* has run with its output on the issue".
- [ ] **Step 5: Lines 72–92** become: the limits (2 per working stage, 4 in flight — the PO's call of 2026-10-06 evening, quoted); the three counting rules (as written, plus "a task with no parent story counts as a card — Task 2's gate"); lines 85–87 ("A plan's tasks are sub-issues… `check_backlog.py` skips them") say the same — a task under its story rides, a parentless one counts; **the expedite lane** (decision 4, quoted: "only on your word ('now'), one at a time, labelled `expedite`. It may take a stage one over its limit, and the gate fails on two"); the bin ("The bin's cards in flight count in the same four; a bench session is the PO's hands and sits outside them"); the trial note unchanged.
- [ ] **Step 6: Three new sections** after the flow, from the spec's §1 verbatim with "you" → "the PO": **Runs: reads, councils, reviews** (including the 2026-10-08 Review-stage rule from Task 1 Step 3), **The token budget** (decision 2 (a) quoted), **Asks to the PO** (one batch at a time, at most six, nothing decided until answered, *Waiting on* and *Waiting since*, the decision window).
- [ ] **Step 7: The Definition of Done:** clause 3 becomes "`python3 scripts/check_spine.py` on the proof project — exit 0 when `scripts/` changed (the chain still runs end to end)"; clause 4 adds "or, for work with no PR (a setting, a board field), the output of the command that shows it, posted on the issue"; clause 7 reads "Its closing comment quotes the gate's size line (`scripts/: N code lines (+M since origin/main)`) and says why (W15)"; add clause 9: "Before the PR: the council with a documentation expert, and its fixes (the PO, 2026-10-08)".
- [ ] **Step 8:** Run `python3 tools/check_docs.py && python3 -m unittest tests.test_orphans tests.test_docs 2>&1 | tail -2`. Expected: clean, `OK`. Commit: `P146: scrum/README.md says how we work — the cadences, the stages with their entry and exit, runs, the budget, asks, the DoD`.

### Task 11: `scrum/TEAM.md` — three role cards, and the two new roles

**Files:** Modify `scrum/TEAM.md` (58 lines today).

**Decision needed (Q1 in the question batch below):** what the **tech lead** and the **PO assistant** do across the process. Until the PO answers, write the recommended option and mark the two paragraphs "(the PO's answer to Q1 of 2026-10-09 may change this)".

- [ ] **Step 1:** Lines 1–6 ("Cross-functional means…") become the spec's **"Who does what"** table (§1) verbatim, "you" → "the PO", with the 2026-10-08 amendment in Claude's *decides* cell (Task 1 Step 2) — three columns: the PO (Petr), Claude (developer and orchestrator), the agents Claude launches.
- [ ] **Step 2:** "The test each member has to pass" stays, and its last sentence gains: "It applies to every lens of a council too."
- [ ] **Step 3:** "The roster" keeps the two agent rows and gains two **role** rows (roles, not agents — played by lenses the main session launches): **the tech lead** — "technical feasibility and the technical vision: a lens in every spec council, plan council and final review; proposes technical slices, refactors and the architecture cards; owns the technical lines of `DECISIONS.md`" (the PO's words of 2026-10-06 quoted: *"a tech lead role, to represent the technical feasibility and vision etc."*); **the PO assistant** — "drafts cards from the PO's words, proposes the Ready order and the slices, triages found work, keeps the day-close and the waits current; never decides value or order" (his words: *"the po agent role, like the po assistant, or so"*).
- [ ] **Step 4:** "How work reaches a member" (lines 49–58) is replaced by the spec's *does* column for Claude and the agents, and "Members do not commit" becomes: "An implementer commits on its task branch when a plan runs subagent-driven, never on `main`; the main session pushes, and the PO merges."
- [ ] **Step 5:** Run the docs checks; commit: `P146: TEAM.md is three role cards — the PO, Claude, the agents — with the tech lead and the PO assistant named`.

### Task 12: `scrum/WORKING_AGREEMENTS.md` — the cut to ten

**Files:** Modify `scrum/WORKING_AGREEMENTS.md` (269 lines; the headings: W1:11, W2:21, W3:36, W4:46, W5:59, W6:67, W7:79, W8:89, W9:101, W10:110, W11:117, W12:126, W13:136, W14:153, W15:164, W15b:172, W16:184, W17:191, W20:199, W19:227, W18:239, W21:252).

The spec's §3 table is the instruction, row by row. **Every heading stays** (44 files cite the numbers); a moved or merged rule's body becomes one dated line: `*Moved 2026-10-09 (P146) to <where>.*` / `*Merged 2026-10-09 (P146) into W<n>.*`, under its heading.

- [ ] **Step 1:** Keep and rewrite as the table says: **W1** (binds gates and agents' reports; the offline gate as the written exception — could-not-run, push allowed; fix the stale `answer()` pointer by grepping for the function it names), **W3** (absorbs W12; drop "no tooling, no hook" and "scrum master"), **W6** (the decided limits, counting rules, the expedite lane, both boards — one paragraph pointing at `tools/check_backlog.py`), **W8** ("every change reaches `main` by a PR that closes its card"; branch protection, decision 1 — "once set", with Part C's state), **W13** (absorbs W17 and W20's estimate clause), **W14** (Ready's entry policy; absorbs W7: "build only what is pulled, and reuse first"), **W15** (absorbs W15b: the size line in the closing comment; drop the retired budget clause — already amended in #98, check), **W19** (the card stands in its working stage before any agent starts; the launch hook — decision 1). **W2** and **W16** keep their text.
- [ ] **Step 2:** Move: **W5** and **W21** → `DECISIONS.md` (Task 13); **W10** and **W11** → the role cards (Task 11: the PO's card gets "paid minutes and the token allowance are the PO's" and "only the PO orders; an answer covers only what its option showed"). Merge: **W7**→W14, **W12**→W3, **W15b**→W15, **W17**→W13, **W20**→W9 and Ready's row, **W18**→the Design and Ready rows (its "one sitting" becomes the service level in the README's cadences). Habits: **W4** and **W9** move to a new final section **"Habits — no command judges these"** with their text; their headings get the dated pointer.
- [ ] **Step 3:** Append the section **"How a rule changes"**: *"By a PR whose card quotes the PO's yes, with a dated line on the rule. This replaces 'retired in `RETROSPECTIVES.md`', which was skipped twice in the week of 2026-10-06."*
- [ ] **Step 4:** Check no link to a heading breaks: `/usr/bin/grep -rn -o -E "WORKING_AGREEMENTS\.md#w[0-9a-z-]+" --include=*.md . | sort -u` — every anchor still exists (the headings stay). Run `python3 tools/check_docs.py && python3 -m unittest tests.test_orphans 2>&1 | tail -2`. Commit: `P146: the working agreements are ten — the rest moved, merged or made habits, each leaving its dated pointer`.

### Task 13: `DECISIONS.md`, `GLOSSARY.md`, the backlog design, the developing guide, the issue form

**Files:** Modify `DECISIONS.md`, `GLOSSARY.md`, `docs/2026-10-05-backlog-in-github-design.md`, `docs/guide/developing.md`, `.github/ISSUE_TEMPLATE/item.yml`.

- [ ] **Step 1 — `DECISIONS.md`:** a new section **"Product rules"** takes W5 (state the scope of an assertion) and W21 (keep a datum only if a decision rests on it), each with its origin line; the Ws it restates become one-line pointers to `scrum/WORKING_AGREEMENTS.md`. **Lines 53–56** ("`make check` in [the bin's local folder name] is deliberately RED…", "Six fab blockers stand…", "Simulation minutes … 21 of 50", "The Wokwi token…", "Pads 14/16…") and **line 69** (the spine table's "**blocked**" row): verify each against today's state before touching it (`make check` in the bin, the bin's STATUS.md blocker table, the chain's proof run); delete what is false, date what is kept. W17 applies: say in the commit what each line's check showed.
- [ ] **Step 2 — `GLOSSARY.md`:** "The budget" (147–154) — after #98 it says "a number, not a cap"; make sure it does, and point at W15. "Working agreement — W1, W2, … W21" (220) becomes "Working agreement — ten of them, W1…W19 by their numbers; two habits, two role rules, two product rules (`scrum/WORKING_AGREEMENTS.md`, P146)". "The board" (232–237) adds: the entry and exit of each stage are the README's table; the merge is the PO's. "Epic, story, task" (231–232): a task "rides on its story, with no slice or limit of its own" holds only for a task under a story — one with no parent story counts as a card (Task 2); say so. "Needed by" (162–168): the gate fails a push on an open item whose Needed by is empty — from Ready on (the commitment), since Task 3; in Idea, Discovery and Design a card decides whether to build; say so. The same sentence lives in `docs/guide/developing.md:62` ("every open item has a Needed by and a slice") and in the backlog design's §8 (:145, "an open item has an empty Needed by section or no Slice") — both become "every card from Ready on".
- [ ] **Step 3 — the backlog design:** §3 (48–56): the Build row's "the PO's yes" → "(decision 6, 2026-10-06: no plan yes unless the plan widens scope or goes past the allowance)"; the limits already read 2/5/2; §8 (136–140) adds "`STORY_MAP.md` rows say what each slice does today (P97, 2026-10-08)"; §9 (176–186) adds a dated paragraph: "P146 (2026-10-06, accepted; built 2026-10-09) gave the stages their entry and exit, the expedite lane, the appetite, the counting rules and the token allowance — `docs/2026-10-06-process-design.md`"; §11 gets a dated entry listing the six decisions with their dates.
- [ ] **Step 4 — `docs/guide/developing.md:61`:** the sentence on the board's limits links the README's table (it does) and adds "and the counting rules, the expedite lane and the bin's cards in flight (P146)". Two sentences still give the gate's offline word as "skipped" (Task 7 made it could-not-run): `docs/guide/developing.md:63` ("the board part says skipped and passes") and `docs/2026-10-05-backlog-in-github-design.md:151` ("prints that it was skipped") — both become "says could-not-run and passes". Three pages say the gate reads "spark's board" alone, which is now understated: `docs/2026-10-05-backlog-in-github-design.md:143`, `scrum/WORKING_AGREEMENTS.md:159` (Task 12's W8/W6 text) and `GLOSSARY.md:225` — each says "both boards: spark's stages and limits, and the bin's cards in the same flight total".
- [ ] **Step 5 — `.github/ISSUE_TEMPLATE/item.yml`:** remove the `proof` textarea (lines 19–24: "Proof — The command that proves it (from P102d on)…"); it is empty on every open card because proofs live in comments (the spec §4). Check `tests/` for a test reading the template (`/usr/bin/grep -rn "item.yml" tests/`), and adjust it.
- [ ] **Step 6:** Run the docs checks and the suite; commit: `P146: DECISIONS takes the two product rules and loses its stale cautions; GLOSSARY, the backlog design, the developing guide and the issue form follow the process`.

### Task 14: P146's own proof line, and the memory pointers (the controller's step)

- [ ] On #80, post the rewritten *Value proven by*: "The PO reads `scrum/README.md` and `TEAM.md` and confirms they describe how we work. The rules a script checks are checked: `python3 tools/check_backlog.py` prints the limits, the counting rules, the expedite and the bin's cards (its tests: `python3 -m unittest tests.test_check_backlog tests.test_board`), and `python3 tools/check_docs.py` and `python3 -m unittest tests.test_orphans` pass on the pages."
- [ ] Memory (outside the repository, by the controller): `scrum-process.md`, `go-on-automatically.md`, `commit-continuously.md`, `board-order-kept-current.md`, `council-before-pr.md`, `refine-backlog-with-team.md`, `finish-before-switching.md`, `background-observers.md` — each rule sentence becomes a pointer to the `scrum/` page that now holds it; `background-observers` becomes "outside eyes at stage points"; `spark-scrum-state` takes the new limits' wording.

### Task 15: The bin's status pages point at the board (a separate PR in `sisuo-brain-transplant`, its council first)

**Files (in the bin's repository, `sisuo-brain-transplant`, on a branch):** `CLAUDE.md:183-194`, `STATUS.md:36-66` (the "Waiting on Petr" list) and `STATUS.md:29` (blocker 2), `HANDOVER.md:94`.

- [ ] **Step 1:** `CLAUDE.md` lines 183–194 (the NEXT list of cards) become: *"NEXT is the bin's board, in the PO's order there — https://github.com/users/xmejkal/projects/1; every card carries its detail. Nothing has touched hardware. B1 (#1) closed 2026-10-06: the audio is the DFR0954 I2S amplifier, owned ×2 (no DFR0534 was ever bought); B29 (#23) retires the DFR0534 fallback. Open circuit questions for the PO: B25 (#19) the ToF wake line asserts at 1.89 V, below the S3's 2.48 V input-high; B26 (#20) the L9110S module drains the AA pack at rest; B28 (#22) the motor current over 0.15 mm track; B27 (#21) this file's Wokwi wake claim."*
- [ ] **Step 2:** `STATUS.md:29` blocker 2 → "**closed 2026-10-06** — the DFR0954 I2S amplifier, owned ×2 (B1)"; the "Waiting on Petr" item 1 (B1) is removed and the list renumbered; item 8 (which FireBeetle) stays. `HANDOVER.md:94`'s B1 line → "B1 (#1) — closed 2026-10-06: the DFR0954".
- [ ] **Step 3:** `make check` in the bin (its own docs check names retired parts outside deliberate passages — `tools/check-current-docs.py`); the council (TRIO + documentation + refuter) on the PR; the PO merges.

---

## Part C — the three guards and the board field (the PO's settings; nothing changes without his yes)

These are prepared as exact snippets and commands. The controller presents them in ONE question batch (below) and runs each only on his yes; a subagent never touches them.

### Task 16: The snippets

- [ ] **(1) The agent-launch hook** (decision 1a; W19). A `PreToolUse` hook on the `Agent` and `Workflow` tools in `~/.claude/settings.json` that refuses a launch whose `description` and `prompt` name no card: the script `tools/hooks/launch_names_a_card.py` (in spark, with tests) reads the hook's JSON from stdin, searches `tool_input.description + tool_input.prompt` for `#\d+` or `\b[PB]\d{1,3}\b`, and exits 2 with `"the launch names no card — W19: the card stands in its working stage before any agent starts"` when none is found; exits 0 otherwise. It does not check the stage (that needs the network at every launch); the status and the day-close catch a card in Idea with a run on it. Settings snippet:
  ```json
  "hooks": {"PreToolUse": [{"matcher": "Agent|Workflow", "hooks": [{"type": "command", "command": "python3 $HOME/Development/spark/tools/hooks/launch_names_a_card.py"}]}]}
  ```
  (merged into the existing `hooks` object, which holds one `SessionStart` hook today.) The spec's stated limit stands: the hook cannot see agents inside a workflow.
- [ ] **(2) Branch protection on `main`, both repositories, enforced for admins** (decision 1a; W8). Neither `main` is protected today (checked 2026-10-09: `gh api repos/<r>/branches/main/protection` → 404 on both). A repository **ruleset** (not the legacy protection API, whose review count cannot be 0) — for each repo:
  ```bash
  gh api -X POST repos/xmejkal/<repo>/rulesets -F name="main by PR only" -F target=branch -F enforcement=active \
    -f 'conditions[ref_name][include][]=~DEFAULT_BRANCH' -f 'bypass_actors=[]' \
    -f 'rules[][type]=pull_request' -f 'rules[][parameters][required_approving_review_count]=0' \
    -f 'rules[][parameters][dismiss_stale_reviews_on_push]=false' -f 'rules[][parameters][require_code_owner_review]=false' \
    -f 'rules[][parameters][require_last_push_approval]=false' -f 'rules[][parameters][required_review_thread_resolution]=false' \
    -f 'rules[][type]=deletion' -f 'rules[][type]=non_fast_forward'
  ```
  (The controller checks the exact field shape with `gh api repos/xmejkal/spark/rulesets --method GET` and GitHub's rulesets documentation before running; the first run is on `spark`, read back with `gh api repos/xmejkal/spark/rulesets`, and the PO confirms a direct push to `main` is refused before the bin's is set.) Effect: every change to `main` goes by PR; the PO's own merges keep working; the day-close and the board tools do not push to `main`.
- [ ] **(3) The `ask` rule for paid minutes** (decision 1a; W10): in `~/.claude/settings.json`, `"permissions": {"ask": ["Bash(wokwi-cli:*)", "Bash(make simulate:*)", "Bash(make simulate-all:*)"]}` (the `permissions` key is absent today).
- [ ] **(4) The board field Appetite** (decision 5): `gh project field-create 2 --owner xmejkal --name Appetite --data-type NUMBER` — a number of working days the PO gives an epic when it enters Discovery; Task 8's flag reads it.

### Task 17: Close the PR

- [ ] The controller: `python3 tools/check_commit.py` (TMPDIR inline), push, the PR body (what landed, Part A's sentences as the gate prints them from a run, the per-file sizes in code lines, the decisions quoted, the guards' state — which of the four the PO set, with the output that shows it), the council before the PR (the PO assistant, the user's journey, the tech lead, a documentation expert, the refuter), its fixes, then "ready to merge". The PO merges; P146 (#80) → Done with its proof posted.

---

## The question batch for the PO (one batch, six questions, each with a recommendation)

1. **The two roles' duties** (Task 11). (a) **Recommended:** the tech lead is a lens in every spec council, plan council and final review, proposes technical slices and refactors, and owns `DECISIONS.md`'s technical lines; the PO assistant drafts cards from your words, proposes the Ready order and the slices, triages found work, and keeps the day-close and the waits current — neither decides value or order. (b) Both only as council lenses, as the discovery skill uses them today. (c) Your own wording.
2. **The launch hook** (Part C item 1): set it now as written? (a) **Recommended:** yes — the pattern check only, no network. (b) Not yet.
3. **Branch protection** (item 2): (a) **Recommended:** the ruleset on `spark` first, confirm, then the bin. (b) Not yet.
4. **The `ask` rule** for `wokwi-cli` and `make simulate` (item 3): (a) **Recommended:** yes. (b) Not yet.
5. **The Appetite field** on the spark board (item 4): (a) **Recommended:** yes, a number of working days. (b) No appetite for now.
6. **The stale cautions in `DECISIONS.md`** (Task 13 Step 1): (a) **Recommended:** delete what today's checks show false, keep the rest dated. (b) Keep them all, dated.

Decision 6 of 2026-10-06 ("one yes per story, on its spec") lets Parts A and B run without a plan yes; the four Part C items change your settings and GitHub, so each waits for its answer.
