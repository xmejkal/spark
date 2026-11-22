# P983: `--fetch` finds a shelf record by the rule of every other writer: rows

Card: [P983 #1426](https://github.com/xmejkal/spark/issues/1426). Acted, raised and rejected findings only.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `--fetch` found a shelf copy through `record_kind.record_home` and wrote the copy itself, while `--fact-set`, `--function-set`, `--keep --part`, `--keep-picture`, `--find-documents` and `--features-set` write its project's record through `record_home.record_path`; the next of those writes refreshed the copy from the project's record and the fetched `documents` were lost. Spark's library was refused by every writer, and none wrote it | reproduction on a scratch store | acted | `datasheets.fetch_home` finds the record by `record_path` and `fetch_documents` makes the shelf copy current; `test_a_fetch_through_a_shelf_copy_keeps_the_documents_in_its_project_and_the_copy_follows` |
| 2 | `--fetch` read the cited URLs back from the `record_home` file, which a shelf copy that could not be refreshed would leave stale | plan | acted | `FetchDocuments.build_answer` reads the file `fetch_home` names |
| 3 | By the same rule `--fetch` now reaches a record that only another listed project holds, which it called `no_such_part` before, as the other writers do | plan | acted | `record_path` is the one rule; the card asks for it |
