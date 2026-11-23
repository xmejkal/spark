# Round 1, the tech lead, scope and privacy lens (Opus), on the architect's draft (5e99b392)

2026-11-23. Read-only. The lens read design.md, brief.md (D1 to D26), story-map.md, items.md, risks-and-tests.md, the P1035 plan, cards #1518, #1187 and #1533 to #1536, and the code named below. In the walk project it read only the shape of files and keys and printed no value. Verdict: build after fixes. Seven findings are must-fix. The worst are P-1, P-2, F-1 and F-2.

## Privacy

- P-1 · must-fix · The stamp's "which files" list shows the secrets file's name on the page, so A7 fails by construction. STAMP_FILES includes the firmware folder, and the walk project keeps a gitignored secrets file there (design.md, the stamp and the slice 1 mockup). Fix: leave the secrets file out of STAMP_FILES. Show a folder as one line ("firmware/, newest <time>"), never its file names. A test with a made-up secrets file checks that its name is not in the page.
- P-2 · must-fix · "Every new text passes the same mask" protects nothing for the new free texts (issue titles, decided lines, goal, deploy sentences). The page's mask hides paths only: `privacy_for` passes `secrets=()` (show_flow.py:35-37, privacy.py:79-87). Fix: `privacy_for(project)` also masks the string values of the project's secrets file, read with `ast` and never imported. The A7 count tool (T-2) uses the same reader. Test it with made-up values.
- P-3 · must-fix · The `--read` rule fails open: a missing, unknown or stale value lets titles through. The value from `get_artifact` was never read. On a first publish there is no value. Fix: fail closed. Show issue text only when `.spark/page.json` holds a `read` value from a known list that means "owner only". 1f's plan first reads what `get_artifact` answers. If that answer has no such field, use the other option of open item 3.
- P-4 · must-fix · `PublishedPageStore.write` replaces the whole file with `{"artifact": id}` (write_flow_page.py:85-88). So `--artifact` deletes `read` and `published`. Fix: 1f and 1c merge keys through the store's one atomic write. A test checks that `--artifact` keeps `read`.
- P-5 · should-fix · The board logs hold `heard`, the console text that the board printed, which is free text. One of the 27 logs has a Wi-Fi word there. The header lines are safe (deploy_service.py:47-54). Fix: #1533 says the reader takes only the header fields and the verdict sentence, never `heard`, with a mutation row.
- P-6 · should-fix · `gh issue list` in a folder that is not the top of its own repository reads the parent repository's issues, which can name other projects (A7). Fix: `ReadProjectIssues` refuses as could-not-run when `git rev-parse --show-toplevel` is not the project folder. Run gh with stdin closed, `GH_PROMPT_DISABLED=1`, a timeout and an explicit `--limit`.
- P-7 · nit · `.spark/` and `page.html` are tracked in a project's git (the walk project tracks `.spark/page.json`, `project.json` and `page.html`). So `.spark/issues.json` goes into the project's own repository, the same audience. The new cost is git churn: `read_at` changes on every `/spark:page`. Fix: name the churn in 1e's plan. Add no ignore rule in this epic.
- P-8 · ok · Tests use made-up titles in 1e (D23). Add the same rule to 1f and to the D22 test fixture.

## Feasibility

- F-1 · must-fix · The named build never shows D17's mismatch. The plugin's version is 0.9.0 since 2026-10-13, across about 3,800 commits, P1009 among them (.claude-plugin/plugin.json:3). Fix: record a drawing version in the build record, a constant in the sheet's module that any PR raises when it changes the step order or the pills, guarded by a test. Show the plugin version only as text. No schema change is needed (build_record.py:21-22).
- F-2 · must-fix · The stamp test and the published stamp block each other: page.json must be in STAMP_FILES, and `--published` writes it after the publish, so `behind` stays true. Fix: a named exemption list in the test, with a reason each (`.spark/page.json`, `.spark/page-request.json`). Better: cut `--published` (S-3).
- F-3 · should-fix · `decided` with its origin has no writer. `init.py --answers` takes `decided` as any list, and the template says "no script reads it" (project_setup.py:219-222, :357). Fix: 1b's Done-when names the writer: `--answers` accepts `{line, by}`, takes `at` from the clock, keeps plain strings, and updates the `//decided` note.
- F-4 · ok · `gh` through `outside.run` works: flow.py builds a ProgramRunner when RUNS is declared (outside.py:84, flow.py:87-88). Add `read-project-issues` to the operations test and the new modules to `TheFlowAreaTest.MODULES` (test_architecture.py:718, :736).
- F-5 · should-fix · The stamp test writes the page once per fixture file, and `kept_wiring` parses `circuit.json` on each write (write_flow_page.py:104-115). Fix: one small fixture, every time set with `os.utime`, no sleep, measured under a few seconds before the merge. The store's files are outside the stamp, and the page says so: D5's "every file it reads" holds for the project's files only.
- F-6 · nit · `guide.now` as `{phase: null, ...}` breaks truthiness checks (flow_page.py:315, show_flow.py:62, :74, phase_steps.py:67, guide.py:190) and the json.md contract. Fix: keep `now: null` and add one sentence key.
- F-7 · nit · The second D22 test has no mechanism. Fix: an AST test that `write_flow_page` reaches project facts only through `reading_of` and `kept_parts`.

## Scope, size and order

