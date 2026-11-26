<!-- The refuter, P1190 #1735, 2026-11-26. Read on branch p1190-simulation at 6f4c3368. Nothing written in the tree but this file. No paid run. -->
# P1190 the simulation step: the refuter

Tags: holds, partly, refuted, could not open. "Partly" means the source says something weaker or narrower.

## Check first: the existing product

1. **Does the change address the observed problem?** Only in part, and mostly through P999, which the brief puts "beside it".
   - The only board record with no Wokwi part is the store's shelf/boards/firebeetle2-esp32c6.json (`wokwi_part_type` null). The repository's two board records and the store's T-Display record all name a Wokwi part. P999 #1455 gives that one record a stand-in. After P999, no known board reads `board_not_in_wokwi`. Item 1 then has no instance, and its proof ("the clock's `.spark/build.json` after a rebuild says `skipped`") would be produced by P999 plus `every_part_skipped` (PO-18), not by item 1.
   - The card's Done when says "each part simulated directly, by a setting or by a custom chip". The architect folds "a setting" into a controls list on a Wokwi model (architect.md §4). The PO's words name parts "we can simulate by some script or setting". A script-based way off Wokwi is the logic-level runner, parked behind a spike (Q3 b). No slice from 0 to 3 covers a part simulated by a script on a board Wokwi lacks.
   - "The simulation has no step and screens of its own": slice 0 gives one page line. The screens wait behind the replay's pass line (brief, Riskiest test). So the PO's "simulation screen and step built in" is conditional, not planned.
