<!-- Resume: invoke product-discovery again; `discovery.py check <this folder>` names the next step. -->
# P269 views and editors: discovery brief

<!-- Readiness, its one home. collecting evidence: anything short of the two below. an experiment: the decider chose
a test (a D) before choosing an option. design: the decider confirmed the frame, the jobs and a direction, and accepted
the remaining risk (D rows). An extension may tighten these. Next: design, or a chosen test of kind spike or prototype
→ the design skill the facts name, with this file; otherwise none, and the collection plan says who runs it.
Stands on: the assumptions not retired in risks-and-tests.md; of which those the decider rated high, or — while any
is unrated. check computes both. -->
**Ready for:** design <!-- REQUIRED:ready -->
**Stands on:** 11 H, 2 of which would change the decision (A1 high by D11, A3 high by D4) <!-- REQUIRED:debt -->
**Decision needed:** none now: the PO chose the direction (D8); each step's plan decides its own technical questions <!-- REQUIRED:decision-needed -->

## Frame
- Request, verbatim (corrections marked): the PO, 2026-10-16, on P269 (#304): "probably we will want to reuse code for the perfboard stagte, so please also create some common base, think about what the differences are, how making routes works there, etc, what other data we would nreed to store for parts/modules/boars to also enable the perfboard visualisation and editing. In the end we will want to have a really nice editor, wokwi is actually quite a good inspiration how it dowa its breadboare and also pcb and schema, so just keep that in mind, so me good thought through way of siplaying the schema in different stategs will be good to have and we will want to in the end have it really nicely made ux and graphics wise." His answers the same day: plain perfboard and stripboard, both; "Discovery first"; "It would be grteat to have the system made so that its easy to add more, we'de in the end ideally want to enable all these views, we can start by a webpage, vue probably, or some canvas and 3js typescript libraries maybe, ideally if reusable for the artifact and later even some electron version of the page for example. We will also want to enable the catalogue editing app for the parts and modules and boards and batteries, etc."; "it would be great if it could import images from web, sooner or later, of the parts etc. And think of saving and loading, sharing.." <!-- REQUIRED:request -->
- Decision · decider: which base model, which editor stack and which first slices spark builds for showing and editing one circuit in every stage · the PO <!-- REQUIRED:decision -->
- Outcome and how it is observed (a metric with unit and source, a proof command, or a log): the PO decides the base, the stack and the slice order from the brief (a D); then, per slice, a build stage writes a view the person opens. The first observable proof: P268's SVG of button-light drawn on the chosen base (`breadboard.svg` beside `breadboard.md`), checked by its tests <!-- REQUIRED:outcome -->
- Already decided (D · who · when · where; include the product's stated non-goals and earlier decisions the request names): D-a · discovery first, P268 waits · the PO · 2026-10-16 · the plan question in this session, recorded on #302; D-b · perfboard means plain perfboard and stripboard · the PO · 2026-10-16 · same; D-c · start the editor as a web page, TypeScript, reusable for an Artifact and Electron (Vue, a canvas library or three.js named as maybes) · the PO · 2026-10-16 · same; D-d · the lenses: PO assistant, tech lead, a senior on the data, a UX lens, the refuter on Opus · the PO approved the plan · 2026-10-16 · the approved plan in this session, saved as ~/.claude/plans/bubbly-gathering-shamir.md; D-e · one bar: a change moves a basic project closer to a breadboard with working firmware; spark exports facts, never behaviour; one core, many interfaces; free, few and local; public under MIT, no vendor files · AGENTS.md principles; D-f · the store's sharing questions belong to P178 (the store epic) · memory next-version-the-store, 2026-10-11 <!-- REQUIRED:decided -->
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
- [★C1] Every stage fits one model: a surface of holes whose built-in joins form groups (a breadboard row, a stripboard strip that a cut splits, a single perfboard hole, a PCB's free pads), parts whose legs sit in holes, and connections that join holes. The breadboard code already holds it under Wokwi names and in px · H council/tech-lead.md:10 (TL-1), on E council/tech-lead.md:16 (TL-2) (scripts/breadboard_drawing.py:22-37, 97-136) · caveat: untested beyond the breadboard: no perfboard or stripboard code tests the model, the code has no strip cuts and no connectivity check, and a PCB has SMD pads, not holes <!-- REQUIRED:findings -->
- [★C2] No record holds a per-pin x and y in mm. A few hold a pitch or pad spacing (jst-ph-2's `pitch_mm` 2.0, the store's dfr0831 and ds3231, two catalog terminals), the FireBeetle holds header geometry, and the XIAO's 14 pins exist only in data/wokwi-geometry.json, converted from Wokwi's board.json · E council/data.md:9 (DATA-1), parts/jst-ph-2-power-inlet.json, data/wokwi-geometry.json:7-17 · caveat: the store was read on 2026-10-16, read-only
- [★C3] The schematic and the PCB views can come from tscircuit's `circuit-to-svg` on the kept `circuit.json`, which holds both in mm · E council/tech-lead.md:198 (TL-8), council/tech-lead.md:206 (TL-10) · caveat: the PCB is not the perfboard: its resistor is SMD while the sheet asks for a through-hole one (TL-11)
- [★C4] spark reads the circuit's connections three ways: netlist.py, `breadboard.py points()` and the converter. netlist.py and `points()` differ on purpose. The converter's rule of one way covers only the converter · E scripts/netlist.py:25-27, scripts/breadboard.py:92-93, tools/circuit-to-wokwi/ARCHITECTURE.md:50-53 · caveat: whether the three can disagree on a real circuit is not tested
- [★C5] Today nothing in spark keeps a person's edit across a build. `merge.ts` exists, but the build writes `diagram.json` into a fresh temporary folder and then copies it over the kept file, so it never merges. `merge.ts` counts the edits it drops without naming them. A rebuild rewrites `breadboard.json` and deletes an old one · E scripts/check_spine.py:498, scripts/check_spine.py:658, scripts/check_spine.py:841, scripts/breadboard.py:427-430 · caveat: on a breadboard a part's position is its connection, so a kept move can contradict the new circuit
- [★C6] Nobody is blocked without this now. The PO is the only user, and the persona is a hypothesis · E council/po-assistant.md:36 (PO-20), council/po-assistant.md:37 (PO-21); scrum/VISION.md:38 · caveat: the PO's own wish is evidence of value for him, n = 1, and this discovery also holds P268, which he asked for
- [★C7] Licences limit reuse: Fritzing's part art is CC BY-SA 3.0 Unported (share-alike), VeroRoute is GPLv3 (a tool to run, not code to copy), wokwi-elements is MIT, and wokwi/wokwi-boards, where the XIAO's board art lives, states no licence · E council/refuter.md (licence files opened 2026-10-16, `gh api repos/wokwi/wokwi-boards` licence null) · caveat: VeroRoute has no macOS build and imports only TinyCAD, gEDA or KiCad netlists
- [C8] An Artifact page loads scripts only from four CDNs, holds at most 16 MB and keeps state in its own data store. spark already bundles TypeScript into one file (`bundle.sh`) · E council/tech-lead.md:264 (TL-19), council/tech-lead.md:271 (TL-20) · caveat: none
- [C9] The XIAO's size differs: spark says 21.0 x 17.8 mm, Wokwi draws 18.1 x 23.4 mm · E council/data.md:11 (DATA-3) · caveat: Wokwi's size includes the USB overhang
- [C10] Sources disagree on a stripboard strip's current, from 250 mA to 1 to 3 A. Records hold few current fields, among them the L9110S's `continuous_current_a` 0.8 · E council/tech-lead.md:335 (TL-32), parts/l9110s-module.json:57 · caveat: hobby sources; the tech lead's count of current fields was wrong
- [C11] Wokwi's diagram documentation names no schematic or PCB view · E council/user.md:26 (USER-14) · caveat: the editor itself was not opened, and the PO named both as an inspiration

## Options <!-- CLAIMS -->
<!-- Two or three per open decision: decision · option · cost · what it would prove · opinion (whose), then the tag
and caveat cells. e.g. `- Q2 what first · fix delivery · two weeks · whether seen tasks get done · opinion (the facilitator's) · H ★C2 (per-pin x and y) · caveat: none` -->
- Q2 what first · S0 the base in mm, then S1 P268's SVG, then S2 the connectivity check · three small stories · that the model holds and the picture helps · opinion (the tech lead) · H ★C1 (untested beyond the breadboard) ★C6 (n = 1) · caveat: S0 shows no new output; the PO assistant favours the breadboard SVG first, by AGENTS.md's one bar
- Q2 what first · S3 a read-only viewer first, on today's code · one story, bigger · whether he likes a viewer · opinion (the user lens) · H · caveat: built on the Wokwi-shaped base, rework follows
- Q2 what first · a perfboard first · a planner and a surface · J2's value · opinion (none of the lenses) · H ★C2 (per-pin x and y) · caveat: needs pin data no record has
- Q3 routes · spark plans, the person edits · a planner per stage · H council/tech-lead.md:251 (TL-17) · caveat: Lee routing is new code
- Q3 routes · the person routes, spark only checks · the check of S2 only · H council/tech-lead.md:251 (TL-17), ★C4 (three ways) · caveat: more work for him
- Q3 routes · spark exports a netlist to VeroRoute for stripboard · an exporter · H ★C7 (share-alike) (GPLv3, a tool) · caveat: a second tool to install, no macOS build, and it reads only TinyCAD, gEDA or KiCad netlists
- Q4 edits · one layout file with edits marked inside · H council/tech-lead.md:300 (TL-26) · caveat: the build must not overwrite marked items
- Q4 edits · a separate edits file the build never writes · H council/tech-lead.md:300 (TL-26), as `board.tsx` is kept today (DATA) · caveat: two files to keep in step
- Q5 editor drawing · SVG DOM, with or without Vue · H council/tech-lead.md:275 (TL-21) · caveat: slower past a few thousand elements
- Q5 editor drawing · a canvas library (Konva, PixiJS) · H council/tech-lead.md:275 (TL-21) · caveat: export and hit testing by hand
- Q6 one core in the browser · a small TS checker that shares fixtures with Python · H council/tech-lead.md:282 (TL-22), council/tech-lead.md:288 (TL-23) · caveat: logic in two languages
- Q6 one core in the browser · Pyodide running the Python core in the page · H council/tech-lead.md:288 (TL-23) · caveat: a large download, an Artifact's 16 MB limit (C8) <!-- REQUIRED:options -->
- Proposed no-gos and rabbit holes (proposals until the decider confirms): no Fritzing art and no vendor picture in the public repository (★C7 (share-alike), AGENTS.md); no copying of VeroRoute's code (★C7); Electron only if the local page falls short (TL-35); no current or heat check on a stripboard until each loaded part records its current (C10); the PCB's own routing stays with tscircuit (the frame) · H the lenses, proposals · caveat: none confirmed by the PO <!-- REQUIRED:nogos -->

## Riskiest assumption and its test
- Riskiest: A1, a moved part keeps its position after a rebuild, or spark names why not; today nothing keeps it (★C5 (a person's edit)) · D11 <!-- REQUIRED:riskiest -->
- Test · kind · pass line, dated before any result · proposed | D<n>: a spike in step 5's plan: move a part and a jumper in a button-light layout, change the requirements, rebuild with a merge rule the spike writes; pass line: in 3 of 3 cases (a moved part, a moved jumper, an edit the new circuit breaks) the edit survives or is named, set 2026-10-16. A3 is tested by step 2 itself: he says the picture helped him wire · proposed — the lead, from the PO assistant, the tech lead and the refuter <!-- REQUIRED:test -->

## Questions
<!-- A queue; the first open question is asked alone. Each: Q<n> · question · decides: … · options · unblocks ·
opinion (whose) · kind: decision | account (a past-tense question about the decider's own use; the answer is E,
account, n = 1) · status: queued | asked <date> | answered D<n>.
If the decider cannot be asked, the queue stays here, and whatever rests on it stays H. -->
- Q0 · Is this frame right: the decision, the start and reach, the extensions and the depth? · decides: the frame · status: answered D1 <!-- REQUIRED:q0 -->
- Q1 · How important is each assumption, and what pass line must the riskiest test meet? · decides: importance and pass lines · status: answered D2 to D7, walked through as six short questions <!-- REQUIRED:q1 -->
- Q2 · Which slice comes first: the base, the SVG and the check (S0 to S2), a viewer, or a perfboard? · decides: the board order · options in Options · unblocks: P268 · opinion (the tech lead, the PO assistant: S0 to S2) · kind: decision · status: answered D8
- Q3 · Who makes the routes on a perfboard or stripboard: spark plans and you edit, you route and spark checks, or an export to VeroRoute? · decides: S5 and S6's size · kind: decision · status: queued for step 6's plan
- Q4 · Where are your edits kept: marked inside one layout file, or in a separate file the build never writes? · decides: the save format and the rebuild rule · kind: decision · status: queued for step 5's plan
- Q5 · How does the editor draw: SVG with or without Vue, or a canvas library? · decides: the stack and the Artifact's libraries · kind: decision · status: queued for step 3's plan
- Q6 · How does the browser check a layout: a small TS checker beside Python, or the Python core in the page (Pyodide)? · decides: whether logic lives in two languages · kind: decision · status: queued for step 3's plan
- Q7 · Pictures: keyed by the part's record, and may Fritzing's share-alike art be kept in your own store, never in spark? · decides: S1's and S7's picture source · kind: decision · status: queued for step 2's plan
- Q8 · Is the catalogue editor part of P269, or of P160 inside the store epic P178? Is a battery its own kind of record? · decides: S7's home · kind: decision · status: queued for step 7's plan
- Q9 · Do P199's walk-through page and this editor share one page? · decides: one web app or two · kind: decision · status: queued for step 3's plan
- Q10 · Your own use, ten short account questions (council/user.md Q-a to Q-j), for example: have you opened `breadboard.json` in Wokwi, and if so, did you move anything? · decides: which friction comes first · kind: account · status: answered in part by D2 to D5; the rest dropped

## Decisions
<!-- D<n> · what · who · when · where recorded · options considered.
A yes covers only the actions and choices it names. A standing yes names its kind of action and its source.
Name what a D confirms in its words: the frame, the jobs, a direction, the remaining risk, a test, items.md. -->
- D1 · the frame is right: the decision, start and reach, scope, the five lenses and the budget of 16 searches · the PO · 2026-10-16 · AskUserQuestion Q0 in this session · options: the frame, change the scope, fewer lenses
- D2 · a lost edit after a rebuild is "Annoying, but OK": A1 is low · the PO · 2026-10-16 · AskUserQuestion, a walk through Q1 · options: deal-breaker, annoying but OK, I do not care
- D3 · he will solder a perfboard or stripboard "Yes, but later": A4 is low for now · the PO · 2026-10-16 · same · options: yes soon, yes but later, not sure
- D4 · when wiring he would look at "The picture" most: A3 is high, and its pass line is met as an account · the PO · 2026-10-16 · same · options: the picture, both, the steps
- D5 · where to open it: "All, in that order": the sheet, then a page on his Mac, then an Artifact; A7 is low for now · the PO · 2026-10-16 · same · options: in the sheet, a page on my Mac, an Artifact link, all in that order
- D6 · sharing: "Later is fine", with the store epic P178; A11 is low · the PO · 2026-10-16 · same · options: later is fine, early
- D7 · the base: "OK, rework later": build it as far as the breadboard and the picture need, check it against the perfboard on paper only; A2 is low · the PO · 2026-10-16 · same · options: rework later, prove it now
- D8 · the direction, the remaining risk and items.md: "Yes, this order": 1 a small base, breadboard only; 2 the picture in breadboard.md (P268); 3 a page on his Mac with schematic and PCB tabs; 4 the same page as an Artifact; later 5 editing that keeps moves, 6 stripboard and perfboard, 7 the catalogue editor with web pictures, 8 sharing. The five unrated technical guesses (A5, A6, A8, A9, A10) are checked in each step's own plan. Filing the items in items.md is yes · the PO · 2026-10-16 · AskUserQuestion in this session · options: yes this order, yes but change it
- D9 · the jobs, confirmed with changes: "number 7 is the most importatnt, in steps is ok, mvp first, 2 is nice, 3 yes, and it should stay where we move it, export should be possible, ultimately whatever is needed for fusion , if possoble to have it 3d made there, including pcb and parts ? Number one is not necessary, just that parts should have pictures, photos". So J7 is the most important, J1 is dropped, J5 says photos, J3 needs edits that stay, and J8 export for Fusion 360 is new, after step 7. D11 settles what "stay" means · the PO · 2026-10-16 · AskUserQuestion in this session · options: yes these are my jobs, change one
- D10 · the catalogue editor marks pins on the picture: "so to be able to add and edit where on the picture which holes and connectors etc are would be good" · the PO · 2026-10-16 · his message in this session · options: none offered, his own addition to J4 and step 7
- D11 · "it should stay where we move it" means "Stays after a rebuild": a moved part keeps its position after spark rebuilds, or spark names why it could not. A1 is high for step 5, and this supersedes D2 · the PO · 2026-10-16 · AskUserQuestion in this session · options: stays after a rebuild, stays when saved
- D12 · the remaining risk: "Yes, check them later": A5, A6, A8, A9 and A10 are each checked in their own step's plan, with no test now · the PO · 2026-10-16 · same · options: yes check them later, test some now
- D13 · a new Slice option "Views and editors" for steps 1 to 5 · the PO · 2026-10-16 · AskUserQuestion in this session · options: a new slice, v0.10 The basic journey, parked after v0.10. The lead did not add it, because the API replaces the whole option list; the PO adds it by hand
- D14 · the rows AT273 to AT276 in docs/observations/INDEX.md, outside this folder · the PO's standing rule · rules.md (CLAUDE.local.md): "The gaps and findings of every agent run become rows in spark's docs/observations/INDEX.md" · a standing yes for that kind of action

## Found on the way <!-- CLAIMS -->
<!-- Outside this item's scope. Each is a separate proposal, never folded in. Same line format as What we found. -->
- [C12] The XIAO board record lacks the header facts that the FireBeetle record holds (rows, pitch, first pad) · E council/tech-lead.md:211 (TL-11), council/data.md:10 (DATA-2) · caveat: a separate fix, proposed as its own item | none <!-- REQUIRED:found -->

## Board actions <!-- REQUIRED:spark-process:board-actions -->
<!-- Each action on the board or the issue (stage, waiting flag, comment, filing): taken, with its D, or pending.
None is taken without a D. e.g. `- move #16 to Discovery · pending` -->
- P269 (#304) is in Discovery · taken before this discovery, by the PO's approval of the plan (D-a)
- set "Waiting on: the PO" while Q1 waited · not needed, he answered in the session
- a comment on #304 linking this brief · D8, done with the PR
- filed the items in items.md under #304, #306 to #314 · D8, done
<!-- EXTEND:brief-sections -->

## Hand-off
<!-- Written only after the decider confirms the understanding (a D); copies only confirmed constraints. Holds: outcome ·
who · success and its proof · constraints (appetite, confirmed no-gos, rabbit holes) · what they said (D) against what
we assume (H) · links to the journeys and the map · riskiest assumptions and their tests · options considered. -->
Outcome: the maker sees one circuit in every stage, step by step, MVP first (J7, the most important by D9): the picture in the sheet, then a page with the breadboard, schematic and PCB, then an editor whose moves stay (J3, D9), then the boards he solders (J2), then the catalogue with photos (J4, J5), then an export for Fusion 360 (J8, D9). Who: the PO, n = 1. Success and its proof: step 2 (P268) puts `breadboard.svg` in `breadboard.md` for button-light, and he says the picture helped him wire (A3, open, D4); step 5 keeps his moves across a rebuild (A1, D11). Constraints: the order in D8; the base only as far as the breadboard and the picture need (D7); no share-alike or vendor art in the repository (★C7 (share-alike)); the one bar of AGENTS.md. What he said (D2 to D12) against what we assume: A5, A6, A8, A9 and A10 stay H, each checked in its step's plan (D12). Links: [jobs](jobs-and-journeys.md), [map](story-map.md), [risks](risks-and-tests.md), [items](items.md). Options considered: in Options; the first-slice split (base first against picture first) is settled by D7 and D8: a small base, then the picture. <!-- REQUIRED:handoff -->

## Files
[Jobs and journeys](jobs-and-journeys.md) · [Story map](story-map.md) · [Risks and tests](risks-and-tests.md) · [Verification](verification.md) · [Items](items.md) · council/
