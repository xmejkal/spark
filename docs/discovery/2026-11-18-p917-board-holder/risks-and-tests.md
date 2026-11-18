# Risks and tests

## Risks
<!-- One row per type; an active extension adds its own rows. evidence now: tag and ids (★C<n>, A<n>).
status: open · retired · n/a because ….
e.g. `| usability | H no test yet (A2) | a five-person prototype test | open |` -->
| risk | evidence now | cheapest way to retire it | status |
| --- | --- | --- | --- |
| value <!-- REQUIRED:risk-value --> | H A2, A5. E ★C17 (the agreement was never used): nobody is blocked today | the PO's account (Q2) and the desk read of A2 | open |
| usability <!-- REQUIRED:risk-usability --> | H A1, A4. E C20: the agreed lines were not used yet | a use log of step 2c on #1283 | open |
| feasibility <!-- REQUIRED:risk-feasibility --> | E ★C12 (some serials give cannot tell), ★C13 (one ended grant in one store): the parts exist. H A3 | `mpremote devs` with the game box on USB | open |
| viability <!-- REQUIRED:risk-viability --> | H A6. E ★C7 (an upgrade alone brings no gate): pixel-games runs the plugin 0.4.0 | a question to the pixel-games session and the PO | open |
| ethics and safety <!-- REQUIRED:risk-ethics --> | E ★C15 (read in the code, not measured): a touch restarts a board and stops a running game. The view opens no port | keep the view free of any touch, proved by a test | open |
| power and battery <!-- REQUIRED:electronics-firmware:power --> | — | — | n/a because the item changes no circuit, load or power path |
| current and stall <!-- REQUIRED:electronics-firmware:stall --> | — | — | n/a because the item changes no circuit, load or power path |
| thermal <!-- REQUIRED:electronics-firmware:thermal --> | — | — | n/a because the item changes no circuit, load or power path |
| EMC and ESD <!-- REQUIRED:electronics-firmware:emc-esd --> | — | — | n/a because the item changes no circuit, load or power path |
| sensor drift and calibration <!-- REQUIRED:electronics-firmware:sensor-drift --> | — | — | n/a because the item reads no sensor |
| brown-out <!-- REQUIRED:electronics-firmware:brown-out --> | — | — | n/a because the item changes no circuit, load or power path |
| wake and low power <!-- REQUIRED:electronics-firmware:wake --> | — | — | n/a because the item changes no circuit, load or power path |
| the firmware–hardware contract <!-- REQUIRED:electronics-firmware:contract --> | E ★C15 (read in the code, not measured), read in the code (provenance: stated): which touch restarts the board | electronics-firmware:R6, one bench look per touch | open |
| supply and documents <!-- REQUIRED:electronics-firmware:supply --> | — | — | n/a because the item names no part |
<!-- EXTEND:risk-rows --><!-- EXTEND:pair-rows -->

