# P1061: page_script.ts is the source of the page's script, and the gate checks the compiled .js: rows

Card: [P1061 #1559](https://github.com/xmejkal/spark/issues/1559), PR [#1606](https://github.com/xmejkal/spark/pull/1606).
The PR review: a lens on Sonnet and the refuter on Opus, one round. No must-fix, and every claim of the PR held. This
file holds the acted, raised and rejected findings only. 2026-11-24.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | a branch that deletes page_script.ts turns the drift check off in silence: `needs_tsc` gives False for a tree with no `.ts`, even when `changed` names it | the refuter, should-fix | acted | `needs_tsc` gives False for a tree with no `.ts` only when `changed` names none of the four, or when the tree holds none of them. The second part keeps C10: a test's empty archive never reaches tsc, even on a branch that changed the script. `test_a_branch_that_deleted_the_source_still_needs_tsc` (a gate on a repository whose commit deleted the `.ts` exits 2); row "a branch that deleted page_script.ts turns the check off" in `tests/mutations/p1061-page-script-ts.json` |
| 2 | a clone without `origin/main` has `changed` None, so every push needs tsc | the refuter, nit | acted | the behaviour stays (D3: a doubt runs more); the bullet in `docs/guide/developing.md` says so within its one line |
| 3 | `script_drift` runs a bare `tsc`, not the one whose version `tsc_refusal` read | the lens and the refuter, nit | acted | `script_drift(tree, tsc, run)` runs the path `which("tsc")` found. The tests assert the compile's program; row "the compile runs a bare tsc" |
| 4 | `docs/guide/agents/flow.md:257` is over 120 characters | the lens, nit | acted | the paragraph is wrapped again within its 7 lines; P1061 is named plain, as P1043 is in the same file. The file stays at 400 |
| 5 | `TSC_LINES_SHOWN` is a constant used once | the lens, nit | rejected | it gives the number a name, as `NAMES_SHOWN` and `RED_TESTS_SHOWN` do beside it |
