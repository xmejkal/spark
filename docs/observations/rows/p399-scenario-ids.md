# P399 PR 1: a wrong component id stops before a Wokwi run: rows

Card: [P399 #515](https://github.com/xmejkal/spark/issues/515). Rows 1 to 14 come from the plan check: a Sonnet reviewer, an Opus refuter, and the Opus refuter's second round.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | The brace-counting reader lost the kind of a flow step, because `from_text` strips the opening `{` | refuter, round 1 | acted | the reader was replaced |
| 2 | `PIN_ONLY` names `led1`, which the new `setUp` does not hold | refuter, round 1 | acted | it names `ledred5mm` |
| 3 | `golden_bench.py` writes `{}`, so `not checked` would reach the goldens | refuter, round 1 | acted | the fixture writes an empty parts list, and the goldens keep their bytes |
| 4 | `main` is at its ratchet of 21 lines, and the script may hold only `main` | refuter, round 1, then `test_architecture` | acted | `scenario_run.free_checks` holds the checks and returns the lines that `main` prints |
| 5 | Mutation anchors die in four tables | refuter, rounds 1 and 2 | acted | nine rows retargeted |
| 6 | A read-only `wokwi.toml` becomes a traceback if the write moves to `run()` | refuter, round 1 | acted in PR 2 | PR 2 catches `OSError` |
| 7 | `wait-serial: temp {part-id: ghost}` was read as an id | refuter, round 1 | acted | only the kinds that name a component are read |
| 8 | No test for `onboard_button` and `onboard_led` (P480) | refuter, round 1 | acted | test added |
| 9 | A regex reads a quoted name as an id, in flow form | refuter, round 2 | acted | the reader uses the step's own keys, through the code of `_name` |
| 10 | `_kind` splits on commas, so `"boot, ready"` loses its ready | refuter, round 2 | acted | the value comes from the unsplit text |
| 11 | `stamp` still needs `now()`, so removing the `datetime` key fails as NEW | refuter, round 2 | acted | the key stays |
| 12 | Move the ready-wait fixes to another card | reviewer | rejected | the card's 2026-10-24 council put them in PR 1, and both bugs reproduce |
| 13 | Use one regex in place of the own-keys reader | reviewer | rejected | round 2 showed that a regex refuses a good scenario |
| 14 | Names: `DiagramIds`, `has_ready_wait`, `write_image_name`, `steps_text` | reviewer | acted | renamed |
| 15 | The plan listed a block-scalar name as a reason for an unread step | implementation | closed | the own-keys reader never reads a name's body, so the reason is gone and the step keeps its id |
| 16 | `_kind` and the own-keys reader both found the kind | implementation | acted | `_kind` is gone, and the 122 older tests pass |
| 17 | P396's row 9: an old limits note stays | card comment | closed | `scripts/spark/build/kept_files.py:292` removes it |
| 18 | What wokwi-cli does with an unknown id | refuter | raised | finding out needs a paid run, and no paid run is allowed. The check is free either way |
| 19 | `part-id: my` with the next line going on is misread: a false exit 2 or a silent wrong id | PR refuter | acted | the step is unread, with a test |
| 20 | `- name: press [A` stopped counting a step that main counted | PR refuter | acted | a bracket counts only where a value starts it |
| 21 | `- &boot { wait-serial: "ready" }` got a second wait | PR refuter | acted | anchors and tags before a step are skipped |
| 22 | Two mutation rows described behaviour no test reached | PR refuter | acted | one row renamed, and tests added for both |
| 23 | `agents.md` said a line starts with `not checked:`, but it starts with the script's name | PR refuter | acted | it says "holds" |
| 24 | `free_checks` and `run()` both call `problem()` | PR reviewer | raised | the double call is older than this card; PR 2 moves the only write out of it |
| 25 | A `wait-serial` whose text holds `part-id` prints `not checked` | PR reviewer | rejected | the plan chose a harmless note over silence for a step of another kind |
| 26 | The module docstring had a broken wrap | PR reviewer | acted | reflowed |
