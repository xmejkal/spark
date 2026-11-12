# P771 the temperature flag follows its note: rows

Card: [P771 #1062](https://github.com/xmejkal/spark/issues/1062), chore, XS, store data, under P735. Plan
`~/.claude/plans/p771-temperature-flag.md`. Rows 1 and 2 are the plan refuter (Opus), 3 the implementer. 2026-11-12.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | write through `parts.py --fact-set` with a dry run, not a hand edit | plan refuter | rejected | the dry run writes the irrigation project's copy and refreshes the shelf from it (row 3). The card keeps the irrigation copy untouched, so the shelf copy is edited as in P745 and P769, with `--validate` after |
| 2 | `why_it_matters` names where the 150 C junction figure comes from | plan refuter | acted | "HM70P04K.PDF, page 1" |
| 3 | the shelf copy follows its home in the irrigation project (`based_on`, §5.5), and P745, P769 and P771 edited the shelf only: a write on the part would undo all three | implementer | raised | [P775 #1070](https://github.com/xmejkal/spark/issues/1070), in Idea for the PO's choice |
