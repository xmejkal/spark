# P594 the effects epic's close: rows

What the epic's close found: the audit, the walkthrough's check, the PO's choices and the tools. Epic: [P594 #795](https://github.com/xmejkal/spark/issues/795).
PRs: https://github.com/xmejkal/pixel-games/pull/30 (the walkthrough, a draft until the PO walks through it) and https://github.com/xmejkal/pixel-games/pull/31 (the audit's small fixes).

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The four slices of the PO's close plan are done: P590 #791, P598 #799, P607 #809, P602 #803 | #795, comment of 2026-11-04 | verified | all four closed and merged |
| 2 | The PO chose "Move with the rest" for P606 and "New epic 'More effects'" for the open cards | #795, 2026-11-05 | acted | P620 #827 holds P597, P600, P601, P606, P610 and P611 |
| 3 | The epic audit (Fable 5.1) found no MUST. It reran 159 tests and sampled about 30 of the walkthrough's line pointers, and all matched | the audit | verified | no home path, secret or vendor file in the epic's diff |
| 4 | The audit's four small finds: a README number with no bench source, no static assert on the share table, a stale cooling-map comment, a literal 64 | the audit | acted | pixel-games PR 31 |
| 5 | The audit found the engine's argument limits in four files, and no test reaches the binding's HeatField checks | the audit | raised | P621 #828 |
| 6 | The audit found glue in two or three copies: two step clocks in fire.py, read, drain and frame checks in binding.c, the neighbour sweep in fx_balls.c | the audit | raised | P622 #829 |
| 7 | The audit found n, events and damping each meaning two things | the audit | raised | P623 #830 |
| 8 | The walkthrough draft (Sonnet) named a home path in its first line, and pixel-games is public | the lead's read | acted | removed before the commit. Lesson: a draft for a public repo gets a home-path grep before it is committed |
| 9 | The walkthrough's fact check (Sonnet) checked about 90 pointers, fixed 2 and 1 number, and rendered both diagrams with mermaid-cli | PR 30 | verified | one "not checked" left and answered from the code |
| 10 | The Miro sweep for P598 stopped at the Free plan's limit of 100 MCP calls a day | the Miro agent | raised | the P598 panel is on the board, not read back. The frame's subtitle, legend, order text and four strips wait for the reset. A lesson for the retro: count Miro calls per sweep |
| 11 | In the PO's auto mode, Claude Code's classifier blocked `gh pr merge` ("Merge Without Review"), so the PO merged by `!` commands | the session | raised | in the retro inbox. Ask: a permission rule, or the PO merges |
| 12 | The PR 31 refuter (Fable 5.1) found no MUST. It confirmed that the static assert fails the build when a radius changes, and that both builds accept `_Static_assert` (no `-pedantic`) | PR 31 | verified | a NIT for later: a `-pedantic` flag would break that line first |
| 13 | The PR 31 refuter found that bench.md's "90 ms in run 100" was the first sample only, and the steady value is about 97 ms. The README's run names also sat after the wrong number | PR 31 | acted | 8018075 |
| 14 | In auto mode, the two spark cards in Ready got plans with Fable councils, not code: P473 #647 (two rounds, two MUSTs fixed in round 1) and P517 #713 (one check, an XS card). Both wait for the PO's OK, and P517 asks him one question first | #647, #713 | raised | the plans are on the lead's Mac. A lesson for the retro: a plan's approval is the PO's, so an auto-mode night ends at "plan ready" for logic cards |
