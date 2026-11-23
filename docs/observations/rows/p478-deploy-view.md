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
