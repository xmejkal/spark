# P480 product lens: the cards against the vision, P100 and the PO's words

> Walk 3 reached a lit LED on the real board, so the basic journey (P100, #6) works. The gaps that matter now make a pass dishonest (G32, G37), a simulation blind (G28) or a store write silent.
> Of 37 gaps, 21 need a card, 10 ride in an open card, 6 stay rows. C2 (a board's own parts) and C6 (bench result) come first.
> The PO wants simulation back now. So C1 splits: a small "simulation back on" card moves up, and the emulator spike stays after the MVP.

Evidence base: card #658 (the PO's verbatim words), `scrum/VISION.md` (the hobbyist "succeeds when the firmware runs on their board"), `scrum/STORY_MAP.md` step 8 (Simulate) and step 9 (Firmware), the open-card list from `gh issue list` (run today), the walk 3 diary gaps. Gap claims are not re-checked in code, that is the technology lens.

## Findings

| # | finding | evidence | card or plan | proposal | severity |
|---|---|---|---|---|---|
| 1 | A passed run that tested no must line is taken by deploy as "tested". It is the one false green in the chain. | G32, G37, diary step 16 and 21 | C6 (bench result for a must line) | Do first. It guards the vision's "refusing rather than guessing". | high |
| 2 | The board-only build draws no LED and no button, so no scenario can test either must line. The PO asked for a real circuit with the parts "on me". | G13, G20, G28, G29, I1, the PO's words at 07:27 and 08:05 | C2 (a board's own part) | Keep, as the biggest card. Slice it. The PO wants the same code path for onboard and added parts. | high |
| 3 | `parts.py <op> <project>` made a stray project folder and list entry, and no command removes it. | G9, G10, G17, PO at 07:19 "noted and debugged how it happened" | C3 (project name or folder) | Small bug, store data. Do early. | high |
| 4 | A board-only build never writes `built`, and its dry run is missing. The page says the chain writes `built`. | G27, G25, PO at 07:59 "analyze and fix later" | C2 (G27 is a bug of the board-only path), C4 | G27 rides C2, because the fix sits in `board_alone`. G25 rides C4. | medium |
| 5 | Store writes are not named on pages or in `--help`: init's projects list, `--step`, `--needs-set`. Claude told the person the wrong thing. | G5, G8, G17 | C4 (store writes said, with a dry run) | Keep, docs and help text first, dry runs second. | medium |
| 6 | The look cannot say "board read, no token yet", and it refuses to start without `requirements.json`. A new user cannot learn which board is on USB. | G1, G3, G4, G18 | C5 (spark says which board is on USB) | Keep a reduced C5: only these four. The vision's hobbyist "quits when their board is not one spark knows". | medium |
| 7 | Seven gaps in C5 already have an open card. | G15, G7 in P466 (#634, MAC names its unit); G16, G19, G34 in P465 (#633, a board that does not start); G36 in P473 (#647) | P466, P465, P473 | Strip them from C5. Add the walk 3 gap ids to those cards. | medium |
| 8 | The serial monitor is not wired in a board-only diagram. | G26, P468 (#636) already says it | P468 | Rides P468. Needed before any scenario can hear `ready`. | medium |
| 9 | The Mac has no moving clock, no PWM duty over time and no command that presses a pin. Each walk writes its own test. | G24, G30, G31, I2 | C8 (free firmware tests on the Mac) | Split C8. Keep the small part (G30 console lines in the example, G31 a press-and-read command). Move G21 stubs to rows. | medium |
| 10 | The PO wants simulation "reenabled" with the 50 CI minutes accepted and free local checks. The chain has the pieces but no switch. | PO at 07:41; P410 (#536 one setting), P413 (#539 minute count), P399 (#515 refuse a bad id), no-paid-Wokwi-runs rule | new card C1a, P410, P413, P399 | See the order section. | high |
| 11 | The deploy page says Claude Code does not ask before `deploy.py`, but auto mode refused it. A claim on a page is wrong. | G35, S7 | P476 (#652, deploy page) | Rides P476 as a one-line fix of the claim. | low |
| 12 | Hand edits: the PO said "collect notes now and get into it later". The keep-or-overwrite rules exist in code but no page lists them. | I3, G33, PO at 08:17 | C7 | Drop the card. A page for G33 rides C4. Keep I3 as a row for a later epic. | low |
| 13 | The own-emulator question has no user page. | G23, PO at 07:41 | C1 | The one-line link to the finding rides C1b. | low |

## The 37 gaps, by where they go

- Need a card (21): G1, G3, G4, G18 (C5); G5, G8, G25, G33 (C4); G9, G10, G17 (C3); G13, G20, G27, G28, G29 (C2); G32, G37 (C6); G24, G30, G31 (C8). G22 (one page of test kinds) rides C8's docs.
- Ride in an open card (10): G26 in P468 (#636); G15, G7 in P466 (#634); G16, G19, G34 in P465 (#633); G12 in P406 (#531, the offer shows the fact); G36 in P473 (#647); G35 in P476 (#652); G23 in C1b.
- Stay rows (6): G2 (plugin cache 0.4.0, belongs to the stranger's first install, a later epic); G6 and G11 (walk 2's G1 and G8, still open, rows until the PO picks them); G14 (the other-choice note); G21 (MicroPython stubs, not on the P100 path); G22 if C8 is cut.
- G13 also feeds P467 (#635, onboard part ranks first) and P332 (#426, the board's onboard pins are never handed out). Both stay open and ride with C2's first slice.

## C1 to C8

- C1: split. C1a "simulation back on" is a story, not a spike. C1b is the spike as the PO wrote it, after the MVP.
  - C1a, the change: one setting picks "simulate, deploy, or quick free check" (P410 #536). Every scenario run counts its minutes (P413 #539). `run_scenario.py` refuses a bad component id first (P399 #515). A board-only project's simulation runs the onboard LED and button once C2 slice 1 is in.
  - C1a, done when: the walk 3 project runs a Wokwi scenario that presses GPIO47 and sees GPIO21, in CI on the free plan, and `run_scenario.py --json` says how many minutes it spent.
  - C1b keeps the PO's four questions and adds the link for G23.
- C2: keep, rewrite as slices. Slice 1 (the story): the FireBeetle's LED and button are parts in the diagram, with "on" set to the board, the serial wires from P468, and `built` written (G27). Done when: the walk 3 board-only build gives a diagram that holds the LED on GPIO21 and the button on GPIO47, and a scenario presses and sees them. Slice 2: schematic, breadboard sheet and page. The systematic design is the architecture lens's task.
- C3: keep. The change: a listed name or a folder, say which, refuse a missing folder, and one command removes a project from the list. Done when: a test with the name "walk3" makes no `walk3/walk3` and names the folder it used.
- C4: keep, rewrite. The change: pages and `--help` name each store write (init list, `--step`, `--needs-set`, `built`), then add dry runs, plus one page for G33. Done when: a test fails if a command that writes to the store lacks the words in `--help`.
- C5: rewrite, reduced to G1, G3, G4, G18. The change: the look reads chip, flash size and MAC with no `requirements.json`, and its status tells "read, no token yet" from "not read". Done when: in an empty folder the look names the chip and the MAC and says what to do next.
- C6: keep, first. The change: a bench result for a must line is written in the project and the store, and a passed run that tested no must line says so in its verdict. Done when: after a bench "yes", the next look lists the must line as "passed on the bench" and `/spark:deploy` shows "no must line tested" for a run that tested none.
- C7: drop. Reason above (the PO's "get into it later"). I3 stays a row. The page for G33 rides C4.
- C8: split. C8a: G30 and G31 (console lines in the example, a press-and-read command). C8b: the moving clock and PWM duty (G24, I2). C8b waits on the C1a decision, because Wokwi's `--vcd-file` may replace it.

## New cards

- P? — a passed simulation that tested no must line goes to deploy as tested → the verdict says "no must line tested" and deploy shows it. This is C6's second half, filed alone if C6 is split.
- P? — simulation is paid per run and chosen run by run → C1a above. Done when: stated in C1a.
- P? — a project folder made by mistake stays → a command removes it. This is G10, filed with C3.

## Order for the top of Ready

Rule: first what makes the walk honest, then what makes the simulation useful, then comfort. Reasons are against P100.

| rank | card | reason against P100 (a basic project to a breadboard with working firmware) |
|---|---|---|
| 1 | C6, bench result and honest verdict | The deploy gate trusts a pass that tested nothing. A false green breaks the bar. |
| 2 | C3, project name or folder | The wrong project entry corrupts the store, and a person cannot undo it. Small. |
| 3 | P468 (#636), serial monitor in every diagram | A scenario cannot hear `ready` without it. It is the first piece of simulation back on. |
| 4 | C2 slice 1, a board's own LED and button in the diagram | Without it, the common "button and LED on my board" project has no testable must line. Includes G27 and P467 (#635). |
| 5 | C1a, simulation back on | The PO's ask. Needs ranks 3 and 4. Sets one switch (P410), counts minutes (P413), checks ids (P399). |
| 6 | P469 (#637), the look reads without a restart | A running program on the board stops three times before a flash. It protects the person's other project at the bench. |
| 7 | P473 (#647), `next` carries the store | Claude in a fresh shell uses the wrong store. The journey breaks on the AI path. Also holds G36. |
| 8 | C5 reduced, the look before init | Helps the first minute, but a person can name the board. P466 and P465 follow it. |
| 9 | C4, store writes said | Fixes a wrong sentence Claude told the person. Docs and help first. |
| 10 | C8a, example console lines and a press command | Saves each walk one hand-written test. Not on the bar. |
| 11 | P476 (#652), a reason for each deploy step | A teaching gain. The deploy already works. Rides G35's claim fix. |
| after MVP | C1b, the emulator spike | The PO's words: after the MVP. |

What it means that simulation comes back now: C1b stays after the MVP, but only its first question (use Wokwi's free tools more) is cheap and moves into C1a. The emulator part (question 2) and the "model each real part" part (questions 3 and 4) wait. C2 slice 1 moves ahead of everything but C6 and C3, because a simulation with no LED and no button proves nothing. Paid runs stay off, as the standing rule says. The CI free minutes and `wokwi-cli lint` with `expect-pin` are the allowed path.

## Not checked

- No gap was re-run in code. The 37 claims are taken from the diary and the council's technology lens checks them.
- The size of C2 slice 1 is a product guess. The architecture lens judges where the code lives.
- Walk 2's G1 and G8 owners (G6, G11) were not looked up. They may already ride an open card.
- The list of open cards was read by title, not by body, except the ones named here.
- Ready's current order was not read on the board. The three Ready cards are taken from the brief.
