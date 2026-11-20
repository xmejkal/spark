# P852 PR 1: the build's stages come from one table: rows

Card: [P852 #1216](https://github.com/xmejkal/spark/issues/1216). Two plan rounds (a planning agent, then the
architecture lens and the refuter on Opus) and council 1 (D1 to D5, delegated), then a build to the plan. This file
holds the acted, raised and rejected findings only. 2026-11-20.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | round 1 listed 14 of the 29 `Stage(` sites in `build_service.py` | plan refuter, round 2 | acted | all 36 sites in the three modules end through `ok`, `ended` or `stopped_by`; the rewritten guard in `test_check_spine` finds no `Stage(` call in `scripts/` outside `stages.py` |
| 2 | the stage names had four more readers: `kept_files.py`'s literals `"build"` and `"simulation"` and its `REQUIREMENTS_STAGE`, and `phase_readers.py`'s `BUILD_STAGE` and `SIMULATION_STAGE` | plan refuter, round 2 | acted | they read `BUILD.name`, `SIMULATION.name` and `REQUIREMENTS.name`; the four constants are gone |
| 3 | the goldens reach about 8 of the 36 sites, so they cannot prove the move byte-equal alone | plan refuter, round 2 | acted | `test_build_service.EachEndingSaysWhatItSaidBeforeTheStageTableTest` and one unwired-diagram test pin the other templates; committed first, green on the old code, and unedited since. The goldens took no accept |
| 4 | about 18 rows anchor on the moved code | plan refuter, round 2 | acted | 27 did, the name readers' 7 among them; each anchored again on the same defect, and `tools/mutate.py --anchors` refuses the same 20 rows as on main and no other |
| 5 | an ending that no call site uses would still show in `--help` | plan refuter, round 2 | acted | `test_stages.TheTableTest.test_each_ending_is_named_and_a_call_site_ends_a_stage_with_it` |
| 6 | `code or stop.code` gives None in silence when a call site forgets `code=` | plan round 1, attack | acted | council D3: `stopped_by(found)` takes the design error's code, no `code=` keyword exists, and `ended` raises ValueError for an ending that is neither skipped nor coded |
| 7 | a literal `%` in a message breaks the fill | plan round 1, attack; council D5 | acted | every message is filled with `%`; `test_stages.EachMessageIsFilledWithPercentTest` fills each ending once, and a value too few, one too many and a lone `%` raise |
| 8 | the old guard parses the `Stage(` calls the build moves, so it fails at the commit that moves the first site | build | acted | the guard is rewritten in the commit that moves the sites, the plan's commits 3 and 4 in one, so every commit is green; its oracle `CODES_IN_ORDER` is unchanged |
| 9 | the role table's Renderer cell has no room for `StageHelpTable` (300 characters) | build | acted | the build area's paragraph names `StageHelpTable`, `StageDefinition` and `StageEnding`; the Value row names the two Values |
| 10 | `board_emitter.SCHEMATIC_STAGE` and `FOOTPRINT_STAGE` spell two names the table holds too | build | acted | P852 PR 3 on #1216 (the plan's later step: board_emitter's names from the table); `STAGE_NAMED[refused.stage]` raises KeyError if they part |
| 11 | a skip has no code, so the help says its message with each value as `…` | build | acted | P852 PR 3 on #1216 gives the two real skips their codes, a JSON contract change that waits for the PO |
