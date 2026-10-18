# The whole journey on paper: what stops a real end-to-end run

Desk analysis, 2026-10-18. The PO's words are on [P100, #6](https://github.com/xmejkal/spark/issues/6): "I just say
something like 'I want an RC car', and together we put it together ... I plug it in. It also builds. If the simulation
works, then it builds the real board, deploys it, and/or the serial works. We can also go back and edit the schema, and
then everything rebuilds." Sources: the README table, `docs/guide/journey.md`, `docs/guide/agents.md`,
`commands/build.md`, open cards from `gh issue` (2026-10-18), and the runs named in the table.

> **TL;DR.** No, the loop does not run end to end today, for a button and an LED or for anything else. Every stage ran
> alone, on different days, on two different boards, and the wiring and the button press at the bench never happened.
> For an RC car it stops at the first step. The four blockers:
> 1. **No board does it all.** The FireBeetle builds and simulates but has no drawn breadboard and has not met the bench.
>    The XIAO met the bench, but its shipped record cannot build; the bench used a hand-made copy.
> 2. **A goal outside the eight library parts needs research that never ran.** "Beeps" has no buzzer (the library holds only audio modules); an RC car has no
>    motor, battery or radio.
> 3. **Nobody has walked the loop once.** The button-and-LED breadboard is not wired (P100).
> 4. **Deploy needs a passed Wokwi run, so it needs a Wokwi token and CI minutes.** The repository states no free limit.

## The walk, step by step

"Today" cites a README row, a guide section, a test or a run. Runs marked 2026-10-18 were mine, in a scratch store
(`SPARK_HOME` inline), with no USB. `tests.test_journey_basic` and `tests.test_journey` passed that day: 23 tests, none
skipped.

