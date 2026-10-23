# P400 AI lens: where the AI went wrong in walk 2

> No field of spark's output says what a passed run tested. In walk 2 only the agent's care kept `passed` from becoming a false test claim.
> The AI made one wrong claim: at 06:45 and 06:53 it said the erase replaces reaction-game's firmware (O14). Its other near errors came from the word `passed`.
> The token premise is false: the Wokwi part is 1,506 bytes and the diagram is 219 bytes. Docs and turns cost the tokens.

## Findings

| # | finding | evidence | card or plan | proposal | severity |
|---|---|---|---|---|---|
| 1 | O14. Spark printed a hold (`used_in {"reaction-game": 1}`) and nothing on the board's firmware. The AI read the hold as the firmware and said so twice. The store record lists 17 deploys: 12 blink-c6, 4 button-light, 1 walk2. None is from reaction-game. | Diary O14, G29 and hold answer 6 (an inference from code, not a run). Transcript text at 06:45 and 06:53 (the diary says 06:52). Record `boards/8c-bf-ea-cc-97-70.json`, my count. | none | N1. Rule for the AI: read the board's store record before you say what an erase destroys, or write "not checked". | high |
| 2 | G23 and O12. Spark printed `passed` for a run whose only step waited for `ready`. The AI did not claim a press test and noted the gap. But the one word reaches the log header, the look's `data.simulation`, the board log, `spark.json` on the board and the store record. | `run_scenario.py:103-104` and `:259-260`. `image_evidence.py:17-18`. `board_envelope.py:76`. `board_facts.py:23-28`. Board log line 3. | P345 (#440) | Fields A and B below. | high |
| 3 | Nothing in the output tells an agent what the pass covers. The text look prints no simulation line, and only `--json` has `data.simulation`. A passed run adds no caveat to the yes question. Only the `none` branch does. | No "simulation" text in `board_look.py` (my grep). `image_evidence.py:20`, `:41` and `:107`. | P345 | Field D. | medium |
| 4 | The rules have a hole. agents.md says a run that exits 2 is not a pass, and neither is a `skipped`. No item says a `passed` run covers only what its scenario asserts. build.md says "a pass here is not a bench", which is about stand-ins. | `agents.md:574` and the list `:572-730`. `build.md:283`. The project's `AGENTS.md`, section "spark". | none | N4. Docs only, no code. | high |
| 5 | The gate takes the ready line alone. `with_ready_wait` puts `wait-serial: ready` into every scenario, and wokwi-cli exit 0 is `passed`. A scenario that names a must line (I5) is still the author's claim. | `run_scenario.py:66-84` and `:103-104`. | P345 | Count the steps (field A). Print the count beside each named must line. | high |
| 6 | I5 needs a reader that does not exist. No script reads the brief's `must` list. Only `init_project.py:218` writes it. | My `grep -rn '"must"' scripts/*.py`. | P345 | Later, not MVP: one small class reads `must` and `goal` (G6 needs it too). Field A comes first. | medium |
| 7 | G18. Spark printed "no serial monitor is wired" with two causes. The AI called it a false alarm and gave one cause, `serialInterface`. But the log names Wokwi CLI v0.27.1, the tools list installs 0.28.0, and build.md says Wokwi stopped wiring serial at 0.28.0. The AI did not weigh that. The warning also fires for every board-only build. | Run log line 21. `data/tools.json:51`. `build.md:275-277`. `check_spine.py:542-558`: the diagram has `"connections": []` and skips the converter. | none | N2. A false alarm teaches agents to skip warnings, and `agents.md:475` says to relay them. | medium |
| 8 | The AI told the person at 01:14 that no simulation can press the button. Then it spent a paid run on a start-only scenario, to get the passed log that the gate needs. The 01:14 text I read names no `--no-simulation` route (P337), which exists for such firmware. | Transcript text at 01:14, tool calls 154-156, 169 and 170. Scenario lines 2-4. `deploy.md:67-73`. | P397 | Before a paid run, the AI names both routes and the label each one writes: `passed` or `none`. | low |
| 9 | The only test of the press before the bench left no trace. `press_test.py` sits in the session's scratch folder, prints three lines and asserts nothing. The AI judged it by reading the print. | Scratch file `press_test.py:10-14`. Diary row 16 and G23. | none | N3. | medium |
| 10 | The build's `limits` line (P37: a green scenario must not read like a bench result) is empty for a board-only build. | `check_spine.py:538` against `:558`. `sim_project.py:118-123`. | P396 | Fill `limits` for the board alone (field C). | medium |
| 11 | The button-name question: the AI answered right. `ONBOARD_BUTTON = 9` cites the schematic. The part maps D9 to GPIO20 and has no GPIO9. The doubt came from "no button" meaning the part. The web read was a 620-character summary. | `firmware/pins.py:6`. Board record line 163. Store part file. My `curl` hash on 2026-10-23: same SHA-256 as the store copy. | P398 | Write "Wokwi's part has no button". Check a web file with `curl` and a hash. | low |
| 12 | Token cost. Reading the part and the diagram took 3 calls and 2.5 KB at 01:12 and 01:13. All 216 calls returned 207 KB, about 52k tokens (my estimate). The heaviest hour was 01:00 with 28 calls and 60.7 KB. | Scan of the walk 2 transcript (tool names and result sizes). `wc -c` of both files. | P396, P398 | Do not justify these cards by tokens. They save turns and errors. Lines 1 to 63 of `run_scenario.py` (docstring and epilog) are 3.4 KB, and the AI read 12.7 KB of its source. | low |
| 13 | Word clash. P396 to P399 say a scenario "reaches" a pin. `reach.py` and `board_reach.py` use "reach" for a board on USB. | `reach.py:2`, `board_reach.py:2`, `developing.md:283`. | P396 to P399 | Use `limits` (the word `check_spine.py` has) and "drive" or "read". | low |
| 14 | S1. The AI wrote the goal into the brief by hand and did not say that no script gives it to idea. The person waited 8 minutes. | Diary S1, G4, G6. | none | The AI says what a step does not do. | low |

