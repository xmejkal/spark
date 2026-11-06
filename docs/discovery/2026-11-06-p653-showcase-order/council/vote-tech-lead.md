# P653 vote, tech lead (2026-11-06)

Tags: E seen, with a pointer. H hypothesis, with its source. Lens: feasibility, risk, technical direction. I vote for the PO; he can overrule any line.

## What changes the facts

- V-1 · He already owns the sound and joystick parts: MAX98357 I2S amplifier DFR0954 (count 2), stereo 3W 8 ohm speaker FIT0502 (count 2), analog joystick module PS2 style (count 2), I2S MEMS microphone SEN0526 (count 3), and a Bluetooth amplifier DFR0675-EN. DFR0954 and FIT0502 are marked used in project plant-alarm (1 each), so one of each is free · E · `~/.local/share/spark/drawer/dfrobot-dfr0954.json`, `dfrobot-fit0502.json`, `analog-joystick-module-ps2-style-5-pins-mh-on-the-board.json`
- V-2 · So "sound soon" needs no shop order and no wait of days. P581 #782 asks for a piezo buzzer, but a synthesized fire sound fits the owned amplifier and speaker better. This is the answer to Q7. The shop-order argument drops out. Spark's idea step would find these in the drawer and reserve them (store first) · E · AGENTS.md "what you own" via the drawer skill; H · my reading of spark:idea's description
- V-3 · One walk can serve both. Sound and the joystick are two parts, two requirements lines and one regenerated `pins.py`, in one `idea` to `build` pass. Both are input/output on one board, so one pin-map run avoids two regenerations and two PRs. The cost is one bigger review for the PO (a feel slice for each) · H · TL-29, TL-34 of council/tech-lead.md
- V-4 · Pins. Taken today: 0, 11, 12, 13, 14, 15, 16, 17, 21, 38, 47 · E · games/pins.py (TL-30). The I2S amplifier needs 3 pins (BCLK, LRC, DIN); the joystick needs 2 ADC pins and 1 digital pin for its push button. The S3's ADC1 channels sit on GPIO1 to 10, which the FireBeetle 2 S3 breaks out as the analog header; ADC2 collides with Wi-Fi and so with ESP-NOW. Use ADC1 pins for the stick. Which exact pins are free on this board I did not read from its record · H · model knowledge of ESP32-S3 ADC1/ADC2, not read; the board record `~/.local/share/spark/boards/` not read. The spark `build` pin-conflict check settles it in seconds
- V-5 · Risk of the joystick: every game is one-button (TL-29), so a joystick changes no existing game. It serves a new game (the flamethrower aiming) only. A flamethrower game is one game plus an input path, not 14 changes · H · TL-29
- V-6 · Risk of sound: RAM and the app partition. The image had 217 kB left (P602) before later growth, so a sample buffer must stay small. A synthesized sound (a C kernel fills a short buffer, I2S DMA streams it) needs no stored samples · E · bench.md:443 for the 217,312 B figure; H · the buffer size is my estimate
- V-7 · The PO's "flamethrower game" is the strongest answer to "other cool fire games": it uses the fire effect (P651 #874 is the Runner on fire), the joystick aims, and the amplifier gives the roar. One game then shows effect, input and sound together, which is the better demo clip · H · my synthesis of the PO's three phrases

## Votes

- Q1 · Spark as the main line (wave 4, then LangGraph and RAG), with one games card at a time beside it. Why: the PO said it on 11-04 and 11-06, and TL-37 shows the two lines touch disjoint files. The "one games card" must be the sound-and-joystick spark walk first, because it is short and spark's own journey (parts from the drawer, pin map, build), so it also counts as spark progress. Would change if: he says the demo clip is needed by a fixed date (then the games lane gets two cards at a time and review time is the limit).
- Q2 · Yes, with two changes. Add "a flamethrower game: joystick aims, fire effect, synthesized sound" as the last item, replacing the Runner on fire (P651 #874) as the one effect game, which stays as a fallback. Drop "no new games card enters Ready until 1 to 3 are met" for the sound-and-joystick walk only. Why: his three phrases point to this game. Would change if: the first board test of the I2S amplifier or the joystick fails on pins, then fall back to the Runner on fire.
- Q3 · Default: the main line (wave 4, then P417 LangGraph, then P419 RAG) never pauses for the games lane; the games lane pauses for the main line. I give no date. Why: the CV is the job goal (the PO 11-06), and wave 4 plus P417 is the longest chain (W4-2 about 700 lines, W4-3 about 650, TL-26) while the games cards are small. If he names a date, the order does not change, only which games card gets dropped. Would change if: he gives a date within two weeks, then P417 may start on W4-1's shapes without waiting for W4-2.
- Q4 · Move the burning people (P635 to P637, card #850) to Idea. Why: they are costly feel slices (council Not now table), and the flamethrower game replaces them as the fire showpiece without a person on fire. Would change if: he says he wants it in the employer demo anyway.
- Q5 · Move P622 #829 and P640 #858 to Idea. Why: the demo needs neither (TL-17), and Ready has a limit of 5, which the sound-and-joystick card and the story page need. Would change if: the flamethrower game needs a new scene list, so P640 becomes a blocker. I would then pull it back (H, I did not read the card bodies).
- Q6 · Page first, with one clip embedded at the top. Why: an employer reads a repository link first, and a page holds the clip and the evidence in one place. The first clip can be the flamethrower with its sound. Would change if: the CV link goes to a video host.
- Q7 · Synthesized fire sound through the owned MAX98357 amplifier and FIT0502 speaker, not a buzzer. Why: V-1 shows he owns the parts, the PO wrote "I'm looking forward to synthesising the fire sounds", and the S3's I2S with DMA is the reuse he named. Refine #782 to say this, with a buzzer cue as the first test only if the I2S path stalls. Would change if: the pin check finds fewer than 3 free pins beside the joystick, then use the buzzer on one PWM pin first.

## Where "sound soon", "fire games" and "joystick" change the order

1. After stage 0 and in parallel with PR A, add one card to the games lane: "sound and joystick walk". Steps: (a) the drawer check shows the parts (no order), (b) requirements lines for the amplifier, speaker and joystick, (c) regenerate `pins.py` and build, (d) a Mac stand-in test of the sound kernel, (e) a board bench row. This is the first sound step and is cheap.
2. Next games card: the flamethrower game, which waits for step 1 and the PO's play (feel slices wait for the PO, Q12 of 11-03).
3. The story page (Q6) goes in the games lane after the flamethrower, so it can use its clip.
4. Stage 2 keeps ESP-NOW and a second button. Sound and the joystick leave stage 2 and move up. Stage 1 gets heavier by one card; the board limit of 2 per working stage still holds.
5. One shop order is not needed today. If a part fails, the Czech and EU shops (GME, Hadex, LaskaKit, Botland, TME) take days, so the order is placed at the first fail, not before.

## Not checked

- The board record's free pins and the analog header's GPIO numbers on the FireBeetle 2 S3: not read.
- Whether the plant-alarm project still holds its amplifier and speaker (count 2, used 1 each): the drawer file says 1 is free.
- Issue bodies of #782 and #874: not read.
