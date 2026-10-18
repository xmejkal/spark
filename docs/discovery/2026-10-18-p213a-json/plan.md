# P213 PR a: `look.py --json` and `deploy.py --json` (#192)

> TL;DR: both scripts print one `outcomes.envelope` on stdout with `--json`. Text and exit codes do not change. The
> envelope's status is built from the exit code, so the two cannot disagree. A step that waits for the person
> (a typed yes, the R press) is a `next` step with `needs_yes: true`.

## Council

Round 1 tech lead changed: problems from the status lists; no redirect, `out=`; no Result class; `then` for look/yes; `reset_seen`. Refuter changed: esptool writes to fd 1, so `DeployService(echo_to=sys.stderr)` passes `stdout=` to the flash run under `--json`; `effects` use the vocabulary `writes`/`deletes`; a deploy step is keyed on the token, not the status; the no-terminal step is for the person's own terminal and carries `run_in_terminal` and a `grant` step; ready unknown gives a `watch` step (the REPL), never a second erase; a flash that fails is `stage:"flash"` (the board may be erased). Round 1 (tech lead sonnet, refuter opus) and round 2 (tech lead, PO assistant with an AI-UX eye, both
sonnet) are recorded here with what each changed.

## Design

- New library module `scripts/board_envelope.py`. `look_envelope(report)` and `deploy_envelope(run_result, code)` return the
  `outcomes.envelope` dict. `main()` in both scripts only parses, prints and maps the exit code.
- `main` keeps a dict `reached` (plan, look, token given, `consent.who`, `DeployResult`, store record path or why not,
  one `refusal` sentence) and passes it to `deploy_envelope` at each exit. No new class (round 1: a mutable "Result" breaks
  the table).
- No `redirect_stdout`. `main` picks `out = sys.stderr if args.json else sys.stdout` and every print takes `file=out`,
  `TerminalConsentStrategy` gets `stdout=out`. The envelope alone goes to stdout. Argparse errors and a raise inside
  `verify` stay as today (usage / traceback, no envelope): a row, not this PR.
- Status by construction: code 0 gives no problems, 1 gives `problems`, 2 gives `unchecked`, so `EXIT_FOR[status] == code`.
- `GateClosedError` gets `next_op` (None, `NEXT_DEPLOY` for "no terminal", `NEXT_LOOK` for no token or "changed since the look"),
  and `DeployResult` gets `reset_seen` (None, True or False). Both replace a comparison of English text (no magic strings).
- `look_envelope` builds `problems` from the same lists `LookReport.status` uses (differing fields + stops) and `unchecked`
  from unknown fields + no token, and reuses `LookReport.to_dict()` as `data`. A flash that differs but fits is `problems`.
- `next` steps: `op` is `look` or `deploy`; `argv` holds the script's arguments, not its name, as `parts.py` does.

## The JSON, by case (`envelope: 1`, compact on one line; shown shortened)

look, matching board, token:
```
{"tool":"look","op":"look","status":"ok","data":{"port":"/dev/cu.usbmodem101","chip":"ESP32-C6","flash_mb":4,
 "mac":"8c:bf:ea:cc:97:70","board":"xiao-esp32-c6","fields":{"chip":"same","flash":"same"},"stops":[],"warnings":[],
 "unknown":{},"verdict":"match","token":"3f9a-0c1e","no_token_reason":null},"problems":[],"unchecked":[],
 "next":[{"op":"deploy","argv":["--project","/p","--token","3f9a-0c1e","--port","/dev/cu.usbmodem101"],
 "why":"erases ALL of the flash, then writes the passed image","effects":["deletes","writes"],"needs_yes":true}]}
```
- look, a stop: `status: problems`, `problems: [{"subject":"stop","sentence":"...","fix":"..."}]`, `token: null`, no deploy step.
- look, a field unknown or no token: `status: could-not-run`, `unchecked: [{"sentence":"flash unknown: ...","fix":"..."}]`.
- look, `LookStop` (no board, two boards): `data: null`, `unchecked: [{sentence, fix}]`; `fix` is the doctor's last line.
- deploy, no token or "changed since the look" (code 2): `unchecked`, `next`: the `look` step.
- deploy `--dry-run`: `status: ok`, `data: {"stage":"plan","dry_run":true,"commands":[[...],[...]],"repl_command":[...]}`,
  `next`: the `look` step.
