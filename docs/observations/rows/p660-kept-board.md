# P660: a kept board.tsx whose traces join other pins than this build's is named: rows

Card: [P660 #886](https://github.com/xmejkal/spark/issues/886), found on the P581 bench (rows file
`spark-walks/p581-sound-joystick/p581-rows.md`, row 7). Size S, in auto mode: plan council (lens Sonnet, refuter Opus)
in two rounds, then one lens and the refuter on the PR. This file holds the acted, raised and rejected findings only
(rules.md), with the build's own rows. 2026-11-15.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | a kept board.tsx keeps the old pins after the pin map changes, and only "left alone" is said | card | acted | `kept_files._traces_compared` adds a `traces differ` entry after the `left alone` one, naming each trace on each side; on P581's kept board it names the 10 moved signals |
| 2 | "a second run builds the old board" (bench row 7) | plan council round 1 (refuter) | rejected | no script reads the kept board.tsx; every build emits its own in the workdir (`build_service.py:286`, `board_engine.py:96`). The harm is by hand: wiring from it, `tsci dev`, `npx --no tsci build board.tsx` |
| 3 | the card asks "the build stops", but the build is right and dist/ is not the kept file | plan council round 1 (refuter) | acted | the exit and `status` stay, as `drawing differs`' do; the entry tells the person not to wire or build from the file. A comment on the card and the PR say it departs from the title |
| 4 | the why promised that dist/ and breadboard.md follow this build, which is false after a build that did not finish | plan council round 1 (lens, refuter) | acted | the why names only "the board this build made from the requirements" |
| 5 | after a `--keep` build that did not finish, the earlier dist/ stays, so check_all reads an older board (P581's dist/ holds the screen alone) | plan council round 1 (refuter) | raised | card [P816 #1168](https://github.com/xmejkal/spark/issues/1168) |
| 6 | a hand-kept board writes traces as template literals (the smart bin), which a regex would list as false differences | plan council round 1 (refuter) | acted | such a file gets one `traces not compared` entry with the count |
| 7 | a commented-out trace counted as a trace | plan council round 1 (refuter) | acted | `/* */` and `//` comments are stripped first |
| 8 | a hand-kept board can list every trace; the line needs a cap | plan council round 1 (lens) | acted | 10 a side and "and N more" on stderr; --json lists all |
| 9 | a new module for 15 lines needs the architecture list and an area page | plan council round 1 (lens) | acted | the logic is private functions in `kept_files.py` |
| 10 | names: `only_yours` and `only_built` were two words for one side | plan council round 1 (lens) | acted | `only_in_kept` and `only_in_build` |
| 11 | a stale footprint .tsx needs a card too | plan council round 1 (lens) | rejected | a footprint changes only with the board record; the kept FireBeetle2Esp32S3.tsx equals a fresh emit (refuter) |
| 12 | the entry needs a `code` (no magic strings) | plan council round 1 (refuter) | rejected | the entry has one kind, and `did` is a constant (`TRACES_DIFFER`), not English |
| 13 | docs: commands/build.md:164, never-assume §5, commands.md, journey/build.md were missing from the plan | plan council round 1 (refuter) | acted | each says the `traces differ` line |
