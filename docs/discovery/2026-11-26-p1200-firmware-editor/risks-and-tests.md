# Risks and tests

## Risks
<!-- One row per type; an active extension adds its own rows. evidence now: tag and ids (★C<n>, A<n>).
status: open · retired · n/a because ….
e.g. `| usability | H no test yet (A2) | a five-person prototype test | open |` -->
| risk | evidence now | cheapest way to retire it | status |
| --- | --- | --- | --- |
| value <!-- REQUIRED:risk-value --> | H for A1 and A3. A2 retired by D3 (★C11, counted by co-author line) | SQ21 left it open (D12). A use log of the page once the show slice exists | open |
| usability <!-- REQUIRED:risk-usability --> | H: the friction of 2026-11-25 was the words and the copying (A4, rated high by D10) | SQ14 missed the pass line (D13): the deploy step carries a Copy button | retired by D13 |
| feasibility <!-- REQUIRED:risk-feasibility --> | E ★C1 (nobody tried a port there), ★C7, ★C8. D4 builds no host feature, so no feasibility test is needed now | none now | retired for this epic by D4 and D5 |
| viability <!-- REQUIRED:risk-viability --> | H: the epic is after the MVP and nobody is blocked (council/po-assistant.md, PO-1). H: the Artifact contract moved twice in six days (A10) | read the contract version at each republish for two weeks | open |
| ethics and safety <!-- REQUIRED:risk-ethics --> | E ★C9, ★C10: a page yes is relayed, and a program can type a yes into a pseudo-terminal. E ★C13: a literal secret in main.py is masked nowhere (A8, A9) | the no-gos in brief.md, and a scratch page with a fake literal once the fold exists | open |
| power and battery <!-- REQUIRED:electronics-firmware:power --> | n/a because the epic changes how firmware reaches the board, not the board's power | — | n/a |
| current and stall <!-- REQUIRED:electronics-firmware:stall --> | n/a because no motor or driver is involved | — | n/a |
| thermal <!-- REQUIRED:electronics-firmware:thermal --> | n/a because no part changes its load | — | n/a |
| EMC and ESD <!-- REQUIRED:electronics-firmware:emc-esd --> | n/a because no circuit changes | — | n/a |
| sensor drift and calibration <!-- REQUIRED:electronics-firmware:sensor-drift --> | n/a because no sensor is involved | — | n/a |
| brown-out <!-- REQUIRED:electronics-firmware:brown-out --> | n/a because the flash path keeps today's USB power | — | n/a |
| wake and low power <!-- REQUIRED:electronics-firmware:wake --> | n/a because no sleep mode changes | — | n/a |
| the firmware–hardware contract <!-- REQUIRED:electronics-firmware:contract --> | E C19, for a browser flash only | n/a after D4: no browser flash | n/a, D4 |
| supply and documents <!-- REQUIRED:electronics-firmware:supply --> | n/a because no part is bought | — | n/a |
<!-- EXTEND:risk-rows --><!-- EXTEND:pair-rows -->

