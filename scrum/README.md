# How this team works

**In short**

- [The stages](#the-flow--an-items-stages): Idea → Discovery → Design → Ready → Build → Review → Done. The PO's order
  into Ready is the commitment.
- The limits: 2 per working stage, Ready 5, at most 4 cards in flight across both boards.
- The PO orders Ready and merges; Claude proposes, builds and says "ready to merge".
- Where things stand: `python3 tools/board.py status`; the push gate by hand: `python3 tools/check_backlog.py`; the
  day-close, printed and not posted: `python3 tools/board.py close --dry-run "<line>"`.
- An agent's launch names its card, which stands in its working stage first
  ([W19](WORKING_AGREEMENTS.md#w19--the-item-exists-before-the-work-starts)):
  `Agent(description="#80 P146: the documentation lens", …)`.

Every rule the team runs on is a file in this folder, and all its work is a card on a board.

We run Kanban and keep from Scrum the Product Owner, the Definition of Done and the retrospective, and add *Value
proven by*. There are no sprints, no Scrum Master and no ceremonies.

Nothing lives only in an agent's head or in a conversation that scrolls away — if a rule, a goal or a decision is not
written here, it is not in force. The design behind this page:
[`docs/2026-10-06-process-design.md`](../docs/2026-10-06-process-design.md) (accepted by the PO on 2026-10-06). **(D)**
marks what he had decided earlier on 2026-10-06, before he accepted the design (12:21 UTC). **Decision N** (1 to 6) is
the numbered decision of the design's [§5](../docs/2026-10-06-process-design.md#5-decisions-for-the-po), each answered
by the PO on 2026-10-06; **card C1** to **C4** is a card its §4 proposes, filed only on his order.

Two repositories, one team, a board for each (the PO orders both):

- **`spark`** — the product. A Claude Code plugin for AI-assisted electronics design.
- **the bin** (`sisuo-brain-transplant`) — the test case. An ESP32 bin controller, and the only real evidence that
  spark works. Work on the bin is justified when it exercises or proves spark, and otherwise it competes with the
  product for the same hours.

## The people

Three roles: **the Product Owner** (Petr), **Claude** (developer and orchestrator) and **the agents** Claude launches;
the tech lead and the PO assistant (the PO, 2026-10-06) are roles a council's lenses play. What each decides, proposes,
does and may not is on their role cards in [`TEAM.md`](TEAM.md).

Petr is the Product Owner and that is not decorative. Proposals for ordering come to him ranked with reasons; the
ranking is a recommendation until he says otherwise. An agent never decides that something is valuable — it can only
report what something costs and what it would prove.

## The artifacts

| file | what it is for |
| --- | --- |
| **the spark project** (https://github.com/users/xmejkal/projects/2) | **the board, since 2026-10-05 (P102a).** Every item is an issue, with its *Needed by* and *Value proven by*; Kanban stages and limits ([the flow](#the-flow--an-items-stages), below); the Ready column's order is the PO's. The bin's own board: https://github.com/users/xmejkal/projects/1 |
| [`PRODUCT_BACKLOG.md`](PRODUCT_BACKLOG.md) | **the archive, frozen 2026-10-05.** Every heading says where its item went (MOVED to an issue) or how it ended |
| [`SPRINT.md`](SPRINT.md) | the history of Sprints 1–10 |
| [`RETROSPECTIVES.md`](RETROSPECTIVES.md) | every retro, the change it produced, and **whether that change stuck** |
| [`WORKING_AGREEMENTS.md`](WORKING_AGREEMENTS.md) | the rules, and where each one came from |
| [`TEAM.md`](TEAM.md) | the role cards, the roster and the test each member has to pass to exist |
| [`VISION.md`](VISION.md) | what spark is, who it is for, v1 and what it is not (confirmed by the PO on 2026-10-03, P69) |
| [`STORY_MAP.md`](STORY_MAP.md) | the journey a person takes, and the slices in order — each a milestone a command or a bench log proves; a card's *Slice* field names one (confirmed by the PO on 2026-10-03, P69) |

The work lives on the two boards and nowhere else, each card an issue in its repository. `docs/observations/INDEX.md`
is **raw observation intake**, not a queue of work: anything in it that should be built is an issue on a board or it is
not happening. That consolidation is deliberate: three parallel lists is how 37 observations and 20 findings reached
zero resolved between them.

## The cadences, and what each one leaves

A cadence that leaves nothing did not happen. Since 2026-10-05 the team works Kanban with a day-close (P102a; the PO's
choice after a three-lens council).

| when | what | what it leaves |
| --- | --- | --- |
| each session start | `tools/board.py status`, the existing hook | what is in flight and its age, the waits oldest first, Ready, the last close |
| when the PO stops | the day-close, `tools/board.py close` | one status update: what moved, what was proven, what is aging, the runs and their tokens, the next card |
| Ready is down to two | ordering Ready | Claude proposes in a batch, and the PO orders. When he names "next" in conversation, the card moves that turn, with his words quoted |
| an epic's last story is Done, or its appetite is spent (decision 5; the PO reads it on the board) | value check, outside audit, retro | the PO's verdict; the audit's report in `docs/observations/`; a retro of at most two changes, each with the command that checks it, plus a look at the limits |
| once a week | the weekly look | one status update: cards done; in flight and the oldest; waits and the oldest; Idea in and out. Plus a list of Idea cards to close, which the PO strikes or confirms |
| 2026-11-02 | the trial check (kept) | its first question now counts work on cards the board showed in Idea. It notes "limits raised 2026-10-06, the trial's second day" |

- **The session start** is P102c's hook, in the PO's own settings; it prints nothing outside his project folders. It
  also gives the gate's verdict and the open PRs, marks the `expedite` and `bench` cards in flight, lists every wait on
  both boards (one on someone other than the PO says who), marks a wait older than three days with `!`, and says
  *"Ready is down to N"* at one or two. It reads each board whole, page by page, and *"N open"* counts all of it; a
  board read in part, or a card in a stage the gate does not know, makes the whole status one could-not-run line
  naming it, and a card with no Status is said and stands in Idea (P168, P167).
- **The day-close** posts Claude's line, then what is in flight and every wait, as a status update on the spark board —
  at risk when the gate finds a problem (a broken limit, a missing *Needed by* or slice, an undated wait, a second
  expedite) or a wait is older than three days. A day has one close; a second for the same day is refused. A session
  that opens with *"! the day of … has no close"* writes that day's close first, with `--date`.
- **The weekly look** has no command: `tools/board.py` posts only the day-close, and reads every status update that
  carries a start date as a day's close. So the weekly look's update is posted by hand with no start date.
- **The service level**, one best guess (the design's measures, accepted with it on 2026-10-06): *"a card leaves Build
  and Review within 2 working days, 8 times in 10."* The status prints each card's days in its stage, but nothing flags
  one past the service level yet (card C3 of the design, not built); the trial on 2026-11-02 corrects the guess.
- **The appetite** (decision 5 (a)): when an epic enters Discovery, the PO gives it an appetite in working days, in
  the Appetite number field on spark's board. When it is spent: *"ship what is Done, bet again, or drop it"*. The field
  is process data the PO sets and reads on the board; nothing in spark reads it, and the status says nothing of it
  (the PO, 2026-10-09, [question 5 on #80](https://github.com/xmejkal/spark/issues/80#issuecomment-6077488115)).

## The flow — an item's stages

Every item is an issue on the board, and its card moves through the stages as the work does (the process design's §1;
`tools/check_backlog.py` checks the limits at every push). Idea, Discovery and Design decide **whether** to build; the
PO's order into Ready commits.

| stage | limit | enters when | leaves when | how |
| --- | --- | --- | --- | --- |
| **Idea** | — | the PO's words are recorded, or Claude files found work (decision 3); no slice is needed | the PO starts it, or it closes as not planned or as a duplicate | the issue form: *Needed by*, *Value proven by* |
| **Discovery** | 2, epics count | the PO says "discover it", or a read runs on the card (D) | its document merges by PR (D) and the PO decides: design, park or drop. A read that only answered a question posts the answer, and the card goes back to Idea (D) | with the PO, through his `product-discovery` skill (P102e): journeys, a story map, his answers in batches. Drawing them in Miro and Canva is P102b |
| **Design** | 2, epics count | a story the PO chose has no approved spec, before Ready or when it is pulled from Ready | the spec is in `docs/`, its council has run (full by default, light on request (D)), and the PO says yes | superpowers' brainstorming, then the spec in `docs/` |
| **Ready** | 5 | the PO orders it. **This is the commitment.** The card has a slice, a *Needed by* that names the design that is blocked (W14), and a *Value proven by*, which is a hypothesis until it is reproduced at Done — nothing closes on an unreproduced criterion (W20, merged into W9 and this row, 2026-10-09). Chores and bugs enter here directly | Claude pulls the top card when Build is free, or into Design if the story has no spec | the PO's row order is the order (W11); when Ready is full, the PO moves one back to Idea |
| **Build** | 2 | pulled from the top of Ready, or an expedite; a story's plan runs with no second yes unless it widens the scope or goes past the allowance, and a chore or bug needs no plan yes (decision 6, 2026-10-06) | the plan's tasks are done, test-first, and the final review starts | superpowers' writing-plans — a plan council only for a plan of several tasks (decision 6) — then executing-plans or subagent-driven-development; the plan's tasks become sub-issues |
| **Review** | 2 | a fresh final review on the most capable model | the council before the PR (the PO assistant, the user's journey, the tech lead, a documentation expert, then the refuter) has run and its fixes are in; the DoD green; the proof posted; **then the PO merges** on Claude's "ready to merge" | the PR says `Closes #N` |
| **Done** | — | the work is where it is used (merged, or installed when there is no PR), and *Value proven by* has run with its output on the issue | (end) | the proof is posted on the issue |

Ready takes five (D); each working stage two, and at most four cards in flight — Discovery to Review — at once: the
PO's call of 2026-10-06 evening, after the first day at the cap of three (*"2 everywhere, cap 4"*). What counts (P146,
the PO, 2026-10-06):

- an epic counts only in Discovery and Design, where it is the work itself; in Ready and after, its stories carry the
  limit;
- a card is in its working stage while any work runs on it, a background read included; a read that only answers a
  question puts its card back in Idea when the answer is posted;
- every card counts: a card that one PR closes together with another still counts on its own, so a pair that one PR
  closes fills Build;
- a task with no parent story counts as a card, and so does one whose story is closed (`tools/check_backlog.py`).

The gate asks a card for its *Needed by* and slice from Ready on — Ready, Build and Review — never in Idea, Discovery
or Design.

**A plan's tasks are sub-issues of their story** (labelled `task`): they show the story's progress on the board and
ride on it while the story is open — no slice, *Needed by* or place in a limit of their own. A task with no open parent
story is a card like any other.

**The expedite lane** (decision 4 (a), the PO's choice of 2026-10-06): *"only on [the PO's] word ("now"), one at a
time, labelled `expedite`. It may take a stage one over its limit, and the gate fails on two."* Claude proposes it for
a check that lies or a gate that breaks. The gate lets the expedite's working stage, and the four in flight, hold one
over; Ready never, because the expedite enters Build. It is one lane across both boards.

**The bin.** The bin's cards in flight count in the same four; a bench session is the PO's hands and sits outside them:
a bin card labelled `bench` is left out of the total. The bin's cards fill none of spark's stages and are asked for no
*Needed by* or slice. With no `gh` or network the gate prints could-not-run and lets the push through, the exception
the design writes into W1; a bin board or parent stories it could not read are said with their cause, and do not stop
the push.

The trial is checked on 2026-11-02 (the limits were raised on 2026-10-06, the trial's second day, then raised to 2 per
stage and 4 in flight the same evening; the check compares how many days cards waited on the PO before and after):
was any limit broken without being caught, counting work on a card the board showed in Idea, was a weekly look
skipped twice, do epics start and finish? If not, one-day sprints replace it (the backlog design's §9,
`docs/2026-10-05-backlog-in-github-design.md`).

## Runs: reads, councils, reviews

- **Claude starts these on its own:** whatever a stage names for the card in it. That is the spec council in Design,
  the plan's agents in Build, and the final review in Review.
- **These start on the PO's yes:** a read that answers his question, or one that opens discovery.
  - Claude first answers in a few lines from what is already known.
  - Then it offers the read: *"a read of N agents, about M tokens, on #X, which moves to Discovery. Now, or after
    the card in flight?"*
  - If the stage is full, the PO picks which card waits.
- **How a run shows on the board:**
  - one run per card at a time, and the card stands in the run's stage;
  - runs use Agent-tool agents, which the PO's VS Code panel shows, and a workflow only when he asks (D);
  - when a run ends, it gets one comment on its card: what it found and refuted, its size and cost, and where the
    report is.
- **Found work** goes into that comment as one checklist. At most 3 items become cards — those that block the card's
  proof or break W1 — filed in Idea with no slice; the rest are filed when a design pulls them (decision 3 (a)).
- **The council before every pull request, bigger or smaller:** the PO assistant, the user's journey and the tech
  lead, **plus a documentation expert**, then the refuter; its findings are fixed before the merge, not only reported.
  First run: P158's council on PR #98, 2026-10-08. The PO's words of 2026-10-08, as #80 records them (typos
  corrected) — [the rule](https://github.com/xmejkal/spark/issues/80#issuecomment-6058289117) and
  [the addition](https://github.com/xmejkal/spark/issues/80#issuecomment-6058297081):

  > make sure to always add a documentation expert into this council that I want you to run before any bigger PR, or
  > even smaller and make sure its well tested too, as well as documented both technically correct but also well
  > readable, teaser on the front page, maybe usage and code and agent calling examples and a link to a separate
  > detailed page and that all the current documentation is also still up to date and fix gaps, missing parts, changed
  > things, wrong information, unclear texts, hallucinations most of all. Then lets plan the fixes and implement them
  > before merging

  > the documentation expert also makes sure and updates if wrong or missing help for both agents and humans and that
  > there are no hallucinations and is always up to date

## The token budget

- **Sized to the question.** A look-up gets one agent; a comparison, a few. A full council (about 90 M input tokens)
  runs only where a council belongs, and councils are full by default (D).
- **Cheapest model that does the job.** Lenses run on Sonnet. Refuters, the synthesis and the final review run on
  the most capable model.
- **Inside the PO's allowance** a run starts. Above it, Claude asks first, with the estimate. The allowance is decision
  2 (a), his choice of 2026-10-06: *"with no question asked, one run per card in flight, sized to its question, and at
  most one full council a day. Anything bigger is asked first, with its estimate."*
- **Reported daily.** The day-close states the day's agent tokens (no tool counts them yet; card C1).
- **Capped by the limits.** One run per in-flight card means at most four at once, five while the expedite lane is in
  use.

## Asks to the PO

- **One batch is open at a time,** at most six questions (D). Each question carries Claude's recommendation.
- **Nothing is decided until the PO answers.** An option's text names every move it makes, and his answer covers only
  what it showed.
- **A card that waits on the PO** carries *Waiting on* and *Waiting since*. The gate names a *Waiting on* with no
  *Waiting since*, on both boards, in any open stage, a riding task included.
- **The decision window.** The session start lists those cards oldest first. It is not a meeting.

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

Every one of these, for every item. No exceptions, no "mostly".

1. `python3 -m unittest discover -s tests` — green.
2. **Mutation tested.** Re-introduce the defect the change prevents; the suite must go red. A fix
   with no failing-first test is not a fix.
3. `python3 scripts/check_spine.py` — exit 0 when `scripts/` changed. With no file named it runs the reference design
   that ships with spark: the chain still runs end to end.
4. The item's own *Value proven by* command runs and shows what it claims, and its output is posted on the issue — or,
   for work with no PR (a setting, a board field), the output of the command that shows it, posted on the issue.
5. Committed, with a message saying what was wrong and why the fix is right.
6. Any claim it makes in a docstring or README is **true when run**, not when written.
7. Its closing comment quotes the gate's size line (`scripts/: N code lines (+M since origin/main)`) and says why
   (W15).
8. A change to what a step of the journey does updates [the journey guide](../docs/guide/journey.md) and the README's
   *What works today* in the same change (P104, the PO 2026-10-05). Nothing mechanical checks it: `tools/check_docs.py`
   cannot tell whether a status is still current, so the council reads it.
9. Before the PR: the council with a documentation expert, and its fixes (the PO, 2026-10-08).
10. **A version bump is a release.** The PR that changes the version in `.claude-plugin/plugin.json` (and README's
   footer, which `tools/check_docs.py` ties to it) is tagged `vX.Y.Z` on its merge and gets a GitHub release whose
   notes say what new functionality and which bug fixes came in; the PR's body names the release. Major when a
   journey or a command changes shape, minor for new functionality, patch for fixes. `gh release list -R xmejkal/spark`
   and `git log vX.Y.Z..main --first-parent` answer "what has been added since the last release". The PO, 2026-10-09
   (P169): *"lets'use git tags and releases, and we can always fill in the version /release content, what new
   functionality and bug fixes etc have been added"*.

**When an epic is done** (P98; P102a moved it from the sprint's close): `python3 tools/mutate.py tests/mutations/*.json` — every table in one sweep, which
prints its time. An escape is a missing test, opened as a backlog item the same day.

A stage that could not be exercised is `could-not-run`, never `ok`. That rule outranks every other
sentence in this folder.
