# R9 facts, read 2026-10-18 about 09:00

The data every council member reads. Each number names its command. Raw outputs sit in the lead's scratch folder,
not in the repository.

## The board (`gh project item-list 2 --owner xmejkal --format json --limit 300`, one read)

- 188 items: Done 92, Idea 83, Ready 5, Build 2, Design 2, Review 1, no status 3.
- In a working stage: Build P235 #224 (epic, slice Live 0), Build P213 #192; Design P218 #200 (epic, Waiting since
  2026-10-17, no Waiting on), Design P269 #304 (epic); Review P297 #360 (spike, PR #362 already merged).
- Three of the five cards in working stages are epics. Without epics, 2 cards are in flight.
- Ready: P278 #314, P290 #347, P296 #358, P299 #365, P300 #366.
- Waiting since is set on one open card only (P218, 2026-10-17). The board keeps no history of when a card entered
  Review, so wait time in Review cannot be read from the board today.
- Mutation fields are filled on 11 Done cards (P283, P239, P273, P272, P280, P242, P253, P254, P247, P282; P287 has
  only Mutation minutes 14). Over the 10 cards with counts: 213 planted, 25 escaped, 23 real gaps found. P272: 6 of
  12 escaped, all 6 real gaps. P247: 0 of 12.

## Merged PRs (`gh pr list --state merged --search "merged:>=2026-10-15" --limit 100`)

- 51 PRs merged from 2026-10-15 00:23 to 2026-10-18 08:37 UTC: 16 on 10-15, 9 on 10-16, 15 on 10-17, 11 on 10-18.
- Open to merge: median 24 min, 85th percentile 190 min; 20 of 51 under 15 min. Longest: #296 494 min (overnight),
  #343 449 min (P239 PR 6), #261 416 min, #321 380 min, #334 and #335 264 min each.
- Merge commits of main into a branch since 10-15 (`git log origin/main --since=2026-10-15`, grep "Merge ... main"):
  15. Ten of their messages name observation rows (INDEX.md) as what the merge kept or renumbered.
  Examples: `ac4e965` "rows AT420-AT442 kept beside AT450-AT454", `d47b2c9` "rows renumbered AT383-AT386".

## Agent logs (this session's subagent JSONL, 135 agents, 2026-10-17 11:10 to 2026-10-18 08:49 UTC)

Read by a throwaway script with `python3 -I`, line by line; counts are string matches, so CONFLICT includes a word
read in a file, not only a git conflict.

| type | agents | tool calls | minutes (sum) | input tokens incl. cache (M) | push refused | CONFLICT | rate limit | full-suite runs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| general-purpose (builders, lenses, spikes) | 80 | 2405 | 1115 | 453 | 14 | 18 | 16 | 16 |
| refuter (opus) | 34 | 739 | 119 | 46 | 0 | 8 | 0 | 1 |
| mutation-tester | 11 | 110 | 193 | 3.8 | 0 | 2 | 0 | 1 |
| Plan | 6 | 34 | 9 | 1.3 | 0 | 1 | 0 | 0 |
| code-reviewer | 3 | 42 | 2 | 1.8 | 0 | 0 | 0 | 0 |
| total | 135 | 3338 | 1438 | 506 | 14 | 29 | 17 | 18 |

- Largest single run: P239 PR 6 LookReport, 460 tool calls, 41 min, 103 M input tokens (the inbox: most of it went on
  the merge after P242 touched the same files). Next: P242 188 calls 58 M; P273 150 calls 42 M; P287 110 calls 38 M.
- Push refusals by run: P239 PR 7 6, P287 3, P288 2, P242 1, P213a 1, P272 plan 1.
- Rate-limit hits by run: P213a 4, hygiene sweep 4, P239 PR 8 3, P294 2, others 1 each.
- 287 tool results flagged as errors (164 general-purpose, 102 refuter, 20 mutation-tester).

## Already acted on (do not propose again)

- P288 #344, PR #349: mutation analysis with numbers from the repo.
- P296 #358 (Ready): rows out of the shared INDEX.md, the source of most merge fixes.
- P289 #345: process data (the number fields above).
- WIP limits: 2 per working stage, 5 in Ready, 4 in flight; the push hook checks them.
