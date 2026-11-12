# P454 and P455: a rule below its lowest is refused, and every check reads rules.json through fab.read_rules

Findings of P454 (#615) and P455 (#616), 2026-10-31, Prague, built on main 00a410b6.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | `copper_thickness_mm`, `min_trace_width_mm`, `board_thickness_mm` and `min_via_*` are read at import with no rules, so a project value never reaches them | review | raised | later card: pass `rules` to `copper.py` and `emit_board.py` constants — P776: waits on the PO: a PCB-stage bug; the PO says when, the breadboard bar comes first — P776: waits on the PO: a PCB-stage bug; the PO says when, the breadboard bar comes first |
| 2 | `init_project.py:331` reads rules.json raw in the `--force` merge | review | raised | stays out: init repairs a bad file, so it must not refuse. Later card: name the file on a bad one — P776: waits on the PO: a PCB-stage bug; the PO says when, the breadboard bar comes first — P776: waits on the PO: a PCB-stage bug; the PO says when, the breadboard bar comes first |
