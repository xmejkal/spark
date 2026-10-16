<!-- Resume: invoke product-discovery again; `discovery.py check <this folder>` names the next step. -->
# P269 views and editors: discovery brief

<!-- Readiness, its one home. collecting evidence: anything short of the two below. an experiment: the decider chose
a test (a D) before choosing an option. design: the decider confirmed the frame, the jobs and a direction, and accepted
the remaining risk (D rows). An extension may tighten these. Next: design, or a chosen test of kind spike or prototype
→ the design skill the facts name, with this file; otherwise none, and the collection plan says who runs it.
Stands on: the assumptions not retired in risks-and-tests.md; of which those the decider rated high, or — while any
is unrated. check computes both. -->
**Ready for:** collecting evidence <!-- REQUIRED:ready -->
**Stands on:** 11 H, — of which would change the decision <!-- REQUIRED:debt -->
**Decision needed:** Q1, the importance of each assumption and the pass line of the riskiest; then the queue below, first the slice order <!-- REQUIRED:decision-needed -->

## Frame
- Request, verbatim (corrections marked): the PO, 2026-10-16, on P269 (#304): "probably we will want to reuse code for the perfboard stagte, so please also create some common base, think about what the differences are, how making routes works there, etc, what other data we would nreed to store for parts/modules/boars to also enable the perfboard visualisation and editing. In the end we will want to have a really nice editor, wokwi is actually quite a good inspiration how it dowa its breadboare and also pcb and schema, so just keep that in mind, so me good thought through way of siplaying the schema in different stategs will be good to have and we will want to in the end have it really nicely made ux and graphics wise." His answers the same day: plain perfboard and stripboard, both; "Discovery first"; "It would be grteat to have the system made so that its easy to add more, we'de in the end ideally want to enable all these views, we can start by a webpage, vue probably, or some canvas and 3js typescript libraries maybe, ideally if reusable for the artifact and later even some electron version of the page for example. We will also want to enable the catalogue editing app for the parts and modules and boards and batteries, etc."; "it would be great if it could import images from web, sooner or later, of the parts etc. And think of saving and loading, sharing.." <!-- REQUIRED:request -->
- Decision · decider: which base model, which editor stack and which first slices spark builds for showing and editing one circuit in every stage · the PO <!-- REQUIRED:decision -->
- Outcome and how it is observed (a metric with unit and source, a proof command, or a log): the PO decides the base, the stack and the slice order from the brief (a D); then, per slice, a build stage writes a view the person opens. The first observable proof: P268's SVG of button-light drawn on the chosen base (`breadboard.svg` beside `breadboard.md`), checked by its tests <!-- REQUIRED:outcome -->
- Already decided (D · who · when · where; include the product's stated non-goals and earlier decisions the request names): D-a · discovery first, P268 waits · the PO · 2026-10-16 · the plan question in this session, recorded on #302; D-b · perfboard means plain perfboard and stripboard · the PO · 2026-10-16 · same; D-c · start the editor as a web page, TypeScript, reusable for an Artifact and Electron (Vue, a canvas library or three.js named as maybes) · the PO · 2026-10-16 · same; D-d · the lenses: PO assistant, tech lead, a senior on the data, a UX lens, the refuter on Opus · the PO approved the plan · 2026-10-16 · the approved plan in this session, saved as ~/.claude/plans/bubbly-gathering-shamir.md; D-e · spark exports facts, never behaviour; one core, many interfaces; free, few and local; public under MIT, no vendor files · AGENTS.md principles; D-f · the store's sharing questions belong to P178 (the store epic) · memory next-version-the-store, 2026-10-11 <!-- REQUIRED:decided -->
- Open questions: 1 the stage-neutral model; 2 how routes are made per stage; 3 the data records need; 4 one circuit in every stage; 5 the editor stack and its hosts; 6 pictures from the web; 7 saving, loading and sharing; 8 the slice order <!-- REQUIRED:open -->
- Scope · out of scope (proposed): in: the model, the record data, the editor and catalogue-editor architecture, pictures, saving and sharing, the slices · out: any code, any purchase or paid service, the PCB's own routing (spark builds PCBs with tscircuit already), firmware <!-- REQUIRED:scope -->
- Start and reach (proposed until Q0): start existing product (spark, with P267's drawn breadboard merged) · decider reachable yes · users the PO only (n = 1, the decider as a user); none other reachable · data and connectors: the repository, GitHub, Miro, the web (WebSearch, WebFetch), Chrome with Wokwi · decider as a user n = 1 · must not get worse: the sheet, the Wokwi diagram and the drawn breadboard of P267 <!-- REQUIRED:start-reach -->
- Flags (yes · no · —; asked only when it changes a decision; never legal advice; any date or threshold is read at its source at run time and cited):
  - sold or given away, or personal use: personal use, and spark is given away as open source (MIT) <!-- REQUIRED:flag-sold -->
  - connects to a network or runs software (for example the EU's Cyber Resilience Act): yes: the editor is software, and sharing may use a network · the CRA question is only for a sold product: — <!-- REQUIRED:flag-network -->
  - children or food contact: no <!-- REQUIRED:flag-children -->
  - market: the PO in Czechia, EU; spark public on GitHub <!-- REQUIRED:flag-market -->
  - radio (unlicensed-device rules; read at their source when it decides): no: this item draws and edits; it ships no radio <!-- REQUIRED:electronics-firmware:flag-radio -->
  - a Li-ion cell (charging, transport, battery rules): batteries enter the catalogue as records only; no charging design here <!-- REQUIRED:electronics-firmware:flag-li-ion -->
  - mains: no <!-- REQUIRED:electronics-firmware:flag-mains -->
  <!-- EXTEND:flags -->
- Extensions (each active id · the fact that activated it; when none matched, only "none matched: core only · the fact that decided it", naming no extension; list any directive skipped under rule 9): electronics-firmware · repo-has boards/*.json; spark-process · repo-has scrum/WORKING_AGREEMENTS.md <!-- REQUIRED:extensions -->
- The item (its issue, or the proposal in the decider's words) · what is still open elsewhere · the repository's push check, or "no push check here": P269 (#304), an epic in Discovery, under P199 (#152); P268 (#302) waits on it · still open elsewhere: P218 (#200) in Design; Ready holds P235 (#224) and P239 (#238) · the push hook (`tools/pre-push`) runs the suite <!-- REQUIRED:spark-process:item -->
<!-- EXTEND:frame -->
- Depth: TRIO (default: PO assistant, user, tech lead) | FULL or LIGHT (who asked, when); add "no independent review" if subagents could not start: the plan's five lenses (D-d), beyond TRIO by the PO's approval of the plan <!-- REQUIRED:depth -->
  <!-- Cost, measured once: the P900 rehearsal's council took 6 agents, 499 calls and about 90M input tokens (2026-10-06). -->
- Search budget: two web searches per open question, at most 16, stopping at the first good match <!-- REQUIRED:budget -->
- Appetite (the decider's, asked only when heading for design) | —: — <!-- REQUIRED:appetite -->

## What we found <!-- CLAIMS -->
<!-- One claim per line: `- [★C<n>] claim · E pointer | H source | D who date · caveat: qualifier | none`.
★ marks a claim that a decision, an option or the riskiest assumption rests on. A quote is verbatim, with its pointer.
Say what the evidence can support: an account (what happened to one person), data (how often, in its population and
period), a document (what was specified), the product (what exists, not whether anyone needs it), a benchmark (a
comparison). Model knowledge is H until a source is read. Elsewhere cite a ★ claim as ★C<n>, with its keep: words.
e.g. `- [★C2] 13 of 526 tickets ask for recurring tasks · E tickets.csv:2-14 · caveat: picked by Lena; shows that, not how often` -->
- [★C1] Every stage fits one model: a surface of holes whose built-in joins form groups (a breadboard row, a stripboard strip that a cut splits, a single perfboard hole, a PCB's free pads), parts whose legs sit in holes, and connections that join holes. The breadboard code already holds it under Wokwi names and in px · H council/tech-lead.md:10 (TL-1), on E council/tech-lead.md:16 (TL-2) (scripts/breadboard_drawing.py:22-37, 97-136) · caveat: no perfboard or stripboard code tests the model yet
- [★C2] No part record holds a pin position in mm. A part has `pin_order` and a footprint name only, and only the FireBeetle board record holds header geometry · E council/data.md:9 (DATA-1), council/data.md:10 (DATA-2) · caveat: the store was read on 2026-10-16, read-only
- [★C3] The schematic and the PCB views can come from tscircuit's `circuit-to-svg` on the kept `circuit.json`, which holds both in mm · E council/tech-lead.md:198 (TL-8), council/tech-lead.md:206 (TL-10) · caveat: the PCB is not the perfboard: its resistor is SMD while the sheet asks for a through-hole one (TL-11)
- [★C4] spark finds the circuit's points two ways: `breadboard.py points()` runs its own union-find, while the converter reads connectivity one way and calls a second way a defect · E council/tech-lead.md:192 (TL-7) (scripts/breadboard.py:90-119, tools/circuit-to-wokwi/ARCHITECTURE.md:50-53) · caveat: none
- [★C5] An edit survives a rebuild only through a merge rule. `merge.ts` keeps the person's positions in `diagram.json`, but today a rebuild rewrites `breadboard.json` and deletes an old one · E council/tech-lead.md:256 (TL-18), scripts/breadboard.py `write()` · caveat: merge.ts was not tried on `breadboard.json` (council/po-assistant.md PO-24)
- [★C6] Nobody is blocked without this now. The PO is the only user, and the persona is a hypothesis · E council/po-assistant.md:36 (PO-20), council/po-assistant.md:37 (PO-21); scrum/VISION.md:43 · caveat: the PO's own wish is evidence of value for him, n = 1
- [★C7] Licences limit reuse: Fritzing's part art is CC BY-SA 3.0 (share-alike), VeroRoute is GPLv3 (a tool to run, not code to copy), wokwi-elements is MIT · E council/po-assistant.md:27 (PO-14) to council/po-assistant.md:29 (PO-16), council/data.md · caveat: read from search summaries; the upstream Fritzing and wokwi-boards licence files were not opened
- [C8] An Artifact page loads scripts only from four CDNs, holds at most 16 MB and keeps state in its own data store. spark already bundles TypeScript into one file (`bundle.sh`) · E council/tech-lead.md:264 (TL-19), council/tech-lead.md:271 (TL-20) · caveat: none
- [C9] The XIAO's size differs: spark says 21.0 x 17.8 mm, Wokwi draws 18.1 x 23.4 mm · E council/data.md:11 (DATA-3) · caveat: Wokwi's size includes the USB overhang
- [C10] Sources disagree on a stripboard strip's current, from 250 mA to 1 to 3 A, and records hold 5 current fields in all · E council/tech-lead.md:335 (TL-32), council/tech-lead.md:341 (TL-33) · caveat: hobby sources
- [C11] Wokwi's diagram documentation names no schematic or PCB view · E council/user.md:26 (USER-14) · caveat: the editor itself was not opened, and the PO named both as an inspiration <!-- REQUIRED:findings -->

## Options <!-- CLAIMS -->
<!-- Two or three per open decision: decision · option · cost · what it would prove · opinion (whose), then the tag
and caveat cells. e.g. `- Q2 what first · fix delivery · two weeks · whether seen tasks get done · opinion (the facilitator's) · H ★C2 · caveat: none` -->
- Q2 what first · S0 the base in mm, then S1 P268's SVG, then S2 the connectivity check · three small stories · that the model holds and the picture helps · opinion (the tech lead, the PO assistant) · H ★C1 ★C6 · caveat: S0 shows no new output
- Q2 what first · S3 a read-only viewer first, on today's code · one story, bigger · whether he likes a viewer · opinion (the user lens) · H · caveat: built on the Wokwi-shaped base, rework follows
- Q2 what first · a perfboard first · a planner and a surface · J2's value · opinion (none of the lenses) · H ★C2 · caveat: needs pin data no record has
- Q3 routes · spark plans, the person edits · a planner per stage · H council/tech-lead.md:251 (TL-17) · caveat: Lee routing is new code
- Q3 routes · the person routes, spark only checks · the check of S2 only · H council/tech-lead.md:251 (TL-17), ★C4 · caveat: more work for him
- Q3 routes · spark exports a netlist to VeroRoute for stripboard · an exporter · H ★C7 (GPLv3, a tool) · caveat: a second tool to install
- Q4 edits · one layout file with edits marked inside · H council/tech-lead.md:300 (TL-26) · caveat: the build must not overwrite marked items
- Q4 edits · a separate edits file the build never writes · H council/tech-lead.md:300 (TL-26), as `board.tsx` is kept today (DATA) · caveat: two files to keep in step
- Q5 editor drawing · SVG DOM, with or without Vue · H council/tech-lead.md:275 (TL-21) · caveat: slower past a few thousand elements
- Q5 editor drawing · a canvas library (Konva, PixiJS) · H council/tech-lead.md:275 (TL-21) · caveat: export and hit testing by hand
- Q6 one core in the browser · a small TS checker that shares fixtures with Python · H council/tech-lead.md:282 (TL-22), council/tech-lead.md:288 (TL-23) · caveat: logic in two languages
- Q6 one core in the browser · Pyodide running the Python core in the page · H council/tech-lead.md:288 (TL-23) · caveat: a large download, an Artifact's 16 MB limit (C8) <!-- REQUIRED:options -->
- Proposed no-gos and rabbit holes (proposals until the decider confirms): no Fritzing art and no vendor picture in the public repository (★C7, AGENTS.md); no copying of VeroRoute's code (★C7); Electron only if the local page falls short (TL-35); no current or heat check on a perfboard until records hold the currents (C10); the PCB's own routing stays with tscircuit (the frame) · H the lenses, proposals · caveat: none confirmed by the PO <!-- REQUIRED:nogos -->

## Riskiest assumption and its test
- Riskiest: A1: a person's edit to a layout survives the next build, or is reported, never lost (★C5) · proposed — the PO assistant and the tech lead, pending Q1 <!-- REQUIRED:riskiest -->
- Test · kind · pass line, dated before any result · proposed | D<n>: a spike, two hours: move a part and a jumper in a button-light layout, change the requirements, rebuild with a merge rule like `merge.ts`, and read the result · pass line: in 3 of 3 cases (a moved part, a moved jumper, an edit the new circuit breaks) the edit survives or is reported by name, set 2026-10-16 · proposed — the lead, from the PO assistant and the tech lead <!-- REQUIRED:test -->

## Questions
<!-- A queue; the first open question is asked alone. Each: Q<n> · question · decides: … · options · unblocks ·
opinion (whose) · kind: decision | account (a past-tense question about the decider's own use; the answer is E,
account, n = 1) · status: queued | asked <date> | answered D<n>.
If the decider cannot be asked, the queue stays here, and whatever rests on it stays H. -->
- Q0 · Is this frame right: the decision, the start and reach, the extensions and the depth? · decides: the frame · status: answered D1 <!-- REQUIRED:q0 -->
- Q1 · How important is each assumption, and what pass line must the riskiest test meet? · decides: importance and pass lines · status: queued <!-- REQUIRED:q1 -->
- Q2 · Which slice comes first: the base, the SVG and the check (S0 to S2), a viewer, or a perfboard? · decides: the board order · options in Options · unblocks: P268 · opinion (the tech lead, the PO assistant: S0 to S2) · kind: decision · status: queued
- Q3 · Who makes the routes on a perfboard or stripboard: spark plans and you edit, you route and spark checks, or an export to VeroRoute? · decides: S5 and S6's size · kind: decision · status: queued
- Q4 · Where are your edits kept: marked inside one layout file, or in a separate file the build never writes? · decides: the save format and the rebuild rule · kind: decision · status: queued
- Q5 · How does the editor draw: SVG with or without Vue, or a canvas library? · decides: the stack and the Artifact's libraries · kind: decision · status: queued
- Q6 · How does the browser check a layout: a small TS checker beside Python, or the Python core in the page (Pyodide)? · decides: whether logic lives in two languages · kind: decision · status: queued
- Q7 · Pictures: keyed by the part's record, and may Fritzing's share-alike art be kept in your own store, never in spark? · decides: S1's and S7's picture source · kind: decision · status: queued
- Q8 · Is the catalogue editor part of P269, or of P160 inside the store epic P178? Is a battery its own kind of record? · decides: S7's home · kind: decision · status: queued
- Q9 · Do P199's walk-through page and this editor share one page? · decides: one web app or two · kind: decision · status: queued
- Q10 · Your own use, ten short account questions (council/user.md Q-a to Q-j), for example: when you opened `breadboard.json` in Wokwi, did you move anything? · decides: which friction comes first · kind: account · status: queued

## Decisions
<!-- D<n> · what · who · when · where recorded · options considered.
A yes covers only the actions and choices it names. A standing yes names its kind of action and its source.
Name what a D confirms in its words: the frame, the jobs, a direction, the remaining risk, a test, items.md. -->
- D1 · the frame is right: the decision, start and reach, scope, the five lenses and the budget of 16 searches · the PO · 2026-10-16 · AskUserQuestion Q0 in this session · options: the frame, change the scope, fewer lenses

## Found on the way <!-- CLAIMS -->
<!-- Outside this item's scope. Each is a separate proposal, never folded in. Same line format as What we found. -->
- [C12] The XIAO board record lacks the header facts that the FireBeetle record holds (rows, pitch, first pad) · E council/tech-lead.md:211 (TL-11), council/data.md:10 (DATA-2) · caveat: a separate fix, proposed as its own item | none <!-- REQUIRED:found -->

## Board actions <!-- REQUIRED:spark-process:board-actions -->
<!-- Each action on the board or the issue (stage, waiting flag, comment, filing): taken, with its D, or pending.
None is taken without a D. e.g. `- move #16 to Discovery · pending` -->
- P269 (#304) is in Discovery · taken before this discovery, by the PO's approval of the plan (D-a)
- set "Waiting on: the PO" and "Waiting since" while Q1 waits · pending
- a comment on #304 linking this brief · pending
<!-- EXTEND:brief-sections -->

## Hand-off
<!-- Written only after the decider confirms the understanding (a D); copies only confirmed constraints. Holds: outcome ·
who · success and its proof · constraints (appetite, confirmed no-gos, rabbit holes) · what they said (D) against what
we assume (H) · links to the journeys and the map · riskiest assumptions and their tests · options considered. -->
not yet: the jobs, a direction and the remaining risk are unconfirmed <!-- REQUIRED:handoff -->

## Files
[Jobs and journeys](jobs-and-journeys.md) · [Story map](story-map.md) · [Risks and tests](risks-and-tests.md) · [Verification](verification.md) · [Items](items.md) · council/
