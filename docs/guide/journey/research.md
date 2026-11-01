## Research

**Partly.** The library comes first:

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --need motor driver --project .
```

<!-- output: run 2026-10-08, spark 0.7.0 -->
```text
  l9110s-module                motor-driver   L9110S dual motor driver module
```

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --need soil moisture --project .
```

<!-- output: run 2026-10-08, spark 0.7.0 -->
```text
  nothing in the library matches 'soil moisture'.
  Research it: /spark:research "soil moisture"  — vendors in order: dfrobot, seeed; sellers: none named in the brief
```

*The brief* is the project's `.spark/project.json`.

A real gap goes to [`/spark:research`](../../../commands/research.md), which works through agents:

- For a commodity part (an LED, a button, a connector: one datasheet describes it), `part-finder` finds the exact
  part on the maker's site.
- `datasheet-reader` then fills the record from the datasheet pages the decision needs.
- For a module, `parts-researcher` researches it from primary sources.

Either way the result is a record in the project's `parts/`, with every fact cited and every unconfirmed fact marked.
Another project finds it once `parts.py --promote <id> --project .` copies it into spark's library, or once a drawer
entry links it, which puts a copy on your shelf. That part runs as agents in a conversation and was not run for this
page.

A module you already own can start from a photo instead: [`/spark:identify`](../../../commands/identify.md).
