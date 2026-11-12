# P653 the games demo and spark's refactor: rows

What the three council lenses, the refuter and the PO's words in the session found. Card:
[P653 #876](https://github.com/xmejkal/spark/issues/876) under [P652 #875](https://github.com/xmejkal/spark/issues/875).
Also covers the paused P649 discovery (draft https://github.com/xmejkal/pixel-games/pull/46).

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The first synthesis put wave 4 last, against the PO's "Finish wave 4 first" (11-04) and "we're actually manily working on spark" (11-06), and against the job goal | the refuter (Fable) | acted | the refuter's rival order is now the proposal: spark main line, one games card beside |
| 2 | Stage 2 (C sound kernel, I2S, PIE) is pixel-engine work labelled spark work. spark's share is one part, one requirements line, one pin map | the refuter | acted | stage 2 says so, and the rebuild with spark alone is named as the walk that serves spark's bar |
| 3 | A sound card already exists: P581 #782, a piezo buzzer for cues on hits and deaths | the refuter, from TL-31 | acted | stage 2 starts from #782. Q7 asks buzzer or synthesized sound |
| 4 | The rain's 24 to 25 against 8 to 9 fps sits at bench.md:398-399, not :262, and the Python HUD label lowers its fps slightly | the refuter | acted | the table cites :398-399 with the caveat |
| 5 | "The games work at 22 to 25 fps" was run107 of all 14 on 2026-11-04, not today's image. the burning bodies miss D5 in both modes | the refuter | acted | the short version and the table say so |
| 6 | "11 against 4" is stronger than LF-2, because epics count in no stage and the epics are not marked | the refuter | acted | stage 0 marks the epics first. the count stays unknown |
| 7 | Flappy with fire exists (PS-10) | the product lens | rejected | TL-7: the PO removed it on 2026-11-04 (bench.md:441-456) |
| 8 | `gh project item-list --limit 400` drops cards past 400 of 535 without a warning | the lean flow lens | closed | a board count must use `--limit 1000`. proposed as a learned rule — P776: stale note: Learned rule on gh limit. |
| 9 | No card exists for W4-2 onward, so "finish wave 4" cannot be measured | the lean flow lens | acted | the main line files W4-2 first |
| 10 | The wave 4 plan's line numbers are stale (planned on 67c37600, 2026-11-01). its shape still holds | the tech lead | acted | the main line refreshes the plan first |
| 11 | No photo, GIF or clip of the board exists in either repository | the product lens | acted | the games lane's story page needs pictures |
| 12 | "Uses the S3's optimizations" holds for DMA and PSRAM, not PIE. the C driver and engine were built outside spark's chain | the product lens | acted | the story page's claims, games lane item 1 |
| 13 | The job goal: spark presentable for an AI developer CV, with LangGraph and RAG | the PO, 2026-11-06 | acted | P417 #545 and P419 #548 on the main line. memory updated. Q3 asks the date |
| 14 | Sound synthesis in C with the S3's strengths, and ESP-NOW multiplayer | the PO, 2026-11-06 | acted | stage 2 of the order. comments on #875 |
| 15 | P649: the two water cards read no velocity field, so a fluid layer serves gases, not water | the P649 lens (Sonnet) | closed | paused discovery, draft pixel-games #46. resume steps on #871 — P776: tracked by #46 (closed), #871 (open), P649 #871 (open) |
| 16 | The lens brief said the panel is "320x170-ish". it is 240 x 320 with a 160 x 120 field | the P649 lens | acted | a slip in Claude's prompt. the brief's Found on the way |
| 17 | "Lean flow and the tech lead also placed wave 4 before sound" is wrong. The tech lead took no side (TL-35 to TL-37) | the PR reviewer (Sonnet) | acted | README: "The tech lead took no side" |
| 18 | Three council reports hold home paths on line 3, against AGENTS.md's public-repo rule | the PR reviewer | acted | rewritten as `~/Development/...`. Scratch paths became "the session scratch folder" |
| 19 | Stage names, the epic guesses, "card #417, not P417", the wave 4 count, the 165-test cite, two long sentences, the refuter's README version | the PR reviewer | acted | all fixed in README.md and council/refuter.md |
| 20 | The drawer holds two MAX98357 I2S amplifiers, two 3 W speakers and two PS2 joysticks. One amplifier and one speaker are used in plant-alarm, so one of each is free. No shop order unless the pin check fails | the tech lead's vote (Sonnet) | acted | sound and the joystick move into the games lane. P581 #782 refined |
| 21 | The PO assistant's vote planned a shop order for the speaker and the joystick | the PO assistant's vote (Sonnet) | rejected | row 20: the parts are in the drawer |
| 22 | The votes answer Q1 to Q7: spark main line, games lane with sound, joystick and a flamethrower game, P635, P622 and P640 to Idea | both votes, for the PO | acted | README "The answers". Board moves done, P654 #878 filed |
| 23 | The answers contradicted the short version, the diagram, the old games lane and stage 2. "Two of each" hid that one amplifier and one speaker are in plant-alarm. The Q2 edits, the fps and bench-row clauses and the Mac test were dropped | the answers reviewer (Sonnet) | acted | the answers are the one source. The old lane points to them. Stage 2 holds a second button and ESP-NOW. Dropped vote items are listed |
