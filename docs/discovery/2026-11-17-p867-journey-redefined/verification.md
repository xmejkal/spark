# Verification
<!-- One line per ★ claim in brief.md; rejected claims stay. refuter: holds · partly · refuted · could not open, with
the line it read, verbatim. result: reproduced · not reproduced · rejected. keep: the words any summary of the claim
must carry (phrases separated by ;), or none; keep comes last on the line.
e.g. `- ★C3 · STATUS.md:84 · refuter: partly — "Shown on the C6, assumed for the S3" · reproduced how: re-read STATUS.md:84 · result: reproduced · keep: assumed for the S3` -->
- ★C1 · the facilitator's run of `flow.py show` on spark-walks/p711-sound-demo · refuter: partly — "one hop" (council/existing.md:11); the case is a hand-written file · reproduced how: ran the command 2026-11-17, read "↻ requirements" above "✓ build" and "✓ breadboard"; re-read phase_readers.py:172-217 · result: reproduced · keep: one project <!-- REQUIRED:claims -->
- ★C2 · scripts/spark/flow/phase_readers.py:219-265 · refuter: holds · reproduced how: re-read the three readers 2026-11-17 · result: reproduced · keep: reads no record
- ★C3 · council/architecture.md:27 · refuter: partly — the file-time mechanism could not open · reproduced how: re-read three of the four mechanisms (requirements, build, breadboard); the file-time one read in SimulateReader's call only · result: reproduced in part · keep: read by the lens
- ★C4 · the facilitator's run of `assign_pins.py --json` · refuter: holds, and its caveat was too narrow · reproduced how: 7 runs on scratch copies of two walk projects, 2026-11-17: a second joystick 2 of 15, an I2C part 6 of 15 and 3 of 4, an SPI display 4 of 4, a button 0 of 15 and 0 of 4; the refuter ran the same counts apart · result: reproduced; the feasibility lens's "4 moved" not reproduced · keep: simulated; one board model
- ★C5 · council/feasibility.md:43, :48 · refuter: partly — the sheet's Changes section does compare · reproduced how: not re-read · result: not reproduced · keep: not run
- ★C6 · spark-walks/p711-sound-demo/firmware/main.py:21 · refuter: holds for the state; the harm stays not measured · reproduced how: read the line 2026-11-17 (`shutdown = Pin(pins.AUDIO_SHUTDOWN, Pin.OUT, value=1)`); the new pin map from ★C4's run · result: reproduced for the state; the harm is unknown · keep: not measured
- ★C7 · scripts/spark/build/kept_files.py:301-308, :319-327 · refuter: holds; its caveat partly · reproduced how: re-read 2026-11-17 · result: reproduced · keep: by design
- ★C8 · council/feasibility.md:38, :40; kept_files.py:316-321 · refuter: partly — need_requirements.py could not open · reproduced how: re-read the pins.py check only · result: reproduced in part · keep: read by the lens
- ★C9 · council/architecture.md:84 · refuter: partly — the two records' readers could not open · reproduced how: the deploy reader's constant re-read (★C2); the two records not opened · result: reproduced in part · keep: never what is on the bench
- ★C10 · the facilitator's run on spark-walks/p711-walk4-button-led · refuter: holds · reproduced how: ran the command 2026-11-17 and read the build line · result: reproduced · keep: a board-only project
- ★C11 · scripts/spark/flow/flow_codes.py:9; council/architecture.md:11 · refuter: partly — the lenses count five and three · reproduced how: the nine phases read; the other vocabularies not re-read · result: reproduced in part · keep: at least four
- ★C12 · council/feasibility.md:28-32 · refuter: partly — the PCB has data in part · reproduced how: not re-counted · result: not reproduced · keep: counted by the lens
- ★C13 · council/architecture.md:59; scripts/spark/flow/phase_readers.py:37 · refuter: partly — the key `next` exists, as an empty list · reproduced how: printed the JSON's keys 2026-11-17: `next = []`; the Offer value read · result: reproduced after the wording changed · keep: a contract
- ★C14 · council/architecture.md:107, :138, :211 · refuter: holds as proposals; a caveat was dropped · reproduced how: read the three candidates in full 2026-11-17 · result: reproduced as a proposal · keep: the lens's proposals
- ★C15 · council/architecture.md:303-323 · refuter: partly — the lenses split · reproduced how: not re-read against the cards · result: not reproduced · keep: the lenses split
- ★C16 · the board's status line of 2026-11-17; council/risks.md:10-11 · refuter: refuted as worded — "The one person blocked is the PO at the bench" · reproduced how: read council/risks.md:10 in full 2026-11-17, with its last sentence; read `tools/board.py status` · result: rejected as first worded; reproduced as reworded · keep: no card is blocked
- ★C17 · #1234; mvp-plan.md's Decisions · refuter: holds · reproduced how: read both texts 2026-11-17 · result: reproduced · keep: his list is a question
- ★C18 · council/user.md:13, :85; p711-sound-demo/rows.md row 10 · refuter: partly — a diary reading by one lens · reproduced how: row 10 read; "Claude typed every command" not re-checked · result: reproduced in part · keep: n = 1
- ★C19 · council/existing.md:45-50 · refuter: partly for Bazel and GOV.UK; could not open the other three · reproduced how: not re-read · result: not reproduced · keep: licences were not read
- ★C29 · spark-walks/p711-*/rows.md; council/refuter.md:9-16 · refuter: its own finding (R-0a) · reproduced how: the three rows files read once by the facilitator at the start of the session; no row about a wrong tick recalled, not counted again · result: reproduced in part · keep: counted by the refuter
- ★C30 · spark-walks/p711-sound-demo/rows.md row 12; council/refuter.md:17-26 · refuter: its own finding (R-0b) · reproduced how: read row 12 and the folder's requirements.json 2026-11-17 (display, amplifier, joystick, speaker terminal); `flow.py show` names four needs (board, amp, speaker, volume) · result: reproduced · keep: a hand-written file
- ★C31 · council/live.md:224, :11-75 · refuter: pending (second pass) · reproduced how: read the lens's proposals (council/live.md:222-256) and its not-checked list 2026-11-17; the cards, the code and the pages not re-read by the facilitator · result: not reproduced · keep: not tested

