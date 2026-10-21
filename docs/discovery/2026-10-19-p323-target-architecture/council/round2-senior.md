# Round 2, senior engineer: can it be built as written

Checked against scripts/look.py, parts.py:1581, tests/ and tests/mutations/ on main (2026-10-19). Python 3.10, unittest.

## Findings

**F1. The baseline (D10).** `ast` gives `end_lineno`, so every rule is checkable. Store `tests/architecture_baseline.json`, one key per line, sorted, no line numbers: `"S6|scripts/parts.py|_op_list": 71`. The value is today's size or count. The test fails when a measure is above its value (new breach or growth) and when it is below (stale: "lower the baseline"). `python3 tests/test_architecture.py --lower` rewrites it, and can only lower. One key per line keeps merges line-wise. Scope text for the standard: S4, S5 (first half), S7, S11 apply to `scripts/spark/` only. S1, S5 (door size), S6, S8, S12 apply to all of `scripts/` and `tests/`. Otherwise S11 puts about 1,000 functions in the baseline.

**F2. S12 hits real code.** Today `command_for`, `build_commands`, `repl_command` and `is_library` mean a shell command and a folder. Replace S12 with: "No class name uses Validator, Verifier, Checker, Command, Library, Context or Manager as a whole CamelCase word. No function name uses validator, verifier, checker or manager as a whole word."

**F3. Slice 1 cannot plant a cycle.** `spark/` holds only `core/errors.py`. Replace the done-when's planted-defect clause with: "`ArchitectureCheck(root)` takes a folder. Five unittest cases build a temp tree and plant a cycle, a door import, a `print` in `spark/`, a new `mock.patch` and a module the guards skip. Each is caught. `tests/mutations/p323-architecture.json` plants the same five in the checker's own logic."

**F4. `run_door` needs more than the design shows.** Look's test seam is `look.main(argv=None, run=subprocess.run)`, and `test_look` calls `look.main(["--project", p, ...], run=run)`. Signature:

```python
def run_door(prog, operations, argv=None, *, options=(), **collaborators) -> int
# look.py:  def main(argv=None, run=subprocess.run): return run_door("look.py", OPERATIONS, argv, run=run)
```

`prog` is positional so no collaborator can clash. Four gaps:
1. `EPILOG` is 28 lines, so a 40-line door cannot hold it. Add `description` and `epilog` to `Operation`. They live in `bench/operations.py`.
2. `LookStop` is not a plain `SparkError`. It carries the doctor result and `look_stop_envelope`, and prints doctor lines to stderr. S5 bans `print` in `spark/`. The look Operation catches it and returns an answer with a new `diagnostics` field. `run_door` writes that field to stderr.
3. Exit code today is `report.exit_code()`. Slice 2 must assert it equals `EXIT_FOR[status_of(...)]` on every `test_look` case.
4. `run_door` must turn a bad argument into an answer, as parts.py's `_Parser.error` does (`BadArgument`). Put that in the helper.

**F5. Core imports outcomes.** `run_door` needs `outcomes` and the design says `outcomes` stays flat until its move, but 2.2 says core imports only stdlib. Fix: slice 2 moves `outcomes.py` to `core/outcomes.py`. It imports only `json`. Cost: 39 importers, 7 mutation rows, 0 patches.

**F6. `Argument` against parts.py:1581.** It fits, with two additions.
- The 21+ rows are flags of a required mutually exclusive group, not subcommands. The Operation's selector is its own flag, so `Operation.arguments` must be `(Argument("--signals", nargs="+", metavar="PART"),)` and `run_door` must build the group.
- The 11 `OPTIONS` rows are shared by all Operations. Hence `options=` above. Also add `data: tuple` to `Operation` (the 5th tuple field, the keys of `data`), or `--describe` loses output keys. `"deletes"` appears only in a comment, so the effects vocabulary is complete. `store.locked()` for `writes` stays in parts' own `operations.py`, since core cannot import store.

**F7. First move, bench.** Modules: look, deploy, grant, board_doctor, board_live, board_reach, flasher, board_connection, board_console, board_look, board_envelope, board_facts, deploy_service, deploy_gate, ready_check, download_mode, firmware_platform. Count: 34 importing files, 188 mutation rows in 18 tables, about 15 `mock.patch.object` lines on bench modules (deploy_service 8, board_look 3, board_doctor 2). Another 16 patch `tools.find`, and they retarget when `tool_finder` moves. Patches are object patches, not strings, so they change by import and name. Guard regexes that match `import store` or `scripts/*.py` (`test_store:78`, `test_orphans:52,82`) also need the package form in each move PR. Say so in 5.3.

## Sizes

- Slice 1: about 400 hand-written changed lines (`ArchitectureCheck` 220, guard switch 30, `measure.py` columns 80, errors 15, roles table 20) plus a generated baseline of a few hundred lines. **Split** into 1a (core/errors, `rglob`, measure move) and 1b (architecture test and baseline).
- Slice 2: about 450 lines (core 150, outcomes move 40 import edits, look door and bench/operations 130, tests 120). One PR, if the outcomes move is its own first commit.
- Slice 3: about 150 lines (codes, 6 sites in `board_envelope`, contract test, `deploy.md`). One PR. "`parts.py --describe` unchanged" is true by construction, keep it as a cheap guard.

## Verdict

Buildable with stdlib after F1 to F7 are folded in. Without F4 to F6, slice 2 cannot hold `look.py` under 40 lines or express `parts.py`.
