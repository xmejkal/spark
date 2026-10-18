# Round 2: PO assistant (Opus)

> The order is right and the MVP line after the walk is right. Fix one contradiction (the token), three wrong
> dependencies, and add two small cards he asked for in his own words: the page look ("dark colors") and the
> variant on the walk-1 project. Rewrite titles as problem then fix, and the choices as concrete bench questions.

## Order and MVP line

1. **The MVP is still one step too strict.** Item 6 ties walk 1 to `/spark:deploy` (M), and choice 3 hides the
   fallback. He said "let's also not get stuck too much". Fix: split item 6. 6a is the walk with plain `deploy.py`
   after items 1-4 (Claude reads its text). 6b is `/spark:deploy` after item 5, used on the second deploy if ready.
   Flip choice 3's default to "walk without waiting".
2. **Item 18 is part of item 1.** Item 1 already copies facts from `xiao-esp32-c6-fresh`; making the two records agree
   is the same diff. Fix: fold 18 into 1's done-when ("the fixture and the shipped record agree on all copied and
   cited facts"). One card fewer.
3. **Item 19 (jumper check) sits behind the drag (15), but the PO wires from that picture at walk 1.** A wrong
   jumper on the sheet costs the bench. Fix: depend on 2, place it right after 2 if S holds; else keep after the
   line with depends "2".
4. **Item 16 (live view) depends on 15 (drag), which it does not need.** Fix: depends "14". Two L items no longer chain.
5. **Item 21 (variant) waits for the RC car (L).** "All the way, the whole full end-to-end" can be proved on walk 1's
   project: "make a copy with a buzzer instead of the LED". Fix: depends "12, 13", test it on button + LED; the
   stepper car is its later example.

## Missing for him

6. **"Rebuild it now, but with the dark colors" has no card,** and the UX lens notes he dislikes today's look
   (`council/ux.md:98`). Fix: NEW after 14, "The page looks plain and has one theme, so give it a style Claude can
   change by words": "make it dark" changes one style setting, the rebuild keeps it, light and dark both read. S.
   Add to item 14's done-when: "the PO opens it and says it reads well".
7. **"I basically just watch it" has no done-when.** The Artifact republish is only in the vision text. Fix: item 14's
   done-when adds "after each build Claude republishes the page, and the PO sees the change land".
8. **Czech shops are absent.** Walk 1 uses parts he owns, so it is not a blocker. Fix: NEW after the line, S, "Buy
   lines name no shop, so name a Czech or EU one": a missing part's buy line names GME, Hadex, LaskaKit, Botland or
   TME with a price, from the record. Or fold into item 13 (the buzzer is the first part he may buy).

## Contradiction

9. **Item 10 says the token is "readable only by him"; choice 4 says "readable by any agent with store access".**
   Fix: pick one in the table (file mode 600 in the store, which agents can still read) and phrase choice 4 as below.

## Wording

10. **Titles name the fix only.** The ask is problem, then fix. Fix, for example: 1 "The XIAO record stops at the
    schematic, so copy its five power facts"; 2 "Steps say 'a free row', so name each hole"; 3 "A rebuild moves jumpers
    without a word, so print what to change"; 4 "The first deploy connect fails, so retry once"; 8 "Claude reads the
    scenario verdict from text, so add `--json`".
11. **Item 1's done-when is not in his terms.** Fix: lead with "Claude builds a button + LED project on the XIAO with
    no stop", then the command. Item 6's "both board logs show it" is vague: say "each board log shows the press".
12. **Line 23 "see the end of this section after the fix" is a placeholder.** Fix: fill it with what round 2 changed.

## Choices as concrete bench questions (one at a time)

13. Fix: rewrite them, for example:
    - (2) "You sit at the bench and the sheet says 'a wire in a free row'. Wait two S cards for '15j', or wire now?"
    - (4) "Claude needs your Wokwi token at each simulation. Keep it in the store, where any spark agent can read it,
      or type it once per session?"
    - (5) "No token, and the stand-in simulator passes. Should Claude flash your board, saying 'stand-in only'?"
    - (6) "Claude asks you to type a yes before deploy and again before live serial. One yes per session for both?"
      This one names no item; make it a card or drop it.
