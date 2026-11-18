# Risks and tests

## Risks
<!-- One row per type; an active extension adds its own rows. evidence now: tag and ids (★C<n>, A<n>).
status: open · retired · n/a because ….
e.g. `| usability | H no test yet (A2) | a five-person prototype test | open |` -->
| risk | evidence now | cheapest way to retire it | status |
| --- | --- | --- | --- |
| value <!-- REQUIRED:risk-value --> | H A2, A5. E ★C17: nobody is blocked today | the PO's account (Q2) and the desk read of A2 | open |
| usability <!-- REQUIRED:risk-usability --> | H A1, A4. E C20: the agreed lines were not used yet | a use log of step 2c on #1283 | open |
| feasibility <!-- REQUIRED:risk-feasibility --> | E ★C12, ★C13: the parts exist. H A3 | `mpremote devs` with the game box on USB | open |
| viability <!-- REQUIRED:risk-viability --> | H A6. E ★C7: pixel-games runs the plugin 0.4.0 | a question to the pixel-games session and the PO | open |
| ethics and safety <!-- REQUIRED:risk-ethics --> | E ★C15: a touch restarts a board and stops a running game. The view opens no port | keep the view free of any touch, proved by a test | open |
| power and battery <!-- REQUIRED:electronics-firmware:power --> | — | — | n/a because the item changes no circuit, load or power path |
| current and stall <!-- REQUIRED:electronics-firmware:stall --> | — | — | n/a because the item changes no circuit, load or power path |
| thermal <!-- REQUIRED:electronics-firmware:thermal --> | — | — | n/a because the item changes no circuit, load or power path |
| EMC and ESD <!-- REQUIRED:electronics-firmware:emc-esd --> | — | — | n/a because the item changes no circuit, load or power path |
| sensor drift and calibration <!-- REQUIRED:electronics-firmware:sensor-drift --> | — | — | n/a because the item reads no sensor |
| brown-out <!-- REQUIRED:electronics-firmware:brown-out --> | — | — | n/a because the item changes no circuit, load or power path |
| wake and low power <!-- REQUIRED:electronics-firmware:wake --> | — | — | n/a because the item changes no circuit, load or power path |
| the firmware–hardware contract <!-- REQUIRED:electronics-firmware:contract --> | E ★C15, read in the code (provenance: stated): which touch restarts the board | electronics-firmware:R6, one bench look per touch | open |
| supply and documents <!-- REQUIRED:electronics-firmware:supply --> | — | — | n/a because the item names no part |
<!-- EXTEND:risk-rows --><!-- EXTEND:pair-rows -->

## Assumptions
<!-- About ten at most. type: value, usability, feasibility, viability or ethics. importance: "— (decider)" until
the decider rates it, then "high D<n>" or "low D<n>". pass line: written, with its date, before any result.
status: open, or retired with the date of its Results row.
e.g. `| A2 | Assignees never see new tasks | value | H ★C2 | — (decider) | query opened-within-48h | under 50 %, set 2026-10-06 | over 80 % | open |` -->
| id | belief | type | evidence now | importance | cheapest test | pass line, dated | result that would change the decision | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 <!-- REQUIRED:assumptions --> | A tool reads the record before each touch | usability | H council/po-assistant.md RISK-3 | — (decider) | a use log of step 2c: the take and release lines on #1283 | proposed 2026-11-18: each take and each release has its line, and the PO sets the count at Q1 | a touch with no line before it | open |
| A2 | The records that exist hold enough to show who uses the game box | value | E ★C3, C4: today they do not | — (decider) | a desk read with the box on USB, no port opened | proposed 2026-11-18: the records name the project that used the box last | the view is empty for the box | open |
| A3 | The boards that the PO shares have a USB serial that names them with no touch | feasibility | H ★C12 | — (decider) | `mpremote devs` with each shared board on USB | proposed 2026-11-18: the serial equals the MAC in the store's `boards/` | "cannot tell" for the game box | open |
| A4 | An end time by the clock is close enough to the real use | usability | H C11, an estimate | — (decider) | compare the stated end with the release at step 2c | proposed 2026-11-18: the release comes before the stated end, and the PO sets the margin at Q1 | the use runs past the end | open |
| A5 | Two projects use one physical board by turns | value | E ★C24: five project names on one board in 17 days. H: whether two lanes shared it | — (decider) | Q2, the PO's account | proposed 2026-11-18: one dated case | no case, only step 2c | open |
| A6 | The pixel-games tool will call a spark command, so it registers | viability | H D4 | — (decider) | ask the pixel-games session and the PO | proposed 2026-11-18: a yes with the command it can call | `box.py` stays outside | open |

## Collection plan
<!-- One row per gap. e.g. `| Do assignees open new tasks? | Q2 | Lena, from analytics | one query | this week |` -->
| question | decision it blocks | who can answer | how | when |
| --- | --- | --- | --- | --- |
| Do two projects use one board by turns, and which? <!-- REQUIRED:collection --> | Q3, A5 | the PO | Q2, one question | in this discovery |
| What does `mpremote devs` list for the game box? | A2, A3 | this session, after the PO's yes and the pixel-games session's "free" | one command that opens no port | the PO's next bench time |
| Were the take and release lines written at step 2c? | A1, A4 | both sessions | the comments on #1283 | at step 2c of P904 |
| Do two Claude sessions get different values of `CLAUDE_CODE_SESSION_ID`? | Q4, ★C14 | both sessions | each prints the variable | after Q4 |
| Can `box.py` call a spark command with `--json`? | A6, Q6 | the pixel-games session and the PO | a message | after Q3 |

## Results
<!-- Filled on a return; may stay empty until then. One row per result: what was tested, what was seen (verbatim,
with its pointer), the pass line met or missed, what it changes. -->
| date | source and pointer | what was seen | pass line met or missed | what it changes |
| --- | --- | --- | --- | --- |

## Budgets <!-- REQUIRED:electronics-firmware:budgets -->
<!-- Energy per mode · peaks per rail against the source · dissipation per part, each number with its provenance and
the rung that would settle it (electronics-firmware:R<n>). "n/a — no battery, motor, radio or regulator" is allowed. -->
n/a — no battery, motor, radio or regulator
<!-- EXTEND:risks-sections -->
