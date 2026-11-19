# P855 PR 2: seven core CLIs take their help from their Operations: rows

Card: [P855 #1220](https://github.com/xmejkal/spark/issues/1220), PR [#1327](https://github.com/xmejkal/spark/pull/1327).
This file holds the acted, raised and rejected findings only. The review: the refuter on Opus (5 claims: 4 hold, 1
refuted). Every `--help` is byte-equal under Python 3.10 and 3.9. 2026-11-20.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `tools/inventory.py` reads a script's first docstring line as its purpose, and deploy.py, live.py, reach.py and research.py now say "The deploy's CLI (P192): its --help sentence and paragraphs are DeployImage's" | the refuter | acted | fixed: each first line says in a few plain words what the script is for, and the pointer to its Operation follows. The inventory's purpose column, compared with origin/main's, is shorter and plainer |
| 2 | the PR's title says nine core CLIs, and seven moved | the refuter | acted | fixed: the title says seven |
| 3 | the inventory's importer lists of download_mode, ready_probe, image_evidence and board_grant no longer name deploy.py and live.py | the refuter | acted | fixed: the PR body says so. The imports moved into deploy_image.py and run_live_code.py with the texts that use them |
| 4 | `BuildBoard.summary` copies the first line of check_spine.py's docstring | the refuter | acted | fixed: the docstring's first line is "check_spine.py: the CLI of the build.", so the sentence lives once, in the Operation |
| 5 | three help texts sit in the wrong place: deploy's `why:` paragraph after its exit codes, live's board doctor paragraph after its `--json` paragraph, and boards `--list`'s `--json` sentence in `ListBoards.details`. To move them changes `--help` | build | raised | the morning notes, for the PO's eye |
| 6 | flow.py and grant.py stay as they are: each runs two Operations under one sentence and one epilog, and ShowFlow and WriteFlowPage have their own, different summaries | build | raised | the morning notes, for the PO's eye |
| 7 | the card's done line says "every one-Operation core CLI", and flow and grant are two-Operation CLIs, so the line needs restating | build | raised | the morning notes, for the PO's eye |
| 8 | no story run maps to `scripts/spark/design/list_boards.py`, so the hook ran the quick run for this PR | build | raised | the morning notes, for the PO's eye |
