# P516: step S runs init first

The rows of P516 (#712), the walk 4 council's N5a: the idea page runs `/spark:init` with no board before step S reads the brief, so the goal the person gave lands in `project.json` at step S. A page change only, written by the lead in the PO's full auto mode on 2026-11-02.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | `/spark:init` needs a board, so it cannot run before step S. | walk 3 row 4 | rejected | the lead ran `init_project.py --project <scratch>` with no `--board` and a scratch store: exit 0, `.spark/project.json` (`goal: null`, `must: []`, `board: null`) and `rules.json` written, the project listed in `projects.json`. `--board` reads "omit to see what is available" |
| 2 | Step L's `/spark:init --board <pick>` keeps a brief that an early init wrote. | lead's check | verified | the second run with `--board firebeetle2-esp32s3` and no `--force` wrote `boards/active.json` and kept the goal written in between |
| 3 | `commands/idea.md` has 112 older hits of the simple-english lint, none in the lines P516 changed. | the lint hook on the edit | raised | row only: for the docs council P498 (#682) |
