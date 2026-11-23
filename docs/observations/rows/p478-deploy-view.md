# P478: deploy.py's text view, slice 1: rows

Card: [P478 #656](https://github.com/xmejkal/spark/issues/656). Two plan rounds (round 1: the UX and AI-UX lens, the
architecture lens and the refuter; round 2: the refuter), then the build of slice 1. This file holds the acted, raised
and rejected findings only (rules.md). 2026-11-23.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | A new `print` in a `_said` helper and passing `os.environ` from `run_cli` would be new X2 and T1 breaches | plan round 2, A and B | acted | `run_cli` prints the View's text itself, and `Terminal.text_style(environ=None)` reads the environment inside the Adapter. `measure.py --rules` shows no new breach; the one rule change is `TERMINAL_CLASSES` gaining `TextViewReporter` |
| 2 | The deploy harnesses build `outside=` with `TerminalReporter.for_json`, so the view's Reporter never reaches deploy there | plan round 2, C | acted | test_deploy_gate's and test_deploy's `deploy` take `view_for(...).reporter`, as `run_cli` gives it; the changed tests are named in the PR |
| 3 | Rows lose their anchors when their code moves | plan round 2, D | acted | re-aimed: p507 "a BEGIN that prints", p423 "the terminal prints an event's text as it is", p476 "the gate has no why", p1032 "a rich paint that raises is not caught" and "the headline's sentence skips printable", p677 "run_cli never masks the result", p726 "the payloads are not loaded"; p476 "the why line comes before its BEGIN" names its new catcher. `--anchors` refuses no row that main accepts |
| 4 | `first_sentence` cut only at `. `, so `you answered no.` would print `..` | plan round 2, E | acted | the last dots are dropped; test_deploy_service.TheDeployViewTest holds both cases |
| 5 | The plan's dry-run words, "nothing ran", are untrue with `--no-simulation`, whose compile child runs | plan round 2, G | acted | `Dry run: nothing was flashed, and the board was not looked at.` |
| 6 | `announce=False` must apply only to the reads inside `wait_for_start`, not to the READ_AGAIN read | plan round 2, F | raised | slice 2 of #656 (the next PR) |
| 7 | A LINE painted through rich as `fact` could change its bytes (rich expands a tab) | the build | acted | `TextViewReporter` prints a LINE plain, as `TerminalReporter` does; only the heading goes through the painter. Test 1 holds for any painter |
| 8 | patterns-and-names.md is at its line budget (279) | the build | acted | the new words are one-line paragraphs, and the class diagram gains the Reporter seam in relation lines |
| 9 | The hook on aaa546cf failed two tests the plan does not name: the help test pins the why sentence last, and test_self_confirmation refuses a test that reads ready_probe's verdicts | the build, the hook | acted | the new help sentences come before the why sentence, and TheDeployViewTest writes the verdict words; no existing test changed (3739fc47) |
| 10 | `DeployStage` has no `endings`, so a doc_blocks stages block over `DeployImage.stages` raises AttributeError where main gives a BlockError | the review, refuter 1 (Opus) | acted | `DeployStage(name, summary, endings=())`, and `test_a_stages_block_renders_deploy_s_stages` runs `StageMarkdownTable.render(DeployImage.stages)` |
| 11 | "What to try is above." is true only when the ready_unknown fix line was said; a start code (the port gone) prints no fix line | the review, lens 1 (Sonnet) | acted | `TRY_ABOVE` is added only for the reason `ready_unknown`; a `port_gone` case in TheDeployViewTest has no pointer |
| 12 | `TerminalReporter.for_json` has no caller in scripts/ now | the review, refuter 2 (Opus) | acted | dropped, with test_core's `test_for_json_picks_stderr_and_stdout_without`; `view_for`'s `--json` stream is tested in test_view_reporter.TheViewTest, and p507's row "a LINE on stdout under --json" is re-aimed at `view_for` |
| 13 | scripts.md appended deploy's text view to the look's bullet | the review, lens nit 5 | acted | its own bullet |
| 14 | The dry run's lone `[1/5]` heading, and a pointer for ready not seen | the review, lens nits 2 and 3 | raised | P1052 #1544, the reword card |
