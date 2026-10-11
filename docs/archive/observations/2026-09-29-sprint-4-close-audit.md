# Sprint 4 close audit — 2026-09-29, night

An outside read of the second half of Sprint 4 and its close: P20–P25, the closing review, retro
R4 and the Sprint 5 proposal. Five questions, in the order they were asked: do the DONEs re-run
cold, did R4's actions hold when checked now, what did the second half break or leave, is the
Sprint 5 proposal aimed at what misleads today, and where should the third cold test point.
Every claim below was run or read; the command or the line number is beside it, and every line
number is pinned to the revision named next.

**Revision.** `git rev-parse --short HEAD` → **`0678501`**, `git status --short` empty in the
spark checkout before and after every run. Suite and mutation runs were made on `git archive`
copies in the scratchpad (one archive per commit for the test counts; a separate arena for the
mutation chain, so a mutation in flight could not colour a read of anything else); the probes,
the stranger run, the two-device build and the reference spine ran against the working tree's
scripts, read-only, in temp directories. The suite on the HEAD archive: **`Ran 608 tests … OK
(skipped=2)`**, 5.9 s — the two skips read files beside `../smartbin-local`, which an archive has
no sibling for. Nothing here contacted wokwi.com; the simulation stage is the bin's offline
converter under `bun`.

**Mutation runs, R4.5's rule.** All sixteen tables were run in ONE background process, strictly
one after another, on the arena copy; the per-table logs carry start and end times and each
table's end is the next one's start (p21 15:13:01–15:13:55, p22 15:13:55–15:14:40, …). No other
`mutate.py` run was started until the chain wrote its `ALL-DONE`. **74 mutations in 16 tables:
74 caught, 0 escaped, 0 refused, exit 0 for every table, no `.mutate.lock` left behind, and the
arena `diff -rq` clean against a fresh archive** (only `__pycache__` differs).

---

## 1. Do the DONEs of the second half hold when re-run cold?

