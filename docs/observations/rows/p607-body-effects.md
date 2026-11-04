# P607 a body carries an effect: rows

What the plan, the review, the mutation run and the board found. Card: [P607 #809](https://github.com/xmejkal/spark/issues/809).
PR: https://github.com/xmejkal/pixel-games/pull/24. The plan is named "the plan" here.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The refuter (Fable 5.1) found a MUST in plan round 1: without the engine the field is None, and the flare handler would crash on the first hard landing | the plan, round 1 | acted | the handlers are empty without a field, and a no-engine test pins it |
| 2 | Plan round 1 SHOULD: the tests replaced `game.bodies` after setup, so the effects did not read the real stepper | the plan, round 1 | acted | the helpers call `attach_effects()` on the stand-in |
| 3 | Plan round 1 SHOULD: "bodies" meant three things | the plan, round 1 | acted | the scene slot is `self.stepper` |
| 4 | Plan NIT: run84 does not exist, so the next run is run84 | the plan, round 1 | rejected | run84 exists as git-ignored logs, so run85 was next |
| 5 | The Sonnet code review found no MUST. SHOULD: a star-call allocated per body. Name NITs: `forget`, `light` | PR 24, "Review" | acted | place is unpacked first, and the step went from 7.64-7.75 ms to 7.60-7.68 ms on the board. The name NITs were fixed later by the PO's rename (row 9) |
| 6 | The Fable refuter found a MUST: `apply` twice, or a missing `or` before `react`, passed every test | PR 24, "Review" | acted | closed by a `play()` test with the exact burn list |
| 7 | The refuter replayed 1,500 frames on master and on the branch: both made the same 10,749 `HeatField.burn` calls. The 3-frame PNG cmp was a real test | PR 24, "Review" | verified | no change |
| 8 | The mutation run planted 20 defects and the tests caught 19. The escape: `cx < W` in place of `2 * W` in `FireTrail.update` | PR 24, "Review" | acted | closed by a test for both side margins |
| 9 | The PO's rule of 2026-11-04, industry-standard names: `BodyEffects` became `EffectSystem`, `react(reactions)` became `dispatch(handlers)`, `apply` became `update`, `forget` became `reset`, `light` became `attach_effects` | pixel-games 3e146eb | acted | epic [P609 #812](https://github.com/xmejkal/spark/issues/812) carries the rename for the whole engine |
| 10 | Process: `mpremote cat` adds CR line endings. A compare with the repo needs `tr -d '\r'`. The first compare wrongly showed every board file as different | PR 24, "On the board" | acted | the compare strips the CR first |
