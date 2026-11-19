# P927: the memory facts move into the docs, and AGENTS.md gets a structure block with a test: rows

Card: [P927 #1312](https://github.com/xmejkal/spark/issues/1312), a chore. The plan is a comment on the card. This
file holds the acted, raised and rejected findings only (rules.md). The first rows are from the builder's check of
the plan's claims in the code. The review's rows follow them. 2026-11-19.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the plan said that the runtime at v1.29.0 "has only `IRQ_RISING` and `IRQ_FALLING`", and `machine_pin.c` there also holds `WAKE_LOW` and `WAKE_HIGH` | the builder, from the file at the tag | acted | fixed: `boards/README.md` says "the only `IRQ_` names of `Pin`" |
| 2 | `docs/guide/patterns-and-names.md` said "the four Operations in `scripts/spark/bench/`", and the map lists nine | the builder, from `docs/guide/map.md` | acted | fixed: the paragraph is one line that points to the map. It pays for the two lines of the names fact |
| 3 | a sentence in the W10 bullet of `scrum/TEAM.md` lost words on 2026-10-12 ("and an ask rule for Claude asked him") | the builder, from the commit 0499a9d5 | acted | fixed: "Claude asked him on 2026-10-12 whether to add an ask rule for it" |
| 4 | the W10 bullet says "Claude asks him before each run", and the PO allowed a free-plan run on 2026-10-31 | the builder, from the memory note | raised | fixed: the bullet gives both with their dates. The PO reads it before his merge |
| 5 | the simple-english hook counts 79 to 174 hits in the old text of four pages that this PR touches | the hook | rejected | dropped because the card orders no style rewrite of the working agreements, and the new lines hold the rules |
