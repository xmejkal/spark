# P1071: locate's three lookups pass over a place spark cannot read, and find names it: rows

Card: [P1071 #1571](https://github.com/xmejkal/spark/issues/1571). This file holds the acted, raised and rejected findings
only. The plan had one plan check, the refuter on Opus, and spark-main decided each item. The PR's review rows come after it.
2026-11-24.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `to_install` and `plan` call `locate(want, project)` with no list, so a refused place would raise `file_refused` there: `--status` would print the ok row and exit 2 with no "to install" line, and `--install tscircuit --dry-run` would say "cannot" though tsci is on PATH | the plan check, the refuter (A) | acted | fixed: `locate` makes its own list when it is given none, so every caller passes over a refused place; the downloads keep P1041's raise. Mutation row 4 |
| 2 | no test that `to_install` does not raise when the tool is on PATH and a place is refused; the child test does not pin an empty stderr or the "to install" line | the plan check, the refuter (B) | acted | fixed: the npm-on-PATH test asserts `to_install`, and the child test asserts stderr is empty and that tscircuit is in the "to install" line |
| 3 | json.md's `tool_missing` row is the look's and the deploy's, where the new tail never appears, and json.md is held by #1579 and #1580 | the plan check, the refuter (C) | acted | fixed: the line is in docs/guide/agents/firmware-codes.md (run_scenario), commands/setup.md and commands/build.md; json.md is unchanged |
| 4 | on main, the test of a later `also` path fails with a PermissionError, not a ToolError; the p82-1 row's bare anchor text occurs three times after the change | the plan check, the refuter (D) | acted | fixed: the PR says PermissionError; the p82-1 row anchors on `role or tool_name, tool_name,\n` and the hint line, once |
| 5 | with no PATH, tscircuit's need bun is missing first, so the board-engine row of the child test would be bun's sentence, not tsci's | the build | acted | fixed: the child's project file sets bun's exe to this Python, so the row is tsci's own |
