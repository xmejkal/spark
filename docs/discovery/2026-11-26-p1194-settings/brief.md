<!-- Resume: invoke product-discovery again; `discovery.py check <this folder>` names the next step. -->
# P1194 settings in layers: discovery brief

<!-- Readiness, its one home. collecting evidence: anything short of the two below. an experiment: the decider chose
a test (a D) before choosing an option. design: the decider confirmed the frame, the jobs and a direction, and accepted
the remaining risk (D rows). An extension may tighten these. Next: design, or a chosen test of kind spike or prototype
→ the design skill the facts name, with this file; otherwise none, and the collection plan says who runs it.
Stands on: the assumptions not retired in risks-and-tests.md; of which those the decider rated high, or — while any
is unrated. check computes both. -->
**Ready for:** collecting evidence <!-- REQUIRED:ready -->
**Stands on:** 8 H, — of which would change the decision (unrated until Q1) <!-- REQUIRED:debt -->
**Decision needed:** Q1, the importance of A1 to A8 and the pass line of the riskiest test; then Q2 to Q11 settle the model <!-- REQUIRED:decision-needed -->

## Frame
- Request, verbatim (corrections marked): the PO, 2026-11-26, answering P1193 #1738's P2, on #1740: "git identity, but configurable and asks until configured (like the other configs for it) for new projects, spark should have a settings /config feature per multiple layer like global/per project/per account logged in etc. for now just remember it for all configurable streategies and things like this, create a card for it, we will move the config there and also tell all new features to keep that in mind, we will also make the ui for it later, or you can already start the epic of config and analyze etc and create the ux/ui. I think some general settings and some per user settings, per project, maybe by per other thing, to be refined". And on 2026-11-26 in spark-artifact's question dialog, his choice "Settings page (Recommended)" for the next piece of the page design. <!-- REQUIRED:request -->
- Decision · decider: which settings model (its layers, how a value is found, who may change it) and which settings page spark builds after the MVP, and which existing settings move in first · the PO <!-- REQUIRED:decision -->
- Outcome and how it is observed (a metric with unit and source, a proof command, or a log): proposed: a person sees each spark choice in one place with its value, its default and the layer that set it, and changes it with one sentence to Claude or one step on the page. Observed by a walk: the PO finds and changes 3 named settings (the firmware check of P410, the vendor order of P368, the commit author of P1193) without opening a file. A later proof command lists every setting with its layer as JSON. <!-- REQUIRED:outcome -->
- Already decided (D · who · when · where; include the product's stated non-goals and earlier decisions the request names): D1 · the PO · 2026-11-26 · #1740: layers (global, per project, per account, more to refine), a default each, a setting with no value asks until set, existing choices move there, the page now or later. D2 · the PO · 2026-11-26 · P1193 #1738 P1 and P4: what leaves the store on a share is "None of these by default, but configurable", and what syncs to the public is a setting. D3 · the PO · 2026-11-26 · memory settings-layers-rule: every new plan names its setting, default and layer. D4 · the PO · 2026-11-26 · spark-artifact's dialog: start this discovery and the page design now. D5 · the PO · 2026-11-26 · Q0 in spark-artifact's dialog: the frame holds, and the account layer is designed now, not left as an open question. Non-goal W14 (scrum/VISION.md, Not goals): nothing designed on paper before a design needs it; D1 and D4 are his yes to design now. Standing page rule (councils/p1113, the architect's answer, taken by the PO 2026-11-25): the page shows what spark holds, a change goes as an offer (a sentence to Claude or a page request), and the page never changes a record by itself. <!-- REQUIRED:decided -->
- Open questions: which layers, and is "global" the same as the person's store on one machine; what "per account logged in" means for spark; does the page change a value itself or hand Claude a sentence; where a project's settings live (beside .spark/tools.json or inside it); which values never show (the Wokwi token); a project's file can name install commands, so how far a project layer is trusted <!-- REQUIRED:open -->
- Scope · out of scope (proposed): in: the settings model (names, layers, defaults, who set a value), today's inventory, the page's UX and UI on the design canvas, how Claude reads and changes a setting, the order in which today's settings move. also in (D5, narrowed by D6): the account layer as a seam the architecture leaves room for, what an account would hold, and where managing it would sit on the page; the sign-in itself, accounts and account management are a later version. out: building the seam (cards after the PO's yes), syncing settings to a central repository (P1193), building a sign-in, an MCP server, any setting a feature has not asked for yet ("records grow by need") <!-- REQUIRED:scope -->
- Start and reach (confirmed D5): start existing product · decider reachable yes · users: the PO as the maker (n = 1); the hobbyist persona is H (scrum/VISION.md: no outside person has installed spark); the agent at the keyboard as a constraint · data and connectors: the code, the store and GitHub issues (read with gh); no usage data and no user tickets exist · decider as a user n = 1 · must not get worse: /spark:setup and the tools list's three layers (records/tool_finder.py:92), the tools.py commands (which have no --json answer today: scripts/tools.py --help, read 2026-11-26, corrected after USER-6), the store's place (records/store.py:59-65) <!-- REQUIRED:start-reach -->
- Flags (yes · no · —; asked only when it changes a decision; never legal advice; any date or threshold is read at its source at run time and cited):
  - sold or given away, or personal use: given away: spark is public under MIT (AGENTS.md) <!-- REQUIRED:flag-sold -->
  - connects to a network or runs software (for example the EU's Cyber Resilience Act): yes, it runs software; a setting can name a token, so a secret is never shown or written to a shared file <!-- REQUIRED:flag-network -->
  - children or food contact: no <!-- REQUIRED:flag-children -->
  - market: — <!-- REQUIRED:flag-market -->
  - radio (unlicensed-device rules; read at their source when it decides): no, this item holds no hardware <!-- REQUIRED:electronics-firmware:flag-radio -->
  - a Li-ion cell (charging, transport, battery rules): no <!-- REQUIRED:electronics-firmware:flag-li-ion -->
  - mains: no <!-- REQUIRED:electronics-firmware:flag-mains -->
  <!-- EXTEND:flags -->
- Extensions (each active id · the fact that activated it; when none matched, only "none matched: core only · the fact that decided it", naming no extension; list any directive skipped under rule 9): spark-process · repo-has scrum/WORKING_AGREEMENTS.md; electronics-firmware · repo-has boards/*.json <!-- REQUIRED:extensions -->
- The item (its issue, or the proposal in the decider's words) · what is still open elsewhere · the repository's push check, or "no push check here": P1194 #1740, epic, slice 10 The store; the move from Idea to Discovery is asked of spark-main (2026-11-26) · open elsewhere: P1193 #1738 discovery (session change-tracking, draft PR #1741), P1190 #1735 discovery (session simulation, draft PR #1742), P1161 #1697 (waits on his order), spark-and-git (an experiment), P1142 #1677 in Build · push check: the pre-push hook (the story run) <!-- REQUIRED:spark-process:item -->
<!-- EXTEND:frame -->
- Depth: TRIO (default: PO assistant, user, tech lead) | FULL or LIGHT (who asked, when); add "no independent review" if subagents could not start: TRIO, 3 agents on Opus (an epic: every lens on Opus, CLAUDE.local.md), then the refuter on Opus <!-- REQUIRED:depth -->
  <!-- Cost, measured once: the P900 rehearsal's council took 6 agents, 499 calls and about 90M input tokens (2026-10-06). -->
- Search budget: 6 web searches in all, 2 per lens, each for how a known tool layers its settings (git config, VS Code, npm), to reuse before inventing <!-- REQUIRED:budget -->
- Appetite (the decider's, asked only when heading for design) | —: — <!-- REQUIRED:appetite -->

## What we found <!-- CLAIMS -->
<!-- One claim per line: `- [★C<n>] claim · E pointer | H source | D who date · caveat: qualifier | none`.
★ marks a claim that a decision, an option or the riskiest assumption rests on. A quote is verbatim, with its pointer.
Say what the evidence can support: an account (what happened to one person), data (how often, in its population and
period), a document (what was specified), the product (what exists, not whether anyone needs it), a benchmark (a
comparison). Model knowledge is H until a source is read. Elsewhere cite a ★ claim as ★C<n>, with its keep: words.
e.g. `- [★C2] 13 of 526 tickets ask for recurring tasks · E tickets.csv:2-14 · caveat: picked by Lena; shows that, not how often` -->
- [★C1] Spark has one layered setting today, the tools list: three files merged field by field, the project winning · E `scripts/spark/records/tool_finder.py:91-115`, council/inventory.md · caveat: it holds tools only; its merge refuses a value that is a list or a string (TL-3)
- [★C2] Nobody is blocked without the seam today: P1193 and P1203 #1752 keep their settings where they are until the seam exists, and P410 #536 and P368 #470 were never pulled · E council/po-assistant.md:10 (PO-1), #1752, #536, #470 · caveat: one person's backlog; the cost of waiting is more places to move later
- [★C3] The PO repeats the same five shops in 3 of his 24 project briefs, and his store has no personal tools list · E facilitator's count of `sellers` in every `.spark/project.json` under ~/Development and spark-walks, 2026-11-26 (reaction-game, irrigation, spark-quickstart); PO-2; USER-3 · caveat: n = 1; why he did it is not known
- [★C4] A brief value of the wrong shape is dropped without a word, and spark's default runs: smartbin-local's `prefer` sentence gives the vendor order ("dfrobot", "seeed") · E `scripts/spark/records/brief.py:25-29,62`, `scripts/spark/sourcing/brief_choices.py:13-19`, USER-4, PO-3 · caveat: one project
- [★C5] A project's `.spark/tools.json` can point a role at its own script, claim the role's contract itself and blank `account_env`, which skips the Wokwi token check · E council/tech-lead.md TL-14 (a scratch experiment), `tool_finder.py:292-302`, `scripts/spark/firmware/scenario_run.py:273-274` · caveat: whether the script then runs was not tested
- [★C6] "Asks until set, like the tools list does today" (#1740) holds for one row only, the Wokwi token's `[!   ]` line; every other missing value takes the default · E `tool_finder.py:359-362`, PO-6, USER-14 · caveat: so asking is new behaviour, not a move
- [★C7] One layer has five names in spark today (global, user, personal, the person's, the store), and "global" means the person in git, the whole machine in npm and the user in VS Code · E council/user.md:25 (USER-9), council/po-assistant.md:62 (PO-8), https://code.visualstudio.com/docs/configure/settings read 2026-11-26 · caveat: outside tools read on one day
- [★C8] A tools-list choice made without `--project` goes to the person's file and reaches every project; nothing asks which layer was meant · E `commands/setup.md:79-82`, `scripts/tools.py:10`, USER-1 · caveat: the product, not how often it bites
- [★C9] Only the tools list can be changed from the terminal, and `tools.py` has no `--json`; the vendor order, the shops and P410's check have no command · E `scripts/tools.py --help`, USER-6, USER-23 · caveat: none
- [★C10] The page's request channel carries three Operations, and it takes a step's values from spark's own offer, never from the request · E `scripts/spark/flow/run_request.py:1-5,38-41`, TL-17 · caveat: so a free value from the page goes as a sentence to Claude
- [★C11] The core already has the shape a missing value needs: a Question with kinds yes_no, value and choice, and an open question exits 2 with `needs_reply` · E `scripts/spark/core/replies.py:30-95`, `docs/guide/agents/replies.md`, TL-10 · caveat: the replies file is research's own today, and no answer is written to a lasting layer
- [★C12] Git, VS Code and Claude Code each stop a project's file from setting some things (protected configuration, user-only settings, settings ignored in a project) · E council/po-assistant.md:73 (PO-9), https://code.claude.com/docs/en/settings-reference read 2026-11-26 · caveat: the VS Code scope list was not found whole
- [★C13] A deploy grant is a consent, not a setting: it lets Claude erase and write a board with no yes for each deploy, and the direct-flashing switch fails closed · E `scripts/spark/bench/board_grant.py:86-89,98-99,206-215`, electronics-firmware:physics-1 and 2 · caveat: none
- [★C14] Claude Code's plugin `userConfig` values do not reach commands that Claude runs through Bash, so spark's scripts cannot read them · E council/po-assistant.md:143 (PO-14), https://code.claude.com/docs/en/plugins-reference read 2026-11-26 · caveat: whether its values sync with the Claude account is not known
- [★C15] Of the candidate settings, only P410's (the check before the board) is on the MVP bar's path · H the tech lead, TL-1, on E #536 · caveat: the order is the PO's <!-- REQUIRED:findings -->

## Options <!-- CLAIMS -->
<!-- Two or three per open decision: decision · option · cost · what it would prove · opinion (whose), then the tag
and caveat cells. e.g. `- Q2 what first · fix delivery · two weeks · whether seen tasks get done · opinion (the facilitator's) · H ★C2 · caveat: none` -->
- Q2 the layers and their words · (a) three now, "spark's default", "yours, on this computer" (the store), "this project", plus an empty "your account" slot; no word "global" · small · whether one word per layer holds for a person and for Claude · opinion (the user lens, USER-10; the PO assistant, PO-8) · H ★C7 · caveat: words untested with anyone but the PO
- Q2 · (b) git's words, "global" and "local" · small · familiarity for git users · opinion (none of the lenses) · H ★C7 · caveat: "global" means three things outside
- Q2 · (c) four layers, with "this computer" apart from "you" · medium · room for a shared machine · opinion (the facilitator, for completeness) · H · caveat: no machine with two people is known
- Q3 how far a project is trusted · (a) each setting lists the layers that may set it, and spark refuses the others with a sentence · small · that a cloned project cannot widen sharing or spending · opinion (all three lenses: USER-12, TL-15, PO-9) · H ★C5 ★C12 · caveat: the tools list keeps today's rule until Q6
- Q3 · (b) the project wins everything, as the tools list does today · none · nothing new · opinion (none) · H ★C1 ★C5 · caveat: keeps ★C5's exposure
- Q4 a setting with no value · (a) two kinds: a default that is used and said, or a question once at the first need with "use spark's default" as an answer spark keeps · small · whether asking once is enough and never nags · opinion (the tech lead, TL-11; the user lens, USER-14) · H ★C6 ★C11 · caveat: none
- Q4 · (b) ask until set, at every run · small · the literal reading of #1740 · opinion (none) · H ★C6 · caveat: the replies file asks on every run today, which can nag
- Q5 a value spark cannot read · (a) refuse and say which file and why · small · no silent fallback · opinion (the PO assistant, PO-3) · H ★C4 · caveat: a refusal stops a run
- Q5 · (b) use the default and say so in the run's first line · small · the run goes on · opinion (the facilitator) · H ★C4 · caveat: a line can be missed
- Q6 the tools list · (a) it stays behind its own merge in the first slice, shown read-only through the seam · small · the seam without risk to /spark:setup · opinion (the tech lead, TL-3, TL-20) · H ★C1 · caveat: two places hold choices for a while
- Q6 · (b) it moves into the seam now · large (5 caller modules) · one place at once · opinion (none) · H ★C1 · caveat: risk to /spark:setup
- Q7 the first setting · (a) the vendor order to prove the seam, then P410's check · small, then medium · the seam on one caller · opinion (the tech lead, TL-20) · H ★C3 ★C4 · caveat: not on the bar
- Q7 · (b) P410's check first · medium · the one setting on the bar · opinion (the tech lead names it the bar's; the user lens, USER-15) · H ★C15 · caveat: needs new behaviour in deploy
- Q7 · (c) P1193's author identity first · medium · the ask-once path · opinion (the tech lead, as the ask path's test) · H ★C6 · caveat: waits on P1193
- Q8 a change from the page · (a) a sentence to Claude now; one button per choice later, with a confirm that names the layer and the projects it reaches · none now · the standing page rule · opinion (the facilitator, from the architect's answer of 25 Nov) · H ★C10 · caveat: two clicks and a paste
- Q8 · (b) one offer per choice through the request channel now · medium · one click · opinion (the tech lead, TL-17) · H ★C10 · caveat: widens the page's allow-list
- Q9 the account slot · (a) an empty slot now; a GitHub sign-in its first candidate later (D6) · none now · that the seam takes a fourth layer with no caller change · opinion (the PO assistant, PO-10; the tech lead, TL-21, TL-22) · H · caveat: no second machine or person is known
- Q9 · (b) the Claude account · — (a spike) · whether Claude Code exposes it to scripts · opinion (none) · H ★C14 · caveat: spark cannot write to it
- Q10 the line between settings and consents · (a) grants and the direct-flashing switch are never settings; a paid-run setting only narrows when spark asks, and the yes stays typed · none · that no setting answers a yes · opinion (the tech lead, physics-1 to 3; the user lens, USER-16; the PO assistant, PO-13) · H ★C13 · caveat: P1190's D13 asks for "run only for releases", which needs a careful reading
- Q11 the order with P1193 · (a) P1151 #1687 writes P1193's two roles into the tools list now, and they move later · none · P1193 is not held up · opinion (P1193's synthesis) · E council/tech-lead.md:141 (TL-18) · caveat: two settings move twice
- Q11 · (b) P1151 waits for the seam's first slice · — · one move only · opinion (the tech lead, TL-18) · E council/tech-lead.md:141 (TL-18) · caveat: holds P1193 <!-- REQUIRED:options -->
- Proposed no-gos and rabbit holes (proposals until the decider confirms): no account code, no sign-in and no new service now (D6); no setting that answers a yes to spend money or write a board; goal, must, needs and the rules stay records, not settings (PO-12); no word "global"; the page never shows a token's value or a path on the person's computer; the tools list is not rewritten in the first slice. Rabbit holes: syncing settings between machines before a second machine exists; Claude Code's `userConfig` as the store (★C14) · H the three lenses, D6 · caveat: proposals until he confirms <!-- REQUIRED:nogos -->

## Riskiest assumption and its test
- Riskiest: A1, that a person looks on a page for why spark did something and whose word a value is, rather than asking Claude in the chat · proposed — the facilitator's opinion, from the PO assistant's pre-mortem (PO-17), pending Q1 <!-- REQUIRED:riskiest -->
- Test · kind · pass line, dated before any result · proposed: a prototype walk of the Settings artboard by the PO (n = 1) with three tasks: say which check runs before the board in the clock and whose word it is; say why smartbin-local used DFRobot; say how to set his shops for all projects · prototype · pass line: 3 of 3 found on the artboard without help, set 2026-11-26 · proposed — the facilitator's opinion, pending Q1 <!-- REQUIRED:test -->

## Questions
<!-- A queue; the first open question is asked alone. Each: Q<n> · question · decides: … · options · unblocks ·
opinion (whose) · kind: decision | account (a past-tense question about the decider's own use; the answer is E,
account, n = 1) · status: queued | asked <date> | answered D<n>.
If the decider cannot be asked, the queue stays here, and whatever rests on it stays H. -->
- Q0 · Is this frame right: the decision, the start and reach, the extensions and the depth? · decides: the frame · status: answered D5 <!-- REQUIRED:q0 -->
- Q1 · How important is each assumption (A1 to A8), and what pass line must the riskiest test meet? · decides: importance and pass lines · status: queued <!-- REQUIRED:q1 -->
- Q2 · Which layers, and which word for each? · decides: the layer names and count · options in Options · opinion (the user lens and the PO assistant): (a) · kind: decision · status: queued
- Q3 · May a project's file set every setting, or does each setting list the layers that may set it? · decides: the trust rule for the project layer · opinion (all three lenses): (a) · kind: decision · status: queued
- Q4 · When a setting has no value, is its default used and said, or does spark ask once and keep the answer? · decides: the two kinds of setting · opinion (the tech lead, the user lens): (a) · kind: decision · status: queued
- Q5 · When spark cannot read a value, does it refuse, or use the default and say so? · decides: the rule ★C4 shows is missing · kind: decision · status: queued
- Q6 · Does the tools list stay behind its own merge in the first slice? · decides: the first slice's size · opinion (the tech lead): yes · kind: decision · status: queued
- Q7 · Which setting goes first: the vendor order, P410's check, or the author identity? · decides: the first slice's card · kind: decision · status: queued
- Q8 · From the page, a sentence to Claude now, or one button per choice? · decides: whether settings join the page's allow-list · kind: decision · status: queued
- Q9 · Is the account an empty slot now, with a GitHub sign-in as its first candidate later? · decides: what the seam leaves room for · opinion (the PO assistant, the tech lead): yes · kind: decision · status: queued
- Q10 · Do grants and the direct-flashing switch stay outside the settings, and may a paid-run setting only narrow when spark asks? · decides: the line between settings and consents · kind: decision · status: queued
- Q11 · Does P1151 #1687 write P1193's two roles into the tools list now, or wait for the seam? · decides: whether two settings move twice · kind: decision · status: queued
- Q12 · In the last 30 days, did you run spark on a second computer, or want one of your choices to follow you there? · decides: whether the account slot stays empty for long (A5) · kind: account · status: queued
- Q13 · When did you last want to know why spark did something, such as skip the simulation, and where did you look? · decides: whether the settings list or the step folds come first (A1) · kind: account · status: queued

## Decisions
<!-- D<n> · what · who · when · where recorded · options considered.
A yes covers only the actions and choices it names. A standing yes names its kind of action and its source.
Name what a D confirms in its words: the frame, the jobs, a direction, the remaining risk, a test, items.md. -->
- D1 · settings in layers, a default each, ask until set, existing choices move there · the PO · 2026-11-26 · #1740 · options considered: —
- D2 · what leaves the store on a share and what syncs to the public are settings, none by default · the PO · 2026-11-26 · P1193 #1738 P1, P4 · options considered: P1193's lists
- D3 · every new plan names its setting, default and layer · the PO · 2026-11-26 · memory settings-layers-rule · options considered: —
- D4 · start this discovery and the page design now · the PO · 2026-11-26 · spark-artifact's question dialog · options considered: settings page, history screens, firmware editor, tidy the canvas
- D5 · confirms the frame, with the account layer in scope · the PO · 2026-11-26 · Q0, spark-artifact's question dialog · options considered: the frame as written, add the account layer, LIGHT depth
- D6 · the account layer: accounts and a GitHub sign-in are optional and for a later version, not the MVP; with an account spark could create projects, reach the parts and suggest edits; an account layer needs a way to manage one's account; now, the architecture must let the layer be added later · the PO · 2026-11-26, about 12:45 CET · in spark-artifact's chat, verbatim: "Yeah, so we should probaby also add accounts and github sign in, optionally , but then one can have spark create projects, access the parts, suggest edits, etc, but I'm thinking this might really only be a feature for later versions, not MVP, but if we add the user account layer, which atually would make sense for a few features, we need to make sure one can manage his account. We can just make sure the architecture is well made so that we can add this layer later." · options considered: the account layer designed now (D5), a seam only
- D7 · users, permissions and groups come later, with the accounts of D6 · the PO · 2026-11-26, about 12:50 CET · in spark-artifact's chat, verbatim: "And like users and permissions and groups, etc later" · options considered: —
- D8 · every feature is independent of its interface and reachable from the other interfaces, unless it depends on one interface and makes no sense without it; for this item, reading and changing a setting is an Operation that the CLI, Claude and the page reach alike · the PO · 2026-11-26, about 13:00 CET · in spark-artifact's chat, verbatim: "And as always, make sure the fatures are always independent of the interface, the functinality  should aslo be accesssible from other interfaces, that's a general rule, unless its something dependent on the interface and wouldn't make sense without it" · options considered: — (a standing rule, beside AGENTS.md's "one core, many interfaces")
- D9 · widens D8: every feature is reachable at least from the CLI now, later from MCP and from code (LangGraph and the like), and always for both agents and people · the PO · 2026-11-26, about 13:15 CET · in spark-artifact's chat, verbatim: "yeah evevrything must be accessible at least from CLI, later it will be MCP, in a code, like Langgraph, etc, and always for both agents and humans." · options considered: —

## Found on the way <!-- CLAIMS -->
<!-- Outside this item's scope. Each is a separate proposal, never folded in. Same line format as What we found. -->
- [F1] A project's `.spark/tools.json` can point a role (for example `simulator`) at a script inside the project, declare the role's contract itself, and blank `account_env`, which skips the Wokwi token check; `tool_finder.find` returned that script in a scratch project · E council/tech-lead.md TL-14, `scripts/spark/records/tool_finder.py:292-302`, `scripts/spark/firmware/scenario_run.py:273-274` · caveat: whether the script then runs was not tested; a separate proposal (a card), never folded into this item 
- [F2] The brief's `prefer` drops a sentence without a word (★C4); a bug of today's code, a separate card · E council/user.md:15 (USER-4), council/po-assistant.md:27 (PO-3) · caveat: one project
- [F3] The tools list's choices (`--on`, `--off`, `--use`, `--pin`, `--new`) have no Operation, so under D8 and D9 they reach only the CLI · E council/tech-lead.md:52 (TL-8), council/tech-lead.md:156 (TL-23) · caveat: a gap for #94's records area <!-- REQUIRED:found -->

## Board actions <!-- REQUIRED:spark-process:board-actions -->
<!-- Each action on the board or the issue (stage, waiting flag, comment, filing): taken, with its D, or pending.
None is taken without a D. e.g. `- move #16 to Discovery · pending` -->
- move #1740 to Discovery · taken by spark-main, 2026-11-26, on D4
- Waiting on and Waiting since on #1740 while a question waits · pending
- a comment on #1740 that links the brief · pending, with the draft PR
<!-- EXTEND:brief-sections -->

## Hand-off
<!-- Written only after the decider confirms the understanding (a D); copies only confirmed constraints. Holds: outcome ·
who · success and its proof · constraints (appetite, confirmed no-gos, rabbit holes) · what they said (D) against what
we assume (H) · links to the journeys and the map · riskiest assumptions and their tests · options considered. -->
not yet: the jobs, a direction and the remaining risk are unconfirmed <!-- REQUIRED:handoff -->

## Files
[Jobs and journeys](jobs-and-journeys.md) · [Story map](story-map.md) · [Risks and tests](risks-and-tests.md) · [Verification](verification.md) · [Items](items.md) · council/