| item | `Value proven by:` / claim | ran | holds? |
| --- | --- | --- | --- |
| suite | 608 (`0678501`) | `python3 -m unittest discover -s tests` on the archive → `Ran 608 tests … OK (skipped=2)` | **yes** |
| P20 `c3e2e28` | `assign_pins.py` on `/spark:build`'s example and on the car prints a pin per signal, exit 0 (car: `MOTOR_IA` on A5); both RC boards byte-identical; a malformed part is could-not-run through both mains | the example, from a directory holding only the document's JSON: 4 signals, `MOTOR_IA D3`, exit 0. `car.requirements.json` inside rc-car: `MOTOR_IA A5 GPIO11`, exit 0; from `/private/tmp` by absolute path: the same. `emit_board.py` on both RC files → `diff -q` identical to the committed `car.tsx` and `remote.tsx`. `parts/broken.json` holding `{"schema": 1, "id": "broken", ` → `assign_pins` exit 2 `could not load the design: the record for 'broken' is not JSON`, `emit_board` exit 2, `check_spine` `[????] schematic`, exit 2. Table `sprint-4-p20.json`: 4 of 4 caught | **yes** |
| P21 `7381fed` | a named VL6180X on `.Mcu > .SDA/.SCL`; two named VL6180X built with tsci, 12 traces, 0 errors, both on the MCU's pads; CLK/DIN/DOUT on SCK/MOSI/MISO; XYZ on bus spi refused naming the lines | named: `RANGEFINDER_SDA SDA GPIO1 … dedicated hardware`, `RANGEFINDER_SCL SCL GPIO2`, exit 0. Two named (`RangeFront`, `RangeBack`): `assign_pins` places both pairs on SDA/SCL (the second "shared with everything else on the I2C bus"); `emit_board --assume-missing-sizes` + `emit_footprint` + `npx tsci build` → **12 `pcb_trace`, 0 errors**, source traces `Mcu.pin9 → RangeFront.SDA`, `pin10 → .SCL`, `pin9 → RangeBack.SDA`, `pin10 → .SCL`. `{CLK, DIN, DOUT, CS}` on `bus: spi` → SCK, MOSI, MISO, SS. `XYZ` → `XYZ is on the SPI bus but 'XYZ' is not one of its lines: SCK (SCK/CLK/SCLK), MOSI (…), MISO (…), SS (SS/CS/NSS)`, exit 1. Two chip selects: `EPD_CS SS`, `SD_CS D3 … a chip select — every SPI device has its own, and the board's SS pin is taken`. Table: 5 of 5 caught | **yes** — and it refuses a shipped part (C6, §3) |
| P22 `c565778` | the stranger test, and the run by hand from a directory holding only the requirements: every documented step exit 0, `tsci build` 11 traces 0 errors, the one command end to end | §1a below | **yes** — with a fixture caveat (C10, §2) |
| P23 `5605065` | a probe regulator on `logic` → `net.V33 IS DRIVEN BY MORE THAN ONE SUPPLY: …VOUT, the microcontroller module's own V33` in the file and on stderr; two on `servo` named; one on its own rail not | four probe regulators in a temp project (`parts.py --validate --project .` → four `ok`): on `logic` → the line at `board.tsx:36` and the stderr note, exit 0; two on `servo` → `net.SERVO IS DRIVEN BY MORE THAN ONE SUPPLY: Buck A.VOUT, Buck B.VOUT`; on `sensor5` → 0 such lines. `check_spine` on the first → `[!!  ] schematic-notes` carrying the note, "the chain is broken" (a design defect, rightly). Table: 4 of 4 caught | **yes** |
| P24 `fd25f15` | `check_design.py --help` → usage, exit 0; a missing design → could-not-run, exit 2, in text and JSON | at HEAD: `usage: check_design.py [-h] [--json] design`, exit 0; `check_design.py: no design at does-not-exist.json`, exit 2; `{"check": "design", "status": "could-not-run", …}`, exit 2. Table: 2 of 2 caught | **yes at HEAD; not at the commit** — `fd25f15` as committed does not run (§2, C3) |
| P25 `ebb8339` + `7361679` | one definition each, every script importing it, four designs byte-identical; every function the audit listed named by a test | `outcomes.py` exists; 16 scripts import it (`grep -l`), the five that do not are `bench_sim`, `copper`, `design`, `findings`, `outcomes` itself. Two RC boards byte-identical today (above); the reference on both boards has no committed baseline to compare against. Named by a test: 13 of the 16 functions B16 listed — `init_project.nets_in`, `rules_for`, `has_answers` have 0 mentions in `tests/` (C9) | **mostly** |
| the close `0678501` | 603 OK on `77af415`; 608 after the tool changes; `--anchors` 74 in 16, every anchor once; intake 83 acted, 11 closed, 1 rejected, 0 raised; R9 refused at `77af415` (anchor moved under P20) and two P11 anchors moved by P22; reference spine 12 traces, 10 wires, tsci 0.0.2600; r9 and p11 caught alone | 603 and 608 at their archives; `mutate.py --anchors tests/mutations/*.json` → `74 mutation(s) in 16 table(s): every anchor present, once`, exit 0; `awk` by status cell → `**acted** 83, **closed** 11, **rejected** 1`, and by row id 95 rows, `raised` 0, `verified` 0. HEAD's tool with `--root` on the `77af415` archive and its own tables: `sprint-4-r9.json` → `1 would be refused` (`the rails override is never applied`, `scripts/design.py`), `sprint-3-p11.json` → `2 would be refused`, all tables → `3 would be refused`; on `476f680`: `1 would be refused` (B8's). `python3 scripts/check_spine.py` with nvm's tsci first on PATH → `build 12 trace(s), 0 errors, tsci 0.0.2600`, `simulation 10 wire(s)`, exit 0. r9 and p11 in the chain: 4 of 4 and 8 of 8 caught | **yes** |

### 1a. The stranger run, `commands/build.md` as written

A fresh directory holding `requirements.json` — the `json` block of `commands/build.md:14-23`,
extracted by the same regex the test uses — and a `node_modules` symlink to
`smartbin-local`'s so `tsci` can build (the document says the build needs tscircuit). Then the
document's commands, in its order, with `${CLAUDE_PLUGIN_ROOT}` = the spark checkout. Log:
`stranger.log` in the scratchpad.

