# P498 documentation council: rows

What the four lenses and the synthesis found in the README and the guides on 2026-11-01. Card: #682. Record:
[the council](../2026-11-01-p498-docs-council/README.md).

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | README Honest limits says nothing was validated on hardware, but `deploy.py --no-simulation` ran on a FireBeetle 2 ESP32-S3 on 2026-10-31 and 2026-11-01 (D14 lit D13), and the XIAO on 2026-10-14 and 2026-10-15 | brief, new person | acted | README:237 against README:91, P461 #629, P462 #630. Fix in PR1 (F1). PR1: Honest limits now names both bench boards and their dates |
| 2 | agents.md:681-683 says a mistyped `--project` answers ok, exit 0 | brief, AI reader | acted | check_all.py:334 raises, `main` returns exit 2 at :530-537. P117 #51 open per the brief (not re-read: GitHub rate limit). Fix in PR1 (F2). PR1: agents.md says exit 2 with `no directory at <path>`, re-run 2026-11-01 |
| 3 | The README run-date sentence stops at 2026-10-18 | brief, tech writer | acted | `journey.runs_up_to(README)` prints 2026-11-01. README:77. Fix in PR1 (F3). PR1: the section says the runs go up to 2026-11-01 |
| 4 | README links P109 #43, P120 #54 and P128 #62 as plans, all closed as not planned | brief | acted | `gh issue view` on #43 and #54, #62 per the brief. README:65, 70, 245. Fix in PR1 (F4). PR1: the README names none of the three |
| 5 | journey.md:252's `parts.py --match` output is stale (XIAO "stops at the footprint stage") | brief | acted | output note dated 2026-10-08 at journey.md:245, P278 since 2026-10-18. Fix in PR1 (F5). PR1: a dated note under the output gives the 2026-11-01 match |
| 6 | commands.md:53 says init writes `CLAUDE.local.md`, true only when the store holds `rules.md` | brief | acted | ai_files.py:93-95. Fix in PR1 (F6). PR1: commands.md says init links only when the store holds `rules.md` |
| 7 | The Bench cell says the button-and-LED breadboard is not wired, while the D14 button lit D13 on 2026-11-01 | synthesis | acted | README:91. PR1 checks it against the P462 comment. PR1: still true. The 2026-11-01 run was board only (the P462 comment: D14 button, D13 LED, no breadboard). The Bench cell and Honest limits say no wired breadboard has run |
| 8 | No "what do I type" example on the first screen | new person | acted | README:3-25. PR1. PR1: the first screen holds the requirements file, the command, its dated output and one breadboard.md line |
| 9 | A 2026-10-08 history paragraph sits in the intro | new person | acted | README:32-37. PR1 moves it to journey.md. PR1: moved to journey.md Build, "The XIAO ESP32-C6, then and now" |
| 10 | "What it shows on the example" is a list of 12 issue links | new person | acted | README:45-72. PR1. PR1: cut. Each fact was already in journey.md (see row 36) |
| 11 | Table cells are paragraphs: Bench 4,348 characters | new person, tech writer | acted | `awk length` on README:91. PR1, guarded by PR2's 300-character cell test. PR1: each cell is one sentence, the detail is in journey.md "Today, in full" |
| 12 | No diagram in the README or commands.md, one Miro link to the board root | new person, diagrams | acted | grep of mermaid and miro.com. PR1 (two roads, frame links), PR5. PR1: the README has the two-roads mermaid and four Miro frame links |
| 13 | The README footer v0.9.0 is stale | new person | rejected | plugin.json ships 0.9.0, `check_docs.version_mismatch` enforces it |
| 14 | "not run here" about 10 times | new person | acted | 7 "not run here", 12 "not run" in the README. PR1 gathers them in one list. PR1: one "Not run for these docs" list under Honest limits |
| 15 | agents.md:444 is one 2,299-character table cell | AI reader | verified | `awk length`. PR1 shortens the row, PR4 moves the keys to agents-json.md |
| 16 | No JSON example of `check_spine.py --json`, and the check_all sample is from 2026-10-05 | AI reader | acted | agents.md:333 and :338. PR1 adds a dated example. PR1: agents.md has a dated `check_spine.py --json` example |
| 17 | The brief's example `check_spine.py --keep --json` lacks the folder `--keep` takes | synthesis | acted | `check_spine.py --help`: `--keep DIR`. PR1 uses `requirements.json --keep build --json`. PR1: the example uses `--keep build` |
| 18 | No short contract at the top of agents.md | AI reader | acted | the exit table is at agents.md:669, after 668 lines. PR1. PR1: agents.md opens with a 7-rule contract |
| 19 | A crash exits 1, said at README:202 and not under agents.md's exit table | AI reader | verified | agents.md:669-673. PR4 (one home) |
| 20 | No sentence on how a rebuild merges the Wokwi diagram, and "Is it ready?" ends without the next action | AI reader | raised | PR4 |
| 21 | journey.md's Idea section is 600 lines | tech writer | rejected | Idea is 274 lines (114-387). Idea to "Before you power it" is 598 (114-711). The split stands in PR3 |
| 22 | Exit codes have three homes | tech writer | verified | README:202, agents.md:554, agents.md:671. PR4 |
| 23 | developing.md mixes five jobs, and :600-643 belongs to `scrum/` | tech writer | verified | the headings. PR6 |
| 24 | Semicolons in the guides | tech writer | verified | agents 91, journey 89, developing 50, how-it-works 43, README 29. Each split PR rewrites what it moves |
| 25 | An anchor check is owed before any split | tech writer | rejected | `check_docs.broken_links` checks relative links and heading anchors already. Its gap is sub-folders (`doc_files` globs `docs/guide/*.md`). PR2 widens it |
| 26 | A length budget test is owed before any split | tech writer | verified | no such test in tests/. PR2 |
| 27 | Check the build-chain flowchart against `check_spine.py stages` | diagrams | rejected | no such subcommand: it reads `stages` as a path. The flowchart at how-it-works.md:19 matches its stage table and text |
| 28 | A status state diagram is owed | diagrams | raised | PR5 |
| 29 | Store, one-core context, and simulation-and-bench diagrams are owed | diagrams | raised | PR5 |
| 30 | A "which command next" flowchart for agents, a records diagram, and per-step sub-diagrams | diagrams | raised | later, after PR5. The rule "records grow by need" holds them until a reader asks |
| 31 | The "spark journey" Miro frame id is not in the team's notes | synthesis | acted | PR1 reads it from the board. PR1: the team's notes hold it (journey frame 3458764687016851094, 2026-10-30). Not read back from the board |
| 32 | The README needs an owner: it changes only through the documentation council or a story's one-sentence status line | PO, synthesis | acted | PR1 adds the rule to developing.md "The docs name only what is there". PR1: developing.md "Who changes the README" |
| 33 | Each fact cut from the README has a home | PR1 | acted | Cells: Idea, Build, Checks, Simulate and Bench got a "Today, in full" paragraph in journey.md. Drawer, Research and Firmware cells held nothing journey.md lacked (Drawer :77 and :112, Research :746, Firmware P59, P421, "reads 0", P74). Before you start, Linux and the update paragraph went to journey.md Build. The agent `--dry-run --json` tip went to agents.md "What reads and what writes" |
| 34 | The README's six-line road-one block and its "the last line exits 2, no step is in the history" note | PR1 | closed | cut with the block. The recorded run in journey.md shows each command with its output, and the S, M, C, L marks |
| 35 | "What it uses underneath" in the README | PR1 | closed | cut to three lines. how-it-works.md holds the rest: the tools (:238), P112's unpinned MCP servers (:245, :266), the history and the tally's transcripts (:225-231), KiCad (:275). The DFRobot import through Claude in Chrome is in journey.md Drawer |
| 36 | "What it shows on the example" bullets | PR1 | closed | already in journey.md: the sheet's D3 step (:439), P202, P267, P268, P412, P273, P287, P279, P271, P272 (Before you power it), the CONFLICT (Checks), the 0.225 mm ring and the 355 mA line (Checks output), MOTOR_IA's reason (Firmware) |
| 37 | "Before ordering" and the `$CLAUDE_PLUGIN_ROOT` note in the README | PR1 | closed | journey.md "From draft to order" holds the draft limits. The journey intro ("Paths") and agents.md "Set up" explain `$CLAUDE_PLUGIN_ROOT` |
| 38 | journey.md Bench ended with "The button-and-LED project is not yet wired and flashed" and "Apart from the blink above, every green result is a build ..." | PR1 | acted | false since P215 (2026-10-15 flash) and P461, P462. Replaced by the Bench "Today, in full" list |
| 39 | A board MAC in agents.md :141 and journey.md (two grant file names) | PR1 | acted | masked as `8c-bf-ea-xx-xx-xx`, the form the deploy output already uses |
| 40 | journey.md's `--audit` output (:573) and the soil match output (:606) also show the XIAO "stops at the footprint stage" | PR1 | acted, partly | the audit got a dated 2026-11-01 note (re-run in a scratch store). The note says the other 2026-10-08 outputs keep the old line. PR3 re-runs or re-dates them when it splits the page |
| 41 | The README is 182 lines, over the brief's "about 180" | PR1 | raised | the commands list and the Miro list take 13 lines. PR2's budget test (README 150) decides what moves next |
| 42 | The simple-English lint flags sentences that end in a link, then `).` | PR1 | rejected | the linter does not split a sentence after a link's `)`. The sentences it joins are short. The remaining hits in the added text are this pattern and a bold label before "If" |
| 43 | journey.md now says some facts twice (the "Today, in full" paragraphs beside the older step text) | PR1 | raised | move first, then dedupe: PR3 gives each step one page and one home per fact |
