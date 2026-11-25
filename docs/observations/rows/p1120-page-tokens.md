# P1120 with P1123: the page's teal tokens, two button kinds and planes, and page.html as an ordered SECTIONS table: rows

Cards: [P1120 #1649](https://github.com/xmejkal/spark/issues/1649) and [P1123 #1653](https://github.com/xmejkal/spark/issues/1653).
The plan council: a lens on Sonnet (the everyday model, UX and AI-UX) and the refuter on Opus, two rounds, 2026-11-25.
Rows 1 to 24 are the council's, rows 25 to 32 the build's, rows 33 to 37 the review's. This file holds the acted, raised and rejected findings
only. 2026-11-25.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | in light, the confirm box on the NOW line takes the Now ink on a white surface (1.09:1) | council round 1, refuter | acted | `[role=group]{color:var(--ink)}`; the contrast test checks the rule and the pair |
| 2 | p1062 row 19's anchor has an 8-space indent; as a module function `_wiring_open` has a 4-space body | round 1, refuter | acted | commit 1 re-anchors p1062 rows 0, 1 and 19; `--anchors` refuses none |
| 3 | dark: the teal button on the Now plane is 2.7:1 against it, with a teal border, so it has no edge | round 1, lens and refuter | acted | `.now [data-makes-stale]>button` takes the `--now-halo` edge; the pair is in `EDGE_PAIRS` |
| 4 | `[data-makes-stale]>button:hover` outranks `button:disabled`, so a disabled button turns teal | round 1, lens and refuter | acted | the kind-1 rules hold `:not(:disabled)`; `test_no_accent_fill_reaches_a_disabled_button_or_cancel`; p1120-page-tokens row 7 |
| 5 | the teal test reads only the token name: `a{color:var(--focus)}` passes | round 1, refuter and lens | acted | the test takes every token whose value is teal in either theme and a closed list of (selector, property): `TEAL_ROLES` |
| 6 | two token regexes need `[a-z-]` | round 1, lens and refuter | acted | both read `--[a-z-]+`; one assertion checks `--radius-button` is read |
| 7 | Send and Cancel look the same, so the yes is not visible (D1) | round 1, lens | acted | Send, the confirm's first button, is kind 1; D1 is reversed. P1115 replaces both selectors |
| 8 | the contrast test misses four pairs | round 1, lens | acted | muted on line, ink on surface, the Now ink on the Now plane, and the confirm box are in `TEXT_PAIRS` |
| 9 | "ring" means the focus outline and the Now dot | round 1, lens | acted | the Now dot's ring is the halo (`--now-halo`); the ring is the focus outline only (patterns-and-names.md) |
| 10 | the class suffixes mix the table's meaning and the HTML element | round 1, lens | acted | the suffix names the element (Heading, Line, Section, Fold); patterns-and-names.md says so once |
| 11 | `SECTIONS` already names the finding headings in `core/renderers.py` | round 1, refuter | rejected | kept: the same meaning, the parts of a rendered output in order; the architect named it and the PO accepted it |
| 12 | a new line in the guide is not "one new section" | round 1, refuter | rejected | dropped because the guide is one part on the canvas: a new line in it is a change inside `GuideHtmlSection` |
| 13 | a section that returns "" drops silently; add a case per droppable section | round 1, lens | rejected | dropped because the golden holds the sections (but see row 25) |
| 14 | no card asks for `--space-*`, `--size-*`, `PLANES` or T14 | round 1, lens | rejected | P1123 asks for radius, size and space, P1120 for state planes with a mark and a word, and P1123 for each section's basis keys |
| 15 | small counts in the plan were wrong | round 1, refuter | acted | fixed in the plan's text |
| 16 | the Artifact's CSP for Google Fonts is unchecked | round 1, refuter | raised | dropped because a blocked font changes only the look: the system fonts take over |
| 17 | while Send shows, the offer button stays teal beside it | round 2, lens | acted | `[data-makes-stale]:has(>[role=group])>button` and its hover fall back to the outline; the disabled test checks it |
| 18 | "a button inside `.now`" reaches Send and Cancel: a halo edge on white is 1.48:1 | round 2, lens and refuter | acted | the selector is `.now [data-makes-stale]>button` |
| 19 | `a{color:var(--ink)}` beats the Now color, so the step link is ink on ink | round 2, refuter | acted | `.now a{color:var(--now-ink)}`; the contrast test checks the rule; p1120-page-tokens row 8 |
| 20 | the base kind-1 rule ties with `button:disabled` | round 2, lens | acted | the base and the hover rules hold `:not(:disabled)` |
| 21 | the teal test misses `--accent-hover` and `--now-halo` | round 2, refuter | acted | `TEAL_FAMILY` names the five tokens |
| 22 | dark: the confirm frame's teal edge is 2.74:1 on the Now plane | round 2, refuter | acted | `--accent-edge` is `#5eead4` in dark; the pair is in `EDGE_PAIRS` |
| 23 | the anchors hold only while `_now`, `_step_link`, `_stands_at`, `_guide` and `_parts` stay at their indent | round 2, refuter | acted | their bodies stay methods (8 spaces); `--anchors` refuses none |
| 24 | check once that the golden holds all ten sections | round 2, lens | acted | checked after commit 1: nine of ten (row 25) |
| 25 | the golden cannot hold all ten sections: the stands-at line shows only with no guide, and the sample has a guide | the build | raised | dropped because the refuter rendered all 238 pages of tests.test_flow_page before and after the move, stands-at included, byte for byte the same, and the stands-at line has its own test (`test_with_a_guide_the_stands_at_line_goes_and_without_one_it_stays`) |
| 26 | `TheInlinePictureTest.test_the_breadboard_is_inline_with_no_namespace_and_the_schematic_and_pcb_stay_img` forbids `http` in the whole page (`test_flow_page.py:978`), so the font link turns it red; the plan does not name it | the build | acted | the font commit, applied on spark-main's yes: the test keeps `xmlns` and `ns0:` on the whole page and checks `http` with `assert_only_the_font_is_loaded`, the page with the font link removed; p1120-page-tokens rows 12 to 14 |
| 27 | R1 caps a module at 600 raw lines; the plan's 480 counted code lines, and flow_page.py would reach 605 | the build | raised | the page's STYLE is repacked to 120 columns (the same bytes): 593 lines. Destination: P1128 #1659 |
| 28 | the amber and red tokens are unused until the planes, so the token test (defined equals used) fails in commit 2 | the build | acted | they join both themes in commit 4, with the planes |
| 29 | the plane class changes the developer heading line, p1062 row 3's anchor | the build | acted | row 3 is re-anchored on the new line, with the same name and test |
| 30 | the Round 2 fixes 3 and 4 have no row | the build | acted | p1120-page-tokens rows 7 and 8 |
| 31 | a circle (the Now dot, the pad swatch) has no radius token | the build | acted | the radius test allows `50%` beside the two radius tokens, as the plan's full text says |
| 32 | on the NOW box's NEXT line the confirm takes the line's 20px size, so its lines read large | the build's screenshots | acted | `[role=group]{font-size:var(--size-text)}`; `test_the_confirm_reads_at_the_text_size_wherever_it_stands`; p1120-page-tokens row 11 |
| 33 | five planted mutants pass TheLookTest and only the goldens catch them: the confirm-open rule before the teal rule, no ink on the confirm, `filter:drop-shadow`, `border-top-left-radius`, a muted NEXT line | the review | acted | fixed: the fallback is tested after the teal rule and the confirm's color and fill are pinned; the no-shadow test reads every property and value, the radius test every property with "radius", and a new test reads every rule that reaches the Now plane; p1120-page-tokens rows 15 to 20, each run by hand against its test (the ink one was already red in the contrast test) |
| 34 | the confirm-open fallback `[data-makes-stale]:has(>[role=group])>button` outranks `button:disabled`, so a disabled offer with the confirm open loses its disabled look | the review | acted | fixed: the fallback rules hold `:not(:disabled)`; `test_the_confirm_open_outline_never_styles_a_disabled_offer_and_stands_after_the_teal_rule`; p1120-page-tokens row 16 |
| 35 | a disabled offer on the Now plane keeps the halo edge | the review | rejected | dropped because the edge is needed for 3:1 against the dark plane (without it 1.18:1), the grey fill still says disabled, and the style's comment says so; the test checks the fill |
| 36 | the privacy sentence names only the IP address, and the font files come from fonts.gstatic.com | the review | acted | fixed: four places say the stylesheet's host, the font files' host, the IP address, the User-Agent, and the origin of a published page |
| 37 | the commit order differs from the plan's commit 3 | the review | rejected | dropped because the PR body names the plan's commit 3 |
