# R9 retro, the story builder

Helped
- A written plan before code. PR #343 (P239 PR 6) and #346 (P239 PR 7) each carry a plan.md, a TL;DR, a class diagram and a "no change a user sees" line. Mutation runs on 10 cards planted 213 defects and 25 escaped (23 real gaps), so a plan alone did not make the tests complete.
- Small PR slices. 20 of 51 PRs merged in under 15 min, median 24 min. P239 PR 7 and PR 8 were small enough to land the same day.

Slowed or wasted
- Merges of main into a branch. 15 since 10-15, and 10 of them only kept or renumbered observation rows (ac4e965 AT420-AT442 beside AT450-AT454, d47b2c9 AT383-AT386). Each costs a merge, a re-run and often a refused push.
- Push refusals. 14 in the logs: P239 PR 7 had 6, P287 had 3, P288 had 2. P239 PR 7 ran 75 min for 83 tool calls.
- P239 PR 6 LookReport: 460 tool calls, 41 min, 103 M input tokens, about 20% of the 506 M total, mostly the merge after P242 touched the same files. P242 (188 calls, 58 M) and P273 (150 calls, 42 M) are next.
- Parallel stories on the same files. P239 PR 6 and P242 both edited the deploy and look modules, so the second builder paid the first one's cost.
- Rate limits hit builders 16 times (P213a 4, P239 PR 8 3), each a stall inside a run.

The change I ask for
- Put observation rows in one file per row, or per PR, before the next builder starts (P296 #358, now Ready). Pull it ahead of P299 and P300. It removes the cause of 10 of 15 main merges and most refused pushes.
