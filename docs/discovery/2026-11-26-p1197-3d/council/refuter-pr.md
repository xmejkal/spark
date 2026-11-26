# P1197: the second refuter, on PR #1798

Read on 2026-11-26, at HEAD 1ef1f2d5, against a08a4eb5 and origin/main. Experiments ran in a scratch folder under /tmp,
removed at the end. I wrote nothing else in the tree or the store. The T1 folder is ~/.local/share/spark/t1-step-2026-11-26/.

## Part A: what changed since a08a4eb5

### RP-1 · must fix before merge · T1 as the brief describes it is not the T1 that the PO holds

Sentence (brief.md:115): "The facilitator prepares three STEP files of one probe board: tscircuit's with JSCAD bodies,
kicad-cli's assembly, and one from a small STEP writer written again in scratch (★C20 (boxes only))."

What I found:
- The folder holds two files, not three, of the real amplifier fixture, not a probe board (README.md:3-5, :14-15).
- The tscircuit file's bodies are plain boxes that replace the header pins (README.md:21-22). My read of its solids:
  `Mcu` 25.4 x 60.0 x 1.6 mm, z 0.8 to 2.4, with the board top at 0.8. No pin row exists in any solid.
- D13 Q13 chose "a union of the record's box and its pin row". The architect made that a condition: "T1's JSCAD file
  uses that plan" (council/delegated-architect.md:9). The PO assistant did too: "T1's first file carries the form that
  #1729 will write, a box plus the pin row, so the test covers what ships" (council/delegated-po-assistant.md:9).
- The files went to the PO at 17:25 CET (risks-and-tests.md:47). D13 was recorded at 17:27 CET. So T1 cannot carry D13's form.
- #1804 says T1's results "confirm or turn the delegated answers to Q13". A T1 pass on box-only bodies cannot confirm a union.
- risks-and-tests.md:32 (A3) still says "he imports three files (tscircuit with JSCAD bodies, ...)". Its own
  collection row (:47) says two.

Smallest fix: change the sentence to "two STEP files of the amplifier fixture: tscircuit's with box bodies and no pin
row, made before D13, and kicad-cli's assembly. The third is not made." Add to D13 Q13: "T1's file does not carry the
union, so T1 tests names and units, not Q13's chosen form." Or remake the tscircuit file with the union. Fix A3's test cell.

### RP-2 · must fix before merge · D13 drops conditions and one split that the seat files hold

D13 (brief.md:149-156) reads as seven clean majorities. The seat files hold more:
- Q13: the two T1 conditions of RP-1 are dropped.
- Q16: the seats split on what a T2 miss does. The architect: "A miss turns Q16 to (b) or (c)"
  (council/delegated-architect.md:15). The PO assistant: "If T2 misses, `make-case` waits and the case goes to Claude in
  Fusion ... It does not fall to (b) by itself" (council/delegated-po-assistant.md:15). D13 records neither. risks A7
  carries only the architect's.
- Q16: the tech lead's change "the solver's plan never goes through `tsci export` for the print file" is dropped.
- Q18: the tech lead's "Measure one fixture build with and without bodies before merge"
  (council/delegated-tech-lead.md:21) is dropped. The #1729 section on GitHub lacks it too. The Frame's must-not-get-worse
  line says "the build time stays".
- Q17: "made manifold with `@jscad/modeling`'s `generalize`" is the tech lead's alone. His evidence is PrusaSlicer
  `--info`, and he writes "`--info` is not a print, and T2 is the proof". D13 and P1250 #1807 ("one manifold STL")
  state it with no caveat.

D13 does match the seat files on the choices and the counts. Q9, Q13 to Q16 and Q18 are 3 of 3. Q17 is 2 of 3. All
three seats say "Fable". D13 is recorded as delegated and his to change.

Smallest fix: one more clause per question in D13: the two T1 conditions (Q13), the split on a T2 miss (Q16), the
build-time measurement (Q18), and "manifold by `--info`, not printed" (Q17).

### RP-3 · should fix · header lines and rows that the later D rows made untrue

