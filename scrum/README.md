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
| **the spark project** (https://github.com/users/xmejkal/projects/2) | **the board, since 2026-10-05 (P102a).** Every item is an issue, with its *Needed by* and *Value proven by*; Kanban stages and limits (`docs/2026-10-05-backlog-in-github-design.md` §3); the Ready column's order is the PO's. The bin's own board: https://github.com/users/xmejkal/projects/1 |
| [`PRODUCT_BACKLOG.md`](PRODUCT_BACKLOG.md) | **the archive, frozen 2026-10-05.** Every heading says where its item went (MOVED to an issue) or how it ended |
| [`SPRINT.md`](SPRINT.md) | the history of Sprints 1–10 |
| [`RETROSPECTIVES.md`](RETROSPECTIVES.md) | every retro, the change it produced, and **whether that change stuck** |
| [`WORKING_AGREEMENTS.md`](WORKING_AGREEMENTS.md) | the rules, and where each one came from |
| [`TEAM.md`](TEAM.md) | the roster and the test each member has to pass to exist |

There is exactly one backlog: the spark project's board. `BACKLOG.md` at the repo root is **narrative** — how the product
got here and what was learned — and `docs/observations/INDEX.md` is **raw observation intake**.
Neither is a queue of work. Anything in either that should be built is an issue on the board or it is not
happening. That consolidation is deliberate: three parallel lists is how 37 observations and 20
findings reached zero resolved between them.

## The ceremonies, and what each one must produce

A ceremony that produces nothing is a status meeting. Each of these has an output that changes a
file, or it did not happen.

Since 2026-10-05 the team works **Kanban with a day-close** (P102a; the PO's choice after a three-lens council). There
are no sprints; the cadences are these.

| cadence | when | must produce |
| --- | --- | --- |
| **Replenish** | Ready runs low | the PO orders the Ready column (at most three); refilling it is when he chooses what comes next |
| **Day-close** | the end of each working day | one dated line: what moved, what was proven, what is aging, the next card — posted as a status update on the spark board with `tools/board.py close` (P102c). Claude writes it when the PO stops; a session that opens with *"! the day of … has no close"* writes that day's close first, with `--date` |
| **Weekly look** | once a week | the PO's look at the board: anything waiting more than three days, epics started and finished |
| **Epic done** | an epic's last story is Done | its **review** (validated value — see below), the **outside audit**, then the **retro**: one change to how we work, written into `WORKING_AGREEMENTS.md`, **with a check that tells us later whether it stuck** |

## The flow — an item's stages

Every item is an issue on the board, and its card moves through the stages as the work does (the stages and limits:
`docs/2026-10-05-backlog-in-github-design.md` §3; `tools/check_backlog.py` enforces the limits at every push).

| stage | what happens there | how |
| --- | --- | --- |
| **Idea** | the PO's words are recorded as an issue — nothing more (ideas stay ideas) | the issue form: *Needed by*, *Value proven by* |
| **Discovery** | who it is for and what it is: the journeys, the story map, the PO's answers | with the PO, one question at a time; the journeys and map kept as text in the repo and drawn in Miro and Canva (P102b); a discovery skill (P102e) |
| **Design** | a spec, reviewed by a council, approved by the PO | superpowers' brainstorming, then the spec in `docs/` |
| **Ready** | approved and ordered by the PO; at most three | the PO's row order is the order (W11) |
| **Build** | a plan, its council, the PO's choice of execution, then the tasks test-first | superpowers' writing-plans, then executing-plans or subagent-driven-development; the plan's tasks become sub-issues |
| **Review** | the final review on the most capable model, one fix pass, the PR open | the PR says `Closes #N` |
| **Done** | merged **and** its *Value proven by* has run | the proof is posted on the issue |

Chores and bugs skip Discovery and Design. At every session start, in the PO's project folders, `tools/board.py
status` prints the board — what is in flight and for how long, what waits on the PO, Ready, the open PRs, the last
close (P102c's hook, in the PO's own settings).

**A plan's tasks are sub-issues of their story** (labelled `task`): they show the story's progress on the board and
ride on it — no slice, *Needed by* or WIP of their own (`tools/check_backlog.py` skips them, as epics carry no limit).

The trial is checked on 2026-11-02: was the Build limit broken without being caught, was a weekly look skipped twice,
do epics start and finish? If not, one-day sprints replace it (the design's §9).

## Validating value, which is not the same as finishing

An item is **Done** when the Definition of Done passes. An item has **delivered value** only when the
thing it promised is demonstrably true for Petr. These come apart constantly, and the gap is where
this project has lost most of its time.

Worked example, from this project, in one day: a footprint generator was written, tested, mutation
tested and committed — Done by any reasonable bar. The chain it was meant to unblock still emitted
a board with zero traces, so the *value* was zero until four further defects were found. The
review that matters asks **"can Petr now do the thing?"**, not "did the work complete?".

So every issue carries a *Value proven by* section naming a command whose output Petr can read, and
review runs those commands. If an item cannot name one, it does not enter Ready.

## Definition of Done

Every one of these, for every PBI. No exceptions, no "mostly".

1. `python3 -m unittest discover -s tests` — green.
2. **Mutation tested.** Re-introduce the defect the change prevents; the suite must go red. A fix
   with no failing-first test is not a fix.
3. `python3 scripts/check_spine.py` — exit 0. The chain still runs end to end.
4. The item's own *Value proven by* command runs and shows what it claims, and its output is posted on the issue.
5. Committed, with a message saying what was wrong and why the fix is right.
6. Any claim it makes in a docstring or README is **true when run**, not when written.
7. Its Done line says how many code lines it added to `scripts/` and why — the pre-push gate prints the
   figure (W15b, P99).

**When an epic is done** (P98; P102a moved it from the sprint's close): `python3 tools/mutate.py tests/mutations/*.json` — every table in one sweep, which
prints its time. An escape is a missing test, opened as a backlog item the same day.

A stage that could not be exercised is `could-not-run`, never `ok`. That rule outranks every other
sentence in this folder.
