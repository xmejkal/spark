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

## Sprint 3 — pulled

See [`SPRINT.md`](SPRINT.md). Goal: **spark reports what it did and nothing less.**

| id | item | size |
| --- | --- | --- |
| ~~P11~~ | A design is loaded once, in one place, and `main()` is tested — **done `0c21ef5`** | M |
| ~~P12~~ | The spine tells a toolchain fault from a design fault — **done `c4d0582`** | S |
| ~~P13~~ | Sibling scripts are imported, not loaded by path — **done `55e7bb8`** | S |
| P14 | `emit_board` says each thing once | M |

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

### P14 — `emit_board` says each thing once
`emit()` is 186 lines and 39 branches: ten sections, none a function. The power-pin walk is
written four times, the placeholder filter twice, `("needs", "power", "unused_pins")` three times
in `parts.py`, the circuit-glob pair in two files, and the MCU pad loop still carries the
`continue` that G2 removed for parts. Each is a site where the next fix lands once and misses the
rest; three of this sprint's fixes did exactly that before the audit.
**Value proven by:** one power-connection generator, one placeholder filter, one pin-list
constant, one circuit-glob list; each `emit()` section a function with a test; the generated
reference board and both RC boards byte-identical before and after.

### R7 — The generator chain is named by no skill, no command and no agent [G13]
`assign_pins`, `emit_board` and `emit_footprint` are the chain that just produced two working
boards, and `spark-design:31` still tells a user to write the `.tsx` by hand. Verified: two
mentions of `parts-researcher` plugin-wide, both non-routes.
**Value proven by:** a user following the documented flow reaching a built board without being told
the script names by someone who already knew them.

### R8 — Asked for a servo; nothing started looking [G1] **[PO — this is a product decision]**
The first thing the exercise hit and still the largest. No search, no candidate list, no sourcing,
not even "you have no part of this kind". There is a well-specified `parts-researcher` agent and
nothing routes to it. Steps one to three of any new project — decide what you need, find it, write
it down — are unaided.
**Not obvious what it should be**, which is why it is marked PO: a signpost (`--need servo` printing
the schema and the agent's name) is an afternoon; actual sourcing is a product.

### R9 — A part states its rail, but the rail belongs to the design [G5]
The shipped `l9110s-module` puts VCC on `motor`, which names the bin's 6 V pack. The car runs the
same driver at 7.4 V, so the whole record had to be copied to change one string — and that copy is
now frozen against plugin updates.
**Value proven by:** `{"part": "l9110s-module", "rails": {"VCC": "traction"}}` in a requirements
file, with no duplicate part record.

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
