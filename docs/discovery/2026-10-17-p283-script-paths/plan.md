# P283 — the line a person runs works from any folder

Card: https://github.com/xmejkal/spark/issues/329 (Build). Branch `p283-full-path-lines`. One PR. Written while the PO
works away (2026-10-17, "go for a few hours automatically"), so the plan is a file, not a plan-mode prompt.

## Council

(Filled after round 1 and round 2.)

## Context

At P247's bench the PO typed `grant.py --minutes 30` and got `zsh: command not found: grant.py`. Two places gave
him a line that does not run:

- `scripts/grant.py:77` builds the line for the person's own terminal as a bare `grant.py --minutes 30`.
  `deploy.py`'s `rerun_line` (`scripts/deploy.py:156`) already prints the script's absolute path and the project's.
- `docs/guide/journey.md:1187` shows a bare `grant.py --minutes 30`, while the same guide shows
  `python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py"` elsewhere and `<spark>/scripts/deploy.py` at `:1123`.
  `$CLAUDE_PLUGIN_ROOT` is not set in the person's own terminal.

The card asks for the smallest first slice: the full path in the lines and the guides, before any new spark command
or a PATH change. If the PO still wants a PATH line from `/spark:setup` or one `spark` command, it is a later slice.

## Design

```
deploy_gate.format_rerun_line(script_file, arguments) -> "'/abs/scripts/grant.py' --minutes 30 --project /abs/proj"
        ▲                                    ▲
grant.py main(): TerminalConsentStrategy(line)        deploy.py rerun_line(args, port)
```

1. `scripts/deploy_gate.py`: `format_rerun_line(script_file, arguments)` returns `shlex.join([absolute script path]
   + arguments)`. It lives beside `NO_TERMINAL`, the sentence that prints the line. One job, no state: a function.
2. `scripts/grant.py`: the line is `format_rerun_line(__file__, ["--minutes", N, "--project", <project, absolute>]
   + ["--port", P])`, the port only when one is given. The project goes in because the person's terminal can be
   in another folder.
3. `scripts/deploy.py`: `rerun_line` calls `format_rerun_line`. Its output stays the same.
4. No change to the agents rule "never run `grant.py --minutes`".

## Tests

Red before the fix, in `tests/test_grant.py`: with a consent that has no terminal, `grant.py --minutes 30` stops
with exit 2. Its stderr line starts with the absolute path of `scripts/grant.py` and holds `--project` with an
absolute path. Guard: `deploy.py`'s existing rerun-line test still passes unchanged.

## Docs (same PR)

- `docs/guide/journey.md:1187`: Claude gives you the line, with the paths written out, for example
  `<spark>/scripts/grant.py --minutes 30 --project <project>`. `<spark>` is where spark is installed, as at `:1123`.
- `docs/guide/agents.md:127`: when the person must give a grant, give them that line with `$CLAUDE_PLUGIN_ROOT` and
  the project written out as absolute paths, never a bare `grant.py`.
- The `grant.py` epilog: when it shows a bare line that a person types, the same change.

## Verification

- `python3 -m unittest tests.test_grant tests.test_deploy`, then the whole suite through the push hook.
- By hand: run `scripts/grant.py --minutes 1 < /dev/null` from another folder, copy the printed line, and see that
  `zsh` finds the script. Do not answer yes, because no board grant is wanted.
- Review: one reviewer (Sonnet) and the refuter (Opus), and the mutation tester. Rows in `docs/observations/INDEX.md`.
