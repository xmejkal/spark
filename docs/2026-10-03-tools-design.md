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
   failure — and says exactly what is missing and how it installs here:
   `simulator (wokwi-cli) is not installed — install: npm install -g wokwi-cli`.

**Installed on the spot, with one yes (the PO, 2026-10-03: "isn't there a way to download or enable
the tools?").** The command the person is running — `/spark:build`, `/spark:research` — reads that
line and asks once: *"the simulator (wokwi-cli) is not installed — install it now?"* With a yes it
installs it the way `/spark:setup` would, or registers an MCP server or plugin with Claude Code, and
**carries on with the step**. The boundary is deliberate: a script never installs anything silently in
the middle of a check — it reports, and the conversation asks and installs — so nothing lands on the
machine without the person's yes. What cannot be automatic is said plainly: anything that needs
`sudo` (spark never uses it), accounts and keys (a Wokwi token only the person can create), and
hardware (sigrok needs the analyzer plugged in).

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

## 3. Swapping a tool: what each step needs from it (proposed)

A role names **what the step needs from whatever tool fills it** — its contract. A tool's entry says
which contracts it meets (`"meets": ["wokwi-project"]`). Point a role at a tool that does not declare
the role's contract and the step refuses by name, before running anything:
`simulator: my-sim does not say it runs a Wokwi project (contract "wokwi-project"), so the
simulation step will not use it`. Where a contract has a tiny sample, `/spark:setup` also runs the
tool on it once, so "declares it" is checked against "does it".

| role | default | the contract — what the step needs | swappable in practice |
| --- | --- | --- | --- |
| `board-engine` | tscircuit | builds the board file spark writes (tscircuit TSX) into `circuit.json` | **versions only** — the generator writes tscircuit; another engine would need its own generator, which no design asks for (W14) |
| `simulator` | Wokwi (`wokwi-cli`) | runs a Wokwi project (`diagram.json`, `wokwi.toml`, a flash image, a scenario file) and exits 0 when the scenario passes | **yes**, for anything that runs a Wokwi project |
| `pdf-text` | `pdftotext` (poppler) | prints one page's text, laid out, for a page number; says when the page is past the end | **yes** — e.g. MuPDF's `mutool` behind a one-line wrapper |
| `littlefs` | `littlefs-python` | packs files into the ESP32 port's littlefs image | versions only |
| `micropython-<chip>` | micropython.org's build for the chip | the interpreter `.bin` the flash image starts with | **yes** — another release, or your own build, as a file |
| `parts-search` (MCP) | jlcpcb | finds candidates with a datasheet link | **yes** — any MCP server whose tool returns that |
| `chip-docs` (MCP) | espressif-docs | searches the chip maker's documentation | **yes** |
| `bench` (MCP) | sigrok (off) | reads an instrument at the bench | **yes** |

**One limit, said plainly.** spark's own agents (`part-finder`, `datasheet-reader`) can use only the
MCP tools their files name — that is how Claude Code works, and spark's files ship with spark. A server
the person adds is used by spark's **commands**, which run in the conversation and see every connected
server; the commands hand what it found to the agents. So "add your own MCP" works through the
commands, not inside the agents.

## 4. `/spark:setup` (proposed)

**What the person sees.** One command, in the project or anywhere:

```
/spark:setup

  spark's tools — personal: ~/.local/share/spark/tools.json · project: .spark/tools.json

  [ok  ] board-engine   tscircuit 0.1.2113 (project's node_modules)
  [ok  ] pdf-text       pdftotext 26.09.0
  [????] simulator      wokwi-cli — not installed          install: npm install -g wokwi-cli
  [????] littlefs       littlefs-python — not installed    install: python3 -m pip install --user littlefs-python
  [ok  ] parts-search   jlcpcb (MCP, spark's own)
  [ok  ] chip-docs      espressif-docs (MCP, spark's own; Node 22)
  [off ] bench          sigrok (MCP)                       turn on: /spark:setup add sigrok
  [!   ] simulator      needs a Wokwi token — create one at wokwi.com/dashboard/ci and set WOKWI_CLI_TOKEN in your shell

  2 to install. Install them now?
```

**One yes installs everything listed**, each the way its kind installs, always in the person's own
space and never with `sudo`: an npm tool into the project (`npm install --save-dev`), a Python package
with `pip install --user`, a system tool with Homebrew where it is there, a downloaded file (the
MicroPython build) into the person's spark folder with its checksum checked against the entry. What
cannot be installed for them is listed with what to do — a token, a `sudo` command on Linux, an
instrument to plug in. Run it again and everything reads `[ok]`.

**Changing a choice is a subcommand that writes the one line** — the person never edits JSON unless they
want to:

| the person says | spark writes | where |
| --- | --- | --- |
| `/spark:setup add sigrok` | `{"sigrok": {"on": true}}`, then installs it and registers the MCP server with Claude Code | personal, or `--project` |
| `/spark:setup remove sigrok` | `{"sigrok": {"on": false}}`, and unregisters it | the same |
| `/spark:setup use simulator=my-sim` | `{"roles": {"simulator": "my-sim"}}` — refused if `my-sim` does not meet the contract | the same |
| `/spark:setup pin tscircuit=0.0.2700` | `{"tscircuit": {"version": "0.0.2700"}}` | project, by default |
| `/spark:setup new` | asks for name, purpose, role, how to check and install it, and writes the entry | personal |

**MCP servers and plugins go through Claude Code's own commands** — `claude mcp add` / `claude mcp
remove` at user scope for a personal choice, project scope for a project's — so they show in `/mcp` like
any other. Claude Code loads servers when a session starts, so setup says when a restart is needed.

**Behind the command** is one script, `tools.py`, with the same subcommands (`--status`, `--install`,
`--on`, `--off`, `--use`, `--pin`); `/spark:setup` is the conversation around it, asking the one yes.

## 5. Testing and the order of the change (to come)
