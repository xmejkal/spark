# P653 council: product and showcase lens (2026-11-06)

Tags: E = evidence with a pointer, H = hypothesis with its source, D = decision (who, when). Paths: PG = /Users/petr/Development/firebeetle-games, SP = /Users/petr/Development/spark. "—" = unknown.

## 1. Findings

| id | claim | tag | pointer |
| --- | --- | --- | --- |
| PS-1 | The origin step has a full record: walk 4 on 2026-11-01. Claude was asked for a GDI display, ran /spark:research, an agent wrote `parts/dfr0664-tft-2in.json` (SPI, ST7789, each fact verified) in about 3 min with 25 tool calls; the board then ran MicroPython, 10 one-button games were written by an agent in about 6 min with 12 tool calls | E | ~/Development/spark-walks/walk4/walk4-diary.md lines 17-33; SP/tests/data/parts/dfr0664-tft-2in.json |
| PS-2 | The "stuck" step is recorded: PO at 2026-11-02 08:05 "Kinda smooth, not smooth enough, it still gets stuck and it's not playable"; s3lcd image measured flappy 9.5 fps, runner 6.8 fps (run1-v129-s3lcd) | E | PG/bench.md lines 16-45 |
| PS-3 | The C-driver step is recorded: P533 slices 0-5 (probes, no byte swap, frame in C, partial show), P537 finding ranks the options; the spike P539/P537 root cause list is "frames at uneven 40-80 ms intervals" | E | PG/bench.md lines 59-150; PG/p537-finding.md; PG/research.md |
| PS-4 | The engine step is recorded: P589 (what a C step costs), P593 rain (C 24-25 fps, 0.22 ms step vs Python 8-9 fps, 28 ms step), P590, P596, P598, P607, P608, P633, P639, P646 each have a bench.md section | E | PG/bench.md headings at lines 230, 262, 378-458, 555-637; PG/README.md "Status" |
| PS-5 | The C-versus-Python comparison, the strongest single "why C" number, is in one place and can be re-run live: the rain's BOOT tap swaps C and Python on the board | E | PG/README.md Status "The rain"; PG/bench.md line 262 |
| PS-6 | A reader who never saw the project has no single entry page. PG/README.md is a log-style status list of 14 bullets with P-numbers; the story from "spark found the screen" is split over spark walk 4 files, PG/research.md, p537-finding.md and bench.md (659 lines). No page links the steps in order | E | PG/README.md lines 28-80; `wc -l` PG/bench.md = 659 |
| PS-7 | The repo has almost no pictures: PG has art/preview.png, art/preview-ink.png and docs/discovery/2026-11-06-p647-flame-motion/average-fire.png; no photo, GIF or video of the board in README or the two engine docs (grep gif/video/screenshot found no hit) | E | `find PG -name "*.png" -o -name "*.gif"`; `grep -n -i "gif\|video\|screenshot\|photo"` PG README.md docs/engine-walkthrough.md: no output. P647 title mentions "Mac frames" (flame clips), so Mac renders may exist elsewhere | 
| PS-8 | Mac-side render exists: `tools/render_scene.py burning out.png` draws heat-field scenes to PNG with no board; this is a free source of pictures | E | PG/README.md "What is here" table, tools row |
| PS-9 | GAMES lists 14: Fire, BallPit, BurningBodies, Rain (4 effect scenes); Flappy, Runner, Stack (3 painted); Snake, Cave, Tunnel, Road, Starfire, CubeTiming, GravityPong (7 flat). Only the 4 effect scenes use the C engine; only Fire/BallPit/BurningBodies/Rain are "scenes", not games with a goal | E | PG/games/app.py:44; PG/README.md line 77 |
| PS-10 | Of the effect scenes only one is a game-like interaction: the ball pit (BOOT pours, hold shakes). The "games using the effects" the PO wants are partly there: flappy has the fire trail (P602, merged, "the PO tried it ... and kept it for other games"), but flappy with fire runs 16-17 fps and "lower than 25 seems stuck" (P612 #817, closed as a finding) | E | PG/README.md "Done last"; gh issue 812 sub-issue #817 title |
| PS-11 | Fire + flappy is already recorded but P602's fire "merged with no game on it" per the walkthrough; whether flappy ships with fire on is — (README line 'Fourteen games' does not say) | E/— | PG/docs/engine-walkthrough.md "Done last" paragraph |
| PS-12 | Playable effect+goal candidates on the board: P651 Runner on fire (#874, Idea, XS-sized, same `body.effect = FireTrail(...)` as burning.py:98; cost risk: fire ~21 ms/frame in burning, bench P646 step 7.91-8.06 ms, draw 13.21-13.78 ms); P606 Runner in the C rain (#808, Idea); P635 silhouette people (#850, Idea, feel slice, "controversial", slice 0 only has a cost probe at bench.md line 508); P636 a game with a goal and controls from P635 (#851, Idea) | E | gh issue view 874, 850; sub_issues of #827 |
| PS-13 | P635/P636/P637 (burning people, a game from them, talking figures from an LLM) are the most memorable but also the riskiest for an employer-facing showcase: the PO himself called it "nicely controversial" (grandma who cannot escape) | E | gh issue 850 body, PO 2026-11-05 quote |
| PS-14 | Open effect cards in #827 that add visual variety without a new game: P597 water (#798), P600 ripple/sand/plasma (#801), P610 blur (#814), P611 motion blur (#815), P625 spark burst on a hit in a flat game (#838), P626 snake glow and cave floor burns (#839). P601 SWAR/PIE (#802) is the "S3 optimisations" story, and bound probe exists (bench.md line 610) | E | sub_issues of #827; PG/bench.md line 610 |
| PS-15 | "A whole engine in C using the S3's optimisations": what is true today is C core + DMA frame + early-out blend; the S3 PIE vector instructions are NOT used yet (P601 #802 open, P583 effects on PIE is "Later"). Claim "uses the S3's optimisations" is true for DMA, PSRAM double buffer, octal PSRAM, not for PIE | E | PG/README.md Status ("P583 ... Later"); PG/docs/engine-walkthrough.md "Done last"; bench.md line 610 "bound probe, before any SWAR blend" |
| PS-16 | Engine epic P609 #812 is open with 15 open and 5 closed children; most are refactor/structure cards (P621-P623, P628-P631, P634, P640-P644, P648-P649). None blocks showing the current games; all feed the "mature reusable engine" goal. P609 says "In Idea until the PO orders it" | E | gh issue 812 and its sub_issues |
| PS-17 | The engine and driver are already split into submodules (pixel-engine, s3lcd fork) with a README stating "the repository is also a log of how the games got smooth: every step was measured on the bench" - this is the project's own showcase thesis, already written | E | PG/README.md line 5; P632 #846 closed |
| PS-18 | Controls: the whole box has two buttons (BOOT GPIO0 for the game, the board button for switching); every game is one-button. No D-pad, joystick or sound in the repo. grep for sound/buzzer/speaker/audio found no hit in README, the docs or discovery items | E | PG/games/buttons.py:1-8; `grep -rniE "sound\|buzzer\|speaker\|audio"` PG README.md docs/*.md docs/discovery/*/items.md p537-finding.md: no output |
| PS-19 | Spark's own side of this story is thinner than the games side: spark README says the bench step is "partly", "A C driver image went on outside spark (walk 4)" and no breadboard wired from a sheet has run yet. So "done by just talking to Claude and using spark" is true for part research, deploy and the first games; the C driver and engine were built outside spark's chain | E | SP/README.md lines 124-125, 161 |
| PS-20 | Spark principle conflicts with the showcase framing: AGENTS.md says "Spark exports facts, never behaviour" and "spark is the product; a spark change does not update the demo projects". The games are pixel-games, a separate repo; showcasing them is not a spark card, it is a PO decision to spend time outside the bar "a basic project closer to a breadboard with working firmware" | E | SP/AGENTS.md "Principles for changing spark" |
| PS-21 | The PO's own earlier positioning: spark = his job-application example "showcase architecture + clean Python, pruned" | D | PO 2026-10-21 (memory spark-showcase-and-teaching) |
| PS-22 | Time since last spark-side work: spark's wave 4 refactor is going first per P651's note; the PO now offers a reorder (games first, then spark) | D | gh issue 874 Notes (PO 2026-11-06); PO message today |
| PS-23 | Bench evidence is heavy but not curated: PG root holds about 130 `run*.log` and 25 `build-*.log` files | E | `ls PG` output (run1 to run129, build-*.log, flash-*.log); no index of which runs are the "story" runs |
| PS-24 | Home paths: the walkthrough and bench mention `~/esp/...` only; README says clone and build steps with `~/esp/esp-idf-v5.5.2`. No absolute /Users path seen in the README | E | PG/README.md lines 27-33 (not exhaustively grepped) |

## 2. Proposed demo set and story outline

### Smallest demo set (proposal; the PO decides)

A reader needs to see three things: (a) it moves smoothly, (b) it is C doing the heavy work, (c) it is a game, not only a screen saver. Proposed minimum, 5 scenes of the existing 14:

| scene | shows | exists | open card needed |
| --- | --- | --- | --- |
| Rain with C/Python swap on BOOT | the why-C number on the board, 24-25 fps vs 8-9 fps (PS-5) | yes (P593) | none |
| Fire (linear/picture/nearest) | the best-looking effect, the heat field, bilinear filter | yes (P595, P608, P646) | none (P650 #872 is a look polish, optional) |
| Ball pit | physics in C, 100 balls at 23-24 fps, a touch of play (pour, shake) | yes (P598) | none |
| Bodies on fire | effects composed on bodies, events C to Python | yes (P596, P607, P639) | none |
| One real game with an effect | the "games using the effects" ask | flappy with fire trail (P602) exists but at 16-17 fps (PS-10) | P651 Runner on fire (#874) is the smallest one (H: XS); its fps risk must be measured first (cost note in the card) |

A second game with a goal that is not fire-only (for example Runner in the C rain, P606 #808) is optional. P635/P636 (#850/#851) are not needed for the minimum (H: PS-13).

Cards needed for the demo (H, from the above): P651 #874; the documentation/pictures work in section 3 (no card yet; a new card would be needed, this lens does not file it). Cards not needed for the demo: all of #812's structure children, P597, P600, P601, P610, P611, P625, P626, P635-P637.

### Story page outline (one page, short version first)

1. The ask: "put a game on this board" (walk 4, 2026-11-01). Evidence: walk4-diary.md; pictures: none (gap).
2. Spark finds and records the screen: DFR0664, ST7789, research agent output. Evidence: dfr0664-tft-2in.json, diary lines 24-26. Picture: none; the breadboard sheet would not apply (no breadboard run, PS-19).
3. MicroPython on, games written by an agent: 10 games, game loop, buttons. Evidence: diary lines 32-47. Picture: none.
4. "It gets stuck": the numbers. bench.md "Slice 3 at the bench" (flappy 9.5 fps, runner 6.8 fps); p537-finding.md cause list. Picture: a bench chart (none yet; could come from existing numbers).
5. The own C driver: P533 slices, DMA frame, partial show; fps result after (run18/19: 21-24 fps per walkthrough). Evidence: bench.md 59-150. Picture: none.
6. The own engine: C core with no MicroPython header, Mac-testable, binding, Python decides. Evidence: engine-walkthrough.md section 0-1 (class diagram in mermaid), deep-dives. Picture: the mermaid diagram exists; Miro board linked in the walkthrough header.
7. The proof on the board: rain C vs Python 24 vs 8 fps; fire; pit; burning bodies; one game with an effect. Evidence: bench.md P593, P595, P598, P596. Picture: Mac renders (tools/render_scene.py) and a board video (gap).
8. What I learned / what comes next: engine epic, spark.

### Gaps in evidence (from the outline)

- Steps 1-3 and 4-5 are in two repositories and a walks folder; the order is unrecorded in one place (PS-6).
- No photo/GIF/video of the board anywhere (PS-7). A short clip per effect is the cheapest proof.
- Step 5's "before and after" fps for the driver is split between bench.md runs 1-22; a one-line table does not exist (H: PS-23).
- The "S3 optimisations" claim needs a precise wording (PS-15).
- Which commit/hash and image the clips come from: — .

## 3. What waits, and why

(proposals; each one gives its reason)

- Engine-epic structure children (#828-#831, #834, #840-#844, #848, #858-#863, #870, #871): none changes what a viewer sees (PS-16). Exception to check: P629/P630 (flappy paint passes, late-frame sleep) feed the fps of a game in the demo (H: P630 touches every game's pace; if flappy+fire must reach 25 fps, one of these may be needed; P612 #817 closed says what to do).
- P635-P637 (burning people, a game from them, talking figures): high effort, controversial subject for a job-application showcase (PS-13), feel slices that stop at "ready to play" (PS-12). Later, as an optional "second act".
- P601 SWAR/PIE and P583: a good "next level" story but not in the demo; and the S3 PIE claim should not be made until they run (PS-15).
- P597 water, P600 ripple/sand/plasma, P610/P611 blur: visual variety, not needed for the minimum set (H).
- P625/P626 effects in flat games (spark burst, snake glow): small and cheap; they would make "games using the effects" true for flat games, so they are the first candidates after the minimum set (H).
- Spark's wave 4 refactor and journey cards: wait only if the PO picks "games first". The PO set the order (D, today). This lens takes no side beyond the question in section 5.
- Spark's walk-4 gap C-cards (P510 council C1-C11): not read here.

## 4. What I could not check

- Whether flappy with fire is on in the shipped GAMES list and at what fps now (PS-11): I did not read games/flappy.py or run anything.
- Whether any video or photo of the board exists outside both repositories (phone, Miro): not searched. The walkthrough links a Miro board; its contents I did not open.
- The discovery folders' item lists and verification files (only titles and one P537 finding read).
- Cards P651, P635 bodies beyond their first 1500 characters; #812, #827, #795 bodies the same.
- The state of PG's open branches (p582-heavy is paused per walkthrough) and of the working tree.
- Whether spark's walk-4 notes are public: they sit in ~/Development/spark-walks, outside the spark repo (home path rule applies to anything copied in).
- Size of effort for P651 or any card: H only; no estimate exists in the cards I read.
- Number of gh calls used: 4 of 10; no GraphQL error seen.

## 5. Questions for the PO

| question | what it decides |
| --- | --- |
| Who is the reader: an employer who reads, or a peer who watches a clip? | one story page vs a video first; pictures needed |
| Is "done" the 5-scene minimum in section 2, with P651 as the one added game? | the card list for the demo |
| Does the fire need to reach 25 fps in a game (flappy 16-17 fps now), or is "plays, with an honest number" enough? | whether P629/P630 become demo cards |
| Is the burning-people subject (P635-P637) in or out of a showcase for an employer? | whether #850 stays after the demo |
| After the demo: more controls and sound, or the spark refactor first? (see below) | the order of the next epic |
| Do the C driver and engine (built outside spark's chain) belong in the spark story, or is it "spark started it, the games repo carried it"? (PS-19) | the story's claim about spark |
| May I propose a card for the story page plus clips (no card exists for it)? | whether the documentation work is counted and ordered |

### Controls and sound (proposal on question 3)

- Controls: now the box has one useful button (PS-18). One-button games hide that the board can do more; a D-pad or a second button would add "I changed hardware and spark helped me wire it", which is spark's own journey (idea, parts, build, breadboard, deploy), the part spark owns and the games story does not show (PS-19). H: this makes the best second act and is the point where the story returns to spark. Not part of the minimum; right after it.
- Sound: no record, no part in the store, no card seen (PS-18). Adds a sense (a hit sounds) that makes the effects events (HIT, SLEEP, PS-4) audible with almost no engine change, because the C engine already reports events to Python (H). It needs a part (buzzer or I2S amp), a pin plan and a spark build, so it is spark's journey again. Proposal: after controls, as the same "add a module" demo; not part of the first showcase.
- Not at all: only if the PO wants the story to stay a pure graphics story.
