# Decisions that are settled

Read this after a context clear. It is the short list: what was decided, and why, so none of it
gets re-litigated. Everything still open is a card on a board — spark's
(https://github.com/users/xmejkal/projects/2) or the bin's (/projects/1); `docs/observations/INDEX.md` is raw intake.

Last condensed: 2026-09-25; the product rules and the cautions revised 2026-10-09 (P146).

---

## The goal, in one line

**idea → parts → schema → simulation** (3D and PCB later). Working schema and code come first.
Anything not on that spine is a distraction, however interesting.

## The rule everything else derives from

> **A check that could not look must never read as a check that passed.**

Four outcomes, never two: `ok` · `problems` · `could-not-run` · `skipped`. `scripts/check_all.py`
has a single function, `answer()`, that decides status, so no check can invent a third way to say
"fine". This rule was written after a runner reported `ok` on a flagship check that did not exist.

Its corollaries, each learned from a real defect:

- **A test must run the thing, not read it.** No assertion on source text; no assertion that is an
  arithmetic identity of the function under test. (A test once asserted `load("check_design")`
  appeared in the source — the check was *named*, never *run*.)
- **Mutation testing is the acceptance bar.** Re-introduce the defect; the suite must go red. A fix
  without a failing-first test is not a fix. Repeatedly this exposed rules with no test at all.
- **Never change a test to make it pass.** Change the decision or the docstring first; the test
  follows the decision. (Petr's standing instruction, and the reason three red tests once led to a
  design change rather than three edits.)
- **State the scope of an assertion.** Moved below, to [Product rules](#product-rules) (W5).

## Locked technical decisions

| decision | why | where |
| --- | --- | --- |
| **No KiCad footprint converter** | Two councils killed it. 18 of 27 footprints already convert to geometry identical to what exists — reproduced to the micron. | `INDEX.md` C1 |
| **The pill-hole gap is a reader gap, not a source gap** | Pill holes carry `hole_width`/`hole_height`; the rules read `hole_diameter`. ~10 lines in `check_footprints`, not a new pipeline. | `INDEX.md` C2 |
| **CLI over MCP** | An MCP server loads its tool schema into context every session; a CLI costs nothing until called. | user, explicit |
| **Don't reinvent KiCad/Wokwi/tscircuit** | They already have shapes, boards, 3D, simulation. spark's value is the judgement between them. | user, explicit |
| **Audio is I²S (MAX98357A / DFR0954)** | Petr chose it over the DFR0534 UART module. The module is identified: B1 (the bin's #1) closed 2026-10-06 — the DFR0954, owned ×2, identified from the DFRobot order history; no DFR0534 is in any DFRobot order. | `parts/max98357a-dfr0954.json` |
| **`assign_pins` output is authoritative in `emit_board`** | The generator looped over parts and their `needs`, so any signal for a part with no record (button, LED, connector, shunt) vanished — 6 of 12 gone, exit 0, under a banner claiming completeness. Now assignments drive, and unclaimed ones are printed loudly. | `emit_board.py` |
| **The vendor's drill is not our drill** | The board file's `drill_mm: 0.9` is DFRobot's finished hole for their own pad. A hole that accepts their 0.64 mm square pin needs ≥1.0. Generating from the vendor number produces a board that will not mate. | `check_footprints` rejects it — spark caught spark |
| **Observers write to `docs/observations/`** | Every serious defect found here came from someone who was not doing the work. Findings must outlive the context that found them. | memory: `background-observers` |
| **A claim leaves `INDEX.md` only by being acted on or rejected with a reason** | `rejected` is terminal and stays in the corpus, or a confidently-wrong observer raises it again every run. | `INDEX.md` |

## Product rules

Two rules about the product's own facts, not about how the team works. They were W5 and W21 in
[`scrum/WORKING_AGREEMENTS.md`](scrum/WORKING_AGREEMENTS.md), which points here; the wording is theirs,
unchanged.

### State the scope of an assertion (was W5)

"The FireBeetle" is two power designs. "The VL6180X breakout" is four pinouts. "The DFRobot MP3 one"
is four products. An unscoped claim is a defect, not a shorthand.

**Origin:** a board file described one SKU and was true of half of them; a part file described one
carrier and was applied to another.

### Keep a datum only if a decision rests on it (was W21)

**Adopted by the PO on 2026-10-03, after the data council** (five lenses: a senior hardware engineer, a
data steward, a minimalist economist, the hobbyist's advocate, and a devil's advocate for keeping). It
**replaces his rule of 2026-09-29** — *"whatever you find online is kept, chosen or not."*

> **Keep a datum only if a decision rests on it — by code, by a check, or by a person at the moment
> they decide — and it stays true without upkeep (a part number, a printed version, a page). Point at
> everything else. Never gather what no decision reads, or what changes before anyone reads it again.**

Why: about 38 % of research tokens went to data no decision used — seller listings (19 %), full
records for candidates nobody chose (13 %), the datasheet of the chip inside a module (5 %), whole
datasheets (1 %). But "no code reads it" is the wrong test: 79 of 140 facts sampled are what a design
decision rests on, and the warnings that found today's wrong boards were read by a person. So the
test is the decision, and a warning that protects a board must be SHOWN where the decision is made —
a typed fact or a check that prints, never only a prose note (P81).

**Checked by:** `agents/parts-researcher.md` and `commands/research.md` carry the sentence; the
validator refuses what the principle forbids as P80, P81 and P83 make it mechanical.

## Live cautions

Each line below was checked on 2026-10-09 against the bin (`sisuo-brain-transplant`, read-only) and
dated; what the check found false is gone.

- **The bin's PCB is not being ordered, and that is the goal's word, not a blocker count:** the goal
  is a circuit that is good and working, so a fabrication-process limit is parked while a circuit fault
  is not. Of the bin's seven original fab blockers, six are closed and the seventh (the annular rings)
  is an advisory. The last to close was the audio module: B1 (the bin's #1) closed on 2026-10-06 — the
  DFR0954, owned ×2, identified from the DFRobot order history; no DFR0534 is in any DFRobot order.
  Newer circuit faults are open cards on the bin's board, in Idea: B25 (#19), B26 (#20) and B28 (#22).
- **No Wokwi token is committed in either repository** (2026-10-09: a search for `wok_` followed by
  eight or more characters finds none in spark or in the bin; both repositories name only the
  variable, `WOKWI_CLI_TOKEN`, and the bin's Makefile tells its owner to put the token in their own
  shell profile). Keep it that way.
- **Pads 14 and 16 of the 18-pin row are still UNRESOLVED** (2026-10-09: the bin's `.spark/board.json`
  still says so) — GND versus NC. Two readings of the same DFRobot schematic disagree. Recorded as GND
  (the safe direction); settle with a continuity meter.

## The spine, as it actually stands

`scripts/check_spine.py` on the reference design, run 2026-10-09 in the `p146-process` worktree with
tscircuit on the PATH (`tsci 0.0.2621`; exit 0: "the chain runs end to end"). Its verdict is the table.
Without tscircuit the same run stops at the build with `[????] build` and exit 2 — "this is not a pass".

| step | state |
| --- | --- |
| idea → parts → pin map | not stages of that run, which starts at the reference design's board file (`[ok] board`, the FireBeetle 2 ESP32-S3); each has its own tests |
| pin map → schematic | `[ok] schematic`, 23 traces written |
| footprint | `[ok] footprint`, `FireBeetle2Esp32S3.tsx` generated, 32 pads |
| schematic builds | `[ok] build`, 20 traces, 0 errors (`tsci 0.0.2621`; the documents were measured on core 0.0.2600). The earlier "blocked" (a footprint module the plugin ships none of, `INDEX.md` R5) is marked `acted` there and is gone |
| schematic → simulation | `[ok] simulation`, 18 wires in the diagram, 2 chips reused; what it cannot show is said from the records: a connector is not simulated, the L9110S model carries no current (no stall), the VL6180X model always answers a good range |
