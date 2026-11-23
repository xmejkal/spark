# P1039, spark past the MVP: the direction in one picture

A synthesis of six lens reports (council/), written on 2026-11-23 by the architect agent and revised after the refuter (council/refuter.md). It proposes and decides nothing. A ★C number points to a claim in [the brief](brief.md), with its caveat there. E is evidence with a pointer, H is a hypothesis with its source, D is a decision with who and when. Every recommendation says whose opinion it is.

## The short version

1. Opinion (the architect's, Q3's option a, not decided): past the MVP, spark is one line from a vague idea to a gadget in use. Today the flow never shows a deploy as done (E ★C19). After its first deploy the PO's gadget went on in its own repository and kept using spark's deploy step (E ★C20, one reading of two, n = 1). Past the breadboard the line is thin (E ★C21).
2. Opinion (the architecture lens's, shared by the architect, not tested: A9): the architecture needs no second design. The core calls no model (E ★C1) and its seams exist in the code (E ★C9, ★C10). 15 of 27 CLIs are off the core, and no second interface has run (E ★C7). What ties spark to Claude is frontmatter and variables in the agent layer (E ★C2), names in the areas' code (E ★C3) and at least seven yes gates (E ★C11).
3. The PO asked for all five directions (D, #1522). A second agent harness is installed on his computer, and nothing of spark has run in it (E ★C6). Opinion (the architect's, with the risks lens): seams only and no new epic now. The PO's own answers say which direction has a pull (A1), and that direction gets the first spike. The cheapest proof for another harness needs no install (Q7, option b).

## The product past the MVP: the factory line

"Exists" means that a spark step does it. "Partly" means that it works with a named gap or by hand. "Missing" means that nothing does it.

| # | stage | today | what the evidence says |
| --- | --- | --- | --- |
| 1 | shape the idea, the needs | partly | `/spark:idea` writes needs. The README reads "partly" for Idea (E council/risks-and-assumptions.md:19, RA-6) |
| 2 | know what you own, research a part | partly | a researched record guessed the wrong controller, with 3 of 33 facts verified (E UJ-14, an account) |
| 3 | pick parts, on the page or in the chat | partly | four round trips for four picks on the page (E UJ-10, an account). The page is P1038 #1521's own discovery |
| 4 | build and check the board | partly | Build and Checks read "works" in the README (E RA-6). A built board with no Wokwi model shows "could not run" (E UJ-12, P1008 #1467) |
| 5 | wire the breadboard from the sheet | partly | one walk wired from text, because a stale store copy cost the picture (E UJ-9, an account) |
| 6 | settle a fact at the bench | missing | done by a hand-written trial firmware (E UJ table, step 10). P1003 is in Idea |
| 7 | firmware, written by the conversation | exists, by decision | spark exports facts, never behaviour (D the firmware decision, AGENTS.md) |
| 8 | simulate | partly | no Wokwi model for the C6 (E UJ-12) |
| 9 | look and deploy | partly | it works after three fixes of 2026-11-22, as the lens reports (E ★C20). The phase never shows as done (E ★C19) |
| 10 | debug the running board | partly | `live.py` exists. mpremote failed on that board before P1007, so the walk used a scratch helper (E ★C15) |
| 11 | keep what the bench taught | partly | by hand, after a yes each time. P1002 #1461 is in Idea (E UJ-9) |
| 12 | iterate the gadget after it runs | partly | 36 commits in the walk's own repository, with spark's deploy step still in use (E ★C20, one reading of two). The flow's nine phases end at deploy (E council/architecture.md:48, AR-18) |
| 13 | PCB: Gerbers, parts list, rules | partly | a draft layout and a hand command, with the review skill as the gate before anything is fabricated. No walk made one (E ★C21) |
| 14 | order the PCB | missing | "not designed yet" (E ★C21). The effect words have no word for money or an order (E ★C22) |
| 15 | enclosure and 3D model | missing | P203 #163 is open (E ★C21). The CAD tool is H (council/architecture.md:175) |
| 16 | print or fabricate, wait, receive | missing | a wait of days fits the flow's files and a phase reader, not one run (opinion, the architecture lens's, council/architecture.md:176) |

Opinion (the architect's, Q3, not decided): the next product step is the end of the line (stages 9 to 12), not its extension (13 to 16). Q14's answer says whether the PO's own gadget left the line or stayed on it (★C20). That every later stage fits the core as more Operations, effect words and phases is the architecture lens's reading, and no stage was tried (H ★C22). An unattended line that writes behaviour is a proposed no-go (D the firmware decision).

## The architecture today

```mermaid
flowchart TB
  subgraph person["A person"]
    chat["the chat in Claude Code"]
    page["the page: a Claude Artifact, read and three kinds of click"]
    term["own terminal: the deploy's yes, a grant"]
    sheet["the breadboard sheet"]
  end
  subgraph claude["Claude-specific"]
    bind["binding: plugin.json, .mcp.json, CLAUDE_PLUGIN_ROOT, allowed-tools, model fields, Artifacts, transcripts for cost, the prompt that asks before a network step"]
    know["agent knowledge: 9 commands and 4 agent files, Claude Code frontmatter and variables around plain Markdown"]
  end
  open["agent knowledge in open formats: 3 skills, the agents' guide, AGENTS.md"]
  subgraph neutral["Plain Python, calls no model"]
    cli12["12 CLIs through run_cli, JSON in four shapes"]
    cli15["15 CLIs off the core, 8 with no --json"]
    ops["Operations in 8 tables, the flow with 9 phases, deploy never done"]
    core["core contract: OperationResult, effects, Question and ReplyStrategy, Event with 2 kinds, a trace hook with no caller"]
    store["records and the person's store"]
  end
  chat --> know
  chat --> open
  know --> bind
  open --> bind
  bind --> cli12
  bind --> cli15
  page --> bind
  term --> cli12
  cli12 --> ops
  cli15 -. "own logic, not Operations" .-> store
  ops --> core --> store
  ops --> sheet
  ops -. "sentences name Claude and /spark: commands" .-> claude
```

Sources: E ★C1, ★C2, ★C3, ★C7, ★C8, ★C9, ★C10, ★C11, ★C19. Nobody counted the Operations in the eight tables: one lens counts 51 Operation classes and another writes about 40. The layers follow the layer diagram of the architecture lens (council/architecture.md:85-131).

## The proposed target

Opinion (the architecture lens's, council/architecture.md:81 and :112-118, shared by the architect). Nothing in it is decided. Dashed boxes are not built.

```mermaid
flowchart TB
  subgraph person["Interfaces for a person"]
    text["terminal text with one layout: status, fix, next step"]
    page2["a page that renders the derived show-flow read"]
    term2["own terminal: the yes to a flash"]
  end
  subgraph ai["Interfaces for an AI"]
    cli["every journey CLI on the core, one envelope, a next step in every answer"]
    lines["events as JSON lines"]:::planned
    mcp["a stdio MCP adapter"]:::planned
    lg["a LangGraph node, P417"]:::planned
  end
  subgraph knowledge["Agent knowledge"]
    skills["skills in the Agent Skills format, short, because next carries the path"]:::planned
    guide["the agents' guide with a short first layer"]:::planned
  end
  subgraph bindings["One small binding per harness"]
    cc["Claude Code binding, the first one: Claude-specific"]
    other["a second harness binding"]:::planned
  end
  subgraph corebox["One core, calls no model"]
    cat["one catalogue of Operations with their declared keys"]:::planned
    ops2["Operations and a flow whose phases end and go past deploy"]
    contract["core contract: effects with consent for the network, typed Questions, events for begin, line, end and finding, a trace hook with a session id passed in"]
    store2["records and the store, behind one Storage, P1033"]
  end
  server["one local server for a live page and the HTTP MCP, only when the live page is ordered"]:::planned
  text --> cli
  page2 --> cli
  term2 --> cli
  cli --> ops2
  lines --> contract
  mcp --> cat
  lg --> cat
  cat --> ops2 --> contract --> store2
  skills --> cc
  skills --> other
  guide --> cc
  guide --> other
  cc --> cli
  other --> mcp
  other --> cli
  server -.-> lines
  contract -. "optional adapter, on a yes" .-> trace["a tracer, such as Langfuse over OpenTelemetry"]:::planned
  classDef planned stroke-dasharray: 5 5
```

What changes between the two pictures, as seams on the core work in flight (Q5 in the brief):

| seam | what it keeps open | evidence |
| --- | --- | --- |
| S1 an area's sentence says the job, and each interface adds its own how | another harness, a local model | E ★C3 |
| S2 consent in the core for every network operation, at least seven today | the gates in any harness | E ★C11 (nobody listed them from the code) |
| S3 one catalogue of Operations, each with its declared keys | MCP, LangGraph, a knowledge guard | E ★C9, ★C14 |
| S4 one envelope, a next step in every phase's answer, the four journey CLIs on the core | every interface, a smaller model | E ★C7, ★C12 |
| S5 event kinds for a step done and a finding, and a JSON-lines Reporter | streaming with no server | E ★C8 |
| S6 the session id and the cost as values that the harness passes, and a first caller of the trace hook | evaluation in any harness | E ★C17, ★C3 |
| S7 no absolute path in a next step for a remote client | a page or an MCP client on another machine | E council/feasibility.md:246 (FE-21) |
| S8 phases that end and go past deploy, effect words for money and an order | the factory's later stages | E ★C19, ★C22 |

## The interface options, for the PO's question

The PO, 2026-11-23, #1522: "What are other ways of separating the interface and the core, and what are other options in general for the human interface and AI interface at the same time?" The verdicts are the architecture lens's opinion (council/architecture.md:61-83), not a decision.

| # | family | spark today | the lens's verdict |
| --- | --- | --- | --- |
| 1 | scripts with a JSON answer and thin human views | 12 of 27 CLIs on the core, four JSON shapes (E ★C7) | keep, and "keep" means "finish": P793's pieces |
| 2 | a core library with ports and adapters | exists: `run_operation`, the outside world, the Reporter, the ReplyStrategy (E ★C9, ★C10) | keep. It is what "one core" means |
| 3 | one state document that every view renders | the derived `show-flow` read with its fingerprint (E council/architecture.md:28, AR-9) | keep as a derived read. A stored document is a second truth |
| 4 | a local server with one API | none, and the core has no async code (E ★C8) | later, one server, only when the live page is ordered, after the CLI and a stdio MCP are whole |
| 5 | an MCP server as the AI interface | the tool schemas exist, no server (E ★C9) | add, stdio first. It gives tools and no knowledge |
| 6 | a protocol of spark's own, shaped like a language server | none | no. A new protocol where MCP exists breaks "few" |
| 7 | skills as folders of text and scripts | 3 skills, and 9 commands and 4 agent files with Claude Code frontmatter (E ★C2) | add. In the lens's opinion the cheapest carrier of knowledge. No source says how another harness resolves the plugin's variable, and Hermes loads a project's skills only after a trust step (E ★C4, ★C5) |
| 8 | a durable workflow engine | none. The flow reads files | no for now. It breaks "free, few and local" |
| 9 | an editor protocol for agents (ACP) | spark is no agent (E ★C1) | no work. It is the harness's layer |
| 10 | agent-to-agent protocols (A2A) | spark has no agent of its own | no for now. Reopen if spark ships an agent |
| 11 | events as JSON lines beside the answer | the Reporter seam exists (E ★C8) | add. It serves the streaming rule before any server |
| 12 | an instructions file (AGENTS.md) | `/spark:init` writes one in each project (E council/feasibility.md:236, FE-19) | keep, free of Claude-only words |
| 13 | a UI generated from the schemas | the schemas exist (E ★C9) | a question for the page's discovery, P1038 #1521 |

The lens's order: 1, 2, 3, 11, 7, 5, then 4. The epaper session's leaning (keep 1 and 3, add 5, no server until a case needs it) misses 7 and the neutral sentences (E council/architecture.md:50-59). On the server the two do not differ: the PO's words are "when we'll want to use", a future wish, and a core that is ready for a consumer fits "no server until a case needs it" (council/refuter.md:51). No other lens proposes another order. The risks lens warns against a second redesign while P793 is in flight (H, pre-mortem 8).

## The use cases

Each line names what the person does and sees, and what the AI reads and calls.

| use case | the person does and sees | the AI reads and calls | today |
| --- | --- | --- | --- |
| U1 a vague idea becomes a deployed gadget (J1) | talks, picks on the page or in the chat, wires from the sheet, types the yes in his own terminal, sees the gadget run | the commands and skills, `flow.py show --json`, `parts.py`, `check_spine.py`, `look.py`, `deploy.py --json` | ran once (E ★C20, n = 1) |
| U2 the gadget changes after it runs (proposed J7) | asks where it stands, changes a part or the firmware, sees what is out of date | `flow.py show --json` with a deploy that reads as recorded | the deploy step is used, and the flow does not show it (E ★C19, ★C20) |
| U3 a PCB to order, then an enclosure (J1, later) | says yes to an order and pays himself, waits, receives | an export Operation, an order check, a phase that waits | by hand or missing (E ★C21) |
| U4 the same journey in another harness (J2) | the same chat in another tool, and the same yes in his terminal | AGENTS.md, skills, the scripts with `--json`, or MCP tools | not tried (H). A second agent harness is installed (E ★C6). The text says "Ask Claude" there (E ★C3) |
| U5 a small local model drives one step (J2) | the same, slower | one small answer with its next step, a few tools | not tried (H ★C27). The guide is too large for it (H ★C16) |
| U6 a change to spark reaches the agents' knowledge (J4) | the PO sees a red hook when a new script or flag is taught nowhere | the agent pages, generated from what the Operations declare | one direction only (E ★C13) |
| U7 the team sees whether spark got better, and which model did the job (J3) | the PO reads one row per release beside the journey picture (H, the UX lens's shape, council/ux-and-ai-ux.md:148) | a fixed task, graded by spark's own exit codes and phases | missing (E ★C17) |
| U8 the bench and the page show what Claude sees (J5) | reads the same status, fix and next step in the terminal and on the page | the same envelope | partly (E ★C12). The page is P1038's |
| U9 spark is shown as a project (J6) | a reader sees one picture of the line and the architecture | — | this page is the first draft (H) |

## The features, grouped by the five questions

| question | exists | partly | missing |
| --- | --- | --- | --- |
| 1 the factory | idea to build, the checks, the simulation, the deploy with its yes | bench facts, live debug, the write-back, the PCB draft | a deploy that shows as done, iteration, the order, the enclosure (E ★C19 to ★C22) |
| 2 harnesses, runtimes, boards, kinds of project | a core that calls no model, AGENTS.md per project, 3 skills, `--json` on 19 of 27 scripts (E ★C1, ★C7) | the firmware platform seam for MicroPython (D the PO, 2026-10-15 and 2026-10-31), bringing your own board (E UJ table, step 3) | neutral sentences, consent for the network in the core, a catalogue, an MCP adapter, commands in a portable form, a second binding (E ★C2, ★C3, ★C9, ★C11). Other runtimes wait on P356 #457 (E ★C28) |
| 3 evaluation and improvement | tests, mutation rows, walks with diaries and rows, learned rules, retros, `cost.py` (E council/feasibility.md:187, FE-15) | a docs guard in one direction, an inventory that is no gate (E ★C13) | a scored agent run, a measured model table, a join key across the sources, a guard for untaught names (E ★C14, ★C17) |
| 4 the core and its interfaces | the Operation contract, effects, typed Questions, the page from a derived read (E ★C9, ★C10) | 12 of 27 CLIs on the core, a next step for the build only, two event kinds (E ★C7, ★C8, ★C12) | one envelope, JSON-lines events, an MCP adapter, one human layout for every CLI (P1032 #1512) |
| 5 a local AI | small answers, and Claude Code's own road to a local model through Ollama (E ★C16, ★C27) | — | any run of spark on a local model, a short first layer of the guide, tools offered by phase (H, council/architecture.md:137, AR-21) |

## The options in full

The brief lists each decision's options on one line. Their cost and what each proves are here. Every cost is the architect's estimate (H). One agent wrote the costs and most opinions, so the table is one opinion, not a second source.

| decision | option | cost | what it proves | opinion (whose) |
| --- | --- | --- | --- | --- |
| Q2 the order against the MVP | a: the PO says what proves v0.10, and no direction leaves Idea before that | none | the one bar holds | the architect's, with the risks lens: this one |
| | b: one named exception runs beside the MVP | its tokens, named first | whether a direction runs without slowing the walk (A7) | the architect's: only for a test that needs no council |
| Q3 what "factory" means | a: the gadget's line gets an end (a deploy that reads as recorded, iteration), then the PCB, the order, the enclosure | flow work per stage | one conversation reaches a thing in use | the architect's: this reading, the end first |
| | b: the team's own process (a planner, a builder, a reviewer, human gates) | none new, it is scrum/README.md | nothing about a gadget | the architect's: this is how spark improves itself |
| | c: a line for software projects that are not gadgets | unknown, nobody read anything for it | — | none. It is the plain reading of the PO's words, and scrum/VISION.md is about gadgets |
| Q4 how the directions enter the backlog | a: seams only. This folder is the record, each direction is a line under "later", the existing cards carry them | one docs PR and one comment | nothing by itself | the architect's: now |
| | b: P1039 stays the one epic, with at most three spikes | up to 3 cards | A1's direction, A2, A4 | the architect's: per direction that passes A1 |
| | c: five epics | 5 epics beside 43 open ones, and a discovery each | nothing more | the architect's and the risks lens's: no |
| Q5 the seams | a: S1 to S7 as acceptance lines on P793 #1105's open pieces | one comment | no direction is closed off, and nothing is built for one | the architect's: this one |
| | b: P793 goes on as planned, the seams after it | none now, then a second wording pass and a second consent pass | nothing | the architect's: no for S1 and S2 |
| Q6 the split | a: finish today's split in the order 1, 2, 3, 11, 7, 5, and one server only when the live page is ordered | P793's pieces, one Reporter, one adapter | a second interface with 0 lines changed in the core (A9) | the architecture lens's, shared by the architect: this one |
| | b: the epaper session's leaning: 1 and 3, a thin MCP adapter, no server until a case needs it | less | MCP tools only, and no knowledge travels | the architecture lens's: it misses skills and the neutral sentences |
| | c: a server, a protocol of spark's own or a workflow engine first | a long-lived process, or a new protocol, or a service | live streaming to several clients, runs of several days | the architecture lens's: no for now |
| Q7 harness generality | a: a property kept by S1, S2, S3 and by AGENTS.md and SKILL.md | nothing beyond Q5 | nothing run | the architect's: now |
| | b: a trial with no install. In the second agent harness on the PO's computer, export the plugin's variable and ask for `flow.py show --json` on a fixture and the next step | model use on the PO's own account there, and his yes | whether the first step runs with "about 0 code" (FE-12). One step, not the journey | the refuter named it. The architect's: the first proof |
| | c: an audit of each Claude-only construct per command, then the job of `/spark:build` in one other harness | one agent on the everyday model, then model use | A2 | the risks lens's test: after b |
| Q8 the knowledge's form | a: skills carry the journey, the commands shrink after P793's pieces 1 to 3 | a rewrite of 9 commands and 4 agent files | whether a harness that reads skills can follow the journey | the architecture lens's, shared by the architect: later |
| | b: no change until then | none | nothing | the architect's: now |
| Q9 the guard | a: no guard now. Search from each untaught name into the P934 diaries for a moment where it was the tool for the job | one read-only agent | whether an untaught name ever cost a step (A6) | the architect's, with the risks lens: first |
| | b: `tools/inventory.py` counts agent pages only and runs in the hook for scripts and flags | one test, and a rule for "taught" | a new script or flag fails the hook until an agent page names it | the architect's: if a finds a case, and after the catalogue |
| Q10 evaluation | a: the PO names one row of the model table and the result that changes it | one question | that a result has a reader (A5) | the risks lens's, shared by the architect: first |
| | b: one fixed task inside Claude Code, reruns, graded by spark's exit codes and phases, tokens from `cost.py`, `--no-publish` | the runs' tokens, named first, outside the hook | A4, whether reruns agree | the architect's: second |
| | c: Inspect or promptfoo across harnesses, a tracer on the trace hook | installs and model runs per harness | one task set for J2 and J3 | the architect's: when a second binding exists |
| Q11 a local AI | a: one line under "later", and S4 | none | nothing | the architect's, with the risks lens: now |
| | b: a small model reads 10 golden answers, or `claude plugin eval` runs against a local model (not tried, EX-25) | a download, almost no tokens | A3 | the architect's: once the machine is named |
| Q12 the person's yes | a: every gate for hardware, the store, money or the network in a script | consent for at least seven network operations, a list of the other gates | the gates hold in any harness (A10) | the architect's: this one |
| | b: the harness's prompt stays the gate | none | nothing. An allow rule or auto mode already skips it | the architect's: no |
| | c: an elicitation "accept" or a click stands for the yes | a change to never-assume.md, rule 7 | the page and an MCP client reach the bench | the UX lens leaves it to the decider. The architect's: no for a flash |

## How spark evaluates itself, as a loop

```mermaid
flowchart LR
  walk["a walk: free-form, a diary and rows, no score"] --> row["a row: raised, acted or dropped"]
  row --> card["a card, or a fix during the walk"]
  card --> change["a change to spark, through the hook: tests and mutation rows"]
  change --> teach["the agents' knowledge: commands, skills, guides"]
  teach --> evalrun["a scored run on a fixed task"]:::missing
  evalrun --> table["the model table and the skills' text"]:::missing
  table --> walk
  teach -. "no guard for an untaught name" .-> walk
  row --> rules["learned rules and the retro"] --> walk
  classDef missing stroke-dasharray: 5 5
```

- Walks: they exist and stay without a score (D the PO, 2026-10-31). Rows become cards: of the 20 cards that the lens lists from two runs, 6 wait in Idea (E council/users-journey.md:112, UJ-17).
- Evals: none scores an agent, and two earlier evals of other things were pruned (E ★C17). Free tools exist (E ★C18). Opinion (the architecture lens's): a scored run is a new kind of run beside the walk, graded by facts that spark already holds, such as the phase reached and the count of `needs_reply` loops (council/architecture.md:155-162).
- Model choice: set by hand (E ★C17). Opinion (the risks lens's, shared by the architect): the PO first names one row and the result that changes it, and only then does a test run (A5).
- Agent knowledge: guarded in one direction (E ★C13). The walks hold no clean case of an untaught name, and rows undercount that cause (E ★C15). Opinion (the architect's): search from the untaught names into the walks before any guard is built (Q9).
- What the loop costs: a full council is put at "about 90 M input tokens", with no measurement on file (E ★C26). 174 issues were filed against 95 closed in the 7 days to 2026-11-23, a ratio that measures the filing rule too (E ★C24).

## What this page does not show

Nothing of spark has run in another harness or on a local model (E ★C6). No hobbyist has used spark (E ★C23). No option was tried. The card's words on other boards, other kinds of project, IDEs, CI and benchmarks have no finding here. The refuter read the first version of this page, and its points are applied (council/refuter.md).
