# P508 (#703): E2a, deploy goldens past the gate: rows

The plan check on the plan of P508, and what the PR did with each, on 2026-11-02 in auto mode. The card grew from XS to S: the bench code changed (a stderr golden, a planted file, a fake erase), not only goldens.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | The design's two goldens (the no-terminal runs) pin the `show_line` and `echo_to` lines | event-seam-plan.md E2a row | rejected | [ran] they stop at the gate, so no `yes:`, `running:`, retry or flash-tool line prints; the plan's own risk 3 says so |
| 2 | A valid deploy grant in the Case's store takes the real deploy.py past the gate | plan check, refuter | acted | [ran] `DEPLOY_GRANT` in `tests/golden_bench.py`; both runs exit 2 after the 5 s retry and print the look, `yes:`, `running:`, the retry line and the failure |
| 3 | The fake esptool needs an `erase-flash` answer on stdout with exit 2, so that `echo_to` is tested | plan check | acted | `tests/fake_modules/esptool/__main__.py`; under `--json` the line lands on stderr |
| 4 | `plant` text must be computed at run time, and clock times need a scrub pattern | plan check | acted | `plant` accepts a callable; `CLOCK` in `scrub` gives `<time>` |
| 5 | `run_case` must collect both reasons before it asserts, so one accept run writes both goldens | plan check | acted | `tests/test_golden_bench.py` `run_case` |
| 6 | The stdout and stderr goldens do not pin the order between the streams | plan | raised | separate pipes; E1's toy test covers the order |
| 7 | Each grant run takes about 5 s (the flasher's real retry wait) | plan check | verified | [ran] the suite grew from about 9 s to about 15 s |
