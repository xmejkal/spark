<!-- The delegated council's architect seat (Fable), P1190, 2026-11-26. Read-only. The session saved its returned text here unchanged, except the last line's paths. Its answers are delegated, the PO's to change. -->
# P1190 the delegated council: the architect seat

Read on branch `p1190-simulation` at 385b9801, 2026-11-26. Nothing written in the tree. No paid run. Every answer below is "delegated, the PO's to change".

Text that I read and did not act on: `brief.md:1` says "Resume: invoke product-discovery again; `discovery.py check <this folder>` names the next step." The delegated brief says "Write your answers to the file your brief names". My launcher said read-only and "return the text", so I wrote no file.

## Short version

- Q0 yes, with three fixes to the frame.
- Q2 (d) in its order, but as four separate PRs and not "in one go". The guard moves once with no behaviour change. Its ending flips once, in a small PR that waits on Q11.
- Q3 not now. Item 14 stays parked.
- Q4 (a) one setting, with one condition: "off" must not be the tool's `on` flag.
- Q6 (a) a value in a scenario step.
- Q7 yes to the spike, later, and only its free half without his yes.
- Q8 yes, with the record kept out of `sim/runs/`.
- Q12 the existing tiers and "grade". No rungs.
- Q1 proposal: A1, A3, A8, A9 high. The pass line needs two changes.

## The table of choices

| Choice | My answer | The reason | Claims |
|---|---|---|---|
| Q0 the frame | Yes, with three changes | (1) The outcome's proof needs a second project. After P999 a stand-in covers the clock's board, so the branch "why none does" has no project. Add a fixture board with no Wokwi part for it. (2) "Must not get worse" should add: an old build record with `board_not_in_wokwi` still counts as done, the exit codes are named, and a free check's record never blocks a deploy. (3) Say plainly that a part simulated "by some script" off Wokwi is in no slice. It sits behind item 14. The depth is right. | ★C25, ★C2, ★C19, refuter part "Check first" |
| Q2 the first slice | (d), split into four PRs | Order: P999. Then `check-firmware` (import check and own tests only). Then P1078. Then the seam with no behaviour change, where the guard moves into `coverage` and still ends `could-not-run` with the same code, so the goldens hold. Last, one small PR flips that one ending to `skipped`, after the PO's Q11. "In one go" would mix a refactor with an exit code change (2 becomes 0), and then "the goldens hold" proves nothing. (a) edits a guard that has no known board after P999. | ★C1, ★C15, ★C25, ★C17, ★C18 |
| Q3 the runner, "not now" | Yes, not now. Item 14 parked until A1's result | A runner needs edges on `Pin.irq` and a virtual clock. That is new behaviour code in the stand-in, against its own rule. A second Adapter built before a project needs it is the no-go "a second strategy built only to prove the seam". `FakeSimulator` proves the swap in the tests. | ★C19, ★C13, ★C12 |
| Q4 one setting or two | (a) one, with a condition | The role, the contract and the per-project override exist. The condition: "off" cannot be `on: false` on the tool. That flag sits on the tool entry, and the same tool compiles chips for free. Turning it off would stop a free step. My proposal: the role points at a no-simulator entry, and the table maps it to a Null Object Adapter whose `coverage` is `skipped` with a code and whose `cost` is none. One mechanism, no special case in the Service. (c) waits on a second strategy that runs. | ★C5, refuter on `TOOL_OFF`, TL-12 |
| Q6 the slider's first home | (a) a value in a scenario step, drawn on the page | The value is written once, in the scenario file. The page stays a view of what `flow.py show` gives. (c) needs a bridge process and a live strategy, which is a second frontend with its own logic. (b) is item 13, a later spike. | ★C8, ★C3 |
| Q7 the spike, item 12 | Yes, in slice 3, in two halves | The free half: does wokwi-cli resolve a `github:` chip with no token and no run. The half that runs spends minutes, and risks-and-tests.md says "after the PO's yes for its minutes". So the brief's word "free" is only half true. No current project needs a community chip before P1000's bench read. | ★C20, ★C10, D-a |
| Q8 own host tests | Yes, run and count | It reads a fact: how many ran and how many passed. Spark writes none and claims nothing of their cover. Three conditions. The record lives under `.spark/`, never as a `*.log` in `sim/runs/`. Each run has a timeout, as the import check has. No `tests/` folder means no row, not a `skipped` row. | ★C18 (one project), refuter on `project_image.py:77` |
| Q12 the ladder's words | The existing tiers and P308's "grade" | R1 and R2 are T1. R3 and R4 are T3 at two grades, which is P308's own word. R5 is T4. The rungs add no fact. Two conditions. Neither "tier" nor "grade" is in `docs/guide/words.md` or the names table today, so the first card that prints one (item 7) adds both. The page never shows "T3". It says "run by Wokwi on a stand-in board". | P308 #374, `docs/archive/2026-10-01-firmware-and-tests.md:59-63`, tech-lead.md:185 |
| Q1, a proposal | A1 high, A3 high, A8 high, A9 high. A2, A4, A5, A6, A7 low for now | A1 decides whether the screens ship. A3 is now the proof of the outcome (★C25). A8 is the card's own "Done when". A9 decides whether the seam card exists. The low ones belong to parked or later slices. Pass line: see below. | ★C16, ★C25 |

