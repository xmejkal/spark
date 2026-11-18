<!-- Resume: invoke product-discovery again; `discovery.py check <this folder>` names the next step. -->
# P917, who holds a connected board: discovery brief

<!-- Readiness, its one home. collecting evidence: anything short of the two below. an experiment: the decider chose
a test (a D) before choosing an option. design: the decider confirmed the frame, the jobs and a direction, and accepted
the remaining risk (D rows). An extension may tighten these. Next: design, or a chosen test of kind spike or prototype
→ the design skill the facts name, with this file; otherwise none, and the collection plan says who runs it.
Stands on: the assumptions not retired in risks-and-tests.md; of which those the decider rated high, or — while any
is unrated. check computes both. -->
**Ready for:** collecting evidence <!-- REQUIRED:ready -->
**Stands on:** — H, — of which would change the decision (no assumption is listed yet) <!-- REQUIRED:debt -->
**Decision needed:** Q0, whether this frame is right <!-- REQUIRED:decision-needed -->

## Frame
- Request, verbatim (corrections marked), the PO, 2026-11-18, on the card (https://github.com/xmejkal/spark/issues/1298): "Oh, and that might actually also change something in the Spark store. Maybe that's an interesting functionality for us that would just help us out and might just be good to leave in Spark in general anyway afterwards." And: "Well, at least to see how it's in the projects. Maybe this session is working on one project, so it uses the connected board for that project to build that thing on it. Or the other session uses it for another, so it always has to build the other project." <!-- REQUIRED:request -->
- Decision · decider: whether spark keeps a record of who holds a connected board and until when, what a holder is, and which tools read the record · the PO <!-- REQUIRED:decision -->
- Outcome and how it is observed (a metric with unit and source, a proof command, or a log): proposed (H, the facilitator's): one command names, for a connected board, the project that uses it now and the project that was deployed to it last. A proof command with two project folders and one board shows both lines. The PO did not confirm this outcome yet. <!-- REQUIRED:outcome -->
- Already decided (D · who · when · where; include the product's stated non-goals and earlier decisions the request names): the discovery runs with the PO, and the agreement between the two sessions holds until it ends (D1). The kept board lives in the store and never in the project (D · the PO · 2026-11-17 · P865 #1231). Another board and no kept board stop the deploy, the grant, reach and live, and send to `look.py` (D · the PO · 2026-11-18 · #1266). Spark exports facts and never behaviour, and it uses free and local tools (D · the PO · AGENTS.md). The vision's non-goals: — (not read yet). <!-- REQUIRED:decided -->
- Open questions: the four on the card. Who is a holder: a session, a project or a person. Which tool writes a hold, which tools read it, and whether a tool stops on another holder's board or only says so. How a hold ends, and what a session that stopped with no release leaves behind. Whether the hold is its own record or a part of the grant. Added here: whether the record names what a holder owes at release (C10), and whether the game box serves a second project (the pixel-games session does not know). <!-- REQUIRED:open -->
- Scope · out of scope (proposed): in scope: one Mac, one store, boards on USB, every project on this Mac that touches a board, and the view the PO asked for first. A tool that is not spark's, for example `box.py` of pixel-games (★C6), can read the record through one spark command. Out of scope: a shared store between machines (P178), a change inside pixel-games' own tools, a lock on the serial port itself, and any change to P892's gate for one project with one board. <!-- REQUIRED:scope -->
- Start and reach (proposed until Q0): start existing product · decider reachable yes · users the PO, in this session, and the pixel-games session, by message · data and connectors: the store's `boards/` and `grants/` records and the card's comments are readable, and usage analytics are not connected · decider as a user n = 1 · must not get worse: one project with one kept board gets no new question, and `look.py` stays the first board step <!-- REQUIRED:start-reach -->
- Flags (yes · no · —; asked only when it changes a decision; never legal advice; any date or threshold is read at its source at run time and cited):
  - sold or given away, or personal use: given away (spark is public under MIT, AGENTS.md) <!-- REQUIRED:flag-sold -->
  - connects to a network or runs software (for example the EU's Cyber Resilience Act): runs software on one Mac, with no network use in this item <!-- REQUIRED:flag-network -->
  - children or food contact: no <!-- REQUIRED:flag-children -->
  - market: — <!-- REQUIRED:flag-market -->
  - radio (unlicensed-device rules; read at their source when it decides): no (the item changes no radio use) <!-- REQUIRED:electronics-firmware:flag-radio -->
  - a Li-ion cell (charging, transport, battery rules): no <!-- REQUIRED:electronics-firmware:flag-li-ion -->
  - mains: no <!-- REQUIRED:electronics-firmware:flag-mains -->
  <!-- EXTEND:flags -->
- Extensions (each active id · the fact that activated it; when none matched, only "none matched: core only · the fact that decided it", naming no extension; list any directive skipped under rule 9): electronics-firmware · repo-has boards/*.json; spark-process · repo-has scrum/WORKING_AGREEMENTS.md <!-- REQUIRED:extensions -->
- The item (its issue, or the proposal in the decider's words) · what is still open elsewhere · the repository's push check, or "no push check here": P917 (https://github.com/xmejkal/spark/issues/1298), in Discovery since 2026-11-18, under P365 #467 · open elsewhere: the discovery of P820 #1173 (collecting evidence) and Q11 of P867, and `tools/board.py status` reports 5 cards in flight against a limit of 4 (read 2026-11-18 15:59 CET) · the pre-push hook <!-- REQUIRED:spark-process:item -->
<!-- EXTEND:frame -->
- Depth: TRIO (default: PO assistant, user, tech lead) | FULL or LIGHT (who asked, when); add "no independent review" if subagents could not start: TRIO, proposed until Q0 <!-- REQUIRED:depth -->
  <!-- Cost, measured once: the P900 rehearsal's council took 6 agents, 499 calls and about 90M input tokens (2026-10-06). -->
- Search budget: two web searches, for how other tools record who holds a shared device and until when (proposed until Q0) <!-- REQUIRED:budget -->
- Appetite (the decider's, asked only when heading for design) | —: — <!-- REQUIRED:appetite -->

## What we found <!-- CLAIMS -->
<!-- One claim per line: `- [★C<n>] claim · E pointer | H source | D who date · caveat: qualifier | none`.
★ marks a claim that a decision, an option or the riskiest assumption rests on. A quote is verbatim, with its pointer.
Say what the evidence can support: an account (what happened to one person), data (how often, in its population and
period), a document (what was specified), the product (what exists, not whether anyone needs it), a benchmark (a
comparison). Model knowledge is H until a source is read. Elsewhere cite a ★ claim as ★C<n>, with its keep: words.
e.g. `- [★C2] 13 of 526 tickets ask for recurring tasks · E tickets.csv:2-14 · caveat: picked by Lena; shows that, not how often` -->
- [★C1] Two projects can keep the same board, and nothing compares their records · E `scripts/spark/bench/known_board.py` (`KnownBoardStore`, one file per project folder), read on main at 2c78c3c3, comment 2 on #1298 · caveat: read in the code, not run with a board
- [★C2] The store keeps each deploy per board with the project's folder name and the date · E `scripts/spark/records/deploy_record_store.py:100` and the three files in the PO's store `boards/`, read 2026-11-18 · caveat: the value is a folder name, so two folders with one name look the same
- [★C3] The PO's store holds no `known-boards/` folder, so no project keeps a board there yet · E `ls` of the store, 2026-11-18 15:59 CET · caveat: one store on one day
- [C4] No record in the PO's store names a deploy from the pixel-games project · E the three files in `boards/` (14, 1 and 17 deploys), all 32 read 2026-11-18: nine project names, none of them a pixel-games folder · caveat: a deploy that did not use `deploy.py` leaves no record
- [★C5] No record holds who uses a board now and until when, and the only such record is a comment on a card · E the body of #1298 and comment 2 · caveat: none
- [★C6] The pixel-games project touches the game box through its own `tools/box.py` (mpremote) and by hand, and no script of it calls spark's board tools · E account, the pixel-games session's message of 2026-11-18 about 16:10 CET, read by it from its files · caveat: not read again by this session
- [★C7] The spark plugin that the pixel-games project runs is 0.4.0, and it holds no `other_board` and no `no_known_board` stop · E account, the pixel-games session's message of 2026-11-18 about 16:10 CET, read by it from its files · caveat: a grep by that session, not read again here
- [C8] `box.py` takes the first USB serial port in sorted order, so with two boards on USB it can reach the wrong one and nothing asks · E account, the pixel-games session's message of 2026-11-18 about 16:10 CET, read by it from its files · caveat: read in its docstring, not run
- [★C9] Before a take that session could not read anywhere: who holds the board and until when, which board is on the port, which firmware and lineup (the list of games on the box) are on it, and whether the PO plays on it now · E account, the pixel-games session's message of 2026-11-18 about 16:10 CET, read by it from its files · caveat: one session, one day
- [C10] After P904's step 2c the box holds a test lineup, so a release owes the lineup that was there before the take · E account, the pixel-games session's message of 2026-11-18 about 16:10 CET, read by it from its files · caveat: an estimate before the step ran
- [C11] Step 2c expects one hold of 60 to 90 minutes with about 5 deploys and 5 to 10 console reads, each with a hard reset · E account, the pixel-games session's message of 2026-11-18 about 16:10 CET, read by it from its files · caveat: stated by that session as an estimate, not measured <!-- REQUIRED:findings -->

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
- Q0 · Is this frame right: the decision, the start and reach, the extensions and the depth? · decides: the frame · status: asked 2026-11-18 <!-- REQUIRED:q0 -->
- Q1 · How important is each assumption, and what pass line must the riskiest test meet? · decides: importance and pass lines · status: ⟨fill⟩ <!-- REQUIRED:q1 -->

## Decisions
<!-- D<n> · what · who · when · where recorded · options considered.
A yes covers only the actions and choices it names. A standing yes names its kind of action and its source.
Name what a D confirms in its words: the frame, the jobs, a direction, the remaining risk, a test, items.md. -->
- D1 · the discovery of P917 runs, with the PO, through this skill, and the sessions' agreement holds until it ends · the PO · 2026-11-18 · comment 3 on #1298 ("1 yes, all according yo your recommendations") · options considered: later, or no discovery
- D2 · the pixel-games session answers for its side, and the PO gets one question at a time · the PO · 2026-11-18 · this session's request · confirms: a message to that session, nothing else
- D (standing) · the discovery folder lands by PR · the PO · the extension spark-process, `process.md` · covers: the commits and the PR of this folder

## Found on the way <!-- CLAIMS -->
<!-- Outside this item's scope. Each is a separate proposal, never folded in. Same line format as What we found. -->
- ⟨fill⟩ | none <!-- REQUIRED:found -->

## Board actions <!-- REQUIRED:spark-process:board-actions -->
<!-- Each action on the board or the issue (stage, waiting flag, comment, filing): taken, with its D, or pending.
None is taken without a D. e.g. `- move #16 to Discovery · pending` -->
- move #1298 to Discovery · taken before this run, D1
- a message with four questions to the pixel-games session · taken 2026-11-18, D2
- set *Waiting on: the PO* on #1298 while Q0 waits · pending
- an issue comment that links this brief · pending
<!-- EXTEND:brief-sections -->

## Hand-off
<!-- Written only after the decider confirms the understanding (a D); copies only confirmed constraints. Holds: outcome ·
who · success and its proof · constraints (appetite, confirmed no-gos, rabbit holes) · what they said (D) against what
we assume (H) · links to the journeys and the map · riskiest assumptions and their tests · options considered. -->
⟨the hand-off | not yet: what is unconfirmed⟩ <!-- REQUIRED:handoff -->

## Files
[Jobs and journeys](jobs-and-journeys.md) · [Story map](story-map.md) · [Risks and tests](risks-and-tests.md) · [Verification](verification.md) · [Items](items.md) · council/
