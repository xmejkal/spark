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
| **B** | *"I have these modules, wire them up"* | partial — the skill describes it, nothing drives it |
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
| 1. Unit test | Does the check bite? | 142 tests. **Every check must have a design that violates it** |
| 2. Self-refutation | Can it cry wolf? | Each rule needs a case that looks wrong and is fine |
| 3. Eval | Does the *agent* find it? | `evals/`, reported as a rate over *n* runs, with a no-plugin baseline |
| 4. Reality | Did it hold? | The bin: `make check`, and eventually a bench |

**The rule that keeps this honest: a refusal is not a pass.** "I could not look" and "I looked and
found nothing" must be different answers with different exit codes. Several checks were rewritten
for this.

---

## 4. Done

Evidence, not assertion. 142 tests, 6 skills, 10 scripts, 1 agent (5 dimensions), 3 evals,
and a library of verified board definitions.

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
| Measurement discipline | `bench_sim.py` marks everything `simulated`; nothing that costs money may rest on it |

**The proof it works:** applied to a real board, this stack plus a four-lens review found 20+
real defects, including several that would have cost a fabrication run.

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

**S5 — Use case B end to end: modules in, schematic out.**
The largest gap between what the skills describe and what they drive.
*Done when:* "I have a FireBeetle, an L9110S and a VL6180X" produces a `board.tsx` that builds
and passes every check, without hand-holding.

**S6 — Evals for the checks that have none.**
Three evals exist and predate half the tooling.
*Done when:* each new check has an eval with a baseline, so we know the agent uses it.

### Later

**S7 — Idea → parts (use case E's missing half).** Needs a parts-sourcing capability.
**S8 — Enclosure from the board.** `circuit.json` has no outline and no component heights today;
that gap is the first thing to close.
**S9 — Analog simulation.** `circuit-json-to-spice` → ngspice → assertions.
**S10 — An unattended loop.** A workflow that runs the review, works the top finding, re-checks,
and stops at anything needing a human. Only once 1–3 are trusted.

### Debt

- **The `examples/` design and `evals/fixtures/` predate the current board** and describe a
  machine that no longer exists.
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
