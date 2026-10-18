# Tech lead at R9
Evidence: facts.md, retro inbox, plan Council sections (P271, P239 PR 4), agent log table.
## What helped
- Plan councils caught design faults before code. P271 round 1 swapped inline SVGs for `<img>` data URIs after Chrome reproduced the mixed styles. P239 PR 4 fixed two clock names and renamed `RunLog` to `BoardLog`.
- The refuter found real defects (34 runs; the inbox says visual defects twice). Mutation runs found real test gaps: P272 had 6 of 12 escape, all real; 23 of 25 escapes over 10 cards were real.
- Small PRs merge fast: median 24 min, 20 of 51 under 15 min.
## What slowed or wasted
- Two PRs on the same files: P239 PR 6 ran beside P242 on deploy.py, look.py and board_look.py. The merge cost 460 tool calls and 103 M input tokens, the largest run in the log.
- Shared INDEX.md: 10 of 15 merges of main into a branch were about observation rows. P296 already covers it.
- Plan mode stopped four running review agents on 10-16 (AT272). A 28 MB module came from an unchecked edit script slice (AT283); only the next import caught it.
- 14 push refusals, 6 of them in P239 PR 7.
## One change I ask for
Before a card moves to Build, the lead compares its file list from the plan with the other Build cards. If files overlap, the second card waits and goes behind the first. The WIP limit of 2 does not catch this: two cards in Build still collide on the same files, and P239 PR 6 paid for it.
