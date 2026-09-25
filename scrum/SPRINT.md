# Sprint 1

**Started** 2026-09-25 · **Re-goaled** 2026-09-25 by the Product Owner · **Facilitator** main session

## Goal

> **The bin is a working project: a board fit to order, parts you can buy, simulations that pass,
> software that runs.**

Petr reordered mid-sprint, which is his call: *"lets prioritize having a working bin project with
a schema, parts, simulations and software and such"*. The previous goal — a generated design
reaching a simulator — is not abandoned, it is **later**. The bin is the only real evidence spark
works, and it is closer to done than the plugin's simulation path is to started.

**Measured state at the moment of re-goaling**, not remembered:

| half | state |
| --- | --- |
| **software** | 84 tests, green |
| **simulation** | local MicroPython run, all checks passed, costs no Wokwi minutes |
| **schema — the board** | **`make check` RED.** 7 fab blockers. This is the sprint. |
| **parts** | `SHOPPING.md` stale — lists a XIAO and a LiPo JST the board no longer has |

So two of the four are already there. The goal is the other two.

## Pulled

| id | item | state | why this order |
| --- | --- | --- | --- |
| **B3** | Deep sleep never wakes (blocker 5) | **in progress** | firmware, independent of every open question, and today the bin would not wake at all |
| **B2a** | Annular rings on Speaker + BinConnector (blocker 7) | next | connector footprints; survives any audio decision |
| **B1** | Confirm the audio module **[PO]** | **blocked on Petr** | four blockers turn on it. It is a look in a drawer |
| **B2b** | I²S redraw (clears blockers 1, 3, 4, 6) | blocked by B1 | drawing it for the wrong module is a week of rework |
| **B4** | Refresh `SHOPPING.md` | after B2b | the list changes with the audio decision |

W6: one at a time. B3 first because it is unblocked, real, and locally provable.

## Definition of Done

Full text in [`README.md`](README.md). Clause 3 (`check_spine.py`) applies to spark changes; for
bin changes the equivalent gate is `make check` **green for a real reason, not because a gate was
removed**, plus both firmware suites.

## Daily log

### 2026-09-25 — morning

The schema half of the *plugin* went from never run end to end to exit 0, 8 traces. Four
zero-trace defects fixed. `check_footprints` learned the other two hole shapes and immediately
found two real fab blockers on a board declared ready to order. `check_spine.py` exists.

### 2026-09-25 — afternoon, after the re-goal

**Measured the bin rather than trusting the handover note.** Software and simulation are already
green; the board is not. Sprint re-pointed at the board and the shopping list.

**Impediments, named.**
1. **B1 is blocked on a physical look** and gates four of seven blockers. Everything else in the
   audio path is guesswork until it is answered.
2. **W3 still enforced by memory** — carried from this morning, now P4.

**Next.** B3 — the deep-sleep wake, which is firmware and needs nobody.

## Review — validated value

Run at sprint end. Not "did the work complete" but **can Petr order the board and have it work**:

```
cd smartbin-local && make check                                   # green, for real reasons
cd firmware/micropython && python3 -m unittest discover -s tests -t tests
micropython sim/run_on_micropython.py                             # free; no Wokwi minutes
```

Plus: `STATUS.md` lists zero fab blockers, and `SHOPPING.md` names only parts the current board
actually has.
