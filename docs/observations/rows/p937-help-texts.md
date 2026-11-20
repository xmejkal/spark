# P937 item 2: five --help texts in their place, and one sentence per Operation: rows

Card: [P937 #1333](https://github.com/xmejkal/spark/issues/1333). The PO's yes, 2026-11-20: "Yes, fix all five". A text
move with no new behaviour, so no plan. This file holds the acted, raised and rejected findings only. 2026-11-20.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the brief says to change each text in the core, and boards --list's --json sentence is the frontend's own text | build | acted | `Operation.details` holds no frontend text (its docstring: "its `--json`, a bad flag, its exit codes" are not in it), so the sentence moved out of `ListBoards.details` into boards.py's `LIST_EPILOG`, where deploy.py, live.py and look.py keep theirs |
| 2 | live's board-doctor paragraph ends with "--json carries it as doctor.", a --json sentence that now stands in `RunLiveCode.details` | build | rejected | the PO's yes was to move the paragraph, not to reword it, and reach's details hold --json sentences too (`ReachBoard`: "With --json an open question prints one line") |
| 3 | flow.py and grant.py keep one shared epilog for their two Operations | build | rejected | the PO's yes covers one sentence per Operation; each epilog says both verbs or modes by name (`flow.py show`, `flow.py page`, `grant.py --minutes`, `grant.py --check`), so each --help still names the other |
