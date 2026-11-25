<!-- Resume: invoke product-discovery again; `discovery.py check <this folder>` names the next step. -->
# spark and git: whose rules, which repository, which folder: discovery brief

<!-- Readiness, its one home. collecting evidence: anything short of the two below. an experiment: the decider chose
a test (a D) before choosing an option. design: the decider confirmed the frame, the jobs and a direction, and accepted
the remaining risk (D rows). An extension may tighten these. Next: design, or a chosen test of kind spike or prototype
→ the design skill the facts name, with this file; otherwise none, and the collection plan says who runs it.
Stands on: the assumptions not retired in risks-and-tests.md; of which those the decider rated high, or — while any
is unrated. check computes both. -->
**Ready for:** collecting evidence <!-- REQUIRED:ready -->
**Stands on:** ⟨fill⟩ H, ⟨fill⟩ of which would change the decision <!-- REQUIRED:debt -->
**Decision needed:** the PO: whose rules go where; whether and how a spark project gets its own git repository and spark uses it (history, undo); who makes a project's folder and calls init; and how each answer holds across interfaces <!-- REQUIRED:decision-needed -->

## Frame
- Request, verbatim (corrections marked): the PO, 2026-11-25, in the session "spark page design", five messages in a row: (1) "Actually, let's think about it a bit more, because what rules is it? Is it for the agents working on Spark, or are they rules that also apply to agents working on the projects? I would definitely like the Spark projects to have a Git repository. I think we can also make Spark be able to work with Git and revert and all these things. Maybe it's for a better, consistent standard. Maybe can we actually hold a council for how to do that the best, and if and how Spark could use Git? Generally, also, how does it work when we create a new project with Spark: who creates the folder, when, and so on?" (2) "And it might be good to consult what Anthropic recommends, although we do want to make it general, not only for Claude." (3) "Or maybe it should be Sparks agents that create the folder and call the init?" (4) "Oh yeah, and also let's consider how it will differ with different interfaces. When we use it, just in code, like LangGraph, or as an MCP, it will probably be different, right?" (5) "And also, one more thing: maybe in the future (I'm not sure about that), maybe we'd also like to make a public website that uses Spark, and you can just make projects and tinker around online. How would it be there?" (6), while the frame was asked: "Yeah, and that's basically probably the next interface, or how, in general, that would work. We would probably have some server. We would present this web page too, but the buttons would do something else. It should go through the server, probably, not directly to Claude." Before these, the same day: "And shouldn't we save the rules somewhere more findable and also like so that we have it in Git?" and "I think we should actually instruct Spark generally to make the projects with a Git" <!-- REQUIRED:request -->
- Decision · decider: D-q1 which rules apply to the agents that develop spark and which to the agents that work on a person's project, and where each set lives · D-q2 whether a spark project always has its own git repository, who makes it and when · D-q3 what spark does with git (commit its writes, show history, undo) and through which layer · D-q4 who makes the project's folder and calls init (the person, Claude, spark's agents, the core) · D-q5 how D-q2 to D-q4 hold on the CLI, in code (LangGraph), over MCP and on a hosted website · decider: the PO <!-- REQUIRED:decision -->
- Outcome and how it is observed (a metric with unit and source, a proof command, or a log): proposed: one written answer per decision, each fitting the core (rules.md, "The core is important", 2026-11-25); observed when a fresh person's project, made through the CLI, has its own repository and its brief commit (init's `committed as <sha>` line, commands/init.md:67-70) with no step by hand, and an undo through spark reverts one write <!-- REQUIRED:outcome -->
- Already decided (D · who · when · where; include the product's stated non-goals and earlier decisions the request names): D-a · the rules go into git and are pruned, and changes come by PR · the PO · 2026-11-25 · this session (the move to scrum/ is on hold until this discovery decides) · D-b · one core, many interfaces; spark exports facts, never behaviour; free, few and local · AGENTS.md principles · D-c · every plan and PR with new logic says how it fits the core; a new interface adds the architecture lens on Opus · the PO · 2026-11-25 · rules.md · D-d · the core is ready for streaming and for LangGraph, a live web page and an SSE MCP; each MVP card takes the small seam that keeps other hosts open, never the other host · the PO · 2026-11-16 and 11-23 · memory spark-architecture-direction · D-e · a revert runs only on the person's yes, and spark's own code never runs it · commands/idea.md:78-79 (P1027) · D-f · harmless private text stays in history; history is rewritten only for secrets · the PO · 2026-11-23 · memory <!-- REQUIRED:decided -->
- Open questions: see Questions <!-- REQUIRED:open -->
- Scope · out of scope (proposed): in: the two rule sets and their homes; a project's repository; spark's use of git; the folder's start; the four interfaces; what Anthropic recommends for Claude Code (CLAUDE.md, memory, settings) and the tool-neutral conventions (AGENTS.md); the website as a constraint on the seams · out: building the website, LangGraph or MCP; a git host or remote for a person's project (asked as a question, not assumed); the prune itself (a card after this) <!-- REQUIRED:scope -->
- Start and reach (proposed until Q0): start ⟨existing product | someone else's idea | own idea⟩ · decider reachable ⟨yes | no⟩ · users ⟨who, how | none reachable⟩ · data and connectors ⟨by category, from your own tool list; "not connected" is a gap; never ask to connect one⟩ · decider as a user ⟨n = 1 | no⟩ · must not get worse ⟨for an existing product⟩: start existing product · decider reachable yes · users none reachable beyond the PO; his 23 project and walk folders are evidence (8 with their own repository, 15 without, read 2026-11-25) · data and connectors: the repository, gh, the store, the web for Anthropic's and AGENTS.md docs · decider as a user n = 1 · must not get worse: init's brief commit and its way back (P1027); the 29 CLAUDE.local.md links <!-- REQUIRED:start-reach -->
- Flags (yes · no · —; asked only when it changes a decision; never legal advice; any date or threshold is read at its source at run time and cited):
  - sold or given away, or personal use: personal use now; a public website later is the PO's "not sure" (message 5) <!-- REQUIRED:flag-sold -->
  - connects to a network or runs software (for example the EU's Cyber Resilience Act): — <!-- REQUIRED:flag-network -->
  - children or food contact: no <!-- REQUIRED:flag-children -->
  - market: — <!-- REQUIRED:flag-market -->
  <!-- EXTEND:flags -->
- Extensions (each active id · the fact that activated it; when none matched, only "none matched: core only · the fact that decided it", naming no extension; list any directive skipped under rule 9): spark-process · repo-has scrum/WORKING_AGREEMENTS.md <!-- REQUIRED:extensions -->
- The item (its issue, or the proposal in the decider's words) · what is still open elsewhere · the repository's push check, or "no push check here": the discovery card is asked of spark-main (not yet filed); still open elsewhere: P1002 #1461 in Discovery, and the P1038 page-design discovery (ready for design); the push check is the pre-push hook <!-- REQUIRED:spark-process:item -->
<!-- EXTEND:frame -->
- Depth: TRIO (default: PO assistant, user, tech lead) | FULL or LIGHT (who asked, when); add "no independent review" if subagents could not start: FULL proposed (the PO asked for "a council", and the question touches the core and four interfaces): the PO assistant, the user, the tech lead, the architecture lens on Opus, the UX and AI-UX lens (his rule of 2026-10-18), one researcher for Anthropic's and the tool-neutral recommendations, then the refuter; the architect writes the synthesis <!-- REQUIRED:depth -->
  <!-- Cost, measured once: the P900 rehearsal's council took 6 agents, 499 calls and about 90M input tokens (2026-10-06). -->
- Search budget: one researcher, at most 10 searches, primary docs only; each lens reads the repository and the store, no web <!-- REQUIRED:budget -->
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
- D1 · the frame: the five decisions D-q1 to D-q5, the website as a check on the seams only · the PO · 2026-11-25 · AskUserQuestion in this session · options: this frame, without the website, only D-q1, D-q2 and D-q4
- D2 · depth FULL: PO assistant, user, tech lead, architecture on Opus, UX and AI-UX, one researcher (Anthropic's and tool-neutral advice, at most 10 searches), then the refuter; the architect writes the synthesis · the PO · 2026-11-25 · AskUserQuestion · options: full council, trio and research
- D3 · D-q1, the team's rules: the team's process (board, lanes, PRs, hook, councils) moves to spark's scrum/ in git; a project that runs the team process names it in one line of its own AGENTS.md; a gadget session loads no team rule · the PO · 2026-11-25 · AskUserQuestion (synthesis Q1) · options: this, one pruned file as today, no project gets them
- D4 · D-q1, the PO's own lines (about him, not about spark): a file of his own in spark's scrum/, public, in git, changed by PR; the store's rules.md links to it, so the 29 links keep working · the PO · 2026-11-25 · AskUserQuestion (synthesis Q2, recommendation changed after the refuter's ★C11 verdict) · options: this, a private repository, the store only
- D5 · D-q4 and D-q3, one exchangeable strategy: the PO's answer to "who makes the folder", verbatim: "Well, ok, let's make it configurable, it should again be a good architecture so that the strategy of the revert and init and all these are exchangable, but the first one we implement for spark is going to be git  and the init operation calls it I would say. And then later also the history or reverting calls the same strategy. Another strategy might be human does that, using just file manipulation, or maybe on the server some other system would do this" · the PO · 2026-11-25 · AskUserQuestion (synthesis Q3) · options offered: one spark Operation, Claude with mkdir, the person
- D6 · D-q2: spark makes a git repository by default, with an ignore list first and a first commit of the files it wrote, said in one line; a person can turn it off once in their settings · the PO · 2026-11-25 · AskUserQuestion (synthesis Q5, recommendation changed after the refuter's direction verdict) · options: always by default, ask once, never
- D7 · D-q3, who carries out a take-back: the strategy runs it (the git strategy runs the take-back, for example git revert, itself) after the person's yes, which comes through the core, so it works on every interface; a human or server strategy does it its own way. This replaces "spark's own code never runs it" (commands/idea.md:79, from commit 57e59143, not the PO's words per the refuter's ★C25 verdict) · the PO · 2026-11-25 · AskUserQuestion · options: the strategy runs it, the strategy writes the earlier content as a new write
- D8 · D-q3, which writes are kept steps: the records the person decided (the brief, the needs, the picks, the requirements, the board), one step per decision; build outputs and the page are made again from them · the PO · 2026-11-25 · AskUserQuestion (synthesis Q8) · options: this, the brief only, everything. Caveat for the design: a pick also holds parts in the store, which is outside the project's git (UX-3)
- D9 · how far back: any kept step, from the history; the newest is the default answer to "undo that". This replaces P867 D6 ("one previous version, no full undo history", 2026-11-17) and follows his rule of 2026-11-23 on #1506 ("keep every change reversible", "probably using git") · the PO · 2026-11-25 · AskUserQuestion (synthesis Q9) · options: any step, the last step only
- D10 · D-q4, where a new project goes: a projects home that the person sets once, kept in the store; each new project goes there unless the person names another place; a command can then list the person's projects · the PO · 2026-11-25 · AskUserQuestion (synthesis Q4) · options: a projects home, where you are now
- D11 · the words after a kept step: plain words ("Kept. To take it back, say: undo that."), each interface adds its own way, the commit id stays in the JSON · the PO · 2026-11-25 · AskUserQuestion (synthesis Q11) · options: plain words, git words
- D12 · D-q5, the website: only the seams now (the folder is a value passed in, the yes goes through the core, the strategy is exchangeable, no message names git or Claude); nothing for a server is built · the PO · 2026-11-25 · AskUserQuestion (synthesis Q12) · options: only the seams, also accounts
- D13 · the first test: A1, spark's commits happen and are safe, in a scratch folder; pass line: 3 of 3 brief writes print a kept line, 0 tracked files match the ignore list; it also counts the files already tracked in the 9 repositories that the ignore list would cover · the PO · 2026-11-25 · AskUserQuestion (synthesis Q13), set before any result · options: A1, A2, both

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
