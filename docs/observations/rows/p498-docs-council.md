# P498 documentation council: rows

What the four lenses and the synthesis found in the README and the guides on 2026-11-01. Card: #682. Record:
[the council](../2026-11-01-p498-docs-council/README.md).

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | README Honest limits says nothing was validated on hardware, but `deploy.py --no-simulation` ran on a FireBeetle 2 ESP32-S3 on 2026-10-31 and 2026-11-01 (D14 lit D13), and the XIAO on 2026-10-14 and 2026-10-15 | brief, new person | verified | README:237 against README:91, P461 #629, P462 #630. Fix in PR1 (F1) |
| 2 | agents.md:681-683 says a mistyped `--project` answers ok, exit 0 | brief, AI reader | verified | check_all.py:334 raises, `main` returns exit 2 at :530-537. P117 #51 open per the brief (not re-read: GitHub rate limit). Fix in PR1 (F2) |
| 3 | The README run-date sentence stops at 2026-10-18 | brief, tech writer | verified | `journey.runs_up_to(README)` prints 2026-11-01. README:77. Fix in PR1 (F3) |
| 4 | README links P109 #43, P120 #54 and P128 #62 as plans, all closed as not planned | brief | verified | `gh issue view` on #43 and #54, #62 per the brief. README:65, 70, 245. Fix in PR1 (F4) |
| 5 | journey.md:252's `parts.py --match` output is stale (XIAO "stops at the footprint stage") | brief | verified | output note dated 2026-10-08 at journey.md:245, P278 since 2026-10-18. Fix in PR1 (F5) |
| 6 | commands.md:53 says init writes `CLAUDE.local.md`, true only when the store holds `rules.md` | brief | verified | ai_files.py:93-95. Fix in PR1 (F6) |
| 7 | The Bench cell says the button-and-LED breadboard is not wired, while the D14 button lit D13 on 2026-11-01 | synthesis | raised | README:91. PR1 checks it against the P462 comment |
| 8 | No "what do I type" example on the first screen | new person | verified | README:3-25. PR1 |
| 9 | A 2026-10-08 history paragraph sits in the intro | new person | verified | README:32-37. PR1 moves it to journey.md |
| 10 | "What it shows on the example" is a list of 12 issue links | new person | verified | README:45-72. PR1 |
| 11 | Table cells are paragraphs: Bench 4,348 characters | new person, tech writer | verified | `awk length` on README:91. PR1, guarded by PR2's 300-character cell test |
| 12 | No diagram in the README or commands.md, one Miro link to the board root | new person, diagrams | verified | grep of mermaid and miro.com. PR1 (two roads, frame links), PR5 |
| 13 | The README footer v0.9.0 is stale | new person | rejected | plugin.json ships 0.9.0, `check_docs.version_mismatch` enforces it |
| 14 | "not run here" about 10 times | new person | verified | 7 "not run here", 12 "not run" in the README. PR1 gathers them in one list |
| 15 | agents.md:444 is one 2,299-character table cell | AI reader | verified | `awk length`. PR1 shortens the row, PR4 moves the keys to agents-json.md |
| 16 | No JSON example of `check_spine.py --json`, and the check_all sample is from 2026-10-05 | AI reader | verified | agents.md:333 and :338. PR1 adds a dated example |
| 17 | The brief's example `check_spine.py --keep --json` lacks the folder `--keep` takes | synthesis | verified | `check_spine.py --help`: `--keep DIR`. PR1 uses `requirements.json --keep build --json` |
| 18 | No short contract at the top of agents.md | AI reader | verified | the exit table is at agents.md:669, after 668 lines. PR1 |
| 19 | A crash exits 1, said at README:202 and not under agents.md's exit table | AI reader | verified | agents.md:669-673. PR4 (one home) |
| 20 | No sentence on how a rebuild merges the Wokwi diagram, and "Is it ready?" ends without the next action | AI reader | raised | PR4 |
| 21 | journey.md's Idea section is 600 lines | tech writer | rejected | Idea is 274 lines (114-387). Idea to "Before you power it" is 598 (114-711). The split stands in PR3 |
| 22 | Exit codes have three homes | tech writer | verified | README:202, agents.md:554, agents.md:671. PR4 |
| 23 | developing.md mixes five jobs, and :600-643 belongs to `scrum/` | tech writer | verified | the headings. PR6 |
| 24 | Semicolons in the guides | tech writer | verified | agents 91, journey 89, developing 50, how-it-works 43, README 29. Each split PR rewrites what it moves |
| 25 | An anchor check is owed before any split | tech writer | rejected | `check_docs.broken_links` checks relative links and heading anchors already. Its gap is sub-folders (`doc_files` globs `docs/guide/*.md`). PR2 widens it |
| 26 | A length budget test is owed before any split | tech writer | verified | no such test in tests/. PR2 |
| 27 | Check the build-chain flowchart against `check_spine.py stages` | diagrams | rejected | no such subcommand: it reads `stages` as a path. The flowchart at how-it-works.md:19 matches its stage table and text |
| 28 | A status state diagram is owed | diagrams | raised | PR5 |
| 29 | Store, one-core context, and simulation-and-bench diagrams are owed | diagrams | raised | PR5 |
| 30 | A "which command next" flowchart for agents, a records diagram, and per-step sub-diagrams | diagrams | raised | later, after PR5. The rule "records grow by need" holds them until a reader asks |
| 31 | The "spark journey" Miro frame id is not in the team's notes | synthesis | raised | PR1 reads it from the board |
| 32 | The README needs an owner: it changes only through the documentation council or a story's one-sentence status line | PO, synthesis | raised | PR1 adds the rule to developing.md "The docs name only what is there" |
