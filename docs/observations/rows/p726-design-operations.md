# P726 PR 1: the six goal handlers of `parts.py` run on `run_cli` as design Operations: rows

Card: [P726 #989](https://github.com/xmejkal/spark/issues/989), chore, under #94 (v0.13, one core). Plan
`~/.claude/plans/p726-design-operations.md`. Rows 1 to 16 are the plan reviewer (Sonnet: architecture, names, UX and
AI-UX, callers), 17 to 23 the plan refuter (Opus), 24 to 27 the plan refuter's second round (Fable), 28 to 35 the PR reviewer (Sonnet), 36 on the PR refuter (Opus: Fable hit its limit).
2026-11-11.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `REFUSED_LINE % (sentence, None)` prints `— None`; `_say` adds ` — fix` only when a fix exists (parts.py:292), and parts-need-could-not-run-unknown-matcher.txt has no fix | plan reviewer | acted | `to_result` builds the line with `_say`'s conditional; a unit test for an item with no fix |
| 2 | parts-tally-could-not-run-no-transcript.json also changes: its unchecked item gains `code`; every `needs.match` or `need_requirements` problem gains `"code": null` through `envelope_item` | plan reviewer | acted | named under "Behaviour that does change"; the golden is regenerated; test_needs' four whole-dict asserts take the key |
| 3 | `Argument` has no `metavar`, so `--match` prints `--match MATCH` where today it prints `PROJECT` | plan reviewer | acted | `Argument.metavar` beside `nargs`; a test on `--match --help` |
| 4 | a base in design cannot serve the sourcing PR (design imports sourcing); `START_FIX` and `refused` already sit in audit_records | plan reviewer | acted | `records/answer_operation.py`, `AnswerOperation`, `START_FIX` there; `audit_records.refused` is one line on `Answer.to_result` |
| 5 | the base reads `values["start"]` by name, but only `match` has `--from` | plan reviewer | acted | `MatchNeeds.build_answer` refuses `start < 0` itself |
| 6 | the base catches `PartError`, but no raiser sits in the six's paths | plan reviewer | acted | traced: datasheets.py:358 is `fetch`'s path, caught at :415; needs, need_requirements, offers, run_cost raise none; the catch goes |
| 7 | the keyword `needs` in `ListNeeds.answer(needs)` shadows the module `spark.design.needs` | plan reviewer | acted | the selector dests say the role: `project`, `words`, `key` |
| 8 | `GoalOperation` is not verb then object, "goal" is not a glossary word, and `answer()` returning an `Answer` is two meanings | plan reviewer, plan refuter | acted | `AnswerOperation`, the step `build_answer` |
| 9 | 46 rows aim at goal_handlers.py, not 44; 41 move, 5 stay (the pick helpers) | plan reviewer, plan refuter | acted | the plan's counts; the scratch script prints what it moved |
| 10 | how-it-works.md:153, sourcing.md:26 and :30, map.md:123 and the baseline's `R1:scripts/parts.py:main` (23) name or bound what moves | plan reviewer | acted | the plan's docs list; `main` shrinks |
| 11 | `COMMON_ARGUMENTS["project"]` defaults to `Path(".")`, but `--need` and `--offer` pass None today | plan reviewer | acted | `--project` (Path, default None) in the table, as `AuditRecords` |
| 12 | the bad-argument fix sentence `parts.py --help lists the arguments` names a page that lists the old flat flags only | plan reviewer | rejected | `parts.py --match --help` lists the Operation's arguments, as audit's does since P707; the same sentence serves every CLI on the core |
| 13 | `_op_needs_drop` converts an `OperationResult` into an `Answer` by hand while the plan adds the other direction | plan reviewer | acted | `Answer.from_result`, `_op_needs_drop` calls it |
| 14 | `outcomes.dumps` and `nargs` are core changes inside a move PR | plan reviewer | verified | small and tested; named under "Behaviour that does change" and in the PR body |
| 15 | the plan has two versions of the `ON_THE_CORE` filter | plan reviewer | acted | the row-based filter only |
| 16 | `--from` with `--need`, `--offer`, `--tally` or `--requirements` exits 2 after; today it is accepted and ignored | plan reviewer | acted | named under "Behaviour that does change" |
| 17 | the dispatch rule picks what argparse picks for every exact flag, `=` form and unique prefix (113 forms run); it disagrees on three argv that are wrong today (`--need w --mat m`, `--match P --f 3`, `--show s --need x`) | plan refuter | acted | named under "Behaviour that does change" |
| 18 | two goldens have no fix and would print `— None`: parts-need-could-not-run-unknown-matcher and parts-offer-problems-no-such-offer | plan refuter | acted | row 1's conditional; both goldens compare bytes |
| 19 | the plan's golden list misses parts-offer-ok, parts-requirements-ok and parts-tally-could-not-run-no-transcript.json; test_needs.py:2238, :2275, :2320, :2325 compare whole item dicts | plan refuter | acted | ten goldens named as bytes, one regenerated, the four asserts updated |
| 20 | with `--json`, `to_result` puts the refusal lines in `diagnostics`, so they print on stderr, which `_say` never did | plan refuter | acted | named as a change; `--audit` does the same since P707 |
| 21 | `SparkError` and `PartError` subclass `CodedMessageError`, so the catch order matters; `store.locked()` is re-entrant and the core takes none | plan refuter | verified | the base re-raises `SparkError` first; the lock as parts.main took it |
| 22 | nine mutation finds stop matching after the move: eight hold `args.dry_run`, p97-cost 34 and p97-requirements 7 and 16 span two lines | plan refuter | acted | rewritten by hand before the script runs; proved with `--anchors` |
| 23 | `board_envelope.dumps` has no caller | plan refuter | acted | pruned in this PR |
| 24 | records may import the core and nothing forbids a records module to subclass `Operation`; `TheRecordsAreaTest.MODULES` must gain `answer_operation` | plan refuter 2 | verified | test_architecture.py:493 to :545, :528 |
| 25 | the plan says the base resolves `project` when not None in one place and only a `Path` in another; `ListNeeds`' text would change on a `str` | plan refuter 2 | acted | one rule: resolved only when it is a `Path` |
| 26 | `from_result(to_result(a)) == a` fails on `lines`, which `text_lines` grows; the hand conversion also drops `next`, `truncated` and `assumptions` | plan refuter 2 | acted | the test compares one field at a time; `from_result` carries the three fields (DropNeed returns none) |
| 27 | four parts.py citations are stale (`_text_of` :295 to :320, `_say` :323 to :345, the refusal line :338) | plan refuter 2 | acted | the plan's numbers |
| 28 | with `--json`, a refusal with no lines also prints its sentence on stderr, which `_say` never did | PR reviewer | acted | kept, as `--audit` since P707 (row 20); json.md says it on the line it already changed |
| 29 | `_say`'s docstring names `_text_of`, which is gone | PR reviewer | acted | it names `Answer.text_lines` |
| 30 | the help of `--matcher`, `--project`, `--from` and `--dry-run` is written twice, in parts.py's OPTIONS and in the Operations, so `--describe` can drift | PR reviewer | acted | OPTIONS reads each from the Operation's module (`find_offers.MATCHER_HELP`, `PROJECT_HELP`, `match_needs.START_HELP`, `write_requirements.DRY_RUN_HELP`): one text |
| 31 | underscore names cross modules: `_cannot`, `_problem`, `_names_your_entries`, `_what_a_pick_wrote` | PR reviewer | raised | the convention predates P726 (parts.py imports them since W6-S3a); a rename of the record_kind item builders and the pick helpers is a card for the end of #94, not this move |
| 32 | `START_FIX` sits in records but only `match` and `audit` read it; `NO_NEEDS_SENTENCE` and `NO_NEEDS_LINE` say the same in two modules; `--needs` on an empty project exits 0 where `--match` is could-not-run | PR reviewer | verified | old behaviour, moved as it was; the sourcing PR's `--list` reads `START_FIX` too, so records is its home |
| 33 | `FILE_UNREADABLE` also names a failed write of `--requirements` | PR reviewer | acted | the code is `file_refused`, "read or written"; `file_unusable` is breadboard's, and the codes test refuses a word in two tables |
| 34 | the six exit 2 for an option they do not take; prefix routing and the ambiguity message work | PR reviewer | verified | named in scripts.md and the plan |
| 35 | json.md says the items of the seven carry `code` and an `unchecked` item has no `subject` | PR reviewer | verified | the envelope seen matches |
