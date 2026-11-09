# P714 (hook half): the push hook runs the story's tests: rows

Card: [P714 #963](https://github.com/xmejkal/spark/issues/963).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | The selection did not always fail toward more tests: documents outside `docs/`, the converter, package files, scripts named only by golden helpers, tests that import a changed test | plan refuter, round 1 | acted | each is a row of the table in `tools/story_tests.py`, with a test |
| 2 | A named test that does not exist fails the run | plan refuter, round 1 | acted | `select` keeps only names in the tree |
| 3 | A push of another branch from main shows no change, because the gate measures `HEAD` | plan refuter, round 1 | acted | an empty diff is the quick run. P106 stays open: the gate does not measure the ref pushed |
| 4 | "A changed test names itself" is false for 89 of 108 test files | plan refuter, round 2 | acted | a changed test that exists selects itself |
| 5 | The stem `build` selected 51 tests for `commands/build.md` | plan refuter, round 2 | acted | a command page matches its own path |
| 6 | `tests/mutations/**` selecting `test_mutate` had a false reason | plan refuter, round 2 | acted | it selects none |
| 7 | Tree-walking tests outside the always list: `test_store`, `test_boards`, `test_grant`, `test_fab`, `test_board_look`, `test_check_all`, `test_parts` | plan refuter, round 2 | raised | they run when a file names them and at a sweep |
| 8 | The always list costs too much | implementation | closed | 17 test files, about 38 s in an archive of main on 2026-11-09, under the plan's 60 s |
| 9 | The gate prints no name of a failing test | retro item on the card | raised | run the failing modules by hand. A later card can print the names |
| 10 | A `@whole_repository` marker in place of the table | plan reviewer | rejected | it touches 19 test files, and one table has a test that counts its names |
| 11 | Rename "story run" to "changed run" | plan reviewer | rejected | the PO's rule says "test the story" |
| 12 | One full run on this branch | plan reviewer | rejected | the PO's rule makes it a sweep. A planted defect replaced it |
| 13 | A mention in an always-run test removed the doubt: a planted bug in `board_rules` passed the story run while `test_boards` failed | PR refuter | acted | a file that only `ALWAYS_RUN_TESTS` name runs the quick run. So `firmware_codes`, `pyproject.toml` and some `SKILL.md` files also run it |
| 14 | Three tests could not fail: a package file, `--full` given a story, a renamed file | PR refuter | acted | each has a test and a mutation row |
| 15 | A selected test that cannot compile gave a line with no reason | PR refuter | acted | the gate quotes the runner's last line. It failed closed before and after |
| 16 | The run's name was built in three places, and `changed_files` and the defaulted fields served one state | PR reviewer | acted | `StoryTests.run_word`, and `scope()` is None for the quick run |
