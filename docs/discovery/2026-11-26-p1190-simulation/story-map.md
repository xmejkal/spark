# Story map
<!-- Proposed, not applied: this map stays here until the decider confirms it; nothing changes the product's own
map file. -->
**Status:** proposed, not applied <!-- REQUIRED:map-status -->

## Backbone
Know what can run → Check free → Write the scenario → Run → Read the result → Hand over <!-- REQUIRED:backbone -->

## Slices
The slices are the architect's proposal (council/architect.md §10). The item numbers point to items.md.

| slice | activity | story | job | tag | proof |
| --- | --- | --- | --- | --- | --- |
| 0 walking skeleton <!-- REQUIRED:slices --> | Know what can run | A board that no simulator covers ends the simulation stage `skipped` with a reason, and the build record's top status follows (item 1) | J2 | E ★C1 ★C2, H the architect | the clock's `.spark/build.json` after a rebuild |
| 0 walking skeleton | Check free | `check-firmware`: the import check and the project's own tests in one Operation, with no `sim/` needed (item 2) | J1, J3, J6 | E ★C17 ★C18 | `check-firmware --json` on the clock |
| 0 walking skeleton | Check free | The page's Simulation step shows one coverage line and the free checks' result (item 3) | J1, J2 | H the architect | the clock's page |
| 0 walking skeleton | Read the result | The "what this simulation cannot show" list prints only after a run (item 4) | J2 | E C23 | a deploy with no run |
| 0 walking skeleton | Know what can run | The FireBeetle 2 C6 on Wokwi's ESP32-C6 DevKitC-1 as a stand-in (P999 #1455, beside the slice) | J2 | E ★C11 | the clock's build |
| 1 the seam | Run | `run-scenario` as an Operation, the paid run a `needs_yes` step (P1078 #1582) | J6 | E ★C15 | `run_scenario.py --json` |
| 1 the seam | Run | `Simulator`, `WokwiSimulator`, the Fake and the table from contract to Adapter, no behaviour change (item 6) | J7 | H the architect and the tech lead | the goldens hold, one selection site |
| 1 the seam | Read the result | The run record names its simulator and its grade (item 7, P308 #374) | J1, J6 | E P308 #374 | a log header |
| 2 the paid run made visible | Run | The `simulator` role, on or off, as the one setting (item 8, replaces P410 #536) | J3 | E `tool_finder.py:274-307` | the command says the setting |
| 2 the paid run made visible | Run | The cost and the time cap before the yes (item 9, with P413 #539) | J3 | E ★C10 | the question before a run |
| 2 the paid run made visible | Write the scenario | `SimulationControls`, and the scenario shown as sentences with the values and ranges it sets (item 10) | J4 | E ★C8 | the page for the VL6180X project |
| 2 the paid run made visible | Read the result | The result on the page, the caveat in the verdict's line (item 11) | J1, J6 | E council/user.md USER-8 | walk2's "only the start" reads so |
| 3 models | Know what can run | A community chip by reference in wokwi-cli, and its licence rule (item 12, replaces P409 #535) | J5 | E ★C20 | one free run of a referenced chip |
| 3 models | Write the scenario | A live value in Wokwi's editor for a spark project (item 13) | J4 | H | a spike finding |
| later | Check free | The clock's `main.py` loop on the stand-in with a virtual clock (item 14, parked until A1's test) | J1, J2 | E ★C19 | a spike finding |
| later | Hand over | Gate A's evidence row (item 15, under P79 #16) | J1 | E ★C14 | the "On the board" card |

## Delta to the product's map <!-- REQUIRED:spark-process:map-delta -->
Proposed, not applied. `scrum/STORY_MAP.md` journey step 8 reads `| 8 | Simulate | check_spine → Wokwi (paid minutes) | — |`.
The proposed row is: `| 8 | Simulate | check-firmware (free: imports, the project's own tests), then run-scenario by the chosen simulator (Wokwi today, paid minutes after a yes) | a board no simulator covers reads skipped with its reason |`.
<!-- EXTEND:map -->
