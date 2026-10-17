# P239 PR 4: named results and honest consent (#238)

## Context

PR 4 of the synthesis (docs/observations/2026-10-14-p239-oo-council/synthesis.md). PRs 1-3 are merged. I read main at
2ca0410. All five items still apply. `--help`, exit codes and the store record's field names do not change.

| Item | On main | Touches |
|---|---|---|
| `ReadyResult` | `ReadyCheck.check` returns a bare 3-tuple, glued to `(facts, facts_line)` in `read_board` | ready_check.py, deploy.py |
| `DeployPlan` | `plan()` returns a 3-tuple, unpacked twice (once with `_`) | deploy.py |
| `BoardLog` | `keep_board_log` takes 7 arguments and reads the clock | deploy.py |
| `ConsentStrategy.who` | `record_deploy` writes "typed in a terminal by <user>" whatever the yes was; `yes_by` is never passed | deploy_gate.py, board_facts.py, tests/fakes.py |
| Clock injected | `facts()` and `keep_board_log` read the clock | board_facts.py, deploy.py |

## Council

Round 1 ran: tech lead (Sonnet) and refuter (Opus). It changed:
- The clock has two names: the parameter `clock` (a callable) and the value `moment`. `main` reads it once.
- `RunLog` became `BoardLog`, which holds no `ReadyResult`.
- The download-mode branch changes only the sentence and the log, so it uses `_replace`.
- `who` is a property of `TerminalConsentStrategy` with a named constant for its text.
- Tests: no tuple guard, literal golden strings, one test for the dropped `yes_by`.
- Four mutation anchors on the removed `read_board` line are re-anchored. developing.md:246 changes.

Round 2 ran: tech lead and PO assistant (Sonnet). It changed:
- `BoardLog` is a Value (facts, no actions) with `text()`. A function `write_board_log(project, log, moment)` saves it.
  Golden test 7 checks `text()` alone, with no file system.
- `image_sha256` is computed in `main` (the old code hashed the image in the log call). `heard + ready.log` make the
  `heard` field, so the text stays byte for byte today's.
- One `moment` per `main` is a deliberate change: `read_board`'s retries now write the same `deployed` time.
- The plan is trimmed to about 90 lines.

## Design

```
 deploy.main --parses, prints, maps the exit code
   |-- plan() ---------------> DeployPlan   (Value)   commands, mpremote, notes
   |-- ConsentStrategy -------- .who  (str)  "typed in a terminal by petr"
   |       `- TerminalConsentStrategy
   |-- read_board(.., moment) -> ReadyCheck.check() -> ReadyResult (Result) verdict, sentence, log
   |-- BoardLog (Value) -------- .text() -> str ;  write_board_log(project, log) -> Path
   `-- board_facts.facts(.., moment) / record_deploy(facts, verdict, who)
```

| Class | Role word | File | Job |
|---|---|---|---|
| `ReadyResult` | Result (namedtuple) | ready_check.py | `verdict`, `sentence`, `log` of one check. `check` returns it. |
| `DeployPlan` | Value (namedtuple) | deploy.py | `commands`, `mpremote`, `notes`. `plan` returns it. |
| `BoardLog` | Value | deploy.py | Facts of the board's log: `moment`, `port`, `image_sha256` (hashed in `main`), `facts_line`, `verdict`, `sentence`, `heard` (the console text, then `ready.log`). `text()` is the file's text. |
| `write_board_log` | function | deploy.py | Saves `text()` in sim/runs/board/ under `log.moment`'s name, and returns the path. Replaces `keep_board_log`. |
| `ConsentStrategy.who` | abstract property | deploy_gate.py | Who said yes, as a phrase. `TerminalConsentStrategy.who` is a property that reads `getpass.getuser()` when asked (so only when the record is written), with the constant `TYPED_BY = "typed in a terminal by %s"`. |

