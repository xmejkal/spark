# P1049: look.py --port, deploy.py --port, grant.py and bench.py record give slice 3's asleep fix: rows

Card: [P1049 #1539](https://github.com/xmejkal/spark/issues/1539), from a raised row of PR #1531 (P1022 slice 3). The
plan was written on main c1ec9f18. Round 1 was one lens (Sonnet) and the refuter (Opus), round 2 the refuter (Opus),
which cut the scope. A "row" in the last column is a row of `tests/mutations/p1049-asleep-stops.json`, counted from 1.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | look.py --port on a port not on USB gives board_not_read with the doctor's plug_in step, the cable advice of the 14:05 sighting again | the refuter of PR #1531, reproduced in the plan | acted | `board_envelope.stop_said` after the doctor: the asleep fix on the `next` line and as the fix. `test_a_named_port_off_usb_with_a_deepsleep_call_gets_the_asleep_fix_as_the_doctor_s_next_step`. Rows 8, 11 |
| 2 | deploy.py --port takes the same road (D1) | plan | acted | `refuse_at_look` calls `stop_said`. `TheNamedPortOffUsbTest` in test_deploy_known_board, which answers the board question first. Rows 10, 12, and the re-aimed p1022-asleep row |
| 3 | After the doctor, the asleep fix comes only for a named port (D2), and UNPARSED is no answer (D3) | plan | acted | `asleep_after_doctor`. Rows 3 to 5 |
| 4 | `data.doctor.next_step` stays plug_in; the fix is spark's advice (D4, round 1 D) | plan | acted | json.md's `board_not_read` row and scripts.md say: relay the `fix`, not the step. The test pins the fix unequal to the plug_in sentence |
| 5 | grant.py, live.py and reach.py --json carry no fix field | round 1 A, round 2 J | acted | grant.py's tests assert stderr; json.md claims no fix for them. Their JSON is P1055 #1552 |
| 6 | live.py and reach.py can say "the port you named" of a port spark picked; stop_result is at R3's limit | round 2 H | acted | scope cut: `stop_result` calls `stop_said` only when the script gives `doctor_for` (grant.py already does; bench.py record gives `stops.undoctored`). live.py and reach.py give none and keep today's words: P1057 #1554. Rows 1, 2, 9 |
| 7 | reach.py --port with an unlisted port crashes after a yes | round 2 I | raised | destination: P1056 #1553 |
| 8 | A plug_in result can carry an `if not` line, so `with_step` must place the step | round 1 B | rejected | IF_NOT_HELPED holds press_reset only (round 2 L); `with_step` says so in its docstring. Rows 6, 7 |
| 9 | bench.py record's stderr ends with "Nothing was written. fix what the line above says…" after the asleep fix | round 1 E, round 2 M | acted | kept as it is, by the plan's choice: the asleep fix is the second line, the AGAIN line stays last |
| 10 | `_finding` lets the fix the run said win over the doctor's step, with the anchored text kept | round 1 G | acted | `if doctor and not reached.get("fix")`. One p1022-asleep row re-aimed to `fix=fix`, the same meaning. Row 10 |
| 11 | A port that spark picked and the doctor then finds gone gets no asleep fix; it needs its own opening | plan, out of scope 1 | raised | destination: P1057 #1554 |
| 12 | live.py's own doctor inside `LiveTryService` keeps its plug_in step | plan, out of scope 2 | raised | destination: P1057 #1554 |
| 13 | test_look's comment said reach.py stops with port_not_listed; it asks the board question | plan | acted | the comment of `test_a_named_port_that_is_not_on_usb_opens_with_that_port_never_with_no_board` is corrected; no assertion changed |
