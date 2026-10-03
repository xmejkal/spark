# MCP servers — which spark uses, and how to add the others

spark drives tscircuit and Wokwi through their command-line tools (a CLI costs nothing until it is
called; an MCP server's tools load into every session). Two MCP servers earn their place, because
spark's research agents call them; the rest are offered here for anyone who wants them, each with
what was checked on 2026-10-03.

## Declared by spark (`.mcp.json`) — used by its agents

| server | used by | what it gives | needs | checked |
| --- | --- | --- | --- | --- |
| **jlcpcb** — `npx -y @jlcpcb/mcp` | `part-finder` | `component_search`: candidates with a datasheet link and an LCSC code in one call (distributor data — it finds a part; the maker's datasheet is the fact source) | Node | answered `tools/list` with 6 tools, on Node 18 and later |
| **espressif-docs** — `npx -y mcp-remote https://mcp.espressif.com/docs` | `datasheet-reader` | `search_espressif_sources`: semantic search over Espressif's official documentation, for facts about the ESP32 itself | **Node 20 or newer** — `mcp-remote` fails on Node 18 with `ReferenceError: File is not defined` | "Espressif Documentation" 3.3.1 answered on Node 24 |

If `/mcp` shows espressif-docs failing, check which Node your shell starts: `node --version`. With
nvm, `nvm alias default 22` makes new sessions use Node 22.

## Offered — add them yourself

Each is one choice in `/spark:setup`; it adds the server for you (or, with `--project`, for this
project), not for every spark user. `/spark:setup remove <name>` takes it away again.

**wokwi** — drive a simulation interactively (start, press, read the serial port). Every run spends
minutes from your Wokwi plan, so spark itself only runs `wokwi-cli` when you ask.
```
/spark:setup add wokwi-mcp
```
Installs `wokwi-cli` if it is missing — Wokwi's own release binary for your machine, version 0.28.0,
its checksum checked, into `~/.local/share/spark/downloads/` (it is not an npm package) — and registers
the server by `wokwi-cli`'s full path, since wherever it lives is often not on the PATH Claude Code
starts. Needs `WOKWI_CLI_TOKEN`
set in your shell — never in a file you commit. Not checked here: the
check would start the paid simulator's server.

**sigrok** — a bench scope or logic analyzer, from the machine the instrument is plugged into.
```
/spark:setup add sigrok
```
Installs `sigrok-cli` (Homebrew) and registers the server. Needs
[KenosInc/sigrok-mcp-server](https://github.com/KenosInc/sigrok-mcp-server), which you install yourself.
Not checked here: neither is installed on the machine this was written on. spark's bench steps
(P73) will want it.

**KiCad** — not offered. The `kicad-mcp` package on PyPI drives a *running* KiCad editor through its
socket and asks for an OpenAI API key; under `uvx` it also fails to start with the newest `mcp`
library (`No module named 'mcp.server.fastmcp'`) unless run as `uvx --with "mcp<2" kicad-mcp`. spark
draws boards in tscircuit, so no step of its journey needs it.
