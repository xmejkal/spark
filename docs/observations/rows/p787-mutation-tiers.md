# P787: the mutation rows run in tiers, PR 0 of 7: rows

Card: [P787 #1088](https://github.com/xmejkal/spark/issues/1088); the council's plan is the first comment on the card (data lens on
Sonnet, tech lead on Fable, 2026-11-12; the PO: "go, build it"). PR 0 of 7: `--copy`'s red pre-check fixed and the exact duplicate
rows dropped; no ledger, no tiers, no budget (PRs 1 to 5). This file holds the acted, raised and rejected findings only (rules.md).
Built on Fable, 2026-11-12.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the plan: "261 tables hold 3158 rows" | plan, build | acted | 271 tables, 3183 rows on main `ed679c38` before this PR (P777 and P778 added tables after the plan was written); 3171 after |
| 2 | the plan: "a row's identity is `sha1(find + replace)[:12]`, so a duplicate in two tables is one row" | plan, build | raised | 24 pairs share that key, and 12 of them sit on two different files (`the scrub skipped` on four golden test files, the P443 `hasattr` row on three stand-ins, the P455 rules refusal on three checks): one `find` and `replace` on two files are two defects. The identity must hold the file too: `sha1(file + find + replace)`. Those 12 cross-file pairs stay. For PR 1 (the ledger's key); the card holds this row |
| 3 | the plan: "12 exact" duplicates | plan, build | acted | right under the identity of row 2 (the same file, `find` and `replace`): 12 rows dropped, rows 4 to 15, by `scratch/drop_dupes.py` (a text edit of each table, proved by parsing: the rows after are the rows before minus the one; no table is `json.dump`ed) |
| 4 | `p219-reader.json:15` "ignore flag inverted" | build | acted | dropped; its twin `p219-de2.json:2` "inverted-flag" stays (`scripts/spark/bench/image_evidence.py`) |
| 5 | `p239-pr8.json:7` "plan-older-runs-always-refuse" | build | acted | dropped; twin `p219-de2.json:1` "refuse-always" (`image_evidence.py`) |
| 6 | `p423-guard-lines.json:8` "a refusal's diagnostics print around the guard" | build | acted | dropped; twin `p423-guard-lines.json:6` "the look's failed read prints its lines without the guard: run_cli prints the diagnostics raw" (`scripts/spark/core/cli.py`), the same table |
| 7 | `p429-firmware-line.json:3` "P429: an indented firmware line is not seen by the reader" | build | acted | dropped; twin `p130-followup.json:4` "an indented, unreadable firmware line is not seen" (`scripts/spark/firmware/sim_project.py`) |
| 8 | `p433-bench-codes.json:27` "a bad flag with --json prints the usage" | build | acted | dropped; twin `p433-bench-codes.json:26`, the same name, the same table (`cli.py`) |
| 9 | `p433-bench-codes.json:30` "the deploy usage error shows the person's characters raw" | build | acted | dropped; twin `p433-bench-codes.json:29` "the look usage error shows the person's characters raw" (`cli.py`): `run_cli` is one function for both |
| 10 | `p462-start-wait.json:12` "needs_person is always on" | build | acted | dropped; twin `p433-bench-codes.json:18` "the watch step needs the person whatever happened" (`scripts/spark/bench/board_envelope.py`) |
| 11 | `p699-design-net.json:2` "the proxies not set, so a design child could open a URL" | build | acted | dropped; twin `p687-checks-net.json:2` "the proxies not set, so a child could open a URL" (`tests/golden_checks.py`) |
| 12 | `p699-design-net.json:3` "the child's PATH keeps another folder, where a real tsci or node may be" | build | acted | dropped; twin `p687-checks-net.json:3` "… where a real gh may be" (`tests/golden_checks.py`) |
| 13 | `sprint-10-p96-final.json:0` "needs.read accepts a stray field" | build | acted | dropped; twin `sprint-10-p96-3.json:0` "a need may carry a reason, a count or a place" (`scripts/spark/design/needs.py`) |
| 14 | `sprint-10-p96-final.json:5` "needs.read accepts a mark outside the four" | build | acted | dropped; twin `sprint-10-p96-3.json:1` "any word is a mark" (`needs.py`) |
| 15 | `sprint-3-p11.json:4` "an unreadable rules file is silently no rules" | build | acted | dropped; twin `p432-one-refusal.json:12` "P432: a rules file nobody can read is no rules" (`scripts/spark/design/loader.py`); the first by table name is kept, as the brief says, though sprint 3 wrote the row first |
| 16 | a dropped row's name may be cited in `docs/observations` | build | closed | `grep -F` of the 12 names (and the one shared name) over `docs/observations`: no hit |
| 17 | the tables after the drop | build | closed | `tools/mutate.py --anchors tests/mutations/*.json`: "3171 mutation(s) in 271 table(s): every anchor present, once" |
