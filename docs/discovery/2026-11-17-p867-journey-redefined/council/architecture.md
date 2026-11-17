# P867 #1234, council: the architecture lens

Read on 2026-11-17, about 08:15 to 08:45 Europe/Prague, on the branch `p867-journey-discovery` at 12f13aee. Tags: E
(evidence, with a pointer), H (a hypothesis, with where it comes from), D (a decision, with who and when), — (unknown).
The three shapes in AR-12 to AR-14 are options with their costs. Nothing here is decided or recommended as decided.

## Findings

### What exists, as a model (a)

- AR-1 · The journey is defined today in at least five places: (1) the tuple `PHASES` of nine
  names, (2) the tuple `READERS`, nine objects whose order must equal `PHASES` by a comment, (3) the EPILOG of
  `flow.py` and docs/guide/agents/flow.md, which repeat the nine names as prose, (4) `tools/journey.py`'s `STEPS`, a
  second list with other names and another cut (Drawer, Idea, Research, Build, Checks, …), which draws the README's
  picture, (5) commands/*.md and skills/spark-design/SKILL.md, which say the order as sentences · E
  scripts/spark/flow/flow_codes.py:9, scripts/spark/flow/phase_readers.py:268-269, scripts/flow.py:17-31,
  docs/guide/agents/flow.md:13-14, tools/journey.py:28-40, commands/build.md:108,137, skills/spark-design/SKILL.md:106 ·
  supports only: that the names and the order exist more than once. I did not check whether a test compares (1) with (2)
  or (4) (tests/test_flow.py and tests/test_journey.py were not read).

- AR-2 · What is data today: the phase names and their order (`PHASES`). The three phase words `not-started`, `partial`,
  `stale`. Who does a phase (`BY_YOU`, `BY_CLAUDE`, `BY_TERMINAL`). The four offer kinds (`PICK`, `NEEDS_DROP`,
  `WRITE_REQUIREMENTS`, `BUILD_BOARD`). The status-to-word-and-glyph table `MARKS`. Every sentence, as a constant ·
  E scripts/spark/flow/flow_codes.py:9-20,26-58, scripts/spark/flow/phase_readers.py:30-32 · supports only: the
  vocabulary is data. No dependency, no transition and no "out of date" rule is in these tables.

- AR-3 · Every dependency and every "out of date" rule is code inside one reader, and each uses its own mechanism. There
  are four mechanisms for the same question, "was this made from what is there now?":

  | edge (made from → made) | rule | mechanism | pointer (E) |
  | --- | --- | --- | --- |
  | needs and picks → requirements.json | stale when what the picks give differs from the file | recompute and compare the content | phase_readers.py:172-175 |
  | requirements.json → the build | stale when the file's sha256 differs from `requirements_sha256` in `.spark/build.json` | a stored input hash | phase_readers.py:179-185, scripts/spark/build/build_record.py:28-30 |
  | requirements.json → breadboard.md | stale when the build is, or when the copy in `dist/board/built-from.json` differs from the file | a stored copy of the input | phase_readers.py:81-88,218, scripts/spark/breadboard/sheet.py:97-99 |
  | firmware/ → the flash image | "changed after the image" | file times (mtime) | scripts/spark/firmware/project_image.py:106-110 |
  | the image → a passed run | a run counts only if its log names the image's sha256 | a stored input hash, in the run log | project_image.py:81-95 |
  | the image → the board on the bench | the store keeps `image_sha256` per deploy, by the board's MAC | a stored hash, readable only with the board on USB | scripts/spark/records/deploy_record_store.py:94-102 |
  | the sheet → the wired breadboard | `wiring-record.json` keeps what the earlier sheet told the person to wire, and a rebuild prints "Changes since the last build" | a stored copy of the output | scripts/spark/breadboard/bench_changes.py:1-16 |

  supports only: these seven edges exist in code. The edges firmware/pins.py → firmware/main.py and the build →
  board.tsx are not in any reader (AR-5).

- AR-4 · "Out of date" does not travel along the line. On the walk folder `p711-sound-demo`, `flow.py show` says
  requirements is `↻ out of date`, and in the same answer build is `✓` and breadboard is `✓`, because each compares
  itself only with the requirements.json on disk, which nobody wrote again · E the command
  `SPARK_HOME=<the store> python3 scripts/flow.py show --project spark-walks/p711-sound-demo`, run 2026-11-17,
  exit 0: "↻ requirements: out of date, requirements.json differs from what the picks give", "✓ build: the last build,
  2026-11-17T07:59:38+01:00: ok", "✓ breadboard: breadboard.md", "stands at: requirements" · supports only: one project,
  one moment. `stands_at` still names the right first phase. The marks after it read as done.

- AR-5 · Three things that the walks saw of a change in the middle have no rule anywhere, data or code: (1) the firmware
  names pins the new pins.py lacks: `FirmwareReader` reads only whether main.py is there and its time, and the only hint
  is a sentence in the drop Operation, (2) spark's own unedited board.tsx is reported as "traces differ", because spark
  keeps no record that it wrote the file, (3) a refused build removes the earlier pins.py, sheet and page · E
  scripts/spark/flow/phase_readers.py:223-233, scripts/spark/idea/drop_need.py:28-29, scripts/spark/build/kept_files.py:39,
  :301-306, :324-328, :401-409, spark-walks/p711-sound-demo/rows.md row 13, #1234's comment · supports only: the rules
  are absent in the flow reader, (3) is written behaviour of the keep step (P280), not an accident.

- AR-6 · The transitions exist in three unconnected forms. (1) An offer: `{key, effect}`, a key and one sentence, with no
  argv, no effects list and no statement of which phases it makes out of date. (2) A `next` step of the envelope:
  `{op, argv, why, effects, needs_yes, needs_person, env}`, produced by the bench Operations and the record kinds,
  `ShowFlow` returns none. (3) Prose: "run parts.py --requirements … or edit the file, then build" in a note, and the
  order of the commands in commands/*.md · E scripts/spark/flow/phase_readers.py:36,
  scripts/spark/core/outcomes.py:114-122, scripts/spark/bench/board_envelope.py:52,73,106,
  scripts/spark/flow/show_flow.py:61-68 (no `next` passed), scripts/spark/idea/drop_need.py:28-29 · supports only: an
  offer and a `next` step are two shapes for "something that can be done next", and the flow's answer uses only the
  weaker one. The mapping from an offer kind to a script is planned for P829's `RunRequest` and is not in the code yet
  (flow_operations.py:1-4).

- AR-7 · `Operation` already carries the facts a generated interface needs: `name`, `arguments`, `effects` (reads, runs,
  board, deletes, writes, asks, fetches), `data_keys`, `input_schema()` and `output_schema()`. It does not say what it is
  made from or what it makes (no file or record names), so no graph can be derived from the Operations today · E
  scripts/spark/core/operation.py:31,65-115 · supports only: the shape of the class, P417 #545 (the LangGraph spike) is
  open and proved nothing yet (gh issue list, 2026-11-17).

- AR-8 · "revision" (P820's plan: the sha256 of needs.json, requirements.json and .spark/build.json together) is not in
  the code, and neither it nor "phase", "offer" or "request" has a row in docs/guide/patterns-and-names.md, though the
  plan says they were added there · E `/usr/bin/grep -rn -i revision scripts/spark scripts/flow.py` gives only
  unrelated uses (replies.py:31, drawer.py:28, physics_check.py:404), `/usr/bin/grep -n -i -E "\bphase|\boffer|\brequest\b|revision"
  docs/guide/patterns-and-names.md` gives one line (49) with none of them as a defined word,
  docs/discovery/2026-11-15-p820-artifact-interface/mvp-plan.md:54-63 · supports only: the four words live in the plan,
  in flow_codes.py and in flow.md, not in the names table.

- AR-9 · The bench state is not readable from the project's files, but two witnesses of it are already recorded: what the
  last sheet told the person to wire (`wiring-record.json`, in the project) and what the last deploy wrote (the store's
  record by MAC, with `image_sha256`, `project` and `verdict`). `DeployReader` reads neither and always answers
  `not-started`. The look reads the deploy record only with the board on USB · E
  scripts/spark/flow/phase_readers.py:258-265, scripts/spark/records/deploy_record_store.py:28-36,94-102,
  scripts/spark/breadboard/bench_changes.py:1-9, spark-walks/p711-sound-demo/wiring-record.json · supports only: a
  witness says what spark last told or did, never what is on the bench now (rows.md row 16: a joystick in the record,
  not on the gadget). The core has a three-state rule for exactly this kind of reading: `recorded`, `none-recorded`,
  `not-checked` (scripts/spark/core/outcomes.py:35-49).

- AR-10 · The line of nine cannot say which phases need which. From the code's own edges (AR-3), breadboard and firmware
  both come from the build and neither needs the other. Simulate needs the firmware and the build's diagram, not the
  wired breadboard. Deploy needs the image and, for the gadget to work, the wired breadboard · E the table in AR-3,
  H for "deploy needs the wired breadboard" (physics, not in the code) · supports only: the dependency structure in the
  code is a graph already. The tuple flattens it into one order.

### Three candidate shapes (b, c)

- AR-11 · A fact that bears on all three: `stands_at` is defined as "the first phase whose status is neither ok nor
  None", and three phases (idea, firmware, simulate) answer None by design, because spark does not judge them · E
  scripts/spark/flow/show_flow.py:64, docs/guide/agents/flow.md:27-30 · supports only: any shape must say how a phase
  that spark cannot judge takes part in "out of date". A None cannot become `stale` without a recorded witness.

- AR-12 · Candidate 1, the line extended: a table of phase definitions and a rule that "out of date" travels down the
  line · H this lens, from AR-1 to AR-4.

  ```mermaid
  flowchart LR
    idea --> needs --> parts --> requirements --> build --> breadboard --> firmware --> simulate --> deploy
    requirements -. "stale here makes every later done phase stale" .-> deploy
  ```

  - Data: one table, a row per phase: name, who does it, the files it reads, its offer kinds, its screen. `PHASES` and
    `READERS` become one table, so the order is written once. One rule in `ShowFlow`: a phase after the first phase that
    is `stale`, `partial` or `not-started` cannot read `ok`.
  - Stays code: each reader's own comparison (the four mechanisms of AR-3).
  - "Go back": take an offer of an earlier phase. Everything after it reads `stale` until made again. Nothing is undone.
  - "Add another joystick": a new need, so parts is `partial`, and all seven later phases read `stale`. Too wide: it
    says the firmware is out of date even when no pin moved, and it cannot say that the breadboard and the firmware are
    independent (AR-10). It also does not answer AR-5 (the pins a firmware names).
  - Bench: stays two phases at the end with `by: you` or `your terminal`. The wired breadboard has no place except as
    the breadboard phase's sentence.
  - Interfaces: the CLI's lines and `--json` are as today, with more `stale`. The page's rail is the line. A framework
    gets a chain of nine nodes, which adds little over calling `flow.py show` in a loop.
  - Refactor: `flow_codes.PHASES` and `phase_readers.READERS` into one table of a small Value (a working name,
    `PhaseDefinition`), `ShowFlow.run` gains the rule. Pattern names: Strategy for the readers (Gamma et al., Design
    Patterns, 1994, already the word in patterns-and-names.md:15), the line itself is Pipes and Filters (Buschmann et
    al., Pattern-Oriented Software Architecture, 1996) · H model knowledge for both citations, not read today.
  - Smallest first slice that proves it on a real change: on `p711-sound-demo` as it stands (AR-4), build and breadboard
    read `stale` with a sentence that names requirements as the cause. One rule, one fixture.
  - Costs: the least code. No new record. It over-reports, it cannot hold the PO's added phases (shops, what to
    validate, the PCB) except as more places in one line, and the definition still does not say what a phase is made
    from.

- AR-13 · Candidate 2, a dependency graph of the things spark makes: each is made by one Operation from named inputs,
  and it is out of date when the recorded hash of an input differs from the input now. The phases are views over the
  graph · H this lens. The mechanism exists in two places already (AR-3: `.spark/build.json`, the run log).

  ```mermaid
  flowchart TD
    goal["goal (chat; not stored)"] --> needs[".spark/needs.json: needs and picks"]
    drawer[("store: drawer, records")] --> needs
    needs -->|"write requirements"| req["requirements.json"]
    req -->|"build"| build[".spark/build.json, dist/board, board.tsx"]
    build --> pins["firmware/pins.py"]
    build --> sheet["breadboard.md, page.html"]
    build --> diagram["sim/diagram.json"]
    pins -. "names imported" .-> fw["firmware/main.py (Claude writes)"]
    fw --> image["the flash image"]
    diagram --> run["sim/runs/*.log (names the image's sha256)"]
    image --> run
    sheet -. "witness: wiring-record.json" .-> wired(["the wired breadboard (bench)"])
    image -. "witness: the store's deploy record, by MAC" .-> flashed(["the flashed board (bench)"])
    subgraph phases as views
      needs
      req
      build
      sheet
      fw
      run
      flashed
    end
  ```

  - Data: a table of nodes: name, files, the Operation that makes it (or "the person", "Claude"), its inputs, the phase
    it shows under. Beside each made thing, a record of the input hashes it was made from (`.spark/build.json` holds
    one such hash today).
  - Stays code: how each thing is hashed or compared (the requirements comparison recomputes, which keeps its useful
    property: a changed need that gives the same requirements.json makes nothing out of date). Each Operation. Every
    sentence.
  - "Go back": no separate act. Changing any input makes exactly the things downstream of it out of date. What is kept
    is everything not downstream. "What do I lose" is the downstream set, computable before the change.
  - "Add another joystick": needs.json changes. Requirements.json is out of date. After it is written again and built,
    pins.py either has the same hash for the part that stays (firmware not out of date) or not. This answers the walks'
    open question "do the pins of the parts that stay move?" as a fact read from two files, and AR-5 (1) becomes an
    edge, pins.py → main.py, if something records which pin names main.py was last checked against (import_firmware.py
    is the existing place that looks).
  - AR-5 (2), spark's own board.tsx: a record of the hash of what spark wrote tells "unedited, spark's" from "edited by
    hand", so spark can replace the first and must ask about the second.
  - Bench: a bench node has no file to hash. It fits as a node whose state is one of the reader rule's three words
    (AR-9): `recorded` with what the witness says and when, `none-recorded`, or `not-checked`. It never reads `ok` from a
    witness alone. It does not fit the hash rule itself: "the breadboard is wired as the sheet says" can only come from
    the person (a reply) or from a look.
  - Interfaces: the CLI can keep its nine lines, each phase's status computed from its nodes, and add the cause
    ("because needs.json changed"). `--json` keeps `data.phases` and `data.stands_at` and could add a key for the nodes
    and edges. The page's rail is the phases. A panel can show "made from" and "makes out of date" before a click. A
    framework gets the graph directly: a node per Operation, an edge per input, and a node done by the person becomes a
    pause for a human (LangGraph's `interrupt` and `Command`, with conditional edges by status).
  - Refactor: `build_record.BuildRecordStore` generalised from one `requirements_sha256` to named inputs, `sheet`'s
    built-from.json and `ProjectImage.find_newer_files` (mtime) move to the same check. Each `PhaseReader` asks one
    shared freshness check, `Operation` gains two declared tuples (what it reads as inputs, what it makes), beside
    `effects`, which is where a generated graph would read them (AR-7). Pattern names: a dependency graph with a
    "rebuilder" that decides whether a task must run again, here by "verifying traces" (recorded hashes), and "early
    cutoff" for the requirements comparison (Mokhov, Mitchell and Peyton Jones, Build Systems à la Carte, ICFP 2018 and
    JFP 2020) · E the search of 2026-11-17 (below), secondary summaries of the paper. The paper itself was not opened.
    GNU Make's own words are "target" and "prerequisite" · H model knowledge.
  - Names: "artefact" is not used in scripts/spark and has no row in the names table (grep, 2026-11-17), and it would
    read like "the Artifact page", which is already a thing here. A word for "a thing spark makes" is open (Q3). "stale"
    already means out of date and stays one word. "revision" (AR-8) would be the same input hashes under a second name.
  - Smallest first slice: rows.md row 13. The build records the hash of the board.tsx it wrote, the next build replaces
    an unedited one without "traces differ" and still reports a hand-edited one. One record field, one comparison, one
    walk row closed. A second small slice: AR-4's case, where build reads `stale` because its input is.
  - Costs: a new record shape and a migration of `.spark/build.json` (schema 1 is read "by the keys it knows",
    build_record.py:20-21), more recorded state in each project, the spark-is-not-a-build-system line must be held: it
    says what is out of date and which offer makes it again, and runs nothing by itself (D-d: no offer runs without a
    yes). Records grow by need (AGENTS.md): each edge enters only when a check or a walk row needs it.

- AR-14 · Candidate 3, a state machine with named transitions: forward, back, change · H this lens.

  ```mermaid
  stateDiagram-v2
    [*] --> not_started
    not_started --> partial: offer taken (some)
    not_started --> ok: offer taken
    partial --> ok: offer taken (all)
    ok --> stale: an earlier phase changed
    stale --> ok: offer taken again
    ok --> problems: offer taken, it found something
    problems --> ok: fixed and taken again
    not_started --> could_not_run: cannot look
    state "bench (person says)" as bench {
      told --> confirmed: the person's reply or a look
      confirmed --> told: a rebuild changed the sheet or the image
    }
  ```

  - Two readings, with different costs. (3a) One machine per phase, as drawn: the states are today's status words, and
    the transitions are a table `(phase, offer kind) → the phases it makes stale`. The state is still derived from the
    files, so it is the same information as candidate 2's edges, written by hand per transition and not derived from
    inputs. (3b) One machine per project with a stored current state: this needs a state file or a log of transitions,
    which is a second truth beside the files (against D-d, "the project's files are the truth", the PO, 2026-11-15),
    and nine phases with six statuses each do not reduce to a small set of project states.
  - Data: the transition table: name, from, to, the offer kind or the Operation, its effects, needs_yes, what it keeps
    and what it makes stale. Stays code: the readers, the Operations.
  - "Go back": a named transition, for example `change-needs`, whose row lists what it makes stale. Readable for a
    person ("back to parts: keeps the build's files, marks five phases out of date"). "Add another joystick": the
    transition `add-need` from any state, with the same row. The answer is as right as the row someone wrote: the
    question "did the kept pins move?" is not answered by a table.
  - Bench: fits best of the three in words, because a bench state can only change by an event (the person's reply, a
    look, a deploy), and a machine is made of events. It needs a place to keep the person's "wired" (a reply. The
    replies file exists, scripts/spark/core/replies.py).
  - Interfaces: the CLI can print "you can: …" from the table, `--json` could give each offer its transition. The page
    shows back and change as buttons, though D-d allows only four kinds on the page. A framework maps one to one:
    states to nodes, transitions to conditional edges, a person's transition to an interrupt.
  - Refactor: a table in the flow area (a working name, `flow_transitions.py`), `Offer` grows from `{key, effect}`
    toward the `next` step's shape (AR-6), so an offer and a step become one Value. P829's kind-to-script table is this
    table. Pattern names: a finite state machine as a transition table (Nystrom, Game Programming Patterns, the State
    chapter. Gamma et al., State). Parallel regions for the bench are Harel's statecharts (1987) · H model knowledge,
    not read today. LangGraph's words: nodes, conditional edges, `interrupt`, `Command` · E the search of 2026-11-17
    (docs.langchain.com/oss/langgraph/interrupts and /oss/python/4-human-in-the-loop, named in the results, not opened).
  - Smallest first slice: the drop of a need. `DropNeed` answers a `next` step built from the table (write the
    requirements, then build) in place of the sentence in drop_need.py:28-29, and `flow.py show` marks what the drop
    made stale. Proven on the walk's own case (a need dropped and another added, #1234's comment).
  - Costs: a hand-written table that can disagree with the code's real inputs, (3b) breaks D-d, "transition" is a new
    word beside "offer", "request" and `next` step, so one of them must absorb the others.

- AR-15 · The three are not exclusive in structure: 2 holds what candidate 1's rule and candidate 3a's table would
  otherwise write by hand (which phase makes which out of date), 1 is 2 with every edge drawn to the next phase, and
  3a's per-phase states are today's status words · H this lens, from AR-12 to AR-14 · supports only: a comparison of
  shapes, not a choice.

- AR-16 · Fit with AGENTS.md's direction, per candidate · H this lens, read against AGENTS.md (the principles):
  - One core, many interfaces: all three keep one reader behind `ShowFlow`. Only 2 and 3a put the transitions where a
    generated interface can read them. Today an agent's prompt (commands/*.md) repeats the order (AR-1), which the
    principle forbids ("An agent prompt never repeats its logic").
  - Facts, never behaviour: 2 exports facts (made from, hash then, hash now). 3's table says what should happen next,
    which is spark's own flow, not the gadget's firmware. Whether the principle reaches that far is the PO's (Q5).
  - Records grow by need: 2 adds a record field per edge, each tied to a walk row. 1 adds none. 3b adds a state file
    with no check that needs it.
  - Small class, one job: 1 and 3a are a table and a rule. 2 is a Store and one check, and removes three ad hoc
    mechanisms (AR-3).

### What must not get worse (d)

- AR-17 · The contract an agent reads today, each with its pin: `data.phases` (each `{phase, status, mark, by, says,
  offers}`) and `data.stands_at`, declared as `data_keys` and compared with a real answer by a test. Exit 0, 1, 2 from
  the Findings, problems winning. An offer is `{key, effect}` and its key is one of four kinds, `flow.py` runs no offer,
  the envelope's schema is the same for every Operation · E scripts/spark/flow/show_flow.py:56,64-68,
  scripts/spark/core/operation.py:83-85,112-114, scripts/spark/core/outcomes.py:23,52-53,
  scripts/spark/flow/flow_codes.py:20, docs/guide/agents/flow.md:11-47 · supports only: what is written. What each
  candidate risks:
  - A new status word (for example "stale because of an earlier phase") changes the set flow.md lists, reusing `stale`
    with a new sentence in `says` does not.
  - More or other phases change the "nine phases in order" that flow.md, the EPILOG and P827's "Done when" state as a
    number.
  - In a graph, several phases can be open side by side, `stands_at` is one name. Keeping it as the first open phase in
    the listed order keeps the key. A new key beside it is additive.
  - New keys beside `phases` and `stands_at` (nodes, transitions) are additive for a reader that ignores unknown keys,
    the `data_keys` test must name them.
  - The page: "Python writes every word, mark and effect line, the script only switches panels" (mvp-plan.md:92-95). A
    graph or a transition table rendered on the page must arrive as finished sentences and marks, never as edges the
    script walks.
  - The allowlist: "back" and "change" as page buttons would be a fifth and sixth kind, or must be expressed through the
    four (a drop, a pick). D-d is the PO's (2026-11-15).
  - A phase spark cannot judge (None) and a bench witness must never read as `ok` (AR-9, AR-11,
    docs/guide/agents/never-assume.md as named in AGENTS.md).

### The cards in Ready (e)

- AR-18 · P827 #1185 (the page shell) depends on one interface of the core: `ShowFlow`'s `data.phases`, a list of
  `Phase` values. Its "Done when" says "shows the nine phases" · E gh issue view 1185 (2026-11-17),
  mvp-plan.md:122-131,163-166 · H: a rail that renders the list it is given, in order, with each phase's mark and
  sentences, survives all three candidates and a changed number of phases. A rail with nine hard-coded panels does not.
  The number in the acceptance line is the part exposed to the redefinition.

- AR-19 · P828 #1186 (the views and the wiring steps) depends on the wiring steps and the before-power lines as data
  (P826) and on the inlined drawings, and on P827 · E gh issue view 1186 (2026-11-17), mvp-plan.md:167-168 · H: it
  touches no phase, status or transition, so the redefinition changes only which panel holds it. If the PO's order
  ("later the breadboard") moves the breadboard, that is a row in a table under any candidate.

- AR-20 · P829 #1187 (the requests) is the card that writes a second and third definition if it is built first: its
  table "each kind → its script and arguments" is candidate 3's transition table for four kinds, and its "revision"
  (the sha256 of three files together) is candidate 2's input hashes under another name, limited to three files (it
  leaves out firmware/, pins.py and the simulation, which is enough for its four kinds) · E gh issue view 1187
  (2026-11-17), mvp-plan.md:59,139-147 · H: built before the redefinition, both parts are small and would be folded
  into the definition later (a rename and a move, if the kind table is a table of Values and the revision is computed
  by one function). Built after, they are read from it. It depends on `ShowFlow`'s offers (key and effect) and on a
  channel seam (the comment on #1187 from P834).

- AR-21 · The acceptance of P829 walks forward only (Pick, then Requirements, then Build). No card in Ready exercises a
  change in the middle, so none of the three would show AR-4 or AR-5 · E gh issue view 1187, "Done when" · supports
  only: the cards' text.

## What I could not check, and why

- Whether a test ties `PHASES` to `READERS`, or `tools/journey.py`'s `STEPS` to the flow's phases: tests/test_flow.py and
  tests/test_journey.py were not read (time).
- The whole of `tools/journey.py`'s `STEPS` (only its first five rows were read) and the README's "What works today"
  table: so the exact overlap of the two lists of steps is —.
- P820's own architecture findings: the brief names "its council/ folder", but
  docs/discovery/2026-11-15-p820-artifact-interface/council/ holds existing.md, feasibility.md, physics.md, refuter.md,
  risks.md, user.md and ux.md and no architecture file, I read the plan's Council section (mvp-plan.md:3-17) only.
- The other two walks' rows (p711-identify-amp, p711-walk4-button-led) and page-notes.md: not read (time). The evidence
  of a change in the middle here is #1234's comment and p711-sound-demo/rows.md rows 6, 13 and 16.
- Whether a refused build still removes pins.py, the sheet and the page today: read in the code
  (kept_files.py:301-328, 401-409), not run, because the rules of this lens allow no build.
- Whether the pins of the parts that stay move when a part is added: scripts/spark/design/pin_assigner.py was not read.
  The walks did not look at it either (#1234's comment).
- scripts/spark/core/cli.py, privacy.py, scripts/spark/design/needs.py, need_requirements.py, pick_parts.py,
  write_requirements.py and scripts/spark/bench/ beyond board_envelope.py's `next` steps: only grepped, not read whole.
- The codebase graph tools were not used. Callers were traced with grep.
- The sources of the pattern names (Gamma et al., Nystrom, Buschmann et al., Harel, the GNU Make manual) and the
  Build Systems à la Carte paper itself were not opened today. LangGraph's documentation pages were named by a search
  and not opened. Each is tagged H or "secondary" where used.
- Docs/guide/developing.md and docs/guide/agents.md were not read whole, AGENTS.md's principles were read from the
  session's instructions.

## Questions for the decider

- Q1 · Is "out of date" a fact spark reads from what a thing was made from (candidate 2), a rule along one line
  (candidate 1), or a row someone writes per named change (candidate 3)? · decides the shape of the definition and
  which records each project gains.
- Q2 · May spark keep a stored "state of the project" beside the files, or is every state always read from the files and
  the store's records? · decides whether candidate 3b is open at all (D-d says the files are the truth).
- Q3 · What is the one word for "a thing spark makes from named inputs" (a file or a record such as pins.py or the
  build), given that "Artifact" already means the page? · decides the names of candidate 2 and whether "revision"
  stays a separate word.
- Q4 · Does the bench (wired, flashed) belong in the definition as something spark only has a witness of, shown as
  "recorded / none recorded / not checked", or as phases the person confirms by a reply? · decides whether a reply
  becomes an input of the flow and what the deploy and breadboard phases can ever say.
- Q5 · Does "spark exports facts, never behaviour" forbid a table that says which step comes next in spark's own flow,
  or does it speak only of the gadget's firmware? · decides whether candidate 3's transition table fits the product.
- Q6 · Are "go back" and "change" things a person can click on the page (new offer kinds beside the four), or do they
  stay the existing four kinds plus the chat? · decides whether D-d's allowlist is reopened.
- Q7 · Should an offer and a `next` step become one Value (key, effect line, argv, effects, needs_yes)? · decides the
  interface P829 builds on and what a framework's node is generated from.
- Q8 · Is P829's "Done when" to gain one change in the middle (drop a need after a build) before it is built, or does
  that wait for the redefinition's first slice? · decides whether P829 is built before or after, and what its revision
  covers.
- Q9 · Is "nine" part of the contract (flow.md, P827's acceptance), or may the number and order of phases change with
  the definition? · decides how P827's rail is written and whether flow.md's sentence is a promise.

## Searches

- "LangGraph StateGraph add_node add_conditional_edges interrupt human-in-the-loop documentation" · served: what a
  node-and-edge runner needs from the definition (a framework's graph, part b) · used: the words nodes, conditional
  edges, `interrupt`, `Command`, and the two official pages named in the results
  (https://docs.langchain.com/oss/langgraph/interrupts, https://docs.langchain.com/oss/python/4-human-in-the-loop), read
  as search results on 2026-11-17, pages not opened.
- "build system "out of date" target content hash instead of timestamp "Build Systems à la Carte" verifying traces
  rebuilder scheduler" · served: the industry names for candidate 2 (part c) · used: scheduler, rebuilder, verifying
  trace, early cutoff, and that Make compares modification times. Sources named in the results:
  https://www.microsoft.com/en-us/research/publication/build-systems-a-la-carte/ and the JFP 2020 version
  (doi:10.1017/S0956796820000088), read as search summaries on 2026-11-17, paper not opened.
- A third search was not made.