| # | command, as `build.md` writes it | line | what happened |
| --- | --- | --- | --- |
| 1 | `${CLAUDE_PLUGIN_ROOT}/scripts/check_spine.py requirements.json` — the one command | :49 | `[ok] board … — from the plugin's library; no project up from the requirements file, so no rules` · schematic 14 traces written · footprint · `build 11 trace(s), 0 errors, tsci 0.0.2621` · `simulation 9 wire(s)` · **`the chain runs end to end`**, exit 0 |
| 2 | `scripts/parts.py --list` | :74 | six records, exit 0 |
| 3 | `scripts/parts.py --show l9110s-module` | :75 | exit 0 |
| 4 | `scripts/assign_pins.py requirements.json` | :76 | the library note, then 4 signals placed (`MOTOR_IA D3`, `MOTOR_IB A5`, `BTNOPEN_BUTTON D12`, `BTNMODE_BUTTON D11`), exit 0 |
| 5 | `scripts/emit_board.py requirements.json > board.tsx` | :77 | exit 0, 7557 bytes, line 1 `import { FireBeetle2Esp32S3 } from "./FireBeetle2Esp32S3"`, the note on stderr |
| 6 | `scripts/emit_footprint.py --board firebeetle2-esp32s3 -o FireBeetle2Esp32S3.tsx` | :78 | `wrote FireBeetle2Esp32S3.tsx (32 pads, 1.00 mm holes)`, exit 0 |
| 7 | `npx tsci build board.tsx` | :79 | `1 passed`, exit 0; `dist/board/circuit.json`: **11 `pcb_trace`, 0 error elements** |

