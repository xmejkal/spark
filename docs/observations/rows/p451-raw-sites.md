# P451: the raw raise sites pass their values to ValueMessageError, and the V1 baseline empties

Findings of P451 (#606), 2026-10-31, Prague, built on main 00a410b6. Counts taken on this head, `-B`, own TMPDIR.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The V1 baseline holds 49 sites in 9 files, unchanged since #614 and #613 | plan | verified | `python3 tools/measure.py --rules` on 00a410b6: `design.py` 22, `boards.py` 8, `needs.py` 8, `flash_image.py` 4, `drawer.py` 2, `parts.py` 2, and 1 each in `check_all.py`, `deploy_record_store.py`, `image_evidence.py`. After: no V1 entry |
| 2 | `RulesError` already inherits `ValueMessageError`; only `PartError` was raw | plan council | verified | `PartError(ValueMessageError)` with its 7 raises moved in commit 1, `:273` through `PartError.of_lines`, `:264` keeps its own `\n` in the template |
| 3 | `design.py:338` caught `(PartError, ValueError, OSError)` in one except | plan | acted | split: `PartError` through `DesignError.of_error`, `ValueError` and `OSError` through `"%s", broken` |
| 4 | The plan's `drawer.py:131` handling, "two templates in a conditional", would keep V1 counting it | plan | acted | V1 reads the first argument; a conditional there is no string constant. Two `if` statements with one raise each, both templates are constants |
| 5 | `drawer.py:239` (a `parts._problem` call) is `:252` and already one line | card | verified | the value is `json.dumps(values["is"])`, which escapes a newline and a surrogate. Left as it is |
| 6 | `tools.off_sentence` and `tools.entry_problem` hold raw values | card | acted | the three returns of `off_sentence` and the install-line return of `entry_problem` use `flat_line`. The status row prints through `flat_line` already; the sentence also reaches `step["problem"]` |
| 7 | `image_evidence.py` returns and raises `CANNOT_CHECK_MESSAGE % (...)` | plan | acted | `flat_line(CANNOT_CHECK_MESSAGE, ...)` at the two returns, `ToolProblem("%s", flat_line(...))` at the raise. Rows 2 and 3 of `p436-tool-missing.json` re-anchored |
| 8 | A nested `ToolProblem` of several lines collapses to one line inside `flat_line` at the three `image_evidence.py` sites | build | raised | only a board error with problem lines reaches there (`flash_image.board_build`); the lines now read as one line with `?` between them. Later, if a person asks: take the lines apart with `of_error` as `flash_image.py` does |
| 9 | `flash_image.py:95` wraps a `BoardError` of several lines | plan | acted | `of_lines([prefix + first] + rest)` from `str(cannot).split("\n")`, so the problem lines stay lines |
| 10 | The plan's test reads `needs.FILE` | build | acted | `tests/test_self_confirmation.py` refuses a test that reads the code's own constant; the test writes `.spark/needs.json` as a literal |
| 11 | A first push of commit 4 failed the hook on `ruff` (an unused import in `tests/test_tools.py`) | hook | acted | import cut; the hook's own output named only "FAILED (failures=1)", the line came from `ruff check .` |
| 12 | The plan's mutation row for V1 expected the zero test to catch `seen[name] += 1` -> `pass` | plan | acted | with an empty baseline the zero test sees nothing either way; the planted-tree V1 test (`test_v1_a_call_of_a_value_message_error_or_a_subclass_with_a_template_that_is_no_constant`) is the catcher, named in the table |
| 13 | `--anchors` refused 106 rows on main and 123 on the branch before the fix | build | acted | 17 older rows re-anchored (their `find` held the old `%`); after: 106 on both, the refused sets are equal (`diff` empty). The P444 row "cut at 160" is renamed "cut at 255" (the cap since #605) |
| 14 | P444 row 26 (pickle cannot rebuild `LookStop`) and row 33 (`IntEnum` under `%d`) | P444 | raised | stay raised: no code pickles an error, no site passes an `IntEnum` |
| 15 | P444 row 14 (messages built before the raise escape V1) | P444 | acted | `off_sentence` and `entry_problem` (row 6); V1 still does not see `msg = ...; raise E(msg)` or an alias, named in `docs/guide/developing.md` |
| 16 | New tests fail on main | build | verified | each commit's new tests failed on a `git stash` of `scripts/` (4, 5, 3 and 4 failing) and passed on the branch |
