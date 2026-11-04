# P603 the blend: rows

What the plans, the reviews, the mutation runs and the PO's look found, over two PRs. Card: [P603 #804](https://github.com/xmejkal/spark/issues/804).
PRs: https://github.com/xmejkal/pixel-games/pull/18 (part 1, byte order) and https://github.com/xmejkal/pixel-games/pull/19 (part 2, alpha follows heat). Numbers are in pixel-games `bench.md`,
section "P603 (#804)" and its part 2.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | Part 1 review: the swap macro's parentheses, a sentence in lcd.py, and the unused `bitmap` path needed a "Later" comment | PR 18, "Checks" | acted | fixed in 5d4aa25 |
| 2 | Part 1 mutation run: 10 planted, 9 caught. The escape, the swap macro without its `& 0xFFFF`, is an equivalent mutant: every use stores into a `uint16_t` | PR 18, "Checks" | rejected | no input shows a difference, so no test is written |
| 3 | The s3lcd bitmap, PNG and font-draw paths mix byte orders, and no game calls them | [comment](https://github.com/xmejkal/spark/issues/804#issuecomment-6624724847) | raised | later. Fix the byte order when a game first calls one of them |
| 4 | Three worst frames of part 1's board run were longer (81 to 132 ms against 80 to 94 ms), in one run each | PR 18, bench.md P603 | raised | the cause was not looked for. Part 2 cut the paint to 6.9 to 8.5 ms and its worst frame to 68 to 84 ms |
| 5 | A blend can only mix, so at half alpha the dark edge cells darkened the sky, and mid heats dim a light sky | PR 19; [comment](https://github.com/xmejkal/spark/issues/804#issuecomment-6624602480) | acted | the PO picked curve B from four Mac renders: clear at heat 0, full alpha from heat 96 (`ALPHA_FULL`), c95e739 with a test |
| 6 | Part 2 plan check: 3 MUSTs | PR 19, "Checks" | acted | in the plan and the first commit |
| 7 | Part 2 refuter planted a wrong map, a wrong alpha index and a wrong skip; the tests caught each. Three stale comments | PR 19, "Checks" | acted | comments fixed in eddf6b7 |
| 8 | Part 2 mutation run: 12 planted, 9 caught. One escape is equivalent (the skip at alpha 0, the blend returns the sky there). Two were the alpha table | PR 19, "Checks" | acted | a new test pins the table and fails on both (cbf3f4b). The equivalent one is rejected |
| 9 | The binding's argument checks have no Mac test | PR 19, "Checks" | acted | a board probe called `draw` with nine argument sets, all as expected. A Mac test cannot load the C module |
| 10 | The PO's look at part 1 on the panel: "the sides of the flame are weird, cause they are dark" | PR 19 | acted | rows 5 and 8 |
