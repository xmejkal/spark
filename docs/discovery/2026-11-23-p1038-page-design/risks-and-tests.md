# Risks and tests

## Risks
<!-- One row per type; an active extension adds its own rows. evidence now: tag and ids (★C<n>, A<n>).
status: open · retired · n/a because ….
e.g. `| usability | H no test yet (A2) | a five-person prototype test | open |` -->
| risk | evidence now | cheapest way to retire it | status |
| --- | --- | --- | --- |
| value <!-- REQUIRED:risk-value --> | E ★C12: 5 clicks in 11 minutes and none after (clicks, not views), and later work went through the chat (n = 1); H that a true page gets opened (A1, A2) | the next walk (A1's test); QA1 and QA2 are answered (Results) | open |
| usability <!-- REQUIRED:risk-usability --> | E P1011 #1470, USER-4 to USER-8, USER-15: wrong order, stale top, step numbers off by one, developer lines; H that grouping and one NOW fix it (A5) | a prototype screenshot read by the PO, n = 1 | open |
| feasibility <!-- REQUIRED:risk-feasibility --> | E ★C10, TECH-5: the deploy logs exist and hold time, image and ready line; — whether a live route works (A4, A8) | a read of the 27 logs (A3); a db spike only if a live route is chosen | open |
| viability <!-- REQUIRED:risk-viability --> | E C5: runtime contract 0.2.98, below 1.0; E ★C16: GitHub Pages is public on every plan except an organization on Enterprise Cloud; only that host was read | keep the page working with every capability null (P820's no-go), so a runtime change cannot blank it | open |
| ethics and safety <!-- REQUIRED:risk-ethics --> | E ★C16: files reads raw files with the viewer's access beside wifi_secrets.py; GitHub Pages is public on every plan except an organization on Enterprise Cloud; E C14: Build on a wired board can move pins (H, not run) | no route that reads raw files or goes public (proposed no-gos); a guard on pin-moving offers (A7) | open |
<!-- EXTEND:risk-rows --><!-- EXTEND:pair-rows -->

## Assumptions
<!-- About ten at most. type: value, usability, feasibility, viability or ethics. importance: "— (decider)" until
the decider rates it, then "high D<n>" or "low D<n>". pass line: written, with its date, before any result.
status: open, or retired with the date of its Results row.
e.g. `| A2 | Assignees never see new tasks | value | H ★C2 | — (decider) | query opened-within-48h | under 50 %, set 2026-10-06 | over 80 % | retired 2026-11-23, missed |` -->
| id | belief | type | evidence now | importance | cheapest test | pass line, dated | result that would change the decision | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 <!-- REQUIRED:assumptions --> | The PO opens the page after the build, instead of the chat or the project's issues, once it shows the true stand | value | H the frame's outcome; against it E ★C12 (n = 1) and QA1 ("A Claude session", Results); P820's A5 ran the same test (PO-19); rival: he opens it once it reads well | high D3 | QA1 now; then the next walk: does he open the page on his own after the build | in the next walk, whose plan does not script the page and whose session does not name the page first, he opens it on his own at least once after the build and does not then ask Claude where the project stands; the session writes it in the diary from his words, set 2026-11-23 (D3) | he never opens it, or opens it and then asks Claude where the project stands | open |
| A2 | Most of what he wants first is held by spark as a record or a witness | value | H; against it E ★C13 | high D3 | the desk check: he names five things (QA2), each marked spark record or witness, project file or issue, or nowhere | at least 3 of 5 from a spark record or witness, set 2026-11-23 (the tech lead also counts the brief record and the logs as spark\'s; the architect counts decided lines as the project\'s file) | 2 or fewer: the page needs new readers of the project's own files, or a link out | retired 2026-11-23, missed |
| A3 | The deploy logs in sim/runs/board/ give the deploy's stand per project, without the board's MAC | feasibility | E TECH-5 (one log read; no MAC in the 27 logs) | high D3 | read the 27 logs' headers | proposed: every log has time, image sha256 and a ready line, set 2026-11-23 | a log without a ready line or an image | retired 2026-11-23 |
| A4 | The files capability works from a local Claude Code session (a chan_ id) | feasibility | — (PO-13, TECH-19) | low D3 | a one-page spike, only if O3 picks a live read of files | not proposed: no option needs it, set 2026-11-23 | — | open |
| A5 | One NOW, picks grouped per need and the developer lines folded make the page readable to him | usability | E P1011 #1470; H the fix | high D3 | a prototype screenshot read by the PO | proposed: he names the next step and finds every Pick within 30 seconds, set 2026-11-23 (the 30 seconds has no source; the tech lead drops it) | he still says "not readable" | open |
| A6 | A style with system fonts and no web loads (D7) can look good to him | usability | H; E C15 (the skill asks for chosen typefaces) | low D3 | two screenshots, system fonts against one inlined font | proposed: he prefers the system-font version or calls them equal, set 2026-11-23 | he prefers the inlined font clearly | open |
| A7 | No secret and no other project's name reaches a viewer other than the PO; drawer counts follow D10 of P820 unless the PO tightens it | ethics | E ★C16, USER-15 ("held by reaction-game") | high D3 | a read of the page text and its db rows for each route | zero hits for the Wi-Fi name and password, the secrets file, home paths, the store's path and the board MAC, on the page text and its db rows; on a copy shared beyond the PO also zero names of other projects, set 2026-11-23 (D3) | any hit | open |
| A8 | A db state doc can carry the flow's state to an open page within the db's limits | feasibility | — (TECH-18; size and rate not read) | low D3 | a spike, only if O3c is chosen | proposed: a state doc of p934-display2's flow is written and an open page shows it within 60 seconds, set 2026-11-23 | — | open |
| A9 | A snapshot page is fresh enough when its stamp has a date and covers every file it reads (the trigger is Q12) | usability | H; E C11 (the stamp covers 3 files) | high D3 | the next walk: does a stale page mislead him | proposed: no step taken on a stale page's word, set 2026-11-23 (the architect adds: page.html and `flow.py show --json` name the same stand at the walk's end) | one step taken on a stale page | open |

## Collection plan
<!-- One row per gap. e.g. `| Do assignees open new tasks? | Q2 | Lena, from analytics | one query | this week |` -->
| question | decision it blocks | who can answer | how | when |
| --- | --- | --- | --- | --- |
| What did he open the last time he came back to the clock? <!-- REQUIRED:collection --> | A1, Q2 | the PO | QA1, answered 2026-11-23 | done |
| Which five things does he want to see first? | A2, Q2 | the PO, then the facilitator marks each | QA2, answered 2026-11-23; the mark took a minute, not the planned 30 | done |
| Which goal is current: the clock and button, or a quote every hour? | the page's goal line | the PO | QA3, answered 2026-11-23 (the quotes clock) | done |
| Do the 27 logs all carry time, image and ready line? | A3, item 1 | the facilitator or the story's builder | read the headers | before item 1's plan |

## Results
<!-- Filled on a return; may stay empty until then. One row per result: what was tested, what was seen (verbatim,
with its pointer), the pass line met or missed, what it changes. -->
| date | source and pointer | what was seen | pass line met or missed | what it changes |
| --- | --- | --- | --- | --- |
| 2026-11-23 | QA5, the PO, 17:42 CET (account, n = 1) | the top line "? Could not run: the board record names no wokwi_part_type" after a build that worked: he read it as "The build failed" | — (evidence for A5) | the first page slice words a partial result plainly: what worked, what could not run and why |
| 2026-11-23 | QA6, the PO, 17:42 CET (account, n = 1) | he named the picture and Claude in the chat, not the page's text steps or breadboard.md; but diary.md:190 has him say at 11:41 "i've already connected it", and breadboard.svg was written at 11:44, so he may name a later check or re-wire | — (weak evidence for A5 and P1045) | which leads, the picture or Claude's words, is —; P1045 keeps the list and the picture in step either way |
| 2026-11-23 | QA1, the PO in the page-design session, 17:39 CET (account, n = 1) | "A Claude session" (an option label in the dialog) | — (A1 is tested in the next walk; this is evidence against it, for its rival) | Claude is the first reader of the state, so `flow.py show --json` and the how-to's sentences (D12, commands/page.md:73) matter as much as the page |
| 2026-11-23 | QA2, the PO (four option labels picked), 17:39 CET, and the facilitator's mark of each item against where its facts live in p934-display2 | he named 4 things: what is on the board (spark: deploy logs, board record), the next step (partly spark: NOW up to the deploy, then the project's issues), the goal and must lines (spark: brief record; whether each works: nowhere), the open problems (mostly the project's issues and docs) | missed on the facilitator's grouping (A2): 2 of 4 clearly from spark's records, against "at least 3 of 5"; with goal and must as two items it is 3 of 5, met, and three of the six open issues have their fact or its null in a spark record (council/refuter.md, T-9) | D19: the page also reads the project's open issues (O2b) |
| 2026-11-23 | p934-display2/sim/runs/board/*.log, the first 8 lines of each, read with `head` by the facilitator, about 16:43 CET; also council/answers-tech-lead.md | 27 of 27 logs hold (the facilitator's count) an `image sha256:` line and a `ready ` line, the first line names the time and the port | met (A3), for one board on this machine; the logs hold two of the four verdicts, and a clone has no logs (sim/runs/ is gitignored) | item 1 can read the deploy states from the logs, with no MAC; D10 sets what each state shows |

<!-- EXTEND:risks-sections -->
