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
| 16 | A stored time that the machine's zone cannot hold raised `OverflowError` in `line()` and `in_question()`, so it crashed the look and the question | PR review, PR refuter | verified, acted | caught with `ValueError`, said as stored. Two tests |
| 17 | A folder or a dangling link in the record's place read as "none in its store record" | PR refuter | verified, acted | only a path that is not there at all is `none-recorded`. A test for each |
| 18 | An empty stored time printed as a blank | PR refuter | acted | a blank field is `not-checked` |
| 19 | A `Z` time was printed raw on Python 3.10 | PR refuter | acted | read as `+00:00`, then said in the machine's zone |
| 20 | A project name with a newline added a fake line to the look | PR refuter | acted | characters that do not print as themselves show as `?` |
| 21 | `board_facts` imported `board_grant` for a time helper, which closed a cycle `board_facts -> board_grant -> board_look -> board_facts` | PR review | acted | `stamp` and `say_in_local_zone` moved to `scripts/zone_time.py`, which imports no spark module. Row 14's "no cycle fails" is now "no cycle" |
| 22 | Three look tests asserted a `+02:00` time, so they passed only in a zone at +02:00 on that date | PR review | acted | `LookCase.setUp` pins the zone with `fakes.pin_time_zone` |
| 23 | The deploy page said the line "says what spark last put on this board" and named the card id to the person | PR review | acted | it says what spark's store record names, and `not checked` names both causes |
| 24 | The journey guide listed the look's output without the last deploy | PR refuter | acted | one clause, marked as after its dated run |
