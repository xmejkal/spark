# Verification

The refuter (Opus) read the brief as it stood before its corrections. The rows below give its verdict on that text, then the reproduction, then the words any summary must keep. The brief now carries the corrected wording.

- ★C1 · council/refuter.md:9 · refuter: partly, "DFRobot dimensioned holes for 2 of 4 (SEN0526, DFR0995) and header positions for 2 of 4" · reproduced how: re-read walk/dfr0457/diary.md:89 (no thickness) and walk/dfr1117/diary.md:20 (KiCad footprint) · result: reproduced, as corrected · keep: 4 parts picked by Claude <!-- REQUIRED:claims -->
- ★C2 · council/refuter.md:21 · refuter: partly, "no typed field … only as ad hoc facts entries or documents" · reproduced how: re-read council/tech-lead.md:9 · result: reproduced, as corrected · keep: none
- ★C3 · council/refuter.md:30 · refuter: holds · reproduced how: `data/wokwi-geometry.json` parts keys are board-xiao-esp32-c6, wokwi-led, wokwi-resistor, wokwi-pushbutton, and `scripts/spark/breadboard/drawing.py:70` defines NotDrawnError · result: reproduced · keep: until a reader exists
- ★C4 · council/refuter.md:35 · refuter: holds, caveat wrong, "datasheets.py:25-26 … A default changes only with the PO's yes" · reproduced how: `parts.py --need load switch` and `--need ESP32-C6` answer "nothing in the library matches", `--need mosfet` names dfr0457-mosfet-power-controller · result: reproduced · keep: a P211 default
- ★C5 · council/refuter.md:41 · refuter: partly, "nothing writes a boards/<id>.json skeleton" · reproduced how: `parts.py --unverified xiao-esp32-c6` answers "no part called 'xiao-esp32-c6'" · result: reproduced, as corrected · keep: none
- ★C6 · council/refuter.md:46 · refuter: holds, all eight reproduced or read · reproduced how: scripts/spark/sourcing/part_facts.py:184 writes "//sourcing" · result: reproduced for the skeleton bug, the other seven rest on the refuter and TL-13 to TL-19 · keep: on scratch copies
- ★C7 · council/refuter.md:53 · refuter: refuted, "So they have no route into the store is false" · reproduced how: scripts/spark/sourcing/datasheets.py:31 and walk/dfr1117/diary.md:44 · result: rejected as first written, reproduced as corrected · keep: by hand
- ★C8 · council/refuter.md:58 · refuter: holds, the VIN pad is the VUSB net before the 1N5819W · reproduced how: re-read walk/sen0526/sen0526-i2s-mic.json:282 and walk/dfr1117/diary.md:67 · result: reproduced · keep: not measured
- ★C9 · council/refuter.md:68 · refuter: partly, "16 of 112 drawer entries link a record; 8 of the 99 DFRobot ones do" · reproduced how: a count of the `is` key over ~/.local/share/spark/drawer/*.json printed 112 16 8 · result: reproduced, as corrected · keep: not counted
- ★C10 · council/refuter.md:73 · refuter: partly, "3 to 10 fetches and 0 to 16 URL checks" · reproduced how: re-read the four diaries' Counts parts · result: reproduced, as corrected · keep: estimates

## Agree / split
- Agree: the four walks, the three lenses and the refuter agree on three points. The record has no typed place for geometry, no reader draws it, and the hand steps of ★C6 repeat in every walk. <!-- REQUIRED:agree-split -->
- Split: the PO assistant read the walks as evidence against A1 (enough published geometry), the refuter as evidence for it. The brief follows the refuter, and A1's new pass line tests content, not links · Q1
- Split: the tech lead treats `--need` as a bug, the refuter as the PO's P211 default · Q5 in the brief's queue
- Split: P446 forbids an AI-made shape, the PO's words on P734 allow one (C13) · a design council question
- Second pass (council/refuter.md, Second pass): the reader came too late for A2, slice 0 could not meet its proof, A1's evidence and pass line counted differently, and the diagram said more than the architect. All four are fixed in the brief, the map and the risks. The DFR0457 rename reason was wrong, because irrigation keeps its own copy (`~/Development/irrigation/parts/` listed 2026-11-10).
