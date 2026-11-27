# P1256 PR 2: the rule copyable and the one line builder: rows

Card: [P1256 #1815](https://github.com/xmejkal/spark/issues/1815). The plan's delegated yes Y2 (2026-11-27) splits the
card in two PRs. PR 1 quotes the placeholders in the docs. This PR adds the rule `copyable` and makes `step_command` the
one builder of the follow-up's and the build's `next:` lines. The review was the architecture lens (Opus) and the refuter
(Opus), read-only, with no test run. This file holds the acted, raised and rejected findings. 2026-11-27.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `next_lines` and `FollowUp.line` build the same `PastedLine(STEP_LINE % ...)` twice | architecture lens | acted | one core function `follow_up.step_line(step, after="")`, which both call |
| 2 | the hook `mark` takes the word that names the status glyph (`✓`, `MARK_OK`) | architecture lens | acted | the hook is `after_command(step)` in the code, the docs and row 12 |
| 3 | the parameter `line` of `copyable` reads as the whole `next:` line, which R3-2 says is never asked | architecture lens | acted | `copyable(command, home)`, and its docstring says to ask it of a command only |
| 4 | the docs call `copyable` "the rule a printed command passes" as if the product asked it | architecture lens | acted | shell_line.py's docstring and patterns-and-names.md say that tests ask it today and P1286's page is its first product caller |
| 5 | the step's why is unmasked now in the text, but masked in `--json` | architecture lens, refuter 4 | acted | follow_up.py's docstring says so (spark's whys are fixed sentences and names, with no path), and flow.md and json.md name the `next:` lines among the lines that keep their paths |
| 6 | build.md says the line holds the store's path, but only when SPARK_HOME is set, and flow.md says "unmasked" though tokens are masked | architecture lens | acted | both sentences say it as the code does |
| 7 | a `~` right after `=` passes in all three forms (`--project=~/lamp`, `='~/lamp'`, `="~/lamp"`), and bash and zsh print it as it is | refuter 1, architecture lens (smaller point) | acted | `unexpanded_tilde` refuses it, the near miss moved to the refusals, row 17 |
| 8 | `shlex.quote("=ls")` leaves `=ls` bare, and zsh runs it as `/bin/ls` | refuter 2 | acted | `copyable` refuses an unquoted `=` that starts a word (row 18), and `renderers.shell_word` quotes such a word in `step_command` (row 20) |
| 9 | an unclosed quote or a final backslash passes | refuter 3 | acted | `read_states` gives the end state, and `copyable` refuses an open end (row 19). The docstring lists what it does not check: `#`, `*`, `(`, and a space in a path outside the home folder, which shlex quotes or spark never writes |
| 10 | no row or test pins `printable(why)` | refuter 5 | acted | test_core's `test_a_why_with_a_line_end_stays_on_its_one_line` and row 16 |
| 11 | the old line took SPARK_HOME from the environment, so a later step built without env would lose the store | refuter 6 (nit) | dropped because | every step builder carries `store.read_given_env()`, and P1286 #1852 changes the store's form in the line |
| 12 | the follow-up's and the build's lines changed bytes | refuter claim 2 | rejected | a look step with a spaced store and project gives the same bytes before and after |
| 13 | the build's lines changed | refuter claim 3 | rejected | `render` always ends with one newline; a newline in a why now prints `?` instead of a second line |
| 14 | a row escapes its test, or a reader still needs `next_text` or a plain str | refuter claims 4 and 5 | rejected | each named test catches its row, p1035 row 18, p679 and the p804 row too; `next_text` stays only in old discovery and observation text |
