# P1008: a build that built answers as built on the page: rows

Card: [P1008 #1467](https://github.com/xmejkal/spark/issues/1467). Seen in the p934-display2 walk, 2026-11-22 11:40 CET.
The plan check: a lens on Sonnet and the refuter on Opus, one round. This file holds the acted, raised and rejected
findings only.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the answer row says could-not-run for a build that wrote the board, the sheet and the pin map | the walk, row 9 | acted | `run_request.answer_of`: status ok, line `ran <label>: ok`, and `note` the simulation's sentence, by the guide's `stops_only_for_no_model`. Rows 1 to 4 |
| 2 | a crash leaves an older `.spark/build.json`, so a rule that reads the file answers ok for a crashed build | plan refuter 1 | acted | `answer_of` reads the run's own Findings, never the file. The still-could-not-run test writes such an old record. Row 3 |
| 3 | the envelope says could-not-run and exit 2 while `data.status` is ok | plan lens 2, plan refuter 2 | acted | kept, as `flow.py show` keeps the build phase could-not-run. flow.md says to decide on `data.status`, and page.md step 7 names `data.status` |
| 4 | the refusal's data lacks `note`, and two tests pin the whole data | plan lens 1 | acted | `note: None` in the refusal. Both tests updated |
| 5 | the page shows only the kind's ok words, so the note never reaches the person | plan lens 4 | acted | `page_script.js` appends `words.note` ("Note: %s.") when the note is a non-empty string. Row 5 |
| 6 | exit 2 with an ok answer breaks /spark:page | plan refuter 3 | rejected | the refuter's own check: page.md steps 6 and 7 branch on `data.ran` and `data.status` only |
| 7 | the note shows a record's field name ("names no wokwi_part_type") to the person | PR refuter 3 | acted | fixed: the note is the meaning of the code in `NO_MODEL_CODES` |
| 8 | no test covers a board-only build with no Wokwi part, which also answers ok | PR refuter 4 | raised | dropped because the guide counts it done by the same rule, and the MVP needs no more |
| 9 | no mutation row changes the note's value | PR lens | raised | dropped because the built-with-a-note test asserts the note's text |
| 10 | a real build mixes a blocking Finding with the simulation's | PR refuter 1 | rejected | the refuter's own check: `BuildBoard.run` makes Findings only from `findings_of`, keep results are diagnostics |
