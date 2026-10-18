# Architect B: the Artifact's `db` as the shared design

> **TL;DR.** The design lives in the Artifact's `db`. Claude writes it with `ArtifactData`, and the page draws it live
> through `onSnapshot`. A drag writes a row, and Claude reads that row on its next turn. This is the Fusion pattern
> (the document lives in the tool, Claude acts through a door), with claude.ai as the tool and no server of spark's own.
> Its weak spots: it needs an online claude.ai account, Claude gets no signal when Petr drags, and it has no local or
> Electron story without a second store. All Artifact facts below come from the d.ts files and were not run (unverified).

## Shape and swap points

- `DesignStore` (strategy): `load()`, `apply(change)`, `subscribe(onChange)`. `ArtifactDbStore` wraps `claude.use("db")`.
  `FileStore` reads and writes `breadboard.json` and `requirements.json` (local page by download, Electron by fs).
  `FakeStore` keeps it in memory for tests. Only `ArtifactDbStore` knows `db`. The page picks it when
  `claude.use("db")` resolves, and falls back to `FileStore` when it resolves `null` (db.d.ts, "AVAILABILITY").
- Other strategies, unchanged by this choice: `SimulationEngine` (wokwi-cli, spark bench), `BreadboardRenderer` (spark SVG,
  @wokwi/elements, Konva), `Surface` (local page, Artifact, Electron), `FirmwarePlatform` (`scripts/firmware_platform.py`).
- Documents: `parts/<id>` (type, x, y, rotation), `wires/<id>`, `requirements/main`, `meta/state` (`rev`, `actor`,
  `status`). One document per part keeps writes small. Writes are last-writer-wins per document (db.d.ts, line ~495),
  so a drag on the buzzer and Claude's edit of the button do not clobber each other. Limits: 256 KiB per document,
  25,000 documents per artifact (db.d.ts ~487). A breadboard fits easily.

## What the person sees while Claude acts

Claude first sets `meta/state.status = "Claude: swapping LED for buzzer"`. The page shows a banner and greys the drag
handles. Each `ArtifactData` batch reaches every open view through `onSnapshot`, with no reload and no lost zoom. A
republish (the `artifact` arm) reloads every view, so Claude never republishes to show a change. `room` adds a live
"Claude is here" marker only when the server admits the publishing session as `kind: "agent"`, and that is
"flag-gated, off by default" (room.d.ts 52-60). Else `meta/state` carries presence; the MVP does not need `room`.

## What Claude calls, and how the rebuild gets the state

1. `ArtifactData list parts`, `list wires`, `get requirements/main` and `get meta/state`.
2. It writes `breadboard.json` and `requirements.json` on the Mac (one small Python class, `DbSnapshot`, maps rows to
   files and back, so no agent prompt repeats the mapping).
3. `check_spine.py --keep` rebuilds as today; tscircuit and wokwi-cli run on the Mac as today.
4. `ArtifactData batch`: the rebuilt layout, the `not kept` list in `meta/state`, `rev + 1`, status cleared.

The files on disk stay the record that git, the CLI and other users see. `db` is the live copy during a session.
Claude writes the files before every rebuild, so the two never drift by more than one turn.

## The example: Claude swaps the LED for a buzzer, then Petr drags it

Petr types "swap the LED for a buzzer". Claude sets the banner, reads the rows, edits `requirements.json`
(LED out, `wokwi-buzzer` in, same GPIO), runs `--keep`, and writes the batch. Petr sees the LED vanish and the buzzer
appear with its jumpers, then the banner clears. He drags the buzzer three rows down. The page writes `parts/buzzer`
with `actor: "person"` and `rev + 1`. Claude does not hear it. Petr says "moved it", or the page's "Tell Claude"
button calls `sendToClaudeSession` (room.d.ts line 19). That reaches "THEIR Claude beside this page", and whether it
reaches a Claude Code terminal is unverified. Claude reads `parts/buzzer`, sees the new rows, writes the files and
rebuilds with `--keep`.

## Weak spots, named

- **No push to Claude.** Claude learns of a drag only on its next turn. The Fusion MCP has the same gap.
- **Online and account lock-in.** `db` needs a signed-in viewer and claude.ai. Snapshots with `fromCache` cover short
  gaps only (db.d.ts ~253). There is no offline mode. Deleting the artifact erases the store. Spark is public under
  MIT, so a user without claude.ai gets only `FileStore`.
- **Two stores to keep honest.** `ArtifactDbStore` and `FileStore` must pass one contract test on `FakeStore`.
- **Unknown availability.** P294 left open whether `db` is on for this account (finding.md section 4 (b)).
- **Token cost per hop.** Every read and write is a tool call with rows in context. That is cheap per part and costs
  more on a whole-board rebuild. Money: no cost beyond the account (unverified).
- **Principles.** Free: yes. Few: yes, because no server and no MCP of spark's own (ArtifactData is Claude's own tool).
  Local: no. Local pages and Electron work only through `FileStore`, so this option bends "a local CLI first".

## First small step, and what the MVP decides now

Step: publish a one-part page that declares `db`. Claude sets `parts/led` with `ArtifactData`, and Petr watches it
appear. He drags it, and Claude reads the new x and y with `get`. Measure the delay, and check for `kind: "agent"` in
`room`. If `db` is off for the account, this option ends here. Decide now: the `DesignStore` interface and its
contract test; one document per part; disk files as the record, `db` as the live copy; `rev` and `actor` on every
write; how Claude learns of a drag (Petr says so, or the button) and nothing more.
