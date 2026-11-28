# P1354: the Discovery stage runs through petr-discovery: rows

Card: [P1354 #1943](https://github.com/xmejkal/spark/issues/1943). One refuter on Opus reviewed the PR (no new code path). This file holds the acted, raised and rejected findings only. 2026-11-28.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the line's claims (the copy's name, the original moved, not deleted) are wrong | refuter 1 | rejected | `~/.claude/skills/petr-discovery/SKILL.md:2` reads `name: petr-discovery`; `~/.claude/skills-off/product-discovery` exists |
| 2 | 18 merged briefs still say "invoke product-discovery again" on line 1, and several hold queued questions | refuter 2 | acted | the README row says a brief whose first line says `product-discovery` resumes with petr-discovery |
| 3 | the copy's no-fire eval names product-discovery | refuter 4 | acted | `evals/no-fire/prompt.md:15` in the copy, commit 3f6a214 there (outside this repository) |
| 4 | two memory notes name the product-discovery skill as the one to run | refuter 5 | acted | both notes name petr-discovery (outside this repository) |
| 5 | `scrum/PRODUCT_BACKLOG.md:842` names product-discovery | refuter 3 | rejected | history: it names another skill of 2026-10-05 |
