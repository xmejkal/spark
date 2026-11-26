# P1190 council: the user's lens

The lens: the user's journey. The primary persona is the PO, a hobbyist (n = 1). The second user is Claude, which runs
spark for him and reads each answer as JSON. Written 2026-11-26 by the user lens (Opus), read-only on the tree. Tags:
E (with a pointer), H (with its source), D (who, when), — for an unknown.

## 1. Findings

### The walk as he does it today

USER-1 · On the clock (the walk project p934-display2), the free checks that spark offers cannot run at all. `run_scenario.py --dry-run` first refuses with `no_sim_project` when `sim/diagram.json` or `sim/wokwi.toml` is missing. The build writes neither for a board with no `wokwi_part_type`. The clock's `sim/` holds only `flash-with-firmware.bin` and `runs/`. So the "free steps" the PO named exist only where the paid run also exists · E `scripts/spark/firmware/scenario_run.py:131-133`, `ls sim` in the walk project p934-display2 (2026-11-26), the store's shelf/boards/firebeetle2-esp32c6.json (`wokwi_part_type: null`) · supports only: the free checks are tied to Wokwi's project files today, so a board Wokwi lacks gets no free check of behaviour from spark.

USER-2 · The clock has a free behaviour check that spark does not see. The conversation wrote host tests of the firmware's logic (`tests/test_schedule.py`, `tests/test_quotes.py`). 35 tests ran in 0.031 s and passed. Spark's page and `flow.py` name no such check, and the simulate phase stays "later, no Wokwi model of this board" · E `python3 -m unittest discover -s tests` in the walk project p934-display2, output "Ran 35 tests in 0.031s OK" (2026-11-26). The first test commit is df94542, 2026-11-22 20:50 CET. `grep import_firmware\|unittest scripts/spark/flow` finds nothing · supports only: for the board Wokwi lacks, the check that actually ran was the conversation's own. Whether the PO knows these tests exist: —.

USER-3 · The free import check (`import_firmware.py`) needs no `sim/` and no Wokwi. It imports each firmware module except `main.py` on spark's `machine` stand-in. No flow phase, sentence or offer names it, so the person meets it only if Claude runs it · E `scripts/import_firmware.py:1-20`, no hit for `import_firmware` in `scripts/spark/flow/` (grep, 2026-11-26) · supports only: a free substep exists for every board, and the page hides it.

USER-4 · Even with a stand-in board, the clock's one part would not be simulated. The e-paper's shelf record holds a skip stance: its colours, controller and refresh are unknown to Wokwi, and "the refresh time and partial update of this module are measured on the bench". A run on a C6 stand-in would show the boot, the ready line and the serial text, not the display · E the store's shelf/epaper-2in9-bwr-mh-et-live.json `simulation.skip` · supports only: "what can be simulated" is per part as much as per board. For the clock the honest first screen is a coverage list, not a run button.

USER-5 · The page tells him what is missing, not what he can still do. The station line greys Simulation as "later (no Wokwi model of this board)". A muted line says "No simulation: Wokwi has no model of this board. You test it on the real board." In the walk the build's answer row also said "Could not run: the board record names no wokwi_part_type", which the walk diary calls a line that "reads as a failure" · E `scripts/spark/flow/flow_codes.py:441`, `:454-456`, `scripts/spark/flow/guide.py:24-25`, `:206-228`, the walk project p934-display2's diary.md:172-179 (2026-11-22 11:40 CET) · supports only: the PO's harm "reads could-not-run although it works" was seen once in a walk (n = 1).

USER-6 · The simulation's files reached into the deploy. With no simulation, the deploy first refused for a missing `sim/wokwi.toml` ("no sim/wokwi.toml in .: build with /spark:build --keep . first"). P1001 fixed it in the walk. The deploy's logs still live under `sim/runs/board/` (28 logs in the clock), so the folder named for the simulation holds no simulation result and 28 board logs · E the walk project p934-display2's diary.md:234-251, `ls sim/runs/board | wc -l` = 28 (2026-11-26), P1001 #1459 · supports only: a person who looks in `sim/runs` for "the results" finds the bench's logs. A strategy seam must also move the deploy's tie to Wokwi's file names.

