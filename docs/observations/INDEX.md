# What the observations found, and what happened to it

One line per claim. **A claim leaves this table only by being reproduced and acted on, or by
being rejected with a reason.** Nothing sits here unread.

## Why the table exists

This project has a live demonstration of what happens without one. The findings store in the
smart-bin repo is genuinely good engineering — structural identity so the same defect worded
differently is one finding, anchors validated against the built netlist so a hallucinated
component is refused, locking that survived twelve concurrent writers. On 2026-09-25 it held
**20 findings: 11 blocked, 8 open, 1 rejected, 0 resolved.** Nothing has ever come out of it.

A folder of observation essays would do the same thing, only worse, because nothing would even
be counted.

## Status, and what each one obliges

| status | meaning | what has to happen next |
| --- | --- | --- |
| `raised` | an observer claimed it | reproduce it, or reject it |
| `verified` | reproduced here, by running something | put it in `BACKLOG.md` or fix it |
| `acted` | fixed, or in the backlog with a named item | nothing; keep the row as history |
| `rejected` | reproduced and found wrong, or judged not worth doing | nothing; **keep the row**, so it is not raised again |

`rejected` matters as much as `acted`. An observer that is confidently wrong will be wrong the
same way next time, and a claim with nowhere to retire comes back every run.

## The rule that keeps it honest

**Reproduce before promoting.** Several observer reports have been confidently wrong: one
council's central claim about the evals was correct and changed the roadmap, another's verdict on
two of nine findings was wrong in a way that would have buried real defects. A row moves to
`verified` only when someone has run something and seen it.

