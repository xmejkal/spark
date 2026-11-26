<!-- Resume: invoke product-discovery again; `discovery.py check <this folder>` names the next step. -->
# One layout core for every surface (P1199): discovery brief

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
- Request, verbatim (corrections marked): the PO, 2026-11-26, quoted on #1747: "Alright and now back to the more real parts, what about the perfboard wiring router, is it well implemented and architected? using good algorithm to offer the best options of routing iwth options to go for the smallest size or to take up the whole perfobard and use the space, being also able for humans to edit the connections and move the parts around ? And what about the breadboard router and teh human/ai being able to move parts and wires around ? Can we refactor out some protocole or omdule or class or whatever to reuse for these common problems? Does it also support the steps reverting and all these Git or other strategies to save versions, merge projects, etc ? Please ask the mani coordinator to create all these and other cards based on thesde topics, lets create the epics, preanalyze, research,refine , plan, etc..  What about the webeditors for them?" And his standing rule for every brief, in the card's words: "The architecture needs to be well made so that we can change these strategies and tools and it is reusable and DRY: one seam per strategy, chosen by a setting, behind an Operation, interfaces thin, nothing twice." <!-- REQUIRED:request -->
- Decision · decider: D-q1 the core's boundary: which pieces are stage-neutral in mm (the surface and its hole groups, the ledger, the body, the placement, the router, the same-pins check), which stay with one surface (the breadboard's step order, rails and resistor pass, the perfboard's three joins), and which surfaces the core serves first · D-q2 placement goals: which goals (the first fit, the smallest board, spread over the whole board), which algorithm stands behind each, and the setting that chooses one · D-q3 perfboard routing: the three joins (a solder bridge, a bare wire on the back, an insulated jumper over a crossing), a second pass when a net fails, and what the same-pins check reads · D-q4 edits that survive a rebuild: what a move of a part or a wire is as a fact, which Operations a person and Claude call, and how keep moves joins P1193's one strategy as a kept step · D-q5 the web editors: what the breadboard and the perfboard pages edit, and what they reuse (P294's finding, perfwire) · D-q6 reuse of outside code: a dependency, a copy with its notice, or ideas only, per licence · D-q7 the perfboard record: the person's perfboards in the drawer, cut smaller but never bigger (the PO's note 2 on #311) · D-q8 the order by the MVP bar · decider: the PO <!-- REQUIRED:decision -->
- Outcome and how it is observed (a metric with unit and source, a proof command, or a log): proposed: one written answer per decision, each fitting the core (rules.md, "The core is important", 2026-11-25). Observed later when (1) the breadboard plans through the core in mm and the golden breadboards keep their bytes (tests/golden-breadboard, tests.test_golden_breadboard), (2) one setting switches the placement goal and the plan reports the used area in mm² for each goal, (3) a part moved by a person or by Claude through an Operation stays after a rebuild and goes back through P1193's take-back, and (4) a button-light perfboard layout passes the same-pins check with its routes read as joins (#311's Done when) <!-- REQUIRED:outcome -->
- Already decided (D · who · when · where; include the product's stated non-goals and earlier decisions the request names): D-a · the perfboard comes after the editor that keeps moves (step 5), and stripboard is dropped · the PO · 2026-10-16 · P269 D8, #310 closed (docs/discovery/2026-10-16-p269-views-and-editors/brief.md) · D-b · "it should stay where we move it" means a moved part keeps its position after a rebuild, or spark names why not · the PO · 2026-10-16 · P269 D11 · D-c · the same-pins check also warns about the person's edited breadboard.json · the PO · 2026-10-18 · #317 (P279, closed) · D-d · "Spark plans, Claude changes" for the perfboard. The person's perfboard sizes come from the drawer and are cut smaller, never bigger. Three join kinds · the PO · 2026-11-26 · #311 comment · D-e · a layout edit on the page is a kept step through the project timeline's one Service, with no second seam · delegated council of P1193, confirmed by the PO's D19 and D20 · 2026-11-26 · #1699 comment, docs/discovery/2026-11-26-p1193-change-tracking/items.md:56 · D-f · merge of two points waits · the PO · 2026-11-26 · P1193 D15 · D-g · every configurable strategy names its setting, its default and its layer, until P1194 #1740 holds them · the PO · 2026-11-26 · P1193 D8 · D-h · every feature is an Operation that the CLI reaches first, then MCP and code, for people and agents. Only what makes no sense outside one interface (a drag) stays in it · the PO · 2026-11-26 · his words in the P1194 session, kept in the memory note on the architecture direction · D-i · moving parts and wires on the page (P1163 #1699) comes after the MVP, slice parked · the PO · 2026-11-25 · #1699 · D-j · tscircuit stays the board engine, and KiCad is an export · the PO · 2026-11-26 · P1089 #1600 closed (P1193 brief, the item line) · D-k · one core, many interfaces. Spark exports facts. Free, few and local. MIT with no vendor file · AGENTS.md principles <!-- REQUIRED:decided -->
- Open questions: see Questions <!-- REQUIRED:open -->
- Scope · out of scope (proposed): in: the core's boundary and its unit, placement goals, perfboard routing and its joins, edits that survive a rebuild and their Operations, keep moves inside P1193's strategy, the web editors' shape for the breadboard and the perfboard, reuse and licences, the perfboard record, the order · out: building any of it, the PCB's placement draft and the circuit sculpture (the card names them as later clients, so only their fit is checked), stripboard (dropped, D-a), merge (D-f), "capture the reality" from a photo of a wired board (P1163's nice-to-have), drag and drop on other pages (P1162 #1698), a paid tool <!-- REQUIRED:scope -->
- Start and reach (proposed until Q0): start ⟨existing product | someone else's idea | own idea⟩ · decider reachable ⟨yes | no⟩ · users ⟨who, how | none reachable⟩ · data and connectors ⟨by category, from your own tool list; "not connected" is a gap; never ask to connect one⟩ · decider as a user ⟨n = 1 | no⟩ · must not get worse ⟨for an existing product⟩: start existing product · decider reachable yes, through spark-main's question rounds. When he is away, a council of three on Fable (the PO assistant, the architect, the tech lead) answers what he delegated, recorded as "delegated, the PO's to change" · users none reachable beyond the PO · data and connectors: the repository, gh, the store (read-only), and web search (spent in research.md) · decider as a user n = 1 · must not get worse: the drawn breadboard's bytes for an unchanged project (tests/golden-breadboard), a person's moves kept across a rebuild (P273, kept_moves.py), the same-pins check (P279), the build's time (the router's budget, wire_routing.py:207), and Wokwi taking breadboard.json <!-- REQUIRED:start-reach -->
- Flags (yes · no · —; asked only when it changes a decision; never legal advice; any date or threshold is read at its source at run time and cited):
  - sold or given away, or personal use: personal use now. Spark is public under MIT <!-- REQUIRED:flag-sold -->
  - connects to a network or runs software (for example the EU's Cyber Resilience Act): no change: the layout runs locally. A web editor runs in a page, and its host is P1038's question <!-- REQUIRED:flag-network -->
  - children or food contact: no <!-- REQUIRED:flag-children -->
  - market: — <!-- REQUIRED:flag-market -->
  - radio (unlicensed-device rules; read at their source when it decides): n/a: the layout moves no antenna and changes no radio <!-- REQUIRED:electronics-firmware:flag-radio -->
  - a Li-ion cell (charging, transport, battery rules): n/a: the layout does not touch a cell <!-- REQUIRED:electronics-firmware:flag-li-ion -->
  - mains: no <!-- REQUIRED:electronics-firmware:flag-mains -->
  <!-- EXTEND:flags -->
- Extensions (each active id · the fact that activated it; when none matched, only "none matched: core only · the fact that decided it", naming no extension; list any directive skipped under rule 9): spark-process · repo-has scrum/WORKING_AGREEMENTS.md · electronics-firmware · repo-has boards/*.json. It stays on because the layout decides which holes join, and a perfboard join carries current (a run of several amps needs a thicker wire, the PO's note 3 on #311). Its Physics lens goes to the tech lead <!-- REQUIRED:extensions -->
- The item (its issue, or the proposal in the decider's words) · what is still open elsewhere · the repository's push check, or "no push check here": P1199 #1747 (https://github.com/xmejkal/spark/issues/1747), an epic in Discovery since 12:58 CET 2026-11-26, slice Views and editors. Still open elsewhere: P275 #311 (plain perfboard), P1163 #1699 (move a part or a wire, after the MVP), P1162 #1698 (drag and drop), P269 #304 (views and editors), P293 #352 (working with the breadboard), P1193 #1738 (one strategy for versions), P1152 #1688 (the project timeline), P1194 #1740 (settings in layers). The push check is the pre-push hook <!-- REQUIRED:spark-process:item -->
<!-- EXTEND:frame -->
- Depth: TRIO (default: PO assistant, user, tech lead) | FULL or LIGHT (who asked, when); add "no independent review" if subagents could not start: FULL, as spark-main's brief of 2026-11-26 asks ("Opus for you and the council's lenses, the architect agent for the synthesis, the refuter on Opus"), proposed until Q0. Four lenses on Opus: the PO assistant, the user (with the UX and AI-UX lens by the PO's rule of 2026-10-18), the tech lead (with the Physics lens), and the architecture lens, because the epic makes a new core piece. Then the refuter on Opus and the architect for the synthesis <!-- REQUIRED:depth -->
  <!-- Cost, measured once: the P900 rehearsal's council took 6 agents, 499 calls and about 90M input tokens (2026-10-06). -->
- Search budget: the research step spent 11 searches and 4 page reads (research.md). The lenses read the repository and the store, read-only. Only the PO assistant may make up to 3 searches, for a tool that research.md missed. The architect and the refuter may fetch up to 5 pages each, to check a source that a decision rests on <!-- REQUIRED:budget -->
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
- Q0 · Is this frame right: the decision, the start and reach, the extensions and the depth? · decides: the frame · status: asked 2026-11-26 through spark-main <!-- REQUIRED:q0 -->
- Q1 · How important is each assumption, and what pass line must the riskiest test meet? · decides: importance and pass lines · status: queued <!-- REQUIRED:q1 -->

## Decisions
<!-- D<n> · what · who · when · where recorded · options considered.
A yes covers only the actions and choices it names. A standing yes names its kind of action and its source.
Name what a D confirms in its words: the frame, the jobs, a direction, the remaining risk, a test, items.md. -->

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
