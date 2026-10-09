# The backlog in GitHub — design (P102a)

**Status:** the spec, for the PO's review (2026-10-05). Designed with the PO in one sitting, after he asked for the
tools chore (P102) before the next epic. It takes in P70 (2026-10-03), whose design stands except where §2 says
otherwise. Every decision the PO made is in §11 with its date.

## 1. What it is for

The PO, 2026-10-05: *"switch to github projects, for every epic and user story if appropriate … so that the new
functionality can already be having good discovery and the PB and the epic and also planning tasks for user stories
is already in gh."* He also asked to be *"always aware of what we're actually doing now, what the functionality is …
how much of that is already working and what's remaining, also if we're actually finishing epics."*

So the backlog moves out of a 1,200-line Markdown file, and into issues and a board that show:
- what is in progress;
- which epic each story belongs to;
- whether an epic's stories are finished.

**Done means** (P70's line, kept):
- `gh project item-list` lists every open spark item with *Needed by* filled;
- the frozen file says it is the archive;
- the W14 check reads the issues and fails on one without *Needed by*.

## 2. Where things live — each repository its own project

The PO, 2026-10-05: *"I'd like spark to have a separate gh project and repo and also the demo projects should."* This
replaces P70's "one user-level project spans spark and the bin".

| repository | its project | what goes there | done by |
| --- | --- | --- | --- |
| `xmejkal/spark` (public) | **spark** (public, user-level) | every spark item | this spec |
| `xmejkal/sisuo-brain-transplant` (public) | **the bin** (public) | the bin's items: B1, B5, B8 | this spec |
| `xmejkal/spark-demos` (new, public) | **spark demos** (public) | irrigation, rc-car, plant-alarm, the quickstart and P100's new idea, one folder each | P102f, its own design — each history is checked before it is published (vendor files, GPS in photos, tokens) |

A demo that becomes a real product moves out to its own repository, as the bin did.

## 3. The project

The same shape for spark and the bin.

The team works **Kanban, with a day-close** (the PO, 2026-10-05, after a three-lens council; §9). There are no
sprints and no iterations.

- **Status: the stages of our flow.**

  | stage | true when an item is here | WIP limit |
  | --- | --- | --- |
  | **Idea** | the PO's words are recorded, nothing more (ideas stay ideas) | — |
  | **Discovery** | journeys, story map, the PO's answers: what it is and who it is for | 2, epics count |
  | **Design** | a spec is written and reviewed by the council, and waits for the PO's yes | 2, epics count |
  | **Ready** | the spec is approved and *Value proven by* is set; this column's order is the PO's | 5 |
  | **Build** | plan, plan council, then the tasks with their reviews (decision 6, 2026-10-06: no plan yes unless the plan widens scope or goes past the allowance) | 2 |
  | **Review** | final review, fix pass, PR open, waiting for the PO's merge | 2 |
  | **Done** | merged **and** its *Value proven by* has run | — |

  - **At most 4 items are in flight** across Discovery, Design, Build and Review, and each of those stages takes 2:
    the PO's call of 2026-10-06 evening, after the first day at the cap of 3 (§11).
  - **What counts** (raised on 2026-10-06, §11):
    - an epic counts in Discovery and Design, where it is the work itself; from Build on its stories carry the limit;
    - a card is in its working stage while any work runs on it, a background read included; a read that only answers a
      question puts its card back in Idea when the answer is posted;
    - every card counts: a card that one PR closes together with another still counts on its own, so a pair that one
      PR closes fills Build.
  - Chores and bugs skip Discovery and Design and enter at Ready.
- **Waiting on:** a single select (the PO / hardware / outside), with **Waiting since**, a date. Waiting is a flag
  that stays on the card in its stage, not a column. Anything waiting more than 3 days is named at the weekly look.
- **Slice:** a single select. Its options are the story map's slices 1–10, *team tools* and *desk lane*. It places an
  item on the map, as `STORY_MAP.md` does today.
- **Order:** the Ready column's row order, set by the PO by dragging (W11: the PO orders). Refilling Ready is when he
  chooses what comes next.
- **Views:**
  - Board by Status, with the column limits above;
  - Table (all fields);
  - Roadmap by Slice.

  GitHub's API cannot create views or set a column limit. They are made by hand in the browser, a few clicks, by the
  PO or by Claude with his go. A column limit on GitHub only warns, so §8's check is what enforces it.
- **Proven** (proven / not proven / not run) is added by P102d, not here.

## 4. Issues

- **One issue per item,** in the repository it is about.
- **The title keeps the id,** so commits, plans and the archive still trace: `P96 — Store 1b: a goal, matched`.
- **The body comes from an issue form,** `.github/ISSUE_TEMPLATE/item.yml`. Its sections are:
  - *Needed by* (required);
  - *Value proven by* (required);
  - *Archive*, a link to the item's heading in the frozen file (moved items only).

  These facts live in the body, not in project fields, so a check, a CI job or a stranger's agent can read them with
  no project scope and no token.
- **Labels say what the issue is.** Personal repositories have no issue types, so the labels are `epic`, `story`,
  `task`, `chore` and `bug`. Of these, only `bug` exists today.
- **Hierarchy is GitHub's sub-issues.**
  - An epic's stories are its sub-issues, and the epic shows their progress.
  - When a story is planned, each task of its plan becomes a sub-issue of the story, and its plan document stays in
    `docs/`.

## 5. Revalidation — only what still holds moves

P70's rule, and the PO's choice: a lens proposes and the PO confirms.

1. A W14 lens reads each of the 35 open items (34 for spark and the bin; P102 itself is kept). It proposes one of:
   - **keep**, as an epic, story, chore or bug, with its slice and its parent epic;
   - **close as done**, naming the commit that proves it;
   - **park**, with what pulls it back;
   - **merge into** another item.

   Every proposal carries one line of reason.
2. The PO confirms or changes the table in one pass.
3. The confirmed table is the migration's only input.

## 6. The migration — once, not shipped

A one-off script runs from the PR's scratch space and never enters `scripts/` or `tools/`. A shipped importer would be
dead code after one run (W16). It goes in this order:

1. Create the labels.
2. Commit the issue form.
3. Create the issues.
4. Link the sub-issues.
5. Create the projects and their fields.
6. Add the items to the projects.
7. Set Status and Slice. Waiting on and Waiting since are set where the revalidation table says so.

It is **idempotent**: an issue is found by its title's id before one is created, so a second run changes nothing. It
runs **as a dry run first**, printing every issue it would create. It runs for real **only with the PO's yes**,
because it publishes around 30 public issues. It works through `gh` with the PO's own login and stores nothing.

## 7. The archive

- **`PRODUCT_BACKLOG.md`** is frozen.
  - It opens with a banner: the date, *this is the archive*, and the projects' links.
  - Each moved heading ends `— MOVED to xmejkal/<repo>#N`. A closed item ends `— DONE` or `— CLOSED <date>: <reason>`,
    as the revalidation table says.
  - The test's closed pattern gains `MOVED`.
  - Nothing is added to the file after the freeze.
- **`STORY_MAP.md`** keeps the map as text: the backbone, the slices and which items sit in each, by issue number.
  This text is what P102b draws in Miro and Canva. Order and status leave it for the project. Its rows say what each
  slice does today (P97, 2026-10-08).

## 8. The checks

- **`tools/check_backlog.py`,** in the pre-push gate (`tools/check_commit.py` calls it). It reads both boards: spark's
  stages and limits, and the bin's cards in the same flight total. It fails the push when:
  - a card from Ready on (Ready, Build or Review) has an empty *Needed by* section or no Slice;
  - **a WIP limit is broken**: a stage holds more than its limit in §3, counted as §3 says, or more than four are in
    flight.

  This makes *finish before switching* a command, not a memory (the retros' own finding: what a command enforces
  holds).
  - With no network or no `gh`, it says could-not-run and passes. The gate must work offline.
  - Its test feeds it a recorded `gh` answer, so the suite stays offline.
- **`tests/test_orphans.py`:** its two backlog checks become one. The archive is frozen when no open heading lacks a
  `MOVED`, `DONE`, `CLOSED`, `PARKED`, `MERGED`, `DELETED` or `SPLIT` marker.
- **The bin:** it has only three items, so no check is built for its project yet (W14). One is added when an item
  first lacks *Needed by*. **Amended 2026-10-09 (P146):** the gate reads the bin's board too. Its cards in a working
  stage fly in the same total of four as spark's (a card labelled `bench` sits outside it), the expedite lane is one
  lane across both boards, and a card of the bin's that waits on someone is asked since when; its cards fill none of
  spark's stages and are asked for no *Needed by* or slice.

## 9. What changes in how we work

| rule | before | after |
| --- | --- | --- |
| **W19:** the item exists before the work | a Markdown entry | an issue on the project |
| **W8:** big items go through a PR | unchanged | the PR body says `Closes #N` |
| a plan's tasks | checkboxes in the plan only | also sub-issues of the story (the plan stays the source of each task's text) |
| **W11:** the PO orders | `STORY_MAP.md`'s order lines | the Ready column's row order |
| the unit of work and review | a sprint (`scrum/SPRINT.md`) | **an epic.** When an epic is done: its review, the outside audit, then the retro. `SPRINT.md` stays as the history |
| finish before switching (W6, W18) | prose, held by memory | the WIP limits, enforced by §8's check |
| the day | — | **the day-close**: at the end of each working day Claude writes one dated line — what moved, what was proven, what is aging, the next card. It is also the restart point after an interrupted or compacted session. Where it is written is P102c's design |
| the week | — | **the PO's weekly look** at the board: what is waiting more than 3 days, which epics started and finished |

