<!-- Resume: invoke product-discovery again; `discovery.py check <this folder>` names the next step. -->
# P663 pin conflicts: discovery brief

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
- Request, verbatim (corrections marked): "You know what, le'ts actually really do this properly, add it to the journeys the story map, really analyse the option, design with good architecture respecting what we want from the architecture and have it refined, council, etc. etc. Maybe there can be more scenarios we didn't think about, so lets'have a good thought through general approach t conflicts like that, how each interface deals with it, the core, etc.." (the PO, 2026-11-07, after he chose option B for the GDI cable, D1) <!-- REQUIRED:request -->
- Decision · decider: How spark finds, explains and resolves a conflict over a pin or another resource that two things claim: which kinds of conflict it handles, which it asks the person about, what the core decides and what each interface (the CLI and its --json, the commands and agents, MCP) shows. The first slice to build. · the PO (Petr) <!-- REQUIRED:decision -->
- Outcome and how it is observed (a metric with unit and source, a proof command, or a log): The P581 project (GDI screen, MAX98357A, joystick on a FireBeetle 2 ESP32-S3) gets a pin map, a breadboard sheet and a build in which no two claims share a pin and each conflict is named or asked, proved by `check_spine.py requirements.json --keep .` on that project and by a fixture per conflict kind (proposed) <!-- REQUIRED:outcome -->
- Already decided (D · who · when · where; include the product's stated non-goals and earlier decisions the request names): D1 · the PO · 2026-11-07 · AskUserQuestion, issue #892: for the GDI cable, option B, ask "cable or wires?" then place the connector's pins first, with a check that stops on a conflict that is left (C) · P527 #726 (story, open): a pin a connector fixes is accepted on a strapping pin, and the strap is named · P460 #628 (spike, open): how a board record holds the GDI and camera connectors · C4 of the close audit: a strapping pin asked for by name with no connector stays refused (`scripts/assign_pins.py:65-70`) · D2 · the PO · 2026-11-07 · this session: "And lets finish the refactoring soon, I want it already in a good version, so we can make it all work nicely with all the interfaces etc", so the conflict model is built on the core, in or after wave 6's design move (`docs/discovery/2026-10-19-p323-target-architecture/architecture/refactor-plan.md:11-12`), and the refactor's next PRs (W4-4, wave 5) go first · the architecture principles in AGENTS.md: one core, many interfaces; spark exports facts, never behaviour; records grow by need; checks read facts in records rather than logic per part · the non-goals in `scrum/VISION.md`, read at step 2 <!-- REQUIRED:decided -->
- Open questions: Which kinds of conflict exist beyond the four seen so far (a connector's fixed pins, an onboard part on a pin, a strapping pin, the pins a working project already uses)? Which does the person decide and which does spark decide alone? Where does the decision live (the requirements file, the project's records, the board record)? How does a person, and Claude, see a conflict in each interface? <!-- REQUIRED:open -->
- Scope · out of scope (proposed): In: conflicts over a board's pins and the resources behind them (a pin, a bus, a connector, a strap, an onboard part), as the assigner, the build and the sheet meet them; the journey steps where they show; the core's model and each interface's view · Out: electrical budgets (current, voltage), which check_physics owns; PCB routing; firmware behaviour, which spark never writes (proposed) <!-- REQUIRED:scope -->
- Start and reach (proposed until Q0): start ⟨existing product | someone else's idea | own idea⟩ · decider reachable ⟨yes | no⟩ · users ⟨who, how | none reachable⟩ · data and connectors ⟨by category, from your own tool list; "not connected" is a gap; never ask to connect one⟩ · decider as a user ⟨n = 1 | no⟩ · must not get worse ⟨for an existing product⟩: start existing product · decider reachable yes · users the PO at his bench, walk P581, and Claude as the second user of every interface · data and connectors: the repository, the part records and the shelf, the board files, the walk diaries and their rows files, GitHub issues through gh, Miro (100 calls a day) · decider as a user n = 1 · must not get worse: C4's refusal of a strapping pin with no connector, the pin maps of the walks that build today, the exit codes <!-- REQUIRED:start-reach -->
- Flags (yes · no · —; asked only when it changes a decision; never legal advice; any date or threshold is read at its source at run time and cited):
  - sold or given away, or personal use: personal use; spark is public under MIT <!-- REQUIRED:flag-sold -->
  - connects to a network or runs software (for example the EU's Cyber Resilience Act): no, this changes pin assignment, not what the gadget connects to <!-- REQUIRED:flag-network -->
  - children or food contact: no <!-- REQUIRED:flag-children -->
  - market: — <!-- REQUIRED:flag-market -->
  - radio (unlicensed-device rules; read at their source when it decides): — (ADC2 pins are unusable with WiFi, a pin limit the lenses can name) <!-- REQUIRED:electronics-firmware:flag-radio -->
  - a Li-ion cell (charging, transport, battery rules): no <!-- REQUIRED:electronics-firmware:flag-li-ion -->
  - mains: no <!-- REQUIRED:electronics-firmware:flag-mains -->
  <!-- EXTEND:flags -->
- Extensions (each active id · the fact that activated it; when none matched, only "none matched: core only · the fact that decided it", naming no extension; list any directive skipped under rule 9): electronics-firmware · repo-has boards/*.json; spark-process · repo-has scrum/WORKING_AGREEMENTS.md <!-- REQUIRED:extensions -->
- The item (its issue, or the proposal in the decider's words) · what is still open elsewhere · the repository's push check, or "no push check here": P663 #892 (story, Idea, under P100 #6), proposed to grow into an epic for pin conflicts with P663 as its first story, Q0 · open elsewhere: P659 #890 and P514 #888 in Review, their gates running; the P581 bench walk paused at the must lines · push check: the pre-push hook, `scripts/check_commit.py` <!-- REQUIRED:spark-process:item -->
<!-- EXTEND:frame -->
- Depth: TRIO (default: PO assistant, user, tech lead) | FULL or LIGHT (who asked, when); add "no independent review" if subagents could not start: FULL, asked by the PO on 2026-11-07 (Q0, D3): 7 lenses in parallel on the everyday model (Sonnet): the four core lenses (Existing first, Feasibility, the user's journey, Risks and assumptions), electronics-firmware's Physics lens, and the PO's two standing lenses, architecture (2026-10-14) and UX with AI-UX (2026-10-18); then the refuter on the strongest model (Fable). 8 agents in all <!-- REQUIRED:depth -->
  <!-- Cost, measured once: the P900 rehearsal's council took 6 agents, 499 calls and about 90M input tokens (2026-10-06). -->
- Search budget: two web searches per decision, for how other pin assigners and board tools handle conflicts (for example PlatformIO, ESPHome, KiCad's ERC), stopping at the first good match <!-- REQUIRED:budget -->
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
- Q0 · Is this frame right: the decision, the start and reach, the extensions and the depth? · decides: the frame · status: answered D3 <!-- REQUIRED:q0 -->
- Q1 · How important is each assumption, and what pass line must the riskiest test meet? · decides: importance and pass lines · status: ⟨fill⟩ <!-- REQUIRED:q1 -->

## Decisions
<!-- D<n> · what · who · when · where recorded · options considered.
A yes covers only the actions and choices it names. A standing yes names its kind of action and its source.
Name what a D confirms in its words: the frame, the jobs, a direction, the remaining risk, a test, items.md. -->
- D1 · option B for the GDI cable: ask "cable or wires?", then place the connector's pins first, with a check that stops on a conflict that is left · the PO · 2026-11-07 · AskUserQuestion, issue #892 · options: A place without asking, B ask then place, C warn only, D keep what is wired
- D2 · finish the refactoring soon; the conflict model lands on the core · the PO · 2026-11-07 · this session, his words in the frame · options: none offered
- D3 · Q0: the frame is confirmed, with a FULL council instead of TRIO · the PO · 2026-11-07 · AskUserQuestion · options: as written, FULL, keep P663 a story, change it

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
