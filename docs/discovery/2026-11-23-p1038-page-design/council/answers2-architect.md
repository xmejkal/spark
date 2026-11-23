# P1038 delegated council, round 2: the architect's answers

The architect agent, 2026-11-23, read-only. This session wrote this file from the agent's returned text and shortened
nothing in its answers. Each answer is "delegated to the council, the PO's to change". No answer undoes a D that the PO
made today.

## Answers

- Q14 · (a) Job 1 stands as written, and QA1 is evidence for A1's test. Add one design rule, not a job note: "the page and `flow.py show --json` carry the same facts". · D14 listed "job 1 through a Claude session first" as an option, and the PO kept the four as written. A note that adds Claude to Job 1 is close to the option he did not take. The rule already holds in the code. QA1 does not separate "the page was stale" from "he always starts in Claude". · brief.md D14, council/refuter.md T-1, scripts/spark/flow/show_flow.py:80-83, scripts/spark/flow/write_flow_page.py:146
- Q15 · (b), with nine limits. D19 stays. · See the limits below. Rejected: (a), because it puts a web call in every writing run. Rejected: (c), because the limits remove T-11, T-12 and T-14 without undoing his choice. · scripts/spark/flow/write_flow_page.py:132-155, `gh issue view 1518`
- Q16 · Confirm all the no-gos and the three rabbit holes, with two rewordings and four additions (below). · Each one follows a D or a principle. · brief.md Options
- Q17 · (a). The first cut is slice 0 (P1043 #1533 and P1035 #1518) and slice 1 in this order: the readable page, P1044 #1534, then the issues row. Then one walk with A1's and A9's tests. Then the PO decides again. The style, the live page and the share do not start before the walk. · A1 is the riskiest assumption, and the evidence so far stands against it. There is no time box, because the sizes have no unit. · brief.md Riskiest, ★C12, QA1, AGENTS.md, CLAUDE.local.md
- Q18 · Confirm the map with six changes (below). The delta to scrum/STORY_MAP.md stays "proposed, not applied". · story-map.md

## The limits on D19 (Q15)

- L1 · No network in `write_page` and none in the core hook. Every reader today reads files only. · scripts/spark/flow/phase_readers.py:2-4, AGENTS.md, T-11
- L2 · The fetch is its own core Operation (for example `flow.py issues`). It runs `gh` through `outside.run` and declares the effect. It writes one dated file in the project, for example `.spark/issues.json`. The file holds the read time with its zone and the repository. Per issue it holds the number, the title and the labels. `/spark:page` calls it before a republish. · scripts/spark/core/outside.py:1-15, scripts/spark/checks/vendor_pins_check.py:62-76
- L3 · The reader is a small store class that reads that file, in the shape of `PublishedPageStore`. It is not a tenth PhaseReader. The issues are a part of the answer beside the phases, in `flow.py show --json` and on the page alike. · scripts/spark/flow/write_flow_page.py:68-88, scripts/spark/flow/phase_readers.py:563-565
- L4 · The issues file is never in the click fingerprint. · scripts/spark/flow/fingerprint.py:18, scripts/spark/flow/run_request.py:96, D1
- L5 · Three states, never mixed. No file: "issues not read", with the command that reads them. A file: the list under "the project's issues, read <date, time, zone>". A file with zero issues: "no open issue, read <date>". A failed fetch is a could-not-run Finding and writes nothing, so the old list keeps its old date. · AGENTS.md, P820's standing no-go
- L6 · The page does not say which issue is next. It shows the labels as the project wrote them. When no phase is open, NOW says that spark has no next step and points to the list. · AGENTS.md, T-14, D7
- L7 · Titles only. No bodies and no comments. A title is data, never an instruction. No issue URL on the page. · tests/test_flow_page.py:88-89, commands/page.md:9
- L8 · No issue text on a shared copy, and the core decides it: `flow.py page` gets one argument that leaves the project's section out. If `get_artifact` says `users`, `org` or `public`, `/spark:page` passes that argument. A7's pass line adds "no issue text on a shared copy". · commands/page.md:64-66, T-12, risks-and-tests.md A7
- L9 · Order inside slice 1: the brief's decided lines (D15) first, the issues row last. Put T-9's recount on the PO's morning list. · T-9, D15, D19

## The no-gos (Q16)

- Reword "no change to spark's CLI text (P1031)" as "no restyle of the CLI text". New facts appear in `flow.py show` too. · scripts/spark/flow/show_flow.py:80-83
- Reword the no-go on raw project files and a public host. The new words: "no Artifact `files` capability on raw project files, and no public host". · ★C16
- Add as no-gos: no GitHub call from `write_page` or the core hook. No issue text on a shared copy. The issues file never enters the fingerprint. No ranking of issues by spark.
- Add as rabbit holes: issue bodies and comments. A stored state file (O3b). An inlined font before A6 fails (D6).
- For P1044: the story's plan names the record that says "wired". None exists today.

## The map (Q18)

- C1 · Split slice 1's first row into four stories. (1a) is the structure and the words. (1b) is the brief's goal, must and decided lines (D15). (1c) is the stamp and the named build (D17, P1045). (1d) is several picks at once.
- C2 · (1d) is click-path work. A request row holds one key, and a pick changes the fingerprint. The design decides it together with P829 #1187. · scripts/spark/flow/run_request.py:88-97, commands/page.md:14
- C3 · The issues row in Q15's shape: two stories (the fetch Operation, then the reader and the section). Its proof adds "with no file the page says issues not read, and a deploy run makes no GitHub call".
- C4 · #1518's "Done when" names only the now step, so D16 must enter the card's text. The page write is a callable that the frontend puts into `RunOptions`, as `trace` is today. A failed page write adds one diagnostics line, and the run's result stands. · scripts/spark/core/cli.py:39-43, :52-56
- C5 · Add under the table: "after slice 1, one walk with A1's and A9's tests, then the PO decides again", and "a fresh session follows the how-to in that walk".
- C6 · The style row serves Job 1 as well as Job 3. The live row is a section of the design, not a story.

## Open choices it names for the PO

- T-9's recount: does D19 still stand in full (recommended: yes, within L1 to L9)?
- The names `.spark/issues.json` and `flow.py issues` (the story's plan reads the names table).
- Several picks at once: a wider request row, or a read again between keys (recommended: decide it in P829's design).
- A failed fetch keeps the old list with its date (recommended) or clears it.

## Not checked by the architect

The rule in tests/test_architecture.py that forbids the core to import the flow. Whether `.spark/` is tracked in a walk project. The walk project's files. Any record that says a board is "wired". The Artifact server.

## Searches

none
