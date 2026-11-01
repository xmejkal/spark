# P510 product lens: walk 4's cards against the vision, P100 and the PO's words

> Walk 4 reached both goals, so the basic journey (P100, #6) works. The cards that move it closer are C1 (SPI build bug), C6 (no-hands deploy) and C2 (module on a fixed connector). C5, C10 and half of C7 are polish.
> Repeat gaps G5, G8, G13, G16 and G18 stay open because each sits in a "later" card or has none. Three walks is the cut: file or won't fix.
> Ready holds 6. P506 (#700) goes back to Idea, because it is a question for the PO, not work.

Evidence base: rows file `docs/observations/rows/p510-walk4-council.md`, the diary `walk4-diary.md`, `walks-compared.md` of P480, `gh issue view` (read only). Lines marked "not checked" have no evidence.

## Findings

| # | finding | evidence | card or plan | proposal | severity |
|---|---|---|---|---|---|
| 1 | Ready holds 6 (P510, P473, P503, P506, P507, P508) against a limit of 5. P506 holds a question, "does a page move to scrum/", with a PO decision as its Done when. It builds nothing for P100's bar. | #700 body: "The PO decides; if yes, one PR moves the part". P504's council already kept the part in developing.md. | P506 (#700) | Move P506 to Idea. It returns when the PO has a free minute. If a second card must go, P503 (#692, diagrams), because it serves no stage of the journey. | high |
| 2 | P507 and P508 lack "### Needed by". Both serve one design: the event seam of P479 (#657), part of P323's target architecture and its epic P158 (#94). | #702 and #703 bodies cite `event-seam-plan.md` section 2 rows E1 and E2a. See the section below. | P507 (#702), P508 (#703) | Add the "Needed by" text below to both bodies. | medium |
| 3 | G5, G8, G13, G16 and G18 are open since walk 2 or 3. They stay open because each was parked behind a card that waits on another card, or has no card (see the section below). | `walks-compared.md` rows D, I; walk 4 rows 5, 8, 13, 16, 18; compare notes "G5 none, G16 none". | P314 (#388), P390 (#505), P118 (#52), P490 (#669), C9, C6 | Decide each now: G18 and G8 pull their open cards, G5 gets a line in P390, G13 and G16 get a stated home, none stays "row only". | high |
| 4 | C1 is the only card that blocks a goal: no SPI part builds on the FireBeetle 2. The person said "we definitelly should fix this". Every display and many sensors use SPI. | rows file C1 and G29, G30. Technology lens reproduces it (not checked by this lens). | C1 | Top of Ready, ahead of the event-seam chores. | high |
| 5 | The I3 words ("without me having to switch to the other terminal ... ideally also without pressing the buttons") name the top recurring cost: 11 presses in one walk. P472 (#643, closed) found the way, and P469 (#637) is open on the look. | rows 15, 36, 40, 41, I3 | C6 and P469 | Keep C6, as two cards: the no-hands look and deploy, then the standing yes. Merge the look part into P469. | high |
| 6 | C2 is large. It mixes the board record (connectors), the part record (plugs into), the pin map (honors it) and the pick (warns). P460 (#628) is a spike, so the design question is open. | rows C2, G19 to G24, G27; #628 title | C2, P460 | Merge into P460 as its answer. File the build card only after the spike finds the shape. | medium |
| 7 | C10 (BOOT as second button) and C5 (first steps) serve few people today and are cheap. C5's brief fix (G1, G9) is a real defect: the goal is lost at step S. | rows 1, 9, 11, 34 | C5, C10 | Keep C5 split: G1 and G9 first (the goal reaches the brief), G2 and G11 into P488 (#667). C10 joins P467 (#635). | medium |
| 8 | C11 (the driver tuning) is outside spark. The PO set it right after P510. The product cost is its return to C8 and P336 (#430), not the driver. | rows C11, PO words 21:58 | C11 (P511 #706) | Not replanned. It must return facts only: the pinned image, its `vfs`, its serial. | low |

## The Ready card that goes back to Idea

P506 (#700). Reasons:
1. Its Done when is the PO's decision, so no agent can finish it.
2. A move of a doc part changes no stage of the journey. P100's bar is "closer to a breadboard with working firmware".
3. The P504 council already gave a verdict (keep it in developing.md). A yes or no costs the PO a minute and can wait for the next retro.
4. After it leaves, Ready holds P510, P473, P503, P507, P508 and the council adds C1 and C6 on top. The synthesis must then move P503 (diagrams) out too, or lift the limit by the pull rule. Not checked: the board's exact Ready count today.

## What P507 and P508 serve

Both serve the event seam, P479 (#657), merged in PR #686. It is a step of P323's target architecture and the one-core epic P158 (#94).
- P507 (E1): the probe. It adds `Event`, `Reporter`, `TerminalReporter` and `OutsideWorld.report`, used only by the look. Proof: 16 goldens stay byte-equal.
- P508 (E2a): two new deploy goldens. They pin deploy's printed lines so E2 (inside W4-2, the deploy wave) can move `show_line` to `outside.report` and prove no byte changed.
- Both unblock P478 (#656), the colored terminal, and the MCP progress reporter. They also serve the PO's rule "whatever spark does must work through every interface" (2026-10-31), because the seam is how a run tells a CLI, an MCP or an agent what happens now.
- Journey value: indirect. The seam lets C6's automatic deploy show its phases without a terminal step (rows 35, 41).

Proposed "### Needed by" text for both:
> P479's event seam (`event-seam-plan.md`), part of P323's target architecture and epic P158 (#94). It feeds W4-2 (deploy on the core), P478 (#656) and the interfaces that follow a run (MCP, P417 #545). P508: "E2 cannot move deploy's lines without these two goldens." P507: "E2 and every later output place copy the probe the look proves."

## Why G5, G8, G13, G16 and G18 stay open

| gap | seen in | what is open | why it stays | verdict |
|---|---|---|---|---|
| G5, `--match` lists `xiao-esp32-c6-fresh (button-light)` with no word | W2 G8, W3 G11, W4 G5 | P314 (#388) and P390 (#505), both open. The compare notes say "G5 none". | The fix is a record in one project. P390 is a big card (a shelf), P314 is about pin roles. Neither names the label. Each walk adds a row, none pulls a card. | Card: add one line to P390 (a project-local record is labeled in `--match`) or file an XS. Not won't fix, it shows in every walk. |
| G8, "not asked for" for skipped checks | W2 G1, W3 G6, W4 G8 | P118 (#52), open since early. P480 added a Value proven by on it. | Never ranked high enough. Each time it was "rank 8 and later" in the plan (`plan.md:122`). | Card exists. Pull P118 as XS now, or the PO says won't fix. After three walks "later" is a decision. |
| G13, no command to press a button or read the LED on the Mac | W2 G23, W3 G31, W4 G13 | P295 option B / C9, P492 (#671, spike). | Waits for the Wokwi spike, which waits for the own simulator finding. The chain has no end date. | Card: C9 as one XS (a press and a read on the stand-ins), with no wait for P492. Name P492 as a later widening. |
| G16, 2 s of silence does not tell a running firmware from a dead board | W3 G16, W4 G16 | None. P465 (#633) was tried and rejected by the refuter (rows P480 row 44). | The home card was wrong, so the gap fell between cards. | Card: fold into C6's watch step (later console lines in the board log, G35). One home, not two. |
| G18, a bench result has no place in the store | W3 G37, W4 G18 | P490 (#669), open, labeled N10 "after W4-2". | Parked behind W4-2 by design. The card is ready, the dependency is long. | Card exists. Move it up: the typed yes and a store field need only the store, not W4-2. Check with the architecture lens. |

Rule proposed for the retro: a gap that repeats in 3 walks gets a card in Ready or the PO's "won't fix". Not "row only".

## C1 to C11

| card | verdict | why |
|---|---|---|
| C1 SPI build bug | keep, top | Blocks every SPI part on this board. Small. The person's words. |
| C2 module on a fixed connector | merge into P460 (#628) | The spike holds the question. C2 is its probable answer, not a separate card. File the build card after the finding. |
| C3 remove a part | keep, rewrite smaller | The journey "swap a part" has no step. Change: a `--pick . need=` or `--drop` with a dry run frees the hold. Done when: a dropped need leaves no pin name in `pins.py`, and the hold is free. Leave the import test of old firmware to a later card. |
| C4 walk presets and holds | merge into P466 (#634) for holds, split the rest | G3, G4 ride P466. G6, G7 (offer to raise the owned count, print entry keys) are one XS. The preset (I1) waits for the retro, because P510 rules say no walk predictions. |
| C5 first steps | split | G1 and G9 first (goal reaches the brief). G2 into P488 (#667). G11 (next step in the verdict) one XS. |
| C6 automatic mode | keep, split in two | Part 1: no-hands look and deploy via `machine.bootloader()`, merged into P469 (#637) and P472 (closed). Part 2: one standing yes for N minutes, the PO's I3. Both include the watch step and G16. |
| C7 one word about what a run tests | merge into P490 (#669) and P409 (#535) | G18 into P490, G25 into P409. G10, G17, G28, G33 form one XS: one word for "not testable here". |
| C8 own MicroPython build | merge into P336 (#430) and P349 (#445) | The principle holds (carry a pinned image, no driver). Order: PSRAM SKU (G37, G38, G39) first, the native driver (G42 to G46) after C11 returns. |
| C9 free firmware tests | rewrite as XS | Done when: one command presses a pin and reads a pin or a PWM duty on the stand-ins. The `s3lcd` stand-in (G43) and type stubs (G14) are later. |
| C10 BOOT as second button | merge into P467 (#635) | Same family: the board's own part in `--match`. |
| C11 driver tuning | not replanned | It is P511 (#706). Check that it returns facts to C8 and P336. |

## New cards

1. P? — a gap seen in three walks has no owner → each of G5, G8, G13, G16 and G18 has a card in Ready or a won't fix. Need: the PO's rule "something always works" and "finish before switching", seen in `walks-compared.md` rows D and I. Done when: each of the five rows in the rows file names a card number or "won't fix, the PO, date".
2. P? — a build says `source_trace_not_connected_error` with no trace named → the verdict names the trace (G30). Need: the person's words "we definitelly should fix this". Done when: a broken trace prints its source and target names. Ride on C1 as the same PR if small.
3. P? — the goal of the person never reaches the brief → `/spark:idea` writes the goal at step S (G1, G9). Need: P100's first step. Done when: `.spark/project.json` holds the goal after step S.

## Order for the top of Ready (against P100)

1. C1 SPI build bug: blocks goal 2 of the walk.
2. C6 part 1, no-hands look and deploy (with P469): the highest recurring cost, I3.
3. P508 (#703) then P507 (#702): they unblock W4-2, which builds deploy's `next` on the core. P473 (#647) rides W4-2.
4. P118 (#52) and P490 (#669), pulled as XS to close two of the five repeat gaps.
5. C5 part 1 (goal reaches the brief), then C3 (remove a part).
6. P503 (#692, diagrams) behind these. P506 goes to Idea.

## Not checked

- The code behind each gap (the technology lens owns it).
- The exact Ready count and the order on the board today (only the brief's list).
- The bodies of P314, P390, P118 and P490 beyond their titles.
- Whether P503 (#692) must also leave Ready to stay at the limit of 5 once C1 and C6 arrive.
