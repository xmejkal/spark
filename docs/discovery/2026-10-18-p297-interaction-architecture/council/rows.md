# P297 council rows

Finding rows from the council (three architects and the refuter, all Opus), kept here and not in
`docs/observations/INDEX.md`, per P296 [#358](https://github.com/xmejkal/spark/issues/358). Status: raised, verified,
rejected, acted.

| Row | Raised by | Finding | Status | Where |
|---|---|---|---|---|
| R1 | survey | Fusion, Figma and KiCad keep the document in the tool; the MCP server is a thin door | verified (sources in research.md) | finding, summary |
| R2 | A | add or swap must change `requirements.json` and `breadboard.json` in one step, in the core | acted: MVP decision 4 | finding |
| R3 | A | a token cost per tool limits the MCP server to about seven tools | rejected by refuter: tool search, Fusion MCP has 93 tools | refuter.md |
| R4 | A | Claude Code to a local HTTP MCP server is unverified | rejected by refuter: `claude mcp add --transport http` is documented | refuter.md |
| R5 | A | an MCP server is needed for a live view | rejected by refuter: a file watch with SSE gives it | refuter.md |
| R6 | A | an event log with undo in the MVP | rejected: `.bak` or a commit per rebuild is enough now | finding, decision 6 |
| R7 | B | `db` limits 256 KiB per doc, 25,000 docs, last-writer-wins | verified by refuter in db.d.ts | refuter.md |
| R8 | B | `room` agent peer is flag-gated, off by default | verified by refuter in room.d.ts | refuter.md |
| R9 | refuter | `host:` MCP is limited to the Artifact's owner (`mcp.d.ts:122`) | verified | finding, "our interface" |
| R10 | refuter | no `.d.ts` names `ArtifactData`; B rests on it | partly answered: the tool is listed in this session's deferred tools and in the Artifact tool's text; not run | open question 2 |
| R11 | refuter | B keeps two truths: a drag lives only in `db` until Claude copies it | verified (reasoning) | options table |
| R12 | C | spark writes `breadboard.json` with `write_text` (`scripts/breadboard.py:490,497`), so a watcher can read half a file | verified by refuter | MVP decision 3 |
| R13 | refuter | C's server lock misses Claude's direct writes; the check belongs in the core | acted: decision 1 and 3 | finding |
| R14 | refuter | all three papers covered only the breadboard while the card now covers every step | acted: the journey table and variants | finding |
| R15 | lead | `deploy.py`, `run_scenario.py`, `drawer.py` have no `--json`; no theme, remove or variant command | verified by grep on main, 2026-10-18 | journey table |
| R16 | lead | Claude Code terminal rendering MCP Apps: no source found | unverified | options table |
| R17 | refuter | whether `db` is on for this account; whether `files` reads local disk | unverified | open question 2 |
