# P401: the yes before an erase names what spark last put on the board, findings rows

Findings from planning and building P401 (2026-10-24, Prague). The plan council ran two rounds: one Sonnet 5.5 lens over
code, tests, names and the views of a person and of Claude, then one Opus 5.5 refuter. The build checked each claim of the plan in the code.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The plan printed the verdict as "passed", a value from memory | round 1 | acted | the store keeps `ready seen`, and "passed" is the `simulation` field. The line prints the verdict as stored |
| 2 | A `DeployEntry` Value is planned beside the store code, and none exists | round 1 | acted | one Value, `LastDeploy`, replaces it. A round-trip test proves that `record_deploy` and the read agree |
| 3 | `say_in_local_zone` gives a zone to a stored time that has none | round 1 | acted | `tzinfo is None` is tested first. The time is printed as stored with "(zone not stored)". `test_a_time_with_no_zone_is_not_given_one` |
| 4 | A fifth golden, `deploy-could-not-run-no-terminal.json`, prints a look | round 1 | acted | accepted with the other four and the diff read: only the `last_deploy` key and the one line are new |
| 5 | The record is keyed like `record_deploy` writes it | round 1 | acted | `store.slug(mac)`. `test_another_board_s_record_is_not_this_board_s` has a near-miss MAC |
| 6 | The words claim more than the store holds | round 2 | acted | a flash that fails after the erase writes no record, and a flash outside spark leaves no trace. The words say "its store record" |
| 7 | A look with no MAC gives no token and never reaches the question | round 2 | acted | the no-MAC wording is tested at the Value and in the look. `test_a_board_whose_mac_was_not_read_gets_no_token_and_no_question` |
| 8 | The question test at `test_deploy_gate.py:152` needs no change | round 2 | verified | it asserts a substring that the new sentence keeps |
| 9 | The plan names `tests/test_board_facts.py` as an existing file | build check | acted | no such file existed. The build creates it. The `record_deploy` tests stay in `test_deploy_gate.py` |
| 10 | "Every fake report gains a `last_deploy`" | build check | rejected | the gate tests use real `LookReport` objects from `LookCase.look`. No fake report needed a change |
| 11 | The suite's scratch store gives "none in its store record" each run | build check | acted | false inside one process: the deploy tests record the look's MAC in the same store. `LookCase.setUp` gives each test a store of its own |
| 12 | Mutation anchors that name `LookReport` or the question follow the code | build check | rejected | `--anchors` refuses the same 7 rows in the three touched files before and after the change. None quotes the changed lines |
| 13 | The plan lists three states and the cases of a bad record | build check | acted | also a newest entry with a missing or non-string field, a file that cannot be opened, and a file nested 100000 deep. All are `not-checked` with one why |
| 14 | `board_facts` imports `board_grant`, which imports `board_look`, which now imports `board_facts` | build check | verified | the import works at the top of the module. No cycle fails |
| 15 | G27: the look's next step and the terminal line name `--port` even with one board on USB | Claude | acted | two sentences on `commands/deploy.md`. The golden `deploy-could-not-run-no-terminal.json` shows the `--port` in both |