2. **What breaks for current users.** The brief's "must not get worse" names only the deploy and the free checks. It drops these.
   - Old records. `scripts/spark/flow/guide.py:44-48` reads: "An old record with no code is never counted as done." The architect removes `NO_MODEL_CODES` (architect.md §3, "goes"). Every build record written before item 1 still says `could-not-run, board_not_in_wokwi` (the walk project p934-display2's `.spark/build.json`). Without the special case, those builds read as not done until a rebuild. Smallest fix: keep `NO_MODEL_CODES` as a reader of old records, and stop writing the code.
   - Exit codes. `docs/guide/agents.md:16`: "`ok` exits 0, `problems` exits 1 and `could-not-run` exits 2." A build that moves to `skipped` changes what an agent reads. The architect lists this under "What I did not check" (architect.md:244). The brief drops that caveat.
   - Goldens and tests. `board_not_in_wokwi` or `NO_MODEL_CODES` appear in tests/test_stages.py, test_run_request.py, test_flow.py, test_build_service.py, test_json_contracts.py, test_check_spine.py and tests/mutations/p701-build-codes.json, p977-guide.json, p1008-built-answer.json.
   - Docs made untrue by item 1: `docs/guide/agents/flow.md:47-48` ("A build whose only stop is a simulation stage with the code `board_not_in_wokwi` is counted as done"), `:360`, `docs/guide/how-it-works.md:40`, and `scripts/flow.py:33-35`. No item names them.
   - The deploy. `scripts/spark/firmware/project_image.py:77` reads every `sim/runs/*.log`, and `image_evidence.py:433` refuses an image with a log whose verdict is not passed. If item 2's "one kept record stamped with the firmware's sha256" lands in `sim/runs/` with a `verdict:` header, a failed free check would block the deploy. No item says where that record lives.
   - "Free" is not "no setup". The dry run builds the flash image and needs littlefs and a MicroPython interpreter (USER-12, `scenario_run.py:142-147`). The brief's ★C4 and Q2 (a) drop that.
   - A turned-off simulator. Q4 (a) makes the role "on, off or another tool" the one setting, caveat "none". Today `tool_finder.find` raises `TOOL_OFF` for a tool with `on: false` (`scripts/spark/records/tool_finder.py`, the `find` function). That is a could-not-run, the very word the card wants gone.
3. **Does the direction answer "the architecture needs to be well made so that we can change these srtrategies and tools and its reusable, dry"?** It defers it.
   - Slice 0 changes the guard at `build_service.py:450-456` to `skipped` (item 1). Slice 1's seam card then moves the same guard into `coverage` (architect.md §3, "`build_service.py:399`, `:466` with the guard at `:450`: become `coverage`"). The same site changes twice.
   - Item 2's free checks include "the strategy's `problem`" (architect.md §3, Operations), but no strategy object exists until item 6. Slice 0 would call Wokwi's dry run directly, then be rewritten.
   - The main reason given for the seam's wait is P1078 and PR #1580. PR #1580 merged on 2026-11-25 at 08:53 Prague time (`gh pr view 1580`). The brief's Q2 (b) still says it waits on it.
   - DRY across seams: the architect shares only the lookup from contract to class, and "They share no base class" (architect.md §3). The pattern (role, contract, table, base, Fake) is then written twice, once per seam. That is the same shape, not shared code. The PO's "reusable, dry" may mean one strategy registry. Nobody asked him.

## 1. The ★ claims

- **★C1 · holds.** `scripts/spark/build/stages.py:112-113`: `NO_WOKWI_PART_TYPE_ENDING = StageEnding(build_codes.BOARD_NOT_IN_WOKWI, COULD_NOT_RUN,` / `"the board record names no wokwi_part_type")`. `build_service.py:454`: `if not board.get("wokwi_part_type"):`. Cite fix: the function starts at `:450`, and `:451` is its docstring. `:395` is `def _simulation(...)`.
- **★C2 · holds.** The walk project p934-display2's `.spark/build.json`: `"name": "simulation", "status": "could-not-run", "code": "board_not_in_wokwi"`, written `2026-11-22T11:44:33+01:00`. `scripts/flow.py:33-35`: "A build that stopped only because Wokwi has no model of its board (board_not_in_wokwi) is counted as done there, and the guide says there is no simulation."
- **★C3 · holds.** `flow_codes.py:11`: `PHASES = ("idea", "needs", "parts", "requirements", "build", "breadboard", "firmware", "simulate", "deploy")`. `:364`: "Ask Claude for the scenario command, and run it in your terminal. It uses Wokwi CI minutes."
- **★C4 · holds, a caveat dropped.** `scripts/run_scenario.py:21`: "--dry-run makes the free checks alone: it needs no token, starts no run and writes nothing (P399)." Dropped: the dry run needs `sim/` (★C17), littlefs and a MicroPython image (USER-12).
- **★C5 · holds.** `data/tools.json:5`: `"simulator": "wokwi-cli",`. `:21`: `"simulator": "wokwi-project",`. `tool_finder.find`: "%s: %s does not say it meets %r, so this step will not use it". Add: "off" ends as `TOOL_OFF`, a could-not-run.
- **★C6 · holds.** `grep -rli wokwi scripts/spark` gives 42 files, all `.py`. Per file: `sim_project.py:39`, `scenario_run.py:35`, `drawing.py:47`.
- **★C7 · partly.** The repository counts hold: 2 `wokwi.part` (led-red-5mm, tactile-button), 2 `wokwi.chip` (l9110s, vl6180x), 4 `skip`. The caveat "most with no `simulation` key (17 of 18 read)" has no source in the folder. PO-8 says the store's 10 shelf records all hold a `simulation` key. My count: the store's shelf has 10 records, 10 with the key. Its drawer has 114 records, 0 with the key. Change the caveat to: "the store's 10 shelf records all carry a `simulation` key (5 parts, 1 chip, 4 skips, PO-8). Its 114 drawer entries carry none."
- **★C8 · holds.** `parts/vl6180x-breakout/chip/vl6180x.chip.json:5`: `"controls": [`, `:8`: `"label": "Distance (mm)",`, `:9`: `"type": "range",`, `:27`: `"type": "boolean",`.
- **★C9 · partly.** The page says: "Custom Chips are usually written in C, but you can use any language that compiles to WebAssembly (e.g. Rust, AssemblyScript, etc.)". "Usually" is not "recommended". The caveat is refuted. The page's own description reads: "The Chips API is currently in beta." Change the caveat to: "The page labels the Chips API beta."
- **★C10 · partly.** The CI page: "Free users: 50 minutes", "Each user has a limit of simulation time per rolling 30-day window". The pricing page, read today: Pro "€25" "/seat/mo", "Annual billing", "Save 20%", "2000 monthly CI minutes". EUR 20 is the annual-billing figure (research-wokwi.md:9 says "annual billing"). The brief drops the billing period. The caveat "Hobby and Hobby+ CI minutes are not on the pricing page" is literally true but misleads. The CI page the brief cites lists "Hobby users: 200 minutes Hobby+ users: 500 minutes". It also caps a session: "Free and Hobby users: 5 minutes" of wall clock. And it offers "on-premise deployment of Wokwi CI" by contact. Change to: "Pro is EUR 20 per seat a month on annual billing (EUR 25 shown). Hobby 200 and Hobby+ 500 minutes per 30 days (CI page). A free session ends after 5 minutes of wall clock."
- **★C11 · holds.** `boards/firebeetle2-esp32s3.json`: `"wokwi_part_type": "board-esp32-s3-devkitc-1"`, `"wokwi_is_stand_in": true`. Issue #1455 line 3: "the FireBeetle 2 ESP32-C6 can be simulated today as a stand-in on Wokwi's ESP32-C6 DevKitC-1, free; GPIO14 is missing there."
- **★C12 · partly.** The release `esp-develop-9.2.2-20261109` says: "Added initial support for ESP32-C6, ESP32-H2, ESP32-C5, ESP32-C61, ESP32-H4 and ESP32-P4." The README's feature table, per my fetch, covers ESP32, S3 and C3 only, with a "GPIO strap" row. Neither source says the C6 boots or has strap-only GPIO. That is an inference from the other chips. Velxio's blog: "The entire emulation core is open source under AGPLv3." and "ESP-IDF, Arduino C++, and MicroPython are all available on the ESP32 family". The blog does not describe driving pins from outside (research-alternatives.md cites ESP32_EMULATION.md for that, not the blog). The blog names "new emulators for the ESP32, ESP32-S3, ESP32-C3 and ESP32-C6" in development. Change to: "QEMU's release names initial C6 support, and its README lists GPIO only for ESP32, S3 and C3. Velxio has no C6 today and announces one."
- **★C13 · holds, the caveat narrowed.** `stand_in/machine.py:4`: "Pins remember the level written to them, and a test sets an input with `set_level(gpio, level)` and reads an output". `import_firmware.py:3`: "Import a project's firmware on the Mac, without running main.py (P59, #7)." The P295 finding prices more than a bench: `finding.md:11`: "Cost: **large** for page plus bench". Change "priced a bench on it" to "priced a page plus bench on it".
- **★C14 · holds.** The store's councils/past-breadboard/architect.md:9: "The simulation cannot be part of the gate, because the clock's own simulation is `could-not-run`." refuter.md:35: "**CONFIRMED, it locks the clock.** ... the same lock that ruled out the simulation."
- **★C15 · partly.** `scripts/run_scenario.py:64-67`: `def main(argv=None, find_tool=None):` and `parser = argparse.ArgumentParser(...)`. Issue #1582 line 11: "Waits on PR #1580 merged and P1077." PR #1580 merged 2026-11-25. Change the caveat to: "P1078 waits on P1077. PR #1580 merged on 2026-11-25." I did not read P1077's state.
- **★C16 · partly.** The count reproduces: walk2 2026-10-23 01:16, walk3 2026-11-01 08:15, walk4 and p581-sound-joystick 2026-11-01 19:33:44, all `verdict: passed`. But a log is not a run. `scenario_run.py:128` names the log by the scenario alone, `:243` overwrites it with `write_text`, and `:186` and `:197` delete it on a refused or unstarted run. So 4 logs are a floor of last runs, not a count of runs. The caveat "It shows that runs are rare, not why" is also too weak. The walk project p711-walk4-button-led's diary.md:20-26 says why for one walk: "run_scenario.py --dry-run: ... exit 0." and "Wokwi run skipped. ... The council's condition (at least 10 minutes left) could not be confirmed. The run waits for the PO." Its line 3: "in auto mode (the PO away until 20:49 CET)". Change to: "at least 3 distinct runs (logs are overwritten per scenario). In one walk the free checks ran and the paid run waited for the PO's yes, because the minutes left were unknown."
- **★C17 · holds.** `scenario_run.py:133-134`: `if not all((self.sim / name).is_file() for name in ("diagram.json", "wokwi.toml")):` / `return Refusal("no simulation project in %s: build first with /spark:build --keep ." ...`. `ls sim` in the walk project p934-display2: `flash-with-firmware.bin`, `runs`.
- **★C18 · holds.** My run in the walk project p934-display2: "Ran 35 tests in 0.006s" / "OK".
- **★C19 · holds.** `machine.py:26`: "The rule for ADC, SPI, I2C and I2S: each keeps its arguments and returns a fixed value. None models a device." `:74`: "Remembered, never called: the stand-in has no edges."
- **★C20 · holds.** `boards/epaper-2in9/board.json:9`: `"chips": [{ "id": "chip", "type": "github:bonnyr/wokwi-ws29v2-custom-chip@0.0.5" }],`. `gh api repos/wokwi/wokwi-boards --jq .license` prints null.
- **★C21 · partly.** `boards/xiao-esp32-c6.json`: "Wokwi wakes this chip from a timer but not from a GPIO - established by experiment, see firmware/micropython/sim/README.md. Deep sleep is a bench test." True for the XIAO C6 record. But the clock wakes by timer only. Its `firmware/main.py:3`: "A timer wakes it at each hour edge". `:11-12`: the press wake was "DROPPED by the PO on 2026-11-23". So the same record says Wokwi can show the clock's kind of wake. PO-19 ("Timer wake on the C6 in Wokwi is not checked") and PHYS-6 ("the clock project ... has its wake tested only on the bench, whatever the simulator") contradict the record. Add to the caveat: "the clock wakes by timer, which the record says Wokwi simulates."

## 2. The brief against its detail

- **Q2 (a) looks free of waits, and it is not.** items.md item 2: "depends on: the P1078 #1582 pattern for the envelope". TL-11 sizes the free Operation on "P1078's pattern". The brief gives (a) no dependency and (b) "waits on P1078 #1582 and PR #1580". Both depend on P1078. The PR #1580 part is stale.
- **Q4 (a) caveat "none"** drops that "off" is a could-not-run today, and drops TL-12: "A project can need two simulators (Wokwi for the parts it models, logic level for a board it lacks)". Q4 (c)'s caveat reduces this to "needs two strategies that run".
- **Q6 (c) caveat** "the page is a static file and needs a local bridge" is stated as fact. The architect calls it "H, PO-22" and lists "The page's code and its request mechanism" as unchecked (architect.md:247).
- **Q9's premise** "nobody ran the scenario" is stronger than its sources. PO-2 says p711-walk4-button-led holds "one scenario file, never run". Its diary shows the dry run ran (exit 0). USER-7 says reaction-game's scenario was "never run (no `sim/runs/`)". A refused run deletes its log, so no log does not show no run. Q9 also asks "Why did you skip it", but the p711 walk ran in auto mode with the PO away. The agent held the run, not the PO.
- **PO-18 is dropped.** The brief never says that P999 alone may turn the clock grey (`every_part_skipped`). That is the strongest rival to item 1 and to the Outcome's proof project.
- **The architect's unchecked list is dropped.** "The exit code and the goldens after the stage changes from `could-not-run` to `skipped`" and "PR #1580 and P1078's plan" (architect.md:244-245). The brief's Riskiest and Q2 carry neither.
- **The rabbit hole "29 modules"** drops TL-5's base. Tech-lead.md:272: "The split of the 42 modules rests on up to five lines read per module, not a full read."
- **★C10** drops research-wokwi.md's "annual billing" and its wall-clock cap.
- **★C13** narrows P295's "page plus bench" to "a bench".
- **PO-19 against ★C21** disagree on the timer wake. The brief keeps neither side's caveat.
- **The Outcome** promises a proof on the clock: "the board's state says which strategy covers it or why none does, in grey". After P999 a strategy covers the clock's board. The "why none does" branch then has no known project to show it.
- **Already decided D-c** is read as "a build that stopped only on `board_not_in_wokwi` counts as done". The architect's item 1 removes that rule's code. The brief does not mark item 1 as reversing a decision of the PO's (2026-11-21), and does not ask him.
- **verification.md** is still the template (the template's fill marks). The brief's "Stands on: 9 H" names no list.

## 3. Rival explanations the folder does not rule out

- **The architect's direction (free checks and honest words first).** Rival: P999 (S, the PO's yes of 2026-11-22) removes the only `board_not_in_wokwi` board. It also makes the Wokwi dry run possible on the clock. Then the harm the card names has no instance, and slice 0's item 1 serves no current board. The "reads as a failure" harm was seen once (USER-5, n = 1), and the page already says "No simulation: Wokwi has no model of this board. You test it on the real board." (USER-5). The smallest fix may be the build answer row's words, not a new Operation.
- **The seam after, with no behaviour change.** Rival: the seam first is cheaper in total. Slice 0 edits the guard, the free checks and the flow words. Slice 1 then moves the same sites behind `Simulator`. The memory rule "No work that gets redone" points the other way. The stated blocker, PR #1580, is merged.
- **Gate A: evidence, never a condition.** Rival 1: a condition already exists and is free. `image_evidence.py:433` refuses a deploy after a failed run on the same image. A gate A condition of "no failed run on this image" costs no minutes and does not lock the clock. The options set lacks it, and the architect's rejection of "a condition only where covered" (a paid toll) does not apply to it. Rival 2: the architect rejects "left out" because "no later step reads the result". An evidence row that never gates is also a row nobody must read. The same pre-mortem (PO pre-mortem 6) applies.
- **★C16 as a value risk.** Rival: the rarity is friction and rules, not low value. (a) Every paid run needs the PO's yes (D-a), and he is often away. (b) The minutes left are unknown (P413, the p711 diary). (c) A scenario must be written first (the walk project p829-button-light's diary.md:365: "No scenario is written yet, so ask Claude to write one first"). (d) A walk council limited runs ("one Wokwi run only if the free checks pass", the p711 diary line 5). (e) Logs are overwritten, so the count is a floor. None of these is ruled out, and (b) and (d) are written in a diary the folder did not read.
- **The replay test.** Rival: it cannot test A1 fairly. The clock's repository starts on 2026-11-22 at 19:05, after the deploys from 13:04 that day. Its tests were added at 20:50 (`df94542`) and later. Replaying today's tests on older commits uses tests written after the faults were found. The fixes before the bench are physical ("Turn the picture around", "a press counts only after 40 ms held", the refresh timing). An import check and host tests on CPython would not catch them. The pass line "at least 2 faults" may fail by design, or pass by hindsight.
- **★C18 as a habit.** Rival: the clock has host tests because no simulator covered it, and only from 2026-11-22. One project shows no habit.

