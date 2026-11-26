# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. One block per item; copy the
block for more. needed by: the decider's words, quoted. value proven by: a proof the decider can read.
status: proposed, or filed D<n>. -->

Four new cards and two extensions of existing cards, from the architect's synthesis (council/synthesis.md, "Proposed
items"). The later slices stay one line each on #1745, because plans shrink with distance (AGENTS.md). The P-numbers
are taken at filing time, after reading the highest one (P1239 on 2026-11-26).

## P1247: nobody opened a spark STEP in Fusion or printed a case from record facts, so every 3D choice rests on a guess → two tests in a scratch folder with dated pass lines
- type: spike <!-- REQUIRED:item-type -->
- needed by: "the whole thing openable in fusion and the user or ai could use it  and create the cover or other parts" (the PO, 2026-11-26, #1745) <!-- REQUIRED:needed-by -->
- value proven by: a finding file with his screenshot of Fusion's browser tree for each T1 file (three, in the store's t1-step-2026-11-26/ with its README, none from spark's own STEP writer, which does not exist), and a photo of his FireBeetle in the printed case with a calliper reading, each against its pass line <!-- REQUIRED:value-proven-by -->
- depends on: two sittings of the PO. He said yes to both tests and has callipers (D6). T1 runs first, on his Personal licence (D2) <!-- REQUIRED:depends-on -->
- status: filed D16, P1247 #1804 (2026-11-26) <!-- REQUIRED:item-status -->
- label (the repository's type label): spike <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1197 #1745 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): 9 An enclosure <!-- REQUIRED:spark-process:slice -->
- touches: #1745's cycle. It gives P277 #313 its first run ("open in Fusion 360 as a 3D model"). Its results confirm or turn the delegated answers to Q13, Q16 and Q17 (D13)

## P1248: "height" and "thickness" each mean two things in the records, and the z facts sit under seven keys → one word for each z fact in words.md, one rule in `record_kind`, and one question each in `fact-needs.json`
- type: chore <!-- REQUIRED:item-type -->
- needed by: "it would just be the best if every record had its 3d shape" (the PO, 2026-11-26, #1745) <!-- REQUIRED:needed-by -->
- value proven by: the words.md rows, and `parts.py --validate` naming the two store records whose `facts.thickness_mm` holds an overall height (DFR0205 and DFR0831) <!-- REQUIRED:value-proven-by -->
- depends on: nothing. The words are `z_max_mm` and `z_min_mm`, with z 0 at the top face of the part's own board (D13, delegated) <!-- REQUIRED:depends-on -->
- status: filed D16, P1248 #1805 (2026-11-26) <!-- REQUIRED:item-status -->
- label (the repository's type label): chore <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1197 #1745 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): 9 An enclosure <!-- REQUIRED:spark-process:slice -->
- touches: #1729 (it takes the naming of "a height fact" out of that card, and can be its first PR if the PO wants fewer cards). This epic writes only the height facts it needs, and P735 #1010 writes the size, hole and opening facts (D11). The store's records are his: the card names the keys to move and moves none

## Extend P1185 #1729 (no new card): a box from `body_mm`, with a height fact → the box comes from a `PartBodyMaker` chain with `BoxBodyMaker`, for each module and the Mcu
- type: story (as today) <!-- REQUIRED:item-type -->
- needed by: its own lines, and "everything on the PCB and also the perfboard has a good 3d model, or at least some similar enogh general shape" (the PO, 2026-11-26, #1745) <!-- REQUIRED:needed-by -->
- value proven by: the amplifier fixture's 3D tab shows three bodies at the records' sizes, and a record with no z fact gives a finding that names the field <!-- REQUIRED:value-proven-by -->
- depends on: the words chore. Not on #1728, under Q18 (a) <!-- REQUIRED:depends-on -->
- status: filed D16, edited, the section "From the P1197 discovery" (2026-11-26) <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): its parent stays P203 #163 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): 7 Perfboard to PCB (unchanged) <!-- REQUIRED:spark-process:slice -->
- what it adds: the body arrives resolved on each part, so `emit` gets no eighth parameter (C27). It never reads `body_of`'s 16 x 12 mm default (AR-18). `MakerUses` and `Decline` move to a neutral module first, with the old names kept as imports for one step (AR-2). The JSCAD plan is a union of the record's box and its pin row, and one function writes `cadModel` (D13, delegated). KiCad still loses the header body (★C33)

## Extend P1183 #1727 (no new card): `export-board` writes a DRC report, a render and a STEP → it also takes the forms `step` and `glb` from `tsci`, and checks every body first
- type: story (as today) <!-- REQUIRED:item-type -->
- needed by: its own lines, and "export to 3d, so a tool/strategy can open it, like fusion 360 or other free tools" (the PO, 2026-11-26, #1745) <!-- REQUIRED:needed-by -->
- value proven by: `export-board --json` on the amplifier fixture names each body with its maker and likeness, and a missing body file gives a finding, never an `ok` <!-- REQUIRED:value-proven-by -->
- depends on: #1729 extended <!-- REQUIRED:depends-on -->
- status: filed D16, edited, the section "From the P1197 discovery" (2026-11-26) <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): its parent stays P203 #163 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): 7 Perfboard to PCB (unchanged) <!-- REQUIRED:spark-process:slice -->
- what it adds: it widens `TscircuitExport`, with no third wrapper of `tsci` (AR-10). A body file is a local absolute path from the store, and a URL is refused, so the export declares no `fetches` (★C22, TL-9). The 3D outputs go into spark's `.gitignore` section (AR-19). The answer names each part that has a body in one form and none in the other, and each part with no z fact (D13, delegated). `kept_files.py` is at its 600-line limit, so the keep is split first (AR-20)

## P1249: a board's mechanical facts are spread over its record, each part's record and the placements, so Claude guesses a number for a case → one Value `BoardMechanics` and the Operation `show-board-mechanics`, with each missing number named and asked
- type: story <!-- REQUIRED:item-type -->
- needed by: "the user or ai could use it  and create the cover or other parts" (the PO, 2026-11-26, #1745), and "do you have all the details in the record?" (the PO, 2026-11-20, P934 diary, quoted in US-6) <!-- REQUIRED:needed-by -->
- value proven by: the JSON for his FireBeetle with each number's source, and one cold Claude run that asks for the missing fact and invents none (A9) <!-- REQUIRED:value-proven-by -->
- depends on: the words chore, the spike's T2, Q9. "How a module sits" (in sockets, D7) is one of its facts <!-- REQUIRED:depends-on -->
- status: filed D16, P1249 #1806 (2026-11-26) <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1197 #1745 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): 9 An enclosure <!-- REQUIRED:spark-process:slice -->
- touches: P735 #1010 (one owner for the facts, Q12). P1199 #1747 gives the perfboard's filler later

## P1250: the journey names a Case step with no Operation behind it → `make-case` behind a `CaseMaker` seam with one member, and each case number a named setting
- type: story <!-- REQUIRED:item-type -->
- needed by: "some basic cover would be created" and "allow for prining and exporting the 3d printer files for like verysimple cases" (the PO, 2026-11-26, #1745) <!-- REQUIRED:needed-by -->
- value proven by: the printed case for his FireBeetle fits (a photo and a calliper reading), and `FakeCaseMaker` runs through the same Operation in the tests <!-- REQUIRED:value-proven-by -->
- depends on: T2 passing, which the PO set as the condition (D8), and the mechanics card. Its first member is tscircuit's solver called direct, and its print form is one manifold STL per printed part (D13, delegated) <!-- REQUIRED:depends-on -->
- status: filed D16, P1250 #1807 (2026-11-26) <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P1197 #1745 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): 9 An enclosure <!-- REQUIRED:spark-process:slice -->
- touches: the `case` entry of `UNBUILT_STEPS` (`flow_codes.py:481`), README's "What works today" and `tools/journey.py` in the same PR

## Board actions
- file the four new cards as sub-issues of #1745 on the Slice "9 An enclosure", Status Idea · taken D16, 2026-11-26: P1247 #1804, P1248 #1805, P1249 #1806, P1250 #1807, each added to the board by this session <!-- REQUIRED:board-actions -->
- edit #1729 and #1727 with the lines above · taken D16, 2026-11-26, as an appended section on each
- on #1745: list the eight overlapping cards (brief C28) and add one line each for the later slices · taken D16, 2026-11-26, in the comment https://github.com/xmejkal/spark/issues/1745#issuecomment-7198054003
