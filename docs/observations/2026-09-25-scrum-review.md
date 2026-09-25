# Process review — 2026-09-25

Observer: a session given read access to both repos, the full git log, and permission to run the
plugin's own tooling and `tsci`. It built nothing and changed nothing except this file and its
rows in `INDEX.md`.

The brief was not "find defects" — two observers already did that and their 37 rows are in
`INDEX.md`. The brief was: **is the process working?** Claims are numbered `S1`–`S13` so they can
be logged one line each. Every one names something that was run or read.

> Note on ids: `INDEX.md` now has `S1`–`S13` from this review and `BACKLOG.md` has `S1`–`S10` as
> backlog items. They are different things. The `source` column disambiguates, but this is the
> second naming collision in a repo whose whole thesis is that an unscoped label is a defect
> class. Renaming one of the two sets is a five-minute job that should be done.

---

## The headline

The stated goal is **idea → parts → schema → simulation**. `DECISIONS.md` (written today, still
untracked) states it in those words and adds: *"Anything not on that spine is a distraction,
however interesting."*

**72.6% of all work done in this repo is not on the spine, and the spine does not build.**

I ran it. Both numbers are measured below.

---

## S1 — 27.4% of the work is on the spine. The largest single category is checks, which are not. *(measured)*

I attributed every line of every commit — 16,561 insertions + deletions across 64 commits — to a
category by file path. Script and method: reproducible from `git log --numstat`.

| category | lines | share | commits |
| --- | ---: | ---: | ---: |
| CHECK verification (`check_*.py`, `compare_design.py`, their tests) | 4,624 | 27.9% | 21 |
| REVIEW findings-store (`findings.py`, `spark-review`, `design-reviewer.md`) | 1,856 | 11.2% | 13 |
| META docs/audit (`docs/**`) | 1,767 | 10.7% | 7 |
| **SPINE** parts-library (`parts/**`, `parts.py`) | 1,345 | 8.1% | 13 |
| EVALS (`evals/**`) | 1,280 | 7.7% | 5 |
| META plugin prose (`README`, `BACKLOG`, `plugin.json`, `commands/`) | 1,268 | 7.7% | 19 |
| **SPINE** board-defs (`boards/**`, `boards.py`) | 1,153 | 7.0% | 7 |
| META skill prose (`skills/**` other than simulate/review) | 1,014 | 6.1% | 4 |
| **SPINE** schema-gen (`emit_board.py`) | 784 | 4.7% | 9 |
| **SPINE** pin-assign (`assign_pins.py`) | 569 | 3.4% | 4 |
| **SPINE** init (`init_project.py`) | 355 | 2.1% | 1 |
| **SPINE** simulate (`bench_sim.py`, `skills/spark-simulate`) | **338** | **2.0%** | 4 |
| META fixtures (`examples/`, `.spark/`) | 186 | 1.1% | 3 |

**SPINE total 4,544 (27.4%). Non-spine 12,017 (72.6%).**

Two things in that table deserve to be said out loud.

**The checks are bigger than the entire spine.** 4,624 lines against 4,544. `check_*.py` is
excellent work and it is the thing the README is honest about being the measured value. But it
verifies a design *somebody else already made*. It is not a step in idea → parts → schema →
simulation; it is a gate beside the last step. The backlog has never said so.

**Simulation — the fourth and final word of the stated goal — is 2.0%,** and what is there is
`bench_sim.py`, which its own commit (`45b5c2d`) calls *"a pretend bench, so the loop can be shown
without a real one"*. The step the goal ends on has never been started. `skills/spark-simulate`
is prose about Wokwi and a fake `machine` module, which is a real technique but is the *bin
project's* technique, documented, not a capability the plugin provides.

### The last day, separately

Last 20 commits: META docs 45.7%, CHECK 25.5%, SPINE 20.3%.

The ten commits of 2026-09-25 by intent:

| kind | commits |
| --- | --- |
| documents *about* the work | `086fe86`, `b32422a`, `10eea53`, `3d8e061`, `6be6ac0` — **5** |
| repairs of the author's own checks | `7f00547`, `3e8ed02`, `af702eb`, `244feb1` — **4** |
| new capability | `23170f7` — **1** |

Half a day of work produced five documents, four repairs and one feature. Two of the four repairs
(`244feb1`, and the untracked `emit_footprint.py` that follows from `23170f7`) *are* on the spine
and are the right target — so the direction turned this morning, which is to the author's credit.
What did not change is the ratio.

---

