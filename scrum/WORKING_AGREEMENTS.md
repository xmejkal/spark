# Working agreements

The rules the team actually runs on. Each one names **where it came from**, because a rule whose
origin is forgotten is the first one somebody argues away.

A rule enters this file only from a retro or from Petr. It leaves only by being explicitly
retired, with a reason, in `RETROSPECTIVES.md`.

---

## W1 — A check that could not look must never read as a check that passed

Four outcomes, never two: `ok` · `problems` · `could-not-run` · `skipped`.

**Origin:** the runner reported `ok` for a flagship check that called a function which had never
existed. Six more instances have been found since, in different files, by different people.

**How we know it holds:** `check_all.py` has one function, `answer()`, that decides status, and
`check_spine.py` exits 2 rather than 0 when it could not be exercised.

## W2 — A test must run the thing, not read it

No assertion on source text. No assertion that is an arithmetic identity of the function under
test.

**Origin:** a test asserted `load("check_design")` appeared in the runner's source. The string was
there; the call beneath it named a function that did not exist. The test was green for the entire
life of the defect — it verified the check was *named*, not that it *ran*.

**Mechanical since P54 (2026-10-01):** `tests/test_self_confirmation.py` fails when a test reads a
module-under-test constant that is not shared vocabulary and has no written reason, and when a
shipped file is named by no mutation table and has no written reason. Its first catch:
`test_flash_image` found the filesystem at `flash_image.FILESYSTEM_OFFSET` — and passed with it
moved to an offset MicroPython never reads.

## W3 — Mutation testing is the acceptance bar

Re-introduce the defect; the suite must go red. Before commit, not after somebody finds it again.

**Origin:** repeatedly, a rule was found to have no test at all while its file had many.

**Known weakness, flagged by the scrum master 2026-09-25:** this is enforced by memory. There is
no tooling, no hook and no CI. Until there is, it holds only as long as somebody remembers — and
the first retro's action item is to stop relying on that.

## W4 — Never change a test to make it pass

Change the decision first; the test follows the decision. If the test is wrong, say why in the
docstring and change its *premise*, not its assertion.

**Origin:** Petr, verbatim: *"always never just change the test so that it passes or even just
delete it or similar instead of actually finding everything and be open about everything"*.

**Worked correctly on 2026-09-25:** `test_every_shipped_part_can_produce_signals` required every
part to ask the host for a pin, which a power inlet never does. The premise was wrong for a whole
category, so the rule underneath was restated — a part must ask for a pin *or* carry a rail — and
the docstring records why.

## W5 — State the scope of an assertion

"The FireBeetle" is two power designs. "The VL6180X breakout" is four pinouts. "The DFRobot MP3
one" is four products. An unscoped claim is a defect, not a shorthand.

**Origin:** a board file described one SKU and was true of half of them; a part file described one
carrier and was applied to another.

## W6 — Finish before starting

The board's limits are the rule: one item in each working stage, at most two in flight (one being worked, one
waiting), three in Ready. `tools/check_backlog.py` fails the push when a limit is broken, so this holds by command,
not by memory (P102a, 2026-10-05).

**Origin:** Petr, twice: *"make sure you often prioritize your work, finish before moving on to
too many things at the same time"* and *"go by priority and concentrate on the goal in mind"*.

## W7 — Don't reinvent what KiCad, Wokwi or tscircuit already do

Check whether it exists before building it. If it exists and works, lift or wrap it.

**Origin:** Petr, explicit. Vindicated immediately: a plan to import KiCad footprints was killed
when 18 of 27 were shown to convert to geometry identical to what already existed.

**Its other edge:** the bin's `circuit-to-wokwi` is 1645 lines of tested TypeScript that spark
does not have. Not reinventing means moving it, not rewriting it.

## W8 — Commit continuously, push often

Every landed piece of work is a commit whose message says what was wrong and why the fix is right.
The log is the team's memory; observers read it to find what nobody wrote down.

**Origin:** Petr, and `git checkout` is not an undo.

**Big items come through a pull request** (the PO, 2026-10-04). An item with a design or a plan of
several tasks — P82 was one, P84 will be — is built on its own branch and reaches `main` through a
GitHub pull request that names the item and the items it builds on, so the review and the link between
item and code stay on the public repository. Small fixes and scrum updates still go straight to `main`.

## W9 — An observer's claim is a hypothesis until reproduced

Several have been confidently wrong in ways that would have buried real defects. Reproduce, then
act. `rejected` is a real outcome and stays on the record so the same wrong claim is not raised
every run.

