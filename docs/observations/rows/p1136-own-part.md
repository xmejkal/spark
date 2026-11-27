# P1136 PR A: a board's own part says so, and the Send box opens in view: rows

Card: [P1136 #1671](https://github.com/xmejkal/spark/issues/1671), PR A of two. The plan is in the store's
`plans/p1136-plan.md`, with the plan lens, two plan refuter rounds and the delegated council of three on Opus. This file
holds the raised, verified and acted findings of the build, the Chrome check and the PR review. 2026-11-27.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `docs/guide/agents/flow.md` stood at 402 lines against its budget of 400 on P1180's branch, so the hook's `test_docs` would fail | the build | acted | fixed on P1180 (two bullets rewrapped, no word changed), merged here. The docs tests ran 26 tests, OK |
| 2 | sample-page.json has no board offer for a button need, and adding one changes a test the plan does not name | the build | acted | the sample gets `"own_part": null` on each offer; the page row is pinned by the new `TheBoardsOwnPartOnThePageTest` |
| 3 | `test_flow_script` pins the node tests' pass count, and p1030-one-step.json row 5 anchors on `Phase.to_dict`'s offer line; neither is in the plan's lists | the build | acted | 31 to 32 (one new node test), and row 5 re-anchored. The PR refuter checked both |
| 4 | `own_part_of` takes `what[0]`, and `what` is sorted, so a board names its alphabetically first function for the verb: "its onboard 802.15.4 radio (Thread, Zigbee)" for a wifi need, "its joystick" for a button need | PR lens and PR refuter (Opus), reproduced with the library boards | acted | `own_part_of` takes the first `what` word that shares a word with the need (`matching.need_words`, as `needs.serving_roles` admits a board), else the first. The test board names "joystick" too, a direct test pins the fallback, and two mutation rows prove it. A refinement of the council's Q5 ("the first what word only"), within its intent of one word |
| 5 | the `is_on_picked_board` docstring and flow.md said the own part "plausibly serves" the need, but `is_plausible` judges the whole board | PR refuter (Opus) | acted | both say the board is a plausible pick for the need |
| 6 | flow.md no longer said that the text and the page join two picks with ", " | PR refuter (Opus) | acted | said again on the `needs` line, with no new line |
| 7 | the `✓ picked “…”` line of a need names the board alone, with no own part | PR refuter (Opus) | raised | card [P1308 #1880](https://github.com/xmejkal/spark/issues/1880) |
| 8 | with two compute needs that pick two boards, both boards' offers for a light say "The board you picked has one." | PR refuter (Opus) | rejected | a basic project has one board, and the parts list asks for one |
| 9 | the `is_plausible` clause of `is_on_picked_board` never changes the flow's output, since `need_picks` offers only plausible boards | PR refuter (Opus) | rejected | the plan keeps it as the guard for PR B's fold, which offers more; row 5 proves it by a direct call |
| 10 | the label quotes the own part inside the part's quotes, while `offers[].part` is the name alone | PR lens | rejected | the council's Q3 form; `part` stays a name by Q9 |
| 11 | `confirm`'s comment says the scroll has no motion, which holds only while the page sets no smooth scroll | PR lens | rejected | the page sets no `scroll-behavior` (PR refuter checked), so it holds |
| 12 | no mutation row for the `part_words` call in the page row | PR lens | rejected | row 7 drops OWN_PART in `part_words`, which the label and the page row both call, and names the page test |
| 13 | the canvas's "Your board" badge on the own-part card | the Chrome check | rejected | the council dropped the badge: it belongs with the canvas's cards, a later card |
| 14 | the canvas's fold of the other parts and its held parts as greyed cards | the Chrome check | raised | P1136 PR B, held by the PO's MVP-first direction of 27 Nov |