## Assumptions
<!-- About ten at most. type: value, usability, feasibility, viability or ethics. importance: "— (decider)" until
the decider rates it, then "high D<n>" or "low D<n>". pass line: written, with its date, before any result.
status: open, or retired with the date of its Results row.
e.g. `| A2 | Assignees never see new tasks | value | H ★C2 | — (decider) | query opened-within-48h | under 50 %, set 2026-10-06 | over 80 % | open |` -->
| id | belief | type | evidence now | importance | cheapest test | pass line, dated | result that would change the decision | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 <!-- REQUIRED:assumptions --> | He wants to read main.py and pins.py on the page, not in the chat or an editor | value | H: a wish on record twice (council/user-ux.md, UX-18), no account of a moment | high D10 | account question Q2 and SQ21 | he names one moment he wanted to read the firmware himself and where he looked, set 2026-11-26 | no moment: the show slice waits | open after D12, "Do not remember" |
| A2 | He wants to change firmware with his own hands on a page, and telling Claude is not enough | value | H, against it E ★C11. E against it: D3 | — (retired by D3) | account question Q3 | he names at least one moment when he wanted to type a value himself and telling Claude was not enough, set 2026-11-26 | no moment: D-q2 (a), the sentence for the chat | retired 2026-11-26, Results row 1 |
| A3 | After a deploy his open question is what the board runs, and a read-back on the page answers it | value | H from E ★C12 (10 of 28 ended "ready unknown"). Rival: in 9 of 10 spark could not read the files, and the cause may be the firmware or the port (★C12, one project) | high D10 | account question SQ13 | he names how he found out what the board ran, and that the page was not where he looked, set 2026-11-26 | he found it at once in the terminal: D-q1 (b) waits | open |
| A4 | The deploy's friction is the words and the copying, not the terminal itself | usability | H from E: the store's bench-2026-11-25 notes (UX-4) | high D10 | account question SQ14, queued before P1242 #1799 is ordered | he picks "a short line that copies whole" over "a button", set 2026-11-26 | he picks the button: D-q3 (b) stays a candidate | retired 2026-11-26, Results row 3: missed |
| A5 | A person who saves an edit understands that the board still runs the old image | usability | H, E for the mechanism (project_image.py:121-125) | low D10 | a paper sketch of the fold's "what comes next" line, read by him | he says what comes next without help, set 2026-11-26 | he does not: the fold needs the line before any edit | open |
| A6 | The Artifact in a browser cannot open a serial port | feasibility | E ★C1 for the attribute and the standard, H for the result | low D10 | the one-button test page of research.md, section 8, no board | requestPort() rejects with SecurityError, set 2026-11-26 | it opens a chooser: the host table changes | open |
| A7 | The desktop-app host can run spark's Python for his own artifact, and he uses that host | feasibility | H from E ★C2, not run. His use: — | low D10 | account question SQ7, then the desk spike on P494 #674 | childProcess runs `flow.py show` after one Allow, set 2026-11-26 | it fails, or he does not use the app: no desktop column | open |
| A8 | A yes on a page can be made by Claude, so it must stay relayed | ethics | E ★C9, ★C10 | low D10 | the desk spike for the app's own pty | the app's pty passes isatty and the page can write to it, set 2026-11-26 | it does not pass: the hole is Python's pty only | open |
| A9 | Firmware text and an image can carry a secret that no mask covers | ethics | E ★C13, H for a published literal | high D10 | a page from a scratch project with a fake literal in main.py, once the fold exists | the literal shows unmasked, set 2026-11-26 | it is masked: the rule needs no change | open |
| A10 | The Artifact host stays stable enough to carry a host-specific feature | viability | H from E: the contract moved twice in six days (P1038 brief.md:47) | low D10 | read the contract version at each republish for two weeks | at most one change in two weeks, set 2026-11-26 | more: host-specific features wait | open |

## Collection plan
<!-- One row per gap. e.g. `| Do assignees open new tasks? | Q2 | Lena, from analytics | one query | this week |` -->
| question | decision it blocks | who can answer | how | when |
| --- | --- | --- | --- | --- |
| Which files did "the generated code" mean? <!-- REQUIRED:collection --> | D-q1, D-q2 | the PO | Q2, through spark-main | answered D2 |
| Did he want to change a firmware value himself? | D-q2, A2 | the PO | Q3, an account question | answered D3 |
| May a deploy start from the page? | D-q3 | the PO | Q4 | answered D4 |
| When does it reach code? | D-q5 | the PO | Q5 | answered D5 |
| Does he read the firmware on the page once it is there (A1)? | none now, D14 accepted the risk | the PO | a use log of the page after P1242 #1799 ships | after P1242 #1799 |

## Results
<!-- Filled on a return; may stay empty until then. One row per result: what was tested, what was seen (verbatim,
with its pointer), the pass line met or missed, what it changes. -->
| date | source and pointer | what was seen | pass line met or missed | what it changes |
| --- | --- | --- | --- | --- |
| 2026-11-26 | Q3, an account question to the PO through spark-main, brief.md D3 | "Telling Claude was enough." He named no moment when he wanted to type a value himself | missed: the proposed pass line asked for one moment | D-q2 (a): a sentence for the chat. The edit on the page stays a named seam, not built (D5) |
| 2026-11-26 | SQ21, an account question to the PO through spark-main, brief.md D12 | "Do not remember" | neither met nor missed | A1 stays H and open. P1242 #1799 keeps its order: after the MVP walk and P1004 |
| 2026-11-26 | SQ14, an account question to the PO through spark-main, brief.md D13 | "A button on a page" | missed: the pass line asked for "a short line that copies whole" | the deploy step on the page carries its line with a Copy button (D4). A button that starts a deploy is not reopened, and waits on the PO |

## Budgets <!-- REQUIRED:electronics-firmware:budgets -->
<!-- Energy per mode · peaks per rail against the source · dissipation per part, each number with its provenance and
the rung that would settle it (electronics-firmware:R<n>). "n/a — no battery, motor, radio or regulator" is allowed. -->
n/a: no battery, motor, radio or regulator changes. The epic changes how the firmware reaches the board, not the board
<!-- EXTEND:risks-sections -->
