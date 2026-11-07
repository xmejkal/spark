# P678 the map of the code: rows

What the implementation found while it built W5-2. Card: [P678 #910](https://github.com/xmejkal/spark/issues/910). Plan: `docs/discovery/2026-10-19-p323-target-architecture/architecture/wave5-plan.md`, "W5-2, the map".

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | "The CLIs in `scripts/*.py` that import an area's `OPERATIONS`": no CLI imports `OPERATIONS` | implementer | acted | each CLI imports `build_project_outside_world` and an Operation class. The page lists the Operation classes a script imports as `from spark.<area>.<module> import <Class>`, with the printed `name` read from the class by `ast` |
| 2 | "The map covers core and bench": `scripts/spark/idea/` exists too | implementer | acted | every folder under `scripts/spark/` with an `__init__.py` is listed, so `idea` is on the page, and `parts.py` shows `needs-drop` |
| 3 | "five bench CLIs": the map finds five bench scripts (`deploy`, `grant`, `live`, `look`, `reach`) and `parts.py` for idea | implementer | acted | the page lists what the code imports |
| 4 | "its test file, `tests/test_<module>.py` or none": almost no module has a test of that name (`look_at_board.py` is tested in `tests/test_look.py`), so "none" would say that tested code is untested | implementer | acted | the test cell lists the test files that import the module (`from spark.<area>.<module> import` or `from spark.<area> import <module>`), three at most, then "N more" |
| 5 | The registries are "keys": `parts.OPERATIONS` and `WIRING_VIEWS` are tuples of tuples, `DRAWING_RENDERERS` a tuple of objects | implementer | acted | `Registry` holds a key function per registry (the first field, `FILE_NAME`, or the dict key). The map imports the module that holds it |
| 6 | Mutation row "a registry's keys unsorted": the keys stay in the order the code lists them, because that order is the meaning (the sheet's views, the drawings) | implementer | acted | the row is "a registry loses its first key" instead. "The test compares a prefix" has no meaning, because the test compares the whole page |
| 7 | `docs/guide/developing.md` is at its budget of 379 lines | implementer | acted | the link joins the intro sentence and adds no line. `map.md` takes the default budget |
| 8 | A docstring's first line is often half a sentence | implementer | rejected | the plan says "first docstring line". Kept, because a sentence rule needs more code and the line is enough to find a module |
| 9 | A module that has `AreaMap.of` import `tools.py`-style registries means a test run imports `breadboard` and `parts` | implementer | acted | accepted: the import is the only way to read a key from an object. The test passes a fake registry for the unit tests |
| 10 | A mutation row for `--write` writing nothing | implementer | rejected | `main()` has no test (it only parses and prints, like `journey.py`) |
| 11 | A docstring's first physical line ends mid-sentence ("(P442,") | reviewer, PR | acted | `first_line` takes the first sentence of the first paragraph, cut at 100 characters on a word with "…". Row 8 is superseded |
| 12 | `tests_of` read only `from` imports, and "none" in a column named "Test file" hid tests that import by `import x [as y]` | refuter, PR | acted | `import` forms are read, `test_<stem>.py` comes first, the column is "Tests that import it" |
| 13 | `clis_of` crashed on a script that imports a module that is not there | reviewer, PR | acted | the module is skipped, and the docstring names the one import form it reads |
| 14 | `operation_names` took any class with `name = "..."` (`board_doctor.py` has two that are no Operations) | refuter, PR | acted | a class counts only with `Operation` among its bases |
| 15 | `registries_of` imports the registry module, a cost the page does not need | reviewer, PR | acted | marked `# --- Later, not MVP ---`: reading the keys with `ast` would avoid the import |
| 16 | The module test looked for a file name anywhere on the page, so a name in two areas hid a missing row | reviewer, PR | acted | the test looks in the module's own area section |