## S2 — The spine does not build. 0 traces, 10 errors, exit 1. *(measured, just now)*

`BACKLOG.md:390-393` states:

> `scripts/emit_board.py` closes it. `{"board": "firebeetle2-esp32s3", "parts": [...]}` produces a
> `board.tsx` that `tsci build` compiles, **that routes**, and that passes the buildability check
> out of the box

I ran exactly that. Input:

```json
{"board":"firebeetle2-esp32s3","parts":["l9110s-module","vl6180x-breakout","dfr0534-module"]}
```

`emit_board.py` refused first — correctly, and this is the best behaviour in the repo — because
the VL6180X has no recorded outline. With `--assume-missing-sizes` it emitted 82 lines. Its import
of `./FireBeetle2Esp32S3` resolves nothing in the plugin (`INDEX.md` R5), so I generated that with
the **untracked** `scripts/emit_footprint.py`, which works: 32 pads, 1.00 mm holes, silkscreen
labels in `portHints`. That is the R5 blocker genuinely cleared.

Then:

```console
$ tsci build board.tsx
Async effect error in PcbTraceRender "autorouting":
TypeError: undefined is not an object (evaluating 'connectedPort.x')
...
Build complete
  Circuits  0 passed 1 failed
⚠ Build completed with errors
Build exiting with code 1
```

From `dist/board/circuit.json`, counted the way `CLAUDE.md` says to count:

```
pcb_trace: 0
pcb_port_not_connected_error: 5
pcb_trace_missing_error: 5
source_component_pins_underspecified_warning: 3
source_no_ground_pin_defined_warning: 3
source_no_power_pin_defined_warning: 3
```

**Zero traces. Ten errors.** For comparison, the hand-made board in the sibling repo, same
command: 45 traces, 0 errors.

`DECISIONS.md`'s own spine table is more honest than `BACKLOG.md:393` — it marks "schematic
builds" as **blocked**. But it blames R5, the missing footprint module. R5 is now cleared and the
spine is still red. **The table was written from a hypothesis, not from a run.** That is the exact
habit this project exists to punish everywhere else.

---

## S3 — The cause: a part's `footprint` and its `pin_order` disagree, and nothing compares them. *(measured)*

`emit_board.py:253-254`:

```python
lines.append('    <chip name="%s" footprint="%s" pcbX={%g} pcbY={%g}'
             % (name, part.get("footprint", "pinrow4"), *placements[name]))
```

It takes the footprint string from the part file and, separately, writes `pinLabels` from
`pin_order`. Nothing checks that the two describe the same connector. For the VL6180X they do not:

| part file | `footprint` | `len(pin_order)` |
| --- | --- | ---: |
| `parts/dfr0534-module.json` | `pinrow10` | 10 ✓ |
| `parts/l9110s-module.json` | `headermodule6` | 6 ✓ |
| **`parts/vl6180x-breakout.json`** | **`pinrow5`** | **7** ✗ |
| **`parts/max98357a-dfr0954.json`** | **absent → `pinrow4`** | **12** ✗ |

So the generator writes `pinLabels={{ pin2: "VIN", pin3: "GND", pin4: "SDA", pin5: "SCL",
pin7: "GPIO1" }}` onto a five-pad footprint. `pin7` has no pad, so it has no `x`, and tscircuit's
autorouter dereferences `connectedPort.x` and dies — taking every other trace on the board with
it. One unmatched label costs all 45 traces.

The part file even explains the mismatch in prose it wrote itself
(`parts/vl6180x-breakout.json` → `//pin_order`): *"Pololu's 7-pin header reads VDD · VIN · GND ·
SDA · SCL · GPIO0/CE · GPIO1. This file wires five of them; pad 1 … and pad 6 … stay empty."*
Five wired, seven pads — and somebody wrote `pinrow5`.

`parts/max98357a-dfr0954.json` is worse: no `footprint` key at all, so it silently inherits the
`pinrow4` default with twelve pins to place. It was added yesterday (`cecc4bb`) and is the part
the whole audio decision now rests on. Nobody has emitted a board with it.

The invariant is one line — *the footprint must have at least as many pads as `pin_order` has
entries, and the pad-count in the footprint string must be derivable* — and 312 green tests do not
contain it. This is the project's own defect class (a fact nobody compares to another fact)
sitting in the generator, one layer below where `244feb1` looked this morning.

---

## S4 — The observations table is a graveyard, not a backlog. Its drain rate is exactly zero. *(measured)*

