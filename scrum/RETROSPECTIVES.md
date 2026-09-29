# Retrospectives

One entry per retro. Each carries **the change it produced** and **a check that tells us later
whether it stuck** — because an action nobody verifies is the thing retros are famous for.

The check is run at the *next* retro and its result written into the previous entry. An action
that did not stick is not quietly dropped; it is recorded as not having stuck, and we ask why.

---

## R1 — 2026-09-25, on the two days before the team existed

**Present:** facilitator, scrum-master agent (reported independently, having read the commit log
and run the tooling itself).

### What happened

The product goal was reached on one axis and not started on the other. `idea → parts → schema`
went from never having been run end to end to exit 0 with 8 traces. `→ simulation` is untouched.

### What went well, with evidence

- **Outside eyes found what the tests could not.** The scrum-master agent found the root cause of
  the zero-trace board — a part file whose footprint said 5 pads beside a pinout naming 7 — that
  350 green tests did not. That is the fourth time a reader has beaten the suite.
- **The honest-reporting rule paid out in cash.** Teaching `check_footprints` to read pill holes
  took a few lines and immediately found two real fab blockers on a board declared ready to order.
  The rule that a check which could not look must not read as a pass is now load-bearing, not
  aspirational.
- **Two councils killed a week of work correctly.** A KiCad footprint-import pipeline was proposed
  and abandoned when 18 of 27 footprints were shown to convert to geometry identical to what
  already existed.

### What did not

- **A claim was overstated in a commit message.** "The emitted board now BUILDS" was written while
  `tsci build` exited 1. The schematic built; the build did not. Written by the person who wrote
  the rule against exactly this, and caught by an agent, not by the author.
- **Every link was tested and the chain was not.** Each component did precisely what its own tests
  asked, and the product produced a board with no copper for weeks. Unit tests cannot see this
  class of defect; only running the whole thing and counting the output can.
- **Work was scattered across three queues** — `BACKLOG.md` §5, `docs/observations/INDEX.md`, and
  a findings store — which between them resolved nothing. Two parallel lists is a backlog; three
  is a graveyard.
- **The rework rate is real.** A measured ~39% of commits repaired damage hours old. Mostly caught
  by readers rather than by the suite, which points at the discipline, not the people.

### Actions — the changes this retro produced

| # | change | check that it stuck | result |
| --- | --- | --- | --- |
| **R1.1** | The chain gets one gate that runs it end to end and counts traces, not exceptions. **Done same day** — `scripts/check_spine.py`, and it is clause 3 of the Definition of Done. | At R2: has any PBI been called Done while `check_spine.py` was red or unrun? | **stuck.** Chain green through nine fixes: 5 stages ok, 12 traces, 10 wires, exit 0 on 2026-09-29 |
| **R1.2** | One backlog. `scrum/PRODUCT_BACKLOG.md` is the only queue; `BACKLOG.md` becomes narrative and `INDEX.md` becomes intake. A claim becomes work only by being promoted to a PBI. | At R2: count rows added to `INDEX.md` vs rows promoted or **rejected**. If `rejected` is still zero, this did not stick. | **did not stick.** 59 rows: 46 raised, 7 verified, 6 acted, **0 rejected**. G14 was rejected — in the diary and the backlog, never in the intake table |
| **R1.3** | Mutation testing stops being enforced by memory. → **P4** in the backlog. | At R2: does `scripts/mutate.py` exist and is it used in a commit? | **did not stick.** Does not exist. ~30 mutations run by hand this sprint; two escaped (trace sizing, placeholder wiring) until happened upon |
| **R1.4** | Every PBI names a `Value proven by:` command before it can be pulled, and review runs it. Aimed squarely at the gap between Done and valuable, which cost this project the most time. | At R2: was any PBI pulled without one? Did review actually run them? | **stuck**, with a caveat: every task item has one and each DONE cites its command. R8 and R10 lack one by design — they are PO decisions, not tasks |
| **R1.5** | Keep an outside reader running. The evidence is now four-for-four: every serious defect came from someone not doing the work. | At R2: did an observer run during the sprint, and was its report reproduced before being acted on (W9)? | **stuck.** Gap recorder ran (G8–G14); auditor running now. W9 earned its keep: G14 was reproduced and found wrong |

