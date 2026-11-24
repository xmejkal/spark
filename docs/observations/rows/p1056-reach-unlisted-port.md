# P1056: reach.py --port with a port the list does not hold stops with port_not_listed: rows

Card: [P1056 #1553](https://github.com/xmejkal/spark/issues/1553). The plan was written on main 0a2ffdf5 and checked by
the refuter (Opus), with D1 = A, delegated and the PO's to change. This file holds the acted, raised and rejected
findings only (rules.md). A "row" in the last column is a row of `tests/mutations/p1056-reach-unlisted-port.json`.
2026-11-24.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | reach.py --port with a port that mpremote does not list asks the board question, and after a yes it crashes with `AttributeError` at reach_board.py:136 (`row.usb` on a `None` row) | the refuter of P1049's plan, round 2 | acted | `finder.require_one_board(SCRIPT, port)` in place of `find_listed`: the port stops with `port_not_listed` before the question, through `stop_result`. `test_8_reach_stops_a_port_the_list_does_not_hold_with_port_not_listed_also_after_a_yes`, red on main with the crash. Row 1 |
| 2 | D1: stop before the question (A), or guard `row.usb` and stop with `not_reached` after the yes (B) | plan | acted | A, delegated (auto mode), the PO's to change. It changes P892's plan decision ([P892's rows](p892-board-questions.md), row 15), which rested on the PO's decision 3 ("A board that spark cannot tell: all three ask on every run"). A applies his decision 3 as grant and live already do: a port the list does not hold is no board that spark cannot tell, but no board on the list. Two assertions of test_board_questions change with it, test 8 and test 16 |
| 3 | The plan said that A "reverses P892's decision 3"; the PO's decision 3 on #1266 is about a board that spark cannot tell, and the reach rule was the plan's | plan check A | acted | the PR, this file and the commits name P892's plan decision (rows row 15) |
| 4 | Under A, the stop gives no list of the ports that mpremote sees and no fix | plan check B | raised | destination: P1057 #1554 |
| 5 | Under A, a Linux /dev/serial/by-id path also stops with `port_not_listed`, because `mpremote devs` lists the device name | plan check B | raised | destination: P1057 #1554 |
| 6 | json.md's `port_not_listed` row says "a look", but the look reads a named port the list does not hold and never stops with this code | plan check C | acted | the row now names a grant, a live try, a reach and a `bench.py record` (`record_deploy.py` calls `require_one_board`), each checked in the code |
| 7 | test_look's comment says that reach.py asks the board question for a port the list does not hold | build | acted | the comment of `test_a_named_port_that_is_not_on_usb_opens_with_that_port_never_with_no_board` names reach.py beside grant.py, live.py and bench.py record; no assertion changed |
