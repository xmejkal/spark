# P158 part 1 — diagnosis: chain-and-checks

Written 2026-10-10 by the area's diagnostician, against spark 0.8.1 (main `a8aa34d`), from the code and from runs on two
scratch stores (`<scratch>/store`, a copy of the PO's store taken today; `<scratch>/store2`, empty) — never the real one.
Every run below carried the three-word prefix (`SPARK_HOME=… HOME=… TMPDIR=…`), verified once with `env | grep SPARK_HOME`.
Findings are the catalogue's K ids (`../catalogue.md`), plus the two by-design notes the area scope names: ★C7 (the exit code
and the goal suffix) and the STATUS_LED note (★C4). Tags: **E** a pointer or a run, **H** a claim with its source, **D** a
decision (who, when), — unknown. Line numbers are spark's at `a8aa34d`; irrigation's files are named as such.

The PO's criteria for every change (D the PO, 2026-10-10, verbatim): *"we want the system to be well designed so its well
testable and understandable where a mistake is happening and why"* — testability, diagnosability (a failure names where and
why, to a person and to an AI agent), simplicity (remove before add).

## 1. Root causes

### RC-chain-and-checks-1 · the rules file is a snapshot of derived facts, taken once, beside the person's answers

**Where.** `scripts/init_project.py:134-199` (`rules_for`: `i2c_buses` and `must_not_float` are derived from the part
records present *at init*, the rails from a built design present *at init*); `:274-303` (`merged`, the `--force` path: a
value stays, a null is filled, and `:300-302` an **empty list is "nobody filled this in" and is seeded again**); `:251-271`
(`not_yet_stated`: a list with some entries removed is nagged for each one); `scripts/check_spine.py` never calls it after a
build (`init_project` is imported for `PINNED_CORE` only, `:63`, `:314`); `scripts/check_all.py` reads the file as it is
(`:124`, `:138`). The documented sequence puts init first: `commands/idea.md:126` ("Run `/spark:init --board <the board pick>`
in the project first"), then `--requirements`, then `/spark:build`; `commands/init.md:36` says "**After a build, run it again
with `--force`**"; `commands/build.md:219` ("After it builds") names only `check_all`.

**Why.** One file holds two kinds of content: what a person answered (currents, volts, `i2c_hz`, fabrication limits) and
what spark can derive (the rail names from the circuit, the inputs the records declare, the bus lines the host must pull up).
The derived half is computed once, when the person happens to run init, and nothing in the chain recomputes it. Run before
any part exists — the order idea.md gives — the seed sees no parts: `must_not_float: []`, `i2c_buses: []`, `rails: {}`
(E: `<scratch>/proj-k46`, init before `requirements.json` existed, printed `rules after init: i2c_buses= [] must_not_float= []
rails= {}`). After the build, `check_all` then answers with two could-not-runs (E, same project: `[????] physics … !
physics.rails: no rail is described …` and `[????] rules-vs-netlist … ! the rules file states no rule to compare: i2c_buses
and must_not_float are both empty, which is what `/spark:init` writes and where they have stayed`, `2 check(s) could not
look: physics, rules-vs-netlist`, exit 2). The manual re-seed works (E: `init_project.py --force` → `must_not_float=
[['L9110sModule','AIA'],['L9110sModule','AIB']]`, `i2c_buses= ['Vl6180xBreakout.SCL','Vl6180xBreakout.SDA']`, rails `GND,
MOTOR6V, V33`; `rules-vs-netlist` then `[ok]`), but no command in the chain runs it, and the sentence that reports the gap
blames the file's author ("where they have stayed") and names hand-writing as the fix (`scripts/compare_design.py:258-259`:
"name the I2C lines and the pins that must never float"; `scripts/check_physics.py:475-477`), not the command that derives
them. The same snapshot design makes a derived entry impossible to retract: delete all four of irrigation's valve entries and
`--force` seeds them back (E: `init_project.merged({'must_not_float': []}, {'must_not_float': [['Valve1','SIGNAL']]})` →
`{'must_not_float': [['Valve1','SIGNAL']]}`); delete one and `not_yet_stated` says "the part records also name Valve1.SIGNAL,
which this file does not. Add it, or leave it out deliberately" on every `--force` (E, same run). The skeleton also carries
`physics.i2c_hz` and `i2c_bus_capacitance_pf` for every project (`:185-187`), so a board with no I²C part is asked about a bus
it does not have (init.md:72-73 tells the agent "with no I²C bus, it does not apply"; the file has no way to say so — P111 #45).

**Kind.** design.

**Explains.** K46 (the exit 2 after init, and nothing re-seeds), the "no way to say so to the rule" half of K45 (a retracted
entry comes back or is nagged), the I²C-fields half of K63. The "re-asks the goal S heard" half of K63 is prose sequencing
between idea.md S and init.md (an agent's two pages, not a script) — H, read not run.

**How a person or an AI agent would have known.** `check_all` prints the honest word (`????`, exit 2) and a wrong cause:
"which is what `/spark:init` writes and where they have stayed" is false when init was run before the parts existed — init
would have seeded them a step later — and the fix text sends the reader to type entries by hand that `--force` derives. Nothing
in `check_all`, `check_spine` or `--requirements` says "your rules are older than your design". init.md:36 holds the remedy;
the output does not. The second trap (a retracted derived entry returns) has no output at all: `--force` says "merged into
rules.json — every answer already in it was kept", which is true of answers and silent about the list it refilled.

### RC-chain-and-checks-2 · a line on the generator's stderr is a broken chain, and the one note most projects meet is about a signal the person declared

**Where.** `scripts/check_spine.py:374-375`: `if emitted.stderr.strip(): stages.append(Stage("schematic-notes", PROBLEMS,
emitted.stderr.strip()))`; `:526-530` (`verdict`: one PROBLEMS stage → exit 1 "the chain is broken"). The notes:
`scripts/emit_board.py:1124-1147`. The first of them, `:1128-1130` ("`%s was assigned a pin and no part claims it`"), fires
for `placed - claimed`, where `placed` is every assigned signal and `claimed` every record need's signal (`:1125-1127`); the
only signals not from a record are the file's own `signals` list (`scripts/design.py:291-305`, `signals_of`: records' signals,
then `wanted.get("signals")`). Documented at `docs/guide/how-it-works.md:37` ("It counts as a problem, so the run exits 1 even
when the board builds") and `commands/build.md:41-43` ("adds a pin no part record claims … *assigned, and connected to
nothing*, for you to wire by hand, and the spine flags that").

**Why.** Severity is decided by the channel, not the content: anything the generator writes to stderr is a problem of the
design. Of the five notes, four name a circuit gap the build will also stop on (a rail nothing sources, an output nothing
receives, an undriven side of a pair, two supplies on one rail) — and `--requirements` already says each of them before the
build and does **not** refuse (`scripts/needs.py:538-568`, `_power_gaps`; D the PO, 2026-10-08, in the docstring: "Said before
the build, never refused"). The fifth can only ever be about something the person typed: by construction `placed - claimed`
equals the file's `signals` (E: on `l9110s-module + vl6180x-breakout + jst-ph-2-power-inlet` with `signals: [STATUS_LED]`,
`placed - claimed = {'STATUS_LED'}`; on irrigation's copy the one note was STATUS_LED). So a project that declares a bare
signal exits 1 for as long as it keeps it, over a board that built, routed and simulated (E: irrigation's copy — `[ok] build
42 trace(s), 0 errors`, `[ok] simulation 36 wire(s)`, `[!!] schematic-notes note: STATUS_LED …`, `the chain is broken`, exit
1; the same verdict the cold test recorded on 2026-09-29, `~/Development/irrigation/DIARY.md:134-135`: "the STATUS_LED note is
`!!`, as build.md says it will be"). A verdict that is wrong by agreement stops being read: the diary's wording is the
evidence. A stderr line that is not a note at all — a Python warning, a library's deprecation message — would be "the chain is
broken" too (H: from `:374-375`; a run with `PYTHONDEVMODE=1 PYTHONWARNINGS=always` produced no warning on this machine, so
this stays reasoned).

**Kind.** design.

**Explains.** The STATUS_LED by-design note (★C4's surviving half); the reading context of K20 (the verdict line is what is
read, and here it is false by design).

**How a person or an AI agent would have known.** The stage line names the signal and the fact ("no part claims it, so
nothing in the emitted board connects to it"). It does not say that the signal is the file's own request, that the exit will
stay 1 while the file keeps it, or how to make it 0 (there is no way but deleting the signal). An agent following the
documented flow reads "the chain is broken", exit 1, and has to know from build.md:43 that this one is expected.

### RC-chain-and-checks-3 · `--keep` protects `board.tsx` but the chain never reads it: the verdict, `dist/` and the `built` record describe the regenerated board

**Where.** `scripts/check_spine.py:357-371` (the generator's output is written to `workdir/board.tsx`), `:399-401` (built
there), `:637-665` (`keep_into`: an existing `.tsx` is "left alone … named", `dist/` is replaced — "pure build output"),
`:608-609` and `:625-629` (`handed` is the work folder's requirements; `note_built` records it when the verdict is ok),
`:682-684` (the kept lines go to stderr **after** the verdict). `commands/build.md:72-74` says so ("`dist/` is still replaced
with a build of the freshly generated board, not of your `board.tsx`"). `tests/test_check_spine.py:316-331` pin exactly this
behaviour. Card: #44 (P110), open; **D the PO, 2026-10-05: build the kept file.**

**Why.** `run` has one input (the requirements) and builds its own emission; `--keep` is a copy step after the verdict, so the
person's file is never an input to anything. E (irrigation copied to `<scratch>/irr`, its committed `board.tsx` in place):
`check_spine.py irrigation.requirements.json --keep .` → stderr `left alone: board.tsx (delete it to have it regenerated)` /
`wrote dist — this is what every check reads`; `diff board.tsx <regenerated>` = 13 lines (a `BtnModePullupA` resistor and its
two traces that the kept file lacks, one header count 1→2, one host-requirement sentence moved); `dist/board/circuit.json`
holds `BtnModePullupA`, `board.tsx` does not; `check_all.py --project <copy>` then judged that `dist/` (exit 1, the four
floating-input findings), i.e. a board the person does not have beside the one they do. The `built` history event would be
written for the handed design's digests, which is the regenerated board's (`:625-629`), not the file's.

**Kind.** design (the decision is taken; the implementation is open).

**Explains.** K20; the regenerated-board caveat on ★C4's counts (`council/refuter.md:366-369`).

**How a person or an AI agent would have known.** Only by reading two stderr lines together, after the verdict, and knowing
that `dist/` is what `check_all` reads. The verdict line and `--json` say nothing; `check_all`'s "resolved from" block prints
`circuit dist/board/circuit.json`, which is true and cannot say whose board it is.

### RC-chain-and-checks-4 · "owes" is one flat list; what a missing fact does to the chain is decided in five places and stated in none

**Where.** `scripts/parts.py:97-98` (`CHAIN_FACTS = ("footprint", "pin_order", "pin_order_proof", "body_mm", "simulation")`,
comment: "absent, the record owes them, and **no build can place it**"), `:107-110` (`owes`). The consequences, each in its
own file: `scripts/emit_board.py:1081-1089` footprint → refuse, `:1091-1099` pin_order → refuse, `:1101-1109` body_mm → refuse
*unless* `--assume-missing-sizes`, which `scripts/check_spine.py:360` always passes; `scripts/sim_project.py:55-57` +
`scripts/check_spine.py:462-465` simulation absent → the **simulation** stage is could-not-run *after* the build passed;
`pin_order_proof` is read by nothing in the chain (grep: `scripts/parts.py:377-385` validate and `:826` the unverified listing
only). The policy: `scripts/needs.py:405` (`LAYOUT_FACTS = ("body_mm",)`), `:599-605` (refuse unless owed ⊆ LAYOUT_FACTS).
The promises: `scripts/parts.py:1631` (`--need`: "`--promote %s --project .` builds with it"), `:1518` (`--describe`: "one that
owes only its outline is written with a warning, one that owes more is refused").

**Why.** The truth table, from the code: footprint or pin_order missing → the schematic stage stops (exit 2); body_mm
missing → placed at a placeholder, said in the file's header, every stage `[ok]`; simulation missing → the board builds,
the simulation stage is `[????]`, exit 2; pin_order_proof missing → nothing stops anywhere. `--requirements` refuses a pick
owing `pin_order_proof` or `simulation` (stricter than the chain), warns on `body_mm` (right), and `--need` tells the reader a
catalog record "builds with it" while `--audit` lists what it owes (E: `--need rtc` on the store copy printed four records with
"`--promote … --project .` builds with it"; `--audit --json` lists each with `"owes": ["pin_order_proof", "simulation"]`; 17
owed rows in a catalog of 18 records, 0 broken — `--catalog`, 2026-10-10). The one comment that defines the list ("no build can
place it") is true of two of five facts. The PO's words on #102 (D, 2026-10-08) ask for the per-step, per-target version of
exactly this table; it does not exist as data anywhere.

**Kind.** design.

**Explains.** K47, K48; it is the hook P125 (#59) and P165 (#102) need.

**How a person or an AI agent would have known.** `--audit` says "owes pin_order_proof, simulation"; `--need` says "builds
with it"; `--requirements` says "owes X — fill it in its own home with --fact-set" and refuses. None of the three says what
the chain does without the fact, so the reader cannot tell a refusal that protects a build from one that protects a proof.

### RC-chain-and-checks-5 · the requirements writer reads the file with its own loader and names instances with its own copy of the rule

**Where.** `scripts/needs.py:607-615` (`json.loads`; `:612` `held = held if isinstance(held, dict) else {}`), `:430-432`
(`_called`, a copy of `emit_board.component_name`, `scripts/emit_board.py:290-302`), `:477-481` (`held_by.setdefault`: two
existing entries that are one name keep the first and say nothing). The reader the chain uses: `scripts/design.py:93-128`
(`read`: `:104-106` refuses a non-object, `:119-127` refuses two names that are one, naming both; `:75-90`
`names_that_are_one` skips unnamed entries because the default name is the generator's). The cycle: `emit_board` imports
`design` (`:42`), so `design` cannot import `emit_board`; `design.py:22-26` says naming components is `emit_board`'s "because
the name is decided by what the emitted file needs".

**Why.** Three readers of one file and two homes for one rule (W16). The writer accepts what the next reader refuses
(E `<scratch>/proj-k59`: `--requirements` with hand-written `OpenLid` and `Openlid` → "wrote …: board firebeetle2-esp32s3;
parts tactile-button (OpenLid), tactile-button (Openlid)", "kept, not from a pick: tactile-button (Openlid)", exit 0; then
`check_spine.py` → `[????] requirements … parts[0] is called OpenLid and parts[1] Openlid — the build refuses two components
of one name …`, exit 2). The writer replaces what the reader would refuse (E `<scratch>/proj-k61`: `requirements.json` =
`["a", "list", "of", "parts"]`, a board picked → "wrote …: board firebeetle2-esp32s3; parts tactile-button", exit 0; the file
is now an object; the list is gone without a word). And the default-name case is checked by neither reader (E:
`design.read` passes `["tactile-button", {"part": "tactile-button", "name": "Tactilebutton"}]`;
`emit_board.duplicate_component_names` finds `['TactileButton / Tactilebutton']` — the generator's net, one stage later).

**Kind.** implementation.

**Explains.** K59 (P175 #118), K60 (P176 #119), K61.

**How a person or an AI agent would have known.** K61: "wrote …" lists what was written, not what was lost — nothing. K59:
"kept, not from a pick" hints an entry was not explained, not that two entries clash; the chain says it next, correctly, and
the person looks at the chain rather than at the write. K60: the generator's refusal names both spellings — right words, late
stage.

### RC-chain-and-checks-6 · the board is stated in two files and the chain moves one of them

**Where.** `scripts/needs.py:498-518` (`_board_problems`: "it is one"; "pick one board"), `:617` (`board=board_picks[0]`);
`scripts/parts.py:2070-2109` (`_op_requirements`: prints `board: X → Y` at `:2085`, never touches `boards/active.json`);
`scripts/init_project.py:469-477` (writes `boards/active.json`); readers of `active.json`: `boards.active_id` through
`boards.py --id/--path/--get/--resolve` (`scripts/boards.py:513-524`) and `check_all.discover`'s note (`scripts/check_all.py:356`);
the chain itself takes the requirements' board (`scripts/design.py:342`, `board_id or wanted.get("board")`).

**Why.** `boards/active.json` was "the one place the board is chosen" when a project had a hand-written `board.tsx` (the bin's
CLAUDE.md says so); `requirements.json` now carries `board` too, and `--requirements` changes only that one. E
(`<scratch>/proj-k49`): init with `--board firebeetle2-esp32s3`; pick the board need to `xiao-esp32-c6`; `--requirements` →
`board: "firebeetle2-esp32s3" → "xiao-esp32-c6"`, exit 0; `boards/active.json` still `firebeetle2-esp32s3`; `boards.py --id`
answers `firebeetle2-esp32s3`. Two statements, one moved. The "one board, one MCU" limit the PO wants lifted (D the PO,
2026-10-07, #94 body part 2) is enforced at `needs.py:504-518` and `:617`, at `design.load`'s single board (`:342`) and in
`emit_board.place`'s single `Mcu` (H: `emit_board.py:346`, not traced further here — part 2's work).

**Kind.** design.

**Explains.** K49's `active.json` half; it locates the limit for K49's other half.

**How a person or an AI agent would have known.** The arrow line is printed; nothing says that `boards/active.json` now
disagrees, and `boards.py --id` answers the old board with no sign.

### RC-chain-and-checks-7 · five contract checks test the wrong property, in the wrong place, or with the wrong word

**Where and why**, one per finding (kind: implementation for all five):

- **K52** `scripts/boards.py:476`: `_validate_all` asks `active_id(project)` inside the per-board loop, for the "active" marker;
  with no `active.json` it raises `BoardError`, `main` (`:537-539`) prints it and exits 1. `--list` already guards the same call
  (`:526-529`). E: from a folder in no project, and with `--project <the plugin>`: `boards.py: no board selection at
  …/boards/active.json`, exit 1 — the one command that checks every board file cannot run where the board files live.
- **K54** `scripts/parts.py:101-104` (`_absent`) and `:658-660` (validate) ask "numeric", never "above zero"; `_op_fact_set`
  (`:1903-1904`) refuses only what `_absent` says; `positive()` exists for host parts alone (`:464-466`). E (store copy,
  `--dry-run` on `sen0550-flow-meter`, which owes `body_mm`): width −3, height 0 → "would set … body_mm … → {"width": -3,
  "height": 0, …}", exit 0; width `"wide"` → "body_mm is absent — a write fills a fact, it never empties one", exit 1 — the
  value is present and wrong, and the sentence says absent. A record with −3 × 0 would also "owe nothing" (`owes` uses
  `_absent`).
- **K63** (`--step`) `scripts/parts.py:2112-2126` → `store.add_project` (`scripts/store.py:253-269`), which resolves the path
  and never asks whether the folder exists; `init_project` refuses a missing folder (`:408-410`), `--step` does not. The store
  design has S make the project folder (§4 S1) — `needs.write` does (`scripts/needs.py:111-115`), but idea.md:17 runs `--step
  <project> S` first. E (`store2`): `--step <scratch>/ghost-project S` → "started step S of ghost-project … listed ghost-project
  on your projects", exit 0; `projects.json` holds it; the folder does not exist.
- **K50** `scripts/parts.py:517` applies `SELECTOR_SAFE` (`:176-185`, measured against tscircuit *selectors*) to a Wokwi chip
  name, which is a file name and a TOML string (`:520-521` says so). E (a project copy of irrigation's flow-meter record with
  the chip renamed `flow-meter`): `--validate` → "simulation.wokwi.chip is 'flow-meter', but a chip's name is a name — letters,
  digits and _", exit 1. And `scripts/needs.py:360-362` (`URL_IN_WORDS`) eats a `>` only when a `<` opened it: E
  `kept_reason("see https://x.com/a> more")` → `('see> more', True)`.
- **K51** `scripts/sim_project.py:92-97` collects a record's `stand_in`/`note`/`skip` sentence as it is; `:114` writes it into
  Markdown unescaped; `scripts/check_spine.py:516-522` prints the same sentence in the terminal with the same assumption. E:
  `limits_note([("Soil1", "a stand-in\n# A forged heading\n- a forged list item")])` prints a heading and a list item of its
  own.

**Explains.** K50, K51, K52, K54, K63 (the `--step` half).

**How a person or an AI agent would have known.** K52's sentence names a cause that is not the one asked about (a selection,
when validation was asked). K54's "absent" is false for a present non-number; the accepted nonsense prints as a success. K63
says exactly what it did ("listed ghost-project on your projects"), which is the fault. K50 and K51 say what happened;
neither loses data.

### RC-chain-and-checks-8 · the floating-input rule has one word for an input, and the record has no field to narrow it

**Where.** `scripts/init_project.py:81-101` (`declared_inputs`: every need with `direction: "in"` becomes a `must_not_float`
pair); `scripts/compare_design.py:177-212` (`check_floating_inputs`: a pin holds only when its net is a rail or a resistor on
its net reaches one; `:209-211` the remedy "add a pull-up or pull-down, or **remove the rule if the part pulls it itself**");
B13 (`4daa58f`, 2026-10-03) pinned by `tests/test_compare_design.py:67-74`. The record: irrigation's
`parts/dfr0457-mosfet-power-controller.json`, `needs[0]`: `"direction": "in"`, note "high lights the optocoupler's LED …
Sources about 5 mA at 3.3 V"; `"//"`: "a single-channel, optically isolated, HIGH-SIDE switch". Irrigation's
`.spark/rules.json` lists the four valves under `must_not_float` — derived by init, not written by a person (the `//` note
beside it says "Seeded from every pin the design's own part records declare as an input").

**Why.** The SIGNAL pin is a current load: an LED behind a resistor on the module. With the GPIO tri-stated no current flows,
the LED is dark, the MOSFET is off — the pin's "undefined level" has a defined effect, OFF. The rule's premise (a CMOS input
drifts) does not hold for it, and nothing in the record's vocabulary can say so: `direction` is one word, and the fact lives
in prose. The seed therefore puts the pin on the list; the rule then fails it (E: `compare_design.py` on irrigation's committed
`dist/board/circuit.json` with its rules → four `[floating-input] ValveN.SIGNAL: joined to Mcu.<pad> and no resistor to a rail`,
exit 1; `Valve1.SIGNAL`'s only net members are `Mcu.pin4` and itself). The remedy the finding offers — remove the rule — is
undone by `--force` when all four go, and nagged when some go (RC-1). So A6's two halves are both true: the rule is too wide
for a current-load input **and** the project's entries are not a person's data but init's derivation, which cannot be
corrected where it is.

**Kind.** design (the vocabulary) with a data consequence.

**Explains.** K45 (★C4's surviving half, F1, A6).

**How a person or an AI agent would have known.** The finding names the pin, the mechanism and a remedy. An agent that
follows the remedy meets RC-1's nag on the next `--force`, and nothing connects the two. The record's own words ("a CURRENT
load — two LEDs behind resistors — not a CMOS input", `council/refuter.md:103-117`) are in a `note` no check reads.

### RC-chain-and-checks-9 · ★C7, by design: the exit code is the chain's and the goal's gaps are a suffix — judged against the criteria

**Where.** `scripts/check_spine.py:533-541` (`left_off`: the `unserved` note `parts.py --requirements` wrote), `:544-555`
(`render`: the suffix only when `code == EXIT_OK`), `:668-679` (`--json`: `unserved` top-level, `status` unchanged);
`commands/build.md:94-98` ("Say it to the person: a green build says nothing about those needs"); `docs/guide/agents.md:250`.
D the PO, 2026-10-08 (#94 comment 12:52): a green build warns, not refuses, on a need with no pick and on a record-less
on-board pick. E (`<scratch>/proj-c7`, the reference parts plus an `unserved` note): text ends `the chain runs end to end —
but not every need is on the board: batt (no record: lipo-1000mah), report (no pick)`, exit 0; `--json`: `status: ok`,
`unserved: [...]`.

**Judgement under the criteria.** Testable: pinned (`tests/test_check_spine.py:1085-1098`). Diagnosable: the suffix names each
need and why, on the last line, which is the line a hurried reader takes (check_all's own rule, `scripts/check_all.py:413-415`);
the JSON carries it beside `status` and the agent guide says to read it. The exit code answers the question the command's
name asks — did the chain run — and the PO decided warn-not-refuse. The design holds. Two small asymmetries, not faults: the
text drops the note when the chain is not ok (`:554`) while the JSON keeps it (E: with a build error the JSON read `status:
problems` with `unserved` present; the text read "the chain is broken" alone); and whether a stranger misreads the line is an
H (USER-5) that only a person typing can settle (★C9). Nothing to change here before that test; one wording option is in §3.

## 2. What the design gets right and must be kept

- **Three outcomes, defined once, and `ok` unreachable while anything went unchecked.** `scripts/outcomes.py:19-43`
  (`status_of`), every check and the chain answer by it (`check_all.py:428-441`, `check_spine.py:526-530`,
  `compare_design.py:262`). The founding rule W1 (`scrum/WORKING_AGREEMENTS.md:15`). RC-1's exit 2 is this rule working.
- **A check that could not look says so and exits 2; "skipped" is a fourth word, distinct from could-not-run.**
  `check_all.py:16-39`, `:59`, `:84-95` (`Check.run` catches `SystemExit` too). All-skipped is could-not-run (`:437-440`).
- **Every resolved input is printed; two candidates are ambiguous, never a coin toss.** `check_all.py:308-360`, `:467-473`.
- **The build is proven by copper, not by the absence of an exception**: traces counted, error elements found, islands found
  through the source netlist (`check_spine.py:24-33`, `:229-233`, `:242-297`, `:419-448`); an empty `circuit.json` is refused
  before any check reads it (`check_all.py:105-117`).
- **A broken tool is told from a broken design**: the trivial-board preflight and the named tsci and core
  (`check_spine.py:135-148`, `:300-316`, `:404-417`).
- **One loader for a design, from its file, with every bad input a `DesignError` → could-not-run** (`design.py:1-29`,
  `:93-128`, `:337-347`); the chain's requirements stage is that reader (`check_spine.py:586-595`). RC-5 is about the one
  writer that does not use it.
- **What `built` vouches for is loaded once, before anything can change under it** (`check_spine.py:558-569`, `:608-609`;
  pinned at `tests/test_check_spine.py:955-970`).
- **`keep_into` never overwrites a `.tsx`** (`check_spine.py:637-665`) — the half of RC-3 to keep: a hand-edited board is
  never lost; what changes is which file the chain builds.
- **The `unserved` suffix and its `--json` key** (RC-9): a green chain never stands alone over a goal it does not serve.
- **Nulls are the output; `merged` keeps every answer; the brief is never replaced while it has answers**
  (`init_project.py:13-22`, `:238-248`, `:274-303`, `:306-328`). RC-1 keeps the answers half and moves the derived half.
- **A seeded rule comes from the records, keyed by the generator's own component name** (`init_project.py:81-131`), so a rule
  is keyed by the string that reached the netlist — the right source; RC-8 adds one word to it.
- **Refusals name what to record, in the generator's own words, as could-not-run** (`emit_board.py:1056-1121`; build.md's
  refusal table `:134-148`).
- **`--requirements` says the circuit's gaps before the build and does not refuse** (`needs.py:538-568`; D the PO, 2026-10-08).
- **Tests pin the documents**: the example output block, the one command's `--keep` (`tests/test_check_spine.py:355-364`,
  `tests/test_routes.py:140-154`). A change in §3 flips a pinned test on purpose and says which.
- **Stand-in limits are said in the terminal and beside the diagram, in the records' own words** (`sim_project.py:75-123`,
  `check_spine.py:498-504`) — RC-7/K51 is about one line break, not the idea.

## 3. Changes

Each block: title · kind · size (S under an hour, M a day, L more) · fixes · removes/adds · testable · diagnosable · proof.
Proposals; the PO orders.

### C1 · The chain re-seeds the derived half of `rules.json` after every kept build, and the derived half stops being a snapshot
- kind: story · size: **M** now (C1a), **L** as the refactoring (C1b) · fixes: K46, the retraction half of K45, the I²C half of
  K63; serves P137 (#71), P111 (#45).
- **C1a (M).** `check_spine.py --keep` ends by merging what init derives — `init_project.rules_for(nets_in(dist/…/circuit.json),
  design_in(project))` through `init_project.merged` — into `.spark/rules.json`, and says one line: `rules.json: seeded 2
  input(s), 2 bus line(s), 3 rail(s) from this build — every answer kept`. Removes: the instruction "After a build, run it again
  with `--force`" from `commands/init.md:36-42`, `README.md:155`, `docs/guide/journey.md:717-722` (three homes of one manual
  step). Adds: ~15 lines in `check_spine.report`, no new file. The messages change: `compare_design.py:254-259` says "nothing
  has seeded them: run the one command with `--keep .` after the parts are picked, or `init_project.py --force`"; the
  `check_physics.py:471-478` fix text the same. **C1b (L, the direction for the council):** the derived keys leave the file.
  `must_not_float`, `i2c_buses` and the rail *names* are derived at check time from `requirements.json` + the records + the
  circuit (the functions exist: `declared_inputs`, `i2c_lines`, `nets_in`); `rules.json` keeps answers only — currents, volts,
  `i2c_hz`, `fabrication`, and a hand list for a board with no requirements file (the bin). Removes `merged`'s list seeding
  (`:300-302`), `not_yet_stated` (`:251-271`), the two `//` seeding explanations, and the class of fault "the rules are older
  than the design". The bus fields are then asked only when a bus exists (K63's half).
- testable: `tests/test_check_spine.py::test_a_project_initialised_before_its_parts_has_its_rules_seeded_by_the_kept_build`
  (init with no parts → requirements → `report` with `--keep` → `rules.json` names the inputs and buses the records declare,
  and a hand-set `max_current_a` survives). For C1b, the K46 sequence as a `check_all` test that needs no `--force`.
- diagnosable: a stale-rules state is no longer reachable by the documented path; where it still is (a project with no
  `--keep` run), `check_all` prints `! the rules file states no rule to compare — nothing has seeded them yet: run
  check_spine.py requirements.json --keep . (it seeds them from the build), or name them by hand`.
- proof: on `<scratch>/proj-k46`'s sequence — init, requirements, the one command, `check_all` — `rules-vs-netlist` reads
  `[ok]` with no `--force` typed; the number of could-not-run checks drops from 2 to 1 (physics, which still owes the
  records' currents — the next proof is RC-4's).

### C2 · A signal the file declares is reported, not refused; a stderr line that is not a note is could-not-run, not a broken chain
- kind: story · size: **S–M** · fixes: the STATUS_LED by-design note (★C4), the exit-1-for-life it causes; hardens K20's
  reading context.
- removes/adds: remove the `placed - claimed` note from `emit_board.py:1125-1130` as a *problem*; the schematic stage's detail
  carries it: `[ok  ] schematic  46 trace(s) written; 1 signal of yours assigned and left for you to wire: STATUS_LED` (the
  generated file's header already lists it, build.md:42-43). `check_spine.py:374-375` splits the generator's stderr: lines
  starting `note:` are the four circuit-gap notes and stay PROBLEMS (the build would stop on them); anything else is
  `Stage("schematic", COULD_NOT_RUN, "the generator said something unexpected: …")`. `docs/guide/how-it-works.md:37` loses
  "It counts as a problem, so the run exits 1 even when the board builds". Alternative the PO may prefer: require
  `signals[].to` ("an LED, wired by hand") and keep the problem for an entry that says nothing — it adds a field; the
  recommendation above adds none.
- testable: `tests/test_check_spine.py::test_a_signal_the_file_declares_is_said_on_the_schematic_line_and_does_not_break_the_chain`
  (fixture with `signals`, `find_toolchain` patched → stages have no `schematic-notes`, the schematic detail names
  `STATUS_LED`); `::test_a_stderr_line_that_is_no_note_is_could_not_run` (patch the subprocess to print a warning);
  `tests/test_routes.py:151` keeps asserting no notes for the example. Irrigation's requirements become the fixture that
  exits 0 (the first time it ever has: `council/refuter.md:34-36`).
- diagnosable: the line names the signal and whose it is; "the chain is broken" is again a sentence that means something on a
  project with a bare signal.
- proof: `check_spine.py irrigation.requirements.json` on a copy exits 0 with the build `[ok]` and the schematic line naming
  STATUS_LED; `~/Development/irrigation/DIARY.md:134-135`'s "as build.md says it will be" becomes history.

### C3 · A record can say that an input defines its own level; the seed and the rule read it
- kind: story · size: **M** · fixes: K45 (answers A6: both — a rule too wide for current-load inputs, and no field to say so).
- removes/adds: adds one optional key on a need, e.g. `"holds_level": {"how": "a current load: the opto's LED behind a
  resistor on the module — open is off", "verified": true, "source": "<the schematic>"}` (a fact with provenance, as
  `body_mm` has); `init_project.declared_inputs` (`:81-101`) leaves such a pin out and the `//must_not_float` note says which
  and why ("Valve1.SIGNAL left out: its record says it holds its own level — …"); `compare_design.py:209-211`'s remedy gains
  "or, when the part defines its own level (an opto LED, a current load), say so in its record's need as `holds_level`".
  Nothing removed. With C1a, irrigation's four derived entries must be deleted by hand once (the seed then stays away); with
  C1b they vanish on their own — the argument for C1b.
- testable: `tests/test_init_project.py::test_an_input_whose_record_holds_its_own_level_is_not_seeded_and_the_note_says_which`;
  `tests/test_parts.py::test_holds_level_is_a_fact_with_provenance`; a test that irrigation's DFR0457 record (copied into
  `tests/data`) seeds nothing for SIGNAL.
- diagnosable: the finding on a seeded pin stays as it is; a pin left out is named in the rules file's own note, so a reader
  who wonders why Valve1 is not checked finds the sentence beside the list.
- proof: on a copy of irrigation with the record's one key added and the four entries removed, `check_all.py --project .`
  shows no `[FAIL]`, and `init_project.py --force` does not bring them back.

### C4 · One table says what each owed fact does to the chain, and every mouth reads it
- kind: story · size: **M** · fixes: K47, K48; the data for P125 (#59) and the step axis of P165 (#102).
- removes/adds: `parts.CHAIN_FACTS` becomes a table — `footprint: ("schematic", "stops")`, `pin_order: ("schematic",
  "stops")`, `body_mm: ("schematic", "placeholder — placed at a declared size, said in the file")`, `simulation:
  ("simulation", "that stage does not run; the board builds")`, `pin_order_proof: (None, "nothing stops; the order is
  unproven")`. `owes()` returns the same ids; a sibling `owed_sentences(record)` renders "owes simulation — the board builds;
  the simulation stage will not run until it is filled". `--requirements` refuses exactly the facts whose consequence is
  "stops" and warns on the rest, each with its consequence (removes `needs.LAYOUT_FACTS`, `:405`, and the policy at
  `:599-605` becomes a lookup); `--need` (`:1631`) prints the owed sentences instead of "builds with it"; `--match` and
  `--audit` print the same; `--describe` (`:1518`) says "one owing a fact the build stops on is refused". Removes the comment
  "no build can place it" (`:97`). The target axis (breadboard, perfboard, PCB, 3D) of #102 is a second column on the same
  table, later.
- testable: `tests/test_check_spine.py::test_what_each_owed_fact_does_to_the_chain_is_what_the_table_says` — for each fact,
  a record without it runs `check_spine.run` (toolchain patched) and the stopping stage equals the table's; and
  `tests/test_needs.py::test_requirements_refuses_exactly_the_facts_the_build_stops_on`.
- diagnosable: every owed-fact sentence ends with its consequence and the stage, so a refusal that protects a build is told
  from one that protects a proof, and an agent can decide to go on (the PO's words on #102: "allows to go on … but warns and
  makes sure its marked").
- proof: `--need rtc` on the PO's store lists the four DFRobot RTCs with "owes pin_order_proof (nothing stops), simulation (the
  simulation stage will not run)"; `--requirements` of a pick owing only `pin_order_proof` writes the file with that warning
  instead of refusing.

### C5 · The requirements writer reads the file through `design.read` and names instances with the one function
- kind: bug ×3 · size: **S** · fixes: K59 (P175 #118), K60 (P176 #119), K61.
- removes/adds: move `component_name` to `design.py` (it already owns `signal_name`; the name is the instance's identity for
  six modules, not an emission detail — `design.py:22-26` is overturned in its own docstring); `emit_board.component_name =
  design.component_name` for the 12 call sites, or the call sites move; **delete** `needs._called` (`:430-432`) and `_one_name`'s
  alias stays. `names_that_are_one` (`design.py:75-90`) uses it for unnamed entries. `needs.requirements` replaces `:607-615`
  with `design.read(file)` (a `DesignError` becomes the refusal, in design's words; the `parts`-is-a-list check at `:613-615`
  stays). Three small removals, one move, no new rule.
- testable: `tests/test_needs.py::test_a_requirements_file_that_is_a_list_is_refused_and_left_alone` (the twin of `:1521`),
  `::test_two_hand_written_entries_that_are_one_name_are_refused_naming_both_and_nothing_is_written`,
  `tests/test_design.py::test_an_unnamed_entry_s_default_name_is_one_name_with_a_named_one`; `tests/test_needs.py:1442-1446` keeps asserting
  the two functions agree — by being one.
- diagnosable: the sentences already exist: "…holds a list; a requirements file is an object with `parts`" and "parts[0] is
  called OpenLid and parts[1] Openlid — the build refuses two components of one name…" now print at `--requirements`, where
  the person is, with exit 1 and nothing written.
- proof: the three reproductions in RC-5 flip: `<scratch>/proj-k61` keeps its list and is refused; `<scratch>/proj-k59` is
  refused naming both; the default-name file is refused at the requirements stage of the chain.

### C6 · The board changes in one place
- kind: bug · size: **S** · fixes: K49's `active.json` half (C-40's "now" fix).
- removes/adds: `_op_requirements` writes `boards/active.json` when the board it writes differs from the active one (it
  already computes `board_was`), and prints `boards/active.json: firebeetle2-esp32s3 → xiao-esp32-c6`; or the alternative,
  `boards.active_id` falls back to the one requirements file's `board` when no `active.json` exists — the first keeps one
  file per statement moving together, the second removes a file from projects that have a requirements file. Recommend the
  first now; the second belongs with part 2 (no MCU, two MCUs), where "the board" stops being one field.
- testable: `tests/test_needs.py::test_a_re_picked_board_moves_active_json_with_it_and_says_so`.
- diagnosable: the line names the file and both ids; `boards.py --id` agrees with `requirements.json`.
- proof: `<scratch>/proj-k49`'s sequence ends with `boards.py --id` → `xiao-esp32-c6`.

### C7 · Five small contract fixes
- kind: bug ×5 (one chore if filed together) · size: **S each** · fixes: K50, K51, K52, K54, K63 (the `--step` half).
- removes/adds, each with its test and its sentence:
  - K52 `boards.py:476`: compute `current` once before the loop with the same `try/except BoardError` as `--list` (`:526-529`);
    the marker is blank when nothing is active. Test: `tests/test_boards.py::test_validate_runs_with_no_board_selection`.
    Sentence: none — it validates.
  - K54 `parts.py:101-104`, `:658-660`: width and height are numbers above 0 and finite; a present non-number is "body_mm.width
    is 'wide', not a number", a non-positive one "body_mm.width is -3; a dimension is above 0 mm". `_op_fact_set` inherits it.
    Test: `tests/test_parts.py::test_a_dimension_that_is_not_above_zero_is_refused_by_name`.
  - K63 `parts.py:2112-2126` / `store.py:253-269`: `--step` makes the folder it lists (`mkdir(parents=True, exist_ok=True)`)
    and says `made <folder>` — S "makes the project folder" (store design §4 S1) and `--step S` is S's first command
    (idea.md:17); the alternative is to refuse a missing folder with "no folder at …; make it, or run --needs-set first, which
    makes it". Test: `tests/test_parts.py::test_a_step_on_a_folder_that_does_not_exist_makes_it_or_refuses_and_lists_nothing_absent`.
  - K50 `parts.py:517`: a `CHIP_NAME` of letters, digits, `_` and `-` (a file name and a TOML string; whether Wokwi accepts a
    hyphen in a chip id is H — its own `chip-<name>` types carry hyphens, not checked here); `needs.py:360-362`: a `>` left
    directly after a removed URL goes with it. Tests: `tests/test_parts.py::test_a_hyphenated_chip_name_is_a_name`,
    `tests/test_needs.py::test_a_stray_bracket_after_a_url_leaves_with_it`.
  - K51 `sim_project.py:92-97`: the sentence is normalised once where it is read (`" ".join(sentence.split())`), so the
    terminal (`check_spine.py:516-522`) and the Markdown (`:107-115`) both get one line. Test:
    `tests/test_sim_project.py::test_a_line_break_in_a_record_s_sentence_cannot_forge_a_heading`.
- diagnosable: each sentence above names the field and the value; K52 stops naming a cause nobody asked about.
- proof: the five reproductions in RC-7 flip.

### C8 · `--keep` builds the kept `board.tsx` and says how it differs (P110 #44; D the PO, 2026-10-05)
- kind: story · size: **M** · fixes: K20.
- removes/adds: when `--keep DIR` holds a `board.tsx`, `run` still emits (the notes and the diff need it) and then builds the
  **kept** file: it is copied into the work folder over the emission, the kept footprint with it. The schematic stage says
  `board.tsx kept: differs from what requirements.json generates in 13 line(s) — delete it to regenerate`; `0 line(s)` says
  "the same". `note_built` is **not** written when the kept file differs — the `built` event vouches for the records'
  digests, and a hand file is not a build of them — and stderr says "the build was not recorded in your history: board.tsx is
  not what the requirements generate". Removes: the two stderr lines after the verdict (`:682-684`) for the `.tsx` case (the
  stage line carries it); `commands/build.md:72-74`'s caveat and its "build it with `npx --no tsci build board.tsx`" remedy.
  Flips `tests/test_check_spine.py:316-331` to pin the new behaviour, as #44 says.
- testable: `tests/test_check_spine.py::test_a_kept_board_tsx_is_what_dist_holds_and_the_stage_says_how_it_differs`;
  `::test_a_kept_board_that_differs_records_no_built_event_and_says_so`; the island and copper checks still run on the kept
  circuit (`:419-448` unchanged).
- diagnosable: the verdict and `--json` (`stages[].detail`) carry the difference; `check_all` then judges the board the person
  has.
- proof: on `<scratch>/irr`, after the change, `dist/board/circuit.json` holds no `BtnModePullupA` while the kept `board.tsx`
  has none; the stage line says 13 lines differ.

### C9 · ★C7 — keep; one wording option
- kind: chore · size: **S** · fixes: the asymmetry in RC-9, nothing else.
- removes/adds: `render` (`check_spine.py:554`) prints the unserved note on its own line in every outcome — `not every need is
  on the board: batt (no record: lipo-1000mah), report (no pick)` — so text and `--json` agree; the exit code stays the chain's
  (D the PO, 2026-10-08). Whether a stranger misreads the green line is slice 5's test (★C9), not a change.
- testable: `tests/test_check_spine.py:1085-1098` extended with the broken-chain case.
- diagnosable: unchanged — the line already names each need and why.
- proof: the two runs in RC-9 print the same note in both outcomes.

## 4. What I could not check, and why

- **"Any stderr line from the generator is a broken chain"** (RC-2's last sentence) is read from `check_spine.py:374-375`;
  a run under `PYTHONDEVMODE=1 PYTHONWARNINGS=always` produced no warning, so no stray line was observed. H.
- **Whether Wokwi accepts a hyphen in a custom chip name** (C7/K50): not checked against Wokwi's documents; the chip types
  spark writes are `chip-<name>` (`sim_project.py:66`), and I did not run a simulation. H.
- **K63's "re-asks the goal S already heard"**: a matter of two command pages read by an agent in sequence (`idea.md` S,
  `init.md`), not of a script; read, not run with an agent. H.
- **The one-board limit's full extent** (K49's other half): located at `needs.py:504-518`, `:617` and `design.load`; the
  generator's single `Mcu` (`emit_board.place`) is named from a function list, not traced. Part 2's work.
- **The real store**: never read or written; both scratch stores are copies or empty. Counts in this file are the copy's
  (18 catalog records, 17 owed — `--catalog`, `--audit --json`, 2026-10-10).
- **Incidental, outside the area, observed once:** on irrigation's toolchain (`tsci 0.0.2663`; the documents were measured on
  core `0.0.2600`), a two-part design `l9110s-module + jst-ph-2-power-inlet` built with `1 error(s):
  pcb_port_not_connected_error` ("the chain is broken", exit 1), while the three-part reference built clean. Whether that is
  the core version (init_project.py's docstring records `0.0.2687` failing the example) or the design (the driver's outputs
  drive nothing) was not examined. E for the run; — for the cause.
- **Build times** for provenance: the reference design 6.6 s, irrigation 9.6 s wall clock (`time`, this Mac, 2026-10-10) —
  so every change above is cheap to prove by running the chain.

## 5. Searches

none.
