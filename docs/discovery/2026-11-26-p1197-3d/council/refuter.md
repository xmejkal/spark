# P1197 3D: the refuter

Read on 2026-11-26 between about 16:05 and 16:40 CET. The brief changed while I worked. I started at commit 1bee61bb
and finished at a08a4eb5, which adds D1 to D4 (frame confirmed, Fusion licence "Personal, free", last case "Drew it in
Fusion", prints on "A Prusa"). I judge the brief at a08a4eb5. The probes ran in my own scratch folder with a
`package.json` and a `node_modules` link to the store's toolchain (`@tscircuit/cli` 0.1.2113, `tscircuit` 0.0.2600,
`@tscircuit/create-fdm-enclosure` 0.0.4), and with `kicad-cli` 10.0.6. Each probe ran once. The folder is deleted. I
installed and downloaded nothing. This file is the only one I wrote in the repository.

## Check first: does the change address the observed problem, and what breaks for current users?

The observed problem is the PO's request on #1745: a 3D shape per record, the board openable in Fusion, and a case
that Claude makes. D3 now says he drew his last case in Fusion himself.

- It addresses part of it. The recommended first built slice (#1729 box bodies, #1727 STEP export) gives him a STEP
  to model on in Fusion. D3 says that is how he works today. The case Operation (`make-case`) serves a path he has not
  reported using. "Claude makes the case in Fusion", his own words, sits in slice 4, last.
- **CONFIRMED, a regression nobody listed.** Q13 (a), the recommended body form, is a JSCAD `cadModel`. In my probe a
  JSCAD body replaces the module's built-in header model in both exports.
  - KiCad: the plain board's `kicad_zip` holds `(model "${KIPRJMOD}/3dmodels/tscircuit_builtin.3dshapes/pinrow10.step"`
    for the 10-pin module. With a JSCAD body on the same module, that line is gone. Only `pinrow4.step` stays. So
    KiCad's render and STEP lose the one body each module shows today. Q13 (a)'s caveat says KiCad shows "none until
    a STEP member exists". It does not say that KiCad loses what it has now.
  - tscircuit's STEP: the plain board has 162 faces below the board under the module (the pin tails). With the JSCAD
    body it has 0. The header pins vanish. The synthesis's own caution (the C6's soldered pins reach below the board,
    so the standoff may be too small) needs exactly that geometry.
  - Smallest fix: Q13 (a)'s caveat names both losses, and #1729's extension keeps the header. One way is a JSCAD union
    of the record's box and the pin row. Another is a body only above the board with the footprint's pins kept. Which
    one works was not run.
- **CONFIRMED.** A missing model file makes the two exports of one board disagree, both with exit 0. The STEP has no
  `U1` (solids `PCB` and `U2`). The GLB of the same board has a node `U1`, a generic box of 24.4 x 2 x 1.5 mm. A
  reader of the GLB sees a body that the STEP lacks. Smallest fix: ★C22's caveat says so, and #1727's model check
  covers every form, not only STEP.
- **CONFIRMED.** `<enclosure.fdm.box />` placed inside `<board>` exports with exit 0 and no case at all. The STEP was
  1,052,409 bytes, the same as the board with no element. The case appears only inside `<assembly.device>` with
  `boardRef=".B1"`, as the package README shows. This is one more silent failure for Claude's journey step 3. Smallest
  fix: one line in ★C5's caveat.
- Not run: whether a board with bodies slows the build (A6), and how many goldens and fixtures change when
  `board.tsx` gains a `cadModel` per part.

## 1. The ★ claims

