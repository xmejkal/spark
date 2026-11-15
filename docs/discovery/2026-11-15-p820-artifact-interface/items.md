# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. One block per item; copy the
block for more. needed by: the decider's words, quoted. value proven by: a proof the decider can read.
status: proposed, or filed D<n>.
e.g. `- needed by: "I want to know what we should build next" (Lena, 2026-10-06)` -->

The MVP cards below follow D5 and the approved plan ([mvp-plan.md](mvp-plan.md), D11). They replace the provisional blocks that predate D5, once numbered P823 to P831 (numbers now taken by other cards): the spike ran inside this discovery (D6, Results); the wiring-steps block is card 2; the TypeScript block folds into card 3a; P826 folds into card 3b and P306 #372; the legend and focus blocks fold into card 3a; the Pick and publish-routes blocks fold into card 4; the data-shapes block waits with P481 #660. All five are filed (D11).

## Card 1 — no reader says where a project stands in the flow → `flow.py show --json` answers each phase's status, facts and offers, and the build keeps its verdict in `.spark/build.json`
- type: story · size S · order 1 <!-- REQUIRED:item-type -->
- needed by: "start with an mvp with the flow, so both claude and I as a human can control it" (the PO, 2026-11-15, D5) <!-- REQUIRED:needed-by -->
- value proven by: on fixtures (no needs, picked, built, a could-not-run stage, requirements changed after the build) a test pins each phase's status and offers <!-- REQUIRED:value-proven-by -->
- depends on: — <!-- REQUIRED:depends-on -->
- status: filed D11 · P825 #1183 <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P820 #1173 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors <!-- REQUIRED:spark-process:slice -->

