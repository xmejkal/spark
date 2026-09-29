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
| **R11** | Research parts and modules, vendor by vendor, and keep what was found | the third cold test, on day one |
| **P6** | The generated board honours the host requirements it prints | every generated motor board |
| **P8** | `must_not_float` false-positives on spark's own output | every generated board, at review |
| **P10** | A project's own board file must not switch `vendor-truth` off | any project with its own board |
| **P28** | The tools this repository relies on, made true | this repository's Definition of Done |
| R2.5 | The third cold test — **PO: one letter, (a), (b) or (c)** | it is the test |

### R11 — Research parts and modules, vendor by vendor, and keep what was found
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

### P6 — The generated board honours the host requirements it prints
**Needed by:** every generated board with an L9110S — the file prints "10 k pulldowns on both
inputs" and leaves the inputs floating; the reference design and the RC car both.
`emit_board` acts on the mechanical requirements it can (a pulldown, a decoupling capacitor, a
bulk capacitor on a rail) as real components on the board, and says plainly which requirements
are the reader's.
**Value proven by:** the reference design's L9110S inputs carry pulldowns in the built netlist;
`check_all` on it reports no floating input; the file lists the requirements it did not do.

### P8 — `must_not_float` false-positives on spark's own output
**Needed by:** every generated board at review — `check_all` on the reference design reports
`L9110sModule.AIA: connects to nothing` on a trace that exists. A rule that cries wolf is switched
off, and then catches nothing.
**Value proven by:** `check_all` on the generated reference design reports no `must_not_float`
finding, while a genuinely floating input still does.

### P10 — A project's own board file must not switch `vendor-truth` off
**Needed by:** any project whose board is its own file rather than the library's — the mechanism
you are told to use to record what you verified turns off the check that verifies.
**Value proven by:** a project with a board override still gets a `vendor-truth` verdict against
the override.

### P28 — The tools this repository relies on, made true
**Needed by:** this repository's own Definition of Done (close audit C8–C12, C14, C16). The mutate
lock is taken after the pre-check suite; `mutate.apply` reads a missing file where `anchors`
refuses it; the outcome words are spelled again in `compare_design.py`; `init_project`'s
`nets_in`, `rules_for` and `has_answers` are named by no test; the stranger test types the steps
itself instead of running the document's lines; `/spark:build`'s example output block shows
numbers no command produced.
**Value proven by:** each of those false; `tools/check_commit.py` green.

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
