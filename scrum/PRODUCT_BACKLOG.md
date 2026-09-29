# Product backlog

The single ordered list. If work is not here, it is not happening.

**Order is the Product Owner's** (W11). What follows is a *proposal*, ranked with reasons, until
Petr says otherwise. Anything marked **[PO]** needs his decision before it can move.

Every item carries `Value proven by:` — a command whose output Petr can read. An item that cannot
name one is not ready to be pulled.

Last ordered: 2026-09-29 — a proposal; the PO has not reordered since 09-25.

---

## The product goal

**From an idea to a simulated design.** `idea → parts → schema → simulation`, with 3D and PCB
after. In Petr's words: *"we first need to have working schema and code, then 3d or pcb"*.

Where that stands today, measured:

| step | state |
| --- | --- |
| idea → parts | works — `parts.py`, 5 records, contract-tested |
| parts → pin map | works — `assign_pins.py`; bus pins spent last (P3, `831f756`) |
| pin map → schematic | works |
| schematic → **builds** | works — 12 traces, 0 errors |
| **schema → simulation** | **works as of 2026-09-25** — a 10-wire `diagram.json` from a design nobody typed |
| → 3D / PCB | later, by Petr's instruction |

**The whole spine runs**: `python3 scripts/check_spine.py` →
`idea -> parts -> pin map -> schematic -> footprint -> build -> simulation`, exit 0. What is left
on it is quality, not existence: the structural question under P1, and the loader defects the sprint audit found (P11).

---

## Sprint 5 — proposed to the PO

See [`SPRINT.md`](SPRINT.md). Goal: **a generated board is a design someone could build.**

| id | item | size |
| --- | --- | --- |
| P8 | `must_not_float` false-positives on spark's own output | M |
| P7 | `check_design` recommends pins `assign_pins` refuses | S |
| P6 | `emit_board` honours the mechanical host requirements, or says which are the reader's | M |
| P16 | The bin's wake-polarity check, in spark | M |
| P17 | An off-board part is emitted as its header | M |
| R2.5 | Third cold test — **PO chooses the domain** | L |

## Sprint 4 — done 2026-09-29

See [`SPRINT.md`](SPRINT.md). Goal: **spark is usable by someone who has not read its source.**
Met: every non-PO item done, R7 reopened by the audit and done again as P22.

| id | item | size |
| --- | --- | --- |
| ~~P15~~ | Drain the intake: 42 `raised` rows, reproduced or rejected — **done `f35e7df`** | S, time-boxed |
| ~~R7~~ | The generator chain named by a skill, a command and an agent — **done `1f769f8`** for the one command; the steps reopened as P22 | M |
| ~~R9~~ | A rail belongs to the design, not the part — **done `227f5d4`** | M |
| ~~P20~~ | `assign_pins.main` through the loader; signals derived once — **done `c3e2e28`** | M |
| ~~P21~~ | A bus is shared; an instance name does not take a part off it — **done `7381fed`** | M |
| ~~P22~~ | A stranger can build [reopened R7] — **done `c565778`** | M |
| ~~P23~~ | Two outputs on one net, across parts — **done `5605065`** | S |
| ~~P24~~ | `check_design.py` gets a command line — **done `fd25f15`** | S |
| ~~P25~~ | One outcome vocabulary; a test for every rule function — **done `ebb8339`, `7361679`** | M |
| R2.5 | Third cold test — **PO chooses the domain** | L |

## Sprint 3 — done 2026-09-29

Goal: **spark reports what it did and nothing less.** Met; review in `SPRINT.md`.

| id | item | size |
| --- | --- | --- |
| ~~P11~~ | A design is loaded once, in one place, and `main()` is tested — **done `0c21ef5`** | M |
| ~~P12~~ | The spine tells a toolchain fault from a design fault — **done `c4d0582`** | S |
| ~~P13~~ | Sibling scripts are imported, not loaded by path — **done `55e7bb8`** | S |
| ~~P14~~ | `emit_board` says each thing once — **done `f7674b4`** | M |

---

## Ready — ordered

### P1 — Bring `circuit-to-wokwi` into spark — **the value is already delivered; the move is not**
**Done, and this is what it produced:** `check_spine.py` now has a `simulation` stage and the
chain runs `idea -> parts -> pin map -> schematic -> footprint -> build -> simulation`, emitting
a 10-wire `diagram.json` from a design nobody typed.

