# P771 the temperature flag follows its note: rows

Card: [P771 #1062](https://github.com/xmejkal/spark/issues/1062), chore, XS, store data, under P735. Plan
`~/.claude/plans/p771-temperature-flag.md`. Rows 1 and 2 are the plan refuter (Opus), 3 the implementer, 4 to 6 the PR refuter (Opus). 2026-11-12.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | write through `parts.py --fact-set` with a dry run, not a hand edit | plan refuter | rejected | the dry run writes the irrigation project's copy and refreshes the shelf from it (row 3). The card keeps the irrigation copy untouched, so the shelf copy is edited as in P745 and P769, with `--validate` after |
| 2 | `why_it_matters` names where the 150 C junction figure comes from | plan refuter | acted | "HM70P04K.PDF, page 1" |
| 3 | the shelf copy follows its home in the irrigation project (`based_on`, §5.5), and P745, P769 and P771 edited the shelf only: a write on the part would undo all three | implementer | closed | [P775 #1070](https://github.com/xmejkal/spark/issues/1070), in Idea for the PO's choice — P776: tracked by #1070 (open), P745 #1021 (closed), P769 #1060 (closed), P771 #1062 (closed), P775 #1070 (open) |
| 4 | the PR's change, quotes and `--fact-set` claim | PR refuter (Opus) | closed | reproduced: only the one fact changed, both quotes match their pages, the dry run names the irrigation copy and "would refresh the shelf copy" |
| 5 | the `next:` hint of `--unverified` suggests the `--fact-set` that would undo the shelf's changes | PR refuter (Opus) | acted | said in P775 #1070 |
| 6 | the shelf copy's `based_on.digest` (d49211…) does not match the irrigation file's sha256 (60e9…), and nobody checked whether a digest is compared | PR refuter (Opus) | closed | for P775's decision — P776: tracked by P775 #1070 (open) |
