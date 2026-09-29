# Sprint 4 audit — 2026-09-29, evening

An outside read of the day that closed Sprint 3 and did most of Sprint 4. Five questions, in
the order they were asked: does every DONE re-run, does R7 survive a stranger, did the R3 actions
stick, is the code sound after the refactors, and where should the third cold test point. Every
claim below was run or read; the command or the line number is beside it.

**Revision.** The tree did not move: `git rev-parse --short HEAD` → **`476f680`**, `git status
--short` empty, before and after every run. Suite and mutation runs were made on a `git archive
HEAD` copy in the scratchpad so a mutation in flight could not colour a read of the working tree;
`check_spine` and the rc-car commands ran against the working tree (read-only, temp workdirs).
The two suite runs agree: **547 tests, OK** in the working tree (`python3 -m unittest discover -s
tests`, 10.9 s) and **547, OK, skipped=2** on the archive — the two skips read files beside
`../smartbin-local` (`tests/test_check_firmware.py:172`, `test_emit_footprint.py:35`,
`test_findings.py:289`) and the archive has no sibling.

---

## 1. Does every DONE hold when re-run cold?

| item | `Value proven by:` / claim | ran | holds? |
| --- | --- | --- | --- |
| suite | 547 tests (`227f5d4`) | `python3 -m unittest discover -s tests` → `Ran 547 tests … OK` | **yes** |
| P3 `831f756` | a design that needs SPI keeps the bus together; one that does not leaves it free | `assign_pins.py` on 6 plain signals (FireBeetle): D3, A5, D12, D11, D10, D6 — no bus pin; on 10: the bus (MOSI, MISO, SCK) is spent after those six and *before* A0 (ADC1); SCK/MOSI/MISO/SDA/SCL as `bus` signals land on their own pins; XIAO with 6 plain: D7 then the four SPI pins then I2C, as the result text says | **yes** |
| P3 | `mutate.py tests/mutations/sprint-3-p3.json` 6 of 6 (the table now holds 7, A3's added) | 7 caught, 0 escaped | **yes** |
| A3 `5689147` | one malformation, one problem | temp project part with `power: [{rail, direction}]`, no pin → `parts.py --validate --project` reports `power[0] has no pin` **once** (the second line is the unrelated `pin_order` rule), exit 1 | **yes** |
| P11 `0c21ef5` | 14 `thickness=` inside rc-car with no flag; spine from elsewhere on the remote; malformed file is could-not-run | `emit_board.py car.requirements.json` inside rc-car → `grep -c thickness=` **14**; from the scratchpad: `check_spine.py …/remote.requirements.json` → build 12 traces, **12 wires**, exit 0; `{"board": …, "parts": [` → `[????] requirements … is not JSON`, exit 2; `sprint-3-p11.json` 8 of 8 caught | **yes** |
| P12 `c4d0582` | the spine passes with either tsci, version named | `which -a tsci` → nvm `0.0.2600` first; `check_spine.py` → `ok build 12 trace(s), 0 errors, tsci 0.0.2600`, 10 wires, exit 0; `PATH=…/smartbin-local/node_modules/.bin:$PATH` → the same, `tsci 0.0.2621`; `sprint-3-p12.json` 4 of 4 | **yes** |
| P13 `55e7bb8` | `check_all.load` gone, one `parts` per process | `grep -n "def load\|spec_from_file_location\|importlib" scripts/check_all.py scripts/check_physics.py` → comments only; `OneModulePerProcessTest` (`tests/test_check_all.py:555-597`) green; `sprint-3-p13.json` 3 of 3 | **yes** |
| P14 `f7674b4` | byte-identical on four designs; each section a function with a test | both RC boards re-emitted from their committed requirements → `diff -q` identical to `car.tsx` and `remote.tsx`; `sprint-3-p14.json` 8 of 8. **But** `power_note_lines` and `module_power_lines` are named by no test (`grep -c` over `tests/test_emit_board.py` → 0 and 0); they are reached only through `power_lines` | **mostly** — the "with a test" clause is false for two of ten sections |
| P15 `f35e7df`+`3c0108d` | `grep -c '\`raised\`' INDEX.md` → 1; `rejected` used once | the command prints **3** (`INDEX.md:28` legend, `:88` S5's text, `:117` A12's text) — and printed 3 at `3c0108d` too, so the 1 was never its output; zero rows carry the status (`grep -cE '^\| [A-Z][0-9]+[a-z]? \|.*\| \`raised\` \|'` → 0); `rejected` → R19, once; `sprint-4-p15.json` 2 of 2; `check_spine.py empty.requirements.json` → `[????] parts`, exit 2 | **substance yes, literal no** (§3, R3.5) |
| R7 `1f769f8`/`7ac2ba1` | a user following the documented flow reaches a built board without being told script names | §2. The one command reaches `the chain runs end to end` (11 traces, 9 wires — `25e585d`'s numbers) **only with a `python3` prefix**; the documented steps do not reach a build without four things the documents do not say; `sprint-4-r7.json` 4 of 4 | **no, as stated** |
| R9 `227f5d4` | `{"part": "l9110s-module", "rails": {"VCC": "traction"}}` with no duplicate record | `rc-car/car.requirements.json` carries exactly that; `ls rc-car/parts/` → no `l9110s-module.json`; `git show 9376dcc --stat` → the record deleted, `car.tsx` 1 line changed (a comment); `check_spine.py …/car.requirements.json` → build **13 traces, 0 errors**; `sprint-4-r9.json` 4 of 4 | **yes** |
| sprint-2 table | (not a DONE item; re-run because it holds the two escapes R2 named) | `sprint-2.json` → 9 caught, **1 refused**: `placeholder wiring passes nothing (escaped once)` — "`find` occurs 0 time(s) in scripts/check_all.py", exit 1 | **no** — see §3, R3.1 |

**Test counts at every commit that states one**, suite run on a `git archive` of each: `997b756`
472 · `831f756` 480 · `5689147` 481 · `0c21ef5` 505 · `c4d0582` 511 · `55e7bb8` 515 · `f7674b4`
528 · `8a3c4be` 528 · `f35e7df` **532** (the message said 533, corrected in `2ce43d7`) · `1f769f8`
539 · `7ac2ba1` 541 · `227f5d4` 547 · `476f680` 547. Every stated count reproduces; the one
miscount is the one already admitted.

**Mutations, all nine tables, one pass each:** 50 mutations, 49 caught, 0 escaped, 1 refused.

Also run while there, holding: the car from outside the project builds with 13 traces and then
stops at simulation — `[!!  ] simulation  no diagram was produced … no Wokwi part is mapped to
… Sg90Servo … Mp1584Buck5v … Xt30TractionInlet`, "the chain is broken", exit 1. Nothing today
claims the car simulates, so no record is wrong; the classification is §4's.

---

## 2. The stranger test of R7

A fresh directory holding only `requirements.json` — the JSON block of `commands/build.md`,
extracted by regex so it is the document's, not mine — and a `node_modules` symlink so `tsci` can
build. Then the commands of `commands/build.md` and `skills/spark-design/SKILL.md`, as written,
with `${CLAUDE_PLUGIN_ROOT}` = the spark checkout. Log: every command, its output, its exit code.

| # | command, as the document writes it | document | what happened | needed knowledge not in the documents |
| --- | --- | --- | --- | --- |
| 1 | `scripts/parts.py --list` | SKILL:18, build:68 | six records, exit 0 | — |
| 2 | `scripts/parts.py --show l9110s-module` | SKILL:20, build:69 | exit 0 | — |
| 3 | `scripts/boards.py --list` | SKILL:27 | `no project here: nothing up from … holds boards/active.json or .spark/`, **exit 1** | that a project must exist first — `/spark:init`, which neither document mentions |
| 4 | `scripts/assign_pins.py requirements.json` | build:70, SKILL:52 | `could not load the board: no project here`, **exit 2** | the same |
| 5 | `scripts/emit_board.py requirements.json > board.tsx` | build:71, SKILL:54 | `cannot emit a board: no project here`, **exit 2**, 0 bytes | the same. `build.md:38` says "this works from anywhere"; not from nowhere — `check_spine.main` falls back to the plugin library (`check_spine.py:417-422`), `emit_board.main` does not (`emit_board.py:651` → `design.load` → `project_for` raises) |
| 6 | `scripts/check_spine.py requirements.json` — **the one command** | build:43, SKILL:58 | `permission denied`, **exit 126** | that the file is mode `100644` (`git ls-files -s scripts/check_spine.py`; so since `c1537b2`) and needs `python3` in front — which the command's `allowed-tools` pattern (`build.md:3`) does not pre-approve |
| 7 | `npx tsci build board.tsx` | SKILL:79 | fails on the empty file from #5 | — |
| 8 | `scripts/check_all.py --project .` | SKILL:85 | exit 0: vendor-truth `ok`, six `--` skipped, "nothing found by the 1 check(s) that completed, of 7" | (honest by its own rule; noted) |
| 9 | `scripts/boards.py --validate --for-fab` | SKILL:85 | `no project here`, exit 1 | as #3 |
| 10 | `scripts/parts.py --unverified` | SKILL:86 | `error: argument --unverified: expected at least one argument`, **exit 2** | that it takes part ids (`parts.py:420`, `nargs="+"`); `parts.py:8`'s own usage line shows it bare |
| 11 | `npx tsci export -f schematic-svg board.tsx` | SKILL:89 | fails on the empty file | — |

**Part 2 — pushing past each blocker with what it took** (`stranger2.log`):

| # | command | result |
| --- | --- | --- |
| 12 | `python3 scripts/check_spine.py requirements.json` | `the chain runs end to end` — schematic 14 traces written, build **11 trace(s), 0 errors, tsci 0.0.2621**, simulation **9 wire(s)**, exit 0. This is R7's corrected claim (`25e585d`) and it reproduces |
| 13 | `python3 scripts/init_project.py --board firebeetle2-esp32s3` | writes `.spark/rules.json`, `.spark/project.json`, `boards/active.json` |
| 14 | `scripts/assign_pins.py requirements.json` (now inside a project) | **`TypeError: unsupported operand type(s) for +: 'dict' and 'str'`**, traceback, exit 1 — `assign_pins.py:330` hands the raw `wanted["parts"]` to `parts.signals_for`, which does `part_id + ".json"` (`parts.py:92`); the documented `{"part": "tactile-button", "name": "BtnOpen"}` entry is a dict. The same at `:343` (`unverified`). Reproduced on rc-car's committed `car.requirements.json` (the `rails` form) inside rc-car: the same traceback. No test calls `assign_pins.main` (`grep -n "main(" tests/test_assign_pins.py` → only `unittest.main()`); `test_routes.test_every_chain_script_has_a_command_line` (`:69-76`) runs `--help` and nothing else |
| 15 | `scripts/emit_board.py requirements.json > board.tsx` | exit 0, 7557 bytes; line 1: `import { FireBeetle2Esp32S3 } from "./FireBeetle2Esp32S3"` |
| 16 | `npx tsci build board.tsx` | **`Cannot find module './FireBeetle2Esp32S3'`**, exit 1. The footprint module is written only by `emit_footprint.py`, which `build.md`, `SKILL.md`, `README.md` and `agents/hardware-engineer.md` never name (`grep -c emit_footprint` → 0, 0, 0, 0), and which `tests/test_routes.py:22`'s `CHAIN` omits |
| 17 | `python3 scripts/emit_footprint.py --board firebeetle2-esp32s3 --project . -o FireBeetle2Esp32S3.tsx` | `wrote FireBeetle2Esp32S3.tsx (32 pads, 1.00 mm holes)` |
| 18 | `npx tsci build board.tsx` | `1 passed`; `dist/board/circuit.json`: 11 `pcb_trace`, 0 errors |
| 19 | `scripts/check_all.py --project .` | exit 1: `FAIL buildability — JstPh2PowerInlet: pad 1.20 mm around a 0.75 mm hole leaves 0.225 mm of ring` (the bin's blocker 7, on the shipped inlet record); `???? physics` rails not stated (honest) |

**Verdict.** The chain runs end to end for a stranger only along the one-command path, and only
once the stranger knows to type `python3` in front of a file the document presents as an
executable. The step-by-step path the same two documents lay out — the path a person takes when
the one command stops, which is what "the stage that stopped it" invites — does not reach a
build without four things neither document says: create a project first, do not run
`assign_pins.py` on the documented file (it crashes), run `emit_footprint.py` before `tsci
build`, and give `parts.py --unverified` an argument. R7's value statement — *"a user following
the documented flow reaching a built board without being told the script names by someone who
already knew them"* — is met by `check_spine` and not by the flow. The R7 mutation table cannot
see any of this: it checks that names appear in documents, and every name does.

---

## 3. The R3 actions, checked now rather than at R4

### R3.1 — a weak fixture is the defect; the mutation stays

| check | evidence | result |
| --- | --- | --- |
| any mutation removed from a table since R3 | `git diff 8a3c4be HEAD --stat -- tests/mutations/` → three files added, 66 insertions, 0 deletions | **none removed** |
| escapes since R3, with causes | `227f5d4`'s message: one escape on the first run of `sprint-4-r9.json`, "re-pointing the loaded record in place", cause: the test re-read a file `parts.load` reads fresh — the fixture could not see it; fixed by holding `on_rails` to its copy contract (`tests/test_design.py:177-186`), the mutation kept (table entry 3, caught today). `1f769f8`, `7ac2ba1`, `f35e7df`: no escape recorded | **one escape, W12's shape, handled as W12 says** |
| **not asked, found:** a mutation that is dead rather than removed | `sprint-2.json` → `[refused] placeholder wiring passes nothing (escaped once) — find occurs 0 time(s) in scripts/check_all.py`. The anchor `placeholder_components_in(inputs.get("project")))` on its own line went away when P11 made the call return `(names, notes)` (`check_all.py:219`). This is the escape backlog R6 records and R2.2 was written for, and since P11 nothing has checked it — the DoD re-runs the item's own table, not the older ones | **the mutation stays in the table and checks nothing** |

### R3.2 — drain the 43; `raised` count and honest closures

| check | evidence | result |
| --- | --- | --- |
| `raised` rows in `INDEX.md` | 0 rows carry the status (75 rows: 70 `acted`, 4 `verified`, 1 `rejected`) | **drained** |
| `rejected` > 0 | R19, with a reproduction (the L9110S's motor terminals are on the module) | **yes, once** |
| the count | 42 rows carried `raised` at `8a3c4be`, not 43 — see R3.5 | — |
| four rows left at `verified` | O4a, O4c, O4d, O8 — `INDEX.md:29` obliges `verified` to "put it in BACKLOG.md or fix it". `3c0108d`'s message says "Every row from the 09-25 reports is now acted … or rejected". O4c reproduces today: `check_design.py --help` → `no design at --help`, exit 1. O4d reproduces: `plugin.json` still promises "a verification gate that refuses to emit a board with unverified part pins" and `emit_board.main` (`:640-737`) refuses on no such thing. O4a has rotted a third time: `README.md:163` says 528 tests, the suite runs 547 — S5's own pattern | **four rows the drain did not drain** |
| five `acted` rows from the evening, at random | `random.seed(20260929); random.sample(<41 evening acted rows>, 5)` → **R22, S13, R15, S1, O5**. R22: "the concern stands and R2.5 continues it" — R2.5 is a named item in `SPRINT.md:24`; honest, barely. S13: `check_spine` reaches `simulation` (10 wires today), `bench_sim.py` still ships (145 lines), P19 and P2 exist; honest. R15: P16 exists (`PRODUCT_BACKLOG.md`); honest. S1: "a measurement of the past … superseded" — no fix, no item; the legend (`:31`) gives "judged not worth doing" to `rejected`, not `acted`. O5: P19 exists; "still 0 resolved" checked against `smartbin-local/.spark/findings.json` → blocked 11, open 8, rejected 1, resolved 0; honest | **4 of 5 honest; 1 mis-statused** |
| how many `acted` rows record no action | rows whose note says "no work", "superseded", "a confirmation", "closed as history": **O2, S1, S2, S7, M4, M5** (evening) and **A1, A13, A14** (morning) — 9 | `rejected` = 1 understates by the table's own legend |

### R3.3 — an outside read closes the sprint

This report, and its rows in `INDEX.md` as B1–B20. Whether they go through W9 before anything is
acted on is R4's to check.

### R3.4 — the PO question asked so the answer is one word

`SPRINT.md:27-38`: three domains, each with what it exercises, "the PO's answer can be one
letter", "Not started until chosen"; `PRODUCT_BACKLOG.md` Sprint 4 table marks R2.5 "PO chooses
the domain". **Asked concretely.** Not answered and not parked — the check at R4 is still open,
but the action was to ask, and it was.

### R3.5 — no summary before its count

Every numeric claim in `SPRINT.md`'s Sprint 3 and Sprint 4 sections, with whether a command sits
beside it and whether the number reproduces:

| line | claim | command beside it? | reproduces? |
| --- | --- | --- | --- |
| :84 | `Ran 528 tests — OK` | yes | **yes** — 528 at `8a3c4be` (archive run) |
| :85-86 | 5 tables, 30 mutations, every one caught | yes | **yes** — 7+8+4+3+8 = 30 in the five `sprint-3-*` tables; 30 caught today |
| :87-90 | build 12 traces, 0 errors, 10 wires, with both tsci, versions named | yes | **yes** |
| :91 | 14 `thickness=` (was 1) | yes | **yes** |
| :92-93 | remote from `/tmp`: end to end, 12 wires | yes | **yes** (from the scratchpad) |
| :76 | four items in one day | — | yes, four hashes |
| :107 | sixteen claims, six re-run | — | 16 A-rows; the six named |
| :108 | twenty-three intake rows closed | — | **yes** — 23 rows changed status in `c2ef430` |
| :109 | **forty-three** older `raised` rows remain | no | **no — 42.** `git show 8a3c4be:docs/observations/INDEX.md \| grep -cE '^\| [A-Z][0-9]+[a-z]? \|.*\| \`raised\` \|'` → 42 (46 at `7e84315`, minus R4, M1, M2, M7 closed in the morning). The 43 recurs in `SPRINT.md:21`, `:44`; `RETROSPECTIVES.md:122`, `:139`, `:159`, `:174`; `PRODUCT_BACKLOG.md` P15; commits `f35e7df`, `3c0108d`. **Not admitted** |
| :21 | 40 resolved, 3 fixed, 1 rejected, 4 new items | no | **no** — 40+3+1 = 44 for 42 rows; the rows are 38 + 3 (M3, R13, R20) + 1 (R19). The 4 new items exist (P16–P19). **Not admitted** |
| :45 | `grep -c '\`raised\`' docs/observations/INDEX.md` → 1 (the legend line) | yes — and that is the point | **no — 3**, at `3c0108d`, `2ce43d7` and HEAD alike; the number beside the command was never the command's output. **Not admitted** |
| :50 | R9: 13 traces | — | **yes** |
| :54-62 | R7: 11 traces, 9 wires (the corrected numbers); 533 → 532 | — | **yes**, both — the three admitted miscounts (12/10, 533, "the table has drained") are real and corrected |
| :101-105 | P3: the first value 15; six, then ten signals | — | matches `sprint-3-p3.json` and `tests/test_assign_pins.py` |
| :111-126 | P11 505, P12 511, P13 515, P14 528 (in the backlog; the log names the items) | in the commits | **yes**, all four at their commits |

Three numeric claims do not reproduce and are not admitted; all three are P15's, all three
written in the same hour as the three that were admitted. Every count that came from a test run
or a build reproduces; every one that came from counting rows in a markdown table by eye does not.

---

## 4. Architecture after the refactors

### Sizes, counted with `ast` (`scripts/emit_board.py`, 741 lines)

| function | lines | top-level statements | branch nodes |
| --- | --- | --- | --- |
| `emit` | 17 (`:621-637`) | 4 | 1 |
| `main` | **98** (`:640-737`) | 24 | **19** — was 104 / 21 at `7e84315`; it lost six lines, and it is still the largest function in the file |
| `header_lines` | 46 | 6 | 1 |
| `signal_lines` | 39 | 9 | 7 |
| the other eight sections | 5–27 each | | ≤ 5 |

Elsewhere: `check_spine.run` **143 lines, 23 branches** (`:232-374`); `parts.validate` **186
lines, 63 branches**; `boards.validate` 117 / 48; `assign_pins.main` 64 / 17; `design.py` 191
lines, six functions, none over 20 lines. The P14 split did what it said: `emit` is a sum, each
section returns lines, and the composition test (`tests/test_emit_board.py:752-760`) asserts
order on a fixture where every section is non-empty.

### `design.py` — one loader, three callers, and one script that does not use it

`emit_board.main` (`:651`), `check_all.placeholder_components_in` (`:208`) and `check_spine.main`
(`:414`, `:420`) load through `design`. **`assign_pins.main` does not**: it reads the JSON
outside any `try` (`:312`), resolves the project from `cwd` (`:318`, `boards.project_root()`
with no start), and passes the raw parts list to two functions that expect ids (`:330`, `:343`).
Three of P11's four claims — A8, A10 and "the documented invocation" — hold again, one script
over, on a documented command (§2, #14). It is the one entry point on the chain the loader was
built for that the loader does not serve, and the one `main()` on the chain with no test.

### Rules still written at more than one site

1. **`.spark/rules.json`** — `design.RULES_PATH` (`design.py:43`) exists for this, and
   `check_all.CONVENTIONS` writes the literal again (`check_all.py:309`). P14 fixed exactly this
   shape for `CIRCUIT_PATHS` (`:308` imports it) one line above.
2. **The upward walk** `for directory in [x, *x.parents]` — `boards.py:123` (the project),
   `check_spine.py:96` (the toolchain), `:172` (the converter), `findings.py:134`. Four walks,
   two rules for "where is my context".
3. **The three-outcome vocabulary** — `EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN = 0, 1, 2` in
   14 files, the `"could-not-run"` string in 9, and four scripts with a different middle name
   (`EXIT_IMPOSSIBLE`, `EXIT_INVALID`, `EXIT_MISMATCH`, `EXIT_NOTHING_TO_DO`). W1's rule has no
   home module; every file restates it.
4. **The bus-pin rule** is written once (`assign_pins.py:180-183`) and the instance-name rule
   once (`emit_board.py:264-276`), and they disagree: see "failure modes" below.
5. `sys.path.insert(0, str(SCRIPTS))` in 9 files — the price of scripts that are also modules;
   noted, not a defect.
6. **Two outputs on one net** is checked inside a part (`parts.py:306-327`, per rail and
   polarity) and nowhere across parts or against the board's own `power_pads`.

### Functions with no test, by name over `tests/`, then read

| module | untested by name | indirect coverage? |
| --- | --- | --- |
| `assign_pins` | **`main`**, `roles_of`, `_penalty`, `_why`, `_why_not` | the helpers through `assign`; **`main` through nothing** — the TypeError lives there |
| `emit_board` | `power_trace`, `trace_width_mm` (A15 named them; still unnamed), `power_note_lines`, `module_power_lines` | all four through `emit()`/`power_lines` and the sizing mutation, which is caught |
| `design` | `rules_in` | through `load` (`tests/test_design.py:114-134`) |
| `check_physics` | `check_trace_currents`, `check_capacitor_voltages`, `check_resistor_power`, `check_i2c_rise_time` | through `run` (27 tests) |
| `init_project` | `nets_in`, `rules_for`, `has_answers` | through `main`; the R13 mutation is caught |
| `check_all` | none that matters | as before |

### Input read outside a `try`, by `ast` (a `json.loads`/`read_text` with no `Try` ancestor in its function)

- **`assign_pins.py:312`** — the requirements file; malformed → `JSONDecodeError` traceback,
  exit 1. Reproduced.
- **`parts.py:101`** — the part file, in `load`; `design.parts_of` catches `PartError` only
  (`:162`). A malformed project part file → through `emit_board`: traceback, exit 1; through
  `check_spine`: `[!!  ] schematic  Traceback …`, **"the chain is broken"**, exit 1, because
  `check_spine.py:265-270` classifies any exit but 2 as a design defect. Reproduced. The A8
  class, one module below the loader that fixed it.
- `init_project.py:53`, `check_physics.py:496`, `check_footprints.py:523`,
  `check_firmware.py:184,207` — standalone `main`s; older, same class. `check_all` wraps its
  checks' reads in `Check.run`'s `try` (`:88-95`), so through the runner they are could-not-run.

### Failure modes that read as something they are not

| where | input | what it says | what it is |
| --- | --- | --- | --- |
| `assign_pins.py:180-183` | a `bus` signal whose name is not a board label — `{"name": "CLK", "bus": "spi"}` | `CLK  D3  needs nothing special`, exit 0 | the bus was dropped; nothing says so. `assign_pins.py:28-32` promises the opposite: "It does not silently drop a requirement it cannot meet" |
| `emit_board.py:660` + the same line | a **named** bus part — `{"part": "vl6180x-breakout", "name": "Rangefinder"}` | `.Mcu > .D3` → `Rangefinder.SDA`, `.Mcu > .D12` → `.SCL`, "needs nothing special", exit 0; unnamed, the same part lands on `.Mcu > .SDA`/`.SCL` "dedicated hardware, not a choice" | the instance prefix (`RANGEFINDER_SDA`, from `0201d6d`'s G7 fix) never matches a board pin, so naming an instance — the documented remedy for two of a kind (`build.md:27-29`) — takes it off the hardware bus in silence. Two different I2C parts, unnamed: `cannot emit a board: SDA asks for SDA (GPIO1), which is already taken` (a shared bus read as a pin conflict, exit 2); named: four GPIOs, no bus, exit 0. **A shared I2C bus cannot be expressed today, and the one way past the refusal is silently wrong.** Seventh instance of the family; no test names a bus part with an instance |
| `emit_board` | a project part whose `VOUT` is `rail: "logic", direction: "out"` | `<trace from=".Buck12v > .VOUT" to="net.V33" />` beside `<trace from=".Mcu > .3V3" to="net.V33" />`, exit 0, no note | two regulator outputs paralleled on one net; the per-part output rule (`parts.py:306-327`) cannot see across parts or the MCU's `power_pads` |
| `check_spine.py:363-365` | a build that succeeds and a converter with no mapping for a part | `[!!  ] simulation  no diagram was produced`, "the chain is broken", exit 1 (the car, today) | a converter limitation reported as a design defect — A9's shape at the last stage |
| `check_spine.py:265-270` | `emit_board` exiting 1 on a traceback | `[!!  ] schematic`, "the chain is broken" | the tool failed, not the design |
| `check_design.py` | a path that is not a file | `no design at --help`, exit 1 (O4c, still true) | could-not-look, exit 1 |

### Docstrings describing behaviour the code beneath does not have

- `assign_pins.py:28-32` — "It does not silently drop a requirement it cannot meet." It drops a
  `bus` it cannot match (above).
- `parts.py:8` — `parts.py --unverified            what nobody has checked yet, across every
  part in use` — the usage line shows no argument; `:420` requires one. The design skill copied
  the docstring (`SKILL.md:86`) and inherits the error.
- `check_all.py:33-40` — "the command in `spark-review`'s own skill leaves two of these seven
  permanently unasked … That skill's command is still wrong". `skills/spark-review/SKILL.md:34`
  is `check_all.py --project .`, which discovers all seven. Stale.
- `commands/build.md:38` / `emit_board.py:8-9` — "The project is found up from the requirements
  file's own directory, so this works from anywhere." True of `emit_board` and `check_spine`
  from anywhere *inside or beside* a project; `assign_pins.py:318` resolves from `cwd`, and
  `emit_board` refuses outright with no project at all (§2, #5).
- `design.py:132-137` (`on_rails`: "`parts.load` reads the file every time") — **true**;
  `parts.py:99-106` has no cache. Recorded because it is the docstring the R9 escape corrected.

---

## 5. What a third cold test should be aimed at

**(a), the battery sensor node — and this audit has already run the first three of its code
paths without building anything.** The family being hunted is "less than asked, exit 0", and
the paths that produce it today sit exactly where (a) walks:

1. **A bus part with an instance name** (`emit_board.py:660` → `assign_pins.py:180-183`). (a) has
   a BME280 on I2C and an e-paper on SPI; a second sensor on the bus, or a second display, or
   simply following `build.md:27-29`'s advice to name instances, takes the part off its bus with
   exit 0. Two different I2C parts unnamed is refused; named is silently wrong. Today's tests
   place SDA by an explicit `pin` (`tests/test_assign_pins.py:118`, `:175`) or through unnamed
   parts (`tests/test_emit_board.py:40`); none names a bus part.
2. **A bus signal named the way the vendor names it** (`assign_pins.py:180-183`). E-paper modules
   print DIN/CLK/CS/DC/RST/BUSY; a record written from the vendor's pinout, as
   `SKILL.md:23-26` insists, will say `DIN` and `CLK` with `bus: "spi"`, and both land on plain
   GPIOs with "needs nothing special". The reference design's I2C signals happen to share the
   board's labels, so the spine never sees this.
3. **A second rail regulated to logic** (no cross-part output rule). (a)'s battery goes through
   a regulator to 3.3 V; a record whose output is `rail: "logic"` is paralleled with the
   FireBeetle's own 3V3 on `net.V33`, exit 0. (c) walks this path too — its 12 V rail has to
   come down to logic somewhere — so it is not what separates them.
4. **Deep sleep and wake** — the `wake` capability and the bin's polarity constraint (P16) —
   which (a) needs and (b), (c) do not.

(c) exercises the most that is *new* — a MOSFET driver class, a 12 V `out` rail — but the new
paths it walks produced honest notes in the probe (`net.VALVE1 … NOTHING ON THIS BOARD RECEIVES
IT`; `nothing sources net.BATTERY12`): the generator says what it did not do. (b) walks G7's
fixed path eight times and the ADC1 budget, and has no bus, no second rail, no wake; its silent
risks are in firmware, which spark does not check. The defects that exit 0 without a word are on
(a)'s path, and one of them is reachable from the documented example by adding a name.

The PO's question stands (R3.4); this is a recommendation with its reasons, not a choice.

---

## What I would change first

**`assign_pins.main` through `design.load`, and a test that runs the documented example through
every documented command** — not `--help`. Evidence that this, not another document, is the
highest-value change: the one command a stranger is given cannot be executed as written (mode
`100644`), the first step they are given crashes on the file the same page shows them
(`assign_pins.py:330`), and the module written today to make loading one thing is used by every
chain script except the one that is documented first. `tests/test_routes.py` proves every link
is *named*; W2's lesson was that named is not run. The test is a `subprocess.run` of each command
in `build.md` on `build.md`'s own JSON block, in a temp project, asserting exit 0 — the R7
mutation table would then have something to catch.

Then, in order: make an instance-named bus signal find its bus pin (carry the need's own name
beside the instance name; `assign_pins.py:180-183` matches on the wrong one); let two parts share
a bus instead of refusing the second; report two `out` supplies on one net; fix the one dead
mutation in `sprint-2.json` and make the DoD re-run *every* table, not the item's; and write
the numbers in `SPRINT.md:21`, `:45`, `:109` from the commands beside them — 42, 3, and 38 + 3 + 1.
