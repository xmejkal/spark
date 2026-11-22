# P973: `parts.py --audit` says could-not-run when a folder it reads cannot be listed: rows

Card: [P973 #1394](https://github.com/xmejkal/spark/issues/1394). Acted, raised and rejected findings only.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `unlisted()` must run inside the try, or a project folder at mode 0 crashes the audit | plan check, refuter | acted | the call is inside the try; `test_a_project_folder_at_mode_zero_is_could_not_run_with_no_traceback` |
| 2 | Another listed project's parts/ and boards/ are read by `drawer.linkable`, so an unlisted one reads as a dangling entry | plan check, refuter | acted | `unlisted()` walks `store.projects()`; `test_another_listed_project_s_parts_folder_the_disk_will_not_list_is_could_not_run` |
| 3 | The audit prints the raw folder path, as its other record_unreadable sentences do | plan check, refuter | raised | card [P985 #1435](https://github.com/xmejkal/spark/issues/1435) |
| 4 | `store.records` globs a folder and skips an unlisted one in silence, for every other operation too | plan | raised | card [P986 #1436](https://github.com/xmejkal/spark/issues/1436) |
| 5 | Nothing covered the drawer: removing it from `unlisted()` passed every test; the new tests' scratch folders were never removed | refuter on PR #1437 | acted | `test_a_drawer_folder_the_disk_will_not_list_is_could_not_run_and_named`, a mutation row for the drawer, and an `rmtree` cleanup in each new test |
| 6 | A project folder at mode 0 names `P/parts` with `[Errno 13]` and the "fix the file" fix, as on main | refuter on PR #1437 | raised | card [P986 #1436](https://github.com/xmejkal/spark/issues/1436) |
