# P877: `--requirements` names an entry it wrote for a pick that is gone, and removes it on a yes: rows

Card: [P877 #1245](https://github.com/xmejkal/spark/issues/1245), a story. New logic: a plan check, a plan council of two
rounds (one lens on Sonnet, the refuter on Fable, who ran a stand-in in a scratch copy in round 2) and a review of the PR. This
file holds the acted and raised findings only (rules.md). 2026-11-17.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | A1: no run stops for this; a run with no yes writes as today, exits 0 and names each entry, with the key and a `next` step | plan council, round 1 | acted | `data.unexplained`, `data.remove_key`, `data.previous` are always emitted; `data.kept` is unchanged; the text line `kept, not from a pick` holds only the person's entries |
| 2 | A2: the yes is read from the replies file; nothing waits inside the store's lock | plan council, round 1 | acted | `--replies` on the Operation, read by `EntryRemoval` with `RepliesStore`; no `ASKS`; only the JSON `true` is a yes |
| 3 | A3: the key holds the file's bytes and the entries | plan council, round 1 | acted | 8 hex digits of the sha256 of the bytes and the canonical JSON of the entries |
| 4 | A4: a yes writes once, and keeps the previous version | plan council, round 1 | acted | `PreviousVersionFiles` stages the file before and commits it after the write; a failed stage says `left alone` and writes as today |
| 5 | A5, A6: a no, a dry run and a refused run | plan council, round 1 | acted | a no leaves the rows out of the record; a dry run and a refused run read and clear nothing |
| 6 | A7: the rows of a record that does not fit the file are not trusted | plan council, round 1 | acted | the record holds a hash, and rows are read only when it fits; a note says so |
| 7 | A8: the classes in a new module, no `StagedFile` move | plan council, round 1 | acted | `entry_origin`: `WrittenEntry`, `UnexplainedEntries`, `EntryOriginStore`, `EntryRemoval` (an Adapter) |
| 8 | A9: the existing tests, goldens and rows the card changes are named first | plan council, round 1 | acted | listed in the PR under "An existing test changed" and "Mutation rows re-anchored" |
| 9 | A10: the tests, with no "nothing is written" test, and a flow test that can fail | plan council, round 1 | acted | one test per Done-when line; the flow test reads `data.unexplained` before and after |
| 10 | A11: the docs | plan council, round 1 | acted | `commands/idea.md` and `build.md`, `how-it-works.md`, `json.md`, `replies.md`, `never-assume.md`, `journey/idea.md`, `patterns-and-names.md`, the `--help` |
| 11 | B1: the key printed fits the next run | plan council, round 2 | acted | the key is of the bytes the run leaves; a run checks a reply against the bytes it finds; the walk test pins it |
| 12 | B2: a reply for another key removes nothing and says so | plan council, round 2 | acted | one note with the key that fits now; the run exits 0 |
| 13 | B3: the hash is of the `parts` list, not of the bytes | plan council, round 2 | acted | a reformat or a key beside `parts` keeps the rows; a changed `parts` list makes every entry the person's (named in `never-assume.md`) |
| 14 | B4: one order for a yes | plan council, round 2 | acted | read and clear the reply, stage the previous version, write, commit the previous version, write the record last; the replies file that cannot be written stops the run with its own fix |
| 15 | B5: eight row files anchor in the two modules | plan council, round 2 | acted | `--anchors` on each; three rows of `p97-requirements-fix.json` re-anchored with the same meaning; the describe golden changes on the `--requirements` line only |
| 16 | B6: `build_answer` has 3 lines of room | plan council, round 2 | acted | `build_answer` is short; the old body is `_answer_of`, and the new logic is in `entry_origin` and two helpers |
| 17 | B7: Done-when 1 is the drop of a need | plan council, round 2 | acted | the test for the drop was missing from the first push and came in the review round (row 25); `test_a_re_pick_...` changes one text line |
| 18 | B8: an ok answer carries the `next` step | plan council, round 2 | acted | `outcomes.step(..., needs_person=True)` |
| 19 | B9: the yes is read from the replies file, not asked as an effect | plan council, round 2 | acted | the PR names it under "Departures from the card" |
| 20 | the staged write (`StagedFile`) lives in the build area and three areas use it | plan council | raised | a line on P891 #1263 |
| 21 | the look's gate and this card's yes both read replies their own way | plan council | raised | P892 #1266 |
| 22 | R1: a damaged record (bytes that are no text, or a folder at its path) stopped every real run, after the file was written | PR refuter | acted | the record's write never fails the run: one note, exit 0; two tests and a row |
| 23 | R2: the note of a yes that fits no key named the key over the bytes found, which fits no run | PR refuter | acted | the note holds `data.remove_key`; a test and a row |
| 24 | R4: a no was answered by asking again | PR lens | acted | after a no, one line `kept as yours: ... (you said no)`, `data.unexplained` is `[]`, no key, no step; two tests and a row |
| 25 | R3: no test dropped a need (Done-when 1) | PR refuter | acted | the test drops a need and compares the bytes of every file and of the replies file. It is a pin: it passed at once. A row (the need is not said) |
| 26 | F1: a person at a terminal was not told the simple way | PR lens | acted | a line after the named entries; a test and a row |
| 27 | F2: the `left alone` line printed an absolute path and said nothing of the spent yes | PR lens | acted | the entries by name, paths from the project, and that the yes is used up; two tests and a row |
| 28 | F3: the clear must touch only `requirements.` keys | PR lens | acted | a pin test (it passed at once) and a row |
| 29 | F4: a second removal replaces the one previous version | PR lens | acted | said in `commands/idea.md` |
| 30 | F5: `settle` meant two things | PR lens | acted | `UnexplainedEntries.without_removable`; `EntryRemoval.settle` keeps its name; no anchored line moved |
| 31 | D1 to D3: the idea page and `replies.md` give Claude the full rule, `json.md` has its own bullet, the PR body says the departures | PR lens | acted | docs and PR body |