- S-1 · must-fix · Story 1d (`keys` on the request row) is a new click-path interface, which the D24 no-go forbids. P829's code is complete, and its Done-when walk is still the PO's (#1187, comment of 2026-11-22). A1 and A9 do not need 1d. Fix: cut 1d from slice 1. Move the picks-per-need grouping, with the one-click buttons of today, into 1a. File "several at once" under P829 after its walk.
- S-2 · should-fix · 1a as written is L, and 1c holds four things. Fix: 1a-i is FlowReading, the D22 test and page.md reading `show` (no visible change). 1a-ii is the layout. #1535 keeps step N = pill N, the date and the named build. 1c is the stamp list.
- S-3 · should-fix · The published stamp is the architect's proposal, held by no D, and A9's pass line does not need it. P1035 PR 2 already gives Claude a note (`subject: page.html`), and `/spark:page` always republishes (P1035 plan, decision I). Fix: cut it from slice 1, and with it F-2's loop.
- S-4 · should-fix · Order: start P1035 PR 1, P1043 and 1e in parallel (1e has only new modules). Then P1035 PR 2, then 1a. Then 1b, 1c and #1534 (after P1043), then 1f, then the walk. Read the board's WIP limits first.
- S-5 · ok · Each story's Done-when can be read by a test or by the PO, once T-1's rows are added.

Files that two stories touch at once: write_flow_page.py (P1035 PR 2, 1a, 1c, 1f). commands/page.md (P1035 PR 2, 1a, 1e, 1f). page_script.js (P829's walk, 1a, 1c, 1d). run_request.py (P829, 1d). guide.py and show_flow.py (P1043, 1a, 1b, 1f; P1035 PR 1's `FlowFollowUp` calls `now_steps`, which must handle no NOW after P1043). flow_codes.py and phase_readers.py (P1043, P1044, 1a to 1f, P1027's branch). tests/test_architecture.py:718 (P1035 PR 1, 1a, 1c, 1e, 1f). docs/guide/agents/json.md (P1035 PR 1, P1022, 1a, 1e). tests/fakes.py (P1035, P1022, 1e).

## Tests and proof

- T-1 · should-fix · Mutation rows per story. P1043: a tick only on ready seen, the newest log wins, firmware newer than the image means stale, no log means not started, `heard` never appears. 1a: one reading feeds both, developer lines always folded, no tick on a status that is not ok. 1b: a plain string means `by` and `at` are null, a non-list reads as empty, `at` from the clock. 1c: one dropped STAMP_FILES entry is caught, max not min, the mismatch condition, a record with no version, the secrets file left out. 1e: no write after a failed gh, titles and labels only, `read_at` from the clock, the top-folder refusal. 1f: four states, fail-closed `read`, the issues file not in the fingerprint, the mask on titles. Each row is proved with `tools/mutate.py --anchors`.
- T-2 · should-fix · The A7 read is safe only if the secret values never appear on a command line, in the transcript or in a file. Fix: a small tool with tests on made-up values. It reads the secrets file with `ast` and also counts the file's name, the store's path, the home path, the board MACs from the store's board records, and other projects' names. It reads `page.html` and a rows file that Claude exports, prints `name: count` only, and exits 1 on any hit. Build it in 1f. The walk runs it.

## The cards

File 1a (split per S-2), 1b, 1e, 1f and the walk under #1521. Do not file 1d under P1038 (S-1).

- 1a: "The page and flow.py show read the project in two ways, and Claude reads page.html whole → one FlowReading feeds both, one NOW box, developer lines always folded, picks grouped per need; page.md reads flow.py show."
- 1b: "The brief's goal, must and decided lines are not on the page, and a decided line has no origin → Brief.decided as {line, by, at}, written by init.py --answers with the clock's time, shown on top."
- 1e: "Spark cannot read the project's open issues → flow.py issues writes .spark/issues.json (titles, labels, read time) through gh in the repository's top folder; a failed run writes nothing."
- 1f: "The page does not show the project's open issues → an issues box with four states, marked as the project's and ranked by none; issue text only while .spark/page.json says the Artifact is private; the page masks the project's secret values."
- Walk: "Slice 1 is untested with the PO → one walk in p934-display2 with A1, A5, A7 and A9's tests and the leak count; rows in risks-and-tests.md."
- 1d, under #1187: "Several picks at once need one request with keys → decided after P829's walk."

Cards to change:

- #1518: add "PR 2 (D16 of P1038): when page.html exists, the follow-up writes it again on disk, atomically, never publishes and makes no GitHub call."
- #1533: drop "A log with no verified write shows nothing" (it contradicts D10). Add "the reader takes only the log's header and verdict, never its heard text."
- #1535: Done-when becomes "a build made before a change to the sheet's step order says so on the page (a drawing version; the plugin's 0.9.0 has not changed since 2026-10-13)."
- #1534: add "the witness of 'wired' is a log in sim/runs/board/; the warning names its date."

## Open items

- 1 · yes: no build of P1038's sub-issues before the PO confirms. Slice 0 goes on.
- 2 · yes: keep the Flash and Deploy button no-go through the walk.
- 5 · change: STAMP_FILES without the secrets file, with a named exemption list and fixed times in the test (P-1, F-2, F-5).
- 6 · yes to the names and `.spark/issues.json`. Change: refuse a folder that is not the repository's top folder (P-6).
- 7 · no: cut `--published` from slice 1 (S-3). If it stays, page.json merges keys (P-4).
- 8 · yes: the wiring and the pictures stay outside `show --json`.
- 9 · yes: a board log is the witness, and the warning says only what the log shows.
- 10 · yes, recorded for the PO as a narrowing of D23: "with its cause" holds only for "no file". An older file still shows its own read time.
- 11 · yes: the how-to is a short file under docs/guide, written in 1a. Its A7 section points to the T-2 tool.
