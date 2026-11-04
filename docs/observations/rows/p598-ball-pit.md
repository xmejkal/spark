# P598 the ball pit: rows

What the two plans, the board, the review, the mutation run and the PO's play found. Card: [P598 #799](https://github.com/xmejkal/spark/issues/799).
PR: https://github.com/xmejkal/pixel-games/pull/28. "The card plan" is the first plan, and "the feel plan" is the plan for friction and bounce.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The refuter (Fable 5.1) found four MUSTs in card plan round 1: render_scene took only fire and burning, one relaxation pass left 1.29 px of overlap and 114 px/s jitter, Python could not see a side swap between substeps, and the Mac `import engine` trap | the card plan, round 1 | acted | two passes, damping, `hasattr(engine, "Balls")`, render_scene gained balls |
| 2 | Lesson: the Mac `import engine` trap came up a third time (P608 row 3, P602 row 2) | the card plan, round 1 | raised | a lesson for the retro: a plan template line for the Mac engine check |
| 3 | Card plan round 2, two MUSTs: the `closest` check failed a correct run and missed real side swaps, and a resting pile fired up to 135 hits a call | the card plan, round 2 | acted | a move cap of 1.5 px a substep, a test that steps one substep at a time, the hit speed read after the integrate |
| 4 | The first board build ran 300 balls at 5 fps, a step of 165 ms a frame. The plan's estimate was 6 to 15 ms | run96, bench.md P598 | acted | three root causes fixed: the arrays found once a substep, an int cell division, a contact with no `sqrtf` or division (the S3 calls a library routine for each) |
| 5 | Lesson: on the S3, a float division and `sqrtf` are library calls. A plan for C on the board names them before the first build | run97 to run97d | raised | a lesson for the retro, and a fact on P614 #820 |
| 6 | The HUD's text rebuild costs about 50 ms twice a second and caps every scene near 24 fps | run100 | raised | on P614 #820 |
| 7 | The implementer (Fable) left seven deviations from the card plan, each reported in its commit | commits 1 to 7 | verified | the PR's review read them |
| 8 | The PO played it and asked for more: a shake on a hold, a HUD with the fps first, up to 2,000 balls and 10 a pour | comments on #799 | acted | 4b5f010, fc78f03, e83d5a1, 1f0d8a2 |
| 9 | The feel plan's refuter found two MUSTs: a friction-0 slide cannot pass 150 px, and a bounce as extra separation gave no bounce for a light ball on a heavy one | the feel plan | acted | a 120 px bar, the bounce at the velocity level with a bounce list |
| 10 | The feel plan's refuter found that a soft contact with no damping adds its own bounce and lets the pile sink | the feel plan | acted | the PO chose "Bounce + friction now", and the soft contact became P618 #824 |
| 11 | The bounce at the velocity level still gave a ball that landed on the pile only 0.17 to 0.34 of its closing speed, because the floor took the lower ball's share back | Mac probe, 8807669 | acted | a resting ball under the other acts as ground: 0.43 for every radius pair at restitution 0.5 |
| 12 | I told the PO that friction and bounce cost 38 % at 320 balls. That compared two different piles at different frame rates (run100 against run104) | run104, run106 | acted | run106 measured one pile at both materials: about 5 %. A lesson for the retro: compare a cost on one fixture, one image, one run |
| 13 | My first `gh issue comment` with `-q` failed, and `2>/dev/null` hid the error, so I said "posted" before it was | the #799 comment | acted | posted again and read back. Lesson: never hide stderr on a write |
| 14 | The auto-mode classifier blocked my `kill` of an `mpremote run` that an earlier session started | the board | closed | the PO ran the kill. Board runs that a session starts are now its own background tasks, stopped with TaskStop |
| 15 | The Sonnet review found no MUST and five SHOULDs: a stale docstring, the binding test tests the mirror, no `dt` check, an unread `bounces_dropped`, stale test numbers | PR 28, "Review" | acted | all fixed in 862e32e |
| 16 | The Fable PR refuter found that friction makes a settled pile creep for about 16 s, with a hit or two a second, so "0 hits at rest" was false | PR 28, "Review" | acted | the comment says so. The cause (friction corrections in two Gauss-Seidel passes feed the velocity) is a fact for P618 #824 |
| 17 | The Fable PR refuter planted friction with no kinetic limit, and no test caught it | PR 28, "Review" | acted | the heap test is a window (40 to 47 px) that catches it |
| 18 | The PO played the feel slice: "Yeah, better. I like it. The bounce could be a bit stronger" | comment on #799 | acted | restitution 0.7 (9cb3cba) |
| 19 | The PO's new tests: textured balls and balls on fire, to see what the graphics cost | comments on #825 and #822 | raised | P619 #825 filed, P616 #822 gained his words |
| 20 | The mutation run planted 28 defects, and the tests caught 18. Two escapes are equivalent: a float compare at `hit_min`, and a bounce change of exactly 0 | PR 28, "Review" | closed | equivalent: the same behaviour |
| 21 | Eight escapes were real gaps: the friction split, the friction limit, the bounce threshold between balls, the right wall's bounce sign, the ground rule's angle and rest test, a kick on a moving ball, and a press of exactly HOLD_MS | PR 28, "Review" | acted | a52f067 adds a test for each. A rerun of the eight caught seven, and a slanted-hit momentum test caught the last one |
| 22 | Lesson: a ball test that starts the lower ball first covers only one branch of a rule that depends on the index order. Run each pair rule in both orders | row 21 | raised | a lesson for the retro |
| 23 | The mutation run took 48 minutes for 28 rows, because `mutate.py --tests tests` runs the whole suite (2 to 2.4 min) for each row | the mutation run | raised | for P495 #677 (slow gates): let a table name its test modules |
