# P485 honest pass: rows

What the P485 plan council, the build (PR #672), its review and its refuter found. Card: #664.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The card's words "no must line tested" are a fact spark holds | plan council, refuter round 1 | rejected | a `wait-serial` step can test a must line; the line names the missing step kinds instead; card edited |
| 2 | "The firmware starts" is true for every pass | refuter round 1 | rejected | `with_ready_wait` adds no wait when a `- ` line holds both strings, and `verdict()` returns OK on exit 0 without the MATCHED line; the words were dropped |
| 3 | "Only the start was tested" is fair for any scenario with no set-control and no expect-pin step | refuter round 1 | rejected | `write-serial`, `touch` and `take-screenshot` steps test without a pin; the line names only the missing kinds |
| 4 | The card's JSON exists on `run_scenario.py` | plan | rejected | it has no `--json`; the JSON is the look's `data.caveats`, now from the same method |
| 5 | A run with an expect-pin step and no set-control step keeps "passed" (card) | reviewer round 1, plan council | acted | one rule with the look (P345): it prints the set-control caveat; card's Done when edited |
| 6 | Three subjects for one idea ("the passed run's scenario has", "the scenario has", several logs) | reviewer round 1 | acted | the printed line says "its scenario has", the look keeps its two subjects; all three sit together in `run_scenario.py` |
| 7 | A scenario whose steps cannot be counted still prints a bare "passed" | council round 2 | acted | `passed_sentence` prints "passed, but not checked: a step of the scenario has no kind"; test |
| 8 | An `assertIn("verdict: passed")` lets a log that took the printed sentence survive | refuter round 1 | acted | the tests assert `run_record(log)[0] == "passed"`; mutation row |
| 9 | A pass with a caveat could go to stderr unnoticed | council round 2 | acted | test compares stdout with all printed; mutation row |
| 10 | `run_scenario.py` stays under the 600-line module rule | build | rejected | 627 lines after the change; `SimulationLimits` and its constants moved to `sim_project.py` (584 lines left); four `p345-pr2a` rows follow the code |
| 11 | The new tests may read the code's sentences as their expectation | build | rejected | the self-confirmation rule refused five reads; the tests write the text |
| 12 | `docs/guide/agents.md` said the run "prints the same caveat", but its subject differs and the not-checked form was not named | reviewer | acted | "the same rule in its own words", and the not-checked form, in agents.md, build.md and the docstring |
| 13 | The `"passed"` verdict was spelled in five places | reviewer | acted | `run_scenario.PASSED`, used by `verdict()`, `passed_sentence()`, `project_image.py` and `image_evidence.py`; four older mutation rows follow the text |
| 14 | The moved block opened a second MVP marker inside an open one, and its comment told history | reviewer | acted | inner markers dropped; comment says what the constant is |
