# P354 a held console blocks the next deploy: findings rows

Findings from planning and building P354 (2026-10-21, Prague). The plan is item 4 of the P351 plan (PR #449). The
council ran two rounds: a tech lead on Sonnet and the refuter on Opus, then one Sonnet agent in three roles.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | deploy.py is the one board script that does not call the board doctor, so a held port gave the hold-BOOT hint | implementer, refuter | acted | `deploy.py` `_deploy` calls `board_doctor.stop_answer` for a `LookStop` |
| 2 | The doctor's lock really fails against a port that mpremote holds on macOS | refuter | verified | a pty held and opened a second time the probe's way gave errno 35, counted as busy; a real USB port is not yet tried |
| 3 | The Ctrl-X words were to be written in three places | tech lead | acted | one constant, `board_console.LEAVE_CONSOLE`, used by the doctor and `WATCH` |
| 4 | The first plan built `fix` from `stop_lines` and a new `reached["fix"]` key, which nothing read | tech lead, refuter | acted | one `stop_answer` call, `reached["doctor"]`, `board_envelope.doctor_fix` shared with `look_stop_envelope` |
| 5 | The test seam named in the first plan did not exist: `main(probe=)` is the download-mode probe | refuter | acted | the tests patch `board_doctor.after_esptool` |
| 6 | A `LookStop` can also come from a second look at the gate in `service.deploy` | tech lead | rejected | `deploy_service.py` `deploy` reads the report it is given and runs no look; the test for it was dropped |
| 7 | The doctor's check line at `board_doctor.py:118` must change to agree with the new step | round 2 | rejected | it already says "another program holds the port" |
| 8 | A busy port during verify's facts copy (mpremote's `failed to access`) still gives no Ctrl-X step | implementer | raised | the look runs seconds before the copy, so the gap is small; no card yet |
