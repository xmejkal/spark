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
| 9 | one read of the check record per show | plan check, lens point 2; review refuter 4 | rejected | dropped because one show takes 0.21 s instead of 0.15 s (median of five), which a person does not notice. The times are in the PR body |
| 10 | one `ast` reader of firmware files; sleep_calls shares the loop and the rebinding rule | council | raised | a card: [P1328 #1906](https://github.com/xmejkal/spark/issues/1906) |
| 11 | the text view prints no assumptions | council | raised | a card: [P1329 #1907](https://github.com/xmejkal/spark/issues/1907) |
| 12 | a scope-aware module-alias rule | council | raised | a card, Idea: [P1330 #1908](https://github.com/xmejkal/spark/issues/1908) |
| 13 | `PIN_MODULE` names two things (import_probe.py:17, kept_files.py:27) | council | raised | a card: [P1331 #1909](https://github.com/xmejkal/spark/issues/1909) |
| 14 | the design-reviewer agent reads `data.pin_map` | council | raised | a card: [P1332 #1910](https://github.com/xmejkal/spark/issues/1910); a comment on P1270 #1829: it reuses `PinMapUses` |
| 15 | a table cell over 300 characters in firmware-codes.md | the build, `tests/test_docs.py` | acted | the two new codes have a row of their own beside the `check_firmware.py` row |
| 16 | with no pins.py the line said "0 of 2 uses found" | review, refuter 1 | acted | `to_data` holds `has_map: false` then, and `line_from` says "pin map: firmware/pins.py is not there, and N uses need it, first F:L". The two check-firmware goldens gain `"has_map":false` (their project has no pins.py). `test_with_no_pin_map_the_line_says_it_is_not_there`, `test_with_no_pin_map_show_says_it_is_not_there_and_not_a_count_of_found_uses` |
| 17 | a name guarded with `hasattr` or `getattr(pins, "X", d)` was a missing use | review, refuter 2 | acted | it is a place in that file. `test_a_name_the_file_guards_with_hasattr_or_getattr_is_a_place_not_a_missing_use`; firmware-codes.md says a read in `try/except AttributeError` still counts |
| 18 | a name bound with `:=` or `globals()` is not seen as bound | review, refuter 3 | acted | one docs line, no code |
| 19 | the word "unseen" in `read` | review, lens 1 | acted | renamed `not_compared` |
| 20 | "not seen" and "cannot see" in the docs | review, lens 2 | acted | "not read at all (no use, no place)" and "What the check does not read" |
| 21 | the variant Code was built from the word | review, lens 3, refuter 5 | acted | `Code(PIN_MAP_NAME_MISSING, ...)`; `test_the_pin_map_variant_has_its_parent_s_word_and_meaning_and_its_own_fix`; the docs name its fix |
| 22 | `line_from`'s docstring | review, lens 4 | acted | three lines, each "None when" |
| 23 | one sentence constant with a plural trick | review, lens 8 | acted | `NO_PIN_MAP_ONE` and `NO_PIN_MAP_MANY`; the new lines of build.md and flow.py rewrapped |
| 24 | the docs section's W8 sentences | review, lens W8 | acted | copies DETAILS' "It compares names only. It never sees whether the pin is wired, right or used right." |
| 25 | "place" means two things (the guide's, and an item the check cannot compare) | review, lens 7 | raised | [P1331 #1909](https://github.com/xmejkal/spark/issues/1909), the card about one name for one thing |
| 26 | the fix round's logic had no mutation rows | final review 1 | acted | six rows: `_guarded` (two), the no-map branch of `line_from`, `has_map` in `to_data`, the one-or-many pair, the no-map branch of `pin_findings`; each caught by hand against its test |
| 27 | the summary, the `run` docstring and check_firmware.py's header did not name the pin names | final review 2 | acted | all three say "the pin names against firmware/pins.py" |
| 28 | the PR body's golden bullet and test counts | final review 3 | acted | the bullet names `"has_map":false`; the counts are the ones seen |
| 29 | `has_map` was undocumented and `_shape_of` refused True | final review 4 | acted | json.md and DETAILS say "false, only when firmware/pins.py is not there"; `_shape_of` accepts a bool |
| 30 | the no-map sentence lived twice | final review 5 | acted | `no_map_sentence` and `NO_MAP_ONE`/`NO_MAP_MANY` in pin_map_uses.py; the finding uses them, the line adds "pin map: ". The line now reads "..., and 1 use needs it" like the finding |
| 31 | flow.py:85 was short | final review 6 | acted | reflowed |
| 32 | patterns-and-names.md and words.md did not name the Value | final review 7 | acted | `PinMapUses` in the Value row (three "(P...)" tags dropped to keep the cell under 300 characters); a words.md row names `missing_pin_line` |