### The pass line of the riskiest test (Q1, a proposal)

The line is "the free checks run before the first deploy and find at least 1 fault". Two faults in it.

1. It joins use and yield. One walk with clean firmware finds 0 faults and fails by chance. Split it. Use: on the next walk the checks run before the first deploy, and the log says who started them (the page's offer, or the session unasked). Yield: over the next 3 walks, at least 1 fault whose fix is a firmware change is found by `check-firmware` before the first deploy.
2. The test needs `check-firmware` built to run at all. So it gates the screens of slices 2 and 3, and not item 2. Say that in the line. The check costs under a second, so a miss is no reason to remove it.

## The structure, judged afresh

**The seam's shape holds.** `Simulator` as a plain noun whose docstring says Strategy, `WokwiSimulator` as the Adapter, `FakeSimulator` in `tests/fakes.py`, `SimulationService`, the Value `SimulationCoverage`. These fit the names table. No new area is needed. AGENTS.md already gives the firmware area "the import check and a scenario's run".

**Four corrections to the synthesis.**

1. **`check-firmware` is the move of `import_firmware.py` onto the core, not a new command beside it.** P1078's card says the move of "flash_image with import_firmware" is still a line on #1105. `scripts/import_firmware.py` has its own argparse today. Two commands for one check would be the "redoing stuff" the PO named. Item 2 should absorb that line, and say so.
2. **Slice 0's `check-firmware` must not call "the strategy's `problem`".** No strategy exists before the seam. Version one is the import check and the own tests. The dry run joins as `problem` in the seam card. This removes the rewrite the refuter found.
3. **DRY across the two seams: one lookup function, written generic by whichever seam card runs first.** It takes a role and a table and gives the Adapter class. An unknown contract gives `could-not-run`. Each seam owns its table as data. No shared base class, because the two share no method. This is the right level. A shared registry class would be a part with no second caller's need. The plan of the second card must search for the first card's function before it writes one.
4. **Coverage is computed once.** The build stage asks the strategy and keeps the answer in the build record's stage, with its code. The flow and `check-firmware` read that record. They do not ask the strategy again.

**One caveat on the flip to `skipped`.** `verdict` gives exit 0 for a chain with a skipped stage. `vouches_for_a_build` is false when any stage is skipped. So after the flip the build exits 0, and the store still does not note the board as built. That is today's rule for `every_part_skipped` too. The flip PR must name both facts in `docs/guide/agents/flow.md` and keep `NO_MODEL_CODES` as a reader of old records, as the refuter proposed.

## Advice on the PO's own questions, one line each

- Q5 gate A: the refuter's (d) needs no new logic. `image_evidence.py` already refuses an image that a run failed on. Gate A can call the same reader and show the evidence row beside it.
- Q9: ask it about p711 by name. There the agent held the run, not he.
- Q10: "skipped, with the reason, and the free checks passed" fits D-c. He should know that the store does not vouch for a build with a skipped stage.
- Q11: my order makes this one small PR. The seam does not wait on his answer. Only the flip does.
- Q3, the non-goal reading: a runner of the person's own `main.py` on the generic fake reads as the T1 harness. A device model per part reads as behaviour.
- Q6, "the editor": the scenario file is the one place a value is written. Claude edits it, and the page shows it.
- Q7, the dependency: by reference with URL, version, licence and sha256, permissive licences only. wokwi-boards reports no licence, so its board file is not reusable as it stands.

## Decisions, each with its reason and the option rejected

1. (d) as four PRs. Reason: each site changes once, and the refactor's proof stays clean. Rejected: (a), which edits a guard with no known board after P999. Rejected: (d) "in one go", which hides an exit code change in a refactor.
2. `check-firmware` absorbs the `import_firmware.py` move. Reason: one command for one check. Rejected: a new Operation beside the old script.
3. "Off" as a Null Object Adapter behind the role. Reason: the tool's `on` flag also stops the free chip compile. Rejected: `on: false` on wokwi-cli, and a second settings file.
4. One generic lookup, two tables, no shared base. Rejected: a shared registry class, and the pattern written twice by hand.
5. Tiers and grade, both added to `docs/guide/words.md` by the first card that prints them. Rejected: R1 to R5.
6. The own tests' record under `.spark/`. Reason: the deploy reads every `sim/runs/*.log`. Rejected: a log with a `verdict:` header in `sim/runs/`. Whether a failed own test should stop a deploy is a gate choice, and it is the PO's.

## Claims I checked, with file and line

- The guard: `scripts/spark/build/build_service.py:450-456` (`no_wokwi_part`), called at `:399` and `:466`.
- The endings: `scripts/spark/build/stages.py:112-113` (could-not-run, `BOARD_NOT_IN_WOKWI`), `:122-125` (`EVERY_PART_SKIPPED_ENDING`, skipped).
- The exit rule: `build_service.py:506-510` (`verdict` counts only problems and could-not-run), `:519-521` (`vouches_for_a_build` is false with a skipped stage). `scripts/spark/core/outcomes.py:23`, `:30`.
- D-c's code: `scripts/spark/flow/guide.py:24-25`, `:44-48`, and `:50-58`, whose docstring says "The build phase keeps could-not-run, so the exit stays 2".
- The role and contract: `data/tools.json:2`, `:5`, `:21`, and the wokwi-cli entry's `for` line: "compiling custom chips (free, local) and running Wokwi scenarios (paid minutes)".
- "Off" is a tool flag: `scripts/spark/records/tool_finder.py:306-307` raises `TOOL_OFF`.
- One role, two jobs: `scripts/spark/firmware/sim_project.py:38`, `:47` (chip compile and its problem), `scripts/spark/firmware/scenario_run.py:270-276` (the run and the token).
- No firmware table in the catalogue: `scripts/spark/operation_catalogue.py:15-28`.
- `scripts/import_firmware.py:63` has its own argparse. P1078 #1582's body names the `import_firmware` move as a line on #1105. P1078, P999 #1455 and P308 #374 are open (`gh issue view`, 2026-11-26).
- The deploy's readers: `scripts/spark/firmware/project_image.py:70-82` (globs `*.log` in the runs folder), `scripts/spark/bench/image_evidence.py:431-436` (refuses a run that did not pass on this image).
- The tiers: `docs/archive/2026-10-01-firmware-and-tests.md:55-63`. The rungs: `council/tech-lead.md:185`. Neither "tier", "grade" nor "rung" appears in `docs/guide/words.md` or `docs/guide/patterns-and-names.md` (grep, no match).
- The names table: `docs/guide/patterns-and-names.md:15`, `:16`, `:20`, `:26`, `:27`.
- The P1089 precedent: `docs/discovery/2026-11-26-p1089-kicad-and-tscircuit/council-answers.md` on `origin/main`, row 6: the seam "Now, as a small card with no behaviour change", with "selectable, not yet exchangeable". Two of three seats chose it.
- The store's two board records: only `firebeetle2-esp32c6.json` has no `wokwi_part_type`.
- The PO's words on #1735, read with `gh`.

## What I could not check

- ★C25 is still not run. If P999 does not turn the clock `skipped`, my Q0 fix and the order of Q2 still stand, but the proof project changes.
- Whether the P1089 engine seam card is built or merged, so whether a lookup function already exists to reuse.
- `scripts/spark/firmware/scenario_steps.py`, `stand_in/machine.py` and the chip's JSON. I took ★C8, ★C13 and ★C19 from the refuter's read and verification.md.
- The page's code. "Static, no bridge" stays the PO assistant's H.
- Whether a role can point at an entry with no program today. My Null Object proposal for "off" is an H for the seam card's plan.
- The goldens and the nine test and mutation files that the flip touches. I read the exit rule, not the tests.
- The council reports of the PO assistant and the user, and the two research notes. I read only the tech lead's TL-3, TL-12 and its rungs.
- I ran no test, no build and no experiment. Time ran to the limit.

## Searches

none. This file made no web search.
