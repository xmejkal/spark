# Refuter at R9 (opus, 34 runs, 2026-10-17 to 2026-10-18)
Evidence: facts.md agent table, logs.json (type "refuter"), INDEX.md rows that name the refuter. I read no PR bodies.
What helped
- It still finds real defects. INDEX.md has 223 rows that name the refuter: 43 carry CONFIRMED and 12 carry REJECTED (uppercase match).
- A REJECTED claim fails its reproduction, so it never reaches a fix. That saves work.
- It is cheap next to the builders: 46 M of 506 M input tokens (9%), 119 of 1438 minutes (8%), about 3.5 minutes a run.
What slowed or wasted
- 102 of 739 tool calls came back as errors (14%), 3 a run, the highest error count of any agent type except the builders.
- 21.7 tool calls a run, 20.4 of them Bash. I cannot tell from the logs how many go to re-finding the diff.
- I cannot show the brief got shorter. The logs record no brief length, so that half of the question has no number.
One change I ask for
- The council gives me the PR number, the branch worktree path and the reviewers' claims as a numbered list. Each verdict then maps to one claim.
Verdict: change. Keep the seat on every PR that holds logic. Drop it for docs-only PRs under 50 lines, where the rules already send one reviewer. Log brief length so R10 can judge it.
