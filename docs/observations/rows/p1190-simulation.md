# P1190: the simulation as a step of its own: rows

Card: [P1190 #1735](https://github.com/xmejkal/spark/issues/1735), an epic in Discovery. The discovery is
`docs/discovery/2026-11-26-p1190-simulation/`. Its refuter on Opus ran twice on the brief (council/refuter.md), and
the PR's refuter on Opus ran once on the PR (council/pr-refuter.md), all on 2026-11-26. This file holds the acted,
raised and rejected findings only.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the 4 scenario logs are a floor of runs, not a count, and a walk diary says the run waited on the unknown minutes | refuter (Opus) | acted | brief.md ★C16 and its caveat, Q9 reworded |
| 2 | PR #1580 merged and P1077 is closed, so P1078 waits on nothing | refuter (Opus) | acted | brief.md ★C15, option (d) of Q2 |
| 3 | P999 alone may cover the clock, which takes item 1's proof | refuter (Opus) | acted | brief.md ★C25, the Outcome's fixture board (D2) |
| 4 | removing `NO_MODEL_CODES` reverses the PO's D-c, and old records and exit codes change | refuter (Opus) | acted | Q11, answered by the PO (D11) |
| 5 | Pro is EUR 20 on annual billing only, and Hobby has 200 minutes and Hobby+ 500 | refuter (Opus) | acted | brief.md ★C10 |
| 6 | the replay of the clock's commits cannot test A1, because its tests came after its faults | refuter (Opus) | acted | the Test line: a forward use log instead |
| 7 | the clock drives GPIO14, which P999's stand-in lacks | refuter (Opus), round 2 | acted | brief.md ★C25, A3 |
| 8 | D2 made a free check's record a deploy rule that is the PO's, and D3 claimed 3 of 3 for a 2 of 3 order | refuter (Opus), round 2 | acted | brief.md D2, D3 |
| 9 | ★C12 is wrong: esp-emulator and esp32sim run the C6 | the pre-analysis | acted | brief.md ★C12, research-alternatives.md's added section |
| 10 | `chips/wokwi-api.h` comes from Wokwi and carries no licence line | the pre-analysis | raised | P1225 [#1774](https://github.com/xmejkal/spark/issues/1774) |
| 11 | `tests.test_suite_runs` fails under Homebrew's Python 3.13 on this shell's PATH | the session, the first push | rejected | spark-main: the project's interpreter is pyenv's 3.10, a known retro item. The push with it passed |
| 12 | #1772 and #1773 named #1773 for item 14 | PR refuter (Opus) | acted | both bodies fixed |
| 13 | P308 #374's deploy rule was lost when it closed as absorbed | PR refuter (Opus) | acted | written in P1213 #1762's Notes, and a comment on #374 |
| 14 | D17 wants item 19's first steps before item 6's plan, but #1773 is parked after v0.10 | PR refuter (Opus) | raised | P1212 #1761's Notes say its plan waits on them, and the order is the PO's, sent through spark-main |
| 15 | D15 read as a reversal of the non-goal, which the PO's words do not say | PR refuter (Opus) | acted | brief.md D15, P1223 #1772's Notes |
| 16 | D16 and D18 mixed his words with the reading | PR refuter (Opus) | acted | brief.md D16, D18 |
| 17 | stale lines in brief.md, items.md, README.md, story-map.md and risks-and-tests.md | PR refuter (Opus) | acted | each line fixed |
| 18 | a misfiled card or unsafe text in the folder | PR refuter (Opus) | rejected | all 19 cards match their items, parents, stage and slice. No home path, token or vendor file |
