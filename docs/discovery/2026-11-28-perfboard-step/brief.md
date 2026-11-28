<!-- Resume: invoke product-discovery again; `discovery.py check <this folder>` names the next step. -->
# The perfboard step: discovery brief

<!-- Readiness, its one home. collecting evidence: anything short of the two below. an experiment: the decider chose
a test (a D) before choosing an option. design: the decider confirmed the frame, the jobs and a direction, and accepted
the remaining risk (D rows). An extension may tighten these. Next: design, or a chosen test of kind spike or prototype
→ the design skill the facts name, with this file; otherwise none, and the collection plan says who runs it.
Stands on: the assumptions not retired in risks-and-tests.md; of which those the decider rated high, or — while any
is unrated. check computes both. -->
**Ready for:** ⟨fill⟩ <!-- REQUIRED:ready -->
**Stands on:** ⟨fill⟩ H, ⟨fill⟩ of which would change the decision <!-- REQUIRED:debt -->
**Decision needed:** ⟨fill⟩ <!-- REQUIRED:decision-needed -->

## Frame
- Request, verbatim (corrections marked): the PO, 2026-11-28, about 10:55 CET, relayed by spark-artifact: "I'd actually like you to start refining and planning and designing etc. the perfboard step, it should actually maybe not be so much different from the breadboard, they will definitely share some modules or strategies and interfaces if you will, like routable, etc. etc. Make sure the architecture is good as usual, reusable, feel free to refactor anytime you think something could be dried out (that works in general, if it kinda makes sense, we don't want to have multiple places in the codebase implementing almost the same, remember this), so yeah, lets do that, including the designs, etc." And on P1350 #1937, the same morning: "lets just leave the penalties for turning and crossing and such configurable or at least as constants in the code, so that we can later play around with it." <!-- REQUIRED:request -->
- Decision · decider: D-q1 the perfboard step for a person: from a tested breadboard to a soldered board, what they pick, see and do (the board from the drawer, the plan, the two sides, the step sheet, the check) · D-q2 what the breadboard and the perfboard share (a surface of holes, a placer, a router search with named costs, the same-pins check, a step-sheet writer, the scene drawing), which existing breadboard code moves into that shared part, and which stays per surface · D-q3 the joins and their router: solder bridge, bare wire on the back, insulated jumper over a crossing, and the costs that choose between them as named constants or settings · D-q4 parts on a perfboard: a dev board on headers or sockets, a resistor's lead span, the part pictures without pins (P275 comment of 2026-11-20) · D-q5 the perfboard record and the cut size (P275 note 2, P1199 D-q7) · D-q6 the order against the MVP, P1237 #1790 (the layout skeleton) and the spikes P1238 #1791 and P1239 #1792 · decider: the PO <!-- REQUIRED:decision -->
- Outcome and how it is observed (a metric with unit and source, a proof command, or a log): proposed: one written answer per decision, each fitting the core (one small class behind an Operation, interfaces thin, nothing twice). Observed later when (1) a button-light perfboard plan passes the same-pins check with its routes read as joins (P275 #311's Done when), (2) the breadboard plans through the shared part with 8 of 9 golden breadboards byte for byte and the rebuild golden's diff read (P1199 D13, tests.test_golden_breadboard), and (3) one search for a second surface class, router or sheet writer in scripts/spark finds none (a grep named in the design) <!-- REQUIRED:outcome -->
- Already decided (D · who · when · where; include the product's stated non-goals and earlier decisions the request names): D-a · the perfboard comes after the editor that keeps moves, stripboard dropped · the PO · 2026-10-16 · P269 D8, #310 closed · D-b · "Spark plans, Claude changes": a fresh plan that keeps the tested pins, dragging later with P1163 #1699 · the PO · 2026-11-26 · #311 note 1 · D-c · the person's perfboard sizes come from the drawer, cut smaller, never bigger · the PO · 2026-11-26 · #311 note 2 · D-d · three join kinds from one search, and "I am not sure what the best practices are actually" · the PO · 2026-11-26 · #311 note 3 · D-e · the perfboard drawing takes the breadboard's part pictures without pins and with soldered vias · the PO · 2026-11-20 · #311 comment · D-f · one layout core on whole holes, built after the MVP in the first slice that needs it; edits only in .spark/layout-edits.json; only placed parts stay at a rebuild; roomy is the perfboard's default with the size in holes and mm; he measures the FIT0193 when the perfboard card is pulled; 8 of 9 goldens · the PO · 2026-11-26 · P1199 D3, D4, D6, D7, D8, D13 · D-g · tscircuit stays the PCB engine and KiCad an optional export, after the MVP · the PO · 2026-11-26 09:03 CET · option B, P1089 · D-h · the router's penalties stay named constants or settings · the PO · 2026-11-28 · #1937 comment · D-i · never several places that implement almost the same thing · the PO · 2026-11-28 · the request · D-j · every configurable choice names its setting, default and layer · the PO · 2026-11-26 · P1193 D8 · D-k · one core, many interfaces, CLI first; spark exports facts; free, few and local · AGENTS.md <!-- REQUIRED:decided -->
- Open questions: see Questions <!-- REQUIRED:open -->
- Scope · out of scope (proposed): in: the perfboard step's journey and screens, the shared layout parts and the breadboard code that moves into them, the joins and the router's costs, the perfboard step sheet, the perfboard record, parts on a perfboard, the order · out: building any of it (his Ready order), the PCB (D-g), stripboard (D-a), the drag editors (P1163 #1699, P1162 #1698), merge, a photo of a soldered board (P1164 #1700), a paid tool <!-- REQUIRED:scope -->
- Start and reach (proposed until Q0): start existing product · decider reachable yes, through this session's question dialog and spark-main's rounds; when he is away, the council of three answers what he delegates, recorded as "delegated, the PO's to change" · users none reachable beyond the PO · data and connectors: the repository, gh, the store (read-only), the canvas "spark project page", web search · decider as a user n = 1 · must not get worse: the golden breadboards' bytes (tests/golden-breadboard), the router's budget and P1350 #1937 in Build on wire_routing.py, the same-pins check (P279), the build's time, Wokwi taking breadboard.json <!-- REQUIRED:start-reach -->
- Flags (yes · no · —; asked only when it changes a decision; never legal advice; any date or threshold is read at its source at run time and cited):
  - sold or given away, or personal use: personal use now. Spark is public under MIT <!-- REQUIRED:flag-sold -->
  - connects to a network or runs software (for example the EU's Cyber Resilience Act): no change: the plan runs locally <!-- REQUIRED:flag-network -->
  - children or food contact: no <!-- REQUIRED:flag-children -->
  - market: — <!-- REQUIRED:flag-market -->
  - radio (unlicensed-device rules; read at their source when it decides): n/a, but a dev board's antenna end must not sit over a bare wire or the board's edge copper; the tech lead checks it <!-- REQUIRED:electronics-firmware:flag-radio -->
  - a Li-ion cell (charging, transport, battery rules): n/a now: no part record holds a cell. A cell holder soldered on a perfboard later brings its own rules <!-- REQUIRED:electronics-firmware:flag-li-ion -->
  - mains: no <!-- REQUIRED:electronics-firmware:flag-mains -->
  <!-- EXTEND:flags -->
- Extensions (each active id · the fact that activated it; when none matched, only "none matched: core only · the fact that decided it", naming no extension; list any directive skipped under rule 9): electronics-firmware · repo-has boards/*.json; spark-process · repo-has scrum/WORKING_AGREEMENTS.md <!-- REQUIRED:extensions -->
- The item (its issue, or the proposal in the decider's words) · what is still open elsewhere · the repository's push check, or "no push check here": P1352 #1939 (https://github.com/xmejkal/spark/issues/1939), filed by spark-main on 2026-11-28 in Discovery, slice Views and editors, a sub-issue of the epic P1199 #1747; P275 #311 stays the build card with its spikes · still open elsewhere: P275 #311 (the perfboard), P1199 #1747 (the layout core), P1237 #1790 (its skeleton), P1238 #1791 (calipers), P1239 #1792 (the join router spike), P1350 #1937 (in Build, the router's clearance rule), P1163 #1699 (moves), P1194 #1740 (settings) · the push check is the pre-push hook <!-- REQUIRED:spark-process:item -->
<!-- EXTEND:frame -->
- Depth: TRIO (default: PO assistant, user, tech lead) | FULL or LIGHT (who asked, when); add "no independent review" if subagents could not start: TRIO on Opus (the PO assistant, the user with the UX and AI-UX lens, the tech lead with the Physics lens), plus the architecture lens on Opus, because the design moves breadboard code into a shared part. P1199 ran FULL two days ago, so this discovery reads its council and does not repeat it. Then the refuter on Opus, and the architect writes the design <!-- REQUIRED:depth -->
  <!-- Cost, measured once: the P900 rehearsal's council took 6 agents, 499 calls and about 90M input tokens (2026-10-06). -->
- Search budget: the tech lead may make up to 4 searches on perfboard practice (P275 note 3 asks to check it). The other lenses read the repository, the store and P1199's folder, read-only. The architect and the refuter may fetch up to 3 pages each <!-- REQUIRED:budget -->
- Appetite (the decider's, asked only when heading for design) | —: — <!-- REQUIRED:appetite -->

## What we found <!-- CLAIMS -->
<!-- One claim per line: `- [★C<n>] claim · E pointer | H source | D who date · caveat: qualifier | none`.
★ marks a claim that a decision, an option or the riskiest assumption rests on. A quote is verbatim, with its pointer.
Say what the evidence can support: an account (what happened to one person), data (how often, in its population and
period), a document (what was specified), the product (what exists, not whether anyone needs it), a benchmark (a
comparison). Model knowledge is H until a source is read. Elsewhere cite a ★ claim as ★C<n>, with its keep: words.
e.g. `- [★C2] 13 of 526 tickets ask for recurring tasks · E tickets.csv:2-14 · caveat: picked by Lena; shows that, not how often` -->
- ⟨fill⟩ <!-- REQUIRED:findings -->

## Options <!-- CLAIMS -->
<!-- Two or three per open decision: decision · option · cost · what it would prove · opinion (whose), then the tag
and caveat cells. e.g. `- Q2 what first · fix delivery · two weeks · whether seen tasks get done · opinion (the facilitator's) · H ★C2 · caveat: none` -->
- ⟨fill⟩ <!-- REQUIRED:options -->
- Proposed no-gos and rabbit holes (proposals until the decider confirms): ⟨fill⟩ <!-- REQUIRED:nogos -->

## Riskiest assumption and its test
- Riskiest: ⟨fill⟩ · proposed — ⟨whose opinion⟩, pending Q1 | D<n> <!-- REQUIRED:riskiest -->
- Test · kind · pass line, dated before any result · proposed | D<n>: ⟨fill⟩ <!-- REQUIRED:test -->

## Questions
<!-- A queue; the first open question is asked alone. Each: Q<n> · question · decides: … · options · unblocks ·
opinion (whose) · kind: decision | account (a past-tense question about the decider's own use; the answer is E,
account, n = 1) · status: queued | asked <date> | answered D<n>.
If the decider cannot be asked, the queue stays here, and whatever rests on it stays H. -->
- Q0 · Is this frame right: the decision, the start and reach, the extensions and the depth? · decides: the frame · status: ⟨fill⟩ <!-- REQUIRED:q0 -->
- Q1 · How important is each assumption, and what pass line must the riskiest test meet? · decides: importance and pass lines · status: ⟨fill⟩ <!-- REQUIRED:q1 -->

## Decisions
<!-- D<n> · what · who · when · where recorded · options considered.
A yes covers only the actions and choices it names. A standing yes names its kind of action and its source.
Name what a D confirms in its words: the frame, the jobs, a direction, the remaining risk, a test, items.md. -->
- D1 · Q0: the frame as written (the decisions D-q1 to D-q6, the scope and what is out of it, the extensions electronics-firmware and spark-process, the depth TRIO on Opus plus the architecture lens, then the refuter and the architect). His answer: "Yes, frame is right" · the PO · 2026-11-28, about 11:20 CET · this session's question dialog · options: yes, narrow it to the architecture and the canvas, let the council of three answer. It confirms the frame

## Found on the way <!-- CLAIMS -->
<!-- Outside this item's scope. Each is a separate proposal, never folded in. Same line format as What we found. -->
- ⟨fill⟩ | none <!-- REQUIRED:found -->

## Board actions <!-- REQUIRED:spark-process:board-actions -->
<!-- Each action on the board or the issue (stage, waiting flag, comment, filing): taken, with its D, or pending.
None is taken without a D. e.g. `- move #16 to Discovery · pending` -->
⟨fill⟩
<!-- EXTEND:brief-sections -->

## Hand-off
<!-- Written only after the decider confirms the understanding (a D); copies only confirmed constraints. Holds: outcome ·
who · success and its proof · constraints (appetite, confirmed no-gos, rabbit holes) · what they said (D) against what
we assume (H) · links to the journeys and the map · riskiest assumptions and their tests · options considered. -->
⟨the hand-off | not yet: what is unconfirmed⟩ <!-- REQUIRED:handoff -->

## Files
[Jobs and journeys](jobs-and-journeys.md) · [Story map](story-map.md) · [Risks and tests](risks-and-tests.md) · [Verification](verification.md) · [Items](items.md) · council/
