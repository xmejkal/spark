<!-- Resume: invoke product-discovery again; `discovery.py check <this folder>` names the next step. -->
# P1200: the firmware on the page, a deploy from the browser, and which feature works on which host: discovery brief

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
- Request, verbatim (corrections marked): the PO, 2026-11-26, quoted on #1748: "And the last epic will be online firmware editor , also not an MVP thing, but when using the page as inteface, it might also be nice to offer some on the page editing and display of the generated code and maybe even deploy directly rfom the broswer, if that's supported. And maybe some of these functionalities are available but only for a version of the page running on our server or local server, but not for the claude artifact version ? Let's get into this topic  too, ask the coordinator to also process these ideas". His standing line for every brief, the same day: "the architecture needs to be well made so that we can change these srtrategies and tools and its reusable, dry" <!-- REQUIRED:request -->
- Decision · decider: the PO decides, through spark-main. D-q1 what the page shows of the firmware: `firmware/main.py`, the generated `firmware/pins.py`, the pin map, and which other generated files · D-q2 whether a person edits the firmware on the page, which files, and how an edit reaches the project, the conversation and the kept steps of P1193 #1738 · D-q3 whether a deploy starts from the page, and through which path: the browser itself over Web Serial, or spark's own deploy run on the person's computer by a host that can run a program. Either path keeps the look at the board, the person's yes and the read-back. This reopens P218 D11 ("no browser flasher for now") and P820's no-go on a Deploy button · D-q4 which host offers which feature: the Artifact in a browser, the Artifact installed as a desktop app, a local server, and a server of spark's own · D-q5 the seams and their settings: the editor, the flasher, the page host, each one seam chosen by a setting behind an Operation <!-- REQUIRED:decision -->
- Outcome and how it is observed (a metric with unit and source, a proof command, or a log): proposed: (1) a table of features by host, each cell with its evidence and "not tested" where nobody ran it, and (2) one written answer per decision D-q1 to D-q5, each fitting the core (rules.md, "The core is important", 2026-11-25). Observed later when, in a scratch project on a board on USB, (a) the page shows main.py and pins.py as spark holds them, (b) an edit on the page lands in `firmware/main.py` and the conversation and the timeline see it, and (c) a deploy started from the page shows the look, waits for the person's yes and reads the board back, on each host the table marks as able <!-- REQUIRED:outcome -->
- Already decided (D · who · when · where; include the product's stated non-goals and earlier decisions the request names): D-a · no browser flasher for now: the Python esptool stays the one flashing tool · the PO · 2026-10-13 · P218 D11 (docs/discovery/2026-10-13-p218-deploy-and-board/brief.md:153), with its no-go "revisit only for a first install by a person with no Python" (brief.md:97) · D-b · one well-architected core that a CLI, a web server and MCP use · the PO · 2026-10-13 · P218 D8 · D-c · a confirmed click on the page is a yes "never for the board or a simulation", and firmware, simulate and deploy stay in the chat or the terminal in the MVP · the PO · P820 D9 (docs/discovery/2026-11-15-p820-artifact-interface/brief.md:182) and the MVP plan's line that D11 approved (mvp-plan.md:188). The no-go on a Flash, Deploy or Run-live-code button was a proposal in P820 (brief.md:97), confirmed by P1038's D24 through a delegated council, the PO's to change (council/po-assistant.md, PO-5) · D-c2 · the page loads nothing from the web, a request carries a key from an allowlist and never a command line or a path, the page's script holds no logic, and there is no Node build · P820 D7 (brief.md:180), P820's mvp-plan.md:7-8, P1038 D24, P269 D16 (council/po-assistant.md, PO-6) · D-d · a yes that another program collected never opens the erase (`RelayedConsentStrategy.opens_erase = False`) · P675, scripts/spark/bench/deploy_gate.py:117-126 · D-e · spark exports facts, never behaviour: the conversation writes the firmware, and spark writes only `pins.py`, whose header says not to edit it · AGENTS.md, the vision's not-goals ("A firmware generator, or anything that writes behaviour") · D-f · one exchangeable strategy for a project's kept steps, git first, and spark commits a declared kept record after the person's yes · the PO · 2026-11-26 · P1193 D6, D14 (its folder returns to main by spark-main's branch restore-after-1775) · D-g · for a website, only the seams are built now · the PO · 2026-11-25 · the git discovery's D12 (docs/discovery/2026-11-25-spark-and-git/brief.md:80, :105) · D-h · every configurable choice names its setting, its default and its layer · the PO · 2026-11-26 · P1193 D8, epic P1194 #1740 · D-i · the epic is after the MVP · the PO · 2026-11-26 · #1748 <!-- REQUIRED:decided -->
- Open questions: see Questions <!-- REQUIRED:open -->
- Scope · out of scope (proposed): in: what the page shows of the firmware and the generated files, an edit of the firmware on the page and its way to the project, the conversation and the kept steps, a deploy started from the page on each host, the table of features by host, the seams and their settings · out: building any of it, a firmware generator (D-e), an edit of `pins.py` by hand (it is regenerated), a live REPL or "run this code now" button (P235's live-on-board work), Arduino or ESP-IDF firmware, a public website with accounts (D-g), the page's editing of parts and wires (P1163 #1699), and a paid service <!-- REQUIRED:scope -->
- Start and reach (proposed until Q0): start ⟨existing product | someone else's idea | own idea⟩ · decider reachable ⟨yes | no⟩ · users ⟨who, how | none reachable⟩ · data and connectors ⟨by category, from your own tool list; "not connected" is a gap; never ask to connect one⟩ · decider as a user ⟨n = 1 | no⟩ · must not get worse ⟨for an existing product⟩: start existing product · decider reachable through spark-main only: the PO's questions go to spark-main in rounds of up to four · users none reachable beyond the PO · data and connectors: the repository, gh, the store read-only, the claude-artifacts server, Chrome through Claude in Chrome (read-only use), and the web (research.md) · decider as a user n = 1 · must not get worse: the deploy's look, yes, erase, write and read-back with a typed yes (P675), the page's rule that spark takes every value from its own offer (run_request.py:1-5), `pins.py` regenerated from the design, and the page as it works in the Artifact today <!-- REQUIRED:start-reach -->
- Flags (yes · no · —; asked only when it changes a decision; never legal advice; any date or threshold is read at its source at run time and cited):
  - sold or given away, or personal use: personal use now. Spark is public under MIT <!-- REQUIRED:flag-sold -->
  - connects to a network or runs software (for example the EU's Cyber Resilience Act): yes: a deploy writes firmware to a device, and a page that runs a program or opens a serial port reaches the person's computer. No rule is read here, because no decision here turns on one <!-- REQUIRED:flag-network -->
  - children or food contact: no <!-- REQUIRED:flag-children -->
  - market: — <!-- REQUIRED:flag-market -->
  - radio (unlicensed-device rules; read at their source when it decides): n/a: the epic changes how firmware reaches the board, not what radio the firmware uses <!-- REQUIRED:electronics-firmware:flag-radio -->
  - a Li-ion cell (charging, transport, battery rules): n/a <!-- REQUIRED:electronics-firmware:flag-li-ion -->
  - mains: n/a <!-- REQUIRED:electronics-firmware:flag-mains -->
  <!-- EXTEND:flags -->
- Extensions (each active id · the fact that activated it; when none matched, only "none matched: core only · the fact that decided it", naming no extension; list any directive skipped under rule 9): spark-process · repo-has scrum/WORKING_AGREEMENTS.md; electronics-firmware · repo-has boards/*.json <!-- REQUIRED:extensions -->
- The item (its issue, or the proposal in the decider's words) · what is still open elsewhere · the repository's push check, or "no push check here": P1200 #1748 (https://github.com/xmejkal/spark/issues/1748), an epic in Discovery since 2026-11-26 15:02 CET, slice Views and editors · still open elsewhere: P820 #1173, P199 #152, P494 #674, P1038 #1521, P1193 #1738, P1194 #1740 · the push check is the pre-push hook <!-- REQUIRED:spark-process:item -->
<!-- EXTEND:frame -->
- Depth: TRIO (default: PO assistant, user, tech lead) | FULL or LIGHT (who asked, when); add "no independent review" if subagents could not start: FULL, as spark-main's brief of 2026-11-26 asks: four lenses on Opus (the PO assistant for Existing first and Risks, the user's journey with the UX and AI-UX lens by the PO's rule of 2026-10-18, the tech lead for Feasibility with the electronics-firmware:physics lens, and the architecture lens because the epic adds seams to the core), the architect agent for the synthesis, and the refuter on Opus. The pre-analysis and the research ran first as two Opus agents (preanalysis.md, research.md) <!-- REQUIRED:depth -->
  <!-- Cost, measured once: the P900 rehearsal's council took 6 agents, 499 calls and about 90M input tokens (2026-10-06). -->
- Search budget: research.md holds the web search, with every query listed. The lenses read the repository, the store and the folder, with at most 3 web searches each to check a claim that a decision rests on. The refuter has at most 5 fetches <!-- REQUIRED:budget -->
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
- Q0 · Is this frame right: the decision, the start and reach, the extensions and the depth? · decides: the frame · options: yes · yes, but drop the deploy (D-q3) and keep show and edit · change it · kind: decision · status: asked 2026-11-26 15:28 CET, through spark-main <!-- REQUIRED:q0 -->
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
