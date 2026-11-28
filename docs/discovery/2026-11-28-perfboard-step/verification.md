# Verification
<!-- One line per ★ claim in brief.md; rejected claims stay. refuter: holds · partly · refuted · could not open, with
the line it read, verbatim. result: reproduced · not reproduced · rejected. keep: the words any summary of the claim
must carry (phrases separated by ;), or none; keep comes last on the line. -->
The refuter on Opus read the brief on 2026-11-28 (council/refuter.md): 10 claims hold, 13 hold in part, none is refuted. Each partly claim is rewritten in brief.md with the refuter's narrower words. The facilitator re-read the lines marked "re-read".

- ★C1 · P269 brief.md:15, #311 note 1 · refuter: partly — "probably we will want to reuse code for the perfboard stagte" · reproduced how: re-read the refuter's quotes; the claim now says the wants recur, and that note 1 is relayed · result: reproduced · keep: not how soon he uses it; relayed, not read from him <!-- REQUIRED:claims -->
- ★C2 · P1199 brief.md:124 · refuter: holds — "D3 · Q3: the layout core is built after the MVP, born in the first slice that needs it" · reproduced how: re-read P1199 brief.md:124 · result: reproduced · keep: two readings; an open question (Q2)
- ★C3 · scrum/VISION.md, architect.md:9 · refuter: partly — "One gate opens the permanent build" · reproduced how: `grep -c` gave 0, re-run 2026-11-28 · result: reproduced · keep: the perfboard step only; the drawing.py split is judged on its own
- ★C4 · po-assistant.md:53 · refuter: holds — "If it holds fewer than 3 lines, the walking skeleton P1237 #1790 waits until the perfboard card is pulled." · reproduced how: the refuter re-ran the grep; the facilitator did not · result: reproduced · keep: a soldering session leaves no trace in spark's files
- ★C5 · drawer/dfrobot-fit0193.json:3 · refuter: holds — "\"label\": \"ProtoBoard Pro - Double Sided (100x75mm)\"" · reproduced how: re-read both drawer files 2026-11-28 · result: reproduced · keep: bought is not the same as still in the drawer; the seller's label
- ★C6 · Perfboard.dc.html:26, :58, :200 · refuter: partly — "The plan needs 26 × 18 holes. A board can be cut smaller, never made bigger." · reproduced how: the refuter read both files; the claim now names two gadgets · result: reproduced · keep: two gadgets; may be a choice per gadget
- ★C7 · Perfboard.dc.html:186 · refuter: holds — "'Trace for ' + b + ' on the back: from the board’s ' + a" · reproduced how: the refuter's quote · result: reproduced · keep: none
- ★C8 · Perfboard.dc.html:164 · refuter: holds — "const X = (c) => mir ? 624 - (c - 0.5) * P" · reproduced how: the refuter's quote · result: reproduced · keep: how he turns a board is unknown
- ★C9 · json.md:297-298 · refuter: partly — "These do not take it: ... `breadboard.py`" · reproduced how: re-read json.md:297-298 and scripts/breadboard.py:22-24, 2026-11-28 · result: reproduced · keep: Claude can move a part in breadboard.json today, in px
- ★C10 · drawing.py:290 · refuter: partly — "if part_px.get(\"covers_holes\") and not self._pins_keep_a_free_hole(holes, covered, ledger):" · reproduced how: re-read drawing.py:286-292, :310-318; the trial was not re-run (no test slot) · result: reproduced · keep: one trial with a patched Surface; times from one run; the rule may need another form
- ★C11 · breadboard_scene.py:114 · refuter: partly — "x0, y0 = min(hole.x for hole in surface.terminal), min(surface.letters_y.values())" · reproduced how: re-read the three lines 2026-11-28 · result: reproduced · keep: read, not run
- ★C12 · drawing.py:241 · refuter: partly — "Strategy: which holes the jumpers take, once the parts are placed and each jumper has its two rows." · reproduced how: re-read drawing.py:241 · result: reproduced · keep: a perfboard needs its own planner around that seam; a split
- ★C13 · wire_routing.py:236-241 · refuter: partly — "for move in (1, 3): leg = _step(search.start, move)" · reproduced how: the refuter's quote · result: reproduced · keep: start legs, state shape and single goal are breadboard rules; its worth is H
- ★C14 · wire_routing.py:198, :202 · refuter: holds — "CELL, OUTSIDE, BESIDE_A_LINE, BEND, CROSS = 1, 2, 2, 4, 6" · reproduced how: re-read wire_routing.py:196-208 · result: reproduced · keep: line numbers are before P1350
- ★C15 · drawing_match.py:44-45 · refuter: holds — "for jumper in layout.jumpers: self._join(jumper.one.group, jumper.other.group)" · reproduced how: re-read drawing_match.py:40-52 · result: reproduced · keep: a perfboard part has no joined_pins
- ★C16 · perfboarddesigner.com guide · refuter: holds — "they can't cross anything" · reproduced how: the refuter fetched the page 2026-11-28 · result: reproduced · keep: one hobby guide, not a standard
- ★C17 · the Espressif guide · refuter: holds — "It is suggested to place the module's on-board PCB antenna outside the base board" · reproduced how: the refuter fetched the page · result: reproduced · keep: for a module on a base PCB; a dev board on headers is a weaker case
- ★C18 · architecture.md:81 · refuter: partly — "`SceneGrid` says it turns px into cells \"as the router's TrackGrid does\"" · reproduced how: re-read breadboard_scene.py:112-115 · result: reproduced · keep: near-duplicates only as an H; merging couples three jobs
- ★C19 · tools/measure.py:242 · refuter: partly — "MODULE_LINES = 600" · reproduced how: `wc -l drawing.py` gave 599 · result: reproduced · keep: a move out of drawing.py needs no room
- ★C20 · bench_changes.py:26, kept_files.py:16 · refuter: holds — "from spark.build.build_record import STAGE_SUFFIX, StagedFile" · reproduced how: the refuter's grep · result: reproduced · keep: none
- ★C21 · scripts/breadboard.py:25 · refuter: partly — "written = write(requirements, out)" · reproduced how: re-read scripts/breadboard.py:20-26 · result: reproduced · keep: two frontends, each calling sheet.write
- ★C22 · flow_codes.py:364 · refuter: holds — "ASK_CLAUDE, COPIED_SAYS, NOT_COPIED_SAYS = \"Ask Claude\", \"Copied: paste it in Claude Code.\"" · reproduced how: the facilitator's grep 2026-11-28 · result: reproduced · keep: it words the next step, not a layout change
- ★C23 · parts/led-red-5mm.json · refuter: partly — "pinrow2 is two through-holes at 2.54 mm, which is the drawing's lead spacing" · reproduced how: the refuter's quote · result: reproduced · keep: drawer labels only

