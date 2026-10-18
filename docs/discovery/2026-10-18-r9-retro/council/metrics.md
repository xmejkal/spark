# R9 flow metrics

Sources: F = council/facts.md; L = logs.json (135 agents); P = prs.json; B = board.json; G = `gh issue view` on 4
issues (createdAt, closedAt, updatedAt), read 2026-10-18.

## 1. Throughput, cycle time, WIP age

- Throughput: 51 PRs merged in 4 calendar days, 16 / 9 / 15 / 11 (10-15 to 10-18) (P, F). About 12.8 per day.
- Closed cards per day: not measured. B has no closedAt; Done is 92 of 188 items (F). Not read here, to spare the GraphQL limit.
- PR cycle time (open to merge): median 24 min, 85th percentile 190 min, 20 of 51 under 15 min (F). Longest 494 min, overnight (#296).
- Card cycle time (Build to Done): not measurable; B holds no stage-entry dates.
- Age of working-stage cards since the issue was created (G, as of 10-18 09:00). The board has no date for entering the stage.

| card | stage | age | last issue update |
| --- | --- | --- | --- |
| P213 #192 | Build | 5.6 d | 10-18 08:05 |
| P218 #200 (epic) | Design | 4.9 d | 10-18 05:49; Waiting since 10-17 (B) |
| P235 #224 (epic) | Build | 4.6 d | 10-17 01:31 |
| P269 #304 (epic) | Design | 2.0 d | 10-16 10:31, nothing since (1.9 d) |

- P297 #360 sits in Review with PR #362 already merged (B, F). It is done work with a stale column.
- Three of five working-stage cards are epics (F). The two non-epic cards are P213 and P297, and P297 is finished.

## 2. What the data cannot show, and the cheapest fix

- Time in Review, time in Design per card, card cycle time, and blocked time: the board keeps one date field, Waiting since, set on 1 open card (F).
- Cheapest fix: one board field "Entered stage", written by the same push hook that already counts WIP, each time a card changes status. Zero new tools. One date per card gives all four numbers by subtraction at the next retro.
- Fallback with no code: a one-line comment on the issue at each move ("Review, 10-19 14:10"), read back with `gh issue view --json comments` for at most 10 cards.

## 3. Cost of merge fixes and same-file parallel work (L, F)

- P239 PR 6 ran beside P242 on the same files: 460 calls, 41 min, 103 M input tokens. That is 14% of all 3338 calls and 20% of all 506 M tokens, from 1 of 135 agents.
- Six agents hit a refused push: 511 calls, 402 min, 134 M tokens (27% of all input tokens), 14 refusals in total. Not all of that cost is the refusal, since these are also the long runs.
- 15 merge commits of main into a branch; 10 name observation rows in INDEX.md (F). P296 #358 targets that file.
- Tool-call counts are string matches (F). Read all of these as upper bounds on what a merge fix costs.

## 4. Mutation yield (B, F, L)

- 10 cards with counts: 213 planted, 25 escaped (11.7%), 23 real gaps. P272 gave 6 real gaps of 12; P247 gave 0 of 12 (F).
- Cost: 11 mutation-tester runs, 193 min, 110 calls, 3.8 M tokens (L). That is 13% of agent minutes and under 1% of tokens.
- Yield: 193 / 23 = 8.4 min per real gap. Tokens are cheap, so the cost is wall time.
- Unknown: how many of the 23 a lens or the refuter catches anyway. Without that, the data supports keeping it for logic changes only. It does not support dropping it.

## 5. What to read at the next retro

| experiment | number | how to read it |
| --- | --- | --- |
| Epic not in flight | In-flight count excluding epics, read from B at each push; and age of non-epic cards in Build | Today 2 non-epic cards in Build/Design/Review (F). If it stays at or under 2 while PRs per day stay near 12.8, the epic slots were idle. If PRs per day fall, the slots were doing work. |
| Review limit 2, wait measured | Median and maximum days from "Entered stage = Review" to merged, per card | Needs the field from section 2. Compare with the PR median of 24 min: a card median above 1 day means the wait is the PO's merge, not the work. Count days with 2 cards in Review. |
| No parallel cards on the same files | Per card with a merge fix: calls and input tokens of its agent, and merge commits of main into its branch (`git log --merges`, grep "Merge ... main") | Baseline: 15 merge commits, 10 on INDEX.md, P239 PR 6 at 460 calls and 103 M tokens. Success is no run above 200 calls from a merge, and INDEX.md merges near 0 after P296. |
