# P1325: check-design checks the folder's boards: rows

Card: [P1325 #1903](https://github.com/xmejkal/spark/issues/1903). The PR review (a lens on Sonnet and the refuter on
Opus) read the branch at 49cea19c, and P1255's plan check added two rows. This file holds the acted, raised and rejected
findings only. 2026-11-27.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | a folder with several `*requirements.json` files (the car and its remote) is checked against one board only, a regression | refuter 1 | acted | `folder_boards(checked)` returns a list, one board per file, a file with none taking the project's board; tests `test_two_requirements_files_check_both_boards` and the selection test |
| 2 | a sub-folder's broken `requirements.json`, or a `board` that is no text, loses the second `boards` line | refuter 2 | acted | `discover_boards` raises the folder's own sentence; two tests |
| 3 | `boards_to_verify` reads the files a second time | refuter 3, lens 5 | acted | no default: the boards are computed once in `discover_boards` and passed on |
| 4 | the rule is written in full in three places | lens 1 | acted | in the `--help` and json.md only; scripts.md points to json.md |
| 5 | json.md's one long line, and never-assume.md's sentence | lens 2 | acted | a rule paragraph and two bullets in the same line budget; the never-assume sentence says the `boards` line lists every board |
| 6 | prose says "own" and "named" | lens 3, lens 4 | acted | the docstrings say "the folder's boards" and "Empty when no file and no project names a board"; spark-review says "the folder's boards" |
| 7 | the second `boards` line is the `not resolved (...)` text | lens 6 | acted | json.md and the `discover_boards` docstring say "a second `boards` line gives the reason (`not resolved (...)`)" |
| 8 | `CheckedFolder`'s docstring lacks its role word, and the R6 baseline key was renamed by hand | spark-artifact point 1 | acted | the docstring starts with "Value:"; the key is removed, and `tests.test_architecture` passes without it |
| 9 | main holds 50 critical rows, the cap | spark-artifact, the ledger | acted | the two rows of the branch are not critical; `tests.test_ledger` run before the report |
| 10 | map.md says "none" for the tests of `checked_folder.py` | lens 7 | rejected | the tests reach the module through `test_check_all.py`, and the map is no test claim |
| 11 | a requirements file the build refuses (a bad signal) also gives every board, and the docs say only "cannot be read" | final review 2 | acted | json.md and the `folder_boards` docstring add "or the build refuses it (signals, parts)"; a test with a signal that has no name |
| 12 | wording: the spark-review row, the `discover_boards` docstring and the test class docstring still speak of one board or only the project's boards | final review 4 | acted | "each of the folder's boards"; the docstring names the shelf's and the library's boards; the class docstring is plural |
| 13 | checks.md's dated-record sentence does not link the rule | final review 5 | acted | one link to json.md inside the same line |
| 14 | `TheFolderBoardIsCheckedTest` leaves its temp folders | final review 6 | acted | `addCleanup(shutil.rmtree, ...)` for the store, the project and the bare folder |
| 15 | the error for a `board` that is no text names `design_codes.REQUIREMENTS_FIELD_WRONG`, which the checks area may not name (test_json_contracts) | push hook | acted | the records code `RECORD_FILE_BROKEN`, as `board_records.requirements_board` gives for the same sentence; one home for both is P1342 #1925 |