USER-7 · Paid runs are rare in his walks. Across 15 walk folders there are 4 scenario logs. Two of them (walk4 and p581-sound-joystick) are the same run, with the same time 2026-11-01 19:33:44 and the same image sha256. So there are 3 distinct paid runs since 2026-10-23. The reaction-game project has a scenario written and never run (no `sim/runs/`) · E `find spark-walks -path '*/sim/runs/*.log' -not -path '*/runs/board/*'`, `head` of each log, `ls reaction-game/sim` (2026-11-26) · supports only: in practice the paid run is the exception. The free checks and the bench carry the weight. Why reaction-game's scenario never ran: —.

USER-8 · A passed run can prove only the start. Walk2's run passed, but its scenario says the must line "cannot run here": Wokwi's XIAO ESP32-C6 part has no BOOT button, so "this scenario tests only the start". The log's verdict is plain `passed` and holds no step counts line, so the P485 caveat ("passed, but no set-control step") was not printed for it · E the walk project walk2's sim/runs/the-firmware-starts.log (run 2026-10-23 01:16), lines 1-2 and the scenario comments. The caveat rule is at `scripts/spark/firmware/scenario_steps.py:36-44` · supports only: "passed" overstates when the strategy lacks a part. The result screen must say what the run could not show, in the verdict's own line.

USER-9 · Spark already writes "what this simulation cannot show" beside the diagram and into each log. On the bench the PO met it where it did not apply. With no run, the look and the deploy printed the five-item list twice, and the notes call it "noise". The idea there was one line: "no simulation tested this image: test the display, the button and the LED on the board" · E `scripts/spark/firmware/sim_project.py:120`, `:158`, `scripts/spark/firmware/scenario_run.py:207-218`, the store's bench-2026-11-25.md:55-57 and :76-78 · supports only: the limits list helps after a run, and it is clutter before one.

USER-10 · The cost line names no number. Every sentence says "It uses Wokwi CI minutes". Spark keeps no count, and `wokwi-cli` reports no balance. A walk "could not tell how many free minutes it had left before a run" · E `scripts/spark/flow/flow_codes.py:364`, `:427-434`, P413 #539 and its comment of 2026-11-17 · supports only: the yes for minutes is asked blind today. The free plan's 50 simulated minutes per rolling 30 days is from research-wokwi.md §1.

USER-11 · On this Mac, `WOKWI_CLI_TOKEN` is set in the shell and `wokwi-cli` is installed · E `[ -n "$WOKWI_CLI_TOKEN" ]` gave "token-set", `which wokwi-cli` found it (2026-11-26) · supports only: the token is not the PO's blocker here. A later hobbyist with no token would stop at `no_token` after the free checks (`scenario_run.py:262-273`).

USER-12 · Free does not mean no setup. The dry run builds the flash image in memory, so it needs littlefs and a MicroPython interpreter (the one /spark:setup downloads). A missing tool refuses the free checks as `tool_missing` · E `scripts/spark/firmware/scenario_run.py:142-147`, `run_scenario.py:57` · supports only: the "free checks" screen needs a state for a missing local tool, apart from the paid part's token.

USER-13 · For Claude, the simulate step is a terminal command, not an Operation. `phase_steps.scenario_steps` returns a NextStep `run_scenario` with `needs_person` set, one per scenario, or one with the placeholder `sim/scenarios/<name>.scenario.yaml`. `run_scenario.py` prints text and exit codes. It has no `--json` · E `scripts/spark/flow/phase_steps.py:39-46`, `scripts/run_scenario.py:62-81`, P1078 #1582 · supports only: Claude reads the verdict from text and the log. A "passed, but" caveat is one printed line that an agent can miss.

USER-14 · The scenario is written in Wokwi's words. A step names `part-id` and a control `name` (for example `set-control: { part-id: tactilebutton, name: pressed, value: 1 }`). What the scenario does not cover lives in YAML comments ("Not covered: the LED itself and the real reaction times") that no reader parses · E the walk project reaction-game's sim/scenarios/five-rounds.scenario.yaml:1-3, `scripts/spark/firmware/scenario_steps.py:17-19` · supports only: the PO can give "what should happen" in words (a must line). He cannot give part ids, control names or step syntax. Those come from the diagram and the chip JSON.

USER-15 · Sliders exist in one chip, and they live in Wokwi's editor. The VL6180X chip has a "Distance (mm)" range (0 to 255, start 200), a "Range status" range and an "Unplug the sensor" boolean. Wokwi's chip.json page lists only `range` as a valid type. A slider moves a value in a live simulation in Wokwi's web editor. A headless `wokwi-cli` run has no slider: a scenario's `set-control` sets the value instead · E `parts/vl6180x-breakout/chip/vl6180x.chip.json`, https://docs.wokwi.com/chips-api/chip-json (search result read 2026-11-26), research-wokwi.md §2 and §4 · supports only: a slider on spark's page cannot drive a Wokwi CI run live. On the page, a slider can only write a value into a scenario step or a start value. That is an editor of the scenario, not a live control. Whether the `boolean` type works in Wokwi: —.

