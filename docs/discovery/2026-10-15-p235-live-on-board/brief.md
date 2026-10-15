<!-- Resume: invoke product-discovery again; `discovery.py check <this folder>` names the next step. -->
# P235, live on the board: discovery brief

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
- Request, verbatim (corrections marked): the PO, 2026-10-13, on #224: *"Also, while revisiting the plan and architecture, let's review the functionality for REPL and WebREPL and just running code live on the device when connected and debugging maybe? Seral monitor, things like that, lets please revew the plans and options for that, I think we also have an epic for that or lets make one and move all related stories there, if its ok , then update all journeys and use cases and story maps."* Moved to Discovery: *"P235 next"* (2026-10-15). <!-- REQUIRED:request -->
- Decision · decider: what P235 builds first and in which order (a live REPL try over USB, a serial monitor, running a file live without a flash, debugging; WebREPL and OTA later), and whether the spike P222 (#204) runs before it · the PO <!-- REQUIRED:decision -->
- Outcome and how it is observed (a metric with unit and source, a proof command, or a log): the PO picks a first slice and an order, recorded as D rows here; the first slice is later proven at the bench on the XIAO ESP32-C6 with P246's board-only project, by a bench log in docs/observations/ <!-- REQUIRED:outcome -->
- Already decided (D · who · when · where; include the product's stated non-goals and earlier decisions the request names): D29 live tries are free `exec` after one yes per session, each try ends with a reset · D30 P222 also reads a third-party MicroPython MCP plugin and belay, each install with its own yes · D31 OTA and a Wi-Fi REPL get their own discovery · D43 the live session's yes goes through P219's gate (the look's token and a terminal yes) · all the PO, 2026-10-13, docs/discovery/2026-10-13-p218-deploy-and-board/brief.md · spark exports facts, never behaviour (AGENTS.md, the firmware decision) · D1 below (Q0) <!-- REQUIRED:decided -->
- Open questions: Q1 onward, in Questions <!-- REQUIRED:open -->
- Scope · out of scope (proposed): in: the USB REPL, live `exec`, running a file without a flash, a serial monitor, debugging on the board, P222's question, P246 as the bench project · out: OTA and WebREPL as the first slice (an option for a later slice, D31), firmware platforms other than MicroPython (P221 #203), flashing and the gate itself (P218) <!-- REQUIRED:scope -->
- Start and reach (proposed until Q0): start ⟨existing product | someone else's idea | own idea⟩ · decider reachable ⟨yes | no⟩ · users ⟨who, how | none reachable⟩ · data and connectors ⟨by category, from your own tool list; "not connected" is a gap; never ask to connect one⟩ · decider as a user ⟨n = 1 | no⟩ · must not get worse ⟨for an existing product⟩: existing product <!-- REQUIRED:start-reach -->
yes- Flags (yes · no · —; asked only when it changes a decision; never legal advice; any date or threshold is read at its source at run time and cited):
  - sold or given away, or personal use: personal use · the PO's own boards (E memory, the bench logs) <!-- REQUIRED:flag-sold -->
  - connects to a network or runs software (for example the EU's Cyber Resilience Act): yes for WebREPL and OTA (Wi-Fi), no for the USB slice · read the CRA at its source only if a Wi-Fi slice is chosen <!-- REQUIRED:flag-network -->
  - children or food contact: no <!-- REQUIRED:flag-children -->
  - market: — (personal use; spark is public under MIT) <!-- REQUIRED:flag-market -->
  - radio (unlicensed-device rules; read at their source when it decides): only for WebREPL and OTA (the ESP32's own Wi-Fi) · not for the USB slice <!-- REQUIRED:electronics-firmware:flag-radio -->
  - a Li-ion cell (charging, transport, battery rules): no (the bench boards run on USB power) <!-- REQUIRED:electronics-firmware:flag-li-ion -->
  - mains: no <!-- REQUIRED:electronics-firmware:flag-mains -->
  <!-- EXTEND:flags -->
- Extensions (each active id · the fact that activated it; when none matched, only "none matched: core only · the fact that decided it", naming no extension; list any directive skipped under rule 9): electronics-firmware · repo-has boards/*.json; spark-process · repo-has scrum/WORKING_AGREEMENTS.md <!-- REQUIRED:extensions -->
- The item (its issue, or the proposal in the decider's words) · what is still open elsewhere · the repository's push check, or "no push check here": #224 (P235, epic), with P222 #204 and P246 #260 under it · still open elsewhere: P218 #200 in Design (its epic stays open while its stories finish), the P100 discovery waits for evidence (docs/discovery/2026-10-09-p100-real-use) · the push hook is the gate (`check_commit`) <!-- REQUIRED:spark-process:item -->
<!-- EXTEND:frame -->
- Depth: TRIO (default: PO assistant, user, tech lead) | FULL or LIGHT (who asked, when); add "no independent review" if subagents could not start: TRIO, three Sonnet agents: the PO assistant, the user, the tech lead (who also takes electronics-firmware:physics) · D1 <!-- REQUIRED:depth -->
  <!-- Cost, measured once: the P900 rehearsal's council took 6 agents, 499 calls and about 90M input tokens (2026-10-06). -->
- Search budget: the PO assistant at most 6 web searches, the tech lead at most 4, the user none (n = 1, the bench logs) <!-- REQUIRED:budget -->
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
- D1 · Q0: the frame is right as proposed: the decision is P235's first slice and order, USB first, Wi-Fi (WebREPL, OTA) a later option, P222 may run first, TRIO depth · the PO · 2026-10-15 · this session, he picked "Yes, as proposed" · options considered: Wi-Fi in scope now, only the USB REPL and monitor, LIGHT depth
- D2 · standing yes: the discovery folder lands by draft PR, committed as work lands · the PO · CLAUDE.local.md "Anything for his review is a PR" · covers commits and the PR only

## Found on the way <!-- CLAIMS -->
<!-- Outside this item's scope. Each is a separate proposal, never folded in. Same line format as What we found. -->
- ⟨fill⟩ | none <!-- REQUIRED:found -->

## Board actions <!-- REQUIRED:spark-process:board-actions -->
<!-- Each action on the board or the issue (stage, waiting flag, comment, filing): taken, with its D, or pending.
None is taken without a D. e.g. `- move #16 to Discovery · pending` -->
- #224 moved to Discovery · taken by the PO's words "P235 next", 2026-10-15
- a comment on #224 linking the brief · pending
- the P235 frame on the Miro journey board · pending
<!-- EXTEND:brief-sections -->

## Hand-off
<!-- Written only after the decider confirms the understanding (a D); copies only confirmed constraints. Holds: outcome ·
who · success and its proof · constraints (appetite, confirmed no-gos, rabbit holes) · what they said (D) against what
we assume (H) · links to the journeys and the map · riskiest assumptions and their tests · options considered. -->
⟨the hand-off | not yet: what is unconfirmed⟩ <!-- REQUIRED:handoff -->

## Files
[Jobs and journeys](jobs-and-journeys.md) · [Story map](story-map.md) · [Risks and tests](risks-and-tests.md) · [Verification](verification.md) · [Items](items.md) · council/