- **★C1 · partly.** pre-analysis.md:15: "The count covers every record with pins, a kind or a `physical` block: 12 in
  the repository (`parts/`, `boards/`, `chips/`), and 31 in the store's `catalog/`, `boards/`, `known-boards/` and
  `shelf/`." My scan with the same rule finds 43 files. Three of them are Wokwi chip definitions, matched only because
  they carry `pins`: `parts/l9110s-module/chip/l9110s.chip.json`, `parts/vl6180x-breakout/chip/vl6180x.chip.json` and
  the store's `shelf/sen0217-flow-meter/chip/flowmeter.chip.json`. `chips/` holds no JSON. So the population is 40
  part and board records. 30 hold `body_mm`, and the 4 board records hold `physical.width_mm` and `height_mm`. So 34 of
  40 hold an outline in the board plane, not 30 of 43. The 3 with an overall height as a field hold (DFR0205, DFR0831,
  MKDS). The seven z keys and the two meanings of `thickness_mm` hold. The In short's "3 of 43 records say how far a
  part stands above its board" is stronger than PHY-1. PHY-1 lists at least four more that say it in a note (MAX98357A
  7.1 mm, VL6180X 1.2 mm, the LED 8.6 mm, WJ500V 14.0 mm). Change to: "3 of 40 part and board records hold a body's
  height above the board as a field, and at least 4 more state it only in a note. 34 of 40 hold an outline in the
  board plane."
- **★C2 · partly.** board_sections.py:258-259: `lines.append('    <chip name="%s" footprint="%s" pcbX={%g} pcbY={%g}'`
  and `% (name, part["footprint"], *placements[name]))`. No `cadModel` holds. The footprint is not always `pinrowN`.
  It is the record's own string: the repository's parts use `pinrow10`, `pinrow7`, `pinrow2`, `headermodule6`,
  `dip12_w15.24mm`, `jst_ph_2` and `pushbutton`. Change "`<chip footprint="pinrowN">`" to "`<chip>` with the record's
  footprint (pinrowN, headermoduleN, dip, jst_ph) and no `cadModel`".
- **★C3 · partly.** pre-analysis.md:86: "| module with a local `stlUrl` | failed: "RangeError: Out of bounds access" |
  315 KB, ran | the STL lands as loose faces, z from -5.3 to 0.7 mm: through the board, not on it |". The STEP merge
  holds. My 10 x 8 x 1.4 mm STEP body merged at z 0.00 to 1.40, and the GLB node `U1` held it. The STL half does not
  hold as written. A 12-triangle 10 x 10 x 5 mm STL, once ASCII and once binary, exported to GLB with exit 0, and the
  GLB node `U1` held the box. In the STEP the box sat at z -4.30 to 0.70, through the board, as claimed. So the GLB
  fault belongs to the probe's STL file, not to STL bodies in general (TL-10 blames an ASCII file read as binary).
  Also "installed today" is wrong: the toolchain's files are dated 2026-10-11. Change to: "tscircuit 0.0.2600,
  installed in the store since 2026-10-11, merges a local STEP body into its STEP and its GLB. An STL body lands
  through the board in the STEP. The GLB export failed on the probe's STL file and ran on a clean one."
- **★C4 · holds.** council/tech-lead.md:23: "In tscircuit's STEP, a part with a STEP body loses its reference name."
  Reproduced. My STEP-body board's solids are `PCB` twice (the board's and the body file's own) and `U2`, with no
  `U1`. kicad-cli on the same board wrote `NEXT_ASSEMBLY_USAGE_OCCURRENCE('2','U1'` and `('4','U2'`.
- **★C5 · partly.** pre-analysis.md:84: "plus two solids `unnamed_enclosure_fdm_box_1`, about 54 x 42 x 15 mm".
  README lines 17-18: "Mounting bosses, inserts, fasteners, assembly DRC, full component-body clearance, and non-FDM
  processes remain future work." The two solids and the MIT licence hold. The size does not. occt-import-js reads the
  case around a 50 x 36 x 1.4 mm board as 56.00 x 42.00 x 15.40 mm (z -6.70 to 8.70). 50 + 2 x (1 + 2) is 56, not 54.
  Change "about 54 x 42 x 15 mm" to "56 x 42 x 15.4 mm", and add the silent failure of the check-first section.
- **★C6 · holds.** pre-analysis.md:90. Reproduced, exit 1: "ENOENT: no such file or directory, open
  '…/@tscircuit/cli/dist/cli/manifold.wasm'".
