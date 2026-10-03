---
description: Show which tools spark needs and which are missing, and install them with one yes; turn integrations on or off, point a job at another tool, pin a version, describe a tool of your own.
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/tools.py *)
---

# spark:setup

spark's dependencies are one list: spark's defaults (`data/tools.json`), the person's choices
(`~/.local/share/spark/tools.json`) and the project's (`.spark/tools.json`), the project winning. This
command shows that list as it stands on this machine and changes it one line at a time.

## 1. Show the picture

```
${CLAUDE_PLUGIN_ROOT}/scripts/tools.py --status --project .
```

`[ok  ]` is found, `[????]` is missing (with the line that installs it), `[off ]` is an integration that
is off, `[!   ]` is something only the person can do — an account, a token, an instrument to plug in.
The last line names what is missing: `N to install: <names>`.

## 2. One yes installs everything missing

If anything reads `[????]`, list those to the person and ask **once**: *install them now?* With a yes:

```
${CLAUDE_PLUGIN_ROOT}/scripts/tools.py --install <names from the last line> --project .
```

Each installs the way its kind does, in the person's own space: an npm tool into the project, a
Python package with `pip install --user`, a system tool with Homebrew, the MicroPython build into
`~/.local/share/spark/downloads/` with its checksum checked. **Never `sudo`**: a line that needs it is
printed for the person to run. Then show the picture again — what was installed reads `[ok  ]`.

## 3. The choices — each writes one line

| the person says | run | writes |
| --- | --- | --- |
| `add sigrok` | `tools.py --on sigrok` | `{"sigrok": {"on": true}}`; installs it, and registers an MCP server with Claude Code |
| `remove sigrok` | `tools.py --off sigrok` | `{"sigrok": {"on": false}}`; unregisters the server |
| `use simulator=my-sim` | `tools.py --use simulator=my-sim` | `{"roles": {"simulator": "my-sim"}}` — refused unless my-sim meets the job's contract |
| `pin tscircuit=0.0.2700` | `tools.py --pin tscircuit=0.0.2700 --project .` | `{"tscircuit": {"version": "0.0.2700"}}` |
| `new` | `tools.py --new 'NAME={…}'` | the person's own entry — ask its name, what it is for, how spark finds it (`kind` and `exe`, `module`, `file`/`url`/`sha256`, or `mcp.command`), how it installs, and which contract it `meets` |

A choice is the person's own by default. Add `--project .` to make it this design's: it goes into
`.spark/tools.json` and travels with the project. A pin is usually the project's.

After an MCP server was added or removed, say that **Claude Code loads servers when a session starts**,
so the change takes effect after a restart. spark's own two servers (`jlcpcb`, `espressif-docs`) come
with the plugin; turning one off is done in Claude Code's `/mcp`.

## From any other command

A spark command that reports a missing tool — `… is not installed — install: …` — is answered the same
way: ask the person once, run `tools.py --install <name> --project .`, and carry on with the step.
