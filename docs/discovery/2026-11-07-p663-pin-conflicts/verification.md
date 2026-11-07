# Verification
<!-- One line per ★ claim in brief.md; rejected claims stay. refuter: holds · partly · refuted · could not open, with
the line it read, verbatim. result: reproduced · not reproduced · rejected. keep: the words any summary of the claim
must carry (phrases separated by ;), or none; keep comes last on the line.
e.g. `- ★C3 · STATUS.md:84 · refuter: partly — "Shown on the C6, assumed for the S3" · reproduced how: re-read STATUS.md:84 · result: reproduced · keep: assumed for the S3` -->
- ★C1 · scripts/assign_pins.py:283-284, :70-71 · refuter: partly — "K5's sentence names one claimant and no choice; K2's names two ways out, both wrong for a cable (F5)" · reproduced how: re-read the facilitator's cited lines on 2026-11-07 · result: reproduced · keep: two ways out
- ★C2 · scripts/assign_pins.py:538-540, :557-562 · refuter: holds — "print("cannot place every signal on this board:\n\n  %s" % refused); return EXIT_IMPOSSIBLE" · reproduced how: refuter run with a named strap and --json, plain sentence, exit 1 · result: reproduced · keep: none
- ★C3 · scripts/check_spine.py:408-410 · refuter: holds as quoted, but agents.md:131 is about a crash — "assign_pins.py:531 does return EXIT_COULD_NOT_RUN for a design it cannot load" · reproduced how: the facilitator re-read assign_pins.py:529-531 and :538-540, emit_board.py:1089-1093, check_spine.py:408-410 on 2026-11-07 · result: reproduced · keep: none
- ★C4 · ~/Development/spark-walks/p581-sound-joystick/requirements.json · refuter: holds — "15 signal(s) placed", "I2S_BCLK D6 GPIO18", "JOY_SW D7 GPIO9", "TFT_BL D3 GPIO38", exit 0 · reproduced how: the facilitator reran assign_pins.py --project on the walk folder with the walk's file, signals removed, on 2026-11-07 · result: reproduced · keep: walk's own file; GPIO38
- ★C5 · tests/data/parts/dfr0664-tft-2in.json:245-257, :268 · refuter: holds for placement — "A grep of scripts/*.py for gdi_on_firebeetle2 finds no line" · reproduced how: not re-read by the facilitator, the refuter's verdict stands · result: not reproduced by the facilitator, holds by the refuter · keep: verified: false
- ★C6 · boards/firebeetle2-esp32s3.json · refuter: holds — "printed 0" for connector or gdi, #628 OPEN · reproduced how: the facilitator re-ran the grep on 2026-11-07 · result: reproduced · keep: #628
- ★C7 · scripts/assign_pins.py:357-360, :290-292 · refuter: partly — "the shared job (onboard_led) is named in TFT_BL's comment; the other signal name (ONBOARD_LED) is not" · reproduced how: the refuter re-read the walk's firmware/pins.py:9 · result: reproduced · keep: second signal
- ★C8 · scripts/spark/core/result.py:15, :18 · refuter: holds — "Finding = namedtuple("Finding", "severity subject code sentence fix")" · reproduced how: the facilitator re-read result.py and outcomes.py:113-119 on 2026-11-07 · result: reproduced · keep: two claims
- ★C9 · refactor-plan.md:560-569 · refuter: holds — "The order of the areas is firmware, breadboard, checks, design with build, records with sourcing." · reproduced how: the refuter grepped lines 555-600 for a date and found none · result: reproduced · keep: no date
- ★C10 · reading of D2 · refuter: holds as an H — "H by construction (a reading of D2)" · reproduced how: not applicable, a reading · result: reproduced as an H · keep: (Q2)
- ★C11 · ESP32-S3 datasheet v2.2 Table 3-1 p.32, Table 3-3 p.33, §3.4 p.34, Table 3-5 p.35 · refuter: holds, with two notes — "the strapping value must be controlled by the external circuit that cannot be in a high impedance state" · reproduced how: the refuter read the stored datasheet · result: reproduced · keep: default chip
- ★C12 · ESP32-S3 datasheet Table 5-4 p.65 · refuter: partly — "the 40 mA and its conditions hold; R15 2K and R3 1K were not re-read" · reproduced how: the refuter read p.65 · result: reproduced for IOH, not reproduced for R15 and R3 · keep: Vbe
- ★C13 · scripts/breadboard.py:330, GLOSSARY.md:75, :80 · refuter: holds — "**CONFLICT** on %s: %s" · reproduced how: the refuter re-read the lines · result: reproduced · keep: pull-up
- ★C14 · scripts/needs.py:659-660 · refuter: holds — "What is there stays, unchanged and in its order" · reproduced how: the refuter re-read the lines (659-660, not 660) · result: reproduced · keep: validates only
- ★C15 · esphome/pins.py, LICENSE · refuter: holds — "if all(e[2].get(CONF_ALLOW_OTHER_USES, False) for e in others):" · reproduced how: the refuter fetched both files on 2026-11-07 · result: reproduced · keep: ERC
- ★C16 · P581 row 7, issue 886 · refuter: holds — "After a pin map change the kept board.tsx still holds the old pins" · reproduced how: the refuter read row 7 and gh issue list · result: reproduced · keep: #886
- ★C17 · P581 row 1, W4:30 · refuter: holds, pointer wrong — "the person ... pasted the end of the output: 'Nice!' and 'It works'" · reproduced how: the refuter read W4:27, :28, :30 · result: reproduced · keep: W4:30 <!-- REQUIRED:claims -->

## Agree / split
<!-- Where the lenses and the refuter agree, and where they split; each split becomes a question.
e.g. `- Split: Feasibility says a day, Risks says a week · Q4` -->
- Agree: the lenses and the refuter agree on ★C2, ★C6, ★C8, ★C9, ★C13, ★C14, ★C15, ★C16 as the brief states them.
- Agree: three cable pins are taken, not two. The refuter and the facilitator reproduced TFT_BL on GPIO38 (★C4).
- Agree: the exit-code split is the same Impossible refusal, and agents.md:131 is not contradicted (★C3, F1).
- Split: Physics (PH-5, PH-15) says K3 is bookkeeping with no answer, and the first brief made it a stop. Resolved in the files: K3 is a note, never a stop. D6 answers the first half of Q10 (K3 is a note). The severity per kind stays for the plan council.
- Split: the brief says K2 is bookkeeping unless the eFuse is burned, and Physics (PH-1, PH-2) with datasheet §3.4 says a defined level is still asked for. Weakened in ★C11 · Q12
- Split: the Feasibility lens used ~/Development/firebeetle-games and the refuter used the walk's own file. Same result, so no question.
- Split: the lenses did not name P281 #323 for F2, and RI-15 did. P672 is narrowed and the choice "add to #323" is in Q6.
- Split: the lenses hold the model is wanted, and the refuter's rival is a one-reader fix for K1 · Q17
- Split: D1 rests on one AskUserQuestion, and #892's own body states a cable default · Q13 (moved first)
- Split: EX-16 (ESPHome warns unless acknowledged) would weaken C4, and no question held it · Q18
- Split: A6's pass line does not cover the intended new stop on walk 4's unpinned project · Q19
- Open, not a split: the P581 build stops at 300 s (P664 #893), so the Outcome's proof depends on it. Added to the depends-on of P663 and P665. <!-- REQUIRED:agree-split -->
