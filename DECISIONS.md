# Decisions that are settled

Read this after a context clear. It is the short list: what was decided, and why, so none of it
gets re-litigated. Everything still open lives in `BACKLOG.md` and `docs/observations/INDEX.md`.

Last condensed: 2026-09-25.

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
- **State the scope of an assertion.** "The FireBeetle" is two power designs; "the VL6180X breakout"
  is four pinouts; "the DFRobot MP3 one" is four products. An unscoped claim is a defect class.

## Locked technical decisions

| decision | why | where |
| --- | --- | --- |
| **No KiCad footprint converter** | Two councils killed it. 18 of 27 footprints already convert to geometry identical to what exists — reproduced to the micron. | `INDEX.md` C1 |
| **The pill-hole gap is a reader gap, not a source gap** | Pill holes carry `hole_width`/`hole_height`; the rules read `hole_diameter`. ~10 lines in `check_footprints`, not a new pipeline. | `INDEX.md` C2 |
| **CLI over MCP** | An MCP server loads its tool schema into context every session; a CLI costs nothing until called. | user, explicit |
| **Don't reinvent KiCad/Wokwi/tscircuit** | They already have shapes, boards, 3D, simulation. spark's value is the judgement between them. | user, explicit |
| **Audio is I²S (MAX98357A / DFR0954)** | Petr chose it over the DFR0534 UART module. Module identity still unverified — he does not have it to hand. | `parts/max98357a-dfr0954.json` |
| **`assign_pins` output is authoritative in `emit_board`** | The generator looped over parts and their `needs`, so any signal for a part with no record (button, LED, connector, shunt) vanished — 6 of 12 gone, exit 0, under a banner claiming completeness. Now assignments drive, and unclaimed ones are printed loudly. | `emit_board.py` |
| **The vendor's drill is not our drill** | The board file's `drill_mm: 0.9` is DFRobot's finished hole for their own pad. A hole that accepts their 0.64 mm square pin needs ≥1.0. Generating from the vendor number produces a board that will not mate. | `check_footprints` rejects it — spark caught spark |
| **Observers write to `docs/observations/`** | Every serious defect found here came from someone who was not doing the work. Findings must outlive the context that found them. | memory: `background-observers` |
| **A claim leaves `INDEX.md` only by being acted on or rejected with a reason** | `rejected` is terminal and stays in the corpus, or a confidently-wrong observer raises it again every run. | `INDEX.md` |

## Live cautions

- **`make check` in smartbin-local is deliberately RED** on the MOSFET SOT-23 pad mapping. tscircuit
  binds pad 1 = drain; every real SOT-23 P-FET is gate-source-drain. Do not "fix" the red.
- **Six fab blockers stand** in `smartbin-local/STATUS.md`. The board must not be ordered.
- **Simulation minutes are scarce** — 21 of 50 free remain. One scenario per question, not five.
- **The Wokwi token is session-only.** Never written to disk, never committed; verified by grep.
  Petr adds it to `~/.zshrc` himself.
- **Pads 14/16 of the 18-pin row are UNRESOLVED** — GND vs NC. Two readings of the same DFRobot
  schematic disagree. Recorded as GND (the safe direction); settle with a continuity meter.

## The spine, as it actually stands

| step | state |
| --- | --- |
| idea → parts | works (`parts.py`, 4 modules, contract-tested) |
| parts → pin map | works (`assign_pins.py`), but no board file has an `spi` role, so the SPI bus gets spent on LEDs (`INDEX.md` R4) |
| pin map → schematic | works as of the `emit_board` fix; signals no longer vanish |
| **schematic builds** | **blocked** — the emitted file imports a footprint module the plugin ships zero of (`INDEX.md` R5) |
| schematic → simulation | unreachable until the above builds |
