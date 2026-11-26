# P1140: after a hand edit of requirements.json, flow and the page say the file changed by hand: rows

Card: [P1140 #1675](https://github.com/xmejkal/spark/issues/1675). Found in the PO's P829 walk, 2026-11-25. The plan council ran on
2026-11-26, about 12:33 to 12:45 CET (one lens on Sonnet, the refuter on Opus). This file holds the acted, raised and rejected
findings only. 2026-11-26.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the card's "spark wrote no list before" is true of 15:43 (a file that came with the copy), not of the 15:50 hand edit, which came after spark's own write at 15:47 | the plan, from the diary | acted | the hand edit says "changed by hand"; a file with no record names no cause, on purpose |
| 2 | the guard tests repick `light`, but `parts/` holds one light, so the phase stays `ok` and the True case is never reached | the refuter, confirmed by a run | acted | the guards repick `brain=firebeetle2-esp32s3` and assert `stale` first (v2-1) |
| 3 | the fact is read twice in one `show`, and two places map the answer to words | the lens | acted | one table, `flow_codes.STALE_REQUIREMENTS`, maps True, False and None to (the phase line, the NOW sentence); the rule stays `EntryOriginStore.is_as_written`, called once by the phase reader and once by `guide.with_requirements_now` (v2-2) |
| 4 | an untouched file always gives True, through a second write, a reformat or `run_request` | the refuter | rejected | the risk does not hold: the hash is of canonical JSON, and every write goes through `settle` |
| 5 | a harmless hand edit (a new key) gives False while the phase stays `ok`, so a later repick says "changed by hand" until the next write | the refuter | acted | said in the PR as a risk: the file was changed by hand, so the line is true |
| 6 | Claude's own edit (`commands/init.md:51`, `commands/build.md:334`) also reads as "by hand" | the refuter | acted | the card's words stay; the PR says spark did not write the file, whoever did |
| 7 | five line numbers of the plan are off | the refuter | acted | the builder read each place before the edit |
| 8 | the re-anchored p1139 row's `replace` must keep the new `content_sha256` line | the refuter | acted | the row's find is the `mkdir` line plus the comment line after it, so the `record` line is not in it; `tools/mutate.py --anchors` passes and the row was run by hand |
| 9 | `parts_sha256()` now hashes the whole file, so its name misleads | the lens | acted | one comment line in `save`; no rename |
| 10 | a save that fails reads "changed by hand" on later runs | the lens | acted | `NOTE_UNWRITTEN` is pinned by `test_needs` and `test_run_request` already; named in the PR as the existing failure mode |
| 11 | the file with no record names no cause, and the walk folder shows the line only after one more write | the lens | acted | said in the PR; the real-folder check ran on a copy under scratch, with a write and a hand edit |
| 12 | the `test_needs.py` hash is of canonical JSON, not the file's bytes | the lens | acted | a comment in both assertions |
| 13 | the hand-edit NOW sentence is three sentences while P1135 asks for less text | the lens | raised | P1135 #1670: the PR names `tests/golden-design/flow-ok-page.txt` line 154 and the two button sentences |
| 14 | plan row 5 (`is_as_written(held) is False`) fits no code after v2-2, and its first rewrite (`and None`) left False as False, so no test went red | the builder, by a run | acted | the row replaces `is_as_written(held)][0]` with `is_as_written(held) or None][0]`, and a run by hand fails 2 tests |
