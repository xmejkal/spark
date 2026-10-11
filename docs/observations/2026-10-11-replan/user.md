# User lens: hobbyist, FireBeetle S3, breadboard, button+LED, then a soil sensor

Tags: [E] evidence (card, file, output), [H] hypothesis. Read from origin/main: README.md, docs/guide/journey.md, commands/build.md.

## 1. The journey, 8 stages, each with a done-test

1. Install: `/plugin install`, `/spark:init`, `/spark:setup`. Test: `tools.py --status` exits 0 on a clean machine and says how to make the Wokwi token. Stalls: token is "only you can make" [E journey.md]; no Windows lines [E data/tools.json].
2. Idea to parts: words to `requirements.json`, run in Claude Code, not by scripts. Stall: the drawer/idea conversation was never run [E journey.md "not run"].
3. Build to sheet: a person wires `breadboard.md` right first time. Stalls: never wired by a person [E brief]; headers soldered? unsaid [H]; sheet's deep-sleep notes contradict its own pull-up wiring [E journey.md sheet].
4. Checks: button-light gets exit 0 or one plain line per gap. Stall: exit 2, `!` lines about rails never built [E brief, P140 #74].
5. Firmware: importable `main.py`, prints "ready"; Mac check passes (released 0, pressed 1). Stall: `/spark:build` does not write `pins.py` (separate `assign_pins.py` run) [E check_spine.py has no emit-pins]; no `machine` stand-in [E P59 #7].
6. Simulate: one command, pass line. Stall: three raw commands, hand scenario, CI token [E build.md:184-196].
7. Deploy: one command; pressing the button lights the LED on the desk. Stall: nothing exists [E P192 #144]; wrong MicroPython build for the PSRAM variant [H].
8. Second idea (soil sensor) through 2-7 on the same board; then PCB/GLB on request from current requirements. Stalls: board "held by button-light", pick refused [E journey.md]; no soil record, and PCB-only facts (footprint) stop a breadboard pick [E journey.md, P165 #102]; stale `board.tsx` is kept [E build.md, P110 #44].

## 2. First slice, ordered by what blocks soonest

| # | item | value proven by | size | after |
|---|---|---|---|---|
| 1 | README first screen (P182 #128, cut) | first 25 lines name breadboard sheet, firmware, simulation, flash; PCB/3D "on request" | S | - |
| 2 | Cold walk of button-light in Claude Code, words only, wired by the PO (P100 #6 reframed + P191) | every guess becomes a card | M | - |
| 3 | `/spark:build` writes `pins.py`; sheet drops sleep notes unless the project sleeps; adding a part never moves a wired pin, or the sheet flags it [H: placement depends on the signal set, assign_pins.py:289] | test on button-light then +soil | S | - |
| 4 | check_all verdict for button-light (P140, P118) | exit 0 or plain reasons | S | - |
| 5 | Ship the `machine` stand-in plus one Mac command (P59 minimal; P74 later) | LED reads 0 then 1 | S | 3 |
| 6 | Generated scenario plus `/spark:simulate`, token checked first (P130 #64, P116 #50) | pass line printed | M | 3,5 |
| 7 | Deploy (P192 #144 with P189 #138 and B21 SKU) | LED lights on the desk | M | 6 |
| 8 | A breadboard project holds no board, or `--release` | second project picks the FireBeetle | S | - |
| 9 | Soil sensor: P165 minimal (breadboard ignores footprint/outline) plus library record with slider stand-in | sheet, sim pass, flash | M | 7,8 |
| 10 | PCB/GLB on request reflect current requirements (P110 #44 cut) | glb shows both parts | S | 9 |

Finish first: pause P158 #94 at its last merge (no new C items); P100 #6 becomes item 2. Out of Ready: P186 #135, P187 #136, bin P58 #5, P73 #2, B8 #3. Stays: P189 #138. Enters Ready: 1-5. Before any stranger: P147 #81 (version never changes, fixes never arrive) [E card].

## 3. Merge, split, narrow
P125 #59 into P165; P116 #50 into item 6; P77 #13 narrowed to button-light, then it is the regression run; P132 #66 split, install only; P79 #16 is the umbrella of 1-10.

## 4. Prune: leaves the active backlog (parked as later)
- Store redesign, nothing in a button+LED run touches it: #96, #17, #123, #93, #99, #82, #114, #118, #119, #19, #21, #22, #23.
- Team tooling, invisible to a hobbyist: #27, #28, #30, #97, #103, #108, #111, #113, #121, #101; #39 only if the push gate blocks.
- Motors, I2C, fab, PCB depth, library growth: #70, #89, #60, #9, #78, #79, #86, #87, #54, #63, #41, #42, #45, #43, #76, #85, #12, #10, #55, #83, #84, #61, #62, #5, #134, #186, #187, #188.
- Bin, second proof after the basic journey: all except B31 #26 (its sim prints nothing, same cause as P190) and B21 #15 (SKU for item 7); B25/B26/B28 stay in Idea.

## 5. Ask the PO
1. Is the Wokwi token required for a hobbyist's "passes in simulation", or is the Mac stand-in the free pass?
2. Mac only for v1?
3. Your FireBeetle: N16R8 or N4, headers soldered?
4. May a breadboard project stop holding the board?
5. May P158 pause?
