# How this team works

Everything the team runs on is a file in this folder. Nothing lives only in an agent's head or in
a conversation that scrolls away — if a rule, a goal or a decision is not written here, it is not
in force.

Two repositories, one team, one backlog:

- **`spark`** — the product. A Claude Code plugin for AI-assisted electronics design.
- **`smartbin-local`** — the test case. An ESP32 bin controller, and the only real evidence that
  spark works. Work on the bin is justified when it exercises or proves spark, and otherwise it
  competes with the product for the same hours.

## The people

| role | who | decides |
| --- | --- | --- |
| **Product Owner** | **Petr** | what is worth building, and in what order. Nobody else reorders the backlog. |
| Facilitator / dev | the main Claude session | how it gets built, and says when it is done |
| The team | the agents in [`../agents/`](../agents/) | the work, each in their discipline |

Petr is the Product Owner and that is not decorative. Proposals for ordering come to him ranked
with reasons; the ranking is a recommendation until he says otherwise. An agent never decides that
something is valuable — it can only report what something costs and what it would prove.

## The artifacts

| file | what it is for |
| --- | --- |
| [`PRODUCT_BACKLOG.md`](PRODUCT_BACKLOG.md) | **the single ordered list.** Every PBI, with its value and how we will know it worked. |
| [`SPRINT.md`](SPRINT.md) | the current goal, what was pulled, the daily log, and what is blocking |
| [`RETROSPECTIVES.md`](RETROSPECTIVES.md) | every retro, the change it produced, and **whether that change stuck** |
| [`WORKING_AGREEMENTS.md`](WORKING_AGREEMENTS.md) | the rules, and where each one came from |
| [`TEAM.md`](TEAM.md) | the roster and the test each member has to pass to exist |

There is exactly one backlog. `BACKLOG.md` at the repo root is now **narrative** — how the product
got here and what was learned — and `docs/observations/INDEX.md` is **raw observation intake**.
Neither is a queue of work. Anything in either that should be built is a PBI here or it is not
happening. That consolidation is deliberate: three parallel lists is how 37 observations and 20
findings reached zero resolved between them.

## The ceremonies, and what each one must produce

A ceremony that produces nothing is a status meeting. Each of these has an output that changes a
file, or it did not happen.

| ceremony | when | must produce |
| --- | --- | --- |
| **Planning** | start of a sprint | a **one-sentence sprint goal** and the PBIs pulled to serve it, in `SPRINT.md`. A goal naming two things is two sprints. |
| **Daily** | each working session | a line in `SPRINT.md`'s log: what moved, what is blocked, what is next. Impediments named, not endured. |
| **Review** | end of a sprint | **validated value** — see below. Petr sees the thing working, or hears plainly why he cannot. |
| **Retro** | end of a sprint, after review | one change to how we work, written into `WORKING_AGREEMENTS.md`, **with a check that tells us later whether it stuck**. |

## Validating value, which is not the same as finishing

A PBI is **Done** when the Definition of Done passes. A PBI has **delivered value** only when the
thing it promised is demonstrably true for Petr. These come apart constantly, and the gap is where
this project has lost most of its time.

Worked example, from this project, in one day: a footprint generator was written, tested, mutation
tested and committed — Done by any reasonable bar. The chain it was meant to unblock still emitted
a board with zero traces, so the *value* was zero until four further defects were found. The
review that matters asks **"can Petr now do the thing?"**, not "did the work complete?".

So every PBI carries a `Value proven by:` line naming a command whose output Petr can read, and
review runs those commands. If a PBI cannot name one, it is not ready to be pulled.

## Definition of Done

Every one of these, for every PBI. No exceptions, no "mostly".

1. `python3 -m unittest discover -s tests` — green.
2. **Mutation tested.** Re-introduce the defect the change prevents; the suite must go red. A fix
   with no failing-first test is not a fix.
3. `python3 scripts/check_spine.py` — exit 0. The chain still runs end to end.
4. The PBI's own `Value proven by:` command runs and shows what it claims.
5. Committed, with a message saying what was wrong and why the fix is right.
6. Any claim it makes in a docstring or README is **true when run**, not when written.
7. Its Done line says how many code lines it added to `scripts/` and why — the pre-push gate prints the
   figure (W15b, P99).

**At each sprint's close** (P98): `python3 tools/mutate.py tests/mutations/*.json` — every table in one sweep, which
prints its time. An escape is a missing test, opened as a backlog item the same day.

A stage that could not be exercised is `could-not-run`, never `ok`. That rule outranks every other
sentence in this folder.