## What stops a false test claim today

- The log header is read by scripts, never by the firmware, so a firmware cannot forge a pass (`run_scenario.py:213-214`). The deploy gate needs a passed log that names this image's SHA-256 (`deploy.md:59-61`).
- Nothing checks what the scenario asserted. No envelope carries it: `run_scenario.py` has none, and `look.py` has only `passed` or `none`. Its `unchecked` holds unknown fields and a missing token.
- What the AI got right: it never supplied the yes. It gave the person the deploy line word for word. It wrote the scenario's limit into the scenario file, but scripts do not read comments.

## Fields that fit agents.md

The contract has three places. `unchecked` holds what was asked and not done. It sets the exit code to 2 (`agents.md:122`, `outcomes.py:46`). `data` holds facts. `limits` holds what a stand-in cannot show.

- A. `run_scenario.py` gets `--json` (the P213 pattern) and a closing text line. `data.run` is `{"steps": {"set-control": 0, "expect-pin": 0, "wait-serial": 1}, "inputs": [], "checks": ["ready"]}`. Spark counts it from the scenario text (`run_scenario.py:145`). The log header gets one `steps:` line.
- B. `look.py` and `deploy.py` get `data.simulation_run`, the same object read from the passed run's header (null with `--no-simulation`). They add one `unchecked` item for each must line that no scenario names. Its sentence: "no scenario tests the must line 'Pressing the button lights the LED': the passed run set no control". Its fix: "tell the person the bench is the test". An `unchecked` item has no `subject` (`agents.md:398`). The token stays and `next` keeps the deploy step. The grant must refuse it as it refuses an unknown field (`agents.md:715-716`), so the question names the line. The PO decides: `unchecked` or a note.
- C. `check_spine.py --json` gets a top-level `limits` list, as `unserved` is one (`agents.md:371`). One entry: `{"name": "ONBOARD_BUTTON", "gpio": 9, "sentence": "Wokwi's XIAO part has no button and no pin on GPIO9, so no scenario can press it"}`. The status stays `ok`. A limit is said and never fails (P37).
- D. A passed run with `inputs: []` adds one line to the yes question: "the passed run set no control: it tested that the firmware starts". It sets `PassedRunEvidence.caveat` (`image_evidence.py:41`).
- E. Init's AGENTS.md block gets one bullet with the same text as rule 8 for agents.md. Rule 8: "A `passed` run tested what its scenario asserts and nothing more. Read `data.simulation_run`. A run with no input and one `ready` wait tested that the firmware starts. Call a must line tested only when a step sets its control and a step checks the result."

## The four cards, and P345

