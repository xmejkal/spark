# Product backlog

The single ordered list. If work is not here, it is not happening. **Order is the Product Owner's**
(W11). Every open item names the design that needs it (`**Needed by:**`, W14) and a
`**Value proven by:**` command whose output Petr can read; an item that cannot name both is not
pulled. The suite refuses a backlog with an open item missing its need line.

**The order lives in `STORY_MAP.md`; who it is for and what v1 means, in `VISION.md`** — both
confirmed by the PO on 2026-10-03 (P69). Every open item below sits on one of the map's slices, or
is parked or deleted; the suite fails on one that is not placed. The council table of 2026-09-30
that used to stand here was stale by its own header and is in git history.

## Items

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
**Done** (`71a244d`, `91bb9ba`), and the cause was worse than this item said. `@tscircuit/cli`
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

### P62 — A record points at the exact source it rests on, and the file is found before it is fetched again — **SPLIT into P62a and P62b, both DONE**
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

**Refined 2026-10-02 by a council lens and the PO — SPLIT into P62a and P62b below.** Reproduced:
the catalog holds **48** vendor files (16 PDF, 29 JPG, 3 WEBP — the earlier "45" left out the WEBPs);
`grep -c pdf` would read 0 with 32 images still in git; `--kept` does not exist; no spark record
points at the WROOM v1.1 datasheet and nothing can fetch it — it exists only as the bin's file, so an
IMPORT step is needed; the board records hold 0 keepable URLs. And a bug two lenses found
independently: `cited_urls` (parts.py:769) iterates a dict-shaped `sources` by its keys and accepts a
source only if it STARTS with http, so `--sources`/`--fetch` see **0 URLs in all 8 library and board
records** (`parts.py --sources dfr0534-module` says "cites no URL"; the record holds 2).
**PO, 2026-10-02: the store lives at `~/.local/share/spark/sources/<sha256>/<file>`.** Its backup is
the PO's machine backup; on another machine a pointer reads MISSING until re-fetched.

### P63 — A fact this project wrote down wrongly is corrected where a conversation will read it — DONE 2026-10-01
**Spark `ac2e86f`, the bin `62a3139`.** Every correction reproduced at source before the edit (W20).
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

### P64 — Every claim spark ships is checked against its source by someone who did not write it — **SPLIT into P64a, P64b and P64c**
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
P63 has not yet removed it (run against `91e89ff`'s tree if it has).

## Seeing the board — the PO's request of 2026-10-01, all four chosen and ordered the same day

The PO: *"I'd like to have the viewer accessible when working with the plugin … both the schema and
circuit to 3d model, but also the wokwi simulator. Is there a nice way to show them?"* Found the
same day: tscircuit ships a live viewer (`tsci dev`, every spark project has it); the bin's
`tools/build-viewer.py` makes an offline page from the exports (B4); the Wokwi VS Code extension
is installed here, and wokwi.com/pricing lists "Wokwi for VS Code" from **Hobby+** up, which the PO
does not hold or is unsure of — so it is documented, not tried.

**Refined 2026-10-02 by a council lens and the PO — SPLIT into P64a, P64b and P64c below.** Reproduced:
217 of 270 holds exactly, but points the wrong way — the catalog's 200 verified facts all cite a URL;
the **36** failing fields are in the 6 library records and the FireBeetle's `power.*`. The mechanical
check would NOT have caught ALL_LOW: none of the library's 19 `host_requirements` cites anything, so
the false one looked like the other 18 — and `emit_board` copies them verbatim into every generated
board, which is how it spread. **Needed by (W14, corrected):** every design that reads the library —
the bin, irrigation and the RC car all received the false sentence through their generated boards.

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

### P66 — Every build writes a viewer page — **PARKED 2026-10-03 by the story map**: `tsci dev` already shows the board where you work (P65); pulled back the day someone opens it and the board does not render
**Needed by:** the PO and anyone the board is shown to. The bin's generator (B4) moves into the
plugin as `scripts/viewer.py`; `/spark:build` writes `board-viewer.html` beside the board; the bin's
Makefile calls the plugin's copy and its own is deleted (W16). It needs the SVG and GLB exports,
which the chain does not make today — say what that costs in seconds before deciding where it runs.
*Estimate* ~100 code lines against ~146 left of 4,000: the budget is the constraint, measured first.
**Value proven by:** in a fresh project, the one documented command leaves a `board-viewer.html`
whose three tabs render (headless Chrome screenshot); the bin's `make all` builds its viewer through
the plugin's script.

**Refined 2026-10-02 (council lens, measured):** the chain exports nothing today; the bin's generator
built irrigation's page unchanged in 0.04 s (2.7 MB, all three tabs rendered headless, title still
"Smart Bin Board" — hard-coded). Exports from the BUILT circuit take ~1 s each and are byte-identical
to exporting `board.tsx`; for the bin they are byte-identical to its committed exports. Design:
`scripts/viewer.py` exports from `circuit.json` into a temp dir, writes `dist/board-viewer.html` only
under `--keep`, never changes the chain's verdict ("viewer not written: why"), titles the page from the
project, and answers `#pcb` / `#3d`. The bin's `make board-viewer.html` calls the plugin's script, its
own three files are deleted (W16), and without spark `make all` says SKIPPED for the viewer.
**Value proven by (corrected):** in a fresh project `check_spine.py requirements.json --keep .` writes
`dist/board-viewer.html` and headless screenshots of `#schematic`, `#pcb`, `#3d` show the board; with
three.js absent the verdict is unchanged and the reason printed; in the bin `git ls-files tools | grep
-c viewer` → 0 and `make board-viewer.html` runs the plugin's script.

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

### P68 — The viewer can be opened anywhere — **PARKED** with P66, which it builds on
**Needed by:** P66's page, away from the machine that made it. After a build the conversation
offers — never does unasked — to publish the viewer as a private Claude artifact; the PO decides
each time, because publishing is outward-facing. Depends on P66.
**Value proven by:** `commands/build.md` carries the offer and its condition; one publish of the
bin's viewer, with the PO's yes, returns a link that renders the three tabs.

**Parked by the PO, 2026-10-02:** its premise is untested — a published artifact may block the 3D tab's
`data:` modules (the CSP allows scripts from five CDN hosts). One private test publish settles it;
the PO said not now. Until then P68 is not an item, only a question.

### P69 — A roadmap with milestones, and the backlog reordered against it — **DONE 2026-10-03**
**Needed by:** the PO — *"let's review what the roadmap is, reprioritize the backlog, let's finish
open, have the team do that so we have clear milestones and let's go."* The backlog holds about a
hundred headings across nine sprints of history, done items beside open ones, proposals beside
parked ones; Sprint 9 is half-started. Nothing names the milestones between here and a spark a
stranger installs and a bin that works.
**A council question, then the PO's order (W18, W11).** Lenses: an inventory of every open item and
its real state; milestones with exit criteria a command can prove; and a W14 pass — what no design
needs is parked or deleted.
**Value proven by:** `scrum/ROADMAP.md` names each milestone, its exit criterion and the items in it;
every open backlog item is in exactly one milestone, parked, or deleted; and the PO has ordered it.
**Refined 2026-10-03 by the PO, after the three lenses reported:** the roadmap is not written from the
backlog but from a **discovery council** — *"so we can be sure we're actually developing prioritized
and thought-through needs and scenarios … and we don't do bloat just because we can."* It produces a
vision with non-goals, two or three personas (each marked evidence or hypothesis), and a story map:
the journey as its backbone, a persona's steps under it, horizontal slices that ARE the milestones,
and per slice the scenarios that prove it with a command or a bench log. The new rule it brings: an
item that hangs on no cell of the map is parked or deleted. The lenses' reports are its input.
**Value proven by (replaces the line above):** `scrum/VISION.md` and `scrum/STORY_MAP.md` exist; every
open item sits on one cell and one slice, or is parked or deleted with a reason; the PO has confirmed
the personas and ordered the slices.

### P70 — The backlog lives in GitHub Projects — **the PO's decision of 2026-10-03; after P69**
**Needed by:** the PO, who plans and reorders the work and wants a roadmap view rather than a
1,200-line file; and P69's story map, whose slices need a place to be ordered.
Chosen over Jira: `gh` already works here, and the issues live beside the code they change, so a
check can read them with GitHub's own credentials and no stored secret (the PO's rule: no tokens on
GitHub). One user-level project spans spark and the bin; fields carry *Needed by*, *Value proven
by*, slice and size; iterations are the sprints. Only the revalidated items move, never the raw file.
After the move the Markdown backlog is frozen as the archive, with a pointer, and holds no order or
status (W16: the replacement deletes what it replaces). W14's test reads the issues instead.
Needs the PO once: `gh auth refresh -s project`.
**Value proven by:** `gh project item-list` lists every open item with *Needed by* filled; the frozen
file states it is the archive; `test_orphans`' W14 check runs against the issues and fails on one
without *Needed by*.

**Done 2026-10-03.** The council ran four lenses (vision, personas, story map, skeptic) on top of
the three of the morning; the PO chose: **the hobbyist is the primary persona** (a hypothesis, until a
real outsider tries spark); fabrication is later, **pulled by the bin once its first copper passes**;
the process takes **all three cuts** (P72); bench and firmware-on-a-Mac first, and the repository
public now (P71). `VISION.md` and `STORY_MAP.md` hold it; `test_orphans` fails on an open item the
map does not place. Found on the way and fixed the same day: B9.

