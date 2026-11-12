# P743 `--need` matches the drawer's functions and the boards by default: rows

Card: [P743 #1019](https://github.com/xmejkal/spark/issues/1019), story, under P735, D15. Plan `~/.claude/plans/p743-need-store.md`. Rows 1 to 13 are
the plan reviewer (Sonnet: architecture, names, UX, callers), 14 to 19 the plan refuter (Fable), 20 to 24 its second round, 25 to 29 the
implementer, 30 to 37 the PR reviewer (Sonnet) and the PR refuter (Fable), 38 the implementer. 2026-11-11.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the seven stale anchors of row 25 are stale on main too (a main worktree, same names); `in` cannot tell the layer "project" from a project registered as `project`: the PO's projects.json holds scratch projects `project`, `b`, `p`, `p138`, `walk` | PR refuter (Fable) | raised | housekeeping: drop the scratch projects from projects.json; a chore for the stale anchors — P776: waits on the PO: Scratch projects in the PO's projects.json: the PO decides what to drop. — P776: waits on the PO: Scratch projects in the PO's projects.json: the PO decides what to drop. |
