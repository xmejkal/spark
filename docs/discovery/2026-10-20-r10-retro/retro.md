# R10 retro (2026-10-20, prepared for Petr)

> Walk 1 lit the LED on the bench on 10-19, and one walk found 21 rows. That is more than any review found.
> R9's worktree and same-files rules worked: 2 merges of main (was 16), and the largest run is 26 M tokens (was 103 M).
> Cards grow faster than they close (73 opened, 29 closed), and three R9 checks left no record to read.

In 54 hours, 30 PRs merged and 29 cards closed. The changes that removed collisions held. The changes that asked
Claude to write a record by hand (typed tasks, Review wait, mutation fields, factcheck) mostly did not happen. The
proposals below remove manual steps or let a script do them, and they put walk 2 first.

Prepared by one agent (Opus) as a Lean coach, an Agile coach and a flow analyst, with the logs as the team's voice.
Every number is from [council/facts.md](council/facts.md) unless a line names its own command. The window is
2026-10-18 10:00 to 2026-10-20 about 16:30, Prague time.

## R9's actions, checked as written

| action | measure at R10 | verdict |
| --- | --- | --- |
| R9.1 "in flight: N of 4" at each launch | slips in the inbox after the hold: 0 (target 0). Whether the launch line was written was not counted. | held, on a self-reported measure |
| R9.2 P296 first (rows out of INDEX.md) | merges of main that name INDEX.md rows: 0 of 2 merges, over 30 PRs (was 11 of 51) | held |
| R9.3 mutation once per story, Opus lenses only on a design or an epic | Mutation field on 3 cards: 28 planted, 6 real gaps, 50 min, so 2.0 gaps and 17 min a card (was 2.3 gaps). Five stories have no field. Lens models were not counted. | not measurable (3 of 8 cards) |
| R9.4 worktrees, batched board edits | rate-limit text: 10-18 28, 10-19 5, 10-20 0 (was 17 in 21 hours). Plan-mode error text: 2. Stray checkout and edit blowups: not found in the logs. | not held, falling to 0 on 10-20 |
| R9.5 typed `task` sub-issues on 3 stories | stories with 2 or more tasks: 0 of 6 (target 3 of 3). Petr's word: not asked. | not held |
| WIP A, no epic counts | PRs per day 13.6 (was 12.8), so the epic slots did not hide work. Hook refusals over the limit: not in the logs. Design holds 5 cards, 3 of them epics. | held on PRs per day, refusals not measurable |
| WIP B, Review wait measured | no card got "Waiting on" or "Waiting since" in Review. Only P100 has a "Waiting since". PR open to merge: median 25 min, p85 122 min (was 24 and 190). | not held (the fields stayed empty) |
| WIP C, same files never in parallel | merges of main not about rows: 2 (was 5). Largest run: 26 M tokens (was 103 M). | held |
| Cadence | R10 held 2 days after R9, within 7 days, and opens with this table | held |
| Logs as the team's voice | the 103 M run and the 16 merges in R9's logs led to WIP C and P296, and both numbers fell (26 M, 2 merges) | held |

## Experiments to judge

| experiment | evidence | proposal |
| --- | --- | --- |
| P324 #415: the builder checks plan claims, `tools/factcheck.py` checks plans, one refuter | factcheck is named in 2 of 18 rows files (P337, P221). P331, P330 and P326 have no hit. On P337 it ran only after Petr asked, and claims were marked "seen" before a grep. The builder's false claim ("tests pass unchanged") was caught by the refuter, not by the builder. | change: the push hook runs factcheck on plan files (theme 3). Drop "the builder checks each claim" as a written step, since it did not happen. |
| The refuter on Opus (P261) | 38 refuter agents, 48.1 M of 319.1 M agent tokens (15%), 169 min. 122 of 314 rows have the refuter as source, 98 acted, 13 rejected. It caught all 9 of P337's plan problems. | keep, one per plan and one per PR that holds logic. No refuter on a docs-only PR (14 of 30 PRs). |
| The course change of 10-19 (walk 1 first, one refuter, no new council, spike or Miro unless asked) | Walk 1 ran that evening and the LED lit. Councils since: 0. Spikes since: 1 (P361, inside a plan), 2 the hour before. Second refuters: 2 (both on the P331 plan, 18:19 and 18:51). Lines changed: 4644 in code, 7748 in other files (ratio 1.7). | keep. Count a second refuter on one plan as a slip in the inbox. |