- brief.md:12: "his yes to items.md, and the viewer (Q11)". D14 answered Q11. D16 answered items.md.
- brief.md:11: "(unrated until Q1)". Q1 is marked answered (D9). See RP-4.
- brief.md:175: "not yet: the frame, the jobs, a direction and the remaining risk are unconfirmed". D1 confirms the
  frame and D5 a direction. The comment on #1745 says "Discovery done".
- brief.md:169: "set Waiting on: the PO ... while round 1 waits · pending". Round 1 ended at 16:18 CET.
- brief.md:114: "its test T2 runs only if he wants a case that spark makes (Q8)". brief.md:115: "If he wants a case from
  spark (Q8), test T2 follows". D6 and D8 settled both.
- brief.md:140 (D4): "the model goes into round 3 to confirm". It went into round 4 (Q20, D15).
- brief.md:125 (Q7): "(21.7 or 27.7 mm on the amplifier board, PHY-2)". ★C19 now says 20 to 22 and 26 to 28 mm.
- brief.md:163 (C30): "caveat: ★C24 (is not used) names 2.6.1 only". ★C24 now names 2.9.0 beside 2.6.1.

Smallest fix: update each line to the D that answered it.

### RP-4 · should fix · Q1 and the risk ratings are stronger than D9

D9's options were "A3 only, A3 and A2, all four, other". They cover A1 to A4. A5 to A10 still read "— (decider)"
(risks-and-tests.md:34-40). So Q1, "How important is each assumption", is answered for four of ten. D9 says "A1, A2 and A4
are not high". risks-and-tests.md:32-35 writes "low D9". "Not high" is not "low".

Smallest fix: Q1's status "answered D9 for A1 to A4. A5 to A10 unrated". Write "not high D9" in A1, A2 and A4.

### RP-5 · should fix · the In short drops D5's caveat, and ★C34 leans on a decision made before it

Sentence (brief.md:14): "The PO chose the order (D5, D6, D8): tests T1 ... and T2 ... first, then a box body per module
with a STEP export, and spark's own case Operation only if the test print fits."

D5 says "Options (d) and (e) of the refuter's addendum were not shown to him". The In short drops this.

★C34's caveat reads "the frame already places the epic after the MVP (D1)". D1 was recorded at 16:18 CET in a08a4eb5.
★C34 entered in 2f253895, after it. The vision's v0.10 row puts "with the PCB and 3D model on request" in the basic
journey (scrum/VISION.md:67).

Strongest rival not ruled out: option (d). It is the box body and the STEP export with no case Operation, which is the
same as what D5 plus D8 build now. D10 offered "the whole epic waits" and he declined it, so (e) is partly answered.
(d) was never put to him.

Smallest fix: add "options (d) and (e) were not shown (D5)" to the In short. In ★C34's caveat, add "D1 was given
before this claim was found".

### RP-6 · should fix · ★C35 and ★C36: what holds, and what has no evidence

Holds, reproduced by me:
- Four `DIRECTION('',(NaN,NaN,0.))` lines at 1235, 1236, 1257 and 1258.
- occt-import-js prints "ERR StepFile : Incorrect Syntax : Fails Count : 8".
- The two sha256 values match README.md:57-58.
- The box solids measure 18.0 x 18.0 x 7.1 mm and 25.4 x 60.0 x 1.6 mm.
- The kicad file names `Max98357aDfr0954`, `SpeakerTerminal` and `board_PCB`, and has no FireBeetle.
- My trace of references: all four NaN directions belong to the solid named `PCB`, none to an added box.

No evidence:
- ★C35: "The board without added bodies has them too, and the small probe boards had none". README.md:19, the cited
  line, says neither. No file of the board without bodies is kept. verification.md:32 cites an occt run on it, in a
  deleted scratch folder. I could not reproduce it: `tsci export circuit.json -f step` on
  tests/data/breadboard/amplifier/dist/board/circuit.json failed with "Element type is invalid".