## Agree / split
<!-- Where the lenses and the refuter agree, and where they split; each split becomes a question.
e.g. `- Split: Feasibility says a day, Risks says a week · Q4` -->
- Agree: four lenses (existing, user, UX, architecture) and the facilitator's run on ★C1; existing, risks and architecture on ★C2; feasibility and physics on the direction of ★C4 <!-- REQUIRED:agree-split -->
- Split: feasibility counts 4 moved signals, physics 2 of 15 · settled by the facilitator's run: 2 of 15, and feasibility's base did not match the kept pins.py
- Split: physics says "another joystick" cannot be written in requirements.json (PH-1); feasibility wrote it as a named copy · settled by the facilitator's run: the bare id twice is refused, a named copy works
- Split: the page notes name "the catalog's why_not" as a place spark reads; feasibility says no · settled by a search: only the research command's prose names it, and no script reads it
- Split: the PO's list has the shops early, D10 has them after the MVP · Q9
- Split: architecture's candidate 3 against "facts, never behaviour" · Q13
- Split: P280's rule (a refused build leaves no output of the old design) against going back with nothing deleted · Q2
- Split: the facilitator's first opinion (the dependency graph, with A1 as the riskiest) against the refuter (the walks' pain is hand work in commands; A1's test could hardly fail) · the brief's opinion, riskiest assumption and test changed; Q5 and Q1
- Split: the architecture lens (P829 exposed) against the risks lens (P827 high, P829 low) · Q8
- Split: the facilitator's opinion on the witnesses against walk 2's row 6, where a record was read as the state · Q4
- Not checked by the refuter (never "holds"): the Terraform, LangGraph and KiCad pages, the datasheet page, need_requirements.py, project_image.py, the two witness-record readers, the three diaries in full, P820's brief.md
