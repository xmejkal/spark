# P429: a wokwi.toml firmware line of the wrong type, findings rows

Findings of P429 (#566), 2026-10-27, Prague. From the plan council and the build.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | `sim_project.firmware_in` raised a TypeError in the look when the line was `firmware = 3` | card | acted | it returns a `FirmwareLine(state, name, why)` and never raises. The look says `no token: sim/wokwi.toml names its firmware in a form spark cannot use: line 3 ...`. Pinned by `test_look` |
| 2 | The reader needs a path rule like P397's store-path rule | plan | rejected | `--firmware` may name a path under `sim/` (`tests/test_deploy.py`, `images/flash.bin`), and `run_scenario` has its own "outside sim/" sentence. The reader takes any non-empty JSON string; `TheFirmwareLineTest` pins `../x.bin` as a name |
| 3 | The reader must see every firmware line, not only `firmware = ` at column 0 | council | acted | any line whose stripped text starts with `firmware` and is not `firmware = ` plus a JSON string is NOT_CHECKED. `run_scenario.image_in` lost its own `lstrip()` scan; its ValueError text is kept |
| 4 | A rebuild drops a NOT_CHECKED line without a word, since `wokwi_toml(None)` rewrites the file | council | acted | `check_spine` prints one stderr line through `guard_lines` and still rebuilds (it does not refuse). Not printed when `--firmware` names an image, since that replaces the line on purpose |
| 5 | A missing wokwi.toml is NONE_RECORDED, not NOT_CHECKED | build | acted | a first build has no file, and must print nothing. A folder or bytes that are no text are NOT_CHECKED |
| 6 | `firmware   "x.bin"` (three spaces, no `=`) is read as a name if the reader cuts a line at column 11 without the prefix check | build | acted | the written-form check stays, and the test input is in `TheFirmwareLineTest` |
| 7 | The negative tests ("says nothing") pass on main | build | acted | they are assertions inside the one test that fails on main; no new test passes on main |
| 8 | The reason is shown through the look's guarded lines | plan | verified | it holds a line number and fixed words, never the toml's text. The check_spine line goes through `guard_lines` and a test plants a right-to-left mark |
| 9 | wokwi-cli reads full TOML, spark reads a JSON string | build | raised | a TOML literal string (`'x.bin'`) or a value with a comment after it is valid TOML, and NOT_CHECKED here. The reason says so. A second reader for TOML is not planned |
| 10 | Mutation rows | mutation | raised | `tests/mutations/p429-firmware-line.json` (12 rows), and the rows of p130, p130-followup and p196 that quoted the changed lines now quote the new ones. `--anchors` refuses the same 105 rows as main |
