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
| **P33** | The documented setup must build the documented example | 5 | S | `/spark:init` writes a package file pinning nothing; `npm install` then fetches a tscircuit that fails on the plugin's own example |
| **P34** | A check that compared nothing says so | 5 | S | `compare_design` prints `every rule holds` having compared zero; `check_physics` prints its own could-not-run and exits 0 |
| **P35** | The rules see spark's own wiring | 5 | M | the generator wires signals pin-to-pin, so every rule keyed on a net name is dead on spark's own boards — P8 fixed this in one file of three |
| **P29** | The board's own supply, and nothing left unfed | 5 | S+M | no trace reaches the microcontroller's supply on any generated board, while the file says one does; the vendor fact it waited for is already recorded |
| **P39** | The library answers a need it has no words for | 4 | S | `--need measure distance` misses the rangefinder and `--need switch 12 V load` misses the MOSFET module — both send a researcher to write a record that exists |
| **P32** | One home for the converter and the chips — **PO: (a), move now** | 4 | L | v1's last word, "simulated", is true only beside the bin's repo (D17); two copies of each chip (D19, D20) |
| **P36** | The pin map is a file the firmware imports | 4 | S | twelve GPIO numbers are hand-copied into the irrigation firmware and a thirteenth into its scenario; nothing compares them |
| **P37** | What this simulation cannot show, printed | 4 | S | every stand-in record carries a mandatory honesty sentence and no command prints it, so a green scenario reads like a bench |
| **P38** | The capacitors P6 promised | 3 | M | `host_parts` has pulldown, pullup and divider; P6's own text promised a decoupling and a bulk capacitor |
| **P2** | A simulation that costs no Wokwi minutes | 3 | M | its "needed by: none yet" is false now: the irrigation firmware has no test of any kind and three diagnostic runs went to the quota |
| **R2.6** | A fourth cold test — **PO: the domain** | 5 | L | the cold tests found 13 and 12 gaps; ten of the twelve were invisible to every test in this repo |

### P33 — The documented setup must build the documented example
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

### P34 — A check that compared nothing says so
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

### P35 — The rules see spark's own wiring
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

### P29 — The board's own supply, and nothing left unfed
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

### P32 — One home for the converter and the chips — **PO: (a), move now** (2026-09-30)
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

### P37 — What this simulation cannot show, printed
**Needed by:** anyone reading a passing scenario. Every stand-in record already carries a mandatory
`stand_in` sentence — Wokwi's DS1307 answers at the DS3231's address with the same seven time
registers and has no alarms, no temperature; each valve is an LED with no MOSFET, no 12 V and no
flyback — and no command prints any of it, so a green run reads like a bench result.
The spine's simulation stage and `parts.py --show` print the stand-in limits for the design.
**Value proven by:** `check_spine.py <irrigation>` prints the three limits under its simulation
line, and a record whose `stand_in` is empty is already refused by the contract.

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
