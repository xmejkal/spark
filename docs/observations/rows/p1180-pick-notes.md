# P1180: a pick's notes stand by the pick: rows

Card: [P1180 #1722](https://github.com/xmejkal/spark/issues/1722). The plan is in the store's `plans/p1180-plan.md`,
with the delegated council of three on Opus and the round-2 refuter. This file holds the raised, verified and acted
findings of the build, the Chrome check and the PR review. 2026-11-27.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | in a Send of several picks, a note that two chosen picks share moves into the shared lines once, and "it" then names no pick | plan refuter, round 2 (Opus) | acted | `confirmPicks` keeps a pick's notes out of the shared count. The node test "a note two chosen picks share stays on each pick's line" and a mutation row pin it |
| 2 | every offered row of one need can carry the same note, so the note tells no row apart | plan refuter, round 1, and the Chrome check | raised | seen in Chrome: the three drawer boards of the board need all say "Spark cannot build from it: no board file." Also two `wet` picks of the test fixture. Card [P1295 #1863](https://github.com/xmejkal/spark/issues/1863) |
| 3 | the plan's mutation row 3 (`blocking_facts` keeps `body_mm`) and row 10 (`_hooked` writes no note) are the same mutations as p97-council row 5 and p1135 row 11 once those are re-anchored | the build | acted | neither is written twice. p1180-pick-notes.json holds 14 rows, among them two the plan did not list: a pick's words leave out its notes, and row 1's fix |
| 4 | the node test's fake element had no `id` property, which the DOM has, so the radio's `aria-describedby` read `undefined` | the build | acted | the fake reads and writes `id` through its `id` attribute, as the DOM does. All 31 node tests pass |
| 5 | `test_flow_script` pins the node tests' pass count | the build | acted | 29 to 31: the plan expected one more test, and row 1's fix adds a second |
| 6 | the canvas's fit, onboard and held notes, its cards with badges, and its held parts as greyed cards are not on the page | the Chrome check | raised | P1136 #1671's, the next card of the page lane |
| 7 | a pick that is the NOW line's offer leaves the parts fold, so its notes showed only in its Send box and the closed developer fold, not by the pick | PR refuter (Opus), reproduced with a scratch store | acted | `GuideHtmlSection._now` writes the offer's notes under NEXT with `_note_line`, which the fold's row also uses. A test pins it, and a mutation row proves it. P1135's board-file line had the same gap |
| 8 | `docs/guide/agents/flow.md` and `GLOSSARY.md` still said the fingerprint hashes each offer's "key, effect and makes_stale" | PR lens and PR refuter (Opus) | acted | both say "and a pick's notes when it has some", and that an unsure entry or a store record changes a pick's notes |
| 9 | no mutation row made the owed note or the simulation note never fire, or dropped the notes from the developer fold | PR lens and PR refuter (Opus) | acted | three rows in p1180-pick-notes.json, and a fourth for row 7. p1135 row 11 is re-anchored on `_note_line`. `tools/mutate.py --anchors`: 5415 mutations, every anchor present, once |
| 10 | flow.md did not say a pick radio's `aria-describedby="note-KEY"`, and said a shared line stands once, which is untrue for a note | PR lens and PR refuter (Opus) | acted | flow.md says both |
| 11 | the developer fold's notes were in neither flow.md nor the `flow.py page --help` | PR lens (Opus) | acted | both say them |
| 12 | `commands/page.md` read "with what to know of each, with one Send" | PR lens (Opus) | acted | "and what to know of each, with one Send" |
