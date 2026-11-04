# P593 the rain: rows

What the build, the board run and the review of the first demo scene found. Card: [P593 #794](https://github.com/xmejkal/spark/issues/794), under the engine
epic P586 #787. PR: https://github.com/xmejkal/pixel-games/pull/14. Numbers are in pixel-games `bench.md`, section "P593 (#794)".

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The plan's two rounds brought the read-back cost, the 60 ms dt clamp and the HUD cost into the plan | PR 14, "Council and review" | acted | all three are in the plan and the code |
| 2 | The claim "drawing costs the same in both modes" was wrong: Python mode draws 2 to 4 times slower | PR 14, review fixes in ffc7d9a | acted | claim removed, log ranges widened |
| 3 | The C world outlives a soft reset, so a run at N = 192 followed by N = 160 raised `ValueError: an array('h') of 3n ints is needed`. Only the board showed it | PR 14, bench.md P593 | acted | fixed in 5b72b20: the rain loads exactly N bodies first. A Mac test pins it |
| 4 | The HUD text costs 10.6 to 10.9 ms a frame in C mode, more than the plan's guess of 3 to 8 ms. That is why 192 boxes missed 24 fps | bench.md P593 | acted | N became 160. The cost became P599, the HUD strip |
| 5 | Python mode's heap allocation is 200 to 487 kB against 99 kB, which points at gc, and its draw grows over the first 20 s | bench.md P593 | raised | the cause was not looked for |
| 6 | Free internal RAM at start was not measured: the logs hold only the total with PSRAM | bench.md P593, PR 14 | raised | marked "not measured" after the review. The next scene to hold a field in internal RAM measured it (P595, A9) |
| 7 | Three games needed 16 s instead of 9 s to print their first fps line; the first `mpremote run` after a `cp` prints nothing | bench.md P593 | raised | harmless, a second run works. Known since 2026-11-01 |
| 8 | The review (Sonnet reviewer, Fable refuter) found no MUST | [card comment](https://github.com/xmejkal/spark/issues/794#issuecomment-6602316001) | verified | the PO played it ("nice. Alright, I really like it") and merged |
