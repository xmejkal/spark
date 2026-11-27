# P882: check-firmware compares the pin names the firmware uses with the pin map: rows

Card: [P882 #1250](https://github.com/xmejkal/spark/issues/1250). This file holds the acted, raised and rejected findings
only: the plan check's fixes, the delegated council's fixes (2026-11-27) and what the build found. 2026-11-27.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `from pins import LED` then `LED = Pin(LED, ...)` hid a use that the check could compare | plan check, refuter fix 1 | acted | a from-import's names are always compared, at the import's line; the rebinding rule applies to the module alias only. `test_a_from_import_is_compared_when_the_file_binds_the_name_again`, mutation row 4 |
| 2 | an uncompared use read as a pass | plan check, refuter fix 2 | acted | the line counts the places (`not compared in 2 places, first ...`) and each is an assumption. `test_a_use_it_cannot_compare_is_an_assumption_and_a_line_and_the_status_stays_ok` |
| 3 | show's finding takes `says[0]` | plan check, refuter fix 3 | acted | the pin line comes first, then the written line. `ThePinMapTest` |
| 4 | the contract scan reads only firmware_check.py and pins six codes | plan check, refuter fix 4 | acted | `CheckFirmware.pin_findings` builds the Findings; the test names eight codes. The scan also refused an explicit `fix=` on `Finding.of`, so the no-pins.py problem has its own variant Code (`PIN_MAP_NAME_MISSING_NO_MAP`, the same word and meaning, P935) |
| 5 | names: "pin name" already means a part's pin | council F3 | acted | `PinMapUses`, `pin_map`, `pin_map_name_missing`, `pin_map_not_read`, `not_compared`; no "unseen" |
| 6 | the data shape belongs to the Value | council A1, A3 | acted | `PinMapUses.line_from(data, missing_only=False)` is the one reader of the shape and the one template; checks_reading only tests currency. `missing_only` is a keyword of it, so the flow needs no second method |
| 7 | the sentences a person reads | council W1 to W8 | acted | the finding, fix, line, place and parse-error sentences are as the council gave them; `pin_findings` and `line_from` tests pin each |
| 8 | the pin line shows twice in `flow.py show` | council A4 | acted | on purpose: in the free checks' line and as the firmware phase's first line. Named in the PR body. `test_the_free_checks_line_says_the_pin_line_too_so_it_shows_twice_on_purpose` |
| 9 | one read of the check record per show | plan check, lens point 2 | raised | a card, only if the PR's timing shows a cost; the PR gives one time before and after |
| 10 | one `ast` reader of firmware files; sleep_calls shares the loop and the rebinding rule | council | raised | a card (spark-main files it) |
| 11 | the text view prints no assumptions | council | raised | a card (spark-main files it) |
| 12 | a scope-aware module-alias rule | council | raised | a card, Idea (spark-main files it) |
| 13 | `PIN_MODULE` names two things (import_probe.py:17, kept_files.py:27) | council | raised | a card (spark-main files it) |
| 14 | the design-reviewer agent reads `data.pin_map` | council | raised | a card (spark-main files it); a comment on P1270 #1829: it reuses `PinMapUses` |
| 15 | a table cell over 300 characters in firmware-codes.md | the build, `tests/test_docs.py` | acted | the two new codes have a row of their own beside the `check_firmware.py` row |