## 4. Numbers without unit, population, period or provenance

- "9 H" (Stands on): which nine is not listed.
- Sizes "S", "M", "L", "S plus M": no unit (hours, days, PRs). TL-11 calls them "this seat's sizes", an opinion.
- "17 of 18 read" (★C7): no population, no reader, no date. It conflicts with PO-8.
- "EUR 20 per seat a month" (★C10): the billing period (annual) is missing. "2000 CI minutes": no period. The page says "monthly".
- "15 walk folders hold 4 scenario logs, which are 3 distinct runs" (★C16): no period (the oldest log is 2026-10-23). It is a floor, because logs are overwritten and deleted. "16 walk projects" (PO-1, architect.md:155) against 15: one is a file, walk4-paste-to-start.md.
- "34 run logs in the last 30 days" (the p711 diary, not in the brief): the logs likely include deploy logs under `sim/runs/board/`. My count today is 58 logs under `sim/runs/` in all walks, of which 4 are scenario logs.
- "28" deploy logs (C22): the period, 2026-11-22 to 2026-11-23, is missing.
- "35 tests ... well under a second": three timings exist, 0.019 s (brief), 0.031 s (USER-2) and 0.006 s (mine). Fine for "under a second". No machine is named.
- "29 modules" (rabbit holes): the provenance is five lines read per module.
- "at least 2 faults that reached the bench" (pass line): no denominator (how many commits or fixes are replayed) and no period.
- "6 agents, 499 calls and about 90M input tokens" (Depth comment): no source file cited.
- "50 minutes": "simulated time" in ★C10, plain "minutes" in USER-10 and Q-a. The unit matters, because wall time on a free session is capped at 5 minutes.

