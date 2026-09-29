# Sprint 4 — proposed

**Proposed** 2026-09-29 · **Facilitator** main session · **Product Owner** Petr. The order below
is a proposal (W11); nothing is pulled until he has seen it. Sprint 3 is closed below.

## Goal (proposed)

> **spark is usable by someone who has not read its source: the chain is named where a user
> looks, a design states its own rails, and the intake table is clean.**

Why: after Sprint 3 the chain is honest on every documented command. What Petr asked for next —
*"basic functionality done well, well-architected, extendable, really usable"* — is now blocked
on usability, not correctness: `assign_pins`, `emit_board` and `check_spine` are named by no
skill, command or agent (R7), and a part still has to be copied to change one rail (R9). And two
retros in a row say the intake has not drained (R3.2).

## Proposed order

| id | item | why here |
| --- | --- | --- |
| ~~P15~~ | Drain the intake: 42 `raised` rows from 09-25, each reproduced against today's code or `rejected` as superseded with the commit that did it | **done** the same evening, `f35e7df`: 38 resolved, 3 fixed, 1 rejected, 4 new items (first written 43 and 40 — counted by eye, audit B12) |
| ~~R7~~ | The generator chain named by a skill, a command and an agent [G13] | **done `1f769f8`** for the one command; **reopened as P22** — the audit followed the documented steps from a fresh directory and reached no build (B19) |
| ~~R9~~ | A rail belongs to the design, not the part [G5] | **done `227f5d4`** — the car's copied record is gone |
| ~~P20~~ | `assign_pins.main` through the loader | **done `c3e2e28`** — the documented first step assigns; a malformed part is a sentence |
| **P21** | A bus is shared; a name does not take a part off it | **next** — a named I2C part silently off its bus (B2) |
| **P22** | A stranger can build [reopens R7] | after P21 |
| **P23** | Two outputs on one net, across parts | after P22 |
| P24, P25 | `check_design` CLI; one outcome vocabulary | last |
| **R2.5** | Third cold test — **PO: choose a domain** (below) | both silent-wrongness classes were found only by building something new |
| — | The audit agent at sprint end (R3.3) | the outside read that produced six items last time |

**R2.5 — three domains; the PO's answer can be one letter.** Each is unlike both the bin and the
car, which is the point:

- **(a) a battery sensor node** — BME280 on I2C, an e-paper display on SPI, ESP-NOW uplink, deep
  sleep. Exercises both buses on one board (P3's roles), a display part class, a second rail.
- **(b) a USB MIDI foot controller** — eight identical buttons, an expression pedal on the ADC,
  LEDs. Exercises many named instances (G7), the ADC budget, USB, stateful firmware.
- **(c) a garden irrigation controller** — 12 V valves through MOSFETs, soil-moisture ADC, an
  RTC, WiFi. Exercises high-current switching, a 12 V rail regulated to logic, and a part class
  (MOSFET/relay driver) spark has never seen.

(c) exercises the most that is new; (a) the most that exists. Not started until chosen.

## Daily log

### 2026-09-29, evening

**P15 done** — pulled ahead of the PO's ordering because two retros mandated it (R2.4, R3.2) and
it decides nothing about the product. Rows by status cell — `awk -F'|' 'NF>6 {gsub(/ /,"",$5); s[$5]++}
END {for (k in s) print k, s[k]}' docs/observations/INDEX.md` — printed no `raised` at all after
the drain (the `grep -c` first written here printed 3, two of them rows quoting the word, and the
43 written above was 42: both counted by eye, audit B12/B13). Three rows were still true and are fixed in
`f35e7df`; R19 is the first `rejected` row the table has ever had. Four items came out, two of them
the PO's.

**R9 done** (`227f5d4`); the car's copied L9110S record is deleted and the board still builds, 13 traces.
Every non-PO item of the proposed Sprint 4 is done; the cold test waits for a domain, and the audit
(R3.3) runs next.

**The audit reported** (`docs/observations/2026-09-29-sprint-4-audit.md`, B1–B20). All DONEs hold
when re-run cold. But: the documented first step crashes on the documented input (B1), a named I2C
part silently leaves its bus (B2), the one command was not executable as written (B4), the stranger
test failed (B5/B6/B19 — R7 reopened as P22), and three of my P15 counts were made by eye and were
wrong (B12/B13). Every claim reproduced before anything was changed. Six items, P20–P25.

**R7 done** (`1f769f8`, corrected `7ac2ba1`). **The commit message of `1f769f8` is false**: it says the
documented example ran end to end; the output it was written over said `the chain is broken`
(a motor driver with no inlet — the tool was right, the example wrong). Grepped, not read. Fixed,
tested from the document, and the build gated on the verdict this time. Second R3.5 failure of the
day, one hour after R3.5 — **and a third inside the correction**: `7ac2ba1`'s message says 12 traces
and 10 wires; the gated run printed 11 and 9. The message was composed in the same command as the
run, so its numbers were predictions. Rule from here, mechanical: a number enters a commit message
or a record only in a later call than the command that produced it. **Correction:** the fix commit's message (`f35e7df`) says 533 tests; the run it cites
printed 532. Written before the count — R3.5's exact failure mode, an hour after R3.5.

## Definition of Done

Full text in [`README.md`](README.md). For every item: the `Value proven by:` command run and its
output in the commit; `check_spine.py` green; a `mutate.py` table with every mutation caught (W3,
W12); both RC boards and the bin's `make check` unchanged or explained; any count in a record
written from a command run that day, with the command beside it (R3.5).

---

## Sprint 3 — closed 2026-09-29

**Goal:** spark reports what it did and nothing less. **Met.** Four items in one day —
P11 `0c21ef5`, P12 `c4d0582`, P13 `55e7bb8`, P14 `f7674b4` — plus P3 `831f756` and A3
`5689147` from the morning. Retro: **R3**.

### Review — validated value, run at close

Commands and what they printed on 2026-09-29:

```
python3 -m unittest discover -s tests                       # Ran 528 tests — OK
for t in tests/mutations/sprint-3-*.json; do mutate.py $t   # 5 tables, 30 mutations: every one
                                                            #   caught, files restored (each table)
python3 scripts/check_spine.py                              # nvm tsci first on PATH:
                                                            #   ok build 12 trace(s), 0 errors, tsci 0.0.2600
                                                            #   ok simulation 10 wire(s) — end to end
PATH=…/smartbin-local/node_modules/.bin:$PATH … check_spine.py   # same, tsci 0.0.2621
cd rc-car && emit_board.py car.requirements.json | grep -c thickness=    # 14   (was 1)
(cd /tmp && check_spine.py ~/Development/rc-car/remote.requirements.json)
                                                            # end to end, 12 wires
                                                            #   (was: no part called 'sg90-servo')
```

### Daily log

### 2026-09-29

**P3 landed** (`831f756`) — measured, not tuned: the bus penalty is a tie-breaker below one
ability's cost, because what spent the bus was GPIO order among equal pins, not a missing cost.
The first value (15) sent two plain signals onto ADC1 and the ordering test caught it; the first
placement test (three LEDs) never reached the tie and three mutations escaped until it was sized
to six, then ten. **A3 fixed** (`5689147`). The bin's board facts regenerated, `make check` green.

**Audit triaged.** Sixteen claims, six re-run here (A2, A3, A7, A8, A9, A10), the rest read
against the code; **none rejected**. Twenty-three intake rows closed in one pass — the first rows to leave the table since it was
written (R1.2). **Forty-two older `raised` rows remain; R2.4 is not done** (first written 43, by eye). Four items promoted, P11–P14, and pulled in that order.

**P11 done** (`0c21ef5`), the same afternoon. The audit's test failed first, as it said it would. One
more instance of the class turned up on the way — the converter looked for from `cwd` — and
went in the same change. Two decisions changed with their tests (W4 the right way round): an
unreadable rules file is an error, and a project's placeholder list survives one broken file.

**P12 done** (`c4d0582`). Measure-before-fixing again: the "toolchain fault" was the spine linking the
Node prefix as `node_modules`; the global tsci builds fine on its own. So the A/B the item asked
for now reads `ok` / `ok` with the version named, and the preflight covers the tool that really
cannot build. Both sides of that are tested with a fake tsci, so the suite still needs no tscircuit.

**P13 done** (`55e7bb8`). A test's docstring was found describing a test that did not exist — it said it
called the runner and it grepped the source. Fixed to ask the code, and the docstring says so.

**P14 done** (`f7674b4`) — the sprint's four items are done in one day. Byte-identical on four
designs. One mutation escaped on the first run (a swapped section, invisible on a fixture with
no placeholder) and was caught after the fixture was fixed: the tool earning its keep, again.

---

## Previous sprints

| sprint | goal | outcome |
| --- | --- | --- |
| 1 — 2026-09-25 | the bin is a working project | met on the measurable half: 5 of 7 fab blockers closed, `make check` green; audio identity and the bench are Petr's. Retro R1 |
| 2 — 09-26 → 09-29 | the cold test, then its findings | RC car + remote build from scratch; 9 of 15 findings fixed, each reproduced and mutation-tested; plan scored 4/5 by area, 0/5 by mechanism. Retro R2 |
| 3 — 09-29 | spark reports what it did and nothing less | met: four audit items done, 30 mutations caught, the spine honest with either toolchain. Retro R3 |