The blocker was not what the observer reported. The converter did not need three missing rows —
it needed to stop mistaking a NAME for an IDENTITY: `match: "MotorDriver"` is string equality
against what the BIN calls its driver, and a generated design names components after the part.
Fixed in `smartbin-local` (`59b7a0b`), which was right on its own merits: the same rule would
have failed for anyone who called their driver `M1`.

**What remains, and it is a structural decision for the PO, not a task [PO]:** the converter is
still ~1800 lines of TypeScript in the bin. spark finds it by searching upward and reports
`could-not-run` honestly when it is absent, so nothing lies — but a stranger installing this
plugin gets no simulation. Moving it means spark depends on bun. Options: move it, vendor it,
or leave it and document the dependency. **Not obvious, so not decided here.**

## The cold test — 14 findings from building something that is not the bin

On 2026-09-26 the plugin was used to build an ESP32 RC car and its remote from scratch
(`~/Development/rc-car`, full evidence in its `DIARY.md`). Both boards build. The exercise found
fourteen defects, and it is the single best source of ordered work this backlog has.

**Nine are fixed** — four below, five in the struck-through items that follow — each reproduced
before acting and each mutation-tested:

| id | what | fix |
| --- | --- | --- |
| G2 | rails outside a closed four-name vocabulary silently dropped — 3 of 8 power pins gone | `cc94dd1` |
| G7 | five identical parts collapsed into one, shorting five GPIOs to its single port | `0201d6d` |
| G8 | a second board in a project switched six of seven checks off and reported `ok` | `f2202e9` |
| G9 | `active.json` holding a list gave `--id` a Python repr to print, exit 0 | `3b5f38f` |

Three of those are the same defect class the bin already had twice — **the generator or the runner
produces less than it was asked for and exits 0** — and every one was found by building something
new, never by a test.

The rest, ordered. The first group is that same family and comes first because each is cheap and
each currently misleads.

### ~~R1 — `parts.py --validate` ignores project parts~~ [G14] — **REJECTED, reproduced and wrong**
The claim was that `--validate --project .` checks only the five shipped records and exits 0.
Reproduced: it lists all four of the project's own parts and exits 1 on a contract violation.
Fourth observer claim on this project to be wrong on reproduction. Kept, not deleted, so it is not
raised again.

**The reproduction found a real defect the claim missed [G15], now fixed in `3b5f38f`:** `validate()`
crashed with `KeyError` on a `needs` entry with no `pin` — the exact malformation it checks for —
because the `pin_order` block read `need["pin"]` three lines after reporting it. The test for that
fix found the same crash again in `power`. Fixed at the cause: only `needs` was ever checked for a
pin while three lists were read for one.

### ~~R2 — `init_project` silently picks one of two circuits~~ [G10] — **DONE `9fcb3c1`**
Refuses, names both files, and writes nothing when it refuses. Four tests, mutation caught.

### ~~R3 — A part stating a real requirement breaks the chain~~ [G12] — **DONE `9fcb3c1`**
One `CAPABILITIES`, owned by `parts.py`; `assign_pins` imports it. `pwm` added, satisfied by every pin unless a board lists `pwm_gpio`. The RC car's servo now declares its real requirement and the board says "needs pwm, and this pin does exactly that and no more". Six tests, two mutations caught.

### ~~R4 — A pin name with `+` or `-` cannot be wired, and nothing warns~~ [G3] — **DONE**
Measured on a probe board rather than assumed: `IN+`, `OUT-` and `A.B` do not resolve as
selectors; `V_IN`, `GND2` and `3V3` do. The contract now refuses a `pin` outside `[A-Za-z0-9_]`
where the record is written, and an entry may carry `printed` — the silkscreen, unrestricted —
mirroring `physical.pad_aliases` on the board side. The emitted file records both where they
differ. The MP1584 keeps `IN+ IN- OUT+ OUT-` as printed names. Four mutations caught.

Closing this tier triggered the sprint audit — `docs/observations/2026-09-29-sprint-audit.md`,
sixteen claims, every one reproduced or read (`INDEX.md` A1–A16). They became P11–P14 below.

### ~~R5 — The generator sizes no trace~~ [G6] — **DONE `dd01824`**
Sized from `.spark/rules.json` by `copper.py`, the module `check_physics` judges with — so the two
cannot disagree. The RC car's `physics` check now passes on a board the generator sized itself.

