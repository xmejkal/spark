# P1041: a tools file or a store folder that spark cannot read is a refusal with a code: rows

Card: [P1041 #1529](https://github.com/xmejkal/spark/issues/1529). This file holds the acted, raised and rejected findings
only. The plan had one plan check, the refuter on Opus. The PR's review (one lens and the refuter) adds its rows here.
2026-11-23.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the FILE_REFUSED comment would name "all four users", but six modules raise it today, seven with tool_finder | the plan check, the refuter | acted | fixed: the comment names answer_operation, store, storage, keep_file, keep_picture, validate_parts and tool_finder |
| 2 | a link loop in the place of a tools file was absent on main and becomes a refusal that says "fix its permissions" | the plan check, the refuter | acted | fixed: the sentence says "fix it or its permissions", and a test pins the loop as `file_refused` |
| 3 | `board_engine.find_toolchain` turns any ToolError into None, so the refusal's sentence is lost there | the plan check, the refuter | raised | a card, to be filed by spark-main with row 4 |
| 4 | the bench gives every ToolError the code `tool_missing` and an empty fix (`stops.CODE_OF_CLASS`), also for a tools file it cannot read | the plan, out 1 | raised | a card, to be filed by spark-main; this PR pins today's mapping in `AnUnreadableStoreTest` |
| 5 | a store folder that is there but that spark cannot enter makes the store say `cannot make <store>`, as if it were missing | the plan, out 2 | raised | a card, to be filed by spark-main |
| 6 | a broken link in the place of a tools file stays absent, but storage.py refuses one | the plan, out 3 | raised | a card, to be filed by spark-main if the PO wants one rule for both |
