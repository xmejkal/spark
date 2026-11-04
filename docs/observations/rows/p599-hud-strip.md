# P599 the HUD strip: rows

What the plan, the review, the mutation run and the board probes found. Card: [P599 #800](https://github.com/xmejkal/spark/issues/800). PR: https://github.com/xmejkal/pixel-games/pull/17.
Numbers are in pixel-games `bench.md`, section "P599 (#800)".

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The refuter's 2 MUSTs: a heap claim with no source, and a test that passed only through another test's state | PR 17, "Checks" | acted | both fixed in 9238d7a |
| 2 | Mutation run: 22 planted, 20 caught. The escapes were a `HUD_RECT` height of 15 and a fire key without its name | PR 17, "Checks" | acted | two tests in the last commit catch both |
| 3 | The rain misses the card's 1 ms line (1.7 to 2.5 ms): its label changes every 500 ms and each redraw costs 24 to 28 ms in one frame | bench.md P599; [comment](https://github.com/xmejkal/spark/issues/800#issuecomment-6610903251) | raised | the card is partly met. The rain's slowest frame grew from 45 to 46 ms to 57 to 64 ms |
| 4 | After the strip, the rain's own draw got 2.5 to 6 ms slower and the game-over box about 4 ms. Nine probes show the strip's redraw is the trigger, not why | PR 17, bench.md P599 | raised | filed as spike P604 [#805](https://github.com/xmejkal/spark/issues/805) on the PO's yes ([comment](https://github.com/xmejkal/spark/issues/800#issuecomment-6611517109)). bench.md lists what the probes ruled out |
| 5 | The rain's draw repeats with a period of 5 frames, the same as `GC_FRAMES`, but the phase against a collection is inferred and master was not traced | bench.md P599 (probe E13) | raised | goes to P604 |
| 6 | The refuter expected the HUD at 0.5 to 0.7 ms; flappy and runner gave 0.8 to 0.9 ms | bench.md P599 | closed | still under the card's 1 ms |
| 7 | Nobody looked at the panel in the board run | PR 17, "Checks" | closed | the PO looked on 2026-11-03: "Yeah, hdu is ok" ([comment](https://github.com/xmejkal/spark/issues/800#issuecomment-6611480992)) |
