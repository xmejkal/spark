<!-- Resume: invoke product-discovery again; `discovery.py check <this folder>` names the next step. -->
# P1038: the project page, designed (UX, graphic style, architecture, Artifact how-to): discovery brief

<!-- Readiness, its one home. collecting evidence: anything short of the two below. an experiment: the decider chose
a test (a D) before choosing an option. design: the decider confirmed the frame, the jobs and a direction, and accepted
the remaining risk (D rows). An extension may tighten these. Next: design, or a chosen test of kind spike or prototype
→ the design skill the facts name, with this file; otherwise none, and the collection plan says who runs it.
Stands on: the assumptions not retired in risks-and-tests.md; of which those the decider rated high, or — while any
is unrated. check computes both. -->
**Ready for:** collecting evidence (the frame is confirmed, D1; the lenses, options and the refuter are not run yet) <!-- REQUIRED:ready -->
**Stands on:** — H, — of which would change the decision (not yet counted: no assumption is written) <!-- REQUIRED:debt -->
**Decision needed:** After the lenses and the refuter: which direction the page design takes (a design for the architect, with the full council). <!-- REQUIRED:decision-needed -->

## Frame
- Request, verbatim (corrections marked): "lets analyze it and really design it both ux and graphic style and also architecture and claude artifact howto" (the PO, epaper session, 2026-11-23, after: "get back to where the page is and try to show this project on the page and continue working on it more, so we can make it work and be really UX perfect in graphic and later interactive part and can show all the steps and guide etc"). Later, the PO added a question and a decision: architecture options for human and AI interfaces (on P1038 and P1039), and the design skill anthropics/skills@frontend-design, to install at the page cards (open: user level, /spark:setup, or both). <!-- REQUIRED:request -->
- Decision · decider: the PO (xmejkal): what the project page shows and how it looks, how it is built, and how it is published, for the design step. <!-- REQUIRED:decision -->
- Outcome and how it is observed (a metric with unit and source, a proof command, or a log): A person who opens the page of a project sees where the project really stands, what to do next and the project's own facts, without asking Claude. Observed by: the page's state against the project's own records (flow.py page --json against the store's deploy record and the project's branches) on a walk, and the PO's reading of the page, n = 1. A metric and a pass line are not set (Q1). <!-- REQUIRED:outcome -->
- Already decided (D · who · when · where; include the product's stated non-goals and earlier decisions the request names): D · the PO · 2026-11-22 · P1011 #1470 body: the page 'is not very readable or intuitive or readable or good looking'; picks one at a time grey out the others. D · the PO · 2026-11-23 · P1038 comments: 'Now, in parallel' to this epic, and the design skill decision above. D · the PO · 2026-11-22/23 · P1031 finding: rich as an optional extra for the CLI text (a different interface of the same core). Earlier: the Artifact's click path is P829 #1187, in Build. <!-- REQUIRED:decided -->
- Open questions: What must the page show first, and for whom (the PO as the one user, n = 1, a future spark user)? Which graphic style? Does the page stay one Artifact file, or become a view of a state document that other hosts can show (P834)? Which Artifact capabilities does it need (files, sample, db, assets)? Which of the eight option families for human and AI interfaces (P1039 comment) does the page follow? Install of the design skill: where, and for whom. <!-- REQUIRED:open -->
- Scope · out of scope (confirmed D1): In: the page of a project (page.html, flow.py page), its content, layout, style, publish route and how Claude fills it, the how-to for building such an Artifact. Out (proposed): spark's CLI text (P1031), the click path (P829), the storage seams (P1033, P1036), the R&D epic's questions on other harnesses (P1039). <!-- REQUIRED:scope -->
- Start and reach (confirmed D1): start existing product (spark's page, built and published in the P934 walk) · decider reachable yes · users the PO only (n = 1), no other person reached · data and connectors: the Artifact server of claude.ai (read today: runtime contract 0.2.98, capabilities listed), the project's files and the store, GitHub through gh; Figma and design connectors: not connected, not asked · decider as a user n = 1 · must not get worse: the click path of P829, the privacy of the page (private Artifact, no secrets, no location data in its images) <!-- REQUIRED:start-reach -->
- Flags (yes · no · —; asked only when it changes a decision; never legal advice; any date or threshold is read at its source at run time and cited):
  - sold or given away, or personal use: personal use now; spark is public, so a page made for another person may leave this machine: not asked <!-- REQUIRED:flag-sold -->
  - connects to a network or runs software (for example the EU's Cyber Resilience Act): yes: the page is published to a server and its buttons write rows to a database; this is read-only discovery, nothing is published for it; no legal advice <!-- REQUIRED:flag-network -->
  - children or food contact: — <!-- REQUIRED:flag-children -->
  - market: — <!-- REQUIRED:flag-market -->
  <!-- EXTEND:flags -->
- Extensions (each active id · the fact that activated it; when none matched, only "none matched: core only · the fact that decided it", naming no extension; list any directive skipped under rule 9): spark-process · repo-has scrum/WORKING_AGREEMENTS.md <!-- REQUIRED:extensions -->
- The item (its issue, or the proposal in the decider's words) · what is still open elsewhere · the repository's push check, or "no push check here": P1038 #1521 (the page design epic, in Discovery) · open elsewhere: P829 in Build (the click path), P1022 in Ready, P1039 the R&D epic in Discovery; one discovery at a time (epics are exempt from the push gate) · the push check: spark's pre-push hook, run on the push <!-- REQUIRED:spark-process:item -->
<!-- EXTEND:frame -->
- Depth: TRIO (default: PO assistant, user, tech lead) | FULL or LIGHT (who asked, when); add "no independent review" if subagents could not start: TRIO (the default); no one asked for FULL or LIGHT <!-- REQUIRED:depth -->
  <!-- Cost, measured once: the P900 rehearsal's council took 6 agents, 499 calls and about 90M input tokens (2026-10-06). -->
- Search budget: about 15 searches or fetches and the files named here; the Artifact server read only; no create_from_type and no publishing for this discovery <!-- REQUIRED:budget -->
- Appetite (the decider's, asked only when heading for design) | —: — <!-- REQUIRED:appetite -->

## What we found <!-- CLAIMS -->
<!-- One claim per line: `- [★C<n>] claim · E pointer | H source | D who date · caveat: qualifier | none`.
★ marks a claim that a decision, an option or the riskiest assumption rests on. A quote is verbatim, with its pointer.
Say what the evidence can support: an account (what happened to one person), data (how often, in its population and
period), a document (what was specified), the product (what exists, not whether anyone needs it), a benchmark (a
comparison). Model knowledge is H until a source is read. Elsewhere cite a ★ claim as ★C<n>, with its keep: words.
e.g. `- [★C2] 13 of 526 tickets ask for recurring tasks · E tickets.csv:2-14 · caveat: picked by Lena; shows that, not how often` -->
- [★C1] The page shows a state that does not match the project: stands_at 'deploy', phases build 'could-not-run' and deploy 'not-started', and a NOW box that says to plug the board in and run the deploy · E `flow.py page --project . --json` in p934-display2, 2026-11-23 15:23 CET · caveat: the project's deploys (27 logs in sim/runs/board/, 18 'ready seen', 9 'ready unknown', counted from the files, 2026-11-23) were made by deploy.py outside the page's phases, so the page follows spark's chain, not the project's real work
- [C2] The page file is 714,020 bytes: 607,060 are two SVG data URIs, about 43.6 KB is the rest (text, style, two scripts of 22,130 bytes together) · E p934-display2/page.html, a byte count with `python3`, 2026-11-23 · caveat: none
- [C3] The page text holds the wiring, 12 breadboard steps, the parts' notes and the phase list; it holds nothing on the firmware, the deploys, the bench facts, the decisions or the battery · E p934-display2/page.html, its text read with `python3` and the markup removed, 2026-11-23 · caveat: read without the scripts' output
- [C4] No request waits on the page: its 5 requests (3 picks, requirements, build) all have an answer; the build answer says 'the board record names no wokwi_part_type', status could-not-run · E `db_query` on the artifact's requests and answers, 2026-11-23 · caveat: the page's own database only
- [★C5] The Artifact runtime is contract 0.2.98. Scripts load only from a short list of CDNs, remote images are blocked, fetch goes only to the artifact itself, alert and downloads are limited. A page may declare: artifact, assets, comments, db, dictation, downloads, files (a Claude Code project's files, only with a known project id), mcp, room, sample, tts, user · E the Artifact server's `guide` topic pages and `describe_capabilities`, read 2026-11-23 · caveat: what each capability costs or allows in detail is not read (describe_capabilities with a name is not called)
- [C6] The server has a Design artifact type for visual designs (create_from_type) · E `guide` with intent design, 2026-11-23 · caveat: not called, and its definition is not read
- [C7] Open spark cards on the page: P1011 #1470, P834 #1196, P887 #1257, P889 #1259, P992 #1445, P307 #373, P494 #674, with P829 #1187 in Build · E `gh issue list` and `gh issue view 1470`, 2026-11-23 · caveat: their bodies, except P1011's, are not read
- [C19] The page renders as a static, read-only file with no host: its script adds buttons only when `claude.use("db")` resolves and the viewer is the owner · E scripts/spark/flow/page_script.js:320-323, read 2026-11-23 · caveat: a static host is a separate question, see ★C16
- [C8] The design skill anthropics/skills@frontend-design has 1.2M installs and its repository about 199k stars, pushed 2026-11-16 · E `npx skills find` and `gh api repos/anthropics/skills`, 2026-11-23 · caveat: installs and stars show use, not fit
- [★C10] The deploy phase is fixed at "not started" and reads no file, and NOW goes to the first open phase, so every project past the firmware stands at deploy for ever · E scripts/spark/flow/phase_readers.py:554-560, scripts/spark/flow/guide.py:80-89, read 2026-11-23 (TECH-2, TECH-3, PO-1) · caveat: this is the first cause of ★C1; the second is that the published page is a copy that only /spark:page writes again (TECH-4)
- [C11] The page's stamp and fingerprint read only three files: needs.json, requirements.json and .spark/build.json; the walk's page says data-written 2026-11-22T11:44:33+01:00 beside a firmware line of 2026-11-23 14:18 · E scripts/spark/flow/fingerprint.py:18, write_flow_page.py:132-136, page.html, read 2026-11-23 (PO-3) · caveat: none
- [★C12] In the P934 walk the page was used for 11 minutes, 5 clicks between 11:25 and 11:36 CET on 2026-11-22; the later work (wiring, the deploys, firmware, battery) went through the chat and the terminal, and the project tracks its state in its own private GitHub issues (doing and next labels) and diary.md · E the walk's diary.md, `gh issue list` in p934-display2, 2026-11-23 (PO-5, PO-6) · caveat: n = 1; a page not named in the diary may still have been opened (QA1)
- [★C13] Most of what the page lacks (firmware behaviour, decisions, battery, bench facts) is in files and issues that spark holds as no record; of the missing facts only the deploy logs, the pin map and the parts' bench facts are spark's · E AGENTS.md:51 "Spark exports facts", the project's file list, diary rows 15 and 20 (PO-7, TECH-8) · caveat: the facilitator did not count which of these the PO wants first (QA2)
- [C14] The page offers Build to its owner on a wired board; since P1010 a rebuild moves EPD_RST to D11 and EPD_BUSY to MISO, while the wires stay on SDA and SCL · E page.html:450, spark commit a3a5ba50, firmware/pins.py:7-8 (USER-3) · caveat: the pin move is read from the commit's test, the build was not run; it did not happen
- [C15] The page loads nothing from the web (D7 of P820), and a test forbids "http" in it; the design skill asks for chosen typefaces and lists all-caps labels and middle dots as tells, which today's page uses · E tests/test_flow_page.py:87-88, the skill's SKILL.md through gh api, 2026-11-23 (TECH-22, TECH-29, TECH-30, PO-11) · caveat: fonts can be inlined as data: URIs, at a size cost
- [★C16] Privacy limits two routes: the files capability reads any project file unmasked (the walk project holds firmware/wifi_secrets.py), and GitHub Pages on a free plan serves only public repositories, so the drawer facts and other projects' names would go public; sim/runs/ is gitignored, so a page built from git cannot see the deploys · E `describe_capabilities` files, GitHub Docs read through search results 2026-11-23, p934-display2/.gitignore (TECH-20, TECH-21, PO-12, PO-14) · caveat: the GitHub pages were read as search summaries, not fetched; the PO's GitHub plan is —
- [C17] A db state doc that the page watches is the one documented way to change an open page without a republish; D10 of P820 keeps drawer facts out of db, and the parts lines carry drawer holds · E describe_capabilities db, P820 brief.md:183, read 2026-11-23 (TECH-18) · caveat: the db's size and rate limits for such a doc are not read
- [C18] For Claude, reading the page's state writes page.html (a tracked file in the project's git), and commands/page.md asks to read page.html whole before each republish, which a 714 KB page does not fit in one Read · E commands/page.md:24-34, :62, `git status` in p934-display2 (USER-11, USER-12) · caveat: the read-only `flow.py show` exists but page.md does not name it <!-- REQUIRED:findings -->

## Options <!-- CLAIMS -->
<!-- Two or three per open decision: decision · option · cost · what it would prove · opinion (whose), then the tag
and caveat cells. e.g. `- Q2 what first · fix delivery · two weeks · whether seen tasks get done · opinion (the facilitator's) · H ★C2 · caveat: none` -->
- Q2 what the page shows first · O2a spark's records and witnesses only, with the deploy reader fixed first (item 1), and one line that names what spark does not check · one core story and one page section · whether spark's own facts carry Job 1 · opinion (the PO assistant and the tech lead lean here; the facilitator's) · E ★C10 ★C13, council/tech-lead.md:17, council/po-assistant.md:54 · caveat: A2 may fail, then O2a shows little after the build
- Q2 what the page shows first · O2b O2a plus the project's own facts (goal and must lines, open issues, docs) read by new core readers and marked by their source · new readers, records grow by need · whether a page that mirrors the project's tracker gets opened · opinion (the user lens's order) · E ★C13, council/user.md:27 (USER-2) · caveat: facts spark does not hold go against "spark writes only what it derives from a record it holds", unless each is marked as the project's
- Q2 what the page shows first · O2c O2a plus one link out to the project's own tracker (its GitHub issues) · small · whether a link out is enough for "what next" · opinion (the facilitator's) · H · caveat: the link points to a private repository
- Q3 how the page stays true · O3a one file, restyled, written again at /spark:page as today, with a dated stamp over every file it reads · S to M · whether a snapshot with an honest age is enough · opinion (the facilitator's) · E C11 C19, scripts/spark/flow/fingerprint.py:18 · caveat: no push; ★C1's second cause stays
- Q3 how the page stays true · O3b the core writes one state value (.spark/state.json, the same data as `flow.py show --json`), Python renders the page from it, and the page is published as files so a republish sends the small state only · M · one state for the CLI, the page and an agent (family 3 of the card's eight), a cheaper republish · opinion (the tech lead's b1, the facilitator's) · E council/tech-lead.md:58, :92, :101 (TECH-9, TECH-15, TECH-16) · caveat: as fresh as the core's last write; whether an `<img>` of the artifact's own file loads is not read
- Q3 how the page stays true · O3c O3b plus a db state doc that an open page watches, with the drawer facts left out (D10 kept) · M to L · the PO's streaming rule on an open page · opinion (the tech lead's TECH-24) · E C17, council/tech-lead.md:114 · caveat: A8 not tested
- Set aside (considered, with reasons): a page that reads raw project files through the files capability (★C16, A4 unknown, a second core in JS: TECH-19); the page on a public static host (★C16); a JS renderer beside the Python one (W16, TECH-15) · E council/tech-lead.md:121, :136, :92 · caveat: none
- Q4 the graphic style · O4a system fonts, tokens planned once with the design skill's plan step, D7 kept · S · whether D7 can look good (A6) · opinion (the facilitator's) · E C15, council/tech-lead.md:208 · caveat: the skill's screenshot pass needs a browser tool
- Q4 the graphic style · O4b one font inlined as a data: URI, D7 kept · S, plus the font's size on every republish · whether a chosen face is worth its weight · opinion (none) · E council/tech-lead.md:148 (TECH-22) · caveat: the font's licence must allow it
- Q4 the graphic style · O4c lift D7 for fonts.googleapis.com, which the runtime allows · S, and the test changes · a web font · opinion (none) · E C15, tests/test_flow_page.py:87 · caveat: the page then loads from the web, and D7 is the PO's
- Q5 where the deploy reader fix lives · O5a its own story under P793 (item 1), before the page design's first slice · S · the core knows the deploys for the CLI too · opinion (the tech lead, PROC-1) · E ★C10, scripts/spark/flow/phase_readers.py:554 · caveat: none
- Q5 where the deploy reader fix lives · O5b inside P1038 as slice 0 · S · one epic holds the whole fix · opinion (none) · E ★C10, council/tech-lead.md:220 (PROC-1) · caveat: hides a core change in a page epic (PROC-1)
- Q6 the design skill's install · O6a user level (`npx skills add anthropics/skills@frontend-design -g -y`) · O6b a /spark:setup line for every spark user · O6c both · each copies text and runs nothing (TECH-29) · opinion (none yet) · E C8 C15, council/tech-lead.md:199 · caveat: the install itself is the PO's; it waits for him in every option
- Q7 Job 3 (show to others) in this epic · O7a later, on P834 #1196 · O7b now, as a shared Artifact without the drawer facts · opinion (the facilitator's: O7a) · H the CV memory · caveat: no account of a share exists (QA4) <!-- REQUIRED:options -->
- Proposed no-gos and rabbit holes (proposals until the decider confirms): no-gos: no new interface for the click path (P829); no change to spark's CLI text (P1031); no install of the design skill without the PO; no copy of the skill's text into spark (a vendor file); no route that reads raw project files or publishes to a public host; no logic in the page's script (P820); no offer that moves a wired board's pins without saying so. Rabbit holes: the chan_ project id of the files capability; the room capability; a second renderer in JS · H the facilitator's proposals, from council/tech-lead.md and council/po-assistant.md · caveat: proposals until the decider confirms <!-- REQUIRED:nogos -->

## Riskiest assumption and its test
- Riskiest: A1, the PO opens the page after the build once it shows the true stand; it is important and ★C12 stands against it (n = 1) · proposed — the facilitator's and the PO assistant's opinion, pending Q1. The earlier candidate (the files capability, A4) matters only if Q3 picks a live read of files, which no option does <!-- REQUIRED:riskiest -->
- Test · kind · pass line, dated before any result · proposed | D<n>: QA1 (an account question) now, then a use log in the next walk after the build · kind use log, n = 1 · pass line: he opens the page on his own at least once after the build, set 2026-11-23 · proposed — the facilitator's opinion, pending Q1 <!-- REQUIRED:test -->

## Questions
<!-- A queue; the first open question is asked alone. Each: Q<n> · question · decides: … · options · unblocks ·
opinion (whose) · kind: decision | account (a past-tense question about the decider's own use; the answer is E,
account, n = 1) · status: queued | asked <date> | answered D<n>.
If the decider cannot be asked, the queue stays here, and whatever rests on it stays H. -->
- Q0 · Is this frame right: the decision, the start and reach, the extensions and the depth? · decides: the frame · status: asked 2026-11-23, answered D1 <!-- REQUIRED:q0 -->
- Q1 · How important is each assumption, and what pass line must the riskiest test meet? · decides: importance and pass lines · status: queued (after the refuter; to the delegated council) <!-- REQUIRED:q1 -->
- Q2 · What does the page show first? · decides: the content boundary · options O2a, O2b, O2c · unblocks: the design's first slice · opinion (the facilitator's: O2a, then O2c) · kind: decision · status: queued
- Q3 · How does the page stay true? · decides: the architecture of the page · options O3a, O3b, O3c · unblocks: the architect's design · opinion (the facilitator's: O3b) · kind: decision · status: queued
- Q4 · Which graphic style route? · decides: fonts and D7 · options O4a, O4b, O4c · opinion (the facilitator's: O4a) · kind: decision · status: queued
- Q5 · Where does the deploy reader fix live? · decides: item 1's parent · options O5a, O5b · opinion (the facilitator's: O5a) · kind: decision · status: queued
- Q6 · Where is the design skill installed? · decides: the install route (the install waits for the PO) · options O6a, O6b, O6c · kind: decision · status: queued
- Q7 · Is Job 3 in this epic? · decides: the scope of sharing · options O7a, O7b · opinion (the facilitator's: O7a) · kind: decision · status: queued
- QA1 · The last time you came back to the e-paper clock, what did you open first to see where it stood? · decides: A1 · kind: account · status: queued for the PO (no council can answer it)
- QA2 · Name the five things you want to see first on this project's page. · decides: A2 and the desk check · kind: account · status: queued for the PO
- QA3 · The clock's goal line says "display clock and react on pressing the button", and its must lines say a quote every hour. Which describes the gadget today? · decides: the page's goal line · kind: account · status: queued for the PO
- QA4 · Did you ever show this page, or another spark page, to anyone? · decides: Job 3 · kind: account · status: queued for the PO
- QA5 · When the page said "Could not run" after the build, what did you take it to mean? · decides: how the top panel words a stale answer · kind: account · status: queued for the PO

## Decisions
<!-- D<n> · what · who · when · where recorded · options considered.
A yes covers only the actions and choices it names. A standing yes names its kind of action and its source.
Name what a D confirms in its words: the frame, the jobs, a direction, the remaining risk, a test, items.md. -->
- D1 · the frame confirmed as written: the decision, the start and reach (the PO as the one user, n = 1), the scope and what is out of it, the extension spark-process, depth TRIO · the PO · 2026-11-23, 16:15 CET · AskUserQuestion in the page-design session · options considered: as written; users wider (a future spark user); add the architecture choice for the human and AI interfaces; change it

## Found on the way <!-- CLAIMS -->
<!-- Outside this item's scope. Each is a separate proposal, never folded in. Same line format as What we found. -->
- The deep-sleep case of look.py's no_port sentence was sent to P1022 slice 3, not folded in here · D the epaper session, 2026-11-23 · caveat: none
- [C20] The deploy reader fix is a core change under P793 piece 6, not a page change · E #1105 comment 2026-11-23T14:17:14Z (TECH-7, PROC-1) · caveat: proposed as item 1
- [C21] The page's lines before power hold two contradictory BUSY lines, and breadboard.md disagrees with the page on the e-paper driver · E page.html:34, breadboard.md:104, :108 (USER-5) · caveat: read from the files, the panel was not tested
- [C22] The README's Bench row says no breadboard wired from a sheet ran yet; the P934 walk wired from spark's sheet and deployed with "ready seen" · E README.md, diary.md:209-215 (PO-29) · caveat: not checked against how the README defines "runs"; item 4
- [C23] P494 #674 asks a question that P820 D5 to D11 answered in effect, and P873 #1241 and P870 #1237 overlap this epic but were not in the brief's list · E `gh issue view` 674, 1241, 1237 (PO-16, PO-17) · caveat: their closing is the PO's <!-- REQUIRED:found -->

## Board actions <!-- REQUIRED:spark-process:board-actions -->
<!-- Each action on the board or the issue (stage, waiting flag, comment, filing): taken, with its D, or pending.
None is taken without a D. e.g. `- move #16 to Discovery · pending` -->
- P1038 is already in Discovery (spark-main, 2026-11-23) · taken by spark-main; nothing else is taken or pending from this folder
<!-- EXTEND:brief-sections -->

## Hand-off
<!-- Written only after the decider confirms the understanding (a D); copies only confirmed constraints. Holds: outcome ·
who · success and its proof · constraints (appetite, confirmed no-gos, rabbit holes) · what they said (D) against what
we assume (H) · links to the journeys and the map · riskiest assumptions and their tests · options considered. -->
not yet: the frame is unconfirmed (Q0), and the jobs, the lenses and the refuter are not run <!-- REQUIRED:handoff -->

## Files
[Jobs and journeys](jobs-and-journeys.md) · [Story map](story-map.md) · [Risks and tests](risks-and-tests.md) · [Verification](verification.md) · [Items](items.md) · council/
