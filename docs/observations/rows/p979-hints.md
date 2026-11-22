# P979: the page's hints a person can act on: rows

Card: [P979 #1411](https://github.com/xmejkal/spark/issues/1411). This file holds the findings of the plan check (the
refuter on Opus), 2026-11-22. All five were acted in the build.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | Row 16 of `tests/mutations/p825-flow-reader.json` looks for the expression the plan removes | plan check, refuter | acted | re-anchored on `return self.phase(PROBLEMS, [str(missing), flow_codes.SCENARIO_HINT])`; `--anchors` over all tables |
| 2 | An image that no run tested still says "run a scenario with run_scenario.py ... run look.py --no-simulation" (`why_untested`) | plan check, refuter | acted | `SimulateReader` gives `IMAGE_UNTESTED_MESSAGE`, keyed on the fact (no failed run on the image), not on the English; `test_a_simulation_fact_says_a_passed_run_tested_the_image_or_why_not`, mutation row 5 |
| 3 | The docs sentence "says never holds a path" is false: a could-not-run line holds the error's own sentence | plan check, refuter | acted | `docs/guide/agents/flow.md` says the hints name the command and who acts and hold no placeholder, and that a could-not-run line is the error's sentence, masked |
| 4 | The deploy hint left out the deploy grant, which answers the person's yes | plan check, refuter | acted | `DEPLOY_HINT` ends "unless your deploy grant answers for you." |
| 5 | `SCENARIO_HINT` would be a near-copy of `SIMULATE_NOW` | plan check, refuter | acted | `SCENARIO_HINT = SIMULATE_NOW`, one text in `flow_codes.py` |
