# Verification
<!-- One line per ★ claim in brief.md; rejected claims stay. refuter: holds · partly · refuted · could not open, with
the line it read, verbatim. result: reproduced · not reproduced · rejected. keep: the words any summary of the claim
must carry (phrases separated by ;), or none; keep comes last on the line.
e.g. `- ★C3 · STATUS.md:84 · refuter: partly — "Shown on the C6, assumed for the S3" · reproduced how: re-read STATUS.md:84 · result: reproduced · keep: assumed for the S3` -->
- ⟨fill⟩ <!-- REQUIRED:claims -->

## Agree / split
<!-- Where the lenses and the refuter agree, and where they split; each split becomes a question.
e.g. `- Split: Feasibility says a day, Risks says a week · Q4` -->
- Agree: all six lenses on ★C2, that the commands and agent files are in Claude Code's formats. Existing-first and architecture on ★C1, that the scripts call no model <!-- REQUIRED:agree-split -->
- Agree: feasibility, architecture, UX and existing-first on ★C3, that the core's own sentences name Claude and `/spark:` commands, with counts that match (79 lines, 42 files)
- Agree: feasibility, UX, existing-first, risks and the user's journey on ★C13, that nothing fails when a flag, key or code is taught nowhere
- Agree: the user's journey, UX and architecture on ★C19, that the deploy phase never shows as done
- Agree: feasibility and architecture on ★C8 (two event kinds, no async) and on ★C7 (12 of 27 CLIs on the core)
- Agree: existing-first, feasibility, risks and architecture on ★C17, that no agent eval exists and the model table is set by hand
- Agree: existing-first and risks on ★C6, each from its own `command -v` run
- Agree: risks, feasibility (FE-18) and architecture ("the CLI works fully first") that no direction comes before the core's CLI work. No lens proposes a second architecture
- Split: spark-main's reading on #1522 (check_docs.py guards commands, skills and agent pages) against feasibility (FE-1: it reads README.md, AGENTS.md and docs/guide only) · settled by FE-1's read of tools/check_docs.py:61-64. ★C13 carries the correction
- Split: architecture (AR-9, AR-20: `flow.py show --json` answers `next: []`) against feasibility (FE-9) and UX (UX-4), which ran the command and saw a step · settled for the build by the two runs. P1034 #1517 holds the other phases. ★C12
- Split: the core-gaps finding (11 CLIs on the core) against feasibility and architecture (12) · settled by the architect's grep: 12 of 27
- Split: three counts of untaught flags. Feasibility: 13 of 192, in the agent text. `tools/inventory.py` (risks, UX): 16 of 202, on any page. The user's journey: 5 flags in 13 of 27 scripts · three populations, not one error. What counts as "taught" is Q9
- Split: risks (RA-16: the walks fail on product behaviour, and a guard is not where they fail, "a weak sign") against the user's journey (UJ-5, UJ-6: a tool and a flag invented again) and UX (UX-1, UX-2: no guard, a stale entry page) · Q9, A6, and the account question Q15
- Split: the epaper session's leaning ("no server until a case needs it") against architecture (the PO named a live page and an SSE MCP as consumers, and both are servers) · Q6
- Split: architecture (move the commands' knowledge into skills, add a stdio MCP adapter) against risks (pre-mortem 3: a port becomes a second product, and W14) · Q7, Q8
- Split: existing-first (EX-25: the plugin as it is "could be tried on a local model without a second harness") against risks (RA-21: on this 8 GiB M1 a local model is "a weak driver") · Q11
- Split: feasibility (FE-12: a local model needs "no code") against architecture (AR-21: tool profiles from the flow's now phase) and UX (UX-3: the guide has no short layer) · Q11
- Split: feasibility (FE-11: evaluation "needs nothing from the core to start") against architecture (AR-22: it needs one join key and one sink, a session id that the harness passes and a first caller of the trace hook) · Q10, seam S6
- Split: existing-first (EX-18: an eval tool is already on the PO's Mac) and UX (UX-14: one row per release) against risks (W14 names an eval harness as its own example, and an eval was pruned once) · Q10, A5
- Split: on Hermes Agent, existing-first, architecture and UX read its pages (E) while feasibility holds the same facts as H from snippets, and risks notes that its sources conflict on install paths · kept as E with the caveat "read through a summariser" in ★C5. Which Hermes the PO means is Q7
- Split: inside existing-first (EX-2), spark's research of 2026-10-13 says Codex has an agent format and a third-party page says a Codex plugin holds no agents · not settled, on the collection plan
- Split: three word counts for the agent text: 64,430 (UX-3), about 63,500 (UJ-20) and 28,511 for the 16 prompt files (FE-13) · three sets of files, named in ★C16's caveat. No question
- Split: feasibility (FE-10: there is one Reporter, the terminal's) against the architecture lens's layer diagram ("Reporters: Terminal, Masking") · not settled, the architect did not check it. It changes no option
- Split: UX asks whether a recorded deploy counts as the deploy phase done, while P867's D8 already chose "recorded" and "none recorded", never as a pass · the brief's Found on the way proposes D8's words
- Split: risks names A1 (outside Claude Code) and A7 as the riskiest, and the architect proposes A1 widened to any of the five directions, with A9 and A7 next · Q1
- Split: the UX lens leaves open whether an elicitation "accept" can stand for the person's yes, and the architect's opinion is no for a flash · Q12
- Not yet here: the refuter's lines. The refuter has not read this synthesis, so no ★ claim reads "holds"
