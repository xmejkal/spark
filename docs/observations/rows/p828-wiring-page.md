# P828: page.html shows the wiring: rows

Card: [P828 #1186](https://github.com/xmejkal/spark/issues/1186), a story, step 1 in PR #1260. New logic: a plan check
on the strongest model, a plan council (one lens, the refuter), then one lens and the refuter on the PR. This file
holds the acted, raised and rejected findings only (rules.md). 2026-11-17.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the rule that shows one step at a time hid every list item of the section, the lines before power too | plan lens, plan refuter | acted | the rule is scoped to `ol#steps`; a test holds that no before-power item is inside it, and a print rule shows every step |
| 2 | turning the sheet's marks into HTML on a filled line reads a record's `2**8 or 2**9` as bold | plan refuter | acted | the HTML templates are made once from the sheet's templates, and the escaped fields go into them |
| 3 | a kept schematic of an earlier design survives a build that did not finish | plan refuter | acted | both kept pictures are removed where the page is removed |
| 4 | the page value held the breadboard area's types, so the mask skipped them without an error | plan lens | acted | `PageWiring` takes plain values, converted once in write_flow_page.py |
| 5 | a sixth parameter on `write_page` breaks the rule of five | plan lens | acted | one swap point, `parts`, gives `PageParts(pictures, wiring)` |
| 6 | a failure while a kept picture file is removed crashes the build | PR refuter, PR lens | acted | the failure is one "not kept" entry, and the build goes on |
| 7 | a failed write of a picture file blocks the page | PR refuter | acted | the files are written in their own guarded step, and the page is still written |
| 8 | a very deep circuit.json stops the page with a RecursionError | PR refuter | acted | `kept_wiring` catches every exception; a reason that is not the sheet's own is one fixed sentence |
| 9 | the fixed sentence pointed to a breadboard picture that was not drawn | PR refuter, PR lens | acted | the sentence and each step's "Picture" link appear only when the breadboard picture has an SVG |
| 10 | a keep folder that is no project also got the two picture files | PR refuter | acted | they are written and removed only in a project; a test holds it |
| 11 | the PO's D-b asks for "pictures and animated connections", and his D7 allows one inline script; this PR has neither | plan refuter | raised | card [P887 #1257](https://github.com/xmejkal/spark/issues/1257) |
| 12 | no read-only command gives the wiring steps as JSON | plan lens | raised | card [P888 #1258](https://github.com/xmejkal/spark/issues/1258) |
| 13 | the pin table that the PO liked is on no page | plan lens | raised | card [P889 #1259](https://github.com/xmejkal/spark/issues/1259) |
| 14 | the lines before power stand in the sheet's order, so an 833-character line buries the short ones | PR lens | raised | card [P890 #1261](https://github.com/xmejkal/spark/issues/1261) |
| 15 | after the requirements change, the page shows the old schematic with no note beside it | PR refuter | raised | a comment on [P880 #1248](https://github.com/xmejkal/spark/issues/1248) |
| 16 | the one-at-a-time rule and `:has()` ran in no browser | the builder, both reviews | raised | the PO: the bench checklist in PR #1260 and on #1186 |
| 17 | hand the before-power renderer in, so that the flow's renderer imports nothing of the breadboard area | plan lens | rejected | dropped because the PR lens found that the flow area already imports the breadboard area in three places, and a hand-in adds a parameter for no gain |
| 18 | the refusal's backticks show as plain characters on the page | PR lens | rejected | dropped because the words are the sheet's own, and the page keeps them as they are |

Step 2 (PR #1410, 2026-11-21): the page opens on the wiring and folds its phases, after the PO said at the bench that the
page "just doesn't guide a person". Plan check: a UX lens and the refuter (Opus). PR review: a lens (Sonnet) and the
refuter (Opus).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 19 | the guide's rule puts "now" at the build for p934, never at the wiring, and reads `unserved` as the person's choice | plan UX lens, plan refuter | raised | P977 #1407: its plan is rewritten and checked again before it is built |
| 20 | ship the page-only half first and the guide's facts after | plan UX lens | acted | this PR is the page-only half |
| 21 | a rail link scrolls to a closed fold and opens nothing | PR lens | acted | the rail's target is a div inside the details; Chrome opened the needs phase on a click |
| 22 | a page with no wiring steps folds away the only guidance | PR lens | acted | only a page with wiring steps folds its phases |
| 23 | the intro says "the build wrote a wiring sheet" when no breadboard.md exists | PR refuter | acted | WIRING_FIRST names no sheet |
| 24 | the guiding tests do not run when the test file runs alone | PR lens, PR refuter | acted | the class stands above the main block |
| 25 | the fixture test passes with the name said once per line | PR refuter | acted | it counts one name line per run of two or more |
| 26 | the rail lists Wiring and Pictures last while the page shows them first | PR refuter | acted | with wiring steps, the rail's links come first |
| 27 | two records of one short name join a run, and a run's name escape is untested | PR lens, PR refuter | acted | the run key holds the record, a test holds `A&B` |
| 28 | the firmware, simulate and deploy hints show placeholders a person cannot run | plan UX lens | raised | card [P979 #1411](https://github.com/xmejkal/spark/issues/1411) |
| 29 | a printed page shows a folded phase's heading only | PR lens, PR refuter | rejected | dropped because no use of a printed page is known, and the wiring steps print whole |
| 30 | a screen reader may drop the h2 role inside a summary | PR refuter | rejected | dropped because it is unverified here and HTML allows a heading in a summary |
