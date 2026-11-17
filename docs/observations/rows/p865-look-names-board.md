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
| 13 | `deploy.py`'s own look restarts any one board before the token is compared (`deploy_service.py:93`) | plan, section 8 | raised | a card, filed by the coordinator before the merge |
| 14 | `grant.py` reads the board before its question (`board_grant.py:234`, `:240-241`) | plan, section 8 | raised | a card, filed by the coordinator before the merge |
| 15 | `reach.py` connects to whichever board is on USB (`reach_board.py:83-90`) | plan, section 8 | raised | a card, filed by the coordinator before the merge |
| 16 | the board doctor's console read can restart a board with no question (`look_at_board.py`'s DETAILS) | plan, section 8 | raised | a card, filed by the coordinator before the merge |
| 17 | the look's old `mac` line and `data.mac` still print the full MAC | plan, section 8 | raised | a card, filed by the coordinator before the merge |
| 18 | the replies file's name, `research-replies.json`, is research's, and the look's file is the agent's own | plan, section 8 | raised | a card, filed by the coordinator before the merge |
| 19 | a port that comes back late (walk 2 row 5), and one read between the look and the deploy (walk 3 row 14) | plan, section 8, from the card's first comment | raised | a card, filed by the coordinator before the merge |
| 20 | a moved or copied project leaves an orphan record in `known-boards/` | plan, section 8 | raised | a card, filed by the coordinator before the merge |
| 21 | an unlisted alias of a listed port (`/dev/tty.*` for a listed `/dev/cu.*`) reads as before, with no question | plan council, round 2 S6 | raised | a card, filed by the coordinator before the merge |
| 22 | the last-deploy line does not say that it is spark's own record and that a flash outside spark is not seen (walk 2 row 6) | plan council, round 2 S9 | raised | a card, filed by the coordinator before the merge |
| 23 | the CH340 `--port` path (no serial) reads with no question, as the deploy does | plan council, round 2 S9 | raised | a card, filed by the coordinator before the merge, with the deploy's card |
