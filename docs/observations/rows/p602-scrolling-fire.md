# P602 the scrolling fire: rows

What the plan, the review, the mutation run and the PO's play found. Card: [P602 #803](https://github.com/xmejkal/spark/issues/803).
PR: https://github.com/xmejkal/pixel-games/pull/27. The plan is named "the plan" here.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The refuter (Fable 5.1) found a MUST in plan round 1: on the Mac, `import engine` finds the empty `engine/` folder, so a check of "engine is not None" is wrong | the plan, round 1 | acted | the code checks `hasattr(engine, "HeatField")`, and a test covers it |
| 2 | Lesson: this is the second time. P608's row 3 had the same wrong claim about `engine` on the Mac. Check the claim in the code before a plan states it | the plan, round 1 | closed | a lesson for the retro — P776: done by P608 #810 (closed) |
| 3 | Plan round 1 MUST: the Mac test canvas lacked gradient, sprite and tft | the plan, round 1 | acted | the test canvas gained all three |
| 4 | Plan round 1 SHOULDs: rename the cooling map's `scroll` fields to `map_row`, so "scroll" means one thing. Use integer scroll math with a remainder test. Clear a field each round. Count the 60 ms dt cap | the plan, round 1 | acted | all four went into the plan |
| 5 | Plan round 2 SHOULD: draw Flappy through the real `lcd.TftCanvas` on the Mac | the plan, round 2 | acted | the Mac test draws through the real canvas |
| 6 | The implementer found that plan step 3 would make a tuple a frame | the implementer | acted | FireTrail keeps int path fields |
| 7 | The estimate was wrong. The plan said 16 to 17 fps and the board gave 21, because the blend skips heat 0 | PR 27, "On the board" | closed | a lesson for the retro: an estimate from a full-screen scene overstates a sparse one — P776: stale note: Lesson for the retro. |
| 8 | The Sonnet review found two SHOULDs: take the signed dx from `FireLayer.update`, and fix the docstrings that said "a frame makes nothing" while the FireTrail lag makes floats | PR 27, "Review" | acted | both fixed |
| 9 | The Sonnet review found a NIT: `clear()` did not reset the step clock | PR 27, "Review" | acted | fixed, with a test |
| 10 | The Fable PR refuter found a SHOULD: no board number backs the claim "no allocation" | PR 27, "Review" | acted | run95 on the board: 0 B for update and draw |
| 11 | The mutation run planted 30 defects and the tests caught 24. Four escapes were in flappy | PR 27, "Review" | closed | the four closed with flappy's removal (row 13) |
| 12 | Two escapes were in kept parts: scroll by w-1, and clear by -W+1 | PR 27, "Review" | acted | 7a4d342 adds a test for each |
| 13 | The PO played it: "it looks good, I'm glad we have this effect, but it doesn't really fit the flappy, so we should remove it, this was just a test, but we could definitely use it in other games." | bench.md, P602 section | verified | flappy was reverted, and the parts are marked Later |
| 14 | The PO's wish for a faster fire became spike P612. It overlaps P583 (PIE) | comments on [#817](https://github.com/xmejkal/spark/issues/817) and [#784](https://github.com/xmejkal/spark/issues/784) | closed | noted on #817 — P776: tracked by #817 (closed), P583 #784 (open), P612 #817 (closed) |
