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
| 7 | A7: the docs said "edited or not" in four more places | plan lens | acted | `commands.md`, `journey/build.md`, `never-assume.md` (and the link to its heading) and `json.md` say the four words |
| 8 | B1: the board was written before the previous version, so a failed copy left a half-changed pair | plan refuter, round 2 | acted | the new board is staged first, the previous version is kept, then one `os.replace`; two tests with a file and a directory in the way |
| 9 | B2: the plan's window test needed a mock | plan refuter, round 2 | acted | a test calls `kept_into` and `keep_build_record` and saves a person's bytes between them |
| 10 | B3: a `--keep` with no requirements file writes no record, so it could replace a board it would never record | plan refuter, round 2 | acted | `_kept` gives `kept_into` the map only when a requirements file is given and the folder is a project; one test |
| 11 | B4: `SPARK_WROTE` is dead after A1 | plan refuter, round 2 | acted | dropped; a person who restores spark's old bytes gets `replaced`, and the build page says so |
| 12 | B5: `json.md` and the heading in `never-assume.md` | plan refuter, round 2 | acted | `replaced` and `unchanged` in the `did` list, the keys `previous` and `sha256`, the new heading |
| 13 | B6: the card's note says `kept_into` gets the previous-version Store as a parameter | plan refuter, round 2 | acted | not followed (A5); the PR says so |
| 14 | the board is replaced and the dist copy then raises: the record keeps the old sha256 and later builds say left alone | plan refuter, round 2 (4a) | raised | a card, filed by the coordinator before the merge |