`INDEX.md` was created at **11:06 today** (`10eea53`) with 0 claim rows. By 11:20 (`3d8e061`) it
had 13. By 11:51 (`6be6ac0`), 37. It has 37 now.

**37 rows in 45 minutes. Zero rows drained, ever.**

That is not a figure of speech. I diffed the status column between `6be6ac0` and the working tree:

```console
$ diff <(git show 6be6ac0:docs/observations/INDEX.md | awk ...) <(awk ... INDEX.md)
$   # empty
```

No row has changed status after being written. Every `acted` and every `verified` was **born**
that way — written by an observer describing a fix that had already happened, or by the author
logging his own morning. The status column records history; it has never recorded a decision.

Current standing: **25 `raised`, 8 `verified`, 4 `acted`, 0 `rejected`.**

`rejected` is the state `INDEX.md`'s own preamble calls as important as `acted` — *"an observer
that is confidently wrong will be wrong the same way next time"* — and it has never once been
used. Of 37 claims from three independent observers, not one has been judged not worth doing.
That is not a sign the observers are perfect; it is a sign nothing is being judged.

### The proof it is a graveyard, in one line

`O4a` says `README.md:152` claims 265 tests. It was marked **`verified`** at 11:20 this morning,
with the note *"actual 301. Trivially stale, and the kind of number that should not be
hand-written."*

At 12:30, `README.md:152` still reads **"265 of them"**. The suite now runs **312**. The claim was
verified, filed, and in the four hours since has drifted 11 tests further from true.

`O4b` is the same story: 5 of 16 scripts still take no `--json` (`boards.py`, `check_bom.py`,
`check_design.py`, `emit_board.py`, `init_project.py`), against a README that says *"Every one
runs standalone, takes `--json`"*. Verified at 11:20. Unchanged.

Eight `verified` rows is eight defects that were reproduced by running something and then left in
place. **`verified` is currently a synonym for `raised` with more work behind it.**

### A policy that would hold

The table needs a closing move that is cheap enough to use. Three rules:

1. **WIP limit: 10 `raised` rows.** The eleventh raised claim cannot be added until one is drained.
   An observer that finds more than ten things reports the ten it would bet on and says it stopped.
   This is the only rule that changes the observer's behaviour, which is where the flood starts.
2. **Expiry: 48 hours.** A `raised` row untouched for two days is automatically moved to
   `rejected` with the reason *"expired — nobody reproduced it"*. It stays in the corpus, so it is
   not raised again, and the cost of being wrong about the expiry is one row's history.
3. **Triage is a commit, not a session.** One commit per batch of observations, and nothing else in
   that commit. Its message names the counts: `triage: 4 acted, 3 rejected, 6 expired, 12 raised`.
   Drain is then visible in `git log` without opening the file.

With those three, the current 25 `raised` becomes: keep the ten that touch the spine (R3, R5, R7,
R8, R16, R18, R19, plus S2/S3 below), reject the rest today with one sentence each. Half of them
deserve rejection on the stated goal alone — R6, R11, R12, R13, R14, R21 are all about *checking*
or *recording*, not about getting from idea to simulation.

---

## S5 — Rework is unchanged at ~40%, and it is additive, not destructive. That changes the fix. *(measured)*

`O2` measured 22 of 57 commits (39%) as the author repairing his own hours-old damage. Re-measured
on the current 64:

- **09-25 alone: 4 of 10 commits are repairs** (`7f00547`, `3e8ed02`, `af702eb`, `244feb1`) — 40%.
  The rate has not moved since it was raised.
- Deletions are only **1,225 against 15,336 insertions — 8.0%.** Almost nothing is thrown away.

That second number matters and nobody has said it. The rework here is **not** wasted code. It is
almost entirely *additive*: a check shipped that did not look, and a later commit adds the lines
that make it look. So the cost is not in lines. The cost is the **interval**, during which an
instrument stood in the repo reporting `[ok]` on something it had never examined. In this domain
the interval ends at a PCB order.

### Where the repairs come from

All four of 09-25's repairs were found by a **reader** — an observer report or a cold rebuild —
not by the test suite, which was green the whole time (312/312, `OK`, 0.086s). `check_physics` was
repaired twice in 15 minutes (`7f00547` 11:20, `3e8ed02` 11:35), a file whose defect `O1` had
found by reading the source that morning while the tests passed.

`DECISIONS.md:28` states the acceptance bar:

> **Mutation testing is the acceptance bar.** Re-introduce the defect; the suite must go red. A fix
> without a failing-first test is not a fix.

