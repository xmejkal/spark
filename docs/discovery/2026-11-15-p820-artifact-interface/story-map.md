# Story map
<!-- Proposed, not applied: this map stays here until the decider confirms it; nothing changes the product's own
map file. -->
**Status:** proposed, not applied <!-- REQUIRED:map-status -->

## Backbone
<!-- The activities, left to right, as the user does them. e.g. `Assign → Notice → Act → Close` -->
Idea → Needs → Parts and store options → Requirements → Build → Breadboard steps → Firmware → Simulate → Deploy <!-- REQUIRED:backbone -->

Each row is a proposal (H, the synthesis) and names the lens finding it rests on. Pointers are to council/ files. Jobs are those in jobs-and-journeys.md. "Not on the page" is a choice to keep a step in the chat, not a gap.

## Slices
<!-- Walking skeleton first: the thinnest slice that runs end to end. One row per story. job: a job in
jobs-and-journeys.md. tag: as in the brief. proof: something the decider can read.
e.g. `| 0 | Notice | the assignee gets one daily digest | job 1 | H ★C2 | the digest log for one team |` -->
| slice | activity | story | job | tag | proof |
| --- | --- | --- | --- | --- | --- |
| 0 spike <!-- REQUIRED:slices --> | across Needs to Build | a throwaway page (no spark data) settles: does a click's `db` row reach Claude Code's `db_get`; do rows survive a republish; do both publish routes reach one artifact and one `db`; can `files` read a local Claude Code project; does a click made with no session open wait unlost (A11) | job 4 | H feasibility.md:72 (FE-38), risks.md:27 (A1) | the Results row in risks-and-tests.md against the pass lines dated 2026-11-15 |
| 1 refactor, before the MVP | Breadboard steps | a JSON renderer of `BreadboardSteps` beside `NumberedList` and `MermaidDiagram`; the page writer embeds the data | job 2 | E feasibility.md:27 (FE-14), :60 (FE-35, step 1) | a test pins the JSON steps equal to breadboard.md's numbered list on a fixture |
| 1 refactor, before the MVP | across | the page's TypeScript builds to one file, and the story run tests it (a folder mapping, a `node_modules` loan, a wrapper test, as the converter has) | all | E feasibility.md:39 (FE-23), :40 (FE-24) | the hook's output on the commit that adds the package |
| 2 MVP, the floor | Breadboard steps | the page shows every wiring step, one at a time and all at once, with the picture and the "Before you power it" lines first, generated from the build's records; it works opened from disk with no Claude | job 2 | E user.md:41 (US-3), ux.md:80 (UX-12), ux.md:204 (UX-39); H that the PO accepts a generated page as the standard (ux.md:15, UX-5); the one-step mode needs a script, which fails tests/test_tabbed_page.py:53-56 unless the PO retires that guarantee (brief Q29); P306 #372 already holds this job (brief Q20) | button-light's page.html, opened from disk, shows each step and each before-power line; the P100 walk wires from it |
| 2 MVP, the floor | Build | each stage shows its state with a word and a glyph, never color alone: ok, problem, not checked, not measured, skipped, could-not-run, stale | job 1 | E ux.md:143 (UX-21), physics.md:35 (PH-15), user.md:55 (US-10) | a fixture build with a could-not-run stage and a null fact; a test pins that neither is drawn as a tick |
| 2 MVP, the floor | Needs, Parts | the page shows the needs and the candidates per need from the masked `--match` envelope, read-only | job 1 | E feasibility.md:25 (FE-12), ux.md:101 (UX-13) | the page beside the CLI's `--match` text for button-light: the same candidates |
| 2 MVP, the click | Parts | a Pick on a need card writes a request row in the shape of a `next` step, or copies the line for the chat; Claude runs `--pick --json` at its next turn and the page shows "done" | job 1, job 4 | E feasibility.md:42 (FE-26), :71 (FE-37), ux.md:162 (UX-30); H that it works (the spike) | the `db` row, the chat transcript, and `needs.json` holding the pick (the brief's outcome) |
| 2 MVP, the click | across | each step's next-step panel names the action and who does it: "Ask Claude" (a request) and "I do it myself" (the command, copied) | job 3 | E ux.md:187 (UX-34, the PO's words 2026-10-31); H for every step | the PO picks the next step from the panel in one walk |
| — not on the page | Idea | the goal becomes needs in the chat, always | job 1 | E feasibility.md:48 (FE-29) | — |
| — not on the page | Firmware | Claude writes the firmware in the chat; the page hands back with a line ("Tell Claude 'wired'") | job 3 | E AGENTS.md (the conversation writes the firmware); feasibility.md:29 (FE-16) | — |
| 3 refactorings | across | P481 #660 steps 1 and 2: each Operation has `summary` and `details`, so step titles and help come from the core | job 4 | E feasibility.md:32 (FE-19), :60 (FE-35, step 2) | `--describe` shows a summary for every Operation the page lists |
| 3 refactorings | Build | P804 #1138: the build and check_all are Operations with the envelope, so the build half renders like the idea half | job 1 | E feasibility.md:26 (FE-13) | `check_spine.py --json` answers the envelope |
| 3 refactorings | across | each Operation declares its data shape, so a step's panel is rendered without hand-made TS (no card yet) | all | H feasibility.md:67 (FE-36), E :31 (FE-18) | a page panel for one step built from the declared shape alone |
| 4 later | Requirements, Build | the conflict banner when the page and the chat change the same thing ("Not applied … [Apply again] [Keep Claude's]") | job 3 | H ux.md:188 (UX-35) | — |
| 4 later | Build | a power panel: the rail headroom with its provenance and the unverified figures under any ok | job 1 | E physics.md:9 (PH-2), :11 (PH-3), :13 (PH-4); pending brief Q14 | — |
| 4 later | Parts and store options | shop options with prices, only if "store options" means shops | job 1 | E ux.md:113 (UX-14); pending brief Q15 | — |
| 4 later | Simulate | the run's verdict with its `limits` and caveats beside any pass, and the line to run, with Copy; no Run-simulation click unless it names its cost and waits for a yes (no paid Wokwi run) | job 1 | E jobs-and-journeys.md:43 (step 8); ux.md:123 (UX-16), ux.md:137 (UX-18) | — |
| 4 later | Deploy | the look, the caveats, the limits and the exact line to type, with a Copy button; no Flash, Deploy or Run-live-code button | job 1 | E ux.md:124 (UX-17), feasibility.md:33 (FE-20); docs/guide/agents/never-assume.md:167 (a relayed yes can make a live grant; brief Q31) | — |
| 4 later | across | `files` shows the kept files without a republish, if the spike shows it reaches a local project | job 4 | E feasibility.md:17 (FE-7) | — |
| 4 later | across | an MCP route (P417 #545's MCP half, or MCP Apps), only if the decider wants a click that acts at once | job 4 | E feasibility.md:11 (FE-1), :21 (FE-11) | — |
| 4 later | across | a labelled "ask the page's helper" box on `sample`, only once its payer is known | job 3 | E ux.md:159 (UX-27), risks.md:13 (RI-7) | — |

## Delta to the product's map <!-- REQUIRED:spark-process:map-delta -->
<!-- The rows to add or change in the repository's own story map file, in that file's table shape, with its journey
step numbers; proposed, not applied. "n/a — no map file" is allowed. -->
Proposed for scrum/STORY_MAP.md, not applied. The file has no row for the board's Slice "Views and editors" (E `/usr/bin/grep -n "Views and editors" scrum/STORY_MAP.md`, no line, 2026-11-15).

- Add to "The slices, in order": `| **Views and editors** | **One page per project** — the board's Slice "Views and editors" | hobbyist | on button-light, one page shows the needs, the picks, the build's stages and the wiring steps, and one click reaches Claude at its next turn | P820 (#1173), P269 (#304), P493 (#673), P494 (#674); the cards in items.md once filed |`
- Change journey step 7 "See it", column gap: add "one page per project with the steps and a click path (P820)".
- Change journey step 10 "Breadboard", column spark today: add "`page.html` with the steps one at a time (P820, once built)".
