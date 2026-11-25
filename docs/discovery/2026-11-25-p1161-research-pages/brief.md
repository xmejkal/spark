<!-- Resume: invoke product-discovery again; `discovery.py check <this folder>` names the next step. -->
# P1161 research and record editing from the page: discovery brief

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
- Request, verbatim (corrections marked): the PO, 2026-11-25 about 20:45 CET, in the page-design session, verbatim (card #1697): "Btw, one more epic to design and analyze/refine/plan/implement, etc is the research. When I want to edit a record and change something there, or I want claude to search the net, etc. We should also have pages for editing records and possibly for researching when adding new parts, based on photos, or just finding online a part/board/module that could do what we need, setting up criteria, etc. Andd how does it all fit to the journey, what screens change, etc. That;s one topic and another will be adding drag&drop to the pages, these two I'd like you to ask the coordinator to create as ideas, etc. the whole cycle". Drag and drop is the other epic, P1162 #1698, and is out of this one. <!-- REQUIRED:request -->
- Decision · decider: D-q1 which record edits a person makes from the page, and on which records (a part record in the project, on the shelf, in the catalog; a board record; a drawer entry) · D-q2 how a research starts from the page: from a photo (identify), for a named part, or by criteria the person sets (find a part, board or module that does the job) · D-q3 where each sits in the journey, and which screens of the design canvas change or are new · D-q4 how each fits the one core as Operations, and which of them the page may send itself and which stay "Ask Claude" offers (P1122) · decider: the PO, delegated to the council of three on Fable while he is away (spark-main's brief, 2026-11-25); a really important choice goes to him <!-- REQUIRED:decision -->
- Outcome and how it is observed (a metric with unit and source, a proof command, or a log): proposed: one written answer per decision, each with its screen sketch and its Operations; observed later, at the epic's Done when (card #1697): "A person edits a part record, starts a research from a photo or online by criteria they set, and sees where each fits in the journey, from the page." A walk on a real part (for example the 1.8 in IPS display DFR0928 in the PO's drawer, Store.dc.html) is the proof <!-- REQUIRED:outcome -->
- Already decided (D · who · when · where; include the product's stated non-goals and earlier decisions the request names): D-a · one core, many interfaces; spark exports facts, never behaviour; records grow by need; free, few and local · AGENTS.md principles · D-b · every plan says how it fits the core: a small class behind an Operation in the catalogue, each interface thin over it · the PO · 2026-11-25 · rules.md · D-c · the page's Claude jobs are Offers with a key and one sentence (`tell`), shown as "Ask Claude" with the sentence visible; a later direct channel carries only id, key, seen and ends in `flow.py run-request`; no Artifact `sample` call · the PO · 2026-11-25 · P1122 #1652 · D-d · a kept step holds the records the person decided, one step per decision; any kept step can be taken back; plain words after a kept step · the PO · 2026-11-25 · git discovery D8, D9, D11 (docs/discovery/2026-11-25-spark-and-git/brief.md:125-128) · D-e · research gathers no prices, stock or seller listings; owning a part never starts research; research is asked for a part the person chooses, with the cost first · commands/research.md section 3; StoreAdd.dc.html "Research a new part" · D-f · the catalogue editor (P276 #312) is step 7 of P269, with photos and pins marked on the picture · the PO · 2026-10-16 · P269 D8 to D10 · D-g · his money rule: anything that costs money is named and asked first · rules.md "What waits on him" <!-- REQUIRED:decided -->
- Open questions: see Questions <!-- REQUIRED:open -->
- Scope · out of scope (proposed): in: editing a part or board record's facts from the page (with its source), the drawer entry's fields as the store pages show them today, starting a research or an identify from the page, a find by criteria (the need in words plus limits), where each sits in the journey, which canvas screens change, the Operations and the offers behind them · out: drag and drop (P1162 #1698); marking pins on a picture (P276 #312, its own step); prices, stock and buying (P884 #1252); a research engine change (P340, P997, P998 stay their own cards); building anything <!-- REQUIRED:scope -->
- Start and reach (proposed until Q0): start existing product (the store pages on the canvas, `/spark:research`, `/spark:identify`, `parts.py`, `research.py`) · decider reachable yes, through Remote Control; his choices go to the delegated council of three · users none reachable beyond the PO · data and connectors: the repository, gh, the store (read only), the design canvas (read only), the web for the existing-first lens · decider as a user n = 1 (his walks: P934 #1323; P992 #1445 quotes him) · must not get worse: `/spark:research` and `/spark:identify` in Claude Code, the store pages as designed, the records' contract (`parts.py --validate`) <!-- REQUIRED:start-reach -->
- Flags (yes · no · —; asked only when it changes a decision; never legal advice; any date or threshold is read at its source at run time and cited):
  - sold or given away, or personal use: personal use now; spark is public under MIT <!-- REQUIRED:flag-sold -->
  - connects to a network or runs software (for example the EU's Cyber Resilience Act): yes: research reaches the web, and the page is a Claude Artifact; no device change in this epic <!-- REQUIRED:flag-network -->
  - children or food contact: no <!-- REQUIRED:flag-children -->
  - market: — <!-- REQUIRED:flag-market -->
  - radio (unlicensed-device rules; read at their source when it decides): no: the epic changes records and pages, no device <!-- REQUIRED:electronics-firmware:flag-radio -->
  - a Li-ion cell (charging, transport, battery rules): no <!-- REQUIRED:electronics-firmware:flag-li-ion -->
  - mains: no <!-- REQUIRED:electronics-firmware:flag-mains -->
  <!-- EXTEND:flags -->
- Extensions (each active id · the fact that activated it; when none matched, only "none matched: core only · the fact that decided it", naming no extension; list any directive skipped under rule 9): spark-process · repo-has scrum/WORKING_AGREEMENTS.md; electronics-firmware · repo-has boards/*.json. Proposed at Q0: keep electronics-firmware narrow. The epic changes no device, but a record edit changes facts that checks read (a supply range, a pin order), so its physics lens asks only what an edit or a research changes in those facts <!-- REQUIRED:extensions -->
- The item (its issue, or the proposal in the decider's words) · what is still open elsewhere · the repository's push check, or "no push check here": P1161 #1697 (https://github.com/xmejkal/spark/issues/1697), an epic in Discovery since 2026-11-25 about 21:00 CET, slice Views and editors · still open elsewhere: the git discovery P1148 (ready for an experiment), P1002 #1461 (in Idea on the board, a bench finding kept in the store), P1162 #1698 (drag and drop), P735 #1010 (full DFRobot part records, back in Idea), P1164 #1700 (capture the reality from a photo), and the overlapping cards P992 #1445, P276 #312, P340 #434, P997 #1454, P998 #1457, P230 #218 · the push check is the pre-push hook <!-- REQUIRED:spark-process:item -->
<!-- EXTEND:frame -->
- Depth: TRIO (default: PO assistant, user, tech lead) | FULL or LIGHT (who asked, when); add "no independent review" if subagents could not start: FULL, asked by spark-main's brief for this card (2026-11-25), every lens on Opus. Five lenses: the PO assistant (existing first, risks), the user (journey), the tech lead (feasibility, and the physics lens narrowed), the architecture lens (the core and the Operations; rules.md: a new interface adds it), the UX and AI-UX lens (the PO's rule of 2026-10-18). Then the refuter on Opus, and the architect agent for the synthesis. Seven agents <!-- REQUIRED:depth -->
  <!-- Cost, measured once: the P900 rehearsal's council took 6 agents, 499 calls and about 90M input tokens (2026-10-06). -->
- Search budget: the PO assistant: at most 6 web searches, for the existing-first question (parametric part search, photo identification); the other lenses: the repository, the store (read only) and the canvas copies, no web <!-- REQUIRED:budget -->
- Appetite (the decider's, asked only when heading for design) | —: — <!-- REQUIRED:appetite -->

## What we found <!-- CLAIMS -->
<!-- One claim per line: `- [★C<n>] claim · E pointer | H source | D who date · caveat: qualifier | none`.
★ marks a claim that a decision, an option or the riskiest assumption rests on. A quote is verbatim, with its pointer.
Say what the evidence can support: an account (what happened to one person), data (how often, in its population and
period), a document (what was specified), the product (what exists, not whether anyone needs it), a benchmark (a
comparison). Model knowledge is H until a source is read. Elsewhere cite a ★ claim as ★C<n>, with its keep: words.
e.g. `- [★C2] 13 of 526 tickets ask for recurring tasks · E tickets.csv:2-14 · caveat: picked by Lena; shows that, not how often` -->
- [★C1] The page's request carries only `id, key, seen`, and the step's values come from spark's own offer key, never from the request. A test pins it. So a value the person types (a fact, a criterion) cannot travel from the page today · E scripts/spark/flow/run_request.py:1-6, tests/test_run_request.py:272-276 · D-c (P1122) · caveat: the channel as built and decided, not whether a wider one is safe
- [★C2] Research, identify and an online find are jobs only Claude can do: `research-part` declares asks and fetches, the agents hold the web search and the image reading, and the accepted page rule bars an Operation that asks or fetches from a page. So each is an "Ask Claude" offer · E scripts/spark/sourcing/research/research_part.py:145, `<store>/councils/p1113/architect-page-actions.md` §3, council/architecture.md ARCH-2 · caveat: no test enforces the bar yet (P1082 is open)
- [★C3] A record edit already has its Operation. `fact-set` writes facts in the record's own home, with a dry run and a `was` and `now` answer. It refuses to empty a fact, and it does not accept `name`, `vendor`, `sku`, `needs` or `power`, which the research agents write by hand · E scripts/spark/sourcing/set_facts.py:28-32, :47-50, council/architecture.md ARCH-7 · caveat: the key list grows by need, so a missing key is a gap, not a misfit
- [★C4] Nothing marks a build, a breadboard sheet or a pin map out of date after a part record changes. The fingerprint reads the needs, the requirements and the build record, and the build record stamps the requirements and `board.tsx` only · E scripts/spark/flow/fingerprint.py:17-18, scripts/spark/build/build_record.py:25-33, council/tech-lead.md TL-21 · caveat: P1160 #1696, a spike in Build, maps these links for take-backs
- [★C5] An edit that sets `verified: true` with any words as its source can make a check pass falsely: the rail check turns needs-measurement into a pass, and `module_has_i2c_pullups` true silences the I2C refusal whatever its flag. Nothing ties `verified: true` to a person, a date or a document · E scripts/spark/checks/physics_check.py:193-199, scripts/spark/sourcing/part_rules.py:138-144, scripts/spark/records/provenance.py:13, council/tech-lead.md PHYS-2, PHYS-3, TL-19 · caveat: read from the code, no edit was run
- [★C6] A part record edit is no kept step today. D8 names the brief, the needs, the picks, the requirements and the board. The shelf, the catalog and the drawer sit in the store, outside every project's git · E docs/discovery/2026-11-25-spark-and-git/brief.md:125, scripts/spark/records/store.py:145-148 · caveat: D8 is the PO's of 2026-11-25, and adding part records is his call
- [★C7] The PO's drawer holds 114 entries: 19 link to a record, 95 do not, 93 of the 95 carry a part number, 99 of 114 come from DFRobot, and 4 of 114 keep a photo · E a read-only count over `<store>/drawer/*.json`, 2026-11-25 about 22:15 CET, reproduced in this session · caveat: shows what the store holds, not how often he wants to edit or research (owning a part never starts research, D-e)
- [★C8] In the one case seen where a record's fact was wrong and mattered (the e-paper controller), research did not settle it, and a bench trial did · E `<walks>/p934-display2/diary.md:157-165`, `:268-271`, council/user.md USER-1 · caveat: 1 of 1 case, an account of one person
- [★C9] spark has no cost before a research run. The only measured runs are three, from 2026-10-03: the old full protocol at a median of about 5.0 M tokens and 25 minutes, one LED at about 0.55 M tokens and 148 s, and part-finder's first use at about 0.17 M tokens and 91 s. The store's history holds no research step · E docs/guide/research-cost.md:3-11, `<store>/history.jsonl` (steps S 14, C 13, M 12, L 10, no G, 2026-11-25), scripts/spark/sourcing/run_cost.py:1-12 · caveat: n = 1 for each lean run, and no module research or identify is measured
- [★C10] The Parts design has no exit for a need with no fitting part: Send waits until every need is picked, and no tile says "not here". This is the moment of P992, where the PO said "what if it's not in the store ?" · E canvas:Parts.dc.html:196, `<walks>/p934-display/diary.md:86-90`, gh issue 1445 · caveat: a design, not built
- [★C11] Find by criteria has no path. A need's words only order the store's own candidates, part-finder is for commodity parts and never ran in a walk, and parts-researcher stops at the first vendor that fits · E agents/parts-researcher.md:35-38, README.md:122, scripts/spark/sourcing/matching.py:70-79, council/user.md USER-7 · caveat: none
- [★C12] No outside parametric search fits "free, few and local" for modules. spark's jlcpcb tool searches by keyword and returns price and stock, and a module query gave 0 LCSC results. DigiKey, Nexar and TME need an account · E council/po-assistant.md PO-4, PO-5 (the tool calls and pages read 2026-11-25) · caveat: one module query, and the terms behind each login were not read
- [★C13] A request has a home only in a project: `run-request` reads the project's request file and fingerprint, and `--skeleton` writes a new record only into a project's `parts/`. No store page exists in code · E scripts/spark/flow/run_request.py:153-157, scripts/spark/sourcing/write_skeleton.py:2-3, council/tech-lead.md TL-12, TL-13 · caveat: the store pages are canvas designs only
- [★C14] No Operation writes a record into the catalog. The code reads the catalog, and the parts-researcher agent writes catalog records by hand from rules in two prompts · E grep of `place("catalog")` over scripts/spark (readers only), commands/research.md:151-158, council/architecture.md ARCH-9 · caveat: none
- [★C15] Nobody is blocked today. Every record edit and every research in the walks ran through Claude in the chat, after the PO's yes. His ask for the page came from looking at the page · E `<walks>/p934-display2/diary.md:277-290`, council/po-assistant.md PO-2 · caveat: an account, n = 1. The hobbyist of scrum/VISION.md is not reached
- [★C16] The DFR0664's 9 unchecked facts need his eyes, a meter, a trial or a kept schematic, and 0 of 9 need a new web search, by the record's own notes. The design's main offer sends two "not published" facts to a datasheet · E `parts.py --unverified dfr0664-tft-2in` (2026-11-25), canvas:StorePart.dc.html:33 against :65, council/user.md USER-2, USER-3 · caveat: the split by who settles each fact is the lens's reading of the notes
- [★C17] Three overlapping cards hold parts of this epic: P992 #1445 (the page offers to add a part the store lacks), P276 #312 (the catalogue editor, the PO's "most important" job of P269), and P1002 #1461 (offer each bench finding to the store). P735 #1010 (a full record for each DFRobot part) and P1164 #1700 (capture the reality from a photo) share the research engine and the photo path · E gh issue 1445, 312, 1461, 1010, 1700 · D the PO 2026-10-16 (P269 D9) · caveat: none <!-- REQUIRED:findings -->

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

## Found on the way <!-- CLAIMS -->
<!-- Outside this item's scope. Each is a separate proposal, never folded in. Same line format as What we found. -->
- [C18] `--promote` copies a project's record into spark's library with no check of `verified`, while every other write refuses the library and commands/research.md says it copies "a verified record" · E scripts/spark/sourcing/part_facts.py:154-177, scripts/spark/sourcing/record_home.py:165-171, commands/research.md:111-112, council/tech-lead.md TL-18 · caveat: proposed as its own card in items.md
- [C19] `research-part` is missing from `parts.py --describe`, `research.py` has no `--describe`, and `--describe` has no word for an Operation that asks · E `parts.py --describe --json` and `research.py --describe` (2026-11-25), scripts/spark/core/describe_operations.py:18, council/architecture.md ARCH-13 · caveat: P1082's guard needs the word
- [C20] Rules sit in prompts and repeat: the facts each kind needs (commands/research.md:76-84 against data/fact-needs.json), the header geometry rule written three times, the vendor order twice, the catalog record's shape in two prompts · E council/architecture.md ARCH-14 · caveat: the refactor list for this epic's plan, not a defect a person meets
- [C21] StoreAdd's photo fold says "every fact marked not checked", while `/spark:identify` marks a fact from the chip's datasheet as checked · E canvas:StoreAdd.dc.html:33, commands/identify.md:53-56, council/ux-ai-ux.md UX-8 · caveat: a canvas wording fix
- [C22] The drawer's seller names differ in case (`aliexpress` 2 entries, `AliExpress` 1) · E council/po-assistant.md PO-32 · caveat: a data fix <!-- REQUIRED:found -->

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
