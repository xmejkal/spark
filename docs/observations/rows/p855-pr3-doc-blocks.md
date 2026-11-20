# P855 PR 3: the scripts page's first generated block, from live's Operation: rows

Card: [P855 #1220](https://github.com/xmejkal/spark/issues/1220). This file holds the acted, raised and rejected
findings only. The plan check: one lens on Sonnet (2 musts, 3 shoulds). 2026-11-20.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | scripts.md holds no `--cure-first` sentence, so the plan's second replaced passage goes, and only live's first sentence is replaced by the block | the plan check | acted, its premise rejected | the sentence is at scripts.md:138 on origin/main 866efc23 (`/usr/bin/grep -n cure-first`). It stays anyway, because the page has no reach block to say it: only live's first sentence goes |
| 2 | live's `--code` Argument is at run_live_code.py:72, not :106 | the plan check | rejected | it is at :106 on 866efc23 (`/usr/bin/grep -n '"--code"'`). A row's anchor is its `find` text, and `tools/mutate.py --anchors` finds both, once |
| 3 | the link to the moved table goes into the sentence that announced it, as json.md:191 links firmware-codes.md, with no new line and no row in agents.md | the plan check | acted | fixed: scripts.md's breadboard bullet links `breadboard-codes.md` on that line |
| 4 | live's paragraph must not read as part of the read-only list above it | the plan check | acted | fixed: it opens "**`live.py` runs code on the board:** it is in neither list, and its flags follow" |
| 5 | the PR body and the card say why one block fits the budget now, and how the next one comes | the plan check | acted | fixed: the PR body and a comment on #1220 |
| 6 | the done line says scripts.md holds generated "blocks", and it holds one: the next needs a cut of about 12 lines | build | raised | a comment on #1220, for the PO's eye: restate the done line or keep the card for the next block |
| 7 | OperationHelpTable shows an `nargs` "*" value as one word too (check_all's `--boards`, which `--help` shows as `[BOARDS ...]`); its docstring names only "+" | build | raised | a comment on #1220: the PR that gives check_all a block handles both |
