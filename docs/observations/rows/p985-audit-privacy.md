# P985: `parts.py --audit` masks the store, the home and the project: rows

Card: [P985 #1435](https://github.com/xmejkal/spark/issues/1435). Acted, raised and rejected findings only.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `AuditRecords` had no `privacy_for`, so its sentences printed the raw store and home paths | P973 rows, row 3 | acted | `privacy_for` in `audit_records.py`; `test_audit_masks_the_store_and_the_home_in_its_sentence_and_its_json` |
| 2 | The P973 and drawer tests asserted the raw store path | the change | acted | they hold the masked form (`<store>/...`), each with a comment naming P985 |
| 3 | The `--function-set ... --project P` line is one a person runs, so masking its project would break it | the change | acted | the line is a `PastedLine`; `test_audit_masks_the_project_but_keeps_the_function_set_hint_to_run` |