- **★C7 · partly.** research.md:21: "| Adafruit_CAD_Parts | STEP, Fusion and STL of Adafruit boards | "MIT License" |".
  kicad.org: "The KiCad libraries are licensed under the Creative Commons CC-BY-SA 4.0 License, with the following
  exception". The Adafruit page: "MIT license". Both hold. But research.md:26 lists a second MIT source, "| tscircuit
  jscad-electronics | parametric chip and header shapes | MIT | yes |". And the bin project used an L9110 STEP that
  its own comment calls "a real model of this module (CC0)" (smartbin-local `board.tsx:73`, unchecked). The
  conclusion "spark ... never commits it" follows from AGENTS.md ("Never commit a vendor file"), not from the
  licences. Change "except Adafruit's (MIT)" to "except Adafruit's and tscircuit's jscad-electronics (both MIT). spark
  never commits a vendor file under any licence (AGENTS.md)."
- **★C8 · partly.** research.md:19: "| KiCad packages3D | STEP and WRL. ESP32 modules (WROOM, C3, S3), the Pico, a WEMOS
  D1 mini. No dev board such as the DevKitC |". The brief's "KiCad and Espressif hold modules (WROOM and others) only"
  is stronger than that row, which names two dev boards. Espressif's `3dmodels/espressif.3dshapes` holds 48 entries,
  none named for a dev kit (gh api). The bigger gap: vendor files exist and the PO has them. `~/Downloads` holds
  DFRobot's `DFR0654_3D_3DM.stp` (26.6 MB, 889 solids, one product `Document`, PA-2), and a second DFR0654 STEP zip
  dated 12 August this year (seen by `ls`, not opened). Change to: "No library found holds the dev boards spark uses.
  KiCad holds modules and two other dev boards. DFRobot serves STEP files of its FireBeetles as vendor downloads, and
  the PO has downloaded two."
- **★C9 · partly.** research.md:29: "It runs headless and needs `cadquery-ocp-novtk`, a 62.5 MB wheel (E, PyPI)."
  PyPI: "cadquery_ocp_novtk-8.0.1.1.0-cp311-cp311-macosx_11_0_arm64.whl: 62.5 MB". The cp312 and cp313 wheels are 63.1
  MB, cp314 is 63.2 MB, and the release has no cp310 wheel. The `python3` on this Mac's PATH is 3.10.0. The 62.5 MB
  is one wheel's download size, for Python 3.11. Change to: "Its kernel wheel is 62.5 to 63.2 MB to download on an
  arm64 Mac, for Python 3.11 to 3.14 only. The `python3` on this Mac's PATH is 3.10." I did not check the "label as
  its name" half.
- **★C10 · could not open.** autodesk.com returned HTTP 403 to my fetch, and my tools cannot reach the Wayback
  Machine. The brief drops a caveat from its own source. research.md:67: "The compare page ticks no "File export" and
  no "Work with non-native data" for personal use." "Work with non-native data" is the import that T1 needs. After D2
  ("Personal, free") this is the live risk for T1. Add to ★C10: "and no "Work with non-native data", which covers a
  STEP import".
- **★C11 · could not open.** The help page cited (`?guid=ADSKMCP-FusionDesktopMcp`) returned "Page Not Found" to my
  fetch. In part reproduced: the installed Fusion build 2705.1.15's en-US string table holds "Fusion MCP
  Server&#10;(runs locally on this device)" and "Fusion MCP Server Port". "Only while Fusion is open" and the address
  were not checked.
