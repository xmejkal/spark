# P400 UX lens: what the person saw in walk 2, and where each warning goes

> The person heard "no button" about the Wokwi model and read it as a wrong name. The name in spark is right. Every line about a board part must say which board it means.
> The pick is the first place for the fact. The build answers at once and for free, and it has a slot that the board-alone path leaves empty.
> "Passed" has no object, so the run, the look and the store show a pass over a run that sent no input. Before an erase, the question names neither what it replaces nor who holds the board.

## Findings

| # | finding | evidence | card or plan | proposal | severity |
|---|---|---|---|---|---|
| 1 | One name covers two boards. The person says "button" and means the real B button. Spark said "no button" about the Wokwi model and never said which board it meant. | Diary, "The button question" 2 to 4. Board record `pin_roles.onboard_button` is GPIO9. Wokwi part in the store: 0 hits for button or boot, and D9 targets GPIO20 (grep I ran). | P396, P397 | Each line names both: on your board, and in the Wokwi model. Say that GPIO9 is the B button and that pad D9 is GPIO20. | high |
| 2 | The pick is the first place the person can act. The build answers at once, for free, in about one second. Its slot for this fact stays empty on the board-alone path. | `check_spine.py:558` passes `()` as limits. The slot is at `:576-579`, shown at `journey.md:363-366`. Diary step 5: the verdict and the stage line name no limit. | P396, P397 | Fill the slot from the board record. Add the fact to the verdict line, as the `unserved` clause does. Pick, build, run and look use one sentence. | high |
| 3 | "Passed" has no object. The run waited for "ready" and sent no input. The log, the look and the store all say passed. | `run_scenario.py:104`, log header `verdict: passed`, `board_envelope.py:76`, store record `"simulation": "passed"`. The scenario file has one step. | P345 (#440, idea I5) | Keep the value `passed` for code. Print after it what the run did and sent. See the lines below. | high |
| 4 | The text look prints no simulation line. The JSON that Claude relays, the board log and the store say `passed`. The person who types yes sees nothing on it. | `board_look.py:233-250` has none. `board_envelope.py:76` and `deploy_service.py:43` have it. `deploy.py` prints the same `report_lines` before the question. | P345 | Add the coverage line to `report_lines`. The look, the deploy and the JSON notes then show one text. | medium |
| 5 | A must line that no scenario names cannot block a deploy. The bench test needs the deploy first. A block is a circle. | AGENTS.md: a `could-not-run` is not a pass. `outcomes.py` `status_of` turns any `unchecked` into `could-not-run`. The person pressed B after the deploy. | P345 | Put the line in `notes`, never in `unchecked`. After `ready seen`, print `now test on the board`. A bench result closes it (N3). | high |
| 6 | The person learned of the gap after a paid run. The free check before the run is the cheapest place for the line. | #513 body. `run_scenario.py` docstring: free checks come first. Diary G26: no dry run. | P399 | Give `run_scenario.py` a dry run. It prints `sends no input` and the must lines no scenario names. Claude reads it before the ask for a paid run. | medium |
| 7 | P397 steers to a button on a pad. The PO soldered no pins to this XIAO. The honest first choice is the bench test. | #506 body, 2026-10-22. #513 "Done when". | P397 | Name `test it on the board` first. Name the pad button second, and say it needs a wire to a pad. | medium |
| 8 | G29. The deploy question names what it writes and not what it replaces. The look holds the MAC, and the store keeps each deploy by MAC. | `deploy_gate.py:100`. Store `~/.local/share/spark/boards/8c-bf-ea-cc-97-70.json`: the last deploy before walk 2 is blink-c6, 2026-10-19T09:24:50+02:00. | N1 | One look line and one phrase in the question. Say "store record", because another tool can flash the board. Print a time with no zone as stored. | high |
| 9 | The hold question. No tool at the deploy says that reaction-game holds the XIAO. A hold is a drawer reservation. It says nothing about the firmware. | `used_in` count is 0 in `deploy.py`, `deploy_service.py`, `look.py`, `board_look.py`, `check_spine.py`, `run_scenario.py`, `board_envelope.py` (grep I ran). Diary O14. | N1, P391 | Add the hold to the look as a warning, like the others. The question repeats it. A deploy grant skips a look with a warning (`commands/deploy.md`, step 3). At `--match`, print "free 0, held by reaction-game" (`parts.py:2115-2117`). | high |
| 10 | G27. The page tells Claude to omit `--port` with one board. The next step of the look and the terminal line always name it. | `commands/deploy.md:22,40`. `board_envelope.py:36-38`. `deploy.py:103`. | none, words only | Change two page sentences (below). The printed line stays. | low |
| 11 | The one warning at the board-alone stage was false, and the true warning was absent. A false warning teaches the person to skip the stage. | `check_spine.py:252-255,556-558,573-575`: the diagram has no connections, so the line always prints. Wokwi part line 12: `USB_SERIAL_JTAG`. Diary G18. | P396 | Print the serial line only for a part that needs wires. Same stage, same change. | medium |
| 12 | Four checks read "not asked for" twice. The cause is that nothing is built. The label hides why, and a skipped check is not a pass. | Diary G1 and G22. Code not read. | none | Write "not run: nothing built yet", or "not run: this project has no circuit". | low |

### The lines to print (each place, at most two lines)

```
PICK  parts.py --match, under the XIAO (its about slot)
      own parts: user LED (GPIO15) and B button, BOOT (GPIO9). Pad D9 is another pin, GPIO20.
      The Wokwi model of this board lists no B button, so spark knows no way to press it in a simulation. Test the press on the board.
PICK  parts.py --pick dry run, press need
  press: xiao-esp32-c6, its B button. Spark knows no way to press it in a simulation: test it on the board.
  Other choice: a tactile button wired to a pad. A simulation presses that one.
BUILD check_spine.py --keep ., the simulation stage and the verdict
             XIAO ESP32-C6: the Wokwi model lists no B button and no pin on GPIO9 (ONBOARD_BUTTON), so spark knows no way to press it. Pad D9 is GPIO20.
  the chain runs end to end for the board alone: nothing to wire, so no board was built. The simulation cannot show the B button.
RUN   run_scenario.py, before the log line
the-firmware-starts.scenario.yaml: passed. It waited for "ready" and sent no input.
No scenario names the must line "Pressing the button lights the LED". Spark does not call it tested.
LOOK  look.py, and deploy.py before its question
  simulation  passed. It waited for "ready" and sent no input.
  to test     "Pressing the button lights the LED": no scenario names it. Test it on the board after the deploy.
  reaction-game holds this board in your drawer. deploy.py will ask you to accept it.
  last put    blink-c6, 2026-10-19 09:24 +02:00 (the store record, not read from the board)
ASK   deploy question
you accept: reaction-game holds this board in your drawer. erase ALL of this board's flash (spark last put blink-c6 on it) and write <image>? type yes to go on:
AFTER deploy.py, once "ready seen" is printed
  now test on the board: "Pressing the button lights the LED"
```

At once: the build, because it is free, repeatable and has the slot. First: the pick. Repeat: the run and the look. One source feeds all four.
Terms, one word for one thing. "B button": the word of the person, B on the silkscreen. "Wokwi model": the simulator copy of the board. "cannot show": a limit of the model. "no scenario names": a must line with no scenario. "test it on the board": the bench step.
G27, `commands/deploy.md:22`: "Run the look with no `--port` when one board is on USB. The deploy line it returns names the port it read: use it as printed." At `:40`: "with the `--port` that the look printed".
P297 sets the direction: the core prints, Claude relays, the person reads. So each warning lives in the command output (`finding.md:151-152`, and the `not_kept` answer at `:67-68`), not in the prose of Claude.

## P396 to P399

- **P396 (#512): rewrite.** The person sees it: partly. The "Done when" speaks in code names, with no place and no exact words. The LED question is open research, so it becomes a spike (N2).
  - The change: the build reads the Wokwi part from the store. Each own part of the board record that the model lacks goes into the `what it cannot show` block, the verdict line and `sim/WHAT-THIS-CANNOT-SHOW.md`. The false serial line goes.
  - Done when: on the walk 2 project, the build prints the BUILD lines above. The file holds the same fact. A test reads the part file in the store.
- **P397 (#513): rewrite.** The person sees it: yes, it states what two commands print. The other choice goes against what the PO said about pins (finding 7). It builds on P389 (#504) and on the reader of P396.
  - The change: `--match` and the `--pick` dry run print the limit with the PICK lines above. The bench test comes first and the pad button second.
  - Done when: for the walk 2 press need, `--match` prints the two PICK lines under the XIAO, and the dry run prints the press line. Both use "B button", "Wokwi model" and "test it on the board".
- **P398 (#514): merge into P399.** The person sees it: no. Nobody but Claude reads part ids and controls. The list is the data for the check of P399 and its error text. For walk 2 it reads `mcu`, pins D0 to D10, no controls.
- **P399 (#515): rewrite, and take P398.** The person sees it: partly. The text names the content of the message but gives no words, and the person sees nothing before the paid run. The title names controls and pins, and the text names only part ids.
  - The change: `run_scenario.py --dry-run` runs the free checks. It lists the part ids, controls and pins of `sim/diagram.json`. It checks the names in the scenario and prints what the scenario sends.
  - Done when: on the walk 2 project it prints "sends no input" and the part id `mcu`. A misspelled part id exits 2 and names the word and the ids that the diagram has. On `tests/data/breadboard/button-light` it lists `tactilebutton` with `pressed` and `ledred5mm` with `A`. A fake wokwi-cli shows that no run started.

## New cards

- `P? — the look and the deploy question do not say what the erase replaces or who holds the board → the look prints the hold and the last deploy, and the question repeats both` (N1). Need: G29, O14, hold answer 6. Done when: reaction-game holds the XIAO, and the store is the one of 2026-10-23. Then `look.py` from walk2 prints the `holds this board` and `last put` lines above. The question starts `you accept: reaction-game holds this board in your drawer.` With no hold and no record, it prints `no record of a spark deploy here` and no hold line. A stored time with no zone prints as stored, with `zone not stored`.
- `P? — nobody knows if a scenario can read the LED through the hidden pin $gpio15 → a finding from one paid run` (N2, label spike). Need: P396 asked it inside "The change". Done when: a finding holds the scenario text and the log, and says whether `expect-pin` on `mcu` pin `$gpio15` reads the LED. The PO says yes to the run first.
- `P? — a passed bench test is nowhere in spark → one command writes the bench result of the person against a must line, and the look prints it` (N3). Need: walk 2 step 12, the person pressed B and said it works. Done when: after that word, the command writes the must line, who, when with zone and "bench" to the board record. The next look prints `tested on the bench by petr, 2026-10-23 06:55 +02:00` and no longer prints `to test`.

## Not checked

- No Wokwi run, no deploy and no web lookup. The claim "no way to press the B button" comes from the part file. No run tried a press, and I did not check whether Wokwi lets a scenario press a built-in button that the file does not list.
- Not checked: whether wokwi-cli accepts an extra key in a scenario, which idea I5 needs. Not checked: whether a scenario can read the LED. Not checked: how a hold maps to one board when the person owns two. The count is 1 here.
- Not read: `VISION.md`, P323, P322, the design of P391, the rows files and the naming table. Open question: does P391 already make the look read holds? Not checked: the state of P389.
- Not read in code: the "not asked for" label (finding 12). Not checked: the silkscreen name of the user LED. The lines use the words of the board record.
