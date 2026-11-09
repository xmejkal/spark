# P727 wave-6 sweep escapes: rows

The end-of-wave-6 mutation sweep (2026-11-09, main 56f45613) ran 149 rows of 12 wave-6 tables in four shards. 147
were caught and two escaped. Both were holes in the tests, not in the product. Card:
[P727 #990](https://github.com/xmejkal/spark/issues/990).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the drawer row escaped because its test's code assert never runs | sweep | acted | `tests/test_drawer.py:72` asserted inside the `with assertRaises` block, after the raising call. The assert moved out of the block. An AST search over `tests/` found no other assert after a raising call in such a block |
| 2 | the `--fetch` row escaped because no golden runs the `--dry-run` branch for a missing record | sweep | acted | the golden ran `--fetch no-such-part --json`, and the mutated sentence is at `part_handlers.py:149`, in the `--dry-run` branch. A Case `parts-fetch-problems-no-record-dry-run.txt` covers it |
| 3 | the first sweep stopped at "not green BEFORE any mutation" in all four shards, with no test named | sweep | acted | the main checkout held an ignored `scripts/stand_in/` (bytecode caches only), left by the P685 firmware move. `mutate.py`'s `copy_of` skips `__pycache__` but still makes the ignored folder, empty, so `test_architecture.py:332` saw it. The folder was removed by hand, and the sweep ran again |
| 4 | `copy_of` makes ignored folders, and `RedBeforeMutation` names no failing test | sweep | raised | the retro inbox holds it, beside the 2026-11-08 row on `check_commit --full`. A copy of tracked files only, and the failing test ids in the message, would have saved one sweep run (about 100 minutes) |
| 5 | the refuter (Opus) on 2ed85157 | review | verified | each row fails its fixed test when applied by hand, the new golden is stable over two runs and exits 1, and no other `assertRaises` block holds an assert after its raising call. It corrected rows 1 and 3 |
