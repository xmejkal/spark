# Product backlog

The single ordered list. If work is not here, it is not happening. **Order is the Product Owner's**
(W11). Every open item names the design that needs it (`**Needed by:**`, W14) and a
`**Value proven by:**` command whose output Petr can read; an item that cannot name both is not
pulled. The suite refuses a backlog with an open item missing its need line.

Last ordered: 2026-09-30 — council of five lenses, every claim reproduced first; **the PO's
to confirm.** Before it: 2026-09-29, by the PO — need-based; cut what nothing uses.

## The product goal

From a requirements file to a built, checked, simulated board:
`idea → parts → pin map → schematic → footprint → build → simulation`. Where it stands: the chain
runs end to end from a directory holding nothing but the requirements file, proven by
`check_spine.py` and by a test that follows the documents as a stranger would.

## v1 — the line we are finishing to

**A stranger goes from a requirements file to a built, checked, simulated board that an engineer
would accept as a first draft — host requirements honoured, no false alarms from the checks — on
two example projects, with the docs alone.** Out of v1, by the PO's call: real PCB layout, analogue
simulation, a link between two boards, and parts research beyond R11 below.

## Ordered — by value against effort, 2026-09-30

Reordered by a council of five lenses (hardware, firmware, a stranger's first hour, verification,
the scrum master), each scoring every item and probing the product to do it; every claim below was
reproduced before it was written down (W9). **The order is the PO's** (W11) — this is the
council's proposal.

**Stale as a list of what is next — 2026-10-01.** Five of its thirteen rows are done (P45, P46,
P29, P37, P32 as P32a) and it was ordered before Sprints 6 and 7 found P51 to P55. It is kept as
the council's reasoning of 2026-09-30, not as the queue; the queue is the sprint plan and the
items below. Reordering it is the PO's (W11) and is the first thing Sprint 8's planning should do.

| # | item | value | effort | why here |
| --- | --- | --- | --- | --- |
| **P45** | The rules a project is checked against are seeded from its design | 4 | M | `init` writes empty rule lists, so the irrigation DS3231's I2C lines are checked by nobody and `compare_design` refuses for want of a rule nobody wrote |
| **P46** | A number a fab house could change is data, not code | 3 | S | the same package table is copied into two scripts, and the via geometry is stated in three places |
| **P29** | The board's own supply, and nothing left unfed | 5 | S+M | no trace reaches the microcontroller's supply on any generated board, while the file says one does; the vendor fact it waited for is already recorded |
| **P43** | What an agent reads back | 3 | M | five JSON shapes, a fourth status word, the aggregate throws away `rule` and `fix`, and one payload is 80% something that has its own command |
| **P44** | Nothing shipped names one person's machine | 4 | S | a shipped agent file names an absolute home directory, and two files hard-code one country's shops as prose |
| **P40** | The architecture the refactor should aim at | 4 | M | the budget's new rule is refactor-before-raise, and duplication has already caused three defects; decide the target once, by people who did not write the code |
| **P39** | The library answers a need it has no words for | 4 | S | `--need measure distance` misses the rangefinder and `--need switch 12 V load` misses the MOSFET module — both send a researcher to write a record that exists |
| **P32** | One home for the converter and the chips — **PO: (a), move now** | 4 | L | v1's last word, "simulated", is true only beside the bin's repo (D17); two copies of each chip (D19, D20) |
| **P36** | The pin map is a file the firmware imports | 4 | S | twelve GPIO numbers are hand-copied into the irrigation firmware and a thirteenth into its scenario; nothing compares them |
| **P37** | What this simulation cannot show, printed | 4 | S | every stand-in record carries a mandatory honesty sentence and no command prints it, so a green scenario reads like a bench |
| **P38** | The capacitors P6 promised | 3 | M | `host_parts` has pulldown, pullup and divider; P6's own text promised a decoupling and a bulk capacitor |
| **P2** | A simulation that costs no Wokwi minutes | 3 | M | its "needed by: none yet" is false now: the irrigation firmware has no test of any kind and three diagnostic runs went to the quota |
| **R2.6** | A fourth cold test — **PO: the domain** | 5 | L | the cold tests found 13 and 12 gaps; ten of the twelve were invisible to every test in this repo |

### P33 — The documented setup must build the documented example — REOPENED 2026-09-30, **CLOSED by P51 2026-10-01** (its proof line was rerun green in an empty directory)
**Needed by:** every stranger who follows `/spark:init` then `/spark:build` — and it is a defect
introduced on 2026-09-29 by P28's own fix (I9). `init_project.py` writes `"@tscircuit/cli": "*"`,
so `npm install` fetches 0.0.2687, which fails on this plugin's documented example with
`Port [Mcu.pin17] is not connected to net [V33] by a PCB trace`, exit 1 — while 0.0.2600, the
version every number in `README.md` and `build.md` was measured on, builds the same file to 15
traces and no errors. Following the documented first step turns a passing chain into a failing one.
Pin the exact version, say in one line why it is pinned and how to move it, and hold the documents
to it.
**Value proven by:** a test that fails if the written package file names anything but the version
the documents quote; and, by hand in an empty directory, `init_project.py --project . --board
firebeetle2-esp32s3 && npm install && npx tsci build board.tsx` → `Circuits  1 passed`.

### P34 — A check that compared nothing says so — DONE 2026-09-30
**Needed by:** the RC car, whose `.spark/rules.json` holds the lists `init` wrote —
`compare_design.py <its circuit> --rules <its rules>` prints `0 rule(s) checked against the built
design` and `every rule holds`, exit 0, and `check_all` shows `[ok  ] rules-vs-netlist`, on a board
carrying the H-bridge whose floating inputs are this project's canonical defect. And the
irrigation controller, where `check_physics.py` prints `1 could-not-run: three of this tool's four
rules were not checked at all` and returns `status: ok`, exit 0, because its `main` builds both
from the `problem`-severity findings alone (`check_physics.py:497-505`) where `check_footprints`
builds them from all three.
Two lines in `check_physics.main`, copied from `check_footprints`; and in `compare_design`, zero
rules compared is `could-not-run` naming what the rules file would have to say.
**Value proven by:** `check_physics.py <irrigation circuit> --rules <its rules>` exits 2;
`compare_design.py <rc-car circuit> --rules <its rules>` exits 2; `check_all --project ../rc-car`
shows `[????] rules-vs-netlist`, not `[ok]`.

### P35 — The rules see spark's own wiring — DONE 2026-09-30 (the walker; the seeding split out as P45)
**Needed by:** every board this tool generates. The generator wires each signal pin-to-pin — a
trace that names no net — so a generated board has named nets only for its rails. `init` therefore
writes `i2c_buses: []` and `must_not_float: []`, `compare_design.check_i2c_pullups` iterates an
empty list, and `check_physics.Board.members` (`:112`) counts members only from net-named traces,
so its capacitor and resistor rules see a fraction of the board. The irrigation controller's
DS3231 sits on SDA and SCL and no check looks at them. P8 gave `compare_design`'s netlist model the
fallback that fixes this; the other two places never got it.
Give `check_physics.Board` the same fallback, and have `init` seed `must_not_float` from the chosen
records' inputs and `i2c_buses` from the board's own bus pins — so an empty list means "nothing to
check here", not "nobody filled it in".
**Value proven by:** `check_all --project ../irrigation` reports the I2C lines as checked or as
could-not-run, never silently absent; a mutation removing the fallback is caught.

### P45 — The rules a project is checked against are seeded from its design — DONE 2026-09-30
**Needed by:** the irrigation controller, whose DS3231 sits on SDA and SCL and whose I2C lines are
checked by nobody, and the RC car, whose `compare_design` now refuses because its rules file names
no rule. This is the half of P35 that was **not** done with the walker, and splitting it out is
deliberate: the walker was a move within `scripts/`, this needs `init` to read the design's part
records, which it does not do today. `init` writes `must_not_float: []` and `i2c_buses: []`, and
the generator wires signals pin-to-pin so no net is ever named SDA — so both lists stay empty and
an empty list is indistinguishable from "nobody filled it in".
`init` seeds `must_not_float` from the chosen records' inputs and `i2c_buses` from the board's own
bus pins, so an empty list means "nothing here to check" and is written as such.
**Value proven by:** ~~`init` on the irrigation project writes the DS3231's two bus lines~~ and the
four valve inputs; `check_all --project ../irrigation` reports them as checked rather than absent.

**The struck half of that line was wrong, and reproducing it is what showed so.** The DS3231
module's own record says: *"Add NO pull-ups: the module carries 4.7 k on SDA and SCL."* Seeding
its bus lines would have made `compare_design` report a bus nothing pulls up, on a bus that is
pulled up — a check firing on a correct board, which is the failure this product exists to avoid.
The records already draw the line: a part that needs the HOST to pull its bus up declares a
`host_parts` pull-up on that pin (the VL6180X does, for exactly this reason); a part that carries
its own declares none. So the seed is the lines this design makes the host responsible for, and an
empty list carries the reason, naming the module. Proposed as **W20**.

