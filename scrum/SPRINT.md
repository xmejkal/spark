# Sprint 1

**Started** 2026-09-25 · **Product Owner** Petr · **Facilitator** main session

## Goal

> **A design spark generated can be simulated.**

One sentence, one outcome. The schema half of the product goal was finished on 2026-09-25 —
`check_spine.py` runs idea → parts → pin map → schematic → footprint → build and reports 8 traces,
0 errors. Simulation is the last word of the goal Petr stated and the only step still missing
before 3D and PCB become the right thing to work on.

**Not in this sprint:** 3D, PCB layout, routing quality, the findings store, the evals. Anything
that is not "a generated design reaches a simulator" is out, and saying so here is what makes the
goal a goal rather than a wish.

## Pulled

| id | item | state | owner |
| --- | --- | --- | --- |
| P1 | Bring `circuit-to-wokwi` into spark | **assessing** — observer measuring whether it accepts a generated board | main |
| P2 | A simulation path that costs no Wokwi minutes | not started | main |

W6: one in progress at a time. P2 is not pulled until P1 is Done or written up as blocked.

## Definition of Done

Every PBI, every time. Full text in [`README.md`](README.md).

1. tests green · 2. mutation tested · 3. `check_spine.py` exit 0 · 4. its own
`Value proven by:` command runs and shows what it claims · 5. committed, with the reasoning ·
6. every claim it makes is true when run.

## Daily log

### 2026-09-25

**Moved.** The schema half of the goal went from "never once run end to end" to exit 0.
`emit_footprint.py` generates the footprint the emitted board has always imported, verified
against an independently-made one — all 32 pads agree. Four defects fixed that each alone produced
a board with zero traces: a part file whose footprint said 5 pads beside a pinout naming 7; a
missing footprint defaulting to `pinrow4`; `rails_without_a_source` never checking for a source;
and its mirror warning that a correctly-supplied rail went nowhere.
`check_footprints` learned to read the other two hole shapes tscircuit emits, and **immediately
found two real fab blockers** on a board that had been declared ready to order.
`check_spine.py` exists: one command, one definition of done.

**Blocked.** Nothing in the sprint. B1 (the audio module's identity) is blocked on Petr and is
not in this sprint.

**Impediments, named.**
1. **W3 is enforced by memory.** Mutation testing is the acceptance bar and there is no tool, hook
   or CI for it. → P4, and the retro's action below.
2. **The observation intake does not drain.** ~37 rows, no row has ever changed status, `rejected`
   never used once. → retro action R1.2.

**Next.** P1 — the observer's assessment of `circuit-to-wokwi`, then the move.

## Review — validated value

To be run at sprint end. Not "did the work complete" but **can Petr do the thing**:

```
python3 scripts/check_spine.py                     # the chain, including simulation
```

The sprint has delivered value when that reaches a `simulation` stage with a verdict, and the
scenario it ran is one that would catch a real firmware or wiring mistake. A converter that emits
a `diagram.json` nobody runs is Done and worth nothing.
