# P653 vote: PO assistant (product value and the PO's goals), 2026-11-06

I vote for the PO at his request ("have the po ssist and tech lead vote for me"). My lens is the CV, the demo and his
joy in the project. Tags: E is evidence with a pointer. H is a hypothesis with its source. The PO's newest words weigh
most: "we can also do some other cool fire games, but I also want the sound soon" and "And the joystick maybe, some
flamethrower game". Where the tech lead and I split on Q1, Q2, Q4 or Q6, this vote counts. Nothing here is decided until
the PO confirms.

## What the new words change

- Sound moves from stage 2 into the games lane. The README put it "after the main line" (README.md, Stage 2). His word
  "soon" outranks that. The spark share is small: one part record, one requirements line and a new `pins.py` (E, README.md
  Stage 2).
- The joystick and the speaker are both new hardware. They share one spark walk (parts, pin map, build, breadboard sheet)
  and one shop order. Two walks cost two orders and two waits. One walk is also the best spark story: "I added two
  modules and spark wired both" (H, product-demo.md:108, PS-19).
- The flamethrower game needs the joystick. A joystick aims the flame, and the one button fires it. Today every game
  uses one button (E, PS-18), so no existing game can show a flame in a direction.
- Fire games with no new hardware stay first, because they work now. P651 #874 (Runner on fire) is the first.
- The main line keeps its place. He wrote "we need to finish the refactoring" on 2026-11-06 and "Finish wave 4 first" on
  2026-11-04 (E, README.md words table). Sound, joystick and fire games ride beside it, one card at a time.

## Games lane, the order of cards (one in flight at a time)

1. Smoke run of all 14 games on today's image, with one bench row (TL-9). It is XS and every later clip rests on it. The
   last run was 2026-11-04 (E, bench.md:475).
2. P651 #874, the Runner on fire, with fps measured first (TL-17, PS-12). It needs no new hardware.
3. Refine P581 #782 into one hardware card: an I2S amplifier with a small speaker, plus a joystick. Look in the drawer
   first (`/spark:drawer`). This is a conversation and costs no flight slot. Then place one shop order for both parts.
   Pick a Czech shop (GME, Hadex, LaskaKit, Botland, TME).
4. P625 #838, a spark burst on a hit in a flat game. It needs no hardware, so it fills the days while the order ships.
5. One spark walk for both modules: part records, requirements lines, new `pins.py`, build, sheet, deploy. Slice 1 of the
   sound is one tone cue in the Runner. Slice 1 of the joystick is a test scene that reads it.
6. The flamethrower game (a new card, to file in Idea). The joystick aims and the button fires a flame at targets. Measure
   its fps first, since fire in the burning scene costs a lot (E, PS-12: step 7.91 to 8.06 ms, draw 13.21 to 13.78 ms).
7. Story page v1 in pixel-games, with Mac renders from `tools/render_scene.py` (E, PS-8). Page v2 adds the clips of the
   fire games with sound. The CV needs the page. A page with the fire games and the sound is stronger, so v1 stays small
   and v2 follows the games.
8. Sound slice 2, the synthesized fire crackle. A C kernel fills the buffer, Python starts it and I2S streams it by DMA
   (H, README.md Stage 2, model knowledge, not read). Then P626 #839, ESP-NOW and a second player.

Cards 1 to 4 can start now. From card 5 onward, a lane card starts only when no main-line PR waits on his review (see Q3).

## The seven votes

**Q1. Spark as the main line with one games card at a time beside it, or the demo first?**
Vote: spark is the main line (wave 4, then P417 LangGraph, then P419 RAG). The games lane runs beside it with the order
above. Why: the CV goal needs P417 and P417 needs wave 4 (E, README.md). He wrote "finish the refactoring" twice. The lane
keeps the fire games, the sound and the joystick alive, so the project stays fun. What changes my vote: a CV date
inside about three weeks that wave 4 cannot meet. Then P417 takes a thin slice before PR C and PR D. A second change: he
asks for one week of play and sound first. Then the lane goes first for that week.

**Q2. Is the games lane's checklist the finish line?**
Vote: yes, with two changes. Add "one sound cue and one joystick read on a fire game" after item 3. Reword item 4 so that
it blocks only non-fire games. Why: the finish line must hold what he named twice (E, spark #875 words). What changes
my vote: the parts are not in the drawer and the shop delay is long. Then the cue and the joystick leave the finish line
and stay as cards.

**Q3. By what date must spark show LangGraph and RAG?**
Vote: I invent no date. Default until he names one: the main line never waits for the lane. A lane card from item 5 on
starts only when no wave 4, P417 or P419 PR waits on his review. When one opens, the card pauses. His review and play time is the
shared resource (README.md, games lane). What changes my vote: a real date. Then count back. If fewer than two weeks
remain per card, the lane stops fully.

**Q4. Are the burning people (P635 to P637) in a demo for an employer?**
Vote: no. Move #850 from Ready to Idea and keep the cards. Why: he called the subject "nicely controversial" (E, PS-13).
These cards are feel slices that stop for his play (E, memory: feel slices wait for the PO). The flamethrower game and the
Runner on fire already give a strong, safe clip. What changes my vote: the demo is for friends and not for an
employer. A second change: an employer-safe variant, for example burning boxes with no faces.

**Q5. P622 #829 and P640 #858: keep in Ready or move to Idea?**
Vote: move both to Idea. Why: neither changes what a viewer sees (PS-16). Ready holds 5 cards at most, so two free slots
let the hardware card and the flamethrower card enter. What changes my vote: a bench finding that the Runner on fire
misses 25 fps only because of one of these two cards. Then that card returns.

**Q6. Who reads the story page first: an employer who reads, or someone who watches a clip?**
Vote: the reader. Page first, with two or three pictures, and one clip near the top once the fire games and the sound
exist. Why: a CV link is opened by a person who skims for two minutes. Text with a picture works with no sound and no
player (H, I have no data on his reader). Today there is no entry page at all (E, PS-6). What changes my vote: he
names a viewer who watches first, such as a meetup or a social post. Then a 30-second clip with sound leads.

**Q7. Sound: buzzer cues as P581 says, or a synthesized fire sound through a speaker?**
Vote: the speaker, synthesized. Refine #782 to an I2S amplifier and a small speaker, bought together with the joystick.
Slice 1 is a one-tone cue. Slice 2 is the fire crackle. Why: he said "I'm looking forward to synthesising the fire sounds"
and "using the s3's chip's advantages too" (E, spark #875). A piezo buzzer gets thrown away. What changes my vote:
the shop delay is over about two weeks. Then a buzzer cue goes first, so that something works sooner.

## What I could not check

- Whether an I2S amplifier, a speaker or a joystick is in his drawer. Run `/spark:drawer` before card 3.
- Whether the engine sends hit events to Python (PS section 5 calls this a hypothesis). One look at the engine code
  settles it before the first sound cue.
- The fps cost of fire in the Runner and in the flamethrower. Cards 2 and 6 measure it first and can change card 4.
- Whether the ESP32-S3 board has enough free pins for a speaker (I2S) and a joystick (two analog inputs) beside the
  screen. The spark pin map answers this in card 5.
