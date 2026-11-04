# P595 the fire: rows

What the plans, the reviews, the mutation run and the PO's three looks found. Card: [P595 #796](https://github.com/xmejkal/spark/issues/796), under
[P594 #795](https://github.com/xmejkal/spark/issues/795). PR: https://github.com/xmejkal/pixel-games/pull/16. Numbers are in pixel-games `bench.md`, section "P595 (#796)" and its parts 2 and 3.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The plan's sky of the picture mode never loaded | PR 16, "Review"; [card comment](https://github.com/xmejkal/spark/issues/796#issuecomment-6605635147) | acted | fixed in the plan before code |
| 2 | A seed of the wrong type leaked the field (the one MUST of part 1) | PR 16, "Review" | acted | fixed, with a test |
| 3 | A runaway on some seeds: a cell outgrew its source | PR 16, "Review" | acted | the cap and the fade. A Mac test keeps seven seeds' top rows under a mean of 48 over 5,000 steps |
| 4 | The right edge of the embers and gusts that stopped short of positive targets were untested | PR 16, "Review" | acted | tests added |
| 5 | Mutation run: 11 planted, 10 caught. The escape, the gust easing, was real | PR 16, "Review" | acted | a new test catches it (41 tests) |
| 6 | Path A (C fills a buffer, Python blits it) costs 15.0 ms against B's 7.7 ms and misses A2 by 0.3 ms of room | bench.md P595 | acted | A dropped (D7, e968acd). The fire swaps B and the sky variant |
| 7 | The fire looked uniform; it rose at one speed; three columns rose together because the 64 cell cooling map repeated over 160 cells | [comment](https://github.com/xmejkal/spark/issues/796#issuecomment-6606083283), [comment](https://github.com/xmejkal/spark/issues/796#issuecomment-6606642373), [comment](https://github.com/xmejkal/spark/issues/796#issuecomment-6607056146) | acted | parts 2 and 3: hot spots, tongues, sway, fast patches, gusts, embers, and a 256 x 32 map |
| 8 | On the sky the colours are weird: gfx.c565 keeps the panel's byte order and s3lcd's blend reads normal order | [comment](https://github.com/xmejkal/spark/issues/796#issuecomment-6608714995) | acted | filed as P603 #804. A3's cost number stays valid, its colours did not |
| 9 | The two-mode cycle after path A was dropped was not timed on the board | bench.md P595 | raised | its picture path was timed, and a Mac test covers the tap. Low risk |
| 10 | Road printed 13 fps in one interval, 21 in the P593 smoke run | bench.md P595 | raised | one interval only, not followed up |
| 11 | The PO's fixed question (D2) was not answered in its words; the merge read A1 as passed on the third look | [comment](https://github.com/xmejkal/spark/issues/796#issuecomment-6608714995) | closed | merged on "never mind, merged ... lets move on" |