## Assumptions
<!-- About ten at most. type: value, usability, feasibility, viability or ethics. importance: "— (decider)" until
the decider rates it, then "high D<n>" or "low D<n>". pass line: written, with its date, before any result.
status: open, or retired with the date of its Results row.
e.g. `| A2 | Assignees never see new tasks | value | H ★C2 (a folder name) | — (decider) | query opened-within-48h | under 50 %, set 2026-10-06 | over 80 % | open |` -->
| id | belief | type | evidence now | importance | cheapest test | pass line, dated | result that would change the decision | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 <!-- REQUIRED:assumptions --> | A tool reads the record before each touch | usability | H council/po-assistant.md RISK-3 | high D5 | a use log of step 2c: the take and release lines on #1283 | set 2026-11-18 (D5): every take and every release has its line on #1283 | a touch with no line before it | open |
| A2 | The records that exist hold enough to show who uses the game box | value | E ★C3 (one store on one day), C4: today they do not | low D5 | a desk read with the box on USB, no port opened | proposed 2026-11-18: the records name the project that used the box last | the view is empty for the box | open |
| A3 | The boards that the PO shares have a USB serial that names them with no touch | feasibility | H ★C12 (some serials give cannot tell) | low D5 | `mpremote devs` with each shared board on USB | proposed 2026-11-18: the serial equals the MAC in the store's `boards/` | "cannot tell" for the game box | open |
| A4 | An end time by the clock is close enough to the real use | usability | H C11, an estimate | low D5 | compare the stated end with the release at step 2c | proposed 2026-11-18: the release comes before the stated end, and the PO sets the margin at Q1 | the use runs past the end | open |
| A5 | Two projects use one physical board by turns | value | E ★C24 (only the PO knows whether it is the game box): five project names on one board in 17 days. E D6: it is the game box | high D5 | Q2, the PO's account | proposed 2026-11-18: one dated case | no case, only step 2c | retired 2026-11-18 |
| A6 | The pixel-games tool will call a spark command, so it registers | viability | H D4 | high D5 | ask the pixel-games session and the PO | set 2026-11-18 (D5): a yes that names the command and a card in pixel-games | `box.py` stays outside | retired 2026-11-18 |

## Collection plan
<!-- One row per gap. e.g. `| Do assignees open new tasks? | Q2 | Lena, from analytics | one query | this week |` -->
| question | decision it blocks | who can answer | how | when |
| --- | --- | --- | --- | --- |
| Do two projects use one board by turns, and which? <!-- REQUIRED:collection --> | Q3, A5 | the PO | Q2, one question | answered 2026-11-18 (D6) |
| What does `mpremote devs` list for the game box? | A2, A3 | this session, after the PO's yes and the pixel-games session's "free" | one command that opens no port | the PO's next bench time |
| Were the take and release lines written at step 2c? | A1, A4 | both sessions | the comments on #1283 | at step 2c of P904 |
| Do two Claude sessions get different values of `CLAUDE_CODE_SESSION_ID`? | Q4, ★C14 (session ids not compared) | both sessions | each prints the variable | after Q4 |
| Can `box.py` call a spark command with `--json`? | A6, Q6 | the pixel-games session and the PO | a message | answered 2026-11-18 (C25). The card in pixel-games is P921 #1303 (D11) |

## Results
<!-- Filled on a return; may stay empty until then. One row per result: what was tested, what was seen (verbatim,
with its pointer), the pass line met or missed, what it changes. -->
| date | source and pointer | what was seen | pass line met or missed | what it changes |
| --- | --- | --- | --- | --- |
| 2026-11-18 | the PO's answer to Q2 (D6 in brief.md) and the store's `boards/34-85-18-xx-xx-xx.json` | "Yes, the same board": the board with 14 deploys from five spark folders, 2026-11-01 to 2026-11-17, is the game box of pixel-games | A5's pass line met: one dated case | A5 is retired. A holder record has a user beyond step 2c |
| 2026-11-18 | the pixel-games session's second message, pixel-games-account.md:34 | "yes, box.py can call one spark command before and after a deploy, but today nothing tells it where that command is" | A6's pass line met in part: the yes names a command as a contract, and the card in pixel-games does not exist | A6 stays open until that card exists. The PO ordered it (D11). The design has to give the command one stable path |
| 2026-11-18 | the card P921 (https://github.com/xmejkal/spark/issues/1303), filed on the PO's order (D11) | the card exists: a spark card with the slice pixel-games | A6's pass line met: the yes names the command (the row above), and the card exists | A6 is retired. P921's own proof shows whether `box.py` then reports a deploy |

## Budgets <!-- REQUIRED:electronics-firmware:budgets -->
<!-- Energy per mode · peaks per rail against the source · dissipation per part, each number with its provenance and
the rung that would settle it (electronics-firmware:R<n>). "n/a — no battery, motor, radio or regulator" is allowed. -->
n/a — no battery, motor, radio or regulator
<!-- EXTEND:risks-sections -->
