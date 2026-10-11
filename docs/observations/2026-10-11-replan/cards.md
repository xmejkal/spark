# Card drafts: the top of the backlog matches the v1 scope (2026-10-11)

Drafts only; nothing is posted. Basis: `docs/2026-10-11-replan.md` and `after-v1.md` (branch `replan-basic-journey`), the cards as
read with `gh issue view` on 2026-10-11, and the PO's addition of the same day (only the top is refined; the rest is closed into
a few version epics). **Full text only for items 1-7; one line for the second slice; nothing below is refined.**

How to read a block: *Why* is the card's **Needed by**, the *done-test* is its **Value proven by**. "Pending Q n" is one of the
replan's six questions, still open. A card's slice is the PO's (TEAM.md), so every slice here is a proposal: the board has no
"Basic journey" option until he answers Q2; the fallback names today's nearest option. New cards enter **Idea**; the PO orders Ready.
P195-P197 are the **next free numbers, check before filing** (highest filed: P193 = #145; no file in the repo uses P195-P197).

---

## A. The first slice, items 1-7

### A1. Item 1 - NEW, P195 (chore, S)

**Title:** `P195 — Nothing walks the basic journey end to end, so a broken stage goes unseen → one test runs button-and-LED through every stage that works today and names the one that breaks`
**Slice:** pending Q2 ("Basic journey"; fallback "3 Firmware on a Mac") · **After:** nothing · **Replan:** item 1, first in Ready

**Needed by**
The PO, 2026-10-11, verbatim: *"To be honest I still feel like we're spending too much on various mutations and i dont know what, but im not even sure if the example pproject would still work and if the basic journey really works for some basic things including all stages"*. The replan (item 1) puts this first because it is the slice's acceptance test: every later item counts as Done only once its stage is in it. It is P158's C11 (`docs/archive/2026-10-10-p158-plan.md`) without the baseline.

**Value proven by**
`python3 -m unittest discover -s tests -p test_journey_basic.py` is green, and removing any one stage's output (the sheet, the diagram, the board, an export) turns it red, naming the stage.

**Body**
- What: `tests/test_journey_basic.py` takes the button-and-LED fixture (`tests/data/breadboard/button-light`) through each stage the replan's table marks as working today (requirements, build with its board, Wokwi diagram and breadboard sheet, PCB and 3D export). It runs the real build where `tsci` is installed. Where it is not, the build stage reports `could-not-run` by name, and the run says that only the stages after the build were exercised.
- Grows: items 2-6 each add their stage (`pins.py`, the Mac import, `check_all`, `ready` in Wokwi, the deploy dry-run).
- Depends on: nothing.
- NOT: a baseline or snapshot of three projects (P184 #133 is Done; P158's baseline waits), a Wokwi minute, a mutation sweep, a new flag on `check_spine`.

### A2. Item 2 - NEW, P196 (story, S)

**Title:** `P196 — /spark:build leaves no firmware/pins.py, a second command writes it → the build writes it, equal to assign_pins --emit-pins`
**Slice:** pending Q2 (fallback "3 Firmware on a Mac") · **After:** P195 · **Replan:** item 2

**Needed by**
The PO, 2026-10-11, verbatim: *"we need to make sure the haanding over works, that it all works together, the schema, parts, firmware, pcb or even 3d model later, but at least to breadboard including working firmware is important, that's what its for."* Walked on 2026-10-11: `commands/build.md:119-120` and `docs/guide/journey.md:922` give `assign_pins.py requirements.json --emit-pins firmware/pins.py` as a separate step, so after `/spark:build` the firmware has no pin file, and the firmware "never types a GPIO number" (`build.md:131`). The user lens named it a stall.

**Value proven by**
After `/spark:build`, `firmware/pins.py` exists and equals the output of `assign_pins.py requirements.json --emit-pins`. A test pins it, and P195's test gains the stage.

**Body**
- What: `check_spine.py --keep DIR` writes `firmware/pins.py` beside `board.tsx` and `breadboard.md`, from the same code as `--emit-pins`, with a line in the kept-files report like theirs.
- Open design points, the card's to settle: whether an existing `pins.py` is left alone (as `board.tsx` is) or rewritten (it is generated, never hand-edited).
- Depends on: P195.
- NOT: firmware generation (spark exports facts, Claude writes behaviour; the PO's direction of 2026-10-01), a change to how pins are assigned, removing the separate `--emit-pins` step.

### A3. Item 3 - existing #7, P59, part a only (S)

**Title:** unchanged. **Slice:** stays "3 Firmware on a Mac" · **After:** P196

**Value proven by - the line that changes**
```diff
- `firmware.main` imports **with a fake `machine` on the path** (CPython or the `micropython` unix port) in a spark-generated project, and the chain reports a signal the requirements ask for that the firmware never drives **or never reads**.
+ spark ships the `machine` stand-in and one Mac command; button-and-LED's firmware imports under CPython with it, and its LED pin reads 0, then 1 (released, pressed). P195's test gains the stage.
```
(The acceptance-line note in brackets stays as history. The reporting half moves to P74 #8, second slice.)

**Append to the body**
```
### Scope for v1 (2026-10-11 replan)
Item 3 of the first slice (docs/2026-10-11-replan.md). Part a only: spark ships the `machine` stand-in and one command that imports a project's firmware on the Mac. Part b (the chain reports a signal never driven or never read) is P74 (#8), second slice.
- Evidence: the comment of 2026-10-11 on this card. A 15-line stand-in on the Mac's MicroPython read the LED 0 released and 1 pressed.
- Needs a button-and-LED firmware file under tests/data. The one written on the walk is not in the repository; this item commits it.
- Irrigation's unimportable main() (this card's first case) is not fixed by a stand-in; irrigation is not in v1.
- Depends on: P196 (the firmware imports pins.py).
- NOT: chip-accurate pins (pins remember values; the test sets an input), checking undriven pins (P74), running on the board.
```

### A4. Item 4 - NEW, P197 (story, M)

**Title:** `P197 — A fresh button-and-LED project's check_all exits 2, so no new project gets a clean check → it exits 0 on button-and-LED, and nothing that could not look reads as a pass`
**Slice:** pending Q2 (fallback "4 v1 on two projects") · **After:** P195 · **Replan:** item 4

**Needed by**
The PO, 2026-10-11, verbatim: *"...im not even sure if the example pproject would still work and if the basic journey really works for some basic things including all stages"*. The replay of 2026-10-11 (comment on #6): *"No fresh project gets a clean check. `check_all` exits 2 on both. Physics cannot look, because init describes no rails. On the button-and-LED project, rules-vs-netlist has no rule to compare."*

**Value proven by**
`check_all.py --project .` on the button-and-LED fixture exits 0. P195's test gains the stage.

**Body**
- What: how it gets there is this card's design. The replan names the routes, it does not choose: P111 #45 (an explicit not-applicable value), P108 #42 (the answer counts the values nobody measured), P118 #52 (each `!` line says what clears it), or rails seeded from the board file. A route that is taken leaves its own card's value line met.
- Depends on: P195.
- NOT: a weaker check. "A stage that could not be exercised is could-not-run, never ok" (README, last line) holds. Exit 0 comes from giving the checks what they need, or an explicit not-applicable value, never from skipping or relabelling. An `ok` that rests on unmeasured values is allowed only with their count in the answer (P108's decision of 2026-10-05). Not irrigation, not the motor example, not a new check.

### A5. Item 5 - existing #64, P130, retargeted (M)

**Title (changes):**
```diff
- P130 — The documented example has a scenario, run once
+ P130 — The basic project passes in Wokwi: a harness waits for `ready`, Claude writes the scenario, one run is dated
```
**Slice:** stays "3 Firmware on a Mac" · **After:** item 3 (the Mac check runs first, so no minute is spent on firmware that does not import; TEAM.md: "any path that runs locally comes first")

**Value proven by - the line that changes**
```diff
- commands/build.md's scenario drives the documented example's own parts (a button press, the motor-driver pin's level), and one dated run of it is pasted.
+ A harness runs a built project in Wokwi and waits for `ready`; the `ready` contract (the firmware prints `ready` on the serial line once its setup is done) is written in commands/build.md; a test of the harness passes with no Wokwi minute spent; and one dated run log of button-and-LED passes with a scenario Claude wrote from the person's words. P195's test gains the stage (the harness test, not the run).
```

**Append to the body**
```
### Scope for v1 (2026-10-11 replan)
Item 5 of the first slice. The project is button-and-LED, not the motor example this card was filed for (FireBeetle + L9110S + two buttons).
- spark ships the harness and the `ready` contract. Claude writes the scenario's steps: pins.py holds pins, not behaviour, and spark does not emit behaviour (refuter finding RF-5, docs/observations/2026-10-11-replan/refuter.md).
- Evidence: the comment of 2026-10-11. A hand-written scenario (wait for ready, press, expect the LED pin high, release) passed in Wokwi once the diagram wired the serial monitor (P190 #142, Done).
- The run spends Wokwi minutes: the PO's yes (TEAM.md), and WOKWI_CLI_TOKEN. Pending Q5: may this run spend minutes, and is a free Wokwi account part of v1 for a hobbyist (VISION.md says the hobbyist may have no Wokwi licence).
- NOT: a scenario shipped for any project, CI wiring, the motor example's scenario.
```

### A6. Item 6 - existing #144, P192, and #145, P193 (S + M + bench)

**Title (#144):** unchanged. **Slice:** none today; Ready needs one, pending Q2 · **After:** item 5 · **Waiting on** (for c): hardware

**Value proven by - the lines that change**
```diff
- `/spark:setup` offers the free flashing tool (`esptool`), and one documented command puts the built flash image, MicroPython and the project's files, onto the board. A board-specific MicroPython build is used where the board needs one. Checked on the PO's FireBeetle 2 ESP32-S3 with the button-and-LED firmware, on a breadboard wired from the sheet (P191).
+ `/spark:setup` offers the free flashing tools (`esptool`, `mpremote`), and one documented command puts the flash image that passed the simulation, MicroPython and the project's files, onto the board. Checked on the PO's FireBeetle 2 ESP32-S3 with the button-and-LED firmware, on a breadboard wired from the sheet (P191): the board prints `ready`.
```
(Struck: "A board-specific MicroPython build is used where the board needs one" - no chip table for one board; a build the PO's board needs is a card from the bench, pending Q5: N16R8 or N4.)

**Append to the body**
```
### Scope for v1 (2026-10-11 replan)
Item 6. The PO, 2026-10-11: "otherwise yes, I would do P192, just not sure where it belongs in the backlog, might not be so necessary yet, but soon robably". It is the last handover, one item behind the simulation. Split when it enters Ready:
- (a) esptool and mpremote in data/tools.json, offered by /spark:setup. Done when `tools.py --status` lists both. Size S.
- (b) `deploy.py --dry-run` flashes the image that passed the simulation (the one flash_image.py wrote); P193 (#145) goes with it. Done when a test pins the printed flash lines. Size M.
- (c) the PO's board prints `ready` after the flash. Bench. Needs B21 (bin #15), the board's SKU and revision. Suggested: run it in item 7's bench session (pending the PO).
Suggested shape at Ready: (a) and (b) are tasks of this story; (c) is its closing proof and the story waits on hardware, so a bench step does not hold a Build slot. P195's test gains (b)'s dry run.
NOT: a chip table (P187/P189 #136/#138 are closed into a later epic), flashing anything but the image that passed.
```

**#145 (P193):** title, body and value line unchanged. **Slice:** none today, set with #144.
**Append one line:** `Rides with P192 (b) (replan 2026-10-11, item 6): same dry-run wording as deploy.py --dry-run; Done with it.`

### A7. Item 7 - existing #6, P100, round A only (M)

**Title (changes):**
```diff
- P100 — Spark in real use: a new idea and an existing project, each walked through with the person
+ P100 — Round A: the PO takes button-and-LED from an idea to a lit LED on a breadboard, from the pages alone, predictions first
```
Pending Q4: if the PO picks a project from the menu (a battery sensor node, a USB MIDI foot controller, or his own), only the project's name in the title and below changes. The label `epic` becomes `story` (pending the PO): an epic counts only in Discovery and Design, and round A is one walk. **Stage:** leaves Discovery. **Slice:** stays "1b From a vague idea" or the PO's choice (Q2) · **After:** item 4 for the talk, item 6 for the bench.

**Value proven by - the line that changes**
```diff
- to be set in refinement.
+ A logged bench verdict. The PO, from the README and the pages alone, takes button-and-LED from an idea in words to a lit LED on a breadboard on his FireBeetle. The predictions are written and dated before the walk and scored afterwards by someone who did not write them; a diary is kept; each stall is filed as a card. This meets P79's (#16) pass line.
```
(Who scores: pending the PO. The scoring rule is R2.6's, the comment of 2026-10-09.)

**Append to the body**
```
### Scope for v1 (2026-10-11 replan)
Item 7 of the first slice: round A only. Rounds B and C wait (see the comment of the same date). The discovery folder docs/discovery/2026-10-09-p100-real-use/ and the PO's D5/D6 words stay as the record.
- Before the walk: P113 (#47) and P138 (#72) are fixed. P185 (#134, the drawer's functions) runs first only if the PO says so (pending Q4).
- The talk (idea to sheet to firmware to simulation) needs items 1-5; the bench needs item 6 and B21 (bin #15).
- D-DP3 on #94 said round A runs on today's spark before any output-changing card merges. Items 2 and 4 change output before this walk. The replay of 2026-10-11 (the comments on this card and on #16) is the today's-spark record. Pending the PO: D-DP3 superseded.
- NOT: irrigation, parts the store lacks (the research route), a PCB order, mutation scoring.
```

### A8. Fixed before the walk - #47 (P113) and #72 (P138)

One appended line each; no other change.
- **#47:** `Fixed before the walk (replan 2026-10-11, item 7): without it the walk's /spark:setup can install npm packages into the nearest parent folder, on the PO's Mac the home folder.`
- **#72:** `Fixed before the walk (replan 2026-10-11, item 7): the walk's /spark:init writes a package.json note that says a bare npx tsci and names no bun.`

---

## B. The second slice, one line each

Appended to each card (no other change; none is closed). Order: the walk decides.
- **#8 P74:** `Second slice, first (replan 2026-10-11): the firmware checked against the pins it should drive is VISION's "next"; item 3 already proves the firmware imports, and the case in this card's value line is irrigation's, which the walk does not use.`
- **#102 P165:** `Second slice (replan 2026-10-11): a second project on the same board is refused today with "held by button-light" (journey.md:308) and needs this card; one project on a breadboard is not stopped by a PCB-only fact (body_mm already only warns).`
- **#13 P77:** `Second slice (replan 2026-10-11): this is the PO's "would the example still work"; P195 covers button-light first, every other example is regenerated after the walk.`
- **#44 P110:** `Second slice (replan 2026-10-11): PCB and 3D export works for a fresh build today; this bites when board.tsx was edited, so it waits for the walk to say.`
- **#128 P182:** `Second slice (replan 2026-10-11): the README's first screen follows the journey that works, so it can say what works.`
- **#81 P147:** `Second slice, last (replan 2026-10-11): before any stranger. The manifest reads 0.8.1 now and the PO decided on 2026-10-06 that every merge raises it, so what is left is the proof that a GitHub install receives a change; v1 is walked on the PO's working-folder install, where this is invisible.`

---

## C. Closing the parked cards into version epics

The PO, 2026-10-11, verbatim: *"Like I really want t make sure we just shrink and siplify our plans and make sure its all up to date. ... Maybe we can somehow plan the versions in decreasing detail? I want it lie that in general , like in scrum / agile / lean, that only the to of the backlog is really refined t detail and the lowe on the backlog the less details and refinement and time spent on it."* This replaces the replan's "After v1" slice option for Q2 (proposed, pending his yes): 55 of the 57 cards close into five epics, #123 stays open as the store epic, and #5 has no epic yet.

### C1. The close comment, one template for all 55

```
Closed into <epic, #n> for a later version, per the replan of 2026-10-11 (docs/2026-10-11-replan.md). Reason: <reason>. Nothing is lost: this card's text and comments stay here and the epic links it. Reopened the moment the walk (P100 round A) or a second project needs it.
```
`<reason>` by epic:
- the store: one person with one local store is enough for v1
- checks for bigger projects: button-and-LED has no rails, motor, I2C bus, copper or capacitors, so these checks cannot trip it
- one core: an input to the v2 refactoring, not v1 work
- team and QA tooling: process, not product, for the first walk
- a stranger's first install: v1 is walked on the PO's Mac; a stranger's machine stays slice 5

### C2. The five epics (bodies)

Each epic: label `epic`, stage Idea, no slice, no value line until the PO starts it. P-numbers P197-P201 if the board's style wants them (check). Pending the PO's yes to all five.

**1. `v2 candidate: one core — spark as a package that the CLI, MCP and Claude call`**
```
### Needed by
The PO, 2026-10-11, verbatim: "Maybe in the next version I will want to do a big refactoring from just python scripts and filesbeing handed over to a real object oriented system , a package or module, that then MCP or AI or human through CLI can be acccessed and its calling the same code, so we don't have extra artefacts and code that's not refactored and reused etc."
### Value proven by
to be set when the PO starts it.
### Body
Input, not plan: P158 (#94) and its work, all on main: docs/archive/2026-10-11-p158-short.md (read first), docs/archive/2026-10-10-p158-architecture-design.md, docs/archive/2026-10-10-p158-plan.md, docs/archive/2026-09-30-refactoring-architecture.md, docs/mcp.md. Refined only when it is next; not before the basic journey has been walked (P100 round A).
Closed into it: #94 #89 #136 #138
```

**2. #123, P178 - reused: retitle `Later: the store, shared`** (body unchanged: the PO's words and his order stay). Append:
```
Version note, 2026-10-11: no longer "the next version". The PO's words of 2026-10-11 name a refactoring to one core as the v2 candidate; the store comes after it or with it, his call. Step 1 of "in his order" (test what works now) is the replan's first slice. Closed into it: #17 #19 #20 #21 #22 #23 #82 #83 #84 #85 #93 #96 #99 #101 #114 #118 #119
```

**3. `Later: checks for bigger projects`**
```
### Needed by
The PO, 2026-10-06 (#70): "an epic for full circuit checks, adding analogue and board checks to spark. Reuse as many existing solutions as possible and integrate them seamlessly into the spark workflow."
### Value proven by
to be set when the PO starts it.
### Body
Rails, motors, I2C, copper, capacitors, a second board, fabrication. The basic journey's project has none, so these return the moment the walk or a second project trips one. Holds meanwhile: a check that could not look is could-not-run, never ok (the README's last line; P133 #67's rule).
Closed into it: #9 #41 #43 #54 #55 #56 #60 #63 #67 #70 #76 #78 #79 #86 #87
```

**4. `Later: team and QA tooling`**
```
### Needed by
The PO, 2026-10-11: "I still feel like we're spending too much on various mutations and i dont know what". And, 2026-10-08 (#97): "how much we can actually trust that when something is said to be working, it actually really iss tested and validated."
### Value proven by
to be set when the PO starts it.
### Body
Mutation scoring, test speed, coverage, the push gate, process data, drawn maps, the demo home. The Definition of Done stays as written until the PO answers Q6 (mutation on every change, or only on logic).
Closed into it: #27 #28 #30 #39 #97 #103 #108 #111 #113 #121 #135 #137
```

**5. `Later: a stranger's first install`**
```
### Needed by
The PO, 2026-10-06 (#66): the cards P104's councils found "are linked under epics. This one holds what a stranger meets first". VISION.md: slice 5 tests it with a real stranger.
### Value proven by
to be set when the PO starts it.
### Body
Pinned MCP servers, init --force, the bug form, boards/README.md, `--on` and `--dry-run`. v1 is walked on the PO's Mac. Not in here: P113 (#47) and P138 (#72), fixed before the walk, and P147 (#81), second slice.
Closed into it: #46 #48 #53 #57 #61 #62 #66
```

No epic fits **#5 (P76, from a vague idea to a block-level schematic)**: it stays an open Idea card until the PO says where it goes (pending the PO).

### C3. Which epic each card goes under

| # | P | card | goes under |
| --- | --- | --- | --- |
| #17 | P94 | The store and its ways in, designed | Later: the store, shared (#123, reused) |
| #19 | P87 | Records are inert | Later: the store, shared (#123, reused) |
| #20 | P89 | --need tells the truth about candidates | Later: the store, shared (#123, reused) |
| #21 | P90 | A document comes back, checked | Later: the store, shared (#123, reused) |
| #22 | P91 | A shelf for the parts you chose | Later: the store, shared (#123, reused) |
| #23 | P92 | Records written through parts.py, read as JSON | Later: the store, shared (#123, reused) |
| #82 | P148 | A project's own copy of a record falls behind silently | Later: the store, shared (#123, reused) |
| #83 | P149 | A Wokwi chip has no identity | Later: the store, shared (#123, reused) |
| #84 | P150 | spark writes compiled chips and promoted records into its own… | Later: the store, shared (#123, reused) |
| #85 | P151 | "verified" means four different things, and --show calls… | Later: the store, shared (#123, reused) |
| #93 | P157 | Choosing among equivalent modules | Later: the store, shared (#123, reused) |
| #96 | P160 | The store editor | Later: the store, shared (#123, reused) |
| #99 | P162 | G, research only the gap | Later: the store, shared (#123, reused) |
| #101 | P164 | The real store has no guard against an agent's unscoped… | Later: the store, shared (#123, reused) |
| #114 | P174 | The store's write lock follows TMPDIR, so two processes with… | Later: the store, shared (#123, reused) |
| #118 | P175 | parts.py --requirements writes back two hand-written entries… | Later: the store, shared (#123, reused) |
| #119 | P176 | The component-name rule has a third copy | Later: the store, shared (#123, reused) |
| #123 | P178 | The next version is the store | is the store epic (retitled, stays open) |
| #9 | P38 | The capacitors P6 promised | Later: checks for bigger projects |
| #41 | P107 | check_physics names a null it cannot use | Later: checks for bigger projects |
| #43 | P109 | check_all reports the generator's CONFLICT lines | Later: checks for bigger projects |
| #54 | P120 | The shipped L9110S and power-inlet records state their VCC… | Later: checks for bigger projects |
| #55 | P121 | The XIAO ESP32-C6 builds, or spark says it cannot before it… | Later: checks for bigger projects |
| #56 | P122 | The I²C rise-time check runs on the boards spark generates | Later: checks for bigger projects |
| #60 | P126 | The fabrication gate reads the board being ordered, and lists… | Later: checks for bigger projects |
| #63 | P129 | The motor rail's net is not named for one project's battery | Later: checks for bigger projects |
| #67 | P133 | The checks tell the truth | Later: checks for bigger projects |
| #70 | P136 | Full circuit checks: analogue and board checks in spark (epic) | Later: checks for bigger projects |
| #76 | P142 | Two I2C devices at the same address build and pass | Later: checks for bigger projects |
| #78 | P144 | The trace-current rule ignores a project's copper thickness | Later: checks for bigger projects |
| #79 | P145 | The floating-input rule raises false alarms on I2S lines and… | Later: checks for bigger projects |
| #86 | P152 | The VL6180X record and its Wokwi chip say the interrupt line… | Later: checks for bigger projects |
| #87 | P153 | Three printed limits fail the rule that printed them (6 V,… | Later: checks for bigger projects |
| #89 | P154 | A council proposes one easy way to choose and switch engines,… | v2 candidate: one core |
| #94 | P158 | The council's refactoring and architecture epic (was in Build) | v2 candidate: one core |
| #136 | P187 | A board whose Wokwi stand-in is another chip validates ok | v2 candidate: one core |
| #138 | P189 | An interpreter built for another chip is packed for a board… | v2 candidate: one core |
| #27 | P102b | Maps and journeys as text, drawn in Miro and Canva | Later: team and QA tooling |
| #28 | P102d | Proofs run as commands; the map says proven or not | Later: team and QA tooling |
| #30 | P102f | The demo projects get a home: spark-demos | Later: team and QA tooling |
| #39 | P106 | The push gate measures the commits being pushed, in a clean… | Later: team and QA tooling |
| #97 | P161 | Measure test coverage and QA quality | Later: team and QA tooling |
| #103 | P166 | QA we can trust — how far what is said to work is tested and… | Later: team and QA tooling |
| #108 | P170 | Time an issue spends in each state, and its waiting times, as… | Later: team and QA tooling |
| #111 | P171 | Clean after ourselves automatically | Later: team and QA tooling |
| #113 | P173 | The suite takes ~32 s and five modules take 26 of it;… | Later: team and QA tooling |
| #121 | P177 | A draft issue in a working stage is counted by the gate as… | Later: team and QA tooling |
| #135 | P186 | mutate.py scores a mutant that no longer imports as caught | Later: team and QA tooling |
| #137 | P188 | Whether a spark change breaks the bin is pinned for one of… | Later: team and QA tooling |
| #46 | P112 | spark's MCP servers are pinned, and /spark:setup says they… | Later: a stranger's first install |
| #48 | P114 | init --force lists only what is still unanswered, and says… | Later: a stranger's first install |
| #53 | P119 | check_vendor_pins says it could not look when the GitHub CLI… | Later: a stranger's first install |
| #57 | P123 | tools.py --on honours --dry-run and says it installs | Later: a stranger's first install |
| #61 | P127 | boards/README.md gives spark's steps for adding a board | Later: a stranger's first install |
| #62 | P128 | A stranger can report a problem with a form that asks for… | Later: a stranger's first install |
| #66 | P132 | A stranger's first board | Later: a stranger's first install |
| #5 | P76 | From a vague idea to a block-level schematic, by conversation | no epic fits (pending the PO) |

Placement is Claude's reading, the PO's to change: #136 and #138 follow #94 (the replan: "goes with it"); #89 (engines and tools through a CLI or MCP) is the core's; #67 (the checks tell the truth) is in the checks epic.

### C4. Comments that say more than the template

- **#94 (P158; leaves Build):** `Closed into the v2 core epic. Nothing is lost: the design, the plan and the short version are on main (docs/archive/2026-10-11-p158-short.md and the two files it links), part 1's 72 changes are in docs/archive/discovery/2026-10-10-p158-gaps-and-refactoring/proposal.md. The first slice stays as filed: P184 and P124 Done; P185 (#134) and #65 wait in Idea; #135, #136, #138 close into their epics; #137 into team and QA. The I0 baseline is not built; P195 is its small replacement. Leaves Build, so a Build slot is free.`
- **#135 (P186):** `Closed into team and QA tooling; leaves Ready. State: branch p186-mutants is pushed (ac5e968), the gate is green, the six-lens council ran on the first commit and its fixes are not applied, the refuter has not run, there is no pull request. The branch keeps it; one finding of its own is in it (the P13 row that only ever crashed is repaired).`
- **#136 (P187):** `Closed into the v2 core epic (P158's C4); leaves Ready. Reproduced 2026-10-10 on a scratch store: a record with chip esp32c6 and the S3's stand-in answers ok, exit 0. v1 has one S3 board, so the walk cannot trip it. Comes back with a second board.`
- **#138 (P189):** `Closed into the v2 core epic; leaves Ready. It hung on P187's chip-name table. The walk flashes the image that passed the simulation (P192 b), so nothing packs an interpreter for another chip. Comes back with #136.`
- **#6, rounds B and C (comment on #6):** `Rounds B (a project needing parts the store lacks: the research route) and C (irrigation improved by one feature) are not part of this card after the replan of 2026-10-11. They come back after round A's diary says what tripped, as their own cards then; none is filed now. The PO's D6 words of 2026-10-09 stay here as the record.` Where they wait is pending the PO: this comment, or a line in an epic (none of the five fits).

---

## D. The bin (repo xmejkal/sisuo-brain-transplant, board Projects #1)

One comment each; the board move is in the first line.
- **bin #5 (P58) - Ready to Idea:** `Back to Idea (spark replan of 2026-10-11). The first slice walks spark's button-and-LED on a breadboard, not the bin; the bin's bench is the second proof, after that walk has been on the bench. Nothing in this card is dropped.`
- **bin #2 (P73) - Ready to Idea:** `Back to Idea (spark replan of 2026-10-11), same reason as P58. Spark's walk logs its own bench verdict; whether this card's design serves both is for when it returns.`
- **bin #3 (B8) - Ready to Idea:** `Back to Idea (spark replan of 2026-10-11). The flaky test is unproven (1 failure in 36 runs); it matters to the bin's gate, not to the walk.`
- **bin #15 (B21), stays Idea:** `Feeds spark P192 (c) (spark #144): the board's SKU and revision decide whether the flash image that passed the simulation suits the PO's board, and the replan's Q5 asks N16R8 or N4. Suggested: read the chip in the same sitting as the walk's wiring. Waiting on: hardware.`
- **bin #26 (B31) - no Status to Idea, closes with P32b (bin #6):** `Idea (it had no Status). Same cause as spark P190 (#142, Done): spark's generated diagrams now wire the serial monitor. This card closes with P32b (#6), when the bin builds its diagram with spark's converter and make simulate-all passes; not before, because the bin's simulation is the second proof. If the PO wants it sooner, this card's own two diagram.json connections are the fix.`

---

## E. Where the cards contradict the replan

| # | card | contradiction | fix |
| --- | --- | --- | --- |
| 1 | #7 P59 | Needed by is irrigation's unimportable `main()`; a stand-in does not fix it. The value line's second clause (undriven pins) is P74's. No button-and-LED firmware file exists in the repo (`tests/data/breadboard/button-light` holds requirements and `dist/` only). | A3: the clause moves to #8, irrigation's case is out of v1, item 3 commits the walk's firmware |
| 2 | #64 P130 | Needed by and value are the motor example, not button-and-LED. `build.md:201` has `ready` as a comment in an example, not a contract. | A5 |
| 3 | #64 P130 | VISION.md: the hobbyist "maybe no Wokwi licence", quits "when a paid simulator blocks them"; the harness run needs `WOKWI_CLI_TOKEN`. | pending Q5. The harness test needs neither, so only the dated run waits |
| 4 | #144 P192, #145 P193 | No slice, and Ready needs one. | the PO sets it, pending Q2 |
| 5 | #144 P192 | "A board-specific MicroPython build" implies the chip table the replan drops. | A6: struck, pending Q5 |
| 6 | #144 P192 | Part (c) is a bench step with a dependency on the other board (bin #15): it would hold a Build slot while it waits. | A6: (c) is the closing proof, the story waits on hardware |
| 7 | #6 P100 | Value is "to be set in refinement" (Ready needs one); label `epic`; Stage Discovery; "council waits until P104" (P104 is Done). | A7 |
| 8 | #6 P100 | "Scored by someone who did not write them": nobody is named. | pending the PO |
| 9 | #94 decision D-DP3 | "Round A runs on today's spark before any output-changing card merges"; items 2 and 4 change output first. | A7 line; pending the PO |
| 10 | #134 P185 | Needed by points at "D-PQ1 on #94" and the plan's C2; #94 is closed. The plan is still on main. | add `(#94 is closed into the v2 core epic; the plan stays at docs/archive/2026-10-10-p158-plan.md)`; it runs before item 7 only if the PO says so (Q4) |
| 11 | #42, #45, #52 (item 4's routes) | They are children of #67 (P133), closing into the checks epic. | P197 cites the rule itself (A4); the children stay open |
| 12 | #81 P147 | Title says the version never changes; it reads 0.8.1 and the decision is in the comment of 2026-10-06. | suggested title: `P147 — An install from GitHub is shown to receive an update`. Pending the PO |
| 13 | #123 P178 | Title: "The next version is the store". The PO's words of 2026-10-11 name the core. | C2: retitle `Later: the store, shared`. The memory entry "Next version: the store" is stale after his yes |
| 14 | replan, `after-v1.md` | They say "stays open in Idea" and a new "After v1" slice option. | follow the PO's yes (Q2); then `STORY_MAP.md`, whose slices 4 and 10 name closed cards (P38, P87, P89, P90, P91, P92, P94 ...), takes a "closed into" line |
| 15 | bin #26 B31 | No Status on the bin's board. | D |
