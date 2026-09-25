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
