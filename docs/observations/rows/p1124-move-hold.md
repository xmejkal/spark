# P1124: one step moves a held part to another project: rows

Card: [P1124 #1654](https://github.com/xmejkal/spark/issues/1654). The PO, 2026-11-25: "Yes, file it", when the store
pages' design showed that a move takes two steps in a fixed order. The plan had two council rounds and the PO's approval
on 2026-11-25. Its claims were checked in the code before the build. This file holds the acted, raised and rejected
findings only. 2026-11-25.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | a stop after the first write leaves a move that a second run refuses, because FROM no longer picks the part | plan refuter (Opus), round 1 | acted | FROM's needs.json is written last. A retry after a stop at the pick and after a failed last write both finish, each pinned by a test |
| 2 | the yes as `--yes` or `needs_yes` clashes with the deploy's typed yes, which Claude never gives | plan lenses, round 1 | acted | the PO chose plan first with `--apply` (2026-11-25). The next step carries `needs_person`. patterns-and-names.md says why it differs from `--dry-run` |
| 3 | a run without `--apply` that declares WRITES makes the CLI write page.html | plan refuter and architecture lens, round 1 | acted | `effects_of` is READS without `--apply`. The nothing-written test compares every file, byte for byte, with no file added |
| 4 | a moved board is not named as out of date, because `parts_left_listed` keeps parts only | plan refuter (Opus), round 1 | acted | out of date comes from `flow_codes.MAKES_STALE`: requirements, build and breadboard, for each project with a requirements.json |
| 5 | the move holds no store lock, so another writer can take the freed piece between the writes | plan refuter and architecture lens, round 2 | acted | `store.locked()` covers the plan and the three writes |
| 6 | `PickPlan.is_current` cannot say which of two picks of a need moves | plan architecture lens (Opus), round 2 | acted | one pick is matched by `as_record` and `PickPlan.resolve`. A test moves one pick of two |
| 7 | two different folders with one folder name hold under one name | plan refuter (Opus), round 2 | acted | refused by path first, then by name, each with its own sentence |
| 8 | `--describe` says `dry_run: false` for the move | plan refuter (Opus), round 2 | acted | describe reads `apply` too and adds an `apply` key. Two rows re-anchored with the same mutation |
| 9 | the giving project's page.html is not rewritten, because the CLI's follow-up refreshes one project | plan refuter (Opus), round 1 | raised | P1167 [#1705](https://github.com/xmejkal/spark/issues/1705), the PO's choice of 2026-11-25 |
| 10 | the first push failed on `parts-describe-ok.txt` | the hook | acted | the golden is written again with `SPARK_ACCEPT=parts`, and a golden case for move-hold is added |
| 11 | a move to a need that already picks the part is refused as part of a count, with a wrong fix | PR refuter (Opus) | acted | fixed: `move_already_picked`, with its own sentence, a test and a row. The retry after the last write still finishes |
| 12 | an unreadable file in the plan says "the move was not finished" | PR lens (Sonnet) | acted | fixed: `move_unreadable` says that nothing was written. `move_unwritten` covers only the writes |
| 13 | `data.written` is false after a stop, though the drawer may be written | PR lens (Sonnet) | acted | json.md says `written` is true only for a whole move, and what a `move_unwritten` stop may have written |
| 14 | the help's first clause does not say that the move writes only with `--apply` | PR lens (Sonnet) | acted | fixed |
| 15 | the bad NEED=ID test covers one form only | PR lens (Sonnet) | acted | fixed: subtests over `chime`, `=speaker` and `chime=` |
| 16 | the text view prints the next step as `scripts/move-hold.py`, a script that does not exist (`core/renderers.py:106`) | the builder | raised | P1177 [#1718](https://github.com/xmejkal/spark/issues/1718), with the needs_person "you, in your own terminal" line |
