<!-- Resume: invoke product-discovery again. `discovery.py check <this folder>` names the next step. -->
# P735 full records of the PO's DFRobot parts: discovery brief

**Ready for:** collecting evidence. The frame (D1) and the direction (D2) are the PO's. The jobs, the importance of each assumption and the pass line of A1 wait on Q1. <!-- REQUIRED:ready -->
**Stands on:** 6 H, — of which would change the decision, until Q1 rates them <!-- REQUIRED:debt -->
**Decision needed:** the PO rates A1 to A6 and sets the pass line of the geometry count (Q1). Then the design of the research pipeline starts in plan mode with a council (D2). <!-- REQUIRED:decision-needed -->

> TL;DR. Four walks ran spark's research flow on four owned DFRobot parts. All four made a valid record, but none reached a record with verified holes and pin positions. The record has no field for a picture, a schematic, holes or connectors, and the breadboard drawing reads none of them. Twelve tool bugs and gaps make each record a hand job. The PO's direction (D2) is a designed research pipeline with swappable sources and strategies, DFRobot first.

## Frame
- Request, verbatim: "Run the product discovery for P735 (#1010): full records of my DFRobot parts, or at least a subset, and take notes, we'll fix gaps and bugs afterwards." Then, during the run: "So it might be a good idea to plan it with the council so that it fits our acrchitecture and usage cases and is ready for the after refactoring state, to be fully reusablew, with interchangable sources or strtegies, etc, we can just do MVP now of DFRobot, later we can add other search sources, probably it should also be configurable what it uses to get it from the online info, whether the datasheets, just site search, clcking through, a text description for a human or ai, or something elese. Let's really have it well designed so it becaomes a good base for all modules, parts and boards" (the PO, 2026-11-10, this session, spelling as typed). The card's words are in #1010. <!-- REQUIRED:request -->
- Decision · decider: what the research pipeline must do and in which order the gaps and bugs get fixed · the PO. <!-- REQUIRED:decision -->
- Outcome and how it is observed: a record of an owned DFRobot part holds the picture, schematic, outline, holes and connectors. Each has its source or "not published", and spark shows them. Proof: `parts.py --show <id>` for each walked part, and the board page or breadboard sheet that shows the fields. <!-- REQUIRED:outcome -->
- Already decided: D1 the frame (walk a subset, take notes, fix afterwards). D2 the direction (a designed pipeline, swappable sources and strategies, DFRobot MVP, one base for modules, parts and boards). D3 the epic and its six sub-issues (#1010 comment, 2026-11-10). AGENTS.md: spark exports facts, records grow by need (P94), free few and local, never commit a vendor file, one core many interfaces (v0.13, #94). <!-- REQUIRED:decided -->
- Open questions: Q1 below. The scope of "every part" (PCB modules and boards, or also cables and motors). If DFRobot gives no shape, whether spark can make one (P446 and P734 disagree, PO-27). Which revision of DFR1117 the PO owns. <!-- REQUIRED:open -->
- Scope · out of scope (proposed): records of owned DFRobot PCB modules and boards, the research flow that makes them, and the bugs the walks found · out: AliExpress and other vendors (later sources under D2), the breadboard drawing code (P734), prices and stock. <!-- REQUIRED:scope -->
- Start and reach: start existing product · decider reachable yes · users the PO himself (n = 1), no other users reachable · data and connectors: the store and drawer (read), the web (read), Chrome (connected, not used), Miro (connected, not used) · decider as a user n = 1 · must not get worse: the existing 16 records and the build chain that reads them. <!-- REQUIRED:start-reach -->
- Flags:
  - sold or given away, or personal use: personal use, spark is public under MIT <!-- REQUIRED:flag-sold -->
  - connects to a network or runs software: no, records are data <!-- REQUIRED:flag-network -->
  - children or food contact: no <!-- REQUIRED:flag-children -->
  - market: none, records in the PO's own store <!-- REQUIRED:flag-market -->
  - radio: no, records only (DFR1117 has a radio, but no decision here rests on radio rules) <!-- REQUIRED:electronics-firmware:flag-radio -->
  - a Li-ion cell: no decision here rests on it (DFR1117 charges one) <!-- REQUIRED:electronics-firmware:flag-li-ion -->
  - mains: no <!-- REQUIRED:electronics-firmware:flag-mains -->
  <!-- EXTEND:flags -->
- Extensions: electronics-firmware · repo-has boards/*.json; spark-process · repo-has scrum/WORKING_AGREEMENTS.md <!-- REQUIRED:extensions -->
- The item: P735 #1010, an epic in Discovery · still open elsewhere: P733 #1003 waits on the PO's bench (sound lane), no open PR · push check: the push hook and `tools/check_backlog.py`. <!-- REQUIRED:spark-process:item -->
<!-- EXTEND:frame -->
- Depth: TRIO (PO assistant, user, tech lead), three agents on Sonnet, plus four walk agents (spark's parts-researcher, Opus) and one refuter. <!-- REQUIRED:depth -->
- Search budget: 8 searches and 12 fetches per walk (the researcher's own rule), 3 for the PO assistant, 2 for the tech lead, none for the user. Used: 5 searches over the walks, 1 by the tech lead, 3 by the PO assistant. <!-- REQUIRED:budget -->
- Appetite: unknown, asked at the design council. <!-- REQUIRED:appetite -->

## What we found <!-- CLAIMS -->
- [★C1] None of the 4 walks reached verified hole and pin positions. Only DFR1117 had a footprint file (DFRobot's KiCad `.kicad_mod` in a layout zip). Height or thickness was missing in 3 of 4. · E council/po-assistant.md:38, council/po-assistant.md:59, walk/dfr1117/diary.md:20 · caveat: 4 parts picked by Claude for shape variety, shows that gaps exist, not how often <!-- REQUIRED:findings -->
- [★C2] A part record has no field for a picture, a schematic, mounting holes, header positions or connectors. The validator accepts unknown keys without a word. · E council/tech-lead.md:9 · caveat: none
- [★C3] The breadboard sheet draws a part only if its record names a Wokwi part that `data/wokwi-geometry.json` holds, and that file holds 4 types. One undrawable part stops the whole drawing. · E council/tech-lead.md:12 · caveat: fuller records alone change nothing on screen until P446 or P734 adds a reader
- [★C4] Reuse-first misses parts the PO owns. `parts.py --need "load switch"` finds nothing, though the drawer holds 8 DFR0457 with function load-switch and the shelf holds its record. `--need ESP32-C6` misses the shipped XIAO ESP32-C6 board. · E council/tech-lead.md:26, walk/dfr0457/diary.md:40 · caveat: none
- [★C5] Spark has no research flow for a dev board. research.md covers parts only, `--skeleton` has no board kind, and `--unverified` and `--sources` answer "no part called …" for a board. · E walk/dfr1117/diary.md:39, council/tech-lead.md:30 · caveat: none
- [★C6] Eight walk bugs reproduce: `--skeleton` writes the forbidden `sourcing` block with prices, `--skeleton` hides a shelf record with no warning, `--fact-set` refuses `legs` and `host_requirements`, `--read` answers FOUND on the absolute-maximum row and on a revision-history row, `check_vendor_pins` fails bare GPIO labels, `boards.py --validate` passes a stand-in with no Wokwi document. · E council/tech-lead.md:27, council/tech-lead.md:33 · caveat: reproduced on scratch copies, nothing changed
- [★C7] `--fetch` keeps only .pdf, .jpg, .png, .webp and .svg. DFRobot ships STEP, CAD and layout files as zips, so they have no route into the store. · E walk/dfr0995/diary.md:40 · caveat: none
- [★C8] Vendor pages carry harm. The SEN0526 wiki pin table order is not the pad order, and wiring by the table swaps 3V3 and GND. DFR0995 says "3.3V" in one table and "DC3.3V-5V" in another. DFR1117 VIN is the USB 5 V wire, so VIN plus USB back-feeds the computer, and a board record has no warnings list. · E walk/sen0526/sen0526-i2s-mic.json:282, walk/dfr0995/diary.md:47, walk/dfr1117/diary.md:67 · caveat: read from vendor documents, not measured
- [★C9] The 99 DFRobot drawer entries are not 99 modules. They include cables, motors, a solar panel, a lock and a mystery box. About 19 of 112 drawer rows link a record. · E council/po-assistant.md:10, council/po-assistant.md:11 · caveat: the 19 is a rough grep, and the PCB-module count is not counted (H about 50 to 60)
- [★C10] One record costs 1 to 2 searches, 3 to 8 fetches and 5 to 16 URL checks, and 7 to 30 minutes of agent time. At 3 to 8 fetches, 99 records are 300 to 800 fetches. · E council/tech-lead.md:49, walk/dfr0995/diary.md:74, walk/dfr1117/diary.md:84 · caveat: 4 walks, times are the agents' own estimates
- [C11] The DFR0457 shelf record says 12 V logic exceeds the opto's 50 mA limit. The arithmetic gives 23 mA at 12 V. · E council/tech-lead.md:75 · caveat: calculated from a typical forward voltage
- [C12] Two hardware revisions sell as DFR1117, with a different regulator (0.6 A against 2 A) and deep-sleep current (14 µA against 37 µA, stated). The PO's revision is unknown. · E council/tech-lead.md:80 · caveat: a photo of the board's back settles it
- [C13] The open cards disagree. P446 says a shape source never calls an AI, the PO's words on P734 list "AI generated and vectorized". P446 plans a `PartShape`, a board record holds `physical`. · E council/po-assistant.md:50 · caveat: none
- [C14] part-data.md:51 says "DFRobot ships no KiCad footprints". The DFR1117 layout zip holds one. · E council/po-assistant.md:22, walk/dfr1117/diary.md:20 · caveat: one SKU

## Options <!-- CLAIMS -->
- Q2 what first · design the research pipeline in plan mode with a council (sources and strategies as swappable parts, one record shape for parts and boards, the bugs of ★C6 as its first slices) · a plan and two council rounds · that the shape fits the v0.13 core before code · opinion (Claude's, after D2) · D the PO 2026-11-10 · caveat: none <!-- REQUIRED:options -->
- Q2 what first · fix the bugs of ★C6 and ★C7 first, design after · about six small cards · that the hand steps go away · opinion (the tech lead's) · E council/tech-lead.md:27 · caveat: fixes can be redone by the design
- Q2 what first · batch the remaining owned parts now with today's tools · 300 to 800 fetches · nothing new, it copies each bug into every record · opinion (none holds it) · E council/tech-lead.md:49 · caveat: none
- Proposed no-gos and rabbit holes: no vendor file in the repository, keep it in the store only, because the licence is unknown. No AI-made shape until the PO settles C13. No batch before the pipeline. Rabbit hole: reading hole positions out of STEP B-splines (the DFR0995 STEP has 0 circles). · E council/po-assistant.md:50, walk/dfr0995/diary.md:22 · caveat: proposals until the PO confirms them <!-- REQUIRED:nogos -->

## Riskiest assumption and its test
- Riskiest: A1, DFRobot publishes enough geometry for most owned PCB modules · proposed — the PO assistant's opinion, pending Q1 <!-- REQUIRED:riskiest -->
- Test · kind · pass line: a script with no AI reads the wiki page of each owned PCB module and counts which link a dimension drawing, a schematic, a STEP and a layout zip. Then a person reads 5 drawings at random for hole and header coordinates · a spike · proposed pass line (set 2026-11-10, before any result): at least half of the PCB modules link a dimension drawing, and at least 3 of the 5 read drawings give hole positions · proposed <!-- REQUIRED:test -->

## Questions
- Q0 · Is this frame right: the decision, the start and reach, the extensions and the depth? · decides: the frame · status: answered D1 (the PO's request names the frame) <!-- REQUIRED:q0 -->
- Q1 · How important is each assumption, and what pass line must the riskiest test meet? · decides: importance and pass lines · status: queued <!-- REQUIRED:q1 -->
- Q2 · What goes first: the design, the bug fixes, or a batch? · decides: the order · options above · status: answered D2 (design with a council) <!-- REQUIRED:q2 -->
- Q3 · Which owned parts are in scope: PCB modules and boards only, or also cables, motors and panels? · decides: the size of the run and the meaning of "done" · status: queued
- Q4 · Which revision is printed on the back of your three DFR1117 boards? · kind: account · decides: which regulator and sleep current the record holds · status: queued, a photo settles it

## Decisions
- D1 · the frame: walk a subset of the owned DFRobot parts through spark's research flow, take notes, fix gaps and bugs afterwards · the PO · 2026-11-10 · this session's first request
- D2 · the direction: plan the research pipeline with the council so that it fits the architecture and the usage cases and the after-refactoring state, reusable, with interchangeable sources and strategies, configurable acquisition (datasheets, site search, clicking through, a text description for a human or AI, or something else), DFRobot as the MVP, a base for all modules, parts and boards · the PO · 2026-11-10 · this session · confirms a direction, not the remaining risk
- D3 · P329, P206, P209, P446 and P734 become sub-issues of P735, and the epic moves to Discovery · the PO · 2026-11-10 · #1010 comment
- D4 · standing approval: discovery output lands by PR, and cards move and get comments as the work happens · the PO · rules.md "The board", read 2026-11-10 · filing items is not covered

## Found on the way <!-- CLAIMS -->
- [C15] The DFR0457 shelf record holds irrigation wording (signal `VALVE_CTRL`, "four valves", "ESP32-S3") in a record every project finds. · E walk/dfr0457/diary.md:69 · caveat: none <!-- REQUIRED:found -->
- [C16] Library records disagree on whether a pin order read off a drawing is verified: `vl6180x-breakout` and `led-red-5mm` say true, the researcher\'s rule says false. · E walk/sen0526/diary.md:40 · caveat: none

## Board actions <!-- REQUIRED:spark-process:board-actions -->
- #1010 is in Discovery · taken before this session, D3
- set Waiting on: the PO and Waiting since 2026-11-10 on #1010 while Q1 waits · pending, D4
- comment on #1010 with the brief's link and the PR · pending, D4
- file the items in items.md · pending, needs the PO's yes
<!-- EXTEND:brief-sections -->

## Hand-off
not yet: the jobs, the importance of A1 to A6 and the pass line of A1 wait on Q1. <!-- REQUIRED:handoff -->

## Files
[Jobs and journeys](jobs-and-journeys.md) · [Story map](story-map.md) · [Risks and tests](risks-and-tests.md) · [Verification](verification.md) · [Items](items.md) · council/ · walk/
