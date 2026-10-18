# P297 refuter (2026-10-18): claims checked against the worktree, the Artifact .d.ts (0.2.85) and the web

1. CONFIRMED, citations in C. `breadboard_keep.py:160-161` (a kept part needs its id and Wokwi type in the circuit),
   `:157-230` (keep rules), `breadboard.py:490,497` (`write_text`, no temp file and rename), `agents.md:172-186`.
2. CONFIRMED, B's db facts. `db.d.ts:487-488`: 256 KiB per document, 25,000 documents. `:345,494` last-writer-wins.
   `:253` `fromCache`. `:118-122` `claude.use("db")` resolves `null` when unavailable.
3. UNVERIFIED, B's load-bearing door. No `.d.ts` file names an `ArtifactData` tool, or says that Claude writes `db`
   (grep found none). The only hint: `room.d.ts:60` "an agent otherwise narrates through `db`". B's whole option rests
   on this tool. B's first step must prove it before anything else.
4. CONFIRMED, with a nuance B misses. `room.d.ts:52-57`: the agent peer is "flag-gated, off by default". It is the
   *Claude Code session that published the page*, and it gets "a digest, never a live stream". So, with the flag on,
   a drag *can* reach Claude. B's "no push to Claude" is true only by default.
5. CONFIRMED, and it is stricter than the papers say. `mcp.d.ts:110-123`: `host:` runs only in the Claude app. In a
   browser tab every call fails, and "only the Artifact's owner can use host servers for now". A and C omit the owner
   limit.
6. REJECTED, A's "Claude Code connects as an HTTP MCP server (unverified)". It is documented
   (code.claude.com/docs/en/mcp: `claude mcp add --transport http`). Claude Code also handles `list_changed`.
7. REJECTED, A's token worry, and A's reason for the adapter. Claude Code's tool search is the default, so tools load
   on demand, and Fusion's MCP has 93 tools, not about 7. The cost of an MCP server is not tokens. It is a second door
   to build and keep. A says the adapter is needed "for the live view, which a CLI cannot give". C refutes that: a
   file watcher with SSE gives the same live view and needs no MCP. So the MCP adapter has no MVP need, and "a local
   CLI before an MCP server" says to wait.
8. REJECTED, A's and B's undo and event log in the MVP. The project folder is under git. A `.bak` or a commit per
   rebuild gives undo for free. An event log is behaviour that nobody has asked for yet.
9. REJECTED, as framed, C's "one change per script call" as a weakness. A gives one event per command, and each
   command also rebuilds. Petr sees the same steps in A and C. The finer grain comes from the command vocabulary,
   not from MCP. C can adopt the vocabulary too.
10. CONFIRMED, a defect in C. The server lock does not cover Claude. Claude edits `requirements.json` and runs
    `check_spine --keep` straight on disk, outside the server. Fix: compare-and-swap on a content hash *in the write
    path* (`breadboard.write`, by temp file and rename). Then any writer, server or CLI, gets refused when stale.
11. CONFIRMED, a defect in B, two sources of truth. A drag lives only in `db` until Claude syncs it. A CLI run, or git,
    in between misses the drag. Lock-in: the user needs a signed-in claude.ai account, it runs online only, and
    deleting the artifact erases the store. That breaks "local" for a public MIT tool, and Electron and the local page
    fall back to a second store anyway.
12. UNVERIFIED: whether Claude Code (terminal or VS Code extension) renders MCP Apps. The ext-apps README lists
    "VS Code" (Copilot chat), not Claude Code. No paper confuses the terminal with Desktop. All three say: no iframe
    in the terminal. Also unverified: whether `files` (`files.d.ts:2`) reads the local disk or a cloud project copy.
    If it reads the disk, an Artifact could show `breadboard.json` read-only, with no `db`.

## What no paper covers

The card now covers ALL steps (parts, requirements, build, page look, simulation, firmware, deploy, console,
variants), yet all three papers design only the breadboard drag. Console, deploy and live simulation stream from USB
and local processes: only a local push channel (C's SSE) carries them, and an Artifact reaches them only via `host:`.
Variants ("DC motors vs steppers") are folder copies or branches, natural with files as truth, awkward in `db` or a
log. "Rebuild with dark colors" is a renderer setting in a file, not a board command.

## Verdict

C's spine survives, extended into the hybrid: one core with a command vocabulary over files (A's MVP decisions 1, 2,
4); every step a CLI `--json` call now; files stay the truth; one thin local server pushes "changed" events and
streams (build, simulation, console) to the one TypeScript page; an MCP adapter over the same core with v0.13 (#94)
when a host needs it; the Artifact is one surface, a snapshot until `ArtifactData` and `host:` are proven here.

## Fixes the synthesis needs

1. Widen the vocabulary to every step (build, restyle, simulate, flash, console, variant). 2. Atomic, hash-checked
writes in the core, not a server lock (point 10). 3. Undo by `.bak` or a commit; no event log in the MVP. 4. Drop "a
CLI cannot give a live view" as the reason for MCP; name the adapter's real trigger. 5. Gate the Artifact surface on
`ArtifactData`, the room agent flag and the `host:` owner limit.
