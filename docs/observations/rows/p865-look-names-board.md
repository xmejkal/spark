# P865: the look names the board, asks once and remembers it: rows

Card: [P865 #1231](https://github.com/xmejkal/spark/issues/1231), a story. New logic: a plan council in two rounds (a
lens on Sonnet, the refuter on Fable), then the PR's review. This file holds the acted, raised and rejected findings
only (rules.md). 2026-11-17.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | a file in the project folder would keep the known board where one `git add .` publishes a MAC | plan council, round 1 | acted | the PO's D-b: the record is in the store's private `known-boards/`, and a test holds that the project's file list does not change |
| 2 | a yes in the chat must count, and must answer one look only | plan council, round 1 | acted | the PO's D-a: the agent's own file and `--replies`; the look sets every `look.` key back to null before it reads |
| 3 | a sixth parameter on `LookAtBoard.run` breaks the rule of five | plan council, rounds 1 and 2 | acted | `run(self, project, port, replies=None, *, outside, **evidence)`; the default keeps the callers that pass no replies |
| 4 | a short serial, `None` or an unlisted `--port` cannot be compared with a MAC | plan council, round 1 | acted | `tell` says `cannot_tell`; an empty key never matches |
| 5 | the existing tests and goldens read a board with no question today | plan council, round 1 | acted | each Case keeps its board in its store first; no existing command or golden changed |
| 6 | a bridge board's serial (CP2104 `01A2B3C4`) would be asked on every look | coordinator's rulings R1, R3 | acted | the record keeps `usb_key`, and a bridge's serial is trusted |
| 7 | a `--port` the look cannot identify must read as before | coordinator's ruling R2, round 2 S6 | acted | it reads with no question and keeps nothing; a test holds it |
| 8 | a firmware that sets one serial on every board (the s3lcd build) would make two boards one | plan council, round 2 S5 | acted | a serial on Espressif's own USB is trusted only when it starts with the MAC read; else every look asks, and the `why` says so |
| 9 | nothing may run before the BEGIN, and the gate prints nothing on stderr before a read's own error line | plan council, round 2 S3 | acted | the list, the gate and the read come after the BEGIN; a test holds it |
| 10 | a yes file must not answer the next look, and only `true` reads | plan council, round 2 S7 | acted | every `look.` key is cleared at the gate; `false` is `answered_no` and any other value leaves the question open |
| 11 | a store that refuses the write must not fail the look | plan council, round 2 S8 | acted | a refused write is a `not kept:` note on a report that stands |
| 12 | the store's places in how-it-works.md lack `known-boards/` | plan council, round 2 S9 | acted | the line names it, edited in place |
| 13 | `deploy.py`'s own look restarts any one board before the token is compared (`deploy_service.py:93`) | plan, section 8 | raised | card [P892 #1266](https://github.com/xmejkal/spark/issues/1266) |
| 14 | `grant.py` reads the board before its question (`board_grant.py:234`, `:240-241`) | plan, section 8 | raised | card [P892 #1266](https://github.com/xmejkal/spark/issues/1266) |
| 15 | `reach.py` connects to whichever board is on USB (`reach_board.py:83-90`) | plan, section 8 | raised | card [P892 #1266](https://github.com/xmejkal/spark/issues/1266) |
| 16 | the board doctor's console read can restart a board with no question (`look_at_board.py`'s DETAILS) | plan, section 8 | raised | card [P892 #1266](https://github.com/xmejkal/spark/issues/1266) |
| 17 | the look's old `mac` line and `data.mac` still print the full MAC | plan, section 8 | raised | card [P893 #1267](https://github.com/xmejkal/spark/issues/1267) |
| 18 | the replies file's name, `research-replies.json`, is research's, and the look's file is the agent's own | plan, section 8 | raised | a line on [P883 #1251](https://github.com/xmejkal/spark/issues/1251) |
| 19 | a port that comes back late (walk 2 row 5), and one read between the look and the deploy (walk 3 row 14) | plan, section 8, from the card's first comment | raised | card [P892 #1266](https://github.com/xmejkal/spark/issues/1266) (the deploy's part) |
| 20 | a moved or copied project leaves an orphan record in `known-boards/` | plan, section 8 | rejected | dropped because the record is small, private and harmless; the look asks once more |
| 21 | an unlisted alias of a listed port (`/dev/tty.*` for a listed `/dev/cu.*`) reads as before, with no question | plan council, round 2 S6 | acted | fixed: `board_look.node_name` reads `/dev/tty.<name>` as `/dev/cu.<name>`, so the alias is the listed row and is asked (R2) |
| 22 | the last-deploy line does not say that it is spark's own record and that a flash outside spark is not seen (walk 2 row 6) | plan council, round 2 S9 | raised | card [P892 #1266](https://github.com/xmejkal/spark/issues/1266) (the deploy's part) |
| 23 | the CH340 `--port` path (no serial) reads with no question, as the deploy does | plan council, round 2 S9 | raised | card [P892 #1266](https://github.com/xmejkal/spark/issues/1266) |
| 24 | a record kept while a fixed-serial firmware ran locks the project to that board: a yes reads another board and ends `other_board` for ever (H1) | PR refuter | acted | a yes to a `cannot_tell` board replaces the record when the read finds another MAC; the question says so first; a named `--port` with no yes still stops and names the way out |
| 25 | mutation row 13 was an equivalent mutant: the raise was swallowed (H2) | PR refuter | acted | the row now lists every board under `--port`; planted by hand, test 9 fails |
| 26 | the open question's next step dropped `--port` and the evidence flags (H3) | PR refuter | acted | `LookRun` carries them into `next[0].argv`; a test holds it |
| 27 | a read-only replies file and a record whose `at` is null crashed the look (H4) | PR refuter | acted | `RepliesStore.clear` raises `bad_argument`; `KnownBoardStore.read` needs `at` as a string; a test each |
| 28 | a yes given to a look that stopped before its gate stayed `true` (H5) | PR refuter | acted | every `look.` key is cleared right after BEGIN; a test holds it |
| 29 | nine right behaviours had no test: only `true` is a yes, all look keys and only look keys are cleared, the clear before the read, an empty MAC or key, a switch, a refused write, no token after `other_board`, the board record before the question, the private file (T1 to T9) | PR refuter | acted | a test and a mutation row each; the table has 29 rows |
| 30 | the words: the first-look `why` on a firmware serial, the no, the kept dates, the unreadable fix, `named()` for a bridge serial, the answer fix (W1 to W6) | PR lens | acted | each sentence says only what holds where it prints; the docs pages follow (D1) |
| 31 | `_key` was a private import across modules (K1) | PR lens | acted | `comparable_key`; measure's private imports are back at 5 |
| 32 | `PLACE` repeats the store's place name (K2) | PR lens | rejected | dropped because store.py has no constant per place; `DeployRecordStore` and `GrantStore` spell theirs the same way |
| 33 | the look's sentences live in two modules, `known_board.py` and `board_look.py` (K3) | PR lens | raised | card [P892 #1266](https://github.com/xmejkal/spark/issues/1266) |
| 34 | a firmware serial of 12 hex digits looks like a MAC, so its first look still says "asks no more for it" | the builder, W1 | raised | card [P892 #1266](https://github.com/xmejkal/spark/issues/1266) |
| 35 | `--port` skipped the question for a listed board whose firmware set its serial, so an agent could restart another session's board (N1) | the council on `_gate` | acted | a named port is read with no question only when the list does not hold it or shows it with no USB serial; every other board is asked; a test and a mutation row |
| 36 | a kept firmware-serial record and a board with a MAC-shaped serial: the `why` said that this board's firmware set its serial and that it asks every time, both false (R1) | PR refuter, last round | acted | the `why` says that the kept board's serial was set by its firmware; a test and a mutation row |
| 37 | after `other_board` on a port the list does not hold, the fix sent the person to a look without `--port`, where the board is not listed (R3) | PR refuter, last round | acted | that fix names the kept record to remove; the `--port` fix stays for a listed port with no serial |
| 38 | six right behaviours had no test: the yes used with `--port`, a bridge serial of 12 characters or more, `--ignore-older-runs` in the next step, the replace sentence only with a kept board and only on `cannot_tell`, the kept board's two bytes in the envelope (E1 to E6) | PR refuter, last round | acted | a test and a mutation row each; the table has 39 rows |
