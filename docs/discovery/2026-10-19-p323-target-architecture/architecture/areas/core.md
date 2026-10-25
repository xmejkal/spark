# Area: core

Back to [level 1](../README.md). Words are in the [glossary](../glossary.md). The files that move here are in the
[refactor plan](../refactor-plan.md#appendix-what-moves-where-by-name).

New names (proposed): every class and function on this page except `outcomes` and its functions, and the Fakes
`FakeOutsideWorld`.

## Level 2: what core does

Core holds the contract that every area and every frontend shares: the Operation, its result, the Finding, the
error and the CLI runner. It imports only Python's standard library, so any area and any frontend can use it.

Core runs no Operation of its own. It runs everyone else's: `run_operation` for any frontend, `run_cli` for a CLI.

| Module | Holds |
|---|---|
| `core/outcomes.py` | the status words, `EXIT_FOR`, `status_of`, `envelope`, `step`, `page`, moved from `scripts/outcomes.py` |
| `core/result.py` | `OperationResult`, `Finding`, `NextStep` |
| `core/operation.py` | `Operation` with `schema()`, `Argument`, `COMMON_ARGUMENTS` (`--project`, `--json`, `--port`, `--dry-run`, `--out`, `--timeout`) |
| `core/errors.py` | `SparkError` |
| `core/codes.py` | the codes two or more areas emit, such as `tool_missing`, `crash`, `bad_argument` |
| `core/outside.py` | `OutsideWorld`, `Privacy`, `pick` |
| `core/cli.py` | `run_operation(..., trace=None)`, `run_cli`, `TextReport`, `JsonEnvelope` |
| `core/zone_time.py` | the leaf `zone_time`: times with their zone |
| `core/text_guards.py` | the leaf `text_guards` (today `screen_text`): the guards where text leaves spark |

| Port | Kind | Who fills it |
|---|---|---|
| `OutsideWorld` | Value of callables and one mapping: `run`, `write`, `fetch`, `clock`, `consent`, `environ` | `records.build_outside` in production, `FakeOutsideWorld` in tests |
| `Privacy` | Value: path replacements and secret values to mask | records, from the record folders and `account_env` rows (`tools.py:339`) |
| the frontend | a function that calls `run_operation` and renders the result | `run_cli` today, an MCP server later |

Core depends on nothing in spark.

## Level 3: how core is built

```mermaid
classDiagram
  class Operation {
    <<Value>>
    name
    arguments
    effects
    codes
    run
  }
  class OperationResult {
    <<Result>>
    data
    findings
    next
    lines
    status()
  }
  class Finding {
    <<Value>>
    severity
    subject
    code
    sentence
    fix
    fix_step
  }
  class NextStep {
    <<Value>>
    op
    argv
    why
    needs_yes
    needs_person
  }
  class OutsideWorld {
    <<Value>>
    run
    write
    fetch
    clock
    consent
    environ
  }
  class SparkError {
    <<Error>>
    code
    fix
    status$
  }
  Operation o-- Argument
  Operation ..> OperationResult
  OperationResult o-- Finding
  OperationResult o-- NextStep
  Finding --> NextStep : fix_step
  Operation ..> OutsideWorld
  Operation ..> SparkError
```

`Operation.run` is a plain function. Its keyword parameters are its arguments' `dest` names, plus `outside` and
`backends`: `def look(project, port, ignore_older_runs, *, outside, backends)`. One test checks that every
`Argument.dest` names a parameter. `SparkError.status` is a class attribute, `could-not-run` by default. Only a
subclass for "the design cannot be done", such as `assign_pins.Impossible`, sets `problems`.

`fix` stays a string, as today (`board_envelope.look_envelope`), so the envelope only gains keys. `fix_step` is a new key
that holds the same advice as a NextStep, or null. `TextReport` and `JsonEnvelope` are the two Renderers of a result.

The effects are `reads`, `writes`, `runs`, `network`, `board` and `erases`. `build_outside` fills only the fields
the declared effects need and puts a refusing stub in the others. A call to a stub raises `SparkError` with code
`undeclared_effect`. `run` needs `runs`, `write` needs `writes`, `fetch` needs `network`, `consent` needs `board` or
`erases`. `environ` is a read-only copy of the variables the Operation names, such as `CLAUDE_CODE_SESSION_ID`
(`cost.py:69`) or the Wokwi token (read in `run_scenario.main`). With `--dry-run`, `run` and `write` record instead of act.

### The main flow

The signature is `run_cli(prog, operations, argv=None, *, build_outside, outside=None)`. A CLI's `main(argv=None,
outside=None)` passes its `outside` on. A test passes a `FakeOutsideWorld` there, and production passes nothing.

```mermaid
sequenceDiagram
  participant CLI as scripts/x.py
  participant RC as run_cli
  participant B as build_outside (records)
  participant RO as run_operation
  participant OP as Operation.run
  CLI->>RC: run_cli(prog, OPERATIONS, argv, build_outside, outside)
  RC->>RC: parse argv with argparse
  alt a bad flag
    RC-->>CLI: envelope, code bad_argument, exit 2
  end
  RC->>B: build_outside(project, effects), unless a test gave outside
  B-->>RC: OutsideWorld, Backends, Privacy
  RC->>RO: run_operation(operation, values, outside, backends)
  RO->>OP: run(values as keywords, outside, backends)
  alt a SparkError
    RO-->>RC: OperationResult with one Finding from the error
  else a crash
    RO-->>RC: OperationResult, code crash, could-not-run
  end
  OP-->>RO: OperationResult
  RO-->>RC: OperationResult
  RC->>RC: Privacy shortens paths and masks secrets
  RC-->>CLI: TextReport or JsonEnvelope printed, EXIT_FOR[status]
```

A bad flag with `--json` prints an envelope, as `parts.py` does today with `_Parser`. The
traceback of a crash always goes to stderr.

### How core is tested alone

- A toy Operation in the test file, a `FakeOutsideWorld`, no spark area imported.
- One test per path in the flow: ok, problems, could-not-run, bad flag, SparkError, crash, undeclared effect.
- The parity test: for each golden, the text and the `--json` render carry the same codes and the same first step.
- `tests/test_json_contracts.py` lists the allowed envelope keys and fails on a new one that is not added there.

### How a new implementation is added

- A new frontend, such as an MCP server, is one module. It turns a tool call into `(operation, values)`, calls
  `run_operation` and renders the result. `isError` is true exactly for `could-not-run`. With two frontends, a
  `Frontend` base class enters (rule T3: a base needs two subclasses or a Fake).
- A new shared flag is one `Argument` in `COMMON_ARGUMENTS`. An old spelling stays as a hidden alias.
- A new code is one constant with a one-line meaning in `core/codes.py` when two areas emit it.
