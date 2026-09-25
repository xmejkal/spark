# spark — what it is, what works, what's next

> **This file is NARRATIVE, not a queue.** As of 2026-09-25 the one ordered list of work is
> [`scrum/PRODUCT_BACKLOG.md`](scrum/PRODUCT_BACKLOG.md). What stays here is how the product got
> where it is and what was learned on the way — worth reading, not worth pulling from.
> §5 below is kept as the record of what was queued before the consolidation; everything in it
> that still matters is a PBI now, and everything that is not, is not happening.

Working document. `README.md` is for someone installing it; this is for someone building it.

Updated 2026-09-24.

---

## 1. What we are building

**A tool that takes an electronics idea to files you can order and firmware you can flash, with
every step checked — usable by a person or by an agent.**

Petr's words, which are the spec: *a tool encapsulating the process of designing a circuit with
specific parts and values, testable, with code tested on it, to a 3D model later — so that
Claude, an agent, or a human can generate the files from an idea.*

Three properties, in priority order:

1. **Every claim is checked against something outside itself.** The failure this exists to
   prevent is a design that agrees with itself and is wrong. That is not a nice-to-have; it is
   the product.
2. **Optimised for an agent, validated by a human first.** Every tool answers with data and a
   distinct exit code, so a caller that is not a person can act on it. Humans gate the important
   decisions until the loop has earned trust.
3. **No bloat.** A check that cannot fail, a field nothing reads, and an agent where a script
   would do are each a cost with no return.

### The shape

```text
idea ──▶ parts ──▶ schematic ──▶ layout ──▶ fab files
                       │            │           │
                       ▼            ▼           ▼
                   firmware ──▶ simulation ──▶ bench ──▶ enclosure
                       └──────── checks run at every arrow ────────┘
```

### What decides script vs agent

