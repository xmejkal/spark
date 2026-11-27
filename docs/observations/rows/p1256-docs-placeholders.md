# P1256 PR 1: unquoted placeholders in docs command lines: rows

Card: [P1256 #1815](https://github.com/xmejkal/spark/issues/1815). The plan's delegated yes Y2 (2026-11-27) splits the
card in two PRs: this one, docs only, quotes each placeholder; the second adds the code. This file holds the raised,
verified and acted findings. 2026-11-27.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | a command line in a code block with an unquoted `<word>` is read by the shell as a redirection when pasted, and `$ deploy.py --project <project> --token xxxx-ae44` emptied a file named `--token` to 0 bytes | plan refuter (Opus), tested in zsh | verified | `tests/test_doc_command_lines.py` failed on 50 hits in 13 files before the fix, none after |
| 2 | the rough scan of about 44 hits in 12 files missed some | the build | acted | the test finds 50 in 13 files (49 by its first rule, one more after the rule read a placeholder with an apostrophe or a comma), among them `docs/guide/agents/breadboard-codes.md`, `scripts.md`, `replies.md` and `commands/setup.md` |
| 3 | `docs/guide/journey/bench.md` (5 lines) | plan refuter | acted | each `<project>` and `<spark>` is quoted: `'<project>'`, `'<spark>'/scripts/...` |
| 4 | `commands/*.md` (build, drawer, idea, identify, init, page, research, setup; 30 lines) | the build | acted | each placeholder is in single quotes. Each line keeps its meaning and its length in lines |
| 5 | `docs/guide/developing.md` (12 lines) and the three `docs/guide/agents/` pages (3 lines) | the build | acted | quoted. A placeholder that holds an apostrophe (`<the wave's files>`) is in double quotes |
| 6 | a pasted `'<project>'` runs as the literal word, so the person still has to replace it | the build | raised | the quote makes the paste safe, not complete. PR 2's `copyable` rule and real example paths on person-facing pages are its answer (Y2) |
| 7 | the test reads command lines only: a line that starts with `$ `, `python3`, `SPARK_HOME=`, `${CLAUDE_PLUGIN_ROOT}`, `<spark>/scripts/` or a path to a `*.py` script | the build | raised | a command that starts otherwise (a bare `cmd` in a block) is not read. The rule is in the test's `COMMAND_START` |
