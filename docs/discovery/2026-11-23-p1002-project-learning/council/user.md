# P1002 council: the user

The lens: the user's journey. Read on 2026-11-23, 14:50 to 15:25 Prague time. A path that starts with `store/` is
under `~/.local/share/spark/`. "The diary" is ~/Development/spark-walks/p934-display2/diary.md.

## Who

- U1, the builder at the bench. A person who wires a board and a module, runs a trial and sees the result with
  their own eyes. Today the one case is the PO in walk P934 (display2) · E · the diary · n = 1.
- U2a, the same person in a later project with the same board or module. This is the only second user today. Two
  of 27 listed projects name these records · E · a read of store/projects.json and of each requirements.json. No
  third project uses them yet (H).
- U2b, another person with spark and the same board. The store is one per person, in their home folder. P1002's
  scope keeps facts out of spark's library · E · scripts/spark/records/store.py:108-116 (the places under the home),
  the brief's scope line · supports: U2b never sees U1's kept facts in this card. U2b gets them only through a later
  promotion to the library (H).

## Jobs

- J1 (U1). After a trial shows what works, I want to keep the finding in one yes, with no JSON to write [D the PO
  2026-11-22, diary.md:275-276]. Then I go on with the gadget.
- J2 (U1). Before spark keeps it, I want to see the finding in my own words [D the PO 2026-11-23, #1461]. Then
  Claude's reading of my answer does not become a fact [E diary.md:368-370].
- J3 (U2a). At the start of a project with a known board, I want to see what earlier projects found, and on which
  setup [H from the risks below]. Then I skip a trial, and I do not trust a fact that does not fit my wiring.

## The journey of U1 today, with its friction

1. The session writes a trial. The PO flashes it and watches the panel · E · diary.md:262-273.
2. The PO says what he saw in the chat: "3 bars and 1 red block" · E · diary.md:268.
3. F1. He asks about the keeping himself. Spark does not offer it · E · diary.md:275-276 ("do they get to be stored
   about them?"), and again at 418.
4. The session runs a dry run of `--fact-set` and waits for his yes · E · diary.md:277-279.
5. F2. The record is another project's. The e-paper and the board files live in p934-epaper. He works in
   p934-display2. Each write waits on "the PO's yes (another project's record)" · E · diary.md:279 ·
   supports: U1 approves changes to a folder that is not the one open in front of him.
6. The write and the shelf copy's refresh · E · diary.md:286.

Friction found after the write:

- F3. Claude's words, not his, went into a source. At 13:12 the session wrote "You saw candidate 3 draw again". The
  PO never said so. The 13:14 source then said "both runs, as the person watched". The fix came at 14:08 · E ·
  diary.md:368-370, row 21.
- F4. A finding depended on his setup, not on the module. A battery stayed connected. So the 13:36 unplug of USB
  never cut the panel's power. The panel slept since about 13:08 · E · diary.md:412-413, 418-421.
- F5. A cause was open at the time of the write. The kept fact `deep_sleep_wake` says that the reset pulse on GPIO19
  does not wake the panel. Its cause is still open: "the wire on the pad SDA, the TXS0108E, or the pulse" · E ·
  diary.md:415, row 20.
- F6. A number changed with the content on the screen. The PO timed a redraw under 5 s at 16:32. His video at
  22:2x showed about 18 s for a picture with red · E · diary.md row 22, and the 22:2x entry · supports: a kept
  "redraw time" from 16:32 misleads the next project. Nobody kept it, by luck of the order.
- F7. Findings settle over hours. The 13:33 cause was wrong (corrected 14:03). The 20:02 note on the port was wrong
  (corrected 22:31) · E · diary.md:416-417, 491-495 · supports: the moment of the offer matters. An offer at each
  result keeps more wrong facts than an offer at the end of a session (H).
- F8. A stale copy already cost U1 once. A shelf copy with no `based_on` was never refreshed. So the drawn breadboard
  was missing while he wired · E · diary.md:186-200, row 10 (P1006, merged) · supports: two copies of one record
  drift, and the person pays for it at the bench.

What U1 can supply: what he saw, from a short fixed list. The P1003 pre-analysis proposes three answers: "3 bars
and 1 red block", "blank" and "something else" · E · `gh issue view 1462 --comments`. Whether a battery or other power is connected · E ·
diary.md:412. A yes or no per fact.

What U1 cannot supply: a current without a meter. The board record keeps `deep_sleep_current_ua` null for that
reason · E · store/shelf/boards/firebeetle2-esp32c6.json, `deep_sleep.deep_sleep_current_ua` ("not measured: no
meter"). The cause of a failure he only sees from outside (F5).

## The journey of U2a, with the kept facts of 2026-11-22 and 23

Where a kept fact helps:

- The board sleeps and the serial port disappears. `look.py` then finds no board, and BOOT with RESET brings it back.
  Without this, a sleeping board looks like a dead board · E · store/shelf/boards/firebeetle2-esp32c6.json,
  `deep_sleep.usb_while_asleep` · supports: a scare and a lost half hour saved (H).
- The e-paper draws with the IL0373 or UC8151 command set. The record's earlier guess (SSD1675A) drew nothing · E ·
  diary.md:270 ("The record guessed SSD1675A") · supports: the P1003 pre-analysis says this guess cost "a whole
  firmware cycle" (E #1462 comment).

Where a kept fact misleads:

- M1. The build. `light_sleep` says the chip resets, "Do not use lightsleep on this board with this build". The build
  is in the source as free text (MicroPython v1.29.0). `verified` is a plain true · E · the same record,
  `deep_sleep.light_sleep` · supports: a reader with another build sees a verified "do not use".
- M2. The board revision. DFRobot gives 16 uA for V1.0 and 36 uA for V1.2 in deep sleep · E · the same record,
  `deep_sleep.deep_sleep_current_ua.source` · supports: revisions differ. The kept bench facts do not name the
  revision of the PO's board (E, a read of the eight `deep_sleep` sources).
- M3. A lookalike module. MH-ET LIVE sells several 2.9 inch boards under one name with other panels. The record says
  it is "not true of those" · E · store/shelf/epaper-2in9-bwr-mh-et-live.json:6 · supports: U2a picks by name and
  photo. The kept driver fact then reaches a module it does not fit (H).
- M4. Two meanings of "verified". The e-paper record says "A verified: true fact here is a chip datasheet's own
  number". The bench facts of 2026-11-22 and 23 are also verified true · E · the same file, line 6, and
  `host_deep_sleep_ok` · supports: U2a cannot tell "seen once on one unit" from "the maker's sheet".
- M5. A value that claims more than the bench showed. `deep_sleep_wake` says "only a power cut wakes the panel".
  Its own source ends "Why the reset does not wake it (the wire, the TXS0108E or the pulse) was not found". It is
  verified true · E · store/shelf/epaper-2in9-bwr-mh-et-live.json, `facts.deep_sleep_wake` · supports: on another
  wiring the reset can work, and U2a skips a path that works (H).
- M6. A project with its own copy sees nothing new. A project's own board file wins over the shared one · E ·
  scripts/spark/records/board_records.py:35-38 · supports: p934-epaper still reads `deep_sleep: null` from its own
  copy (E, a read of ~/Development/spark-walks/p934-epaper/boards/firebeetle2-esp32c6.json).

Where U2a meets the fact: nowhere in spark today. No script reads a board's `deep_sleep` · E · `grep -rn deep_sleep
scripts/` · supports: U2a sees the fact only through Claude's read of the JSON file.

## Riskiest assumption

A fact that U1 saw on one bench setup holds for U2a's setup. The kept facts carry their setup only as free text in
the source (M1, M2). One of them has an open cause (F5). U2a has no way in spark to compare setups. Cheapest test, an
account with the PO (about 10 minutes). Show him the eight `deep_sleep` entries of the board and the e-paper's
four bench facts, as U2a gets them, with no diary. For each fact, he says "I trust it for my next project", "I
retest it" or "I do not know". Pass line (proposed, written 2026-11-23 before any result): at least 9 of 12 get
"trust" or "retest" from the record text alone. A "do not know" means the record lacks the setup.

## Options

- A · The offer at the end of a bench session, not at each result. One short list. Each line holds four things.
  First, the fact in plain words. Second, what the person saw, quoted in their own words, never Claude's summary.
  Third, the setup: power, wiring, firmware build and the board revision. Fourth, the old and the new value. The answers are keep, not now, or wrong. Cost: small
  on top of the writer the tech lead names. Proves: J1 and J2 with no misquote (F3).
- B · The fact shows where U2a needs it. A project picks a board or a module. Then spark's answer adds one line, for
  example "kept from p934-display2, 2026-11-23: 6 bench facts, MicroPython v1.29.0". A project with its own copy also
  sees that the shared record knows more (M5). Cost: one reader in the idea or build answer, about one story. Proves:
  J3, and it is the only option here that tests the reuse.

## What I could not check

- The p934-display2 issue #7 trial logs that the board facts cite. I did not open them.
- Whether U2a reads the record at all in a real project. No later project exists.
- The PO's board revision. Nothing I read names it.

## Questions for the decider

- Which moment do you want the offer at: after each finding, or once at the end of a bench session? · decides: how
  many wrong facts reach the review (F7).
- For a record that lives in another project's folder, is one yes for the store enough? · decides: F2, and where the
  write goes.
- Is "retest it" a kept state of its own, apart from verified and unverified? · decides: whether M4 needs a new field.

## Searches

none
