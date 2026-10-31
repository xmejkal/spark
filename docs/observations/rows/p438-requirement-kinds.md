# P438: a requirements file of the wrong kind is refused with the field named

Findings of P438 (#583), 2026-10-31, Prague, built on main b9156270 (includes P451 and P454+P455). Plan: two council rounds and a coordinator change.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | A `pin` that is a list crashes with `TypeError: unhashable type: 'list'` | card #583 | acted | refused in `design.read` as `signals[0].pin is list`; test in `tests/test_design.py`, `test_emit_board.py`, `test_check_spine.py` |
| 2 | `"signals": 5` is a traceback, exit 1, from both mains | card | acted | `signals is int; write a list of signals`, exit 2 |
| 3 | A signal that is not an object | card | rejected | already refused as "signals[0] needs a `name`" |
| 4 | A `rules.json` folder is read as no rules | card | acted | `rules_in` asks `exists()`; `fab.read_rules` refuses the folder; owned by P438, not P455 |
| 5 | `emit_board.read_inputs` must refuse it in both callers | card | rejected | both callers already turn a `DesignError` into exit 2; no change |
| 6 | `signals: "abc"` and `{"a":1}` were refused with a wrong sentence ("signals[0] needs a `name`") | plan | acted | now `signals is str` / `dict` |
| 7 | `signals: 0` and `{}` passed silently | plan | acted | now refused; the PR says so |
| 8 | `pin: null`, `false`, `0`, `""` were silently no pin | plan | acted | a pin must be a non-empty string: `0`, `false`, `4`, `true` are refused by kind, `""` as an empty name |
| 9 | The P432 crash test used `pin: ["D0"]` as its crash input | plan | acted | switched to `"bus": ["i2c"]` (same `TypeError` from emit_board) |
| 10 | The plan said agents.md lists the requirements-kind crash among the exit 1 crashes | plan | rejected | the list holds no such crash on this base; the exit 2 paragraph gets one new line instead |
| 11 | A `bus` as a list is the same crash (`bus: 5` is already refused) | plan | raised (LATER) | a card; `parts` entries of the wrong kind are not checked here either |
| 12 | A FIFO at `.spark/rules.json` would hang `read_text` now that `exists()` is true (`is_file()` gave {}) | plan | raised (LATER) | narrow; a card if it ever matters |
