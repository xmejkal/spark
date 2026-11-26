<!-- Resume: invoke product-discovery again; `discovery.py check <this folder>` names the next step. -->
# P1197 3D: discovery brief

<!-- Readiness, its one home. collecting evidence: anything short of the two below. an experiment: the decider chose
a test (a D) before choosing an option. design: the decider confirmed the frame, the jobs and a direction, and accepted
the remaining risk (D rows). An extension may tighten these. Next: design, or a chosen test of kind spike or prototype
→ the design skill the facts name, with this file; otherwise none, and the collection plan says who runs it.
Stands on: the assumptions not retired in risks-and-tests.md; of which those the decider rated high, or — while any
is unrated. check computes both. -->
**Ready for:** collecting evidence <!-- REQUIRED:ready -->
**Stands on:** ⟨fill⟩ H, ⟨fill⟩ of which would change the decision <!-- REQUIRED:debt -->
**Decision needed:** ⟨fill⟩ <!-- REQUIRED:decision-needed -->

> In short: ⟨fill after the council⟩

The evidence behind this brief: [pre-analysis.md](pre-analysis.md) (what spark holds, and a probe of tscircuit's 3D
exports on this Mac) and [research.md](research.md) (reuse first, with licences).

## Frame
- Request, verbatim (corrections marked): the PO, 2026-11-26, on #1745: "And related to the PCB and 3d prinitng a cover are actually both related to another big epic and question and that's how we could actually also make sure we have 3d  models for all the parts and boards and modules and how we could store them, how we could use them in the 3d model made by tsscirpt [tscircuit] or KiCad, if we can use some existing solutions and combine them or get inspired or copy pieces etc so that we really can nicely have this working so that everything on the PCB and also the perfboard has a good 3d model, or at least some similar enogh general shape, if it would somehow be possible to create it based on the pictures we have or have found online or took pictures of, really the whle conception with 3d and that also brings us to the future missing step and that's export to 3d, so a tool/strategy can open it, like fusion 360 or other free tools if available, but preferably fusino360 too and caude [Claude] could then also se that 3d tool to craete a cover or some parts for it, using the MCP version of fusion or some other strategy, a LCI [CLI] based, etc.. Or would it even be possible to use some existing free solutions r even make it ourselves later  some way to display the 3d in browser, and allow for prining and exporting the 3d printer files for like verysimple cases?  What other related solutions/ideas/free implementations are out there that would be also useful ? Like in general it would just be the best if every record had its 3d shape and thalso the perfboard and PCB could be put together, some basic cover would be created , the whole thing openable in fusion and the user or ai could use it  and create the cover or other parts." His follow-up, the same day: "And how does it work together with the built in 3d view from KicAD or tsscript [tscircuit] or whatever we now use?" His standing line for every brief, the same day, through spark-main: "the architecture needs to be well made so that we can change these srtrategies and tools and its reusable, dry". <!-- REQUIRED:request -->
- Decision · decider: which first slice of P1197 to design after the MVP, and where models are kept. Also which seams that slice sets for the later strategies. The strategies: the model's source, the engine and export, the CAD tool, the case maker and the viewer · the PO <!-- REQUIRED:decision -->
- Outcome and how it is observed (a metric with unit and source, a proof command, or a log): proposed: for one real spark board, one Operation writes a STEP file and a case. The STEP opens in the PO's Fusion 360 with each module as a body at its real size, named by its reference. The case prints and fits. Observed by a walk with the PO: Fusion's browser tree (a screenshot), and callipers on the printed case against the board. <!-- REQUIRED:outcome -->
- Already decided (D · who · when · where; include the product's stated non-goals and earlier decisions the request names): the Fusion export comes after the catalogue editor. Photos are a part's pictures (P269 D9 · the PO · 2026-10-16 · docs/discovery/2026-10-16-p269-views-and-editors/brief.md:108) · this epic comes after the MVP (spark-main's brief, 2026-11-26, from the card's Slice 9 "An enclosure") · an enclosure is "later" in the vision (scrum/VISION.md:70) · never commit a vendor file, use free tools and a local CLI first, a paid tool waits on the PO's yes (AGENTS.md, Principles) · tscircuit stays the board engine and kicad-cli is an optional export after the build (P1089 finding, section 4, cards P1183 #1727 and P1185 #1729) · every configurable choice names its setting, default and layer (the PO, 2026-11-26, P1194 #1740) · one seam per strategy, chosen by a setting, behind an Operation, thin interfaces, nothing twice (the PO's standing line, above) · the circuit sculpture P1198 #1746 stays parked, and only the frame's fit to it is checked (spark-main's brief, 2026-11-26) <!-- REQUIRED:decided -->
- Open questions: Which first slice gives the PO a case soonest? Where does a fetched model live, and how does a record point to it? Is a generated shape enough for most records? Does Fusion keep each part's name, and does the personal licence limit the path? Does spark make the case (tscircuit's enclosure element, or its own generator), or does it hand the board to a CAD tool and Claude? Do the browser viewer and the print files belong in the first slice? What does the perfboard need before it has a 3D shape? <!-- REQUIRED:open -->
- Scope · out of scope (proposed): in: the 3D facts of a record and their origin, where model files live, and how each engine takes them. Also in: the export, the case, the viewer, the print files, and the seams and settings for each. Out: the circuit sculpture (P1198, parked, fit checked only) and a perfboard layout (P275 #311 and the layout core P1199 #1747 own it). Also out: the PCB's own routing (P1089), a paid model service, and slicing (the person's slicer keeps the printer profile) <!-- REQUIRED:scope -->
- Start and reach (proposed until Q0): start existing product · decider reachable yes, through spark-main · users: the PO as the maker (n = 1), with Fusion 360, KiCad and PrusaSlicer on his Mac (E, pre-analysis section 3). The hobbyist persona is H (scrum/VISION.md: no outside person installed spark). Claude is the agent that runs the Operations · data and connectors: this session read the code, the store, GitHub and the toolchain. Fusion's MCP server is not connected, a gap, and turning it on is the PO's. No model library is connected · decider as a user n = 1 · must not get worse: the build stays free of any 3D tool and of KiCad, the build time stays, and no vendor file enters the repository <!-- REQUIRED:start-reach -->
- Flags (yes · no · —; asked only when it changes a decision; never legal advice; any date or threshold is read at its source at run time and cited):
  - sold or given away, or personal use: personal use (H, the PO as the one maker). It matters for Fusion's personal licence, which is for non-commercial use (E, research.md section 3) <!-- REQUIRED:flag-sold -->
  - connects to a network or runs software (for example the EU's Cyber Resilience Act): no change: the epic adds a file and a case, not software on the gadget <!-- REQUIRED:flag-network -->
  - children or food contact: no <!-- REQUIRED:flag-children -->
  - market: — (the PO in Czechia, EU). It decided one thing: Hunyuan3D-2's licence excludes the EU (E, research.md section 1) <!-- REQUIRED:flag-market -->
  - radio (unlicensed-device rules; read at their source when it decides): no change. A case around an antenna is a physical risk row, not a radio rule <!-- REQUIRED:electronics-firmware:flag-radio -->
  - a Li-ion cell (charging, transport, battery rules): no change. A case around a cell is a physical risk row <!-- REQUIRED:electronics-firmware:flag-li-ion -->
  - mains: no <!-- REQUIRED:electronics-firmware:flag-mains -->
  <!-- EXTEND:flags -->
- Extensions (each active id · the fact that activated it; when none matched, only "none matched: core only · the fact that decided it", naming no extension; list any directive skipped under rule 9): electronics-firmware · repo-has boards/*.json; spark-process · repo-has scrum/WORKING_AGREEMENTS.md. The physics lens reads mechanical numbers here (heights, clearances, wall and fit), and the tech lead takes it. spark-process says questions go through AskUserQuestion: here they go to the PO through spark-main by SendMessage, in rounds of up to four, as spark-main's brief of 2026-11-26 says <!-- REQUIRED:extensions -->
- The item (its issue, or the proposal in the decider's words) · what is still open elsewhere · the repository's push check, or "no push check here": P1197 #1745, an epic in Discovery since 15:02 CET 2026-11-26 · open elsewhere: P1199 #1747 (layout core) and P1194 #1740 (settings), both ready for design after the MVP. Also P1190 (simulation), and the cards P1183 #1727 and P1185 #1729 that this epic builds on · push check: the pre-push hook, and spark-main gives each push slot <!-- REQUIRED:spark-process:item -->
<!-- EXTEND:frame -->
- Depth: TRIO (the PO assistant, the user, the tech lead with the physics lens). spark's rules add the architecture lens for a new interface or a change to the core. So four agents run on Opus, as spark-main's brief says. The architect agent writes the synthesis, and the refuter runs on Opus <!-- REQUIRED:depth -->
  <!-- Cost, measured once: the P900 rehearsal's council took 6 agents, 499 calls and about 90M input tokens (2026-10-06). -->
- Search budget: research: 13 questions, one or two searches each, by three agents (research.md). Council: at most 2 searches per lens, each naming its decision. Refuter: at most 2 <!-- REQUIRED:budget -->
- Appetite (the decider's, asked only when heading for design) | —: — <!-- REQUIRED:appetite -->

## What we found <!-- CLAIMS -->
- [★C1] No record holds a 3D model. 1 of 30 records holds a height above the board. 20 of 30 hold an outline in the board plane · E pre-analysis.md section 1 (survey of the repository and the store) · caveat: 30 records on 2026-11-26, the repository and one store
- [★C2] A module goes to the board with no body: `<chip footprint="pinrowN">` and no `cadModel` · E scripts/spark/design/board_sections.py:259 · caveat: none
- [★C3] tscircuit 0.0.2600, installed today, merges a local STEP body into its STEP export and its GLB. An STL body lands through the board in the STEP and breaks the GLB export · E pre-analysis.md section 4 (probe, 2026-11-26) · caveat: one run per variant on one probe board
- [★C4] tscircuit's STEP names each solid by reference (`PCB`, `U1`, `U2`) in one flat product. kicad-cli's STEP is an assembly. It names an instance by reference (`U2`), but only for a part with a model · E pre-analysis.md section 4 · caveat: names in the file. Whether Fusion shows them is not run
- [★C5] tscircuit already draws a two-part printed case, `<enclosure.fdm.box>` (create-fdm-enclosure 0.0.4, MIT): a base and a lid with a lip and cut-outs per part. It has no mounting bosses yet · E the installed README, and the probe: two solids about 54 x 42 x 15 mm around a 50 x 36 mm board · caveat: version 0.0.4, the case was not printed or measured
- [★C6] tscircuit's 3MF export (`component-box-3mf`) fails in the installed CLI for a missing `manifold.wasm` · E probe log · caveat: one run, installed version 0.1.2113
- [★C7] Every library model found is CC-BY-SA, private-use or under unclear terms, except Adafruit's (MIT). So spark fetches a model at use time into the person's store and never commits it · E research.md section 1 · caveat: the terms of four sites were not read
- [★C8] No library found holds a model of the dev boards spark uses (DevKitC, C6 DevKitC, XIAO, FireBeetle). KiCad and Espressif hold modules (WROOM and others) only · E research.md section 1 · caveat: Seeed and DFRobot hold a few STEP files by wiki page, not checked for these boards
- [★C9] build123d (Apache-2.0) writes STEP with each shape's label as its name, and GLB, STL and 3MF, headless. Its kernel wheel is 62.5 MB · E research.md sections 1 and 2 · caveat: the install size on disk was not measured
- [★C10] Fusion's personal licence keeps STEP export, STL, scripts and add-ins, by Autodesk's blog of 2020-09-25. Its compare page of 2026-11-17 ticks no "File export" for personal use. The "80 cm²" limit is not on that page · E research.md section 3 (Wayback copies, because autodesk.com returned 403) · caveat: the two pages do not agree, and only a run on the PO's Fusion settles it
- [★C11] Fusion has a built-in MCP server that runs on the person's Mac while Fusion is open. Its page names no licence tier · E research.md section 3 (help.autodesk.com) · caveat: not turned on or run
- [★C12] Fusion 360, KiCad 10.0.6 and PrusaSlicer are installed on the PO's Mac. FreeCAD and OpenSCAD are not · E pre-analysis.md section 3 · caveat: installed is not used. How he uses them is an account question
- [★C13] TurboCase (MIT) makes an OpenSCAD case from a `.kicad_pcb`: posts at mounting holes, cut-outs from each part's box and a height property · E research.md section 4 · caveat: not run
- [★C14] The 2D part drawing is already a Strategy family (`ShapeSource` and three sources), and the tools list maps a role to a tool. No 3D role and no 3D Operation exist · E scripts/spark/breadboard/part_shape.py:61-263, data/tools.json `roles`, scripts/spark/operation_catalogue.py · caveat: none
- [C15] kicad-cli writes GLB (109 KB on the probe) and a raytraced PNG · E pre-analysis.md section 4, P1089 finding section 2.1 · caveat: KiCad is optional for a person
- [C16] No perfboard layout or drawing exists, so a perfboard has no 3D start · E scripts/spark/flow/flow_codes.py:479, P1199 pre-analysis · caveat: none
- [C17] One-image AI models give no metric scale, and photogrammetry handles thin shiny boards badly. A box with the photo as its top face gives the exact size from measurements · H research.md section 1 (the agent's judgement) · caveat: untested here
- ⟨fill after the council⟩ <!-- REQUIRED:findings -->

## Options <!-- CLAIMS -->
- ⟨fill⟩ <!-- REQUIRED:options -->
- Proposed no-gos and rabbit holes (proposals until the decider confirms): ⟨fill⟩ <!-- REQUIRED:nogos -->

## Riskiest assumption and its test
- Riskiest: ⟨fill⟩ · proposed — ⟨whose opinion⟩, pending Q1 <!-- REQUIRED:riskiest -->
- Test · kind · pass line, dated before any result · proposed: ⟨fill⟩ <!-- REQUIRED:test -->

## Questions
- Q0 · Is this frame right: the decision, the start and reach, the extensions and the depth? · decides: the frame · status: queued <!-- REQUIRED:q0 -->
- Q1 · How important is each assumption, and what pass line must the riskiest test meet? · decides: importance and pass lines · status: queued <!-- REQUIRED:q1 -->

## Decisions

## Found on the way <!-- CLAIMS -->
- ⟨fill⟩ | none <!-- REQUIRED:found -->

## Board actions <!-- REQUIRED:spark-process:board-actions -->
- move #1745 to Discovery · taken by spark-main by 15:02 CET 2026-11-26, before this session started

## Hand-off
not yet: the frame, the jobs, a direction and the remaining risk are unconfirmed <!-- REQUIRED:handoff -->

## Files
[Pre-analysis](pre-analysis.md) · [Research](research.md) · [Jobs and journeys](jobs-and-journeys.md) · [Story map](story-map.md) · [Risks and tests](risks-and-tests.md) · [Verification](verification.md) · [Items](items.md) · council/
