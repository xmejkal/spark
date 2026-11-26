# Verification
<!-- One line per ★ claim in brief.md; rejected claims stay. refuter: holds · partly · refuted · could not open, with
the line it read, verbatim. result: reproduced · not reproduced · rejected. keep: the words any summary of the claim
must carry (phrases separated by ;), or none; keep comes last on the line. -->
The refuter on Opus read the brief at commit a08a4eb5 (council/refuter.md). The facilitator reproduced what a command
on this Mac could reach, at 16:20 to 16:32 CET on 2026-11-26, in a scratch folder that is deleted at the end.

- ★C1 · pre-analysis.md:15 · refuter: partly — "So the population is 40 part and board records ... 34 of 40 hold an outline" · reproduced how: re-ran the key scan without `*.chip.json`: 40 records, 34 with an outline (2026-11-26) · result: reproduced after correction · keep: 3 of 40 <!-- REQUIRED:claims -->
- ★C2 · scripts/spark/design/board_sections.py:258-259 · refuter: partly — "The footprint is not always `pinrowN`" · reproduced how: re-read the lines · result: reproduced after correction · keep: none
- ★C3 · pre-analysis.md:86 · refuter: partly — "the GLB fault belongs to the probe's STL file" · reproduced how: `tsci export abs.tsx -f glb` with an absolute STL path: exit 0. With `./clean.stl`: "RangeError: Out of bounds access" · result: reproduced after correction · keep: one probe board
- ★C4 · council/tech-lead.md:23 · refuter: holds — "In tscircuit's STEP, a part with a STEP body loses its reference name." · reproduced how: my first probe: the merged body's solid had the name '' and its shape `./body.step` · result: reproduced · keep: Whether Fusion shows them is not run
- ★C5 · pre-analysis.md:84 · refuter: partly — "Change about 54 x 42 x 15 mm to 56 x 42 x 15.4 mm" · reproduced how: occt-import-js on my `encl.step`: 56.00 x 42.00 x 15.40 mm · result: reproduced after correction · keep: version 0.0.4
- ★C6 · pre-analysis.md:90 · refuter: holds — "ENOENT: no such file or directory, open .../manifold.wasm" · reproduced how: my first probe log · result: reproduced · keep: none
- ★C7 · research.md:21 · refuter: partly — "Change except Adafruit's (MIT) to except Adafruit's and tscircuit's jscad-electronics" · reproduced how: re-read research.md:21 and :26 · result: reproduced after correction · keep: never commits a vendor file
- ★C8 · research.md:19 · refuter: partly — "KiCad holds modules and two other dev boards ... the PO has downloaded two" · reproduced how: re-read research.md:19 · result: reproduced after correction · keep: vendor downloads
- ★C9 · research.md:29 · refuter: partly — "62.5 MB is one wheel's download size, for Python 3.11" · reproduced how: not re-run: the refuter read PyPI · result: not reproduced · keep: to download
- ★C10 · research.md:67 · refuter: could not open — autodesk.com returned HTTP 403 · reproduced how: not reproduced: Autodesk pages are not reachable from here · result: not reproduced · keep: the pages disagree
- ★C11 · research.md section 3 · refuter: could not open — the help page answered "Page Not Found" · reproduced how: not reproduced; the refuter read the setting's string in the installed build · result: not reproduced · keep: not turned on or run
- ★C12 · pre-analysis.md:72-73 · refuter: holds — "kicad-cli version prints 10.0.6" · reproduced how: `kicad-cli version` printed 10.0.6 in my probe · result: reproduced · keep: installed is not used
- ★C13 · research.md section 4 · refuter: holds, not run — "Its LICENSE.txt begins MIT License" · reproduced how: not re-run · result: not reproduced · keep: not run
- ★C14 · scripts/spark/breadboard/picture_makers.py:23-58 · refuter: holds — "class PartPictureMaker:" · reproduced how: re-read picture_makers.py:1-60 · result: reproduced · keep: none
- ★C18 · ~/Development/smartbin-local Makefile:198 · refuter: holds — "@tsci export -f glb board.tsx -o $@" · reproduced how: re-read the Makefile, LICENSE and the clearance check's header · result: reproduced · keep: a sibling project
- ★C19 · council/tech-lead.md:194 · refuter: partly — "The 21.7 and 27.7 mm do not hold as stated" · reproduced how: not re-run: the arithmetic rests on record notes the refuter quoted · result: not reproduced · keep: calculated, not printed
- ★C20 · council/tech-lead.md:41-42 · refuter: partly — "The writer half could not be checked: its code was deleted" · reproduced how: not re-run · result: not reproduced · keep: boxes only
- ★C21 · council/tech-lead.md:13-17 · refuter: holds — "A 20 x 12 x 8 mm JSCAD cuboid on U1 gave the STEP solids PCB, U1, U2" · reproduced how: `tsci export jplan.tsx -f step`: solids PCB, U1, U2. A JSCAD spec without the planner shape failed with "size must be positive" · result: reproduced · keep: a probe board
- ★C22 · council/tech-lead.md:77 · refuter: holds — "The STEP export exited 0 and logged Failed to merge STEP model" · reproduced how: `tsci export missing.tsx` for glb, step and kicad_zip: all exit 0, the same warning · result: reproduced · keep: one run each
- ★C23 · the store's drawer/dfrobot-fit0725.json · refuter: holds — "'count': 2" · reproduced how: not re-run · result: not reproduced · keep: none
- ★C24 · council/user.md US-11 · refuter: partly — "The settings belong to 2.9.0, not to the 2.6.1" · reproduced how: not re-run · result: not reproduced after correction · keep: is not used
- ★C25 · council/user.md US-6 · refuter: partly — "generalises one late-evening walk" · reproduced how: not re-run · result: not reproduced after correction · keep: n = 1
- ★C33 · council/refuter.md:18 · refuter: CONFIRMED by the refuter — "With a JSCAD body on the same module, that line is gone" · reproduced how: `tsci export jplan.tsx -f kicad_zip`: only `pinrow4.step`. The plain board holds `pinrow10.step` and `pinrow4.step` · result: reproduced (the KiCad half; the STEP's pin tails not counted again) · keep: one probe board
- ★C34 · council/po-assistant.md PA-29 · refuter: not judged as a claim — the refuter raised it as a dropped caveat (council/refuter.md:180) · reproduced how: re-read AGENTS.md's bar and scrum/VISION.md:67 · result: reproduced · keep: after the MVP
- ★C35 · ~/.local/share/spark/t1-step-2026-11-26/README.md:19 · refuter: not judged, found after the refuter's pass · reproduced how: `grep -n NaN` on the file, and occt-import-js on the board without bodies, which reports the same 8 fails · result: reproduced · keep: one board
- ★C36 · ~/.local/share/spark/t1-step-2026-11-26/README.md:12 · refuter: not judged, found after the refuter's pass · reproduced how: the STEP's NEXT_ASSEMBLY_USAGE_OCCURRENCE names, read with grep · result: reproduced · keep: one board

## Agree / split
- Agree: every lens and the refuter say that no file ran in Fusion, no case was printed, and the z facts are too few and named two ways · none <!-- REQUIRED:agree-split -->
- Agree: the PO assistant and the tech lead say no slice serves the MVP bar (PA-29, TL-14) · recorded as ★C34
- Split: the first board: the FireBeetle alone (PA-28), the amplifier fixture (TL-18), the e-paper clock (AR-3) · Q5
- Split: the riskiest belief: the fit of the first print (PA-23, the architect) or the names in Fusion (TL-16). After D2 and D3 the facilitator proposes TL-16's · Q1
- Split: the body's form: a JSCAD plan that runs today (TL-1) or one STEP file for every engine (AR-8). The refuter adds that a JSCAD body removes today's header body (★C33) · Q13, after T1
- Split: the order of #1729 and #1728 (the P1089 council against AR-9) · Q18
- Split: how many seams now: four in the first slice (AR-27) or one per first member and a Fake (the architect), against "settings for five strategies before one printed case" (PA-25) · Q5
- Split: Fusion's place: the frame's outcome puts it first, P269's D9 puts it after the catalogue editor (PA-21) · Q10
- Split: the print file: STEP into the slicer (PA-6), an STL writer (TL-7) or a form of make-case (AR-16) · Q17
- Split: the viewer: reuse the bin project's now (PA-1, US-1) or wait (AR-15) · Q11
- Split: an unknown height: refuse and ask, or a named default (US-26) · Q9
- Split: who owns the facts: P735, P446, #1729 or this epic (PA-16) · Q12
- Split: the refuter's rival: he may not need spark to make a case at all (two bought boxes, D3) · Q5 options d and e, Q8
