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

### 2026-09-25 — evening

**Sprint goal met, on the measurable half.** Five of the bin's seven blockers are closed and
`make check` is green. Deep sleep never woke (`WAKEUP_ALL_LOW` is an AND across every armed pin);
a screw head bridged V33 to GND at two mounting holes, measured at 0.19 mm against an M3 head's
1.15 mm overhang; the audio moved to I2S, taking four blockers with it.

**Two findings worth more than the fixes.** A mutation no firmware test could catch — reverting
`WAKE_ON_HIGH` left 113 tests green because they all derive from it, so `wake-polarity.ts` now
compares the board's copper against the firmware's constant. And the bring-up script's WAVE
phase had never tested anything: it passed on an interrupt pin nothing had ever driven.

**Also found in spark itself, by an observer:** the generated board's microcontroller shared a
net with none of its 32 pins — no ground, no 3.3 V — while `check_spine` called it done. Fixed,
and the detector the observer proposed (comparing traces asked against traces routed) was wrong
and would have failed correct boards; the real invariant is grounding.

**Remaining, and neither is ours to close today.** The audio module's identity is Petr's, and
nothing else can be known without a bench — the motor's current, the stroke times, and whether
the chip really wakes, which Wokwi cannot test at all.

**Not started: P1/P2**, the simulation lift. Still the right next thing for the plugin.

## Review — validated value

Run at sprint end. Not "did the work complete" but **can Petr order the board and have it work**:

```
cd smartbin-local && make check                                   # green, for real reasons
cd firmware/micropython && python3 -m unittest discover -s tests -t tests
micropython sim/run_on_micropython.py                             # free; no Wokwi minutes
```

Plus: `STATUS.md` lists zero fab blockers, and `SHOPPING.md` names only parts the current board
actually has.
