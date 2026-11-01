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
| 8 | The plan council found nothing | lead | rejected | round 1 (Opus refuter) confirmed that the card and the plan disagreed (the card moved the process part to scrum/): the lead reworded #693 and filed P506 (#700) for the PO; it rejected four other risks (no tool reads the names table from the file, the range breaks no heading, no link breaks, nothing runnable moves). Round 2 (Sonnet): keep the H2 word for word (its anchor), let the pointer name the names table and the role words, fix the lead; all acted |
| 9 | The new page leads back to developing.md | PR reviewer 1 | acted | one line under its intro links developing.md for the tests, the gate, the docs rules and the process |
| 10 | The stub under the old heading only points away | PR reviewer 2 | acted | it now states the one rule (small classes, `main()` only parses and prints) before the pointer |
| 11 | The PO's rules file cites the names table in developing.md | PR refuter 4 | raised | `~/.local/share/spark/rules.md` is outside the repo and the PO's; the stub under the old heading keeps the citation leading to the table; the lead lists it for the PO |
