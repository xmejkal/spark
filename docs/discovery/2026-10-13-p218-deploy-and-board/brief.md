<!-- Resume: invoke product-discovery again; `discovery.py check <this folder>` names the next step. -->
# P218, deploy and the physical board: discovery brief

<!-- Readiness, its one home. collecting evidence: anything short of the two below. an experiment: the decider chose
a test (a D) before choosing an option. design: the decider confirmed the frame, the jobs and a direction, and accepted
the remaining risk (D rows). An extension may tighten these. Next: design, or a chosen test of kind spike or prototype
→ the design skill the facts name, with this file; otherwise none, and the collection plan says who runs it.
Stands on: the assumptions not retired in risks-and-tests.md; of which those the decider rated high, or — while any
is unrated. check computes both. -->
**Ready for:** collecting evidence <!-- REQUIRED:ready -->
**Stands on:** ⟨fill⟩ H, ⟨fill⟩ of which would change the decision <!-- REQUIRED:debt -->
**Decision needed:** none until the council reports; then Q1 <!-- REQUIRED:decision-needed -->

## Frame
- Request, verbatim (corrections marked): "Can we please have the council do the basic research and analysis of the epic and the spikes? And have them design the basic user journeys from the silest [simplest] one to the more advanced ones?" (the PO, 2026-10-13, this session). Before it, the same session: "I mean about the deployment processs [process] and what happens when its a different board, some basic research what is possible to do with repl, etc.. ?" <!-- REQUIRED:request -->
- Decision · decider: Which deploy journeys spark serves, in what order from the simplest to the most advanced, and what each spike answers (P219's different board, P221's other platforms, P222's REPL), so that the epic's stories can be refined · the PO <!-- REQUIRED:decision -->
- Outcome and how it is observed (a metric with unit and source, a proof command, or a log): The PO confirms (a D) a ladder of user journeys, simplest first, each step marked works, partly or not yet with its evidence, and a sourced finding per spike question. Observed in this folder and in the D rows. <!-- REQUIRED:outcome -->
- Already decided (D · who · when · where; include the product's stated non-goals and earlier decisions the request names): D the epic enters Discovery with the PO assistant and tech lead lenses and a feasibility study (the PO, 2026-10-13, #200 body). D a spike answers with a finding with sources, not code (the PO, 2026-10-13, #203 and #204). D spark exports facts, never behaviour, and uses free, few and local tools (AGENTS.md, Principles). D `deploy.py` flashes only an image that a passed simulation run names, erases first, writes at 0x0, pins esptool 5.5.0 and mpremote 1.29.0 (docs/2026-10-12-p192-deploy-plan.md, merged in PR #191). H no deployer agent yet (Claude's note on #192, not a D). <!-- REQUIRED:decided -->
- Open questions: Is P215's bench a source of facts for this discovery, or its first item? Which boards does P219 have to handle (the FireBeetle 2 ESP32-S3, a XIAO ESP32-C6, others)? (OTA: in scope since D5.) <!-- REQUIRED:open -->
- Scope · out of scope (proposed): In: how a project's firmware reaches a real board, how it is updated, what the REPL and a live connection make possible, what happens when the connected board differs from the project's, and what other firmware platforms (Arduino, PlatformIO first) need from the chain. Out: the firmware's behaviour (spark writes facts only), the PCB, the enclosure, ordering, and the store (P178). <!-- REQUIRED:scope -->
- Start and reach (proposed until Q0): start existing product (`scripts/deploy.py`, merged in PR #191) · decider reachable yes · users the PO only, as n = 1; the personas in scrum/VISION.md stand in for others · data and connectors: GitHub through gh (issues, PRs), web search and fetch, the Espressif docs server, Miro; Wokwi CI is metered and not used without a yes; no board on a USB port (ls /dev/cu.*, 2026-10-13) · decider as a user n = 1 · must not get worse: `deploy.py` refuses an image that no passed run names, and its dry run runs nothing <!-- REQUIRED:start-reach -->
- Flags (yes · no · —; asked only when it changes a decision; never legal advice; any date or threshold is read at its source at run time and cited):
  - sold or given away, or personal use: spark is given away under MIT; the gadgets are personal use · E LICENSE <!-- REQUIRED:flag-sold -->
  - connects to a network or runs software (for example the EU's Cyber Resilience Act): — (ESP32 boards run software and have Wi-Fi; no deploy decision rests on the rule yet) <!-- REQUIRED:flag-network -->
  - children or food contact: — <!-- REQUIRED:flag-children -->
  - market: — <!-- REQUIRED:flag-market -->
  - radio (unlicensed-device rules; read at their source when it decides): — (not asked: no decision rests on it) <!-- REQUIRED:electronics-firmware:flag-radio -->
  - a Li-ion cell (charging, transport, battery rules): — <!-- REQUIRED:electronics-firmware:flag-li-ion -->
  - mains: no <!-- REQUIRED:electronics-firmware:flag-mains -->
  <!-- EXTEND:flags -->
- Extensions (each active id · the fact that activated it; when none matched, only "none matched: core only · the fact that decided it", naming no extension; list any directive skipped under rule 9): electronics-firmware · repo-has boards/*.json; spark-process · repo-has scrum/WORKING_AGREEMENTS.md <!-- REQUIRED:extensions -->
- The item (its issue, or the proposal in the decider's words) · what is still open elsewhere · the repository's push check, or "no push check here": P218 (#200), the epic, with P215 (#196), P219 (#201), P213 (#192) and the spikes P221 (#203) and P222 (#204) · open elsewhere: the P100 discovery (docs/discovery/2026-10-09-p100-real-use) waits on the PO's yes to its changed frame; P215 is in Ready; nothing in flight, no open PR · push check: `tools/pre-push` <!-- REQUIRED:spark-process:item -->
<!-- EXTEND:frame -->
- Depth: TRIO (default: PO assistant, user, tech lead) | FULL or LIGHT (who asked, when); add "no independent review" if subagents could not start: TRIO, three agents: the PO assistant, the user, the tech lead (with the physics lens). The PO asked for "the council", 2026-10-13 <!-- REQUIRED:depth -->
  <!-- Cost, measured once: the P900 rehearsal's council took 6 agents, 499 calls and about 90M input tokens (2026-10-06). -->
- Search budget: proposed: the PO assistant 6 web searches, the user 3, the tech lead 8 (a query to the Espressif docs server counts as one), the refuter 2 <!-- REQUIRED:budget -->
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
- D1 · the frame confirmed as proposed: TRIO, the search budget, the scope · the PO · 2026-10-13 · this session, verbatim: "Sounds good as you recommend it" · options considered: TRIO, FULL, OTA in scope
- D2 · the order: P215's bench and this discovery run side by side, then Ready as P214, P139, P138, P202, and P220's discovery after this one · the PO · 2026-10-13 · this session, verbatim: "Can you replan the order and do it ? We can iterate on it, the usual process"
- D3 · standing approval for board moves, waiting flags and issue comments as the work happens, and a Miro board per discovery linked from its issue · the PO · CLAUDE.local.md, "The board" and "How Petr wants work done"
- D4 · deploy never erases or writes a board it did not check, and never without the person's yes; the council designs the use cases and journeys for a person and for Claude: check the board, offer a better-matching board setup, or offer to download the matching firmware base, with safe and correct behaviour · the PO · 2026-10-13 · this session, verbatim: "Yeah, the not checking and ereasing etc cannot happen, let's have the council design the use cases the user journeys , making sure its great UX for both humans and ai and its really has to be safe and check the board, offer a more suiting one or even somehow offer to download the firmware base  or whatever is possible, but safe and correct behavior" · after PO-23 and USER-1
- D5 · the scope widens: two almost identical boards connected at once, updates over the air (OTA), and a protocol or workflow between spark and the board's firmware join the journeys to design · the PO · 2026-10-13 · this session, verbatim: "Thinking about all probable use  cases, what if there are two almost thee same boards connected to the computer, what about OTA, is there any protocol / workflow between the spark plugin and the boardd firmware or anything like that?" · options considered: OTA named only (the frame's open question)
- D6 · when the board is known and correct, the deploy and the update are seamless, and spark is still really sure that everything is right · the PO · 2026-10-13 · this session, verbatim: "On the other hand if the board is known, we know its correct, the upgrade and deploy should be semless, but really being sure everything is ok" · it meets D4's "never without the person's yes": the council proposes how the two hold together
<!-- D<n> · what · who · when · where recorded · options considered.
A yes covers only the actions and choices it names. A standing yes names its kind of action and its source.
Name what a D confirms in its words: the frame, the jobs, a direction, the remaining risk, a test, items.md. -->

## Found on the way <!-- CLAIMS -->
<!-- Outside this item's scope. Each is a separate proposal, never folded in. Same line format as What we found. -->
- ⟨fill⟩ | none <!-- REQUIRED:found -->

## Board actions <!-- REQUIRED:spark-process:board-actions -->
<!-- Each action on the board or the issue (stage, waiting flag, comment, filing): taken, with its D, or pending.
None is taken without a D. e.g. `- move #16 to Discovery · pending` -->
- move #200 to Discovery · taken 2026-10-13, D3
- move #196 to Build, Waiting on the PO, since 2026-10-13 · taken, D3
- Ready reordered: P214, P139, P138, P202 · taken, D2
- comment on #200 linking this brief · pending, at the PR
- a Miro board for the map and options · pending, at step 4, D3
<!-- EXTEND:brief-sections -->

## Hand-off
<!-- Written only after the decider confirms the understanding (a D); copies only confirmed constraints. Holds: outcome ·
who · success and its proof · constraints (appetite, confirmed no-gos, rabbit holes) · what they said (D) against what
we assume (H) · links to the journeys and the map · riskiest assumptions and their tests · options considered. -->
⟨the hand-off | not yet: what is unconfirmed⟩ <!-- REQUIRED:handoff -->

## Files
[Jobs and journeys](jobs-and-journeys.md) · [Story map](story-map.md) · [Risks and tests](risks-and-tests.md) · [Verification](verification.md) · [Items](items.md) · council/
