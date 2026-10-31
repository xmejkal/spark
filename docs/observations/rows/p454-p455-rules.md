# P454 and P455: a rule below its lowest is refused, and every check reads rules.json through fab.read_rules

Findings of P454 (#615) and P455 (#616), 2026-10-31, Prague, built on main 00a410b6.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | `drill_step_mm: 0` is a ZeroDivisionError in `emit_footprint.hole_diameter_mm` | plan | verified | `needed / step`; now refused when the file is read (test_fab, test_design, test_emit_footprint) |
| 2 | `drill_step_mm: -0.1` is accepted and draws a 0.9 mm hole | plan | verified | refused: `lowest` says above 0 |
| 3 | `annular_ring_margin_mm: 0` builds today | plan | verified | kept: its limit is `at_least` 0 |
| 4 | Readers at check_all.py 132 and 144 | card | verified | 132 reads `pulled_by_firmware`, 144 the physics rules; both use `fab.read_rules` |
| 5 | `check_physics.py:632` reads raw | card | rejected | 632 only builds the path; the raw read was line 640 |
| 6 | `compare_design.py:289` reads raw | card | rejected | 289 was the default path; the read was in `compare` |
| 7 | A list top level gives AttributeError, no file named | card | verified | a traceback alone in the two CLIs; an unchecked line with the type name in `check_all`; now one sentence naming the file |
| 8 | An unreadable file gives a PermissionError without the file named | card | rejected | Python's text names the path; the faults were the traceback and the type-name prefix |
| 9 | A missing file is not touched | plan | verified | all four paths test `is_file()` first |
| 10 | Plating of -0.5 gives a hole of 0.0 mm; a margin of -1 gives a pad of -0.5 mm; a `min_annular_ring_mm` of 0 or below turns the ring check off silently | review | acted | refused by `lowest` |
| 11 | `copper_thickness_mm`, `min_trace_width_mm`, `board_thickness_mm` and `min_via_*` are read at import with no rules, so a project value never reaches them | review | raised | later card: pass `rules` to `copper.py` and `emit_board.py` constants |
| 12 | `init_project.py:331` reads rules.json raw in the `--force` merge | review | raised | stays out: init repairs a bad file, so it must not refuse. Later card: name the file on a bad one |
| 13 | The `check_all.py` line-132 read of `pulled_by_firmware` can never refuse | review | verified | `compare_design.compare` runs first (line 126) and refuses the same file; the swap to `fab.read_rules` has no test or mutation row |
| 14 | `check_physics.py` was at 662 of 662 lines | review | acted | after: 659; `main` 39 to 32; `run` kept at 62; the long comment in `Board.narrowest_by_net` shortened, `--accept-new` not used |
| 15 | The old compare_design sentence "not valid JSON" for a broken rules file | plan | acted | now "could not be read" from `fab.read_rules`; no test or doc asserted the old text; the circuit keeps "not valid JSON" |
| 16 | Buildability's own try is redundant | plan | acted | removed: `Check.run` refuses `fab.RulesError` for every check |