USER-16 · Where a value is measured, it sits in the record's prose. The e-paper's skip reason says the refresh is "measured on the bench", but no measured number is in the simulation key · E the store's shelf/epaper-2in9-bwr-mh-et-live.json · supports only: the PO can supply a measured value at the bench. Spark has no field yet for a slider's value with its origin. Records grow by need (AGENTS.md).

USER-17 · Gate A of the past-breadboard design leaves the simulation out, because the clock's simulation is `could-not-run` · E the store's councils/past-breadboard/architect.md:9, :271 · supports only: if the simulation step reports "not possible, here is why, and these free checks passed", it could later count as evidence at gate A without locking the clock. That choice is the PO's.

USER-18 · The page's one simulate offer is "Run the simulation", a chat offer. Its tell, "Help me run the simulation of this project.", shows under "Ask Claude" in a code box. The page never sends it, by design · E `scripts/spark/flow/flow_codes.py:141`, `:153`, `:478`, `scripts/spark/flow/page_sections.py:339-350` · supports only: every simulation screen below keeps this pattern. The person asks Claude, and the paid run stays a typed yes in the chat or the terminal.

### What each user can and cannot supply

| who | can supply | cannot supply | pointer |
| --- | --- | --- | --- |
| the PO | the must lines in words, a yes or a no for paid minutes, a measured value at the bench (a distance, a refresh time), and "it works" on the real board | the minutes left (only his wokwi.com page knows), part ids and control names, a WebAssembly chip, a Wokwi board definition | USER-10, USER-14, USER-16. The WebAssembly line is H (his own words "I am not really sure") |
| Claude | a scenario from the must lines, a host test of pure logic (USER-2), the free checks, and a chip in C from a library, with the PO's yes for any web source | the balance of minutes, whether a passed run covered the must line (unless the strategy says what it lacks), a pass on a board no strategy covers | USER-8, USER-10, USER-13 |

### Where they stall, guess or come to harm

| moment | who | kind | pointer |
| --- | --- | --- | --- |
| a board Wokwi lacks: no free check runs, the step only says "later" | the PO | stall | USER-1, USER-5 |
| the build's answer row says "Could not run" for a board that built | the PO | harm (reads as failure) | USER-5 |
| the host tests passed, and the page does not know | both | harm (work unseen) | USER-2 |
| a yes for minutes with no count left | the PO, Claude | guess | USER-10 |
| "passed" on a scenario that tested only the start | both | harm (overclaim) | USER-8 |
| the limits list printed with no run | the PO | noise | USER-9 |
| the results are in a text log among 28 deploy logs | the PO | stall | USER-6 |
| a slider exists only inside Wokwi's editor, and spark's run is headless | the PO | guess (where to set the value) | USER-15 |
| the step is a terminal command with text output | Claude | guess (parsing text) | USER-13 |

### The screens

All sketches are about 120 characters wide, for a page at 1440 px. They follow the calm design of the page discovery: the project name, the freshness line, a line of steps, one NOW box with who acts, the done line muted under it, and the rest folded (docs/discovery/2026-11-23-p1038-page-design/design.md:270-312). Buttons carry the offer's own words. A chat offer shows "Ask Claude" with its sentence. No sketch shows a Run button, because P820's no-go forbids a Run-live-code button and the paid run is a typed yes (design.md:80, D-a). Every substep name below is the lens's proposal, H from the PO's words on #1735 ("the free steps", "the payd part", "the editor", "displaying the results").

#### Screen 0. The simulation step on the line of steps

- **Job:** say, in the line of steps, where the simulation stands and which substep is next, without reading as a failure when no strategy covers the board.
- **The person** sees the step and opens its NOW box. **Claude** reads the same facts in `flow.py show --json` (design rule D22 of P1038).
- **States** of the station mark: not started · free checks only (a strategy covers nothing, but a free check ran) · ready to run, with its cost · running (a request sent) · passed, with what it could not show · failed · could-not-run · not possible, with the reason in grey.

