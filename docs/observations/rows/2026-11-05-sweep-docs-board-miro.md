# The 11-05 sweep of docs, board, plans and Miro: rows

The PO, 2026-11-05: "lets also make sure we have everything updated, the documentation, miro, plans and backlog and
storymaps". Three read-only audits ran on Sonnet (docs, backlog and plans, Miro), then the fixes.
PR: this branch, `sweep-1105`.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | 14 committed lines in 11 docs files name a home path (`/Users/<name>/...`): archive audits, the P271 discovery plan, the walk 2 council, three rows files | docs audit + `git grep` | acted | each became `~/` (1d8c7115). The public-repo rule has no archive exception |
| 2 | `tools/check_docs.py` has a `PERSONAL` pattern, yet the 11 files passed: the docs gate does not scan `docs/archive/`, `docs/discovery/` or `docs/observations/` | the lead | closed | a test that greps every tracked file for a home path, as `tests/test_orphans.py:121` does for its own files. A row for P495 #677's gate list, no new card — P776: tracked by #677 (open), P495 #677 (open) |
| 3 | pixel-games README said ten games. `games/app.py` registers fourteen (four effect scenes) | docs audit | acted | pixel-games PR #32 |
| 4 | pixel-games README tagged flappy's 24 fps "(P602)", but run92 is the P602 run before the fire went on | docs audit | acted | pixel-games PR #32 |
| 5 | spark's "What works today", the journey picture and the P473 `env` docs agree with the code (`tests.test_journey tests.test_docs`: 44 tests OK) | docs audit | closed | no change |
| 6 | Four open chores had no parent epic: P264 #294, P495 #677, P503 #692, P506 #700 | backlog audit | acted | each is a sub-issue of "Later: team and QA tooling" #158 |
| 7 | P100 #6 has "Waiting since" 2026-10-19 and no "Waiting on" | backlog audit | closed | for the PO: it waits for his bench time (walk 1) or the date goes — P776: tracked by P100 #6 (open) |
| 8 | Build holds 4 cards (#713, #6, #467, #795), Design 4. Three of the Build cards and all of Design are epics | backlog audit | closed | for the PO: do the limits of 2 per stage count epics? `board.py` says the limits hold — P776: tracked by #467 (open), #713 (closed), #795 (closed) |
| 9 | Ready holds one card, P605 #807 | `board.py status` | closed | the lead proposes an order to the PO — P776: done by #807 (closed), P605 #807 (closed) |
| 10 | Every closed card is Done, every Done card is closed, and P594 #795 has no open sub-issue (its open cards are under P620 #827) | backlog audit | closed | no change |
| 11 | Four plan files belong to cards still at Idea (P511, P447, P469, P582). Every other plan from the last 7 days belongs to a closed card, except P517 (in Build) | backlog audit | closed | kept: a plan waits with its card |
| 12 | Miro story map: four cards disagree with GitHub (P221 #203, P219 #201, two "#200 new" cards) and the P158 row says 15 of 23 slices, not 17 | Miro audit | acted | the Miro fix pass |
| 13 | Miro "P158 v0.13 one core" note says "Updated 2026-11-01" and names W4-1 in Build. One card overflows its box | Miro audit | acted | the Miro fix pass |
| 14 | Miro has no frame for the open epics P609 #812 and P620 #827, and the overview's link row misses six epic frames | Miro audit | acted | the Miro fix pass |
