<!-- Resume: invoke product-discovery again; `discovery.py check <this folder>` names the next step. -->
# ⟨topic⟩: discovery brief

<!-- Readiness, its one home. collecting evidence: anything short of the two below. an experiment: the decider chose
a test (a D) before choosing an option. design: the decider confirmed the frame, the jobs and a direction, and accepted
the remaining risk (D rows). An extension may tighten these. Next: design, or a chosen test of kind spike or prototype
→ the design skill the facts name, with this file; otherwise none, and the collection plan says who runs it.
Stands on: the assumptions not retired in risks-and-tests.md; of which those the decider rated high, or — while any
is unrated. check computes both. -->
**Ready for:** collecting evidence: the frame is confirmed (D1), and the council runs <!-- REQUIRED:ready -->
**Stands on:** ⟨fill⟩ H, ⟨fill⟩ of which would change the decision <!-- REQUIRED:debt -->
**Decision needed:** none yet: the council runs, then Q1 <!-- REQUIRED:decision-needed -->

## Frame
- Request, verbatim (corrections marked): three texts of the PO. (1) 2026-11-17, at the bench, during P711's walk 3, on the card #1234: "Please also take notes on the page ad [and] what is already abailable [available] and what not and lets find gaps and bugs. Apperently [Apparently], the breadboard is not available yet, which makes sense, as so far only the goal, the needs, the parts and modules and boards and the schema and where to get parts from and where else they are available, which ones to validate, which oneds [ones] to replace. Only later will breadboard and PCB and simulation be available, right? Maybe we should define this too ? Some journey or screens ? So that it ends up looking like the nice breadboard we did in one of the demos, with the nice pictures and animation of connections, we can redo the walks or do another set later". (2) 2026-11-17, after the walks stopped, in the comment on #1234: "Like I said, since we now have Fable 5.2, let's really recheck the plan and really analyze the whole user journey and the screens, or steps in general: whether it's using the interface of a CLI, an agent using a CLI, or a human using a CLI; whether it's using the artifact and code and communicating with it through the artifact, or any other way. Later, it would be the frameworks, like AI frameworks. Let's make sure we have it nicely defined: what the steps are for each of the states; when we can go back; how; what happens when we, I don't know, let's say, go on, create the goal, the needs, the parts, the schema, even the software maybe, and then I would say, \"Well, let's add another joystick.\" What would happen, actually, and so on. Let's redefine this whole and go from high level to lower, lower, lower-level details." (line breaks joined with semicolons). (3) 2026-11-17, this session: "Pull P867 #1234 into Discovery (the whole journey redefined, my words are on the card) and run the product-discovery skill with the full council. Plans, architecture and synthesis on Fable 5.2, routine lenses on the everyday model. Inputs: P869 #1236's 32 rows in ~/Development/spark-walks/p711-*/rows.md, p711-sound-demo/page-notes.md, flow.py's nine phases, P820's MVP plan. Go from high level to detail, and ask me one question at a time." <!-- REQUIRED:request -->
- Decision · decider: how spark defines its journey, from high level to detail: which phases a project has and in which order, the states of each phase, what each phase holds and shows, when and how a person goes back, what a change in the middle does to everything made after it ("let's add another joystick"), and how one definition serves a person on the CLI, an agent on the CLI, the Artifact page and later an AI framework; then which slices come first and what that changes for the cards in Ready (P827 #1185, P828 #1186, P829 #1187) · the PO <!-- REQUIRED:decision -->
- Outcome and how it is observed (a metric with unit and source, a proof command, or a log): the PO confirms a journey definition (the phases, their states, the ways back and the rule for a change in the middle) and a slice order (a D). The first observable proof, proposed: on one real project that has needs, picks, a build and firmware, a person adds a part ("another joystick"); `flow.py show` then names every phase that is out of date and the next step, and no file is deleted or edited by hand; observed in the output of `flow.py show --json` before and after, and in the rows of a walk run again (P711 #960) <!-- REQUIRED:outcome -->
- Already decided (D · who · when · where; include the product's stated non-goals and earlier decisions the request names): D-a · the definition covers every interface: a person on the CLI, an agent on the CLI, the Artifact page, later AI frameworks, and it covers going back and a change in the middle · the PO · 2026-11-17 · #1234's comment; D-b · the breadboard screen looks like the demo he praised, with pictures and animated connections · the PO · 2026-11-17 · #1234 (and P820's D-b); D-c · the walks start over only after the gaps and bugs of the three walks are fixed · the PO · 2026-11-17 · #1236; D-d · the project's files are the truth, the page is one renderer of them, and a click sends only a key from an allowlist of four kinds (pick, needs-drop, requirements, build); firmware, simulate and deploy have no offer in the MVP · the PO · 2026-11-15 · P820's brief, D5 and D7 to D11 (docs/discovery/2026-11-15-p820-artifact-interface/mvp-plan.md); D-e · one core, many interfaces; spark exports facts, never behaviour, and the conversation writes the firmware; free, few and local; KiCad stays optional · AGENTS.md principles; D-f · not goals: production layout, chip-down design, volume; ordering a board of modules is in the journey, after the firmware works · the PO · 2026-10-03 · scrum/VISION.md:72-76; D-g · no paid simulation run · the PO · 2026-10-31 · rules.md; D-h · his phase order (first the goal, the needs, the parts, modules and boards, the schematic, the shops, what to validate and what to replace; later the breadboard, the PCB and the simulation) is his first guess, asked as a question ("right?"), so it is H until he confirms it <!-- REQUIRED:decided -->
- Open questions: 1 which phases the journey has and in which order: today's nine (idea, needs, parts, requirements, build, breadboard, firmware, simulate, deploy) against his list, which adds the schematic, the shops and alternatives, what to validate, what to replace, the PCB, and puts the breadboard later; 2 whether the journey is a line or a graph: which phases need which, and which can run side by side; 3 the states of each phase, and which file or record is the truth for each; 4 what "going back" means: a person changes an earlier record and everything made from it becomes out of date, or spark undoes later work; what is kept and what is made again; 5 a change in the middle: what happens to the picks and holds, the requirements, the pins of the parts that stay, the board file spark wrote, the breadboard already wired, the firmware that names old pins, and the board on the bench with the old firmware; 6 where the one definition lives so that the CLI, the agents' prompts, the page and a later AI framework read the same phases, states and transitions; 7 what each screen shows per phase, and what a phase with no screen says; 8 what the definition changes for P827, P828, P829 and for P869's triage; 9 how spark learns that a built gadget drifted from its record (walk 3, row 16) <!-- REQUIRED:open -->
- Scope · out of scope (proposed): in: the journey's phases, states and transitions; the rule for going back and for a change in the middle; what each phase reads, writes and shows on each interface; where the definition lives; the slice order · out: any code or spec in this discovery; the page's visual design (design does it); how a part picture is drawn (P734 #1005); fixing the 32 rows (P869 #1236 triages them, and here they are evidence); choosing an AI framework (P417; here only what the definition must offer one); PCB editing; shop prices as a feature; any paid service <!-- REQUIRED:scope -->
- Start and reach (D1): start existing product (spark: `flow.py show` with nine phases, P825; `page.html` with three tabs; the commands /spark:idea, /spark:build, /spark:deploy) · decider reachable yes · users the PO only (n = 1), through the rows of his three walks of 2026-11-16 and 2026-11-17; no other user reachable · data and connectors: the repository, GitHub (issues, the board), the walk folders (spark-walks/p711-*/rows.md, p711-sound-demo/page-notes.md), the store, the claude-artifacts server, Miro, the web (WebSearch, WebFetch) · decider as a user n = 1 · must not get worse: the keys of `flow.py show --json` (data.phases, data.stands_at) and its exit codes, the kept files (breadboard.md, page.html, firmware/pins.py), a could-not-run or a skipped is never shown as a pass, nothing is published without a yes, the deploy asks for the person's yes after a look, and no step runs a paid simulation <!-- REQUIRED:start-reach -->
- Flags (yes · no · —; asked only when it changes a decision; never legal advice; any date or threshold is read at its source at run time and cited):
  - sold or given away, or personal use: given away as open source (MIT); personal use by the PO <!-- REQUIRED:flag-sold -->
  - connects to a network or runs software (for example the EU's Cyber Resilience Act): yes: spark runs on the person's computer and the page on claude.ai · the CRA question is only for a sold product: — <!-- REQUIRED:flag-network -->
  - children or food contact: no <!-- REQUIRED:flag-children -->
  - market: the PO in Czechia, EU; spark public on GitHub <!-- REQUIRED:flag-market -->
  - radio (unlicensed-device rules; read at their source when it decides): no: this item defines spark's journey; it ships no radio <!-- REQUIRED:electronics-firmware:flag-radio -->
  - a Li-ion cell (charging, transport, battery rules): no <!-- REQUIRED:electronics-firmware:flag-li-ion -->
  - mains: no <!-- REQUIRED:electronics-firmware:flag-mains -->
  <!-- EXTEND:flags -->
- Extensions (each active id · the fact that activated it; when none matched, only "none matched: core only · the fact that decided it", naming no extension; list any directive skipped under rule 9): electronics-firmware · repo-has boards/*.json; spark-process · repo-has scrum/WORKING_AGREEMENTS.md <!-- REQUIRED:extensions -->
- The item (its issue, or the proposal in the decider's words) · what is still open elsewhere · the repository's push check, or "no push check here": P867 #1234, a story under the epic P820 #1173, slice Views and editors, moved from Idea to Discovery on 2026-11-17 on the PO's order (D0) · still open elsewhere: P820's own discovery (Ready for collecting evidence, its A11 waits for P829 #1187); P869 #1236 in Idea (the triage of the same 32 rows); Ready holds P711 #960, P827 #1185, P828 #1186, P829 #1187 and P851 #1215; Build holds P866 #1233; the day of 2026-11-16 has no close · the push hook (`tools/pre-push`) runs the story run <!-- REQUIRED:spark-process:item -->
<!-- EXTEND:frame -->
- Depth: FULL, asked by the PO ("the full council", 2026-11-17, D0): seven lenses in parallel, then the refuter. The four core lenses (existing first, feasibility, the user's journey, risks and assumptions), electronics-firmware:physics, an architecture lens with its diagrams (scrum/README.md:109; the PO's rule of 2026-10-14) and a UX and AI-UX lens (the PO's rule of 2026-10-18). Models (D0): Fable 5.2 for the architecture lens, the refuter and the synthesis; the everyday model (Sonnet) for the other six lenses <!-- REQUIRED:depth -->
  <!-- Cost, measured once: the P900 rehearsal's council took 6 agents, 499 calls and about 90M input tokens (2026-10-06). -->
- Search budget: two web searches per open question, at most 14 in all, each naming the decision it serves, stopping at the first good match <!-- REQUIRED:budget -->
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
- Q0 · Is this frame right: the decision, the start and reach, the extensions and the depth? · decides: the frame · status: answered D1 <!-- REQUIRED:q0 -->
- Q1 · How important is each assumption, and what pass line must the riskiest test meet? · decides: importance and pass lines · status: queued <!-- REQUIRED:q1 -->

## Decisions
<!-- D<n> · what · who · when · where recorded · options considered.
A yes covers only the actions and choices it names. A standing yes names its kind of action and its source.
Name what a D confirms in its words: the frame, the jobs, a direction, the remaining risk, a test, items.md. -->
- D0 · the discovery starts: P867 #1234 moves to Discovery, the product-discovery skill runs with the full council, the plans, the architecture and the synthesis run on Fable 5.2 and the routine lenses on the everyday model, and the questions come one at a time · the PO · 2026-11-17 · this session's request (the Frame's request, text 3) · options considered: none, an order
- D1 · the frame is right as written: the decision, the start and reach, both extensions and the FULL depth of seven lenses and the refuter; his phase order stays a guess that the council tests · the PO · 2026-11-17 · AskUserQuestion in this session (Q0: "Yes, start") · options considered: without the physics lens; his phase order as a decision; change the frame

## Found on the way <!-- CLAIMS -->
<!-- Outside this item's scope. Each is a separate proposal, never folded in. Same line format as What we found. -->
- ⟨fill⟩ | none <!-- REQUIRED:found -->

## Board actions <!-- REQUIRED:spark-process:board-actions -->
<!-- Each action on the board or the issue (stage, waiting flag, comment, filing): taken, with its D, or pending.
None is taken without a D. e.g. `- move #16 to Discovery · pending` -->
- move #1234 from Idea to Discovery · taken 2026-11-17, read back as Discovery · D0
- set #1234's Waiting on to the PO, with Waiting since, while a question waits · taken per question · the standing rule in the PO's rules ("It moves as the work moves, with Waiting on and Waiting since set")
- a comment on #1234 that links this brief · pending, at the folder's PR
<!-- EXTEND:brief-sections -->

## Hand-off
<!-- Written only after the decider confirms the understanding (a D); copies only confirmed constraints. Holds: outcome ·
who · success and its proof · constraints (appetite, confirmed no-gos, rabbit holes) · what they said (D) against what
we assume (H) · links to the journeys and the map · riskiest assumptions and their tests · options considered. -->
⟨the hand-off | not yet: what is unconfirmed⟩ <!-- REQUIRED:handoff -->

## Files
[Jobs and journeys](jobs-and-journeys.md) · [Story map](story-map.md) · [Risks and tests](risks-and-tests.md) · [Verification](verification.md) · [Items](items.md) · council/