### What we are deliberately not changing

The rework rate, directly. Two of the five actions above (R1.1, R1.3) attack its causes — no
end-to-end gate, and a discipline held only in memory. Adding a rule that says "make fewer
mistakes" would be the kind of action that cannot be checked, which is what this table exists to
prevent.


---

## R2 — 2026-09-29, on the cold test and the sprint that fixed it

**Present:** facilitator; independent auditor (reporting separately, reading the same evidence
cold).

### What happened

The plugin was used to build something that is not the smart bin — an RC car and its remote —
from scratch, with a plan written first so its predictions could be scored. Both boards build.
Fifteen findings; nine fixed in three days, each reproduced first and each mutation-tested.

### Scoring the plan

All five predictions in `PLAN.md` hit. **But six of the fifteen findings were not predicted, and
they were the worse ones.** The predicted gaps were *structural* — no servo part, one board per
project, no PWM notion, no link between designs, no source for the 5 V rail. The unpredicted ones
were *silent wrongness*: rails dropped without a word (G2), five components collapsed to one (G7),
a second board turning six checks off with an `ok` (G8), the validator crashing on the input it
exists to catch (G15). A plan can foresee what a tool lacks. It cannot foresee what a tool lies
about, and those are the ones that matter.

**The audit sharpened this** (`docs/observations/2026-09-29-sprint-audit.md`, read cold after
R2 was written): 4 of 5 by area, **0 of 5 by mechanism**. Every prediction was readable from the
inventory without running anything; every unpredicted finding was existing code under new input.
Even inside the predicted areas, four findings were BUGs predicted as GAPs — the plan could say
where the tool was missing, never that it would say "ok" there. That is why R2.5 asks for a
third cold test rather than a better plan.

### What went well, with evidence

- **Measure before fixing paid out four times.** The "1.20 mm trace" was six pad necks 0.12–0.85 mm
  long. The selector-safe character set came from a probe board, not a guess. The intake claim
  G14 was reproduced and found wrong — and the reproduction found G15, which was real.
- **Fixing at the cause, not the site.** The validator crash was fixed once in `needs` and the
  test for it found the identical crash in `power`; the contract now covers all three lists.
- **The refactor was earned, not scheduled.** `copper.py` exists because two modules needed one
  formula and one was reaching into the other by `importlib`.

### What did not

- **Two retro actions did not stick**, and the honest reading is that neither had a forcing
  function. The intake table is not on anyone's path; the mutation discipline lives in memory.
- **Two mutations escaped**, both the same shape: the helper was tested and the integration was
  not — "the generator stops sizing traces" and "the wiring passes an empty list".
- **The patch-not-audit pattern recurred three times** (signal prefix at three sites, `["pin"]`
  at four, power traces in two loops). Caught each time, but each time *after* the first fix.

### Actions

| # | change | check that it stuck | result |
| --- | --- | --- | --- |
| **R2.1** | Build `scripts/mutate.py` NOW, in this retro, because R1.3 failed for want of a forcing function. | At R3: every DONE item since cites a `mutate.py` run. | **stuck.** Built in R2 itself (`997b756`); every DONE since — P3 `831f756`, A3 `5689147`, P11 `0c21ef5`, P12 `c4d0582`, P13 `55e7bb8`, P14 `f7674b4` — cites a `mutate.py` run: 30 mutations in five tables, all caught |
| **R2.2** | Every fix that touches an integration gets an integration test, not only a helper test. Named for the two escapes. | At R3: any escaped mutation whose cause was "helper tested, consumer not". | **stuck, and a new shape appeared.** No escape this sprint was "helper tested, consumer not". Four escapes were **"the fixture cannot see the defect"**: P3's three (three LEDs never reached the tie the penalty breaks) and P14's one (no placeholder in the fixture, so a swapped section changed nothing). All four fixed by strengthening the fixture, none by dropping the mutation → R3.1 |
| **R2.3** | Before fixing a rule at one site, `grep` for its other sites — the three recurrences all had a greppable anchor. | At R3: count of commits that say "same defect, second site". | **partly.** One second site found in flight — P11's converter lookup from `cwd`, the same defect one stage later, fixed in the same change — and one found by the audit from before R2 (A3, the double report). Zero "same defect, second site" commits after the fact |
| **R2.4** | Retire the intake table's `raised` backlog: every row either promoted to a PBI, or `rejected` with a reason, before R3. | At R3: `raised` count in `INDEX.md`, and whether `rejected` is still zero. | **did not stick.** 23 rows closed on 09-29 — the audit's 16 and 7 stale ones — and **42 `raised` rows remain** (first written 43, by eye), all from the 09-25 reports. `rejected` still unused → R3.2 |
| **R2.5** | Third cold test in a different domain — to be chosen by the PO — because both silent-wrongness classes were found only by building something new. | At R3: the diary of that test exists and is scored against its plan. | **pending on the PO.** No domain chosen; three proposed in `SPRINT.md`. Not started, deliberately: the domain is the whole point of the test |