Why `BoardLog`, not the synthesis's `RunLog`: `image_check.run_logs` means the scenario logs in sim/runs/. This file
is in sim/runs/board/ and the output calls it "board log:". It takes verdict and sentence as arguments and holds no
`ReadyResult`, so it does not depend on ready_check.

Changes: `check` returns `ReadyResult` on all six lines. `read_board` and `put_facts` take `moment` and pass it to
`facts(project, board, mac, image, files, moment)`, which has no clock. `read_board` returns `(facts, facts_line,
ReadyResult)`. The no-reset branch (`NO_RESET`) uses `ready._replace(sentence=..., log=...)`. `main(..., clock=None)`
reads `moment = (clock or datetime.datetime.now)()` once. `record_deploy(facts, verdict, who)` requires `who`, and
`yes_by` and `getpass` leave board_facts.py (`getpass` moves to deploy_gate.py). The field stays `yes`. The board log's time is now the moment `main` read the clock, before `read_board`. It can be earlier than before by up to the reset wait (about 60 s). This is a deliberate change. `FakeConsent` is
duck-typed and gets `who = "a test"`.

## Tests first (red before the fix)

1. test_ready_check.py: each verdict path returns a `ReadyResult` whose `.verdict`, `.sentence` and `.log` read by
   name. Red today: a plain tuple has no `.verdict`.
2. test_deploy.py: `plan(...)` returns a `DeployPlan` with `.commands`, `.mpremote` and `.notes` by name.
3. test_deploy_gate.py: a real `ConsentStrategy` subclass made in the test, without `who`, cannot be built.
   `TerminalConsentStrategy("x").who` starts with the literal "typed in a terminal by ". The test never imports
   `TYPED_BY` (tests/test_self_confirmation.py).
4. test_deploy_gate.py (line 454 today): a deploy with `FakeConsent(True)` records `yes == "a test"`. Red before
   the fix. This test also covers dropping `yes_by`: no argument can set the `yes` any more. A deploy with the
   terminal consent records the literal prefix and the user.
5. test_deploy_gate.py: `main(..., clock=lambda: fixed)` gives the facts file's `deployed`, the log's file name and
   its header line the fixed time. Red today.
6. Facts tests (in test_deploy_gate.py's `TheFactsAfterTheFlashTest`, or a new test_board_facts.py if none fits):
   `facts(..., moment)` uses `moment`. `record_deploy(facts, "ready seen", "a test")` writes that `yes`. A malformed
   record still raises `StoreProblem`. They reuse the SPARK_HOME helper of the existing tests.
7. Golden: `BoardLog(...).text()` as a literal string, for a ready-seen log and for a no-reset log (`NO_RESET`).
   Pure text, no file system. The text is byte for byte today's. A deploy test also reads the no-reset file.
8. Mutation file tests/mutations/p239-pr4.json: `who` ignored in `record_deploy`, the clock read inside `facts`,
   `ReadyResult`'s `sentence` and `log` swapped, and `_replace` dropped in the no-reset branch.

## Verification

- Four finds target the removed line `facts, facts_line, verdict, sentence, said = read_board(...)`:
  tests/mutations/p243-download-mode.json:65 and p245-read-after-ready.json:35, 41, 53. This PR re-anchors them.
- `python3 tools/mutate.py --anchors` on the deploy mutation tables must pass. Five rows in p215-link and p219-gate
  were already stale on main. They stay for P284 (#331).

## Docs

developing.md:246 says `ReadyResult` "does not exist yet": update that line (the rules and table stay). agents.md,
journey.md, how-it-works.md:220 and commands/build.md:319 stay true, since the `yes` field and the printed lines do not
change. New classes get a role word first in their docstrings. No README or journey.py change.

## Out of scope

PRs 5 to 8 (`ProjectImage`, `DeployToken`, `Flasher`, `DeployService`). board_grant.py:129 writes
`getpass.getuser()` into the grant, not `consent.who`: a later card. No change to `--json` or exit codes.
