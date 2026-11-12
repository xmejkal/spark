# P726 PR 3: the eight payload handlers of `parts.py` run on `run_cli`, and `parts.py` becomes a dispatcher: rows

Card: [P726 #989](https://github.com/xmejkal/spark/issues/989), chore, under #94 (v0.13, one core). Plan
`~/.claude/plans/p726-payload-operations.md`. The PO-assistant and tech-lead council (Fable, 2026-11-12 14:00) decided the
seam and the final shape; this file holds the acted, raised and rejected findings only (rules.md, 2026-11-12). 2026-11-12.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | a loaded payload in the flag's value breaks `PartOperation.answer_refusal`'s join (a crash envelope instead of a problem) | plan lens | acted | the subject joins the str tokens alone; the subject of `--function-set x in.json` is `x` (named) |
| 2 | `sys.stdin` in `core/operation.py` breaks rule X2; the stdin read belongs to the CLI adapter | plan lens | acted | `cli.load_payloads(operation, values, stdin)`, `stdin` injected |
| 3 | the two unreadable-payload goldens print the sentence alone; the plan's usage path and added fix change their bytes | plan lens, plan refuter | acted | a could-not-run result with the diagnostics line `<prog>: <sentence>`, no fix |
| 4 | `--describe --json` has readers: test_routes (the word `network`, `options`: the permission gate), test_needs (`data`), test_parts | plan lens, plan refuter | acted | today's effect words and order, `options` derived, `data` gone (the PO confirms), the tests named |
| 5 | a tuple kind breaks every reader of `.kind`; a `payload` index on `Argument` is smaller | plan lens | acted | `Argument.payload` |
| 6 | `DropNeed` renders the plain envelope and prints nothing on a text refusal, so a flag translation does not keep today's answer | plan refuter | acted | `DropNeedFlag(AnswerOperation)` in parts.py runs `DropNeed`, as the handler does today; no translation |
| 7 | `summary` from the docstring couples an MCP description to prose | plan lens | rejected | `Operation.summary`, optional, the flag's help first |
| 8 | the registry keeps the name `OPERATIONS` (map.py, test_self_confirmation read `parts.OPERATIONS`) | plan lens | acted | |
| 9 | the describe route's bad-argument fix must name `--describe` (test_parts.py:2150) | plan lens | acted | `HelpText.bad_argument_fix` |
| 10 | `vendors.py` says one word for two things (sellers are shops); `change_lines.py` holds an Answer builder; `names_your_entries` is shared by two Operations | plan lens | acted | `brief_choices.py`, `write_answers.py` with `names_your_entries` |
| 11 | the eight have 13 goldens, all text, not 16 with three JSON; 5 mutation rows sit on goal_handlers.py | plan lens, plan refuter | acted | the plan's counts |
| 12 | the describe words must print in a fixed order (`network`, `writes`, `deletes`): `fetch`'s effects tuple is `(READS, WRITES, FETCHES)` and its golden says `[network, writes]`; the registry must keep the `list-boards` filter | plan refuter 2 | acted | the plan |
| 13 | `load_payloads` must branch on `nargs` (a str for a one-value flag, a list else) and skip a None; `INPUT_UNREADABLE` needs its `codes.CODES` row; tools/map.py reads `parts.OPERATIONS` with `itemgetter(0)` | plan refuter 2 | acted | the plan |
| 14 | `--json`'s help in `--describe` becomes the core's sentence ("print one envelope on stdout ...") | plan refuter 2 | acted | named for the PO |
| 15 | `DescribeOperations.run` instantiated every registry class, itself included, which needs the registry | build | acted | the describe entry uses the running instance |
| 16 | `DropNeedFlag` built its outside with no reporter (`build_outside_world` reports through it) | build | acted | `Reporter()`, as the handler gave |
| 17 | a `--passed-over` file holding `null` read as the flag left out, so a pick with junk reasons would write | build (test_needs) | acted | the Argument's default is its own object `NO_REASONS`; `load_payloads` skips a value that is the default |
| 18 | `run_cli` grew to 44 lines (R1) and a helper took six parameters (R3); `sys.stdin` in a helper broke X2 | build (test_architecture) | acted | `_reporter_and_privacy` and `_unreadable_payload`; the stdin read stays in `run_cli` |
| 19 | V1: the payload refusal's template was a module constant, not a literal | build (test_architecture) | acted | the literal in the raise |
| 20 | `--describe` was `required`, so `parts.py --ne P` said "required: --describe"; the describe route's parser lists no other flag, so `parts.py --help` named nothing | build (test_parts, test_docs) | acted | `--describe` not required: `parts.py` alone lists the operations (exit 0); the describe route's HelpText epilog lists every operation and option, so `--help` and the docs checker see them |
| 21 | `--pro` is `PromoteRecord`'s own ambiguity (`--promote`, `--project`), `--ne` is the describe parser's unrecognized argument | build | acted | the test says both |
| 22 | tests patched `parts.store` and read `parts.CodedMessageError`, `parts._say`, `parts._parser`, `parts._read_json_input`; `test_needs` read the gone `data` column | build | acted | `store` and `CodedMessageError` imported where used; `say_through_the_core` drives `run_cli` with a test Operation (test_drawer imports it); the describe test reflects over the registry; the `data` assertions go |
| 23 | 70 rows re-aimed by the retarget script, 32 by hand (`args.` and the method indentation), 5 dropped as duplicates of PR 1 rows or of a column that left (`_say` no-lines, the surrogate, `--describe`'s data keys, the lock, the negative --from), 3 new; `--anchors` over the 262 tables: every anchor present, once | build | acted | tests/mutations |
| 24 | the story's 16 modules 1231 OK; the 13 goldens of the eight byte-equal, parts-describe-ok included; ruff clean | build | verified | /tmp/p3-story.txt |
| 25 | `--ne x` is the describe parser's "unrecognized arguments", not an ambiguity; the docstring and the PR body said otherwise | PR lens | acted | reworded |
| 26 | in text mode a bad flag lost the fix sentence (the usage alone) | PR lens | acted | `run_cli` appends the CLI's `bad_argument_fix` to the usage line when the CLI gives one |
| 27 | `--describe --json`: `options` order changed, `--json`'s text changed, and each operation's `arguments` gained its own bool flag (`list: boolean`) | PR lens | acted | the selector flag leaves `arguments` (an MCP caller never passes it); the order and the text are named for the PO |
| 28 | the `data` keys column left `--describe` and json.md never held the keys, so an agent loses them | PR lens | acted | `Operation.data_keys` on every parts.py Operation, next to the code that builds the data; `--describe` prints it as before, and the drift test (test_needs) compares it with a real answer again |
| 29 | stale `_say` mentions in tests and docstrings; test_architecture's class docstring names the old CLI functions | PR lens | acted | |
| 30 | `DropNeedFlag` is a class in the CLI script; move it beside `DropNeed` and name it by the Adapter row | PR lens | rejected | the flag shape is the CLI's own (an Adapter at the edge), and `DropNeed` already holds the name `needs-drop` in the idea table: two classes with one op name cannot share a table; the name stays until a second shape needs a row |
| 31 | `ORDER` duplicates the registry and `.get` hides a name missing from a table | PR lens | acted | `[name]` fails at import; a test asserts `set(ORDER)` equals the tables' names plus `needs-drop` and `describe` |
| 32 | the options aggregation exists twice (`catalog_epilog`, `DescribeOperations.run`); `effects_of` names a module function and the Operation method | PR lens | acted | `options_of(registry)` and `effect_words_of` in describe_operations, used by both |
| 33 | names: `NO_REASONS` is `--passed-over`'s default; `_reporter_and_privacy` returns the reverse order; `LINE` is generic; the dests mix a noun with `x_and_y` pairs | PR lens | acted | `NO_PASSED_OVER`, `_privacy_and_reporter`, `OPERATION_LINE`; the dest rule: a pair is `x_and_y`, a one-value flag a noun (`items`) |
| 34 | `load_payloads` copies a list it then mutates in place | PR lens | acted | the copy goes |
| 35 | the new row "a loaded payload enters the subject" had no catching test (the two goldens print no subject) | PR refuter (Fable) | acted | `test_a_part_refusal_on_a_payload_flag_names_the_part_alone` |
| 36 | in text mode every argparse error of the eight lost the describe fix; `--describe --json`'s `options` order changed; the rest of the 23 runs match or are named | PR refuter (Fable) | acted | the text usage line carries the CLI's fix again; the order is named for the PO; stdin `-`, the 13 goldens, the anchors (3156 in 262), the import edges and the size pin hold |
