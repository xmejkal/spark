# P504 patterns page: rows

What the P504 plan and its move found. Card: #693.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | "Patterns and names in spark's core" (developing.md 290-567) is one job, so it moves to docs/guide/patterns-and-names.md | plan | verified | sort diff of old against new files shows only the pointer, the H1 and the link lines |
| 2 | developing.md keeps the H2 word for word, so "the names table in docs/guide/developing.md" still leads to the page | plan | acted | H2 kept with one sentence and a link |
| 3 | The process part (findings rows, checking a plan, where the work is planned) stays in developing.md; moving it to scrum/ would change the team's working rules, which the PO changes himself | lead decision | closed | card P506 #700 asks the PO |
| 4 | README.md gets a pointer to the new page | plan | rejected | README is at its budget of 180 lines (tools/check_docs.py BUDGETS) |
| 5 | The moved text has two relative links; `(#the-core-contract)` moves with its target, `agents/scripts.md` is in the same folder | plan | verified | check_docs passes |
| 6 | measure.py reads the page by path | plan | rejected | it only names the page in a comment and in the R6 text; both now name the new page |
| 7 | tests/test_no_magic_strings.py names the page with P260's rule | plan | acted | message names patterns-and-names.md |
| 8 | Council rounds 1 (Opus refuter) and 2 (Sonnet) | plan | closed | the lead ran them in parallel with the plan; their findings are not in this branch's input, so none are listed here |
