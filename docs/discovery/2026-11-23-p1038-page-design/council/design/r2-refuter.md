# Round 2, the refuter, on the revision (31107da7) and the two round 2 lens reports

2026-11-23. Launched on the best model (Fable); its report calls itself "Opus". Read-only. Its compile experiments ran in a temporary folder outside the worktree, now removed. It ran no suite, gate or mutation run.

Verdict: ready for the PO's confirmation after fixes, with no third round. The seam (`FlowReading`, a pure `page_of`, the stamp apart from the fingerprint) held against every check, and no fix changes it. Every round 2 must-fix holds at least in part. V19 is rejected. Eight new findings, two of them must-fix.

## New findings

- S-1 · must-fix · D10's "with its cause" has no source. The board log holds no cause code: its header is the moment, the port, the image, the simulation, the facts line and `verdict: sentence` (bench/deploy_service.py:55-62). The sentence ends in a tool's own error text (bench/ready_probe.py:80, :90). All 9 "ready unknown" logs of the walk project end that way. Fix: P1043 maps spark's own sentence start, before the first colon, to a code with words in flow_codes, and says "cause not recorded" otherwise. `BoardLog` gains a reason line from now on. The port and the facts line stay unread (A7).
- S-2 · must-fix · "The issues show on the page on disk" contradicts fail-closed. The file on disk is the file that `publish_files` sends, and the refresh writes with the audience from page.json. With a missing or unknown audience no page shows the issues, on disk too, and D19 is unmet there. Fix: say so, and put it on the PO's list. Or 1f's plan treats "no Artifact id" as owner only, because a first publish starts private. State which audience the refresh writes with.
- S-3 · should-fix · A route that can close Q-C's share window, not verified: the database declaration has read and write values per path (commands/page.md, step 5). If a path can be owner-read, the server refuses issue rows to a viewer. Fix: 1f's plan asks `describe_capabilities` before it builds the audience route.
- S-4 · should-fix · Claude's read-only route has no source for the Artifact id: `show` does not answer it (show_flow.py:112), and only `flow.py page`, which writes, does (write_flow_page.py:182). Fix: `show` answers `data.artifact`, named among the D22 exemptions.
- S-5 · should-fix · A9's instrument fails on a correct page: after 1c the stamp covers firmware/, and a firmware edit writes no page. Fix: compare `data-stands-at`. For `data-written` the pass is "never newer than show's, and where older the freshness line said what to type". On the PO's list: D16 holds for the core's runs only, so 1b's own writer leaves the DECIDED box stale.
- S-6 · should-fix · The leak count tool fails the page it must pass: it counts other projects' names and exits 1 on any hit, but A7 allows those names on the owner's page. Fix: the tool takes the audience, and the names and the issue text are hits on a shared copy only.
- S-7 · should-fix · "owner: buttons, the request line, the issues" reads as the script hiding issue text from a viewer. Text in the HTML reaches every viewer. Fix: drop "the issues" there. The issue text is a write-time choice by the audience, never the script's.
- S-8 · should-fix · Measured with the installed tsc 7.0.2 on today's script. Layout: 330 lines, 4-space indents, no blank line, so 8 of the 18 anchors no longer match, and the closing `// --- end MVP ---` line is dropped. Options: strict gives 163 errors before any type is written. `module: none`, `outFile` and ES5 are refused (TS6046, TS5102, TS5108). ES2015 emits `__awaiter`, ES2017 does not. At ES2022 a typed class field is emitted as a real field. Fix: target ES2017 to ES2021, or `useDefineForClassFields: false`, with one test. Size S is doubtful: measure first.

## The lens findings

