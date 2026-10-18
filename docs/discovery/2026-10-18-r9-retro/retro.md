# R9 retro (draft, 2026-10-18, to hold with Petr)

> **TL;DR.** 51 PRs merged in four days, and no retro ran for 17 days. The push hook refused two pushes over a limit,
> and the limit still broke twice at the pull; three of five working-stage cards are epics. One run on the same
> files as another used 103 M of 506 M agent input tokens (cache reads included). Six themes, one small experiment each, three WIP experiments, and a cadence: a
> retro every 10 merged stories or 7 days, prepared from the board, the PRs and the agent logs. Every choice is Petr's.

Prepared by Claude (opus) with a council: a Lean expert, an Agile coach, a flow-metrics analyst (sonnet), six team
voices from the agents' own work (sonnet), and the refuter (opus). The numbers and their commands are in
[council/facts.md](council/facts.md); each voice is under [council/](council/). The window is 2026-10-15 to
2026-10-18; the agent logs cover 135 agents from 10-17 11:10 to 10-18 08:49 UTC.

## The 22 inbox items in six themes

| theme | inbox items (date) |
| --- | --- |
| 1. The limit breaks at the pull, and slots hold no work | slice 0 start (10-15), #224 without `epic` (10-15), the #315 hook exception (10-16), P272 pulled at 5 of 4 (10-17), epic card beside its child (10-17), P295 started at 4 of 4 (10-18) |
| 2. Two branches on the same files | P239 PR 6 beside P242 (10-17) |
| 3. Councils and checks: what they find, what they cost | names caught by Petr (10-15), the extra gaps round (10-15), the P261 experiments: the refuter, the weekly look's retro line, the sized council table (10-15), full-suite runs and my wrong claim (10-17) |
| 4. Agents and the lead share tools and collide | plan mode stopped four agents (10-16), the 28 MB edit script (10-16), plan files on the branch in the autonomous hours (10-16), the stray `git checkout` in main (10-17), the GraphQL rate limit hit four times in a morning (10-18) |
| 5. Learning that has no clock | logs analyzed before delete (10-15), the transcript pass P259 (10-15), experiments judged at the retro (10-15), the Kanban coach P265/P266 (10-16) |
| 6. How Claude asks and reports to Petr | typed sub-tasks per story (10-15), teacher-style questions (10-16) |

### Theme 1. The limit breaks at the pull, and slots hold no work

- Numbers: two WIP slips at the pull (P272 on 10-17, P295 on 10-18), plus slice 0 started before P239 finished
  (10-15). The hook refused two pushes: P272 (5 > 4) and #315's merge fix (Design at 3, pushed by Petr with
  `--no-verify`); the gate also counted #224 in Ready (6 of 5) for a missing label. Three of five working-stage cards
  are epics (P235, P218, P269); of the other two, P297 #360 is in Review with its PR #362 already merged. P218's
  issue is 4.9 days old; the board keeps no date for entering Design.
- Root cause: the limit is counted when a card moves, but work starts when an agent launches. Epic cards and cards
  that wait only on Petr fill the slots that the count protects.
- Proposal (Petr decides): before any builder or spike agent starts, Claude writes "in flight: N of 4" from
  `tools/board.py status` as the first line of the launch. Two weeks, to 2026-11-01. Judged by: slips in the inbox
  (today 2 in 4 days; the target is 0).

### Theme 2. Two branches on the same files

- Numbers: P239 PR 6 used 460 tool calls and 103 M input tokens (cache reads included), 20% of the log window's
  agent tokens, mostly on the merge after P242. 16 merges of main into a branch since 10-15; 11 messages name
  INDEX.md rows, 9 of them rows only. 14 failed pushes in the logs (P239 PR 7: 6), hook refusals and stale-branch
  rejects together.
- Root cause: nothing compares the files of two cards before the second starts; one shared rows file collides on
  every PR. P296 #358 (Ready) already moves the rows out.
- Proposal (Petr decides): Petr orders P296 to the top of Ready, so it lands before the next builder starts. Judged
  by: merges that name INDEX.md rows over the next 20 PRs (today 11 in 51).

### Theme 3. Councils and checks: what they find, what they cost

- Numbers: mutation on 10 cards: 213 planted, 25 escaped, 23 real gaps; on the six cards that also have a
  logged run, about 10 agent minutes a real gap, with separate runs for P239 PRs 5 to 8. The refuter: 34 runs, 9%
  of agent tokens in the log window; all-time INDEX.md holds 43 refuter rows marked CONFIRMED and 12 REJECTED. Four Opus lenses on one council cost 15 M tokens and 137 calls; a
  sonnet diff review takes 4 to 16 calls. Names still reached round 2 unchecked (AT451).
- Root cause (opinion, not counted): the sized council table exists but is not written into each PR, so councils
  grow by habit; the mutation tester runs per PR, not per story.
- Proposal (Petr decides): for two weeks, mutation runs once per story on the whole branch (12 plants), and Opus
  lenses run only on a design or an epic. Judged by: tester minutes per story (P239: four runs for one story
  today) and real gaps per story (today 2.3 over 10 cards). Refuter experiment: keep it on every PR that holds
  logic; its brief length is not in the logs, so that half stays unjudged.