**Done, measured.** `init` on the irrigation project writes six floating-input rules (the four
valves, the DS3231's SCL, the mode button) where it wrote none; on the RC car, eight, including
both L9110S bridge inputs — the canonical case, which had no rule at all. On the reference design
it writes `Vl6180xBreakout.SDA` and `.SCL` as buses and two bridge inputs, and `compare_design`
then reports **checked: 4, status ok** against a board the chain built in the same run, where
before it refused for want of a rule.
A bus line may now be written `Component.PIN` as well as a net name, because spark's generator
wires every signal pin-to-pin and no generated net is ever called SDA — which was the other half
of why the list stayed empty and unusable. It resolves through the walker P29 taught to know a pad
by every name it answers to.

### P46 — A number a fab house could change is data, not code — DONE 2026-09-30
**Needed by:** anyone whose board house is not the one these numbers came from, and the three
scripts that already disagree about how to say the same thing. Measured: `PACKAGE_POWER_W` is a
**second copy**, not an import, in `check_footprints` and `check_physics`, so a package added to
one is missing from the other. The via and annular-ring geometry is stated in three files —
`check_footprints` demands at least 0.25 mm of ring, `emit_footprint` draws 0.35, `emit_board`
repeats the via numbers — and they agree today only by having been written on the same afternoon;
raise the checker's minimum and the generator keeps emitting footprints that fail it.
The rule to apply: **a number a fab house, a project or a person could change belongs in
`.spark/rules.json` with a default; a number that is a law or a published standard stays in code
with its source in a comment.** By that test, the process geometry and the pull-up window move;
IPC-2221's coefficients, the I2C rise times and the package ratings stay, and the package table
gets one home.
**Value proven by:** raising the annular-ring minimum in a project's rules file makes that
project's generated footprints fail their own check, and the package table appears once.
**Done.** `data/fabrication.json` is the one file; `scripts/fab.py` reads it and applies a
project's `fabrication` section. Five scripts stopped restating numbers. The PO's own acceptance
test — "can't they all read the same file where the data are?" — is `test_fab.py`'s
`test_no_script_restates_a_number_the_file_holds`. Proven on the irrigation board: with this
plugin's defaults `check_footprints` reports two 0.225 mm rings; with a project stating
`min_annular_ring_mm: 0.45` the same board fails on rings of 0.250 mm that were fine a moment
before. The 0.35 mm the generator draws is now `0.25 + 0.10` and still reproduces the 1.70 mm pad
on the hand-checked reference footprint.
The boundary that was drawn, and is written into the file itself: IPC-2221's coefficients stay in
`copper.py`, the I2C rise times in `check_physics.py` and 2.54 mm pitch in `check_footprints.py` —
a published standard is not a project's to override, and the formula beside it is what explains
it. Moving those would trade prose for a lookup.

### P29 — The board's own supply, and nothing left unfed — DONE 2026-09-30
**Needed by:** the irrigation controller. Its buck's record says "Feeds the FireBeetle's 5 V/VCC
input and the sensors" and the generated board has no such trace: `net.V5V` joins the buck's VOUT
and the flow meter's VCC, and the only supply trace on the board is `.Mcu > .3V3`, the module's own
output. The same hole is in the RC car. The vendor fact this item waited for is already recorded
and verified in `boards/firebeetle2-esp32s3.json` — DFRobot's "5 V DC for powering the board
(cannot charge Li-ion battery)".
Record VCC as a power pad that can receive, with the dual role said (a USB source when nothing else
feeds it, a sink when a regulator does); then the spine's island walk asks every component whether
it reaches a supply as well as a ground, so an unfed module can never again be `[ok]`.
**Value proven by:** the spine names the unfed module on today's irrigation board, and after the
fix `grep 'Mcu > .VCC' board.tsx` finds the trace and the stage is clean.
**Done.** On the board that existed: `Mcu.VCC is fed by net.V5V in this design and is not on it`.
After regenerating and rebuilding: 40 traces, 0 errors, no islands, one `.Mcu > .VCC` trace. The
two RC boards gained the four-line comment saying nothing drives their 5 V rail and no trace —
their buck declares its output on a rail called `servo`, so the condition is correctly false.

**It exposed a second defect, reproduced before it was fixed.** tscircuit names a port after its
label only for a component built from `pinLabels`; one built from a FOOTPRINT — which every
microcontroller module here is — gets ports called `pin17`, `pin32`, with the silkscreen label
only in `port_hints`. The shared walker keyed membership on the name alone, so every rule naming
a pad of the processor missed, in both directions: `compare_design` with
`must_not_float: [["Mcu", "D11"]]` answered "Mcu.D11 connects to nothing" about a pin the
irrigation board wires to a valve. `netlist.Netlist.names_of` now indexes a port under every name
it answers to, which fixes all three callers at once.

### P40 — The architecture the refactor should aim at — DONE 2026-09-30, `docs/2026-09-30-refactoring-architecture.md`
**Needed by:** W15b — the budget now counts code and says refactor before raising, so the first
question at every ceiling is "does this fit in less code", and nobody has answered what the target
shape is. Duplication has already caused three live defects: the three-outcome verdict written out
in three places with one copy wrong (P34), three netlist walkers of which only one learned that a
trace may name no net (P35), and each check's own CLI tail. Deciding the shape while moving code is
how a refactor becomes a rewrite.
A council of five technical lenses — Python engineering, the domain model, agent-system design,
test and change-safety, and migration planning — reads all 3,550 code lines and produces a written
architecture: the target module boundaries, what becomes a shared library and what stays a
standalone command, the sequence of steps each of which leaves the suite green and fits one
sitting, the interleaving with P34 and P35 which touch the same code, and the stopping rule.
**No code moves under this item.** Each step of the plan becomes its own item, ordered by the PO.
**Value proven by:** a document in `docs/` naming every proposed move with its code-line delta and
the defect it prevents or kills; a first step small enough to finish in one sitting; and the
council's own answer to whether this codebase should be refactored now at all.

### P41 — The safety net the refactor needs first — DONE 2026-09-30
**Needed by:** P34, P42, P35 and P29, which all move or change code in the check family, and by
the smart bin, whose `make check` calls this plugin's board tool eight different ways. Measured:
79% of the 596 tests reach into a module by symbol, so a move breaks them at import level rather
than at behaviour level; the board tool's command line has zero tests although a sibling
repository depends on it, and that repository's own Makefile records this exact break happening
before; ten scripts declare `--json`, one test passes the flag, and it asserts only the exit code,
so any payload key could be renamed with the suite still green.
Six tests for the board tool's eight documented invocations, asserting the exit code and the
single line of output; ten tests asserting each `--json` payload's top-level key set and that its
status is one of the three words. Key sets only, never values. About 180 test lines, which are not
budgeted.
**Value proven by:** renaming a key in any `--json` payload turns the suite red; so does changing
what the board tool prints for `--get chip`.

### P42 — The verdict has one home — DONE 2026-09-30
**Needed by:** P34, whose defect is that this rule is written out six times and one copy omits an
outcome. `outcomes.py` already owns the three words and the three exit codes, and its `EXIT_FOR`
map has **zero callers** while five scripts write the same dictionary inline.
`outcomes.verdict(problems, unchecked, unmeasured)` is `check_all.answer` moved verbatim, prose
intact, with `answer` kept as an alias so its mutation anchor survives; `outcomes.report(payload,
as_json, render)` generalises the shape `emit_footprint` already has. Six callers convert. A
`main` can then no longer invent a status, so the defect class is unrepeatable rather than fixed.
**Value proven by:** the status-from-severities expression appears once in `scripts/`; every
script's exit code still matches its printed status, proven by P41's tests.

### P54 — The suite cannot pass by asking the code to confirm itself — DONE 2026-10-01
**Run on the tree before the fix:** both checks failed — 39 module constants read outside the shared
vocabulary, and 84 files no mutation table names, `check_bom.py` and `flash_image.py` the two
scripts among them. Triaged one by one: 38 are sameness, agreement with a second source, a relation
between tuning numbers, or structure, each with its written reason; **one was the identity the item
named** — `test_flash_image` found the filesystem at the module's own offset. Rewritten against
MicroPython v1.29.0's literals (4 MiB, 0x200000, littlefs 4096/32/32/32/128/100), each cited to its
source file. **Shown both ways in a scratch copy:** the old test passes with the offset moved to
0x100000; the new one fails. 12 mutations on the two unmutated scripts, every one caught.
**Needed by:** `flash_image.py`, whose docstring names the symptom it controls — *"the simulated
board boots to a bare REPL with no main.py"*. The verification lens found the live instance:
`tests/test_flash_image.py:22-38` computes **both** its block count and its slice from
`flash_image.FILESYSTEM_OFFSET` and `**flash_image.LITTLEFS_SETTINGS`. It is an arithmetic identity
of the function under test, which **W2 forbids by name**, and the one number that has to match
MicroPython's ESP32 partition table is guarded by nothing. 81 code lines, 4 tests, **0 mutations
ever written.** Mutation testing is blind to this class by construction: a mutation on a constant
the test imports moves both sides of the assertion.
Two mechanical checks, ~15 and ~10 lines: a test may not build its expected value out of a
module-level constant imported from the module under test (legitimate shared vocabulary like
`outcomes.EXIT_OK` is the exception list, and `check_all` has 41 self-references to read through);
and **every file under `scripts/`, `agents/`, `skills/`, `boards/`, `catalog/` is named by at least
one mutation table, or listed as an exception with a reason** — the same shape as the orphan budget.
That second check is what produced every finding below; it needs no agent and runs in a second.
**Value proven by:** it fails on `test_flash_image.py` today, and its unmutated-file list names
`check_bom.py` and `flash_image.py`.

### P55 — The catalog is knowledge, so something must read the real thing — DONE 2026-10-01
**Reproduced first (W20):** 18 catalog records, not 35 (35 counted files and folders); and NO script
reads `module_has_i2c_pullups` — what adds pull-ups is a record's `host_parts`, so the fact and the
behaviour sat side by side with nothing checking they agree. Now `parts.validate` refuses a record
on an I2C bus that neither says its module carries pull-ups nor adds them as `host_parts` on every
line, and a module pull-up outside compare_design's 1k–10k band. `test_parts` walks the REAL
catalog and library (drafts may lack only `pin_order` and `body_mm`). **Acceptance, as a mutation:
flipping `module_has_i2c_pullups` in `catalog/dfr0819` turns the suite red** — caught, with 5 more.
The walk found the PO's own RTC saying the same fact under a second name; renamed (irrigation).
**Needed by:** the 35 research records in `catalog/`, which are the product's actual accumulated
knowledge and are asserted by nothing. All six catalog tests mock the directory away
(`mock.patch.object(parts, "CATALOG", …)` at `test_parts.py:721, 738, 754, 767, 778, 793`);
`test_parts.py:617` walks `parts/` and **nothing walks `catalog/`**. The verification lens flipped
`module_has_i2c_pullups` to false and set `i2c_pullup_ohms` to 1 MΩ in a shipped record and **both
escaped a green 692-test suite.** Per P45's own story, that first field is what decides whether a
bus gets pull-ups at all — so the field that drives the rule is in a file no test reads.
**Value proven by:** setting a shipped catalog record's `module_has_i2c_pullups` to the wrong value
turns the suite red.

### P56 — Does spark produce tested firmware? — DONE 2026-10-01, `docs/2026-10-01-firmware-and-tests.md`
**Needed by:** the product's own definition, which the PO restated today: *"the whole point, to make
DIY projects with ESP32 … to write the firmware and then simulate and test it to make sure it
actually works all together."* The v1 line stops at the board — *a stranger goes from a
requirements file to a built, checked, simulated board* — and spark writes no firmware at all: its
commands are `init`, `build`, `identify`, `research`.
The consequence is measured and uncomfortable. The irrigation controller's `firmware/main.py` is
**95 lines with zero tests of any kind**, written in one night so a Wokwi scenario had something to
run. The smart bin's firmware is **4,152 lines with 113 unit tests and 14 checks on a real
MicroPython runtime**, and that is the PO's own hand-built work, not spark's output. So the only
thing exercising a spark-generated project's firmware is a **paid** simulator — which is why the
quota became load-bearing, and why the PO asked today how to stop paying for it.
**This item is the analysis, not the build** (W19 covers work that only produces a document). It
must answer: **when** in the flow firmware and its tests appear; **how** they are produced without
spark becoming a code generator that writes bloat nobody reads; **why** each layer of test earns
its place, against what it catches and what it costs; and **where the boundary is** — what spark
owes a project and what stays the builder's.
**Value proven by:** a document a council of lenses reproduced its claims for, naming the smallest
increment that gives a generated project a test it did not have, and what that displaces in the
backlog. The PO orders from it (W11).

### P51 — The documented setup runs on a machine that is not the author's — DONE 2026-09-30
**Needed by:** every stranger, which is the whole v1 line. Reproduced by the first-hour lens in an
empty directory, following `commands/init.md` exactly:
```
npm ERR! notarget No matching version found for @tscircuit/cli@0.0.2600.
```
`init_project.PINNED_TSCI = "0.0.2600"` pins **the wrong package's** number: `0.0.2600` is a version
of `tscircuit`, and `@tscircuit/cli`'s 0.0.x line tops out at `0.0.394` (`npm view` both, 09-30).
`npx tsci build` succeeded for the lens only because a global CLI was already on PATH. **P33 is
marked DONE and this is its own `Value proven by` command** — the first and best evidence for W20.
Second half, same shape: after the two documented commands the project holds only
`requirements.json`. The board is built in a temp directory and deleted, so `check_all --project .`
answers *"4 not asked for"* and the word **checked** is unreachable from the documented path.
`--keep` exists, is documented nowhere, and writes to `/var/folders` — delete it or make it write
into the project, not both (W16).
**Value proven by:** in an empty directory with no global tscircuit on PATH, the two documented
commands leave a built, checked board in the project.
**Done** (`7028a08`, `6c1bec5`), and the cause was worse than this item said. `@tscircuit/cli`
declares **`tscircuit: "*"` as a peer dependency** and `tscircuit` was never in the package file at
all — so pinning the CLI could never have constrained the build, and every project spark has ever
created took whatever core npm had newest. The wrong version number is only what made that break
loudly. Both are pinned now. P33's own finding held: core 0.0.2687 stops the documented example at
`pcb_port_not_connected_error`, 0.0.2600 builds it to 15 traces and 0 errors.
Measured from an empty directory: **4 checks not asked for → 1**, buildability now runs, and
`init` seeds 3 rails from the built circuit — which it could never do while the design was being
deleted in `/var/folders` before `init` could read it.
**`--keep` is resolved rather than deleted:** it takes a directory and writes the board where the
checks look, which is the one behaviour W16 allows.

### P60 — Should there be a firmware skill, and for which runtime? — ANSWERED 2026-10-01, `docs/2026-10-01-firmware-skill.md`
**PO, 2026-10-01: accepted provisionally — rerun the measurement on Opus 5.5 once the CLI is
updated, and revisit if it changes the picture.** *Rerun the same day: 4 of 32 runs wrong on the
5.5 models, all four the Wokwi 5 V ADC task (8 of 8 across both generations); the chip and part
misses of 5.0 are gone. The answer stands, narrower — see the document.* The council's answer: no skill; MicroPython only; the facts a
model gets wrong (10 of 30 runs) are chip, part and tool facts, so they go in records, reach the
firmware through P36's file and are enforced by P56's seeded fake. The bin's headline lesson —
`WAKEUP_ALL_LOW` is an AND — is false on the S3 and C6, and spark's own parts library repeats it: P63.

**Needed by:** P56's answer, which puts the firmware in the conversation's hands rather than a
generator's — so how well the conversation writes it becomes the product's quality, and nothing in
this repository helps it. The PO asked, at the end of the day and explicitly to be taken up on
restart: *"do you think we should have something like micropython skill so that claude can write the
firmware well? Or also Arduino or ESP-IDF, lets take a look at this question when I restart."*
**Unanalysed. Do not start it as work** — it is a question to put to a council the way P56 was, and
the PO orders from the answer (W18, W11).
What it has to settle, and the evidence that already exists here:
- **Which runtime, and is it one or three?** The plugin's boards record `micropython_port`
  (`ESP32_GENERIC_S3`, `ESP32_GENERIC_C6`) and nothing else; the bin's firmware is MicroPython and
  its v1 Arduino reference was kept only because the state machine's shape came from it. ESP-IDF is
  named nowhere. Three runtimes is three harnesses, three fakes and three test stories — W14 asks
  which DESIGN needs each.
- **Skill or reference?** `skills/spark-design/references/` already holds the pattern: prose a
  skill loads, not code. A MicroPython skill would be the first that produces something a person
  runs on hardware, which is a different risk class from a skill that produces a board file.
- **What would actually go in it** that the model does not already know. The bin's hard-won facts
  are candidates and are written down: a task cannot cancel itself (`RuntimeError("can't cancel
  self")`), `Pin.irq(wake=DEEPSLEEP)` silently no-ops, `esp32.wake_on_ext0` does not exist on the
  C6, `WAKEUP_ALL_LOW` is an AND across every armed pin, the S3 has no per-pin ext1 polarity, no LP
  core from MicroPython. Those are not general knowledge and each cost a bench session.
  *(The council found otherwise, kept here as asked: `ALL_LOW` is an OR on the S3/C6, the `Pin.irq`
  and LP-core claims hold for the C6 only, and none cost a bench session — nothing has run on
  hardware. Corrected where it is read, by P63.)*
- **The bloat test.** A skill that restates the MicroPython manual is the shape the 09-29 cut
  deleted. One that carries only what was learned the hard way, with its source, is the shape
  `references/` already proves.
**Value proven by:** a document naming one runtime to support first with its reason, and either a
skill with every line traceable to a fact this project established, or a decision not to write one.

### P61 — Where a source we read is kept, so nobody researches it twice — ANSWERED 2026-10-01, `docs/2026-10-01-keeping-sources.md`
**Needed by:** every board and part record, and P60's fact lens, which re-downloaded the
ESP32-S3-WROOM-1 datasheet from the web and reported the cited version (v1.1) as *"not obtained"* —
while `smartbin-local/parts/datasheets/ESP32-S3-WROOM-1_datasheet_Espressif_v1.1.pdf` sat on disk,
unlinked from any spark record. The PO asked: *"are we actually keeping them? … it might be good
not to have to reresearch datasheets and board infos … would it be too much data? … should it be in
the project folder, or the spark itself?"*
Measured 2026-10-01: `parts.py --fetch` keeps a record's cited files beside it; the catalog has
files for 16 of 18 records (45 PDFs/images in git, 10 MB); the library's **6** records hold **0**
attachments (its 4 other files are chip sources); **the two board records hold none**; the bin
keeps 13 PDFs (6.8 MB) spark cannot see; everything an agent reads during research lands in a
session scratchpad and is lost. spark's `.git` is 33 MB and the repository is **private** on GitHub.
*(Corrected the same day: the first version said 8 records, 4 attachments and 13 MB — the first two
counted chip files as records and attachments, the third was `du` of the bin's whole `parts/`. Found
by the architecture lens, rerun before correcting. W13.)*
**A question for a council (W18, W11), not work.** It must settle: plugin, project, or a cache
outside both; what is kept (PDF, the source file at a tag, a text extract); how a record points at
it (version, checksum, the page or line a fact rests on); size and growth; and whether a published
plugin may redistribute vendor PDFs at all.
**Value proven by:** a document naming where each kind of source lives and why, and the one
command a researcher runs to find a source before fetching it again.

**The PO's answer (2026-10-01): spark will eventually be public.** So a record carries the pointer
and the file lives in one store on the person's machine, outside the plugin; the work is P62.

### P62 — A record points at the exact source it rests on, and the file is found before it is fetched again
**PO, 2026-10-01: Sprint 9, first — P64 follows it.**
**Needed by:** the FireBeetle board record, whose deep-sleep PSRAM claim cites "WROOM-1 v1.1 Table
12" as prose — nothing could find the kept v1.1, and the vendor URL now serves v1.8 with different
table numbers; and every researcher, since one fetch in five repeats one already made (P61).
Per P61's document: board records join the fetch path (`cited_urls` reads nested `source` fields);
every attachment holds URL, printed document version, page/table, sha256 and retrieved date; source
code is cited at a tag or commit; `--fetch` writes to a per-person store outside the plugin that
every project shares; `parts.py --kept <words>` finds a kept source without the network and is the
first step in `commands/research.md` and the researcher agent; the catalog's 45 vendor files move
into the store in the same commit (W16). *Estimate* ~30–60 code lines.
**Value proven by:** with the network refused, `parts.py --kept wroom` prints the local path of the
v1.1 datasheet and the board fact that cites its Table 12; and `git ls-files catalog | grep -c pdf`
prints 0.

### P63 — A fact this project wrote down wrongly is corrected where a conversation will read it — DONE 2026-10-01
**Spark `f5e2c66`, the bin `62a3139`.** Every correction reproduced at source before the edit (W20).
Acceptance, run: in spark `grep -on "[^.]*ALL_LOW[^.]*\." parts boards` → two sentences, both
"an AND only on the original ESP32"; in the bin, every remaining mention is that or the old claim
quoted as corrected. The bin's `STATUS.md` row 5 now reads **misdiagnosed, and closed anyway**. The
bin was committed `--no-verify` for its pre-existing CurrentShunt red alone, by the PO's ruling.
**Needed by:** every conversation that writes firmware for an S3 or C6 — spark's
`parts/tactile-button.json:37` teaches that `WAKEUP_ALL_LOW` is an AND across every armed pin, and
ESP-IDF v5.5.2's `esp_sleep.h` makes it an alias of `ANY_LOW` (an OR) on every chip after the
original ESP32. P60 found it, with three more stated wider than their source: `Pin.irq(wake=DEEPSLEEP)`
no-ops on the C6 only (on the S3 a level trigger arms ext0); "no LP core" is the C6's, the S3 has
`esp32.ULP`; the PSRAM 140 µA is Light-sleep in the kept datasheet (P61). Also stale or misfiled:
`firebeetle2-esp32s3.json:283` (`WAKE_ON_HIGH is False`; the bin says `True`; "#17334 was hit"
on no hardware), `:327-328` (PSRAM), `xiao-esp32-c6.json:102` (an API fact filed as silicon), the
C6 record's missing strapping role (its `onboard_led` GPIO15 is a strap).
spark's records here; the bin's own copies (`CLAUDE.md`, `HANDOVER.md`, `STATUS.md`, `config.py`,
`smartbin/board.py`, the `fd24455` reasoning) are the bin's, in the same sitting.
**Value proven by:** `grep -rn "ALL_LOW" parts boards` in spark and the bin's docs shows no claim
that it is an AND on the S3 or C6, and each corrected fact cites the source line it now rests on.

### P64 — Every claim spark ships is checked against its source by someone who did not write it — the PO's proposal of 2026-10-01
**PO, 2026-10-01: Sprint 9, after P62** — P62 gives every claim a document version and page, so the
checker reads the document a fact was written from rather than whatever its URL serves today.
**Needed by:** every conversation that reads spark's records, so a wrong fact stops spreading. The
PO: *"maybe we should have some agent that rechecks our files for halucinations in the already
defined data and code in spark, so that it doesn't then spread further"*.
Measured the same day: P60's false wake fact lives in `parts/tactile-button.json`
`host_requirements` — a **prose field the schema never asks for a source**, so it passed every
check by sitting one field over from `facts`. And `verified: true` is self-declared: **217 of 270**
library and catalog facts carry it, and the first one read (`tactile-button.json`, the 6x6 size) is
`verified: true` with a prose source, not the URL the rule demands. Nobody but the writer has ever
checked a flag.
The shape, for the council to refine: **mechanical first** — a check that every claim-bearing field
(facts, `host_requirements`, a board record's notes) carries a pointer, and that `verified: true`
carries a URL (with P62's version and page once it exists); it cannot hallucinate. **Then an
isolated reader** for what only judgement can do — fresh context, restricted tools, denied the
project's own notes (the reason `design-reviewer` is built that way): for each claim, quote the
source line that supports it, or say it does not. Its findings are hypotheses — raised in
`docs/observations/INDEX.md` and reproduced before any record changes (W9, W20) — because P60's own
lenses misread a footnote and miscounted twice. A checked fact records who checked it, when, and
against which version, so the next pass reads only what changed.
**Value proven by:** the mechanical check lists every unsourced claim in spark's records, with a
count; one isolated pass over the board and library records reports each claim supported,
unsupported or contradicted with the quoted line; and it finds the `ALL_LOW` claim on its own if
P63 has not yet removed it (run against `5056703`'s tree if it has).

## Seeing the board — the PO's request of 2026-10-01, all four chosen and ordered the same day

The PO: *"I'd like to have the viewer accessible when working with the plugin … both the schema and
circuit to 3d model, but also the wokwi simulator. Is there a nice way to show them?"* Found the
same day: tscircuit ships a live viewer (`tsci dev`, every spark project has it); the bin's
`tools/build-viewer.py` makes an offline page from the exports (B4); the Wokwi VS Code extension
is installed here, and wokwi.com/pricing lists "Wokwi for VS Code" from **Hobby+** up, which the PO
does not hold or is unsure of — so it is documented, not tried.

### P65 — The board is one command from being seen while you work — **PO: Sprint 8, after P55** — DONE 2026-10-01
**Run in the fresh project built from `build.md`'s example:** `npx tsci dev board.tsx --port 3020` →
`ready in 8372ms`, `curl localhost:3020` → **200** in about 3 s. **Not shown:** a headless Chrome
screenshot after 60 s of page time showed the viewer's PCB / Schematic / 3D tabs and its loading
tip, not the board — so whether the board renders in it is for a person to see, not claimed here.
`commands/build.md` → *See it*.
**Needed by:** the PO, working in any spark project. `npx tsci dev board.tsx` serves the schematic,
PCB and 3D on localhost:3020 and reloads on every change; nothing in spark mentions it.
**Value proven by:** `commands/build.md` names the command and the port, and in a fresh project
built from its own example the server answers (`curl -s -o /dev/null -w %{http_code}
localhost:3020` → 200). No code.

### P66 — Every build writes a viewer page — **PO: Sprint 9, after P62 and P64**
**Needed by:** the PO and anyone the board is shown to. The bin's generator (B4) moves into the
plugin as `scripts/viewer.py`; `/spark:build` writes `board-viewer.html` beside the board; the bin's
Makefile calls the plugin's copy and its own is deleted (W16). It needs the SVG and GLB exports,
which the chain does not make today — say what that costs in seconds before deciding where it runs.
*Estimate* ~100 code lines against ~146 left of 4,000: the budget is the constraint, measured first.
**Value proven by:** in a fresh project, the one documented command leaves a `board-viewer.html`
whose three tabs render (headless Chrome screenshot); the bin's `make all` builds its viewer through
the plugin's script.

### P67 — The simulation can be watched, not only asserted — **PO: Sprint 8, after P65** — DONE 2026-10-01 (documented, untried)
`commands/build.md` → *See it*: the extension's own command names read from its installed
`package.json` (3.7.0) — *Wokwi: Select Config File*, *Wokwi: Start Simulator*, *Wokwi: Request a New
License* — the licence it needs, and that nobody has run it on a spark project. No code.
**Needed by:** the PO — a passing scenario says nothing you can see. The Wokwi VS Code extension
opens the project's `wokwi.toml` and `diagram.json` — the files spark already writes — and runs the
firmware live, custom chips included. Needs a Wokwi licence of Hobby+ or above (wokwi.com/pricing,
read 2026-10-01); whether it spends CI minutes is not stated there.
**Value proven by:** `commands/build.md` says how to open it, what licence it needs, and that it was
not tried here. No code. Tried for real only once the PO holds a licence.

### P68 — The viewer can be opened anywhere — **PO: Sprint 9, after P66**
**Needed by:** P66's page, away from the machine that made it. After a build the conversation
offers — never does unasked — to publish the viewer as a private Claude artifact; the PO decides
each time, because publishing is outward-facing. Depends on P66.
**Value proven by:** `commands/build.md` carries the offer and its condition; one publish of the
bin's viewer, with the PO's yes, returns a link that renders the three tabs.

### P57 — A stand-in's geometry is could-not-run, not a failure — DONE 2026-10-01, as re-cut by the PO
**Run on the documented example after the last change** (an empty directory, `init`, the one build
command, `check_all --project .`): `[ok  ] buildability … ? JstPh2PowerInlet: pad 1.20 mm around a
0.75 mm hole leaves 0.225 mm of ring: over the 0.18 mm this process can make, under the 0.25 mm it
recommends`. A ring under 0.18 mm still FAILs (tested); both numbers cite JLCPCB's page in
`data/fabrication.json`. The bin's blocker 7 is the same ring and is an advisory now (bin `22677e6`).
**Needed by:** v1's own words, *"no false alarms from the checks"*, and the documented example,
which fails spark's own manufacturability check out of the box. Reproduced 2026-10-01:
`check_all --project .` on a fresh project built from `commands/build.md` gives
`[FAIL] buildability` on **four** 0.225 mm annular rings, every one of them on a **stand-in**
footprint — `jst-ph-2-power-inlet` drawn as a placeholder because nobody has drawn the real part.
P37 established the principle already: a stand-in declares what it cannot show, and its findings
become one could-not-run each rather than measurements of a part that is not on the board.
`check_footprints` has `placeholders` and does exactly this; `check_all` passes the list only when
a project's requirements name them, and the documented example's do not reach it.
**Value proven by:** the documented example's `buildability` becomes could-not-run naming the
stand-in, and a REAL footprint with a thin ring still FAILs.
**Premise FALSE when reproduced, 2026-10-01 (W20), and the item re-cut by the PO the same hour.**
Built from `commands/build.md` in an empty directory: `[FAIL] buildability … JstPh2PowerInlet: pad
1.20 mm around a 0.75 mm hole leaves 0.225 mm of ring, under the 0.25 mm this process guarantees`.
But `jst-ph-2-power-inlet` is **not a stand-in** — no `footprint_placeholder`, a body verified from
JST's B2B-PH-K-S drawing, and `jst_ph_2` is tscircuit's footprint of that very connector (KiCad's
own JST PH footprint has the same 0.225 mm across its narrow axis; 2 mm pitch leaves no room). The
false alarm is elsewhere: `data/fabrication.json`'s 0.25 mm has no source, and JLCPCB's
capabilities page says for 2-layer 1 oz PTH *"Recommended 0.25 mm or above; absolute minimum
0.18 mm"* — a recommendation enforced as a limit. **PO: two sourced limits.**
**Value proven by (re-cut):** the documented example's `buildability` no longer FAILs and says the
inlet's 0.225 mm ring is under JLCPCB's recommended 0.25 mm and over its 0.18 mm minimum; a ring
under 0.18 mm still FAILs; both numbers carry their source in `data/fabrication.json`.

### P58 — The bench instructions name the board you are holding
**Needed by:** the PO, this week — bench bring-up is item 2 on the smart bin's own NEXT list.
`smartbin-local/firmware/micropython/README.md` steps 2–4 still give the **XIAO's** pins: *"OPEN btn
D1, MODE btn D6, LED D7/D10"*, *"VL6180X on D4/D5 (+ INT to D0)"*, *"DFR0534 on D9"* — against
`config.py`'s D11, D14, D7/D5 and SDA/SCL — and step 4 names `bringup/04_mp3.py`, which became
`04_audio.py` when the audio went I2S on 09-25. Following that table wires a FireBeetle to a XIAO's
pin map, and `01_board_alive.py`'s own comment records what happens next: *"step 1 failed on a good
board and the obvious conclusion was 'bad board or bad flash'."*
The bin's own repo, not the plugin's — but the plugin is where the fix generalises (P36 → the
bring-up steps take their pins from the pin map rather than from prose).
**Value proven by:** every pin named in that README appears in `config.py` for the active board, and
every `bringup/*.py` it names exists. A check in the bin's `make check`, so it cannot rot again.

### P59 — A generated project's firmware can be imported without running
**Needed by:** every test tier after the first. `irrigation/firmware/main.py` ends with `main()` at
module scope and `main()` is `while True`, so **the file cannot be imported** — no test can ever
exist for it, by anyone, whoever writes it. 95 lines is not the problem; one line is. The bin shows
the shape: a two-line `main.py` over an importable package.
Reproduced the same day: with the file importable, a ten-line check finds that `VALVE_PINS` has four
entries and the loop drives three, so **GPIO13 (Valve4) is set to 0 at boot and never driven again**
— on a board whose requirements ask for Valve4 and whose netlist routes it. The paid Wokwi scenario
asserts two pins and passed over it. The firmware calls itself a stub, which renames the defect
rather than removing it: nothing says the stub covers less than the design.
**Value proven by:** `firmware.main` imports **with a fake `machine` on the path** (CPython or the
`micropython` unix port) in a spark-generated project, and the chain reports a signal the
requirements ask for that the firmware never drives **or never reads**.
*(Acceptance line corrected 2026-10-01 by P60's builder lens, W20: the first version — bare
`python3 -c "import firmware.main"` — fails on a CORRECT firmware too, for want of `machine`. And
the lens found a third defect of the same class: irrigation's `BUTTON_PIN = 18` is never read.)*

### P52 — A rail states what it carries, from the records that know — DONE 2026-10-01
**Run where `Needed by:` points, after the last change (W13, R6.3):**
- irrigation, `check_all --project .`: `V33: draws at least 355 mA; not stated: Soil1.VCC:
  operating_current_ma is not stated; Soil2.VCC …; Soil3.VCC …` — the soil probe, named.
- rc-car, `check_all --project . --circuit dist/car/circuit.json`: `SERVO: draws 700 mA of 3.00 A,
  resting on figures nobody has verified: Sg90Servo.VCC: stall_current_ma; Mp1584Buck5v.VOUT:
  output_current_a`.
**My own corrected line was wrong too (W20, the same day):** it said the car sums "the servo's stall
current AND the module's own draw" against the buck. The car's module is not on that rail — its VCC
pad sits on `V5V`, which the generated board already reports as undriven — so SERVO carries the
servo alone. Found by reading `car.tsx` before believing the output.
Also found while proving it: P63 had missed three copies of the false wake fact — irrigation's
generated `board.tsx`, and the RC car's own `parts/tactile-button.json` with the `remote.tsx` it
generates. Corrected the same sitting (irrigation `bbc8271`, rc-car `87443a0`).
**Needed by:** the irrigation controller and the RC car. The generated board says the gap in its own
text — *"THE WIDTH OF THE TRACES ABOVE ON net.GND, net.V12V, net.V33, net.V5V IS UNJUSTIFIED…
Nobody has stated what these rails carry"* — and `check_physics` exits 2 there, three of its four
rules unchecked, because `physics.rails` is `{}`. **But the summands are already in the records
with their verification flags**: the flow meter's 15 mA (verified), the DS3231's 200 µA (verified),
the soil probe's unstated current; and the source's rating is in the board file — `TPS62A02 buck,
2 A`. The RC car is the sharper case: two SG90s at 700 mA stall each against a 3 A buck, and
nothing sums them. Stall is the number that burns a regulator.
P29 answered *does a trace reach a supply*. Nothing asks *can that supply carry what is on it*.
Sum each rail's declared loads, compare against the feeding part's rating, and a load with no
stated current is **could-not-run naming the part** rather than a guessed total — which also fills
`max_current_a` so trace sizing stops asking for a number the records already hold.
**Value proven by:** on the RC car the servo's stall current and the module's own draw are summed
against the buck's rating and reported; on the irrigation board the soil probe is named as the one
load nobody has stated, instead of the rails being empty.
*(Acceptance line corrected 2026-10-01 before any code, W20: the car has ONE SG90, not two
(`car.requirements.json`); and irrigation's `physics.rails` is no longer `{}` — P53 seeded four
rails, all `max_current_a: null`. The car's rails are hand-filled (SERVO 1.2 A) and nothing compares
them with the MP1584's rating, which is the half of this item the car proves.)*
**Design, decided at the start (2026-10-01):** a record's power entry names the fact that states its
current — `draws` on an input, `can_supply` on an output, `feeds` on a converter's input (it draws at
most what the named output delivers, an upper bound for a step-down converter), `own_draw` on a
module's output it also consumes from; units from the fact name's `_a`/`_ma`/`_ua`. Linked, not
inferred by name: a part with a stall and an idle figure must say which one its pin draws. The sum
is computed where it is judged, never written into the rules file — a stated `max_current_a` still
wins, because a measurement beats a sum.

### P53 — The rules reach a project that already exists — DONE 2026-10-01
**Needed by:** the RC car, whose `.spark/rules.json` still holds `i2c_buses: []` and
`must_not_float: []` — so `compare_design` exits 2 there today, and **the canonical defect of this
whole product, the L9110S's floating bridge inputs, is checked by nobody on the board that carries
them.** P45 seeds at `init`, and `init` never reaches a project that already ran it. The same hole
one level over: `physics.rails` is `{}` on the irrigation project, which P45 left alone.
**Value proven by:** the RC car's rules file gains its eight floating-input rules and the
irrigation project its rails, without either project's hand-filled values being lost — ~~`--force`
already preserves those~~ and a migration must too.

**The struck clause was false, and it was the item's whole premise.** Reproduced on a copy of the
RC car: `--force` REPLACED the rules file, so `i2c_hz` set to 400000 came back `null` and a rail
current of 0.5 A came back nulls. The documents say *"build, then re-run with --force"* — so the
one workflow this tool prescribes destroyed the answers it had just asked somebody to go and
measure. The brief was protected by `has_answers`; the rules file, which holds the numbers that
need a meter, was not. Third time in a day that an acceptance line assumed a state nobody had
checked, which is W20.

**Done.** `init` merges: a value the file states always wins, a missing or null key is filled, an
empty list is seeded, a list somebody filled in stays theirs — and what the records would add to
it is NAMED rather than silently skipped. The two-board refusal was also blocking the wrong thing:
the RC car's rails genuinely cannot be chosen between, but `must_not_float` comes from part records
and a record says the same thing whichever board was built. That refusal is why the L9110S's
floating bridge inputs went unchecked for two sprints on the board that carries them.
Measured: RC car **0 → 8 rules**, both boards `every rule holds`, its 4 rails untouched; irrigation
**0 → 4 rails**, `check_physics` runs where it refused, its 4 hand-written rules kept and the 2 the
records add named.

### P43 — What an agent reads back
**Needed by:** every skill and command that reads a script's output, and `/spark:build` most of
all. Measured: five different top-level JSON shapes; `check_vendor_pins` returns a fourth status
word, `"mismatch"`; `parts.py --catalog --json` ignores the flag and prints prose; `check_all`
flattens each check's finding to `subject: detail`, throwing away the `rule` and the `fix` the
check produced, so an agent reading the aggregate must run a second command to learn how to fix
anything; and `assign_pins --json` is 35,852 bytes of which 28,739 is a list of unverified part
facts that has its own command, leaving the answer at 8%.
One envelope in `outcomes.py`, findings passed through rather than flattened, and the unverified
list dropped from the assigner's payload.
**Value proven by:** `check_all --json` on the irrigation board carries a `fix` for every problem
it reports; `assign_pins --json` is under 4 KB; every `--json` payload has the same top-level
shape, which P41's tests then hold.

### P44 — Nothing shipped names one person's machine
**Needed by:** anyone who installs this plugin who is not its author. A shipped agent file names
an absolute path under one home directory for the catalog, which `parts.py` already knows how to
find; two shipped files hard-code one country's shops as prose while `.spark/project.json` already
carries a `sellers` list and the tool already prints "sellers: none named in the brief". (The
third instance, the converter looked for in a sibling repository, is P32's.)
**Value proven by:** a test that fails on an absolute path or a home directory in anything under
`commands/`, `skills/` or `agents/`; and the researcher agent reading the brief's sellers instead
of a list.

### P39 — The library answers a need it has no words for
**Needed by:** the irrigation design and the smart bin. `parts.py --need switch 12 V load` finds
nothing, though `dfr0457-mosfet-power-controller` is the part that design already switches its
valves with; `--need measure distance` finds nothing, though `vl6180x-breakout` is the bin's
sensor. Matching requires every word as a substring of id + name + kind + aliases, and the records
say "MOSFET Power Controller" and "time-of-flight rangefinder". A miss then prints "Research it",
which is how a second record for a part we own gets written — the very waste the catalog exists to
end (this is intake I1 and audit D21, open since 2026-09-29).
The reader of this output is Claude, not a person typing, and every record's label together is
about 1,600 tokens — two existing commands already print the whole index in under 1,000. So a miss
prints the index rather than sending anyone to research, and says that is what it is doing.
**Value proven by:** `parts.py --need measure distance --project ../irrigation` puts
`vl6180x-breakout` in front of the reader, and `--need switch 12 V load` does the same for
`dfr0457-mosfet-power-controller`; a test asserts a miss never prints only the research command.

### P32 — One home for the converter and the chips — **PO: (a), move now** — SPLIT into P32a/P32b
**Needed by:** v1's last word. `check_spine.py:166-168` looks for the converter in the project and
then at `../smartbin-local/…`, so the chain reaches `[ok] simulation` only on a machine where the
bin's repo sits beside the project. The first-hour lens reproduced the sharper form: the same
requirements file gives `[ok] simulation` in a bare directory and `[????] no circuit-to-wokwi
converter found` after running the documented `/spark:init` — because `project or SCRIPTS.parent`
then walks up from the plugin and finds the author's own bin repo. **The headline green is
reproducible only on this machine, and doing the documented first step is what turns it red.**
**Refined by the firmware lens, which counted it: ~1,307 lines move, 558 stay.** It is two sittings,
not one, and the second can leave the bin red overnight — so it is two items.

**P32a — the converter moves and the chain finds it anywhere. DONE 2026-09-30.** The nine core files
(`cli.ts`, `lib/{mapping,emitters/wokwi,netlist,board,geometry,merge,validate,types,placement}`) and
their ~590 lines of tests, plus `package.json` — **spark's first JS dependency tree; it has no
`package.json` today.** Make `--circuit/--out/--chips` required rather than defaulted to the bin's
paths, make `SPARK_BOARD_JSON`-or-`--board` mandatory (the fallback `../../../.spark/board.json`
resolves to the bin's and dies on arrival — spark's own `.spark/` holds only `cache`), add the
plugin's own location to `CONVERTER_PATHS`, and move `parts/*/chip/` as the one home for chips.
**Value proven by:** `check_spine.py` reaches `[ok] simulation` **from a directory with nothing
beside it**, and `bun test` is 62/62 inside the plugin.
**Done**, with two corrections to the plan. The suite is **38 tests, not 62**: `real-board.test.ts`
stayed in the bin because it reads that repo's `dist/`, its chips and its root `mcu-pins` — it
tests a board end to end, which is knowledge of that board, not of this tool. And the lens said
only `lib/checks/firmware-pins.ts` imported `mcu-pins`; three test files did too. Two needed four
silkscreen names, which are now the tests' own vocabulary.
**It also found a live regression P29 had shipped**: the irrigation chain stopped at `"VCC" is not
a pin of board-esp32-s3-devkitc-1`, because P29 made that pad wirable and Wokwi's stand-in devkit
calls the pin `5V`. Found by running the chain in the project the need line names — R6.3, written
this morning. Fixed in the board file, and the board CONTRACT now compares `power_pads` against
`wokwi_power_pins` so the class cannot recur.
**And the gate now runs the TypeScript**: `tests/test_converter.py` runs the converter's own suite,
and `check_commit.py` lends the archived tree its installed dependencies. Without that the move
would have taken 1,300 lines of the product out of reach of every guard here.

**P32b — the bin stops carrying its own copy.** The bin's `Makefile:95,241,249` call the plugin's
converter with explicit paths; `check-consistency.ts` imports across; the hand mapping table is
deleted (W16) once the bin's parts have spark records; the bin's duplicate chip sources go — `cmp`
says all six files are byte-identical to `spark/parts/*/chip/`.
**Value proven by:** the bin's `make check` is green but for its one allowed red line, the
unmeasured motor current, with no converter inside the bin repo.
**Staying in the bin, and it should:** `check-consistency.ts` and `lib/checks/{firmware-pins,
scenario-pins,wake-polarity,bringup-pins}.ts` — 558 lines of that board's knowledge of itself, and
`firmware-pins.ts` imports the bin's own root `mcu-pins`. Same reasoning that deleted P16.

### ~~P18 — evals~~ / two files nothing reads — **PO's call, verified 2026-09-30**
**Needed by:** nobody, which is the point. Three verified deletions, each reproduced:
- **`evals/`** — `git ls-files evals` returns **0 tracked files**, 760 KB of HTML reports from
  2026-09-24 sit on disk, and **`.claude-plugin/plugin.json:23` declares `"evals": "./evals"`** — so
  the manifest ships every installer a pointer to an empty promise. P18 has been "run or delete"
  since Sprint 2.
- **`chips/wokwi-api.h`** — the only tracked file in `chips/`, and `grep` across `scripts tools
  commands skills tests` finds **nothing that reads it**. `CHIP_SOURCE_SUFFIXES` is `.chip.c` and
  `.chip.json` only; `wokwi-cli chip compile` downloads its own header and produces a byte-identical
  wasm without it. Three stale copies sit in the irrigation project too.
- **`check_spine.py --keep`** — documented in no command, skill or README, and it keeps the board in
  `/var/folders`, which is not a place anyone looks. Delete it, or make it write into the project as
  P51 requires — not both (W16).

**The PO's decision, 2026-09-30: `evals/` and its manifest key go; the other two stay for now.**
`evals/` is deleted and `"experimental": {"evals": "./evals"}` is out of
`.claude-plugin/plugin.json` — the directory was untracked, so it was moved to this session's
scratchpad rather than destroyed. `chips/wokwi-api.h` and `--keep` remain; `--keep` is P51's to
resolve, since P51 must make the board land in the project and W16 then forbids keeping both.

### ~~P32, the original text~~ — superseded by P32a and P32b above (2026-09-30)
**Needed by:** a stranger's simulation — the spine finds the Wokwi converter only at
`tools/circuit-to-wokwi` in the project or at `../smartbin-local/tools/circuit-to-wokwi`
(audit D17), so v1's "simulated board" holds only beside the bin repo; and W16 — the bin's two
chips were copied beside their records, not moved (D19), and the converter's hand table remains
the bin's own mapping (D20). About 1,000 lines of TypeScript with bun dependencies, and the bin's
`make check` rides on it, so it is a day's work, not a slice.
**Value proven by:** the one command reaches `[ok] simulation` from a project with nothing beside
it but the plugin; one copy of each chip; the bin's `make check` green against the plugin's copy.

### P36 — The pin map is a file the firmware imports — DONE 2026-10-01
**Run in irrigation after the last change** (`8117b27`): `assign_pins.py irrigation.requirements.json
--emit-pins firmware/pins.py` writes twelve plain constants, each with its silkscreen pad (`STATUS_LED
= 15  # pad MO` — the board's key is MOSI, its silkscreen MO), why, and the board record's words for
its roles; `main.py` imports them and types no GPIO. On the `micropython` unix port with a fake
`machine` recording every Pin, ADC, I2C, irq and write over 20 loops: **before and after identical,
24 lines**; a planted VALVE2 = 10 shows on both lines it touches. The test that every signal appears
exactly once is `ThePinMapIsAFileTheFirmwareImportsTest`. The scenario's `pin: 38` is YAML and stays typed.
**Needed by:** the irrigation controller's firmware — twelve GPIO numbers are typed into
`firmware/main.py` by hand and a thirteenth into `sim/scenarios/wet-and-dry.scenario.yaml`, and
nothing compares any of them with the assigner's output; they agree today by luck. The bin needed
121 lines of its own checker to police the same copy.
`assign_pins --emit-pins <file>` writes the map as constants a firmware imports, each with its
signal name, its pad and the reason the pin was chosen.
**Value proven by:** the irrigation firmware imports the generated file and its scenario passes
unchanged; a test asserts every signal the design has appears exactly once in it.
**Amended by the PO, 2026-10-01, before any code:** "passes unchanged" is proven FREE — the
firmware run before and after on the real `micropython` unix port with a fake `machine` drives
exactly the same GPIOs — because Sprint 8 excludes any `wokwi-cli` run and the scenario is metered.
**Bound by P60 (2026-10-01):** the file is plain integer assignments, not `const()`, so it imports
under CPython and MicroPython alike; the assignments are data first, rendered as Python, so a later
`pins.h` is one renderer and is not built now. **PO, 2026-10-01: yes, in P36:** each pin's comment carries
the record facts for that pin (*"GPIO11 — ADC2, unusable with WiFi"*) — P60 measured short notes
fixing 7 of 7 failing runs, and this delivers them at the moment of writing, from a record.

### P37 — What this simulation cannot show, printed — DONE 2026-10-01
**Needed by:** anyone reading a passing scenario. Every stand-in record already carries a mandatory
`stand_in` sentence — Wokwi's DS1307 answers at the DS3231's address with the same seven time
registers and has no alarms, no temperature; each valve is an LED with no MOSFET, no 12 V and no
flyback — and no command prints any of it, so a green run reads like a bench result.
The spine's simulation stage and `parts.py --show` print the stand-in limits for the design.
**Value proven by:** `check_spine.py <irrigation>` prints the three limits under its simulation
line, and a record whose `stand_in` is empty is already refused by the contract.

**Done.** The sentences were already written and already **mandatory** — `parts.py` refuses a
built-in stand-in without one — and no command had ever printed a single one. The chain's
simulation stage now names them, and `WHAT-THIS-CANNOT-SHOW.md` lands beside the diagram, because
the terminal gets closed and the sim directory is what somebody opens a week later.
Measured on the irrigation controller: **7 lines** — the four valves are an LED on a gate drive
with no opto, no MOSFET, no 12 V load and no flyback; the buck is not simulated at all because the
simulator powers the board itself; the DS3231 is a DS1307 with no EEPROM at 0x57.
Twelve lines became seven by grouping identical sentences: three identical soil probes printing
three identical paragraphs is how a finding gets scrolled past, which is partly how this one
stayed invisible. And both the detail and the file write were **extracted out of `run`'s
simulation stage first** — no test on this machine reaches it, so two of this item's own mutations
were about to escape through that hole.

### P38 — The capacitors P6 promised
**Needed by:** the irrigation controller's 12 V rail, which switches four solenoids off an unfused
barrel jack with no bulk capacitor, and every module on the 3.3 V rail with no decoupling. P6's own
backlog text promised "a pulldown, a decoupling capacitor, a bulk capacitor on a rail"; the kinds
it shipped are pulldown, pullup and divider.
Add the two capacitor kinds to `HOST_PART_KINDS`, wired to the rail the record names, placed with
the other passives. (The valves' flyback diodes stay prose: the record puts them across the coil,
between the module's own screw terminals, which is harness wiring and not this board's to place.)
**Value proven by:** the irrigation board carries the bulk capacitor its record asks for; the
file's prose block shrinks by that requirement; a mutation removing the kind is caught.

### P2 — A simulation that costs no Wokwi minutes
**Needed by:** the irrigation controller's firmware, which has no test of any kind, and the quota —
three diagnostic runs went to discovering one documented fact (diary I11), and two audit rows could
not be checked because a scenario run costs minutes. The bin proves both shapes already: a fake
`machine` module for unit tests, and `run_on_micropython.py` for the whole firmware on a real
MicroPython runtime, 113 and 14 checks, free.
**Value proven by:** the irrigation firmware's logic is tested on this Mac with no Wokwi run, and
the scenario is kept for what only a simulator can show.

### R2.6 — A fourth cold test — **PO: the domain**
**Needed by:** the product itself: the third cold test found twelve gaps in one evening and ten of
them were invisible to every test in this repository. Two domains from the earlier menu are
unchosen — a battery sensor node, a USB MIDI foot controller — and the PO may name another.
Written first as a plan with predictions, diary kept as it goes, the plugin used only as
documented. **Its definition of done adds one thing this time: the test ends in firmware that
runs**, because no cold test has yet written any.
**Value proven by:** the diary, the predictions scored by someone who did not write them, and every
gap either fixed in the plugin or in this list with its need.

## Asked and answered — 2026-09-30, the PO's question about a vector store

**Would the boards, modules and components be better in a vector store, searchable by what they
do?** Researched two ways before answering. **No, and not at this size — revisit at about 550
records.** The corpus is 37 records whose whole searchable surface is ~1,600 tokens, and two
commands already print the entire index in under 1,000 — retrieval earns its keep only when the
corpus cannot be shown to the reader, and here it can. It would also be this plugin's first
third-party dependency (there are none today), a model larger than the repository, and a float
blob that diffs as noise in a repo reviewed as diffs.
The outside evidence says the same: no distributor or EDA tool ships embedding search — Octopart,
DigiKey, KiCad, Altium and LCSC all parse units and filter parameters — and the only published
evaluation of embedding retrieval over datasheets covers 18 documents at 72% top-1. The two things
a part record is made of are exactly what embeddings are measured to handle worst: rare exact
identifiers, and numbers with units (13 embedding models averaged 0.54 against a 0.50 random
baseline on numeric retrieval). **P39 is the cheap thing that fixes the real failure instead.**

## Parked — no design needs it yet (W14)

- **P17** an off-board part emitted as its header, not its footprint — **Needed by:** none yet.
- **P29's neighbours** none.
- **R10** a link between two designs **[PO]** — **Needed by:** the RC car's two boards, if their
  agreement is ever to be checked; the PO put it out of v1.

**The firmware horizon — parked by the PO 2026-10-01, after P60.** His direction: all three runtimes
(MicroPython, ESP-IDF, Arduino) eventually; firmware written by Claude **or a human**, tested the same
way either way, in the simulator and then by assisted deployment to real hardware; and when AI
writes it, no hallucinated API, constant or practice. P60 measured why documents cannot promise that:
the version-matched `micropython-esp32-*-stubs` 1.29.0 for the S3 and C6 both declare
`Pin.IRQ_LOW_LEVEL`, which the port's `machine_pin.c` does not define, and the C6's declares
`wake_on_ext0`, which is compiled out. **The guarantee is a check against the real runtime, never a
reference.** Each item below names what pulls it in; none is ordered.
- **F1** Arduino-ESP32 as a runtime — P36's map rendered as a header, `arduino-cli compile` for the
  exact board as the API check, a host test harness. **Pulled by:** the first design whose firmware
  is Arduino.
- **F2** ESP-IDF as a runtime — the same, with `idf.py build`. **Pulled by:** the first design that
  needs what MicroPython cannot reach (e.g. the LP core).
- **F3** The fake's API surface taken from the real firmware image — every module, function and
  constant a firmware may call, read from the build it will run on, never from stubs or docs.
  **Pulled by:** the start of P56's increment II (the harness).
- **F4** Assisted deployment — flashing, deploy and bring-up steps generated from the board record
  (which image, which port, which pin is the LED), run with a person at the bench. **Pulled by:** the
  first spark board on a bench — the bin is next (its NEXT list, item 2; P58).
- **F5** Firmware practices as checks — watchdog, a safe stop on every exit, strap pins untouched,
  driver inputs pulled down; what cannot be checked becomes a question for the reviewer's
  firmware-hardware dimension, not prose. **Pulled by:** the first firmware that drives a motor or a
  battery through spark's harness.

## Deleted — in git history, not in this list

2026-09-29: P1 (its value delivered), P7 (with `check_design`, which had made two tools of one),
P18 (`evals/` deleted), P19 (`findings.py` and its fake bench deleted), R8 (became R11).

2026-09-30, by the council, each with the reason reproduced:
**P9** — delivered by P8: every aggregation site in `check_all` now prints `subject: detail`, and
the irrigation run names `[floating-input] Ds3231At24c32RtcModule.32K`. **P30** — delivered by
P31: `sim_project.mapping_for` keys the mapping on each instance's component name, so a named
instance maps; what remains is P32's hand table. **P16** — its own need line argued against itself
("the bin has its own"), and a wake-polarity rule derived from one board's constant is that board's
knowledge. **P5** — its audit was performed by the council's verification lens; its findings are
**P34** and **P35**, which carry the need. **R2.5** — the third cold test, done 2026-09-29, still
listed open one file down (the shape of audit row D28).

## Done — one line each, the hash is the record
- **P35** — one walk over a built netlist, in `scripts/netlist.py`, where there were three that gave three different answers to one circuit. The rules checker's class is now an alias for it and the physics checker subclasses it, keeping only the two questions it alone asks; the chain's ground walk joins in P29. Identical findings on the bin and the irrigation board, so nothing moved but the code. **Minus 22 code lines.** P8's two mutations moved with the lines and now guard both callers. The seeding half of the item was split out as P45 rather than silently narrowed. 627 → 641 tests. Table sprint-6-p35 (3): caught.
- **P42** — the three-outcome rule has one home: `outcomes.status_of`, called by the six scripts that each restated it; `check_all.answer` moved to `outcomes.answer` keeping every call site and its prose; `EXIT_FOR` came alive after existing with zero callers, and `STATUS_FOR` replaced two hand-written inverses. **Minus 8 code lines, not the minus 45 the architecture estimated** — the copies were smaller than they looked, and the value is elsewhere: P34's mutation now sits in `outcomes` and guards all six callers instead of one. Three of P42's five mutations escaped first, in exit codes no test had ever asserted, and were caught by strengthening the fixtures rather than dropping them (W12). 618 → 627 tests. Table sprint-6-p42 (5): caught.
- **P34** — a check that examined nothing no longer reports a pass. The physics check built its status and exit code from problem-severity findings alone, so it answered `status: ok`, exit 0, over findings that were every one of them could-not-run; it now follows all three severities, and its renderer no longer assumes a reason it was not given. Comparing zero rules is a refusal naming what the rules file would have to say, so the RC car's `[ok] rules-vs-netlist` over zero comparisons is now `[????]`. Three mutations escaped the first run because nothing had ever called the physics check's `main`; three tests now do (W12). Table sprint-6-p34 (4): caught.
- **P41** — the safety net: eight tests for the board tool's command line, which the smart bin's Makefile calls eight ways and no test had ever entered, and ten characterisation tests pinning every `--json` payload's top-level keys and status word. 18 tests, 596 → 614. Proven by its own table: renaming one payload key, prefixing the board id, and changing what `--get` and `--resolve` print are all caught (table sprint-6-p41, 4 caught).
- **P40** — the architecture the refactor should aim at: five lenses read all 3,552 code lines and the answer is that this is not a refactoring project. `docs/2026-09-30-refactoring-architecture.md` names the two live defects reproduced (a check reporting `ok` over its own could-not-run; three netlist walkers giving three answers to one circuit), the duplication ledger, the four things that get one home, the safety net that must come first, the order, what not to touch and why, and the stopping rule. Net about −85 code lines. No code moved.
- **P33** — `/spark:init` pins tscircuit to the version the documents were measured on, and a test holds the pin and `build.md`'s example output to each other; proven by hand in an empty directory: init, `npm install`, `npx tsci build` → `Circuits 1 passed`, 15 traces, no errors (table sprint-6-p33, 2 caught).
- **R11** — research parts and modules, vendor by vendor, and keep what was found: `parts.py --need/--skeleton/--sources/--fetch/--catalog/--promote`, `/spark:research`, `/spark:identify`, the `parts-researcher` agent, the catalog (`e50717a`…`d4f6b0f`, `773cd41`, `040a66d`; proven on the irrigation controller: seven records, 18 candidates kept, every cited URL answering).
- **P28** — the tools made true: the mutate lock covers the pre-check and `apply` refuses a missing file (C8); `nets_in`, `rules_for`, `has_answers` named by tests (C9); the stranger test runs build.md's own lines (C10); the example block is a run's output and a test holds its schematic line to the example (C11); the status words come from `outcomes` in the three files that spelled them (C12); `tools/pre-push` is the versioned gate, installed with one `ln -sf` (C14). Table sprint-5-p28 (2): caught.
- **P10** — a project's own copy of a shipped board is checked against the plugin's cached vendor header instead of switching vendor-truth off: `cached_header` looks beside the board, then in the plugin (table sprint-5-p10, 1 caught; reproduced on the irrigation project first).
- **P6** — what a record demands of its host as a component is placed and wired: `host_parts` (pulldown, pullup, divider) become 0603 resistors beside the module, a divider ends the host's trace at its midpoint; the L9110S's pull-downs, the VL6180X's I2C pull-ups and the flow meter's divider are the first three; the spine asks a passive whether an end dangles instead of whether it touches ground; the generated resistors map to Wokwi's resistor. Reference: 20 traces, 18 wires, exit 0. Table sprint-5-p6 (9): caught.
- **P8** — the floating-input rule sees a pin-to-pin trace: the netlist model skipped every trace that named no net, which is how spark's generator wires every signal; a wire's traces share its connectivity key; the finding names its component and pin (I10). Proven on the irrigation board with four declared inputs and on the bin's own (`compare_design.py`, table sprint-5-p8, 3 caught).
- **P31** — a part record says how it is simulated; the spine builds the Wokwi project from the records, compiles the chips, and one irrigation scenario passes with the probe's and the flow meter's sliders set from the test (`47dbcdc`, `9a8b0e2`, `1710d94`, `dbd3c1c`; irrigation diary, late night; converter `bf9bf09` in the bin repo).

P3 `831f756` · P4 `997b756` · P11 `0c21ef5` · P12 `c4d0582` · P13 `55e7bb8` · P14 `f7674b4` ·
P15 `f35e7df` · R7 `1f769f8` + P22 `c565778` · R9 `227f5d4` · P20 `c3e2e28` · P21 `7381fed` ·
P23 `5605065` · P24 `fd25f15` · P25 `ebb8339` + `7361679` · P26 `07821a0` · P27 `7459983` ·
the cut `066c4af` · the cold test's G-items in `~/Development/rc-car/DIARY.md` · the bin's B2 and B3.

## The bin

### B1 — Identify the audio module **[PO — blocked on Petr]**
**Needed by:** the bin's audio path — four things wait on a look in a drawer. microSD slot means
DFPlayer Mini; micro-USB and "Voice Module V1.0" means DFR0534; pads marked BCLK/LRC/DIN means the
I²S amp the board now assumes.
**Value proven by:** the bin's `make check` against the module that is actually there.

### B4 — The viewer is made by `make`, not kept by hand — **PO, 2026-10-01: regenerate it via make** — DONE 2026-10-01, bin `ee2c638`
**Run after the last change:** `make board-viewer.html` → 25 parts, 60 traces, 0 routing errors,
4.3 MB; `AudioAmp` 14 times, `Mp3` and `XIAO` 0; `make -q` 0 when current, 1 after touching
`board.tsx`. All three tabs screenshotted in headless Chrome, the 3D one drawing the real GLB
through the three.js tscircuit installs. Untracked at 4.3 MB, like the bin's flash images.
**Needed by:** anyone opening the bin's `board-viewer.html`, which CLAUDE.md calls the viewer. It
shows the **XIAO** board of 2026-09-22 — two boards ago — and nothing in the repository makes it.
Found while remaking the board (bin `2367fa1`), whose schematic and PCB images had themselves shown
the MP3 board for a week: a picture nobody regenerates is a picture of the past.
**Value proven by:** `make all` rebuilds `board-viewer.html` from the current schematic, PCB and 3D
exports; it names the components the netlist has (the I²S amplifier, no `Mp3`), and changing
`board.tsx` makes it out of date to `make`.

### B6 — The documents describing the bin as it is now describe the board that exists — **PO, 2026-10-01: now, with the guard** — DONE 2026-10-01, bin `5b61e86`
**Run after the last change:** `make check` exit 0 with a new step, `docs-current`; the committed
stale documents raise 59 problems under it; a planted "Seeed XIAO ESP32-C6 with a DFR0534" line in
the README fails it. A first version excused any passage holding a history word and let the
README's headline through ("its brain was replaced: a XIAO"), so deliberate mentions are listed by
exact quote with a reason instead. The brief's `parts_on_hand` was NOT stale — the XIAO and the
DFR0534 are in the drawer — and stays; it gained the two decisions that moved the board off them.
**Needed by:** anyone reading the bin's repository, and spark's reviewers, which read its brief. The
PO opened `.spark/findings.json` and found the MP3 module in it. A sweep the same hour: the store is
dead (frozen 2026-09-24, its tool deleted 09-29) and the bin's `README.md` still calls the brain a
"XIAO ESP32-C6" with a DFR0534; the brief `.spark/project.json` lists both; `STATUS.md`'s next list
points at the deleted `findings.py` and says the bin "cannot wake at all"; `DESIGN_RULES.md` Part 2 is
a XIAO C6 checklist; `PCB_PIPELINE.md` names XIAO, MP3, OLED; a `vl6180x.py` docstring reasons with
the C6. The board changed twice in a week and the code was swept; the prose was not.
Out of scope, already tracked: the firmware README's bench steps (P58), `SHOPPING.md` and `BOM.md`.
**Value proven by:** the dead store is gone; each listed document describes the FireBeetle S3 and the
I2S amplifier; and `make check` fails when a retired part name (XIAO, DFR0534/Mp3, TB6612, OLED,
VBAT) appears in a current-state document on a line that does not say it is history.

### B7 — The bin's CI runs, or says why it cannot — **found 2026-10-01, the PO's call** — DONE 2026-10-01, the token-free half (bin `f4e6bf5`, `d1ca1aa`)
**The PO's rule: no token on GitHub, in the code or anywhere.** So without spark the Makefile reads
the board's facts from the committed resolved board and SKIPS the checks that run spark's own
scripts — named in the log, raised as warnings on the run, and in the last line. **CI green on
`f4e6bf5` and `d1ca1aa`, the first since 2026-09-23**, with six skip warnings (board contract
twice, vendor pins, BOM twice, physics) and 113 tests, the compiler, pins, simulation and documents
really run. With spark present `make check` is unchanged (zero skips). **Left for when spark is
public:** check it out beside the bin in the workflow, no token, and the skips go.
**Needed by:** the bin's public repository, whose CI has failed on **every push since 2026-09-24**
(25 runs; last green 09-23) while STATUS.md said "CI green on every push". Each run dies at the
first step: `python3: can't open file '/home/runner/Development/spark/scripts/boards.py'`. The
Makefile calls spark at `$(HOME)/Development/spark`; CI checks out only the bin, and spark is
private. Options for the PO: a token with read access to spark as a repository secret, and a
checkout step; or wait for spark to be public (P61's ruling), then check it out plainly.
**Value proven by:** `gh run list` shows the bin's next push green, or the workflow says in its own
log that it skipped the spark-dependent steps and why — never a red run nobody reads.

### B8 — A firmware test failed once and was never caught again — **found 2026-10-01, unordered**
**Needed by:** the bin's commit gate, which is only trusted while it never fails for nothing. A
local no-spark `make check` failed at `firmware-tests` once; the same suite then passed 31 of 31
times alone and the rehearsal 4 of 4 — one failure in 36 runs, and the failing test's name was not
kept (the output went through `tail -1`). The suite runs real asyncio with real sleeps, so a test
racing the scheduler under load is the likely shape; unproven.
**Value proven by:** the failure reproduced and named — e.g. the suite run 200 times under CPU load
with every failure kept — and the test fixed so it cannot race; or 200 clean runs recorded.

### B5 — A derived file in git is checked current, or not kept in git — **from R8.2, unordered**
**Needed by:** anyone reading the bin's repository: its `board-sch.svg` and `board-pcb-routed.svg`
showed the MP3 board for a week after the board changed (remade in bin `2367fa1`), and nothing
noticed. Tracked and derived today: `board-sch.svg`, `board-pcb-routed.svg`, `board.glb`,
`board-gerbers.zip`, `sim/diagram.json`, `.spark/board.json`, `firmware/micropython/smartbin/board_spec.py`.
Two are already checked (`diagram-current`, `board-spec-current`); the rest are not.
**Value proven by:** changing `board.tsx` without regenerating makes `make check` fail on each export
still committed, or that export is untracked and made by `make all`; a timestamp-only difference
(the gerbers regenerate with new dates) is not a failure.

## Proposed 2026-09-30, unordered — the PO asked what we get wrong and how to stop it

Each from evidence in this repository rather than from good practice in general. **None is
started** (W19); the order is the PO's (W11). P48 was ordered and done the same day.

The last two came from a second question — whether the tests, mutations, gates and bash this desk
runs should be agents or skills. Most of the answer is **no, and the PO has already given it**:
the cut of 2026-09-29 deleted the scrum-master, verification-engineer and firmware-engineer agents
with the reason *"my working process shipped as product; nothing routed to them."* That reason
still holds. What survives the test — isolation, restricted tools, fan-out, or context budget — is
one script and one agent, below.

### P48 — The words this repository uses are written down somewhere a stranger finds them — DONE 2026-09-30
**Needed by:** the v1 line itself — "a stranger goes from a requirements file to a built, checked,
simulated board an engineer would accept as a draft" — and by the PO, who asked on 2026-09-30 what
a mutation, an anchor and a gate are. Six sprints built a private vocabulary: mutation, anchor,
re-anchor, caught/escaped/refused, the gate, the three outcomes and the fourth word, the spine,
fixture, characterisation test, cold test, the budget, orphan, needed-by, verified, stand-in,
catalog. Every one is used in the README, the skills, the scripts and the agreements as though it
were ordinary English. None is defined. The person most likely to need them is the one who has
read none of the commit messages.
`GLOSSARY.md` at the root, one entry per term, each with the failure that produced it rather than
a definition in the abstract — the same standard as the working agreements, because a word without
its scar is not memorable. Linked from the README so it is not a document nobody opens.
**Value proven by:** a test fails if the glossary defines a word this repository does not use, or
if the README stops linking it; and the PO's own question — what is a mutation, an anchor, a gate
— is answered by the file.

### P49 — One command runs this repository's own gate
**Needed by:** this desk, measurably, in the session of 2026-09-30. The suite was run with the
wrong `-t` flag and gave an ImportError; files were read twice while a mutation run was still
rewriting them, and from that reading this desk concluded a killed run had corrupted the tree —
it had not, a run was simply still alive; and the line budget and the anchor check were run ad
hoc rather than always, because both are remembered rather than demanded. `spark` has no Makefile
and every gate command is typed by hand in an order held in someone's head.
**Refined smaller by the hardware lens, and it is right: this is not a new runner, it is
`--working-tree` on `tools/check_commit.py`**, which already runs the suite and every anchor before
each push. The flag adds: refuse while `.mutate.lock` is held, naming the process that holds it;
print the code budget against its ceiling; answer in the three outcomes. Nothing is copied — that
is what P46 was about. One runner, two callers: the hook asks it about the COMMITTED tree, a person
asks it about the working tree. Effort S, not the script it was drafted as.
**Value proven by:** every number in a commit message comes from one invocation of it, and an
invocation started while a mutation run holds the lock refuses instead of reporting.

### P50 — An adversarial reading of what the tests would not notice — **KEPT by the PO 2026-10-01**
**The PO declined to delete it** when the scope lens proposed it, and the rule supports him: P50 is
**unbuilt**, so keeping it costs one line in this file, its need is reproduced (five mutations
escaped because one desk wrote both the fix and the test meant to catch it), and its kill criterion
is already written. The lens was arguing about its SHAPE, not its necessity — a judgement better
made after one attempt than before it.
**The verification lens was the isolation this item asks for** — it wrote neither the fixes nor the
tests — and it found **six real escapes on a green suite** in one pass. So isolation pays. But it
did not pay the way this item predicts, and the item as written is gameable three ways:
its escapes live in code **no Sprint 6 item touched** (`flash_image`, the catalog, the agents),
while this item scopes the agent to the finished item's diff, which is where the desk's own table
already saturates; what actually found them was **a query, not an agent** — *which files appear in
no mutation table?*, ten lines of Python; and its acceptance line is an **open-book exam**, because
the three P45 escapes it asks the agent to rediscover are written down in `scrum/SPRINT.md`, which
any agent with `Read` can read. W20 is the rule that catches exactly that.
**So: the query becomes P54, and what stays here is the once-per-sprint-close adversarial pass
aimed at the unmutated list — with the kill criterion verbatim.** The original text follows.
**Needed by:** five escaped mutations in one day — one in P29, three in P45, one in P48 — each a
hole this desk could not see **because it wrote both the fix and the test that was meant to catch
it**. Mutations written by the author are written to be caught; that is the blind spot, and it is
the textbook case for isolation, which is the only thing that earns an agent its place here.
An agent given the diff of a finished item and its test files, and NOT the reasoning that produced
them, asked for one thing: changes to this code that the suite would not notice. Read-only tools,
output a mutation table.
**Its output cannot lie, which is what makes it different from the reviewer agents.** A finding
from a reviewer needs adjudication — the v1 close audit made 33 claims and 11 were false. A
proposed mutation is *executed*: a wrong anchor is refused, and a real one is scored caught or
escaped by `mutate.py`. The agent cannot cost anyone a false alarm; at worst it costs a minute.
**Kill criterion, stated up front:** if across three items it produces no escape that this desk's
own table did not already contain, it is deleted, on the same reasoning as the 09-29 cut. Written
into the item so the experiment ends rather than lingering.
**Value proven by:** run against P45 as it was first committed, it proposes at least one of the
three mutations that escaped there — with the escapes already known, so the answer is checkable.

### ~~P47 — The same number is never written twice~~ — **DELETED 2026-09-30, unbuilt**
Proposed in the morning, cut the same afternoon, and the cut is right for a reason nobody had
first. **Two lenses disagreed and both were wrong on the count**: the hardware lens said no number
appears in two scripts, the verification lens said six with about three exceptions. Measured — every
non-trivial numeric literal in `scripts/`, by `ast`:

> **44 distinct, 8 in more than one script, and all 8 are coincidences.** `1e6` is microfarads, an
> I2C bus-speed key, and megohms. `1000` is a rise time in nanoseconds, a minimum pull-up in ohms,
> and a kilohm threshold. `4` is a gap in millimetres, a rounding precision, and 4 MB of flash.
> `25.0` is a watch distance and a default module width. `300`, `60`: a timeout and a dimension.
> `400`, `200`: a string slice and an HTTP status.

Not one is duplicated **data**, so the exception list would be all eight — a ledger of exceptions
with a test attached, which is noise that has to be maintained. P46 already ships `test_no_script_restates_a_number_the_file_holds`, which guards
the actual data. If a copy returns, extend that. This is the AI-bloat shape: a test about code
shape, written because one review missed something once.

### ~~W20 (proposed)~~ — **ADOPTED, and this copy deleted 2026-10-01**
It lives in `scrum/WORKING_AGREEMENTS.md`. A backlog carrying the proposal text for an agreement
already in force is two statements of one rule, which is what W16 exists to stop.

### ~~W21 (proposed) — A number that has not been run is marked as a guess~~ — **MERGED into W13**
**Needed by:** `docs/2026-09-30-refactoring-architecture.md`, whose estimate table a reader cannot
tell from its measurements.
The hardware lens is right that this is not a second agreement. W13 already says a number enters a
message only after its output is read; this is the same rule about plans, so it is one more clause
on W13, not a rule of its own. Two agreements saying "do not write a number you did not run" is
exactly the duplication this team deletes code for. Evidence it is needed at all: P42 was estimated
at −45 code lines and measured −8, P35 at −40 and measured −22, P29 at +20 and measured +22.

**Still unwritten, from before the compaction:** the layer-rule test — a command may import a
library, and a command importing another command must be listed with a reason. Mentioned to the
PO, never made an item, so it is named here rather than lost.

## Intake, not backlog

Observer claims arrive in `docs/observations/INDEX.md` and leave by being reproduced or rejected;
a claim becomes work only by promotion here, with its need named.
