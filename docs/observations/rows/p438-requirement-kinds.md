# P438: a requirements file of the wrong kind is refused with the field named

Findings of P438 (#583), 2026-10-31, Prague, built on main b9156270 (includes P451 and P454+P455). Plan: two council rounds and a coordinator change.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | A `pin` that is a list crashes with `TypeError: unhashable type: 'list'` | card #583 | acted | refused in `design.read` as `signals[0].pin is a list`; test in `tests/test_design.py`, `test_emit_board.py`, `test_check_spine.py` |
| 2 | `"signals": 5` is a traceback, exit 1, from both mains | card | acted | `signals is a number; write a list of signals`, exit 2 |
| 3 | A signal that is not an object | card | rejected | already refused as "signals[0] needs a `name`" |
| 4 | A `rules.json` folder is read as no rules | card | acted | `rules_in` asks `exists()`; `fab.read_rules` refuses the folder; owned by P438, not P455 |
| 5 | `emit_board.read_inputs` must refuse it in both callers | card | rejected | both callers already turn a `DesignError` into exit 2; no change |
| 6 | `signals: "abc"` and `{"a":1}` were refused with a wrong sentence ("signals[0] needs a `name`") | plan | acted | now `signals is str` / `dict` |
| 7 | `signals: 0` and `{}` passed silently | plan | acted | now refused; the PR says so |
| 8 | `pin: false`, `0`, `""` were silently no pin | plan | acted | a pin must be a non-empty string: `0`, `false`, `4`, `true` are refused by kind, `""` as an empty name; `null` stays no pin, on purpose |
| 9 | The P432 crash test used `pin: ["D0"]` as its crash input | plan | acted | switched to `"bus": ["i2c"]` (same `TypeError` from emit_board) |
| 10 | The plan said agents.md lists the requirements-kind crash among the exit 1 crashes | plan | rejected | the list holds no such crash on this base; the exit 2 paragraph gets one new line instead |
| 11 | A `bus` that is not a string is the same crash (a list, and `"bus": {"a": 1}`, an unhashable dict; `bus: 5` is already refused) | plan | raised (LATER) | a card |
| 12 | A FIFO at `.spark/rules.json` would hang `read_text` now that `exists()` is true (`is_file()` gave {}) | plan | raised (LATER) | narrow; a card if it ever matters |
| 13 | `"parts": 5` is a traceback (exit 1) from `design.read`; `"parts": "led-red-5mm"` was walked letter by letter and refused with the wrong "available" sentence | refuter | acted | `parts is a number; write a list of part ids or {"part", "name"}` before any entry is walked, under `requirements`; tests in `test_design.py` and `test_check_spine.py`; mutation row |
| 14 | The kind in a refusal was a Python type name (`str`, `dict`, `int`) | refuter | acted | `design.JSON_WORDS`: text, an object, a list, a number, true or false, null |
| 15 | `agents.md` and `build.md` said a bad signals or pin stops "under schematic", the same as the rules folder | refuter | acted | signals, pin and parts are refused under `requirements`, only the rules folder under `schematic` |
