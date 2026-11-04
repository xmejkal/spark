# P589 the engine probe: rows

What the probe session, its two plan rounds and its review found. Card: [P589 #790](https://github.com/xmejkal/spark/issues/790). PR: https://github.com/xmejkal/pixel-games/pull/13. Numbers are in
pixel-games `bench.md`, section "P589 (#790)".

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The plan had 2 MUSTs in round 1 and 1 MUST in round 2 | [card comment](https://github.com/xmejkal/spark/issues/790#issuecomment-6600835216) | acted | all fixed in the plan before code |
| 2 | The review (Sonnet reviewer, Fable refuter) found no MUST | [card comment](https://github.com/xmejkal/spark/issues/790#issuecomment-6601134094), PR 13 | verified | the PR merged |
| 3 | A3 (a rigid step under 2 ms) has a lower bound only, because the probe scene has no contacts and no rotation | bench.md P589 | raised | A3 stays open. P598 (bodies that touch) is the card that can close it |
| 4 | The fixed-point step is 1.56 times slower than float (0.211 against 0.135 us per body-step) | bench.md P589 | verified | float stays. PIE SIMD was not measured, so the row is only the base for that path |
| 5 | Reading 12 values back from C costs more than 12 Python list reads (60.03 against 32.35 us) | bench.md P589 | verified | a design that sends every body back each frame pays for the read, not the step. The rain (P593) reads once per frame and draws the cost |
| 6 | The drain of 16 events costs 162.5 us, and that the Python loop is most of it is calculated from the 2.60 us call, not measured | bench.md P589 | raised | not measured. Open until a card needs the drain (P590) |
| 7 | An incremental `./build.sh s3lcd` gave sha256 9c22d6b6f3951c99, not the sha of the image built a day before in the same folder, at the same size | bench.md P589 | raised | the cause was not looked for. Builds are not byte-for-byte repeatable here, so a sha in a log names one build only |
| 8 | The 5.34 us C-to-Python call settles the PO-29 disagreement: the 5.5 us stand-in held, the 20 to 60 us estimate was high | bench.md P589 | closed | A2 passes |
| 9 | Q-U5 (how long the PO waited per build before) was still open at the merge | [card comment](https://github.com/xmejkal/spark/issues/790#issuecomment-6601433269) | raised | waits on the PO |
