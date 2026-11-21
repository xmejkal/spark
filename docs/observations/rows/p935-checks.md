# P935 PR 4: the checks area's codes carry their meaning and fix: rows

Card: [P935 #1330](https://github.com/xmejkal/spark/issues/1330). This file holds the acted, raised and rejected findings
only. The plan check had a lens on Sonnet and the refuter on Opus; the lead's revisions decide where they differ from the
plan. Then come the build's own findings. 2026-11-21.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the area cannot join the scan: `calls_off_the_table` found 28 broken lines, 4 real (`Finding(..., None)` at `check.py` and `check_design.py`) and 24 false alarms (`build_check.py` and `physics_check.py` define their own `class Finding`) | the plan | acted | the 4 sites are `Finding.of`; the scan skips a call of a class the file defines with no bases and does not import |
| 2 | the own-class rule hid two cases: a copied `class Finding(namedtuple(...))` and `class Finding(result.Finding)` | the plan check (the refuter) | acted | the rule counts a class with no bases only; `test_the_scan_takes_a_class_the_file_defines_with_no_bases_for_no_core_finding` plants both, and the plain own class |
| 3 | seven fix texts were worded better than the plan's: HEADER_NOT_KEPT, NO_CACHED_HEADER, NO_VENDOR_VARIANT, NO_RULE_STATED, CHECK_CRASHED, NO_PACKAGE, NO_BOM_IN_PACKAGE | the plan check | acted | the texts are in `check_codes.py` and marked in the PR's table; `CHECK_FIXES` pins all 19 |
| 4 | the module docstring said "No check writes a code in its JSON yet", which is false (`build_check.py`, `vendor_pins_check.py`) | the plan | acted | the docstring is true, and names the two pairs (RULES_REFUSED with design, INPUT_AMBIGUOUS with build) |
| 5 | compare_design's fix for a missing circuit named `make`, and no spark project has a Makefile | the plan | acted | the one output change: no_circuit, no_rules_file and no_rule_stated take their code's fix in `compare_design.py --json` |
| 6 | the NO_PACKAGE row anchor "the command" occurs twice; the CHECK_FOUND_PROBLEMS row looked like line 596 | the plan check (the refuter) | acted | the anchors are "of the fab package, or export one with `npx" and a line with `r["check"]`; `--anchors` proves each |
| 7 | two mutation anchors moved: p693 "CODES misses a constant", p935-design "the design area names no table beside its own" | the build | acted | both re-anchored; `tools/mutate.py --anchors` refuses the same 20 rows as main |
| 8 | CHECK_COULD_NOT_LOOK's fix is generic when its sentence is a crash note | the plan check (lens 4) | rejected | dropped because no output prints a Finding's fix today (`renderers.py:54-61`, `cli.py:46-51`); the plan's raised row 3 stays as the record: P935 #1330, PR 4b |
| 9 | PR 3's row 9: the positional forms (`Refusal(text, code)`, `ImpossibleError`, `RefusedInputError`, `CouldNotKeepError`, `PackageError`, `could_not_run`) are not seen by the scan, and about 8 sites pass a non-literal code | the plan | raised | "P935 #1330, PR 4b"; PR 3's rows file points there now |
| 10 | a missing `gh` raises FileNotFoundError at `vendor_pins_check.py:63`, and `:194` catches RuntimeError only | the plan check (the refuter) | raised | card P975 https://github.com/xmejkal/spark/issues/1403 |
| 11 | RULES_REFUSED's fix is loose for a rules file that is not JSON (`fab.py:105`), in design and checks | the plan check | raised | "P935 #1330, the build PR or PR 4b" |
| 12 | no Refusal fix reaches the JSON (`build_check.py:551` and `vendor_pins_check.py:208` write the code without the fix), and `check_all`'s Finding fixes reach nobody (`JsonDocument` prints data, `TextReport` prints lines) | the plan | raised | "P935 #1330, PR 4b" and the build PR |

The rows: tests/mutations/p935-checks.json.
