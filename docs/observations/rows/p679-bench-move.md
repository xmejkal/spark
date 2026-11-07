# P679 bench move (W5-3a, S11): rows

What the build of W5-3a found against its plan, `docs/discovery/2026-10-19-p323-target-architecture/architecture/wave5-plan.md`
(section "W5-3a, the bench area move"), and the choices it made. Card: [P679 #911](https://github.com/xmejkal/spark/issues/911).
The base is PR #906's branch merged with main (39a35e65).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | 18 modules move, `board_codes.py` and `board_pads.py` stay | plan | acted | `git mv` of the 18; `ls scripts/board_*.py scripts/deploy_*.py` prints `board_codes.py`, `board_pads.py`, `deploy_record_store.py`. `test_architecture.TheBenchAreaTest` holds it |
| 2 | 182 import lines in 58 files (181 by `ast`) | plan | acted | on the base, `ast` counts 183 lines in 59 files for the 20 modules (#906 and W5-1 added some). The 18 that move have 159 lines in 49 files, all `import m` or `from m import`, one name each; one ast-checked script rewrote them to `from spark.bench import m` and `from spark.bench.m import` |
| 3 | 360 mutation rows name one of the 20 (352 on the 18 at a57c304a, plus #906's) | plan | acted | recounted on the base: 364 rows on the 18, retargeted with `tools/mutate.py --retarget` per module. `deploy_stages.py` has none. `board_codes.py` (3), `board_pads.py` (4) and `deploy_record_store.py` (6) stay |
| 4 | two rows name `scripts/board_ready.py`, a file that is gone | plan | raised | both in `tests/mutations/p215-ready.json`. Dead since the file left; not deleted here, so the table's history stays. A later sweep of dead rows decides |
| 5 | the retargeted rows anchor | build | acted | two rows anchored on the text the move changes (`cmd-parent` in `p283-full-path-lines.json`, `deploy-grant-line-relative` in `p242-deploy-grant.json`): their `find` now reads `parents[2]`. `--anchors --for scripts/spark/bench`: 463 rows, 42 refused, the same 42 as on the base |
| 6 | 42 of the bench's 463 rows do not anchor on the base either | build | raised | old tables whose code changed since (e.g. `naive now`, `stamp keeps microseconds`, `the hint says RESET only`). Not this card's: a dead-row sweep, with row 4 |
| 7 | the 23 baseline keys follow the move | plan | acted | 23 keys rewritten. The plan did not say that `test_architecture` wants the file sorted: it is sorted again. `measure.py --rules`, path-normalised and sorted, is the same list as on the base: no new breach, so the R1 (40 lines in `scripts/spark/`) and X2 claims hold |
| 8 | `GRANT_COMMAND`, `DEPLOY_GRANT_COMMAND` write `Path(__file__).resolve().parents[2]` | plan | acted | both in `board_grant.py` |
| 9 | `next_text` writes `Path(__file__).resolve().parents[2]` | plan | rejected | it never resolved: it built `Path(__file__).with_name(...)`. It writes `Path(__file__).parents[2] / ...`, so a move changes the folder and nothing else |
| 10 | `PLUGIN_JSON` two folders up becomes four | plan | acted | `Path(__file__).resolve().parents[3]` |
| 11 | `TheServiceHoldsNoPrintTest` reads `ROOT / "scripts" / <name>` | plan | acted | both paths follow the move. The plan missed that its second test, `test_the_platform_does_not_import_the_service`, reads only `ast.Import` names and `ImportFrom.module`: after the move `from spark.bench import deploy_service` would pass it unseen. It reads the `ImportFrom` names too |
| 12 | the `__file__` sites are the four the plan names | plan | rejected | two tests built the expected grant line from `Path(board_grant.__file__).with_name("grant.py")` (`test_deploy_gate.TheStandingYesTest`, two tests) and failed. They now expect `ROOT / "scripts" / "grant.py"`, a path the code does not choose itself |
| 13 | `tests/test_boards.py` allows `scripts/board_pads.py` by path | plan | acted | true (`test_no_other_python_file_reads_the_key`); the leaf stays, the test is unchanged |
| 14 | each moved module imports alone | plan | acted | a child Python per module of `scripts/spark/bench/` (26, the Operations too). Proved: a planted `from spark.bench import board_look` in `board_pads.py` fails it with "partially initialized module 'boards'" |
| 15 | the goldens stay byte-equal | plan | acted | `git diff 39a35e65 -- tests/golden` is empty |
| 16 | `docs/guide/map.md` is regenerated | plan | acted | `tools/map.py --write`: 18 rows added to the bench area. `deploy_stages.py` shows "none" under tests that import it |
| 17 | the docs name each module where it lives | plan | acted | the live guides name the modules by file name only, which still holds; `check_docs.py` passes. `patterns-and-names.md` says the package holds the libraries and why the two leaves stay; `areas/bench.md` and `refactor-plan.md` section 10 say the same |
| 18 | `tests/test_self_confirmation`'s `module.NAME` keys | build | acted | unchanged: `from spark.bench import board_live` keeps the name `board_live`, and the test reads `ImportFrom` names under `spark` |
| 19 | The glob test misses a moved module that is not board_ or deploy_ (flasher.py, image_evidence.py) coming back to scripts/ | reviewer, PR | acted | test_no_bench_module_has_a_second_copy_in_scripts, seen failing on a planted copy |
| 20 | The plan's goal line misses deploy_record_store.py | reviewer, PR | rejected | wave5-plan.md:211-212 names it, the line break hid it |
