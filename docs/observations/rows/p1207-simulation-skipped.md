# P1207: a board with no Wokwi part ends the simulation stage `skipped`, and the build exits 0: rows

Card: [P1207 #1756](https://github.com/xmejkal/spark/issues/1756), under P1190 #1735. The PO chose on 2026-11-26 to
build it before the `Simulator` seam P1212 #1761. The plan had two rounds: a lens (Sonnet) and the refuter (Opus), then
the refuter on the revised parts. The build's review had a lens (Sonnet) and the refuter (Opus). This file holds the
acted, raised and rejected findings only. A "row" is a row of `tests/mutations/p1207-simulation-skipped.json`, counted
from 1.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | After the flip, `answer_of` read `result.findings[0]`, which is empty on an ok build: an `IndexError` on this card's board | plan lens, plan refuter | acted | `answer_of` reads the run's own stages through `stops_only_for_no_model(result.data)`. Row 6 plants the old condition |
| 2 | `result.data["stages"]` raises `KeyError` in fakes whose data has no stages | plan refuter, second round | acted | the rule reads `.get("stages") or []`. The refuter of the build probed `{}`, `None` and `{"stages": None}`: no crash |
| 3 | The closing line copied the reason's words | plan refuter, second round | acted | `SKIPPED_SIMULATION_LINES` builds it from `BOARD_NOT_IN_WOKWI.meaning` |
| 4 | `json.md:145`, `flow.md:97`, `boards/README.md:256`, `journey.svg` and two code comments still said the old ending | plan lens and refuter | acted | each one changed in the build |
| 5 | A board-only build with no Wokwi part reaches the board-only sentence first | plan lens | acted | `test_a_new_board_only_record_of_a_board_wokwi_has_no_model_of_is_done_once_with_the_board_only_sentence` |
| 6 | `mutate.py --retarget` would move about 20 p977 rows that stay in `guide.py` | plan refuter | acted | the moved rows were edited by hand |
| 7 | `test_check_spine`'s board-alone test still expected `could-not-run` | build | acted | renamed to `test_a_board_wokwi_cannot_show_is_skipped`: D11 changes its expectation, as it does for `test_build_service.py:419` |
| 8 | The README's Build row lost "drawn from records" and then "ground" to fit its 300-character cell | build, build lens | acted | the cell keeps "Modules from records (P945), power, ground on rails (P953)" and P1207's date, which the journey picture reads, in 298 characters |
| 9 | p1008's row on `line = RAN_LINE % ... if note else line_of(...)` survives: a note now exists only for an ok run, and no Finding is ok, so the branch is dead | build refuter | acted | the line is `line = line_of(offer.label, result)`, and the row is gone. The P829 row on the same call (`p829-run-request.json`, entry 12) is re-anchored on it and still caught (3 failures of `test_run_request` when planted) |
| 10 | The fallback comment of `SKIPPED_SIMULATION_LINES` describes a case that cannot happen today | build refuter | acted | the comment says a skipped simulation has one of the two codes today |
| 11 | The hook failed: `phase_readers.py` grew to 610 lines (R1, at most 600) | the hook, 6bb3c3f4 | acted | the rule moved to its own module `scripts/spark/flow/no_model.py`, and `phase_readers.py` has 597 lines. Rows on the rule point at `no_model.py` |
| 12 | The hook failed: three new tests read the code's own constants as their expectation | the hook, 6bb3c3f4 | acted | each test states its sentence as a literal |
| 13 | The hook failed: `docs/guide/map.md` was stale | the hook, 6bb3c3f4 | acted | `tools/map.py --write` |
| 14 | `GLOSSARY.md:72` said only `check_all` has `skipped`, but build stages have it too | plan writer | acted | the heading is "`skipped`, the fourth word, for a check or a stage", its two links follow, and one sentence names the build's skips |
| 15 | `flow.md:50` restarts with "Else" in the middle of a long line | build lens | rejected | the page is at its 400-line budget, so a split would break it. The line is correct |
| 16 | The ok-pick test passes on the old code too | build lens | rejected | it exists to catch the p1008 row that drops the `kind ==` check, which its docstring says |
| 17 | p1207 row 3's name must say which test catches it | build lens | rejected | its name already names the new-record tests of `TheGuideTest` |
| 18 | `flow.py show` prints the "No simulation" sentence under the build and in the guide | build refuter | rejected | by design: the build phase says its own state, and the guide says what to do |
| 19 | The role turned off (D11's second half) | plan writer | raised | [P1214 #1763](https://github.com/xmejkal/spark/issues/1763), comment of 2026-11-26 |
