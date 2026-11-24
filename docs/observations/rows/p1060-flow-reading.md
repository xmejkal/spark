# P1060 PR A: one FlowReading feeds flow.py show and the page: rows

Card: [P1060 #1558](https://github.com/xmejkal/spark/issues/1558), PR A ([#1605](https://github.com/xmejkal/spark/pull/1605)).
The review ran on 2026-11-24, with one lens on Sonnet and the refuter on Opus. It found no must-fix, and every claim of
the PR held. This file holds the acted, raised and rejected findings only. PR B (the secret mask) has its own rows file.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `artifact-how-to.md` §6 gives an order of a republish that contradicts `commands/page.md` 4.3 to 4.5: per request, page.md runs the request, writes and republishes the page, and only then calls `db_write`. §3.1 sends a published page to "the republish", not to "carry the requests" | the refuter | acted | fixed in the PR: §6 copies page.md's order (show, `db_query`, none waiting: page and republish; per request: the request file, `run-request`, page and republish, then `db_write`), and §3.1 links `commands/page.md#carry-the-requests` |
| 2 | test 1 exempts `data.deploy.verdict` by its path, so a page that lost a `ready seen` verdict would pass | the refuter | acted | fixed in the PR: `SAID_IN_WORDS` holds the pair (`data.deploy.verdict`, `ready unknown`), so only that value is exempt |
| 3 | the EPILOG's `flow.py page` paragraph lists page's own `--json` keys beside show's nine, and a reader can take them for show's | the lens | acted | fixed in the PR: "With --json, flow.py page prints its own keys, not show's nine" |
| 4 | an EPILOG line in the page paragraph is over-long | the lens | acted | fixed in the PR: re-wrapped |
| 5 | `flow_and_guide` takes `deploy or read_deploy(project)`, which reads a falsy state as none | the lens | acted | fixed in the PR: `deploy if deploy is not None else ...`. A `DeployState` is a namedtuple of five fields and never falsy, so no answer changes and no test applies |
| 6 | the exemption of a leaf by name and the check by substring can hide a miss | the lens | rejected | dropped because the plan accepts both (A7: a leaf the page does not show is exempted by name with its reason); the refuter checked that no counted leaf is missed on the three fixtures |
| 7 | one `flow.py page` run reads `.spark/page.json` twice: once in `reading_of`, once for `data.artifact` | the refuter | raised | destination: card P1066 #1564 (story 1f, page.json's merged writes). D10 keeps `Written` and the data of `write-flow-page` as they are, so the reading does not reach them in this PR |
| 8 | the reading's read order changed: the fingerprint and the stamp are read before the parts | the refuter | rejected | dropped because it is no regression: the parts read only the pictures and the wiring, and the golden page's bytes are unchanged |
