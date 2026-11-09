# P708 the module splits and the end of the upward imports of onboard_parts: rows

A move-only card: `board_emitter` becomes four modules, `needs` two, `physics_check` two, and `onboard_parts` gives its
converter half to `build/board_alone_input`. Card: [P708 #955](https://github.com/xmejkal/spark/issues/955). Rows 1 to 12
come from the Council section of the plan: the names lens on Sonnet, the refuter on Opus, and its second round. That
section lists the findings in short form, so each row says it in that form.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the first draft's module name changes to `board_components` | names lens | acted | `design/board_components.py` |
| 2 | `board_alone_input` is the name of the converter half | names lens, round 2 | acted | `build/board_alone_input.py`; the function `build_service.board_alone` keeps its name |
| 3 | `supply_net_of` goes to `power_rails` | names lens | acted | `design/power_rails.py` holds it |
| 4 | the split table names each definition, so that no name is left without a home | names lens | acted | the table in the plan and `cut.py`, which stops on a name with no home |
| 5 | two callers need a hand edit: `drop_need` calls `self.needs.parts_left_listed` on an injected module, and `goal_handlers` reads `needs.board_emitter.DEFAULT_BODY_MM` | refuter | acted | `drop_need` imports `need_requirements`, `goal_handlers` imports `board_components` |
| 6 | the `replace` text of mutation rows holds the old names too, and `--anchors` reads only `find`, so a stale `replace` scores a false catch | refuter | acted | each row's `find` and `replace` had the same rewrite |
| 7 | the refused count is 112, not 114 | refuter | acted | `--anchors` at 264af855: "3056 mutation(s) in 243 table(s): 112 would be refused" |
| 8 | the order of the baseline commands: `--accept` writes nothing while new keys exist | refuter | acted | `--rules --accept-new` after reading `--rules`, see row 15 |
| 9 | the table left names without a home | refuter | acted | `cut.py` puts each top-level name in one module, and the proof script finds no name with two homes or none |
| 10 | a from-import keeps a stale name working, so the proof has to search for each old name | refuter | acted | the proof script: 0 stale `old.name` and 0 `from old import name` in `scripts/`, `tests/`, `tools/` |
| 11 | the split makes import cycles | refuter | rejected | the AST pass found none, and each module imports alone in `test_architecture` |
| 12 | `board_alone` clashes with the function `build_service.board_alone` | refuter, round 2 | acted | the module is `board_alone_input` |
| 13 | the row "design loaded by path again" (`sprint-3-p13`) anchors on two import lines of `check.py`, which the rewrite changed | build | acted | its `find` and `replace` name `board_components`; the row names no moved function, so the text rewrite could not reach it |
| 14 | 14 rows of the moved modules hold a `find` that no module holds | build | closed | each is a refused row on main already (`anchors-main` at 264af855), and the card did not touch them |
| 15 | `--accept-new` once at the end leaves `test_architecture` failing at the middle commits | build | acted | the coordinator's answer: run it in each commit that changes a key, after reading `--rules`. Keys changed: physics (R1 `<module>` and R6 `Board` gone), needs (R1 `<module>` gone), emitter (R1 `<module>` gone; R2 `host_part_lines`, R3 `emit` and R3 `power_trace` changed file) |
| 16 | a marker that opens in one block and closes in another has to stay right after the cut | build | acted | the `needs` blocks at lines 174 and 353 stayed whole in `needs.py`. Each new module has one `# --- MVP ---` block around its moved code |
| 17 | the proof compares every top-level block with its new home | build | acted | 175 blocks compared, 0 problems: same text apart from imports, the new docstrings, the two renames and `Board`'s role word |
| 18 | the kept comments of `copper.py` and `loader.py` named `board_emitter` for a job that moved | build | acted | `board_sections` sizes traces, and `board_components` decides a component's name |
| 19 | a new line in `how-it-works.md` put the page over its budget of 277 lines (`test_docs`) | build | acted | the new module shares the line of `needs.py`, and the budget stays |
