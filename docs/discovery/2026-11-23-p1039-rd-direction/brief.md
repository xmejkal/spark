<!-- Resume: invoke product-discovery again; `discovery.py check <this folder>` names the next step. -->
# P1039, spark past the MVP (R&D direction): discovery brief

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
- Request, verbatim (corrections marked): the PO, 2026-11-23, about 15:4x CET, in the epaper session: "lets create another kinda bigger R&D epic and think about whats next, how to make it a software factory, what other harnesses or frameworks we can support, how we should evaluate and improve the system, etc. And lets do some really high level product and architecture and features and use cases level" (#1522 body). His additions on #1522, 2026-11-23: about 15:3x CET, the interface question ("is there another way to architect such a system when we want it to be kind of agent-native and able to run in different harnesses, maybe, but also it works for humans and it has a good interface? ..."); about 15:5x CET, evaluation, other harnesses ("like Hermes or others"), generality ("not only for Claude but just generally runnable"), a local AI later, and "How do we evaluate what models we use for what?"; about 16:0x CET, the agent-knowledge question ("Do we have a system that makes sure that all the new features ... also updates the agentic knowledge (the skills and everything) ...?"). The session order, 2026-11-23: full depth, the architecture lens, the full council, the architect agent on the best model for the synthesis, high level only, no build. <!-- REQUIRED:request -->
- Decision · decider: which directions past the MVP become later epics, in which order, and which seams the core work now in flight (P793 #1105, P1033 #1515) must keep open for them · the PO. This discovery proposes; it decides none of it. <!-- REQUIRED:decision -->
- Outcome and how it is observed (a metric with unit and source, a proof command, or a log): the PO confirms the brief's understanding (a D row here), and later epics are filed from items.md on his yes (their issue numbers in items.md). Observed on #1522 and the board. <!-- REQUIRED:outcome -->
- Already decided (D · who · when · where; include the product's stated non-goals and earlier decisions the request names): the vision and its non-goals, among them no firmware generator, no knowledge skill per runtime (P60), no Arduino or ESP-IDF before a design pulls them · the PO · 2026-10-03 · scrum/VISION.md. The order MVP, then one core (v0.13), then a LangGraph spike, then a RAG spike · the PO · 2026-10-26 · scrum/VISION.md (Versions). One core, many interfaces; facts, never behaviour; free, few and local · the PO · AGENTS.md (Principles). MicroPython behind a neutral seam, only the CLI and skills built now · the PO · 2026-10-15 and 2026-10-31 · the architecture memory note, cards P221 #203 and P336 #430. The core ready for streaming and async events, consumers LangGraph, a live web page and an SSE MCP; the CLI works fully first · the PO · 2026-11-23 · #1105 comments of 12:54 and 12:55 CET. Storage under the Stores shaped like LangGraph's store · the PO's order, 2026-11-23 · #1515. The agent-knowledge question goes under theme 3 · the PO · 2026-11-23 · #1522 comment. <!-- REQUIRED:decided -->
- Open questions: (1) what spark is past the MVP, the software factory idea; (2) which harnesses, frameworks, runtimes, boards and kinds of project spark can support, and what in spark depends on Claude; (3) how spark evaluates and improves itself: walks, benchmarks, learned rules, retros, write-back, which model does which job, and whether the agents' knowledge keeps up with the scripts; (4) other ways to split the core from its human and AI interfaces; (5) a local AI as a later target. <!-- REQUIRED:open -->
- Scope · out of scope (proposed): in scope: the five open questions at the level of product, architecture, features and use cases. Out of scope: any build, spec or plan; the page's design (P1038 #1521, its own discovery); the storage design (P1033 #1515); the PCB and 3D epics' content (P203); the board order of the current lane. <!-- REQUIRED:scope -->
- Start and reach (proposed until Q0): start own idea (the PO's, about an existing product) · decider reachable yes, in this session · users: no person outside the project installed spark (scrum/VISION.md, Who it is for), so the hobbyist stays H; the agent at the keyboard is seen in walk diaries and session logs · data and connectors: the repository, the board and issues through gh, the walk diaries, the store's learned rules and retros, web search, the Espressif docs MCP; no usage analytics exist, no harness other than Claude Code is installed here (not checked yet) · decider as a user: n = 1 (the PO walks spark at his bench) · must not get worse: the MVP journey and its walk (P934 #1323), the hook, the token budget, the core work in flight. <!-- REQUIRED:start-reach -->
- Flags (yes · no · —; asked only when it changes a decision; never legal advice; any date or threshold is read at its source at run time and cited):
  - sold or given away, or personal use: given away, MIT, public on GitHub (AGENTS.md) <!-- REQUIRED:flag-sold -->
  - connects to a network or runs software (for example the EU's Cyber Resilience Act): yes, it is software; asked only if a direction would sell it <!-- REQUIRED:flag-network -->
  - children or food contact: no <!-- REQUIRED:flag-children -->
  - market: anyone on GitHub; the PO is in Czechia (EU) <!-- REQUIRED:flag-market -->
  <!-- EXTEND:flags -->
- Extensions (each active id · the fact that activated it; when none matched, only "none matched: core only · the fact that decided it", naming no extension; list any directive skipped under rule 9): spark-process · repo-has scrum/WORKING_AGREEMENTS.md. electronics-firmware matched by repo-has boards/*.json but is proposed off: the epic touches no part, circuit, power or firmware number; "other boards and runtimes" asks which ones, not how a circuit behaves (its context.md, When it does not apply). Q0 can switch it on. <!-- REQUIRED:extensions -->
- The item (its issue, or the proposal in the decider's words) · what is still open elsewhere · the repository's push check, or "no push check here": P1039 #1522, an epic in Discovery (board, read 2026-11-23) · open elsewhere: P1002 #1461 in Discovery, and nine earlier discoveries still collecting evidence or waiting for design (probe, 2026-11-23); the push gate exempts epics · push check: tools/check_backlog.py, in the hook. <!-- REQUIRED:spark-process:item -->
<!-- EXTEND:frame -->
- Depth: FULL, asked by the PO on #1522 (Done when) and in this session's order, 2026-11-23. Eight agents: six lenses on Opus (the four core lenses, the architecture lens he named, and the UX and AI-UX lens his rule of 2026-10-18 adds to interface work, which the interface question is), the refuter on Fable (an epic, scrum/README.md, the token budget), and the synthesis by the architect agent on Fable. This is the day's second full council after P1033's; his order covers it. <!-- REQUIRED:depth -->
  <!-- Cost, measured once: the P900 rehearsal's council took 6 agents, 499 calls and about 90M input tokens (2026-10-06). -->
- Search budget: 24 web searches in all: Existing first 10, architecture 6, UX and AI-UX 3, risks 3, feasibility 2, the user's journey 0; the refuter 3 more. <!-- REQUIRED:budget -->
- Appetite (the decider's, asked only when heading for design) | —: —, high level only, no build <!-- REQUIRED:appetite -->

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
- D1 · confirms the frame as written: the decision, the five questions, the scope, start and reach, electronics-firmware off, FULL depth with eight agents (six Opus lenses, the refuter and the synthesis on Fable), 24 searches · the PO · 2026-11-23 · this session, AskUserQuestion, option "Yes, as written" · options considered: as written; fewer agents (five); electronics on
- D0 · standing: this session writes only in this folder and on #1522, moves no card, and the folder reaches main by a PR · the PO · 2026-11-23 · this session's opening order

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
