# P400 technology lens: P396 to P399 against the code

> The facts hold in part. Three fail: `--match` never offers the XIAO for press, no source holds the controls, and no test reads the store of the person.
> The four cards are two changes. P396 with P397 read the Wokwi board part. P398 with P399 read the diagram. They share one loader, not one table.
> Smallest first slice that fixes the walk: P396 for the button only, with "not checked" when the store file is absent. Smallest by code: the part-id check of P399.

## Findings

| # | finding | evidence | card or plan | proposal | severity |
|---|---|---|---|---|---|
| 1 | Holds: the XIAO part file is kept (1506 bytes, commit 4294fca6) and the board record names it. `problem()` checks no name. `run_scenario.py` has no dry run. `--pick` prints no simulation note. | `boards/xiao-esp32-c6.json:369-376`, `run_scenario.py:138-155` and `:237-242`, my `--pick --dry-run` run (row 8) | P396 to P399 | Keep the problem statements. | low |
| 2 | Only the XIAO has a kept Wokwi part, and no command keeps one. P229 called `store.keep` from Python by hand. `--fetch` keeps only PDFs and images. The FireBeetle has no `wokwi-board` entry. | `docs/discovery/2026-10-13-p218-deploy-and-board/bench/p229-xiao-board.md:42,213`, `parts.py:929-930`, `boards/firebeetle2-esp32s3.json:107`, grep of `boards/*.json`: one file. No entry in `data/tools.json`, no index in the store | P396 | Print "not checked" when the file is absent. New card 1 keeps it. | high |
| 3 | The test of P396 cannot read the store of the person. A unittest run sets a scratch `SPARK_HOME`. The repo holds no copy of the file. | `store.py:36-43`, `tests/test_needs.py:47` | P396 done-when | Test with a fixture part in a temp store. The licence of a verbatim copy is not checked. | high |
| 4 | The kept file is not strict JSON. Line 32 holds `/* Virtual pins */`, and `json.loads` fails at "line 32 column 5". | I ran `json.load` on the kept file | P396 | Strip `/* */` blocks, keep `//` inside strings. Put the comment in the fixture. | medium |
| 5 | Only two names are in doubt, not each name of `pins.py`. The allocator keys pins by silkscreen label, so a wired pin sits on a header pad. | `assign_pins.py:147,423`, the `pins` table of the record (D0 to D10 and bus aliases) | P396 | Check `onboard_button` and `onboard_led`. Word the reason as: no pin target and no element pin on GPIO9. The schema for buttons is not checked. | medium |
| 6 | "Nobody tried" holds. No scenario in the repo names `$gpio15` or a board pin. The answer needs one Wokwi run. The converter registry lists the pin. | grep of `expect-pin`: one scenario, `ledred5mm:A`. `tools/circuit-to-wokwi/dist/converter.mjs:3949`, `commands/build.md:254-256` | P396 | Split a spike (new card 2). Print the LED line as "not tried". | medium |
| 7 | `--match` does not offer the XIAO for press or light. Only `tactile-button` and `led-red-5mm` show. The XIAO shows under board. The record has `functions` null. | I ran `parts.py --match` on the needs of walk 2 in a temp store | P397, P389 | Build the `--pick` note now. Move the `--match` flag behind P389. | high |
| 8 | `--pick` prints three pick lines and store lines, nothing on the simulation. A note fits in `plan_pick`, beside the footprint note of F12. `tactile-button` is the first `--match` candidate for press. | my `--pick press=... light=... board=... --dry-run` run, `needs.py:339-342`, `parts.py:2118,2153` | P397 | One note per board pick that serves an `input/button` need. Name the first button candidate. | medium |
| 9 | Controls have no source in spark. The converter bundle has 0 hits for "controls". No record has a controls field. Wokwi lists controls as prose only. | `tools/circuit-to-wokwi/dist/converter.mjs` (grep count), `parts/tactile-button.json`, `parts.py:607-618` (chips only), WebFetch of `https://docs.wokwi.com/parts/wokwi-pushbutton` on 2026-10-23: heading "Automation controls", no JSON | P398 | Add a cited `controls` field to `simulation.wokwi`. Print "not recorded" for a record without it. | high |
| 10 | "No file lists them" is half true. `diagram.json` holds the ids and the wired pins. The mapping file holds the pin renames. Controls and unwired pins are missing. | `tools/circuit-to-wokwi/lib/emitters/wokwi.ts:150`, `emit_board.py:293-305`, `check_spine.py:509,555-556`, `commands/build.md:272` | P398 | Re-scope the card to the missing names. | medium |
| 11 | One diagram table cannot serve the pick. No `sim/diagram.json` exists before the build, and the idea and pick steps come first. | `check_spine.py:509`, walk 2 diary rows 3 and 5 | P397, P398 | Two inputs: the board part (P396, P397) and the diagram (P398, P399). One loader. | medium |
| 12 | A pin check against wired pins refuses a valid read. A board-alone diagram has `connections: []`, so `$gpio15` never shows as wired. | `check_spine.py:555-556` | P399 | Check part ids now. Check pins only against a complete pin list of the type. | medium |
| 13 | Every run test writes `diagram.json` as `{}` and names `tactilebutton`. A part-id check refuses them all until the fixture holds that part. | `tests/test_run_scenario.py:29-34,104` | P399 | Change `ProjectCase.setUp` to write a diagram with the three ids. | low |
| 14 | The repo has no YAML library. The steps are flow maps. A line reader finds `part-id:`, `name:` and `pin:` per step. | grep for `import yaml`: no hit. `with_ready_wait` in `run_scenario.py` reads lines | P399 | Read per step line, comments cut. Block style is not checked. | low |
| 15 | The dry-run claim holds. `--pick`, `--drawer-set` and deploy take `--dry-run`. Walk 2 ran no scenario with a wrong name, so the cost claim is a prediction. | `parts.py:1668`, `deploy.py:163`, `sim/scenarios/the-firmware-starts.scenario.yaml` | P399 | Add `--dry-run` as its own small step. | low |
| 16 | The P396 sentence reaches no later reader. `limits` has no hit in `look.py`, `project_image.py`, `deploy.py`, `deploy_gate.py` or `run_scenario.py`. | grep, no hits. `sim_project.py:75,118` | P396, P345 | Feed the existing note `WHAT-THIS-CANNOT-SHOW.md`. P345 carries it to the log and the look. | medium |
| 17 | The word "reach" already means reaching a board over USB. The cards use it for scenario names. | `reach.py:2`, `board_reach.py:2` | P396 to P399 | Use "drive" and "read" for a GPIO, "scenario names" for the table. The naming table of `developing.md` is not checked. | low |

