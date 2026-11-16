# P835: how a plugin is meant to give a person an interface with Claude: the finding

Card: [P835 #1197](https://github.com/xmejkal/spark/issues/1197), a spike (research only). Two research agents (Opus)
read the sources on 2026-11-16. Each source line carries a tag: D (a source says it directly), E (tried, read-only) or
H (inference). The lines are in [artifacts-and-plugin.md](artifacts-and-plugin.md) and
[tool-frontends.md](tool-frontends.md).

## The answer

> Keep the MVP plan. The page shows the flow and takes requests, and Claude Code on the person's Mac acts. The page
> shows each tool's own picture where one exists, and spark's own drawing only where none does. The MVP has no SSE,
> no spark MCP server and no embedded tool. One new card follows the MVP: P836, a spark mod in Claude Code, which
> is untested. Its plan: if the session is idle, the mod acts on a click.

- A page cannot start Claude's turn: "There is no way for a page to start Claude's turn by itself" (the runtime's
  `room` types). A comment wakes only a cloud session. So a click waits for the person's next message (D8). P836
  plans a spark mod that submits it (untested).
- A page cannot call out. The runtime blocks fetch, XHR and WebSocket to other hosts, and iframes of other sites
  (`guide`, topic pages). So the page has no SSE and no embedded Wokwi. The runtime pushes `db` rows to the open page
  through `onSnapshot`. A row showed less than 1 s after the store saved it. From the page's own stamp, the 2 timed
  rows took 2.7 s and 3.8 s (brief.md Results step 2). So live progress can be one `db` row per build stage (H, not tried).
- MCP: a page reaches a local MCP server only in the Claude app (`host:<name>`, "Claude app only"). Claude Code
  renders no MCP App UI. The rule of docs/discovery/2026-10-19-p323-target-architecture/council/ai-interface.md §8
  holds as written: "Build it when a named host cannot run a shell, or when P178's shared store needs it, and not
  before the catalog covers every operation." §8 already names Claude Desktop as such a host. The app's chat has no
  shell, but its Code tab runs Claude Code.
- A Claude Code mod draws a pane beside the conversation, with buttons. It runs programs, calls MCP tools and runs on
  a timer. If the session is idle, it can submit a prompt (https://code.claude.com/docs/en/plugins/mods/api).
- The tools' frontends:

| tool | verdict |
| --- | --- |
| Wokwi simulator | a link out only, with a line that the free plan makes the project public. Simulate stays in the terminal. |
| Wokwi part pictures (`@wokwi/elements`, MIT) | optional later, bundled inline |
| tscircuit schematic and PCB | tscircuit's own SVG export, already in the kept page.html as an `<img>` data URI (kept_files.py:267-268). P828 brings the views to the Artifact page. Its interactive viewers come later, bundled offline. |
| KiCad (KiCanvas, MIT, alpha) | later, in the PCB and order phase |
| the breadboard | spark's own SVG. Wokwi's editor draws breadboards, but no tool that spark can embed offers a breadboard view. |

A later viewer is bundled inline. The runtime allows scripts from a few CDNs, but D7 loads nothing from the web, and
the page must also work from disk. Setup downloads the bundle into the store, because spark commits no vendor file.

## What it changes

- P826 #1184: nothing renders Mermaid on the page. A diagram is inline SVG written by Python, or the page leaves it out.
- P827 #1185: light and dark theme colours. The offer buttons are hidden from a viewer who is not the owner (`user`).
  The page loads no iframe (the runtime refuses one) and no outside script (D7).
- P828 #1186: the current wiring step survives a republish (`window.claude?.hot?.snapshot`).
- P829 #1187: no change. Brief Q9 has its answer: no spark MCP server and no `host:` in the MVP.
- P834 #1196: the Claude desktop app is the first host with a reason for a spark MCP server.
- New: P836 #1198, the spark mod. Its first check: can a mod's `$.mcp.call` reach the claude-artifacts server?

## Not checked

- Whether a bundled viewer runs inside an Artifact. That needs a test page.
- Whether `files` reaches a local checkout.
- Whether circuitjson.com keeps an uploaded file.
- Whether kicanvas.org reads a dropped file locally.