Two things the measurements changed: sizing only ever WIDENS (the IPC minimum for a 0.5 A rail is
0.12 mm, narrower than the router's default), and **a neck is not a trace** — six segments at
1.20 mm turned out to be 0.12-0.85 mm long, each the last step into the board's one 1.2 mm pad.
The constriction is real and belongs to the pad, so necks are reported rather than judged as runs.

`copper.py` is the refactor: no imports, no I/O, no state, checked against handbook figures rather
than against itself. 17 tests of its own.

### ~~R6 — A placeholder footprint is indistinguishable from a real one~~ [G4] — **DONE**
`footprint_placeholder: true` requires a `footprint_note`, mirroring the provenance `facts` and
`body_mm` always had. Four layers, each tested alone: the contract, the generator (which names
placeholders with its own `component_name` so the checker is keyed by the string that reached the
netlist), the checker (one `could-not-run` per stand-in, never dropped), and `check_all` wiring
them together with the generator's own functions rather than a second derivation.

The car's `buildability` went from a real-sounding defect about a part not on the board to "its
footprint is a stand-in ... was not measured". **Zero false problems across the whole suite.**

A mutation escaped — "the wiring passes nothing through" — because every test exercised the
derivation and none the check that consumes it. Same shape as the trace-sizing escape. The
integration test now exists, with a control that the same geometry IS measured without a project.

### From the sprint audit — 2026-09-29
`docs/observations/2026-09-29-sprint-audit.md`: an outside read after the nine fixes. Sixteen
claims, none rejected — every one reproduced or read and holding (`INDEX.md` A1–A16). Four items
came out of it. The first two are the "less than asked, exit 0" family again — this time inside
the generator's own entry point and in the spine's verdict — and they come first for the reason
that family always has: each one misleads today, on the documented command.

### ~~P11 — A design is loaded once, in one place, and `main()` is tested~~ — **DONE `0c21ef5`**
`emit_board.main` resolves the project at one line and passes the *unresolved* `--project` flag
to `rules_in` seventy lines later, so the documented invocation — inside the project, no flag —
emits every power trace unsized, exit 0, and says the widths are unjustified while
`.spark/rules.json` two directories down states them. Reproduced: 1 `thickness=` against 14.
Sixth instance of the family, inside the commit that closed the fifth. Nothing tests `main()`
and the mutation table cannot reach it. Same cause, three more claims: the load-and-tag loop is
copied in `check_all.placeholder_components_in` under `except Exception: return ()`;
`check_spine` resolves the project from `cwd` and the toolchain from the requirements file, so
from `/tmp` it cannot find the project's parts; the requirements JSON is read outside every
`try` — three raw tracebacks, exit 1, which in a three-valued tool reads as "problems found".
One `design.load(requirements, project=None)`: project resolved once, from the file's own
directory upward; JSON read inside the `try`; rules from the resolved project; called by all
three.
**Value proven by:** `emit_board.main` run from inside a temp project holding `.spark/rules.json`,
without `--project`, emits a `thickness=` on a trace — the test that fails today;
`check_spine.py /abs/path/car.requirements.json` from `/tmp` builds; a malformed requirements
file is `could-not-run`, not a traceback. Mutation: the resolved project swapped back for the flag.

**Result.** `scripts/design.py`; all three callers use it. The audit's test failed first and passes
now: 14 `thickness=` on the documented invocation. From `/tmp` by absolute path the chain runs
end to end — which exposed the converter being looked for from `cwd` as well, fixed in the same
change. Two decisions changed with their tests: an unreadable rules file is an error, and one
unreadable requirements file no longer empties the placeholder list for a whole project. Eight
mutations caught, 505 tests.

### ~~P12 — The spine tells a toolchain fault from a design fault~~ — **DONE `c4d0582`**
With nvm's global `tsci 0.0.2600` first on PATH, `check_spine.py` from the spark directory says
`[!!] build — no circuit.json was produced … Cannot find package 'react'` and **"the chain is
broken", exit 1** — a toolchain that cannot build anything, reported as a defect in the design.
W1's mirror image: a check that could not look, reading as a check that failed. The "exit 0"
claim at the top of this file had an unstated precondition, now stated: a project-local `tsci`.
When a build produces no `circuit.json`, build a trivial known-good board with the same `tsci`;
if that fails too, the stage is `could-not-run`, naming the tsci path and version. Costs nothing
on the happy path.
**Value proven by:** the same A/B — global tsci first on PATH → `????  build`, exit 2, the tsci
named; project tsci → `ok`. Mutation: the preflight removed.

**Result — better than asked, because the cause was ours.** Measured first: the global tsci builds
a trivial board on its own and fails only with the Node prefix linked as `node_modules`, which is
what the spine did (`toolchain.parent.parent` is a `node_modules` only for a project-local
install). Now only a project's own modules are linked, and the A/B reads `ok` / `ok` with the
version named — `tsci 0.0.2600` and `0.0.2621`. The preflight exists for a tool that really cannot
build, driven with a fake tsci in tests. Four mutations caught, 511 tests.

### ~~P13 — Sibling scripts are imported, not loaded by path~~ — **DONE `55e7bb8`**
`check_all.load()` (eleven sites) and `check_physics._sibling` import siblings with `importlib`
by file path and register nothing in `sys.modules`: in one process `check_all`'s `parts` is not
`emit_board`'s `parts`, and their `PartError` classes are different objects, so an `except` for
one cannot catch the other. Eight scripts already do `sys.path.insert` + plain import —
`check_physics.py` among them, three lines above its own `_sibling`.
**Value proven by:** `check_all.load` gone; a test asserts one `parts` module per process; suite
green.

**Result.** Both loaders gone; imports inside each check's `call`, so nothing loads before it runs.
Proven behaviourally: a patch on the shared `check_footprints.run` is seen by the buildability
check. The wiring test's docstring turned out to describe a test that did not exist (it grepped
source while claiming to call the runner); it now inspects the names each `call` compiles to.
Three mutations caught, 515 tests.