---

## R3 — 2026-09-29, evening, on the audit sprint

**Present:** facilitator. No independent reader during this sprint — the audit that opened it was
the outside read, and R3.3 makes one close every sprint from now on.

### What happened

Sprint 3's four items were done in one day, each mutation-tested, on top of P3 and A3 from the
morning. The audit's sixteen claims were triaged and **none rejected**: a cold read after a fix
sprint found the "less than asked, exit 0" family a sixth time, inside the commit that had closed
the fifth, in the one function nothing tested. Twenty-three intake rows closed; forty-three did
not.

### What went well, with evidence

- **Measure before fixing, twice more, and both times the measurement changed the fix.** P3: the
  bus penalty is a tie-breaker, not a cost — the first value (15) was wrong and the ordering test
  caught it. P12: the "toolchain fault" was the spine's own `node_modules` link; fixed at the
  cause, the A/B reads `ok` / `ok` with the version named instead of `could-not-run` / `ok`.
- **The mutation tool as a fixture critic.** Four escapes, all one shape — the fixture could not
  see the defect — and all four fixed by strengthening the fixture, none by dropping the mutation.
  R2.2's shape ("helper tested, consumer not") did not recur.
- **Fixed at the contract and said in the file.** A rail-less MCU pad is refused where the board
  file is read *and* reported by the generator if one reaches it anyway; the `continue` is gone at
  both layers.
- **A test's docstring caught describing a test that did not exist.** The wiring test claimed to
  call the runner and grepped the source; the mechanism changed under it and it failed, which is
  how the claim was found. It now asks the code, and its docstring records the episode.

### What did not

- **The intake did not drain — second retro in a row.** 42 `raised` rows from 09-25 remain (first
  written 43, by eye — audit B12) and
  `rejected` is still unused. The cause is plain: nobody's path crosses the old rows; only new
  reports get read.
- **R2.5 sat.** "To be chosen by the PO" is not a question anyone asked; a decision nobody is
  asked for is not made.
- **Two records overstated in the same hour** — "the table has drained" (23 of 66), corrected
  before commit, and the summary written before the count was the pattern both times.
- **No outside reader ran during the sprint.** Every serious defect this project has found came
  from one (R1.5); a sprint without one is running on the author's blind spots.

### Actions

| # | change | check that it stuck | result |
| --- | --- | --- | --- |
| **R3.1** | A weak fixture is a defect: when a mutation escapes because the fixture cannot see it, the fixture is fixed and the mutation stays. Written as **W12**. | At R4: any mutation removed from a table; escapes listed with their cause | *pending* |
| **R3.2** | Drain the 42: **P15**, first item of Sprint 4, half a day, time-boxed. Each row reproduced against today's code or `rejected` as superseded, with the commit that made it so. | At R4: `raised` count in `INDEX.md`; `rejected` > 0 | *pending* |
| **R3.3** | An outside read CLOSES every sprint: the audit agent runs at sprint end, its claims go through `INDEX.md` before anything is acted on (W9). | At R4: the Sprint 4 report file exists and its rows are in `INDEX.md` | *pending* |
| **R3.4** | Ask the PO the R2.5 question so it is one word: three concrete domains in `SPRINT.md`. | At R4: a domain chosen, or the item explicitly parked by the PO | *pending* |
| **R3.5** | No summary before its count: a "N rows/tests/items" claim in a record is written from a command run that day, and the command is beside it. | At R4: count the numeric claims in `SPRINT.md` that carry their command | *pending* |