**Origin:** one council's central claim changed the roadmap and was right; another's verdict on
two of nine findings was wrong in a way that would have buried both.

## W10 — Simulation minutes are a budget, not a resource

~21 of 50 free Wokwi minutes remain. One scenario per question. Prefer any path that runs locally.

**Origin:** Petr, explicit: *"lets not waste the simulation minutes we already only have 21 of 50
free"*.

## W11 — Nobody but the Product Owner reorders the backlog

Agents and the facilitator propose, ranked, with reasons and costs. Petr decides, by the row order of the Ready
column on the board; refilling Ready is when he chooses what comes next. An agent that
reports something is "high priority" is reporting its own opinion and must label it as such.

**Origin:** this is what Product Owner means, and it was worth writing down because for two days
the ordering was done by whoever was typing.

## W12 — A fixture that cannot see the defect is the defect

When a mutation escapes, the first question is whether the fixture could have seen it at all.
Four escapes in Sprint 3 were exactly that — three LEDs never reached the tie a penalty breaks;
a fixture with no placeholder made two swapped sections invisible — and each was fixed by
strengthening the fixture. The mutation stays in the table. Dropping a mutation because "the
test cannot see that" is dropping the test.

**Origin:** R3.1, 2026-09-29. W3 makes the tool report the escape; this says what to do with it.

## W13 — A number enters a message only after its output is read

A count, a hash, a verdict ("the chain runs end to end") goes into a commit message, a backlog
result or a sprint log only in a later call than the command that produced it, copied from output
that is on the screen — **and measured on the tree being committed**: `check_commit.py` archives
HEAD and runs the suite and the anchors there before every push. A commit's message said 589 OK
while the tree it held ran 562 FAILED, because the run was on the working tree and the file it
imported was staged one commit later (close audit C3). And a commit is made only when every step
before it exited 0 — a chain that commits after a failed edit writes a message about edits that
never happened (`cdc7c81`). A value proof in a gated chain asserts the verdict string, never the
presence of output.

**Origin:** R3.5 said this as a rule about care on the morning of 2026-09-29 and was broken three
times before nightfall — 533 for 532, "reaches end to end" over "the chain is broken", 12 and 10 for
11 and 9 — every time by a message composed in the same command as the run. R4.1 makes it a rule
about sequence, which is the form that held for the rest of the day.

## W14 — Pull, never push

Nothing enters the plugin unless a real design is blocked without it that week, and the backlog
item names that design in a `**Needed by:**` line. A capability designed on paper — a review
loop, an eval harness, a research agent — is not built until a project reaches for it. An item
without a design behind it is not pulled; the suite refuses a backlog with one in it.

**Origin:** 2026-09-29, when a third of the repository was deleted as unused. Every piece of it
had been built because it was designed, not because a design needed it.

## W15 — An orphan fails the suite

Every script is named by a command, a skill, an agent, the README or a project's Makefile, or is
imported by another script; every skill and agent is named where a user looks; `scripts/` stays
within a line budget that a change may not exceed without deleting something. `tests/test_orphans.py`
holds all of it, so dead code cannot accumulate silently again — every piece cut on 09-29 had
tests, and looked alive.

## W15b — The size is said at every push, with its reason; refactor before growing

The `scripts/` size counts code lines only: docstrings, comments and blanks are free, because the prose
recording why a fix is shaped as it is, is the most valuable thing in this repository. **It is a number,
not a cap (P99, the PO, 2026-10-04).** The pre-push gate prints it with the growth since `origin/main`
(`scripts/: N code lines (+M since origin/main)`); an item's Done line says how many lines it added and
why, and the epic's review lists them. The cap it replaced failed the suite: P95 raised it six times,
each time to whatever had been measured, and it prompted one refactor of two lines — what caught bloat
there was the reviews and W15's orphan tests, which stay exactly as they are. When an item grows a lot,
the first question is still whether the same behaviour fits in less code — the three-outcome verdict
was written out in three places and one of the three was wrong (P34).

## W16 — A replacement deletes what it replaces, in the same commit

When a new path replaces an old one — a file format, a check, a command — the old one goes in the
same commit. Two formats for one thing is a bug, not a transition: `design.json` and `check_design`
lived beside the requirements chain for four days, and the item "the two tools disagree" existed
only because both did.

## W17 — A summary claims no more than what it summarises

