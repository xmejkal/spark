# P874: the build replaces its own board.tsx and keeps one previous version: rows

Card: [P874 #1242](https://github.com/xmejkal/spark/issues/1242), a story. New logic: a plan check, a plan council (one
lens on Sonnet, the refuter on Fable, two rounds) and a review of the PR. This file holds the acted, raised and rejected
findings only (rules.md). 2026-11-17.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | A1: the record held the sha256 of the file on disk, so a person's save between the board write and the record write would match | plan refuter | acted | `kept_into` hashes the work folder's board and the entry carries it as `sha256`; the record reads that key, and a test saves a person's bytes in the gap |
| 2 | A2: an OSError of the replace reached `_kept` and turned the whole run into one `not kept` | plan refuter | acted | `_replaced` catches it and gives a `left alone` entry with the error; `dist/` is still kept |
| 3 | A3: a `board.tsx` that is a link could be replaced through the link | plan refuter | acted | `_spark_wrote` is false for a link; a test holds that the file outside is unchanged |
| 4 | A4: a rebuild of the same board put an identical copy over the last different previous version | plan lens, plan refuter, the coordinator | acted | a fourth word, `unchanged`: nothing is written and no copy is kept; a test builds A, A, B, B |
| 5 | A5: `previous` as a parameter and a suffix constant add code for no gain | plan lens | acted | `kept_into(workdir, destination, written=None)`; `.txt` is in `path_of`; `OWN_FILES` stays |
| 6 | A6: two tests pass on main today and the plan did not say so | plan lens, plan refuter | acted | they are named as regression pins in the PR, with a mutation row each |
| 7 | A7: the docs said "edited or not" in more places than the plan listed | plan lens | acted | `commands.md`, `journey/build.md`, `never-assume.md` (and the link to its heading) and `json.md` say the four words; the list was not complete, see row 22 |
| 8 | B1: the board was written before the previous version, so a failed copy left a half-changed pair | plan refuter, round 2 | acted | the new board is staged first, the previous version is kept, then one `os.replace`; two tests with a file and a directory in the way |
| 9 | B2: the plan's window test needed a mock | plan refuter, round 2 | acted | a test calls `kept_into` and `keep_build_record` and saves a person's bytes between them |
| 10 | B3: a `--keep` with no requirements file writes no record, so it could replace a board it would never record | plan refuter, round 2 | acted | `_kept` gives `kept_into` the map only when a requirements file is given and the folder is a project; one test |
| 11 | B4: `SPARK_WROTE` is dead after A1 | plan refuter, round 2 | acted | dropped; a person who restores spark's old bytes gets `replaced`, and the build page says so |
| 12 | B5: `json.md` and the heading in `never-assume.md` | plan refuter, round 2 | acted | `replaced` and `unchanged` in the `did` list, the keys `previous` and `sha256`, the new heading |
| 13 | B6: the card's note says `kept_into` gets the previous-version Store as a parameter | plan refuter, round 2 | acted | not followed (A5); the PR says so |
| 14 | the board is replaced and the dist copy then raises: the record keeps the old sha256 and later builds say left alone | plan refuter, round 2 (4a) | raised | P891 #1263 |
| 15 | PR review, round 1: a `board.tsx.new` that is a link is written through, a plain leftover is overwritten, and a person's read-only one is deleted by the cleanup (F1) | PR refuter | acted | the stage is created exclusively and without following a link (`StagedFile`), and only a stage this run made is removed; an existing name gives `left alone`; tests for a link and a leftover |
| 16 | the stage of the previous version is written through a link (F2) | PR refuter | acted | the same `StagedFile` makes it; a test with a link at `.spark/previous/board.tsx.txt.new` |
| 17 | the one previous version is lost when the swap fails (F3) | PR refuter | acted | both copies are staged, the board is swapped in, and only then is the previous version put in place; a failure removes this run's stages; a test locks the board with `chflags` |
| 18 | a build that did not finish replaces a good board (F4) | PR refuter | acted | `_kept` may replace only when the build stage ended `ok`; a test with a `could-not-run` build stage |
| 19 | a footprint recorded by a mutant that ignores `OWN_FILES` was not caught (F5) | PR refuter | acted | a test with a second `.tsx`: the record holds `board.tsx` only and the footprint is `left alone`; a mutation row |
| 20 | a record that is not JSON, and an unreadable board, were not caught by a test (F6, F8) | PR refuter | acted | a test for each, both pins that pass on main; a mutation row each |
| 21 | a stage left behind after a good replace was not caught (F7) | PR refuter | acted | the first replace test asserts no `*.new` is left, and the previous-version test lists one name; a mutation row |
| 22 | `docs/guide/journey/from-draft-to-order.md` said an existing `board.tsx` is never overwritten; the plan's list of docs was not complete (L1) | PR lens | acted | corrected; a search for `never overwritten`, `edited or not` and `regenerat` outside the archive found no other false claim |
| 23 | `never-assume.md` rule 5 had a body that was false for an unchanged board that spark wrote (L2) | PR lens | acted | the body says the next build replaces it and where the old one is |
| 24 | the word `unchanged` had two meanings in `build.md`; `left alone` was a bare literal; the new lines were not wrapped (L3, L4) | PR lens | acted | `LEFT_ALONE` in `kept_files.py`; the status "stays what it was"; the lines wrapped; the docs say a failed replace is `left alone` too; `sha256` is on a `.tsx` that spark wrote, replaced or found unchanged |
| 25 | a test name said "four words" and checked three phrases (L5) | PR lens | acted | renamed to say what it checks |
| 26 | the `why` of `traces differ` ("if you did not edit it, delete it to have it regenerated") may be false after the change (L6) | PR lens | acted | read: it is still true, also for a board left alone after a failed replace (spark cannot prove it wrote it, so deleting it is the way to get a new one); the text is left |
| 27 | a person's save in the window between the hash and the swap can be lost | PR refuter | rejected | dropped because it is inherent without a lock and the window is a few milliseconds |
| 28 | a dangling link at `board.tsx` is written through and said as `wrote` | PR refuter | rejected | dropped because main does the same today and this card does not change it |