- P396 (#512): rewrite. The need is real (S3, G23). Use the `limits` channel and drop "reach".
  - The change: `check_spine.py` reads the board's Wokwi part from the store for a board-only build. For each GPIO that `pins.py` names, it adds a `limits` entry when the part has no pin on it. The stage text, `sim/WHAT-THIS-CANNOT-SHOW.md` and `--json` show the list.
  - Done when: `check_spine.py requirements.json --keep . --json` on walk 2's project lists ONBOARD_BUTTON (GPIO9) in `limits`, and the stage stays `ok`. A test with a part that has a GPIO9 pin lists nothing.
- P397 (#513): keep, after P396. Fix one sentence: the AI said it in chat at 01:14, before the paid run at 01:15:58, and long after the pick at 21:13. The card must also say where the pick reads the names, because `pins.py` does not exist at the pick.
- P398 (#514): merge into P399. `sim/diagram.json` already lists ids and pins, and only the controls are missing. P399's error message names them. A second file needs upkeep.
- P399 (#515): rewrite as the dry run. Its cost claim is not checked: walk 2 had no wrong name, and its run took 8 seconds. G26 did happen.
  - The change: `run_scenario.py --dry-run` makes every free check and compares the scenario's part ids, controls and pins with the diagram. It prints the steps by kind (field A) and starts no Wokwi run.
  - Done when: a wrong part id exits 2 under `--dry-run` and in a real run, before wokwi-cli starts. The message names the word and the ids that exist. A scenario with only a `ready` wait prints `set-control 0, expect-pin 0`. A fake wokwi-cli shows no start.
- P345 (#440): rewrite its body, because I5 landed there. The title promises a "not covered" line, but the body (9 lines, 553 bytes) never says so.
  - The change: fields A, B and D.
  - Done when: on walk 2's project, `look.py --json` shows empty `simulation_run.inputs` and one `unchecked` item that names the must line. The yes question names it too. A scenario that sets the control and checks the LED removes the item.

## Claims in the cards

| card | claims, each with its evidence |
|---|---|
| P396 | The project picked the BOOT button and `pins.py` names it 9: `pins.py:6`, checked. The simulation stage passed: `check_spine.py:558`, checked. The part has no button and no GPIO9 pin: checked in the store part file, and main has the same SHA-256 today. The build can read the part: the file exists, but how `wokwi_part_type` finds it is not checked. "Nobody tried `$gpio15`": the card says so, not checked. |
| P397 | Step C says to pick the board for its own button: `idea.md:93-97`, checked. "The person learned it only after the paid run": false, the AI said it in chat at 01:14. Whether the person read it then is not checked. It builds on P389: the title of #504 matches, checked. |
| P398 | "No file lists the names": false for ids and pins (`sim/diagram.json`). For controls, `parts/tactile-button.json` holds `pressed`, but I did not read the field. "Claude read the part to answer": tool calls 154-156, checked. |
| P399 | Free checks come first: `run_scenario.py:138-155` and `build.md:243`, checked. No name check: `run_scenario.py:140` tests only that `diagram.json` exists, checked. "A wrong name costs a paid run": not checked. Deploy has `--dry-run` (`deploy.md:32`). The other two are from the diary only. |
| I5 on #440 | "The look said simulation: passed": true for `--json` only. "deploy.py flashed the image as a tested one": board log line 3, checked. "That card covers it": its title does and its body does not. "Each scenario names its must line": not checked. Nobody knows if wokwi-cli takes an unknown key, and no script reads `must`. |

## New cards

- N1 P? — before the erase nobody says what the board runs now → look.py and deploy.py print the last deploy to this board from the store record
  - Need: O14 and G29. The AI said twice that the erase replaces reaction-game's firmware. The record says blink-c6 ran last.
  - Done when: `look.py --json` on walk 2's board has `data.running`. It names the project, date and image of the last deploy in `boards/<MAC>.json`. The deploy question names it too. A board with no record gives an `unchecked` item, never a guess.
- N2 P? — the serial warning names two causes and fits neither → the build names the true cause per board and the run log keeps the Wokwi CLI version
  - Need: G18 and finding 7. The warning did not hold on CLI 0.27.1, and it teaches agents to skip warnings. Setup installs 0.28.0.
  - Done when: one logged run under CLI 0.28.0 shows if the XIAO scenario hears `ready` with no wire. The build sentence for a `USB_SERIAL_JTAG` part matches that result. The log header holds the CLI version.
- N3 P? — the press test is a throwaway script that asserts nothing → a spark command runs the stand-in press test and exits 1 on a wrong LED
  - Need: G23 and finding 9. The only test of the must line before the bench lived in a scratch folder.
  - Done when: one command runs `firmware/` against the stand-in and drives the button from `pins.py`. It checks the LED after press and release, and it exits 1 on a wrong level. Its output lists each step.
- N4 P? — the rules call an exit 2 and a `skipped` non-passes and say nothing on `passed` → agents.md and the AGENTS.md block say a passed run covers only its asserts
  - Need: finding 4. It is cheap and guards every agent before any code lands.
  - Done when: agents.md has item 8, init's AGENTS.md block has the bullet, and the docs check passes.

## Not checked

- Why the AI chose a paid run over `--no-simulation`. The diary is silent. I read the transcript for tool names, result sizes and the AI's text near 01:14, 01:16, 06:45 and 06:53 only.
- Whether a scenario can read the LED through `$gpio15`, and whether CLI 0.27.1 or `USB_SERIAL_JTAG` explains the heard `ready`. I ran no scenario.
- Whether wokwi-cli takes an unknown scenario key, and how the build maps `wokwi_part_type` to the store file.
- The file that writes init's AGENTS.md block. My grep of `scripts/ai_files.py` found nothing.
- Token numbers cover result text only. 4 characters per token is my estimate, and turns times context is not measured.
- One web lookup: `curl` of raw.githubusercontent.com/wokwi/wokwi-boards/main/boards/xiao-esp32-c6/board.json on 2026-10-23, compared by hash only. I wrote two scratch scripts in the scratchpad folder.