## What I could not check

- Whether `wokwi-cli lint` or `chip compile` need a token. That needs a run.
- P1077's state, so ★C15's remaining wait is unread.
- Whether a `skipped` build exits 0 in `build.py`. I read the exit table, not the build script's mapping.
- The page's code ("static, no script").
- The walk projects' git history beyond the clock and reaction-game. reaction-game's history holds no `sim/runs` log.
- The README.md that appeared in the folder at 09:39 during my read. I read only two lines of it.

## Searches

none. Page reads: https://docs.wokwi.com/chips-api/getting-started, https://wokwi.com/pricing, https://docs.wokwi.com/wokwi-ci/getting-started, https://github.com/espressif/esp-toolchain-docs/blob/main/qemu/README.md, https://developer.espressif.com/blog/2026/07/velxio-browser-based-esp32-simulation/, and the GitHub API for espressif/qemu releases, wokwi/wokwi-boards and wokwi/wokwi-cli releases.

## Second pass, 2026-11-26

Read on branch p1190-simulation at f4fea35e, with README.md as later committed in f33b1763. Only the sections the session changed. Nothing written but this section. No paid run. One free run: `scripts/import_firmware.py --json` on a temporary copy of the clock's firmware/ and tests/, removed after.

### D rows and the PO's own choices

