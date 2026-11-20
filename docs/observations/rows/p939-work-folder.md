# P939: a crashed build removes its work folder: rows

Card: [P939 #1337](https://github.com/xmejkal/spark/issues/1337), raised by row 8 of
`docs/observations/rows/p938-slot-lines.md`. One plan check (Sonnet), then a build to the plan. This file holds the
acted, raised and rejected findings only. 2026-11-20.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the service cannot remove a folder it returns, as `keep_all` reads it after the return (`build_board.py:109`) | plan | acted | the service removes the folder only when it raises after making it; `BuildBoard`'s `finally` still removes a returned one after the keep step |
| 2 | full ownership (a context manager, or `keep_all` inside the service) changes the result that `fakes.py`, `test_build_service.py` and `run_with` use | plan, plan check | rejected | the rule forbids changing those tests; the split stays |
| 3 | `_work_folder` writes, links and looks up the toolchain after `mkdtemp`, so an OSError there also left the folder | plan check | acted | `mkdtemp` moved into `build`, and `_work_folder(workdir, ...)` runs inside the `try`; `test_a_tools_file_it_cannot_read_leaves_no_work_folder` (an unreadable `.spark/tools.json`, no new `mock.patch`); mutation row 2 |
| 4 | a crash in `note_built` left the folder | card | acted | `test_a_crash_after_the_work_folder_is_made_leaves_no_work_folder`; mutation row 1 |
| 5 | the glob cleanup and its "P939" comment in the P938 crash test became dead and a wrong claim | plan | acted | removed with its `folders` line; no assertion changed |
| 6 | patterns-and-names.md:40 could say "after a return" | plan check | rejected | its line is one paragraph at the page's budget, and the words would make it longer; the module docstrings say it |
