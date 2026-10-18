# P291 and P315 time zones: findings rows

The plan councils of P291 (#348) and P315 (#393). Plan: [`plan.md`](../../discovery/2026-10-18-p291-time-zones/plan.md).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | A grant kept in UTC before this change prints `+00:00` on the `yes:` line and in the record | round 1 | acted | `say_in_local_zone` in `who` and `grant.py`'s two "until" lines; a test |
| 2 | A naive test clock stays naive | round 1 | acted, then changed | round 2: the tests give an aware moment with a fixed offset |
| 3 | Two deploys in one second inside a DST fall-back hour share a log file name | round 1 | rejected | it needs two deploys in one second of a repeated hour |
| 4 | `expires_at` across a DST change keeps the old offset | round 1 | acted | `stamp()` calls `.astimezone()`; a test over 2026-10-25 |
| 5 | A function starts with a verb, and the fake says UTC | round 1 | acted | `read_local_time`, `FakeLocalClock` |
| 6 | `.astimezone()` on the deploy moment only served naive test clocks and made tests depend on the machine | round 2 | acted | removed; `PRAGUE_SUMMER` in the deploy tests, `pin_time_zone` in the grant tests |
| 7 | Three anchors in `tests/mutations/p242-deploy-grant.json` stop matching | round 2 | acted | updated; each find matches once |
| 8 | An old UTC grant misjudges expiry against a local clock | round 2 | rejected | aware times compare by instant (refuter ran it in two zones) |
| 9 | No guide lists `"deployed"` or says UTC | round 2 | closed | step 4 shrank to docstrings |
