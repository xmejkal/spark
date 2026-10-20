# R10 facts, read 2026-10-20 about 16:30 (Prague)

The data every council member reads. Each number names its command. Raw outputs sit in the lead's scratch folder,
not in the repository. Window: R9's hold, 2026-10-18 10:00 Prague (08:00 UTC), to 2026-10-20 about 16:30 Prague
(about 54 hours). Times in the logs are UTC unless a line says Prague.

## The board (`gh project item-list 2 --owner xmejkal --format json --limit 500`, one read)

- 247 items: Done 122, Idea 115, Ready 5, Design 5. Build 0, Review 0, Discovery 0, no status 0.
- Working stages hold only Design: P235 #224 (epic), P269 #304 (epic), P325 #417 (epic), P327 #419 (story),
  P328 #420 (story). Three of five are epics. Without epics, 2 cards are in flight (Design limit is 2).
- "Waiting on" and "Waiting since" are empty on all five Design cards.
- Ready: P100 #6 (epic, Waiting on "hardware", since 2026-10-19), P320 #406, P352 #450, P353 #451, P354 #452.
  Waiting since is set on one open card only (P100). Nothing sits in Review now, so experiment B's wait in Review
  has no card on the board to read. The board keeps no stage history.
- Cards closed in the window (`gh issue list --state closed --search "closed:>=2026-10-18"`, one read, filtered to
  after 08:00 UTC): 29. By label: story 6, chore 5, bug 5, task 8, spike 3, epic 1 (P218 #200), no label 3.
  A card can carry two labels, so the sum is above 29.
- Mutation fields on cards Done in the window, 3 cards: P279 #317 (14 planted, 0 escaped, 1 real gap, 26 min),
  P223 #205 (7, 0, 3, 10 min), P213 #192 (7, 0, 2, 14 min). Sum: 28 planted, 0 escaped, 6 real gaps, 50 minutes.
  A real gap with 0 escaped means the field counts gaps found by the run, not only escapes.
  Stories done in the window with no field filled: P299, P300, P330, P326, P337 (and P290, P278 as non-story cards).
- Cards opened since 10-19 00:00 (`gh issue list --state all --search "created:>=2026-10-19"`): 45. Story 22,
  spike 5, epic 5, chore 2, task 1, no label 10.

## Merged PRs (`gh pr list --state merged --search "merged:>=2026-10-18" ...`, cut at mergedAt 08:00 UTC)

- 30 PRs, #359 to #456. Per Prague day: 13 on 10-18 (from 10:00), 12 on 10-19, 5 on 10-20 (to 14:56).
  About 13.6 per day over 53 hours (R9: 12.8).
- Open to merge: median 25 min, 85th percentile 122 min. 8 of 30 under 15 min (R9: 24 and 190).
  Longest: #447 P326 822 min, #449 P351 814 min, #400 P279 477 min, #397 P300 124 min, #456 P337 B 122 min.
- Docs-only 14 PRs, code 16 (code = a file under scripts/ tools/ src/ lib/ or a .py outside docs/).
  Lines added plus deleted: 4644 in code files, 7748 in all others.
- Largest PR file count is under 100, so the `files` list is complete.

## R9's check column

- R9.1 WIP slips at the pull. The inbox (`~/.claude/projects/<spark>/memory/retro-inbox.md`)
  has 0 new WIP-slip lines dated after the hold. Its only slip lines are before it (P272 10-17, P295 10-18).
  The board now shows Design 5 cards, 3 of them epics. The gate counts 2. Hook refusals over the limit: not found
  (see Not found).
- R9.2 Merges of main into a branch (`git log origin/main --since=2026-10-18T08:00:00Z --merges`, subject
  "Merge ... main", not "pull request"): 2, both on 10-18 before 13:00 UTC: `72796e0` (P213a, README) and
  `bf2c48a` (P278). Neither names INDEX.md rows. R9 counted 16 in three days, 11 naming rows. P296 (#386) merged
  10-18.
- R9.3 Mutation-tester runs: 9 agents in the log window (below). Mutation numbers per card: 3 filled cards, 28
  planted, 0 escaped, 6 real gaps, 50 min. Runs that left no card field: the P337 A run (log 09:47 UTC 10-20).
  Planted-per-story and real-gaps-per-story are known only for those 3 cards.
- R9.4 Incidents. GraphQL rate-limit text in tool results (`API rate limit exceeded`, string match, all sessions):
  10-18 subagents 19, main session 9. 10-19 main session 5. 10-20 0. Plan-mode text in an error result: 2
  (10-18 one, 10-19 one), string match only. Stray `git checkout` in main: not found. Edit-script blowups: not found.
- R9.5 Typed `task` sub-issues (`gh api repos/xmejkal/spark/issues/N/sub_issues`) on the 6 stories closed after
  P278 (#314): P279 #317 0, P299 #365 0, P300 #366 1, P330 #423 0, P326 #418 0, P337 #431 0. Stories with 2 or more
  tasks: 0 of 6 (target 3 of 3). The cards with 3 tasks (P296, P290) are a chore and a bug.
- WIP A (epic does not count): board has 3 epics in Design and 2 stories. Gate reads 2 of 2. PRs per day 13.6, not
  lower than R9's 12.8.
- WIP B (Review wait): 0 cards in Review now. No "Waiting since" history. 30 PRs merged since, over the 20 asked.
  Open to merge median 25 min, p85 122 min, as above. Card-side wait: not found.
- WIP C (same files, no parallel work): merges of main not about rows: 2 (both listed above). Largest single run
  below: 26 M tokens (R9: 103 M).
- Cadence: R10 held 2026-10-20, 2 days after 10-18, within 7 days: yes. PRs since the hold: 30, over 10.

## Agent logs (`~/.claude/projects/<spark>/*/subagents/agent-*.jsonl`)

182 files modified after 2026-10-18 10:00 Prague, first message 09:46 Prague 10-18, last 16:28 Prague 10-20. Read by a
`python3 -I` script, line by line. Types from each file's `.meta.json` `agentType`. Input tokens add input, cache
creation and cache read of every assistant turn. Minutes are last minus first message. Push refused counts the text
"failed to push some refs" (hook refusals and stale rejects together). Rate limit counts "rate limit exceeded".
Full-suite is any Bash call with pytest, unittest or check_commit and no single test file, `-k` or `::`.
It is a wide match. R9's rule is not written down, so compare with care.

| type | agents | tool calls | minutes (sum) | input tokens incl. cache (M) | push refused | git CONFLICT | rate limit | full-suite runs | tool errors |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| general-purpose | 109 | 1797 | 503 | 256.7 | 5 | 1 | 19 | 89 | 113 |
| refuter | 38 | 735 | 169 | 48.1 | 0 | 3 | 0 | 44 | 36 |
| feature-dev:code-reviewer | 12 | 161 | 7 | 6.4 | 0 | 0 | 0 | 1 | 3 |
| Plan | 11 | 59 | 6 | 2.7 | 0 | 0 | 0 | 0 | 1 |
| unknown (no meta) | 1 | 6 | 2 | 2.5 | 0 | 0 | 0 | 2 | 1 |
| mutation-tester | 9 | 60 | 142 | 1.7 | 0 | 0 | 0 | 0 | 2 |
| Explore | 2 | 18 | 1 | 1.0 | 0 | 0 | 0 | 0 | 0 |
| total | 182 | 2836 | 831 | 319.1 | 5 | 4 | 19 | 136 | 156 |

- `CONFLICT` here is git's own `CONFLICT (content)` line (R9 used a word match: 29). Rate limit is the GitHub
  text, not any use of the words.
- The 5 largest runs by tokens: P278 "shipped XIAO record builds" 26 M (113 calls, 30 min, 10-18 10:55),
  "Implement P300 change list" 25 M (90 calls, 71 min). P213a "look and deploy --json" 16 M (73 calls, 47 min),
  "R9 retro with Lean/Agile council" 12 M (75 calls, 19 min), "Implement P337 PR B" 11 M (58 calls, 31 min).
- Refuter-style agents by description: 24 refuters plus 1 general-purpose run named refuter, against 30 PRs.
  Mutation runs by description: 6 (the other 3 mutation-tester files have other descriptions).
- Tool errors: 156 results flagged as errors (R9: 287 in 21 hours).

## Process signals

- Plans through `tools/factcheck.py` (grep "factcheck" in the 18 rows files modified since the hold, from
  `git log origin/main --since=2026-10-18T08:00:00Z --name-only -- docs/observations/rows`): named in 2 files,
  p337-no-simulation.md (2 hits, "16 references ok, 0 broken, 4 new names") and p221-arduino.md (1 hit). The
  inbox of 10-20 says it was skipped on P337 until asked. Other plans of the window (P331, P330, P326): no hit.
- Refuter rows (the source column says refuter, in those 18 files, table parse): 122 rows. Status: acted 98,
  rejected 13, closed 4, raised 5, verified 2. All rows of those files: 314. Acted 205, rejected 33, raised 42,
  verified 21, closed 9. The parse is rough, since columns vary by file. R9's crude count was 257 mentions,
  186 acted, 33 rejected (different base).
- The course change of 10-19 (one refuter per plan. No new council, spike or Miro unless asked). Refuter-agent
  starts after 10-19 18:00 Prague (16:00 UTC): 8, and 7 of them match a card. Per plan or PR: P331 plan 2 (16:19 and 16:51 UTC), P337 plan 1,
  P337 A 1, P337 B 1, P221 finding 1, P221 final plan 1. So P331's plan got a second refuter, and P221 got two (one on the finding, one on the plan).
- Spikes filed since 10-19 18:00 Prague (`gh issue list --search "created:>=2026-10-19"`): P361 #462 (10-20 11:18
  UTC, inside the P356 plan). Spikes filed 10-19 at 17:00 Prague, just before: P344 #439, P348 #443. Councils: no
  council-named agent or card since that evening. Miro: not measured.
- New card families since 10-19 17:00: P349 to P355 (7 cards from walk 1) and P356 to P362 (the P221 plan, 7 cards).

## Not found

- Hook refusals over the WIP limit: the hook's own line is not in the subagent logs, and the hold's run of the
  main session is not read. Only "failed to push" is counted (5, subagents).
- Slips per day at the pull: no new inbox line, and the board has no pull history.
- Wait in Review per card: no stage history on the board. No card is in Review now.
- Stray `git checkout` in the main checkout and edit-script blowups: the logs do not give the working directory
  of each call, so an agent's checkout cannot be placed in main. The main session's own checkouts are by design and not counted.
- Real gaps and planted mutants for stories without a filled Mutation field (P299, P300, P330, P326, P337): not
  on the board. The mutation-tester return text was not read.
- Tool calls and tokens of the main session: only subagent files were read.
- Miro board state and the PO's word on whether typed tasks helped him follow the work: not read.

## Numbers the retro page takes from other sources

- R9's baselines (2.3 real gaps per card, 17 rate-limit hits in 21 hours, 11 of 51 merges naming rows): R9's page,
  `docs/discovery/2026-10-18-r9-retro/retro.md`, and `scrum/RETROSPECTIVES.md` (R9). The 51 is R9's count of PRs merged.
- Walk 1's 21 rows (19 from the walk, 2 from the PR review): `docs/observations/rows/p326-walk1.md`.
- P337's plan: 1 false claim and 8 gaps, all 9 caught by the refuter: `docs/observations/rows/p337-no-simulation.md`.
- Cards opened since the hold: 73 at 16:30 Prague on 2026-10-20 (74 at the review, when one more card was filed),
  `gh issue list --state all --search "created:>=2026-10-18T08:00:00Z" --limit 300 --json number --jq length`.