- D1 to D9 each end "delegated, the PO's to change". Holds.
- Q1, Q5, Q9, Q10, Q11, Q3's non-goal reading, Q6's "the editor" and Q7's dependency are marked queued, the PO's alone. Three places decide them anyway.
  - D2 writes "a free check's record never blocks a deploy" into "must not get worse", a standing rule. Its sources say the opposite of standing: delegated-architect.md decision 6, "Whether a failed own test should stop a deploy is a gate choice, and it is the PO's", and delegated-po-assistant.md Q8, "the PO's, with Q5". D8 itself says "until the PO decides". Smallest fix: "never blocks a deploy until the PO answers Q5".
  - README.md TL;DR: "The simulation is evidence at gate A and never a lock (his to decide)." That states Q5's answer as the direction. All three seats advise evidence plus the free condition "no failed run on the current image" (council-answers.md, advice), which is a lock on a failed run. Smallest fix: "Gate A is his (Q5). The council advises evidence, and a failed run on the current image still stops the deploy."
  - items.md item 12, value proven by: "its licence read, and the rule written". The licence rule for another author's chip is Q7's dependency, the PO's alone.

### 2. The changed sections against their detail

- **D3 "3 of 3" is stronger than the tally for the order.** The tech lead puts P1078 before `check-firmware` (delegated-tech-lead.md, short version). council-answers.md row Q2: "The session takes the two". The PO assistant orders A1's forward test before P1078 and the seam, and puts `check-firmware` "on P1078's envelope". D3 drops the test from the order. So (d) as separate PRs is 3 of 3, and the order is the session's pick.
- **items.md item 2 against the brief.** Item 2: "P1078 #1582 is its next user, not a blocker". Brief Q2 (a): "It depends on the P1078 pattern too (items.md item 2)". The PO assistant seat: "on P1078's envelope". One of the two lines is wrong. Also P1078's body keeps "flash_image with import_firmware" as one line on #1105. Item 2 takes half of it.
- **D5 drops two conditions.** The architect's: "off" must not be the tool's `on` flag, because the same tool compiles chips for free. The PO assistant's: "The mapping goes to the PO before P410 closes as replaced, because P410 holds his own words." D5 also moves a `TOOL_OFF` could-not-run (exit 2) to `skipped` (exit 0) with no question like Q11.
- **The Test line.** "3 of 3 on the split" overstates the PO assistant's line, whose pass needs a run and a failed check together. Dropped from it: "judged after the fact by the session that wants the result. It needs a rule", and its bar, a fault "that would stop `ready` or break a must line". The brief's yield bar is only "a firmware change".
- **Q11** says the flip "also counts as done" and does not name the exit code an agent reads (2 becomes 0), which item 1 and correction 5 name.
- **★C21's new caveat** says the record "says Wokwi simulates" the timer wake. The record's field is `deep_sleep.simulated_by_wokwi: false` (`boards/xiao-esp32-c6.json`). Only its note says a timer wakes, by an experiment on the XIAO C6 part, not on the DevKitC-1 stand-in that P999 uses.
- **README main point 6** drops "most likely" from ★C25 and the tech lead's "★C25 can end there instead" (earlier stops at `build_service.py:403-416`).
- **The frame** still says "Q0 to Q8", although council-answers.md tallies the tech lead's fix. D9 answers Q12, which is in neither Questions nor Options.
- **items.md item 12** still proves value by "one free run", which the tech lead flagged ("it says free and also needs minutes") and D7 contradicts.

