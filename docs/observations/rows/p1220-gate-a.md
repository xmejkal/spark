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
| 15 | `commands/deploy.md:103` linked a section 12 of never-assume.md that does not exist | PR lens (Sonnet), PR refuter (Opus) | acted | deploy.md links `docs/guide/agents/gate-a.md`. never-assume.md is at its line budget |
| 16 | a null `shut_by` row was printed by neither printer in a test | PR lens | acted | one page test and one `show` test assert "Spark cannot tell. The simulation phase says why." |
| 17 | the row's words for a failed run differ from the plan's C1 | PR lens | acted | row 12: the PR names the change for the PO's review |
| 18 | the PR must say that `commands/build.md` and `commands/idea.md` were read and need no change | PR lens | acted | the PR says so: they read only `data.guide.wired` |
| 19 | a board with no Wokwi model keeps `sim/flash-with-firmware.bin` and no `sim/wokwi.toml`, so a failed run there showed as `[]` while the deploy refuses | PR refuter | acted | such a board reads its image with `default_without_toml=True`, as `deploy_reading.py` does. An unreadable log there gives null. A test with that fixture failed first. Row 11 of the mutation rows |
| 20 | the `GATE_A_SAYS` comment was one long chain | PR lens | acted | short sentences |
| 21 | the names row is a sentence appended to another line of patterns-and-names.md, not a row of its own | PR lens | closed | dropped because the page is at its line budget (272), so the sentence stays where it fits |
| 22 | four older mutation rows anchored on lines this PR moved (p1034-phase-steps 9 and 10, p1142-first-line 6, p337b-no-simulation 12) | the push gate | acted | re-anchored on the lines that do the same job now. Each was planted by hand and caught by its named test |
