# P936 PR 2: how-it-works.md's stage table is generated from the build's table: rows

Card: [P936 #1332](https://github.com/xmejkal/spark/issues/1332). A plan, then its check (the architecture lens and the
refuter on Opus), then a build to the checked plan. This file holds the acted, raised and rejected findings only.
2026-11-20.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the plan changed an existing test's sentence for an end marker of the other kind | plan check | acted | `WRONG_END_MESSAGE` stays; `WRONG_KIND_MESSAGE` names an end of the other kind, and `test_doc_blocks.py`'s existing tests are unedited |
| 2 | the schematic-notes ending's exit 1 is said on no other page, and the plan cut it | plan check | acted | the two lines before the block say a schematic note is a problem, so the run exits 1 though the board builds |
| 3 | at least seven rows anchor on the moved lines | plan check, refuter | acted | eight did (P481's five, P852's three), each anchored again on the same defect; `tools/mutate.py --anchors` refuses the same 20 rows as on main and no other |
| 4 | `pages_with_blocks` reads only pages that hold `spark:operation`, so a page with only a stages block is never checked | plan check, refuter | acted | it reads every marker word; `TheTreeTest` names how-it-works.md as it names commands/deploy.md, and a P936 row leaves the filter on `spark:operation` |
| 5 | `Operation.stages` should default to `()` as `data_keys` does | plan check | acted | `stages = ()`, "empty for an Operation that reports no stages" |
| 6 | three fields and two loaders in `BlockKind` are more than the job needs | plan check, architecture lens | acted | `BlockKind` holds the attribute and the render function; one table, `block_operations()`, the bench's and the build's together; `operations=` stays |
| 7 | `StageMarkdownTable` must escape a `\|` as the core's table does, with the same step | plan check | acted | `operation_help_table.table_cell`, which both Renderers call |
| 8 | the simulation's cell is near the 300-character limit | plan check | acted | the `stages.py` docstring says it holds 268 of 300 |
| 9 | "HelpTable" means a Markdown table in the core and `--help` text in the build | plan check, architecture lens | raised | a line on card [P937 #1333](https://github.com/xmejkal/spark/issues/1333) |
