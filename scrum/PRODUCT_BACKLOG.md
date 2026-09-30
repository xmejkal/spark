# Product backlog

The single ordered list. If work is not here, it is not happening. **Order is the Product Owner's**
(W11). Every open item names the design that needs it (`**Needed by:**`, W14) and a
`**Value proven by:**` command whose output Petr can read; an item that cannot name both is not
pulled. The suite refuses a backlog with an open item missing its need line.

Last ordered: 2026-09-29, night — **by the PO: need-based; cut what nothing uses.**

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

## Sprint 5 — in this order

| # | item | needed by |
| --- | --- | --- |
| R2.5 | The third cold test — **PO: one letter, (a), (b) or (c)** | it is the test |

### R11 — Research parts and modules, vendor by vendor, and keep what was found — DONE 2026-09-29
**Needed by:** the third cold test on its first day, and every design that uses a part the library
lacks — the RC car wrote three records by hand with unverified facts because nothing looked.
The unit is the part record the chain already reads: research produces a **draft record** in the
project's `parts/`, with every fact carrying its source: `verified: true` is the vendor's own text
at the cited URL, anything read off an image, inferred or computed is `verified: false` with
`why_it_matters` (two wordings of this rule sent three researchers back to ask — irrigation diary
I6). Vendors in the order the project's brief prefers (`.spark/project.json` → `prefer`; default
DFRobot, then Seeed); plain parts from the brief's `sellers`, local first (PO, 2026-09-29).
**Everything research reads is kept, chosen or not** (PO, 2026-09-29, late — "we want a good
database in time"): a `catalog/` in the plugin holds a record per candidate, drafts allowed, the
datasheet and photo downloaded beside it by `parts.py --fetch`; `--need` searches it after the
library; `--promote` moves a record into a project to build with, or into the library for the
next project. `/spark:identify` researches a module the PO owns from its photo. `parts.py --need` says what exists first; `/spark:research` runs the
`parts-researcher` agent; `parts.py --validate`, `--unverified` and `--sources` check the result —
the last fetches every cited URL, so a hallucinated source is caught. A pinout read off a wiki
image is written down as unverified, never invented. Not built: a scraper per vendor, a price
tracker, automatic pinout verification.
**Value proven by:** the first part the cold test needs that the library lacks goes through
`/spark:research` and comes back as a record that validates, cites resolving sources, lists what it
could not confirm — and the chain builds with it. Then: a candidate the researcher passed over is
in the catalog with its datasheet beside it, and `--need` for the same words finds it next time.

### P6 — The generated board honours the host requirements it prints — DONE 2026-09-29, late night
**Needed by:** every generated board with an L9110S — the file prints "10 k pulldowns on both
inputs" and leaves the inputs floating; the reference design and the RC car both.
`emit_board` acts on the mechanical requirements it can (a pulldown, a decoupling capacitor, a
bulk capacitor on a rail) as real components on the board, and says plainly which requirements
are the reader's.
**Value proven by:** the reference design's L9110S inputs carry pulldowns in the built netlist;
`check_all` on it reports no floating input; the file lists the requirements it did not do.

### P8 — `must_not_float` false-positives on spark's own output — DONE 2026-09-29, late night
**Needed by:** every generated board at review — `check_all` on the reference design reports
`L9110sModule.AIA: connects to nothing` on a trace that exists. A rule that cries wolf is switched
off, and then catches nothing.
Reproduced a third time on 2026-09-29, night, on the irrigation controller: four valve inputs
declared `must_not_float`, four traces in the built `circuit.json` touching them, four findings
"connects to nothing" — and the finding names neither component nor pin (irrigation diary I10),
so the list cannot even be acted on by hand.
**Value proven by:** `check_all` on the generated reference design reports no `must_not_float`
finding, while a genuinely floating input still does — and a finding names its component and pin.

### P10 — A project's own board file must not switch `vendor-truth` off — DONE 2026-09-29, late night
**Needed by:** any project whose board is its own file rather than the library's — the mechanism
you are told to use to record what you verified turns off the check that verifies.
**Value proven by:** a project with a board override still gets a `vendor-truth` verdict against
the override.

### P28 — The tools this repository relies on, made true — DONE 2026-09-29, late night
**Needed by:** this repository's own Definition of Done (close audit C8–C12, C14, C16). The mutate
lock is taken after the pre-check suite; `mutate.apply` reads a missing file where `anchors`
refuses it; the outcome words are spelled again in `compare_design.py`; `init_project`'s
`nets_in`, `rules_for` and `has_answers` are named by no test; the stranger test types the steps
itself instead of running the document's lines; `/spark:build`'s example output block shows
numbers no command produced.
**Value proven by:** each of those false; `tools/check_commit.py` green.

### P31 — A part record says how it is simulated — DONE 2026-09-29, late night (ordered that night: "make the Wokwi simulations work, have the WebAssembly made, set the values in the test")
**Needed by:** the irrigation cold test — its chain ends `????` at simulation because the
converter has no Wokwi part for any of its seven modules, and the PO asked what the options are.
A record carries a `simulation` field the converter reads: a Wokwi built-in stand-in with its
pin map and an honest note (a DS1307 for the DS3231's time registers, a potentiometer for a soil
probe, an LED or relay module for a valve driver), or a custom chip in the project's `sim/chips/`
(a pulse train for the flow meter — the bin's `vl6180x` and `l9110s` chips are the precedent,
five scenarios passing). Research fills it beside the pinout. Analogue questions (a divider's
high level, a flyback clamp, an ADC filter) are hand SPICE netlists through ngspice, not this
item. Not built: a chip generator, a SPICE flow for whole boards.
**Value proven by:** the irrigation chain reaches `[ok] simulation` with a diagram whose stand-ins
are named as such, and one scenario opens a valve when a probe's slider crosses its threshold.
**Slices, each proven on the irrigation chain:** (A) the record contract — `simulation.wokwi`
with a built-in `part` or a `chip` beside the record, `pins`, `stand_in`; or `simulation.skip`
with a reason — and every shipped record gets one, the bin's two chips moving beside their
records; (B) the spine writes the converter's mapping from the design's records, copies the
chips, compiles them with `wokwi-cli chip compile`, writes `wokwi.toml`; (C) the converter takes
`--mapping` and `--chips` and prefers them to its hand table; (D) two chips for the irrigation
modules — a flow meter whose pulse rate is a control, a soil probe whose moisture is a control
driving an analog voltage; (E) the sim project kept in the project, a firmware stub, one
scenario, one Wokwi run. The `scripts/` budget rises as needed — the PO allowed it.

### P32 — One home for the converter and the chips (proposed 2026-09-30 from the v1 audit; the PO orders)
**Needed by:** a stranger's simulation — the spine finds the Wokwi converter only at
`tools/circuit-to-wokwi` in the project or at `../smartbin-local/tools/circuit-to-wokwi`
(audit D17), so v1's "simulated board" holds only beside the bin repo; and W16 — the bin's two
chips were copied beside their records, not moved (D19), and the converter's hand table remains
the bin's own mapping (D20). The move is about 1,000 lines of TypeScript with bun dependencies
and the bin's `make check` depends on it, so it is a scope decision, not a slice.
**Value proven by:** the one command reaches `[ok] simulation` from a project with nothing beside
it but the plugin; one copy of each chip; the bin's `make check` green against the plugin's copy.

## After v1 — only if a cold test asks for it

Each parked, with its need unfilled; none is pulled without a design behind it (W14).

- **P2** a simulation run that costs no Wokwi minutes — **Needed by:** none yet.
- **P5** audit the remaining checks for what they skip — **Needed by:** none yet.
- **P9** `check_all` keeps the subject on every aggregated finding — **Needed by:** none yet.
- **P16** the bin's wake-polarity check, in spark — **Needed by:** none yet (the bin has its own).
- **P17** an off-board part emitted as its header, not its footprint — **Needed by:** none yet.
- **P29** the FireBeetle's VCC input as a power pad **[needs the vendor's fact]** — **Needed by:** any design that feeds the module from its own regulator; the RC car's plan called it a known risk.
- **P30** the simulation converter matching a part by what it is, not its name **[bin + spark]** — **Needed by:** a generated design with a named instance of a mapped part, in simulation.
- **R10** a link between two designs **[PO]** — **Needed by:** the RC car's car and remote, if their agreement is ever to be checked.

## Deleted on 2026-09-29 — in git history, not in this list

P1 (its value delivered; the move is the PO's), P7 (with `check_design`, which had made two tools of
one), P18 (`evals/` deleted), P19 (`findings.py` and its fake bench deleted), R8 (became R11, pulled
by the PO).

## Done — one line each, the hash is the record
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

## Intake, not backlog

Observer claims arrive in `docs/observations/INDEX.md` and leave by being reproduced or rejected;
a claim becomes work only by promotion here, with its need named.
