# Proposed items
<!-- Filing needs the decider's yes to this list: a D in brief.md that names items.md. One block per item.
needed by: the decider's words, quoted. value proven by: a proof the decider can read. status: proposed, or filed D<n>. -->

At most three findings become items (D2); the rest of the found work is on the checklist below. Numbers follow spark's
next free P-number: P154 is #89, filed at the PO's request at 16:38 UTC on 2026-10-06 (`gh issue list --state all`, read about
19:15 CEST). Fields follow `.github/ISSUE_TEMPLATE/item.yml`, where *Needed by* and *Value proven by* are required.

## P154 (#89, filed) — the tools chore receives the council's tool findings
The adapter idea has its home already: #89, filed at his request for after this discovery (D6). This block
proposes no new issue, only that his chore starts with what this council found.
- type: chore, as filed <!-- REQUIRED:item-type -->
- needed by: the PO, 2026-10-06, verbatim on #89: "About the settingss and configurable and changable enginwes and strategies and tools and mcp vs local cli - lets note it down and have the council come up with a good easy system we can use and what would actyaslly be product wise useful and valuable and cheap enough for our use cases? Don't do it now, only create a chore and we can get to it right after what we're doing is done"; and, relayed to this run, "yes, keep only the best one, we can offer the other tools in settings, but then it would have to be easy to switch, some adapter or plugin.." <!-- REQUIRED:needed-by -->
- value proven by: #89 carries, as one comment, the council's tool findings: for each job the free local candidate and its alternatives, each marked free or not, local or networked, and with or without an MCP version (EX-27); what exists today, twin entries and `--use` (EX-28, FE-19); what is missing for "easy to switch" (FE-18, FE-20); so that his chore's council starts from them <!-- REQUIRED:value-proven-by -->
- depends on: this discovery's end, per his "right after what we're doing is done"; his yes to the comment <!-- REQUIRED:depends-on -->
- status: proposed — a comment on #89, no new issue <!-- REQUIRED:item-status -->
- label (the repository's type label): chore, as filed <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): — as filed; #89 names P136 as related <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): "8 A board you can order", as on the board <!-- REQUIRED:spark-process:slice -->
<!-- EXTEND:item-fields -->

## P155 — An open-drain line's level is checked against the pin that reads it, from the part records' facts
- type: story <!-- REQUIRED:item-type -->
- needed by: bin B25 (sisuo-brain-transplant#19): the ToF wake line asserts at 1.89 V, below the ESP32-S3's 2.475 V input-high level, and spark's checks on the bin's files say nothing about it. The PO on #70, 2026-10-06: "in general, can spark do that? to say, hey, there's this problem, I suggest you add either this or make that which would ... then even calculate the components?" <!-- REQUIRED:needed-by -->
- value proven by: a spark check run on the bin's files reports TOF_INT at 1.89 V awake against 2.475 V, and at most 2.33 V with the sensor pin's own maximum 10 µA, so that no pull-down value fixes it, while a much stronger carrier pull-up or a source tied to 3.3 V can, each with its cost (a 2.2 kΩ carrier pull-up reaches 2.589 V at the worst corner and draws about 1.27 mA asleep, calculated); it prints each input with its source and marks typical-only or unsourced inputs `?`; two readers write the expected figures before the code (A2's test); a mutation that drops the pin's current turns the suite red <!-- REQUIRED:value-proven-by -->
- depends on: Q4, Q6 and Q10; P143 (#77), so that no severity vanishes; the inputs no record holds as a fact: the output type (in no form), the series 1 kΩ (prose only), the S3's input-high ratio, the pin's input current, the firmware's pull per state; a fix catalogue and its re-check are a later story <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): story <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P136 (#70) <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): "4 v1 on two projects", beside P152 (#86), B25's record and chip half; or P136's own, per Q11 <!-- REQUIRED:spark-process:slice -->

## P156 — The trace-current rule examines every net that carries a part's current, not only the nets the rules file names
- type: bug, if Q15 is answered yes; otherwise naming the net in the bin's rules file suffices, and no item is needed <!-- REQUIRED:item-type -->
- needed by: bin B28 (sisuo-brain-transplant#22): "The motor's current reaches its shunt over 0.15 mm track, lifting the driver's ground 300 mV at 2 A where board.tsx counts 200". KiCad's DRC at its default rules flagged it among the 199 tracks narrower than 0.2 mm; spark's trace-current rule never looks at that net, because the bin's rules file names only MOTOR6V, GND and V33 (PH-14). The PO, 2026-10-06, on KiCad: "I just want to know if the user needs to have it or not". B28 is filed; no design is blocked by it, which W14 asks for <!-- REQUIRED:needed-by -->
- value proven by: on the bin's files, with the rules file unchanged, spark's physics check names MOTOR_SENSE, its 0.15 mm width and its rise at the stated 1.5 A bound; a mutation that limits the rule to named nets turns the suite red <!-- REQUIRED:value-proven-by -->
- depends on: Q15; where a net's current comes from, the records or the rules file; the motor's real current is unmeasured (bin B15) <!-- REQUIRED:depends-on -->
- status: proposed <!-- REQUIRED:item-status -->
- label (the repository's type label): bug <!-- REQUIRED:spark-process:label -->
- parent (the epic, as a sub-issue): P133 (#67), "the checks tell the truth"; related to P136 <!-- REQUIRED:spark-process:parent -->
- slice (one Slice option of the board, or "ask the decider for a new one"): "4 v1 on two projects", with P133's other cards <!-- REQUIRED:spark-process:slice -->

## Board actions
<!-- Each action, taken or pending, with its D. -->
- comment on #89 with the council's tool findings · pending his yes to this list <!-- REQUIRED:board-actions -->
- file P155 under #70 and P156 under #67, each with its label and Slice · pending his yes to this list
- after filing, run the push check (`tools/check_backlog.py`) and change `scrum/STORY_MAP.md` in the same change as the Slice field · pending

## Checklist
The rest of the found work, kept here and proposed as nothing until a decision or a design pulls it.
- The journey guide says "Nothing here measures the spacing between nets" (`docs/guide/journey.md:605-606`); tscircuit's build measures it against its router's 0.1 mm, though the same guide says the build stops on tscircuit's errors (`:603`): a docs fix once Q3 is answered.
- Passing the fab's minimums to tscircuit's checks would not touch a hand-written board such as the bin, needs spacing keys `data/fabrication.json` lacks, and could fail `check_spine` on boards that pass today (council/refuter.md, part 2): only if Q3 asks for it.
- A rail's standing current at rest, summed from the records, would catch B26 (PH-8): Q4 (c)'s third candidate.
- The ToF draws about 2.46 mA with nothing in view at 2 Hz, seven times the bin's 340 µA estimate (calculated, PH-6); which case holds depends on the lid window: the bin's sleep budget.
- The amplifier's shutdown line is not held in deep sleep, which could cost about 340 µA (H, PH-7): a bench check at bin B14.
- The bin's rules file still describes V33 as "the DFR0534 plus the ESP32" and gives the wake line's pull-down 33 µA where B25 gives 19 µA (JO-9): the bin.
- The two open items on B28's DRC checklist (the V33 feed to the amplifier at 0.15 mm; copper and holes in keepout areas) stay with the bin.
- B26 says the AA set is flat in about 20–26 days; its own 6.4–7.1 mA against 3.0 Ah give about 17.6–19.5 days, unless the cell holds more than 3.0 Ah at that drain (the 3.0 Ah is rated at 25 mA): a question on bin #20.
- P152's third proof may be out of Wokwi's reach if its "simulation" means Wokwi (EX-14): a comment on #86, after a Wokwi run the PO approves.
- The design-reviewer agent has only Read and Grep, so it cannot run a calculator (EX-7): an input for P136's Design.
- For P102e's review: a lens id with a colon makes a file name a Windows checkout cannot hold (the physics report is saved as `electronics-firmware-physics.md`), and `discovery.py check` counts bulleted searches only.
- 51 of 74 open board items with an id are missing from `scrum/STORY_MAP.md`: P146 or P102b.
