# Verification
<!-- One line per ★ claim in brief.md; rejected claims stay. refuter: holds · partly · refuted · could not open, with
the line it read, verbatim. result: reproduced · not reproduced · rejected. keep: the words any summary of the claim
must carry (phrases separated by ;), or none; keep comes last on the line.
e.g. `- ★C3 · STATUS.md:84 · refuter: partly — "Shown on the C6, assumed for the S3" · reproduced how: re-read STATUS.md:84 · result: reproduced · keep: assumed for the S3` -->
- ★C1 · drawing.py:328, wire_routing.py:168, board_components.py:143-180 · refuter: pending · reproduced how: read the three modules and grep for the callers (sheet.py:279, :318, board_emitter.py:129) · result: reproduced · keep: share no code; the perfboard has no code
- ★C2 · pre-analysis.md §2 · refuter: pending · reproduced how: ran the five test modules with `python3 -m unittest`, "Ran 181 tests in 61.774s, OK" · result: reproduced · keep: well made for their one job
- ★C3 · drawing.py:236, tools/measure.py:245 · refuter: pending · reproduced how: read the signature and the R3 limit `PARAMETERS = 5` · result: reproduced · keep: one part at a time
- ★C4 · wire_routing.py:141, :203-205 · refuter: pending · reproduced how: read `free(cell)` (holes excluded) and `LEG_CLEARANCE = 2.5` in px · result: reproduced · keep: its search, costs and budget can be reused
- ★C5 · data/wokwi-geometry.json · refuter: pending · reproduced how: a script printed each part's pin spans: resistor 58.8, LED 10, pushbutton 67 px, tolerance 1.5 · result: reproduced · keep: drawing facts, not physical ones
- ★C6 · council/tech-lead.md TL-1 to TL-4 · refuter: pending · reproduced how: not reproduced by the main session, the lens's scratch run was deleted · result: not reproduced · keep: measured by the lens; 4 decimals
- ★C7 · council/tech-lead.md TL-5 · refuter: pending · reproduced how: not reproduced · result: not reproduced · keep: the breadboard's rule set; random endpoints
- ★C8 · kept_moves.py:175-184, :233-255 · refuter: pending · reproduced how: read `reserve_first` (claims each earlier part in file order) and `name_parts_not_kept` · result: reproduced · keep: every earlier part
- ★C9 · sheet.py:316-321, build_record.py:32 · refuter: pending · reproduced how: read the `except drawing.NotDrawnError` branch and `OWN_FILES = ("board.tsx",)` · result: reproduced · keep: the build names each part it could not keep
- ★C10 · the store's projects.json · refuter: pending · reproduced how: a script counted "listed 28 exist 23 with breadboard.json 1 ['reaction-game']" · result: reproduced · keep: n = 1 maker; not that none is wanted
- ★C11 · p934-epaper/breadboard.md, p934-display2/breadboard.md · refuter: pending · reproduced how: grep for "There is no Wokwi diagram" over the existing project folders found exactly these two · result: reproduced · keep: would not depend on Wokwi's parts
- ★C12 · README.md Bench row · refuter: pending · reproduced how: not re-read by the main session · result: not reproduced · keep: n = 1
- ★C13 · run_request.py:1-5, :42-44 · refuter: pending · reproduced how: read the docstring ("The values of the step come from spark's own offer key, never from the request") and `STEP_OPERATIONS` with three Operations · result: reproduced · keep: none
- ★C14 · parts/*.json, boards/*.json · refuter: pending · reproduced how: grep counted 8 part records with `body_mm` and both boards with `width_mm` · result: reproduced for body_mm and the board sizes, not for the lead patterns · keep: missing for the button and the resistor
- ★C15 · the store's drawer/dfrobot-fit0193.json · refuter: pending · reproduced how: printed its keys, no pitch, no hole counts · result: reproduced · keep: none
- ★C16 · council/tech-lead.md EP-2 · refuter: pending · reproduced how: not reproduced · result: not reproduced · keep: calculated with handbook resistivities
- ★C17 · research.md · refuter: pending · reproduced how: the LICENSE files were read by a fetch agent on 2026-11-26 · result: reproduced by the fetch agent · keep: perfwire's maturity is unknown
- ★C18 · docs/discovery/2026-10-18-p294-wokwi-reuse/finding.md · refuter: pending · reproduced how: read its TL;DR · result: reproduced · keep: a full-board project has no breadboard.json
- ★C19 · drawing.py, tools/measure.py:242 · refuter: pending · reproduced how: `wc -l` gave 599, `MODULE_LINES = 600` · result: reproduced · keep: none <!-- REQUIRED:claims -->

## Agree / split
<!-- Where the lenses and the refuter agree, and where they split; each split becomes a question.
e.g. `- Split: Feasibility says a day, Risks says a week · Q4` -->
- Agree, all four lenses: an edit is a fact in hole names, not bytes of breadboard.json (ARCH-5, TL-12, US Q1). council/synthesis.md G2
- Agree: keep moves becomes a Decorator over any placement, and the Wokwi round trip an importer at the edge (ARCH-5, TL-11). G3
- Agree: the breadboard's router is a picture router, so the perfboard needs a join router inside the plan (ARCH-1, ARCH-2, TL-6). G5
- Agree: the perfboard, the goals and the editors come after the MVP, and the breadboard keeps the first fit (PA-3, TL Q3, US-6, ARCH-16). G8
- Agree: the Operations come before any page (PA-5, US-7, ARCH-8). G7
- Split: when the core is built. The PO assistant: only when the perfboard card is pulled. The tech lead: slices 1 to 8 from now. The synthesis: after the MVP, born in the first slice that needs it · Q3
- Split: the placement seam. ARCH-3: `place_all`. TL-8: a candidate generator and a chooser. The synthesis: two layers of one seam · no question, the design's
- Split: the goal's unit. The brief: mm². US-6: holes. The synthesis: holes first, mm beside · Q7, and the outcome line changed
- Split: the core's unit. The card and the pre-analysis: mm. TL-3, TL-4: mm floats change goldens. The synthesis: whole holes with a pitch in mm · D-q1, A2
- Split: the layout's kept row. P1193's council and PA-6: breadboard.json with a stamp. ARCH-7, TL-13: the edits record · Q4
- Split: the perfboard's default goal. US: roomy. TL: first fit. #311 note 2 is about the board, not the spacing · Q7
- Split: the FIT0193's hole count. TL: at most 40 × 30. US: at most 39 × 29 · Q8, spike C <!-- REQUIRED:agree-split -->
