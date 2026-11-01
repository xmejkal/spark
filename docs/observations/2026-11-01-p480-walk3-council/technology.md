# P480 council: technology lens

> 33 of the 37 gaps hold in the code at `53c1cbb8` (HEAD `6626a1f9` only adds P480 docs). G36 holds only in part, G35 and G2 are page and cache gaps, and G11, G16, G19 and G34 are not fully checked.
> The strongest finding: G27 is by design, not a bug. `vouches_for_a_build` refuses a skipped stage, so a board-only build never writes `built`.
> C2, C5 and C8 are too big for one card. Split them. C3, C6 and C7 shrink to a few lines each.

Card legend: C1 Wokwi and own emulator spike, C2 board's own parts, C3 project name and folder, C4 store writes said and dry run, C5 which board is on USB, C6 bench result and passed-run wording, C7 hand edits page, C8 free firmware tests on the Mac.

## Findings

| # | finding | evidence | card or plan | proposal | severity |
|---|---|---|---|---|---|
| G1 | Holds. Init and idea pages never mention reading the board on USB. | `/usr/bin/grep -n USB commands/init.md commands/idea.md` prints nothing. | C5 | One line on the init page: run `look.py` first. | medium |
| G2 | Page-level gap, cache not checked. The repo plugin version is 0.9.0. | `.claude-plugin/plugin.json` version 0.9.0. I did not read the cache. | none | Not a code fix. A doctor line in `/spark:setup` is a new idea. | low |
| G3 | Holds. A missing file and a missing key give the same stop and an empty `fix`. | `scripts/board_look.py:467-474` (OSError gives name None), `board_doctor.py:171-181` (no doctor for this stop), `board_envelope.py:68-71`. | C5 | Split the two causes. Give `fix` "run /spark:init --board". | medium |
| G4 | Holds. The look reads the board only through `record_of(project)`. | `scripts/board_look.py:464-479`. | C5 | A look with `--board`-less mode that prints chip, flash and MAC. | high |
| G5 | Holds. `add_project` writes `projects.json`, and the init page lists no such write. | `scripts/init_project.py:430`, `scripts/store.py:289-297`, `commands/init.md:50-60`. | C4 | Add one bullet to the init page. | medium |
| G6 | Holds. The wording is "not asked for" for a skipped check. | `scripts/check_all.py:466`. | open walk 2 row | Say "nothing built yet" when `dist/` is absent. | low |
| G7 | Holds. No script reads library, drawer and store record together. | `/usr/bin/grep` of `scripts/` finds no such op. The record reads live in `boards.py`, `drawer.py`, `deploy_record_store.py`. | C5 | A read-only op `board.py --know <key or MAC>`. | medium |
| G8 | Holds. The idea page shows `--step` and does not say it writes history. | `commands/idea.md:14-18` and `scripts/parts.py:2239-2253`. | C4 | One sentence on the idea page and in `--help`. | medium |
| G9 | Holds. `add_project` resolves any path and never checks it exists. `needs.write` creates parents. | `scripts/store.py:272-297`, `scripts/needs.py:116`. | C3 | Refuse a folder that is not there. | high |
| G10 | Holds. No remove or forget op exists. | `/usr/bin/grep -n "remove\|forget" scripts/store.py scripts/parts.py` finds none for projects. | C3 | A `--unlist PROJECT` with a dry run. | low |
| G11 | Not fully checked. The name sits in the store record. | `~/.local/share/spark/boards/8c-bf-ea-cc-97-70.json` holds it. I did not run `--match`. | walk 2 row | Not checked. | low |
| G12 | Holds. I ran `parts.py --offer firebeetle2-esp32s3`. | Output shows "compute microcontroller" twice and a long power JSON line. The LED line has no GPIO. | walk 2 row | Dedupe `does`. Add the role pins to the line. | low |
| G13 | Holds. The board file has no `wokwi-board` document. The XIAO file has one. | `boards/firebeetle2-esp32s3.json:325`, `boards/xiao-esp32-c6.json:396`, `scripts/boards.py:427`. | C2 | Keep the S3 devkit definition as a document of the record. | high |
| G14 | Not checked. The page says what it says. | `commands/idea.md:128-129`. I did not run a pick. | none | Not checked. | low |
| G15 | Holds. The doctor shows the serial and never reads the store record by MAC. | `scripts/board_doctor.py:103` only prints the serial. | C5 | Read `deploy_record_store` by MAC in the look. | medium |
| G16 | Holds in part. The doctor has two steps and no word on "silent firmware". | `scripts/board_doctor.py:28-53`. | C5 | Add a line only when a last deploy exists. | low |
| G17 | Holds. `--step` has a dry run and `--needs-set` says no folder was made. | `scripts/parts.py:2239-2253` and `2109-2114`. | C3, C4 | Print the folder and the store path. | medium |
| G18 | Holds. The token is part of the status, so no-token and not-read share status 2. A code tells them apart. | `scripts/board_look.py:313-319`, `scripts/spark/bench/look_at_board.py:62-65`. | C5 | Add a `board_read: true` field to the look data. | medium |
| G19 | Holds in part. The `next` is empty when there is no token. | `scripts/spark/bench/look_at_board.py:59-76`. The doctor step text sits at `board_doctor.py:46-47`. | C5 | Repeat the RESET line in the look's `fix`. | low |
| G20 | Holds. A board-only build skips parts, schematic, footprint and build. | `scripts/check_spine.py:576`. | C2 | See C2 below. | high |
| G21 | Holds. Only `compile()` runs. No stubs exist in the repo. | `scripts/image_evidence.py:95`. A search for stubs finds only a backlog line. | C8 | Ship `typings/` stubs for `machine` and `time`. | low |
| G22 | Holds. No page on kinds of test. | `/usr/bin/grep -n "kinds of test" docs/guide/*.md` prints nothing. | none | One table in `docs/guide/journey.md`. | low |
| G23 | Holds. No user page links the P295 own-simulator finding. | `/usr/bin/grep -rn p295-own-simulator README.md docs/guide commands` prints nothing. | C1 | Link it from the journey page. | low |
| G24 | Holds. No script uses `--vcd-file`. The PWM stand-in keeps the last duty. | `/usr/bin/grep -rn vcd scripts` prints nothing. `scripts/stand_in/machine.py:6,100`. | C1, C8 | Wokwi cannot check duty. Use the Mac stand-in. | medium |
| G25 | Holds. `check_spine` has no dry-run flag. It writes `built`. | `scripts/check_spine.py:668-690` (arguments), `739-745` (write). | C4 | Add `--no-record` or a dry run. | medium |
| G26 | Holds. The board-only diagram is hand-written with `connections: []`. | `scripts/check_spine.py:583-586`. | C2 | Use the normal converter. | high |
| G27 | Holds, and it is by design. A skipped stage blocks `built`. The page and the verdict say otherwise. | `scripts/check_spine.py:622-624` and `743`. | C4 | Fix the wording, or decide that board-only records `built`. Ask the PO. | high |
| G28 | Holds. The diagram holds the devkit part only. | `scripts/check_spine.py:583-586`. | C2 | See G26. | high |
| G29 | Holds. No `wokwi-board` document is in the FireBeetle record. | `boards/firebeetle2-esp32s3.json:325`. | C2 | Same as G13. | high |
| G30 | Holds. The repo has no example firmware with the console lines. | `/usr/bin/grep -rln "uselect\|sys.stdin"` finds only `tools/` and `tests/`. `journey.md:1285` describes the lines. | C8 | Put the lines in the firmware step page as text. | medium |
| G31 | Holds. `import_firmware.py` only imports. The stand-in has no clock. | `scripts/import_firmware.py:68-111`. `/usr/bin/grep -n ticks scripts/stand_in/machine.py` prints nothing. | C8 | Follow P295 option B step 1. | medium |
| G32 | Holds. The log says "passed". The look names the caveat. | `scripts/run_scenario.py:433`, `scripts/image_evidence.py:40-41`. | C6 | Put the caveat in the run's verdict line. | medium |
| G33 | Holds in part. `agents.md` lists some rules and no page lists all. | `docs/guide/agents.md:842`, `journey.md:904`, `check_spine.py:583-586`. | C7 | One table of kept and replaced files. | medium |
| G34 | Not fully checked. The doctor step comes from `data/tools.json`, and the record holds no fact. | `scripts/board_doctor.py:15`. I did not read `tools.json`. | C5 | Add a `silent_step` fact to the FireBeetle record. | low |
| G35 | Holds. The deploy page has no auto mode text. | `/usr/bin/grep -in "auto mode" commands/deploy.md` prints nothing. | C6 | Two lines on the page: relay the terminal line. | medium |
| G36 | Holds in part. The page now explains it at `deploy.md:40-41`. The code still prints `--port`. | `scripts/board_envelope.py:38`. | walk 2 row | Drop `--port` when one board is on USB. | low |
| G37 | Holds. `--fact-set` records part facts, not a must line result. | `scripts/parts.py:1574`. No other writer exists. | C6 | A bench line in `.spark/project.json`. Needs a design. | medium |

