# P738 the fact need tree, thin: rows

Card: [P738 #1014](https://github.com/xmejkal/spark/issues/1014). Plan: `~/.claude/plans/distributed-doodling-kernighan.md`.
Rows 1 to 11 are the plan council's architecture lens (Sonnet), 12 to 20 its refuter (Fable), 21 to 23 round 2 (the
refuter on Fable), 24 to 27 the implementer, 28 to 31 the PR review (a reviewer on Sonnet, the refuter on Fable). 2026-11-10.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the shape is right: a frozen Value, `from_file`, the join in the shared handler | plan architecture lens | verified | kept; the handler builds the text line and the entry from one `read_by` |
| 2 | `severity`, `condition` and `why` have no reader; behaviour-like data | plan architecture lens | acted | cut from the file and the Value; the reason is in the `//` key |
| 3 | the prefix half of `of_fact` has no caller: `list_unverified_facts` never writes a block prefix | plan architecture lens | acted | exact match |
| 4 | the need belongs in the handler, not in provenance's pure row | plan architecture lens | verified | kept |
| 5 | three of four rows are `will read`, dead data in this PR | plan architecture lens | rejected | kept because the design asks for them (design.md:217); row 21 says when they surface |
| 6 | `will read: P734` packs an enum and a card into one string; a regex would parse English | plan architecture lens | acted | `status` in {reads, will read} and a `card` field |
| 7 | `key` clashes with the design's `Question.key` | plan architecture lens | acted | `fact_name` |
| 8 | `of_kind` and `of_fact` do not start with a verb | plan architecture lens | rejected | `of_kind` is the design's name; `of_fact` follows it; the table allows `find_` on a Value, a later rename if the design's name changes |
| 9 | a module-level load at import; `drawing.py:111` uses a classmethod with a path default | plan architecture lens | acted | `from_file(path=FILE)`, no module-level load |
| 10 | a bare substring check is weak | plan architecture lens | acted | the quoted literal `"<fact_name>"` |
| 11 | `of_kind` has no production caller until P737 step 3 | plan architecture lens | rejected | one line, the design names it |
| 12 | `body_mm` is read in `board_components.py:21,27`, not in `board_emitter.py` as the design says | plan refuter | acted | the consumer is `spark.design.board_components`; the design's name was a slip |
| 13 | "one reader per fact path" is false: `need_requirements.py:71,255` reads `body_mm` too | plan refuter | acted | a second row; the envelope carries a `read_by` list |
| 14 | `RecordShapeSource` reads a board's `physical.header` today; `thickness_mm` and `mounting_holes` are in no file | plan refuter | acted | the `//` key says so; the rows stay `will read` per (module, consumer) |
| 15 | the x-joy fixture asserts the whole entry, `kind: test` | plan refuter | verified | the join ignores kind |
| 16 | the vl6180x golden does not change; it is the only `--unverified` golden | plan refuter | verified | unchanged after the run |
| 17 | `parents[3]` and the frozen Value pattern hold | plan refuter | verified | `fab.py:30`, `board_pads.py:12` |
| 18 | P260's test scans comparisons only; constants are right anyway | plan refuter | verified | `READS`, `WILL_READ` |
| 19 | `tools/map.py` lists every module and `test_map` fails on a stale page | plan refuter | acted | `map.py --write` in the PR |
| 20 | `import_module` on a class path fails | plan refuter | acted | `rpartition` split in the test |
| 21 | a `physical` block's `write` is `physical`, so the `will read` rows cannot surface in `--unverified` until P734 widens the join or writes per-key proofs | round 2 refuter | raised | a note for P734 (issue comment) |
| 22 | `outcomes.envelope` passes `None` and lists through; `parts.py` prints only four keys | round 2 refuter | verified | text unchanged where no row |
| 23 | `fab.py` lives in `design/`, not `records/` | round 2 refuter | acted | the plan's citation |
| 24 | the card's proof `--unverified sen0526-i2s-mic` gains no `read_by`: that record's `body_mm` is verified and it has no `physical` | implementer | raised | the proof is the x-joy fixture; a comment on the card |
| 25 | no library record has `kind: module`; how a record's kind maps to `module` is P737 step 4's question | implementer | raised | a note for step 4 |
| 26 | the architecture lens read the design's `card` as part of `status`; the file now holds both | implementer | closed | rows 6 and 13 |
| 27 | validators that require `body_mm` (`CHAIN_FACTS`, `part_records`, `matching`) are not consumers | implementer | raised | `CHAIN_FACTS` moves later (design.md:224) |
| 28 | mutation row 2 (match on the leaf name) survives: no test's write key ends in a listed leaf | PR reviewer, PR refuter | acted | `of_fact("header") == []` in test_fact_needs |
| 29 | the `(will read, P734)` text line is unreachable today and had no test | PR reviewer, PR refuter | acted | a test with a patched `FactNeeds` proves the line; the branch stays for P734 |
| 30 | `of_fact` ignores the record's kind: a sensor record gets the `module` rows | PR refuter | raised | the file's `//` says so; a join on kind when a second kind has rows (P737 step 4 maps kinds) |
| 31 | the consumer-missing test, the two `read by` lines, the golden, the map and the data loaders all hold | PR refuter | verified | scratch runs, rows 1, 2, 4, 6, 7 of its report |
