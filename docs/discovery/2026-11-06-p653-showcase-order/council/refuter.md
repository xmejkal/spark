# P653 council: refuter (Fable, 2026-11-06)

This report cites the README as of 13:05 Prague. Its line numbers, Q8 and "stage 3" belong to that version.

Read: README.md at 13:05 (133 lines; it grew from 122 lines at 13:02 while this check ran, adding the job goal, ESP-NOW and Q8), the three lens reports, pixel-games master c9e1045, spark main 331842eb, #875's four comments, #617 and #782 by REST. PG = ~/Development/firebeetle-games, SP = ~/Development/spark. I decided nothing.

## 1. Claims and their sources

| # | README claim | source opened, verbatim | verdict · change |
| --- | --- | --- | --- |
| 1 | Short 1, table row 1: the four scenes "run on the board, 22 to 25 fps" (bench.md:262, :458-476, :637-659) | PG/bench.md:474: "Smoke (`run107-p598-smoke.log`, `games/*.py` at 9cb3cba): all fourteen entries start, with no error, at 22 to 25 fps." bench.md:651: "The pass line was set before the runs: D5 (draw 13.5 ms or less, 23 fps or more) in every 5 s line, with more than 0.5 ms to spare. Both modes miss it." bench.md:467: "95 balls 24 fps, 185 balls 20, 275 balls 11, 320 balls 8" | partly. 22 to 25 is the all-14 smoke of 2026-11-04, not today's image. Change row 1 to "22 to 25 fps in run107 (2026-11-04, games 9cb3cba); the burning bodies miss their own pass line D5 in both modes; the pit holds 24 fps only to about 100 balls" |
| 2 | "The Mac suite passes 165 tests" | ran `python3 -B -m unittest discover tests` at c9e1045: "Ran 165 tests in 19.983s / OK" | holds |
| 3 | Row 2: rain "24 to 25 fps against 8 to 9 fps, live" (PS-5, TL-6 → bench.md:262) | bench.md:262 is the heading "## P593 (#794), 2026-11-03: the rain, the C engine on screen". Its table, :268-271: "160 \| C \| 24", "160 \| Python \| 7 to 8", "192 \| C \| 23", "192 \| Python \| 6 to 7". bench.md:264: "its HUD label "python, no C" is 6 glyphs longer, so its fps is slightly low." The 24 to 25 / 8 to 9 pair is at bench.md:398-399 (P590, 2026-11-04, N 160) | partly. The cited line carries 24 against 7 to 8. Change to "24 to 25 against 8 to 9 fps at 160 boxes (bench.md:398-399, P590); the live swap measured 24 against 7 to 8 (P593), and the Python label is longer, so its fps reads slightly low" |
| 4 | Row 3: flappy with fire removed 2026-11-04; "PS-10 says it exists: refuted by TL-7" | bench.md:455: "The PO played it (2026-11-04): "it looks good, I'm glad we have this effect, but it doesn't really fit the flappy, so we should remove it ..." The merged branch keeps the scroll and `FireLayer` with no game on them." bench.md:447: "Flappy falls from 24 to 21 fps. The plan's estimate was 16 to 17 fps" | holds. PS-10's "16-17 fps" was the plan's estimate, not a measurement |
| 5 | Row 9: spark README.md:124-125, :161 | SP/README.md:125: "**partly**: `deploy.py` flashes the firmware onto the board after your yes, but no breadboard wired from a sheet has run yet. ... A C driver image went on outside spark (walk 4)". :161: "No breadboard wired from a sheet has run yet." | holds |
| 6 | Short 3: W4-1 on main, W4-2 to W4-4 not started | SP/scripts/firmware_platform.py:37 "class FirmwarePlatform:", :82 "class MicroPythonPlatform(FirmwarePlatform):"; deploy_service.py:68 "def __init__(self, project, platform, evidence, run=subprocess.run, clock=None, ...". `grep -rln "DeployImage\|FlatJsonLine\|RelayedConsent\|def schema" scripts` printed nothing; `ls scripts/spark/bench` = `__init__.py look_at_board.py` | holds |
| 7 | Short 3: "No card exists for W4-2 onward (LF-8)"; stage 3 rides W4-2 on #617 | REST: "#617 open \| P457: the image check's littlefs lookup ignores a project's tools list" | holds as far as checked. #617 is not a W4-2 card. The whole board was not re-exported (GraphQL budget) |
| 8 | Short 2: "no pictures ... Neither repository holds a photo or clip of the board" | PG `find`: art/preview.png (a sprite and parallax sheet, viewed), art/preview-ink.png, docs/discovery/2026-11-06-p647-flame-motion/average-fire.png. No jpg, gif, mp4, mov | holds for "of the board". "no pictures" is stronger than PS-7's "almost no pictures"; change to "no photo or clip of the board; the pictures that exist are art sheets and one Mac render" |
| 9 | Row 7: "Sound \| no code, no speaker \| TL-31, PS-18" and stage 2 "Spark's research picks them" | REST: "#782 open \| P581: the games are silent → a small piezo buzzer plays short cues on hits and deaths \| updated 2026-11-02". TL-31 names it: "a buzzer is P581 #782 (not fetched, state unknown)". PG/docs/discovery/2026-11-03-engine/risks-and-tests.md:22: "The buzzer (P581 #782) and a joystick are their own later cards" | refuted in part. A sound card exists and is a games card. Change the row to "no code, no speaker; the card P581 #782 (piezo buzzer, 2026-11-02) is open" and let stage 2 reuse it instead of a new research |
| 10 | Short 4: "The board is over its limits: 11 cards sit in the working stages against 4 in flight" | LF-2: "Which of these 11 are epics, I did not read — so the true count against 4 is —." LF-12: the push gate "fails when a limit breaks" | partly: stronger than its source. Could not re-export the board (GraphQL limit). Change to "11 cards sit in the working stages; how many count against the limit of 4 depends on which are epics (LF-2)" |
| 11 | Stage 0: "#44 waits for P650 (its engine commit has no PR yet, TL-13)" | `git -C PG/engine branch -r --contains ab970c4` = "origin/p647-motion"; TL-13: "no open pixel-engine PR" | holds; the commit is pushed, so TL's open item (section 2, line 70) is closed |
| 12 | Row 8: two buttons, every game one | PG/games/app.py:52-53: "self.fire = buttons.Button(read_fire, ...) # BOOT plays", "self.boot = buttons.Button(read_boot, ...) # D14 switches"; app.py:2 "ten one-button games" | holds |
| 13 | Row 10: PIE not used | PG/README.md:98: "Later: ... P583 (#784), effects in C on the S3's PIE (its vector instructions)" | holds |
| 14 | Stage 2: D12 "Python decides" | PG/docs/engine-walkthrough.md:18: "The rule is "C steps and paints, Python decides" (D12 in the code comments)" | holds |
| 15 | Job goal, ESP-NOW, "recreate ... later", fire sounds: the PO's words on #875 | #875 comments, verbatim: "the main demo about it is spark, so we'll have to recreate the things later purely by using spark again, but thats later"; "I also nered to have spark presentable for finding a job as ai eveloper so to also show it being used by langgraph, maybe RAG integration"; "And ESP now integration for multiplayer" | holds. See part 3 for what the order does with them |
| 16 | Short 4: "17 to 21 days" idle; "Spark's 189 Idea cards" | not opened (board export needs GraphQL) | could not open |

