# P146: how we work, a proposal

*The process design of P146 (spark #80). Written as a proposal for the PO on 2026-10-06 from the four research reads
(R1 to R4), the three practice lenses and the board proposal of that day (kept outside the repository); **accepted by the
PO on 2026-10-06, 12:21**, every line as written, with the six decisions of §5 answered **(a) all three guards, (a),
(a), (a), (a), (a)** — his words are quoted on #80. **(D)** marks what he had decided on 2026-10-06 morning. Later
decisions are marked where they stand, with their date: the limits of two per working stage, Ready 5 and four in flight
(2026-10-06 evening); the two roles, a tech lead and a PO assistant (2026-10-06, 17:16); the Review-stage rule — a
council with a documentation expert before any PR, its fixes before the merge (2026-10-08); and that the merge is the
PO's, not Claude's (observed 2026-10-07 and 2026-10-08: the classifier refuses `gh pr merge` by Claude).*

*Noted 2026-10-09: the clock times on this page are GitHub's, in UTC — the acceptance at 12:21 UTC was 14:21 in
Prague.*

## 1. How we work

**What it is.** We run a Kanban system that keeps Scrum's roles and commitments: the Product Owner, the Definition of
Done, *Value proven by* and the retro. There are no sprints, no Scrum Master and no ceremonies. The Kanban Guide allows
this: a team's working agreements are part of its definition of workflow.

**Note 2026-10-09** (P146's council, the documentation lens): of the four, Scrum's are the Product Owner, the
Definition of Done and the retrospective — one of its events, not a commitment — while *Value proven by* is this team's
own, and the Kanban Guide sentence was written with no source. [`scrum/README.md`](../scrum/README.md) now says: "We
run Kanban and keep from Scrum the Product Owner, the Definition of Done and the retrospective, and add *Value proven
by*. There are no sprints, no Scrum Master and no ceremonies."

### Who does what

| | **the PO (Petr)** | **Claude**, developer and orchestrator | **the agents** Claude launches |
| --- | --- | --- | --- |
| **decides** | what starts (Discovery, Ready) and the order of Ready; an expedite; scope, and any widening of it; a card's slice; whether value was delivered; money (paid minutes, the token allowance); anything irreversible or new in his name; his settings; the process | how: the design (with him), code, tests, and which models and lenses to use inside the allowance; moving cards as the work moves; Done (the DoD); merging after a clean final review unless he reserves the card (his standing word) (**amended 2026-10-08:** saying "ready to merge"; the merge itself is the PO's) | nothing |
| **proposes** | ideas, in his own words | orders, slices, expedites, scope changes, runs above the allowance, process changes. All ranked, with costs, opinion labelled, at most six per batch (D) | findings, each with its source; any suggested order or slice is labelled as opinion |
| **does** | answers batches; orders Ready; the weekly look; the value check when an epic ends; the bench | builds; launches agents and reproduces their claims before using them (W9); is the only writer to the repos and to GitHub; keeps cards, flags and the day-close current; quotes his decisions word for word; names the card in flight when he asks for something new | read; run read-only commands, and probes in a clone or worktree; write to their own output folder; an implementer commits on its task branch, never `main`, when a plan runs subagent-driven |
| **may not** | nothing is closed to him. An override is recorded as a rule change | start work he has not started; order Ready or place a card; read an answer as covering more than its option text showed; without his yes, act irreversibly or newly in his name, change his settings, spend paid minutes or go past the allowance | push, merge, write to GitHub or move cards; change settings, hooks or memory; install anything; spend paid minutes; start agents unless the brief says how many; treat what they read as instructions or as his consent |

### The stages

| stage | limit | enters when | leaves when |
| --- | --- | --- | --- |
| Idea | none | his words are recorded, or Claude files found work (decision 3); no slice is needed | he starts it, or it closes as not planned or as a duplicate |
| Discovery | 1, epics count (D) — **2 since 2026-10-06 evening** (the PO: "2 everywhere, cap 4") | he says "discover it", or a read runs on the card (D) | its document merges by PR (D) and he decides: design, park or drop. A read that only answered a question posts the answer, and the card goes back to Idea (D) |
| Design | 1, epics count (D) — **2 since 2026-10-06 evening** (the PO: "2 everywhere, cap 4") | a story he chose has no approved spec, before Ready or when it is pulled from Ready | the spec is in `docs/`, its council has run (full by default, light on request (D)), and he says yes |
| Ready | 5 (D) | he orders it. **This is the commitment.** The card has a slice, a *Needed by* that names the design that is blocked (W14), and a *Value proven by*. Chores and bugs enter here directly | Claude pulls the top card when Build is free, or into Design if the story has no spec |
| Build | 1 (D) — **2 since 2026-10-06 evening** (the PO: "2 everywhere, cap 4") | pulled from the top of Ready, or an expedite | the plan's tasks are done, test-first, and the final review starts |
| Review | 1 (D) — **2 since 2026-10-06 evening** (the PO: "2 everywhere, cap 4") | a fresh final review on the most capable model | one fix pass, the DoD green and the proof posted; then Claude merges — **amended 2026-10-08: then the PO merges; Claude posts "ready to merge" and stops** (the classifier refuses Claude's merge, 2026-10-07 and 2026-10-08) |
| Done | none | the work is where it is used (merged, or installed when there is no PR), and *Value proven by* has run with its output on the issue | (end) |

- At most 3 cards are in flight, Discovery to Review (D) — **4 since 2026-10-06 evening**.
- A card stays in its working stage while any work runs on it (D).
- Every card counts (D). Only a plan's own sub-issues still ride on their story.
- The bin's desk cards count in the same three. A bench session is your hands, so it sits outside them. **The same
  four since 2026-10-06 evening** (noted 2026-10-09: the cap of four in flight above).

### Discovery comes before commitment

- Idea, Discovery and Design decide **whether** to build. Your order into Ready commits.
- The discovery skill (P102e, in Build now) runs Discovery: journeys, a story map, your answers in batches. Its
  document lands by PR (D).
- "Don't build it" is a good result: the card closes as not planned.
- A finding outside a card's core is a nice-to-have by default, triaged by severity.

### Runs: reads, councils, reviews

- **Claude starts these on its own:** whatever a stage names for the card in it. That is the spec council in Design,
  the plan's agents in Build, and the final review in Review.
- **These start on your yes:** a read that answers your question, or one that opens discovery.
  - Claude first answers in a few lines from what is already known.
  - Then it offers the read: *"a read of N agents, about M tokens, on #X, which moves to Discovery. Now, or after
    the card in flight?"*
  - If the stage is full, you pick which card waits.
- **How a run shows on the board:**
  - one run per card at a time, and the card stands in the run's stage;
  - runs use Agent-tool agents, which your VS Code panel shows, and a workflow only when you ask (D);
  - when a run ends, it gets one comment on its card: what it found and refuted, its size and cost, and where the
    report is.
- **Found work** goes into that comment as one checklist. At most N items become cards (decision 3), filed in Idea
  with no slice.

- **Added 2026-10-08 (the PO, on P97's PR):** before ANY pull request, bigger or smaller, a council runs on the open
  PR — the PO assistant, the user's journey and the tech lead, **plus a documentation expert**, then the refuter. The
  documentation lens checks that the pages are technically correct and readable, that the front page has a teaser with
  usage, code and agent-calling examples and a link to the detailed page, that every current page is still up to date,
  and that the help for agents and for humans (`--help`, `--describe`, the command pages, the guides) is right and
  complete — gaps, missing parts, changed things, wrong information, unclear text, **hallucinations above all**. Its
  findings are fixed before the merge, not only reported. First run: P158's council on PR #98, 2026-10-08.

  **Note 2026-10-09** (P146's council): the paragraph above paraphrases the PO; it drops "make sure its well tested
  too" and hardens his "maybe". His words, as #80 records them (typos corrected) —
  [the rule](https://github.com/xmejkal/spark/issues/80#issuecomment-6058289117) and
  [the addition](https://github.com/xmejkal/spark/issues/80#issuecomment-6058297081):

  > make sure to always add a documentation expert into this council that I want you to run before any bigger PR, or
  > even smaller and make sure its well tested too, as well as documented both technically correct but also well
  > readable, teaser on the front page, maybe usage and code and agent calling examples and a link to a separate
  > detailed page and that all the current documentation is also still up to date and fix gaps, missing parts, changed
  > things, wrong information, unclear texts, hallucinations most of all. Then lets plan the fixes and implement them
  > before merging

  > the documentation expert also makes sure and updates if wrong or missing help for both agents and humans and that
  > there are no hallucinations and is always up to date

### The token budget

- **Sized to the question.** A look-up gets one agent; a comparison, a few. A full council (about 90 M input tokens)
  runs only where a council belongs, and councils are full by default (D).
- **Cheapest model that does the job.** Lenses run on Sonnet. Refuters, the synthesis and the final review run on
  the most capable model.
- **Inside your allowance** (decision 2) a run starts. Above it, Claude asks first, with the estimate.
- **Reported daily.** The day-close states the day's agent tokens.
- **Capped by the limits.** One run per in-flight card means at most three at once. **Four since 2026-10-06
  evening**, five while the expedite lane is in use (noted 2026-10-09).

### Asks to you

- **One batch is open at a time,** at most six questions (D). Each question carries Claude's recommendation.
- **Nothing is decided until you answer.** An option's text names every move it makes, and your answer covers only
  what it showed.
- **A card that waits on you** carries *Waiting on* and *Waiting since*.
- **The decision window.** The session start lists those cards oldest first, before anything else. It is not a
  meeting.

### Cadences

| when | what | what it leaves |
| --- | --- | --- |
| each session start | the existing hook | what is in flight and its age, the waits oldest first, Ready, the last close |
| when you stop | the day-close | one status update: what moved, what was proven, what is aging, the runs and their tokens, the next card. A later close the same day amends it |
| Ready is down to two | ordering Ready | Claude proposes in a batch, and you order. When you name "next" in conversation, the card moves that turn, with your words quoted |
| an epic's last story is Done, or its appetite is spent (decision 5; *2026-10-09: the PO reads the Appetite field on the board — see the note at decision 5*) | value check, outside audit, retro | your verdict; the audit's report in `docs/observations/`; a retro of at most two changes, each with the command that checks it, plus a look at the limits |
| once a week | the weekly look | one status update: cards done; in flight and the oldest; waits and the oldest; Idea in and out. Plus a list of Idea cards to close, which you strike or confirm |
| 2026-11-02 | the trial check (kept) | its first question now counts work on cards the board showed in Idea. It notes "limits raised 2026-10-06, the trial's second day" |

### Measures worth watching

- **Throughput:** cards done since the last close.
- **Age**, measured against one best-guess service level, flagged with "!": *a card leaves Build and Review within 2
  working days, 8 times in 10.*
- **The oldest wait** on you.
- **Idea in and out**, each week.
- **Agent tokens**, each day.

Nothing else. Five Done cards support no chart and no forecast.

## 2. What changes, and why

| # | change | today, as written | theory | evidence |
| --- | --- | --- | --- | --- |
| 1 | Three role cards, each with decides / proposes / does / may not | a three-row table with "Facilitator / dev"; nine role rules live only in memory | Scrum Guide: the PO stays accountable when he delegates, and *how* is the Developers'. Expansion Pack: the PO must be human, a Developer may be automated, and one person may hold more than one role. So you hold the process, and no Scrum Master role is needed | the written roles contradict each other seven times (roles §3.2); 4 of 8 merges came with no prompt, a rule written three ways; agents committed 7 times under "members do not commit" |
| 2 | Count the work, not the cards (D) | epics are exempt; at most 2 in flight | Kanban Guide: WIP is everything between started and finished. Exceptions must be explicit, and ours was, so the case rests on the evidence | at 10:45 on 10-06 the gate counted 1 card while 4 cards had work running (R1 §1.3) |
| 3 | Name the start point and the commitment point | neither is defined | Kanban Guide: a workflow's definition needs both. Kanban University: before the commitment point, work items are options | P102e went from Idea to Build, past Ready; Ready was used as "chosen next", and two cards went back to Design |
| 4 | A read starts on your yes and runs on its card | W19: the card exists before the work | Theory of Constraints: your decisions are the drum, and work is released at its pace (the rope) | 12 workflow launches on 10-06, 4 of them restarted when the question moved; P102e waited behind them; 17 of your 57 messages in two days asked what the agents were doing |
| 5 | A token budget (W10 widened) | W10 covers simulation minutes only | Anthropic: multi-agent work uses about 15× a chat's tokens, and effort should scale with the question | agents took 86 % of 10-06's spend, and 0.4 % of agent messages ran on Sonnet; one cost figure changed your council answer; `research_cost.py` under-counts output (305 against 13,322) |
| 6 | Asks: one batch open at a time, dated, oldest first; an answer covers only what its option showed | W18's "a concrete question" | Reinertsen: a fixed cadence puts a bound on waiting. OpenAI §4.2: many quick approvals become a rubber stamp. Benson's Pen: waits carry dates and a limit (the six is our own number) | R2.6's wait has no date, so it never ages; B1 waited 10 days; you took the recommended option in 61 of 83 prompts; the bin's Ready order came from an answer about buying parts |
| 7 | Found work is capped, filed without a slice, and discarded weekly | Idea holds "your words, nothing more", yet the gate wants a slice even in Idea | Kanban University: options are constrained against capacity, and many are discarded. GitHub's agent workflows file one issue per run by default | 50 new cards in two days, at least 36 from agents, against 5 Done; an agent chose P136's slice "so the push gate passes" |
| 8 | An expedite lane (decision 4) | none | Kanban's expedite class of service | P105 went from filed to merged in 39 minutes, outside any rule |
| 9 | Fewer yeses per card (decision 6) | a yes on the spec, on the plan and on its execution | Theory of Constraints: spend the constraint only where it alone can decide. Scrum Guide: *how* is the Developers' | 5 or 6 of your touches per story; a plan council ran once in two days |
| 10 | An appetite per epic (decision 5) | the trial asks "do epics finish?", but nothing makes them finish | Shape Up: a fixed appetite and a circuit breaker. In Scrum, the Sprint used to cap this | P102 has 3 of 8 sub-issues done; no epic has closed under Kanban |
| 11 | Every cadence leaves a record; one best-guess service level | the weekly look writes nothing; one close a day | Kanban Guide: its minimum includes a service level, and "a best guess will do". Anderson: at small scale, combine the cadences | the evening of 10-05 is in no close; the trial counts skipped weekly looks that nothing records |
| 12 | Rules move from memory into `scrum/`, and three become settings (decision 1) | the README says a rule not written there is not in force | Claude Code: written instructions only advise, while hooks guarantee | the classifier, not the rule, refused three irreversible acts after the memory rule was written; reads ran on Idea cards despite W19 |
| 13 | Outside eyes at stage points, instead of observers at all times | memory: observers run "at all times" | the token budget (row 5) | no standing observer ran on 10-05 or 10-06. The epic-end audit is a habit, it held, and the team calls it load-bearing |
| 14 | The words | "ceremonies", "facilitator", "scrum master", "sprint log", "Done line", "PBI", "iteration" | Scrum Guide: partial Scrum "is not Scrum" | your words: *"we're not doing scrum, but rather Kanban"* |

**Not adopted, as bloat for this team:**

- the SRM and SDM role names, seven meetings, a STATIK workshop, the maturity model and Flight Levels;
- four classes of service, WSJF, flow charts and forecasts;
- a Definition of Ready document, a discovery board and a blocker log;
- Build 2 — **adopted 2026-10-06 evening** (the PO: "2 everywhere, cap 4"; noted 2026-10-09);
- agent teams, issue-driven cloud agents, a card per run, and a Scrum Master agent;
- planted false findings to test the refuters. They marked 50 of 254 findings "partly", so they do push back.

## 3. The working agreements, W1 to W21

This is P72's cut, which you chose on 10-03: an agreement either fails a command, or it moves to one unnumbered page of
habits. P72 is closed, and P146 carries the cut out. The numbers stay as they are, because 44 files cite them. A merged
or moved rule leaves a dated one-line pointer.

| W | rule | verdict | the one line |
| --- | --- | --- | --- |
| W1 | could not look ≠ passed | keep, rewrite | binds our gates and agents' reports too; the offline gate is written down as an exception (could-not-run, push allowed); fix the stale `answer()` pointer |
| W2 | a test runs the thing | keep | its check widens to `tools/` (card C4) |
| W3 | mutation testing is the bar | rewrite, absorbs W12 | drop "no tooling, no hook" (false since `mutate.py` and the pre-push anchors) and "scrum master" |
| W4 | never change a test to pass | habit | in your words, carried in every implementer and reviewer brief; no command can judge it |
| W5 | state the scope | move to the product | `DECISIONS.md` and the agent files already hold it |
| W6 | finish before starting | rewrite, mechanical | the decided limits and counting rules, the expedite lane and both boards, in `check_backlog.py` |
| W7 | don't reinvent | merge into W14 | "build only what is pulled, and reuse first" |
| W8 | commit often; big items by PR | rewrite, mechanical | "every change reaches `main` by a PR that closes its card", as practised since 10-05; branch protection (decision 1) |
| W9 | an observer's claim is a hypothesis | habit, absorbs W20 | "every claim is a hypothesis until reproduced"; refuted claims stay in the run's comment |
| W10 | simulation minutes are a budget | move to the PO's role card, widened | paid minutes and the token allowance are yours; drop the undated "~21 of 50"; an `ask` rule (decision 1) |
| W11 | only the PO orders | move to the role cards | adds the slice, and "an answer covers only what its option showed" |
| W12 | a blind fixture is the defect | merge into W3 | |
| W13 | numbers only after their output | keep, absorbs W17 and W20's estimate clause | the pushed-ref half lands with P106 |
| W14 | pull, never push | rewrite as Ready's entry policy, absorbs W7 | *Needed by* and the slice are checked from Ready on, not in Idea |
| W15 | an orphan fails the suite | keep, absorbs W15b | drop the retired budget clause; cover `tools/` (C4) |
| W15b | the size is said at each push | merge into W15 | the closing comment quotes the size line, replacing "the Done line"; count `tools/` |
| W16 | a replacement deletes the old | keep, mechanical for docs | a retired-words check over `scrum/`, `GLOSSARY.md` and `DECISIONS.md` (C4) |
| W17 | a summary claims no more | merge into W13 | |
| W18 | refinement is the team's | rewrite into the Design and Ready rows | drop "scrum master"; "one sitting" becomes the service level |
| W19 | the card exists before the work | keep, rewrite | the card stands in its working stage before any agent starts; the launch hook (decision 1) |
| W20 | an acceptance line is a hypothesis | merge into W9 and Ready's row | its estimate clause goes to W13 |
| W21 | keep a datum only if a decision rests on it | move to the product | the agent and command files and `DECISIONS.md`; its twin, Claude's research budget, joins W10 |

**What is left:**

- **10 numbered agreements:** W1, W2, W3, W6, W8, W13, W14, W15, W16 and W19.
- **2 rules on the role cards:** W10 and W11.
- **2 habits:** W4 and W9.
- **2 product rules:** W5 and W21.

**How a rule changes from now on:** by a PR whose card quotes your yes, with a dated line on the rule. This replaces
"retired in `RETROSPECTIVES.md`", which was skipped twice this week.

## 4. The document changes

**In P146's Build, one PR.** This page becomes P146's spec, `docs/2026-10-06-process-design.md`.

- **`scrum/README.md`:**
  - the top paragraph (a Kanban system with Scrum's roles);
  - "The people" becomes a link to TEAM;
  - the ceremonies become the cadences table (§1);
  - the flow table gains its entry and exit columns;
  - lines 72–82: the limits, the counting rules, the expedite lane, the bin and the trial note;
  - three short new sections: runs, the token budget, asks;
  - DoD clauses 3, 4 and 7, and Done for work that has no PR.
- **`scrum/TEAM.md`:** the three role cards replace "cross-functional", the roster paragraph and "How work reaches a
  member". The four-way test for agents stays, and now applies to every lens.
- **`scrum/WORKING_AGREEMENTS.md`:** §3, a Habits section at the end, and the line on how a rule changes.
- **`docs/2026-10-05-backlog-in-github-design.md`:** §3 (lines 48–56, and line 53 on who merges), §8 (lines 138–139),
  §9 (lines 178–184), and a dated entry in §11.
- **`GLOSSARY.md`:** lines 149–154, 220 and 232–237.
- **`docs/guide/developing.md:61`:** links to the README's table.
- **`DECISIONS.md`:** takes in W5 and W21; its restated Ws become pointers; the stale lines 53–56 and 69 go.
- **`.github/ISSUE_TEMPLATE/item.yml:22`:** the Proof field goes. It is empty on all 65 open cards, because proofs
  live in comments.
- **P146's own proof line is rewritten.** The docs and orphan tests it names do not read `scrum/`.
- **The bin:** `CLAUDE.md:183-194` and `STATUS.md:36-60` stop copying the cards and B1's wait, and point at the board.
- **Memory:**
  - each note that states a rule becomes a pointer to `scrum/`;
  - `background-observers` becomes "outside eyes at stage points";
  - `scrum-process` and `spark-scrum-state` take the new limits;
  - the diary shrinks to pointers, because the board and the closes now hold the state.

**The folder name: keep `scrum/`.** Its first line says what it is. Renaming it to `process/` would cost this:

- **24 tracked files:** 9 dated docs, 3 guides, 3 observation reports, the README, GLOSSARY, the issue form, 3 files
  inside the folder, and 3 test files;
- **of those, tests and mutation anchors:** `tests/test_orphans.py` builds the path at lines 108 and 149, the fixture
  `tests/data/p102a-items.json` quotes it, and `tests/mutations/sprint-9-p69.json` anchors two mutations on
  `scrum/PRODUCT_BACKLOG.md`;
- **elsewhere:** the bin's `CLAUDE.md:172` and `HANDOVER.md` lines 13 and 278, and 4 memory notes;
- **dead paths** in 30 issue bodies (24 on spark, 6 on the bin).

**What the scripts must enforce, in P146:**

- **`tools/check_backlog.py`:**
  - the decided limits and counting rules (the board proposal's prototype, about 8 lines);
  - a `task` with no parent story counts as a card;
  - *Needed by* and a slice are required from Ready on, not in Idea;
  - a *Waiting on* with no *Waiting since* fails;
  - at most one `expedite` (decision 4);
  - the bin's cards in flight count in the same total;
  - offline, it prints could-not-run.
- **`tools/board.py`:** `in_flight()` uses the same rules; the status prints every wait, oldest first, and says
  "Ready low" at two.
- **Tests and a mutation table** for each change (W2, W3). P102a's "an epic counts" row is deleted, not re-anchored
  (W16).

**Cards to file, each only on your order.** None is part of P146, so P146 stays one sitting.

- **C1, a bug.** `research_cost.py` under-counts output tokens. The fix takes the last count per message id and brings
  R4's per-day agent-token measure into `tools/`. The budget rests on this number.
- **C2.** The agent-launch hook (decision 1).
- **C3.** Measures in the status and the close:
  - throughput;
  - the service-level "!";
  - a same-day close that amends;
  - "no weekly look in 7 days";
  - each epic's progress (done of total) and its appetite (decision 5). *Noted 2026-10-09: the status will not show
    the appetite — the note at decision 5.*
- **C4.** Wider checks:
  - `tools/` in the orphan, self-confirmation and size checks;
  - the retired-words check;
  - `check_docs` reads `scrum/README.md` and `TEAM.md`;
  - `check_spine` runs at push when `scripts/` changes (DoD 3).

## 5. Decisions for the PO

**One yes to this page also accepts the following.** Strike any line you do not want.

- the role cards, the stage policies and the cadences;
- reads start on your yes;
- lenses run on Sonnet, which changes the councils you set to full;
- one batch of asks open at a time;
- the best-guess service level;
- keeping the name `scrum/`;
- the W1–W21 cut;
- outside eyes at stage points, instead of your "observers at all times";
- cards C1 to C4 are proposed, and none is filed until you say so.

**Six new decisions:**

1. **Three guards in your settings.** These rules broke while they lived only in memory, and each guard is a setting of
   yours.
   - **(a) Recommended: all three.**
     - A hook that refuses an agent launch unless its description names a card standing in a working stage (W19).
     - Branch protection on the `main` of both repositories, enforced for admins (W8).
     - An `ask` rule for `wokwi-cli` and `make simulate` (W10).
   - (b) The hook only.
   - (c) None of them: they stay habits, which the weekly look counts.

   *Why:* reads ran on Idea cards, and only the classifier stopped a direct commit. The `ask` rule is preventive: no
   overspend has been seen.
2. **The token allowance.**
   - **(a) Recommended:** with no question asked, one run per card in flight, sized to its question, and at most one
     full council a day. Anything bigger is asked first, with its estimate.
   - (b) Claude asks before any run of more than one agent.
   - (c) A daily token ceiling that you name. This needs C1.

   *Why:* agents took 86 % of one day's spend, and you hit your usage limit.
3. **Found work.**
   - **(a) Recommended:** a run's findings land as one checklist on its card. At most 3 become cards, namely those that
     block the card's proof or break W1, filed in Idea with no slice. The rest are filed when a design pulls them.
   - (b) 1 card per run, which is GitHub's default for its agents.
   - (c) As today: every confirmed finding becomes a card (your decision 13 on P104).

   *Why:* 50 cards arrived in two days, against 5 Done.
4. **An expedite lane.**
   - **(a) Recommended:** only on your word ("now"), one at a time, labelled `expedite`. It may take a stage one over
     its limit, and the gate fails on two. Claude proposes it for a check that lies or a gate that breaks.
   - (b) No expedite: "now" puts the card at the top of Ready, and it waits for a free slot.
5. **An appetite per epic.**
   - **(a) Recommended:** when an epic enters Discovery, you give it an appetite in working days. The status flags it
     when the appetite is spent, and you then ship what is Done, bet again, or drop it.
   - (b) No appetite. "Do epics finish?" stays a question for the trial.

   *Noted 2026-10-09: the PO decided the flag is process data, not spark's
   ([Q5 on #80](https://github.com/xmejkal/spark/issues/80#issuecomment-6077488115)): the Appetite field exists on the board,
   and the status does not read it.*
6. **Your yeses per card.**
   - **(a) Recommended:** a story needs your yes once, on its spec. Its plan runs with no second yes, unless the plan
     widens the scope or goes past the allowance. Chores and bugs need no plan yes. A plan council runs only for a plan
     of several tasks. Value stays yours, at the epic's check, and you may reserve any card.
   - (b) As written: a yes on the spec, on the plan and on its execution, for every card.

   *Why:* each story took 5 or 6 of your touches, and you took the recommendation three times in four.

## Skeptic pass

On rereading, I changed these things:

1. **Each run gets one comment, not two.** The start comment is cut: the card's stage and your VS Code panel already
   show a run while it runs. (Process for its own sake.)
2. **There is no gate check that a story in Ready names its spec.** That check would fail at once on P97, which you put
   in Ready with no spec. Instead, a story with no spec passes through Design when it is pulled, as two cards did in 13
   and 21 minutes. (It contradicted a decision.)
3. **An unanswered ask no longer goes to its default.** R1 proposed that. The roles lens shows two cases where Claude
   read consent into an answer, and both went wrong. Now nothing is decided until you answer. (The reports contradict
   each other, and the evidence decides.)
4. **There is no signature on Claude's GitHub writes,** and no daily "Product Goal" line. Each would be a habit with no
   check and no decision resting on it. Your decisions are quoted word for word instead. (A rule that relies on
   memory.)
5. **The measures and warnings moved into card C3,** out of P146. This keeps P146 one sitting, and nothing is built
   without your order. (Bloat inside the card.)
6. **Slices are asked for only at Ready.** The weekly look no longer triages slices, and the gate checks a slice from
   Ready on, not from Discovery on. Asking you to place a card just so a read can run, or to place cards nobody has
   pulled, would be a trivia ask.
7. **"Lenses on Sonnet" is now listed in what one yes accepts.** It changes the councils you set to full, so it should
   not ride in unannounced.
8. **Claims the verify files weakened are not used:** "three in flight is drum, buffer and rope", "halve the measured
   WIP", "fan-out is free", "two workflows at once, per Anthropic" and "nobody can hold the Scrum Master role". The
   three in flight is your "a bit". Concurrency follows the limits instead of a number of its own. (The reports
   contradict.)
9. **Limits stated plainly:**
   - The launch hook cannot see agents inside a workflow. That is acceptable only because workflows run when you ask
     for one.
   - The service level of 2 days is a guess, and the trial on 11-02 will correct it.
   - The Sonnet lenses are untested. The first such council is compared with the last full one.
