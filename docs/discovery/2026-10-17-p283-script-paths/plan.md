# P283 — the line a person runs works from any folder

Card: https://github.com/xmejkal/spark/issues/329 (Build). Branch `p283-full-path-lines`. One PR. Written while the PO
works away (2026-10-17, "go for a few hours automatically"), so the plan is a file, not a plan-mode prompt.

## Council

Round 1 ran: tech lead (Sonnet) and refuter (Opus, reproduced the bare line from a scratch folder). It changed:

- The line the PO sees most is not `grant.py`'s own. When there is no grant, `live.py` and `grant.py --check` print
  `board_grant.MESSAGE_FOR`'s "the person runs grant.py --minutes N" (`scripts/board_grant.py:41-43`). These
  sentences now carry the full path too.
- The tests are in `tests/test_board_grant.py` and `tests/test_deploy_gate.py`. `tests/test_grant.py` does not
  exist. `deploy.py` has no `rerun_line` test, so one is written first, before the refactor.
- The red test passes `consent=None` with a stdin and stdout that are not terminals. An injected consent never
  uses the line (`scripts/grant.py:79`), so that test passes without the fix.
- `agents.md` tells Claude to pass on the line that the script prints, not to build one from `$CLAUDE_PLUGIN_ROOT`.
  The plugin cache path in `installed_plugins.json` holds a version and no `scripts/`.
- Callers pass `Path(__file__).resolve()`, so a script started by a relative path still prints an absolute one.
- Out of scope, said in the PR: lines that Claude runs, not the person (`look.py`, `deploy.py --token`,
  `board_doctor.stop_lines`' prefix, the epilogs' prose). This slice prints a long line to paste, not the card's short
  command. The PR asks the PO whether he still wants a PATH slice.
- Rejected after a run: a path with a space or a quote survives `shlex.join` in `zsh`. The script runs without
  `python3` in front (mode 100755, `#!/usr/bin/env python3`). An absolute `--project` changes nothing in `grant.py`.

Round 2: (pending).

## Context

At P247's bench the PO typed `grant.py --minutes 30` and got `zsh: command not found: grant.py`. Three places give
a line that does not run in the person's own terminal:

- `scripts/grant.py:77` builds the line for the person's own terminal as a bare `grant.py --minutes 30`.
  `deploy.py`'s `rerun_line` (`scripts/deploy.py:156`) already prints the script's absolute path and the project's.
- `scripts/board_grant.py:41-43`: the no-grant sentences that `live.py` and `grant.py --check` print.
- `docs/guide/journey.md:1187` shows a bare `grant.py --minutes 30`. `$CLAUDE_PLUGIN_ROOT` is not set in the
  person's own terminal.

## Design

```
deploy_gate.format_rerun_line(script, arguments) -> "/abs/spark/scripts/grant.py --minutes 30 --project /abs/proj"
     ▲                           ▲                                   ▲
grant.py main()          board_grant.GRANT_LINE (at import)     deploy.py rerun_line(args, port)
TerminalConsentStrategy  -> MESSAGE_FOR's three sentences
```

1. `scripts/deploy_gate.py`: `format_rerun_line(script, arguments)` returns `shlex.join([str(Path(script).resolve())]
   + [str(a) for a in arguments])`. It lives beside `NO_TERMINAL`, the sentence that prints the line.
2. `scripts/grant.py`: the line is `format_rerun_line(__file__, ["--minutes", N, "--project", <project, absolute>])`,
   and `--port P` goes in only when the person gave one.
3. `scripts/board_grant.py`: `GRANT_LINE = format_rerun_line(<this folder>/grant.py, ["--minutes", "N"])`, and the
   three no-grant sentences in `MESSAGE_FOR` say "the person runs <GRANT_LINE> in their own terminal". The `why`
   codes in `--json` do not change.
4. `scripts/deploy.py`: `rerun_line` calls `format_rerun_line`. Its output stays the same.
5. No change to the agents rule "never run `grant.py --minutes`".

## Tests

Written first:

- `tests/test_deploy.py`: a test of today's `rerun_line` output, a guard for step 4.
- `tests/test_deploy_gate.py`: `format_rerun_line` gives an absolute path from a relative one, and quotes a space.
- `tests/test_board_grant.py`, red before the fix: `grant.main(["--minutes", "30"], consent=None)` with a stdin and
  stdout that are not terminals exits 2. Its stderr line starts with the absolute path of `scripts/grant.py`, holds
  `--project` with an absolute path, and holds no `--port`. A second run with `--port` holds it.
- `tests/test_board_grant.py:208` changes: the no-grant sentence holds the absolute path of `scripts/grant.py`.

## Docs (same PR)

- `docs/guide/journey.md:1187`: Claude gives you the line with the paths written out, for example
  `<spark>/scripts/grant.py --minutes 30 --project <project>`. `<spark>` is where spark is installed, as at `:1123`.
- `docs/guide/agents.md:127`: when the person must give a grant, pass on the line that `live.py` or `grant.py
  --check` printed, with its full path. Never give a bare `grant.py`.

## Verification

- `python3 -m unittest tests.test_board_grant tests.test_deploy_gate tests.test_deploy`, then the push hook.
- By hand: run `scripts/grant.py --minutes 1 < /dev/null` from another folder, and run the printed line with
  `zsh -c` and `< /dev/null` again, so it stops at the same place. It must find the script.
- Review: one reviewer (Sonnet) and the refuter (Opus), and the mutation tester. Rows in `docs/observations/INDEX.md`.
