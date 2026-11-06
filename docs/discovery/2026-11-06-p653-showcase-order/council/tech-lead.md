# P653 council, tech lead (2026-11-06)

Tags: E = seen, with a pointer. H = hypothesis, with its source. D = decided, by whom and when. Paths: PG = ~/Development/firebeetle-games (pixel-games, branch master c9e1045), SP = ~/Development/spark (main 331842eb). I decided nothing.

## 1. Findings

### Works

- TL-1 · GAMES holds 14 entries: Fire, BallPit, BurningBodies, Rain, Flappy, Runner, Snake, Stack, Cave, Tunnel, Road, Starfire, CubeTiming, GravityPong · E · PG/games/app.py:44
- TL-2 · The Mac suite passes: 165 tests, OK, 20.7 s · E · `python3 -B -m unittest discover tests` in PG, this session
- TL-3 · Fire: 24 fps, step+draw 11.5 to 11.8 ms (variant B); sky variant 15 to 16 fps (P595, early). Linear draw is now 13.21 to 13.78 ms at 24 fps; picture 14.78 to 16.48 ms at 22 to 23 fps (P646, those rows are for the burning scene, not plain Fire) · E · PG/README.md Status; PG/bench.md:637-659
- TL-4 · BallPit: about 100 balls hold 23 to 24 fps, step 17.9 ms (run99d); 320 balls 6 to 8 fps; settled pile step 4.2 ms at 100, 13.8 ms at 300 · E · PG/bench.md:458-476 (P598)
- TL-5 · BurningBodies (8 bodies + FireTrail + soft front flames): linear 24 fps, step 7.91 to 8.06 ms, draw 13.21 to 13.78 ms; picture 22 to 23 fps, step 8.34 to 8.53 ms, draw 14.78 to 16.48 ms (run128/129, engine 2a5ffdd). Both modes miss the plan's D5 line (draw 13.5 ms or less, 23 fps or more, 0.5 ms spare); linear by 0.28 ms, picture by up to 2.98 ms · E · PG/bench.md:637-659
- TL-6 · Rain: C engine 24 to 25 fps, 0.22 ms step; Python fallback 8 to 9 fps, 28 ms step (P590/P593) · E · PG/README.md Status; PG/bench.md:262
- TL-7 · Flappy 24 to 25 fps without fire (run92), 28 fps with no pace (run109). Flappy with fire ran 21 to 23 fps (run93) and the PO removed it on 2026-11-04 as not fitting; `FireLayer` and `HeatField.scroll` merged with no game on them. So there is no "flappy fire" to show today · E · PG/bench.md:441-456; D · PO 2026-11-04 (quoted there)
- TL-8 · Runner 21 to 24 fps with no play; Stack (as RENT) 24 fps. Snake, Cave, Tunnel, Road, Starfire, CubeTiming, GravityPong ("seven flat"): no per-game bench row found in my read · E · PG/README.md "Fourteen games"; — for the seven
- TL-9 · The last all-games smoke is run107 (all 14 start, 22 to 25 fps) at games commit 9cb3cba, before P633 (plugins), P639, P601 and P646 and the P632 image. A smoke after those is not in bench.md · E · PG/bench.md:475; H · no later "smoke" line (grep of bench.md, last at :475)
- TL-10 · Per-game tests on the Mac exist for fire, balls, burning, rain, effects, plugins, blend, HUD, paint. The arcade games (Snake, Cave, Tunnel, Road, Starfire, CubeTiming, GravityPong, Flappy, Runner, Stack) have none by name; only tests/test_paint.py mentions some of them · E · `ls PG/tests`; `grep -l` of game names in PG/tests
- TL-11 · Other C effects: HeatField (fire), Balls, Bodies; `effects.FireTrail` is the only body effect; `FireLayer` exists with no game. Smoke was cut by the PO (2026-11-04). Water, ripple, plasma (P597 #798, P600 #801) are open, not built · E · PG/games/effects.py; PG/README.md Status; D · PO 2026-11-04 per README · issues #798, #801 open

### Open drafts and branches

- TL-12 · pixel-games #10 (p582-heavy, draft): RENT's heavy floors; 13 commits, 10 files, +1130/-55 against master; last commit 2026-11-03 08:35 Prague; README calls it "Paused ... not merged". Needs: a rebase over P633/P632 (the engine moved to a submodule; I did not try the merge) and the PO's play of it · E · `git log master..p582-heavy`, `git diff --stat master...p582-heavy`; PG/README.md "Done last"; H · rebase cost, from the repo layout change in P632
- TL-13 · pixel-games #44 (p647-motion, worktree pixel-p647, draft): 5 commits, 4 files +61/-1: flow settings (bend, wander) in the ctypes mirror and the stand-in, 3 tests, render_scene `--flow --gif`. Its engine pointer is ab970c4 on a local engine branch `p647-motion` with no open pixel-engine PR (`gh pr list` on pixel-engine printed nothing). Needs: the engine commit pushed and merged in pixel-engine first, then the PO's pick from the clips, then P650 #872 for the board. The merged P647 finding is #45 · E · `git log master..HEAD` in pixel-p647; `git -C pixel-p647 submodule status`
- TL-14 · pixel-games #46 (p649-fluid-discovery, worktree pixel-p649, draft): 3 commits, 8 files, +328, docs only, "paused at step 5" before the refuter. Needs: the refuter pass, then the PO's yes on D1 (LIGHT). No code · E · `git log master..HEAD`, `git diff --stat` in pixel-p649
- TL-15 · The pixel-p647 worktree diff against master also shows a deleted PNG (`average-fire.png`, 292 KB) — E · `git diff master p647-motion --stat`; the branch was cut before #45 merged, so a merge would need a check that the PNG is not lost or re-added · H · my reading of the stat, not tested

### Half-done in the engine

- TL-16 · Engine cards open: P634 #848 (balls paint inside their physics; fx_discs.c painter), P622 #829 (glue in two or three copies; StepClock, binding helpers), P640 #858 (scene lists layers with a number), P641 #859 (rect + blend mode, dirty region), P642 #860 (blend moves from the driver to the engine core), P643 #861, P644 #863 (effect base class), P621 #828, P623 #830, P601 #802 (SWAR blend), P648 #870 (kept benchmarks), P650 #872 (light flow on the board), P649 #871 (fluid layer, paused) · E · `gh api repos/xmejkal/spark/issues` listing, state open
- TL-17 · Of these, a demo of "games using the effects we have" needs none to run: Fire, BallPit, BurningBodies, Rain already run on the board image. The ones that change what a viewer sees or feels are P650 #872 (flames that move; the PO's pick pending), P651 #874 (Runner on fire; the body effect in a second game), P606 #808 (Runner in rain), P615 #821 (pinball on the two buttons) · H · the card titles and TL-5; whether the PO wants any is a question for him
- TL-18 · P601 #802 is closed in practice as a probe: the bound probe showed no blend rewrite passes D5, and P646's early-out then took linear below the bound. The card stays open on GitHub. P648 #870 was planned "ready before P601's S..."; its title is cut in my read · E · PG/bench.md:610-659; issue list title cut at 140 chars
- TL-19 · P634 #848 blocks any game that wants balls without their painter (pinball P615, a pit with P613 containers). P622 #829 and P640 #858 are refactors of the engine glue that a new game would be written on · H · from the card titles; I did not read the cards' bodies
- TL-20 · The engine submodule in master is at pixel-engine a10a4c7 (merge of PR #2, P646). It matches bench.md's "engine at pixel-engine main a10a4c7" (commit 21cb9e6) · E · `git -C PG/engine log -1`

### Refactor (spark)

- TL-21 · Wave 4 status on main: W4-1 is done. P475 #651 is closed; `FirmwarePlatform` and `MicroPythonPlatform` exist (SP/scripts/firmware_platform.py:37, :82); `DeployService` takes one `clock` (SP/scripts/deploy_service.py:63-70) · E · those lines; issue #651 closed
- TL-22 · W4-2 (deploy on the core), W4-3 (grant, live, reach) and W4-4 (relayed yes) have not started: no `DeployImage`, `FlatJsonLine`, `RelayedConsent` or `schema()` anywhere in SP/scripts; `scripts/spark/bench/` holds only look_at_board.py; deploy.py is 293 lines, grant.py 134, live.py 109, reach.py 109 · E · `ls SP/scripts/spark/bench`; `grep -rln "DeployImage\|FlatJsonLine\|RelayedConsent\|def schema" scripts` printed nothing; `wc -l`
- TL-23 · The card names of the PO's list: PR A P605 #807 open (schema, trace hook, Privacy step); PR B W4-2 + E2 + P457 #617 open; PR C W4-3 + P383 #491 open; P417 #545 open. P508 (E2a, deploy goldens) closed, P507 (E1 probe on look) closed. No open pull request in spark (`gh pr list` printed nothing) · E · issue list under #94; `gh pr list --repo xmejkal/spark --state open` empty output
- TL-24 · The duplicate path today: one bench CLI (look) runs on the core (`run_cli`, `OutsideWorld`, `Operation`), four (deploy, grant, live, reach) run on the old scripts. Only look.py and bench/__init__.py use `OutsideWorld` · E · `grep -rln OutsideWorld scripts`. Whether the duplicate gets worse with time: the code does not move by itself; the risk is rebase drift on deploy.py, deploy_service.py, fakes.py and test_deploy_gate.py when other cards touch them · H · wave4-plan Risks 1 and 5
- TL-25 · The plan is still valid in shape against main (W4-1 shapes landed as planned: single `clock`, `FirmwarePlatform` base). Its line numbers are stale: it says it was planned on origin/main 67c37600 on 2026-11-01 with PR #648 read as merged; main has about 594 commits since 2026-10-25 (all areas). The T2 mock.patch count is 15 across test_deploy_gate, test_grant, test_live and test_reach now; the plan's W4-2 expects the deploy_gate entry to go and "16 to 5" after W4-1. Not recounted per file · E · wave4-plan.md:1-10, :70-75; `grep -rn mock.patch` count; `git log --since=2026-10-25 | wc -l`; H · the staleness conclusion
- TL-26 · Sizes the plan itself states: W4-2 about 300 product + 400 test lines; W4-3 about 350 + 300; W4-4 about 60 + 80 + 30 doc; W4-2 retargets 34 mutation rows, W4-3 30 · E · wave4-plan.md "Review size" and W4-2/W4-3 Net · H · they were written as estimates
- TL-27 · Nothing else half-moved was found in the parts I read: `core/events.py` exists (E1 landed), `text_guards` and `zone_time` are in core. I did not diff the whole tree for duplicates · E · `ls SP/scripts/spark/core`; — for the rest

### Controls and sound

- TL-28 · Controls today: two buttons. BOOT (GPIO0) plays; D14 (GPIO47, `pins.ONBOARD_BUTTON`) switches games. Button class debounces, with an interrupt edge counter for taps. A hold of about 5 s on D14 powers the board off (2026-11-02) · E · PG/games/buttons.py:1-49; PG/games/app.py:52-53, :160-161
- TL-29 · All 14 games are one-button ("ten one-button games" in app.py docstring; README: "Fourteen games"). More controls means new pins, a part (buttons or a joystick or the DFR0664's own keys, which I did not check), a requirements entry, a regenerated pins.py via spark, and every game's input path · E · PG/games/app.py:2-4; PG/games/pins.py header ("written by spark's assign_pins.py ... Regenerate it; do not edit it")
- TL-30 · Pins in use per pins.py: SCLK 17, MOSI 15, MISO 16, TFT_BL 38, TFT_CS 11, TFT_DC 12, TFT_RST 13, SD_CS 14, ONBOARD_LED 21, ONBOARD_BUTTON 47; plus GPIO0 in buttons.py. The remaining free pins of the FireBeetle 2 S3 I did not read from the board record · E · PG/games/pins.py; — for free pins (spark board record not read)
- TL-31 · Sound: none. No speaker or buzzer code in games/*.py (grep for buzzer, speaker, sound, audio, i2s, pwm hit only pins.py, for the TFT backlight "needs pwm"). The restyle brief says "The board has no speaker yet (restyle F7, D13)" and a buzzer is P581 #782 (not fetched, state unknown). The engine's discovery lists a sound hook "with nothing to play on" · E · `grep -rniE` in games; PG/docs/discovery/2026-11-03-engine/p588-feel-notes.md:107; council/user.md:36 (USER-22)
- TL-32 · Rough size of controls: a second game button on a free pin plus the Button class reuse is small in code (about 10 to 20 lines in app.py and one game's input) and needs hardware and a pin-map regeneration; a d-pad or joystick is a larger change in each game · H · my estimate from buttons.py (49 lines); no source
- TL-33 · Rough size of sound: a piezo buzzer on one PWM pin with `machine.PWM` tones for hit/flare events is small in Python (tens of lines) and fits the existing HIT event hook; real samples through I2S need an amp part, a driver and RAM (the image has 217 kB left in the app partition per P602, before later growth) · H · my estimate; E for the 217,312 B figure: PG/bench.md:443
- TL-34 · A speaker or extra buttons are a spark-chain exercise (idea, parts pick, requirements.json, build, breadboard, pins.py). That makes them part of the showcase story "spark finds the screen", as well as demo features · H · AGENTS.md ("From a requirements file it generates ... the pin map the firmware imports")

### Cost of paths

- TL-35 · (a) Showcase first, then refactor. Showcase work lands in pixel-games and pixel-engine; spark's W4 files are untouched meanwhile, so the code stays as planned and the plan's line numbers drift only from other cards. Cost: the showcase has no fixed end, since the effect cards (TL-16) and the controls and sound (TL-28 to TL-34) are open-ended; wave 4 waits behind it · H · TL-24, TL-25
- TL-36 · (b) Refactor first. Wave 4 is three open PRs and a spike (TL-26: about 700 product lines and 700 test lines for W4-2 and W4-3). It needs the full council for W4-4 and PO merges for rules changes. The pixel-games drafts #10, #44, #46 wait with a growing rebase distance on the engine pointer; P647's prototype and its PO pick wait too · H · TL-12 to TL-14, TL-26
- TL-37 · (c) Interleave. The two lines touch disjoint files (SP/scripts/deploy*.py, tests vs PG/games, PG/engine). Worktrees make parallel PRs possible, as W4-2 and W4-4 were already planned. Cost: the PO's review and play time is the shared resource (the board's limits are 2 per working stage, 4 in flight), and a feel slice stops at "ready to play" until he plays it · E · SP/CLAUDE.local.md Board; D · PO 2026-11-03 Q12 (feel slices wait for the PO, from memory file)
- TL-38 · The finish line for a showcase: no card says what "nice demonstrable state" means. A candidate from the facts: all effect scenes smoke-pass on the current image (TL-9), the 3 drafts closed or parked, and one game on the buttons using an effect (Runner on fire P651 #874, or pinball P615 #821) · H · my proposal, not a PO word
- TL-39 · The risk of a showcase first is also external: the README says pixel-games is "a log of how the games got smooth", and the spark side of the story ("built by talking to Claude with spark") lives on P652 #875; I did not read #875 or #876 · E · PG/README.md:3-5; — for #875/#876 bodies

## 2. What you could not check

- I did not read issue bodies for #848, #829, #858, #802, #870, #872, #871, #782 (P581 buzzer), #874; I used titles only (the gh budget). State of P581 #782 is unknown.
- I did not flash or run the board. No bench row is mine; all numbers come from bench.md.
- The per-game fps for Snake, Cave, Tunnel, Road, Starfire, CubeTiming, GravityPong: not found. Run107's range 22 to 25 fps is for all fourteen together.
- Whether branch p582-heavy still merges or rebases cleanly over P633/P632: not tried.
- Whether the P647 engine commit ab970c4 is pushed: `gh pr list` on pixel-engine printed nothing; I did not check remote branches.
- Free GPIO pins and the DFR0664's own buttons or SD slot: the spark board record was not read. The SD_CS pin in pins.py suggests an SD slot exists; unverified.
- Whether wave 4's line numbers hold per file (deploy.py, deploy_service.py, fakes.py, test_deploy_gate.py): I confirmed W4-1's shapes and the absence of W4-2 to W4-4 shapes, not the individual line numbers.
- #94's thread for the PO's "Finish wave 4 first" (2026-11-04): I did not read it; I rely on the task text.
- The refactor plan's wave 5 and 6 and P417's readiness: not read.
- Open spark PRs: `gh pr list` printed no lines; I did not see an error either, but I did not confirm it with a second call.

## 3. Questions for the PO

- What shows that the showcase is "nice demonstrable"? Name the games and effects, or accept a list I propose (TL-38) · decides where (a) stops, and so how long wave 4 waits.
- Do you want the Runner on fire (P651 #874) or pinball (P615 #821) as the demo game, or the existing scenes only? · decides whether the engine cards P634 #848 and P640 #858 sit on the showcase path or not.
- Does sound mean a buzzer (one pin, tones on hits) or real samples (an amp and I2S)? And does a second button or a joystick come before sound? · decides the hardware, whether the spark chain is exercised on stage, and the size of TL-32/TL-33.
- Should the three drafts be finished, parked or closed: #10 (heavy RENT floors, paused since 2026-11-03), #44 (flow prototype, waits on your clip pick and an engine PR), #46 (fluid layer, paused at step 5)? · decides how much rebase debt the showcase carries.
- Is "Finish wave 4 first" (2026-11-04) still your order, now that you want the demo first? And if yes, does it hold for PR A P605 #807 and P417 #545 too, or only for the deploy/grant/live/reach moves? · decides the order in (b) and (c).
- May the council propose a split, a PR A + PR B step in parallel with one showcase slice at a time, given the board's limits? · decides whether (c) is allowed.
