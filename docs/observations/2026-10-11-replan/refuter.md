# Refuter: the replan of 2026-10-11

Verified: the E citations; all 55 numbers are distinct and open.

**RF-1, blocker.** Item 6 depends on P187 (#136), which the replan parks. #138 says *"Depends on P187 (the chip-name table)"*, and C76 (6a) *"depends on C4"*, which is P187 (p158-plan.md:2675). Fix: drop P189 from 6b (the journey has one S3 board) and build 6a without C4.

**RF-2, fix.** Five open cards are placed nowhere:
- #13 P77, the PO's *"example still working"*
- #47 P113, npm installs into a parent folder
- #72 and #65
- #134 P185: 91 of 110 drawer entries have no function, and item 7 starts from his drawer.

That leaves 83 of 88 placed. Fix: place them.

**RF-3, fix.** The rule "two lenses" was not applied as stated:
- #81 and #128 were pruned by the PO and TL lenses, yet they sit in slice 2.
- #67 was named by the PO and TL lenses, yet it is listed as "one lens".
- TL kept #54.

Fix: restate the rule as applied.

**RF-4, fix.** The user lens (Q1) and TL (Q2) both asked whether a hobbyist needs a Wokwi account, and that question is gone. The v1 sentence now makes one mandatory. Fix: ask the PO.

**RF-5, fix.** Item 5a:
- `pins.py` holds pins, not behaviour, so asserting "press → LED" means spark emits behaviour.
- The `ready` print contract that stages 5 and 6 rely on is defined nowhere.
- #64's value line is about the motor example.

Fix: make 5a a harness that waits for `ready`, write the contract down, and let Claude write the behaviour.

**RF-6, fix.** Item 4 is four cards in one M:
- C79 depends on C20 and C72 and is gated by Q4 (p158-plan.md:2720, :411).
- It seeds at `--requirements`, not at init.
- "Exit 0, or one line per fact" can pass without exit 0.

Fix: one new card, "button-light `check_all` exits 0".

**RF-7, fix.** Board mechanics:
- Items 1–5 make up to 8 cards against Ready's limit of 5.
- No item has a slice, and README:112 requires one.
- *After v1* is not a Slice option (per `field-list`).
- STORY_MAP still puts the bin's slice 2 second.

Fix: count the cards, give each item a slice, and list the field and STORY_MAP edits among the questions.

**RF-8, fix.** "Not the simulation image" contradicts #144's value line (*"puts the built flash image … onto the board"*). RP4's "mis-flash" is an inference tagged E: lines 28-29 are constants, and both SKUs hold at least 4 MB. Fix: flag it as a change to #144, or flash the image that passed.

**RF-9, fix.** Item 1 is TL's J7, which TL placed after J1–J4. The replan moves it first, with no reason given. With tsci skipped it reads a prebuilt fixture, so it cannot answer "still working". It is also the parked P158's C11. Fix: cite C11 and drop the claim.

**RF-10, note.** No install stage. #66 is pruned and #47 and #72 are dropped, so only the PO's installed Mac is walked. Fix: add a stage 0, or state the assumption.

**RF-11, note.** P74 (#8) goes to slice 2, although the PO and TL lenses put it first and VISION names it. Fix: give the reason.

**RF-12, note.** Item 7 fixes round A's domain, which was the PO's open question (#6), and drops "predictions first". Fix: ask him.

**RF-13, note.** Item 6 is one behind the simulation, not two. Only the PO lens said "chip tables and mutation scoring". "B31 (#26)" lacks "bin".

**RF-14, note.** 68 bare numbers. Fix: cut "Where P192 goes", put the walk list on one line, and move the prune list, with titles, to observations.
