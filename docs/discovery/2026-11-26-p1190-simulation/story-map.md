# Story map
<!-- Proposed, not applied: this map stays here until the decider confirms it; nothing changes the product's own
map file. -->
**Status:** proposed, not applied <!-- REQUIRED:map-status -->

## Backbone
Know what can run → Check free → Write the scenario → Run → Read the result → Hand over <!-- REQUIRED:backbone -->

## Slices
The slices follow the architect's proposal (council/architect.md §10), in the order the delegated council set (D3). The item numbers point to items.md.

| slice | activity | story | job | tag | proof |
| --- | --- | --- | --- | --- | --- |
| 0 walking skeleton <!-- REQUIRED:slices --> | Check free | `check-firmware`: the import check and the project's own tests in one Operation, with no `sim/` needed (item 2) | J1, J3, J6 | E ★C17 ★C18 | `check-firmware --json` on the clock |
| 0 walking skeleton | Check free | The page's Simulation step shows one coverage line and the free checks' result (item 3) | J1, J2 | H the architect | the clock's page |
| 0 walking skeleton | Read the result | The "what this simulation cannot show" list prints only after a run (item 4) | J2 | E C23 | a deploy with no run |
| 0 walking skeleton | Know what can run | The FireBeetle 2 C6 on Wokwi's ESP32-C6 DevKitC-1 as a stand-in (P999 #1455, beside the slice) | J2 | E ★C11 | the clock's build |
| 0 walking skeleton | Check free | Spike: do `wokwi-cli lint` and `chip compile` run with no token and no minutes (item 5, P1211 #1760) | J3 | C24, research-wokwi.md §5 | a finding |
| 0 walking skeleton | Know what can run | `chips/wokwi-api.h`'s licence read and cited, or the file fetched at build time (item 20, P1225 #1774) | J5 | C26 | the header's source and licence |
| 0 walking skeleton | Hand over | The vision's v0.10 line reads "where a simulator covers the board" (item 17, P1222 #1771, the PO's file) | J2 | D12 | `scrum/VISION.md` |
| 1 the seam | Run | `run-scenario` as an Operation, the paid run a `needs_yes` step (P1078 #1582) | J6 | E ★C15 | `run_scenario.py --json` |
| 1 the seam | Run | `Simulator`, `WokwiSimulator`, the Fake and the table from contract to Adapter, no behaviour change (item 6) | J7 | H the architect and the tech lead | the goldens hold, one selection site |
| 1 the seam | Read the result | The run record names its simulator and its grade (item 7, P308 #374) | J1, J6 | E P308 #374 | a log header |
| 1 the seam | Know what can run | The flip: a board that no simulator covers ends the stage `skipped` with a reason, after the PO's yes to Q11 (item 1) | J2 | E ★C1 ★C2, D3 | a fixture board's build record, and an old record still counted as done |
| 2 the paid run made visible | Run | The `simulator` role, on or off, as the one setting (item 8, replaces P410 #536) | J3 | E `tool_finder.py:274-307` | the command says the setting |
| 2 the paid run made visible | Run | The cost and the time cap before the yes (item 9, with P413 #539) | J3 | E ★C10 | the question before a run |
| 2 the paid run made visible | Write the scenario | The simulation editor: the values, how each part and the chip are simulated, and the steps, in spark's words that each simulator turns into its own (item 10, D16) | J4, J7 | E ★C8, D16, research-wokwi-settings.md | the page for the VL6180X project |
| 2 the paid run made visible | Read the result | The result on the page, the caveat in the verdict's line (item 11) | J1, J6 | E council/user.md USER-8 | walk2's "only the start" reads so |
| 3 models | Know what can run | A community chip by reference in wokwi-cli, and its licence rule (item 12, replaces P409 #535) | J5 | E ★C20 | one free run of a referenced chip |
| 3 models | Write the scenario | A live value in Wokwi's editor for a spark project (item 13) | J4 | H | a spike finding |
| after v0.10 | Run | Spark's own simulator, reuse first (item 18, P1223 #1772, D15, D18) | J1, J2, J7 | D15 | the spike's finding, then one walk project on it |
| 1 the seam | Check free | The spike, before the seam's plan (D22): do esp-emulator or esp32sim boot spark's MicroPython C6 image, and can a host drive it (item 19, P1224 #1773, replaces item 14) | J1, J2 | ★C12, A10 | a finding with sources |
| 2 the paid run made visible | Run | A paid-run policy: never, ask, only for a version marked important, or always, and a threshold that warns (item 16, D13) | J3 | D13 | an unmarked version gets no paid run, and the policy is named |
| 1 the seam | Hand over | Gate A: the free condition "no failed run on the current image" and the evidence row (item 15, under P79 #16, D10) | J1 | E ★C14, D10 | the "On the board" card |

## Delta to the product's map <!-- REQUIRED:spark-process:map-delta -->
Proposed, not applied. `scrum/STORY_MAP.md` journey step 8 reads `| 8 | Simulate | check_spine → Wokwi (paid minutes) | — |`.
The proposed row is: `| 8 | Simulate | check-firmware (free: imports, the project's own tests), then run-scenario by the chosen simulator (Wokwi today, paid minutes after a yes) | a board no simulator covers reads skipped with its reason |`.
<!-- EXTEND:map -->