`scrum/WORKING_AGREEMENTS.md` gets these lines in the same commit as the freeze (R7: a document changes with the thing
it describes). The sprint-planning wording in W18, and "the audit closes each sprint" (R3.3, R4.3), are rewritten to
the epic.

**Why Kanban (the council of 2026-10-05).** Three lenses argued the case: flow, one-day sprints, and the evidence from
the history.
- Sprints 3–9 each lasted hours to a day. Sprint 10 has stayed open since 10-03, after work came in that it never
  planned.
- The PO added items mid-sprint in 3 of the 6 sprints read closely, so the sprint commitment rarely held.
- Retro actions held when a command enforced them and broke when they relied on memory.
- The load-bearing ceremony was the outside audit at the close, which is why it moves to each epic's end.

All three lenses converged on a Kanban board with enforced limits and one daily line, rather than a daily plan and
retro.

**The trial — four weeks, checked on 2026-11-02.** The limits were raised on 2026-10-06, the trial's second day, then
raised to 2 per stage and 4 in flight the same evening (§11), and the date stays. Three tests at the weekly look:
- whether any limit was broken without being caught, counting work on a card the board showed in Idea;
- whether a weekly look was skipped twice;
- whether epics start and finish.

The check also compares how many days cards waited on the PO before the raises and after them.

