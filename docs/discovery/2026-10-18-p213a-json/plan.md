# P213 PR a: `look.py --json` and `deploy.py --json` (#192)

> TL;DR: both scripts print one `outcomes.envelope` on stdout with `--json`. Text and exit codes do not change. The
> envelope's status is built from the exit code, so the two cannot disagree. A step that waits for the person
> (a typed yes, the R press) is a `next` step with `needs_yes: true`.

## Council

Not run yet. Round 1 (tech lead sonnet, refuter opus) and round 2 (tech lead, PO assistant with an AI-UX eye, both
sonnet) are recorded here with what each changed.

## Design

- New library module `scripts/board_envelope.py`. `look_envelope(report)` and `deploy_envelope(run_result, code)` return the
  `outcomes.envelope` dict. `main()` in both scripts only parses, prints and maps the exit code.
- `DeployRunResult` (Result): what one deploy run learned, filled where main already knows it: the plan, the look, the
  token given, `consent.who`, the `DeployResult`, the store record path or why not, and one `refusal` sentence.
- `deploy.py`'s body moves to `_deploy(args, ..., run_result)`. With `--json`, stdout is redirected to stderr while it
  runs (the text lines stay, for a person), and `main` prints the envelope to the real stdout. Prompts go to stderr.
- Status by construction: code 0 gives no problems, 1 gives `problems`, 2 gives `unchecked`, so `EXIT_FOR[status] == code`.
- `GateClosedError` gets `needs_yes` (True only for "no terminal"), and `DeployResult` gets `reset_seen` (None, True or
  False). Both replace a comparison of English text (no magic strings).
- `next` steps: `op` is `look` or `deploy`; `argv` holds the script's arguments, not its name, as `parts.py` does.

## The JSON, by case (`envelope: 1`, compact on one line; shown shortened)

look, matching board, token:
```
{"tool":"look","op":"look","status":"ok","data":{"port":"/dev/cu.usbmodem101","chip":"ESP32-C6","flash_mb":4,
 "mac":"8c:bf:ea:cc:97:70","board":"xiao-esp32-c6","fields":{"chip":"same","flash":"same"},"stops":[],"warnings":[],
 "unknown":{},"verdict":"match","token":"3f9a-0c1e","no_token_reason":null},"problems":[],"unchecked":[],
 "next":[{"op":"deploy","argv":["--project","/p","--token","3f9a-0c1e","--port","/dev/cu.usbmodem101"],
 "why":"put the passed image on the board","effects":["erases ALL of the flash","writes the image"],"needs_yes":true}]}
```
- look, a stop: `status: problems`, `problems: [{"subject":"stop","sentence":"...","fix":"..."}]`, `token: null`, no deploy step.
- look, a field unknown or no token: `status: could-not-run`, `unchecked: [{"sentence":"flash unknown: ...","fix":"..."}]`.
- look, `LookStop` (no board, two boards): `data: null`, `unchecked: [{sentence, fix}]`; `fix` is the doctor's last line.
- deploy `--dry-run`: `status: ok`, `data: {"stage":"plan","dry_run":true,"commands":[[...],[...]],"repl_command":[...]}`,
  `next`: the `look` step.
- deploy, flashed and ready seen: `status: ok`, `data` has `stage:"verify"`, `token`, `yes` ("standing yes typed by ..." or
  "typed in a terminal by ada"), `look` (the look's dict), `commands`, `ready:{"verdict":"ready seen","sentence":...}`,
  `facts_line`, `board_log` (path), `store_record` (path or null); `notes` carry a store record that was not written.
- deploy, no terminal (code 2): `unchecked:[{sentence, fix}]`, `data.stage:"gate"`, `next`: the same deploy with `needs_yes: true`.
- deploy, a stop (code 1): `problems:[{"subject":"gate",...}]`. `ready not seen` (code 1): `problems`, subject `ready`.
- deploy, `ready unknown` (code 2): `unchecked`; with `reset_seen: false` the `next` step is the deploy again,
  `needs_yes: true` (the person presses R first).

## Tests first

`tests/test_board_envelope.py` (shapes; status equals the code for each case above) and `--json` cases in `test_look.py` and
`test_deploy.py` (stdout is exactly one JSON line; text runs unchanged; exit codes equal). `test_json_contracts.py` pins
the top-level keys. Mutations in `tests/mutations/p213a-json.json`.

## Names (developing.md table)

`board_envelope` (module: what it builds), `DeployRunResult` (Result), `look_envelope`, `deploy_envelope` (named for what they
return), `needs_yes` (already `outcomes.step`'s word), `reset_seen`. One word each: the person's consent is `yes` in data and
`needs_yes` in steps; the token is `token`; `refusal` is the one sentence that stopped the run.

## Docs

`--help` of both (the `--json` line and the exit codes), `docs/guide/agents.md` (JSON list, fields, `needs_yes`, the stderr
rule), `commands/build.md` (use `--json` for look and deploy). Findings go to `rows.md` here, not the shared index.

## Not in this PR

`/spark:deploy` and the bench walk (P213 PR b). The R press cannot reach Claude before the run ends: the text goes to stderr
and the envelope tells the next step. Noted for PR b.