## Card 2 — the wiring steps and the "Before you power it" lines reach a page only as Markdown → both as data, beside `NumberedList` and `MermaidDiagram`
- type: task · size S · order 2
- needed by: "I love how you did the breadboard with the nice pictures and the step by step guide" (the PO, 2026-11-15, #1173)
- value proven by: a test pins the data equal to breadboard.md's numbered list and its "Before you power it" section on a fixture
- depends on: —
- status: filed D11 · P826 #1184
- label: task
- parent: P820 #1173
- slice: Views and editors

## Card 3a — the page shows three pictures and no flow → `page.html` shows the nine phases with a status word and glyph each, never a tick for a non-pass, readable from disk
- type: story · size M · order 3
- needed by: "the whole spark screens and the whole flow" (the PO, 2026-11-15, D5)
- value proven by: button-light's page, opened from disk, shows the nine phases, and a could-not-run stage is never a tick
- depends on: card 1; D7 (only the `<script` line of tests/test_tabbed_page.py retires)
- status: filed D11 · P827 #1185
- label: story, accessibility
- parent: P820 #1173
- slice: Views and editors

## Card 3b — the wiring guide the PO praised is typed by hand in each session → the page's breadboard and schematic views, and the wiring steps one at a time and all at once, before-power lines first
- type: story · size S · order 4
- needed by: "including the schema and breadboard" (the PO, 2026-11-15, D5)
- value proven by: the P100 walk wires from the page
- depends on: cards 2 and 3a; P306 #372 gets a comment with this card's words
- status: filed D11 · P828 #1186
- label: story
- parent: P820 #1173
- slice: Views and editors

## Card 4 — a click on the page reaches nothing → a confirmed click sends an offer's key; at the PO's next message Claude checks it with `flow.py run-request`, runs it, answers the row and republishes
- type: story · size M · order 5
- needed by: "so both claude and I as a human can control it" (the PO, 2026-11-15, D5)
- value proven by: on button-light, after /spark:idea writes its needs, the PO clicks Pick, then Requirements, then Build, each after the page shows the last result; `needs.json` holds the pick, `.spark/build.json` the build, and the page shows the build's own status
- depends on: card 3a; D8, D9, D10
- status: filed D11 · P829 #1187
- label: story
- parent: P820 #1173
- slice: Views and editors

## Existing cards the lenses map (not re-filed)
Each keeps its own title, parent and slice on the board; the line says its role here.

- P481 #660 (descriptions once, as data): steps 1 and 2 (`summary`, `details`) before the generated shell, OQ4 b; its MCP step waits for OQ2 c · council/feasibility.md:32 (FE-19) · status: existing, not re-filed
- P804 #1138 (the build and check_all as Operations): before the build half of the page, OQ6 c; it moves the keep step in scripts/spark/build/kept_files.py that the old wiring-page block changes (Q33), and it would change the build's `--json` keys agents read · council/feasibility.md:26 (FE-13); refuter.md part 0 · status: existing, not re-filed
- P200 #153 (one inventory of capabilities): the page's step list could be its first reader; it blocks no MVP · council/feasibility.md:60 (FE-35, step 4) · status: existing, not re-filed
- P417 #545 (LookAtBoard as a LangGraph node and an MCP tool): its MCP half only if Q9 keeps an MCP route · council/feasibility.md:12 (FE-2) · status: existing, not re-filed
- P788 #1094 (a Project Adapter): not needed by OQ2 a or b, because Claude runs the CLI on the Mac · council/feasibility.md:60 (FE-35, step 6) · status: existing, not re-filed
- P217 #199 (spark from Claude chat with artifacts): overlaps this epic; fold or keep, Q20 · council/existing.md:21 (EX-13) · status: existing, not re-filed
- P494 #674 (spike: which interface first): overlaps this discovery; fold or keep, Q20; its "Done when" names #152, #304, #372 and #601 as the cards that claim the page · council/risks.md:16 (RI-10); #674 · status: existing, not re-filed
- P306 #372 (one page to wire from, republished as an Artifact): it already holds the old wiring-page block's job, the picture, the steps and the "before power" lines, republished after each build; proposed: the old wiring-page block folds into it (see the old wiring-page block's block), Q20 · `gh issue view 372`, read 2026-11-15; council/risks.md:16 (RI-10) · status: existing, not re-filed
- P199 #152 (one front end for spark: a live page that walks you through): the widest claim on the page; fold or keep, Q20 · `gh issue view 152`, read 2026-11-15 · status: existing, not re-filed
- P449 #601 (the board tab and shapes.py: one viewer tab and one CLI for a part's shape): a later tab on the same page, Q20 · `gh issue view 601`, read 2026-11-15 · status: existing, not re-filed
- P269 #304 (views and editors): one TypeScript stack decision with this epic, Q20 · council/risks.md:17 (RI-11) · status: existing, not re-filed
- P493 #673 (a Walk tab on page.html): a later step section on the same page, Q20 · council/risks.md:16 (RI-10) · status: existing, not re-filed
- P668 #896 (the sheet knows no cable; `pins.py` names a shared pin's second job): it already holds P581's TFT_BL and ONBOARD_LED on GPIO21 (council/physics.md:25, PH-10; spark-walks/p581-sound-joystick/firmware/pins.py:9, :20; p581-rows.md row 4, read 2026-11-15), so no new bug card · status: existing, not re-filed
- P100 #6 (the walk to a lit LED) and P711 #960 (the walk after the refactor): the bar this epic must serve; their order against the build slices is Q21 · council/risks.md:7 (RI-1), :21 (RI-15) · status: existing, not re-filed

## Board actions
<!-- Each action, taken or pending, with its D. e.g. `- move the item to Discovery · pending` -->
- file cards 1, 2, 3a, 3b and 4 as sub-issues of P820 #1173, with their labels and the Slice; a comment on P306 #372 with card 3b's words · taken D11: P825 #1183 to P829 #1187; the comment on #372 is posted <!-- REQUIRED:board-actions -->
- run `tools/check_backlog.py` after the filing · taken: "313 open, the limits hold", after P826 to P829 moved to Idea