- ★C35's grep is stamped 17:22 CET. The file's mtime and the README's "made ... at 17:23 CET" are later. So the grep
  ran on another copy.
- ★C36: "because spark's generated FireBeetle footprint carries no model". This cause was not run. verification.md:33
  only greps names.

Not said anywhere: in the kicad file the amplifier is the product `dip12_w15.24mm`, a body of 14.0 x 15.7 x 5.0 mm, not
18 x 18 x 7.1. Its board is 1.51 mm thick, and the parts start at z 1.59. So the kicad file cannot pass "at real size"
for the amplifier.

Smallest fix: cite the PCB-solid trace for "the board has them". Mark "the board without added bodies" and "the probe
boards had none" as not kept (H). Add the DIP-12 stand-in to ★C36's caveat.

### RP-7 · note · the T1 pass line's size check reads back what spark wrote

Pass line: "the measure tool reads one body within 0.1 mm of its record". Each box is written from the record's
numbers. So a pass shows that Fusion keeps the unit, not "at real size" (A3). The FireBeetle box is the bare 1.6 mm
board, flat on the carrier, not in sockets (README.md:21-22, D7).

Nobody listed this: the tscircuit file's `SpeakerTerminal` solid is 5.9 x 4.5 x 15.4 mm, z -2.6 to 12.8. The kicad
file's `jst_ph_2` is 6.0 mm tall. D3 says he draws his case in Fusion around this file. He would see a terminal 12.8 mm
above the board.

Smallest fix: in A3 and the Riskiest line, write "at the record's size". Add the terminal's height as a caveat to ★C35.

### RP-8 · should fix · numbers with no unit, population or provenance

- brief.md:11 "10 H": ten of what. The template asks for assumptions.
- Q5 (a) "about 25 minutes of the PO and one print": no H tag. T1's README says about 10 minutes.
- ★C8 "26.6 MB with 889 solids" and Q13 (c) "DFRobot's FireBeetle file is 25 MB". 26.6 million bytes is 25.4 MiB. One
  file, two numbers, no stated unit base.
- ★C33 "162 faces to 0": the faces of which module, on which board. The tech lead's union probe counted "252 faces
  below the board, a box-only body left 72" on another board (council/delegated-tech-lead.md:11). verification.md:30
  says "the STEP's pin tails not counted again". So the brief states a half that this pass did not reproduce.
- The tech lead's "a depth of 27.7 mm ... which matches PHY-2" (council/delegated-tech-lead.md:17) used `topHeadroom`
  18.1, a number taken from PHY-2. The match is circular.
- The In short's "3 of 40 records" drops ★C1's population: one store, on 2026-11-26.

### RP-9 · should fix · the evidence files still say what the corrected claims replaced

- pre-analysis.md:5: "a 2D outline for 30 of 43 records". ★C1 says 34 of 40.
- pre-analysis.md:85: "about 54 x 42 x 15 mm". ★C5 says 56 x 42 x 15.4 mm.
- jobs-and-journeys.md:25 (J1): "3 of 43 records hold a body's overall height".
- verification.md:6: "at 16:20 to 16:32 CET". ★C35 and ★C36 ran at 17:21 to 17:22 CET.

## Part B: the PR as a docs change

### RP-10 · should fix · pointers that point at the wrong line

pre-analysis.md gained a line in its In short, so every pointer into it is off by one:
- ★C1 "pre-analysis.md:15" is blank. The count is at :16.
- ★C3 ":86" is the `stepUrl` row. The STL row is :87.
- ★C5 ":84" is the plain row. The enclosure row is :85.
- ★C4, ★C6 and C15 ":75" is blank. The probe starts at :76.
- ★C12 ":56" is blank.
- verification.md:13 ":90" is blank. The manifold line is :91.
- verification.md:19 ":72-73" should read :73-74.

Other wrong pointers:
- council/delegated-po-assistant.md cites D rows by old lines. brief.md:135 (D3) is now :139, :137 (D5) :141, :138
  (D6) :142, :140 (D8) :144, :141 (D9) :145, :142 (D10) :146 and :143 (D11) :147. ":109" for the no-gos is now :111.