### P71 — spark is public, and a stranger can install it — **slice 1** — DONE 2026-10-03
**Needed by:** the hobbyist, spark's primary persona, for whom the README's first line —
`/plugin marketplace add xmejkal/spark` — fails while the repository is private; and slice 5's real
outsider, who cannot start before it.
**Audit of 2026-10-03, all 221 commits:** no secret — the only token-shaped strings are two `wok_...`
placeholders in documentation; **48 vendor binaries**, all under `catalog/`, first added 2026-09-29
(`773cd41`) and untracked since P62a, in 88 commits that a rewrite changes; no LICENSE file, though
the manifest says MIT; five tracked files name `/Users/` (P44). An in-place force-push can leave the
old commits reachable by their hashes on GitHub, so the history is published as a repository that
never held the files; how is the PO's.
**Value proven by:** `gh repo view xmejkal/spark --json visibility` says PUBLIC; `git clone` of it with
no credentials succeeds in an empty directory; in that clone `git rev-list --objects --all` lists no
`.pdf`, `.jpg`, `.png` or `.webp`, and `git grep -l /Users/ -- commands skills agents` finds nothing.
**Done 2026-10-03, the PO's choice of three:** today's repository renamed `xmejkal/spark-archive` and
kept private (the full record, the 48 files, the old hashes); a copy filtered with `git filter-repo`
pushed as a new `xmejkal/spark` — never holding the files — checked from a fresh clone of GitHub, then
made public. Run after the last change: `gh repo view` → `PUBLIC`; a clone with an empty `HOME` and no
credential helper succeeds; in it, 0 binaries in `git rev-list --objects --all`, 0 secrets in `git log
-p`, 0 files under `commands/ skills/ agents/` naming `/Users/`, a LICENSE; 227 commits, the tree
byte-identical to the archive's, 36 MB → 1.4 MB. 90 commits took new hashes; filter-repo rewrote those
in commit messages and one commit remapped the 77 cited in the record files. The README's install line
run against an empty `CLAUDE_CONFIG_DIR`: the marketplace added, `spark@petr-local` 0.6.0 installed
and enabled. Found on the way: B10, and P75 (irrigation's photos carry GPS).

### P75 — A photo spark keeps does not say where it was taken — **slice 1** — DONE 2026-10-03
**Needed by:** the hobbyist, who photographs modules at home with a phone for `/spark:identify` — and
irrigation, all five of whose photos (iPhone, 2026-09-29) carry a GPS block with latitude, longitude
and altitude, found while auditing its history for publication. The bin's five images carry none.
`parts.py --keep` and `--fetch` store an image as it came; a person who commits it, or a store that is
ever shared, publishes the place.
**Value proven by:** `parts.py --keep` on a JPEG with a GPS block stores a file with none (EXIF tag
0x8825 absent) and says so; a test with a fixture photo, and its mutation caught.
**Done 2026-10-03.** `parts.without_location` empties the GPS block in place — every value zeroed, the
entry count 0, nothing else in the file moved — and the store applies it to every JPEG; `--keep` says
so on stderr, keeping its stdout pasteable JSON. On irrigation's five real photos: 15 GPS entries → 0
each; of the nine multi-byte values per photo, none remains except GPS speed `0/1`, whose eight bytes
also occur by chance in another EXIF structure in two of them; no XMP GPS text. Mutations
`sprint-10-p75.json`: 5, all caught. (The tag is emptied, not deleted: a reader shows an empty GPS block.)

### P76 — From a vague idea to a block-level schematic, by conversation — **slice 1b; the PO's direction of 2026-10-03**
**Needed by:** the hobbyist, spark's primary persona, who arrives with an idea in words and no list
of modules — while every spark command today starts from a requirements file or a module someone
already chose. The PO: *"really from just talking about some vague idea … without specific parts,
just what it does, like an MP3 player module."*
Not yet designed: how the conversation runs, what it writes, where it hands over to `/spark:build`,
and what of the catalog it can offer are for a brainstorming session with the PO before anything is
built (W14: the item exists, the design does not).
**Value proven by:** to be written with the PO — at least: a one-sentence idea becomes a file naming
the functions, the kind of module for each, and a block diagram with no part numbers, which the
existing chain then accepts once parts are chosen.
**The PO added, 2026-10-04 — store first, and several ways in:** *"at first when ideating a diy project,
it would consider general requirements and options, only then propose existing stored parts or modules
or boards and look for new ones only when we don't have a similarly working thing in the store
already."* And: *"more scenarios should sooner or later be possible, like I want to use this module I
already have, let's come up with ideas on projects that would use it, or I want to do a diy project that
does something, based on that we then decide what parts we use, or I want to combine these 3 modules I
have, let's come up with ideas, or other useful scenarios."* The ways in, as discussed: **goal first**,
**module first**, **a combination**, **the whole drawer**, **revive** a dead device, **swap** a part,
**extend** a project. They share one core — the store (P94) and the drawer (P93) — and differ in where the
ideas start.

### P77 — Every example is regenerated with today's spark, its scenarios rerun, its steps written down, its old files gone — **the PO's question of 2026-10-03; a council answers, then acts**
**Needed by:** the hobbyist, who learns spark from its examples — and spark's own claim to work. The
PO: *"All of the examples are I think to be fully regenerated to make sure it really works, test all
the scenarios again, and also the old examples are full of old files and we just really want to have
good up to date example projects"* — *"and to document the steps, to be a good example."* — *"All
example projects should also be examples of different scenarios: the irrigation, going really from
idea in words; the bin is special because we start with extra debugging, so to say, and then create
the replacement, etc."* Each example shows a different kind of journey. The
examples were made by older spark (irrigation and the RC car before Sprints 6–9; the bin's board by
hand) and keep outputs of their time (irrigation's `check-all*.txt`, `emit-notes.txt`). Irrigation's
publication (`spark-example-irrigation`, PO-approved with its photos GPS-free) is held for this.
**Value proven by:** written by the council with the PO — at least: each example regenerated from its
requirements in an empty directory with the published spark, every scenario rerun with its output
kept, the steps written down so a reader can repeat them, and no file left that today's spark would
not write or the steps do not explain.

### P78 — An LED is a part, and its series resistor is placed with it — **slice 4; found by the PO 2026-10-03, building the quickstart**
**Needed by:** the quickstart the PO built step by step — offered a status LED as a bare `signals`
entry, he asked: *"Why would the LED hang in the air? Shouldn't there just be some LED and maybe some
pull-up or something?"* — and irrigation, whose `STATUS_LED` ends `check_spine` in `!!`, and the bin,
whose bicolour LED and its resistors exist only because a person drew them. No LED record exists in
the library or the catalog, and a record can ask the board only for `pulldown`, `pullup` or `divider`
(`parts.HOST_PART_KINDS`): a current-limiting resistor in series is none of them.
**Value proven by:** a requirements file listing an LED builds with the LED and its series resistor
wired GPIO → resistor → LED → GND, the resistor's value computed from the LED's forward voltage and
current and the board's logic level and printed with that arithmetic; irrigation's `STATUS_LED`
becomes that part and its `check_spine` stops ending in `!!`.
**Generator half done 2026-10-03:** `host_parts` kind `series` — the host's trace ends at the resistor,
the resistor's far end at the pad — with either `ohms` or `for_current_ma`, from which the value is
computed: (the board's `power.io_volts` − the record's `facts.forward_voltage_v`) / current, rounded UP
to E12, the arithmetic printed in the board file (*"(3.3 V - 2 V) / 5 mA = 260 ohm; next E12 value up:
270 ohm, about 4.8 mA"*); the simulation diagram gets the same value; a missing fact or an LED the pin
cannot light is refused by name. The FireBeetle states `io_volts` 3.3, cited to the kept WROOM-1 v1.1,
Table 9, page 14. Mutations `sprint-10-p78.json`: 9, all caught. Open: the LED record (being
researched — through-hole, after the PO's breadboard direction, P79) and the acceptance line.

### P79 — A breadboard first, the PCB only once the circuit and the firmware work — **slice 7; the PO's direction of 2026-10-03**
**Needed by:** the hobbyist, and the PO building the quickstart: *"we should definitely add a
breadboard phase, before the user decides to go for a PCB — first allow using a breadboard, and so no
SMD parts, right? Only later, when the circuit is tested and the firmware good, we offer the PCB."*
Today spark's only output is a PCB: every passive it places is an 0603 SMD resistor, and nothing
tells a person which wire goes from which module pin to which GPIO. The PO, a moment later: *"or we
can also offer a perfboard step"* — a soldered, permanent build of the same through-hole parts,
between the breadboard and a PCB — and the order, in his words: *"breadboard / only connected by wires
→ perfboard → PCB"*. An overview, not a process —
designed with the PO before anything is built (W14).
**Value proven by:** written with the PO — at least: the quickstart, as a through-hole parts list and a
wiring table a person can build on a breadboard, its firmware run on it, before any PCB is offered.

### P80 — Parts research is lean and professional — **slice 4; the PO's request of 2026-10-03**
**Needed by:** every design that researches a part — the hobbyist pays for each agent's tokens and
time — and the PO: *"Please make sure the parts looking up agent and skills are not wasteful and are
professionals."* Nothing measures what one researched part costs (tokens, tool calls, pages fetched,
minutes), nor scores what it produces against how an engineer would source a part.
**Value proven by:** the LED researched for the quickstart on 2026-10-03 measured — tokens, tool calls,
fetches, minutes — and its record reviewed against a written professional bar (the maker's datasheet
cited by page and table, the exact orderable part number, every unverified fact said so, no candidate
records nobody will read); `agents/parts-researcher.md` and `commands/research.md` changed where either
falls short, and the next researched part measured against the first.
**Council of 2026-10-03 (four lenses: cost, lean design, professional bar, skeptic), and the PO's
decisions.** Measured from the harness's own transcripts of all 16 research runs: the full protocol's
median is 78 tool calls, ~5.0 M tokens processed, ~25 min; the lean brief for the L-7113ID took 19
calls, ~0.55 M, 148 s. Seller listings were half the calls of commodity runs and the design used none;
47 of the store's 91 documents belong only to candidates nobody chose; whole datasheets entered early
are paid for on every later turn — the needed pages are 13 % of the LED's and 2 % of the WROOM's text.
**The PO chose:** (1) **build** `parts.py --read` (stream a kept datasheet page by page, stop when every
wanted fact has a table row, print page, line and locator) and two small agents — `part-finder`
(Haiku: maker-site searches only, at most two candidates with the datasheet URL, writes nothing) and
`datasheet-reader` (Sonnet, no web: fills the record from `--read`, every fact cited) — with
`parts-researcher` kept for modules and photos under a budget, and `/spark:research` routing between
them; reuse first (project, library, catalog, the store — including documents no record cites —
then the network); no seller listings during research. (2) **Shrink** his catalog rule: a candidate
gets a catalog record only when its datasheet was kept — identity, document, why not, no typed facts;
one seen only in a search is a line in `alternatives`. (3) **Wire the MCP servers that help** —
jlcpcb's parametric search to `part-finder`, espressif-docs to `datasheet-reader`, measured with and
without — revising his "CLI over MCP" rule for these two on measurement; sigrok parked until the
bench; kicad and wokwi removed (spark drives tscircuit and wokwi-cli itself). The professional bar's
mechanical checks (M1–M10: identity, a page for every verified fact, conditions and statistic per
number, a worst-case limit for a series resistor, a host pull its record's own fact defeats) are the
next increment, with B11.
**The data council of 2026-10-03 (W21) set the order and narrowed what research gathers:** warnings
first (P81), then these agents — whose per-kind fact list is now "what a decision reads": no seller
listings, no sub-chip datasheet unless a listed fact needs it, a worked example record in
`part-data.md` (schema-learning was 12 % of research calls) — then the clean-up (P83).
**Built 2026-10-03:** `agents/part-finder.md` (Haiku; maker-site searches only, at most two
candidates with the datasheet URL, never a distributor fetch or a guessed URL, writes nothing; jlcpcb's
`component_search`) and `agents/datasheet-reader.md` (Sonnet; no web; `parts.py --read` first, a page
opened whole only for a drawing or a LABEL ONLY; every fact cited; espressif-docs for ESP32 facts);
`/spark:research` routes a commodity part to them with a fact list per kind, and modules and photos to
`parts-researcher`, which now carries W21, reuse first, a budget of 8 searches and 12 fetches, slim
candidates and no seller listings. The LED is promoted into the library and is `part-data.md`'s worked
record. `claude plugin details` loads them: part-finder ~640 tokens, datasheet-reader ~790, against the
researcher's ~2.6k. MCP: `.mcp.json` declares only jlcpcb and espressif-docs, both answering
`tools/list` today — espressif-docs only on Node 20+ (`mcp-remote` fails on 18 with `File is not
defined`, which is why it never connected); `docs/mcp.md` offers wokwi and sigrok as one-line additions
and says why KiCad's PyPI server is not offered. **Open:** use them — after a Claude Code restart, the
next part researched through finder and reader, measured against the lean run (19 calls, ~0.55 M, 148 s).
**First use, 2026-10-03, after the restart:** the quickstart's 4×AA holder. `part-finder` (Haiku): 14
calls, 91 s, ~0.17 M tokens processed (`tools/research_cost.py`) — but it broke its budget (6 web
searches and 7 `component_search` calls against "at most three"), returned the PC-pin variant's
number (2477) for the wire-lead need (2478), and stated "rated for 0.8 A continuous", the motor
driver's figure from its own brief; the maker's page states no current. Checking its claims against
the document before the PO picked caught both. Then the PO: *"the bin lid has already a holder for the
AA batteries, we don't need that"* — the need was not real. Fixed the same hour: the finder's three
rules (budget a hard stop, no number not printed, the variant's own part number) and research's first
question — does the person already have one. The reader is not yet exercised on a real need.

### P81 — A warning that can cause a wrong board is shown where the decision is made — **slice 2, first; the PO's order of 2026-10-03**
**Needed by:** every design the hobbyist builds on a breadboard, where the person is the check — and
the data council's finding that the warnings which protect a board live in prose no output prints,
while the generated board file is 90 % copied comments. Live cases: irrigation's 12 V jack — *"Reversed,
the adapter's 12 V lands on board ground"* — in a `//pin_order` note that `--show`, `--unverified` and
the board file all omit; the L9110S's own 10 k pull-ups against spark's 10 k pull-downs (B11); the
irrigation DS3231 record, whose prose pin order describes the 4-pin board and whose typed `pin_order`
is the 6-pin ZS-042 — following the prose puts SCL on the 32K pad. And `pin_order`, the field where a
mistake reverses a supply, is the one fact the validator asks no proof for.
**Value proven by:** `parts.py --validate` refuses a `pin_order` without a typed source (verified, where
read, a page when it is a kept document); each of the three live warnings is printed by `--show` or
by a check with its arithmetic, and the DS3231 record no longer contradicts itself; mutations caught.
**Increment 1 done 2026-10-03:** `parts.validate` refuses a `pin_order` without `pin_order_proof
{verified, source[, cites]}`, and `--unverified` lists an unverified pin order with why it matters.
The 18 records in use migrated in the same change (W16) — each `//pin_order` note became the proof,
its hazards became `host_requirements` that `--show` and the board file print: the JST inlet's crimp
order, the amplifier's missing pad-1 marker, the 12 V jack's meter check before wiring, the LED's long
lead, and the RC car's buck, servo and XT30 reversals. Only the LED's proof is verified — the one that
cites a page of a kept datasheet; the other 17 say honestly how they were read until their documents
are kept and cited (B12, P64a). The DS3231's contradictory note is replaced by what the PO's photo
shows. Mutations `sprint-10-p81.json`: 4, all caught.
**Increment 2 done 2026-10-03 (with B11):** `parts.pull_conflicts` computes a pull-down the board adds
against the module's own pull-up — the divider, the voltage range over the module's supply range, the
supply above which the pin idles HIGH — and `--show` and the generated board file print it: *"AIA: the
board's 10000 ohm pull-down against the module's own 10000 ohm pull-up to its supply holds the pin at
0.5 of the supply (1.25 V to 6 V over its 2.5-12 V range), so it idles HIGH, not low, on any supply
above 5 V; the module's input-low threshold is not recorded, so below that the level is undefined."*
Quiet when the pull-down holds the pin under the threshold across the whole range. The VL6180X record
now states its carrier's 10 k pull-ups to VIN as verified facts (Pololu's schematic) and its reason no
longer says it carries none — 4.7 k in parallel makes about 3.2 k; the circuit is unchanged. What to do
about the L9110S is a design decision, after the meter reading the bin's STATUS asks for and the
input-low threshold the record lacks. Mutations `sprint-10-p81-pulls.json`: 5, all caught.

### P83 — The catalog leaves the plugin, slim; candidates' photos and seller listings go — **slice 4; the PO's decision of 2026-10-03 (W21)** — DONE 2026-10-04
**Needed by:** everyone who installs spark — the researcher writes catalog records into the plugin's
own folder, which is a commit to a public repository for the author and a cache the next update
abandons for anyone else — and the person's store, where 47 files (10.2 MB) back only candidates
nobody chose. The catalog moves to the person's store (`~/.local/share/spark/catalog/`); the 19
candidate datasheets and drawings stay; the 28 product photos of unchosen candidates are deleted (the
PO approved the list, 2026-10-04); seller listings leave every record (kept: `owned`, a maker-less
part's order code, "this listing is a different part"). A shopping list made at buying time replaces
them (P79's outputs).
**The PO revised the cut, 2026-10-04:** *"shouldn't we store at least some basic info like the pinout
and docs?"* — a candidate keeps **all its part facts** (pinout and its proof, power, body, footprint,
warnings, the cited facts): they describe the part, stay true without upkeep, and a swap decision rests
on them (the DFR0819 is recorded as "the swap if the DFR0641 cannot be bought"). Only what goes stale
leaves: seller listings and the product photos.
**Value proven by:** `git ls-files catalog` is empty and `--need rtc` still names the DFR0819 from the
store, with its pinout; a catalog record with `sourcing` is refused by name; the store holds 63 files.
**Done 2026-10-04.** `parts.CATALOG` is `~/.local/share/spark/catalog/`, beside the kept documents; the
18 records moved there with their part facts and without their seller listings — the three maker-less
parts keep their shop order codes (Hadex D228A, LaskaKit LA217012, LaskaKit LA131042 with Botland's EAN
as an alias). The 28 approved photos were deleted: the store went from 91 files to 63. `git ls-files
catalog` → 0; `parts.py --need rtc` names `dfr0819-ds3231sn-rtc … [catalog: researched before]`, whose
record holds `pin_order` VCC GND SCL SDA INT RST 32K, 18 facts and both kept documents.
`catalog_records()` names a record with `sourcing` as broken, with why. The researcher and
`/spark:research` write candidates to the store. Mutations: `sprint-10-p83` 2 of 2, `sprint-5-catalog`
10 of 10 (one re-anchored), `sprint-8-p55` 4 of 4 (its two catalog-file rows left with the files).

### P95 — Store 1a: my drawer, filled and seen — **slice 10; P94's first increment (the PO, 2026-10-04)** — DONE 2026-10-04
**Needed by:** the PO, who owns 99 DFRobot SKUs and more from AliExpress and wants spark to know them before any
project. Design: `docs/2026-10-04-store-design.md` §4 (store 1a), §5.1–5.5, §6.1–6.4, §6.6, §7.
**Value proven by:** `parts.py --drawer --json` lists the PO's real drawer — the DFRobot import's 99 SKUs and his
typed parts — with SEN0193, DFR0954, DFR0975 and irrigation's DFR0457, DFR0831, SEN0217 and DS3231 linked; the
suite runs green on an empty and a seeded `SPARK_HOME` and never reads the real store; `parts_on_hand` and a
record's `owned` are gone (W16).
**Proven 2026-10-04, from Task 8's output on the PO's real store:** 110 drawer entries, 12 linked — SEN0193 (catalog),
DFR0954 and DFR0975 (library), and irrigation's DFR0457, DFR0831, SEN0217 and DS3231 onto the shelf, which every
project's `--list` now shows. A live re-import in the PO's browser read 8 orders, 106 lines = 106 stated, 99 SKUs,
167 pieces — the first pass exactly — and changed nothing. The suite runs on a scratch `SPARK_HOME` (1,020 tests);
`parts_on_hand`, `owned`, `photo` and the owned listing are retired in spark and the PO's four projects. The code
budget was raised to 5,189 for it, measured after its refactor (W15b). Plan and ledger rulings: the PR.

### P96 — Store 1b: a goal, matched — **slice 10; P94's second increment** — DONE 2026-10-04
**Needed by:** the PO's walking skeleton, the plant thirst alarm. Design §4 (store 1b), §5.3, §5.4, §5.6, §6.2.
**Value proven by:** from "tell me when my plant is thirsty", `parts.py --match <project> --json` lists each
need's candidates from the store with owned and free counts and what each owes (SEN0193: `pin_order_proof`,
`footprint`, `simulation`; DFR0954: `footprint`); `--validate` walks every layer and finds no broken record.
**Proven 2026-10-04, on the PO's real store:** `--match ~/Development/plant-alarm` gave soil — SEN0193, 8 owned, 8 free,
owes footprint, pin_order_proof, simulation; alarm — the DFR0954 amp (2 owned, owes footprint), the FIT0502 speaker,
the DFPlayer Pro, the MP3 mini module (maybe owned); board — the FireBeetle S3 (1 owned, 0 free: the bin holds it)
and the XIAO C6 (1 free); battery — the 1S LiPo (0 free). The PO marked all four `have`. The walk is `--audit`
(ruling: `--validate` keeps its meaning) — catalog 18 owe facts, 0 broken. Size: +278 code lines (the needs file,
the matcher, owed vs broken and the walk).

### P97 — Store 1c: picks to a building list, tallied — **slice 10; P94's third increment**
**Needed by:** the same skeleton, to its end. Design §4 (store 1c), §5.7, §6.5, §6.7, §8 C–T.
**Value proven by:** the bin's FireBeetle S3 refused as already held; owed facts filled in the records' own homes
(the DFR0954 footprint from DFRobot's drawing, one counted request); `check_spine` ends `[ok]`; the cost line
"5 picks: 5 from the store (5 owned) — 1 request, 1 document, N min".

### P98 — Mutation runs that take seconds, not minutes — **the team's tools; the PO, 2026-10-04: next after P95** — DONE 2026-10-04
**Needed by:** the PO — *"I think we should also try to make things faster. How often do we really need to run all
the mutations? Can we optimize it somehow?"* Measured 2026-10-04: each mutation re-runs the whole suite (11.4 s), and
`tests/test_mutate.py` alone takes 6.3 s of it while it can catch no mutation in `scripts/`; a task's table of 18 runs
3–4 minutes. The 438 mutations in 75 tables are never run together — each task runs only its own, and the push gate
checks anchors only — so an old table can go stale unseen. An idea, to refine with the PO before it is planned.
**What it could be:** (1) inside a mutation run, leave out `test_mutate` unless the mutation is in `tools/mutate.py`,
and stop at the first failing test; (2) run the tests that import the mutated file first and the full suite only for a
survivor, so an escape is never misreported; (3) run mutations in parallel, each in a temporary copy of the tree;
(4) every table once per sprint, at the close audit — the task's own table and the push gate's anchors unchanged.
**Value proven by:** one table's run time before and after, on the same table; all 438 run inside a sprint-close audit.
**Proven 2026-10-04 (82155c3):** P95's drawer table, 19 mutations, in clean worktrees — 337 s with the old tool,
69 s with the new; 18 caught by the near tests, 1 by the whole suite. The sweep of every table is in the Definition
of Done for each sprint's close; its first run is Sprint 10's close.

### P99 — The code cap reports growth instead of gating it — **the team's tools; the PO, 2026-10-04: after P98** — DONE 2026-10-04
**Needed by:** the PO — *"Do you think capping the code works for us? Does it really protect us from bloat or other
things? what is it good for and does it actually work?"* Measured on P95, 2026-10-04: `SCRIPTS_CODE_BUDGET` was raised
six times in one item — 5,086, 5,106, 5,183, 5,188, 5,189, 5,228 — each to the measured total in the same commit, and it
prompted one refactor of 2 lines. What stopped bloat and defects in P95 was the reviews (two ways to lose drawer
data, a double count, the suite able to write into the person's store) and the orphan tests. An idea, to refine
with the PO before it is planned.
**What it could be:** the cap stops being a failing test and becomes a reported figure — each pull request and each
sprint review says how many code lines an item added and why; the orphan and unused-code tests stay as they are.
**Value proven by:** a sprint review that shows each item's growth beside its reason, and no commit that exists only
to move the number.
**Proven 2026-10-04:** the cap test is gone; the pre-push gate prints `scripts/: 5,228 code lines (+0 since
origin/main)` (P98 added no product code); W15b and the Definition of Done ask each Done line for its growth
and reason. P99 itself added none to `scripts/`. The sprint review half is Sprint 10's close.

### P94 — The store and its ways in, designed: an extendable, reusable architecture — **slice 10; the PO's request of 2026-10-04**
**Needed by:** every way into spark (P76's goal-first, module-first, combination, whole-drawer, revive,
swap, extend), the drawer (P93), the viewer (P86) and a shared database (P84) — all of which read and
write one store. The PO: *"let's design it and refine and plan the stores with the council, mostly we
want to have a well designed extendable reusable architecture."* What "the database gets better" means
(the PO, 2026-10-04): **more parts known** (researched once, found from every project), **proven by use**
(a part that built and ran says so), and **fewer requests, measured** (a project shows what it cost and
what came from reuse) — not "every part complete": a record grows when a stage needs a fact.
Builds on P85's discovery (`docs/2026-10-04-store-discovery.md`) and its items P87–P92.
**How it is designed (the PO's choice, 2026-10-04):** story map + flows + example mapping — the council
drafts the flow of each way in (the map's backbone), the domain model and architecture options; the PO and
Claude map the stories under the flow steps and cut a walking-skeleton slice; that slice's stories are
example-mapped (rules, examples, questions) into readable checks; a spec and a plan are written for that
slice only, the rest stays on the map until pulled (W14).
**Value proven by:** a design spec the PO approves section by section — the architecture, the data model,
the ways in it serves, what is built first and what waits — and an implementation plan he approves;
then the items it orders. **2026-10-04:** spec version 2 written after a five-lens review council; it orders
P95, P96, P97 (store 1a, 1b, 1c).

### P93 — My drawer: the parts I own — **slice 10; the PO's idea of 2026-10-04 — an idea, not designed yet**
**Needed by:** the maker, who owns *"plenty of existing modules from DFRobot and lots of parts from
AliExpress that I will want to use at some point"*, and any hobbyist with a drawer — so a project starts
from what is there before anything is bought or researched. As discussed: owning is not researching — an
entry can be light (a SKU or a listing, a photo, how many), and a part's facts are read only when a
design considers it; `/spark:identify` is the way in for an unlabelled part.
**Designed in P94 (2026-10-04):** a drawer entry holds `label` and `count` (pieces), optionally where it
physically is, which projects use how many, where it came from, photos and its function; never price or date.
Importers are a strategy: **DFRobot order history and the typed or dictated list first** (store 1a, P95), then
AliExpress orders (not now — the PO), then photos.
**Value proven by:** slice 1's D story — `--drawer --json` lists the PO's real parts, "owned, not researched".

### P86 — A viewer and manager for the store — **slice 10; the PO's idea of 2026-10-04 — an idea, not designed yet**
**Needed by:** the person whose parts, candidates and kept documents are spread over a store, a
library, projects and — with P84 — a shared database, and who can see them today only one command at a
time. The PO: *"Later we will also want to build a standalone viewer and manager of the store, where
one can see what we have, both the local and online stores, edit, download, research, find, etc."*
**Builds on:** P85's use cases (it is the store's second client, beside the scripts), P90–P92 (what it
needs from the data: document status, JSON from every read, one validating writing path) and P84. P85's
trust rules for it: record text shown escaped; origin and review badges; writes only through `parts.py`;
vendor files opened from the local store only. First as a generated read-only page (the skeptic).
**Value proven by:** to be set in discovery, after P85.

### P85 — The store, reviewed whole: use cases, gaps, one plan — **slice 10; the PO's request of 2026-10-04** — DONE 2026-10-04
**Needed by:** every item that touches where spark keeps what it found — P61, P62a and P62b (the
store and its documents), P82 (the layered list, its downloads), P83 (the catalog in the store, done),
B12 (the bin's 16 files: kept in the store and checked byte for byte on 2026-10-04; citing by key and
the removal from the bin paused here) and P84 (a store you can choose, a shared part database — an
idea). The PO: *"let's review and replan all the store related changes together, find gaps and make sure
it's all making sense together and works, let's have the council review it, already specifying the
use cases and such."*
**Value proven by:** a discovery document the PO reads and decides on — the store's vision, its use
cases and user stories for the personas, every gap found with its evidence (a file and line, or a
command and its output), and one ordered plan for B12's remainder, P84 and whatever the gaps add; the
PO's decisions recorded on the items it names.
**Done 2026-10-04.** `docs/2026-10-04-store-discovery.md`: a council of five (the hobbyist's advocate, a
data steward, a software architect, trust and licensing, a skeptic), read-only — a proposed vision, 21
user stories each with its check, 19 gaps with evidence, one ordered plan. The PO decided four things,
recorded there and on B12, P84, P86 and the new items P87–P92: chosen parts go on a shelf in the person's
store; all 23 vendor-derived files leave the bin's tree, its history kept; public copies are sought before
a fact is marked as resting on a private document; P84 drops the selectable backends and its shared
database waits for the first outside researcher.

### P87 — Records are inert: no record text can act, no record path can leave the store — **slice 10; P85's plan, Now**
**Needed by:** every person whose spark reads a record they did not write — a shared one (P84), a
project cloned from someone else — and the agent handed a path. P85 found a record's `footprint`, `name`
and `host_parts.why` reach the generated board file unescaped (`emit_board.py:655-703`; a crafted record
produced live JavaScript, `validate` returned `[]`), `--fetch` names a kept file from a URL that can climb
out of the store with `..%2F` (`parts.py:981`), `documents.file`/`sha256` and `photo` are never
contained, and no agent is told that record text is data.
**Value proven by:** a hostile-record fixture — each bad field on its own — is refused by name by
`--validate`; `--fetch` and `--promote` write nothing outside their folders; the emitted board file
holds every record string as inert text; each agent's instructions carry the sentence; mutations caught.

### P88 — The suite never reads the person's store; one function says where the store is — **slice 10; P85's plan, Now** — DONE 2026-10-04 (carried by P95)
**Needed by:** the maker and any contributor, whose own store decided 4 tests' outcome (a seeded home with
a pin, a tool turned off and one record failed 4; the suite read the real catalog 37 times), and every
future store client. The store's root is spelled twice (`parts.py:665`, `tools.py:44`) with no override.
**Value proven by:** one function gives the root (`SPARK_HOME`, then `XDG_DATA_HOME/spark`, then
`~/.local/share/spark`); the suite runs green with a seeded home and with an empty one, and an audit
check finds 0 reads under the real home.

### P89 — `--need` tells the truth about candidates — **slice 10; P85's plan, Now**
**Needed by:** the agent, told "`--promote X --project .` builds with it" (`parts.py:1257`) of catalog
records none of which passes the contract since P81; and the hobbyist swapping a part, who cannot see why
it was passed over (`//why_not`, which nothing prints).
**Value proven by:** `--need rtc` shows each candidate's contract problems ("draft: 1 to fill —
pin_order_proof"); the 18 records' `//pin_order` and `//why_not` become fields and `--show` prints
`why_not`; a check walks the person's catalog again (P55); `--catalog --json` exists.
**Partly carried, 2026-10-04:** the walk is P96's `--audit` (owed vs broken, every layer), and `--catalog --json`
came with P95. Still open: `--need` showing what each candidate owes, the notes as fields, `--show` printing
`why_not` — pulled by 1c's step that fills owed facts.

### P90 — A document comes back, checked — **slice 10; P85's plan, Next**
**Needed by:** the hobbyist on a new machine and anyone re-checking a fact: `--fetch` skips every URL
already in `documents` and never compares a checksum (`parts.py:971-977`), writes straight to the final
file, and says nothing when a fetch fails; the store keeps no record of a document's own URL, date or
version beside it.
**Value proven by:** on an empty store `--fetch <id>` restores each document from its own URL through a
`.part` file and prints "same sha256", "DIFFERS — the URL now serves another file" or could-not-run; a
manifest beside each kept file holds its URL, archive member, retrieved date and printed version; tools.py
and parts.py share one checked fetch.

### P91 — A shelf for the parts you chose — **slice 10; P85's plan, Next; the PO's decision of 2026-10-04**
**Needed by:** the hobbyist starting a second project, to whom the part chosen and verified in the first is
invisible (`--need rtc` from the quickstart lists 4 rejects, not irrigation's DFR0641); and every non-
maintainer, whose `--promote` into spark's library writes into an install cache the next update discards.
**Value proven by:** `--promote <id> --project .` from a project puts the record on the person's shelf in
the store, without `owned`, `sourcing` or `photo`, and records `based_on`; `--need` reads project → shelf →
catalog → library and from the quickstart lists irrigation's DFR0641; writing spark's library is an
explicit maintainer flag. **Corrected by P94's design (2026-10-04):** resolving an id reads project →
shelf → library → catalog (a draft never hides a checked part); proposing parts reads the drawer first.

### P92 — Records written through `parts.py`, read as JSON — **slice 10; P85's plan, Next**
**Needed by:** the agent, told literal paths to write to (`parts-researcher.md:57`, `research.md:85`,
`identify.md:55`), so nothing validates what it writes and the store cannot move; and the viewer (P86),
which needs JSON from every read.
**Value proven by:** `--skeleton --catalog`, `--keep --into <id>` and `--set-aside <id>` write through the
contract; `grep '\.local/share' agents commands` prints nothing; `--kept`, `--catalog`, `--fetch` and
`tools.py --status` take `--json`.

### P84 — A store you can choose, and a shared part database — **slice 10; the PO's idea of 2026-10-04 — an idea, not designed yet**
**Needed by:** the hobbyist who researches a part someone else already researched, and every spark
user whose kept records live in one folder on one machine. The PO: *"implement and architect it in
such a way that the store is also selectable, whether it just saves it in an MD file or uses some
database or NoSQL … a local store but also some online repo."* And: *"for now it's just an idea — we
would go the whole way through: the vision, the use cases, the user stories, refined and planned, and
then implement as we want to go."*
**Builds on:** P83 (the catalog in the person's store — its folder becomes the first, local store)
and P82 (the layered personal/project list — the same mechanism would choose a store). When P84 is
built, its work is one branch and one pull request that names all three.
**Decided so far (the PO, 2026-10-04):** the online store is **a shared part database** that other
spark users read and contribute to; contributions arrive as **pull requests to a public GitHub repo of
records**, reviewed before they merge (a clone is the local cache); it sits **beside** spark's shipped
library, which keeps its few verified parts for spark's own tests and examples.
**Superseded in part by P94 (the PO, 2026-10-04):** strategy seams *are* designed in (spec §6.2–6.3) —
selectable by name — but no second backend is built until one is pulled. **The PO decided after P85, 2026-10-04:** **no selectable backends** — no database, NoSQL or Markdown
store (the council was unanimous: one implementation behind an interface is indirection, and pull requests
mean JSON in git). The shared database **starts when the first person outside the project researches a
part** (slice 5); first as the skeptic's no-code experiment — a public repo of records that pass the
contract, cloned into the folder spark already reads. Its prerequisites are P87–P92; it adds a record's
identity and provenance (maker part number, `order_codes`, `written`, `review`, `origin`, a fact's
`source_kind`), `--contribute`, and a reviewer's CI. See `docs/2026-10-04-store-discovery.md`.
**To confirm in discovery (assumptions, not decisions):** the shared repo holds records only — identity,
part facts with their citations, the pinout with its proof — and a document as its URL and sha256,
never the file (vendor licences grant nothing; another user fetches from the maker and the checksum
proves it is the same file); a record from someone else is untrusted until reviewed, shows where it
came from, and `--promote` still demands the contract; the local store stays the default and works
offline. A first architecture to weigh then: two ports — a record store (get, put, delete, search by
id) and a content-addressed document store (put and get by sha256) — with adapters chosen in the same
layered personal/project list as the tools (P82), each passing one shared contract test; JSON stays
the record format whatever holds it, Markdown a rendered view; reads go project → local → shared,
writes to one chosen store; the research agents write through `parts.py`, never to a path.
**Value proven by:** to be set in discovery; the PO's success, as understood: a new user's `--need rtc`
finds the DFR0819 from the shared database — its pinout, its datasheet's URL and checksum — without
anyone researching it again.

### B12 — The bin's vendor datasheets are kept, cited, then removed — **slice 6; the PO's decision of 2026-10-03; widened 2026-10-04** — DONE 2026-10-04
**Needed by:** the bin's public repository, which tracks 16 vendor datasheets (7.5 MB) under licences
that grant nothing — 12 of them exist nowhere else, and the L9110S guide that proves B11 has no URL
anywhere. Order, because removing first loses them: `parts.py --keep` each into the store with its URL
where known, cite each from spark's records by key, then `git rm parts/datasheets`. Rewriting the bin's
public history is a separate decision.
**Value proven by:** `parts.py --kept` finds each of the 16; the four spark records that name them cite
them by key; `git ls-files parts/datasheets` in the bin is empty.
**The PO widened it, 2026-10-04 (P85):** all **23** vendor-derived files leave the bin's tree — the 16
plus `parts/xiao/getting_started.md`, two Seeed pinout PNGs, two JLCPCB `.obj` models and two copies of
the XIAO `.kicad_mod`; **the history is kept**. Before the `git rm`, **public copies are sought** for the
documents shipped verified facts rest on that nobody else can obtain (the L9110S guide; the WROOM-1 v1.1);
only what stays unfindable is marked as a private source. The citation map is the appendix of
`docs/2026-10-04-store-discovery.md`. Kept so far: all 16 in the store, checked byte for byte; their URL
proofs in `~/.local/share/spark/b12-kept-from-the-bin.jsonl`.
**Done 2026-10-04.** All 23 are in the store, each checked byte for byte against the bin's copy (the two
footprint copies are one file). spark's four records cite 15 of them by key (`f8b0561`): every `--kept`
word prints `cited by …`, and AN4545, which no spark fact rests on, is held by `vl6180x-breakout`.
Public URLs (`2311bca`): byte-identical for the DFR0534 datasheet, drawing and two photos, the JQ8400
manual, the GME L9110S datasheet, AN4545, both Pololu files, the XIAO footprint (Seeed's library, CC
BY-SA 4.0) and both FireBeetle schematics (members of DFRobot's V1.3 zip); the same text in another save
for the Handson guide and the ETA6003; none for the WROOM-1 v1.1, now `private_only`. The DFR0534
"product photo" was a broken-image placeholder and left the record. In the bin (`0a51689`):
`git ls-files` of the four paths → 0; the text points at `parts.py --kept`; `make check`: everything in
step; history kept. **What it cost, and the lesson:** the search for public copies covered 10 documents
when the decision named 2 — 55 tool calls, about 0.12 M tokens, 11 minutes — against W21's "never gather
what no decision reads"; a lookup is now scoped to the documents a decision rests on.

### P82 — Setting up spark is one step, like installing a package — **slice 1; the PO's request of 2026-10-03** — DONE 2026-10-03
**Needed by:** the hobbyist, and the PO building the quickstart: *"we want to make it as easy and
seamless for users as possible, like packages."* Step 5 of the quickstart stopped at `????` "tsci is not
installed" while `build.md` says its one command "needs neither"; an `npm install` the person had to
know to run fixed it. A newcomer meets four more such steps nobody does for them: the converter's
packages (B10), `littlefs-python` for the flash image, a MicroPython firmware download, and a Node of
version 20 or more for espressif-docs — and a global tool can vanish under them (switching nvm's
default to Node 22 hid a global `tsci` installed under 18). Not designed yet: what spark installs by
itself, what it asks consent for, and what it only names.
**Value proven by:** from an empty `CLAUDE_CONFIG_DIR` and an empty directory, `/spark:init` then
`/spark:build` reach "the chain runs end to end" with at most one consent and no install command the
person types; anything still missing is named with the one command that installs it.
**The PO decided, 2026-10-03:** (1) **one setup step, one yes** — `/spark:setup` checks every
dependency, shows what is missing, and with one consent installs it into the person's user space (npm
in the project, pip `--user`, poppler via Homebrew where present) — never `sudo`; after it, init and
build never stop for a missing tool, and every command still names anything missing with its fix.
(2) **the simulation converter ships bundled** as one self-contained file in spark, so simulation needs
no install at all — B10 goes with it; a check keeps the bundle in step with its source.
**Done 2026-10-03** (branch `tools-list`; spec `docs/2026-10-03-tools-design.md`, plan
`docs/2026-10-03-tools-plan.md`). One list — `data/tools.json`, the person's
`~/.local/share/spark/tools.json`, the project's `.spark/tools.json`, merged field by field with the
project winning — and every script asks `tools.find` for a role; a test refuses a script that names a
tool's executable. `/spark:setup` (`tools.py`) shows `[ok]`/`[????]`/`[off]`/`[!]`, installs with one
yes and never `sudo`, and turns integrations on and off, swaps a tool behind a role, pins a version and
takes a person's own entry. The cold run — a fresh clone, empty `CLAUDE_CONFIG_DIR` and `HOME`, `PATH`
cut to the system, Python and Node — printed `6 to install: pdftotext wokwi-cli bun tscircuit
littlefs-python micropython-esp32s3`; after `init_project.py`, the one `tools.py --install tscircuit
--project .` ran `npm install -g bun` and `npm install --save-dev @tscircuit/cli@0.1.2113
tscircuit@0.0.2600`, and `check_spine.py requirements.json --keep .` ended `[ok  ] build 19 trace(s), 0
errors, tsci 0.0.2600`, `[ok  ] simulation 17 wire(s) in the diagram`, *the chain runs end to end*.
The first cold run found what no earlier step could: `tsci` starts with `#!/usr/bin/env bun`, so the
board engine needs bun — Homebrew had hidden it here; it is on the list now. The slash command itself
ran on 2026-10-04 after a restart, in the quickstart (the PO's own config, not an empty one): one
`[????]` (the MicroPython build), the dry run's one command, one yes, then every row `[ok]`, exit 0.
Mutation tables `sprint-10-p82-1` … `-7`.
**The final review** (a fresh reviewer, the whole branch) found what those runs had not: the simulator's
install line `npm install -g wokwi-cli` is a 404 — npm has no such package — and a broken tools file, a
project turning a tool off, a pin and a project's own install command each misbehaved at a real entry
point. All fixed test-first (`sprint-10-p82-review`, 22 of 22 caught): wokwi-cli is Wokwi's release
binary for the machine, v0.28.0 against GitHub's sha256; a download is a plain file name, lands as
`.part` and is renamed only after its checksum; `--dry-run` shows every command before the yes and marks
those a project's file chose; the board engine installs `--save-exact` (npm had written `^0.1.2113`).
**The third cold run** took both paths the first two missed — a bare directory with no project, and
the simulator itself: `--install bun tscircuit wokwi-cli` ran `npm install -g bun`, `npm install
--save-dev --save-exact @tscircuit/cli@0.1.2113 tscircuit@0.0.2600` and the curl of
`wokwi-cli-macos-arm64` (58282064 bytes, checksum checked, reports `0.28.0`); then `check_spine.py
requirements.json` from the bare directory: `[ok  ] board … from the plugin's library`, `19 trace(s)`,
`17 wire(s)`, *the chain runs end to end*. Nine minor findings are deferred, listed in the branch's
final message to the PO.

### B13 — "must not float" passes a pin that floats — **slice 4; found 2026-10-03 building the quickstart** — DONE 2026-10-03
**Needed by:** the quickstart, whose `rules-vs-netlist` read `[ok]` while both buttons' inputs have no
resistor — the button record itself says *"give it an external pull, not just the internal one"* — and
every design whose rules name an input. `compare_design.check_floating_inputs` asks only whether a pin
connects to *nothing*; a pin wired to a GPIO and nothing else floats all the same.
**Value proven by:** the check fails a `must_not_float` pin whose net reaches no rail through a resistor
and is not itself a rail, and names the quickstart's two buttons; the L9110S inputs, which have their
pull-downs, still pass; mutation caught.
**Done 2026-10-03.** A watched pin holds when its net is a rail, or a resistor on its net reaches one;
rails are tscircuit's power and ground flags plus the rails the rules file names (tscircuit leaves
MOTOR6V unflagged). A series resistor that leads nowhere fixed is not a pull. On the quickstart:
`[FAIL] rules-vs-netlist — BtnMode.A: joined to Mcu.D11 and no resistor to a rail`, the same for
BtnOpen.A at D12, while the L9110S inputs pass. Pads are named by their silkscreen now ("Mcu.D11", not
"Mcu.pin20"). P8's fixture carries the pull-down its own rule needs. Mutations `sprint-10-b13.json`:
5, all caught.

### P72 — The process fits a team of one person and Claude — **desk lane; the PO's decision of 2026-10-03**
**Needed by:** every slice, whose work competes with the process: of the last 80 commits about half
touched only scrum, docs or mutation tables (the skeptic lens, an estimate by path), and the rules
that held are the ones that fail a command.
Three cuts, all chosen by the PO: (1) a working agreement either fails a command or moves to one
unnumbered page of habits; (2) one sprint per slice, a retro of at most two actions, each with the
command that checks it; (3) mutation tables only for code that gives a verdict — the rest excepted in
`test_self_confirmation` with that reason — and the backlog's done and answered history archived
when P70 moves the open items.
**Value proven by:** `WORKING_AGREEMENTS.md` lists only agreements that each name their enforcing
command; the next retro has at most two actions; `UNMUTATED` names the non-verdict files.

### P73 — A bench session leaves a verdict a command can read — **slice 2**
**Needed by:** the bin's bring-up: `bringup/01..06` each end "PASS if …", judged by the person at
the bench, with nowhere to keep the judgement — and F4, which starts from it.
One log per step, kept in the bin: the script's output and the person's PASS or FAIL; the motor's
measured current and a `wake_reason()` after a wave as named lines.
**Value proven by:** a command lists every step with its verdict and exits 1 on a step without one.

### P74 — Firmware is checked against the pin map it imports — **slice 3**
**Needed by:** irrigation, whose requirements ask for four valves and a mode button while its
firmware never drives Valve4 and never reads the button — the sixth `check_all` entry P56's
increment I named and P36 did not build.
**Value proven by:** on irrigation the check names Valve4 as never driven and the mode button as
never read, and exits 1; after P59's fix it exits 0.

### P62a — The catalog's files move to the store, and a record says which document it kept — **Sprint 9, first** — DONE 2026-10-02
**Run after the last change:** `git ls-files catalog | grep -ciE '\.(pdf|jpe?g|png|webp|svg)$'` → **0**
(was 48); `attachments` appears in no catalog record, command or agent — in `scripts/` only in the
rule that refuses it (the acceptance line's "scripts → nothing" was overspecified: refusing a key
means naming it); `parts.py --sources dfr0534-module` lists **both** URLs (before: "cites no URL");
**48 of 48** store files match their recorded sha256. Irrigation's 7 records had the old format too
and migrated the same sitting (irrigation `fa6d198`, 42 files, chips left in place).
**Needed by:** a published plugin, which cannot ship the 48 vendor files (P61), and every record whose sources `--sources` cannot see today.
`documents` replaces `attachments` on every kind of record — keyed by a short name: `title` and
`version` as printed (null when nobody read it), `url`, `sha256`, `file`, `retrieved` — and a fact
cites one with `"cites": {"document": "<key>", "at": "Table 12, page 15"}`. `--fetch` writes into
the store. The 48 catalog files move there and their folders leave git in the same commit (W16),
with the documents that describe them. `cited_urls` reads dict-shaped `sources` and URLs inside prose.
**Value proven by:** `git ls-files catalog | grep -ciE '\.(pdf|jpe?g|png|webp|svg)$'` → 0;
`grep -rl attachments catalog scripts commands agents` → nothing; `parts.py --sources dfr0534-module`
lists its 2 URLs; each moved file's sha256 in the store equals the one its record states.

### P62b — A source is found before it is fetched again — **DONE 2026-10-03**
**Needed by:** the FireBeetle record, whose deep-sleep figure cites a datasheet page nothing can find, and every researcher (one fetch in five repeated one already made, P61).
`parts.py --keep FILE` copies a local file into the store and prints the `documents` entry to paste;
`parts.py --kept WORDS` searches every record's `documents` (library, catalog, boards, a project's own)
with no network and prints the store path — present or MISSING — and every fact that cites it. The
FireBeetle record gains the WROOM-1 v1.1 as a document and `cites` on the two facts it backs; `--kept`
becomes step 1 of `commands/research.md` and of the researcher agent.
**Value proven by:** with outbound network denied (`sandbox-exec`), `parts.py --kept wroom` prints the
v1.1's store path as present and `firebeetle2-esp32s3 power.deep_sleep_ua — Table 12, page 15`, and
`shasum -a 256` of that path equals the recorded sha256.
**Done 2026-10-03.** Reproduced with outbound network denied: `--kept wroom` printed the store path as
`present`, `power.module_peak_a — Table 11, page 15` and `power.deep_sleep_ua — Table 12, page 15`, and
`shasum -a 256` gave the recorded `bc430d66…b76b`. **The first run of that line failed:** it named 15
catalog DC jacks, RTCs and screw terminals as citing the WROOM. A record that did not hold the file was
searched with no key, and every object without `cites` compared `None == None`. The fixture had
every record holding the same datasheet, so the unrelated record never existed (W12: the fixture gained
one). A citation now counts by the name the OTHER record gives the same file (same sha256). Two holes
the work exposed are closed with it: a board's `documents` were never validated (P62b put the first
there), and a `cites` naming a document the record does not hold was accepted. Mutations
`sprint-9-p62b.json`: 10, all caught. Suite 808 OK.

### P64a — Nothing is marked verified without a source a reader can open — **slice 4**
**Needed by:** the bin, irrigation and the RC car, which read the library records whose 36 `verified: true` fields cite no source.
`parts.py --validate` and `boards.py --validate` refuse a `verified: true` fact-shaped object (facts,
`body_mm`, a board's `power.*`) whose source holds no URL and cites no kept document. The 36 fields
that fail today go to 0 in the same commit — each cited, or downgraded to `verified: false` with its
`why_it_matters`. A listing prints every prose claim with no pointer, with its count (65
`host_requirements` today) — the input to P64b.
**Value proven by:** the validators refuse a fixture with `verified: true` and a prose source (a
mutation caught); the real library, catalog and boards pass; the prose listing prints its count.

### P64b — A prose claim can point at the fact it rests on — **slice 6; whether is the PO's**
**Needed by:** every generated board, into which `emit_board` copies `host_requirements` verbatim — the path ALL_LOW took into irrigation and the remote.
`host_requirements` and world-claims in `//` notes carry no pointer, and no schema lets them; the false
ALL_LOW sentence was one of them. A contract change (e.g. `{text, rests_on: [fact]}`) that
`emit_board` and `parts.py --show` both read. The PO decides whether, and when.

### P64c — An isolated reader checks every claim against its kept source — **slice 6, after P64b**
**Needed by:** the same three designs as P64a — a claim with a source can still misread it, which only a reader of the source finds.
A new read-only agent (`claim-checker`, Read and Grep only — TEAM.md's four tests all pass) reads one
record and its kept documents, denied the project's own notes; returns per claim a verdict
(supported / unsupported / contradicted / no-source / suspect), the document@version, the locator and
the exact quote; a script greps each quote in the document's text, and a quote not found is the
checker's error. Non-supported verdicts are `raised` in `docs/observations/INDEX.md` and reproduced
before any record changes. It ships only if `/spark:research` or `--promote` routes to it (W15).
**Value proven by:** one pass over the 8 library and board records, every quote found by script, and —
run against `91e89ff` — ALL_LOW comes back contradicted or suspect naming the ANY_LOW alias.

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

### P58 — The bench instructions name the board you are holding — **slice 2**
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

### P59 — A generated project's firmware can be imported without running — **slice 3** (P2 merged in)
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
generates. Corrected the same sitting (irrigation `f8c59ad`, rc-car `87443a0`).
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

### P43 — What an agent reads back — **slice 4: the `fix` half only**; the rest parked, as it blocks no design
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

### P44 — Nothing shipped names one person's machine — **slice 1** — DONE 2026-10-03
**Needed by:** anyone who installs this plugin who is not its author. A shipped agent file names
an absolute path under one home directory for the catalog, which `parts.py` already knows how to
find; two shipped files hard-code one country's shops as prose while `.spark/project.json` already
carries a `sellers` list and the tool already prints "sellers: none named in the brief". (The
third instance, the converter looked for in a sibling repository, is P32's.)
**Value proven by:** a test that fails on an absolute path or a home directory in anything under
`commands/`, `skills/` or `agents/`; and the researcher agent reading the brief's sellers instead
of a list.
**Done 2026-10-03.** `test_orphans` fails on a home directory in any shipped file outside `docs/`
and `scrum/` (records of what happened) and the mutation tables (planted on purpose); on its first
run it caught its own comment quoting the path. The researcher gets the plugin directory from the
launching command, the sellers only from the brief — none named means asking — and `init`'s hint
shows two countries' shops instead of one. Mutations `sprint-10-p44.json`: 2, both caught.

### P39 — The library answers a need it has no words for — **slice 4**
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
**Run in irrigation after the last change** (`2f0a48d`): `assign_pins.py irrigation.requirements.json
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

### P38 — The capacitors P6 promised — **slice 4**
**Needed by:** the irrigation controller's 12 V rail, which switches four solenoids off an unfused
barrel jack with no bulk capacitor, and every module on the 3.3 V rail with no decoupling. P6's own
backlog text promised "a pulldown, a decoupling capacitor, a bulk capacitor on a rail"; the kinds
it shipped are pulldown, pullup and divider.
Add the two capacitor kinds to `HOST_PART_KINDS`, wired to the rail the record names, placed with
the other passives. (The valves' flyback diodes stay prose: the record puts them across the coil,
between the module's own screw terminals, which is harness wiring and not this board's to place.)
**Value proven by:** the irrigation board carries the bulk capacitor its record asks for; the
file's prose block shrinks by that requirement; a mutation removing the kind is caught.

### P2 — A simulation that costs no Wokwi minutes — **MERGED into P59 2026-10-03**: three lenses found nothing in it P59 and P56's increment II do not carry
**Needed by:** the irrigation controller's firmware, which has no test of any kind, and the quota —
three diagnostic runs went to discovering one documented fact (diary I11), and two audit rows could
not be checked because a scenario run costs minutes. The bin proves both shapes already: a fake
`machine` module for unit tests, and `run_on_micropython.py` for the whole firmware on a real
MicroPython runtime, 113 and 14 checks, free.
**Value proven by:** the irrigation firmware's logic is tested on this Mac with no Wokwi run, and
the scenario is kept for what only a simulator can show.

### R2.6 — A fourth cold test — **slice 5: run by a real person outside the project; the PO picks the domain**
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

- **P66, P68** the viewer page and sharing it — pulled back the day `tsci dev` fails to show a board.
- **P49** one command for this repository's gate; **P50** the adversarial reading — on no slice.
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

2026-10-03, by the story map: **P17** — "Needed by: none yet" since Sprint 5.

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
- **R11** — research parts and modules, vendor by vendor, and keep what was found: `parts.py --need/--skeleton/--sources/--fetch/--catalog/--promote`, `/spark:research`, `/spark:identify`, the `parts-researcher` agent, the catalog (`e50717a`…`d4f6b0f`, `773cd41`, `a4ad278`; proven on the irrigation controller: seven records, 18 candidates kept, every cited URL answering).
- **P28** — the tools made true: the mutate lock covers the pre-check and `apply` refuses a missing file (C8); `nets_in`, `rules_for`, `has_answers` named by tests (C9); the stranger test runs build.md's own lines (C10); the example block is a run's output and a test holds its schematic line to the example (C11); the status words come from `outcomes` in the three files that spelled them (C12); `tools/pre-push` is the versioned gate, installed with one `ln -sf` (C14). Table sprint-5-p28 (2): caught.
- **P10** — a project's own copy of a shipped board is checked against the plugin's cached vendor header instead of switching vendor-truth off: `cached_header` looks beside the board, then in the plugin (table sprint-5-p10, 1 caught; reproduced on the irrigation project first).
- **P6** — what a record demands of its host as a component is placed and wired: `host_parts` (pulldown, pullup, divider) become 0603 resistors beside the module, a divider ends the host's trace at its midpoint; the L9110S's pull-downs, the VL6180X's I2C pull-ups and the flow meter's divider are the first three; the spine asks a passive whether an end dangles instead of whether it touches ground; the generated resistors map to Wokwi's resistor. Reference: 20 traces, 18 wires, exit 0. Table sprint-5-p6 (9): caught.
- **P8** — the floating-input rule sees a pin-to-pin trace: the netlist model skipped every trace that named no net, which is how spark's generator wires every signal; a wire's traces share its connectivity key; the finding names its component and pin (I10). Proven on the irrigation board with four declared inputs and on the bin's own (`compare_design.py`, table sprint-5-p8, 3 caught).
- **P31** — a part record says how it is simulated; the spine builds the Wokwi project from the records, compiles the chips, and one irrigation scenario passes with the probe's and the flow meter's sliders set from the test (`1e77b88`, `204713d`, `3a9808c`, `64000d5`; irrigation diary, late night; converter `bf9bf09` in the bin repo).

P3 `831f756` · P4 `997b756` · P11 `0c21ef5` · P12 `c4d0582` · P13 `55e7bb8` · P14 `f7674b4` ·
P15 `f35e7df` · R7 `1f769f8` + P22 `c565778` · R9 `227f5d4` · P20 `c3e2e28` · P21 `7381fed` ·
P23 `5605065` · P24 `fd25f15` · P25 `ebb8339` + `7361679` · P26 `07821a0` · P27 `7459983` ·
the cut `066c4af` · the cold test's G-items in `~/Development/rc-car/DIARY.md` · the bin's B2 and B3.

## The bin

### B1 — Identify the audio module — **slice 2 [PO — blocked on Petr]**
**Needed by:** the bin's audio path — four things wait on a look in a drawer. microSD slot means
DFPlayer Mini; micro-USB and "Voice Module V1.0" means DFR0534; pads marked BCLK/LRC/DIN means the
I²S amp the board now assumes.
**Value proven by:** the bin's `make check` against the module that is actually there.

**Partly answered 2026-10-04** from the PO's DFRobot order history (read only, saved in his store): he bought
**DFR0954 MAX98357 I2S amplifiers ×2**, **DFR0768 DFPlayer Pro ×2** and **FIT0502 3 W speakers ×2**; no DFR0534
from DFRobot (one may come from elsewhere). Bought is not the same as in the drawer — a look settles it. His
FireBeetle is DFR0975 (N16R8); its hardware revision is still unread (the bin's STATUS item 8).
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

### B10 — An installed spark may not be able to simulate: the converter's packages are not in git — **slice 1; found 2026-10-03** — DONE 2026-10-03, as P82's task 4
**Needed by:** the hobbyist who installs spark from GitHub and runs `/spark:build`, whose last stage
runs the converter in `tools/circuit-to-wokwi` — and v1's "simulated" for a stranger (P51).
Seen: in a fresh clone of the public repository, without `tools/circuit-to-wokwi/node_modules` (git
never carries it), three converter tests fail with bun's *"Cannot find package 'circuit-json'"* — not
a sentence saying what to install; with the folder linked in, all 811 pass. A marketplace install has
no `node_modules` there, and no command or README line says to create one. P51 proved the documented
setup on a machine that was not the author's; whether that run's plugin carried the folder is
unknown, so this is a hypothesis about P51, not a finding against it.
**Value proven by:** from an empty `CLAUDE_CONFIG_DIR`, install spark from GitHub, run the documented
example through `check_spine` to its simulation stage: it either compiles the diagram, or stops with
one sentence naming the command to run — never a bun stack.
**Done 2026-10-03** (P82, task 4). The converter ships as `tools/circuit-to-wokwi/dist/converter.mjs`,
built by `bundle.sh` and held to its sources by a checksum test, and runs on Node found through the
tools list; a missing Node is could-not-run with its install line. In a fresh clone with no
`node_modules`: `tests.test_check_spine tests.test_converter` → `Ran 70 tests`, `OK (skipped=1)` — the
skip is the converter's own development suite. Running the bundle on the quickstart found two defects
the tests had not: `Bun.file` in `cli.ts` ("Bun is not defined"), and bun 1.4.2 bundling
`lib/mapping.ts` twice for Node when `cli.ts` began with `#!/usr/bin/env bun` (the records were
ignored: 9 wires, resistors as RGB LEDs). Both fixed; the quickstart's diagram is byte-identical to the
bun run's, and two tests run the shipped file through a real conversion. The final review found the
documented example still reached the plugin's own `cli.ts` from a directory in no project; the plugin's
source never runs now, and the third cold run converted from a bare directory through the bundle.

### B11 — A part demanded of the board that the part's own verified fact defeats is placed silently — **slice 2; found 2026-10-03 by the P80 council** — DONE 2026-10-03, as P81's increment 2
**Needed by:** the quickstart and the bin, both of which put 10 k pull-downs on the L9110S's inputs
while the same record states, verified from the vendor schematic, 10 k pull-ups to VCC on all four —
a divider near 3 V on a 6 V pack, above the part's 2.5 V input threshold; the record's own note says
so, and no build output does. The VL6180X record says its carrier has 10 k pull-ups and adds 4.7 k
"because the module carries none". The bin's STATUS asks for the meter reading that settles the L9110S.
**Value proven by:** `parts.py --validate` (or the build) names a host pull-down or pull-up on a pin
whose record states an on-board pull to a rail, with the divider's voltage against the input
threshold; the VL6180X record stops contradicting itself.

### B9 — check_all's last line counted checks that could not look as completed — **DONE 2026-10-03** (`3772767`)
**Needed by:** the RC car, irrigation and the bin, whose `check_all` all exit 2 today — and README:32,
spark's founding rule: a check that could not look must never read as one that passed. Reproduced
on the RC car with wokwi-cli off PATH: one `[ok  ]`, three `[????]`, one `[--  ]`, then *"nothing found
by the 4 check(s) that completed, of 5"*. `render` counted a check as completed unless it carried an
`unchecked` list; a could-not-run with only a `reason` slipped through. The exit code (2) was right.
**Value proven by:** the RC car's last line names one completed check; a test renders a could-not-run
that carries only a reason and fails on "completed" counting it; its mutation is caught.

### B8 — A firmware test failed once and was never caught again — **slice 2**
**Needed by:** the bin's commit gate, which is only trusted while it never fails for nothing. A
local no-spark `make check` failed at `firmware-tests` once; the same suite then passed 31 of 31
times alone and the rehearsal 4 of 4 — one failure in 36 runs, and the failing test's name was not
kept (the output went through `tail -1`). The suite runs real asyncio with real sleeps, so a test
racing the scheduler under load is the likely shape; unproven.
**Value proven by:** the failure reproduced and named — e.g. the suite run 200 times under CPU load
with every failure kept — and the test fixed so it cannot race; or 200 clean runs recorded.

### B5 — A derived file in git is checked current, or not kept in git — **slice 2**
**Needed by:** anyone reading the bin's repository: its `board-sch.svg` and `board-pcb-routed.svg`
showed the MP3 board for a week after the board changed (remade in bin `2367fa1`), and nothing
noticed. Tracked and derived today: `board-sch.svg`, `board-pcb-routed.svg`, `board.glb`,
`board-gerbers.zip`, `sim/diagram.json`, `.spark/board.json`, `firmware/micropython/smartbin/board_spec.py`.
Two are already checked (`diagram-current`, `board-spec-current`); the rest are not.
**Value proven by:** changing `board.tsx` without regenerating makes `make check` fail on each export
still committed, or that export is untracked and made by `make all`; a timestamp-only difference
(the gerbers regenerate with new dates) is not a failure.
**Seen 2026-10-03:** a gated commit left `board-gerbers.zip` modified — unzipped and diffed, every
Gerber and drill file differed in exactly its two creation-date lines, `bom.csv` and
`pick_and_place.csv` not at all. Every commit through the gate dirties the tree this way.

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

### P49 — One command runs this repository's own gate — **PARKED 2026-10-03**: the desk's tooling, on no step of the map
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

### P50 — An adversarial reading of what the tests would not notice — **PARKED 2026-10-03** under the story map's rule (on no slice); kept by the PO 2026-10-01, never run
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