## Theme 1. The bench finds what reviews do not

- Numbers: walk 1 (P326, 10-19) produced 21 rows and 7 cards (P349 to P355). 19 of 21 come from the walk itself and 2 from the PR review, for
  example the LED polarity (row 5) and `deploy.py` refusing an image without a Wokwi run (row 7). The
  LED lit, but through `mpremote` outside spark. P100 sits in Ready, "Waiting on: hardware" since 10-19.
- Why? The reviews read code and plans, not a board. Why do walks run so rarely? Each walk waits for a free evening
  of Petr's and for parts. Lean waste: waiting, and defects found late.
- Experiment: walk 2 (P100 round A) runs by 2026-10-27 with what is on the desk: the board's own button and LED, no
  new parts. Measure: steps that leave spark (walk 1: the copy by `mpremote`) and stops that need a card. Target: 0
  steps outside spark. Cost: about 90 min of Petr's bench time. P337 (#456, merged) already removes the Wokwi gate of row 7.

## Theme 2. Cards grow faster than they close

- Numbers: 73 cards opened since the hold (`gh issue list --state all --search "created:>=2026-10-18T08:00:00Z"`),
  29 closed. The board holds 115 Ideas. Walk 1 and the P221 plan filed 7 cards each. P299 was filed from a backlog
  Petr approved with one "yes", and he closed it at its first question (inbox 10-18).
- Why? Every raised row may become a card, and a plan files its follow-ups as cards. Why? The rule "suggest cards for
  found bugs" has no bar. Lean waste: inventory, and overproduction of text (14 of 30 PRs are docs-only).
- Experiment: to R11, a row becomes a card only if it blocks the next walk step. Every other row stays "raised" in
  its rows file. Measure: cards opened per closed card (now 73 to 29). Target: 1 or less. Cost: saves tokens and
  board writes. No PO time.

## Theme 3. Hallucinations are caught at the last gate only

- Numbers: P337's plan held 1 false claim and 8 gaps. The refuter caught all 9. The builder's own check caught none.
  Factcheck ran on 2 plans of 5, once only when asked. No metric shows a trend over plans.
- Why was factcheck skipped? It is a manual step. Why is it manual? P324 built the script but left it out of the hook,
  and the hook is the only gate that always runs. Lean waste: a defect that passes the builder and reaches the last station.
- Experiment: the push hook runs `tools/factcheck.py` on every plan file a push changes, and a broken reference fails
  the push. Measure: plans pushed with a factcheck result (now 2 of 5), and false claims the refuter still finds that
  factcheck could have found. Target: 5 of 5 plans. Cost: one small chore, a few seconds per push. The trend line per
  rows file (inbox 10-20, proposal 1) waits, as it adds a record by hand.

## Theme 4. Records written by hand are not written

- Numbers: Mutation field on 3 of 8 cards, typed tasks 0 of 6 stories, "Waiting since" on 1 open card. Build, Review
  and Discovery hold 0 cards, and Design holds 2 stories beside 3 epics. GraphQL ran out 33 times in the logs.
- Why are the fields empty? Each one is an extra board write per card. Why are they costly? Every board write is a
  GraphQL call, and GraphQL runs out. Lean waste: overprocessing. The records serve the retro, not the breadboard.
- Experiment: drop typed tasks (R9.5) and the Review-wait fields (WIP B). Keep one record per story: the mutation
  line "N planted, M escaped, K real gaps" in the PR's rows file, where the retro script reads it. Measure: stories
  with that line (target: all to R11), and rate-limit hits (target 0). Cost: saves board writes, no PO time.

## What the logs missed

- Whether the "in flight: N of 4" line was written at each launch, so R9.1's 0 slips is self-reported.
- The push hook's own refusal line, so WIP A's refusals and limit hits cannot be read.
- Why the builder marked P337's claims "seen" before a grep. Only the inbox line says it.
- What the mutation tester returned on 5 stories with no field. The return text was not read.
- The main session's own tool calls and tokens, and the Miro board's state.
- Petr's word on whether typed tasks helped him follow the work.

## Questions for Petr

1. Theme 1: does walk 2 (P100 round A) run by 2026-10-27 with the board's own button and LED, yes or no?
2. Theme 2: does a row become a card only when it blocks the next walk step, yes or no?
3. Theme 3: does the push hook run factcheck on changed plan files, yes or no?
4. Theme 4: drop typed tasks and the Review-wait fields, and keep only the mutation line per story, yes or no?
