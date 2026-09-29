# Sprint 5 — proposed

**Proposed** 2026-09-29, night · **Facilitator** main session · **Product Owner** Petr. The order
below is a proposal (W11). Sprint 4 is closed below it, with its review.

## Goal (proposed)

> **A generated board is a design someone could build: its own rules are honoured or named as the
> reader's, its checks do not cry wolf on its own output, and two of its tools never disagree about
> the same board.**

Why: every item that misled on a documented command is closed (Sprints 3 and 4). What is left in
the backlog is quality of the design that comes out — `must_not_float` fails spark's own boards
(P8), `check_design` recommends pins `assign_pins` refuses (P7), and the generated board prints
each part's `host_requirements` and honours none of them, leaving an H-bridge's inputs floating
under the warning that says not to (P6).

## Proposed order

| id | item | why here |
| --- | --- | --- |
| ~~P26~~ | One bus vocabulary; a matrix-routed bus goes anywhere and says so | **done `07821a0`** — a regression of mine from P21, found by the close audit (C6) |
| ~~P27~~ | A named pin checked against what it was asked to do; a project must exist; a signal well-formed | **done `7459983`** (Sprint 4's close) |
| ~~R11~~ | Research parts and modules, vendor by vendor, and keep what was found | **done** — `/spark:research`, `/spark:identify`, the catalog; seven records for the irrigation controller, 18 candidates kept |
| ~~P31~~ | A part record says how it is simulated; chips compiled; values set in the test | **done** — ordered by the PO that night; one irrigation scenario passing on Wokwi |
| ~~P8~~ | `must_not_float` false-positives on pin-to-pin traces | **done `10a056f`** — the netlist model skipped every trace that named no net |
| ~~P6~~ | `emit_board` honours the host requirements it can, or says which are the reader's | **done `1c2698d`** — `host_parts` placed and wired; three records carry them |
| ~~P10~~ | A project's own board file must not switch `vendor-truth` off | **done `9a7479b`** — the plugin's cache is the fallback |
| ~~P28~~ | What the close audit found in the tools and the records (C8–C12, C14) | **done `ca997ed`** — six rows made true; `tools/pre-push` is the gate |
| ~~R2.5~~ | Third cold test — **(c), the 12 V irrigation controller**, running in `~/Development/irrigation` | **done** — definition of done met, diary I1–I12, ten gaps pulled the same night |
| — | P7 deleted with `check_design` (W16); P16, P17 parked — **Needed by:** none yet | |
| — | **Audit at sprint end, before the retro (R4.3)** — `docs/observations/2026-09-29-v1-close-audit.md`, running | |

Still parked, the PO's: **P18** evals (run or delete), **P19** findings.py and its fake bench
(keep, freeze or drop), **R8** parts-research routing, **R10** a link between two designs. Needing
a source before it can be pulled: **P29** (the FireBeetle's VCC pad). Two repositories: **P30**.
Later and not misleading today: P2, P5, P9, P10.

## Daily log

### 2026-09-29, night

**The close audit reported** (`docs/observations/2026-09-29-sprint-4-close-audit.md`, C3–C19): every
DONE of the second half re-runs, and three things I did wrong. `fd25f15` does not pass its own
suite as committed — its message says 589 OK; the tree it holds runs 562 FAILED, because the file
it imports was staged one commit later (C3). `73ca286`'s "sprint-2.json: 2 of 2" described two
lines of a ten-entry table (C16). `ebb8339`'s "fourteen scripts" is sixteen (C9). And P21 had
made the shipped I2S amplifier unplaceable for an evening (C6) — fixed first, `07821a0`.
`check_commit.py` now measures the committed tree before every push; on its first run it caught
the commit that added it (a `check_*.py` the runner did not import, an anchor that had moved with
the vocabulary) and the push did not happen until `ac18a51`.

**A fourth wrong message, `cdc7c81`:** it says the audit's rows were triaged and these records
written; the script that did that had failed on its first line and the chain committed anyway.
The tree it holds is fine (the gate passed); the message is not. This entry and the commit after
it are the triage the message described. The PO question stands: **one letter, (a), (b) or (c)**;
the close audit also recommends (c).

### 2026-09-29, late

**The PO chose (c)** — "alright, lets try it, we can take the irrigation" — and the third cold test
runs in `~/Development/irrigation` (plan first, diary kept, the plugin used only as documented).
Four PO rules arrived while it ran, each pulled into the plugin the same evening: plain parts from
Czech sellers, local first (`sellers` in the brief); modules looked up from a photo
(`/spark:identify`, three modules from the drawer, the owned DS3231 replacing the RTC being
researched to buy); **everything research reads is kept, chosen or not** (`catalog/`, `--fetch`,
`--catalog`, `--promote`, `--need` over the catalog — R11's scope, extended by the PO); and one
meaning of `verified` (diary I6). Seven researcher agents ran at once; six records validated and
every cited URL answered (`irrigation d0500ae`); the diary holds I1–I6. The `scripts/` budget rose
6,000 → 6,100 with its reason beside it (`7ae7fe2` gate: 549 OK, 92 anchors present) — **the PO
may lower it**. Not yet: the catalog mutation table (waits for the last researcher to stop calling
`parts.py`), the requirements file, the build, the predictions scored.

**Later that night — the build.** All seven records validated; the catalog holds 18 candidates
passed over, each with its datasheet beside it; the chosen records name them as alternatives.
The one command's first run stopped inside tscircuit on a net named `12V` (I7, fixed: `V12V`);
its second run built 36 traces, 0 errors, and ended `????` at simulation — no Wokwi part for any
module. The pin assigner's reason text claimed scarcity while ADC pins sat free (I8, fixed). The
manual build steps did not build in the project at all (I9: no package file, then no local
tscircuit; `init` writes the package file now and build.md says `npm install`). `check_all` on
the built board: vendor-truth and rules-vs-netlist ok, buildability names the four valve
sockets' 0.225 mm annular ring (a fab limit of footprinter's `jst_ph_3`, parked by the bin's
rule) and three placeholder footprints, physics could not look because the rules file names no
rail. Seven of eight predictions scored in the irrigation diary. **The PO asked** what the
simulation options are when Wokwi lacks a module; answered in the session and proposed as
**P31** — the PO orders it or not. Spark: 555 tests, 100 mutations in 22 tables, every anchor
present, `85963af` pushed.

**Late night — P31, ordered and done.** The PO: "make the Wokwi simulations work, have the
WebAssembly made, set the values in the test; you can also increase the limit." Five slices,
each proven on the irrigation chain: the record contract (`simulation`: stand-in, chip beside the
record, or skip with a reason), the spine writing the converter's mapping from the records and
compiling the chips, the converter reading it (bin repo `bf9bf09`, 62 bun tests, its own diagram
unchanged), two chips (a probe whose moisture is a slider driving a voltage, a flow meter whose
rate is a slider driving pulses), a flash-image tool and one scenario — **passing**: the slider
opens a valve and the MCU pin reads high, wets it closed, ten litres a minute counts as ten, the
clock stand-in answers I2C. Three diagnostic runs went to Wokwi's 5 V ADC reference (diary
I11), during which a chip-name rule was written on a theory and withdrawn when the next run
disproved it. The PO's photos of the DS3231's back corrected five of the record's seven
unverified facts (diary, "the RTC's back"); `identify` now asks for both sides. Budget 6,500
(the PO's words beside it); spark 574 tests, 113 mutations in 24 tables, every anchor present.

**Later still — P8 and P6.** P8: the floating-input rule's netlist model skipped every trace
that named no net, which is how the generator wires every signal; fixed, the finding names its
pin (I10), the irrigation valves pass. P6: a record's `host_parts` — a pull-down, a pull-up, a
divider — are placed and wired as real resistors; three records carry them; the reference
design's chain exits 0 end to end (20 traces, 18 wires, both chips compiled from the library
records); the spine's "reaches ground" check learned that a passive between a pin and a rail is
not an island. Budget 6,600 with the reason beside it. 587 tests, 125 mutations in 26 tables.

**P10 and P28, and the sprint's items are done.** P10: a project's copy of a shipped board is
checked against the plugin's cached vendor header (reproduced as `????` on the irrigation project
first). P28: the six audit rows made true — the mutate lock covers the pre-check, `apply` refuses
a missing file, three functions are named by tests, the stranger test runs the document's own
lines, the example block is a run's output with a test on its schematic line, the status words
have one home, and `tools/pre-push` is the versioned gate. Every Sprint 5 item — R11, P31, P8,
P6, P10, P28 — is done; the v1 audit follows (R4.3), then retro R5 and the review.
594 tests, 128 mutations in 28 tables, every anchor present.

