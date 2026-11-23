# P1038: the project page, the design: rows

Card: [P1038 #1521](https://github.com/xmejkal/spark/issues/1521). This file holds the acted, raised and rejected findings only. The design is [design.md](../../discovery/2026-11-23-p1038-page-design/design.md). Every finding with its evidence is in [council/design/](../../discovery/2026-11-23-p1038-page-design/council/design/). The council ran two rounds and a last read on 2026-11-23: lenses on Opus, the refuter launched on the best model, and a delegated council of three seats.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | The round 1 findings A1 to A20, UX-1 to UX-22, P-1 to P-8, F-1 to F-7, S-2 to S-5, T-1, T-2 and R-1 to R-9 | round 1 | acted | design.md at 31107da7; r1-refuter.md holds a verdict per finding |
| 2 | The round 2 findings B1 to B17, V1 to V25 (except V19) and S-1 to S-8 | round 2 | acted | design.md at bd9428b3; the architect's table per id is summed up in r2-refuter.md |
| 3 | The last read's R-1 to R-9 | the last read | acted | design.md at 7bdb2c70; r2-refuter.md, section "The last read" |
| 4 | Seven choices that are the PO's (Q-A to Q-G) | round 1 | acted | answered by the delegated council, recorded as delegated, his to change: delegated-answers-r1.md |
| 5 | Cut story 1d from slice 1 (S-1 of round 1) | round 1, tech lead lens | rejected | dropped because D11 is the PO's own decision; 1d stays and waits for P829's walk (Q-E) |
| 6 | Move the TypeScript chore after the walk (V19) | round 2, UX lens | rejected | dropped as an order change because D29 is his order; it is point 10 of his list instead |
| 7 | `published.behind` and its reason (UX-5) | round 1, UX lens | rejected | dropped because the published record is cut (A1, S-3) |
| 8 | The live-page seam as a Reporter (A11) | round 1, architecture lens | acted | one "project written" event that each consumer adapts; nothing is built |
| 9 | The refresh after a deploy at any status but a crash | round 1, the refuter (R-1); round 2 (B11) | raised | story 0c under P793 #1105, for spark-main to file; P1035's plan already gives the refresh its own condition (spark-main, 2026-11-23) |
| 10 | Nine stories of slice 1 have no card: 1a-i, the TypeScript chore, 1a-ii, 1b, 1c, 1e, 1f, 1d and the walk | the design | raised | for spark-main to file under P1038 #1521, after the PO's yes (Q-A) |
| 11 | #1518, #1533, #1534 and #1535 need new text | the design | raised | for spark-main to edit; the texts are in the PR body |
| 12 | The "held by" names on a shared copy: the parts reader keeps the holders as a field | the delegated council (Q-G) | raised | a card on P834 #1196, for spark-main to file |
| 13 | The owner-only word of `get_artifact` and an owner-read database path were never read | round 1 (P-3), round 2 (S-3) | raised | 1f's plan reads both first |
| 14 | The cause map's sentence starts in the 27 board logs were not read | the last read | raised | P1043's plan reads them |
| 15 | Whether the deploy's note joins the secrets filter | the last read (R-8) | raised | 1c's plan decides |
| 16 | The language server does not run with TypeScript 7 | D29, round 2 (B7) | raised | an install that waits for the PO; point 9 of his list |
| 17 | The first publish stays untested in the walk | round 2 (V25) | raised | the walk's card adds a first publish on a scratch project, on the PO's yes |