### 3. Rivals the folder does not rule out

- **P999 first, and ★C25.** The clock's firmware uses GPIO14: the walk project p934-display2's `firmware/pins.py:6`, `EPD_CS = 14`. P999 says GPIO14 is missing on the stand-in. A3's "result that would change the decision" is "the stand-in lacks a pin the clock uses". Both seats listed GPIO14 as unchecked. Rival: P999 needs a pin move on the clock, or ends at an earlier stop. Before `every_part_skipped` the stage can end `tool_missing`, `simulation_fact_missing` (the board's own parts, P792) or `chip_not_compiled`, all could-not-run (`build_service.py:403-416`, `stages.py:110-114`). The e-paper skips, so its pin may not reach the diagram. Not run.
- **`check-firmware` before P1078.** Rival: it writes an Operation envelope before P1078 sets the scenario run's pattern, which is the redone work D3 meant to avoid. The tech lead's order avoids it.
- **P1078 waits on nothing.** Holds. `gh issue view 1581`: CLOSED, COMPLETED, 2026-11-24 02:14 Prague time.
- **The seam with no behaviour change.** Rival: with one Adapter and the flip held on Q11, the seam changes nothing a person sees. If Q11 is no, the card proves only that the goldens hold. A9 is rated high on a judgement with no test.
- **The flip.** Rival: after P999 no real board reaches it. Its only proof is a fixture (item 1). A8's test "on the clock after slice 0" then tests P999's `every_part_skipped`, not the flip, and "slice 0" no longer exists in D3's order (risks-and-tests.md, usability row and A8, collection plan).
- **The split pass line.** Rival: in D3's order the use half cannot test A1. A1 is "once on the page". Item 3 (the page line) depends on item 1, the last PR, which waits on Q11. Until then the log can only read "the session unasked", which tests Claude's habit, not the page.

### 4. Numbers without unit, population, period or provenance

- "3 of 3" (D3): the order is 2 of 3 at most.
- "over the next 3 walks": no period, and no split between walks with the PO present and away. Three walks with no fault anywhere give "no information" and reach neither the pass nor the "below the line" branch.
- "at least 1 fault": no judge and no bar for "fault".
- "costs under a second" (`check-firmware`): measured on one project only. Tests 0.006 s to 0.031 s (three runs), and my import check on a copy of the clock, 0.21 s wall, 2026-11-26. No machine named.
- "none after 2026-11-01" (README point 1, risks-and-tests value row): a floor of overwritten logs cannot bound the last run. The brief no longer names the population (how many walk folders).
- "S", "M" in Q2 (d): still no unit.
- D1: the PO's delegation of 2026-11-17 and 2026-11-20 is cited to "the session's memory", which no repository file holds.

### What I could not check

- P999's build on the clock, so ★C25 and the GPIO14 rival stay H.
- Whether a skipped stage changes the flow's exit, as against the build's. I read `verdict` (`build_service.py:506-510`), not `scripts/flow.py`'s mapping.
- The page's code.
