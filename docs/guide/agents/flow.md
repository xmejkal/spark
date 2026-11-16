# Where a project stands, for AI agents

Part of the [guide for AI agents](../agents.md). `flow.py show` says where a project stands, phase by phase
([P825](https://github.com/xmejkal/spark/issues/1183)). The phases go from the idea to the deploy. It reads the project's
files and the store, and writes nothing. `flow.py` with no verb shows too.

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/flow.py" show --project . --json
```

With `--json` it prints the envelope, as `parts.py` does, with `tool` `flow` and `op` `show-flow`. Its `data` holds two keys:

- `phases`: the nine phases in order, `idea`, `needs`, `parts`, `requirements`, `build`, `breadboard`, `firmware`,
  `simulate` and `deploy`. Each is `{phase, status, mark, by, facts, offers}`.
- `stands_at`: the first phase that is not done. A done phase has `status` `ok` or `null`. When every phase is done,
  `stands_at` is `null`.

The words of a phase:

| key | holds |
| --- | --- |
| `status` | `ok`, `problems` or `could-not-run`, or a phase word: `not-started` (nothing done yet), `partial` (some needs have no pick) or `stale` (done, but requirements.json changed after it). `idea`, `firmware` and `simulate` have `null`: their facts say where they stand |
| `mark` | the glyph a page shows for the status |
| `by` | who does the phase: `you`, `claude` or `your terminal` |
| `facts` | sentences for a person. A fact nobody recorded reads `unknown` |
| `offers` | `{key, effect}`: a next step, and one line that says what it does. `flow.py` runs none |

The offer keys are `needs-drop:<need>`, `pick:<need>:<id or entry>`, `requirements` and `build`. A pick's effect says
how many the person has. If none is free, it also names the projects that hold them.

The build phase reads `.spark/build.json`. If the folder of `check_spine.py --keep` is a project, the build writes this
file and lists it under `kept`. It holds the build's `status`, its `stages`, the `requirements` file, its sha256 and the
time. If the sha256 of that file is different now, the build phase is `stale`, and the breadboard phase is `stale` too.

A phase with problems adds one item to `problems`, with the code `phase_problems`. A phase that spark cannot read adds
one item to `unchecked`, with the code `phase_could_not_run`. A build that ended in `could-not-run` does the same. The
subject of each item is the phase. The exit is 0, 1 or 2 by those items. Every phase answers either way. For example,
a broken `.spark/needs.json` makes the needs, parts and requirements phases `could-not-run`, and the others still answer.

Never take an offer only because `flow.py` lists it. A pick, a drop and a build change files, so say what the effect
line says and ask the person first.
