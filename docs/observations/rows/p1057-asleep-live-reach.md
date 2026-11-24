# P1057 slice 1: live.py and reach.py give the asleep fix on a no-board stop: rows

Card: [P1057 #1554](https://github.com/xmejkal/spark/issues/1554). The plan was written on main 0a249b31 and split the
card in two PRs (D1). This is PR 1. PR 2 is P1057 slice 2 with [P1055 #1552](https://github.com/xmejkal/spark/issues/1552),
after the held PRs that touch `json.md`, `scripts.md` and `board_envelope.py`. The plan check on PR 1 was the refuter
(Opus). A "row" in the last column is a row of `tests/mutations/p1057-asleep-live-reach.json`, counted from 1.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | live.py and reach.py give the cable advice on a no-board stop when firmware/ calls deepsleep | the card | acted | both pass `stops.undoctored(SCRIPT)` to `stop_result`, as grant.py and bench.py record do. `ASleepingBoardTest` in test_live and test_reach. Rows 1, 5 |
| 2 | A port that spark picked must never get "the port you named" | the card | acted | live.py passes the port the person named (`named`), never the picked one. reach.py's LookStopError comes only from `require_one_board`, before spark picks a port. `test_a_picked_port_that_left_usb_keeps_its_own_words`. Rows 2, 3 |
| 3 | live's `--json` stop line keeps the cable sentence as `why` while `next[0].why` points to "the fix" | plan check A | acted | `why` is the stop Finding's sentence, `no board found.` beside the asleep fix and unchanged without it. Row 4 |
| 4 | reach's comment "port is still the named one or None" is false after a ToolError from `make_console_probe` | plan check B | acted | the comment says that a LookStopError comes only from `require_one_board` |
| 5 | The test's firmware writes `import machine` first, so the call is at main.py:2 | plan check C | acted | both `ASleepingBoardTest.setUp`s |
| 6 | A new test class that subclasses LiveScriptTest or ReachScriptTest runs every old test again with a deepsleep firmware, and two old stop tests then see the fix as a second line | the build | acted | the helpers move to `LiveCase` and `ReachCase`, and the old test classes subclass them. No assertion changed |
| 7 | A picked port that leaves USB (live's grant check, or the doctor after a failed exec) gets no asleep fix; it needs its own opening in `board_envelope.py` (D2, D3) | plan | raised | destination: P1057 #1554 (slice 2) |
| 8 | live.py's own doctor inside `LiveTryService` keeps its plug_in step (P1049 row 12) | plan | raised | destination: P1057 #1554 (slice 2) |
| 9 | `json.md` rows 336 and 337 and `scripts.md` line 131 still say that live.py and reach.py give no asleep fix; live's `next` look step names "the fix", which its line does not hold yet (D9) | plan | raised | destination: P1055 #1552. Both pages are in held PRs, so this PR does not touch them |
| 10 | The stop's list of the ports that mpremote sees, and a Linux `/dev/serial/by-id` path (P1056 rows 4 and 5) | plan D7 | raised | destination: a new card. They change `board_look.require_one_board`, which every bench script shares, and are not about deep sleep |
| 11 | reach.py's no-board stop prints no stdout line under `--json` | plan D4 | rejected | its other stops work the same way (replies.md); the fix is its last stderr line. `test_no_board_gives_no_board_found_and_the_asleep_fix_and_no_json_line` pins the empty stdout |
