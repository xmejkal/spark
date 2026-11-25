# P1157, the words for the project timeline, the kept step and the take-back: rows

Card: [P1157 #1693](https://github.com/xmejkal/spark/issues/1693), a docs-only chore under the epic P1152. A council of
three on Fable (the PO assistant, the architect and the tech lead) chose the words on 2026-11-25 about 21:00 CET,
delegated by the PO and his to change. Its answers are on the card. The review was one refuter (Opus).

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | "History", "commit", "revision" and "change" each name something already, so the seam needs other words | the discovery P1148, synthesis C31 and ARCH-12 | acted | `docs/guide/words.md`: project timeline, kept step and take-back, each with what it is not |
| 2 | "Kept step" collides with `--keep`, whose build outputs D8 leaves out | spark-main, on the council's brief | acted | the brief's fact 5 named it beside the option. The table says that no kept step holds a build output |
| 3 | The names page is over its line budget of 279 with the new table | tests.test_docs, the builder's run | acted | both words tables moved to the new page `docs/guide/words.md`, and rule 1 links to it |
| 4 | The renames of "the way back" in `commands/idea.md` and `needs-basis.md` give "take-back" a second meaning: today's `git revert` line runs with no preview and outside the core | the refuter, finding 1 | acted | the two lines and the anchor in `scripts.md` stay as on main. The table says "the way back" names that line until P1152 |
| 5 | The planned names `TakeBackStep` and `take-back-step` use a bare "step", the spine step's op | the refuter, finding 2 | acted | `TakeBackKeptStep`, op `take-back-kept-step` |
| 6 | "Kept" also names the kept document (`parts.py --keep`, `--kept`) | the refuter, finding 3 | acted | named in the kept step's "It is not" cell |
| 7 | The P1160 finding never wrote "the project-history strategy", and its line 194 says "kept files" | the refuter, finding 4 | acted | the phrase is credited to `brief.md` and `items.md`. A line under the table says what the finding's "kept files" means. The finding stays as merged |
| 8 | "Revision" cites `drawer.FIELDS`, a field of any drawer entry | the refuter, finding 5 | acted | cites `replies.py:34` and `physics_check.py:404`, as ARCH-12 does |
| 9 | The move breaks AGENTS.md's "names table is in patterns-and-names.md" | the refuter's own check, finding 6 | rejected | the role table, the names table, stays on that page |
| 10 | The budget can go down to the page's new length, and AGENTS.md can name the new page | the refuter, finding 6 | acted | `tools/check_docs.py` budget 272. AGENTS.md names `docs/guide/words.md` |
| 11 | Two of the words replace the PO's own: "the history" (D5) and the epic title and Slice option "Project history" | the PO assistant seat, the tech lead seat | raised | the card's comment of 2026-11-25. The epic title and the Slice option stay the PO's to rename |