```
+--------------------------------------------------------------------------------------------------------------------+
| p934-display2: a quote and the time on e-paper, once an hour                                                       |
| This page shows the project as of 26 Nov 2026, 10:12, its newest change.                         [which files v]  |
|                                                                                                                    |
| Idea v  Needs v  Parts v  Parts list v  Board files v  Wiring v  Firmware v  [Simulation o]  On the board v        |
|                                                                               what can run > free checks >         |
|                                                                               scenario > run > result              |
|                                                                               (sub-line shows only when NOW)       |
+--------------------------------------------------------------------------------------------------------------------+
```

#### Screen 1. What can be simulated (the coverage)

- **Job:** for each part and the board, say how it is simulated (a Wokwi part, a setting, a custom chip, a skip with its reason), and which strategy covers the board, before anything runs.
- **The person** reads it, and may ask Claude to write a chip or to try a stand-in board. **Claude** reads each record's `simulation` stance and the board's coverage. It proposes a chip or a stand-in, and it writes no record without the person's yes.
- **States:** not possible (no strategy covers the board, and it names why: "Wokwi has no model of the FireBeetle 2 C6") · partly (the board runs, and some parts are skipped, each with its reason) · all covered · a stance missing (a record owes `simulation`, as at `flow_codes.py:196`).

```
+--------------------------------------------------------------------------------------------------------------------+
| NOW  Simulation, by Claude and you                                                                                 |
|   WHAT CAN RUN   The board: no simulator has a model of the FireBeetle 2 ESP32-C6. Nothing here runs the board.    |
|                  The e-paper: skipped. Its refresh is measured on the bench.                                       |
|   NEXT           The free checks still run on this computer. They cost nothing.                                    |
|   Ask Claude  "Run the free checks of this project."                                                               |
+--------------------------------------------------------------------------------------------------------------------+
|  done: idea, needs, parts, parts list, board files, wiring (spark cannot see it), firmware               (muted)  |
|  This is not a failure. Your gadget is tested on the real board.                                         (muted)  |
+--------------------------------------------------------------------------------------------------------------------+
| > Each part and how it is simulated  (2 parts: 0 run, 1 skipped, the board not covered)              [open v]     |
| > Other ways to cover the board  (a stand-in board, a model Claude writes)                           [open v]     |
| > For developers                                                                                     (folded)     |
+--------------------------------------------------------------------------------------------------------------------+
```

The fold, opened, on a project with a covered board (the VL6180X case):

```
| v Each part and how it is simulated                                                                                |
|     XIAO ESP32-C6       Wokwi's own board                       runs                                               |
|     VL6180X             a model kept with its record (a chip)   runs   values you can set: distance, status, unplug|
|     red LED             Wokwi's own LED                         runs   lights on current only                      |
|     DFPlayer module     skipped: no Wokwi part. The log names each cue instead.                                    |
```

#### Screen 2. The free checks

- **Job:** run every check that costs nothing, and say what each one proved and what it did not.
- **The person** asks Claude to run them, or does nothing. They are free. **Claude** runs them: the import check, the project's own host tests (USER-2), and the dry run where the files exist. It reads each verdict.
- **States:** not possible for one check, with why (no `sim/` for the dry run, USER-1) · a tool missing (USER-12) · passed · problems (a module raised, a test failed, an unknown component id) · could-not-run · out of date (the firmware changed after the checks).

```
+--------------------------------------------------------------------------------------------------------------------+
| NOW  Simulation: the free checks, by Claude                                                                        |
|   CHECKED   26 Nov 2026, 10:20. Free, on this computer.                                                            |
|             Each firmware file loads      7 of 7 ok                                                                |
|             Your project's own tests      35 of 35 ok   (tests/ in your project, written in the chat)              |
|             The scenario's parts          not possible: no simulator file for this board                          |
|   NEXT      Nothing more runs here. Test the board on the bench.                                                   |
|   Ask Claude  "Look at the board."                                                                                 |
+--------------------------------------------------------------------------------------------------------------------+
|  What the free checks cannot show: the screen, the timing, the deep sleep, the Wi-Fi.                    (muted)  |
+--------------------------------------------------------------------------------------------------------------------+
```

The words "7 of 7" are an example. The import check was not run on the clock by this lens.

#### Screen 3. The scenario (the editor)

