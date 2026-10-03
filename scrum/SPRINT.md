# Sprint 10 — slice 1, then 1b

**Ordered by the PO 2026-10-03.** First **public** (P71, P75): a fresh public repository whose history
never held the vendor files, today's repository kept private as the archive, and irrigation published
scrubbed. Then **from a vague idea** (P76), designed with the PO in a brainstorming session before
anything is built. The bench and firmware-on-a-Mac (slices 2, 3) follow.

---

# Sprint 9 — closed 2026-10-03

### Review

**Goal half met, and the rest re-placed by the story map.** A fact spark ships can be traced to the
page it rests on — the FireBeetle's two WROOM-1 figures cite Table 11 and Table 12 on page 15, found
offline by `parts.py --kept wroom`, the file's checksum equal to the record's (P62b). The 48 catalog
files left the repository for each person's store (P62a). "Nothing verified without an openable
source" moved to slice 4 with P64a, and "a page for every build" was parked with P66: `tsci dev`
already shows the board (P65). Found on the way and fixed: **B9**, the summary line that counted
three checks that could not look as completed, and a P62b defect its own first acceptance run
caught (15 unrelated records "citing" the WROOM). Discovery (P69) ran inside the sprint and gave the
work an order: `VISION.md`, `STORY_MAP.md`.

### Retro R9 — at most two actions (P72)

R8.1 held: no bin commit since `852f1c6` used `--no-verify`. R8.2 became B5, now on slice 2 with new
evidence. **R8.3 broke:** STATUS.md's stale shopping claim was corrected while CLAUDE.md's copy of it
waited for a lens to point at it — the sweep is a habit, and habits are what break.
- **R9.1** — P72's first cut decides R8.3: the sweep becomes one command that a fact-correcting
  commit runs, or it goes to the habits page and stops being called a rule. *Check:* the next
  fact correction's commit shows the command's output.
- **R9.2** — counts are read with `/usr/bin/grep`: in Claude's shell `grep` is a wrapper function
  that prints nothing for `-c` on a file, so a missing number looked like a clean one twice today.
  *Check:* `type grep` in the session; no `grep -c FILE` in a pasted count.

---

# Sprint 9

**Planned** 2026-10-02 · **Facilitator** main session · **Product Owner** Petr, who chose the
composition after three council lenses refined P62, P64, P66 and P68 — each reproducing its item
first, and each item changed shape when they did (backlog, "Refined 2026-10-02").

## Goal

> **A fact spark ships can be traced to the page it rests on, nothing marked verified lacks a
> source a reader can open, and every board spark builds leaves a page you can open.**

Why: P60 found spark's own library teaching a false fact, and the lens found the rule meant to
prevent that — `verified: true` means the vendor's text at the cited URL — broken by 36 fields that
predate it. P61 decided where sources live; nothing implements it. And the PO asked to see the board.

## The order — as the PO set it

| # | item | what it does | size |
| --- | --- | --- | --- |
| 1 | **P62a** | the catalog's 48 files move to `~/.local/share/spark/sources`; `documents` replaces `attachments`; `--sources` stops being blind to dict-shaped sources | S–M |
| 2 | **P62b** | `--keep` imports a local file, `--kept` finds one with no network; the FireBeetle cites its WROOM-1 v1.1 page | S |
| 3 | **P64a** | "verified" requires a URL or a kept document; the 36 fields go to 0; prose claims are listed | S |
| 4 | **P66** | every `--keep` build leaves `dist/board-viewer.html`; the bin uses the plugin's generator | M |

