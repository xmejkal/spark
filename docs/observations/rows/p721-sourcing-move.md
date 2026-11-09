# P721 sourcing move (W6-S3b): rows

The claims of the W6-S3b plan are in `docs/discovery/2026-10-19-p323-target-architecture/architecture/wave6-plan.md`
(sections "The four moves, W6-R3a, W6-R3b, W6-S3a and W6-S3b", "W6-S3b, the sourcing move" and the "P721 claims
check"). They were checked against main e35f6b1a before any code. One claim opens a decision, so the build stopped
after the check. Card: [P721 #972](https://github.com/xmejkal/spark/issues/972).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the four lists place the 93 names, and the CLI keeps 9 | plan | verified | a symtable map (locals excluded) over the 108 top-level names: `part_facts` 17, `datasheets` 37, `part_handlers` 32, `goal_handlers` 13, the CLI 9. `printed_names` and `has_placeholder_footprint` go to `part_facts`, the lowest module of their users (`board_emitter`) |
| 2 | every reference points down and no two modules import each other | plan | verified | `part_handlers` reads `datasheets` 9 times and `part_facts` 10, `goal_handlers` reads `part_handlers` 8, `datasheets` 3 and `part_facts` 2. No module reads `parts` after the move: `drawer`, `board_emitter`, `loader`, `assign_pins` and `check_spine` read only `part_facts` names. So the `drawer` <-> `parts` two-way import goes |
| 3 | each module is under 600 lines | plan | verified | bodies before headers and imports: `part_facts` 198, `datasheets` 392, `part_handlers` 388, `goal_handlers` 279, the CLI 215 |
| 4 | the plan's keys, counts and lines | plan | closed | 10 keys, not 9. The three `T1` keys of `parts` follow their code to `datasheets` (`datetime` 2, `subprocess` 1) and `part_handlers` (`file-write` 1). The rows: 42, 18, 81, 78, 26 stay, 12 have no `find` (as on main), `drawer.py` 55. `drawer.py` reads `shelvable` and `shelve` at `:315` and `:332` |
| 5 | a function under `scripts/spark/` is 40 lines or less | lesson | raised | `audit` (42) is 40 when its two lazy imports go. `drawer.settle` (43) is not in the plan and needs one Extract Function before the move, with its lines as they were (P703 row 3) |
| 6 | "no other `print` or `sys.exit` sits outside a `main` after W6-S2" | plan | raised | it holds, but X2 also counts `sys.stdin` under `scripts/spark/`. `_read_json_input` (`parts.py:1002`) reads it, for six handlers. A new `X2` key, an upward import, or new logic: a decision for the caller and the PO, with options (a), (b) and (c) in the claims check |
| 7 | the new module names clash with no binding | lesson | verified | symtable over `scripts/`, `tests/` and `tools/` finds `datasheets`, `part_facts`, `part_handlers`, `goal_handlers` and `drawer` bound as a local, a parameter or an assignment nowhere. `self.drawer` in `drop_need.py` is an attribute |
| 8 | `--anchors` refuses only what main refused | build | raised | 114 refused on main e35f6b1a: the baseline for the build |
