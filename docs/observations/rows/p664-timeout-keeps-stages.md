# P664: a tool past its limit is the late stage, and the stages before it stand: rows

Card: [P664 #893](https://github.com/xmejkal/spark/issues/893), found by the P659 PR refuter (rows
`docs/observations/rows/p659-build-timeout.md`, row 11). Size XS: one plan check (refuter, Opus), then one refuter on
the PR. This file holds the acted, raised and rejected findings only (rules.md), with the build's own rows. 2026-11-15.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | a converter or probe timeout after a good build replaced every stage with one `build` stage, so the report said the board was not built | card | acted | `board_engine.LimitedRun` turns a `TimeoutExpired` into `TimedOutError`; `convert` returns a timed-out `simulation` stage; `BuildService._run_engine` appends a timed-out `build` stage; the stages before stand |
| 2 | the plan put `subprocess.TimeoutExpired` into build_service, which `tests/test_architecture.py` and T1 forbid | plan check (refuter) | acted | the adapter owns the timeout; build_service catches the spark-owned `TimedOutError` |
| 3 | `board_alone` calls the converter outside the wrapped stages | plan check (refuter) | acted | `convert` returns the timed-out stage itself, so both callers get it; a test on the FireBeetle record |
| 4 | a converter timeout test needed a 120 s sleep or a new `mock.patch` | plan check (refuter) | acted | `BuildService(..., runner=None)` and `convert(..., runner=None)` take the runner, as `TscircuitEngine` does |
| 5 | moving `timed_out_sentence` left five P659 mutation rows without their anchor | plan check (refuter) | acted | re-pointed to `board_engine.py`; `--anchors` passes |
| 6 | the build area page said the timeout propagates to `RequirementsBuildService` | plan check (refuter) | acted | areas/build.md says the late stage is named and the stages before stand |
| 7 | `convert` took six parameters (R3) | build (hook rules) | acted | `workdir` dropped: the kept diagram is `sim_dir.parent / KEPT_DIAGRAM`, as both callers pass the work folder's `sim/` |
| 8 | `sim_project.stage_chips` runs `chip compile` with no limit, so it can hang | plan check (refuter) | raised | — (note only; a hang is not this card's timeout) |