### Theme 4. Agents and the lead share tools and collide

- Numbers: three incidents in two days (four agents stopped by plan mode, a 28 MB module, a detached HEAD in main),
  each undone after the fact. 17 rate-limit hits in the log window (P213a 4, the hygiene sweep 4).
- Root cause: agents and the lead share one checkout, one plan mode and one GraphQL budget, with nobody owning it.
- Proposal (Petr decides): every agent that runs any git command gets a worktree; plan work happens as a plan file
  on the branch, never in plan mode while an agent writes. Board edits go in one batch per turn. Two weeks. Judged by:
  incidents of this kind (today 3; the target is 0) and rate-limit hits per day in the logs (today 17 in 21 hours).

### Theme 5. Learning that has no clock

- Numbers: R8 was on 2026-10-01; 134 PRs merged into main since, 51 of them from 10-15. At least five inbox lines name an
  experiment "to judge" with no date. The only retro trigger is an epic's last story, and P235 is still in Build.
- Root cause: the trigger never fires on a long epic, and the weekly look's retro line is done by hand.
- Proposal (Petr decides): the cadence below. Judged by: retros held in the next four weeks (the target is 4) and
  experiments judged on their due date (the target is all).

### Theme 6. How Claude asks and reports to Petr

- Numbers: Petr asked for typed sub-tasks per story on 10-15; P252 got two (#275, #276) that day, and no story since. Six teacher-style questions
  worked at once where Q1 "rate the assumptions" confused him (P269).
- Root cause: both live in the inbox, not in the skill or the flow that applies them.
- Proposal (Petr decides): for the next three stories, each gets typed `task` sub-issues (test, implementation,
  documentation) as work reveals them. Judged by: stories with two or more typed tasks (target 3 of 3), and Petr's
  word at the next retro on whether they helped him follow the work.

## Three WIP experiments

| experiment | what changes | measure | time box |
| --- | --- | --- | --- |
| A. An epic card does not count in flight | the gate counts story, spike, chore and bug cards in flight; an epic card shows its state, not a slot | slips and hook refusals over the limit (today 2 slips, 2 refusals, 1 `--no-verify`); PRs merged per day (today 12.8): if it falls, the epic slots held work | to the trial check, 2026-11-02 |
| B. Review stays at 2, and its wait is measured | a card that enters Review gets *Waiting on* "PO merge" and *Waiting since* the same hour (fields that exist); the day-close prints its age | median and longest wait in Review per card, beside PR open to merge (today median 24 min, 85th percentile 190 min); no card-side baseline exists yet | the next 20 merged PRs |
| C. Two cards that touch the same files never run in parallel | each plan lists the files it edits; before a pull, Claude compares them with the cards in Build and Review, and on a match the second card waits | merges of main that are not about rows (today 5 of 16), the largest single run (today 103 M tokens); P296 removes the row merges, so the two read apart | two weeks, to 2026-11-01 |

The Lean expert's view on A: exempt only an epic that waits on Petr and has no agent running, since P218 and P269
also hold real discovery work. Petr picks the broad or the narrow form.

## Cadence

- **Trigger:** a retro every 10 merged stories or 7 days, whichever comes first, and at an epic's end. At today's rate
  the 7-day clock fires first. The session-start status prints "retro due" when either is reached: a prompt, not a gate.
- **Prepared by the team with this council:** a script reads the board, the merged PRs and the agent logs into one
  facts page; the Lean, Agile and metrics experts and the team roles read it and return at most three proposals;
  the refuter checks every number.
- **Held with Petr:** 30 minutes. First the last experiments' verdicts, then the numbers, then the inbox, then he picks
  at most two changes. Claude never closes a retro alone.
- **The running inbox:** each line keeps its date and gets a type: slip, question or experiment. An experiment line
  carries its measure and its due retro from the day it starts.
- **How results come back:** each retro entry ends with a table "experiment / measure / due". The next retro opens with
  that table, and each row gets held, did not hold, or dropped, with the number beside it. An experiment still
  unjudged at its due retro is dropped, so none lives on in silence.

## The team's voice: the logs, as an experiment

Petr's decision (2026-10-18): *"We'll see if the process improvements also happen if it's only with the logs."* So the
team speaks through its logs: a script reads the subagent JSONL for tool calls, minutes, tokens, refused pushes,
conflicts, rate-limit hits and full-suite runs per agent. No agent writes an extra note for now. R9's six role
voices were drawn from that evidence.

- Measure at R10: did a log number lead to at least one proposal that changed a number; and a list of what the logs
  missed that a note gives (R9's first entries: the refuter's brief length, the reason behind each slip).
- Known weakness: "CONFLICT", "rate limit" and "failed to push" are string matches, so they count a word read in a
  file and a stale-branch reject too. R10's script counts git's own `CONFLICT (content)` lines and the hook's own
  refusal line. The log window is 21 hours; R10's covers the whole period.

## What waits on Petr

Hold this retro with Claude: pick at most two theme proposals, the form of WIP experiment A, B and C yes or no, and the
cadence. Then the R9 entry in `scrum/RETROSPECTIVES.md` loses its draft mark.
