# P484 onboard parts: rows

What the P484 build (one PR), its plan's two council rounds and the free Wokwi run found, and what the plan claimed
wrongly. Card: #663.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | Two PRs: the reader alone first | plan | rejected | council round 2 and refuter: a reader with no caller; one PR |
| 2 | `OnboardPartReader` beside `onboard_entries` in boards.py, and an `OnboardRole.part` field | plan, card | rejected | boards.py has no spare line (R1 969); the reader and its table `ONBOARD_PARTS` are in `scripts/onboard_parts.py`, keyed by role |
| 3 | One wired sentence, "a scenario reads that part, not the board's own" | plan | acted | council round 1: false for the devkit, which has a power LED and a WS2812 on pin 38; one sentence per role, about its GPIO only |
| 4 | Board pins: plain `GND` | plan | acted | not a devkit pin; the first `wokwi_power_pins` key that starts with GND (`GND1`), and the record's own pin key for the GPIO (`D13`, `D14`) |
| 5 | Part pins from a table in code | plan | acted | from each part record: its first need's pin, its `power` entry on the ground rail, and `simulation.wokwi` for the Wokwi type, pins and attrs |
| 6 | Board-only builds need Node now | plan risk | acted | the converter runs only when the reader gives a part; the XIAO (no stand-in) keeps the hand-written diagram and needs no converter; a test runs it with no node on PATH |
| 7 | The reader wires any board's LED and button | plan | acted | only a stand-in board (`wokwi_is_stand_in` true): a Wokwi part that is the board itself already holds its own LED and button |
| 8 | Reversed polarity: the return pin to 3V3 | plan | raised | not built: a part whose `active_level` is not the level its record is wired for (an LED lit by a 1, a button that reads 0) is left unwired and keeps P483's sentence. A later card when a board needs it |
| 9 | The part dict carries `name` from the role's label | card | rejected | nothing reads it; the diagram id is the role (`onboard_led`), which a person reads in Wokwi |
| 10 | `design.onboard_parts` and `sim_project.onboard_netlist` | plan | rejected | one module: `onboard_parts.make_converter_input` returns the files as data, and `check_spine.board_alone` writes them (rule T1: only an Adapter writes a file) |
| 11 | check_spine.py at 1030 lines, net 0 | plan, hard limit | acted | one converter call `convert` for `run` and `board_alone`; the stale CONVERTER_PATHS comment ("not part of this plugin yet") pruned to two lines; 1030 |
| 12 | boards.py net 0 | plan, hard limit | acted | the `gpio_limits(board, checked)` wrapper folded into `onboard_limits`; `gpio_limits` takes a definition already read and `wired`; 969 |
| 13 | `wokwi-mapping.json` was spelled twice in check_spine | prune sweep | acted | `sim_project.MAPPING_FILE`, used by check_spine and onboard_parts |
| 14 | The build line says PWM levels are not checked | council | raised | not built: the LED's limit says a passed run shows the firmware drove GPIO21, not that the LED lights; the LED record's own stand-in sentence (brightness) is not printed for an onboard part |
| 15 | The board-only render line still says "nothing to wire, so no board was built" | found | raised | true of the PCB, which is not built; with wired parts it reads oddly. check_spine has no spare line for a second wording |
| 16 | A board-only build without wired parts overwrites a kept diagram, as before P484 | found | raised | only the converter merges; the XIAO path writes the board-alone diagram |
| 17 | The free Wokwi run on walk 3 (scenario: wait ready, wait "effect breathe", press 100 ms, release, wait "effect heartbeat") | run | verified | the firmware printed `effect heartbeat` after the press, so the press reached GPIO47 through the wired `onboard_button`; the run still timed out (exit 1): the firmware moves on the press, so it printed the line during the 100 ms delay, before the last `wait-serial` began to listen. A scenario that waits right after the press, before the release, would pass; one run only, as agreed |
| 18 | The mutation row on cli.ts is caught by the bundle's sha test, not by behaviour | found | raised | the Python suite runs the bundle; the converter's own bun tests cover `--netlist` but mutate.py does not run them |
| 19 | Plan fact: board_alone at check_spine.py:571-590, run returns at :385-389 | plan | verified | read in the code at origin/main |
| 20 | Plan fact: led-red-5mm is wokwi-led (A, C), tactile-button wokwi-pushbutton (1.l, 2.l) | plan | verified | the records' `simulation.wokwi.pins`: A to A and K to C; A to 1.l and B to 2.l |
| 21 | Plan fact: the converter reads only circuit.json | plan | verified | cli.ts called `buildNetlist` on `--circuit` alone; `--netlist` now reads a JSON netlist through `readNetlist` |
| 22 | Plan fact: P482 copies the kept diagram only in run() | plan | verified | `convert` now does it for both callers |