## Agree / split
<!-- Where the lenses and the refuter agree, and where they split; each split becomes a question. -->
- Agree: the same-pins check must read each join as a set of holes (TL2-13, ARCH-P5, UL-8, the refuter on ★C15) · no question <!-- REQUIRED:agree-split -->
- Agree: the router's penalties become one named Value per surface, and the two surfaces share no fields (TL2-16, ARCH-P3) · no question
- Agree: build nothing before his Ready order, and nothing in wire_routing.py before P1350 merges (all four lenses) · no question
- Split: the join seam. ARCH-P1 puts the perfboard's join router in `JumperPlacement`; TL2-12 says the planner around it is breadboard-only, so a perfboard planner is needed · for the design, no PO question: both hold, and the design names the planner
- Split: the order. The PO assistant says D3 stands (no refactor before the MVP); the architecture lens says moves 1 to 3 may run now; the refuter adds spike P1074 #1575 first · Q2
- Split: the dev board's mount. The PO assistant: female headers. The tech lead: a setting with headers as default. The user lens's sketch: the XIAO soldered straight in. The canvas: the clock on headers, button-light off the board · Q4
- Split: the first gadget. The story map's skeleton targets button-light; the only account (P1039 D11) names the clock and the bin · Q6
- Split: the worth of the shared search. ARCH-P2 and TL2-14 lift it; the refuter says the shared part is about 20 lines and risks `cut_short` · for the design, measured by A4
