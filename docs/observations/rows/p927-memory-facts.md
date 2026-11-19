# P927: the memory facts move into the docs, and AGENTS.md gets a structure block with a test: rows

Card: [P927 #1312](https://github.com/xmejkal/spark/issues/1312), a chore. The plan is a comment on the card. This
file holds the acted, raised and rejected findings only (rules.md). The first rows are from the builder's check of
the plan's claims in the code. The review's rows follow them: one lens on Sonnet (documents and public safety, no
must-fix finding) and the refuter on Opus (17 verdicts). 2026-11-19.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the plan said that the runtime at v1.29.0 "has only `IRQ_RISING` and `IRQ_FALLING`", and `machine_pin.c` there also holds `WAKE_LOW` and `WAKE_HIGH` | the builder, from the file at the tag | acted | fixed: `boards/README.md` says "the only `IRQ_` names of `Pin`" |
| 2 | `docs/guide/patterns-and-names.md` said "the four Operations in `scripts/spark/bench/`", and the map lists nine | the builder, from `docs/guide/map.md` | acted | fixed: the paragraph is one line that points to the map. It pays for the two lines of the names fact |
| 3 | a sentence in the W10 bullet of `scrum/TEAM.md` lost words on 2026-10-12 ("and an ask rule for Claude asked him") | the builder, from the commit 0499a9d5 | acted | fixed: "Claude asked him on 2026-10-12 whether to add an ask rule for it" |
| 4 | the W10 bullet says "Claude asks him before each run", and the PO allowed a free-plan run on 2026-10-31 | the builder, from the memory note | raised | fixed: the bullet says "until 2026-10-31 Claude asked him before each run" and then the free plan's rule with its date (row 12). The PO reads it before his merge |
| 5 | the simple-english hook counts 79 to 174 hits in the old text of four pages that this PR touches | the hook | rejected | dropped because the card orders no style rewrite of the working agreements, and the new lines hold the rules |
| 6 | the W10 bullet did not say which run needs no ask, and the ask rule in the PO's settings still fires | the lens | acted | fixed: "a run through `scripts/run_scenario.py`", and one sentence on the settings rule and on the pages for a user |
| 7 | the new W6 paragraph used "touch" with no meaning given | the lens | acted | fixed: "A touch is a look, a grant, a reach, a live try or a deploy" |
| 8 | "the maintainer" is a second word for the PO, and "can be an old one" did not say which hash | the lens | acted | fixed: "the PO", and "a spark hash in a text from before 2026-10-03" |
| 9 | the W3 clause made one line about 215 characters long | the lens | acted | fixed: the line is wrapped |
| 10 | the cut on the names page removed the link #264 and the sentence on what the reach cures | the lens | rejected | dropped because the script's docstring and its `--help` hold the cure, and the page is at its budget |
| 11 | `agent_rows` had no test of its own, and 5 of 6 planted faults passed | the refuter | acted | fixed: two tests on a hand-written text and a third mutation row. Six faults planted in memory each fail a test, and the control passes |
| 12 | the W10 bullet's "Claude asks him before each run" had no date, and row 4 said that both sentences carry one | the refuter | acted | fixed: "until 2026-10-31 Claude asked him before each run" |
| 13 | a table row whose link has another form (an anchor, an absolute path) left the model check with no failure | the refuter | acted | fixed: the pattern takes any link to an agent's file, and the test pins the list of linked agents |
| 14 | a row with no model word equals a file with no `model:` line (None equals None) | the refuter | acted | fixed: the test fails on a file that names no model |
| 15 | the W6 paragraph lost the wait for the other session's "free", and "each touch still asks the PO" is false for a kept board | the refuter | acted | fixed: "waits for its \"free\", because silence is not a yes", and "the PO's yes to the board question, or his grant" |
| 16 | the block said "thin CLIs: `main()` only parses arguments and prints" and "an MCP tool runs it", and two scripts hold logic and the CLI is the only frontend | the refuter | acted | fixed: "the others get there as each area moves onto the core (#94)", and "the CLI is the only frontend today" |
| 17 | an agent's file with no row in the table (`mutation-tester`) is not compared, and the block's "once" and its order are not pinned | the refuter | rejected | dropped because the table's last row gives such an agent "the model its file names", and the order is prose that a person reads |