## The table

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| O1 | `check_physics.footprint_of` reads the field the engine moved, so `check_resistor_power` has never examined a resistor | work-pattern, 09-25 | **acted** | reproduced: 0 of 28 components resolved, 0 of 11 resistors. Two further faults in the same rule found while fixing. `0d01ae4` |
| O2 | ~2/5 of two days was the author repairing his own damage, hours old | work-pattern, 09-25 | `raised` | 22 of 57 commits classified as repair. Classification is the observer's judgement; the commit list is not |
| O3 | The §4d defect class is real but a second class, "the instrument that cries wolf", is unnamed | work-pattern, 09-25 | `raised` | ~5 commits cited. If true it needs a rule, as the first class got one |
| O4a | README claims 265 tests | README:152 | **verified** | actual 301. Trivially stale, and the kind of number that should not be hand-written |
| O4b | README claims every script takes `--json` | README:56 | **verified** | 5 of 15 do not: boards, check_bom, check_design, emit_board, init_project |
| O4c | `check_design.py` has no argparse — `--help` prints `no design at --help` | O4 | **verified** | ran it |
| O4d | `plugin.json` promises "a verification gate that refuses to emit a board with unverified part pins" | plugin.json | **verified** | no such gate in `scripts/`. This is the marketplace description — the first thing a stranger reads |
| O4e | README and spark-review claim seven checks; six run | O4 | `raised` | consistent with what I measured, but the seventh is skipped for want of a design file rather than broken |
| O5 | The findings store is the most-rewritten file in the repo and its author does not use it | work-pattern, 09-25 | `raised` | 20 findings, 0 resolved, 0 measurements. The six current fab-blockers went into prose instead |
| O6 | §4b says "the reviewers are not frozen"; they have been frozen for 33 commits | BACKLOG:160 | `raised` | if true the sentence is aspirational, which is the thing §4b exists to stop |
| O7 | N3, the eval rebuild, has been named three times with zero movement; 47 of 57 commits postdate the last eval run | work-pattern, 09-25 | `raised` | matches my own read. Every avoided item would produce a number that could disappoint |
| O8 | Three of six questions parked on Petr were answerable from published documents | work-pattern, 09-25 | **verified** | I found this myself while closing them: `3a43821`, `db4a7e4`, `fafbd47` |
| O9 | `.gitignore` excludes `evals/results/`, so the runs §4b's argument rests on are not versioned | work-pattern, 09-25 | `raised` | if true, the corrected eval argument cites evidence nobody else can see |
| R1 | `check_physics` passes on `spark init`'s own output — 3 of 4 rules never run | cold rebuild, 09-25 | **acted** | reproduced; `f2a7e1b` |
| R2 | `check_firmware --board` passes a wake source on a non-wake console pin | cold rebuild, 09-25 | **acted** | reproduced; caveat roles now read |
| R3 | `emit_board` silently drops signals with no part record — 6 of 12 placed, exit 0 | cold rebuild, 09-25 | **verified** | reproduced by the design council independently. The §4d defect class, living in the generator |
| R4 | `assign_pins` spends the whole SPI bus on two LEDs and a button — no board file has an `spi` role | cold rebuild, 09-25 | **verified** | `grep spi boards/*.json` → nothing. Fix is one `pin_roles` entry reusing the existing bus path |
| R5 | `emit_board` output cannot build — imports a footprint module the plugin does not ship | cold rebuild + claims audit | `raised` | I reproduced this myself in the walkthrough |
| R6 | Nothing ships the header **pin order** for either board — the one fact you cannot derive | cold rebuild, 09-25 | `raised` | blocked their fabrication. Board file is precise to 0.01 mm and omits this |
| R7 | `emit_board` prints the mandatory `host_requirements` and implements none of them | cold rebuild, 09-25 | `raised` | leaves an H-bridge's unused inputs floating, which the same file warns against |
| R8 | A part's `host_requirements` need a GPIO that `needs` never asks for | cold rebuild, 09-25 | `raised` | the MP3's high-side switch needs a gate pin; the pin map came up one short |
| R9 | `check_design` recommends pins `assign_pins` refuses to use (BOOT, JTAG straps) | cold rebuild, 09-25 | `raised` | follow the advice and put a wake button on BOOT |
| R10 | `must_not_float` false-positives on pin-to-pin traces — including boards spark emits | cold rebuild, 09-25 | `raised` | the generator produces boards that fail the plugin's own flagship rule |
| R11 | `check_all` drops `subject` from aggregated findings — "connects to nothing" twice, unattributed | cold rebuild, 09-25 | `raised` | the aggregator throws away structure its own checks produce |
| R12 | Using the documented board override disables `vendor-truth` | cold rebuild, 09-25 | `raised` | the mechanism you are told to use to record what you verified turns off verification |
| R13 | `init --force`, the only way to seed rails, destroys the brief you were told to hand-write | cold rebuild, 09-25 | `raised` | they recovered from a backup taken one command earlier |
| R14 | Zero design guidance for current sensing — a third of the brief, designed entirely by the engineer | cold rebuild, 09-25 | `raised` | their largest single hole. spark gave the threshold and the warning, none of the arithmetic |
| R15 | Nothing checks that deep-sleep wake sources share a polarity, though the board file records the constraint at length | cold rebuild, 09-25 | `raised` | |
| R16 | `hardware_revisions` is the most design-critical fact in the board file and nothing consumes it | cold rebuild, 09-25 | `raised` | V1.2+ has no I2C pull-ups; the generator emits none either way |
| R17 | `spark-design` points at `references/verified-parts.md`, which has none of the brief's parts, and never mentions the generators | cold rebuild, 09-25 | `raised` | a user following that skill never runs the pin assigner |
| R18 | `on_board: false` and `unused_pins` are read by nothing | cold rebuild, 09-25 | `raised` | the off-board sensor was placed on the PCB |
| R19 | The L9110S record has no motor output pins, though its own note mentions the screw terminals | cold rebuild, 09-25 | `raised` | a generated motor board cannot connect a motor |
| R20 | `design-rules.md` teaches 4.7k I2C pull-ups; `check_physics` rejects them at 400 kHz | cold rebuild, 09-25 | `raised` | the reference file taught the habit the part file warns against |
| R21 | The board file's own `drill_mm: 0.9` is rejected by `check_footprints` in the same plugin | cold rebuild, 09-25 | `raised` | spark caught spark |
| R22 | The plugin ships this project as its worked example, so it cannot be cold-tested by anyone | cold rebuild, 09-25 | `raised` | and the harness injects the project's CLAUDE.md, so the rebuild's gap list understates |
| C1 | The converter plan's demo produces geometry identical to what the board already has | design council, 09-25 | **acted** | reproduced to the micron. Plan abandoned |
| C2 | The pill-hole gap is a field-reading gap in `check_footprints`, not a footprint-source gap | design council, 09-25 | **verified** | pill holes carry `hole_width`/`hole_height`; the rules read `hole_diameter`. Importing adds unreadable holes |
