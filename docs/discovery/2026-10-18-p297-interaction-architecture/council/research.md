# P297 research notes: the facts the council argues from

Read 2026-10-18 by the spike lead. One or two searches per point. "Unverified" means read in docs, not run here.

## How design tools let an agent act while a person watches

| Tool | Shape | What the person sees | Source |
|---|---|---|---|
| Fusion 360 MCP (faust-machines, MIT, beta, updated 2026-09-16) | MCP server (stdio) -> TCP :9876 -> add-in on Fusion's main thread | the change in Fusion's own viewport, at once; `render_view` gives Claude a PNG; an `undo` tool | https://github.com/faust-machines/fusion360-mcp-server |
| Figma MCP server (official, beta, free in beta, paid later) | remote MCP server writes native content (`use_figma`) | the edit appears on the live canvas | https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Figma-MCP-server |
| KiCAD Buddy (62 tools, KiCad 9/10) | MCP server edits `.kicad_sch` with a `.bak`, then `kicad_refresh_editor` makes KiCad reload | KiCad reloads the file | https://pypi.org/project/kicad-buddy/ |
| Wokwi for VS Code diagram editor | closed; edits `diagram.json`; editing needs Hobby+ or Pro | the file in an editor tab; reload on an outside change is not documented | https://docs.wokwi.com/vscode/diagram-editor |
| `wokwi-cli mcp` (experimental, v0.28.1) | MCP server over Wokwi's cloud simulator: read pin, set control, read serial | nothing visual | P295 finding |
| tscircuit RunFrame | viewer raises edit events; a file server applies them to `manual-edits.json` | the viewer | P294 finding, runframe README |

Pattern: every one keeps the **document in the tool** (Fusion, Figma, KiCad), and the MCP server is a thin door into it.
The person watches the tool's own view. None of them uses a chat-side page as the source of truth.

## MCP Apps (UI inside the chat)

- Official MCP extension SEP-1865; stable spec 2026-01-26; `ext-apps` 2.x, Apache 2.0. A tool names a `ui://` resource in
  `_meta.ui.resourceUri`; the host renders its HTML in a sandboxed iframe; JSON-RPC over `postMessage`; "the host passes
  tool data to the UI via notifications, and the UI can call other tools through the host"; hosts can ask consent for
  UI-initiated calls. Hosts: Claude (Desktop and claude.ai), ChatGPT, VS Code, Goose and others.
  https://github.com/modelcontextprotocol/ext-apps , https://blog.modelcontextprotocol.io/posts/2025-11-21-mcp-apps/ ,
  https://claude.com/docs/connectors/building/mcp-apps/quickstart
- Not found: whether the Claude Code terminal renders MCP Apps. Treat it as no (a terminal has no iframe). Unverified.

## MCP transports

- stdio (client starts the server) and Streamable HTTP (one process, many clients, SSE for server-to-client
  notifications). Local servers bind to 127.0.0.1 and check `Origin` (DNS rebinding).
  https://modelcontextprotocol.io/specification/2025-06-18/basic/transports

## Artifact runtime capabilities (this environment's skill text, runtime contract 0.2.85; unverified, not run)

- `db`: shared documents under access rules, live through `onSnapshot`, kept across republishes; Claude reads and writes
  them with the `ArtifactData` tool (get, list, query, set, update, batch). Needs a signed-in viewer.
- `artifact`: the page republishes its whole document; every open view reloads; a concurrent save gets `conflict`.
- `room`: live presence and messages to whoever has the page open, "plus your publishing session when admitted (kind
  agent)"; nothing persists.
- `mcp`: the page calls the viewer's claude.ai connectors, or `host:<name>`, a local MCP server on the viewer's device
  ("Claude app only; else `server_not_connected`").
- `files`: reads a Claude Code project's files as the viewer (needs the project id; new files can lag a few seconds).
- Limits: lives on claude.ai (online, account); scripts only from cdnjs, jsdelivr, unpkg; each page has its own origin.

## Live sync and shared documents

- Yjs: CRDT, MIT; Y.Map/Y.Array; providers y-websocket, y-webrtc; y-indexeddb offline; UndoManager; Python port `pycrdt`.
  https://github.com/yjs/yjs
- Automerge: CRDT for local-first apps, history and branches; JS, Rust (WASM), Swift; no Python binding named.
  https://automerge.org/docs/hello/
- Event sourcing: "Capture all changes to an application state as a sequence of events"; undo by reverting to a snapshot
  and replaying, or by events that store the prior value. https://martinfowler.com/eaaDev/EventSourcing.html

## What spark has today (main, 2026-10-18)

- Claude Code + spark plugin runs Python scripts (`scripts/`); kept files `requirements.json`, `breadboard.json`
  (a Wokwi `diagram.json`), `diagram.json`; `check_spine.py --keep` rebuilds and keeps moves (P273, P287).
- `page.html` is static, Artifact-ready (P272); a private Artifact rendered it. No server, no MCP server of spark's own.
- Swap points already in code: `FirmwarePlatform` (`scripts/firmware_platform.py`), `DRAWING_RENDERERS`, `WIRING_VIEWS`.
- Plans: v0.13 one core (P158 #94: CLI, MCP and Claude call one package); P203 #163 (Fusion 360 via its MCP).
- P294: build a drag, drop, wire layer on `breadboard.json`; a page edit that adds a part must also change
  `requirements.json`. P295: live simulation in the page on a logic-level bench; `wokwi-cli` the final check.
