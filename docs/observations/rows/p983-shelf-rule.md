# P983: `--fetch` finds a shelf record by the rule of every other writer: rows

Card: [P983 #1426](https://github.com/xmejkal/spark/issues/1426). Acted, raised and rejected findings only.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `--fetch` found a shelf copy through `record_kind.record_home` and wrote the copy itself, while `--fact-set`, `--function-set`, `--keep --part`, `--keep-picture`, `--find-documents` and `--features-set` write its project's record through `record_home.record_path`; the next of those writes refreshed the copy from the project's record and the fetched `documents` were lost. Spark's library was refused by every writer, and none wrote it | reproduction on a scratch store | acted | `datasheets.fetch_home` finds the record by `record_path` and `fetch_documents` makes the shelf copy current; `test_a_fetch_through_a_shelf_copy_keeps_the_documents_in_its_project_and_the_copy_follows` |
| 2 | `--fetch` read the cited URLs back from the `record_home` file, which a shelf copy that could not be refreshed would leave stale | plan | acted | `FetchDocuments.build_answer` reads the file `fetch_home` names |
| 3 | `record_path` reaches every listed project, so `--fetch only-irr --project mine` (and with no `--project`) wrote irrigation's record, a project the person did not name; on main it said `no_such_part` | refuter on PR #1438 | acted | `fetch_home` says `no_such_part` when the nearest layers hold no record, and a shelf copy still writes its own project's record; `test_a_fetch_never_reaches_a_record_only_another_listed_project_holds` |
| 4 | `record_path` reaches every listed project for the other writers too: `--fact-set` and the rest likely write a project the person did not name | refuter on PR #1438 | raised | card [P987 #1439](https://github.com/xmejkal/spark/issues/1439) |
