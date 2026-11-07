# P659 the build's time limit fits a real build: rows

What the plan check found, and what the build changed against the plan. Card:
[P659 #885](https://github.com/xmejkal/spark/issues/885). Plan: `~/.claude/plans/p659-build-timeout.md`.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | MUST: the "exit 0" claim was tail's exit code, not the build's, so that decision is gone | plan check, refuter | acted | the plan has no exit-0 decision; the stage stays could-not-run, exit 2 |
| 2 | MUST: one constant served three commands, so the sentence lied for a probe or converter timeout | plan check, refuter | acted | `BUILD_TIMEOUT_S = 900`, `PROBE_TIMEOUT_S = 120`, `CONVERTER_TIMEOUT_S = 120`; `timed_out_sentence` reads `late.cmd` and `late.timeout` |
| 3 | SHOULD: add tsci's last stderr lines to the sentence | plan check, refuter | acted | `timed_out_sentence` adds the last three lines of `late.stderr` (bytes or text) |
| 4 | Every line number in the plan (:88, :179, :458, :557, :723) matched origin/main | build | closed | read before the edit; no wrong plan claim found |
| 5 | The handler's stage is named `build` also for a probe or converter timeout | build | closed | the plan keeps it; the sentence names the real command, so the person is not misled |
| 6 | The push hook refused aaa78527: R1 `<module>` of scripts/check_spine.py rose 1028 to 1039, T2 `mock.patch` in tests/test_check_spine.py rose 35 to 39 | push hook | acted | accepted with `measure.py --rules --accept-new`: check_spine calls subprocess directly and has no seam for a fake run until it moves onto the core (v0.13, #94), so the timeout tests patch `subprocess.run` as the file's other 35 do |