## 2. The synthesis against the lenses

Dropped caveats:
- bench.md:264 (Python HUD label longer, fps "slightly low") and bench.md:651 (burning bodies "miss" D5 in both modes, TL-5) are gone; the short version says "The games work."
- LF-2's "the true count against 4 is —" is gone from short version 4.
- TL-31's buzzer card P581 #782 is gone; stage 2 proposes research that the PO already turned into a card.
- PS section 3: P629/P630 "may be needed if flappy+fire must reach 25 fps"; the stage 1 checklist measures the Runner's fps but says nothing about what happens when it misses 25 (the PO's 11-04 line "25 ok, 30 super", LF item 2).
- PS-20: showing the games is "a PO decision to spend time outside the bar" of AGENTS.md. Gone.
- TL-13: #44 needs the engine commit merged in pixel-engine before P650; the README says only "waits for P650".

Stronger than the source:
- "A demo needs almost no new engine code" rests on TL-17 (the four scenes need none). The stage 1 game P651 is unwritten and bench.md:447 prices its fire at "about 16 ms a frame".
- "Stage 2 before wave 4 is the open question, because the lenses split on it." PS puts controls and sound "not part of the first showcase; right after it", LF rates that option (c) worst ("longest delay of wave 4", "new epics, not slices"), TL takes no side. One for, one against, one silent is not a reason to make (c) the default of the diagram.

