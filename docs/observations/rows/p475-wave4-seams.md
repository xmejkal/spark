# P475: W4-1, the wave 4 seams

Findings of the P475 (#651) builder, 2026-11-01, Prague, built on main 700f29f5, against `wave4-plan.md` (W4-1). All rows are raised.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The plan's file names (`firmware_platform.py`, `deploy_service.py`, `board_look.py`) sit in `scripts/spark/` | wave4-plan.md, "Files" | raised | they sit in `scripts/` (flat); only `scripts/spark/bench/` and `core/` are in the package |
| 2 | `make_board_reader(hint)` takes the hint alone | wave4-plan.md, Classes | raised | the reader also needs `run`: built as `make_board_reader(run, hint)`, as `make_port_finder(run)` is |
| 3 | `after_esptool(stop, project, platform)` | wave4-plan.md, Files | raised | `project` is `platform.project`: built as `after_esptool(stop, platform, run)`; the doctor also needs the flasher's tool for `silent_step`, so the platform gets `find_tool(role)` |
| 4 | `LookService` takes the platform | wave4-plan.md, Files | raised | `looker(platform, run)` builds the finder and the reader from it, and `LookService(finder, reader)` is unchanged (less churn, same seam) |
| 5 | `deploy.main` takes `platform=` and `clock=` and the records seam fixes the test at :816 | wave4-plan.md, Files | raised | `main` is at its R3 baseline of 6 parameters and `_deploy` at 9, so `records=` cannot be added; the test at :816 now makes the record place a folder, and the seam is tested on `DeployService` (W4-2 builds `DeployService` in the Operation and can carry `records`) |
| 6 | `DeployService` gets `clock` and `records` and keeps `probe` | wave4-plan.md, Files | raised | `__init__` is at its R3 baseline of 7: `probe` went (the platform makes the console probe), `sleep` and `start_clock` went (one `clock`) |
| 7 | T2 goes from 16 to 5 and `find_tool` at :131 stays for W4-2 | wave4-plan.md, Net | raised | true: the five left are :144 (`tools.find`), :478, :667, :823 became a folder (gone), :994 and :1184; the count is 5 |
| 8 | `FakeClock.now` is a number today | tests/fakes.py | raised | it was the monotonic value: renamed `elapsed`; `now()` is the zoned time. Four assertions read `.now` and now read `.elapsed` |
| 9 | `board_grant.read_local_time` becomes `SystemClock().now` | wave4-plan.md, Files | raised | done; T1 `board_grant.py:datetime`, `deploy_service.py:time` and `firmware_platform.py:subprocess` left the baseline |