- **★C12 · holds.** pre-analysis.md:72-73: "KiCad with `kicad-cli` 10.0.6, Autodesk Fusion 360 (its `Application
  Support` folder exists), and PrusaSlicer. FreeCAD and OpenSCAD are not installed." `kicad-cli version` prints
  10.0.6. Fusion's app is in `~/Applications`, not `/Applications`. `which openscad freecad` finds neither. Two
  PrusaSlicers are installed (C30).
- **★C13 · holds, not run.** The TurboCase page: "Add bounding boxes for any footprint on the PCB that has a `Height`
  property defined." and "place plastic posts underneath the PCB to fit threaded metal inserts after 3D printing."
  Its `LICENSE.txt` begins "MIT License".
- **★C14 · holds.** picture_makers.py:23: `MakerUses = collections.namedtuple("MakerUses", "tools inputs cost asks")`.
  picture_makers.py:31: `Decline = collections.namedtuple("Decline", "maker reason missing")`. picture_makers.py:48:
  `class PartPictureMaker:`. part_shape.py:61: `class ShapeSource:`. `data/tools.json` `roles` has 14 keys and no 3D
  role.
- **★C18 · holds.** smartbin-local `Makefile:198`: `@tsci export -f glb board.tsx -o $@ > /dev/null`. `LICENSE`: "MIT
  License". Last commit 2026-10-12. `tools/viewer-3d.js` has 66 lines. One thing to add: its `board.tsx:129-134` loads
  OBJ bodies from `modelcdn.tscircuit.com`, so the bin's GLB export reaches the network. That is the practice Q15 (b)
  rejects.
- **★C19 · partly.** create-fdm-enclosure `dist/index.d.ts:531-532`: "Empty vertical space above the PCB top surface,
  not above the tallest component -- only parts owning an aperture report a height at all." The default holds: a
  direct call with the FireBeetle's 25.4 x 60 x 1.6 mm gives a depth of 15.6 mm. In my probe a 10 mm body went 4.0
  mm into the lid. The 21.7 and 27.7 mm do not hold as stated. They use "FireBeetle at about 7 mm of parts"
  (council/tech-lead.md:197-198). The record they come from says: "The STEP model suggests ~7 mm above the top face,
  but it includes the camera and its FPC and could not be reduced to board-only, so no number is recorded here rather
  than a guessed one." The bin's hand body, whose header says "Every dimension below is the real one", gives
  `WROOM_HEIGHT_MM = 3.1` and `USB_HEIGHT_MM = 3.26`. With 3.26 mm the MAX98357A (7.1 mm) is the tallest part, and
  the same arithmetic gives 20.2 mm soldered and 26.2 mm in sockets. The speaker terminal's height is in no record.
  The pointer council/tech-lead.md:159 lands in TL-18. PHY-1 is at line 170 and PHY-2 at line 194. Change to: "about
  20 to 22 mm soldered, or 26 to 28 mm in sockets (H socket and spacer heights, and a FireBeetle height between the
  bin's 3.26 mm and the 7 mm that its record rejects)".
- **★C20 · partly.** council/tech-lead.md:41-42: "A spike of about 110 lines wrote an AP214 file for the VL6180X
  record". The solver half is reproduced. A direct `createFdmEnclosure` call took 1.1 ms the first time and 0.2 ms the
  second. Its two plans, added as `cad_component` records to a copy of `circuit.json`, exported to STEP with exit 0
  and the solids `Casebase` and `Caselid`. These names come from the `source_component` name that the injecting
  script writes, not from the solver. The writer half could not be checked: its code was deleted. T1's third file
  ("one written by spark's own writer") needs that writer written again, which the "about 10 minutes" of A3 does not
  count. Add to the caveat: "the writer's code was deleted, and T1's third file needs it rebuilt".
- **★C21 · holds.** council/tech-lead.md:13-17. Reproduced. A 20 x 12 x 8 mm JSCAD cuboid on `U1` gave the STEP solids
  `PCB`, `U1`, `U2`, with `U1`'s faces at x -15 to 5, y -6 to 6, z 0.70 to 8.70, and a GLB node `U1`. `kicad_zip`
  held only `pinrow4.step`. The claim is incomplete. The check-first section shows the pin-row body that the JSCAD
  body removes.
- **★C22 · holds, export half reproduced.** council/tech-lead.md:77: "A missing model file passes in silence." The
  STEP export exited 0 and logged "Failed to merge STEP model from /nonexistent/missing.step: warn: Only HTTP(S) URLs
  are supported". `main.js:179385`: `if (!/^https?:\/\//i.test(modelUrl)) {`, then `const res = await
  globalFetch(modelUrl);`. I did not run `tsci build`. Add the GLB placeholder of the check-first section.
- **★C23 · holds.** The store's `drawer/dfrobot-fit0725.json`: `'count': 2`, label "Plastic Project Box Enclosure for
  FireBeetle - 3.15 x 1.61 x 0.79 inch". #6, 2026-11-05: "Parked at Idea, 2026-11-05. The PO, asked whether P100
  still waits for his bench time: "Park it"." board_sections.py:126: "Not decided here, and it must be: mounting
  holes, connector keying, and trace widths".
- **★C24 · partly.** council/user.md:77: "His printer and habit: PrusaSlicer 2.9.0 with the preset "Original Prusa i3
  MK3S & MK3S+"". `PrusaSlicer.ini:64`: "version = 2.9.0". The settings belong to 2.9.0, not to the 2.6.1 in
  `/Applications`. The brief keeps "2.6.1" while C30 says otherwise. Its pointer "council/user.md US-5" is the
  FIT0725 finding. The slicer facts are US-11 and PA-5. Prusa's 2.5 post supports the STEP import: "Right now we are
  tessellating the model on import (converting it to a triangle mesh)". It does not say whether a multi-body STEP
  arrives as one object or several, which Q17 (a) needs. Change to: "PrusaSlicer 2.9.0, beside an older 2.6.1, is set
  for ... · E council/user.md US-11, council/po-assistant.md PA-5 to PA-7".
- **★C25 · partly.** p934 diary line 78: "The PO has no ruler at hand and expects the datasheet to give the size."
  That is one evening, 2026-11-19 at 23:41. US-9 cites a calliper measurement: `parts/l9110s-module.json` says
  "measured with calipers on the module in hand". "What the maker supplies on the spot is photos" generalises one
  late-evening walk. Change to: "On the e-paper walk, with no ruler at hand, he supplied photos, and a photo gives no
  height. One earlier outline (the L9110S) was measured with callipers."

## 2. The brief against its sources

Caveats the brief dropped:

1. ★C10 drops "no "Work with non-native data"" (research.md:67). After D2 it is T1's first risk.
2. The synthesis's caution under the riskiest test: "the C6 ran on a breadboard on 2026-11-22 ..., so its header pins
   are soldered and reach below the board. The solver's 4 mm standoff ... may be too small. The test needs the reach
   below the board as a fact too." (synthesis.md:52). The brief recommends the C6 for T2 and leaves this out. T2's
   pass line has no fact for the reach below the board.
3. "Costs are the architect's estimates (H): XS, S, M, L" (synthesis.md:15) and "The size estimates (XS to L). They
   are my judgement, with no measured base" (synthesis.md:364). The brief's Options give every size with no H tag.
4. PA-29: "By the MVP bar, no slice of this epic moves a basic project closer to a breadboard with working firmware."
   TL-14 says the same. The brief never states the MVP-bar verdict. It says only that the epic "comes after the MVP".
5. PA-12: the PO asked on 2026-10-11 for the design to open in Fusion "along with all the functionality and the parts
   and values", and `kicad_zip` gives Fusion's KiCad importer its input. The brief frames Fusion as a STEP route only.
   T1 does not test the electronics route.
6. US-21: his cable's overmold is about 12 mm against a 9 mm receptacle (H). T2's step 1 pass line checks the
   opening's centre, not its size. Step 2 then asks his own cable to plug in. The facts T2 records hold no size for
   the opening.
7. The synthesis found 47 features on the C6, not 45. My count is 47. C26 still says 45.
8. The brief has no Splits section. The synthesis lists twelve (synthesis.md:283-296), among them three different
   first boards: the FireBeetle alone (PA-28), the amplifier fixture (TL-18) and the e-paper clock (AR-3).
   `verification.md` still holds only placeholders.

Claims stronger than their source:

9. In short: "Every tool the epic needs is installed and free." The installed print exports do not work: 3MF fails
   (★C6), `tsci` has no STL form, and TL-7 needed a script of its own. The solver has no bosses. Fusion is free only for
   personal, non-commercial use, and its file rights are unsettled (★C10). Change to: "Every tool for the body and the
   STEP is installed and free. The print file needs a writer of spark's own, and the Fusion step rests on a licence
   that two Autodesk pages describe differently."
10. In short: "3 of 43 records say how far a part stands above its board". See ★C1.
11. Q5 (b): "M to L: a new area and two Operations". PA-28 proposes no new area. Its path is "the record's facts and a
    stated headroom, then tscircuit's enclosure, then STEP, then PrusaSlicer, then a print." T2 is that path without
    product code. So (a) and (b) overlap in T2, and the brief prices (b) with the architecture lens's area, which PA-28
    never asked for.
12. Decision 2 of the synthesis rejects (b) "because ... he owns two bought boxes for that board". T2 prints a case for
    the same board. If the bought boxes lower the value of a FireBeetle case, they lower T2's value as a value test in
    the same way.
13. The riskiest row was written before D3 and not revisited. D3 says he draws his cases in Fusion. That makes A3
    (Fusion opens the STEP with names, under a personal licence) the path he uses today, and A2 (a spark-made case
    fits) a bet on a new habit. A1 now carries D3, but the riskiest row and Q5's order do not.
14. research.md's In short: "Fusion's personal licence keeps STEP export, scripts and a local MCP server." Its own
    section 3 says the MCP page "names no licence tier", and section 6 lists the MCP server on the personal licence as
    not checked.
15. pre-analysis.md's In short: "It takes a local STEP body per part and exports STEP with each solid named by
    reference." Also line 97: "So a part's body reaches both engines today through one fact, a STEP file." TL-2 and my
    probe show that a STEP body loses its reference. pre-analysis.md was not corrected.
16. jobs-and-journeys.md still points at `docs/guide/agents.md:170-176` for a STEP recipe (lines 27 and 41). PA-18 and
    AR-24 found that those lines export `kicad_pcb` and run a DRC. Its Claude journey (line 55) still says "no height
    for 29 of 30 records, holes as numbers for 1".
17. Wrong pointers in the brief. ★C19's council/tech-lead.md:159 (PHY-1 is at 170, PHY-2 at 194). C26's
    council/user.md:97 (US-15 is at 123, US-16 at 141). ★C24's "US-5" (the slicer is US-11).
18. The In short's "a FireBeetle the PO own" and "whether the PO do the two tests" read as a "you" replaced by hand.

## 3. Rival explanations the folder does not rule out

- **He does not need spark to make a case.** He owns two FIT0725 boxes made for the FireBeetle (★C23). D3 says he
  draws his cases in Fusion. His five recent slicer projects are downloaded models (US-11). The newest print file in
  `~/Downloads` is dated 2024-07. The `.f3d` files there are downloads too, not his designs. On this reading, he needs
  a STEP with real bodies to draw around, and spark's `make-case` serves nobody he can name. A1 is the only test, it is
  unrated, and its test is "Q3's answer", which is now answered (D3) without the brief changing course. The folder
  does not rule this out. The cheapest check: ask whether he would print a case that spark made for a board he already
  has a box for.
- **The request is a research question, not a build order.** His words ask "would it even be possible", "What other
  related solutions/ideas/free implementations are out there". The card says "In Idea until the PO orders it". The
  rival: research.md answers him, and the epic waits. Q5 offers no "(d) nothing built now: park the epic with the
  findings and the two tests as one card".
- **The first slice serves the MVP bar less than other cards.** AGENTS.md: "does it move a basic project closer to a
  breadboard with working firmware? ... Pause tooling that does not serve this bar." PA-29 and TL-14 both answer no
  for every slice of this epic. The MVP walk P100 #6 is parked "until he has bench time". scrum/VISION.md:69 quotes
  him on 2026-10-26: "we really need to get to the Langgraph/RRag mvp asap, so I can show it as a project". The v0.13
  core (#94) "runs right after the MVP works". Any of these serves the bar or his stated priority more than #1729 and
  #1727 extended. One line cuts the other way, and the brief does not cite it: VISION.md:67 puts "with the PCB and 3D
  model on request" inside v0.10, the basic journey. That makes a box body arguably part of the MVP text, but not the
  case, the viewer or the seams.
- **"J3 stood at never tried for two months" (US-4, decision 1).** The folder reads this as a cheap unknown that nobody
  ran. The rival: nobody pulled it, because it was not worth his time. Two months without a pull is evidence about
  value, not only about cost.
- **"The PO prints" (PA-5, US-11).** The settings file's date (2026-11-21) shows the app opened, not a print. The
  print files in `~/Downloads` stop at 2024-07. D4 says "A Prusa" with no model and no date of the last print.
- **"A box is similar enough" (A4).** P269 D9 records him saying "Number one is not necessary, just that parts should
  have pictures, photos". The rival: he values a photo-like look over a 3D body. Either way, A4's test (one look at
  three boxes) is cheap and has not run.

## 4. Numbers without their unit, population, period or provenance

- "3 of 43" and "30 of 43" (★C1, In short, riskiest): the population is not defined in the brief, and 3 of the 43
  are Wokwi chip files.
- "about 25 minutes of his time": the sum of PHY-7's 15 minutes (H) and A3's "About 10 minutes (H)". It leaves out
  rebuilding the deleted STEP writer for T1's third file.
- "one to two hours" of print: H, from "a box of about 33 x 66 x 15 mm" (PA-24), with no layer height or speed. The
  solver gives 31.4 x 66 x 15.6 mm for the FireBeetle.
- "4.72 mm" (★C19, riskiest): one probe board. Its module height is in TL's deleted probe, not in the brief.
- "21.7 or 27.7 mm" (★C19, Q7, Budgets): rests on a rejected 7 mm and on H socket heights (8.5 mm) and spacer
  heights (2.5 mm).
- "the default 15.6 mm": true for a 1.6 mm board. tscircuit's default 1.4 mm board gives 15.4 mm.
- "about 54 x 42 x 15 mm" (★C5): measured 56 x 42 x 15.4 mm.
- "5 ms" (★C20): one call, machine and count unstated. I measured 1.1 ms for the first call.
- "about 110 lines" (★C20, Q13 b): code deleted, not countable.
- "62.5 MB" (★C9, Q13 b, Q16 c): a download size, one Python version, not an install size.
- "about 5 % error" (★C25): the agent's estimate of a photo outline, not measured against the board.
- "45 features" (C26): 47.
- "tscircuit pinned 700 versions back" (risks-and-tests.md, viability): 0.0.2600 against 0.0.3300 is 700 patch
  numbers, not a count of releases.
- "the build time rises by 10 % or less" (A6): no base time is given. A real build can take up to 496 s
  (board_engine.py:23).
- "within 14 days" (A1) and "in 20 minutes or less" (A5): pass lines with no stated source for the threshold.
- "Kč 420 a month" (research.md): list price on the day read, with no VAT or billing period noted.
- "about 80 x 41 x 20 mm" (US-5): the outer size from the label in inches. No inner size, so whether a FireBeetle fits
  is unknown.

## What I could not check, and why

- Autodesk's compare page, its 2020 blog and the MCP help page: HTTP 403 to my fetch, "Page Not Found" on the help
  URL, and my tools cannot reach the Wayback Machine.
- The 110-line STEP writer and the build time with bodies: the code was deleted, and a build of the fixture was out of
  my time.
- Anything in Fusion, any print, any slicer import: they need the PO.
- `tsci build` with a missing model (★C22's build half), and build123d's names (★C9): not run.
- Whether a JSCAD union of a box and a pin row keeps the header body in the KiCad export: not run.

## Searches

None. I used no search engine. I opened cited pages directly: kicad.org/libraries/license, github.com/adafruit/Adafruit_CAD_Parts,
codeberg.org/MartijnBraam/TurboCase and its LICENSE.txt, pypi.org/project/cadquery-ocp-novtk, the Hunyuan3D-2 LICENSE
on GitHub ("THIS LICENSE AGREEMENT DOES NOT APPLY IN THE EUROPEAN UNION, UNITED KINGDOM AND SOUTH KOREA", which holds),
github.com/espressif/kicad-libraries, the Prusa 2.5 blog post, and the Autodesk help page (not found). I also read
GitHub through `gh`.
