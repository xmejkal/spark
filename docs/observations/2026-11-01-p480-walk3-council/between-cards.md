# P480 between-cards council: plan.md against the open cards and the refactor plans

> The plan holds, with six changes: P468 (#636) needs a board fact the FireBeetle record lacks, P476 (#652) and P478 (#656) move behind W4-2, N8 joins P469 (#637), N9 joins P466 (#634), P399 (#515) enters the order after N3, and `carried_by` becomes `onboard`.
> Top of Ready: N4, N6, N2, N1, P468, N3, P469 with N8, P473. Names: three need a change (`carried_by`, N7's `effects`, "bench record"). One council agent in four roles on Sonnet 5.5.

I read plan.md, refuter.md, the 41 cards the order touches, `wave4-plan.md`, `refactor-plan.md`, P479 (#657) and the naming table.
The board columns (Ready, Build) are not readable from `gh issue list`, so Ready is taken from plan.md and the card comments.

## PO's assistant

- The order serves the PO's words. "Reenable simulation" is N3 plus P399. "Know what works" is N4. "Automate the buttons" is P469, and the plan puts it ninth.
- Move P469 up to rank 7. The PO said on 2026-10-31 that a person pressing buttons must end (#643). P413 only guards minutes.
- P399 is in N3's Done-when but not in the order. Add it after N3.
- Waits on the PO: the OK on N1 to N8, the board-only `built` question (AT151), the P409 (#535) merge with C1's question 3.

## Tech lead

- W4-1 (P475 #651) is merged, so N8 and N5 meet no seam work. W4-2 splits `deploy_envelope` (`board_envelope.py:74-125`) and keeps the goldens byte-equal (`wave4-plan.md:88`).
- P476 changes deploy's printed lines, so it cannot land before W4-2 without 34 retargeted mutation rows twice. P478 (#656) already waits on W4-2.
- P473 adds an `env` to `NextStep`, a core Value. It lands before W4-2, and W4-2 builds its `next` items on it.
- N1 touches `check_spine.py:705,985`. N3 touches the same file. Order N1 then N3, as the plan says.

## Senior developer

- N3 reads `boards.onboard_entries` (7 uses today). It writes no second reader of `pin_roles`. P332 (#426) already made `pin_roles` the one source.
- P468's cause: the warning at `check_spine.py:606` tests `serial_wired(diagram)`, not a board fact. `boards/xiao-esp32-c6.json:181` has a `usb` key. The FireBeetle record has none (grep). The card needs that fact first.
- N7 meets two vocabularies for `effects`. `parts.py` uses strings (`writes`, `network`, `deletes`, `parts.py:1537`). The core uses `READS RUNS BOARD DELETES WRITES` (`operation.py:17`). N7 declares the place as a second field and keeps both word sets.
- N2 and the FireBeetle's `wokwi_is_stand_in` note (P409 #535 comment) are the same worked example. N2's PR cites that comment.

## AI and UX reviewer

- N4's line must read "no must line tested" from the log's step counts. Claude then reports no more than the log shows.
- N6 is the cheapest fix for Claude, which read wrong pages in walk 3. Keep it second.
- N8's `board_read: true` must say which look read the board. After P469 there are two looks (mpremote, esptool), and the person's next step differs for each.
- The built-in LED and button in the diagram need names a person recognises. Take them from the record's role labels, not from the id.

## 1. Existing cards that walk 3 proved wrong, stale or covered

| card | change | exact new text |
|---|---|---|
| P468 #636 | cause refuted (refuter 8) | Title: "the 'no serial monitor' warning fires for boards that print over USB → it reads a board fact". Body: "Walk 3 heard `ready` with no wires (log line 40). The warning at `check_spine.py:606` tests the diagram, not the board. Outcome: the warning reads the record's `usb` fact (the XIAO has it at `boards/xiao-esp32-c6.json:181`). The FireBeetle record gets the fact from its maker page, cited. Done when: walk 3's build prints no serial warning, and a board with no USB console keeps it." Drop "every diagram wires $serialMonitor". |
| P469 #637 | P472 finding, N8 joins | Add: "There are two looks. mpremote on the running MicroPython does not restart the board. esptool `flash-id` restarts it for certain (about 6 s). The look uses mpremote first and esptool only when mpremote cannot reach the board. Entering download mode with no hands is `machine.bootloader()` through mpremote, then esptool `--before no-reset` (#643, PR #645). Slice 2 is N8: `board_read`, `NO_REQUIREMENTS`, a full `next`. Done when: on the bench a running program keeps running through a look, and the look says which look read the board." Needs its plan first. |
| P473 #647 | keep, one line | Add: "Done when also: `NextStep` in `core/` carries `env`, and W4-2 builds its `next` items on it." |
| P476 #652 | moves behind W4-2 | Add: "Waits for W4-2 (deploy on the core). The why is a field of the event P479 (#657) plans, so deploy's bytes change once. Until then a why line is a row." Out of Ready's top. |
| P478 #656 | already waits | No change. |
| P465 #633 | G16, G19 stay here | Add: "G19: the look's `next` after a flash carries 'press RESET once' (`board_doctor.py:46-47` has the words)." |
| P466 #634 | N9 joins, G15 | Add: "Slice 2 is N9: the look reads a board before init and shows the chip, MAC and store record. G15 (a MAC names its unit) is slice 1." |
| P406 #531 | G12 | Add to Done-when: "`does` words are not doubled in the offer." |
| P399 #515 | N3 depends on it | Add: "N3 gives the diagram `led` and `button` ids from the record. A test presses one and reads the other." |
| P332 #426 | partly done by N3 | Add: "N3 draws the parts. This card keeps the assigner side." |
| P467 #635 | stays | N3 does not cover `--match` ranking. |
| P413 #539, P410 #536 | stay | Walk 3 confirms both (refuter 17). |
| P409 #535 | overlap with C1 | The PO decides at filing: C1's question 3 becomes a section of P409's finding, or C1 links P409. Not closed. |

No card closes as covered. P643 (P472) is already done.

## 2. Duplicates and overlaps among N1 to N11

| pair | verdict |
|---|---|
| N8 and P469 | merge into one plan. Both change the look's reading and its `next`. N8 is slice 2. |
| N9 and P466 | merge as P466's slice 2. Both read a board with no project. |
| N2 and P468 | keep two cards. Both edit `boards/firebeetle2-esp32s3.json`, so one PR if they land together. |
| N3 and P332, P399, P467 | N3 stays. See the table above. P467 is a different code path. |
| N5 and N6 | no overlap. N6 fixes the page text, N5 fixes the behaviour. |
| N6 and N7 | N7 replaces N6's effect sentences with a read of the declaration. |
| N11 and P446 (#597, part shapes) | N11 waits for P446's shape work and N3. The sheet needs a shape for the carried part. |
| N3 positions and P450 (#602, FireBeetle physical facts) | N3 draws parts without positions. P450 adds them later. No merge. |
| N10 and P465 (#633) | no overlap. P465 diagnoses a board. N10 writes a result. |

## 3. Fit with the refactor plans

- `wave4-plan.md`: W4-2 (line 86) builds `OutsideWorld.report(event)` in place of `show_line`, from P479. Add one line under W4-2: "P476's why is a field of the event. P473's `env` is on `NextStep` before this PR." Add N10 (bench result) to the risks: it writes through deploy's gate, so it follows W4-2.
- N7 changes `core/operation.py:17` only if the place becomes a core field. Add to `refactor-plan.md` section 4: "`effects` keeps `READS RUNS BOARD DELETES WRITES`. N7 adds `where`, a place (`store` or `project`) and a file per effect."
- N3: add a row to the refactor plan's record table (line 354). `OnboardParts` lives in `records/board_records.py` beside `onboard_entries`. It is a reader and writes nothing.
- N8: `board_envelope.look_step` becomes a `NextStep` (`refactor-plan.md:626`). N8's full `next` rides that conversion. No wave change.
- N1, N2, N4, N5, N6 touch scripts that wave 4 does not name (refuter 18). No plan change.
- P479 (#657) waits until after walk 3. Neither N card needs it, except N10 and P476.

## 4. Names

| name | table or code | verdict |
|---|---|---|
| `carried_by` | code says `onboard_entries`, `OnboardRole`, `onboard_led` (grep). `carried` means nothing in this sense | change to `onboard`, a part field holding the board id. One word for one thing. |
| `BoardParts` | a board is also a part (BOM), so "board parts" is unclear | change to `OnboardParts`. A reader, a plain noun. |
| `effects` | exists, two word sets (see Senior) | keep the word. N7 adds `where`. Do not add `writes`. |
| `board_read` | `BoardReader`, `BoardReading` exist | keep. It is a bool on the look: the board answered chip, flash and MAC. Docstring says so. |
| `NO_REQUIREMENTS` | pattern `NO_SIM_TOML` (file missing). `NO_BOARD_NAMED` stays for a file with no `board` key | keep. The look-with-no-project flag is `no_project`, never `board_only`. |
| N5 "resolver" | the table has no Resolver. `PortFinder` exists, `RecordFinder` is planned (P392) | call it `ProjectFinder`. |
| N10 "bench record" | "record" means a store JSON file (glossary) | call it "bench result". |
| N4 "verdict line" | `verdict` is a field of the look and the run | keep. |

## 5. Order and the top of Ready

Each card below leaves something working and has a test in its Done-when. N3 is M and splits into two PRs: the reader and the diagram.

| rank | card | reason against P100 #6 |
|---|---|---|
| 1 | N4, the verdict names no must line tested | XS. A pass then says what it proved. |
| 2 | N6, six page fixes | XS docs. Claude gave wrong steps from these pages. |
| 3 | N2, the stand-in's definition | XS data. N3 and every board-only limit need it. |
| 4 | N1, the diagram bug | S. A build destroys the person's work now. |
| 5 | P468 rewritten | XS. The false warning sends Claude after wires. Needs the FireBeetle's `usb` fact. |
| 6 | N3, the board's own LED and button | M. Simulation tests both must lines. |
| 7 | P469 with N8, the look without a restart | The PO's open pain (#643). Needs its plan and two councils. |
| 8 | P473, `next` carries the store | XS. Every interface that follows `next` needs it before W4-2. |

After rank 8: P399 (right after N3 if the PO prefers a free run first), P413, N5, N7, then P476 behind W4-2. After the MVP: C1, N9 with P466, N10, N11.

## Not checked

The board's column of each card. The bodies of P399's later comments past the first five. Whether the FireBeetle maker page states a USB console (P468's fact).
