# P213 b2 bench and buttons: findings rows

The bench walk and the plan council of P213 part b2 (#192). Plan: [`plan.md`](../../discovery/2026-10-19-p213b2-button-places/plan.md).

| # | claim | source | status | evidence / where it went |
|---|-----|--------|-------|------|
| 1 | A new image needs a new look, because the token holds the image's sha256 prefix (ae7b-f34b, then ae7b-94b2): one extra board restart per redeploy | bench walk, 2026-10-19 | verified | by design |
| 2 | The erase retry and the download-mode hint did not fire, so AT313 stays untested | bench walk, 2026-10-19 | raised | a later walk |
| 3 | The doctor's two button steps and grant.py's esptool read also name BOOT and RESET | plan council, round 1 | acted | in scope |
| 4 | A changed fixture test: test_xiao_record.py compares the record's `physical` with a fixture | plan council, round 1 | acted | the fixture gets the field |
| 5 | The doctor's sentences are read by `describe` and `look_stop_envelope`, not by the service | plan council, round 2 | acted | one `step_sentence` |
| 6 | A shape check in `boards.py --validate` and the PortFinder plumbing are not needed for the card | plan council, round 2 | rejected | cut |
| 7 | `download_mode.PRESS_RESET` and `NO_RESET` also name R with no place, and the plan left them out | implementer | acted | templates with `press_reset` and `no_reset`; the plain word is RESET, as in the doctor's steps |
| 8 | `firmware_platform.chip_of` has no caller after `record_of` | implementer | acted | removed |
| 9 | grant.py's restart line says RESET with no place, though grant.py reads the places | review, PR | acted | `RESTART` takes the places; a test |
| 10 | The download-mode sentences name "top left" with no orientation | review, PR | acted | `%(orientation)s` in both; tests |
| 11 | deploy's `--json` watch step says "the board's R button" with no place | review and refuter, PR | acted | `ButtonPlaces.of_project`; the test reads the place |
| 12 | reach.py and live.py still say "press R or replug" with no place | review and refuter, PR | raised | card P321 #410 |
| 13 | An empty `seen_from`, `silkscreen` or `place` prints half a hint | refuter, PR | acted | `_words` needs words; three test cases |
| 14 | The doctor's reset step lost "the board's" | refuter, PR | acted | back |
| 15 | The record is read more than once per run (of_project beside record_of) | review, PR | rejected | a small JSON read; passing it through every caller costs more code |
| 16 | `EsptoolReader`'s default hint is built at import | review, PR | rejected | a constant sentence, built once |
| 17 | NEXT_HOLD_BOOT names BOOT and RESET twice each | review, PR | rejected | the second names are the short form after the place |
| 18 | Mutation: 12 planted, 12 caught (591 s) | mutation, PR | verified | `tests/mutations/p213b2-button-places.json` |
