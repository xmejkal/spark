# P919: `bench.py show`, each board on USB with its deploys, its kept projects and its grants: rows

Card: [P919 #1301](https://github.com/xmejkal/spark/issues/1301), a story, PR #1304. New logic: one lens on Sonnet and
one refuter on Opus read the branch. The refuter's verdict: stands with fixes. It planted 41 faults by hand and the
tests caught 27, and it applied the PR's 19 mutation rows by hand and the tests caught 19. This file holds the acted,
raised and rejected findings only (rules.md). 2026-11-18.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | a `known-boards/` place that cannot be listed, or that is a file, reads as "kept for no project" with exit 0 | the refuter, reproduced | acted | fixed: `read_all` names the place as unreadable, so `kept_for` is `null` and the exit is 2. Two tests |
| 2 | 14 hand mutants escape, for example a grant time with no zone read as live, and the wrong file named for a bad live grant | the refuter | acted | fixed: a test for each, and 11 new mutation rows |
| 3 | the empty-folder test passes only on a host that has `mpremote` | the lens | acted | fixed: the test reads the shared tools list and runs with its own found tool |
| 4 | the grant states `no_zone` and `not_a_grant` from invalid times, the count line for two boards and the text of a live grant have no test | the lens | acted | fixed: tests in `TheFixRoundTest` |
| 5 | three sentences repeat sentences that `outcomes` and `board_codes` already hold | the lens | acted | fixed: `outcomes.NOT_CHECKED_MESSAGE` and `board_codes.CODES` are used. Two own sentences stay, because the code's sentence says "for this project" or "last deploy" |
| 6 | the sentence of `cannot_tell_board` said that spark read none of the board's store records, and it reads the kept boards and the live grant | the builder, in the fix round | acted | fixed: the sentence ends after "by its USB serial" |
| 7 | `to_dict` spells the part names again, `_board` does four jobs, and `identify` reuses `usb_key_to_keep` for another question | the lens | acted | fixed: the constants are the keys, `_deploys` is its own method, and `known_board.serial_trusted` names the rule, with a test that both give one answer |
| 8 | the grant line reads "live: live until" | the lens and the builder | acted | fixed: the text says "holds until". The JSON's state stays `live` |
| 9 | `journey/bench.md` says that two clones look like one board and that a board spark cannot tell shows its port only | the lens | acted | fixed: "are named alike", and "its port and product, with its store parts not checked" |
| 10 | `agents/bench.md` leaves out `store_problem` and the two spellings `not_checked` and `not-checked` | the lens | acted | fixed |
| 11 | the times print in the stored ISO form and not as the plan's "08:04 CET", `read_deploys` also returns the board id, and the JSON keys are pinned in `tests/test_bench_show.py` | the lens | acted | the PR's text names the three departures from the plan |
| 12 | the last-deploy line is not in the column of the other lines | the lens | rejected | dropped because the look prints the same line, and the plan reuses the look's words |
| 13 | P919 needs its own line in `scrum/STORY_MAP.md` | the lens | rejected | dropped because the card's slice is "team tools", the line it stands on |
| 14 | "runs only `mpremote devs`" stands on four pages | the lens | rejected | dropped because each page says what its script does in one sentence, and the keys and codes stand on one page only |
| 15 | `bench.py`'s verb table copies `flow.py`'s, and the deploy record is read by two readers | the lens | rejected | dropped because the plan chose both: the verb table as `flow.py`, and `read_last_deploy` unchanged for its mutation rows |
| 16 | a board with no serial is asked for a live grant under the name `none` | the lens | rejected | dropped because `grant.py --check` asks the same way, and the board's deploy grant is not checked |