If they fail, the team moves to one-day sprints: a short plan each morning and a close each evening, on the same
board.

**P146 (accepted 2026-10-06)** defined the stages' entry and exit, the counting rules, the expedite lane, the appetite
and the token allowance — [`docs/2026-10-06-process-design.md`](2026-10-06-process-design.md); the flow's table in
[`scrum/README.md`](../scrum/README.md#the-flow--an-items-stages) is where they now live. What its build of 2026-10-09
made a command: the gate (the limits and counting rules on both boards, the expedite lane, the undated wait, *Needed
by* and the slice from Ready on) and the status's lines. A spent-appetite flag was built too, and removed on the PO's
decision of 2026-10-09 ([Q5 on #80](https://github.com/xmejkal/spark/issues/80#issuecomment-6077488115)): the board's
Appetite field is process data he reads, and nothing in spark reads it. The three guards of decision 1 went to the
PO as [Q2–Q4 on #80](https://github.com/xmejkal/spark/issues/80#issuecomment-6071367154);
on [his answers of 2026-10-09](https://github.com/xmejkal/spark/issues/80#issuecomment-6081214370), two are set, branch protection and the
`ask` rule, and the launch hook is not: he answered *"Not yet"* (§11, decision 12). The token
allowance is a rule with no tool: nothing counts the day's tokens yet (card C1 of the design).

## 10. Not in this spec

- P102c, the session-start status and where the day-close is written;
- the epic-done audit as a command (with P102d, since it checks that each story's proof ran);
- P102b, maps in Miro and Canva;
- P102e, the discovery skill;
- P102d, proofs and the *Proven* field;
- P102f, `spark-demos`;
- any CI for spark (none exists).

## 11. Decisions (the PO, 2026-10-05)

1. The tools chore comes first, before P100.
2. P102 is split into a, then c, b, e and d, each designed on its own. f was added for the demos.
3. Open items move only after revalidation: the lens proposes and the PO confirms.
4. Item facts live in the issue body. Project fields hold only Status, Waiting on and Waiting since, Slice, and later
   Proven.
5. The projects are public.
6. **Kanban with a day-close, not sprints.** This replaces the one-week iterations decided earlier the same day. The
   PO: *"it might be better to go more in a Kanban style process instead of sprints, to concentrate on WIP and flow
   and to design the stages well to capture our flow"*. He then asked the council about one-day sprints and chose its
   recommendation:
   - the stages and limits of §3;
   - a total of 2 in flight;
   - the day-close;
   - an epic-done review, audit and retro;
   - his weekly look;
   - a four-week trial.
7. Each repository has its own project: spark, the bin, and one `spark-demos` for the demo projects.
8. Diagrams go in both Miro and Canva (P102b).
9. All four helpers are in: epics with sub-issues, the session-start status, diagrams as text first, and proofs run.

**Amended on 2026-10-06, the trial's second day (the PO, P146):**

10. **The limits are raised, and what counts is written down.** The PO decided it on the board proposal for P146.
    - Ready goes from 3 to 5, and in flight from 2 to 3: one worked in the session, one by agents in the background, one
      waiting. This replaces the total of 2 in flight in decision 6. Discovery, Design, Build and Review stay at 1.
    - Two counting rules (§3): an epic counts where it is the work itself, in Discovery and Design, and from Build on its
      stories carry the limit; a card is in its working stage while any work runs on it, a background read included.
    - Every card counts. A card that one PR closes together with another still counts on its own, so Build takes one
      card at a time.
    - The trial keeps 2026-11-02. Its first test widens to count work on a card the board showed in Idea, and it
      compares how many days cards waited on the PO before and after the raise (§9).

**Amended again on 2026-10-06, in the evening, after the first day at the cap of 3 (the PO, P146):**

11. **Every working stage takes 2, and at most 4 are in flight.** The PO: *"I think we should set more than one, dont
    you think? like 2?"*
    - Discovery, Design, Build and Review go from 1 to 2, and in flight from 3 to 4. Ready stays at 5. This replaces the
      limits of 1 and the total of 3 in decision 10.
    - The counting rules do not change (§3): an epic counts in Discovery and Design only, a task never counts, and
      every card counts. With every stage at 2, a pair of cards that one PR closes fills Build.
    - The trial keeps 2026-11-02, with the limits raised to 2 per stage and 4 in flight the same evening. Its tests are
      those of decision 10 (§9).

**Amended on 2026-10-09, in P146's build (the PO accepted its design on 2026-10-06, 12:21 UTC, answering its six
decisions (a) all three guards, (a), (a), (a), (a), (a); the decision numbers are those of
[the process design's §5](2026-10-06-process-design.md#5-decisions-for-the-po)). Beside each, what is built:**

12. **Process decision 1, 2026-10-06: three guards in the PO's settings** — a hook that refuses an agent launch unless
    its description names a card standing in a working stage (W19), branch protection on the `main` of both
    repositories (W8), and an `ask` rule for `wokwi-cli` and `make simulate` (W10). Before the PO's answers none was
    set (checked 2026-10-09). His answers of 2026-10-09 to Q2–Q4 ([on #80](https://github.com/xmejkal/spark/issues/80#issuecomment-6081214370)):
    - **Branch protection** — *Built: yes* (Q3, *"Ruleset + auto-delete (Recommended)"*): a ruleset, "main by PR
      only", on both repositories refuses a direct push to `main`, and GitHub deletes a merged pull request's
      branch (W8).
    - **The `ask` rule** — *Built: yes* (Q4, *"Yes, always ask (Recommended)"*): in his settings, for `wokwi-cli`,
      `make simulate` and `make simulate-all` (W10).
    - **The launch hook** — *Built: no* (Q2, *"Not yet"*): nothing refuses a launch, and W19 holds by practice.
13. **Process decision 2, 2026-10-06: the token allowance** — with no question asked, one run per card in flight, sized
    to its question, and at most one full council a day; anything bigger is asked first, with its estimate. *A rule,
    with no tool:* nothing counts tokens yet (card C1 of the design).
14. **Process decision 3, 2026-10-06: found work** — a run's findings land as one checklist on its card; at most 3
    become cards, filed in Idea with no slice. *A rule, with no tool.*
15. **Process decision 4, 2026-10-06: an expedite lane** — only on the PO's word, one at a time, labelled `expedite`; it
    may take a stage one over its limit, and the gate fails on two. *Built:* the gate.
16. **Process decision 5, 2026-10-06: an appetite per epic** — given in working days when an epic enters Discovery; the
    PO reads the field; the flag was built and removed on his decision of 2026-10-09
    ([Q5 on #80](https://github.com/xmejkal/spark/issues/80#issuecomment-6077488115)). *A board field, the Appetite number, with no tool.*
17. **Process decision 6, 2026-10-06: fewer yeses per card** — a story needs the PO's yes once, on its spec; its plan
    runs with no second yes unless it widens the scope or goes past the allowance, and a chore or bug needs no plan yes.
    *A rule, with no tool.*
