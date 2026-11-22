# P964: `parts.py --fetch` refuses a record of spark's library: rows

Card: [P964 #1382](https://github.com/xmejkal/spark/issues/1382). This file holds the acted, raised and rejected
findings of the plan check (the refuter on Opus). 2026-11-22.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the shared refusal gives `find-documents` a code and a fix, so its golden changes from `"code":null` | plan check 1 | acted | `tests/golden-records/parts-find-documents-problems-library.json` written again with `SPARK_ACCEPT=parts`, the diff read: `code` is `library_record`, `fix` is the code's fix, and the stderr line has the fix after a dash |
| 2 | `parts-function-set-problems-library.txt` prints only the sentence and stays | plan check 1 | rejected | its stderr line now carries the fix too (the CLI adds a problem's fix to the line), so the golden was written again; the sentence is unchanged. `parts-describe-ok.txt` changed for the new `--fetch` help sentence |
| 3 | `research.py` refuses a library record with `bad_argument` (`BAD_ARGUMENT_IN_LIBRARY`), `parts.py` answers problems with exit 1, so the new code is still needed | plan check 2 | acted | `json.md` says `research.py` says `bad_argument` for the same fact (card P982, #1424) |
| 4 | `commands/idea.md` already tells Claude to say that a record is in the library | plan check 3 | acted | checked: the text still fits a `library_record` problem with exit 1; no change |
| 5 | a shelf copy goes through `record_kind.record_home`, not `record_path`, so `--fetch` of a project's shelf copy writes the shelf copy and not the record it follows | the plan | raised | card P983 #1426: `fetch_path` uses the home `record_home` finds, as `--fetch` always did |
| 6 | the architecture tests cap `mock.patch` in test files (T2) and want a constant template for a `PartError` (V1) | the build | acted | the tests set `record_kind.LIBRARY` and `store.fetch` in one helper that restores them; the `PartError` template is a literal |
| 7 | the move of the lookup and the refusal left three old rows refused (p715-records-net, p97-council, p97-fetcher) | `--anchors` | acted | re-anchored to `datasheets.fetch_path`, `record_home.library_problem` and the dry run's `wanted` line, each run by hand and caught; refused is 20 again |
| 8 | `--fetch` answered `library_record` with `fix: null`: `fetch_path` made its own copy of the sentence | review, lens and refuter | acted | `FetchDocuments.answer_refusal` returns `record_home.library_problem`, one sentence and one fix; the CLI test asserts `fix` for `--fetch` and `--dry-run` |
| 9 | the fix of `library_record` said "run again" without the command | review | acted | "copy the record into the project's parts/ folder (a board into boards/), then run the same command again with --project <that project's folder>"; the meaning drops "never by parts.py"; goldens written again, diffs read |
| 10 | the alias `record_homes` in `datasheets.py` | review nit | acted | renamed `home_rules` |