There is **no mutation tooling in this repository**. `grep -rn mutation` returns prose only:
`DECISIONS.md:28`, `BACKLOG.md:274`, `BACKLOG.md:292`, and five citations of those in the
observation essays. There is no `.github/`, no CI, and `.git/hooks/` contains nothing but
`*.sample`. The one automation that exists, `hooks/hooks.json`, shells out to `make check`, which
exists only in `smartbin-local` — a no-op for every other user and for spark's own checkout
(claims-audit `T3`).

**The project's acceptance bar is a sentence in a markdown file, enforced by the author's memory,
in a repo where 40% of commits are repairs of things the author remembered to test.** That is the
whole diagnosis. The mutation discipline is not failing; it is not running.

---

## S6 — WIP: twelve threads open at once, three of them uncommitted on disk right now. *(measured)*

Petr has twice asked for fewer parallel threads. Counted:

| # | thread | state |
| --- | --- | --- |
| 1 | `BACKLOG` N1 — bridge checks into findings store | open |
| 2 | `BACKLOG` N2 — `findings.py next --actionable` | open |
| 3 | `BACKLOG` N3 — rebuild evals | open, named 3×, zero movement |
| 4 | `BACKLOG` N4 — leaf checks count skips | half done (`check_physics`, `check_firmware`; `compare_design`, `check_vendor_pins` outstanding) |
| 5 | `BACKLOG` S5 — modules in, schematic out | **"*in progress*"** |
| 6 | `BACKLOG` S6 — evals for agent-shaped gaps | **"*in progress*"** |
| 7 | `BACKLOG` Debt — plugin prose length | open since `4067b4f` |
| 8 | `docs/audit-2026-09-24/` — 581 lines, ~60 findings | untriaged (`O9`) |
| 9 | `docs/observations/INDEX.md` — 25 `raised` | untriaged |
| 10 | `smartbin-local/.spark/findings.json` — 20 findings | 11 blocked, 8 open, **0 resolved** |
| 11 | `smartbin-local/STATUS.md` — 4 questions on Petr | unchanged verbatim for 2 days (`O8`) |
| 12 | uncommitted work, both repos | see below |

`git status` in `spark`, right now:

```
 M boards/firebeetle2-esp32s3.json
?? DECISIONS.md                 (5,112 bytes, written 12:26)
?? scripts/emit_footprint.py    (222 lines, no tests/test_emit_footprint.py)
```

`git status` in `smartbin-local`: `M .spark/board.json`, `M board-gerbers.zip`.

So: a 222-line generator that clears the single blocker on the spine has been sitting untracked,
untested, for under an hour — against the standing instruction *commit continuously* and against
`DECISIONS.md:28`'s own *"a fix without a failing-first test is not a fix."* The rule was violated
by the commit that wrote the rule down, before that commit existed.

Two of twelve threads are "in progress" simultaneously, which is the number Petr asked for. The
other ten are queues that only grow.

---

## S7 — There is no definition of done, and the bars differ by an order of magnitude within one repo. *(measured)*

```console
$ grep -rniE "done when|definition of done|acceptance|criterion|criteria" BACKLOG.md README.md
BACKLOG.md:365:  ... Criterion met and demonstrated: a new
BACKLOG.md:413:  *Done when:* the manufacturability eval has run with a baseline ...
```

Two of ten backlog items carry a completion criterion. One of those (`:365`) was written
retrospectively, after the item was marked done. Both are prose; neither is checkable by a
program.

The consequence is visible as four different bars in one repository:

| artifact | bar it actually shipped at |
| --- | --- |
| a `check_*.py` rule | unit test + mutation run + `could-not-run` accounting — **high** |
| a `parts/*.json` record | every fact carries a source — but no cross-check against its own footprint (`S3`) — **none** |
| a number in `README.md` | hand-written, compared to nothing (`S4`) — **none** |
| a `SKILL.md` `allowed-tools` list | does not include the commands the same file tells the model to run (claims-audit) — **none** |

### The one bar to adopt

One criterion, checkable, that subsumes the stated goal:

> **`scripts/check_spine.py` exits 0.** It runs, from a fixed three-module requirements file:
> `parts.py` → `assign_pins.py` → `emit_board.py` → `emit_footprint.py` → `tsci build` → counts
> `pcb_trace` > 0 and every `*_error` == 0 in the emitted `circuit.json`.

