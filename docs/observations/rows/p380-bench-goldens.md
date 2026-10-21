# P380 goldens for the five bench CLIs: findings rows

Findings from planning and building P380 (2026-10-21, Prague). The plan council ran two rounds: a design reviewer on
Sonnet and the refuter on Opus, then a PO-assistant on Sonnet and a tech lead on Opus.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | A canned C6 flash id fails the S3 record, and an 8 MB S3 file on a C6 is a chip stop, not "flash differs" | refuter | acted | the fixture is the S3 project; `look-problems.json` uses `s3-flash-id-8mb.txt` |
| 2 | The 4 MB flash image cannot be checked in, because every install copies the repository | refuter | acted | `golden_bench.build_project` builds it at test time |
| 3 | `live` loads `boards/active.json` before any grant check | refuter | acted | `build_project` writes it |
| 4 | Firmware newer than the image adds a note, and a git checkout sets file times freely | refuter | acted | `build_project` makes the image the newest file |
| 5 | A bad-flag golden holds nothing, because argparse writes only to stderr | design reviewer | acted | cut |
| 6 | `reach` writes its could-not-run case only to stderr | tech lead | acted | cut; `check_golden` refuses an empty output |
| 7 | Without a token, deploy stops at "run look.py first", before the terminal check | tech lead | acted | the no-terminal Case takes look-ok's token |
| 8 | The image build gives one sha256 each run, so only the image half of the token needs a placeholder | tech lead | verified | the token prints as `5aed-<image>` |
| 9 | A stray `SPARK_ACCEPT` could rewrite goldens inside the push hook and pass | tech lead | acted | accept fails the test, and `run_script` drops the variable from the child |
| 10 | A child does not pick the scratch store, because it never imports unittest | Explore | acted | `run_script` sets `SPARK_HOME` to a store per Case |
| 11 | A fake package without `__init__.py` is a namespace package, and an installed mpremote wins over it | implementer | acted | each fake has an `__init__.py`; the first run had run the real mpremote |
| 12 | `reach --json` prints the moment of the run | refuter | acted | `golden_bench.MOMENT` replaces it with `<at>` |
| 13 | Ready seen, granted and ran need a faked board or clock | design reviewer, tech lead | acted | P383 #491 |
| 14 | The card's files, names and placeholders changed in the plan | PO-assistant | acted | #487's text has a section "Changed by the plan council" |
| 15 | A failed look-ok left the token None, and the deploy Case then failed with a TypeError | reviewer | acted | `setUpClass` asserts the token, with look's output |
| 16 | The goldens print the token's image half as `<image>`, so nothing pinned it | reviewer | acted | `test_the_token_ends_in_the_image_hash` |
| 17 | The home-path guard missed the temp folder and the repository path | reviewer | acted | `test_no_golden_holds_a_path_of_this_machine` |
| 18 | The child inherited every `SPARK_*` variable of the caller's shell | reviewer | acted | `run_script` drops them all and sets `SPARK_HOME` |
| 19 | A golden of a removed Case stayed, and nothing noticed | reviewer | acted | `test_every_golden_has_its_case` |
| 20 | Names: `check`, `places_of`, `flash_id`, `devs` did not say their role | reviewer | acted | `run_case`, `replacements_of`, `flash_id_file`, `devs_file` |
| 21 | `golden_bench.py` changes `sys.path` at import | reviewer | rejected | it imports `run_scenario` and `sim_project` itself, as every bench test module does |
| 22 | A space in the repository or Python path fails three goldens, because a script quotes such a path | refuter | acted | `QUOTED_PLACE` drops the quotes around a placed path; a copy at a path with a space passes. The refuter's `shlex.quote` mapping was tried and failed on a quoted path with a suffix |
| 23 | `MOMENT` blanked any value in reach's `at` | refuter | acted | it matches only a moment's shape |
| 24 | The mutation run: 12 output changes planted in the five scripts, 12 caught; a scrub without the project path is noticed | mutation tester | verified | table kept out of the tree, because nothing escaped |
