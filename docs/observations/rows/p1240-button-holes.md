# P1240: the 6x6 button's holes across the centre gap: rows

Card: [P1240 #1796](https://github.com/xmejkal/spark/issues/1796). The PO, 2026-11-26: "the tactile button is way
smaller. This is all wrong proportionally. Make sure it fits." The plan was written by the plan-writer (Opus), checked
by a lens (Sonnet) and the refuter (Opus), and given its yes by the delegated council (tech lead, architect, PO
assistant, Opus), delegated and the PO's to change. This file holds the acted, raised and rejected findings only.
2026-11-27.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `tests/data/breadboard/button-light/breadboard.expected.md` pins the old holes, and the plan missed it | plan lens (Sonnet) | acted | accepted with the FireBeetle golden: step 2 reads "e30, e32, f30, f32" |
| 2 | a record with `body_mm` that the sheet does not draw must not pass in silence | plan lens | acted | `UNDRAWN_BODIES` in `tests/test_breadboard_layout.py` names six records with their reason, and any other undrawn record fails `TheBodySpanTest` |
| 3 | the new pictogram must pass the pictogram checks | plan lens | acted | `data/pictograms/wokwi-pushbutton-6mm.svg` passes `ThePictogramsTest` and the flow page's pictogram tests |
| 4 | "span" already names a text range of holes (`StepHoles._span`) | plan lens | acted | the test's helper is `hole_extent_mm` |
| 5 | option (a) only moves the holes into data, while the synthesis line says "from the part's own record (body_mm, legs, footprint)" | plan lens, refuter | rejected | delegated council D1: the record names its Wokwi part, so no code names this part, and `TheBodySpanTest` checks the holes against `body_mm`. Option (b) is new logic and would leave the Wokwi diagram and the simulation on the 12 mm part |
| 6 | the turn centre of `wokwi-pushbutton-6mm` is in no source | plan-writer, refuter | acted | measured in the Wokwi editor on 2026-11-27: (14, 13). `docs/discovery/2026-10-16-p267-wokwi-holes/README.md`, last two sections, with the diagram, its sha256 and two screenshots |
| 7 | the hash comment said the P267 screenshot shows "exactly these bytes", which P953 already made untrue | refuter | acted | the comment now names `button-light-xiao-6mm.png`, which shows the new bytes in Wokwi |
| 8 | the holes do not depend on the centre only for an error under one pitch | refuter | acted | the measured centre is used, so no error is left to bound |
| 9 | `stand_in` as "Wokwi's 6 mm pushbutton" (delegated D3) | the build | rejected | the longer text pushed each need past half of the 3400-byte page, and a page held one need, not two (`tests/test_needs.py`, "6 != 3"). `stand_in` keeps "Wokwi's pushbutton" |
| 10 | the 12 mm part measured (33.5, 24) on 2026-11-27, 0.5 px from the stored (33.5, 24.5) | step 1 in Chrome | dropped | inside the 1.5 px tolerance, and no hole changes. The README records both values |
| 11 | in Chrome, the D10 jumper crosses the gap to a14, and the button's ground runs from a12 to the bottom rail. The canvas's BbDiagram uses j14 and a top rail | step 6 in Chrome | raised | the layout core's jumper choice, not this card: a comment on P1241 [#1797](https://github.com/xmejkal/spark/issues/1797), which already moves each jumper to the nearest free hole |
| 12 | the PR must say that it does less than the synthesis line ("holes from the part's own record") | PR lens (Sonnet) | acted | the PR body names D1 and row 5, as the PO's to change |
| 13 | no test pins the 6 mm part's measured turn | PR lens | acted | `test_the_6_mm_button_turns_about_the_center_wokwi_showed` pins the four turned pins read in Wokwi |
| 14 | `UNDRAWN_BODIES` was compared by its names only, so a record undrawn for another reason passed | PR lens | acted | one constant `NO_ROAD` is the reason `drawn_parts` gives, and the test compares the whole mapping |
| 15 | the test's own `PX_PER_MM` repeats `part_shape.PX_PER_MM` | PR lens | acted | kept on purpose: its comment now says why (the test does not take the number from the code it checks, and the vocabulary test refuses that read) |
| 16 | the `//size` note's 6 mm sentence read as if P267's refuter read it | PR lens | acted | the sentence now follows that line and names its own source and date |
| 17 | the FireBeetle picture's hash says "seen in Chrome", with no record of the look | PR lens | rejected | the session opened both pictures, the XIAO and the FireBeetle, in Chrome on 2026-11-27 and took a screenshot of each. The screenshots stay out of the tree, as the plan's step 6 says |
| 18 | no mutation row hits `LEG_REACH_MM` or `UNDRAWN_BODIES` | PR lens | dropped | both are test constants. The rows mutate the data under test, and each row fails `TheBodySpanTest` (the refuter planted both by hand) |
| 19 | `tests/test_journey_basic.py:97` was skipped where littlefs is missing | PR refuter (Opus) | acted | run with the pyenv Python 3.10, which has littlefs. The PR quotes its output |
| 20 | in the rebuild golden, the button's caption sits on the top - rail line (y 25.25 against the line at 26.14) | PR refuter | raised | the caption placement is existing logic, and the narrower body gave it this place. P1274 [#1834](https://github.com/xmejkal/spark/issues/1834) |
| 21 | the README said "all four turned pins agree" but listed one pin | PR refuter | acted | the table lists all four turned pins of both parts |
