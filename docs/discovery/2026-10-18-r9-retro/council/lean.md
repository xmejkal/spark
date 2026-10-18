# R9 council: the Lean view

Written 2026-10-18. Facts come from `facts.md` and the retro inbox. Lines marked (opinion) are my judgement, not data.

## 1. The biggest wastes and flow problems

1. Rework from parallel work on the same files. P239 PR 6 ran beside P242 on deploy.py, look.py and board_look.py.
   The merge took most of 460 tool calls and 103 M of the 506 M input tokens (about 20% of all agent tokens in the
   window). Fifteen merges of main into a branch since 10-15, ten of them about INDEX.md rows. Push refused 14 times.
   This is the waste of defects and of waiting on a merge: work done twice.
2. Cards that hold a slot and do not move. P218 #200 has sat in Design 4+ days, Waiting since 10-17, no Waiting on.
   P269 #304 waits on a Slice option only the PO can add. Of 5 cards in working stages, 3 are epics, so 2 cards carry
   real work. The limit of 4 is full of waiting, not of work. P297 #360 sits in Review with its PR #362 already merged:
   a stale card that costs a slot.
3. The WIP limit is broken by pull, not by the gate. Two slips in two days (P272 on 10-17, P295 on 10-18), and the 10-15
   slice 0 start. The hook caught only one. Agents ran before the card moved (P295). The limit is counted at the
   stage, not at the moment work starts.
4. No flow data. The board keeps no history of when a card entered Review, so Review wait cannot be read. Waiting
   since is filled on one open card. We steer by feeling. Merge time is the only measured wait: median 24 min, 85th
   percentile 190 min, longest 494 min (overnight).
5. (Opinion) Agent cost is large batch size in disguise: 17 rate-limit hits, 18 full-suite runs, 287 error results.
   Small, ordered slices cause less of this than any tool change.

## 2. The three WIP experiments

Experiment A: an epic card does not count in flight.
- (Opinion) Try it, but only for an epic card that waits on the PO and has no running agent. The README already says
  epics count only in Discovery and Design. The inbox case is P235 in Build beside its children. A blanket exemption
  hides real work, since P218 and P269 are real discovery work too.
- Measure: days a card waited on the PO (the trial's own check), and slips: pushes refused by the hook plus agent runs
  started on a card outside the limit. Success: no rise in slips, fewer days waiting.
- Time box: to the trial check on 2026-11-02, then keep or drop.

Experiment B: keep Review at 2 and measure wait time.
- (Opinion) Keep 2. Review is not the bottleneck: 20 of 51 PRs merged in under 15 min. The long waits are overnight.
  The slots are lost in Design and to stale cards, not here.
- Measure: PR open to merge, median and 85th percentile (now 24 and 190 min), read from `gh pr list`. Add a "Review
  since" date on the card, so the card side can be read too. Success: p85 stays under 190 min.
- Time box: the next 20 merged PRs, about one week at the current rate.

Experiment C: two cards that touch the same files never run in parallel.
- (Opinion) Adopt it. It is the only one of the three with a measured loss behind it (waste 1).
- Measure: merges of main per PR (15 in 4 days now), tokens per run (P239 PR 6: 103 M), and push refusals (14). The plan
  lists the files it touches; the lead orders overlapping cards in Ready. Success: no run above 60 M tokens from a merge,
  and merges of main under half of today's rate.
- Time box: two weeks, 2026-11-01. Judge it with the rows move out of INDEX.md (P296), since that removes the other
  half of the merge cost. Read the two effects apart.

## 3. My first proposal (opinion)

Order cards that share files, and write the file list in the plan. Concrete steps: the plan names the files it edits;
before a pull, the lead checks them against the cards in Build and Review; on a match, the second card waits in Ready.
It is one line in the plan template, no tool, no cost, and it attacks the largest measured waste. Second: close or
cut stale cards (P297 now, P218 this week) so slots show real work.