A Done line, a log sentence, a diary count or a commit's first line is checked against the diff
or the output the way a number is (W13): "moved" means the old copy is gone, "fixed" means the
gap's own command now passes, "one home" means a grep finds one, "unchanged" means the file was
regenerated and compared. The v1 close audit found every count true and four verbs false (D9,
D13, D19, D21, D22): the words were the numbers in disguise. Written 2026-09-30 (R5.1).

## W20 — An item's own acceptance line is a hypothesis until reproduced

W9 says this about an **observer's** claim. It did not say it about ours, and that gap cost a whole
sprint's worth of credibility twice in one day.

**P45's acceptance line** said `init` should write the DS3231's two bus lines. That module's record
says, in its own words, *"Add NO pull-ups: the module carries 4.7 k on SDA and SCL."* Meeting the
criterion as written would have shipped a check that fires on a **correct** board — the one failure
this product exists to prevent.

**P33 is worse**, because it shipped. Its `Value proven by` line is `npm install` in a fresh
project. That command fails today: `init` pins `@tscircuit/cli@0.0.2600`, and `0.0.2600` is a
version of the **`tscircuit`** package — `@tscircuit/cli`'s 0.0.x line stops at `0.0.394`. The item
was marked DONE without its own proof command being run on a machine with no global CLI on PATH.

**And it catches a gameable line before it is built.** P50's proof line asked an isolated agent to
rediscover three escapes that are written down in `scrum/SPRINT.md` — readable by any agent with
`Read`. An open-book exam scored as isolation.

So: **before an acceptance line is relied on, reproduce the state it assumes** — or mark it
unverified, the way a part record marks a fact nobody has confirmed. An item may be written with an
unreproduced criterion; it may not be *closed* on one.

**W13 gains a clause with it:** a number that has not been run carries the word *estimate*, and the
measured one replaces it in the same table. `docs/2026-09-30-refactoring-architecture.md` put
**−45 code lines** for P42 in the same table as measured facts; it came to −8. P35 was estimated at
−40 and measured −22, P29 at +20 and measured +22.

## W19 — The item exists before the work starts

If work is not on the board, it is not happening; W19 says when. An issue is created on the project, with its
*Needed by* and *Value proven by*, **before** the first command of the work is run, including for work that only
produces a document — an audit, an architecture, a piece of research — and a feature's PR says `Closes #N` (since
2026-10-05, P102a). The item may be a single paragraph, and it may be refined once the work reveals its shape, but it exists first, so
the work can be tracked, sized, and stopped.

Written 2026-09-30, at the PO's word — "whenever we want to do something, let's first make sure
the PBI is created, so we can keep track, really just like scrum" — after an architecture review
was set going with no item behind it.

## W18 — Refinement is the team's, and the PO has the last word before the order is fixed

An item is refined **with the team** — the expert lenses and the scrum master, never by the person
who will implement it alone — and the refined text goes to the Product Owner with a concrete
question before it enters Ready. Each item must be small enough to finish in one
sitting, testable by a command whose output the PO can read, sensible on its face, free of
anything no design needs (W14), and **started things finish before new ones start**.

The failure this prevents is the one the PO named on 2026-09-29 — "I don't want it to get AI
bloated, never finishing, too many not even used parts" — which a refinement done alone
reintroduces, because whoever is doing the work is the worst judge of whether the work is needed.
Written 2026-09-30, at the PO's word.

## W21 — Keep a datum only if a decision rests on it

**Adopted by the PO on 2026-10-03, after the data council** (five lenses: a senior hardware engineer, a
data steward, a minimalist economist, the hobbyist's advocate, and a devil's advocate for keeping). It
**replaces his rule of 2026-09-29** — *"whatever you find online is kept, chosen or not."*

> **Keep a datum only if a decision rests on it — by code, by a check, or by a person at the moment
> they decide — and it stays true without upkeep (a part number, a printed version, a page). Point at
> everything else. Never gather what no decision reads, or what changes before anyone reads it again.**

Why: about 38 % of research tokens went to data no decision used — seller listings (19 %), full
records for candidates nobody chose (13 %), the datasheet of the chip inside a module (5 %), whole
datasheets (1 %). But "no code reads it" is the wrong test: 79 of 140 facts sampled are what a design
decision rests on, and the warnings that found today's wrong boards were read by a person. So the
test is the decision, and a warning that protects a board must be SHOWN where the decision is made —
a typed fact or a check that prints, never only a prose note (P81).
**Checked by:** `agents/parts-researcher.md` and `commands/research.md` carry the sentence; the
validator refuses what the principle forbids as P80, P81 and P83 make it mechanical.
