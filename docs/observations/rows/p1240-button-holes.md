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
| 11 | in Chrome, the D10 jumper crosses the gap to a14 and the button's ground runs from a12 to the bottom rail; the canvas's BbDiagram uses j14 and a top rail | step 6 in Chrome | raised | the layout core's jumper choice, not this card: a comment on P1241 [#1797](https://github.com/xmejkal/spark/issues/1797), which already moves each jumper to the nearest free hole |