- council/delegated-architect.md:9 cites `BUILD_MAKERS` at picture_makers.py:181-183. It is at :186.
- C29, C30 and C31 all cite council/synthesis.md:298, which is a section heading.

These held when I read them: P269 brief:108, scrum/VISION.md:67 and :70, docs/guide/words.md:11,
board_sections.py:135, :139-140, :240, :258-259 and :478, flow_codes.py:479 and :481, research.md:19, :21, :29 and :67,
tech-lead.md:13, :23, :41, :77 and :194, po-assistant.md:100 and :118, user.md:77, architecture.md:90, synthesis.md:15,
and refuter.md:18, :34, :43, :87, :95, :106, :125, :137, :163 and :188. The code pointers of the delegated seats also
held: never-assume.md:38, provenance.py:13, replies.py:317, board_records.py:473-474, record_kind.py:343 and :363,
tabbed_page.py:49, board_emitter.py:7 and :180, build_service.py:271, board_engine.py:23, footprint_emitter.py:308,
fab.py:74-75, fact-needs.json:15, store.py:537 and :574, and architecture_baseline.json:54. The tsci error "Board
dimensions not found" is at main.js:179964 in the toolchain, as cited.

Smallest fix: shift the pre-analysis pointers by one. Repoint the PO assistant's D pointers, or cite them by D number.

### RP-11 · should fix · the filed cards against items.md

These hold:
- #1804 to #1807 have parent #1745, the labels spike, chore, story and story, and board fields Status Idea and Slice
  "9 An enclosure" (read with `gh api graphql`).
- The sections appended to #1729 and #1727 match items.md's "what it adds" word for word.
- The comment on #1745 lists the eight cards of PA-16 and the later slices.

Mismatches:
- items.md:13 "for each of three files". #1804 says "each T1 file (two today ...)".
- items.md:19 "It decides Q13, Q16 and Q17". #1804 says "Its results confirm or turn the delegated answers ... (D13)".
- items.md:30 "P735 #1010 writes the same facts (C28)". D11 and #1805 say P735 writes the size, hole and opening facts
  and this epic only the heights. items.md contradicts D11.
- The #1745 comment says "Discovery done". brief.md:175 says the hand-off is "not yet" (RP-3).

Smallest fix: copy the card wording back into items.md:13, :19 and :30.

### RP-12 · note · D13 and D16 do not say what the PO was shown

D1 to D12, D14 and D15 each list the options shown. D13 does not say whether the seven answers were put to him. D16
says "Yes, file all" with its options, but not whether he saw items.md's text or a summary. items.md carries D13's
content: the union, the STL and the store path. So his yes in D16 may read as a yes to D13, and the brief does not
show that.

Smallest fix: D16 "shown: <what spark-main relayed>". D13 "not shown to the PO" or "shown in round 4", whichever holds.

### RP-13 · note · privacy and files

- No file holds an absolute home path, a token, a key, an e-mail address, a photo or a vendor file.
  The only non-text file in the diff is .outside-snapshot.json, which holds git hashes.
- Tilde paths to the PO's private sibling projects are present: brief.md:61 and verification.md:22
  (~/Development/smartbin-local), and council/user.md:5, :18, :30, :36 and :51 (~/Development/smartbin-local and
  ~/Development/spark-walks). origin/main already holds many ~/Development paths, so this follows practice. Whether
  "never commit a home path" covers ~ is the PO's call.
- Personal facts about the PO are present: his licence tier, printer, installed apps and versions, his country, and
  diary quotes. None is a secret.

## What I could not check

- The board without added bodies and the probe boards' NaN lines (RP-6): no file is kept, and my export failed.
- Whether the T1 tscircuit bodies were written as JSCAD plans or by another route. The STEP does not show it.
- The relayed messages of rounds 2 to 4. They are not in any file, so each D row's wording of his answer is unchecked.
- The Autodesk pages (★C10, ★C11) and anything in Fusion.

## Searches

none
