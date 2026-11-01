# P501 journey split: rows

What the P501 plan, its two council rounds and the build found, and what the plan claimed wrongly. Card: #690.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The page map at origin/main (a2b75a9e): index 1-40, how the runs were made 41-68, drawer 69-117, idea 118-203, recorded run 204-568, owed facts 569-729, research 730-768, build 769-977, checks 978-1153, firmware 1154-1215, simulate 1216-1263, bench 1264-1469, from draft to order 1470-1582 | planner | verified | the move proof rebuilds lines 41-1582 from the 12 pages: identical, 1542 lines |
| 2 | A pure move first and the dedupe second, so the move needs no line-by-line review | lead | acted | commit 1 is the move, commit 2 the dedupe and the card's three text points |
| 3 | Budgets at each new page's real size, the index at about 62 | lead | acted | the index has 45 lines. `test_the_journey_guide_keeps_the_budget_of_an_index` caps its budget at 62 |
| 4 | The recorded run (365 lines) is split further only if the dedupe cannot bring it near 200 | lead | raised | it holds no "Today, in full" paragraph, so the dedupe did not touch it: 364 lines, under the default 400. A split is a later card if the PO wants one |
| 5 | File names equal the lowercase step names, the index lists the eight steps in README order, and the shared pages under their own heading | round 1 and 2 | acted | `docs/guide/journey/<step>.md`. The index heading "Pages the steps share" |
| 6 | "How these runs were made" is a bold paragraph, so its page needs a `#` heading. The three example projects go where they fit | round 1 | acted | the page starts `# How these runs were made` and keeps the three projects. The proof undoes only that one line |
| 7 | 34 cross-page anchors need a rewrite | round 1 | rejected | the old page held 25 anchor-only links. 24 cross pages and one stays on its page. 41 relative links leave the folder and got `../` |
| 8 | commands/build.md:311 names the section in prose, and check_docs does not read commands/ | refuter | acted | it names `docs/guide/journey/bench.md`. The links at commands/build.md:373 and commands/deploy.md:114 were checked with `check_docs.broken_links`: no problem |
| 9 | The PR carries a script result that proves the moved text unchanged apart from links | round 2 | acted | the proof script resolves each link to its file and heading on both sides |
| 10 | The proof's first version counted any journey page as the old page, so a link to the wrong page passed | build | acted | a page now counts as the old page only when it holds the linked heading. Three planted defects (a wrong page, a wrong anchor, a changed word) each made a diff |
| 11 | The `# Breadboard:` heading near old line 401 sits inside a fence and is not a cut point | refuter | verified | it is in a ```text block on recorded-run.md, and check_docs strips fences before it reads headings |
| 12 | No check compares the recorded outputs' dates, and every cut falls on a heading outside a fence | refuter | verified | check_docs passes. Each `<!-- output -->` note stays above its block |
| 13 | No test pinned a real budget, so a raised index budget would escape the mutation run | build | acted | the new test in tests/test_docs.py. tests/mutations/p501-journey-split.json row 3 |
| 14 | The dedupe moved the board-match facts (P387, P389, P397) from bench to idea, and idea grew past its commit-1 budget of 85 | build | acted | the Today paragraph names the board's parts in one sentence and leaves the need names to `/spark:idea`'s page. idea.md has 85 lines |
| 15 | The Commands list adds 3 lines to the README, which is at its budget of 181. A reflow to win them back split link text across lines | build | acted | the reflow was undone. Three shorter wordings: the record bullet, init and drawer in one bullet, the More line for the journey guide. The README has 181 lines |
| 16 | The dated notes in docs/archive, docs/discovery and docs/observations still cite `journey.md` lines | build | rejected | they are records of their day and are not rewritten |
| 17 | The mutation run: 3 planted, 3 caught. `mutate.py --anchors` over every table: 119 refused, the count before this PR | build | closed | the run of 2026-11-01 |