Every number `c565778` states — every step exit 0, `MOTOR_IA` on D3, build 11 traces 0 errors,
the one command 11 traces and 9 wires — reproduces. The four things the previous audit found
missing (a project, the crash, the footprint step, `--unverified`'s argument) are gone from the
path: the directory needed nothing but the file.

### 1b. Test counts at every sprint-4 commit that states one

Suite run on a `git archive` of each: `73ca286` **550** · `c3e2e28` **559** · `7381fed` **569** ·
`c565778` **574** · `5605065` **579** · **`fd25f15` 562, FAILED (failures=4, errors=1)** ·
`ebb8339` **589** · `7361679` **603** · `77af415` **603** · `0678501` **608**. Nine of ten
reproduce; the tenth is §2's first row.

---

## 2. R4's actions, checked now

### R4.1 / W13 — every number in the commit messages `476f680..HEAD`

| commit | number as written | what the run it cites prints | matches? |
| --- | --- | --- | --- |
| `73ca286` | `Ran 550 tests, OK` | 550 OK at its archive | **yes** |
| `73ca286` | `mutate.py sprint-2.json: 2 of 2 caught (both "escaped once" entries)` | the table holds **10** entries — at `476f680` and at HEAD (`len(json.load(…))`) — and a run of it reports 10; today 10 caught | **no** — not the output of the command as named (C16) |
| `73ca286` | `sprint-4-b11.json: 1 of 1 caught`; eleven rows to `closed` | 1 of 1 today; `closed` 11 | **yes** |
| `c3e2e28` | `Ran 559 tests, OK`; `4 of 4 caught`; `MOTOR_IA on A5` | 559; 4 of 4; A5 | **yes** |
| `7381fed` | `Ran 569 tests, OK`; `5 of 5 caught`; `12 traces, 0 errors` | 569; 5 of 5; 12 / 0 | **yes** |
| `c565778` | `Ran 574 tests, OK`; `4 of 4`; every step exit 0, `MOTOR_IA on D3`, `11 traces, 0 errors`, `11 traces, 9 wires` | 574; 4 of 4; §1a | **yes** |
| `5605065` | `Ran 579 tests, OK`; `4 of 4`; the three probe outcomes | 579; 4 of 4; §1 | **yes** |
| **`fd25f15`** | `Ran 589 tests, OK`; `sprint-4-p24.json: 2 of 2 caught`; `check_design.py --help → usage, exit 0` | the archive of the commit: **`Ran 562 tests … FAILED (failures=4, errors=1)`** — `test_check_design` cannot import (`ModuleNotFoundError: No module named 'outcomes'`), and three `check_all` seam tests plus `test_every_chain_script_has_a_command_line` fail behind it; `python3 scripts/check_design.py --help` at that archive → the same `ModuleNotFoundError`. `git show fd25f15:scripts/check_design.py` line 31 imports `outcomes`; `git ls-tree fd25f15 scripts/outcomes.py` is empty — the module arrives in `ebb8339`, the next commit, whose count is 589. `mutate.py:216-219` refuses to mutate a red suite, so `2 of 2` cannot have been run on this tree either | **no** — every number in the message was read from a tree that is not the one committed (C3) |
| `ebb8339` | `Ran 589 tests, OK`; `fourteen scripts import them`; four designs byte-identical | 589; **16** scripts import `outcomes` at `ebb8339` (`git grep -l "from outcomes import" ebb8339 -- scripts/`) — 14 is B17's count of files that held the literal; two of the four designs checkable today (the RC boards, identical) | count yes; **14 is 16**; designs 2 of 4 checkable |
| `7361679` | `Ran 603 tests, OK`; `4 of 4`; GPIO 38 carries `not_wake_capable` | 603; 4 of 4; board file `not_wake_capable: [38, 43, 44, 47]`, `wake_capable_gpio` 0–21 | **yes** |
| `0678501` | 603 on `77af415`; `r9 … 1 REFUSED`; two more in P11; 608 after; `74 mutation(s) in 16 table(s)`; `83 acted, 11 closed, 1 rejected, 0 raised`; 12 traces, 10 wires, tsci 0.0.2600 | all as §1's last row | **yes** |

W13 says a number enters a message only in a later call than the run that produced it. `fd25f15`
shows the rule's gap: the run happened, the number was read from its output, and the tree it ran
on held `outcomes.py` uncommitted (P25 in flight under P24 — W6's "one item at a time" in the
same breath). The commit as landed does not import, does not answer `--help`, and cannot have been
mutation-tested. Nothing in W13 as written asks *which tree* the output came from.

### R4.2 — a "user can" value line proven by a test that follows the document

One value line of that kind exists: R7's, `PRODUCT_BACKLOG.md:272` ("a user following the
documented flow reaching a built board …"). P22's (`:432-433`) names the test and the run by hand.
The test, `AStrangerCanBuildTest` (`tests/test_routes.py:149-193`), takes the requirements from
the document (`:162`, the same regex as §1a) and runs from a temp directory — but the step
commands are typed in the test (`:181`, `:184`, `:189-190`), not read from `build.md:74-79`. So it
follows the document's data and not its commands. Probe on a copy of HEAD: `build.md:76` changed
to `assign_pins.py --verbose requirements.json` — a flag the script does not have — makes the
documented step exit 2 (`assign_pins.py: error: unrecognized arguments: --verbose`), and the suite
runs **608, OK**. `test_the_command_shows_each_link_being_typed` (`:56-68`) reads the code blocks
but matches script names only. The pattern R4.2 names cannot see a wrong documented step — W12's
shape, in the test written for R4.2 (C10). (A first probe of mine, `-o` → `--out`, was invalid:
`emit_footprint.py:180` defines `-o, --out`, so the mutated document still worked.)

### R4.5 — refused tables, overlapping runs

| check | evidence | result |
| --- | --- | --- |
| any table refused at HEAD | 16 tables, 74 mutations, one process, one after another: 74 caught, 0 escaped, 0 refused; `--anchors` over all → every anchor once | **none** |
| the three refusals the close reports | reproduced at `77af415` with HEAD's tool and `--root` (r9 1, p11 2; 3 in all); B8's at `476f680` (sprint-2 1) | **as stated** |
| overlapping runs | none started here; the lock was present at every poll during a table's mutation phase and absent after every table (`lock-after:` in each log) | **none** |
| **not asked, found:** the lock and the pre-check | `mutate.py:212` looks for the lock, `:216` runs the whole suite (6–7 s here), and the lock is written at `:128`, inside `run()` called at `:222`. Observed on the chain, no second run launched: `sprint-3-p12` started at 15:21:09 (its log written) and `.mutate.lock` was **absent until 15:21:16**. Two runs started inside that window both pass `:212`, both pre-check, and both take the lock. `test_mutate.py:195-211` tests a lock already held, not the window | **the refusal exists, with a seven-second hole** (C8) |
| the DoD clause "at every commit" | `hooks/hooks.json` runs `make check` on edits to `.tsx`/`config.py`/`.kicad_sch`/`mapping.ts`; `.git/hooks/` holds samples only | **held by memory**, as W3 was before P4 (C14) |

### R4.4 — the PO question asked so one letter answers it

`SPRINT.md:27`, the Sprint 5 table: **`PO: one letter, (a), (b) or (c)`** in bold, the three
domains described at `:115-123`, "parked with the date if unanswered at the sprint's start". No
file in the tree holds a "checkpoint summary" (`grep -rn -i checkpoint --include='*.md'` → only
`RETROSPECTIVES.md:225`, the action's own text). Asked concretely, as an instruction in a table
cell; whether it was put to the PO in a summary is not checkable from the repository — recorded
as could-not-look, not as done (C13). Not yet due: Sprint 5 is proposed, not started.

### R4.3 — the closing audit before the retro

R4 is in `0678501`; this audit was spawned on that HEAD after it, and R4's header reads "a
closing audit reads the whole" — future tense, no report cited. The action was written in the
retro it should have preceded; its check is at R5 (C18).

---

## 3. What the second half may have broken or left

Read: `design.py`, `assign_pins.py` (the bus path and `BUS_LINES`), `emit_board.py`
(`outputs_in_contention`, `GROUND_NETS`), `check_spine.py`, `boards.py` (`project_or_library`,
`walk_up`), `outcomes.py`, `mutate.py` (anchors, the lock), `check_design.py`,
`compare_design.py`; then each suspicion run.

### Failure modes that read as something they are not

| where | input | what it says | what it is |
| --- | --- | --- | --- |
| `assign_pins.py:233-262` | a signal naming its own `pin` and a `needs` the pin lacks — `{"name": "OPEN_BTN", "pin": "D14", "needs": ["wake"]}` | `OPEN_BTN D14 GPIO47 asked for by name — dedicated hardware, not a choice [not_wake_capable, onboard_button]`, exit 0; `{"pin": "D3", "needs": ["adc"]}` → GPIO38 (no ADC), exit 0; `{"pin": "D9"}` → the BOOT strap `candidates()` (`:154`) excludes, exit 0 | the `needs` is dropped without a word — the loop checks only that the label exists (`:235`). `:28-32` ("does not silently drop a requirement it cannot meet") is false again, the way B3 made it false. `check_design.py:193-201` refuses the same three (`A needs a wake pin, but D14 (GPIO47) cannot do that`): the two tools disagree today, in the direction opposite to P7. Without `pin`, the same signals land on A5 and A0 with the reason. Eighth instance of "less than asked, exit 0" (C4) |
| `design.py:81-82` + `emit_board.py:680` | `--project` naming a directory that does not exist, on a design whose parts are all library parts | in a project whose `.spark/rules.json` states 2 A on `MOTOR6V`, `GND`, `V33`: no flag → 11 `thickness=`; `--project ./typo` → exit 0, **1 `thickness=`, the UNJUSTIFIED block, stderr empty**; `assign_pins.py … --project ./typo` → exit 0, stderr empty | `project_for` returns `Path(project).resolve()` unchecked; the library note prints only without `--project`, and `is_library` is False for the typo'd path anyway, so nothing says anything. A2/P11's defect — widths called unjustified while the file states them — reborn by one character. With project parts in the design it refuses (`no part called 'sg90-servo'`), so it bites exactly the designs the documents show. `build.md:42-43` "every command says so" does not reach it; no test names a nonexistent `--project` (C5) |
| `design.py:228` → `assign_pins.py:243` / `check_spine.py:278-283` | a malformed `signals` entry: `[{"needs": []}]` | `assign_pins` → `KeyError: 'name'` traceback, exit 1; `emit_board` → the same, exit 1; `check_spine` → `[!!  ] schematic  Traceback …`, **"the chain is broken"**, exit 1. `["LED"]` → `AttributeError`; `"needs": "adc"` → `X asks for a, c, d, which is not something a pin can be asked for` | the loader validates every `parts` entry (`requested_parts`, `:97-116`) and appends `wanted["signals"]` as is. A8/B10's class one list over: an input fault reported as a design defect (C7) |
| `assign_pins.py:184-187` | the shipped `max98357a-dfr0954`, whose three I2S needs say `bus: "i2s"` | `parts.py --validate` → `max98357a-dfr0954 ok`; `assign_pins.py` → `I2S_BCLK is on bus 'i2s', which is not a bus this knows: i2c, spi`, exit 1; `emit_board` exit 2 | the contract accepts a bus the assigner refuses: `BUS_LINES` (`:164-168`) is checked nowhere a record is written (`parts.py:363-368` passes `bus` through), and `boards.PIN_ROLES` (`boards.py:99-100`) names the same two buses again. G12's shape — `needs` got the fix, `bus` did not. Before P21 the three lines were placed on any pin in silence (B3); the refusal is closer to true for a bus the board does not label, but an ESP32 routes I2S through its matrix and the honest answer is "any pin, kept together, said so" (C6). The record also has no `footprint` (S3), so `emit_board` refused it before P21 as well — one step later |
| `mutate.py:82` | a table naming a file that is not there | `--anchors` → `[refused] … find occurs 0 time(s) in scripts/nope.py`, exit 1; run mode → after the pre-check, `FileNotFoundError` traceback, exit 1 (the code this tool uses for "escaped"), lock released | `anchors()` (`:104`) asks whether the file exists; `apply()` does not. The same question answered at one of two sites, inside the tool that enforces W3 (C8) |

### A fallback that hides a failure — the library, three ways

- **From nowhere, no flag:** every reading script falls back and says so (`LIBRARY_NOTE`,
  `design.py:92-94`); the spine's board stage says so; the stranger run shows it on every step.
  **Holds.**
- **From a project, `--project` typo'd:** falls to whatever the typo resolves to, which has no
  parts, no boards and no rules, and the library fills the first two silently (`boards.search_path`,
  `parts.search_path`) while `rules_in` returns `{}` ("absent is not an error", `design.py:233`).
  Says nothing (C5, above).
- **A typo in the requirements path:** `check_spine.py … car.requirement.json` →
  `[????] requirements  no requirements at …`, exit 2. **Holds.**

### Rules still at two sites, one commit after "defined once"

1. The status words: `outcomes.py:21` and **`compare_design.py:41`** (`OK, PROBLEMS,
   COULD_NOT_RUN = "ok", "problems", "could-not-run"`, one line after importing the exit codes
   from `outcomes`); spelled again at `check_footprints.py:525` and `emit_footprint.py:216` (C12).
2. The upward walk: `boards.py:126` and `findings.py:134` — the commit says `findings.py` was
   left alone for P19's sake; recorded, not disputed.
3. The bus vocabulary: `assign_pins.BUS_LINES` and `boards.PIN_ROLES`, with `parts.validate`
   reading neither (C6).
4. "Does the file exist": `mutate.anchors` yes, `mutate.apply` no (C8).

### Docstrings describing behaviour the code does not have

- `assign_pins.py:28-32` — "It does not silently drop a requirement it cannot meet." True since
  `7381fed` for a bus line; false for a `needs` beside a named `pin` (C4).
- `commands/build.md:41-43` — "from nowhere … every command says so." True from nowhere; with a
  `--project` that is nowhere, no command says anything (C5).
- `mutate.py:110-113` — "the tool refusing to produce a verdict it cannot trust." It refuses once
  the lock is written, which is after the pre-check (C8).
- `boards.py:150-156` (`project_or_library`) — "Callers say so when they land on the library."
  A typo'd `--project` lands on neither the project nor the library (C5).
- `design.py:76-77` — "`--project` wins." True as written; the defect is that it wins without
  being checked.
- `commands/build.md:52-62` — the example output block (`14 trace(s) written`, `12 trace(s), 0
  errors, tsci 0.0.2621`, `12 wire(s)`) is produced by neither the reference design today
  (15 / 12 / 10) nor the document's own example above it (14 / 11 / 9) (C11).

### A test whose fixture cannot see the defect it names (W12)

`AStrangerCanBuildTest.test_the_documented_steps_produce_a_board_file_and_its_footprint` — the
name says the documented steps; the body types its own (§2, C10). The P22 table's fourth
mutation ("the footprint step vanishes from the command") is caught by the name test
(`:56-68`), not by this one.

### Input read outside a `try`

By reading: `mutate.py:82` (`apply`, above) and `:104` (`anchors`, guarded by `is_file`).
`check_spine.main` reads through `design.read` inside its `try` (`:431-434`); `emit_board.main`
and `assign_pins.main` load inside theirs; the leak is the unvalidated `signals` list, which
reaches `assign` and raises there (C7) — a `KeyError`, not an `OSError`, so it is a validation
gap rather than an unguarded read.

### A `could-not-run` that reads as a pass, or a pass that should be `could-not-run`

- C5: a project that does not exist is asked for and a board comes out, exit 0 — should be
  could-not-run naming the path.
- C7: a traceback through the spine is PROBLEMS ("the chain is broken") — should be could-not-run,
  or better, a `DesignError` in the loader.
- C17 (§5): a named instance of a mapped part makes the simulation stage could-not-run (`no
  Wokwi part is mapped … (component RangeFront)`) — honest, and the documented remedy for two of a
  kind costs the last stage of the product goal.
- Also honest, and worth writing down: the spine on the two-device design is `????`, exit 2, not
  `ok`; the P23 note makes the spine `!!` on a design with two supplies on one rail, which is a
  design defect and rightly so.

---

## 4. Is the Sprint 5 proposal aimed right?

**P8, reproduced on spark's own output today.** The stranger run's built board
(`dist/board/circuit.json`, 11 traces) copied into a project, `.spark/rules.json` given
`"must_not_float": [["L9110sModule", "AIA"], ["L9110sModule", "AIB"]]` — the two inputs the same
file traces from `.Mcu > .D3` and `.Mcu > .A5` (`board.tsx:39-40`). `compare_design.py
dist/board/circuit.json` →

```
  [floating-input] L9110sModule.AIA: connects to nothing
  [floating-input] L9110sModule.AIB: connects to nothing
```

exit 1, and `check_all.py --project .` → `[FAIL] rules-vs-netlist`, exit 1. The traces exist in
the netlist — `[('Mcu', 'pin4'), ('L9110sModule', 'AIA')]` — with `connected_source_net_ids: []`,
and `compare_design.Netlist` (`:112-124`) builds membership from net ids alone, so a pin-to-pin
trace is invisible to it. R10's claim of 09-25 is today's behaviour.

**P7, reproduced.** A design.json with a wake button on D14 and an ADC sense on D3:
`check_design.py` → `pins that can: A0, A1, A2, A3, A4, A5, D10, D11, D12, D13, D2, D5, D6, D7,
D9, …` for wake and `… D2 …` for adc (`check_design.py:199-201`). `assign_pins.candidates()` on
the same board excludes **D2 and D9** (`UNAVAILABLE_ROLES = ("strapping",)`, GPIO3 and GPIO0).
The proposal's second item rests on today's code.

**P6, reproduced.** The stranger's `board.tsx:62-68` prints the L9110S's "Pull both inputs down
in HARDWARE …" and the inlet's three requirements under "None of it is done here"; the file holds
0 resistors. The generated motor board leaves the inputs floating under the warning that says
not to, as the item says.

**What misleads today and is not at the top.** Two things say `ok` with exit 0 where the
proposal's own criterion — "a rule that cries wolf", "two tools disagreeing" — would put them
first:

1. **C4** — a `needs` beside a named `pin` is dropped in silence (§3). It is the same family as
   P7 (assign_pins and check_design disagreeing about one board) and worse than P7, because P7
   recommends a pin you could still refuse and C4 places one you asked for wrongly and calls it
   "dedicated hardware". One requirements file reproduces it; a mutation table of two would hold
   it. It is on the path of any design that pins signals for firmware that already exists — the
   bin's `config.py` pins every signal by name.
2. **C5** — a typo'd `--project` emits unsized traces with the UNJUSTIFIED block and exit 0, no
   note, on exactly the designs the documents show (§3). Two lines in `design.project_for` and a
   test. P11's whole point was that the documented invocation sizes traces; this is the same
   output reached by one wrong character, and nothing says so.

Behind those, not misleading but wrong: **C6** (a shipped record the chain refuses while the
contract says `ok` — G12's shape, the item the backlog already fixed once for `needs`) and **C7**
(a malformed `signals` entry reported as a broken design). And on process, **C3**: a commit that
does not pass its own suite, with a message that says it does, is the shape W13 was written
against and does not catch.

The proposal's order otherwise stands as a recommendation: P8 and P7 reproduce, P6 reproduces,
and none of the three says `ok` — P8 says `problems` where it should not, which is the other
half of W1 and the reason the item exists.

---

## 5. The third cold test

The previous audit argued for (a), the battery sensor node, on three code paths that exited 0
with less than asked. All three are closed and, as of tonight, exercised: a named I2C part lands
on SDA/SCL; `CLK`/`DIN`/`DOUT`/`CS` land on SCK/MOSI/MISO/SS; a regulator on `logic` is named in
the file and on stderr (§1). So the question is what is untested *now*, by code path, with (a)
and (c) walked against today's code.

| code path | state today | (a) sensor node | (c) irrigation |
| --- | --- | --- | --- |
| a bus part with an instance name; a vendor-named line (B2, B3) | fixed, tested, mutation-held | walks it (BME280, e-paper) — proven | walks it (RTC) — proven |
| a regulator onto `logic` (B9) | fixed, tested | only if a regulator is added; the LiPo goes into the module's own JST | walks it (12 V → logic) — proven, and reported |
| **the module's power INPUT** | **a gap:** `VCC` is a header pad (`physical.header_order`) and `power_pads` lists `GND1-3` and `3V3` only, all `out` — no generated design can feed the module. The car's plan calls 5 V into VCC "the risk I am taking knowingly" (`PLAN.md:46-47`); the committed `car.tsx` has no trace to `Mcu > .VCC`, and the generator, which sees only consumers, said nothing (C15) | only with a regulator | **walks it** — 12 V → 5 V → VCC is the only way a 12 V system powers this module |
| host requirements printed, not done (P6) | reproduced | I2C pull-ups on a V1.2 board (P5's revision question) — light | **walks it hard:** four MOSFET drivers, each with a flyback diode and a gate pulldown as host requirements, on inductive loads; a rail fuse. The printed-and-not-done hazard is real current into a coil |
| `must_not_float` on pin-to-pin traces (P8) | reproduced | only if the designer writes the rule | **walks it:** "the gates must not float" is the first rule an irrigation designer writes |
| `on_board: false` (P17) | read by nothing (`grep on_board scripts/` → none) | the BME280 on a lead — one part | **eight parts** off the board: four probes, four valves; each valve as an `out` net with one member stops the build until a connector part is invented — the XT30 path again |
| a `needs` beside a named `pin` (C4) | new, misleading | walks it if signals are pinned for existing firmware | less likely; a one-line file reproduces it without a cold test |
| a wake button's polarity (P16) | no check | walks it, if the node has a wake button; a timer-woken node does not | no |
| two buses plus a plain-signal budget (P3) | tested to ten signals | e-paper's DC/RST/BUSY beside CS, INT, LED — the tie-breaker path, already the tested one | no |
| a new part class through the contract | the car's servo, buck and XT30 proved the schema generalises | a display class — new fields (SPI lines) all in `BUS_LINES` now | a MOSFET/relay driver class — `power` `out` to nowhere, `host_requirements` that matter |
| trace sizing at real current (R5) | tested | no rail above 0.5 A | 1–2 A per valve rail, five rails in the rules table |
| the ADC1 budget | 9 candidates on this board | one input | four probes — not stressed |
| simulation of named instances (C17) | could-not-run, honest | the BME280 and e-paper have no converter part either way | the same |

(a) still walks one path nothing else does — P16 — and one new one that needs no cold test to
show (C4). (c) walks P6, P8 and P17, the first three items of the Sprint 5 proposal, at their
worst — a coil with no flyback under a printed requirement, the gate rule crying wolf, eight
off-board parts — and one gap no row had named until tonight, the module's own supply input
(C15). The family the cold tests exist to find, "less than asked, exit 0", now lives in the
generated *design* rather than in the netlist: a board that prints its own hazards and honours
none. That is where (c) walks. Recommendation, with its reasons; the choice is the PO's (W11):
**(c)**.

---

## What I would change first

**A `needs` beside a named `pin` is checked, or refused** (`assign_pins.py:233-262`): the named
loop asks `needs <= pin["can"]` and `roles ∩ UNAVAILABLE_ROLES = ∅` the way the automatic loop
already does, and refuses by name when either fails. Five lines, a table of two mutations, and
`assign_pins.py:28-32` becomes true for the third time. Evidence that this comes before another
document: it is the one path found tonight that says "dedicated hardware, not a choice" about a
pin that cannot do the job, on a file the bin's own firmware pattern would write.

Then, in order: `design.project_for` refuses a `--project` that is not a directory (C5 — two
lines, a test, and A2's defect stops being one character away); the loader validates `signals`
entries the way it validates `parts` (C7); `parts.validate` checks `bus` against the one bus
vocabulary, which then has to have one home (C6); the mutate lock is written before the pre-check
(C8); and — process, not code — W13 gains the clause it lacks: the run whose number goes in a
message runs on the tree being committed (`git stash -u`, or an archive of the staged tree), so
that a commit like `fd25f15` cannot carry a green count from a tree that was never committed (C3).
