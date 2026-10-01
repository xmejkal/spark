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

### P33 — The documented setup must build the documented example — **REOPENED 2026-09-30**, its proof line fails
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

### P54 — The suite cannot pass by asking the code to confirm itself
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

### P55 — The catalog is knowledge, so something must read the real thing
**Needed by:** the 35 research records in `catalog/`, which are the product's actual accumulated
knowledge and are asserted by nothing. All six catalog tests mock the directory away
(`mock.patch.object(parts, "CATALOG", …)` at `test_parts.py:721, 738, 754, 767, 778, 793`);
`test_parts.py:617` walks `parts/` and **nothing walks `catalog/`**. The verification lens flipped
`module_has_i2c_pullups` to false and set `i2c_pullup_ohms` to 1 MΩ in a shipped record and **both
escaped a green 692-test suite.** Per P45's own story, that first field is what decides whether a
bus gets pull-ups at all — so the field that drives the rule is in a file no test reads.
**Value proven by:** setting a shipped catalog record's `module_has_i2c_pullups` to the wrong value
turns the suite red.

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

### P52 — A rail states what it carries, from the records that know
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
**Value proven by:** on the RC car the two servos' stall currents are summed against the buck's
rating and reported; on the irrigation board the soil probe is named as the one load nobody has
stated, instead of the rails being empty.

### P53 — The rules reach a project that already exists — DONE 2026-09-30
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

### P36 — The pin map is a file the firmware imports
**Needed by:** the irrigation controller's firmware — twelve GPIO numbers are typed into
`firmware/main.py` by hand and a thirteenth into `sim/scenarios/wet-and-dry.scenario.yaml`, and
nothing compares any of them with the assigner's output; they agree today by luck. The bin needed
121 lines of its own checker to police the same copy.
`assign_pins --emit-pins <file>` writes the map as constants a firmware imports, each with its
signal name, its pad and the reason the pin was chosen.
**Value proven by:** the irrigation firmware imports the generated file and its scenario passes
unchanged; a test asserts every signal the design has appears exactly once in it.

### P37 — What this simulation cannot show, printed — DONE 2026-09-30
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

### P50 — An adversarial reading of what the tests would not notice — **REWRITE, says the lens that IS it**
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

### W20 (proposed) — An item's acceptance line is a hypothesis until reproduced
**Needed by:** P45, which this nearly broke today, and every item whose proof line is written
before the state it assumes has been looked at.
W9 says that about an OBSERVER's claim. It does not say it about our own, and today that cost a
false alarm's worth of design: P45's "Value proven by" line said `init` should write the DS3231's
two bus lines, and that module's own record says "Add NO pull-ups: the module carries 4.7 k on SDA
and SCL." Meeting the criterion as written would have shipped a check that fires on a correct
board. The rule: before an acceptance line is relied on, reproduce the state it assumes — or mark
it unverified, the way a part record marks a fact nobody has confirmed.

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
