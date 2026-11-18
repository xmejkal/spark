<!-- Resume: invoke product-discovery again; `discovery.py check <this folder>` names the next step. -->
# P917, who holds a connected board: discovery brief

<!-- Readiness, its one home. collecting evidence: anything short of the two below. an experiment: the decider chose
a test (a D) before choosing an option. design: the decider confirmed the frame, the jobs and a direction, and accepted
the remaining risk (D rows). An extension may tighten these. Next: design, or a chosen test of kind spike or prototype
→ the design skill the facts name, with this file; otherwise none, and the collection plan says who runs it.
Stands on: the assumptions not retired in risks-and-tests.md; of which those the decider rated high, or — while any
is unrated. check computes both. -->
**Ready for:** collecting evidence <!-- REQUIRED:ready -->
**Stands on:** 5 H, 2 of which would change the decision (A1 and A6, rated high in D5) <!-- REQUIRED:debt -->
**Decision needed:** the PO's yes to the list in items.md. Its third item is the card in pixel-games that A6's pass line names <!-- REQUIRED:decision-needed -->

## Frame
- Request, verbatim (corrections marked), the PO, 2026-11-18, on the card (https://github.com/xmejkal/spark/issues/1298): "Oh, and that might actually also change something in the Spark store. Maybe that's an interesting functionality for us that would just help us out and might just be good to leave in Spark in general anyway afterwards." And: "Well, at least to see how it's in the projects. Maybe this session is working on one project, so it uses the connected board for that project to build that thing on it. Or the other session uses it for another, so it always has to build the other project." <!-- REQUIRED:request -->
- Decision · decider: whether spark keeps a record of who holds a connected board and until when, what a holder is, and which tools read the record · the PO <!-- REQUIRED:decision -->
- Outcome and how it is observed (a metric with unit and source, a proof command, or a log): proposed (H, the facilitator's): one command names, for a connected board, the project that uses it now and the project that was deployed to it last. A proof command with two project folders and one board shows both lines. The PO did not confirm this outcome yet. <!-- REQUIRED:outcome -->
- Already decided (D · who · when · where; include the product's stated non-goals and earlier decisions the request names): the discovery runs with the PO, and the agreement between the two sessions holds until it ends (D1). The kept board lives in the store and never in the project (D · the PO · 2026-11-17 · P865 #1231). Another board and no kept board stop the deploy, the grant, reach and live, and send to `look.py` (D · the PO · 2026-11-18 · #1266). Spark exports facts and never behaviour, and it uses free and local tools (D · the PO · AGENTS.md). The vision's non-goals: — (not read yet). <!-- REQUIRED:decided -->
- Open questions: the four on the card. Who is a holder: a session, a project or a person. Which tool writes a hold, which tools read it, and whether a tool stops on another holder's board or only says so. How a hold ends, and what a session that stopped with no release leaves behind. Whether the hold is its own record or a part of the grant. Added here: whether the record names what a holder owes at release (C10), and whether the game box serves a second project (the pixel-games session does not know). <!-- REQUIRED:open -->
- Scope · out of scope (proposed): in scope: one Mac, one store, boards on USB, every project on this Mac that touches a board, and the view the PO asked for first. A tool that is not spark's, for example `box.py` of pixel-games (★C6 (read in box.py only)), can read the record through one spark command. Out of scope: a shared store between machines (P178), a change inside pixel-games' own tools, a lock on the serial port itself, and any change to P892's gate for one project with one board. <!-- REQUIRED:scope -->
- Start and reach (D3): start existing product · decider reachable yes · users the PO, in this session, and the pixel-games session, by message · data and connectors: the store's `boards/` and `grants/` records and the card's comments are readable, and usage analytics are not connected · decider as a user n = 1 · must not get worse: one project with one kept board gets no new question, and `look.py` stays the first board step <!-- REQUIRED:start-reach -->
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
- Depth: TRIO (default: PO assistant, user, tech lead) | FULL or LIGHT (who asked, when); add "no independent review" if subagents could not start: TRIO, three agents on Sonnet (D3) <!-- REQUIRED:depth -->
  <!-- Cost, measured once: the P900 rehearsal's council took 6 agents, 499 calls and about 90M input tokens (2026-10-06). -->
- Search budget: two web searches, for how other tools record who holds a shared device and until when (D3) <!-- REQUIRED:budget -->
- Appetite (the decider's, asked only when heading for design) | —: — <!-- REQUIRED:appetite -->

## What we found <!-- CLAIMS -->
<!-- One claim per line: `- [★C<n>] claim · E pointer | H source | D who date · caveat: qualifier | none`.
★ marks a claim that a decision, an option or the riskiest assumption rests on. A quote is verbatim, with its pointer.
Say what the evidence can support: an account (what happened to one person), data (how often, in its population and
period), a document (what was specified), the product (what exists, not whether anyone needs it), a benchmark (a
comparison). Model knowledge is H until a source is read. Elsewhere cite a ★ claim as ★C<n>, with its keep: words.
e.g. `- [★C2 (a folder name)] 13 of 526 tickets ask for recurring tasks · E tickets.csv:2-14 · caveat: picked by Lena; shows that, not how often` -->
- [★C1] Two projects can keep the same board, and nothing compares their records · E `scripts/spark/bench/known_board.py` (`KnownBoardStore`, one file per project folder), read on main at 2c78c3c3, comment 2 on #1298 · caveat: read in the code, not run with a board
- [★C2] The store keeps each deploy per board with the project's folder name and the date · E `scripts/spark/records/deploy_record_store.py:100` and the three files in the PO's store `boards/`, read 2026-11-18 · caveat: the value is a folder name, so two folders with one name look the same
- [★C3] The PO's store holds no `known-boards/` folder, so no project keeps a board there yet · E `ls` of the store, 2026-11-18 15:59 CET · caveat: one store on one day
- [C4] No record in the PO's store names a deploy from the pixel-games project · E the three files in `boards/` (14, 1 and 17 deploys), all 32 read 2026-11-18: nine project names, none of them a pixel-games folder · caveat: a deploy that did not use `deploy.py` leaves no record
- [★C5] No record holds which project or session uses a board now. A grant holds the person's yes and its end, and the agreed comment on a card is the intended record · E #1298, its body and comment 2 · caveat: the agreed comment was not used so far (C20)
- [★C6] The pixel-games project touches the game box through its own `tools/box.py` (mpremote) and by hand, and no script of it calls spark's board tools · E account, pixel-games-account.md:10, the pixel-games session's message of 2026-11-18, read by it from its files · caveat: not read again by this session. Keep: read in box.py only
- [★C7] The one spark plugin installed on this Mac is 0.4.0 of 2026-09-23, and it holds four design skills and no board script · E account, pixel-games-account.md:17, and council/refuter.md:24 · caveat: an upgrade alone does not put `box.py` behind P892's gate, because pixel-games calls no spark board script (★C6 (read in box.py only)). Keep: an upgrade alone brings no gate
- [C8] `box.py` takes the first USB serial port in sorted order, so with two boards on USB it can reach the wrong one and nothing asks · E account, pixel-games-account.md:14, the pixel-games session's message of 2026-11-18, read by it from its files · caveat: read in its docstring, not run
- [★C9] Before a take that session could not read anywhere: who holds the board and until when, which board is on the port, which firmware and lineup (the list of games on the box) are on it, and whether the PO plays on it now · E account, pixel-games-account.md:22, the pixel-games session's message of 2026-11-18, read by it from its files · caveat: one session, one day. That session did not know where to read it. The board on the port is readable with no touch (★C24 (only the PO knows whether it is the game box)). Keep: one session on one day
- [C10] After P904's step 2c the box holds a test lineup, so a release owes the lineup that was there before the take · E account, pixel-games-account.md:20, the pixel-games session's message of 2026-11-18, read by it from its files · caveat: an estimate before the step ran
- [C11] Step 2c expects one hold of 60 to 90 minutes with about 5 deploys and 5 to 10 console reads, each with a hard reset · E account, pixel-games-account.md:19, the pixel-games session's message of 2026-11-18, read by it from its files · caveat: stated by that session as an estimate, not measured
- [★C12] With no touch, spark knows a board only by the USB serial that `mpremote devs` lists, and the MAC needs a read that restarts the board · E council/tech-lead.md:11 (FEAS-1 to FEAS-3) · caveat: a serial that a firmware set, a shared one or a missing one gives "cannot tell". Keep: some serials give cannot tell
- [★C13] A grant stores its end time with a zone, the check reads the end at read time, and an ended grant stays as a file · E council/tech-lead.md:16 (FEAS-6) and council/user.md:50 (USER-10) · caveat: one ended grant seen in one store. Keep: one ended grant in one store
- [★C14] No board tool of spark reads a session, and a grant's `granted_by` is the person's user name. `CLAUDE_CODE_SESSION_ID` is set in a child process of Claude Code · E council/tech-lead.md:15 (FEAS-5) and council/refuter.md:28 · caveat: nobody checked whether two sessions get different ids, or whether an id stays after a clear. Keep: session ids not compared
- [★C15] The look, the grant's read and the deploy restart the board, reach stops the firmware, and `mpremote devs` opens no port · E council/tech-lead.md:38 (PHYS-2 to PHYS-4) and council/refuter.md:29 · caveat: read in the code, not measured at a bench. Live was not read again
- [C16] `box.py log` opens the port with no exclusive flag, so the system's port lock cannot enforce a hold against it · E council/tech-lead.md:37 (PHYS-1) and council/tech-lead.md:46 (PHYS-5) · caveat: read by the lens in the pixel-games worktree
- [★C17] Nobody is blocked today, and the one named need is the hold of step 2c of P904 · E council/po-assistant.md:24 (RISK-2) · caveat: the lens's reading. The agreement was never used, and the bench check of P892 waits on the PO. Keep: the agreement was never used
- [C18] The word "hold" already names the drawer's reservation of a unit (P466 #634) · E council/po-assistant.md:30 (RISK-8) · caveat: none
- [C19] P519 #715 is open: the deploy grant names no project and no count, and the card asks for both · E `gh issue view 715`, 2026-11-18 · caveat: none
- [C20] No take line is on #1283 or #1298, so the agreed lines were not used yet · E council/user.md:46 (USER-6) · caveat: read once on 2026-11-18
- [★C24] One board record in the store, a FireBeetle 2 ESP32-S3, holds 14 deploys from five project names between 2026-11-01 and 2026-11-17, and a board whose USB serial starts with that MAC is on USB now · E `system_profiler SPUSBDataType` and the store's `boards/34-85-18-xx-xx-xx.json`, 2026-11-18, found by council/refuter.md:39 · caveat: only the PO knows whether it is the game box. The five names can be one lane's walks
- [C25] `box.py` can call one spark command by subprocess, and today nothing tells it where that command is. It can report the project (the origin remote and the commit), the lineup and the date. It cannot report the port or the USB serial without a change · E account, pixel-games-account.md:34, the pixel-games session's message of 2026-11-18 · caveat: read by that session in its files, not run. The card in pixel-games does not exist <!-- REQUIRED:findings -->

## Options <!-- CLAIMS -->
<!-- Two or three per open decision: decision · option · cost · what it would prove · opinion (whose), then the tag
and caveat cells. e.g. `- Q2 what first · fix delivery · two weeks · whether seen tasks get done · opinion (the facilitator's) · H ★C2 (a folder name) · caveat: none` -->
- Q3 what first · the view alone, from the records that exist, with no new record · one small card · whether existing records answer J1 · opinion (the tech lead's, DIR-4): first · E ★C12 (some serials give cannot tell), council/tech-lead.md:29 · caveat: it shows nothing for the game box today (★C3 (one store on one day), C4)
- Q3 what first · the view, and a registered tool reports its deploys and its use · one card in spark and one change in pixel-games · whether the view then names the game box's project · opinion (the facilitator's): this is the first cut that serves the first real use · H D4 · caveat: "register" is the facilitator's reading
- Q3 what first · the view and a record of the holder with a take and a release · two or three cards · whether tools read a record before a touch (A1) · opinion (the PO assistant's, RISK-3): only after the no-code test · H · caveat: none
- Q4 who is a holder · a project, by its resolved folder · reuses the kept board's key · — · opinion (the facilitator's): this one, from the PO's words in comment 1 · E ★C1 (not run with a board), ★C14 (session ids not compared), council/tech-lead.md:15 · caveat: two sessions in one project look the same, and pixel-games uses one worktree per card, so one project becomes many holders (council/refuter.md:45)
- Q4 who is a holder · a project, by a name that it registers · a name per project in the store, as `projects.json` keeps today · whether worktrees of one project share a holder · opinion (the refuter's rival, taken up by the facilitator): fits pixel-games' worktrees · H council/refuter.md:58 · caveat: names can collide (C22)
- Q4 who is a holder · a label that the caller types (a session's name) · a new field that nothing can prove · — · opinion (the tech lead's): not a key, perhaps a note · E ★C14 (session ids not compared), council/tech-lead.md:15 · caveat: none
- Q5 on another holder's board · the tool only says so · no change to P892's gate · whether a line is enough · opinion (the PO assistant's, RISK-10): fits "facts, never behaviour" · H · caveat: none
- Q5 on another holder's board · the tool asks, as P892's gate asks · one more code in `KnownBoardService.judge` · whether a question stops a wrong touch · opinion (the tech lead's, FEAS-8): possible there · H · caveat: a tool that is not spark's does not pass this gate (★C6 (read in box.py only))
- Q6 how a hold ends · at its stated time, as a grant does · reuses the grant's model · whether an estimate of 60 to 90 minutes holds · opinion (the tech lead's, FEAS-11): the end time is the whole cost of a dead session · E ★C13 (one ended grant in one store), council/tech-lead.md:21 · caveat: C11 is an estimate
- Q6 how a hold ends · at a release, with the end time as a limit only · a release command · — · opinion: — · H · caveat: a session that stops leaves the record until the limit <!-- REQUIRED:options -->
- Proposed no-gos and rabbit holes (proposals until the decider confirms): no lock on the serial port itself (C16). No session as the key of a record until someone checks whether its id differs between sessions (★C14 (session ids not compared)). No change inside pixel-games' tools by a spark card. No deletion of an ended record. Rabbit hole: a board that spark cannot tell with no touch (★C12 (some serials give cannot tell)). · H the facilitator's proposals · caveat: none of them is confirmed <!-- REQUIRED:nogos -->

## Riskiest assumption and its test
- Riskiest: A6, the pixel-games tool will call a spark command. Every slice after slice 0 that serves the game box needs it, and no evidence exists · proposed — the refuter's opinion, taken up by the facilitator, and rated high by the PO (D5). The PO assistant names A1, also high (D5). A2 is not the riskiest: its evidence already says no (★C3 (one store on one day), C4) <!-- REQUIRED:riskiest -->
- Test · kind · pass line, dated before any result · proposed | D<n>: for A6, a question to the pixel-games session and the PO: can `box.py` call one spark command with `--json` before a touch, and who owns that change · an account · pass line proposed 2026-11-18: a yes that names the command and the card in pixel-games · D5. For A1, a use log of step 2c on #1283: every take and every release has its line (D5) <!-- REQUIRED:test -->

## Questions
<!-- A queue; the first open question is asked alone. Each: Q<n> · question · decides: … · options · unblocks ·
opinion (whose) · kind: decision | account (a past-tense question about the decider's own use; the answer is E,
account, n = 1) · status: queued | asked <date> | answered D<n>.
If the decider cannot be asked, the queue stays here, and whatever rests on it stays H. -->
- Q0 · Is this frame right: the decision, the start and reach, the extensions and the depth? · decides: the frame · status: answered D3 <!-- REQUIRED:q0 -->
- Q1 · How important is each assumption, and what pass line must the riskiest test meet? · decides: importance and pass lines · status: answered D5
- Q2 · Is the FireBeetle 2 that is on USB now the game box, and did both the walks of spark and pixel-games put firmware on it? · decides: whether A5 holds with a dated case (★C24 (only the PO knows whether it is the game box)) · kind: account · status: answered D6
- Q3 · What comes first: the view alone, the view with a registered tool's reports, or the view with a holder record? · decides: the first slice · options: the three in Options · opinion (the facilitator's): the second · kind: decision · status: answered D8
- Q4 · Is a holder a project? · decides: the record's key · options: a project, a typed label · opinion (the facilitator's): a project · kind: decision · status: answered D9
- Q5 · On another holder's board, does a spark tool only say so, or ask? · decides: whether P892's gate changes · opinion (the PO assistant's): only say so · kind: decision · status: deferred with the holder record (D8)
- Q6 · What did "tools that register" mean in D4: a tool that makes itself known to the store, a project listed in `projects.json`, or a tool reached through spark's MCP interface? And does "use" mean the board or the record? · decides: what D4 confirms · kind: decision · status: answered D7
- Q7 · Which word names the record, given that "hold" is the drawer's word (C18)? · decides: the names · kind: decision · status: deferred with the holder record (D8) <!-- REQUIRED:q1 -->

## Decisions
<!-- D<n> · what · who · when · where recorded · options considered.
A yes covers only the actions and choices it names. A standing yes names its kind of action and its source.
Name what a D confirms in its words: the frame, the jobs, a direction, the remaining risk, a test, items.md. -->
- D1 · the discovery of P917 runs, with the PO, through this skill, and the sessions' agreement holds until it ends · the PO · 2026-11-18 · comment 3 on #1298 ("1 yes, all according yo your recommendations") · options considered: later, or no discovery
- D2 · the pixel-games session answers for its side, and the PO gets one question at a time · the PO · 2026-11-18 · this session's request · confirms: a message to that session, nothing else
- D3 · the frame is right as proposed: the decision, the start and reach, the scope with tools that are not spark's as readers, both extensions, TRIO and two searches · the PO · 2026-11-18 · this session, his answer to Q0 ("Yes, as proposed") · options considered: one light lens, only spark's own tools, the view only
- D4 · the record is mostly spark's own, and a tool that registers can read it, use it and share the board too · the PO · 2026-11-18 · this session, verbatim: "mostly just spark, but tools that register can access and use it and share too" · confirms: a direction for the scope. The reply before it listed four waiting items, and which one he answered is not recorded. The facilitator's reading (H): "register" means that a tool that is not spark's makes itself known to the store first, and "use" means that it can take a hold, not only read one. The refuter names two other readings (council/refuter.md:58), so Q6 asks him.
- D5 · the ratings and the pass lines: A6, A1 and A5 are high, and A2, A3 and A4 are low. A6 passes with a yes that names the command and a card in pixel-games. A1 passes when every take and every release of step 2c has its line on #1283 · the PO · 2026-11-18 · this session, his answer to Q1 ("Yes, as proposed") · options considered: only A6 high, A1 the highest, the facilitator rates them
- D6 · the FireBeetle 2 ESP32-S3 on USB (MAC 34:85:18:xx:xx:xx) is the game box that pixel-games uses · the PO · 2026-11-18 · this session, his answer to Q2 ("Yes, the same board") · an account (E, n = 1), not a decision. With ★C24 (only the PO knows whether it is the game box: he says yes) it means that spark's walks and pixel-games put firmware on one board by turns
- D7 · a tool that is not spark's registers when it tells the store about itself: the tool, or its project, is written once into the store as a known tool. After that it can read who uses a board, write its own use and its deploys, and so share the board with spark's projects · the PO · 2026-11-18 · this session, his answer to Q6 ("It tells the store about itself"), with `box.py` as the example · confirms: the meaning of "register" and "use" in D4 · options considered: a project listed in `projects.json`, a tool reached through spark's MCP interface, the board and not a record
- D8 · a direction: first the view (one command lists each board on USB with its projects, last deploy and grants, and opens no port) together with a registered tool that reports its deploys, so that the view is true for the game box. No holder record yet · the PO · 2026-11-18 · this session, his answer to Q3 ("View plus a registered tool") · confirms: a direction · options considered: the view alone, the view plus a holder record, nothing before step 2c
- D9 · the view names a project by a name that the tool registers: one name, for example pixel-games, and every worktree reports under it. The registration refuses a name that is taken · the PO · 2026-11-18 · this session, his answer to Q4 ("A name the tool registers") · confirms: the project's key in the first slice · options considered: the folder as today, both the name and the folder
- D10 · the jobs J1 to J4 and the understanding are right: the first slice is the view and a registered tool, a holder record and the jobs J3 and J4 are not now, and the design starts after A6's answer · the PO · 2026-11-18 · this session, his answer to the closing question ("Right; design after A6's answer") · confirms: the jobs and the understanding · options considered: design now with the risk accepted, the view only first, something is wrong
- D (standing) · the discovery folder lands by PR · the PO · the extension spark-process, `process.md` · covers: the commits and the PR of this folder

## Found on the way <!-- CLAIMS -->
<!-- Outside this item's scope. Each is a separate proposal, never folded in. Same line format as What we found. -->
- [C21] `box.py` of pixel-games takes the first USB serial port in sorted order (C8). A card for it belongs to pixel-games · E pixel-games-account.md:14 · caveat: not run
- [C22] The deploy record keeps a project's folder name, so names such as `bench` and `walk4` can collide between folders · E council/tech-lead.md:14 (FEAS-4) · caveat: none
- [C23] The store's lock file is in the temp folder, so two processes with a different `TMPDIR` perhaps do not share it · H council/tech-lead.md FEAS-12, not checked · caveat: not checked <!-- REQUIRED:found -->

## Board actions <!-- REQUIRED:spark-process:board-actions -->
<!-- Each action on the board or the issue (stage, waiting flag, comment, filing): taken, with its D, or pending.
None is taken without a D. e.g. `- move #16 to Discovery · pending` -->
- move #1298 to Discovery · taken before this run, D1
- a message with four questions to the pixel-games session · taken 2026-11-18, D2
- set *Waiting on: the PO* on #1298 while Q0 waits · pending
- an issue comment that links this brief · pending
- the PO's words of D4 as a comment on #1298 · pending
- a message to the pixel-games session with the question of A6 · taken 2026-11-18, D2
<!-- EXTEND:brief-sections -->

## Hand-off
<!-- Written only after the decider confirms the understanding (a D); copies only confirmed constraints. Holds: outcome ·
who · success and its proof · constraints (appetite, confirmed no-gos, rabbit holes) · what they said (D) against what
we assume (H) · links to the journeys and the map · riskiest assumptions and their tests · options considered. -->
Confirmed by the PO in D10. The remaining risk is not accepted yet, so the brief is not ready for design.

- Outcome: for a connected board, one command names the projects that use it and the last deploy, and opens no port (D8).
- Who: the PO at his bench, and a Claude session that works on one project (jobs J1 and J2, D10).
- Success and its proof: after `box.py deploy`, the view names pixel-games for the game box. A test proves that the view opens no port.
- Constraints: a tool registers by telling the store about itself (D7). A project is named by the name that its tool registers, and a taken name is refused (D9). No holder record, no take and no release in this slice (D8). One project with one kept board gets no new question (D3).
- What they said (D) against what we assume (H): D3 to D10 above. Assumed: a tool reads the store before a touch (A1, tested at step 2c). `box.py` finds the command through one stable path (A6, C25).
- For the design to settle: where the command lives so that a tool outside spark finds it, or whether a documented file in the store replaces the command (C25). The pixel-games session names the origin remote as the project's name.
- Journeys and map: [jobs-and-journeys.md](jobs-and-journeys.md), [story-map.md](story-map.md), slices 0 and 1.
- Riskiest assumptions and their tests: A6, a yes with the command (met) and a card in pixel-games (missing). A1, every take and release of step 2c has its line on #1283 (not run yet).
- Options considered: the view alone, the view with a holder record, nothing before step 2c (D8). <!-- REQUIRED:handoff -->

## Files
[Jobs and journeys](jobs-and-journeys.md) · [Story map](story-map.md) · [Risks and tests](risks-and-tests.md) · [Verification](verification.md) · [Items](items.md) · council/
