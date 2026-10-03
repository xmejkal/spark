# Tools spark depends on — easy to turn on, change, swap and add

**Status: DRAFT, being designed with the PO (P82's architecture), 2026-10-03.** Sections 1 and 2 are
agreed; 3–5 are written here for review before they are agreed. Nothing is built until the PO has
approved the whole spec.

## The brief (agreed)

A spark user — the hobbyist first — can, without editing spark's code and without asking anyone:

| the user wants to… | example | how, after this design |
| --- | --- | --- |
| **turn an integration on or off** | "I own a logic analyzer; I want the sigrok MCP" | `/spark:setup add sigrok`, or one line in their personal file |
| **change a version** | "use the newer tscircuit in this project" | one line in the project's file |
| **swap a tool** | "simulate with something other than Wokwi" | one line naming the other simulator — refused by name if it cannot do what the step needs |
| **add their own** | "a new MCP server for part search" | one entry: its name, how to install it, what it is for |

Choices live in two places — **personal** (all your projects) and **project** (committed with the
design, so anyone rebuilding gets the same tools); **the project wins**. With nothing configured,
spark works out of the box. `/spark:setup` shows the whole picture and installs what is missing with
one yes (PO decision, P82). The simulation converter ships bundled, so it needs no install (PO
decision, P82; ends B10).

**Why:** today spark's dependencies are decided in seven places, each with its own lookup and its own
error message — `check_spine.py` (tsci, bun), `sim_project.py` (wokwi-cli), `parts.py` (pdftotext),
`flash_image.py` (littlefs, the MicroPython file), `init_project.py` (pinned versions), `.mcp.json`
(MCP servers), the README (companion plugins). Changing any of them means editing code.

## 1. The tools file (agreed)

Three layers, the same format, merged **entry by entry and field by field**; the project wins over
personal, personal over spark's defaults:

| layer | where | written by |
| --- | --- | --- |
| spark's defaults | `data/tools.json` in spark | spark, shipped with the plugin |
| personal | `~/.local/share/spark/tools.json`, beside the datasheet store | the person, for all their projects |
| project | `.spark/tools.json` in the project, committed | the person, for this design |

One entry per tool, holding only what spark needs to know:

```json
"tscircuit": {
  "for": "building the board",
  "role": "board-engine",
  "version": "0.1.2113",
  "check": "tsci --version",
  "install": {"npm": "npm install --save-dev @tscircuit/cli@{version}"},
  "on": true
}
```

An MCP server or a companion plugin is an entry too, with its Claude Code registration:

```json
"sigrok": {
  "for": "reading a logic analyzer at the bench",
  "kind": "mcp",
  "on": false,
  "mcp": {"command": "sigrok-mcp-server"},
  "needs": ["sigrok-cli"],
  "install": {"brew": "brew install sigrok-cli"}
}
```

Roles make swapping one word: `"roles": {"simulator": "wokwi", "board-engine": "tscircuit", "pdf-text": "pdftotext"}`.

The four examples, as what lands in a file:

| example | file | line |
| --- | --- | --- |
| turn on sigrok | personal | `{"sigrok": {"on": true}}` |
| pin tscircuit for this design | project | `{"tscircuit": {"version": "0.0.2700"}}` |
| swap the simulator | project or personal | `{"roles": {"simulator": "my-sim"}}` plus `my-sim`'s entry |
| add your own | personal | a new entry with `for`, `role`, `check`, `install` |

## 2. How spark's scripts ask for a tool (proposed)

One helper, `scripts/tools.py`, replaces the seven lookups. A script asks for a role or a name:

```python
simulator = tools.find("simulator", project)
subprocess.run(simulator.command + ["..."])
```

`find`, in order:

1. merges the three layers and follows a role to a tool ("simulator" → "wokwi" unless changed);
2. locates it where that kind lives — an npm tool in the project's `node_modules` then on the PATH;
   wokwi-cli also in `~/.local/bin`; a downloaded file (the MicroPython firmware) in the person's spark
   folder;
3. compares its version with the entry's — a difference prints one line and goes on (today's
   tscircuit drift check moves here);
4. when the tool is missing, the step ends **could-not-run** (`????`) — never a traceback, never a
   failure — with the one command that installs it here:
   `simulator (wokwi-cli) is not installed — run /spark:setup, or: npm install -g wokwi-cli`.

What changes in existing code:

| script | today | after |
| --- | --- | --- |
| `check_spine.py` | its own tsci search; bun required | `tools.find("board-engine")`; the converter is bundled and runs on Node — no bun |
| `sim_project.py` | its own wokwi-cli search | `tools.find("simulator")` |
| `parts.py --read` | `shutil.which("pdftotext")` | `tools.find("pdf-text")` |
| `flash_image.py` | a littlefs import; a `.bin` the person downloads | `tools.find("littlefs")`, `tools.find("micropython-esp32s3")` |
| `init_project.py` | pinned versions as constants | read from the tscircuit entry |

One rule holds everywhere: **no script names a tool's executable directly** — a test enforces it, the
way spark's tests already refuse an orphan script.

## 3. Swapping a tool: what each step needs from it (to come)

## 4. `/spark:setup` (to come)

## 5. Testing and the order of the change (to come)