Nothing is done until that script is green. It is ~60 lines, it needs no new concepts, and it
would today print the two failures in `S2`/`S3` in under a minute. Run it as a pre-commit hook and
the 40% repair rate has somewhere to be caught before the commit message claims otherwise.

It also replaces a whole category of prose: `BACKLOG.md:393`'s "compiles, routes, passes" becomes
a green or a red rather than a sentence, and `DECISIONS.md`'s spine table stops needing a human to
keep it true.

---

## S8 — What to drop

Killing work is the point of this section. Each of these is measured, and each is off the spine.

**1. `scripts/findings.py` + `tests/test_findings.py` — freeze, and delete N1 and N2 from the
backlog.** 1,856 lines of churn (11.2%, the second-largest category in the repo), 8 commits, five
separate repair passes. The live store has stood at *20 findings — 11 blocked, 8 open, 1 rejected,
**0 resolved, 0 measurements*** since 2026-09-24 12:09, and `findings.py validate` reports 9 of
the 20 cite elements that no longer exist. The author does not use it: the six fab blockers went
into `STATUS.md` prose instead. N1 ("bridge the checks into the store") and N2 are both proposals
to build *more* on a store with a two-day record of zero throughput. Freeze it where it is; build
neither.

**2. `evals/` — delete the directory, or delete N3. Not both, and not neither.** 1,280 lines
(7.7%). Four cases, all still `schema_version: "1.0"`, two at `runs: 1`. Last run
`2026-09-24T17-16`; **54 of 64 commits postdate it.** `.gitignore` excludes `evals/results/`, so
the seven runs that §4b's central argument rests on exist on one laptop and nowhere else. N3 has
been named three times (`2aad767`, §4b, the Now list) with zero movement. An unclimbable rung on
the validation ladder is worse than no ladder, because it is still being cited.

**3. `docs/audit-2026-09-24/` — 581 lines, ~60 findings, no triage.** Either fold the survivors
into `INDEX.md` as rows under the expiry policy above, or delete the directory. `10eea53` built
exactly the right mechanism and did not point it backwards at the audit that motivated it.

**4. The observation essays — cap them.** `2026-09-25-work-pattern.md` (24 KB) and
`2026-09-25-claims-audit.md` (41 KB) were written today; this file adds a third. They found real
things — `O1` is the best bug report in either repo — but 65 KB of prose produced 37 rows of which
0 have drained. The finding is the row. Cap the essay at what will not fit in a row, and make the
row mandatory.

**5. `scripts/bench_sim.py`.** *"A pretend bench, so the loop can be shown without a real one"*
(`45b5c2d`). It demonstrates a loop nobody runs, feeding a store nobody reads. 217 lines, off the
spine, and its one purpose — `mp3-idle-current` — was made moot by the I²S decision.

**6. `skills/spark-reverse-engineer/` and `agents/design-reviewer.md` + the five review
dimensions — freeze, do not extend.** Reverse-engineering is genuinely good and genuinely not on
idea → parts → schema → simulation. The five reviewer dimensions were justified by one eval arm
whose reasoning was withdrawn 23 minutes later (`2aad767` → `249a33a`) and nothing has measured
them in the 54 commits since.

That is roughly **5,000 lines and four of the twelve WIP threads**, none of which moves the spine.

---

## What I would change, in order

1. **`scripts/check_spine.py` as the single definition of done, wired to a pre-commit hook.**
   Today it prints two failures (`S2`, `S3`). Nothing merges while it is red. Cost: ~60 lines plus
   the repairs it surfaces, maybe half a day. It is the only item here that pays back every day.
2. **Drain `INDEX.md` to ten rows today, then hold the limit.** 25 `raised`, drain rate zero,
   `rejected` never used once. Cost: one hour of rejecting things in writing, and the discipline
   to let an observer's finding die.
3. **Stop the two non-spine queues from growing: freeze `findings.py`, resolve `evals/`.** Drop
   N1, N2, N3. Cost: nothing but the discomfort of deleting a backlog item that was never wrong,
   only never worth doing first.

---

*Measured with: `git log --numstat` over 64 commits; `python3 -m unittest discover -s tests`
(312, OK); `scripts/emit_board.py --assume-missing-sizes` and `scripts/emit_footprint.py --board
firebeetle2-esp32s3` into a scratch directory; `tsci build board.tsx` against
`smartbin-local/node_modules`; a type census of the resulting `dist/board/circuit.json`;
`scripts/check_footprints.py` on the same; `git status` in both repos; and `diff` of the status
column of `INDEX.md` between `6be6ac0` and the working tree.*
