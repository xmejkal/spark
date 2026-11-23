# P1017: the story run follows the imports through scripts/: rows

Card: [P1017 #1483](https://github.com/xmejkal/spark/issues/1483). The plan council: round 1 a lens (Sonnet) and the
refuter (Opus) on v1, round 2 the refuter (Opus) and spark-main on v2. The build adds its own rows. This file holds the
acted, raised and rejected findings only, and the closed ones that a later reader needs. A "row" in the last column is a row of `tests/mutations/p1017-story-imports.json`.

The cause, measured on #1374 (P953 PR 3, merge base 6944a52d, head 1cfa47b2, 37 changed files): the hook chose 57 of 136
test files. tests/test_flow_page.py and tests/test_golden_design.py were not among them. Both were red. The name rule
finds a test only when its text names a changed file's stem, and test_flow_page names none of the seven breadboard
stems. It imports `spark.breadboard.sheet`, which imports four of them, and they reach the other three. No rule read
an import, and no rule added the net of an area that uses the changed area.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | a file that no test names but that a test reaches stays a doubt, so the walk changes nothing for it | round 1, the refuter | acted | the doubt check reads `named | reached`. `test_a_test_that_only_the_walk_finds_is_a_story_run_and_not_a_doubt`, row 10 |
| 2 | "the hook already caps" a wide selection: no cap exists | round 1, the refuter | acted | no cap and no new constant. `scripts/spark/records/store.py` goes from 82 to 125 of 143 test files, the honest selection |
| 3 | a package's `__init__.py` is not an edge, so 64 modules of scripts/ lose tests | round 1, the refuter | acted | `_files_of` gives each package file on the way. `test_a_package_file_on_the_way_is_run_and_so_reaches_its_imports`, row 7 |
| 4 | an import inside a function and the five import forms are not all read | round 1, the lens | acted | `ast.walk`, and `test_each_form_of_import_reaches_its_file` pins `import flow`, `import spark.a.b`, `from spark import a`, `from spark.a.b import X`, a late import and a standard module. Row 6 |
| 5 | v1's row 6 (`_reaching` leaves out the changed file) is an equivalent mutant: a test that imports a module also names its stem | round 1, the refuter | acted | replaced by row 6 (an import inside a function) and row 7 (a package file) |
| 6 | the cost: one graph per `select`, each text parsed once | round 1, the lens | acted | `ImportWalk` builds the graph and the tests' imports once, on the first file of scripts/. Measured: `select` 1.3 s on main's tree (143 test files), 2.2 s on #1374's tree |
| 7 | test 6 reads the real tree for each module | round 1, the lens | acted | `setUpClass` reads it once, through `check_commit.story_texts`, the hook's own reader |
| 8 | the tests that only run a script as a child process are not walked | round 1, the refuter | closed | out of the card (54 test files). The name rule and the area's net still cover them. Part of N4 below |
| 9 | the p714 rows anchored on the rewritten lines no longer find their text (N1) | round 2, the refuter | acted | the four rows re-anchored on the new code, each planted by hand and red. `--anchors`: 33 refused, as on main |
| 10 | a whole-tree test that imports a module turns a doubt into a story run (N2) | round 2, the refuter | acted | `(named | reached) - set(ALWAYS_RUN_TESTS)`. `test_a_whole_tree_test_that_the_walk_finds_does_not_remove_the_doubt`, row 9 |
| 11 | a bench module widens from a few tests to about 40, through `scripts/spark/bench/__init__.py` (N3) | round 2, the refuter | verified | `show_bench.py` 21 to 59 of 143 test files, `board_envelope.py` 22 to 59, `known_board.py` 30 to 59. Each count holds the 19 of `ALWAYS_RUN_TESTS` |
| 12 | a file that no test names and that a helper of tests/ reaches cannot be vouched for by a walk that skips the helpers (N5) | round 2, spark-main | acted | that file stays on the quick run. `test_a_file_that_only_the_walk_finds_and_a_helper_reaches_is_a_doubt`, row 8. `request_codes.py` and `sourcing_codes.py` stay on the quick run, as on main |
| 13 | the tests that reach a module only through a helper of tests/ or a child process, and `tests/test_fact_needs.py`, which imports the modules named in `data/fact-needs.json`, are not selected by the walk (N4) | round 2, spark-main | raised | a card, filed by spark-main after the merge |
| 14 | N5 says a helper "imports" the file, but `fakes.py` imports neither `request_codes` nor `sourcing_codes` directly: it reaches them through scripts/ | the build | acted | the rule reads "reaches": each helper of tests/ is a node of the graph, never a way for a test. `select` takes `helper_texts`, a parameter the plan did not name, and `story_texts` passes every `.py` of tests/ that is not `test_*.py` |
| 15 | the plan's test 1 alone would pin two rules: the walk, and the doubt that the walk removes | the build | acted | test 1 has a second test that names the stem, so it pins only the walk. Its own test pins the doubt (row 1 of this table) |
| 16 | a test text that does not parse stops the choice with an error | the build | acted | `_imported` gives nothing for it. `test_a_text_that_does_not_parse_imports_nothing`, row 11 |
| 17 | the value on #1374: the 11 modules the walk adds | the build | verified | the walk adds the plan's 11 modules (57 to 68). On #1374's tree they ran 416 tests in 11.3 s with 3 failures, all in the two missed tests: two in `test_flow_page` (a jumper step, the page budget) and `test_flow_ok_page_txt` |
| 18 | scrum/README.md line 321 says the story run "runs the tests of the modules the change touched, with its area's golden net" | the build | closed | still true in short. The full rule is in docs/guide/developing.md |
