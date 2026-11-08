# P716 records codes (W6-R2): rows

The claims of the W6-R2 plan, `docs/discovery/2026-10-19-p323-target-architecture/architecture/wave6-plan.md` (section
"W6-R2, the records codes", and its "P716 claims check" block), checked against main 15be9ea9 before any code, and the
choices the build made. Card: [P716 #967](https://github.com/xmejkal/spark/issues/967).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `BoardError` 8 sites, `ToolProblem` 23 (3 in `tools.main`), `StoreProblem` 11 + 3 + 1 + 2 | plan | verified | each line holds at 15be9ea9 (claims check) |
| 2 | the sites are all | plan | acted | not all: 8 `StoreProblem` raises in `spark/design/needs.py` and 5 `ToolProblem` raises in `spark/firmware/image_builder.py` and `spark/bench/image_evidence.py:404`. Each names a code: the needs file and the requirements' parts are `record_file_broken`, a pick key `key_not_plain`, the firmware's `firmware_codes.TOOL_MISSING` and `NO_INTERPRETER`, a board's `BoardError` its own code, the bench's wrap the inner code or `board_codes.TOOL_MISSING` |
| 3 | each class gains a `code` attribute | plan | acted | a decision: one base, `text_guards.CodedMessageError`, with a required `code` keyword (P700's honesty), so no class body grows in `boards.py` or `tools.py` and a raise cannot leave the code out |
| 4 | est. 18 codes | plan | acted | 28 in `scripts/records_codes.py`. `tool_missing` and `missing_fact` are equal literals of board_codes with the same sentence, asserted in `TheBenchCodesTableTest`; no other code is shared |
| 5 | a wrap drops its code | lesson | acted | the two needs wraps in `tools.find` and `tools.status` pass `inner.code`, `image_builder.board_build` passes the `BoardError`'s, the bench's `cannot_check` passes the `ToolProblem`'s. `tools.plan` and `install` fold sentences into `install_failed`, one code for the whole refusal |
| 6 | no R1 key rises | lesson | verified | each `import records_codes` line of `boards.py`, `tools.py`, `parts.py` and `needs.py` is paid by one statement rewrapped onto one line. `parts.validate` 226 to 225 and `tools.plan` 68 to 67 fell, written back with `--accept` |
| 7 | the three codes in `tools.main` (`:627`, `:650`, `:653`) are tested | build | raised | they sit on the line they had, as the plan said, and no test reads them: T2 forbids a new `mock.patch` and an extraction raises `tools.py`'s module key. No mutation row swaps them. They reach a test with the Operation card that takes `main`'s refusals into the library |
| 8 | `store.py:388` (a redirect) and `:448` (a keep that differs) are pinned | build | raised | the tests that reach them assert a multi-line sentence or patch `write_bytes` with no `as`; the code is not asserted there. A row on either would escape |
| 9 | the tests build the errors with no code | build | acted | 34 lines in 17 test files pass a code literal, and 24 rows of older tables follow the coded raises; each replace that builds one of the three errors passes a code, so no row is caught by a TypeError. `--anchors`: 114 refused, the same names as main |
| 10 | `missing_facts` reads `MISSING_FACT` from `records_codes` | plan | acted | it imports `records_codes`, no bench leaf; a mutation row tells another code and `test_missing_facts` catches it on the literal |
| 11 | `DesignError` keeps its own `__init__` | build | raised | it could inherit `CodedMessageError` and lose four lines; W6-S2's `PartError` will need the same base. A small refactor for W6-S2 |
