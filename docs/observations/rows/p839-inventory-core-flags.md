# P839: the inventory reads the flags of every CLI on the core: rows

Card: [P839 #1203](https://github.com/xmejkal/spark/issues/1203), from the review of P804 (row 21). This file holds the
acted, raised and rejected findings only. The review: one lens on Sonnet (points 1 to 5) and the refuter on Opus
(points 6 and 7). Nothing had to be fixed. 2026-11-20.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | a `--help` that runs past its time limit or exits non-zero gives no flags in silence, the same blindness P839 fixes | the lens, points 1 and 5 (no test of that path) | acted | fixed: one stderr line names the script and what happened (`ran past N s`, `exited N`), and the run goes on. The time limit is a parameter, so the test sets 3 s. Two tests, two mutation rows, both caught |
| 2 | the detection misses `from spark.core import cli` with `cli.run_cli(...)` (no script does this today) | the lens, point 2, and the refuter, finding 6 | acted | fixed: `PARSERS` matches the module name `cli`, which covers both forms. A test with that import, and one mutation row, caught. The comment says that `import spark.core.cli` is not matched |
| 3 | the developing page lost "It runs only `--help`", and it does not say what a CLI with several modes misses | the lens, point 4, and the refuter, finding 7 | acted | fixed: the paragraph says both, with `bench.py register` and `record` and `grant.py --check`. The page stays at 379 lines |
| 4 | the PR body says that a flag "fails" the inventory, but the inventory lists it and exits 0 | the refuter, claim (b) | acted | fixed: the PR body says that it lists the flag |
| 5 | three flags named on no page: `check_all.py --boards`, `parts.py --from`, `reach.py --cure-first` | the inventory's run on the real tree, and the lens, point 3 | acted | one sentence each (council D4, 2026-11-20), taken from each flag's own help text, in `docs/guide/agents/scripts.md` (still 308 lines). The inventory now says 13 flags named on no page, down from 16 |
| 6 | the 30 s time limit applies per script, so the worst case is the number of CLIs times 30 s | the lens, point 1 | rejected | dropped because no `--help` came near it (the whole run took 4.7 s) and the hook does not run the inventory |
