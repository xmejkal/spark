<!-- Resume: invoke product-discovery again; `discovery.py check <this folder>` names the next step. -->
# P325 XIAO walks: what spark does in each situation the walks hit, discovery brief

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
- Request, verbatim (corrections marked): *"And before we implement it, we can actually also have the PO/AI and UX experts and architects talk about the actual use cases/journeys and what shoud [should] actuall [actually] happen when the various scenarios happen, like Wokwi not being able to simulate, and other situations we'd design to test spark"* (the PO, 2026-10-19, about P325 #417 and its cards P326 #418, P327 #419, P328 #420) <!-- REQUIRED:request -->
- Decision · decider: what spark should do in each situation the three walks hit, approved per situation · Petr (the PO) <!-- REQUIRED:decision -->
- Outcome and how it is observed (a metric with unit and source, a proof command, or a log): each of the three walks ends with the board running its firmware and spark's own words saying what was proved and what was not; observed in each walk's notes and run logs <!-- REQUIRED:outcome -->
- Already decided (D · who · when · where; include the product's stated non-goals and earlier decisions the request names): D1 the frame, as asked in Q0 · Petr · 2026-10-19 · AskUserQuestion; D2 walk 1 first, at most one refuter per plan, lean · Petr · 2026-10-19 · this session; D3 spark exports facts, never behaviour, the conversation writes the firmware · AGENTS.md; D4 a deploy needs a passed simulation of the image · docs/guide/agents.md <!-- REQUIRED:decided -->
- Open questions: whether Seeed's SEEED_XIAO_ESP32C6 build has the bluetooth module (a check on the board); whether Wokwi's C6 gives a Wi-Fi scan (a check in Wokwi) <!-- REQUIRED:open -->
- Scope · out of scope (proposed): the situations the three walks hit, from an idea in words to a running board · out: code, the breadboard sheet's layout, other boards, a PCB <!-- REQUIRED:scope -->
- Start and reach (confirmed at Q0): start existing product · decider reachable yes · users the PO at his bench, and Claude as the operator · data and connectors the repository, GitHub, the PO's board through spark's scripts · decider as a user n = 1 · must not get worse: the basic loop that works today (build, simulate, deploy) <!-- REQUIRED:start-reach -->
- Flags (yes · no · —; asked only when it changes a decision; never legal advice; any date or threshold is read at its source at run time and cited):
  - sold or given away, or personal use: personal use, and spark itself is public under MIT <!-- REQUIRED:flag-sold -->
  - connects to a network or runs software (for example the EU's Cyber Resilience Act): yes, Wi-Fi and Bluetooth LE on a hobby board, not sold <!-- REQUIRED:flag-network -->
  - children or food contact: no <!-- REQUIRED:flag-children -->
  - market: none, personal use in Czechia <!-- REQUIRED:flag-market -->
  - radio (unlicensed-device rules; read at their source when it decides): yes, the module's own certified radio, used as shipped <!-- REQUIRED:electronics-firmware:flag-radio -->
  - a Li-ion cell (charging, transport, battery rules): no, USB power <!-- REQUIRED:electronics-firmware:flag-li-ion -->
  - mains: no <!-- REQUIRED:electronics-firmware:flag-mains -->
  <!-- EXTEND:flags -->
- Extensions (each active id · the fact that activated it; when none matched, only "none matched: core only · the fact that decided it", naming no extension; list any directive skipped under rule 9): electronics-firmware · repo-has boards/*.json; spark-process · repo-has scrum/WORKING_AGREEMENTS.md <!-- REQUIRED:extensions -->
- The item (its issue, or the proposal in the decider's words) · what is still open elsewhere · the repository's push check, or "no push check here": P325 #417 with P326 #418, P327 #419, P328 #420 · open: PR #416 (P324) waits on the PO's merge, P323 parked as draft PR #414 · the push hook tools/pre-push runs the suite <!-- REQUIRED:spark-process:item -->
<!-- EXTEND:frame -->
- Depth: TRIO plus an AI-UX lens (the PO asked for PO/AI, UX and architects, 2026-10-19): PO assistant, user at the bench, Claude as operator, architect; one refuter (D2) <!-- REQUIRED:depth -->
  <!-- Cost, measured once: the P900 rehearsal's council took 6 agents, 499 calls and about 90M input tokens (2026-10-06). -->
- Search budget: no web search beyond one check per open fact; the repository and the three plans are the sources <!-- REQUIRED:budget -->
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
- Q0 · Is this frame right: the decision, the start and reach, the extensions and the depth? · decides: the frame · status: ⟨fill⟩ <!-- REQUIRED:q0 -->
- Q1 · How important is each assumption, and what pass line must the riskiest test meet? · decides: importance and pass lines · status: ⟨fill⟩ <!-- REQUIRED:q1 -->

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
