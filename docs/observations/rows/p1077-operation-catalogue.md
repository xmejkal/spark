# P1077: one Operation catalogue above the areas, read by DescribeOperations (P793 piece 4): rows

Card: [P1077 #1581](https://github.com/xmejkal/spark/issues/1581). The plan was written on main 0a2ffdf5 and had the plan
council for an S card: the architecture lens (Opus) and the refuter (Opus) in round 1, and the refuter (Opus) in round 2,
whose amendments A to E won over the plan. A "row" in the last column is a row of
`tests/mutations/p1077-operation-catalogue.json`, counted from 1. T1 to T11 are the plan's tests.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | No one list holds spark's 50 Operations: 48 sit in seven area tables, and `research-part` and `disallow-direct-flashing` in none | the card | acted | `scripts/spark/operation_catalogue.py`: `TABLES`, `CATALOGUE` and `NETWORK`. The two strays each get a table (research_operations.py, bench's table). T1, T2. Rows 1, 2, 4 |
| 2 | The research op is `research-part`, not `research` | round 1, refuter 1 | acted | `NETWORK` is `("sources", "fetch", "find-documents", "research-part")`. T4, T5 and T10 name it through `research_part.SCRIPT`. Row 3 |
| 3 | D5 turns test_core's describe test red | round 1, lens M1 and refuter 2 | acted | the test changes on purpose: the toy Fetch's `dry_run` is False, and Quiet's `flag` is None |
| 4 | Write the construction contract down | round 1, lens S1 | acted | the module's docstring and the names page's sentence; T3 builds every entry with no argument. Row 5 |
| 5 | `measure.imports_of` misses a deep import, so the core guard misses `from spark.flow.guide import x` | round 1, lens S2 | acted | T9 reads full dotted paths, with a planted tree. The fix of `TheCoreImportsNoAreaTest` itself is raised in row 21 |
| 6 | Say "the Operation catalogue"; rename `catalog_epilog`, which lists Operations | round 1, lens S3 | acted | `operations_epilog` reuses `DescribeOperations`' lines and options, so `--help` and `--describe` cannot drift; `PARTS_CLI` names it. T11. Row 9 |
| 7 | Two comments promise piece 4 more than it does | round 1, lens S4; round 2, A | acted | run_request.py's comment calls `STEP_OPERATIONS` the page's allow-list (P1082 #1587); now_follow_up.py's names P1081 #1585 |
| 8 | One assertion that each op of `NETWORK` is guarded by test_routes' `network_lines()` | round 1, lens S5; round 2, C | acted | T10 matches `scripts/<script>` inside a line |
| 9 | D5's flag fallback is the frontend's shape | round 1, lens S6 | acted | T6 pins only `flag` None for `look`; the text line shows the op so that it never prints "None". Row 6 |
| 10 | `MAY_READ` must match the tests' reads exactly | round 1, refuter 4 | acted | five entries; `test_every_reason_is_still_needed` stays green |
| 11 | Seven network operations, not eight | round 1, refuter 6 | acted | agents.md names all seven: `--fetch`, `--sources`, `--find-documents`, `research.py`, `tools.py --install` and `--on`, `check_vendor_pins.py`. T5 |
| 12 | `dry_run: bool(words)` is false for 7 entries, and `"--" + op` for 17 | plan | acted | both read the Operation's own arguments; parts.py's `--help`, `--describe` and `--describe --json` are the same, byte for byte. T6. Rows 6, 7 |
| 13 | S3: 11 Operations declare no `data_keys` | plan | acted | T7 holds them as a list that only shrinks |
| 14 | DropNeed has no sentence for a frontend to list | plan | acted | `DropNeed.summary`. T3. Row 5 |
| 15 | The doc pages' blocks read bench's and build's tables only | plan | acted | `block_operations()` returns the Operation catalogue. T8. Row 8 |
| 16 | T5 looked for the flags in backticks, which the new wording does not write | round 2, B | acted | T5 matches each name as a whole word in the one paragraph that says "reach the network" |
| 17 | The construction contract's "None for the real one" is false for register-project | round 2, D | acted | the docstring says a keyword with a harmless default |
| 18 | Piece 5 moves the journey CLIs onto the core; tools.py's `--install` and `--on` then join `NETWORK` | plan, out 1 | raised | destination: P793 #1105, piece 5 |
| 19 | The MCP server and S2's consent gates: a `NETWORK` tool asks the person first | plan, out 2 | raised | destination: P417 #545, piece 8 |
| 20 | Fill the `data_keys` of the 11, one real-answer test each | plan, out 3 | raised | destination: P937 #1333, piece 7 |
| 21 | `TheCoreImportsNoAreaTest` misses a deep import | plan, out 8 | raised | destination: P1080 #1584 |
| 22 | Which script runs an op is in three places | plan, out 9 | raised | destination: P1081 #1585 |
| 23 | The end of `STEP_OPERATIONS`, the page's allow-list | plan, out 5; round 2, A | raised | destination: P1082 #1587 |
| 24 | `--describe` on grant.py, bench.py and flow.py, with `flag` from the frontend | plan, out 4 | raised | destination: P793 #1105, piece 7 |
| 25 | The ops become one namespace, the MCP tool names | plan, out 10 | raised | destination: P417 #545, piece 8 |
| 26 | `DropNeedFlag` is an Operation in a CLI script; a later prune moves it beside `DropNeed`, after a fix of `--needs-drop` | plan, out 6 | raised | destination: P793 #1105, a prune of parts.py |
| 27 | check_vendor_pins.py's network call has no Operation | plan, out 7 | rejected | dropped because the finding's choice 3 keeps the inner tool where it is until a fix touches it |
| 28 | The text line's `one["flag"] or one["op"]` has no test | the review of #1589, refuter 1 | acted | test_core's describe test pins the toy Quiet's line, `  quiet              says nothing`. Row 10 |
| 29 | Row 1's name says test_routes T10 catches the research table left out | the review of #1589, refuter 2 | rejected | the refuter is right that T10 cannot catch it: `NETWORK` shrinks with the mutant. The name no longer claims it |
| 30 | The construction contract says a frontend that runs an entry needs nothing else, but it hands the area's outside builder | the review of #1589, lens should-fix 1 | acted | the docstring says so. The builder per table, keyed by the package of `TABLES`, is raised: destination P417 #545 |
| 31 | Two tests hold "the core imports no area": T9's `imported_modules` and `TheCoreImportsNoAreaTest` | the review of #1589, lens should-fix 2 | raised | destination: P1080 #1584, one test for the rule |
| 32 | T9 skips a relative import; T1 does not check that a table's classes live in its package; `"dry_run"` is a bare word; two paragraphs had a long line | the review of #1589, lens nits | acted | T9 reports a relative import as a finding (planted). T1 checks each class's `__module__` against its package. `DRY_RUN_DEST` sits beside `OPERATION_LINE`. AGENTS.md and agents.md reflowed with the same line count |
| 33 | The lens approves after fixes. The refuter says merge after fixes (1,165 tests OK with main merged, parts.py byte for byte, all 50 entries build, no import cycle) | the review of #1589 | acted | the fixes above, in one commit after the merge of origin/main |
