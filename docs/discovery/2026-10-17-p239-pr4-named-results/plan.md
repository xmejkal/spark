# P239 PR 4: named results and honest consent (#238)

## Context

PR 4 of the synthesis (docs/observations/2026-10-14-p239-oo-council/synthesis.md). PRs 1-3 are merged. I read main at
2ca0410. All four items still apply. Only the code around them moved.

| Item | Status on main | Touches |
|---|---|---|
| `ReadyResult` | Applies. `ReadyCheck.check` returns a bare 3-tuple, and `read_board` glues it to `(facts, facts_line)`. | ready_check.py, deploy.py, tests/test_ready_check.py |
| `DeployPlan` | Applies. `plan()` returns `(commands, mpremote, notes)` and `main` unpacks it twice (one drops `notes` with `_`). | deploy.py, tests/test_deploy.py |
| `RunLog` | Applies. `keep_board_log` takes 7 arguments and calls `datetime.now()` itself. | deploy.py, tests/test_deploy_gate.py |
| `ConsentStrategy.who` | Applies. `record_deploy` writes "typed in a terminal by <getpass user>" whatever the yes was (board_facts.py:64). `yes_by` is never passed. | deploy_gate.py, board_facts.py, tests/fakes.py |
| `now` injected | Applies. `facts()` and `keep_board_log` read the clock. | board_facts.py, deploy.py |

P251 renamed the probe to `board_console.ConsoleProbe`. PR 4 does not touch it. I do not use `format_rerun_line`
(PR #333). The behaviour, the `--help` text, the exit codes and the store record's field names do not change.

## Council

(Filled after round 1 and round 2.)

## Design

```
 deploy.main --parses, prints, maps the exit code
   |-- plan() ---------------> DeployPlan   (Result)  commands, mpremote, notes
   |-- ConsentStrategy -------- .who  (str)  "typed in a terminal by petr"
   |       `- TerminalConsentStrategy
   |-- read_board() ----------> ReadyCheck.check() -> ReadyResult (Result) verdict, sentence, log
   |-- RunLog (Value) ---------- .write(project) -> Path   (sim/runs/board/<now>.log)
   `-- board_facts.facts(.., now) / record_deploy(facts, verdict, who)
```

| Class | Role word | File | Job |
|---|---|---|---|
| `ReadyResult` | Result (namedtuple) | ready_check.py | `verdict`, `sentence`, `log` of one check. `check` returns it. |
| `DeployPlan` | Result (namedtuple) | deploy.py | `commands`, `mpremote`, `notes`. `plan` returns it. |
| `RunLog` | Value | deploy.py | The board's log text: `now`, `port`, `image_sha256`, `facts_line`, `ready` (a ReadyResult), `heard`. `write(project)` saves it. Replaces `keep_board_log`. |
| `ConsentStrategy.who` | abstract property | deploy_gate.py | Who said yes, as a phrase. The terminal one says "typed in a terminal by <getpass user>". |

Changes by function:
- `ReadyCheck.check` returns `ReadyResult(verdict, sentence, log)`. All six return lines change.
- `read_board` returns `(facts, facts_line, ReadyResult)`. `main` keeps one `ready` variable, not three.
- `board_facts.facts(project, board, mac, image, files, now)`: `now` is a datetime, with no clock inside.
- `board_facts.record_deploy(facts, verdict, who)`: `who` is required. The `getpass` import and `yes_by` go. The
  record's field stays `yes`, and its value is `who`.
- `main(..., now=None)`: `now` is a callable that returns a datetime (default `datetime.datetime.now`). `main` calls
  it once and passes the value to `facts` and `RunLog`, so the facts file and the log share one time.
- `who` is abstract, so a new consent must say who. `FakeConsent.who = "a test"`.

Name question for the council: the board's log is not a scenario run log (`image_check.run_logs`). The synthesis says
`RunLog`. `BoardLog` may say its role better.

## Tests first (red before the fix)

1. test_ready_check.py: each verdict path returns a `ReadyResult` whose `.verdict`, `.sentence` and `.log` read by
   name. Red today: a plain tuple has no `.verdict`. Guard: it is still a tuple, so a caller that unpacks works.
2. test_deploy.py: `plan(...)` returns a `DeployPlan` with `.commands`, `.mpremote` and `.notes` by name.
3. test_deploy_gate.py: a `ConsentStrategy` subclass without `who` cannot be built. `TerminalConsentStrategy("x").who`
   starts with "typed in a terminal by ".
4. test_deploy_gate.py (line 454 today): a deploy with `FakeConsent(True)` records `yes == "a test"`, not "typed in a
   terminal". Red before the fix. A deploy with the terminal consent still records "typed in a terminal by <user>".
5. test_deploy_gate.py: `main(..., now=lambda: fixed)` gives the facts file's `deployed`, the log's file name and
   its header line the fixed time. Red today, because the clock is read inside.
6. New tests/test_board_facts.py: `facts(..., now)` uses `now`. `record_deploy(facts, "ready seen", "a test")` writes
   that `yes`. A malformed record still raises `StoreProblem`. The fixture is a store in a temp dir under SPARK_HOME.
7. Guard: the log's text is byte for byte the same as today's for the same inputs (one golden string).
8. Mutation file tests/mutations/p239-pr4.json: `who` ignored in `record_deploy`, `now` read from the clock, and
   `ReadyResult`'s `sentence` and `log` swapped.

## Docs

- developing.md: no rule changes. `ReadyResult`, `DeployPlan` and `ConsentStrategy` already follow its naming table.
- agents.md and journey.md: the record's field `yes` and the printed lines are unchanged, so nothing changes. I
  re-read docs/guide/how-it-works.md:220 and commands/build.md:319 ("whose yes it was"). The words stay true.
- Docstrings: each new class starts with its role word. The module docstrings of ready_check.py, board_facts.py and
  deploy.py name the new types.
- No README or tools/journey.py change, because no step's status changes. The board and a row in
  docs/observations/INDEX.md follow the council.

## Out of scope

PR 5 `ProjectImage` and `DeployError`. PR 6 `DeployToken` and `LookReport`. PR 7 `Flasher`. PR 8 `DeployService` and
`DeployResult`. Moving `DeployPlan` into a service is PR 8's job. No change to `--json`, exit codes, `Problem`
renames outside the deploy area, or `format_rerun_line`.