## The cards

- **C1 Wokwi spike: keep.** It is a spike, so its answer is a finding with sources and no code. Done when: a finding answers the four questions and the open P295 questions, with URLs and dates. Merge question 3 into P391 (boards as modules).
- **C2 board's own parts: split.** It is a whole design, not a small card.
  - C2a rewrite: "A board record names its Wokwi definition." The change: keep the S3 devkit `wokwi-board` document under the FireBeetle `documents`, as the XIAO has. Done when: `--match` no longer says "names no Wokwi definition" and the P396 check lists the reachable GPIOs.
  - C2b rewrite: "Board-only build uses the normal converter." The change: `board_alone` adds the LED, the button and the serial wires from the record. Done when: the diagram has a part on GPIO21 and one on GPIO47, and a wait-serial scenario hears the firmware.
  - C2c keep as a design card, folded into P391: the "on me" link. Do it after C2a and C2b show the shape.
- **C3 project name and folder: rewrite smaller.** The change: `parts.py` takes a listed name or an existing folder and refuses any other, and says which it used. Done when: `--step walk3` in a folder with no `walk3/` makes nothing and says why. Split the unlist command into a later card.
- **C4 store writes said: rewrite.** Page text first (init, idea, build), then `--dry-run` on `check_spine`. Ask the PO about G27 before code. Done when: each writer has a sentence on its page and in `--help`, and `check_spine --dry-run` writes no history line.
- **C5 which board is on USB: split.** It holds five jobs.
  - C5a: the look with no `requirements.json` says "run /spark:init --board" in `fix` (G3). Tiny.
  - C5b: the look data gets `board_read` (G18), and repeats RESET in `fix` (G19).
  - C5c: a read-only "what spark knows about this board" op (G1, G4, G7, G15). Check P391 first.
  - C5d: a FireBeetle `silent_step` fact (G34), after a bench check by the PO.
- **C6 bench result: split.** C6a, small: the verdict of a passed run with no must line names that (G32), and the deploy page says what to do when auto mode refuses (G35). C6b, a design: where a bench result lives (G37).
- **C7 hand edits page: rewrite.** Keep only the table of kept and replaced files. Drop "board-only keeps `sim/diagram.json`", because C2b removes the hand-written diagram. I3 (merge on build) is an epic.
- **C8 free firmware tests: split into four.** Stubs (small). Console lines in the firmware step (small). A press-and-read command (medium). A moving clock and PWM trace (P295 option B, large). Do the first two now.

## New cards

- **P? — a passed run says it tested nothing about the must lines → the verdict line names it.** Need: G32. Done when: `run_scenario` prints the caveat in its last line and the log.
- **P? — `check_all` calls an unbuilt project "not asked for" → it says "nothing built yet".** Need: G6, walk 2 G1. Done when: the line names the missing `dist/`.

## Not checked

The plugin cache (G2), the `tools.json` steps (G34), `--match` output (G11, G14), the live look on a board, and the P391 and P479 plans.
