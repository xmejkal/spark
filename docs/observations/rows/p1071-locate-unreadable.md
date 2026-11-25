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
| 6 | commands/build.md and commands/setup.md say "an install there fails too", which is false for a refused `also` path or a refused bundled file | the review, the lens (should-fix) | acted | fixed: both say "an install into a folder you cannot read fails too" |
| 7 | `_file_here`'s docstring does not say plainly when it raises and when it collects | the review, the lens (nit) | acted | fixed: "A refusal raises a ToolError (P1041) unless a list `refused` is given. Then it is not here, and its sentence goes in the list (P1071)." |
| 8 | `locate`'s docstring does not say what a caller with no list gets | the review, the lens (nit) | acted | fixed: it says that a caller with no list passes over such a place silently |
| 9 | the new mode-0 tests fail when run as root, because root reads a folder of mode 0 | the review, the refuter (note) | acted | fixed: `ALookupSparkCannotReadTest` skips when `os.geteuid() == 0`, as tests/test_brief.py does |
| 10 | json.md:342, the `tool_missing` row, should also name the refused place in its "the sentence says what to install or fix" clause | the review, the refuter | raised | [P1083 #1590](https://github.com/xmejkal/spark/issues/1590), which changes those rows; json.md is held by #1579 and #1580, so this PR does not touch it |
| 11 | the refused places are joined with "; " after the install hint, which reads oddly after a hint that ends in punctuation | the review, the lens (nit) | rejected | dropped because today's install hints end with no punctuation, so "; " reads as one list |
