# Round 1, the refuter, on the architect's draft (5e99b392) and the three lens reports

2026-11-23. Launched on the best model (Fable); its report calls itself "the Opus seat". Read-only, no GitHub write (two `gh issue view` reads: #1534, #1187). In p934-display2 it ran counts only and printed no value. Verdict: revise and go to round 2. The seam (`FlowReading`, the stamp apart from the fingerprint) stands.

## Its own findings

- R-1 · must-fix · The hook does not fire for the stand that was wrong. The P1035 plan plugs `FlowFollowUp` into `parts.py --pick` and `check_spine.py --keep` only (plan line 41), and its round 2 A skips the page after a kept build. So PR 2 writes the page after a pick only. `deploy.py` has no follow-up (scripts/deploy.py:56), though `DeployImage` declares WRITES (bench/deploy_image.py:431) and writes the board log into the project (bench/deploy_service.py:77). A firmware edit, `init_project.py --answers` and `breadboard.py` are out too. Fix: P1035 PR 2 or a named story gives `DeployImage` a `written_project` and the follow-up, or the design states the limit and the plan's "follows every writing run" (plan line 385) goes.
- R-2 · must-fix · A7's shared-copy read fails by construction: the parts phase prints other projects' names (`HELD_BY`, flow_codes.py:108, phase_readers.py:241). Fix: build the held-by rule in 1f, or drop the shared-copy read from this walk and say that A7 stays open for a share.
- R-3 · must-fix · The secrets file's name has a second route: `ProjectImage.find_newer_files` lists every file under firmware/ newer than the image (firmware/project_image.py:121-125), and the simulate reader prints them (`NEWER_MESSAGE`, flow_codes.py:67). Today's p934-display2 page has 0 hits (counted). Fix: one filter for the says line and the stamp list, with one test.
- R-4 · should-fix · `published` in `FlowReading` breaks the D22 test: a published page cannot hold the stamp of its own publishing, and a shared copy drops titles that `show --json` keeps. Fix: name the fields that the D22 test exempts, or cut `published`.
- R-5 · should-fix · Item 9 fails open: wiring comes before the first deploy (phase_readers.py:571-572), so no log exists between wiring and the first deploy, and a clone has no logs. Fix: the earlier witness is the kept sheet (guide.py:104-107), worded "a sheet was written; if you wired from it".
- R-6 · should-fix · If P1044's dated warning lands in `Offer.effect`, every deploy changes the fingerprint (fingerprint.py:28 hashes `effect`), and the next click is refused as stale. Fix: the dated line belongs to the section, never to the offer.
- R-7 · should-fix · The draft rests on D1 to D26 and says the install waits for the PO. D28: frontend-design is installed at user scope.
- R-8 · nit · The mockup's "spark 0.12" and "0.13": the manifest says 0.9.0, and the newest version tag is v0.9.0.
- R-9 · nit · The "no http in the page" test (tests/test_flow_page.py:88-89) trips on free text such as an issue title with "HTTP". The 1f fixture guards `src=` and `href=` instead.

## The lens findings

- A1 · CONFIRMED · write_flow_page.py:196-197; `data-written` and `data-fingerprint` exist (flow_page.py:305).
- A2, A3, A4, A5, A7, A10, A12, A14 · CONFIRMED.
- A6 · PARTLY · `--read` exists at sourcing/read_datasheet.py:33. `decided` is at init_project.py:34, not :47.
- A8 · PARTLY · true in substance. The cited lines are wrong, and the validator takes any list (build/project_setup.py:357).
- A9 · PARTLY · the lines are true. No test read forbids build importing bench.
- A11 · not reproduced · a judgment on a later design.
- A13 · CONFIRMED · one ignored secrets-named file in the walk project's firmware/ (count only). See R-3.
- UX-1 · PARTLY · "?" is could-not-run (phase_readers.py:32). D10 leaves the status to P1043's plan, so the fix is to draw no glyph before that plan picks one. Should-fix.
- UX-2 · PARTLY · the actor is "your terminal" (phase_readers.py:557, flow_codes.py:17), so "by you" is wrong. "Claude first" is by analogy only: `IMAGE_OLDER_NOW` serves the simulate phase (guide.py:129-131).
- UX-3, UX-4, UX-5, UX-9, UX-10, UX-11, UX-20 · CONFIRMED. On UX-4: `--read` moves the stamp the same way.
- UX-6 · PARTLY · D23 holds both clauses in one sentence (brief.md:140), and no design meets both for "no network". The fix breaks "writes nothing", so it is a change to D23, not a must-fix on the draft.
- UX-7, UX-8, UX-12 to UX-19 · design judgments, nothing found against them.
- P-1 · CONFIRMED, and not enough alone (R-3).
- P-2 · PARTLY · `privacy_for` passes `()` (show_flow.py:35-37). The fix as written is unsafe: a secret rule has no word boundary (privacy.py:82), and the rendered page is masked whole (write_flow_page.py:154), so a short Wi-Fi name corrupts the script or the SVG. Mask the texts before the render, with a minimum length.
- P-3 · PARTLY · fail-open is true. "Never read" is not: page.md:64 names `read` with `users`, `org`, `public`. The private value's word is not in the repository.
- P-4 · CONFIRMED · write_flow_page.py:88.
- P-5 · PARTLY · `heard` is free text, but the header is not all safe: its line 4 holds a tool's error text in 8 of 27 logs. 19 logs have a Wi-Fi word after the header. No MAC shape in any header.
- P-6 · not run (it needs a GitHub call). The fix is cheap either way.
- F-1 · CONFIRMED · 0.9.0 since 3ba64f8e (2026-10-13), 3,208 commits to HEAD, P1009 on 2026-11-22.
- F-2 · PARTLY · the loop is true. Cutting `--published` does not end it: `--read` and `--artifact` also write page.json.
- F-3 · CONFIRMED · project_setup.py:219-222, :357. The script is `init_project.py`. A8 and F-3 name the same writer, the CLI and its library.
- F-5 · not measured.
- F-6 · CONFIRMED, raised to should-fix · show_flow.py:63 prints "NOW (None)", :74 reads `["offer"]`, flow_page.py:318 the same, and P1035 PR 1 calls `now_steps` on every writing run.
- S-1 · REJECTED as must-fix · the draft builds 1d only with P829's decision, D26's wording, set in the same round as D24. Cutting it breaks D11 (PO-confirmed: slice 1 holds "several picks at once", brief.md:128). True part: `keys` changes the row, the answer and page.md:13, :78, so P829's walk comes first, and the PO hears that D11's item can miss the walk.
- S-2 · CONFIRMED (judgment). S-4 · PARTLY · the order must place R-1's deploy follow-up. S-3 · PARTLY (item 7).
- T-1, T-2 · CONFIRMED as proposals. T-2 uses P-2's reader with the limit above.

## Where the lenses disagree

- Item 7 (A1 keep a cheaper form, S-3 cut): the evidence holds S-3's side. No D holds the record, A9's line does not need it, and `/spark:page` republishes on every run (page.md:73, :87). The walk compares the published page's stamp with `show`'s instead. The exemption list for page.json stays (F-2).
- Item 10 (yes twice, UX-6 change): neither side meets D23 as written. Cheapest: keep "writes nothing", drop the "type /spark:page" advice from the no-file sentence, and record the narrowing for the PO.

## Not checked

The Artifact server's answers (`get_artifact`'s private value), `gh issue list` in a nested folder, the speed of the stamp test, A11, the cards #1518, #1533 and #1535.
