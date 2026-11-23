# P1017: the story run follows the imports through scripts/: rows

Card: [P1017 #1483](https://github.com/xmejkal/spark/issues/1483). The plan council: round 1 a lens (Sonnet) and the
refuter (Opus) on v1, round 2 the refuter (Opus) and spark-main on v2. The build adds its own rows, and the PR review (a
lens on Sonnet and the refuter on Opus) adds its rows. This file holds the acted, raised and rejected findings only, and
the closed ones that a later reader needs. A "row" in the last column is a row of
`tests/mutations/p1017-story-imports.json`.

The cause, measured on #1374 (P953 PR 3, merge base 6944a52d, head 1cfa47b2, 37 changed files): the hook chose 57 of 136
test files. tests/test_flow_page.py and tests/test_golden_design.py were not among them. Both were red. The name rule
finds a test only when its text names a changed file's stem, and test_flow_page names none of the seven breadboard
stems. It imports `spark.breadboard.sheet`, which imports four of them, and they reach the other three. No rule read
an import, and no rule added the net of an area that uses the changed area.

The rule after the PR review: the walk only adds tests to a story run that the name rule started. It never ends a doubt.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | a file that no test names but that a test reaches stays a doubt, so the walk changes nothing for it | round 1, the refuter | rejected | built first, then the PR review proved that it drops tests (row 19 of this table). The doubt rule is main's again |
| 2 | "the hook already caps" a wide selection: no cap exists | round 1, the refuter | acted | no cap and no new constant. `scripts/spark/records/store.py` goes from 82 to 125 of 143 test files, the honest selection |
| 3 | a package's `__init__.py` is not an edge, so 64 modules of scripts/ lose tests | round 1, the refuter | acted | `_files_of` gives each package file on the way. `test_a_package_file_on_the_way_is_run_and_so_reaches_its_imports`, row 6 |
| 4 | an import inside a function and the five import forms are not all read | round 1, the lens | acted | `ast.walk`, and `test_each_form_of_import_reaches_its_file` pins `import flow`, `import spark.a.b`, `from spark import a`, `from spark.a.b import X`, a late import and a standard module. Row 5 |
| 5 | v1's row 6 (`_reaching` leaves out the changed file) is an equivalent mutant: a test that imports a module also names its stem | round 1, the refuter | acted | replaced by row 5 (an import inside a function) and row 6 (a package file) |
| 6 | the cost: one graph per `select`, each text parsed once | round 1, the lens | acted | `ImportWalk` builds the graph and the tests' imports once, after the name rule found a test. Measured: `select` 1.2 s on main's tree (143 test files), 2.2 s on #1374's tree, 0.06 s for a doubt |
| 7 | test 6 reads the real tree for each module | round 1, the lens | acted | `setUpClass` reads it once, through `check_commit.story_texts`, the hook's own reader |
| 8 | the tests that only run a script as a child process are not walked | round 1, the refuter | closed | out of the card (54 test files). The first build said that the name rule and the area's net still cover them. That is false for the parts.py Operations in scripts/spark/design/ (row 19 of this table). For a file that no test names, main's doubt rule keeps the quick run, so they run. For a named file they run only if they name it or the area's net holds them. Part of N4 (row 13) |
| 9 | the p714 rows anchored on the rewritten lines no longer find their text (N1) | round 2, the refuter | acted | the two net rows are re-anchored on the new code. The two doubt rows find main's line again. Each of the four was planted by hand and red. `--anchors`: 33 refused, as on main |
| 10 | a whole-tree test that imports a module turns a doubt into a story run (N2) | round 2, the refuter | closed | the doubt reads `named` only, as on main, so no test that the walk finds ends a doubt. `test_a_whole_tree_test_that_the_walk_finds_does_not_remove_the_doubt` stays |
| 11 | a bench module widens from a few tests to about 40, through `scripts/spark/bench/__init__.py` (N3) | round 2, the refuter | verified | `show_bench.py` 21 to 59 of 143 test files, `board_envelope.py` 22 to 59, `known_board.py` 30 to 59. Each count holds the 19 of `ALWAYS_RUN_TESTS` |
| 12 | a file that no test names and that a helper of tests/ reaches cannot be vouched for by a walk that skips the helpers (N5) | round 2, spark-main | closed | built first, then removed after the PR review (row 20 of this table): an unnamed file is a quick run again |
| 13 | the tests that reach a module only through a helper of tests/ or a child process, and `tests/test_fact_needs.py`, which imports the modules named in `data/fact-needs.json`, are not selected by the walk (N4) | round 2, spark-main | raised | a card, filed by spark-main after the merge |
| 14 | N5 says a helper "imports" the file, but `fakes.py` imports neither `request_codes` nor `sourcing_codes` directly: it reaches them through scripts/ | the build | closed | the helper path is removed (row 20 of this table) |
| 15 | the plan's test 1 alone would pin two rules: the walk, and the doubt that the walk removes | the build | acted | each test of the walk has a second test that names the changed stem, so it pins only the walk |
| 16 | a test text that does not parse stops the choice with an error | the build | acted | `_imported` gives nothing for it. `test_a_text_that_does_not_parse_imports_nothing`, row 7 |
| 17 | the value on #1374: the 11 modules the walk adds | the build | verified | the walk adds the plan's 11 modules (57 to 68). On #1374's tree they ran 416 tests in 11.3 s with 3 failures, all in the two missed tests: two in `test_flow_page` (a jumper step, the page budget) and `test_flow_ok_page_txt` |
| 18 | scrum/README.md line 321 says the story run "runs the tests of the modules the change touched, with its area's golden net" | the build | closed | still true in short. The full rule is in docs/guide/developing.md |
| 19 | the doubt check `(named | reached) - ALWAYS_RUN_TESTS` moves 26 files (the parts.py Operations in scripts/spark/sourcing/ and scripts/spark/design/, and `idea_codes.py`) from main's quick run to a story run of 29 to 33 modules. A changed `OFFER_UNKNOWN_SENTENCE` in `show_offer.py` and a `store.locked()` read in `list_drawer.py` passed the branch's selection and failed main's quick run | the PR review, the refuter (Opus) | acted | the doubt line is main's again, and the walk only adds. `test_a_file_that_only_the_walk_finds_stays_the_quick_run_as_on_main`, and p714's doubt rows. Both files are a quick run again. A replay over the 1,232 tracked files outside docs/ and scrum/: 1,084 equal, 148 larger, 0 smaller, 132 quick runs on main and on the branch |
| 20 | with main's doubt rule, the helper path of N5 is dead code | the PR review, spark-main | acted | `helper_texts`, the helpers in `story_texts` and the N5 check are removed, with their 2 tests and 4 rows (the walk follows the helpers, N5, a whole-tree test ends the doubt, the walk feeds the doubt) |
| 21 | tools/check_commit.py line 15 is a docstring line of 213 characters | the PR review, the lens (Sonnet) | acted | re-wrapped |
| 22 | the `_tests_for` docstring does not say what the doubt rule does now | the PR review, the lens (Sonnet) | acted | it says that the walk never ends a doubt, and why |
| 23 | `story_texts` reads the helpers of tests/ for nothing but one check | the PR review, the lens (Sonnet) | rejected | the helper path is removed (row 20 of this table) |
| 24 | a test for the `ValueError` branch of the parse | the PR review, the lens (Sonnet) | rejected | it needs a null byte in a tracked .py file. Low value, and the `SyntaxError` branch is pinned (row 7) |
| 25 | a full run (`check_commit.py --full`) on this PR | the PR review | rejected | the diff touches tools/, tests/ and docs only. The replay of row 19 compares the selection for every file, which is the better proof |
| 26 | main went red after the merges of 2026-11-23: 51 critical mutation rows against the PO's cap of 50 (P981), because P1021 added 1 and P1017 added 2, and the story run of neither PR selected `test_ledger` for a change to a mutation table | the P1010 builder's hook, on main 98d96bdd | acted | the row "the walk stops after one import" is ordinary again; "the hook's story run passes no texts of scripts/" stays critical, since without it the whole walk stops in silence. 50 critical rows. The selection gap is filed as a card |
