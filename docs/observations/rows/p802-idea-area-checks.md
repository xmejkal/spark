# P802: the idea area joins the architecture checks: rows

Card: [P802 #1133](https://github.com/xmejkal/spark/issues/1133). Plan check: one refuter (Opus), 2026-11-13. This file
holds the acted, raised and rejected findings only (rules.md), with the build's own rows. 2026-11-13.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `idea/idea_codes.py` calls itself a leaf, but `measure.LEAVES` did not list it, so U1 never checked that it imports nothing of spark | card | acted | `"idea_codes"` in `LEAVES`; `tests/test_architecture.py` holds every module of `scripts/spark/` whose docstring says "A leaf:" to `LEAVES`; mutation row 1 |
| 2 | `bench/deploy_stages.py` and `core/codes.py` also say "A leaf:" and were not in `LEAVES` | plan check, refuter | acted | both added to `LEAVES` and `LEAF_NAMES`; both import nothing, and `measure.py --rules` lists no U1 breach for them |
| 3 | `tests/planted_tree.py` `LEAF_NAMES` must gain each new leaf, or U1 reports it missing in every planted tree | plan check, refuter | acted | the three names added; its docstring said "the five leaf modules", stale since twelve, now "the leaf modules" |
| 4 | the idea area had no area test: no `each_module_imports_alone` | card | acted | `TheIdeaAreaTest`, modelled on bench's (its `__init__` imports `DropNeed` for `OPERATIONS`), with `MODULES` `drop_need`, `idea_codes` |
| 5 | for a changed idea module the story run named `test_golden_idea` (`tools/story_tests.py:110`), which does not exist, and `select` drops a missing net without a word | card | acted | `GOLDEN_NET_ELSEWHERE` maps idea to records: `tests/golden_records.py:196` runs `parts.py --needs-drop`; a test holds every area folder of the real tree to a net file that exists; mutation row 2 |
| 6 | `tests/test_story_tests.py` pinned idea as an area with no net | plan check, refuter | acted | the test keeps its point with a made-up area, `gadget`; idea joins the build and sourcing test |
| 7 | the target architecture's `areas/idea.md` said idea has no golden net and names `test_golden_idea` | card | acted | it names the records net and `parts.py --needs-drop` |
| 8 | a third mutation row: the leaf-docstring test's own check inverted | caller | rejected | dropped because a row plants a defect in the code the suite runs; inverting a test's assertion only shows that the test can fail, which row 1 already shows |
