# P239 PR 4: named results and honest consent (#238)

## Context

PR 4 of the synthesis (docs/observations/2026-10-14-p239-oo-council/synthesis.md). PRs 1-3 are merged. I read main at
2ca0410. All four items still apply. Only the code around them moved.

| Item | Status on main | Touches |
|---|---|---|
| `ReadyResult` | Applies. `ReadyCheck.check` returns a bare 3-tuple, and `read_board` glues it to `(facts, facts_line)`. | ready_check.py, deploy.py, tests/test_ready_check.py |
| `DeployPlan` | Applies. `plan()` returns `(commands, mpremote, notes)` and `main` unpacks it twice (one drops `notes` with `_`). | deploy.py, tests/test_deploy.py |
| `BoardLog` | Applies. `keep_board_log` takes 7 arguments and calls `datetime.now()` itself. | deploy.py, tests/test_deploy_gate.py |
| `ConsentStrategy.who` | Applies. `record_deploy` writes "typed in a terminal by <getpass user>" whatever the yes was (board_facts.py:64). `yes_by` is never passed. | deploy_gate.py, board_facts.py, tests/fakes.py |
| Clock injected | Applies. `facts()` and `keep_board_log` read the clock. | board_facts.py, deploy.py |

P251 renamed the probe to `board_console.ConsoleProbe`. PR 4 does not touch it. I do not use `format_rerun_line`
(PR #333). The behaviour, the `--help` text, the exit codes and the store record's field names do not change.

## Council

Round 1 ran: tech lead (Sonnet) and refuter (Opus). It changed:
- The clock has two names: the parameter `clock` (a callable) and the value `moment`. `main` reads it once.
- `RunLog` became `BoardLog`. It holds no `ReadyResult`.
- The download-mode branch rewrites only the sentence and the log, so it uses `_replace`.
- `who` is built in `TerminalConsentStrategy.__init__`, and its text is a named constant.
- Tests: no tuple guard, literal golden strings, and one test per dropped `yes_by`.
- Four mutation anchors on the removed `read_board` line are re-anchored in this PR.
- developing.md:246 changes. The `getpass` use in board_grant.py is out of scope.

Round 2: (pending).

## Design

```
 deploy.main --parses, prints, maps the exit code
   |-- plan() ---------------> DeployPlan   (Result)  commands, mpremote, notes
   |-- ConsentStrategy -------- .who  (str)  "typed in a terminal by petr"
   |       `- TerminalConsentStrategy
   |-- read_board(.., moment) -> ReadyCheck.check() -> ReadyResult (Result) verdict, sentence, log
   |-- BoardLog (Value) -------- .write(project) -> Path   (sim/runs/board/<moment>.log)
   `-- board_facts.facts(.., moment) / record_deploy(facts, verdict, who)
```

| Class | Role word | File | Job |
|---|---|---|---|
| `ReadyResult` | Result (namedtuple) | ready_check.py | `verdict`, `sentence`, `log` of one check. `check` returns it. |
| `DeployPlan` | Result (namedtuple) | deploy.py | `commands`, `mpremote`, `notes`. `plan` returns it. |
| `BoardLog` | Value | deploy.py | The board's log text: `moment`, `port`, `image_sha256`, `facts_line`, `verdict`, `sentence`, `heard`. Its one method, `write(project)`, saves it. Replaces `keep_board_log`. |
| `ConsentStrategy.who` | abstract property | deploy_gate.py | Who said yes, as a phrase. `TerminalConsentStrategy.__init__` builds it from `getpass.getuser()` and the constant `TYPED_BY = "typed in a terminal by %s"`. |

Why `BoardLog`, not the synthesis's `RunLog`: `image_check.run_logs` means the scenario logs in sim/runs/. This file
is in sim/runs/board/ and the output calls it "board log:". It takes verdict and sentence as arguments and holds no
`ReadyResult`, so it does not depend on ready_check.

Changes by function:
- `ReadyCheck.check` returns `ReadyResult(verdict, sentence, log)`. All six return lines change.
- `read_board(project, report, connection, expected, moment)` and `put_facts(..., moment)` pass `moment` on to
  `board_facts.facts(project, board, mac, image, files, moment)`. `facts` has no clock inside.
- `read_board` returns `(facts, facts_line, ReadyResult)`. `main` keeps one `ready` variable.
- The download-mode branch (deploy.py:237, `NO_RESET`) changes only the sentence and the log: `ready =
  ready._replace(sentence=..., log=...)`.
- `main(..., clock=None)`: `moment = (clock or datetime.datetime.now)()`, once, passed to `read_board` and `BoardLog`.
  The facts file and the log share one time. Never `now` for both.
- `record_deploy(facts, verdict, who)`: `who` is required. `yes_by` and the `getpass` import leave board_facts.py
  (`getpass` moves to deploy_gate.py). The record's field stays `yes`, and its value is `who`.
- `FakeConsent` is duck-typed, not a subclass. It gets `who = "a test"`.

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
6. New tests/test_board_facts.py: `facts(..., moment)` uses `moment`. `record_deploy(facts, "ready seen", "a test")`
   writes that `yes`. A malformed record still raises `StoreProblem`. It reuses the SPARK_HOME helper of the
   existing tests.
7. Golden: the board log's text for two deploys, written as literal strings: one ready seen, and one download-mode
   deploy where no reset came (`NO_RESET`, sentence and log replaced). The text is byte for byte today's.
8. Mutation file tests/mutations/p239-pr4.json: `who` ignored in `record_deploy`, the clock read inside `facts`,
   `ReadyResult`'s `sentence` and `log` swapped, and `_replace` dropped in the no-reset branch.

## Verification

- Four finds target the removed line `facts, facts_line, verdict, sentence, said = read_board(...)`:
  tests/mutations/p243-download-mode.json:65 and p245-read-after-ready.json:35, 41, 53. This PR re-anchors them.
- `python3 tools/mutate.py --anchors` on the deploy mutation tables must pass. Five rows in p215-link and p219-gate
  were already stale on main. They stay for P284 (#331).

## Docs

- developing.md:246 says `ReadyResult` "does not exist yet": update that line. The rules and the table do not change.
- agents.md and journey.md: the record's field `yes` and the printed lines are unchanged, so nothing changes.
  how-it-works.md:220 and commands/build.md:319 ("whose yes it was") stay true.
- Docstrings: each new class starts with its role word. The module docstrings of ready_check.py, board_facts.py and
  deploy.py name the new types.
- No README or tools/journey.py change, because no step's status changes.

## Out of scope

PR 5 `ProjectImage` and `DeployError`. PR 6 `DeployToken` and `LookReport`. PR 7 `Flasher`. PR 8 `DeployService` and
`DeployResult`. board_grant.py:129 writes `getpass.getuser()` into the grant, not `consent.who`: a later PR or card.
No change to `--json`, exit codes, `Problem` renames outside the deploy area, or `format_rerun_line`.