## The four cards

Shared design. Two pure functions and one loader. The loader returns `None` for a part it cannot read, and each caller then prints "not checked".
- `board_limits(board, part)` looks for the GPIO of each onboard role in the pin targets and element pins of the Wokwi part. It reads no diagram, so it runs at pick time.
- `names_in(diagram, facts)` maps each part id to its type, wired pins and controls. It runs at build and before a run. Both names are working names.
- Both feed `limits` (`sim_project.py:75`), so P345 can carry them to the log. The stage status stays `ok`. The loader checks the file against the sha256 in the record.
- Cheaper fallback for P396: one cited sentence in `pin_roles.onboard_button`. It works on every machine, but a person writes it, so nothing finds the pin itself.

P396: rewrite and split. Why: the test cannot see the store (row 3), one board only (row 2), and the LED question needs a Wokwi run (row 6).
- The change: the build reads the Wokwi part of the board from the store. For the onboard button and LED it prints one line in the simulation stage and in `WHAT-THIS-CANNOT-SHOW.md`: reachable, not reachable or not checked.
- Done when: for walk 2, `board_alone` prints "ONBOARD_BUTTON (GPIO9): no scenario can press it. The Wokwi XIAO part has no pin and no element on GPIO9." Without the file it prints "not checked". Tests: `tests/test_sim_project.py` (fixture with the comment) and `tests/test_check_spine.py` near line 1175. No paid run, no board.

P397: rewrite, build after P396. Why: same function, second caller. The `--match` half has nothing to attach to before P389 (row 7).
- The change: `plan_pick` adds one note when a board pick serves an `input/button` need and the onboard button is out of scenario reach. The note names the first button candidate, today `tactile-button`.
- Done when: `parts.py --pick <project> press=xiao-esp32-c6 --dry-run` prints the note. The same flag shows in `--match` once P389 lists the board for press. Test in `tests/test_needs.py`, which patches `SPARK_HOME`.

P398: rewrite and split. Why: ids and wired pins exist already (row 10). Only controls are new, and they need a cited source (row 9).
- Part a, the change: the build prints each part id of `sim/diagram.json` with its Wokwi type, its wired pins and the controls its record names. A record without controls prints "controls: not recorded".
- Part a, done when: for a hand-made diagram of `mcu`, `tactilebutton`, `ledred5mm` and a record that names `pressed`, the list holds `tactilebutton` with `pressed` and `ledred5mm` with `A`. Test in `tests/test_sim_project.py`. No tsci, no node, no paid run.
- Part b: a cited `controls` field in `simulation.wokwi` of each library part that has controls.

P399: split in three. Why: the id check needs no new data. The dry run is a separate wish (row 15). Pins and controls need the table of P398 (row 12).
- Part a, the change: `problem()` compares each `part-id:` word of the steps with the ids of `sim/diagram.json`. A missing word, or a diagram that is not valid JSON, returns a problem.
- Part a, done when: a scenario with `tactilebuton` exits 2, names the word and lists `mcu, tactilebutton, ledred5mm`. The fake wokwi-cli leaves no seen-file, as at `tests/test_run_scenario.py:193`. The fixture at `:104` holds the three ids.
- Part b: `--dry-run` runs the free checks, prints "free checks passed: N steps" and exits 0 without a token. Part c: pins and controls after P398, only for a type with a complete list.

## New cards

1. `P? — a board Wokwi part is kept by hand on one machine → a command keeps it under the sha256 of the board record`. Need: P396 reads a file that only this store holds (P229, E3). Done when: on a fresh store one command keeps `wokwi-xiao-esp32-c6.board.json` and refuses a file with another hash. Overlap with the plan of P331 is not checked.
2. `P? — nobody knows if a scenario reads the XIAO LED on $gpio15 → a spike with a finding and a source`. Need: row 6. Done when: one `expect-pin` on `mcu` pin `$gpio15` ran once, with the yes of the PO, or a Wokwi page answers. A walk 2 run took 8 seconds. The finding names the log or the URL.

## Not checked

- Any Wokwi run: whether `expect-pin` reads `$gpio15`, and whether Wokwi takes block-style steps.
- Whether `--fetch` restores a missing kept file. `parts.py:463` says it does, but `to_fetch` skips known URLs.
- The licence of wokwi-boards for a copy in `tests/data`, and the schema of `board.json` for buttons.
- Where the tests of the `_op_pick` output live, and whether `tests/test_converter.py` skips without node.
- Not read: the vision, P323, P322, P297, P391, P395, the rows files, the naming table of `docs/guide/developing.md`.
- `assign_pins.py` in full, and the pins of Wokwi types other than the XIAO.