- **Job:** show what the run will do, in the person's words, step by step, and let him change a set value before it runs.
- **What is edited** (the PO said "the editor" and did not say what it edits): (a) the scenario's steps, which Claude writes from the must lines. (b) The values a step sets, such as the distance, where the part has a control (USER-15). (c) The part's simulation way (a Wokwi part, a setting or a chip), which is the record and is changed only through Claude with a yes. Which of the three the PO meant: —.
- **The person** reads each step as a sentence, moves a value, and says "change step 3". **Claude** writes the YAML, checks the part ids against the diagram (free), and keeps each step's name as its must line.
- **States:** no scenario yet (Claude writes one first, `flow_codes.py:427`) · written, not checked · checked (the ids match, free) · a step names an unknown part (`unknown_component_id`) · it covers no must line, or no set-control (it proves only the start, USER-8) · changed since the last run.

```
+--------------------------------------------------------------------------------------------------------------------+
| NOW  Simulation: the scenario, by you and Claude                                                                   |
|   SCENARIO  "Something close turns the LED on"   from your must line 2                                             |
|     1  Wait until the firmware says ready.                                                                         |
|     2  Set the distance to   [=====o-------------]  80 mm      (the sensor's control "distance", 0 to 255)         |
|     3  Expect the LED pin to be on.                                                                                |
|     4  Set the distance to   [=================o-]  240 mm                                                         |
|     5  Expect the LED pin to be off.                                                                               |
|   It does not test: the real light level of the LED, or must line 1 (no step names it).                             |
|   NEXT      The scenario matches the drawing (checked free, 10:24).                                                |
|   Ask Claude  "Change the scenario: <what you want>."                                     [Save these values]      |
+--------------------------------------------------------------------------------------------------------------------+
| > The scenario as the simulator reads it (YAML)                                                      (folded)     |
+--------------------------------------------------------------------------------------------------------------------+
```

"Save these values" would only write the values into the scenario's steps through a request, as the parts picks do. It moves nothing live (USER-15). Whether the page may write a scenario at all: —, the PO's to decide.

#### Screen 4. The run (ready, with its cost, and running)

