# P714 slice 1, the texts agents read say the 11-08 test cadence: rows

The PO decided on 2026-11-08 that the full run and the mutation runs are sweeps, not gates of a pull request
(rules.md). Texts that agents read still said the old rule, and P724's plan followed them into a 30-minute mutation
run. This slice makes them say the new rule, with the glossary as the one full statement. Card:
[P714 #963](https://github.com/xmejkal/spark/issues/963). The reviewer ran on Sonnet.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | six texts said a mutation run comes before each pull request that holds logic | PO, P724 | acted | `GLOSSARY.md`, `.claude/agents/mutation-tester.md`, `docs/guide/developing.md`, `scrum/README.md` (council, DoD 1 and 2, sweep), `scrum/WORKING_AGREEMENTS.md` W3, `scrum/TEAM.md` |
| 2 | five more texts said the full run comes before a PR is marked ready or before an auto-mode merge | reviewer | acted | `WORKING_AGREEMENTS.md`, `GLOSSARY.md`, `developing.md`, `tools/check_commit.py` docstring and `--full` help: a sweep, or when the PO asks |
| 3 | the mutation tester's body still spoke of a branch and its changed lines | reviewer | acted | it reads the sweep's diff and writes at most 12 new rows for the whole sweep |
| 4 | the glossary's command block labeled a branch, and `developing.md` used `$changed` with no definition | reviewer | acted | both say a sweep, and name the wave's files |
| 5 | the PO's quotes repeat in `scrum/README.md` and the glossary, and the agent's description is about 90 words | reviewer | rejected | each page is read alone, so each keeps the PO's words; the description says when the agent runs, which is the text the council reads |
| 6 | the hook half of P714 (the push hook runs only the story's tests) is not in this slice | build | closed | the rest of P714 #963 — P776: done by #963 (closed), P714 #963 (closed) |
