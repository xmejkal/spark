# Verification
<!-- One line per ★ claim in brief.md; rejected claims stay. refuter: holds · partly · refuted · could not open, with
the line it read, verbatim. result: reproduced · not reproduced · rejected. keep: the words any summary of the claim
must carry (phrases separated by ;), or none; keep comes last on the line.
e.g. `- ★C3 · STATUS.md:84 · refuter: partly — "Shown on the C6, assumed for the S3" · reproduced how: re-read STATUS.md:84 · result: reproduced · keep: assumed for the S3` -->
- ★C1 · `flow.py show --project . --json` in p934-display2 · refuter: partly — "`stands_at deploy`, `build could-not-run`, `deploy not-started`" and "From 2026-11-22 11:46 to 2026-11-23 about 15:24 the page said `data-stands-at="build"`" · reproduced how: re-ran `flow.py show` 16:35 CET (stands_at deploy, deploy not-started, the NOW sentence), counted the 27 logs (18 seen, 9 unknown) · result: reproduced, claim narrowed · keep: since the 15:23 rewrite; the copy was not rewritten in the walk <!-- REQUIRED:claims -->
- ★C5 · `describe_capabilities` files · refuter: could not open — "this run had no Artifact tool" · reproduced how: the facilitator called `describe_capabilities` files at 16:40 CET: "Runtime contract 0.2.98" · result: reproduced · keep: the contract moves
- ★C10 · scripts/spark/flow/phase_readers.py:554-560 · refuter: partly — "a project whose board has a Wokwi model stands at simulate first" · reproduced how: re-read phase_readers.py:554-560 and guide.py:84-93 (on main) · result: reproduced, claim narrowed · keep: past firmware and simulation
- ★C12 · diary.md:74, :170 in p934-display2 · refuter: partly — "Five clicks in 11 minutes 27 seconds hold. \"The page was used for 11 minutes\" does not" · reproduced how: `gh issue list --state all` (labels doing and next on 8 issues), the diary's later page lines (:203-204) · result: reproduced, claim narrowed · keep: clicks, not views
- ★C13 · AGENTS.md:51, p934-display2/.spark/project.json · refuter: partly — "p934-display2/.spark/project.json holds `goal`, `must` (2 lines) and `decided`" · reproduced how: the refuter's quote of scripts/spark/records/brief.py:2; not re-read by the facilitator · result: rejected as first written, rewritten · keep: the brief record is spark's
- ★C16 · `describe_capabilities` files; GitHub Docs · refuter: partly — "GitHub Pages sites are publicly available on the internet, even if the repository for the site is private" · reproduced how: the facilitator re-read `describe_capabilities` files ("reads a Claude Code project's files as the viewer") · result: reproduced, claim narrowed · keep: with the viewer's access

## Agree / split
<!-- Where the lenses and the refuter agree, and where they split; each split becomes a question.
e.g. `- Split: Feasibility says a day, Risks says a week · Q4` -->
- Agree: all three lenses and the refuter: the deploy reader is fixed at not started (★C10), and the page is a copy written only at /spark:page (TECH-4, R-2) <!-- REQUIRED:agree-split -->
- Agree: the files route and a public static host are set aside on privacy and cost (★C16), and the page already works from disk (C19)
- Split: the facilitator put the true stand first (slice 0); the refuter and the PO's own words put readability first · Q9
- Split: the user lens orders the project's issues and must lines first (O2b); the facilitator leaned to O2a; the PO assistant decided nothing · Q2
- Split: the brief treated the deploy reader as the fix; the PO assistant and the refuter say its states are not decided ("ready unknown") · Q8 and O5c
- Split: the tech lead offers b1 (O3b) as cheaper; the refuter says it saves only the pictures · Q3
