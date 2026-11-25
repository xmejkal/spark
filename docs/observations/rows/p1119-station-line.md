# P1119: the page's station line above NOW: rows

Card: [P1119 #1648](https://github.com/xmejkal/spark/issues/1648), design slice 2. The plan had two council rounds: round 1
had the everyday lens (Sonnet), the architecture lens (Opus) and the refuter (Opus), and round 2 had the refuter and the
architecture lens. The first push's hook failed on D22. The PR review had a lens (Sonnet), the architecture lens (Opus)
and the refuter (Opus). This file holds the acted, raised and rejected findings only. A "row" in the last column is a row
of `tests/mutations/p1119-stations.json`. 2026-11-25.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | Three places and three notes cannot rebuild `done` and `later` byte for byte | plan council round 1, all three seats | acted | Each phase has a place and at most one note, and `names_at` builds both lists from `stations`. The round 2 refuter checked 710 guide calls in 578 tests and found the same bytes each time |
| 2 | "The tests do not change" was false | plan council round 1 | acted | The plan and the PR list each test that changes by design, with the old and the new assertion |
| 3 | The line drew its own places (no now, the two jobs) and repeated the note words | plan council round 1 | acted | `StationsHtmlLine` draws the places as given, and the note words stand once in `flow_codes.STATION_NOTES` |
| 4 | The NOW heading's rename ("NOW (Parts list)") is beyond the card's "Done when" | plan council round 1 | acted | Left out of this card, with a comment on [P1138 #1673](https://github.com/xmejkal/spark/issues/1673) |
| 5 | No note text on the line, because on a phone it would hide and it adds words | plan council round 1 | acted | Reversed by the PO's "Visible note" for D22 (row 13): the note's words stand small and muted under the name, clipped on a phone |
| 6 | KEYS need `status:*`, the design basis needs the plain names, and `missing()` should name a phase with no name | plan council round 1 | acted | `StationsHtmlLine.KEYS`, the phase entries' `name`, and T15 |
| 7 | The test of "no accent" must ban every teal token | plan council round 1 | acted | `test_the_line_uses_ink_and_muted_and_no_teal_token` checks the line's rules against `TEAL_FAMILY` |
| 8 | The two jobs: the breadboard is `now` beside the firmware, so Wiring never shows as done while NOW asks for it | plan council round 2, both seats | acted | `place_of` with `breadboard_place`, the ring on each now station, and `TheStationsTest` |
| 9 | The note table should be keyed by note, and which notes leave a phase out should be an explicit set | plan council round 2 | acted | `STATION_NOTES`, the phase override for no-model, and `LEFT_OUT_NOTES`. The five old label constants are gone, and their rows are anchored again |
| 10 | `no-picks` only before now | plan council round 2 | acted | `note_of` gives it only at the done place, as `test_no_picks_is_given_only_before_now` pins |
| 11 | On a phone the names are clipped, so a caption must name the now station | plan council round 2 | acted | `<p class="stations-now">` with `nowrap`, and `test_on_a_phone_the_names_are_clipped_the_marks_small_and_the_caption_shown` |
| 12 | Should the line show the steps spark does not have yet? | plan council round 2 | acted | The PO's answer in the question dialog: "Nine plus three greyed". `UNBUILT_STEPS` moved to `flow_codes` |
| 13 | The first hook failed on D22: `data.guide.done[1]` stood in no page text | the builder's first push | acted | The PO's "Visible note": the line shows the note, and the developer fold keeps DONE and LATER. `tests/test_flow_reading.py` is unchanged |
| 14 | The mark is hidden from a screen reader, so a station says neither its place nor its status | PR review, lens 1 | acted | Fixed: a clipped `STATION_SAID` span after each name, with `test_each_station_says_its_place_and_its_status_word_to_a_screen_reader_only` and two rows |
| 15 | The note is clipped on a phone | PR review, lens 2 | rejected | dropped because the PO's "Visible note" option said so |
| 16 | The width of 360px is not checked | PR review, lens 3 | acted | Fixed: the coordinator's Chrome check is recorded in the PR body. At 370px the line was 338px wide with no side scroll |
| 17 | The escape of DONE and LATER in the developer fold is not tested | PR review, lens 4 | acted | Fixed: the escape test asserts both escaped lines inside the fold |
| 18 | The NOW heading keeps a code word | PR review, lens 5 | acted | Fixed: `artifact-how-to.md` item 9 says the heading and the developer fold keep the phase words, and P1138 #1673 owns their rename |
| 19 | "no simulation" is unclear words | PR review, lens 5 | rejected | dropped because these are today's words and P1138 #1673 owns the words |
| 20 | "spark cannot see it" is unclear words | PR review, lens 6 | rejected | dropped for the same reason as row 19 |
| 21 | The fallback name (the phase word) is not a plain word | PR review, lens 7 | rejected | dropped because only a phase outside the nine reaches it |
| 22 | `flow.md` needs a reflow, and `json.md` should list the keys | PR review, lens 8 | rejected | dropped because `flow.md` is at its 400-line limit and `json.md` points to `flow.md` |
| 23 | The no-model fact stands three times above the folds | PR review, architecture lens 1 | raised | A comment on [P1135 #1670](https://github.com/xmejkal/spark/issues/1670) |
| 24 | The muted line is a method of one Renderer that another calls | PR review, architecture lens 2 | acted | Fixed: the module-level `_muted_line` beside `_text` and `_fold` |
| 25 | The parameter `wiring` names a place, not the wiring | PR review, architecture lens 3 | acted | Fixed: `breadboard_place`, with three rows anchored again |
| 26 | The moments of the unbuilt steps stand in `flow_codes` | PR review, architecture lens 4 | rejected | dropped because the approved plan's table shape is (key, name, moment) |
| 27 | Phases left out of every list are drawn as done | PR review, refuter 2 | rejected | dropped because the PO's verdict "its ok" was on a screenshot that drew Wiring with `no-sheet` so, and row 14 now says each status to a screen reader |
| 28 | Mutation rows 9 and 24 are caught by a KeyError | PR review, refuter 4 | rejected | dropped because the named test catches them |
| 29 | The PR has no rows file | PR review, refuter 6 | acted | Fixed: this file |
| 30 | The two jobs give two `aria-current` | PR review, refuter 7 | rejected | dropped because both stations are now |
| 31 | `flow.md` needs a reflow | PR review, refuter 8 | rejected | dropped for the same reason as row 22 |
