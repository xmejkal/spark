# Architect C: files and the CLI stay the truth, a page watches them

> Keep `requirements.json` and `breadboard.json` as the one design. Claude keeps calling spark scripts. A tiny local
> server (or Electron's file watch) pushes each change to the page, and the page's drag writes the same file through
> that server. This is the KiCad Buddy shape without the MCP layer, and the MCP server of v0.13 wraps it later.

## The case

- **It is what works today.** The two files, `check_spine.py --keep` and `breadboard_keep.py` already carry a person's
  moves through a rebuild and name what was not kept (`docs/guide/agents.md:172-186`). Option C adds one watcher and
  one write route. Every other option rebuilds this flow behind a new door.
- **The document lives in one place, as in every tool in the survey.** Fusion, Figma and KiCad keep the document in
  the tool, and the MCP server is a thin door (research.md, "Pattern"). For spark the "tool" is the project folder.
  KiCad Buddy is the closest match: it edits `.kicad_sch`, keeps a `.bak`, then asks KiCad to reload
  (https://pypi.org/project/kicad-buddy/). Option C is the same edit-file-then-refresh pattern, with spark's page in
  KiCad's place.
- **Principles.** "A local CLI before a web service or an MCP server" and "free, few and local" (AGENTS.md). Nothing
  online, no account, no paid tier, offline after install. One core, many interfaces: the server is one more
  interface over the same library calls the CLI makes.

## What Claude calls, and what Petr sees

- Claude calls the scripts it calls now: `parts.py`, edits `requirements.json`, `check_spine.py --keep --json`.
- The watcher sees `breadboard.json` change and pushes a reload event (Server-Sent Events from a 127.0.0.1 server
  that checks `Origin`, per https://modelcontextprotocol.io/specification/2025-06-18/basic/transports ; or `fs.watch`
  in Electron). The page redraws in place and animates the parts that moved, so a reload reads as a step, not a flash.
- Honest limit: Petr sees one change per script call, not a cursor moving. A swap is one rebuild, so it lands as one
  jump. To feel like "watching Claude act", the page diffs old and new layouts and plays the diff (part fades out,
  new part slides in, jumpers redraw). That diff runs in the page from two files; it needs no live channel.

## The example: Claude swaps the LED for a buzzer, then Petr drags it

1. Claude reads both files, finds `led1`, finds a buzzer record with `parts.py` (`wokwi-buzzer` simulates, P294
   finding, "The PO's example").
2. Claude edits `requirements.json` (LED out, buzzer in, same signal pin), runs `check_spine.py --keep --json`.
3. The rebuild writes `breadboard.json`; `kept` names the LED's jumpers as not kept. The watcher fires; the page
   fades the LED, slides the buzzer in, redraws two jumpers. Claude says what moved.
4. Petr drags the buzzer three rows down. The page POSTs the new layout; the server writes `breadboard.json` (a temp
   file, then a rename). Only the layout changes, so `requirements.json` stays as it is.
5. At Claude's next turn it runs the rebuild with `--keep`; the move survives if the pins sit over free holes, one
   row each (`scripts/breadboard_keep.py:157-230`). A drag that adds a part sends a change request instead, because
   a kept part needs its id and type in the circuit (`scripts/breadboard_keep.py:160-162`).

## Growth into the v0.13 MCP server (#94) without rework

The server's routes (read layout, write layout, rebuild) are calls into the same library. In v0.13 the same calls get
MCP tool names over Streamable HTTP, and that server's SSE stream is the page's push channel. The page does not change;
only its endpoint gains an MCP door. Swap points fit as strategies behind the server: `SimulationEngine` (wokwi-cli,
spark bench), `Renderer` (spark SVG, @wokwi/elements, Konva), `Surface` (local page, Electron, Artifact),
`FirmwarePlatform` (exists, `scripts/firmware_platform.py`). Each gets a fake; the file store gets an in-memory fake.

## Weak spots, named

- **Artifact.** A claude.ai page cannot reach a 127.0.0.1 server unless the `mcp` capability with `host:<name>` works
  ("Claude app only", research.md; unverified). In claude.ai the Artifact stays a republished snapshot (P272). Option
  C serves the local page and Electron well and the Artifact poorly.
- **Races.** Claude's rebuild and Petr's drag both write `breadboard.json`. Rule: the server holds one lock; a write
  carries the file version it read, and a stale write is refused and redrawn. Unverified: no such code exists.
- **Half-written file.** Spark writes with `Path.write_text` today (`scripts/breadboard.py:490,497`), not a temp file
  and rename, so a watcher can read half a file. The first step fixes this.
- **No undo.** Files have no history. A `.bak` per write (as KiCad Buddy) or a git commit per rebuild gives one step
  back; real undo needs an event log, later.
- **Latency.** A full rebuild runs per Claude edit; its time is not measured (unverified).

**First small step.** A `layout_server.py` (one class, `main()` parses and prints): serve `page.html`, push an
event when `breadboard.json` changes, accept a layout POST with a version, write by temp file and rename. Test with an in-memory store fake.

**What the MVP decides now.** 1. Files are the truth; a live channel carries "changed" events, never the state.
2. Writes are atomic and versioned; a stale write is refused. 3. A page edit that changes the circuit is a change request for Claude, not a file write.
4. The Artifact surface stays a snapshot until the `host:` capability is proven on this account.
