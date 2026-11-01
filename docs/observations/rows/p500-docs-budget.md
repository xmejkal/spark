# P500 docs budget: rows

What the plan claimed, and what its two council rounds changed. Card: #689.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | `doc_files` used `glob`, so a page in a guide sub-folder was skipped | plan (planner) | verified | `tools/check_docs.py` `doc_files`; now `rglob` |
| 2 | `broken_links` named only `path.name` | plan (planner) | verified | now names the path from the root; so do `problems()`'s prefix and `personal_paths` |
| 3 | Sizes today: README 181, agents 1036, commands 284, developing 650, how-it-works 277, journey 1582 | plan (planner) | verified | `BUDGETS` holds them |
| 4 | Lead: budgets at today's size for every page, the README too; no README edit in this card | council | acted | README.md untouched |
| 5 | Lead: no unused step or index budget constants; they come with P501 | council | acted | none added |
| 6 | Round 1 (Opus refuter): the rule follows `tests/test_architecture.py`: over budget fails, a budget for a gone page fails, a smaller page passes | council | acted | `over_budget`; tests for all three |
| 7 | Round 1: a budget set above a page's real size fails | older plan line | rejected | overridden: a smaller page passes, so no push is blocked when a page shrinks |
| 8 | Round 1: the cell rule would fail main, since agents.md has 4 cells over 300 characters (2276, 597, 379, 342) | council | acted | `CELL_LIMITS` per file: agents.md 2276 until P502 |
| 9 | Round 2 (Sonnet): every message names a page by its path from the root | council | acted | `_name`; tests assert the wording |
| 10 | Round 2: the messages are fixed text, and the tests assert them | council | acted | "has N lines, over its budget of B. Move text out or split the page, never raise the budget." |
| 11 | Pages with no entry get a default of 400, over-budget only | council | acted | `DEFAULT_BUDGET` |
| 12 | The gone-page message was not worded in the plan | build | raised | "has a budget but is not there. Remove its entry from BUDGETS." |
| 13 | Council targets (README 150, index 60, step 200) are not set here | council | raised | they arrive with P501, P502 and P504 |
| 14 | Mutation table: rglob back to glob; the comparison flipped; the cell limit raised | plan | acted | `tests/mutations/p500-docs-budget.json`; 3 planted, 3 caught; `--anchors` at 119 refused |
| 15 | A five-line paragraph in developing.md would have raised its 650-line budget | build | acted | the rule is one two-line bullet in the check list; one blank line saved in the section |
| 16 | T2 forbids `mock.patch.dict` on module tables | build | acted | `over_budget` and `long_cells` take the table as an argument |
| 17 | The cell message lets a reader find the cell | PR reviewer 1 | rejected | it named only the page; it now names the line and the fix ("Shorten it or move the text below the table"); a test with a fenced block before it |
| 18 | A cell limit for a page that is gone is flagged | PR reviewer 2 | acted | over_budget now also names a CELL_LIMITS entry for a missing page; test |
| 19 | An escaped pipe or an indented row is handled | PR reviewer 4, PR refuter 3 | acted | split on unescaped pipes, rows found after leading spaces; tests |
| 20 | Every reader of the guides sees sub-folders | PR refuter 2 | acted | tests/test_orphans.py (3 lines) and tests/test_routes.py (1 line) now rglob, before P501 splits journey.md |
| 21 | "These only go down" is enforced | PR refuter 5 | rejected | kept by review, as tests/test_architecture.py keeps its baseline; the comment and developing.md say so |
| 22 | developing.md keeps its old shape | PR refuter 4 | acted | the blank line before "Nothing mechanical" is back and the bullet names both defaults; its budget is its size after this PR (651), set in the same PR that brings the budgets |
| 23 | The names over_budget and long_cells are verb plus object | PR reviewer 3 | rejected | they match the older checks in the file (broken_links, missing_names); a rename of all of them is a later prune |
