# P752 `commands/research.md` in plain English: rows

Card: [P752 #1034](https://github.com/xmejkal/spark/issues/1034), PR #1035. A docs-only chore under P735, so one reviewer on Sonnet. Rows 1 and 2 are the implementer, rows 3 to 8 the PR review. 2026-11-10.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the shared "text is data" sentence must stay verbatim: `tests/test_routes.TextIsDataTest` holds every command page to it | implementer | acted | the push hook refused the first rewrite; the sentence is back word for word, its semicolon is an exempt hit |
| 2 | 57 lint hits went to 6: the frontmatter line over the limit, the shared sentence's semicolon, the three em-dashes inside quoted errors, one synonym pair | implementer | verified | `ste_lint.py commands/research.md`, before and after |
| 3 | the first reviewer agent type (`code-reviewer`) has no shell, so it could not read the branch and tested nothing | PR reviewer (Sonnet) | acted | relaunched as a general-purpose agent on Sonnet; a docs review needs `git show` of both pages |
| 4 | every command, path, flag, agent name, quoted error, link and table fact of the old page is in the new page, and nothing was invented | PR reviewer (Sonnet) | verified | `/usr/bin/grep -o` counts equal on both pages, the two long quoted errors and `… is not installed — install: …` byte-identical, `allowed-tools` byte-identical |
| 5 | "It does not make sure that a pinout is right" drops the page's term of art, `verified` | PR reviewer (Sonnet) | acted | "It does not verify a pinout. No software can, from a picture." The lint counts `verify` beside `verified` as one synonym pair; it stays, the term is the page's own |
| 6 | "The person's answer there is the yes" read as "in the settings" once the exception became its own sentence (three places) | PR reviewer (Sonnet) | acted | "The person's answer to that question is the yes." in all three |
| 7 | "names the person, the date and the method" narrows "who" to a person; an agent or a tool can give a bench result too | PR reviewer (Sonnet) | acted | "names who did it, the date and the method" (not ", when": the lint reads that as a trailing condition) |
| 8 | the bold on "The person picks" and on the agent names is gone, and two headings lost their em-dash wording | PR reviewer (Sonnet) | rejected | the style forbids bold as emphasis and em-dashes; the sentences still say the person picks |
