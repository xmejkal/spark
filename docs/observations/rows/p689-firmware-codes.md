# P689: a LittleFSError traceback and an unreadable firmware line get their own codes: rows

Card: [P689 #930](https://github.com/xmejkal/spark/issues/930), a bug under #94 (v0.13, one core), found by P684's review. Plan
`~/.claude/plans/p689-firmware-codes.md` (XS: one plan check on Sonnet, one PR refuter on Fable). This file holds the acted, raised and
rejected findings only (rules.md). 2026-11-12.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | "do not fit" guesses the cause: a 300-character name gives `LittleFSError -36: LFS_ERR_NAMETOOLONG`, a 3 MB file `-28: LFS_ERR_NOSPC`; the look's sentence at `image_evidence.py:421` guessed the same | plan check | acted | the code is `files_not_written`, the sentence "the files were not written into the image's 2 MB file system: <littlefs' own text>", the class `FilesystemError` beside `filesystem()` |
| 2 | the plan's test fixture (`test_flash_image.py:340-401`) uses `mock.patch`; `EachRefusalHasItsCodeTest` (`:604`) calls `make_image` on a temp folder with a fake interpreter | plan check | acted | the two new tests sit there |
| 3 | the mutation row `p337b-no-simulation.json` "littlefs-uncaught" anchors on the line that goes; `developing.md:123` says a weak fixture is fixed, not a mutation dropped, and a removal is right only when the mutated code is gone | plan check | acted | the row removed, said here; `p689-firmware-codes.json` "littlefs-error-escapes" does its job in `image_builder`, noticed by test_flash_image's two tests and test_image_evidence's big-file test |
| 4 | `core.errors.CodedMessageError` is an `Exception`, not a `ValueError` (`text_guards.py:42`), so reusing it would widen three except sites; a `ValueError` subclass with a class `code` is `InterpreterError`'s shape (`image_builder.py:64`) | plan check | closed | the plan's choice confirmed: `FilesystemError`, `FirmwareLineError` |
| 5 | case 2 of `image_in` (no firmware line, no placeholder) stays `run_input_unusable`: `project_image.py:41-55` gives `firmware_line_bad` for an unreadable line and an image outside `sim/` only | plan check | closed | `test_run_scenario.py:1197-1203` unchanged |
| 6 | `SPARK_ACCEPT=flash-image` is matched by `golden_bench.op_of` (the script's stem), and `golden_firmware.py:8` names run-scenario alone as its example | plan check | closed | the golden accepted that way |
| 7 | the plan said the look's sentence becomes "<image> could not be checked: …"; `CANNOT_CHECK_MESSAGE` is "cannot check %s against firmware/: %s" (`image_evidence.py:47`) | build | acted | `test_image_evidence`'s big-file test asserts the real form |
| 8 | `test_json_contracts.test_agents_md_names_every_code` wants every firmware code in a guide page | build | acted | `firmware-codes.md` names `files_not_written` in both rows |
| 9 | `--anchors` refused `p130-followup.json`'s row on `image_in` (`raise ValueError(` after NOT_CHECKED) | build | acted | re-aimed on `raise FirmwareLineError(` |
| 10 | R2 (nesting at most three deep) refused `filesystem` at four with the try around the loop | build | acted | the per-file write is `write_file(fs, destination, content)`, the try wraps the loop alone |
| 11 | `test_docs`: a table cell of 379 characters in `firmware-codes.md:13`, over 300 | build | acted | shortened to the codes and a few words each |
| 12 | `run_scenario.py` prints the sentence alone, so no run-scenario golden can show a code; the flash-image golden shows the traceback gone, `flash-image-could-not-run-files-not-written.txt` | build | closed | the golden: one stderr line, exit 2 |
| 13 | the README's journey table and `tools/journey.py` do not move: no step's status changes | build | closed | nothing to edit |
