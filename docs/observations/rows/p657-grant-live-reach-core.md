# P657 grant, live and reach on the core (W4-3, S9, P383): rows

What the plan council's two rounds found, and what the build changed against the plan. Card:
[P657 #883](https://github.com/xmejkal/spark/issues/883). Plan: `~/.claude/plans/p657-grant-live-reach-core.md`.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | `main` normalizes `argv` first, because `"--check" in None` crashes | round 1, refuter MUST | acted | grant.py `main`, `operation_for` |
| 2 | `int` enters `JSON_TYPE_OF_KIND`, and `input_schema` lists `required` | round 1, lens MUST | acted | operation.py, tests in test_core.py and test_grant.py |
| 3 | Live's status comes from `board_live.exit_code`, so a failed reset stays exit 2 | round 1, lens MUST | acted | `RunLiveCode._findings`, test_live.py |
| 4 | A crash under a flat `--json` prints no stdout line | round 1, lens MUST | acted | json.md, agents.md, tests in test_core, test_reach, test_live, test_grant |
| 5 | `Argument` gains `choices` | round 1, lens | acted | cli.py `parser_for`, `--scope {live,deploy}` in the help |
| 6 | The mode pick is a named `operation_for(argv)` that takes a prefix of `--check` | round 1, lens and refuter | acted | grant.py, test_grant.py |
| 7 | IssueGrant uses `FlatJsonLine` too, so `--minutes 5 --json` is a usage line | round 1, refuter | acted | test_grant.py |
| 8 | `render_bad_argument` is part of the one Renderer contract, in the Renderer row | round 1, lens | acted | patterns-and-names.md |
| 9 | `refuse_consent` names `asks` | round 1, lens | acted | outside.py, test_core.py |
| 10 | Each Operation catches its stops inside `run`, with the classes named | round 1, refuter | acted | the four Operations; CheckGrant does not catch `GateClosedError` (the check cannot raise it) |
| 11 | The ready-seen fake hashes `<cwd>/firmware/<path>` and needs two scrub rules | round 1, refuter | acted | tests/fake_modules/mpremote, golden_bench.py `BOARD_LOG`, `FACTS_SHA`; the board path is `/main.py`, so the fake strips the slash |
| 12 | test_json_contracts moves in step 3 | round 1, refuter | acted | `test_grant_check` on `outside=` |
| 13 | test_core.py refuses `int` as an unknown kind: the test uses `float` | round 2, refuter MUST | acted | test_core.py |
| 14 | `required` only when a dest is required; `choices` give `enum` | round 2 | acted | `input_schema` |
| 15 | Every Finding code is a board_codes constant with its line in the agents docs | round 2 | acted | board_codes.py (11 new codes), json.md |
| 16 | The fixture's passed-run log holds the `file` lines | round 2 | acted | it names `/main.py`; the ready-seen golden passes three times |
| 17 | Plan claim wrong: `Operation.json_renderer = JsonEnvelope` in operation.py | build | acted | cli.py imports operation.py, so the class cannot import `JsonEnvelope`. The attribute is None for the envelope, and `run_cli` reads `operation.json_renderer or JsonEnvelope` |
| 18 | Plan claim wrong: `render_bad_argument(result, prog)` | build | acted | the envelope needs tool and op, so it is `(result, tool, op)` as `render` is |
| 19 | Plan claim wrong: the `guard_lines` in reach's diagnostics | build | acted | `run_cli` guards the stderr lines once, so the Operation keeps only the flattening of values; the P430 rows "without the guard" point at cli.py |
| 20 | Plan claim wrong: `--check --scope live` stays accepted | build | acted | CheckGrant has no `--scope`, so it is refused with the usage (named in the PR with the help split) |
| 21 | Steps 3 and 4 as two commits | build | acted | one commit: grant.py has two modes in one `main`, so the check alone cannot land |
| 22 | `fake_board.py` of about 60 lines | build | acted | the board lives in the fake mpremote and esptool (about 25 lines), no new module |
| 23 | New: `stops.py` (`reason_of`, `stop_result`) shared by the four Operations | build | acted | `reason_of` moved from deploy_image.py; `stop_result` has 5 parameters (R3) |
| 24 | New: moved test mock.patch (stdin, ButtonPlaces) | build | acted | a non-tty stdin given to the consent and a project folder with a board record; the T2 baseline falls |
| 25 | Duplicate codes: `board_live` and `board_codes` define RAISED, NOT_REACHED and the REFUSED_ codes twice; `RESET_FAILED` is "failed" in one and "reset_failed" in the other | review, refuter | acted | board_live takes its answer constants from board_codes; its reset state is `RESET_FAILED_STATE` (value "failed", printed); test_live loops over `EXIT_FOR_ANSWER` |
| 26 | Stale docs: wave4-plan `IssueGrant(grant_service=None)`, the effect words in patterns-and-names, reach "a script alone", json.md "write no `code`" and the `crash` row | review | acted | `platform_for=None`; one list of effects; one sentence for the four Operations; the flat line has no `code`, the Findings do; the crash row says grant, live and reach print no stdout line, exit 2 |
| 27 | `JsonEnvelope` and `FlatJsonLine` in cli.py, so `Operation.json_renderer` was None (row 17) | review | acted | they moved to `spark/core/renderers.py`; `json_renderer = JsonEnvelope` is the default and `or JsonEnvelope` is gone; row 17's limit no longer holds; the p657 row on `render_bad_argument` re-anchored |
| 28 | Op names `issue_grant` and `check_grant` against the kebab rule | review | acted | `issue-grant`, `check-grant`; one line in the names table (the op is the script's name, a script with two modes names its mode). No golden pins them; tests/test_look.py pinned the `OPERATIONS` keys and changed |
| 29 | Small: a shared `COULD_NOT_RUN_DATA` dict, `check` with no default, `TOOL_MISSING` for a missing probe, inline `# --- MVP ---` comments, re-exported `EXIT_*` with `# noqa`, the bench docstring, a long docstring sentence | review | acted | `dict(...)`; `check=True`; the code `no_probe` (board_codes, json.md); `# P430:` comments; scripts import the codes from `spark.core.outcomes`; docstring and run_cli reworded |
| 30 | Mutation tables: 3 identical rows on cli.py's diagnostics print, 3 on stops.py, the restart-notice row already in p423 and p507 | refuter | acted | one row per (file, find, replace) across the tables; p430 keeps one stops.py row, renamed for the shared path; four rows added to the p657 table |
| 31 | IssueGrant should declare WRITES | review | rejected | WRITES means a write to the board (operation.py); store writes get `place` and `path` in P488 #667 |
| 32 | Rename stops.py and a parameter object for `stop_result` | review | rejected | two callers of the shape, small |
| 33 | Move GRANT_SCRIPT's path out | review | rejected | deploy_image.py uses the same pattern |
| 34 | `operation=None` on look.py's main | review | rejected | out of scope for P657 |
| 35 | `parse_known_args` instead of `operation_for` | review | rejected | the council chose `operation_for` |
| 36 | Mutation run on the 153 rows of the changed files (17,608 s): 4 escaped, 3 refused | mutation | acted | the escapes: stop_result's port and project guards (3 p430 rows), which no test reached because every refusal's own message is flat since P444, and CheckGrant's shared stop data. tests/test_bench_stops.py gives each one a test with a raw value in the message |
| 37 | 3 refused rows: p242's stamp rows anchor on `find` in board_grant.py, which is gone on main too | mutation | raised | old rows, not this PR's; a card for stale tables beside P661 #889 |
| 38 | The run took 4.9 h, because `--for` on whole files pulls every old row on them | mutation | raised | learned rule: estimate about 2 min a row before a run |
