# P1139: the page's parts-list write names the parts it kept, and the origin record is written: rows

Card: [P1139 #1674](https://github.com/xmejkal/spark/issues/1674). The PO's words on walk finding 14 of the P829 walk,
2026-11-25: "but we nedd to fix that". The plan had two council rounds and the PO's approval on 2026-11-25. The
reproduction ran on a scratch copy of the walk project before the plan. This file holds the acted, raised and rejected
findings only. 2026-11-25.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | a note from a refused parts-list write would replace the refusal's sentence in `data.line`, and a broken record gives a refused run a note | plan lens (Sonnet) and refuter (Opus), round 1 | acted | `answer_of` gives the notes only when the run ended ok. A guard test runs the real write, refused, with a broken record, and a mutation row proves it |
| 2 | four tests in `test_needs.py` assert exact notes lists that gain the new note | plan lens (Sonnet), round 1 | acted | each expected list gains the note, named in the commit |
| 3 | `test_entry_origin.py` pins "a save with no rows writes none" | plan lens (Sonnet), round 1 | acted | the test changes on the card's Done-when: a save with no rows writes a record that reads no rows |
| 4 | two run-request tests of the plan pass before the fix | plan lens (Sonnet), round 1 | acted | they are guards, and mutation rows prove them |
| 5 | docs say that the answer's note is the build's only, and that the record is written only for an entry spark wrote | plan lens (Sonnet) and refuter (Opus), round 1 | acted | flow.md, page.md, json.md, how-it-works.md, the comment on `RAN_NOTE_SAYS` and the docstring of `answer_of` |
| 6 | the plan's reason to keep a pick's notes off the page was false: the page's run gives no `page.html` note | plan refuter (Opus), round 1 | raised | P1180 [#1722](https://github.com/xmejkal/spark/issues/1722): a pick's notes on the page, filed on the PO's word |
| 7 | an entry spark wrote for a pick that is gone is kept and not picked too, and the page said nothing of it | plan refuter (Opus), round 1 | acted | one note per gone entry, in the words of its line |
| 8 | `tests.test_parts` runs `--requirements` | plan refuter (Opus), round 1 | acted | in the pre-push set |
| 9 | a note built from `GONE_LINE` keeps the line's two leading spaces | plan refuter (Opus), round 2 | acted | each note is its line constant stripped, and a mutation row proves it |
| 10 | each gone note repeats one item of `data.unexplained`, which an agent could count twice | plan refuter (Opus), round 2 | acted | json.md says to count the entries from `data.unexplained` |
| 11 | on the page a gone entry is named but cannot be removed there: the removal stays in the chat | plan refuter (Opus), round 2 | raised | a line on P1166 [#1703](https://github.com/xmejkal/spark/issues/1703), which covers a parts-list entry whose pick is gone |
| 12 | the first push stopped in the hook's rows check: the P877 row "the need of an entry is not said" found its anchor twice, because the gone note repeated the gone line's formatting | the hook | acted | one helper builds the kept and gone sentences for the lines and the notes. The P97 row "what is kept is not said" moves to the kept sentence |
| 13 | page.md said only the kept parts, while the note can also hold a gone entry and the origin record's notes | PR lens (Sonnet) and PR refuter (Opus) | acted | fixed |
| 14 | no test joined a kept and a gone note through `RunRequest` | PR lens (Sonnet) | acted | a test with the real write and a record that names a gone entry |
| 15 | after a `false` reply, the notes leave out the entries the person kept, and only the `kept as yours` line names them | PR refuter (Opus) | acted | json.md says so. The page sends no replies, so the page is not affected |
| 16 | the second push stopped after 623 s on `test_map`: map.md was stale after the new test imported `entry_origin` | the hook | acted | map.md written again with `tools/map.py --write` |
| 17 | flow.md's shorter `note` bullet no longer said that a parts-list write that did not end ok has no note | fix-commit refuter (Opus) | acted | the clause "only when ok" is back |
