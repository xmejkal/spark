<!-- Resume: invoke product-discovery again; `discovery.py check <this folder>` names the next step. -->
# P269 views and editors: discovery brief

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
- Request, verbatim (corrections marked): the PO, 2026-10-16, on P269 (#304): "probably we will want to reuse code for the perfboard stagte, so please also create some common base, think about what the differences are, how making routes works there, etc, what other data we would nreed to store for parts/modules/boars to also enable the perfboard visualisation and editing. In the end we will want to have a really nice editor, wokwi is actually quite a good inspiration how it dowa its breadboare and also pcb and schema, so just keep that in mind, so me good thought through way of siplaying the schema in different stategs will be good to have and we will want to in the end have it really nicely made ux and graphics wise." His answers the same day: plain perfboard and stripboard, both; "Discovery first"; "It would be grteat to have the system made so that its easy to add more, we'de in the end ideally want to enable all these views, we can start by a webpage, vue probably, or some canvas and 3js typescript libraries maybe, ideally if reusable for the artifact and later even some electron version of the page for example. We will also want to enable the catalogue editing app for the parts and modules and boards and batteries, etc."; "it would be great if it could import images from web, sooner or later, of the parts etc. And think of saving and loading, sharing.." <!-- REQUIRED:request -->
- Decision · decider: which base model, which editor stack and which first slices spark builds for showing and editing one circuit in every stage · the PO <!-- REQUIRED:decision -->
- Outcome and how it is observed (a metric with unit and source, a proof command, or a log): the PO decides the base, the stack and the slice order from the brief (a D); then, per slice, a build stage writes a view the person opens. The first observable proof: P268's SVG of button-light drawn on the chosen base (`breadboard.svg` beside `breadboard.md`), checked by its tests <!-- REQUIRED:outcome -->
- Already decided (D · who · when · where; include the product's stated non-goals and earlier decisions the request names): D-a · discovery first, P268 waits · the PO · 2026-10-16 · the plan question in this session, recorded on #302; D-b · perfboard means plain perfboard and stripboard · the PO · 2026-10-16 · same; D-c · start the editor as a web page, TypeScript, reusable for an Artifact and Electron (Vue, a canvas library or three.js named as maybes) · the PO · 2026-10-16 · same; D-d · the lenses: PO assistant, tech lead, a senior on the data, a UX lens, the refuter on Opus · the PO approved the plan · 2026-10-16 · /Users/petr/.claude/plans/bubbly-gathering-shamir.md; D-e · spark exports facts, never behaviour; one core, many interfaces; free, few and local; public under MIT, no vendor files · AGENTS.md principles; D-f · the store's sharing questions belong to P178 (the store epic) · memory next-version-the-store, 2026-10-11 <!-- REQUIRED:decided -->
- Open questions: 1 the stage-neutral model; 2 how routes are made per stage; 3 the data records need; 4 one circuit in every stage; 5 the editor stack and its hosts; 6 pictures from the web; 7 saving, loading and sharing; 8 the slice order <!-- REQUIRED:open -->
- Scope · out of scope (proposed): in: the model, the record data, the editor and catalogue-editor architecture, pictures, saving and sharing, the slices · out: any code, any purchase or paid service, the PCB's own routing (spark builds PCBs with tscircuit already), firmware <!-- REQUIRED:scope -->
- Start and reach (proposed until Q0): start ⟨existing product | someone else's idea | own idea⟩ · decider reachable ⟨yes | no⟩ · users ⟨who, how | none reachable⟩ · data and connectors ⟨by category, from your own tool list; "not connected" is a gap; never ask to connect one⟩ · decider as a user ⟨n = 1 | no⟩ · must not get worse ⟨for an existing product⟩: start existing product (spark, with P267's drawn breadboard merged) · decider reachable yes · users the PO only (n = 1, the decider as a user); none other reachable · data and connectors: the repository, GitHub, Miro, the web (WebSearch, WebFetch), Chrome with Wokwi · decider as a user n = 1 · must not get worse: the sheet, the Wokwi diagram and the drawn breadboard of P267 <!-- REQUIRED:start-reach -->
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
- Q1 · How important is each assumption, and what pass line must the riskiest test meet? · decides: importance and pass lines · status: ⟨fill⟩ <!-- REQUIRED:q1 -->

## Decisions
<!-- D<n> · what · who · when · where recorded · options considered.
A yes covers only the actions and choices it names. A standing yes names its kind of action and its source.
Name what a D confirms in its words: the frame, the jobs, a direction, the remaining risk, a test, items.md. -->
- D1 · the frame is right: the decision, start and reach, scope, the five lenses and the budget of 16 searches · the PO · 2026-10-16 · AskUserQuestion Q0 in this session · options: the frame, change the scope, fewer lenses

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
