# PO-assistant lens: replan, 2026-10-11
E = evidence, H = judgement. #n spark issue, bin#n the bin's.

## 1. Journey stages (button-and-LED project), done-test each
1. Idea to requirements: `parts.py --pick` leaves requirements.json (E #6: scripts work).
2. Build: `/spark:build` exits 0 (E).
3. Check: `check_all` exits 0 or names what is owed; now exit 2 (E #6).
4. Sheet: a person wires it unaided (E: P191 merged, never wired).
5. Firmware: imports on the Mac with a `machine` spark ships; an undriven pin is reported (E #7, #8).
6. Simulation: shipped scenario passes (E #64; P190 done).
7. Deploy: one command, the FireBeetle runs it (E #144).
8. Bench: button lights the LED, verdict logged (E #16, bin#2).
9. PCB/3D on request: `tsci export -f gerbers|glb` (E: works).

## 2. First slice, in order
1. **Fresh-project verdict** (M, new; uses #45, #74, #75, from #67/#102): `check_all` exits 0 or lists what is owed.
2. **#7 + shipped fake `machine`** (S): the project's firmware imports on the Mac.
3. **#8** (S, after 2): delete the LED write, exit 1.
4. **#64** retargeted to this project (S, after 2): one dated Wokwi run (W10: your yes).
5. **#144 + #138** (M + S, after 4): `/spark:setup` offers esptool; one command flashes.
6. **The walk** (M, your hands, after bin#15 reads the board's revision): wire, flash, press, diary, verdict. It is P79's pass line and P100's round A; each break becomes a card.

P192 sits at 5 (H): the last handover, due once 2 to 4 are Done. It has no slice; Ready needs one.

**Finish first (W6):** #94 (P158) is in Build with a 108-card plan whose first slice is chip tables and mutation scoring (E p158-short, #135, #136): back to Idea, then Later. #6 (P100) holds a Discovery slot: cut to round A, park B and C. Leave Ready: #135, #136 (off the path). #138 stays behind #144.

## 3. Merge, split, close
- #16 and #102 under one epic; story-map slice 7 retitled "Breadboard to flashed firmware", moved before 4 and 5 (your confirmed map).
- Close #67 as umbrella; children stay single.
- Bin walk follows: bin#5, #2, #3, #26 (same cause as P190), then #8, #9, #11.

## 4. Prune
**A usable v1: a hobbyist goes from a basic idea to a parts list, a wiring sheet and firmware that passes the simulation and runs when flashed onto their own board on a breadboard, with PCB and 3D on request.**
Rule: a card leaves unless the walk hit it (W14). One parking epic, "Later"; unlisted cards stay.
- **Shared/online store, sync, editor** (the local drawer is done): #96, #17, #19, #20, #21, #22, #23, #82, #114, #118, #119, #123, #93, #99.
- **Rail, motor, I2C, copper numbers** (a button and LED has none): #41, #54, #56, #63, #73, #78, #79, #86, #87, #76.
- **PCB-side checks and engines:** #70, #60, #89, #9 (a breadboard needs no capacitors), #55, #83.
- **Mutation, QA, team tooling** (your first complaint): #135, #137, #97, #103, #28, #113, #27, #30, #108, #111, #101, #39, #121.
- **Install polish, stranger README** (back if the walk trips one): #46, #47, #48, #53, #57, #61, #62, #66, #71, #72, #81, #84, #128.
- **Bin PCB, enclosure, deep sleep, cleanup** (not ordering the board, CLAUDE.md): bin#4, #6, #13, #14, #16, #17, #18, #19, #20, #21, #22, #23, #25.
- **Stay, after the walk:** #134 (P185), #13 (P77, "does the example still work"), #10, #12, #5.

## 5. Ask the PO
1. Is the v1 sentence yours? May slice 7 move first?
2. P158: Idea then Later, or keep only its I0 baseline?
3. P100 cut to round A?
4. Mutation testing on every change (DoD 2): keep, or only check logic?
5. When can you wire a breadboard; may Wokwi minutes go on item 4?
6. P185 (needs you): before the walk, so parts come from your drawer, or after?