Missing findings that change the order:
- TL question 5 and LF question 6 both ask whether "Finish wave 4 first" (11-04) still stands. The README has no such question, and neither the 11-04 words nor the 11-06 ~12:50 "we're mainly working on spark, finish the refactoring" appear in it (grep: no "Finish wave 4", "refactoring" or "mainly").
- The README's own line 94 says "the job goal pulls stage 3 forward", and line 93 says P417 needs wave 4. The short version, the diagram and Q3 were not changed to match: wave 4 is still last.
- LF-11 and TL-35 (the showcase "has no fixed end") argue for a time box; Q7 asks it, but stage 2 is added inside the same stretch, which is what LF warned against.

## 3. The order

Strongest rival the folder does not rule out: stage 0; then wave 4 (PR A, B, C, D, P417) as the main line, with a docs-only stage 1 beside it (one story page from the records that exist and Mac renders, no new game, no bench); sound and a second button afterwards as games cards (P581 #782 first), and the spark-only rebuild as the walk. What favours it:
- The PO's three latest spark-side words: 11-04 "Finish wave 4 first" (memory spark-scrum-state.md:962), 11-06 ~12:50 "we're mainly working on spark, finish the refactoring" (same file :1114), 11-06 on #875 "recreate the things later purely by using spark again, but thats later".
- The job goal needs P417, which the README itself says needs wave 4 (lines 93-94). The proposed order puts the CV item fifth.
- LF options (a) and (b) both place wave 4 before sound; TL-37 says the two lines touch disjoint files, so a docs page costs wave 4 nothing.

The bar. Stage 2 as written (a C kernel fills the sample buffer, I2S by DMA, PIE mixing, a synthesized crackle) is pixel-engine work. Spark's share is one part record, one requirements line and a regenerated pins.py, the chain walk 4 already ran for the screen (PS-1). AGENTS.md: "Spark is the product. A spark change does not update the demo projects" and the bar is "a basic project closer to a breadboard with working firmware". A speaker on the games box is a walk, which AGENTS.md values, but a short one; the synthesis is a games feature labelled spark work, and its own card (P581) is a games card. The order breaks the 11-04 and 11-06 12:50 words unless the PO revokes them; the README should quote both and ask, as TL and LF did.

Confirmation bias: the README quotes the PO's "looking forward to synthesising the fire sounds" (an enthusiasm) as the warrant for stage 2, and leaves out his two instructions that point the other way. That is the team standing in for the PO.

## 4. Numbers without unit, population, period or provenance

- "22 to 25 fps" (short 1, row 1): population is all 14 games in run107, date 2026-11-04, games 9cb3cba, image 74f1d9d2; not the four scenes on today's image.
- "165 tests": no commit or date (c9e1045, 2026-11-06, about 20 s on the Mac).
- "24 to 25 fps against 8 to 9 fps": no N (160 boxes), no run or date (P590, 2026-11-04); the live-swap run gives 24 against 7 to 8.
- "11 cards", "4 in flight", "189 Idea cards": no export date or source file (LF: items2.json, open.json, 2026-11-06), and no note that epics count in no stage.
- "17 to 21 days": "untouched" means GitHub updatedAt, not "Waiting since" (LF section 4, line 67).
- "almost no new engine code": no number; P651's cost is "about 16 ms a frame" of fire (bench.md:447).
- "tens of lines" (buzzer): TL-33, an estimate with no source.
- "five working days" (Q7): LF calls it "H, no data on the pace".
- "one PR of four in": W4-1 of W4-1 to W4-4; stage 3 lists five items (PR A to D and P417), so the denominator is unclear.
- "about 300 product and 400 test lines": labelled estimates, provenance given (wave4-plan.md). Fine.

## Searches

None.