| step | Claude calls | today | gap | card |
| --- | --- | --- | --- | --- |
| 0. set up | `/spark:init`, `/spark:setup` | partly: the install path "was not run" (README). The Wokwi token is the person's own step at wokwi.com/dashboard/ci | a first-time person meets the token only at step 6 | none |
| 1. goal in words | `/spark:idea` (asks up to 3 questions, writes needs) | partly: the conversation never ran; its scripts did (journey.md, Idea). The person sees needs, then matches | a vague idea with no parts named has no designed flow | [#5](https://github.com/xmejkal/spark/issues/5) P76 |
| 1b. RC car | the same | not tried; the library has an L9110S driver and nothing else for a car | blocker 2 | none |
| 2. what you own, find parts | `/spark:drawer`, `parts.py --match`, `--pick`, `/spark:research` | partly: drawer and match scripts run. `--match` for "indicate / buzzer" offered only the LED, as "other words" (2026-10-18). Research agents never ran (README) | no buzzer in the library; need words must match (`sense/button` missed the tactile button, `input/button` finds it) | [#178](https://github.com/xmejkal/spark/issues/178) P209, [#10](https://github.com/xmejkal/spark/issues/10) P39 |
| 3. requirements file | `parts.py --requirements` | works for adding parts (2026-10-18). A swapped pick adds the new part and keeps the old one: `kept, not from a pick: led-red-5mm` | no command removes a part; the person edits the JSON by hand | no card |
| 4. build, `--keep` | `check_spine.py requirements.json --keep .` (`/spark:build`) | works (README Build; `test_journey_basic`). `breadboard.json`, picture and page for the XIAO C6 only; the geometry file holds only LED, resistor and button | FireBeetle: sheet and page, no drawn breadboard. Rails and the L9110S module are not drawn | [#352](https://github.com/xmejkal/spark/issues/352) P293 |
| 4b. board | `boards.py --list` | FireBeetle builds. Shipped `xiao-esp32-c6` "stops at the footprint stage (P121)" (2026-10-18) | blocker 1 | [#314](https://github.com/xmejkal/spark/issues/314) P278 |
| 5. firmware, checks | Claude writes `firmware/`; `import_firmware.py`, `check_all.py` | partly: the example firmware imports and passes (journey.md, Firmware). No command writes firmware; `check_all` exits 0 on a fresh project | nothing checks that every signal is driven or read | [#8](https://github.com/xmejkal/spark/issues/8) P74 |
| 6. simulate | `run_scenario.py` (Claude writes the scenario) | works: passed 2026-10-12 (FireBeetle project) and 2026-10-14 (XIAO). Needs `WOKWI_CLI_TOKEN`; a run spends CI minutes | blocker 4 | [#356](https://github.com/xmejkal/spark/issues/356) P295 |
| 7a. look | `look.py` | works on a real XIAO (2026-10-13; bench log 2026-10-17). The board restarts | FireBeetle: never looked at; its record names no USB or flash pins | [#323](https://github.com/xmejkal/spark/issues/323) P281 |
| 7b. deploy | `grant.py --scope deploy` (person's terminal), `deploy.py --token` | works: flashed the XIAO, `ready seen` (2026-10-15). The deploy grant was "tested with fakes" (README); #347 records the PO's try on 2026-10-18: the first call failed at the erase, the same call 5 s later worked | no `/spark:deploy`, text output only; the first call can fail | [#192](https://github.com/xmejkal/spark/issues/192) P213, [#347](https://github.com/xmejkal/spark/issues/347) P290 |
| 7c. serial, live | `live.py --code`; `reach.py` (the person's tool) | works: the live try passed on 2026-10-17 on the XIAO (bench log), n = 1 | Claude cannot read the console for a few seconds after a deploy | [#270](https://github.com/xmejkal/spark/issues/270) P248, [#224](https://github.com/xmejkal/spark/issues/224) P235 |
| 7d. wire it | the breadboard sheet | not done: "The button-and-LED project is not yet wired and flashed" (journey.md) | blocker 3 | [#6](https://github.com/xmejkal/spark/issues/6) P100 |
| 8. a change | edit `requirements.json`, then `--keep` again | partly: a rebuild redraws sheet, page and diagram and keeps moved parts and jumpers (P273, P287), naming what it cannot keep. Deploy then refuses until the scenario passes on the new image (build.md) | no remove or swap command (step 3); a jumper moved into a row a part later takes is lost silently; every change costs one more simulation run | [#351](https://github.com/xmejkal/spark/issues/351) P292 |

## What changes for an RC car

- Parts: the library has the L9110S driver and no DC motor, battery or radio. Each needs `/spark:research`, and
  `parts.py --requirements` writes nothing while a pick owes a footprint, pin order or simulation stance (journey.md).
- Circuits: the demo `rc-car` has two circuits (car and remote), and `check_all.py --project` stops on it
  ([#205](https://github.com/xmejkal/spark/issues/205) P223). The driver's pull-ups conflict with the board's
  pull-downs, and `check_all` does not report it ([#43](https://github.com/xmejkal/spark/issues/43) P109, closed into Later).
- Drawing: a motor needs a supply rail, and rails are not drawn, so `breadboard.json` is not written (agents.md,
  `breadboard.py`). No card names rails.

## Blockers, in the order they bite

1. **No board does the whole loop.** FireBeetle: build and simulation work; no drawn breadboard; no bench run; no USB or
   flash pin facts, so `live.py` refuses no pin there (#323). XIAO: the bench and the drawing work, but the shipped
   record stops the build (a refuter run on 2026-10-18 stopped at the schematic stage: the record has no `power.io_volts`, so header facts alone do not fix it), and the bench project used its own `xiao-esp32-c6-fresh`. Cards: #314 (header facts), #323,
   [#336](https://github.com/xmejkal/spark/issues/336) P286 (unknown boards). [#68](https://github.com/xmejkal/spark/issues/68) P134 asks that the example builds on each library board; no
   card asks for one shipped board that runs the whole loop, bench included.
2. **A goal outside the library needs research that never ran.** The README marks Research "partly". The PO set
   rounds B and C aside on 2026-10-11 and no card was filed (#6 comment). #178 covers the by-hand steps for one owned part.
3. **The loop has not been walked once.** The pieces ran on 2026-10-12, 10-14, 10-15, 10-16 and 10-17, never in one
   session from a goal to a lit LED on a wired breadboard. That is what #6 is for.
4. **Deploy waits on Wokwi.** `deploy.py` flashes only an image with a passed log, so a person with no Wokwi account
   cannot reach the board. `commands/build.md` (line 207) says only that it is not stated whether the VS Code extension spends CI minutes; nothing in the repository gives a free limit. #356 asks if spark can run its own
   simulator. For the PO, who has a token, this is a cost and not a stop.

## Gaps that only make it less nice

- No one entry point: Claude chains seven command pages and scripts; simulate and deploy have no command of their own
  (#192, [#152](https://github.com/xmejkal/spark/issues/152) P199).
- Replace a part in one command (step 3): no card.
- The first `deploy.py` call after a look can fail to connect (#347).
- Firmware is not checked against the pin map (#8); firmware beyond MicroPython has a spike only
  ([#203](https://github.com/xmejkal/spark/issues/203) P221).
- Serial: a bounded console read (#270) and run a file from memory ([#271](https://github.com/xmejkal/spark/issues/271) P249).
- The Wokwi token has no walk-through in `/spark:setup`: no card.
- The conversation steps (idea, drawer words, research, identify) were never run in Claude Code for these docs.

## Proposed order: the smallest stories that make the loop run

Each is one PR. The order follows what unblocks the next.

1. **A shipped XIAO record that builds.** Done when `check_spine.py --keep` on `tactile-button` + `led-red-5mm` with
   `"board": "xiao-esp32-c6"` reaches the simulation stage and writes `breadboard.json` (#314 plus the board's `power.io_volts`; widen #314 or file a card).
2. **The bench walk, round A, on the XIAO.** Done when the PO wires the sheet, presses the button, the LED lights, and
   the diary files each stall as a card (#6).
3. **One command to remove or swap a pick.** Done when after `--pick` of another part, `--requirements` drops the old
   part and a `--keep` build keeps the moved parts (new card).
4. **A buzzer through the research route, walked once.** Done when `parts.py --match` offers a buzzer, the build
   reaches simulation and a scenario passes ("a small thing that beeps"; #178, new card).
5. **`/spark:deploy` with JSON** (#192). Done when Claude deploys a passed image with one command and reads `needs_yes`.
6. **A bounded console read** (#270). Done when Claude reads 5 s of the board's output after a deploy.
7. **The Wokwi token in the setup walk-through.** Done when `/spark:setup` names the token, its page and the cost
   (new card; #356 decides whether it stays).
8. **RC car, first slice.** Done when the car's circuit (driver, two motors, battery rail) builds and is drawn (needs
   #205, a card for rail drawing, and research for the motor).

## Checked by

The `refuter` agent (Opus) reproduced the claims on 2026-10-18, with no USB. It confirmed the swapped pick that keeps the
old part, the XIAO stop, the geometry file, the buzzer match, the cited cards, the dates and the style rules. It changed
four things: the XIAO build stops at the schematic stage for lack of `power.io_volts` (story 1 and blocker 1 now say so);
the Wokwi line now quotes `build.md` line 207 as it is; #43 is marked closed into Later; #68 is named beside blocker 1.
Not checked: the hardware rows (no USB) and the deploy refusal itself, which rests on `deploy.py`'s docstring.
