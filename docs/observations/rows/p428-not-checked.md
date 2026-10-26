# P428: one "not checked" shape, findings rows

Findings of P428 (2026-10-26, Prague), slice OC4 of refactor plan v2. From the plan council.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The three words are pinned as literals, so `VOCABULARY` in `tests/test_self_confirmation.py` stays | council | acted | the words are serialized (goldens, JSON `state`), so tests write `"recorded"`, `"none-recorded"` and `"not-checked"` and do not import them |
| 2 | Readers use `import outcomes` and `outcomes.RECORDED`, not a `from` import | council | acted | `board_facts`, `image_evidence` and `sim_project` import the module. `board_facts` imported no `outcomes` before. `tests/test_board_facts.py` asserts it keeps none of the three names |
| 3 | `ScenarioSteps.why` must be read, or it is dead | council | acted | `image_evidence.caveats` says `not checked: <why>: run its scenario again to count them`. A log with no counts line has no `why`, and says the old words, "the passed run's log does not count its steps" |
| 4 | The state is lossy through the log | council | acted | `line()` prints "not read" for NONE_RECORDED and NOT_CHECKED, and `from_log` reads NOT_CHECKED back. Said in the rule's comment and pinned by `test_the_line_round_trips_through_a_log_header` |
| 5 | The rule needs a test | council | acted | `READERS` in `tests/test_outcomes.py`: for `read_last_deploy`, `from_log` and `from_text`, a missing, a malformed and a good input, the states as literals, and no raise. The rule's comment points at it |
| 6 | Words in the rule comment | council | acted | NOT_CHECKED goes into an envelope's `unchecked` list. For scenario text, "recorded" means "read". Three phrasings stay outside the template and are named: "last deploy not checked: %s" (`board_look.py`, `board_envelope.py`) and "spark did not read its record of this board: %s" (`LastDeploy.in_question`) |
| 7 | The council named `board_facts.py:134` as a phrasing outside the template | build | rejected | line 134 is `LastDeploy.line`, which says exactly "not checked: %s", so it uses the template (the plan, step 1). The third phrasing outside the template is `in_question`, line 143, which is named in the rule instead |
| 8 | A keyless step leaves partial counts | build | acted | the plan kept them. NOT_CHECKED now has empty counts, as the rule says: "its own fields are empty". Nothing read the partial counts |
| 9 | `tests/test_imports.py` LEAVES gains "outcomes" | build | acted | the plan says so. It is a guard and does not fail on main, where `outcomes.py` already imports only `json` |
| 10 | Waiting readers | build | raised | `boards.read_simulated_part` (P397), `breadboard_keep.EarlierDiagram.read` and `breadboard_changes.WiringRecord.read` (wave 6) keep their own shapes. `project_image.read_run_logs` and `firmware_platform.record_of` refuse by design. Named in the rule's comment |
| 11 | The mutation run | mutation | raised | `tests/mutations/p428-not-checked.json` has 6 rows. Each was planted alone in a copy and the changed test modules went red for it (the whole table was not run). `--anchors` refuses the same 105 rows as main |