### ~~P14 — `emit_board` says each thing once~~ — **DONE `f7674b4`**
`emit()` is 186 lines and 39 branches: ten sections, none a function. The power-pin walk is
written four times, the placeholder filter twice, `("needs", "power", "unused_pins")` three times
in `parts.py`, the circuit-glob pair in two files, and the MCU pad loop still carries the
`continue` that G2 removed for parts. Each is a site where the next fix lands once and misses the
rest; three of this sprint's fixes did exactly that before the audit.
**Value proven by:** one power-connection generator, one placeholder filter, one pin-list
constant, one circuit-glob list; each `emit()` section a function with a test; the generated
reference board and both RC boards byte-identical before and after.

**Result.** All of it, byte-identical on four designs. The MCU pad `continue` is gone at both
layers (contract and generator). The composition test's first fixture could not see a swapped
section — no placeholder, so the swap changed nothing — and the mutation tool said so; the
fixture now has every section non-empty and asserts it. Eight mutations caught, 528 tests.

### P15 — Drain the intake
Forty-two `raised` rows in `docs/observations/INDEX.md`, all from the 09-25 reports, none read
since. Retro actions R1.2 and R2.4 both failed on this; R3.2 makes it an item with a box around
it. Each row is reproduced against today's code or `rejected` as superseded, with the commit
that made it so — many will be, since the code they describe has changed under them. Rows that
are already backlog items (P5–P10 map to seven of them) are `acted` with the item's name.
**Value proven by:** no row whose status cell is `raised` — `awk -F'|' 'NF>6 {gsub(/ /,"",$5); s[$5]++} END {for (k in s) print k, s[k]}' docs/observations/INDEX.md` — and
`rejected` used at least once with a reason.

### ~~R7 — The generator chain is named by no skill, no command and no agent~~ [G13] — **DONE `1f769f8` for the one command; reopened as P22 for the documented steps (audit B19), done `c565778`**
`assign_pins`, `emit_board` and `emit_footprint` are the chain that just produced two working
boards, and `spark-design:31` still tells a user to write the `.tsx` by hand. Verified: two
mentions of `parts-researcher` plugin-wide, both non-routes.
**Value proven by:** a user following the documented flow reaching a built board without being told
the script names by someone who already knew them.