**Four items**, below Sprint 8's planned five — R7 and R8 found the risk is false premises, not
throughput. Not in this sprint, with reasons: **P64b** (a schema change for prose claims — the PO's
decision); **P64c** (the isolated checker — after P62, ideally after P64b; Sprint 10); **P59**
(Sprint 10, first — its Valve4 and unread-button defects reproduced 2026-10-02); **B5**, **B8**
(the bin's, next sprint); **P68** (parked: its premise needs a test publish the PO declined for now).

## Definition of Done

Per item: the `Value proven by:` command run in the project its `Needed by:` names (R6.3), its output
in the commit, written after the run (W13, W17, W20); a mutation table with every mutation caught;
`--anchors` clean at every commit, one run at a time; a document that describes what moved changes
in the same commit (R7.1); `DONE <date>` is the implementation commit's date (R7.3).
**New from R8.3:** a commit that corrects a fact carries the sweep — the grep over spark, the bin,
irrigation and the RC car — and its output.
**New from B8:** a gate's output is kept in full, never cut to its last line, so a failure names itself.
This sprint's review is written into this file before its last commit (R7.4).

---

# Sprint 8 — closed 2026-10-01

### Review — validated value, every number rerun at close

**Goal met, both halves.** The documented example's buildability no longer cries wolf, and the
irrigation firmware takes its pins from a file spark writes instead of agreeing with the board by luck.

| | before | after, rerun at close |
| --- | --- | --- |
| documented example, `buildability` | `[FAIL]` on a real JST PH's 0.225 mm ring | `[ok]`, one advisory: over JLCPCB's 0.18 mm minimum, under its 0.25 mm recommendation |
| a rail's load | `max_current_a: null`, nothing summed | irrigation `V33: draws at least 355 mA; not stated: Soil1.VCC…`; car `SERVO: draws 700 mA of 3.00 A, resting on figures nobody has verified` |
| irrigation firmware's pins | twelve GPIO numbers typed by hand | `import pins`; the MicroPython trace before and after identical |
| a test confirming the code with its own numbers | `test_flash_image` read the module's offset | mechanical (W2): 39 reads triaged, one identity fixed against MicroPython's literals |
| the catalog | read by nothing; a flipped fact passed a green suite | walked for real; the flip is a caught mutation |
| the false wake fact | in spark's parts library and the bin's docs | corrected at source in four repos |
| seeing the board | nothing said how | `tsci dev` and Wokwi for VS Code in `build.md`; the bin's viewer is a `make` product |

**Evidence at close:** 795 tests OK (741 at the start) · 267 mutations in 48 tables, every anchor
present (212 at the start; 55 new, every one caught) · `scripts/` 3,897 code lines of 5,000 (the PO
raised the ceiling from 4,000 mid-sprint, W15b) · the bin's `make check` red only on CurrentShunt.

**Eight items planned as five.** The PO put P63 first when P60's council found spark's library
teaching a false fact, and added the two documentation items P65 and P67. Outside the sprint, the
same day: P60 and P61 answered by councils, P62 and P64 written and ordered into Sprint 9 with P66
and P68, the firmware horizon parked as F1–F5, the bin's viewer made by `make` (B4).

**What was true of the items, measured:** three of the six code items had a premise or an
acceptance line that was false when reproduced (P52 twice, P57, P55), one needed a paid run its own
sprint excluded (P36, amended by the PO), and one missed copies of what it fixed (P63, completed the
same day). Every one was caught before code by reproducing it first — W20.

---

# Sprint 8 — as planned

**Planned** 2026-10-01 · **Facilitator** main session · **Product Owner** Petr, who chose
"close v1, bridge to firmware" after five lenses analysed whether spark should produce tested
firmware (P56, `docs/2026-10-01-firmware-and-tests.md`).

## Goal

> **v1's checks stop crying wolf on their own example project, and one generated project's firmware
> stops agreeing with its board by luck.**

Why: R7 claimed the v1 line "holds mechanically". That was true only of the stranger clause.
Reproduced on the documented example: `[FAIL] buildability` on four 0.225 mm annular rings — every
one on a **stand-in** footprint — and `[????] physics` with all four rails unstated. v1's own words
are *"no false alarms from the checks"*.

And the PO has set the product's direction: spark should take a DIY ESP32 project to firmware that
is tested before it meets hardware. The analysis says spark exports facts and ships a harness while
the conversation writes the code. **P36 is the bridge** — the smallest item that proves that
direction, with no new concept, no quota and no bench.

## The order — as the PO set it

| # | item | what it does | size |
| --- | --- | --- | --- |
| 1 | **P63** | a fact this project wrote down wrongly is corrected where a conversation reads it — **added first by the PO 2026-10-01** | S |
| 2 | **P52** | a rail states what it carries, summed from the records that already hold it | M |
| 3 | **P57** | a stand-in's geometry is could-not-run naming the stand-in, not a FAIL | S |
| 4 | **P36** | the pin map becomes a file the firmware imports instead of retyping — plain ints, each pin's record facts as comments (PO, after P60) | S |
| 5 | **P54** | the suite cannot pass by asking the code to confirm itself | S |
| 6 | **P55** | something reads the real catalog — 35 records no test touches | S |
| 7 | **P65** | the board is one command from being seen while you work (`tsci dev`, documented) — **added by the PO 2026-10-01** | XS |
| 8 | **P67** | the simulation can be watched in VS Code (documented; needs a Wokwi Hobby+ licence) — **added by the PO 2026-10-01** | XS |

**Sprint 9 opens P62 → P64 → P66 → P68** (the PO, 2026-10-01): the viewer page and its artifact
follow the source work, now that the `scripts/` ceiling is 5,000 code lines.

**Eight items since 2026-10-01**: P63 put first by the PO, and two documentation items (P65, P67) added last: P60's council found spark's own parts
library teaching a false wake fact, and a false fact in a record is what every conversation reads.
**Planned as five, deliberately below Sprint 6's eight.** The reason is measured and in R7: of the last
twelve items, **five had acceptance lines that were false when reproduced**, and both sprints found
faults in their own record at close. The constraint is not throughput; it is the distance between
what gets written down and what has been run.

Not in this sprint, with reasons: **R2.6** (the fourth cold test is the firmware direction's
acceptance — running it now tests an unchanged tool); **P2** (needs P36's export to exist first);
**P43** (right and urgent, but it is the sprint after the export, or this becomes eight items
again); **P32b**, **P16-reopened** (decisions for the PO, not work); **P58, P59** (raised today,
unordered); **P38, P39, P44, P49, P50**; anything at the bench; any `wokwi-cli` run.

## Definition of Done

Per item: the `Value proven by:` command run **in the project its `Needed by:` names** (R6.3), its
output in the commit, written after the run (W13, W17, W20). A mutation table with every mutation
caught; `--anchors` clean at every commit, one run at a time. **New from R7:** the document
describing anything that moves changes in the same commit (R7.1); a `(was N)` is measured from the
parent's archive, not recalled (R7.2); `DONE <date>` is the implementation commit's date (R7.3);
this sprint's review is written into this file before its last commit (R7.4).

**The PO's first act of planning is still owed:** the 09-30 council table is stale by its own header
and reordering it is his (W11).

---

# Sprint 7 — closed 2026-10-01

### Review — validated value, every number rerun at close

**Goal met.** A stranger can install this and get a built, checked, simulated board, and none of
those three words depended on this machine before.

| | before | after |
| --- | --- | --- |
| `npm install` in a fresh project | failed: `No matching version found for @tscircuit/cli@0.0.2600` | exit 0, and the **core** is pinned for the first time |
| after the one documented command | only `requirements.json` | a built board in the project |
| `check_all --project .` | 4 not asked for | **1** (the fab package nobody exported) |
| simulation off this machine | `[????] no converter found` | runs wherever the plugin is installed |
| RC car's rules | none — `compare_design` refused | **8**, both boards `every rule holds` |
| irrigation's rails | none — `check_physics` refused | **4**, the check runs |
| what a green scenario admits | nothing | **7 lines**, in the records' own words |

**Evidence at close:** 741 tests OK · 212 mutations in 43 tables, every anchor present · 38/38 in
the converter's own suite inside the plugin · scripts 3,710 code lines of 4,000 · the bin's
`make check` unchanged, red only on CurrentShunt's unmeasured current.

**Three of four items had an acceptance line that was FALSE when reproduced**, which is W20 — adopted
the morning this sprint began — earning its place three times in one day. P51's understated the
defect: the pin was not merely wrong, `tscircuit` was never in the package file at all and
`@tscircuit/cli` takes it as a `"*"` peer dependency, so **every project spark has ever created
installed an unpinned core**. P53's said `--force` preserves hand-filled values; it deleted them,
in the one workflow the documents prescribe. P32a's said 62 tests would move; 38 did, because a
board's end-to-end test is knowledge of that board.

**P32a found a regression P29 had shipped**: the irrigation chain stopped at `"VCC" is not a pin of
board-esp32-s3-devkitc-1`. The board contract now compares `power_pads` against `wokwi_power_pins`,
so two lists in one file can no longer disagree with a person as the only comparator.

**Two faults this close found in its own record**, both by R6's checks run as written: three
`(was N)` baselines in commit messages were written from memory and are wrong — 692 not 693, 703
not 706, 716 not 718, each understating its own delta (W13); and `commands/build.md` still told a
stranger the converter *"is not shipped with the plugin yet"* and pointed at
`../smartbin-local`. The code moved and the document did not. Both corrected at close, the second
with a test that fails if any shipped prose names another repository.

---

# Sprint 7 — as planned

**Planned** 2026-09-30 · **Facilitator** main session · **Product Owner** Petr, who ordered
"fix the lie first, then v1" after a five-lens council read the whole backlog and reproduced
every claim it made.

## Goal

> **The documented path works on somebody else's machine, and the last word of v1 — "simulated" —
> becomes true anywhere rather than only beside one repository.**

Why: the first-hour lens followed `commands/init.md` in an empty directory and could not finish
step one. `npm install` fails, because `init` pins `@tscircuit/cli@0.0.2600` and that version
belongs to a **different package** — `@tscircuit/cli`'s 0.0.x line stops at `0.0.394`. **P33 is
marked DONE and that is its own acceptance command.** Worse than a bug: a green record over a
broken path.

And the same lens found the chain's headline green is reproducible only here — the same
requirements file gives `[ok] simulation` in a bare directory and `[????] no converter found` after
running the documented `/spark:init`, because the search walks up from the plugin and finds the
author's own bin repo.

## The order — as the PO set it

| # | item | what it does | size |
| --- | --- | --- | --- |
| 1 | **P51** | the npm pin is a version that exists, and `/spark:build` leaves its board in the project | S+M |
| 2 | **P32a** | the converter and the chips move into the plugin; the chain reaches `[ok] simulation` from a directory with nothing beside it | L |
| 3 | **P53** | the rules reach a project that already exists — the RC car's floating bridge inputs are checked by something | S |
| 4 | **P37** | what this simulation cannot show, printed, so a green scenario stops reading like a bench result | S |

**P32a only, not P32b.** The firmware lens counted the move: ~1,307 lines in, 558 staying, and
spark gains its first JS dependency tree. The second half — the bin dropping its own copy — can
leave the bin red overnight, so it is a separate item and a separate sitting.

Not in this sprint: P54, P55, P49, W20 (the trust items the verification lens found — six escapes
on a green suite), P43, P44, P39, P36, P38, P2, P50, R2.6.

## Definition of Done

Per item: the `Value proven by:` command run and its output in the commit, written after the run
(W13, W17). **New this sprint, from R6:** that command is run **in the project its `Needed by:`
line names**, on that project's own tree — not in a temp directory that resembles it. A mutation
table with every mutation caught, `--anchors` clean at every commit, one run at a time. Both RC
boards and the bin's `make check` unchanged **or regenerated and committed in the same commit** —
never described without being produced.

---

# Sprint 6 — closed 2026-09-30

### Review — validated value, run at close

**Goal met, and exceeded by two items the PO added mid-sprint.** A check that examined nothing now
says so (P34, P42: the verdict has one home, so a `main` cannot invent a status). The three walks
over a netlist became one (P35), and the shared type immediately answered a question none of the
three private copies had been asked — which is how P29 found that `compare_design` called a
correctly wired pin floating.

**Beyond the goal, at the PO's order:** P46, because he asked whether the scripts could all read
one file where the data are — they can, and four numbers were duplicated. P45, the seeding half
split out of P35. P48, a glossary, because he asked what a mutation and an anchor are.

**Evidence, each from a run at close:**

| | |
| --- | --- |
| spark's suite | 692 tests, OK |
| mutations | 179 in 38 tables, every anchor present, once |
| `scripts/` | 3,612 code lines of 4,000 |
| the reference design | the chain runs end to end — 20 traces, 0 errors, 18 wires, 2 chips |
| the irrigation board | 40 traces, 0 errors, no islands; `rules-vs-netlist` **ok**, `buildability` FAIL on two 0.225 mm rings, `physics` could-not-run |
| the smart bin | `make check` unchanged — red on one line, CurrentShunt's unmeasured current |
| the RC car and remote | wiring unchanged; each **now** carries the comment saying nothing drives its 5 V rail — `cb11dc7`, committed at close |

**One claim in this sprint's own commit messages was false, and the retro check caught it.** P29's
message said the two RC boards "gained" the four-line comment. They had not: the generator's output
was diffed in a temp file and never written. Reproduced by the scrum master lens against retro
action R5.1 — `grep -c "receives net.V5V" car.tsx remote.tsx` returned 0 on both. The boards were
regenerated and committed at close (`cb11dc7`), so the claim is now true. Same shape as Sprint 5's
audit row D13. Two headlines were soft rather than false: P46's title says "read by every script"
where 5 of 20 import `fab` (its body is exact), and P42's acceptance line claims the status
expression appears once where `parts.py:918` still builds one inline — recorded as P43's.

**Two defects were found by doing the work, neither predicted by the item that found them.** A port
is named after its silkscreen label only when its component came from `pinLabels`; one built from a
FOOTPRINT — every microcontroller module here — is called `pin17`, with the label only in
`port_hints`. Every rule naming a pad of the processor had been missing, silently, in both
directions. And `check_footprints` demanded 0.25 mm of annular ring while `emit_footprint` drew
0.35, related by a sentence in a comment rather than by arithmetic.

**Five mutations escaped** across the sprint — one in P29, three in P45, one in P48 — and every one
was closed by strengthening the fixture, never by dropping the mutation (W12). Two of the three in
P45 were only visible after the suite was made honest again: the first run reported *NOT GREEN WITH
THE FILES RESTORED*, because W14's own test had caught three backlog proposals written minutes
earlier with no `Needed by:` line.

---

# Sprint 6 — as planned

**Planned** 2026-09-30 · **Facilitator** main session · **Product Owner** Petr, who ordered the
five steps below in this order and chose how the smart bin absorbs P34.

## Goal

> **The checks tell the truth, and one command's behaviour has one home: a check that examined
> nothing says so, and the three walks over a netlist become one.**

Why: the v1 close audit and a five-lens architecture review both landed on the same two live
defects. The physics check reports `status: ok` and exits 0 while every finding it emits is
`could-not-run`. Three netlist walkers give three different answers to one circuit, one of them a
false alarm that would abort a good board's build. Both are the class this product exists to kill.

## The order — the architecture's steps, as the PO set them

**Eight items closed, not five.** P33 and P40 landed inside this window and are in no table below; P48
was ordered mid-sprint and is in none either. The table is what was PLANNED; the review above is
what happened. Corrected at close, after the scrum master lens found the header counting five.

| # | item | what it does | size |
| --- | --- | --- | --- |
| 1 | **P41** | The safety net: the board tool's cross-repo command line, and every `--json` payload's shape | S |
| 2 | **P34** | A check that compared nothing says so — in place, no move | S |
| 3 | **P42** | The verdict has one home; six copies become calls | S |
| 4 | **P35** | One netlist walker, three callers | M |
| 5 | **P29** | The board's own supply, and nothing left unfed; joins the walker as its third caller | S+M |
| 6 | **P46** | A number a fab house could change is data, not code — one file, read by every script | S |
| 7 | **P45** | The rules a project is checked against are seeded from its design | M |

All seven are done. **Steps 6 and 7 were added on 2026-09-30 by the PO**, after the desk reported what is still code
that should not be: "the data should be shared if possible. Can't they all read the same file
where the data are? And yes, you can add P45 and the other one and do them." That sentence is also
P46's acceptance test — **one file**, not two agreeing copies.

Not in this sprint, by the PO: **P32** (a day of TypeScript, and it must not interleave with
Python moves), **R2.6** the fourth cold test (parked 2026-09-30, with the date), and P39, P43,
P44, P36, P37, P38, P2, which wait behind these five.

**The smart bin absorbs P34 by stating the facts it knows:** P34 makes the physics check exit
honestly, which turns the bin's `make check` red on two pull-down resistors whose dissipation a
netlist cannot derive. The PO's call is to state those two currents in the bin's rules file, so
the check goes green by being answered rather than by being silenced.

## Definition of Done

Full text in [`README.md`](README.md). Per item: the `Value proven by:` command run and its output
in the commit, written after the run and measured on the tree being committed (W13, W17 for the
words); `check_spine.py` green; a `mutate.py` table with every mutation caught, and
`mutate.py --anchors tests/mutations/*.json` clean at every commit, one run at a time; both RC
boards and the bin's `make check` unchanged or explained. The architecture document's stopping
rule applies: after step 4, stop.

---

---

# Sprint 5 — closed 2026-09-30

**Proposed** 2026-09-29, night · **Closed** 2026-09-30 · **Facilitator** main session · **Product
Owner** Petr.

### Review — validated value, run at close

**Goal met.** A generated board's own rules are honoured as components or named as the reader's
(P6: three records' pull-downs, pull-ups and a divider placed and wired; the rest said as prose);
its checks do not cry wolf on its own output (P8: four declared inputs pass, a floating one is
still named); two tools no longer disagree about one board (P7 went with `check_design`; P10 keeps
vendor-truth on for a project's own board file). Beyond the goal, at the PO's order: research
with a catalog (R11) and a simulation built from the records with one scenario passing on the
irrigation board (P31). The third cold test met its definition of done.

**The v1 line** — a stranger goes from a requirements file to a built, checked, simulated board an
engineer would accept as a draft — holds with the documents alone for every stage but the last,
which holds only beside the bin repo where the converter lives (audit D17 → P32, the PO's).

**Evidence, each from a run at close:** spark 595 tests OK; 130 mutations in 29 tables, every
anchor present, every sprint-5 table caught; reference design 20 traces, 18 wires, exit 0; the
irrigation board 39 traces, 33 wires, one Wokwi scenario passing (`irrigation/sim/runs/`); the
bin's `make check` in step; the RC car regenerated for P6 and both RC boards building. The v1
close audit: 33 rows, 20 true, 11 false — all eleven acted on or raised the same day — 2 could not
be checked (the quota, and the bin's check, which this desk ran).

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
| ~~P8~~ | `must_not_float` false-positives on pin-to-pin traces | **done `ba7162a`** — the netlist model skipped every trace that named no net |
| ~~P6~~ | `emit_board` honours the host requirements it can, or says which are the reader's | **done `c4edb92`** — `host_parts` placed and wired; three records carry them |
| ~~P10~~ | A project's own board file must not switch `vendor-truth` off | **done `95ef6e3`** — the plugin's cache is the fallback |
| ~~P28~~ | What the close audit found in the tools and the records (C8–C12, C14) | **done `c35a2c3`** — six rows made true; `tools/pre-push` is the gate |
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
every cited URL answered (`irrigation 3e19a10`); the diary holds I1–I6. The `scripts/` budget rose
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
present, `63074ab` pushed.

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
come from `outcomes` in the three files C12 named (the finding-severity strings elsewhere are
another vocabulary, B17), and `tools/pre-push` is the versioned gate. Every Sprint 5 item — R11, P31, P8,
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