- deploy, flashed and ready seen: `status: ok`, `data` has `stage:"verify"`, `token`, `yes` ("standing yes typed by ..." or
  "typed in a terminal by ada"), `look` (the look's dict), `commands`, `ready:{"verdict":"ready seen","sentence":...}`,
  `facts_line`, `board_log` (path), `store_record` (path or null); `notes` carry a store record that was not written.
- deploy, no terminal (code 2): `unchecked:[{sentence, fix}]`, `data.stage:"gate"`, `data.run_in_terminal` (the line), `next`: the deploy (`needs_yes: true`, `why`: the person runs it in their own terminal; a chat "go ahead" is not the yes) and, when a grant could cover it, the `grant` step.
- deploy, a stop (code 1): `problems:[{"subject":"gate",...}]`. `ready not seen` (code 1): `problems`, subject `ready`.
- deploy, `ready unknown` (code 2): `unchecked`; `next`: `{"op":"watch","argv":[<mpremote repl>],...}`; with `reset_seen: false`
  its `why` says the person presses R first. Never a second erase. A flash command that fails: `data.stage:"flash"`, and
  the sentence says the board may be erased.
- Every look with a token (a differing flash that fits, an unknown field too) has the deploy step; only a missing token has none.

## Tests first

`tests/test_board_envelope.py` (shapes; status equals the code for each case above) and `--json` cases in `test_look.py` and
`test_deploy.py` (stdout is exactly one JSON line; text runs unchanged; exit codes equal). `test_json_contracts.py` pins
the top-level keys. Mutations in `tests/mutations/p213a-json.json`.

## Names (developing.md table)

`board_envelope` (module: what it builds), `reached` (a dict, no class), `NEXT_DEPLOY`, `look_envelope`, `deploy_envelope` (named for what they
return), `needs_yes` (already `outcomes.step`'s word), `reset_seen`. One word each: the person's consent is `yes` in data and
`needs_yes` in steps; the token is `token`; `refusal` is the one sentence that stopped the run.

## Docs

`--help` of both (the `--json` line and the exit codes), `docs/guide/agents.md` (JSON list, fields, `needs_yes`, the stderr
rule), `commands/build.md` (use `--json` for look and deploy). Findings go to `rows.md` here, not the shared index.

## Not in this PR

`/spark:deploy` and the bench walk (P213 PR b). The R press cannot reach Claude before the run ends: the text goes to stderr
and the envelope tells the next step. Noted for PR b.

## Council round 2 (tech lead, PO assistant), what changed

- `echo_to=2` (an fd, so StringIO and pytest do not break); only the flash loop gets `stdout=`. `show_line`, `choose_consent`
  and `TerminalConsentStrategy(stdout=out)` all take `out`; a test pins that the gate asks on stderr under `--json`.
- `GateClosedError.next_op` is None for "you answered no", "grant ended" and a refused grant. `FlashError(DeployError)` marks
  stage `flash`. `DeployResult.reset_seen` is set where `wait_for_reset()` is read (None when never asked).
- `deploy_argv(project, token, port, ignore_older_runs)` lives in `board_envelope` and `rerun_line` uses it.
- Steps: `watch` has `argv:[port]` and the mpremote line in `data.repl_command`; `grant` has `--minutes 60` (the person picks 1
  to 1440); effects declared (`look` none, `grant` writes). Step `why` says a chat "go ahead" and the token are not the yes,
  and that unknown is not a pass.
- Data: `yes:{"kind":"grant"|"terminal","who":...}`, `store_record_error` beside a null `store_record`, `board_state:
  "may_be_erased"` at stage `flash`, `person_action` (the R press) when `reset_seen` is false. agents.md: tell the person
  before the run that an R press may be asked (the text goes to stderr and the run waits for it).
