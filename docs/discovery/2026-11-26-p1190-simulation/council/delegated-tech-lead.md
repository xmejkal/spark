<!-- The delegated council's tech lead seat (Fable), P1190, 2026-11-26. Read-only; the session saved its returned text here unchanged. Its answers are delegated, the PO's to change. -->
# P1190: the delegated tech lead

**Short version.** Order the work by what can start now: P999, then P1078, then `check-firmware`, then the seam with no behaviour change. The `skipped` ending waits on Q11. Pause the logic-level runner and the screens.

| choice | answer | reason | claims |
| --- | --- | --- | --- |
| Q0 | Yes, two fixes | The frame says "Q0 to Q8", but the list runs to Q11 and lacks Q12. The clock's proof comes from P999, not item 1. | ★C25 |
| Q2 | (d), split | P999 gives the clock a `sim/`. P1078 waits on nothing (#1581 closed, PR #1580 merged). Item 1 waits on Q11. Keep P1078 and the seam as two PRs. Keep the `skipped` change as its own commit, so the goldens prove the seam changed nothing. | ★C15 ★C17 ★C25 |
| Q3 | Not now | The stand-in has no `deepsleep` and calls no irq handler, and `ticks_ms()` is always 0. The clock's loop needs new stand-in behaviour first. | ★C13 ★C19 |
| Q4 | (a) | The role and its off switch exist. No second strategy runs, so (c) has nothing to pick from. | ★C5 ★C12 |
| Q6 | (a) | `set-control` steps and the chip's ranges exist. It needs a reader and no live bridge. | ★C8 |
| Q7 | Yes, in two halves | Read the licence and try lint without minutes first, after item 5. The run spends minutes, so it waits on his yes. | ★C10 ★C20 |
| Q8 | Yes | Use `unittest discover` with a timeout. A project with no `tests/` ends `skipped`, never passed. | ★C18 |
| Q12 | T0 to T4 plus "grade" | R1 to R5 map onto T1, T3 and T4, and the grade says R3 from R4. Neither set is in the guide's names table. | none |
| Q1 | High: A1, A3, A8, A9. Low: A2, A4, A5, A6, A7 | The pass line can miss by chance on one clean walk. Propose three walks and two records: the checks ran before the first deploy, and a check ended `problems` with a firmware edit after it. Zero faults reads "not shown". | ★C16 |

**Advice on the PO's questions.**
- Q11 holds back only the `skipped` commit.
- Q5: option (d) is already code and costs nothing.

**Checks.**
- The guard is six lines with two callers: `scripts/spark/build/build_service.py:450-456`, `:399`, `:466`. Its ending is `scripts/spark/build/stages.py:112-113`. Editing it twice is cheap.
- The code `board_not_in_wokwi` appears in 16 files: 5 scripts, 9 tests and mutations, 2 guides.
- `every_part_skipped` is decided at `build_service.py:433`, after three earlier stops (`:404-424`). ★C25 can end there instead.
- A role turned off ends `could-not-run`: `scripts/spark/firmware/scenario_run.py:270-272`, `scripts/spark/records/tool_finder.py:305-306`. Option (a) must map it to `skipped`.
- Another tool must declare `wokwi-project`: `tool_finder.py:300-301`.
- Stand-in: `scripts/spark/firmware/stand_in/machine.py:26-28`, `:74`, and `scripts/spark/firmware/import_child.py:37-38`.
- `set-control`: `scripts/spark/firmware/scenario_steps.py:17`. Ranges: `parts/vl6180x-breakout/chip/vl6180x.chip.json:5-13`.
- The deploy's refusal: `scripts/spark/bench/image_evidence.py:430-436`.
- Tiers: `docs/archive/2026-10-01-firmware-and-tests.md:60-66`.

**Not checked.**
- ★C25 was not run, and I did not find the clock project in the store.
- Whether the clock uses GPIO14.
- The PO's yes to P999, which I took from the refuter.
- How wokwi-cli treats a `github:` chip.
- The architect's sites in `flow_codes.py` and `phase_steps.py`.
- No test was run.
- The session's change to item 12's wording is not made: it says "free" and also needs minutes.

## Searches

none. This file made no web search.
