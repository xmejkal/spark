# Architect A: spark as an MCP server with board tools, one page subscribed to it

> Spark becomes the tool, as Fusion is the tool for the Fusion MCP. One core applies board commands and logs them.
> Claude calls the commands as MCP tools. The page subscribes to the same process and sends drags as the same commands.

## The shape
- **Core (Python, one job each).** `BoardSession` holds `requirements.json` and `breadboard.json` and applies one
  command: `board_get`, `part_add`, `part_swap`, `part_remove`, `wire_connect`, `part_move`, `undo`. Each command
  changes both files together, so the P294 trap (a page adds a part, the next rebuild drops it) cannot happen.
  Each applied command becomes one event `{rev, actor: claude|person, op, args, before}` in `board-log.jsonl`.
- **Source of truth: files plus the command log.** The kept files are the snapshot after each event; server memory is a
  cache. Undo restores `before` (https://martinfowler.com/eaaDev/EventSourcing.html). CLI and `--keep` work serverless.
- **Doors, all thin.** A CLI `board.py apply --json` first. Then an MCP adapter over the same class: one local process
  on 127.0.0.1 with Streamable HTTP, SSE for notifications and an `Origin` check
  (https://modelcontextprotocol.io/specification/2025-06-18/basic/transports). Claude Code connects to it as an HTTP
  MCP server (unverified for this setup). The page connects to the same port and gets `board_changed` events.
- **Surfaces.** Local page and Electron: the TS page opens the SSE stream; Electron also starts the server. Claude
  Desktop and claude.ai: the same page as an MCP Apps `ui://` resource, where "the UI can call other tools through the
  host" (https://github.com/modelcontextprotocol/ext-apps). Artifact: the `mcp` capability reaches `host:<name>`, a
  local MCP server, in the Claude app only (unverified). Claude Code terminal: no `ui://` (unverified), local page beside.

## Swap points (each a named interface with a fake)
| Interface | Real strategies | Fake |
|---|---|---|
| `BoardStore` (Python) | `KeptFiles` (two JSON files + log) | `MemoryStore` |
| `SimulationEngine` | `WokwiCli`, `SparkBench` (P295) | `FakeEngine` with scripted pin levels |
| `FirmwarePlatform` | exists in `scripts/firmware_platform.py` | exists |
| `BoardChannel` (TS) | `HttpSse`, `McpAppsBridge` (postMessage), `ArtifactDb` | `LoopbackChannel` |
| `PartRenderer` (TS) | `SparkSvg`, `WokwiElements`, `Konva` | `BoxRenderer` |

The page knows only `BoardChannel` and `PartRenderer`. Changing the surface or the drawing touches no caller.

## The example: Claude swaps the LED for a buzzer while Petr watches, then Petr drags it
1. Claude calls `board_get` and gets rev 41 with `led1` on GPIO 4.
2. Claude calls `part_swap {id: led1, record: wokwi-buzzer, base_rev: 41}`. The core writes both files, logs rev 42
   (actor claude), rebuilds with `--keep` and returns the `not kept` jumpers.
3. The page gets `board_changed rev 42` over SSE. It redraws, outlines the buzzer for two seconds and shows the line
   "Claude: led1 -> buzzer1, 1 jumper not kept". Petr sees it with no reload and no republish.
4. Petr drags the buzzer four rows down. The page sends `part_move {id: buzzer1, x, y, base_rev: 42}` through its
   channel. The core logs rev 43 (actor person) and every view redraws.
5. Next turn Claude calls `board_changes since 42`, reads "person moved buzzer1". A stale command gets `conflict`
   and the newer state. (MCP resource-update notifications reaching Claude between turns: not checked, not relied on.)

## Cost, offline and fit with the principles
- Offline: yes for server, files and local page. Only the Artifact and MCP Apps surfaces need claude.ai.
- Cost: core and CLI small; MCP adapter with HTTP and SSE medium; MCP Apps and Electron surfaces medium each, later.
  The Python MCP SDK is one pip package (free; size not checked). A hand-written JSON-RPC adapter avoids it.
- "A local CLI before an MCP server": kept. The CLI over `BoardSession` ships first and stays the reference door.
  The MCP adapter comes only for the live view, which a CLI cannot give.
- "One core, many interfaces" and v0.13 #94: this is a thin slice of #94 (CLI, MCP and Claude call one package),
  limited to board commands. It does not refactor the rest of `scripts/`.
- Research pattern: Fusion, Figma, KiCad keep the document in the tool; the MCP server is a thin door
  (https://github.com/faust-machines/fusion360-mcp-server). Spark is the tool here, so spark holds the door.

## Weak spots, named
- A long-running process: who starts it, one per project, a port clash with a second session (needs a lock file).
- The Claude Code terminal has no live view; Petr keeps a browser tab beside it. The Artifact path needs `host:` MCP.
- More tools cost context tokens every turn (keep about seven). Pulls part of v0.13 forward: a second core if #94
  later picks another shape. Two writers need revision checks from day one, or a drag silently loses Claude's swap.

## First small step
`scripts/board_session.py` with `BoardSession.apply(command)` over `KeptFiles` and `MemoryStore`, three commands
(`board_get`, `part_swap`, `part_move`), the JSONL log, `undo` and revision checks, plus a CLI `board.py`.
Tested with the fake store. No server, no page change.

## What the MVP decides now so it does not block this target
1. The page sends commands, never whole saved files. A drag is `part_move`, not a new `breadboard.json`.
2. One command vocabulary (op names, stable part ids, JSON schema), shared by CLI, MCP and page.
3. Every change carries `rev`, `base_rev` and `actor`. The page uses a `BoardChannel` interface, even over a saved file.
4. A part add or swap changes `requirements.json` and `breadboard.json` in one step, in the core.
