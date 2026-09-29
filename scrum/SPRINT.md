# Sprint 3

**Started** 2026-09-29 · **Facilitator** main session · **Product Owner** Petr (order is his, W11)

## Goal

> **spark reports what it did and nothing less: no documented invocation of the generator or the
> spine emits less than it was asked, and neither blames the design for its own tools.**

Why this goal: the sprint audit (`docs/observations/2026-09-29-sprint-audit.md`) found the
"less than asked, exit 0" family a sixth time — inside `emit_board.main`, the one function nothing
tests, on the invocation its own docstring documents — and found the spine calling a broken
toolchain a broken design. Both mislead today. Everything else open (R7–R10, P2, P5–P10) is a
gap, and a gap does not lie.

## Pulled

| id | item | state | why this order |
| --- | --- | --- | --- |
| ~~P11~~ | One `design.load()`; `main()` tested | **done `0c21ef5`** | the live defect, and four more audit claims with the same cause |
| **P12** | Toolchain fault ≠ design fault | **next** | a wrong verdict class; small |
| **P13** | Plain imports | after P12 | two `PartError` classes in one process is a miss waiting to happen |
| **P14** | `emit_board` says each thing once | last | a refactor, and it lands on the code P11 just touched |

W6: one at a time. **Not pulled:** R2.5, the third cold test — the PO chooses the domain.

## Definition of Done

Full text in [`README.md`](README.md). For every item here: the `Value proven by:` command run
and its output in the commit; `check_spine.py` green; a `mutate.py` table with every mutation
caught (W3); both RC boards and the bin's `make check` unchanged or explained.

## Previous sprints

| sprint | goal | outcome |
| --- | --- | --- |
| 1 — 2026-09-25 | the bin is a working project | met on the measurable half: 5 of 7 fab blockers closed, `make check` green; audio identity and the bench are Petr's. Retro R1 |
| 2 — 09-26 → 09-29 | the cold test, then its findings | RC car + remote build from scratch; 9 of 15 findings fixed, each reproduced and mutation-tested; plan scored 4/5 by area, 0/5 by mechanism. Retro R2 |

## Daily log

### 2026-09-29

**P3 landed** (`831f756`) — measured, not tuned: the bus penalty is a tie-breaker below one
ability's cost, because what spent the bus was GPIO order among equal pins, not a missing cost.
The first value (15) sent two plain signals onto ADC1 and the ordering test caught it; the first
placement test (three LEDs) never reached the tie and three mutations escaped until it was sized
to six, then ten. **A3 fixed** (`5689147`). The bin's board facts regenerated, `make check` green.

**Audit triaged.** Sixteen claims, six re-run here (A2, A3, A7, A8, A9, A10), the rest read
against the code; **none rejected**. Twenty-three intake rows closed in one pass — the first rows to leave the table since it was
written (R1.2). **Forty-three older `raised` rows remain; R2.4 is not done.** Four items promoted, P11–P14, and pulled in that order.

**P11 done** (`0c21ef5`), the same afternoon. The audit's test failed first, as it said it would. One
more instance of the class turned up on the way — the converter looked for from `cwd` — and
went in the same change. Two decisions changed with their tests (W4 the right way round): an
unreadable rules file is an error, and a project's placeholder list survives one broken file.

## Review — validated value

Run at sprint end:

```
python3 scripts/check_spine.py                                   # from spark; then again with
PATH=~/.nvm/versions/node/v18.14.2/bin:$PATH python3 scripts/check_spine.py   # → ???? build, not !!
cd ../rc-car && python3 ../spark/scripts/emit_board.py car.requirements.json | grep -c thickness=   # 14
(cd /tmp && python3 ~/Development/spark/scripts/check_spine.py ~/Development/rc-car/remote.requirements.json)
python3 scripts/mutate.py tests/mutations/sprint-3-p3.json       # and every table this sprint adds
```