**Result.** `/spark:build`; the design skill routed through the chain with hand-written tscircuit
only where the generator stops; the hardware-engineer agent likewise. The documented example, run
as first written, did NOT run: it named a motor driver and no inlet, the generator said so, and
the build stopped on a one-member net. `1f769f8`'s message claims it ran — written from a grep,
not the verdict. Corrected in `7ac2ba1`: the example has the inlet, a test runs it from the
document, and the build was gated on the verdict (11 traces, 9 wires — the commit message says
12 and 10; see the sprint log). The example also needed a
`tactile-button` record the library did not have (the car's, with sources, now shipped). `test_routes.py` keeps every link named and every
route pointing at a script that exists; four mutations caught.

### R8 — Asked for a servo; nothing started looking [G1] **[PO — this is a product decision]**
The first thing the exercise hit and still the largest. No search, no candidate list, no sourcing,
not even "you have no part of this kind". There is a well-specified `parts-researcher` agent and
nothing routes to it. Steps one to three of any new project — decide what you need, find it, write
it down — are unaided.
**Not obvious what it should be**, which is why it is marked PO: a signpost (`--need servo` printing
the schema and the agent's name) is an afternoon; actual sourcing is a product.

### ~~R9 — A part states its rail, but the rail belongs to the design~~ [G5] — **DONE `227f5d4`**
The shipped `l9110s-module` puts VCC on `motor`, which names the bin's 6 V pack. The car runs the
same driver at 7.4 V, so the whole record had to be copied to change one string — and that copy is
now frozen against plugin updates.
**Value proven by:** `{"part": "l9110s-module", "rails": {"VCC": "traction"}}` in a requirements
file, with no duplicate part record.

**Result.** Exactly that, in the loader. The car's copied record is deleted (rc-car `9376dcc`); the
re-emitted board differs in one comment and builds with 13 traces, 0 errors. One mutation escaped
at first because the test re-read a file `parts.load` reads fresh — the fixture could not see it
(W12); it now holds `on_rails` to its copy contract directly. Four mutations caught, 547 tests.

### R10 — Nothing models a link between two designs [G11] **[PO]**
The remote sends a packet the car parses and nothing anywhere can check the two agree. An
exhaustive grep found no notion of it in any schema. The bin has already shown what happens to an
agreement nothing checks — twice.
**Large and not obviously spark's job.** Marked PO.

### P2 — A simulation path that costs no Wokwi minutes
The quota is 50 free minutes and the only source of truth is wokwi.com/dashboard/ci — check
there, do not trust a number written here. A loop that spends them on every check is unusable
either way. The bin already proves a free path exists: `micropython sim/run_on_micropython.py`
runs the real firmware on a real MicroPython runtime locally, 14 checks, exit code as verdict.
**Note:** the `simulation` stage added under P1 costs **no** minutes — generating a diagram is
offline. Only *running* one is billed. So this item is now about a local RUN, not a local emit.
**Value proven by:** a simulation stage that runs to a verdict with the network off.

### ~~P3 — An `spi` role in both board files~~ — **DONE `831f756`**
`assign_pins` spends the whole SPI bus on two LEDs and a button, because no board file records
that those pins are a bus. `grep spi boards/*.json` returns nothing. One `pin_roles` entry each,
reusing the existing bus path — small, and it makes every generated design worse until it is done.
**Value proven by:** a generated design that needs SPI keeps MI/MO/SCK together, and one that does
not still leaves them free for other uses.

**Result, measured rather than tuned.** The penalty is a tie-breaker: below one ability's cost, so
a plain signal still takes a bus pin before it wastes an ADC1 pin. What spent the bus was the
tie among equal ADC2 pins, broken by GPIO number (MOSI 15 before D6 18). My first value, 15,
ranked the bus above ADC1 and sent two plain signals onto the board's scarcest inputs; the
ordering test caught it. The second half of the value statement holds exactly as far as non-bus
pins remain: on the XIAO there is one, so a design with several plain signals uses the bus
whatever the penalty — correctly. Six mutations caught. Both RC boards re-emit byte-identical.

### ~~P4 — Make mutation testing a tool, not a memory~~ — **DONE `997b756`**
W3 is the acceptance bar and it is enforced by nobody: no script, no hook, no CI. It has been
applied by hand three times in one day and correctly each time, which is exactly the situation
that fails the first time somebody is tired. A `scripts/mutate.py` taking a table of
(anchor, replacement) pairs and asserting each turns the suite red — plus the two harness rules
already learned: capture stderr, and assert the anchor is unique before substituting.
**Value proven by:** `python3 scripts/mutate.py <table>` reporting caught/missed per mutation, and
a deliberately-missed mutation reported as missed.

**Result.** Built in R2 itself (retro action R2.1). Its own tests cover the escape, the refusal
of a `find` that matches twice, a red suite, and stale bytecode — the last found by its first full
run. Used on `831f756` and `5689147`: 7 of 7 caught, and three escaped on the first P3 table,
which is the tool doing its job (the tests were not reaching the tie).

### P5 — Audit the remaining checks for what they skip
Done for `check_footprints`'s hole rules, and it immediately found two real defects that had been
invisible on a board declared ready to fabricate. The same audit has never been run over
`check_physics`, `compare_design` or `check_vendor_pins`. W1's guarantee only holds where somebody
has actually looked.
**Value proven by:** each of those three reporting a count of what it could not examine, and a
test per rule that a fixture it cannot read comes back `could-not-run`, not `ok`.

### P6 — `emit_board` implements none of the `host_requirements` it prints
It faithfully prints each part's requirements into the generated file and acts on none of them —
including leaving an H-bridge's inputs floating, which the same file warns against. Either act on
the mechanical ones or stop presenting the list as though the design honoured it.
**Value proven by:** a generated board with an L9110S carries the pulldowns its part record
demands, or the file says plainly which requirements are the reader's to satisfy.

### P7 — `check_design` recommends pins `assign_pins` refuses
Follow the advice and you put a wake button on the BOOT strap. Two components of one product
disagree about the same board.
**Value proven by:** the pins `check_design` suggests are a subset of those `assign_pins` will
place, enforced by a test over both shipped boards.

### P8 — `must_not_float` false-positives on pin-to-pin traces
Including on boards spark itself emits: the generator produces designs that fail the plugin's own
flagship rule. A rule that cries wolf is switched off, and then catches nothing.
**Value proven by:** `check_all` on the generated reference design reports no `must_not_float`
finding, while a genuinely floating input still does.

### P9 — `check_all` drops `subject` from aggregated findings
Two findings both reading "connects to nothing", neither saying what. The aggregator throws away
structure its own checks produce.
**Value proven by:** every aggregated finding names its component or net.
**Audit A11:** three of the four checks already keep the subject; only rules-vs-netlist drops it.

### P10 — Using the documented board override disables `vendor-truth`
The mechanism you are told to use to record what you verified turns off the check that verifies.
**Value proven by:** a project with a board override still gets a `vendor-truth` verdict, against
the override.

### From the sprint 4 audit — 2026-09-29, evening
`docs/observations/2026-09-29-sprint-4-audit.md`: twenty claims (`INDEX.md` B1–B20), read cold at
the end of Sprint 4. The stranger test failed — following the two documents from a fresh directory
reaches no build — so **R7 is reopened as P22**; and the documented first step crashes on the
documented input. Order as before: what misleads or crashes today first, then the refactors.

### ~~P20 — `assign_pins.main` loads through the loader, and signals are derived in one place~~ — **DONE `c3e2e28`**
B1, B10, B16. `assign_pins.py requirements.json` — the first documented step — crashes with
`TypeError` on the `{part, name}` form the same documents show, and on `rails`: it hands raw
entries to `parts.signals_for`, reads the JSON outside any `try`, resolves the project from
`cwd`, and no test calls it. The per-instance signal derivation lives in `emit_board.main`; it
moves to `design` and both mains call it. `parts.load` reads a part file outside any `try`, so a
malformed project part is a traceback through `emit_board` and a "broken chain" through the spine.
**Value proven by:** `assign_pins.py` on `/spark:build`'s own example and on rc-car's
`car.requirements.json` prints a pin per signal, exit 0, the same signals `emit_board` traces; a
malformed part file is `could-not-run` through both. Mutation: the raw entries handed through.

**Result.** `design.load` carries `signals`; both mains consume it; `signal_name` lives with the
loader. The car's pin map assigns (exit 0), both boards re-emit byte-identical, a malformed part
record is a sentence through both mains and the spine. Four mutations caught, 559 tests.

### ~~P21 — A bus is shared, and an instance name does not take a part off it~~ — **DONE `7381fed`**
B2, B3, B18. `signal_name` prefixes an instance's signals (`RANGEFINDER_SDA`) and the bus path in
`assign_pins` finds the bus pin by the signal's *name* matching a board label — so a named
VL6180X lands on D3/D12 "needs nothing special", exit 0 (reproduced); two unnamed I2C parts are
refused ("SDA already taken") when a bus is precisely what they share; and a bus signal named the
vendor's way (`CLK`, `DIN` on `bus: spi`) is placed on any pin with no word (reproduced), against
the assigner's own docstring. A bus signal carries its bus pin apart from its name; signals on one
bus share the pin; a bus signal naming no pin of that bus is refused.
**Value proven by:** a named VL6180X on `.Mcu > .SDA/.SCL`; two I2C parts traced to the same
SDA/SCL; `{"name": "CLK", "bus": "spi"}` refused by name. Mutation: the prefix reaching the bus pin.

**Result.** `BUS_LINES` is where vendor names meet board labels; a bus signal carries its line
through the rename; shared lines share the pin, selects are per device. Two named VL6180X built
with tsci: 12 traces, 0 errors, both on the MCU's SDA/SCL pads. Four designs byte-identical.
Five mutations caught, 569 tests.

### ~~P22 — A stranger can build: the documented steps work from nowhere~~ **[reopened R7]** — **DONE `c565778`**
B5, B6, B19. R7 was called DONE on the strength of the one command; followed as documented from a
fresh directory, `boards.py --list`, `assign_pins.py` and `emit_board.py` refuse "no project here"
where `check_spine` falls back to the library; the emitted board imports `./FireBeetle2Esp32S3`,
which only the never-named `emit_footprint.py` writes; and `parts.py --unverified` as written was a
usage error (fixed). A file in no project is built from the plugin's library and says so;
`emit_footprint` is a named link of the chain; and the stranger test becomes a test — the
documented step commands run from a fresh temp directory produce a board file and its footprint.
**Value proven by:** that test, and the audit's stranger run repeated by hand with nothing but the
two documents, reaching `the chain runs end to end`, gated on the verdict.

**Result.** Every reading script falls back to the plugin's library from nowhere and says so
(only when fallen into, not asked for); `emit_footprint` is a named, typed, runnable link. The
stranger run by hand: every step exit 0, `tsci build` 11 traces 0 errors, the one command end to
end. One mutation escaped twice on the way — a mention in prose satisfied a name test, then a
regex read the prose between code blocks — and the test now holds the command to showing each
link typed. Four mutations caught, 574 tests.

### ~~P23 — Two outputs on one net, across parts and against the board~~ — **DONE `5605065`**
B9. A project part's `VOUT` on `rail: logic, direction: out` is traced to `net.V33` beside the
MCU's own 3V3, exit 0, no note; `parts.validate` checks outputs per rail inside one part only.
An `out` supply onto a rail the module provides, or onto a net another `out` drives, is a short
the file has to name.
**Value proven by:** a probe regulator on `logic` produces a named note in the file and in the
spine's schematic-notes; on its own rail it does not.

**Result.** `outputs_in_contention`, said in the file and on stderr. Grounds excluded — the
first version flagged every design with an inlet, whose GND is rightly `out`; the reference test
caught it. `GROUND_NETS` is one list now, in the generator, read by the spine. Four mutations
caught, 579 tests, four designs byte-identical.

### ~~P24 — `check_design.py` gets a command line~~ — **DONE `fd25f15`**
O4c. `--help` prints `no design at --help`, exit 1: `main(argv)` reads `argv[1]` and nothing else.
argparse, `--json` and a usage line, like every other script.
**Value proven by:** `check_design.py --help` exits 0 with usage; the routes test covers it.

**Result.** argparse, `--json`, `CannotCheck` → could-not-run. One escape on the way (a status
forced to `ok` passed a test that accepted either); fixed with a guaranteed-problem fixture.
Two mutations caught, 589 tests.

### ~~P25 — One vocabulary for the three outcomes, and a test for every rule function~~ — **DONE `ebb8339` + `7361679`**
B16, B17. `EXIT_OK, EXIT_PROBLEMS, EXIT_COULD_NOT_RUN = 0, 1, 2` in 14 files and `"could-not-run"`
in 9, four files naming the middle outcome differently; the upward directory walk at four sites;
`power_note_lines`, `module_power_lines`, `assign_pins.main`, `power_trace`, `trace_width_mm`,
`design.rules_in` and the `check_physics.check_*` rules named by no test. A refactor plus tests;
lands when something touches those files.
**Value proven by:** one definition each, every script importing it, suite green, four designs
byte-identical; every function the audit listed named by a test.

**So far** (`ebb8339`): `outcomes.py`, fourteen scripts importing it, one `walk_up`; suite green, four
designs byte-identical; no mutation, none possible for a pure refactor. **Open:** the named tests
for `power_note_lines`, `module_power_lines`, `power_trace`, `trace_width_mm`, `roles_of`,
`_penalty`, `_why`, `_why_not`, `design.rules_in` and the `check_physics.check_*` rules.

**Done** (`7361679`): every one named; the four rules held to saying so when they cannot look. A dead
guard in `trace_width_mm` found by a mutation that changed nothing, and removed. 603 tests.

### P16 — Lift the bin's wake-polarity check into spark
The bin's `tools/circuit-to-wokwi/lib/checks/wake-polarity.ts` (B3) compares the rail a wake
button is tied to against the level the firmware arms for — the one defect no firmware test could
catch, because every test derives from the constant it checks. spark has no such check (intake
R15) while the board file records the constraint at length.
**Value proven by:** `check_all` on the bin reporting the polarity agreement, and a deliberately
flipped `WAKE_ON_HIGH` reported as a problem.

### P17 — An off-board part is emitted as its header, not its footprint
`on_board: false` is in the VL6180X record and read by nothing (intake R18): the sensor that
sits on a lead was placed on the PCB. The bin's hand-drawn board does it right — a `SensorHeader`
where the module would be.
**Value proven by:** the reference design's rangefinder emitted as a header carrying its pins,
the module's footprint nowhere on the board.

### P18 — evals: run them or delete them **[PO]**
`evals/` holds four cases last run 2026-09-24, results gitignored (intake O7, O9, S11); the plan's
verification of the reviewer roster rests on them. Running them costs model calls; keeping them
unrun costs honesty. Not obvious, so not decided here.

### P19 — findings.py and its fake bench: keep, freeze or drop **[PO]**
1,856 lines and zero resolved findings ever (intake O5, S12); `bench_sim.py` exists only to feed
its tests and prints "what it can pretend to measure" (M6, S13). The plan's review loop (B1–B4)
is built on it. Either that loop gets built on it soon or both go.

### ~~P15 — Drain the intake~~ — **DONE `f35e7df` + this change**
42 rows (first written 43, by eye — audit B12): 38 resolved by what today's code demonstrably
does, 3 reproduced live and fixed (M3, R13, R20), 1 rejected on reproduction (R19). Four items came out: P16, P17, P18 [PO], P19 [PO].

---

## The bin — competing work, and when it is justified

The bin is the test case, so bin work earns its place when it **exercises or proves spark**.
Fixing a bin defect that spark found is proof; fixing one spark cannot see is just bin work.

### B1 — Identify the audio module **[PO — blocked on Petr]**
Everything in the bin's audio path waits on this and it is a look in a drawer. microSD slot means
DFPlayer Mini; micro-USB and "Voice Module V1.0" means DFR0534; pads marked BCLK/LRC/DIN means the
I²S amp. Petr has chosen the I²S route on the merits; the module's identity is still unconfirmed.

### B2 — Fab blockers — **done: five of seven closed, `make check` green**
Blocker 7, the 0.225 mm annular rings, was found by spark within minutes of the checker learning
to read pill holes — **still the best evidence the product works that this project has.** It is
parked deliberately: a fabrication-process limit, and the board is not being ordered.

### B3 — Deep sleep never wakes — **done**
Both wake sources now assert HIGH and the firmware arms `WAKEUP_ANY_HIGH`, a genuine OR.

What it left behind is the part worth keeping: a mutation **no firmware test could catch**.
Reverting `WAKE_ON_HIGH` left all 113 tests green, because every one of them derives from that
constant — the pull, the pressed level, the interrupt polarity — so flipping it flips them with
it. It is only wrong relative to the copper. `wake-polarity.ts` now compares the rail the button
is tied to against the level the firmware arms for.

**Still unproven, and not provable here:** Wokwi does not wake an ESP32 from a GPIO at all, so
whether the chip really wakes is a bench test.

---

## Proposed to drop **[PO]**

Not wrong, never worth doing first. A scrum-master review measured that only 27.4% of 16,561 lines
of churn served the spine, while these consumed a large share.

| item | why drop | evidence |
| --- | --- | --- |
| **N1** — bridge checks into the findings store | the store holds 20 findings, 0 resolved, in two days. Feeding it faster does not empty it. | `findings.py` is 11.2% of all churn |
| **N2** — `findings.py next --actionable` | serves N1's store | — |
| **N3** — rebuild the evals | 54 of 64 commits postdate the last eval run, and `evals/results/` is gitignored, so the argument resting on them cites evidence nobody else can see | scrum review, 2026-09-25 |

Dropping means **deleting the backlog item**, not the code. Say the word and they go.

---

## Intake, not backlog

`docs/observations/INDEX.md` holds ~37 raw observation rows. It is **intake**: claims arrive there
and are reproduced or rejected. A claim becomes work only by being promoted to a PBI here.

It has never drained — no row has changed status since being written, and `rejected` has never
been used once. The first retro's action addresses that.
