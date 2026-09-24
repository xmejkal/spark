# spark — what it is, what works, what's next

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

**2026-09-24, `finds-assembly-problems`: with-plugin 0.67, no-plugin baseline 1.00, delta −0.33.**

The baseline scored perfect. It independently found the mating 2-pin connectors, the crimp order
that puts 6 V across the H-bridge outputs, the absent mounting holes and the consequences of each
— unprompted, with no plugin loaded. This is the second eval to say the same thing: the earlier
`deep-sleep-pins` case scored 1/1 in both arms.

**The conclusion is uncomfortable and it should be acted on: the model does not need help
reviewing. Asking it to review better is not where this product's value is.**

That kills a line of work. Writing more reviewer dimensions, tuning reviewer prompts and
sharpening rubrics is effort spent on the half the model already does well — and the extra
context may actively cost something, which is what a negative delta means.

What the model demonstrably cannot do, and what every defect this week that a review MISSED had
in common:

| Found by | Examples |
| --- | --- |
| **A script, never by a reviewer** | a BOM ordering 100 nF where the schematic said 1 µF; capacitors with no voltage rating at all; a 0.9 mm drill against a 0.905 mm pin; vias left at a tool's floor; a board file disagreeing with its vendor's own header |
| **A library with provenance** | that the L9110S's input threshold is absolute and not ratiometric — the fact that decides whether 3.3 V logic drives a 6 V part at all |
| **Being run at all** | the checks only catch what runs; a review that does not happen catches nothing |

A model asked to review will *sometimes* notice a wrong drill. A script notices every time, in a
second, for free. That difference — not cleverness — is the product.

**So the priorities change:**

1. **Deterministic checks first.** Every defect class that can be settled by arithmetic should be,
   and should move out of the reviewer's remit when it is. *Done so far under this rule:*
   `check_firmware.py`, which takes firmware-hardware agreement off the reviewer entirely.
2. **Libraries with provenance second.** Facts the model would otherwise invent, carrying sources
   and an honest `verified: false`.
3. **Generators third.** Artifacts, not opinions.
4. **Reviewers last, and unchanged.** They are already good enough. Leave them alone.

**And the evals change shape.** Grading review QUALITY measures the model, not the product. What
needs grading is whether the workflow fires and uses the tools — `tool_used` graders on the skill
and on `check_all.py` — because that is the thing that varies and the thing the plugin controls.

---

## 5. Backlog

Ordered by value. Each item says what it is worth and how we will know it worked.

### Now

~~**S1 — Move the BOM check into the plugin.**~~ **done.** `scripts/check_bom.py`, 13 tests, and
the project-specific regex turned out to be dead code — "has a value and no supplier part" is the
rule on any board, with nothing to configure.

~~**S2 — Wire the new scripts into `spark-review`.**~~ **done.** `scripts/check_all.py` runs all
six deterministic checks in one call and answers once, so adding a check no longer means editing
a skill. It reports four outcomes, not two: the usual pair plus `could-not-run` (asked, and still
could not look) and `skipped` (never asked). Conflating those last two is how a review that ran
one check out of seven looked exactly like one that ran all seven.
*Still open from S2:* an eval showing the combined loop finds what the ad-hoc council found.

~~**S3 — A `manufacturability` dimension for `design-reviewer`.**~~ **done.** Five dimensions
now. It is explicitly told what `check_footprints.py` already owns — drill, ring, via class,
package-holds-value, cross-pluggable connectors — so it cannot duplicate arithmetic a script
settles. What is left for it is what a number cannot: assembly order, what a soldering iron can
reach once the tall parts are in, and what the board fails to tell whoever builds it.
*Still open:* an eval scoring it against today's findings as ground truth (see S6).

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
