# Verification
<!-- One line per ★ claim in brief.md; rejected claims stay. refuter: holds · partly · refuted · could not open, with
the line it read, verbatim. result: reproduced · not reproduced · rejected. keep: the words any summary of the claim
must carry (phrases separated by ;), or none; keep comes last on the line.
e.g. `- ★C3 · STATUS.md:84 · refuter: partly — "Shown on the C6, assumed for the S3" · reproduced how: re-read STATUS.md:84 · result: reproduced · keep: assumed for the S3` -->
- ★C1 · the facilitator's run of `flow.py show` on spark-walks/p711-sound-demo · refuter: pending · reproduced how: ran the command 2026-11-17, read "↻ requirements" above "✓ build" and "✓ breadboard"; re-read phase_readers.py:172-217 · result: reproduced · keep: one project <!-- REQUIRED:claims -->
- ★C2 · scripts/spark/flow/phase_readers.py:219-265 · refuter: pending · reproduced how: re-read the three readers 2026-11-17 · result: reproduced · keep: reads no record
- ★C3 · council/architecture.md:27 · refuter: pending · reproduced how: re-read three of the four mechanisms (requirements, build, breadboard); the file-time one read in SimulateReader's call only · result: reproduced in part · keep: read by the lens
- ★C4 · the facilitator's run of `assign_pins.py --json` · refuter: pending · reproduced how: base and a named second joystick on scratch copies, 2026-11-17: base equals the kept pins.py on 15 of 15 signals, 2 of 15 moved · result: reproduced (the physics lens's count); the feasibility lens's "4 moved" not reproduced · keep: simulated; one project
- ★C5 · council/feasibility.md:43, :48 · refuter: pending · reproduced how: not re-read · result: not reproduced · keep: not run
- ★C6 · spark-walks/p711-sound-demo/firmware/main.py:21 · refuter: pending · reproduced how: read the line 2026-11-17 (`shutdown = Pin(pins.AUDIO_SHUTDOWN, Pin.OUT, value=1)`); the new pin map from ★C4's run · result: reproduced for the state; the harm is unknown · keep: not measured
- ★C7 · scripts/spark/build/kept_files.py:301-308, :319-327 · refuter: pending · reproduced how: re-read 2026-11-17 · result: reproduced · keep: by design
- ★C8 · council/feasibility.md:38, :40; kept_files.py:316-321 · refuter: pending · reproduced how: re-read the pins.py check only · result: reproduced in part · keep: read by the lens
- ★C9 · council/architecture.md:84 · refuter: pending · reproduced how: the deploy reader's constant re-read (★C2); the two records not opened · result: reproduced in part · keep: never what is on the bench
- ★C10 · the facilitator's run on spark-walks/p711-walk4-button-led · refuter: pending · reproduced how: ran the command 2026-11-17 and read the build line · result: reproduced · keep: a board-only project
- ★C11 · scripts/spark/flow/flow_codes.py:9; council/architecture.md:11 · refuter: pending · reproduced how: the nine phases read; the other vocabularies not re-read · result: reproduced in part · keep: at least four
- ★C12 · council/feasibility.md:28-32 · refuter: pending · reproduced how: not re-counted · result: not reproduced · keep: counted by the lens
- ★C13 · council/architecture.md:59; scripts/spark/flow/phase_readers.py:37 · refuter: pending · reproduced how: the Offer value read (`key effect`); the flow's JSON not printed by the facilitator · result: reproduced in part · keep: a contract
- ★C14 · council/architecture.md:107, :138, :211 · refuter: pending · reproduced how: read the three candidates in full 2026-11-17 · result: reproduced as a proposal · keep: the lens's proposals
- ★C15 · council/architecture.md:303-323 · refuter: pending · reproduced how: not re-read against the cards · result: not reproduced · keep: the lens's reading
- ★C16 · the board's status line of 2026-11-17; council/risks.md:10-11 · refuter: pending · reproduced how: read `tools/board.py status`: Ready holds P711, P827, P828, P829, P851 · result: reproduced · keep: rework, not a stop
- ★C17 · #1234; mvp-plan.md's Decisions · refuter: pending · reproduced how: read both texts 2026-11-17 · result: reproduced · keep: his list is a question
- ★C18 · council/user.md:13, :85; p711-sound-demo/rows.md row 10 · refuter: pending · reproduced how: row 10 read; "Claude typed every command" not re-checked · result: reproduced in part · keep: n = 1
- ★C19 · council/existing.md:45-50 · refuter: pending · reproduced how: not re-read · result: not reproduced · keep: licences were not read

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
