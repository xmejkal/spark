# P1220: gate A's one free condition and the row "Tested before the board": rows

Card: [P1220 #1769](https://github.com/xmejkal/spark/issues/1769). The PO, 2026-11-26: "we need to analyze and design
how it should actually work, what steps it takes, cause I knw there are some free steps we can do, but then the payd
part". The plan was written by the plan-writer (Opus), checked by a lens (Sonnet) and the refuter (Opus), and given its
yes by the delegated council (tech lead, architect, PO assistant, Opus), delegated and the PO's to change. This file
holds the acted, raised and rejected findings only. 2026-11-27.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | three exact-equality checks of the guide dict in `tests/test_flow.py` break when `gate_a` is added | plan refuter (Opus) | acted | each gains `"gate_a": None` |
| 2 | the council named `_why_run_failed` as the one function, but `ProjectImage.failed_runs` is the public reader it repeats | plan-writer, refuter | acted | open choice 1: `_why_run_failed` calls `failed_runs`, so the deploy, the guide and the row read one function. A comment on the card says so, delegated |
| 3 | the common order (a board log of an older image, a rebuild, a failed run on the new image) had no test | plan refuter | acted | a test gives `shut_by == ["run-failed"]` |
| 4 | the canvas's row also shows the free checks | plan refuter, PO assistant | raised | open choice 4: the free checks have no kept record yet. A comment on P1209 [#1758](https://github.com/xmejkal/spark/issues/1758) says its reader adds them within v0.10 |
| 5 | "costs no minutes" could not fail, because `show` never calls `outside.run` | plan lens (Sonnet) | acted | the test's fake run raises, and the files under `sim/runs/` keep their mtimes, through `ShowFlow` and `WriteFlowPage` |
| 6 | step 1's test passed before step 1 | plan lens | acted | it patches `ProjectImage.failed_runs` to return a failure. It failed with `None != 'one.log did not pass...'` before the change |
| 7 | the no-`sim/wokwi.toml` case and words of permission in a `[]` row had no test | plan lens | acted | both are pinned. No `[]` row holds "open", "ok", "allowed", "ready" or "permitted" |
| 8 | "so making it last waits" promised a step that does not exist | plan lens | acted | the words went |
| 9 | `--json` told Claude nothing to do | plan lens | acted | `docs/guide/agents/gate-a.md` has a table: each `fact` and what Claude does |
| 10 | the tables did not fit `flow.md`, `never-assume.md` and `patterns-and-names.md`, which are at their line budgets | the build | acted | the table is on the new page `docs/guide/agents/gate-a.md`. Each of the three pages gained one sentence and the link. `agents.md` is at its budget, so the new page is linked from `flow.md` and `never-assume.md` only |
| 11 | `docs/guide/agents/json.md` should name `.gate_a` | plan lens | rejected | its flow row's cell is over the 300-character limit that `test_docs` holds. `flow.md` names the key |
| 12 | with `RUN_FAILED_NOW`'s words, the NOW box said the same sentence in the row and in NEXT | the look in Chrome | acted | the row says the fact only, "A run failed on this image (one.log).", and NEXT says what to do |
| 13 | the page differs from the canvas's Simulation artboard: the label in upper case, no check line, no dates, no "on a stand-in board", no separate Gate A box | the look in Chrome | raised | named in the PR for the PO's review. The free checks are row 4 |
| 14 | the mutation rows were not run by `tools/mutate.py`, which did not finish in 28 minutes | the build | raised | `--anchors` passes, and each of the 10 rows was planted by hand and caught. The sweep runs them |
