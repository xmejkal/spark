# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. One block per item; copy the
block for more. needed by: the decider's words, quoted. value proven by: a proof the decider can read.
status: proposed, or filed D<n>.
e.g. `- needed by: "I want to know what we should build next" (Lena, 2026-10-06)` -->
Nothing here is filed. The numbers are provisional: the highest P on 2026-11-15 is P822 (#1175); read the highest again just before filing. The labels are the repository's (spike, story, task, chore, bug, accessibility). The Slice is the board's "Views and editors" unless a block says otherwise. The order is the synthesis's proposal, after the tech lead's (council/feasibility.md:60, FE-35); it depends on Q1 and the direction. Size: S is a day or less, M a few days (H, the synthesis's estimate). The PO's words for every new card, from #1173: "I'd basically just want to standardize this along with all the other steps in the artifact too, so that spark can be fully used from claude uaing the artifact output" (the PO, 2026-11-15); a block quotes a narrower part where one fits.

## P823 (provisional) — Spike: whether a click on an Artifact page reaches Claude Code is untested → a throwaway page settles the `db` round trip, rows across a republish, both publish routes, `files` for a local project, and a click made with no session open
- type: spike · size S (about an hour, council/risks.md:27) · order 1 <!-- REQUIRED:item-type -->
- needed by: "I wonder how we can also then allw sers to use the chat when working with the artifact" (the PO, 2026-11-15, #1173) <!-- REQUIRED:needed-by -->
- value proven by: a Results row in risks-and-tests.md for steps 1 to 7 of the spike, against the pass lines dated 2026-11-15 (A1, A2, A8, A11) <!-- REQUIRED:value-proven-by -->
- depends on: Q1 (the pass lines) and Q4 (the PO's yes to publish a throwaway page); Q32 adds a `room` step if the PO wants it <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): spike <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P820 #1173 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): Views and editors <!-- REQUIRED:spark-process:slice -->

## P824 (provisional) — the wiring steps and the "Before you power it" lines reach a page only as Markdown → a JSON renderer of `BreadboardSteps` beside `NumberedList` and `MermaidDiagram`, the before-power lines exported as data too, and the page writer embeds both
- type: task (a refactoring) · size S · order 2
- needed by: "I love how you did the breadboard with the nice pictures and the step by step guide" (the PO, 2026-11-15, #1173)
- value proven by: a test pins the JSON steps equal to breadboard.md's numbered list, and the JSON before-power lines equal to its "Before you power it" section, on a fixture build; button-light's page.html holds both
- depends on: — (council/feasibility.md:27, FE-14: no change to the wiring logic). The before-power lines are not in the steps: they come from `sheet._before_power` (E scripts/spark/breadboard/sheet.py:195, :361), so this card exports them as well, because P826 promises them (★C3, refuter.md part 1)
- status: proposed
- label: task
- parent: P820 #1173
- slice: Views and editors

## P825 (provisional) — a second TypeScript package has no folder in the story run, no `node_modules` loan and no wrapper test → the page's TypeScript builds into one file with a pinned sources hash, and the hook tests it
- type: chore · size S · order 3
- needed by: "I would also like to really make the html page output witht typescript ointerface work" (the PO, 2026-11-15, #1173)
- value proven by: the hook's output on the commit that adds the package names its test; the built file is under the size the PO sets at Q1 (A6)
- depends on: OQ4's direction; P269 #304's stack question (Q20); Q29, because a script in `page.html` fails tests/test_tabbed_page.py:53-56 (`assertNotIn("<script", page)`) and makes commands/build.md:160 ("It has no script and loads nothing from the web") untrue (E, re-read 2026-11-15)
- status: proposed
- label: chore
- parent: P820 #1173
- slice: Views and editors

## P826 (provisional) — the step-by-step wiring page the PO praised is typed by hand in each session → spark's page.html shows each wiring step one at a time and all at once, with the picture and "Before you power it" first, and works with no Claude
- proposal (the facilitator's, from refuter.md ★C17; Q20 decides): fold P826 into P306 #372 (OPEN, "The person opens three files to wire → one page to wire from, republished as an Artifact"), whose value line already holds this job: "The page holds the picture, the parts with 'you have', the steps, the changes and the 'before power' lines; Claude republishes it after each build" (E `gh issue view 372`, read 2026-11-15). P826's narrower words (one step at a time, works with no Claude, generated from the records) go to #372 as a comment, and no new card is filed. If the PO keeps P306 for a static page, P826 is filed as its successor with P306 as its dependency
- type: story · size M · order 4 (the MVP's floor, OQ5 a)
- needed by: "I love how you did the breadboard with the nice pictures and the step by step guide, so I'd basically just want to standardize this" (the PO, 2026-11-15, #1173)
- value proven by: button-light's page.html, opened from disk with no Claude, shows every numbered step and every before-power line; the P100 walk wires from it
- depends on: P824 (the steps and the before-power lines as data), P825; Q2 (which page is the template); Q20 (fold into P306 #372); Q29: the one-step mode needs a script, which fails tests/test_tabbed_page.py:53-56 and makes commands/build.md:160 untrue, so that guarantee is retired on purpose or the scripted page is a second file; Q33: it changes scripts/spark/build/kept_files.py:259-272, the keep step P804 #1138 moves
- status: proposed
- label: story
- parent: P820 #1173
- slice: Views and editors

## P827 (provisional) — a could-not-run, a skipped and a null show as nothing or as a tick on a page → one legend, a word and a glyph per state and never color alone, rendered from the core's codes on every step
- type: story · size S · order 5
- needed by: "so that spark can be fully used from claude uaing the artifact output" (the PO, 2026-11-15, #1173), under AGENTS.md's "A could-not-run or a skipped is not a pass"
- value proven by: a fixture build with a could-not-run stage and a null fact; a test pins that neither is drawn as a tick; the PO names 6 of 6 states (A7; which six of the legend's eleven marks is Q22)
- depends on: P826; Q22
- status: proposed
- label: story (and accessibility)
- parent: P820 #1173
- slice: Views and editors

## P828 (provisional) — a pick on the page reaches Claude only through the person's words → a Pick on a need card writes a request in the shape of a `next` step (or copies it for the chat), and Claude runs it at its next turn
- type: story · size M · order 6 (the MVP's click, OQ5 b)
- needed by: "that it would also have this clickable functioning interface for people to use it and also claude" (the PO, 2026-11-15, #1173)
- value proven by: the `db` row, the chat transcript, and `needs.json` holding the pick on button-light (the brief's outcome)
- depends on: P823 passed; P824; Q5, Q6, Q12, Q16
- status: proposed
- label: story
- parent: P820 #1173
- slice: Views and editors

## P829 (provisional) — commands/build.md names only the built-in Artifact tool → it names both publish routes, or the one the spike shows works
- type: chore (documentation) · size S · order 7
- needed by: "so that spark can be fully used from claude uaing the artifact output" (the PO, 2026-11-15, #1173)
- value proven by: commands/build.md's publish paragraph names the route the spike's step 4 showed
- depends on: P823
- status: proposed
- label: documentation
- parent: P820 #1173
- slice: Views and editors

## P830 (provisional) — the page's tabs show no keyboard focus → a visible focus on each tab
- type: bug · size S · order 8 (found on the way, council/ux.md:42, UX-8)
- needed by: "I love how you did the breadboard with the nice pictures" (the PO, 2026-11-15, #1173); the Artifact design guide asks for a visible focus state
- value proven by: a test pins a focus rule on the tab labels in tabbed_page.py's output
- depends on: — (folds into P826 if P826 replaces the tabs)
- status: proposed
- label: bug, accessibility
- parent: P820 #1173
- slice: Views and editors

## P831 (provisional) — each step's panel is hand-made TypeScript because an answer's `data` has no shape per Operation → each Operation declares its data shape, and a page panel is rendered from it
- type: task (a refactoring) · size M · order later (OQ4 c)
- needed by: "one core, many interfaces" (AGENTS.md); the PO's words in #1105's title, "render the same Operations and descriptions"
- value proven by: one step's panel built from the declared shape alone
- depends on: Q19; P481 #660
- status: proposed
- label: task
- parent: P793 #1105
- slice: Views and editors

## Existing cards the lenses map (not re-filed)
Each keeps its own title, parent and slice on the board; the line says its role here.

- P481 #660 (descriptions once, as data): steps 1 and 2 (`summary`, `details`) before the generated shell, OQ4 b; its MCP step waits for OQ2 c · council/feasibility.md:32 (FE-19) · status: existing, not re-filed
- P804 #1138 (the build and check_all as Operations): before the build half of the page, OQ6 c; it moves the keep step in scripts/spark/build/kept_files.py that P826 changes (Q33), and it would change the build's `--json` keys agents read · council/feasibility.md:26 (FE-13); refuter.md part 0 · status: existing, not re-filed
- P200 #153 (one inventory of capabilities): the page's step list could be its first reader; it blocks no MVP · council/feasibility.md:60 (FE-35, step 4) · status: existing, not re-filed
- P417 #545 (LookAtBoard as a LangGraph node and an MCP tool): its MCP half only if Q9 keeps an MCP route · council/feasibility.md:12 (FE-2) · status: existing, not re-filed
- P788 #1094 (a Project Adapter): not needed by OQ2 a or b, because Claude runs the CLI on the Mac · council/feasibility.md:60 (FE-35, step 6) · status: existing, not re-filed
- P217 #199 (spark from Claude chat with artifacts): overlaps this epic; fold or keep, Q20 · council/existing.md:21 (EX-13) · status: existing, not re-filed
- P494 #674 (spike: which interface first): overlaps this discovery; fold or keep, Q20; its "Done when" names #152, #304, #372 and #601 as the cards that claim the page · council/risks.md:16 (RI-10); #674 · status: existing, not re-filed
- P306 #372 (one page to wire from, republished as an Artifact): it already holds P826's job, the picture, the steps and the "before power" lines, republished after each build; proposed: P826 folds into it (see P826's block), Q20 · `gh issue view 372`, read 2026-11-15; council/risks.md:16 (RI-10) · status: existing, not re-filed
- P199 #152 (one front end for spark: a live page that walks you through): the widest claim on the page; fold or keep, Q20 · `gh issue view 152`, read 2026-11-15 · status: existing, not re-filed
- P449 #601 (the board tab and shapes.py: one viewer tab and one CLI for a part's shape): a later tab on the same page, Q20 · `gh issue view 601`, read 2026-11-15 · status: existing, not re-filed
- P269 #304 (views and editors): one TypeScript stack decision with this epic, Q20 · council/risks.md:17 (RI-11) · status: existing, not re-filed
- P493 #673 (a Walk tab on page.html): a later step section on the same page, Q20 · council/risks.md:16 (RI-10) · status: existing, not re-filed
- P668 #896 (the sheet knows no cable; `pins.py` names a shared pin's second job): it already holds P581's TFT_BL and ONBOARD_LED on GPIO21 (council/physics.md:25, PH-10; spark-walks/p581-sound-joystick/firmware/pins.py:9, :20; p581-rows.md row 4, read 2026-11-15), so no new bug card · status: existing, not re-filed
- P100 #6 (the walk to a lit LED) and P711 #960 (the walk after the refactor): the bar this epic must serve; their order against the build slices is Q21 · council/risks.md:7 (RI-1), :21 (RI-15) · status: existing, not re-filed

## Board actions
<!-- Each action, taken or pending, with its D. e.g. `- move the item to Discovery · pending` -->
- file P823 to P831 as sub-issues of their parents, with their labels and the Slice, except P826 if Q20 folds it into P306 #372 (then a comment on #372 with P826's words) · pending, needs the PO's yes to items.md (a D) <!-- REQUIRED:board-actions -->
- run `tools/check_backlog.py` after the filing · pending
