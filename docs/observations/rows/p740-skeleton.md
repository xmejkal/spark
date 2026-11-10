# P740 `--skeleton` writes no `sourcing` and names a held record: rows

Card: [P740 #1016](https://github.com/xmejkal/spark/issues/1016). Plan: `~/.claude/plans/distributed-doodling-kernighan.md`.
Rows 1 to 8 are the plan check (the refuter on Fable, the XS rule), row 9 the implementer, rows 10 to 12 the PR review (a reviewer on Sonnet, the refuter on Fable). 2026-11-10.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `store.records(..., drafts=True)` returns the project layer first, and `record_kind.LIBRARY` is parts' library | plan refuter | rejected as a doubt | `store.py:129` walks `reversed(layers)`, nearest wins; a scratch run showed all four layers |
| 2 | the `next` step `["--promote", id]` fails: `--promote` without `--project` answers `unchecked`, exit 2 | plan refuter | acted | argv is `["--promote", id] + _with_project(project)`, as `board_envelope.py:47` does |
| 3 | `promote()` handles shelf and catalog; a library id raises `PROMOTION_WOULD_OVERWRITE` | plan refuter | rejected as a doubt | `part_facts.py:150-155`; the library case gets no `next` |
| 4 | dropping `sourcing` breaks a reader or leaves a doc stale | plan refuter | rejected as a doubt | `record_kind.py:176` types it optional; the only readers are the P735 diaries, which are history |
| 5 | the mutation row "walk reads `drafts=False`" is caught by no planned test | plan refuter | acted | a catalog subtest plants `catalog/x-catalog.json` |
| 6 | `step()` + `add_env(..., store.read_given_env())` matches `_op_unverified` | plan refuter | rejected as a doubt | `part_handlers.py:107`, `outcomes.py:113,123`, `store.py:66` |
| 7 | the golden store holds no shelf; the library Case needs no `written=`; `ROOT` is scrubbed to `<repo>` | plan refuter | rejected as a doubt | `test_golden_records.py:130-131`, `golden_bench.py:210` |
| 8 | `held` is a participle, not the noun of a path; neighbours say `path` | plan refuter | acted | `layer, path = held` |
| 9 | the simple-english hook counts 57 older violations in `commands/research.md`; this card touched four lines | implementer | raised | a docs pass on the command pages, out of this card's scope |
| 10 | the project layer is never asserted: its fix text, sentence and empty `next` have no test | PR reviewer (Sonnet) | acted | a `("project", "x-project")` case joins the loop |
| 11 | "a skeleton here would hide it" is untrue for the project layer: it would overwrite | PR refuter (Fable) | acted | "overwrite" for the project layer, "hide" for the others; research.md says both |
| 12 | refusal, `--promote` next step, exit codes, `next: []`, Linux path and the four mutation rows all hold | PR refuter (Fable) | verified | six scratch runs and the promote run, rows 1 to 7 of its report |
