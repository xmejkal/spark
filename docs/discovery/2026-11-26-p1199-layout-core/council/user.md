# The user lens, with UX and AI-UX (P1199)

Opus, 2026-11-26. The lens agent is read-only, so it returned this report as text. The main session saved it
unchanged except for this header.

## Findings

**US-1 · The journeys mostly do not match the artefacts · E**
- The Wokwi round trip (maker steps 1 to 5) and Claude editing px (Claude step 3) only work for a board that Wokwi draws.
- A FireBeetle is drawn on the 63-column board as `breadboard.svg` alone, and keep moves never runs for it: scripts/spark/breadboard/sheet.py:306-307 and docs/guide/agents/scripts.md:200.
- Of the 23 project folders on the store's list that exist, 3 have a drawn breadboard. Only 1 has a `breadboard.json` (reaction-game). It was written by spark at 19:58 with the build, and git has 0 commits of it.
- The quote "move the LED two columns right" is not in #352. His real example there is the diode swapped for a buzzer.

**US-2 · Keep moves holds every earlier part in place, not only the ones the person moved · E**
- See kept_moves.py:175-184. A part that stays where it was is never named (:239-240).
- So if the person switches the goal after the first build, nothing changes and nothing says why.
- Smallest fix: keep only moves that were recorded as moves.

**US-3 · A rebuild can wipe out every move with no copy · E**
- When the kept plan has no room, or the file cannot be read, the build writes the fresh plan over `breadboard.json`: sheet.py:318-321, tests/test_breadboard_keep.py:266-283.
- `board.tsx` gets a copy in `.spark/previous` (build_record.py:156-167). `breadboard.json` gets none.

**US-4 · "Connect it to pin 20" is not a layout edit · E, H**
- A kept jumper never changes what is connected (kept_moves.py:13-17, :285-291).
- #311 note 1 keeps the pins the firmware was tested on.
- His sentence in #352 is a chain: find a part, pick it, set the pin, then place it. A layout Operation should take only holes and turns, and point a pin change to the design area (H, my reading).

**US-5 · Claude's words for a move exist today, but the codes for a refusal do not fit the core · E**
- The sheet already speaks the maker's hole names: "f49", "j20", "bottom + rail, hole 23" (p934-display2/breadboard.md:27-35). Inside the code the same hole is `49b.f`.
- A move needs: the part id, which pin goes in the hole, the hole, and the turn.
- `--move-hold` already has the answer shape to copy: a dry run first, then `--apply`; a refusal is `problems` with exit 1, nothing written, and `data.written`.
- The kept-moves codes (e.g. `row-shared`) are hyphenated plain strings with no fix, so `Finding.of` raises a TypeError on them (result.py:26-28, codes.py:34-35). The core's codes are snake_case `Code` objects.
- "Move" already means two other things: `--move-hold` (P1124) and the sheet's "Move the red jumper" (bench_changes.py:324).

**US-6 · The goal is measured in a unit the maker does not use · E, H**
- Brief outcome (2) measures mm². The maker thinks in holes across and down and the size to cut (#311 note 2).
- What the plan could show per goal: the cut size, the insulated jumpers, the bridges, the longest bare wire, and how often pads of two different nets sit side by side. That last one is H: it is my guess at a beginner's bridge risk.
- The perfboard screen sketch shows no goal choice and none of these (councils/past-breadboard/architect.md:91-105).
- The breadboard default must stay first fit, because the golden breadboards must keep their bytes.

**US-7 · The page cannot judge a drop by itself · E, H**
- P294 puts the drag layer on `breadboard.json`, but full-board projects have no such file.
- The page's clicks reach Claude only at the next turn (p1038 brief C19). The page got 5 clicks in 11 minutes, then he went back to the chat (★C12).
- So either each drop waits for Claude to run the Operation, or the page holds rules, which D24 forbids (no logic in the page).
- What stays in the page: the drag. What is an Operation: whether the place is allowed, and the move itself.

**US-8 · Taking back an older move can clash with a later one · E, H**
- The walk: move 1 puts the buzzer from e5 to e12. Move 2 puts the LED into e5. Taking back only move 1 is one of the two choices he asked for (words.md:23, the Undo artboard of 11-25). It sends the buzzer back to a hole the LED now holds.
- So the preview needs the keep check of the layout it would make, plus the bench rewiring it costs. He wires before he looks at the picture (p934-display2/diary.md:190).
- Moves become kept steps only at P1152 slice 5 (P1193 D6, items.md:60).

## What I could not check
- The canvas's Perfboard artboard: it needs a claude.ai sign-in, so I used the card's link only as a pointer.
- FIT0193's hole grid: its record has none. At most 39 × 29 holes at 2.54 mm (calculated, before margins).
- Whether wokwi.com needs an account.
- What he soldered before: no evidence; the e-paper diary's soldered header looks factory-made (p934-epaper/diary.md:19).

## Questions for the decider
1. Is a move a fact in a layout record (the part, its pin, the hole, the turn), or bytes of `breadboard.json`? · Decides US-2, US-3 and the words of US-8's preview · I would pick the fact.
2. When an older move's place is now taken by a later move, does the take-back refuse and name the clash, or take back both? · I would pick refuse, name it, and offer taking back both.
3. Which perfboard goal is the default: roomy or smallest? · I would pick roomy.
4. Account questions, past tense, n = 1:
   - Did you ever move a part in Wokwi and copy it back? I found no evidence.
   - Did you ever ask Claude to move a part? None in 7 walk diaries.
   - Did you ever use your FIT0193 × 2 or DFR0481 × 1? Neither drawer record holds holes across, holes down or pitch. The DFR0481 is a FireBeetle cover, so it cannot simply be cut smaller.
   - What did you solder before?

## Searches
None.