**Review evidence, run at close (before the audit's verdict):** the bin's own `make check` —
"everything is in step" with the changed converter and library records (62 bun tests, its
diagram current); the RC car builds 17 traces and the remote 12, 0 errors each, and both end
`????` at simulation as before — the message now names the three car records and the remote's
own `tactile-button` copy that lack a `simulation` field, instead of blaming the converter's
table. Unchanged in outcome, explained in words.

## Definition of Done

Full text in [`README.md`](README.md). For every item: the `Value proven by:` command run and its
output in the commit, written after the run and measured on the tree being committed (W13,
`check_commit.py` before every push); `check_spine.py` green; a `mutate.py` table with every
mutation caught (W3, W12), and `mutate.py --anchors tests/mutations/*.json` clean at every commit,
one mutate run at a time (R4.5); a "user can" value line proven by a test that follows the
document (R4.2); both RC boards and the bin's `make check` unchanged or explained.

---

# Sprint 4 — closed 2026-09-29

**Proposed** 2026-09-29 · **Facilitator** main session · **Product Owner** Petr. The order below
was a proposal (W11); every non-PO item was done the same day. Sprint 3 is closed below.

### Review — validated value, run at close

On `77af415`, the last item's commit, in one background run with nothing else touching the tree:

```
python3 -m unittest discover -s tests                 # Ran 603 tests — OK
for t in tests/mutations/sprint-4-*.json: mutate.py $t
                                                      # b11, p15, p20, p21, p22, p23, p24, p25, r7:
                                                      #   every mutation caught, files restored
                                                      # r9: 0 escaped, 1 REFUSED — its anchor moved
                                                      #   under P20 (the B8 shape, again)
python3 scripts/check_spine.py                        # nvm's tsci first on PATH:
                                                      #   ok build 12 trace(s), 0 errors, tsci 0.0.2600
                                                      #   ok simulation 10 wire(s) — end to end
awk … rows by status cell, docs/observations/INDEX.md # acted 83, closed 11, rejected 1, raised 0
```

**What the review found, and what was done about it before closing.** A refused mutation guards
nothing, and the morning's audit had found the same for the R6 mutation (B8). So `mutate.py` got
an `--anchors` mode that checks every table's `find` in a second — and on its first run found two
more stale anchors, both in the P11 table, both moved by P22 that evening. All three were
re-anchored. Then a second fault, mine: I started the P11 re-run while the R9 re-run was still
going in the background, and two runs rewrote and restored `design.py` under each other; both
printed verdicts neither had earned. The tree was checked clean against HEAD, the tool now
refuses a second concurrent run (a lock, removed in a `finally`), and both tables were run again
alone, one after the other:

```
python3 -m unittest discover -s tests                 # Ran 608 tests — OK (after the tool changes)
mutate.py tests/mutations/sprint-4-r9.json            # every mutation caught, files restored
mutate.py tests/mutations/sprint-3-p11.json           # every mutation caught, files restored
mutate.py --anchors tests/mutations/*.json            # 74 mutation(s) in 16 table(s): every anchor present, once
```

Retro: **R4**.

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
| ~~P21~~ | A bus is shared; a name does not take a part off it | **done `7381fed`** — two named I2C parts on one bus build, 12 traces |
| ~~P22~~ | A stranger can build [reopened R7] | **done `c565778`** — every documented step from an empty directory, build 11 traces |
| ~~P23~~ | Two outputs on one net, across parts | **done `5605065`** |
| ~~P24~~ | `check_design` CLI | **done `fd25f15`** |
| ~~P25~~ | One outcome vocabulary; a test for every rule function | **done `ebb8339`, `7361679`** |
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
