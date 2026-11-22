# P979: the page's hints a person can act on: rows

Card: [P979 #1411](https://github.com/xmejkal/spark/issues/1411). This file holds the findings of the plan check (the
refuter on Opus), 2026-11-22. All five were acted in the build.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | Row 16 of `tests/mutations/p825-flow-reader.json` looks for the expression the plan removes | plan check, refuter | acted | re-anchored on `return self.phase(PROBLEMS, [str(missing), flow_codes.SCENARIO_HINT])`; `--anchors` over all tables |
| 2 | An image that no run tested still says "run a scenario with run_scenario.py ... run look.py --no-simulation" (`why_untested`) | plan check, refuter | acted | `SimulateReader` gives `IMAGE_UNTESTED_MESSAGE`, keyed on the fact (no failed run on the image), not on the English; `test_a_simulation_fact_says_a_passed_run_tested_the_image_or_why_not`, mutation row 5 |
| 3 | The docs sentence "says never holds a path" is false: a could-not-run line holds the error's own sentence | plan check, refuter | acted | `docs/guide/agents/flow.md` says the hints name the command and who acts and hold no placeholder, and that a could-not-run line is the error's sentence, masked |
| 4 | The deploy hint left out the deploy grant, which answers the person's yes | plan check, refuter | acted | `DEPLOY_HINT` names the standing yes; reworded in row 9 |
| 5 | `SCENARIO_HINT` would be a near-copy of `SIMULATE_NOW` | plan check, refuter | acted | `SCENARIO_HINT = SIMULATE_NOW`, one text in `flow_codes.py` |
| 6 | A PR runs no rows and commits no ledger line (W3) | PR refuter | acted | the ledger commit is reverted; the five rows were caught by hand, and row 6 below too |
| 7 | Letting a failed run read as untested passed every test | PR refuter | acted | `test_a_run_that_failed_on_the_image_keeps_the_library_s_sentence`; mutation row 6 of `p979-hints.json`, caught by hand |
| 8 | flow.md named the dry run only, not the line `deploy.py` prints | PR refuter | acted | flow.md names both, citing `commands/deploy.md` step 2 |
| 9 | wording lens: "Then" dangles and "grant" is jargon | PR wording lens | acted | `DEPLOY_HINT` is "Claude then gives you the deploy line. Run it in your terminal and type yes, unless you gave Claude a standing yes for this board."; the test and the golden page hold it |
| 10 | `IMAGE_UNTESTED_MESSAGE` and `NO_IMAGE_MESSAGE` lack the action | PR wording lens | rejected | `SCENARIO_HINT` always follows them on the page and carries the action |
| 11 | `DEPLOY_HINT` and `SCENARIO_HINT` should end in `_MESSAGE` | PR wording lens | rejected | `docs/guide/patterns-and-names.md` allows `_HINT` |
