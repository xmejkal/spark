<!-- Resume: invoke product-discovery again; `discovery.py check <this folder>` names the next step. -->
# P1002 project learning and settings: discovery brief

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
- Request, verbatim (corrections marked): the PO, 2026-11-23, in spark-main's session: "yes, ok, so llets make it work this auto learning. And lets also make it configurable. Do w actually even have some general/project setting? lets analyze this learning card and refine and plan and make it happen, I think that's a good idea to make it learning". Before it (epaper session, relayed): "lets take the learning from the project about all the used boards and modules and like store the gained info about the board into the record, so that we dont need to rediscover it next time or in other projects, like this time probably something about the sleep, etc. And before you do that and make sure spark does it automatically, tell me what you've actually learned and will save in the record". 2026-11-22: "yes and lets make it so that its always offering the new findings to be stored to the store in general.." <!-- REQUIRED:request -->
- Decision · decider: how spark keeps what a project learned about its boards and modules in their records, automatically and configurably, and where a person's general and project settings live · the PO (Petr Smejkal) <!-- REQUIRED:decision -->
- Outcome and how it is observed (a metric with unit and source, a proof command, or a log): after a project's bench work, each new fact about a board or module it used is offered and (by the setting) kept in that record, with its source (the bench log, the date, the project); a second project that uses the same board finds the fact without rediscovering it. Observed by: the record holds the fact with its source after a walk; the next project's research or flow reads it. <!-- REQUIRED:outcome -->
- Already decided (D · who · when · where; include the product's stated non-goals and earlier decisions the request names): spark exports facts, never behaviour (AGENTS.md); records grow by need, each property with its origin (AGENTS.md); a null is never filled with a typical value (the PO, 2026-11-23, and never-assume.md); every fact carries a source (AGENTS.md, keeping sources); spark asks and offers to take care of a change, and every change can be rolled back, probably through git (the PO, 2026-11-23, on P1027 #1506); the person reviews what was learned before it is written (the PO, 2026-11-23). <!-- REQUIRED:decided -->
- Open questions: what counts as a learned fact and who notices it (the bench, a session, a walk's diary); where settings live (the store has no place for a person's settings today, scripts/spark/records/store.py:107-110; only tools.json has a store copy and a project override); what the setting controls (off, offer, keep automatically); how a record change is reviewed and rolled back (records in the store are not in git today). <!-- REQUIRED:open -->
- Scope · out of scope (proposed): scope: facts about boards and modules a project used, kept in their records in the person's store; a general (store) and project setting that controls it. Out of scope: facts about the person's own project (P1027 owns its needs and must lines); writing to spark's own library in the repository; learning firmware behaviour (spark exports facts, never behaviour). <!-- REQUIRED:scope -->
- Start and reach (proposed until Q0): start ⟨existing product | someone else's idea | own idea⟩ · decider reachable ⟨yes | no⟩ · users ⟨who, how | none reachable⟩ · data and connectors ⟨by category, from your own tool list; "not connected" is a gap; never ask to connect one⟩ · decider as a user ⟨n = 1 | no⟩ · must not get worse ⟨for an existing product⟩: ⟨fill⟩ <!-- REQUIRED:start-reach -->
- Flags (yes · no · —; asked only when it changes a decision; never legal advice; any date or threshold is read at its source at run time and cited):
  - sold or given away, or personal use: ⟨fill⟩ <!-- REQUIRED:flag-sold -->
  - connects to a network or runs software (for example the EU's Cyber Resilience Act): ⟨fill⟩ <!-- REQUIRED:flag-network -->
  - children or food contact: ⟨fill⟩ <!-- REQUIRED:flag-children -->
  - market: ⟨fill⟩ <!-- REQUIRED:flag-market -->
  - radio (unlicensed-device rules; read at their source when it decides): ⟨fill⟩ <!-- REQUIRED:electronics-firmware:flag-radio -->
  - a Li-ion cell (charging, transport, battery rules): ⟨fill⟩ <!-- REQUIRED:electronics-firmware:flag-li-ion -->
  - mains: ⟨fill⟩ <!-- REQUIRED:electronics-firmware:flag-mains -->
  <!-- EXTEND:flags -->
- Extensions (each active id · the fact that activated it; when none matched, only "none matched: core only · the fact that decided it", naming no extension; list any directive skipped under rule 9): electronics-firmware · repo-has boards/*.json; spark-process · repo-has scrum/WORKING_AGREEMENTS.md <!-- REQUIRED:extensions -->
- The item (its issue, or the proposal in the decider's words) · what is still open elsewhere · the repository's push check, or "no push check here": ⟨fill⟩ <!-- REQUIRED:spark-process:item -->
<!-- EXTEND:frame -->
- Depth: TRIO (default: PO assistant, user, tech lead) | FULL or LIGHT (who asked, when); add "no independent review" if subagents could not start: TRIO (default), no independent review: one agent wrote all three lens reports (council/po-assistant.md, user.md, tech-lead.md), so they are not independent <!-- REQUIRED:depth -->
  <!-- Cost, measured once: the P900 rehearsal's council took 6 agents, 499 calls and about 90M input tokens (2026-10-06). -->
- Search budget: ⟨fill⟩ <!-- REQUIRED:budget -->
- Appetite (the decider's, asked only when heading for design) | —: ⟨fill⟩ <!-- REQUIRED:appetite -->

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
- D1 · the frame confirmed, widened · the PO · 2026-11-23 · Q0 (AskUserQuestion in spark-main's session) · his words: "Yes its right and also lets consider the future use cases, so we also To prepare our architecture for future storage systems, we need to establish a modular approach that allows us to easily interchange our data storage methods. One effective strategy is to implement a dependency injection pattern, enabling us to switch between file-based storage, databases, or cloud solutions without significant refactoring. We'll categorize our data based on various entities—such as application state, board configurations, and project modules—ensuring that each module can dynamically connect to its preferred storage type. This flexibility will empower our system to integrate seamlessly with Spark when using LangGraph for experiments like Retrieval-Augmented Generation (RAG) use cases. By designing our architecture to prioritize adaptable patterns, we can ensure that changing our data storage approach in the future is straightforward and efficient, ultimately enhancing the scalability and maintainability of our application." · so the scope adds: a storage seam (a repository per entity, injected) behind which the file store, a database or a cloud store can sit, and the settings and learned facts use that seam · options considered: frame as proposed, one lens, change the scope
- D2 · the scope narrowed · the PO · 2026-11-23 · his message in spark-main's session: "The alternative storage systems might be a bigger change of the whole system, so we can separate it out probably into a bigger refactoring card or epic for the storage in general. And we can only use the file system, but already as an implementation, we'll add the other types later, what do you think? this might really want a bigger better model analysis and refactoring. And as always, we dont need to reinvent the wheel, get inspired, research, reuse, etc." · so: P1002 uses the file system only, behind one small seam (an interface for the records it reads and writes, the file store as its one implementation); the general storage work is the epic P1033 #1515 (filed 2026-11-23), analysed on the best model with research first (for example LangGraph's store interface) · options considered: D1's whole storage scope in P1002, or the split
- D3 · the setting's values · the PO · 2026-11-23 · AskUserQuestion in spark-main's session · "off / offer / keep": off: spark keeps nothing; offer: spark lists each new fact with its source and old and new values, and keeps it on the person's yes; keep: spark keeps it at once, reversible · default: offer · options considered: offer and keep only; keep by default


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
