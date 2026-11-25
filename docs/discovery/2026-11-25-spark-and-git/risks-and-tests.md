# Risks and tests

## Risks
<!-- One row per type; an active extension adds its own rows. evidence now: tag and ids (★C<n>, A<n>).
status: open · retired · n/a because ….
e.g. `| usability | H no test yet (A2) | a five-person prototype test | open |` -->
| risk | evidence now | cheapest way to retire it | status |
| --- | --- | --- | --- |
| value <!-- REQUIRED:risk-value --> | H a person wants an undo from spark beyond what Claude does with git (A3). The PO asked for it (D9), n = 1, and nobody is blocked today (G10, H per the refuter) | count each "undo" moment in the next two walks (A3) | open |
| usability <!-- REQUIRED:risk-usability --> | H every rule finds one home and a gadget session loads no team rule (A4). H a person with no git identity knows the one next step (A5). E today's lines name git and Claude (brief C30 in Found on the way) | the A4 table read by the PO, and one scratch start with no identity (A5) | open |
| feasibility <!-- REQUIRED:risk-feasibility --> | H spark's commits happen and are safe (A1, high D13). H a take-back by git revert works for any kept step (A2). H one step per decision keeps the tree clean (A6). H one strategy serves every interface (A7). E ★C14, ★C21 | the A1 scratch walk and count (D13), then A2, A6 and A7 in scratch | open |
| viability <!-- REQUIRED:risk-viability --> | H kept steps on a PR-flow `main` are what the PO expects (A8). The work is off the path to a breadboard (G10) | one account question to the PO (Q14) | open |
| ethics and safety <!-- REQUIRED:risk-ethics --> | E a later `git init` can commit the rules link with a home path (★C16, an open door). E 81 flash images and 3 run files are tracked in 2 repositories (★C15). E the `git restore` fallback overwrites a person's edits (Found on the way) | the ignore list first (A1's pass line), and Q19 on a hook for the never-rules | open |

## Assumptions
<!-- About ten at most. type: value, usability, feasibility, viability or ethics. importance: "— (decider)" until
the decider rates it, then "high D<n>" or "low D<n>". pass line: written, with its date, before any result.
status: open, or retired with the date of its Results row.
e.g. `| A2 | Assignees never see new tasks | value | H ★C2 | — (decider) | query opened-within-48h | under 50 %, set 2026-10-06 | over 80 % | open |` -->
| id | belief | type | evidence now | importance | cheapest test | pass line, dated | result that would change the decision | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 <!-- REQUIRED:assumptions --> | spark's commits in a person's repository happen and are safe: the git strategy makes the repository, writes the ignore list first and keeps each brief write | feasibility | H ★C14 (scratch run not reproduced here), E ★C4, ★C15 | high D13 | a scratch walk (start, three brief writes, the ignore list first), then a read-only `git ls-files` count in the 9 repositories | set 2026-11-25 by D13: 3 of 3 brief writes print a kept line, and 0 tracked files match the ignore list in the scratch walk. The count in the 9 repositories is written down as the size of the problem | fewer than 3 kept lines, or any tracked file in the scratch walk that the list covers | open |
| A2 | the git strategy's take-back (git revert after the person's yes, D7) of any kept step (D9) gives the earlier content and never overwrites a person's uncommitted edit | feasibility | H, and E commands/idea.md:79 says a revert of an older brief commit after a later one conflicts | — (decider) | a 30-minute scratch spike: three kept writes, take back the newest, then an older one, then again with an edit of the person's present | proposed 2026-11-25, not set: 2 of 2 take-backs give the earlier content, a conflict is said in plain words, and with the person's edit present the edit is byte-identical after | a take-back that overwrites the person's edit, or a conflict with no plain words | open |
| A3 | a person wants an undo from spark beyond what Claude does with git | value | H, and D9 is the PO's wish, n = 1 | — (decider) | count each request to go back to an earlier state of a project file in the next two walks after slice 0 | proposed 2026-11-25, not set: at least 2 such requests in those 2 walks concern a decided record | 0 requests, so slice 1's take-back waits | open |
| A4 | after D3 and D4, every line of `rules.md` has one home, and a gadget session loads no team rule | usability | H ★C5, E ★C3 | — (decider) | a table of every line of `rules.md` (8219 bytes, modified 2026-11-25 15:35) with one home or "dropped", read by the PO, then `find` and a grep on the linked file | proposed 2026-11-25, not set: every line placed, 29 of 29 links resolve, 0 lines in the file a gadget session loads name a card, a lane, the hook or a PR | a line with two homes, or a broken link | open |
| A5 | a person with no git, or no git identity, reads the refusal and knows the one next step | usability | E scripts/spark/records/project_commit.py:82-85 refuses a missing identity | — (decider) | one start in a scratch home with `GIT_CONFIG_GLOBAL=/dev/null` | proposed 2026-11-25, not set: the write is done, exit 0, and the line names one step with no "HEAD", "sha" or "rebase" | a line in git's words, or a lost write | open |
| A6 | one kept step per decided record (D8) neither floods the history nor leaves the tree dirty | feasibility | H, and the refuter found no source for the synthesis's "12" ceiling and "1 s" | — (decider) | a replay of one fixture walk with a kept step after each decided record | proposed 2026-11-25, not set: at most one kept step per decision of the person, and a clean tree at the end | more steps than decisions, or a dirty tree | open |
| A7 | one exchangeable strategy (D5) serves every interface, and an area's line names neither git nor Claude (D11, D12) | feasibility | H ★C21, ★C24 | — (decider) | once the seam exists: one test with a Fake strategy and with git, and a grep of the area's output | proposed 2026-11-25, not set: both run with no change to the area, 0 lines of the area's output hold "git" or "Claude", and the CLI still commits in the 6 repositories where the brief's commit fires today | an area change per strategy, or the CLI stops committing | open |
| A8 | kept steps that land on a PR-flow `main` (p934-display2) are what the PO expects | viability | H `council/po-assistant.md` (PO-20 A4) | — (decider) | one account question to the PO (Q14) | proposed 2026-11-25, not set: the PO's answer, no number | "no", so the strategy needs a branch rule | open |

## Collection plan
<!-- One row per gap. e.g. `| Do assignees open new tasks? | Q2 | Lena, from analytics | one query | this week |` -->
| question | decision it blocks | who can answer | how | when |
| --- | --- | --- | --- | --- |
| Do spark's commits happen and stay safe (A1)? <!-- REQUIRED:collection --> | the build of slice 0 | spark-main, through a builder agent | the scratch walk and the read-only count, against D13's pass line | after the PO's yes to items.md |
| Which branch do kept steps go to (A8)? | Q14, the strategy's branch rule | the PO | one account question | before slice 1's plan |
| What do the 22 existing folders get? | Q15 | the PO | one question | before slice 0's plan |
| Which file do spark's own sessions load, and is the spark-rules worktree reused? | Q16, Q17 | the PO | two questions | before the rules split's plan |
| Does a take-back by git revert work for an older step (A2)? | slice 1 | spark-main, through a builder agent | a 30-minute scratch spike | after the PO sets A2's pass line |
| Does a person want an undo from spark (A3)? | slice 1's take-back | the PO, as a user (n = 1) | a count over two walks | the next two walks after slice 0 |

## Results
<!-- Filled on a return; may stay empty until then. One row per result: what was tested, what was seen (verbatim,
with its pointer), the pass line met or missed, what it changes. -->
| date | source and pointer | what was seen | pass line met or missed | what it changes |
| --- | --- | --- | --- | --- |

<!-- EXTEND:risks-sections -->