An **agent** earns its place only with at least one of: context isolation (it must not read the
project's opinion of itself), restricted tools, fan-out, or context budget. Everything with one
right answer is a **script** — faster, free, and it cannot change its mind. This test has been
applied and it keeps moving work out of agents: four of today's worst board findings turned out
to be arithmetic.

---

## 2. Use cases, and which to start with

| # | Use case | State |
| --- | --- | --- |
| **A** | *"Here is my design — check it before I spend money"* | **works** |
| **B** | *"I have these modules, wire them up"* | **works** — `parts.py` → `assign_pins.py` → `emit_board.py` |
| **C** | *"Here is a photo of a dead board"* | works (`spark-reverse-engineer`) |
| **D** | *"Write and prove the firmware before hardware exists"* | works (`spark-simulate`) |
| **E** | *"Take this from idea to ordered files"* | **not built** — the end-to-end goal |
| **F** | *"Give me an enclosure"* | not built |

**Start with A, and keep starting with A.** It is the only one with a proven return: on a real
board it found a drill that would have scrapped the batch, a 4 V tantalum on a 6.4 V rail, a BOM
ordering a 100 nF part where the schematic said 1 µF, and a firmware crash on the shipped path.
It is also the use case an agent can run unattended today.

B is the natural second, because E is B plus the parts step, and B is where the value per unit of
work is highest.

---

## 3. How we validate

Four rungs. A thing is only as trustworthy as the highest rung it has climbed.

| Rung | Question | Mechanism |
| --- | --- | --- |
| 1. Unit test | Does the check bite? | 216 tests. **Every check must have a design that violates it** |
| 2. Self-refutation | Can it cry wolf? | Each rule needs a case that looks wrong and is fine |
| 3. Eval | Does the *agent* find it? | `evals/`, reported as a rate over *n* runs, with a no-plugin baseline |
| 4. Reality | Did it hold? | The bin: `make check`, and eventually a bench |

**The rule that keeps this honest: a refusal is not a pass.** "I could not look" and "I looked and
found nothing" must be different answers with different exit codes. Several checks were rewritten
for this.

---

## 4. Done

Evidence, not assertion. 216 tests, 6 skills, 14 scripts, 1 agent (5 dimensions), 4 evals,
and libraries of verified boards and parts.

| Capability | Proven by |
| --- | --- |
| Pin capability, I²C clashes, double-booked pins | `check_design.py`, tested |
| Rules vs the built netlist | `compare_design.py` — found I²C pull-ups missing since the rule was written |
| Findings as durable state | `findings.py` — structural identity, dedupe, `regressed`, measurement registry |
| **Vendor truth** | `check_vendor_pins.py` — re-derives the pin map from the vendor's header. Catches `D3 = GPIO3` |
| **Physics** | `check_physics.py` — found that *no capacitor declared a voltage rating*, the mechanism behind the tantalum |
| **Buildability** | `check_footprints.py` — drill vs pin diagonal, annular ring, via class, package vs value, cross-pluggable connectors |
| Simulation without hardware | `spark-simulate` — fake `machine`, real MicroPython, Wokwi |
| Photo → netlist | `spark-reverse-engineer` |
| Design review by dimension | `design-reviewer`, 5 dimensions, isolated from the project's own prose |
| **The order** | `check_bom.py` — found one supplier part ordered for two capacitances |
| **One call for all of it** | `check_all.py` — six checks, four outcomes, so "not asked" never reads as "clean" |
| **A board library** | `boards/` + `scripts/boards.py` — adopt a verified board with one line; the contract refuses decisions in a facts file |
| **Pin assignment** | `assign_pins.py` — spends the scarce pins last and explains every choice; refuses rather than half-assigning |
| **A part library** | `parts/` + `parts.py` — what a module asks of its host, as data; and `--unverified` names every number nobody has checked |
| **Modules in, board out** | `emit_board.py` — a module list becomes a `board.tsx` that builds, routes and passes the checks, and that says which of its own decisions are drafts |
| **Firmware vs board** | `check_firmware.py` — matched on GPIO, not on constant names, so renaming a constant cannot silently switch the check off |
| Measurement discipline | `bench_sim.py` marks everything `simulated`; nothing that costs money may rest on it |

**The proof it works:** applied to a real board, this stack plus a four-lens review found 20+
real defects, including several that would have cost a fabrication run.

---

## 4b. What the evals actually say, and what it changes

**This section previously drew a conclusion from one arm of one run, selected from a corpus that
trends the other way. Here is the whole record.**

| run | case | with plugin | without | delta |
| --- | --- | --- | --- | --- |
| 07:52 | deep-sleep-pins | [1,1,1] | [1,0] | **+0.50** |
| 09:19 | deep-sleep-pins | [1,1,1] | [1,1,1] | 0.00 |
| 09:19 | testing-without-hardware | [1,1,1] | [0,1,0] | **+0.67** |
| 09:27 | finds-unswitched-power | [0,0,0] | [0,0,0] | 0.00 |
| 09:30 | finds-unswitched-power | [1,1,1] | [1,1,0] | **+0.33** |
| 16:59 | finds-assembly-problems | [0,0,1] | [0] | **+0.33** |
| 17:16 | finds-assembly-problems | [1,1,0] | [1,1,1] | **−0.33** |

Five of six two-armed runs are ≥ 0; the mean delta is about **+0.30**. The largest effect measured,
`testing-without-hardware` at +0.67, was not mentioned here at all. The single negative result was
cited as if it were the corpus.

**And that negative run measured nothing.** Its `turns` were `[1,1,1]` in *both* arms: one turn
each, so zero tool calls, so no script ever executed. The arms differed only by text in the context
window. The same case had read +0.33 seventeen minutes earlier; at n=3 one run's difference *is*
0.33, so the swing sits at the resolution of the instrument. `finds-unswitched-power` scored
all-zero in both arms at 09:27 and all-one at 09:30 — a total flip in three minutes, which means
the harness itself was not stable in that window. Two cases still use `runs: 1`, and one run is not
a rate.

**Every run in which the tools were actually used is positive.** The evals as built cannot
falsify a claim about the product, because the product does not run inside them.

### What survives

The strategic direction — deterministic checks ahead of reviewer polish — is probably still right,
but it has to rest on the argument below rather than on a delta that is noise. A script runs in a
second, costs nothing, and cannot change its mind. That is the case; the eval never made it.

| Found by | Examples |
| --- | --- |
| **A script, never by a reviewer** | a BOM ordering 100 nF where the schematic said 1 µF; capacitors with no voltage rating at all; a 0.9 mm drill against a 0.905 mm pin; vias left at a tool's floor; a board file disagreeing with its vendor's own header |
| **A library with provenance** | that the L9110S's input threshold is absolute and not ratiometric — the fact that decides whether 3.3 V logic drives a 6 V part at all |
| **Being run at all** | the checks only catch what runs; a review that does not happen catches nothing |

So: deterministic checks first, libraries with provenance second, generators third. The reviewers
are **not** frozen — nothing measured says they should be. They are simply not the bottleneck while
the deterministic half has a broken front door (§4c).

**The evals need rebuilding before they are cited again.** `schema_version: "1.1"` with
`context.add_dirs` so a script can actually run, `tool_used` graders with `arm: both` so a run that
used no tools is visible as such, and n large enough that 1/3 of a run is not the unit of measure.

---

## 4c. The audit — what three independent reviews found, and the one thing they all found

Three reviewers were given the plugin cold: one auditing for gaps, one using it as a stranger on
their own project, one testing whether an unattended agent could drive it. They worked separately, and their reports are kept verbatim in
`docs/audit-2026-09-24/` — roughly sixty findings, more detail than a backlog should carry.
**All three independently opened on the same defect**, and everything below was reproduced here
before it was written down.

### The systemic finding

**Every instrument built to say "this is fine" reports success when it did not look.** The same
defect, six places — including the ones whose own docstrings are essays warning about it:

| where | what it does |
| --- | --- |
| the eval cited in §4b | both arms ran zero tools; read as a measurement of the product |
| `check_all.py` `vendor-truth` | folds `could-not-run` into a notes field, returns **`ok`**, exit 0 |
| `check_all.py` `pin-capability` | calls `check_design.check()` — **a function that has never existed**; the flagship check has never run through the runner once |
| `test_..._wired_into_the_runner` | greps the runner's *source text* for `load("check_design")`. Verifies the check is **named**, not that it **runs** |
| `test_a_missing_circuit_is_not_treated_as_clean` | asserts `== []`, which is precisely "treated as clean". The comment above it says it must not do that |
| `Check.run`'s `except Exception` | `check_bom` raises `SystemExit`, a `BaseException`, so one check's missing file kills all seven and exits 1 = "problems found" |

**216 tests pass.** They pass because they test the boxes and never the seams. Every confirmed
defect today is in a seam: runner→check, board file→role vocabulary, part file→pin numbering, rail
name→net name, README→code, skill prose→script CLI.

This also explains the §4b error. The eval's result was tested; the seam between the eval and the
product — *did the product run?* — was not.

### The rule that would have caught all six

> **A test must run the thing, not read it.** No assertion on source text. No assertion that is an
> arithmetic identity of the function under test. Every check must be exercised *through the
> runner*, with an input that makes it fail.

The plugin's own rung-1 rule is "every check must have a design that violates it". The runner was
exempt from it, and that is exactly where the defect was. Four more tests assert their own
premises: `test_the_board_is_big_enough_for_what_is_on_it` (an identity of `place()`),
`test_both_doors_agree` (a string compared to itself), and two comparing `0, 1, 2` to each other.

### The generator emits a board that would destroy a part

`emit_board.py` writes both bridged amplifier outputs to one net:

```jsx
<trace from=".Dfr0534Module > .SPKP" to="net.SPEAKER" />  {/* bridged amplifier output — never ground either side */}
<trace from=".Dfr0534Module > .SPKN" to="net.SPEAKER" />
```

The part file's own warning is printed on the trace that shorts it. `RAIL_NETS` maps a rail name to
exactly one net, and both outputs declare `"rail": "speaker"`. Emitted under a banner reading *"The
CONNECTIONS are derived and trustworthy… Nothing here is guessed."*

Beside it, `pinLabels` are numbered by **dict insertion order**, not by the module's physical
pinout — `pin1: "AIA"` on a header whose first pad is BIA — so every trace to a module lands on the
wrong pad. And the emitted `import { X } from "./X"` references a footprint module the plugin does
not ship, so the output does not build; `emit_board.py` exits **0** anyway.

### The two shipped boards do not speak the same language

`xiao-esp32-c6.json` says `boot_log_tx`; `firebeetle2-esp32s3.json` says `console_uart`.
`check_design.py` hard-codes the first, `assign_pins.py` hard-codes the second. Nothing validates
role names. So a serial-parsing part on the FireBeetle's console UART passes silently, and
`assign_pins`'s 40-point console penalty never fires on the XIAO. Same hazard, one board checked.

### Nobody can install it

All 14 scripts are mode `100644`. Every skill invokes them as `./scripts/x.py`, and the
`allowed-tools` grants whitelist exactly that form — which cannot execute. `findings.py` tells the
user to run **`spark init`**, which does not exist anywhere but in that error string. `README.md`
says v0.1.0 against `plugin.json`'s 0.6.0 and documents none of the 14 scripts, the board library
or the parts library.

### What this changes

The order in §4b still holds — deterministic checks carry this product — but it now has a
precondition that outranks everything: **the deterministic half has a broken front door.** An
instrument that reports clean without looking makes every other system here unverifiable, and it is
the reason a session's worth of "everything is in step" has to be re-earned rather than trusted.

(The reference project's own `make check` calls each script directly, not through `check_all.py`,
so its eleven gates are genuinely green. The plugin's front door is the broken part.)

---

## 4d. State on 2026-09-25 — what runs, measured not remembered

298 tests. `claude plugin validate` passes. 4 skills, 2 commands, 1 agent, 15 scripts, 2 boards,
4 parts. Everything pushed to `xmejkal/spark`.

### The interface, before and after two days

| | was | now |
| --- | --- | --- |
| scripts a fresh install can run | **0 of 14** (all mode 100644) | 15, all `100755` |
| checks the documented review command runs | **3 of 7** | **6 of 7** |
| skills competing for "check my design" | 3 | 1 |
| parts a second project can add | **0** (the flag was unreachable) | any |
| `spark init` | a string inside an error message | `/spark:init` |
| README version vs `plugin.json` | 0.1.0 vs 0.6.0 | both 0.6.0 |

### The defect class this was all one instance of

**Every instrument built to say "this is fine" reported success when it had not looked**, and the
tests passed because they exercised the boxes and never the seams. Found and fixed, each with a
test that fails without it and a mutation run proving so:

| where | what it did |
| --- | --- |
| `check_all.py` pin-capability | called `check_design.check()`, a function that has never existed. The flagship check had never once run through the runner |
| `check_all.py` vendor-truth | folded "could not look" into a notes field and returned `ok` |
| `check_all.py` physics | discarded its own `could-not-run` findings |
| `Check.run` | `except Exception` let `SystemExit` past, so one check's missing file killed the other six and exited 1 = "problems found" |
| `check_bom.check_design_warnings` | returned `[]` for a file it never opened |
| `check_footprints` hole rules | silently skipped 14 of 74 holes on the real board, four of them the obround shape its own docstring calls its flagship defect |
| `check_footprints` footprint lookup | read `pcb_component.footprinter_string`; the engine moved it to `cad_component`, so **two rules examined nothing and said nothing** |
| `findings.py` `validate --apply` | against an empty `circuit.json` — what a half-failed build leaves — retired **19 of 20 findings** and reported it as success |
| an empty netlist, everywhere | four checks examined nothing, found nothing, and reported `ok` |
| the test written to catch all this | asserted that the string `load("check_design")` appeared in the runner's SOURCE. It verified the check was *named*, not that it *ran* |

**The rule that now governs the suite:** a test must RUN the thing, not read it. No assertion on
source text, none that is an arithmetic identity of the function under test, and every check
exercised through the runner with an input that makes it fail. Every repair this week was
mutation-tested — the defect put back, the suite required to go red — and that run has twice
caught a rule I had just written that no test covered.

### What the bin taught the library

The one real project is the test case, and working it produced checks and contract rules that
generalise:

- **a three-pin semiconductor with no supplier part** is now a BOM problem. Its footprint cannot
  say which pad is the gate, and the board's high-side switch was a bare `sot23` with no part
  number — tscircuit binds pad 1 to the drain, every real SOT-23 P-FET is gate-source-drain, so
  fitting any actual part shorts a 2 A rail through a GPIO. The line had no *value* either, so
  the existing rule exempted it.
- **cross-pluggable connectors are decided by pad geometry**, not by a name. Three components on
  the reference board carry no footprint string at all, including both plug-in modules — the
  exact parts whose swap puts 6 V on a logic input.
- **`pin_order`**: which pad is pin 1 is a fact about the module. The generator numbered pads
  from the order the pins appeared in a JSON file.
- **`body_mm` carries provenance**, and a part nobody measured makes the generator refuse rather
  than invent 16 x 12 mm.
- **an output is not a rail.** Both halves of a bridged class-D amplifier declared `rail:
  speaker` and were wired to one net — a short, under a banner reading "nothing here is guessed".
- **a supply may sit on two pads; a signal may not.** The DFR0954 brings VCC and GND out twice.
- **scope**: an assertion with no stated scope is the defect. One FireBeetle SKU covers two
  different power designs; four VL6180X breakouts share no pinout; "the DFRobot MP3 one" names
  four products. Board and part files now say which thing they describe.

### Still true, and still the gap

`check_all` answers in prose strings; `findings.py` wants `{dimension, anchors, what,
consequence, severity}`. **Nothing bridges them**, so only a model can write to the store — in a
tool whose measured value is the half that is not a model. That is the next structural piece, and
it needs `findings.py sync` in the same change or machine findings never retire.

---

## 5. Backlog

Ordered by value. Each item says what it is worth and how we will know it worked.

### Now

**N1 — Bridge the checks into the findings store.** `check_all` returns prose; the store wants
`{dimension, anchors, what, consequence, severity}` with anchors validated against the netlist.
Today only a model can write findings, which is the wrong half of this product doing it. The
checks already carry the structure — `check_physics` returns `{rule, subject, detail, severity,
fix}` and knows its net and component names — so the mapping is mechanical. Build it as an
`anchors` list filled at each Finding's construction site plus `check_all --findings out.json`,
not as a separate script that would re-run everything.
*What would make it a mistake, and must ship in the same change:* machine findings are
self-clearing — widen a trace and the rule stops firing — so without a `findings.py sync
--source check` that retires what the current run no longer reports, the store fills with stale
entries and the human list becomes noise. Build `sync` with it or not at all.

**N2 — `findings.py next --actionable`.** The live store is 11 blocked of 20 and `next` ranks
blocked first, by design, because clearing one is minutes of a person's time. For an unattended
caller that is a deadlock on turn one. One flag.

**N3 — Rebuild the evals so they can exercise the product.** Every case inlines its design in the
prompt and none references a path on disk, so **no case can run a script** whatever its turn
count. That is why the conclusion in §4b could not have been falsified. Needs
`schema_version: "1.1"` with `context.add_dirs`, `tool_used` graders with `arm: both`, and n
large enough that one run of three is not the unit of measure. Grade knowledge-recall cases and
judgement cases **separately** — they behave differently and averaging them is how the last
conclusion went wrong in both directions.

**N4 — Leaf checks must count what they skipped.** Done for `check_footprints`'s hole rules; the
same audit has not been run over `check_physics`, `compare_design` or `check_vendor_pins`. The
determinism argument only holds if the script reports honestly that it ran.

### Next

~~**S4 — Extract the board plugin system into spark.**~~ **done.** The contract, the resolver and
a library of verified definitions now ship with the plugin. Criterion met and demonstrated: a new
directory containing only `boards/active.json` resolves the full FireBeetle definition — 25 pins,
22 wake-capable GPIOs — with nothing copied. A project's own definition still wins.

The resolver writes `.spark/board.json` and every consumer reads that, which deleted a second,
partial implementation of the same lookup in TypeScript rather than growing it to search two
directories.

**S5 — Use case B end to end: modules in, schematic out.** *in progress.*
The hardest step is done: `scripts/assign_pins.py` works out which pin each signal should go on,
and says what each choice cost. It beat the hand-made map on the project it was written against
— it keeps the console UART and the on-board button free, which the hand map spent.

The judgement it encodes is one number: what an unused capability costs against what a pin's
existing job costs. Ranking those separately meant a zero-capability console pin always beat a
plain wake-capable pin, which is backwards on a chip with twenty-two wake pins and one console.

`scripts/parts.py` + `parts/` now supply the other half: a module list produces the signals, and
the signals produce the pin map. `{"parts": ["l9110s-module", "vl6180x-breakout",
"dfr0534-module"]}` is enough input.

The schema splits deliberately. `needs` is strict, because what a part asks its host for IS
uniform across parts — that is what makes this data rather than prose. `facts` is open, because a
motor driver's facts and a rangefinder's have nothing in common, and one schema over both
degenerates into `{name, notes}`. Every fact carries a source and whether anyone checked, and an
unverified number must say what depends on it or not be carried.

`scripts/emit_board.py` closes it. `{"board": "firebeetle2-esp32s3", "parts": [...]}` produces a
`board.tsx` that `tsci build` compiles, that routes, and that passes the buildability check out of
the box — because it sets the fabrication defaults rather than inheriting a tool's floor.

What it is honest about matters as much as what it emits. The connections are derived and
defensible; the PLACEMENT is a column, chosen because it does not overlap, and the file says so
at the top. It also names what it has not decided — mounting holes, connector keying, trace
widths — and carries each part's requirements of its host into the file, because a design rule
left in a library nobody opens is not enforced.

It refuses usefully too: a module list is a list of CONSUMERS, so nothing sources the motor rail,
and it says that instead of emitting a file that silently fails to route.

*Remaining, and it is a design activity rather than a gap:* real placement.

**S6 — Evals for the agent-shaped gaps.** *in progress.*
`finds-assembly-problems` added: does the manufacturability dimension find what only judgement
finds, and — the harder half — does it stay out of the deterministic checks' territory? It is
graded both ways, with penalties for repeating arithmetic a script already owns.
*Note on scope:* a deterministic check does not need an eval. It has unit tests, and an eval
measures the agent. What needs one is every place the agent has to choose.
*Done when:* the manufacturability eval has run with a baseline, and one case covers whether the
review loop actually invokes `check_all.py` rather than reasoning from the design alone.

### Later

**S7 — Idea → parts (use case E's missing half).** Needs a parts-sourcing capability.
**S8 — Enclosure from the board.** `circuit.json` has no outline and no component heights today;
that gap is the first thing to close.
**S9 — Analog simulation.** `circuit-json-to-spice` → ngspice → assertions.
**S10 — An unattended loop.** A workflow that runs the review, works the top finding, re-checks,
and stops at anything needing a human. Only once 1–3 are trusted.

### Debt

- ~~The `examples/` design and `evals/fixtures/` predate the current board.~~ Resolved, and the
  assessment was half wrong: `evals/fixtures/` was genuinely orphaned and is deleted, but
  `examples/smartbin.design.json` is a FROZEN regression fixture and being out of date with the
  live project is the point. Its one real defect was a `board` path into a sibling checkout that
  stopped existing when the definitions moved — dead metadata nothing read.
- **Plugin prose is long.** ~1,100 lines of skill markdown; some is reference, some is repetition.

---

## 6. How to work this

1. Pick the top item. They are ordered; the order is the argument.
2. Say what it is worth before how it will be done.
3. Build the check before or with the thing, never after — every gate added after the fact here
   found something that had already been broken for weeks.
4. Commit as it lands.
5. When something is genuinely uncertain, say so and record it as unmeasured. A tool that reports
   "I do not know" is worth more than one that guesses.
