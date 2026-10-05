# The state in view at every session start, and the day-close — design (P102c)

**Status:** the spec, for the PO's review (2026-10-05). Issue: xmejkal/spark#26, a story of the tools chore P102
(#24). It builds on P102a: the boards live in GitHub Projects (`docs/2026-10-05-backlog-in-github-design.md` §3, §9),
and `tools/check_backlog.py` already reads the spark board and gives the limit verdict.

## 1. What it is for

The PO, 2026-10-05: to be *"always aware of what we're actually doing now … if we're actually finishing epics"*, and to
be told when he starts something new while something is unfinished (the rule *finish before switching*). P102a's
spec §9 set two cadences that serve this.

- **At every session start**, the session opens knowing the state of the work:
  - what is in flight, and for how long;
  - what waits on the PO;
  - the Ready column in his order;
  - the open PRs;
  - whether a limit is broken;
  - the last day-close.
- **At the end of each working day**, Claude writes one dated line: what moved, what was proven, what is aging, and
  the next card. That line is also the restart point after an interrupted or compacted session.

**Done means:**
- A Claude Code session started in one of the PO's project folders opens with the status. In any other folder it
  prints nothing.
- `tools/board.py close --dry-run` shows the day-close it would post; without `--dry-run` it appears as a status
  update on the spark board.
- A session started the day after a working day with no close says so, and the close is written first.

## 2. `tools/board.py` — one tool, two verbs

It is a team tool, not the product, so it lives in `tools/` beside `check_backlog.py`. It reads the boards through the
PO's own `gh` login and stores nothing.

### `board.py status [--when-in DIR ...]`

At most about twelve lines, for spark's board and the bin's:

```
spark — 28 open, the limits hold · trial check 2026-11-02
  in flight: Design P102c (#26) 0 d
  waits on the PO: R2.6 (#15); bin B1 (#1) since 2026-09-25, 10 d
  Ready: P103 (#32), P97 (#18)
  open PRs: spark #5 P102c (draft)
  last close 2026-10-05: <the line>
  ! the day of 2026-10-06 has no close — write it first
```

- **In flight** is the cards in Discovery, Design, Build and Review. Each shows its stage and its **age**: the days
  since its Status value last changed (GitHub keeps `updatedAt` on each field value). Epics and tasks are left out,
  as the check leaves them out.
- **Waits on the PO** is the cards with *Waiting on* set to the PO, in both boards, each with *Waiting since* and its
  age. A card waiting more than 3 days is marked, as the weekly look asks.
- **Ready** is the Ready column in the board's own row order, which is the PO's order (W11).
- **Open PRs** are listed for spark and the bin, with their numbers, titles and whether each is a draft.
- **The verdict** comes from `check_backlog.problems()`, the same sentences the push gate prints. There is no second
  rule.
- **The last close** is the newest status update on the spark board: its date and its first line.
- **A missing close.** If the last working day before today has no close, `status` prints one line saying so. A
  working day is a day with a commit on any branch in the folders `--when-in` names, read from local git: it costs no
  network call and works offline (decision 5).
- **`--when-in DIR ...`:** status prints nothing unless the current directory lies inside one of the named
  directories. The folders are named in the PO's settings, not in the repository, so no personal path ships.
- **Offline,** or when `gh` is logged out, it prints one line: `board: skipped — <why>`. A session start must never
  fail. Each `gh` call at a session start gives up after 8 seconds, so a stalled network costs seconds, not minutes.

### `board.py close [--date D] [--dry-run] LINE|-`

- It posts the day-close as a **status update on the spark board**, using GitHub Projects' own dated note
  (`createProjectV2StatusUpdate`). The update has:
  - a start date of the day it closes (today, or `--date` for a day missed);
  - the status *on track*, or *at risk* when a limit is broken or something has waited on the PO more than 3 days;
  - a body of Claude's one line, then a two-line snapshot of the board: in flight, and what waits on the PO.
- The line arrives as an argument, or on stdin with `-`. It is never built into a shell command line.
- `--dry-run` prints the update and posts nothing.
- **Closing a day twice** is refused, with the date of the first close, so a retry cannot post twice.

## 3. The hook — in the PO's own settings

- One `SessionStart` hook in `~/.claude/settings.json`:

  ```
  python3 ~/Development/spark/tools/board.py status --when-in ~/Development/spark ~/Development/smartbin-local
  ```

  The folder list is the PO's to extend; irrigation can join when its demo moves (P102f).
- The hook's output enters Claude's context at the start of the session, so the first reply starts from the board.
- **Writing the hook into the PO's settings is a persistent configuration change.** The exact entry is shown to him,
  and it is written only with his yes.

## 4. When a day is closed

- Claude writes the close when the PO says he is done for the day, and before a long pause it knows of.
- If a session starts and `status` reports a missing close, Claude writes that day's close first, from `git log` and
  the board, with `--date`. Only then does it go on.
- **Where this rule is written** is P103's job (the process documented). Until then, the line `status` prints is the
  reminder.

## 5. Testing

- **The formatting, the age arithmetic and the missing-close rule** are pure functions. They are tested on recorded
  board answers and fixed dates, offline, like `check_backlog`'s tests.
- **`--when-in`** is tested with a directory inside the named folders and one outside.
- **`close`:**
  - its update is checked through `--dry-run`'s output;
  - the refusal of a second close of a day is tested on a recorded list of updates;
  - the on-track and at-risk choice is tested both ways.
- **Mutation table:** the missing-close rule and the close's refusal, the two verdicts this tool gives. The status
  text is a report (P72's cut: mutation tables only for verdict code).
- **Proof:**
  - one live `status` in smartbin-local;
  - one `close --dry-run`;
  - then, with the PO's yes, one real close of today, seen on the spark board.

## 6. Not in this spec

- The story map drawn in Miro and Canva (P102b).
- Proofs run as commands, and the *Proven* field (P102d).
- The epic-done audit as a command (P102d).
- Writing the day-close rule into the process documents (P103).

## 7. Decisions (the PO, 2026-10-05)

1. The hook lives in his user settings, and shows only in his project folders.
2. The day-close is a status update on the spark board.
3. A day is closed when he stops, or at the next session's start if it was missed.
4. The design is one tool, `tools/board.py`, with two verbs, `status` and `close`, reusing `check_backlog`.
5. A working day is a day with a commit on any branch, read from local git. The final review found that `main` moves
   only by merges, so a day of branch work went unflagged; the PO: *"it should be ok to be offline when working on it."*
