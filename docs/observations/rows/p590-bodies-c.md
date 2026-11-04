# P590 bodies in C: rows

What the plan, the review, the mutation run, the board and the PO's look found. Card: [P590 #791](https://github.com/xmejkal/spark/issues/791).
PR: https://github.com/xmejkal/pixel-games/pull/22, with the follow-up https://github.com/xmejkal/pixel-games/pull/23. Numbers are in pixel-games `bench.md`, section "P590 (#791)".

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The plan went through two refuter rounds (Fable) with no MUST | [comment](https://github.com/xmejkal/spark/issues/791#issuecomment-6629331682) | verified | the plan went to build as it stood |
| 2 | The Sonnet reviewer found no MUST and six NITs | PR 22, "Review" | acted | three NITs fixed, the other three not |
| 3 | The Fable refuter found no MUST and two SHOULDs: no test pinned the rest speed or the friction | PR 22, "Review" | acted | fixed in d21cc76 with tests on both sides |
| 4 | The refuter confirmed the memory layout under ASan and UBSan for caps 1 to 256, the 0 B claim, and every bench number against the logs | PR 22, "Review" | verified | no change |
| 5 | The mutation run planted 17 defects and the tests caught 16 | PR 22, "Review" | verified | counted as this PR's mutation run |
| 6 | The escape was real: `Stepper.step` could skip the call on 0 steps and drain the last frame's hit twice | PR 22, "Review" | acted | closed by a test on both sides in e513cec, which fails on that defect |
| 7 | Rain in C ran at 24 to 25 fps, with a step of 0.21 to 0.23 ms. Rain in Python ran at 8 to 9 fps | PR 22, "On the board"; bench.md P590 | verified | P593 had 24 fps and 0.16 to 0.17 ms in C. The C step rose by about 0.05 ms, because the world moved from static RAM into the GC heap in PSRAM. That cause is calculated, not measured |
| 8 | The burning scene with flares ran at 24 to 25 fps | PR 22, "On the board"; bench.md P590 | verified | P596 had 24 to 25 fps. The step rose by 0.2 to 0.3 ms for the drain and the flares |
| 9 | Step, read and drain allocated 0 B each over 100 calls | PR 22, "On the board"; bench.md P590 | verified | the gate passes. Three bodies that hit at 900 to 1,100 px/s each reported `SLEEP` once at rest |
| 10 | The PR first quoted the PO's "flames look good" on the flare. He said it about the Fire scene, before he saw the flare. His words on the flare were "Oh, nice!!!" | [comment](https://github.com/xmejkal/spark/issues/791#issuecomment-6631309048) | acted | fixed by https://github.com/xmejkal/pixel-games/pull/23. Lesson: ask which scene the board shows before you quote the PO's look |
| 11 | A feel slice stops at "ready to play" until the PO plays it | [comment](https://github.com/xmejkal/spark/issues/791#issuecomment-6629994444) | closed | the PO played it and wrote "I love it, lets add it to the games". PR 22 merged on 2026-11-04 |
