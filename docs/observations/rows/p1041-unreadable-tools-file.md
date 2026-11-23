# P1041: a tools file or a store folder that spark cannot read is a refusal with a code: rows

Card: [P1041 #1529](https://github.com/xmejkal/spark/issues/1529). This file holds the acted, raised and rejected findings
only. The plan had one plan check, the refuter on Opus. The PR's review was one lens (Sonnet) and the refuter (Opus), and spark-main decided each item.
2026-11-23.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the FILE_REFUSED comment would name "all four users", but six modules raise it today, seven with tool_finder | the plan check, the refuter | acted | fixed: the comment names answer_operation, store, storage, keep_file, keep_picture, validate_parts and tool_finder |
| 2 | a link loop in the place of a tools file was absent on main and becomes a refusal that says "fix its permissions" | the plan check, the refuter | acted | fixed: the sentence says "fix it or its permissions", and a test pins the loop as `file_refused` |
| 3 | `board_engine.find_toolchain` turns any ToolError into None, so the refusal's sentence is lost there | the plan check, the refuter | raised | [P1058 #1555](https://github.com/xmejkal/spark/issues/1555) |
| 4 | the bench gives every ToolError the code `tool_missing` and an empty fix (`stops.CODE_OF_CLASS`), also for a tools file it cannot read | the plan, out 1 | raised | [P1058 #1555](https://github.com/xmejkal/spark/issues/1555); this PR pins today's mapping in `AnUnreadableStoreTest` |
| 5 | a store folder that is there but that spark cannot enter makes the store say `cannot make <store>`, as if it were missing | the plan, out 2 | raised | [P1059 #1556](https://github.com/xmejkal/spark/issues/1556) |
| 6 | a broken link in the place of a tools file stays absent, but storage.py refuses one | the plan, out 3 | rejected | dropped because the PO did not ask for one rule (the plan's D2) |
| 7 | with a readable store and a `downloads` folder of mode 0, `tools.py --status` still ends in a traceback from `is_file()` in `locate` | the review, the refuter | acted | fixed: `_downloaded` gives `file_refused` for a download that the disk refuses to stat, a child test of `tools.py --status` and a fifth mutation row |
| 8 | the raised rows of this file name no card | the review, the lens | acted | fixed: rows 3 to 6 name their card or why they were dropped |
| 9 | the PR body does not say that `register` on a store of mode 0 shows the store's own refusal, not the tools.json sentence | the review, the lens | acted | fixed: the PR body says so and names P1059 |
| 10 | `tools.py --status` has no `--json`, so its refusal is a stderr line only | the review, the lens | raised | no card: tools.py is a status page, not an Operation on the core yet (P793 piece 5) |
| 11 | there is no tests/test_records.py for the tests | the review, the refuter | rejected | the wording of spark-main's brief, not of the change: the tests are in tests/test_tools.py and tests/test_bench_record.py |