- B1 · CONFIRMED · guide.py:69 and bench/image_evidence.py:348 read the list. Only phase_readers.py:558-559 prints names.
- B2 · CONFIRMED · "secret" occurs in four files, all account-token code. The walk project's .gitignore names its file, so the plan can weigh "a file under firmware/ that git ignores" against a name glob.
- B3 · CONFIRMED, reproduced · the 18 rows hold only file, name, find and replace. tools/mutate.py:189 drops SPARK_GATE_TREE from every run. The design's own fallback (mutate the .ts) fails the same way. The gate's verdict is the suite's exit code, so a skip is green, and the fix works only with B4. Simpler: the drift check as a gate step beside `node_refusal`, not a unittest.
- B4 · CONFIRMED, raised to must-fix with B3 · "The gate then stops the story run" is untrue today.
- B5, B6 · CONFIRMED, measured (S-8).
- B7 · CONFIRMED · brief.md:146. The installed typescript package holds no tsserver.
- B8, B9 · CONFIRMED.
- B10 · CONFIRMED · add `run-request`: its data goes into answer rows that every viewer reads.
- B11 · CONFIRMED on the facts, PARTLY on the fix · the P1035 plan's decision 2 (lines 121-124), PR 2's "same condition" (362-364) and its test (380-382). A crash becomes a could-not-run result (core/cli.py:71-75). PR 2 is not built. "Write 0c into PR 2" reverses Q-F (2 of 3, delegated). Either that goes on the PO's list, or 0c stays its own story and PR 2 gives the refresh its own condition function now.
- B12 · CONFIRMED, raised to must-fix · write_flow_page.py:104-115 draws the steps now, and breadboard.py:64 never touches build.json. "Steps and pictures: from the build of" is untrue.
- B13, B15 · CONFIRMED, nits. B14, B16, B17 · CONFIRMED.
- V1 · CONFIRMED · brief.md:127 against the design. The cause needs S-1.
- V2 · PARTLY, should-fix · the mapping is at flow_codes.py:289, but the guide uses it for a simulate NOW only. A deploy NOW takes the reader's own "your terminal" (phase_readers.py:566). The walk project has no Wokwi model, so no IMAGE_OLDER arises there. A new rule for P1043's plan.
- V3, V10 · accepted. V4, V5 · PARTLY: the README and diagrams.md already call the mock "a starting picture, not a decision". V9's paragraph settles them.
- V6, V7, V8, V11, V16, V18, V20, V21, V22 · CONFIRMED. V9 · CONFIRMED, raised to must-fix: it carries V4 to V8.
- V12 · PARTLY · the design already republishes once after a first publish. The fallback half is confirmed and worse (S-2).
- V13, V14, V15, V17, V23, V24, V25 · accepted.
- V19 · REJECTED as an order change · D29 is his order with no date. The chore before 1a-ii writes the script changes once, and nothing starts before his yes (Q-A). tsc's output is now measured. One line on his list is within D29, but moving the chore without him is not.

## Before the PR leaves draft

1. B1 and B2: the secrets rule.
2. B3 with B4, and the third table (p993-blockers).
3. V1 with S-1.
4. B12 and V22.
5. S-2 and V12's fallback.
6. V11.
7. V9's paragraph and B17's marks.
8. B11: decision 2 named, the crash excluded.
9. B10 with run-request.
10. V18's list, with Q-F, the fallback, D16's limit, the language server and the tracked issues file.
11. V20's walk order.

Then one refuter read of the diff, a check and not a round. The rest goes to the stories' plans as rows.

Not checked: the Artifact server (get_artifact's owner-only word, an owner-read database path, whether `publish_files` needs a read), a strict compile with real types, TypeScript 6, and `gh issue list` in a nested folder.

## The last read

2026-11-23, about 19:15 CET. The same refuter read the diff of the last revision (31107da7 to bd9428b3), a check and not a round. All eleven items landed. Two must-fixes: R-1, the Council line promised a result that was not there, and R-2, Claude's closing lines had no source in `Written` (write_flow_page.py:44, :182). Smaller points: R-3, the pick "no Artifact id means owner only" narrows Q-C and goes on the PO's list, and a new id clears the audience. R-4, `holds` clashes (design/needs.py:473, pin_assigner.py:198). R-5, the drift check's key is the changed files, and it runs under `--full`. R-6, the picture says "written on", with the time recorded at `sheet.write`. R-7, the how-to's fresh session comes after A1. R-8, the deploy's note (bench/image_evidence.py:348-350) is for 1c's plan. R-9, four things from a log. The main session fixed all nine in design.md. Verdict: ready to leave draft once R-1 and R-2 land.