- **Job:** name the cost and what the run can and cannot prove, then wait for the person's typed yes.
- **The person** types yes in the chat or the terminal. **Claude** asks with the cost named, runs it, and never takes a token or "go ahead" in a chat as the yes when the step needs the terminal.
- **States:** ready to run, with its cost (the minutes spent by spark this month, from P413, and the run's time cap) · no token (after the free checks) · a request sent, nothing has run yet · running · stale (the firmware changed after the image).

```
+--------------------------------------------------------------------------------------------------------------------+
| NOW  Simulation: the run, by you                                                                                   |
|   COST      Up to 1 minute of your Wokwi minutes. Spark spent 3 minutes on this computer this month.               |
|             Spark cannot see how many you have left. Your Wokwi account page shows it.                             |
|   IT TESTS  must line 2, with the sensor and the LED.  It cannot test: the real light, must line 1.                |
|   NEXT      Say yes to Claude, and Claude runs it. Or run it in your terminal.                                     |
|   Ask Claude  "Run the scenario 'Something close turns the LED on'. I agree to spend Wokwi minutes."               |
+--------------------------------------------------------------------------------------------------------------------+
| Running:  sent 26 Nov 2026, 10:31. The simulator is running it. This page does not update by itself.             |
+--------------------------------------------------------------------------------------------------------------------+
```

The numbers are examples. Spark has no minutes count today (USER-10).

#### Screen 5. The result

- **Job:** say what the run proved, what it could not show, and what comes next, in one box, with the log folded.
- **The person** reads the verdict and the next act. **Claude** reads the same verdict, the caveat and the limits as fields, never from the text alone.
- **States:** passed, with what it could not show · passed, but it proves only the start (no set-control, USER-8) · failed, with the step and the board's last serial line · could-not-run (a simulator lost, a board silent, a timeout), never shown with a tick · out of date (the firmware changed after the tested image).

```
+--------------------------------------------------------------------------------------------------------------------+
| NOW  On the board, by you                                                                                          |
|   SIMULATION  Passed, 26 Nov 2026, 10:32: "Something close turns the LED on". 5 steps, 2 set a value.              |
|               It could not show: the real light level of the LED, or must line 1.                                   |
|   NEXT        Put this tested image on the board.                                                                  |
|   Ask Claude  "Look at the board."                                                                                 |
+--------------------------------------------------------------------------------------------------------------------+
| > The run's log: the serial text, the image, the scenario as run                                     [open v]     |
+--------------------------------------------------------------------------------------------------------------------+

Failed:
|   SIMULATION  Failed at step 3, "Expect the LED pin to be on". The board printed: "dist 80 led 0".                 |
|   NEXT        Claude reads the log with you and fixes the firmware. A new run costs minutes again.                 |
|   Ask Claude  "Go through the failed run with me."                                                                 |

Could not run:
|   SIMULATION  Could not run: the board printed nothing in 60 s. Nothing was tested. This is not a pass.            |
|   Ask Claude  "Read me why the simulation could not run."                                                          |

Passed, but only the start (walk2's case):
|   SIMULATION  Passed, but it tested only the start: the simulator's board has no BOOT button.                      |
|               Your must line "Pressing the button lights the LED" is not tested here.                              |
```

## 2. What I could not check, and why

- Whether the PO read the clock's "No simulation" line as a failure, or as fine. No account from him in the material I read. The diary's word "reads as a failure" is the session's (USER-5).
- Whether the PO knows the clock's host tests exist, and who asked for them. The commit messages do not say (USER-2).
- The import check on the clock. I did not run it, so "7 of 7" in screen 2 is an example.
- The minutes left on his Wokwi account. The account page is not connected (the brief's start and reach).
- What the PO means by "the editor": the scenario, the values, or the part's simulation way. His words do not say (screen 3).
- How Wokwi's web editor shows a chip's slider during a run. The one search found only the JSON definition, not the editor's interface.
- Whether `wokwi-cli` can run with a live slider. Research-wokwi.md §5 does not confirm any interactive control from the CLI beyond `--interactive`, whose meaning was not read.
- Why the reaction-game scenario never ran (USER-7).
- bench-2026-11-20.md holds no simulation note, so it gave nothing to this lens.
- Running the host tests in the walk project p934-display2 may have refreshed its `tests/__pycache__` files, which existed before. I changed no other file.

## 3. Questions for the decider

Account questions for the PO, past tense, one per friction moment. They decide whether the friction is real for him (n = 1).

- QU1 · When the clock's page said "No simulation: Wokwi has no model of this board", what did you think it meant, and what did you do next? · decides: whether screen 1's "not a failure" line is needed (USER-5).
- QU2 · Did you know the clock project has its own tests, and did you ever see them run? · decides: whether the project's own tests count as a free check on the page (USER-2).
- QU3 · The last time you said yes to a paid Wokwi run, did you know how many minutes you had left? How did you find out? · decides: whether the minutes count (P413) belongs on the run screen (USER-10).
- QU4 · Did you ever open a file in `sim/runs/`? Which one, and what were you looking for? · decides: whether the result screen replaces the log for him (USER-6).
- QU5 · When walk2's run passed with only the ready line, did you count the button as tested? · decides: whether "passed, but only the start" is its own state (USER-8).
- QU6 · Did you ever move a slider in Wokwi's own editor for a spark project? What value did you set, and why? · decides: whether the editor is for live values or for the scenario's values (USER-15).
- QU7 · When the look and the deploy listed "what this simulation cannot show" with no run, did you read it? · decides: whether the limits list shows only after a run (USER-9).
- QU8 · Why did the reaction-game scenario never run? · decides: what stops a run in practice: the cost, the time, or the moment (USER-7).

Decisions for the decider.

- QD1 · What does "the editor" edit: the scenario's steps, the values a step sets, or the part's simulation way? · decides: screen 3's scope and whether the page writes a scenario.
- QD2 · Do the project's own host tests (written in the chat) count as a spark free check? · decides: whether spark runs and shows a check it did not write, and whether it breaks "spark exports facts, never behaviour" (D-b).
- QD3 · Is "not possible, with the reason" a status of its own, apart from `could-not-run`? · decides: the grey state of screens 0 and 1, and the end of "reads as a failure" (Done when of #1735).
- QD4 · Does a "passed" whose scenario tests only the start open the deploy as tested? · decides: screen 5's states and P308 #374's grade.
- QD5 · Does the free-checks result ever count at gate A? · decides: how the simulation step feeds the past-breadboard gate (USER-17).
- QD6 · Do the deploy's logs move out of `sim/runs/board/`? · decides: whether "the results" have a place of their own (USER-6).

## 4. Searches

- "Wokwi custom chip controls slider simulation editor click chip" · served: what the editor screen can move (a live slider in Wokwi's editor, or a value written into a scenario) · used: it confirmed that `range` is the only listed control type and that controls change values while a simulation runs. It found nothing on how the editor shows them (USER-15, section 2). Source: https://docs.wokwi.com/chips-api/chip-json
