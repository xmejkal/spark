# After v1: the cards the replan closes into version epics

2026-10-11. On the PO's yes (question 2), each closes as not planned into its version epic, linked from it, and reopens the moment the walk needs it. Chosen when at least two of the three lenses named it for pruning and neither slice uses it, plus P158 (#94) and the two cards that hang on its chip table, P187 (#136) and P189 (#138). Titles as the board read them on 2026-10-11.

## The store's redesign and hardening (one person, one local store is enough for v1)

- #17 [Idea] P94 — The store and its ways in, designed: an extendable, reusable architecture
- #19 [Idea] P87 — Records are inert: no record text can act, no record path can leave the store
- #20 [Idea] P89 — `--need` tells the truth about candidates
- #21 [Idea] P90 — A document comes back, checked
- #22 [Idea] P91 — A shelf for the parts you chose
- #23 [Idea] P92 — Records written through `parts.py`, read as JSON
- #82 [Idea] P148 — A project's own copy of a record falls behind silently: a read-only drift report
- #83 [Idea] P149 — A Wokwi chip has no identity: reuse by file time, silent name clashes, outside the record's digest
- #84 [Idea] P150 — spark writes compiled chips and promoted records into its own plugin folder, which an update replaces
- #85 [Idea] P151 — "verified" means four different things, and --show calls facts verified that cite no kept document
- #93 [Idea] P157 — Choosing among equivalent modules: offer every owned module with the same function, recommend the minimal one that fits — MCUs, drivers and sensors alike
- #96 [Idea] P160 — The store editor: work with every level of the store, and create, download or synchronize boards, modules and parts — designed for AI agents, with good UX for humans
- #99 [Idea] P162 — G, research only the gap: spark finds and offers new parts and boards for a need, owned or not, to buy — for example any board that runs MicroPython
- #101 [Idea] P164 — The real store has no guard against an agent's unscoped command: an export that did not persist listed twelve scratch projects in the PO's projects.json
- #114 [Idea] P174 — The store's write lock follows TMPDIR, so two processes with different temp folders can write one store at once
- #118 [Idea] P175 — parts.py --requirements writes back two hand-written entries that are one name and says nothing
- #119 [Idea] P176 — The component-name rule has a third copy: needs._called repeats emit_board.component_name, so an unnamed entry's default name is not checked where the file is read
- #123 [Idea] P178 — The next version is the store: one shared store online, a local store, projects pointing at local records synced with the shared one — a concept for the refactoring and a new UX, from a council over every store item

## Checks for bigger projects (rails, motors, I²C, copper, capacitors; button-and-LED has none)

- #9 [Idea] P38 — The capacitors P6 promised
- #41 [Idea] P107 — check_physics names a null it cannot use: a null rail voltage skips derating, a null bus capacitance crashes, a missing one is assumed 50 pF
- #43 [Idea] P109 — check_all reports the generator's CONFLICT lines: a problem on verified facts, a ? line otherwise
- #54 [Idea] P120 — The shipped L9110S and power-inlet records state their VCC current
- #55 [Idea] P121 — The XIAO ESP32-C6 builds, or spark says it cannot before it tries
- #56 [Idea] P122 — The I²C rise-time check runs on the boards spark generates
- #60 [Idea] P126 — The fabrication gate reads the board being ordered, and lists the dev board's own unverified facts
- #63 [Idea] P129 — The motor rail's net is not named for one project's battery
- #70 [Idea] P136 — Full circuit checks: analogue and board checks in spark (epic)
- #76 [Idea] P142 — Two I2C devices at the same address build and pass
- #78 [Idea] P144 — The trace-current rule ignores a project's copper thickness
- #79 [Idea] P145 — The floating-input rule raises false alarms on I2S lines and on pull-ups to unmarked supplies
- #86 [Idea] P152 — The VL6180X record and its Wokwi chip say the interrupt line works: no condition in the record, push-pull in the chip
- #87 [Idea] P153 — Three printed limits fail the rule that printed them (6 V, 0.18 mm, 3541 Ω)
- #89 [Idea] P154 — A council proposes one easy way to choose and switch engines, strategies and tools (local CLI or MCP), worth its cost for our use cases

## Mutation, QA and team tooling

- #27 [Idea] P102b — Maps and journeys as text, drawn in Miro and Canva
- #28 [Idea] P102d — Proofs run as commands; the map says proven or not
- #30 [Idea] P102f — The demo projects get a home: spark-demos
- #39 [Idea] P106 — The push gate measures the commits being pushed, in a clean environment
- #97 [Idea] P161 — Measure test coverage and QA quality: how far can we trust that what is said to work is tested and validated
- #103 [Idea] P166 — QA we can trust — how far what is said to work is tested and validated (epic)
- #108 [Idea] P170 — Time an issue spends in each state, and its waiting times, as process data in GitHub
- #111 [Idea] P171 — Clean after ourselves automatically: when a PR merges, the worktree, the branches, the temp folders and the scratch stores go, and the reports are archived
- #113 [Idea] P173 — The suite takes ~32 s and five modules take 26 of it; test_mutate alone 11.5 s for 28 tests
- #121 [Idea] P177 — A draft issue in a working stage is counted by the gate as #None and dropped by the status, which then says the limits hold
- #135 [Ready] P186 — mutate.py scores a mutant that no longer imports as caught → a mutant that does not compile, import or parse is refused, naming the file
- #136 [Ready] P187 — A board whose Wokwi stand-in is another chip validates ok → refused through one chip-name table, naming the boards of the same chip
- #137 [Idea] P188 — Whether a spark change breaks the bin is pinned for one of the four spark tools it calls → behaviour mutants on the bin's real calls
- #138 [Ready] P189 — An interpreter built for another chip is packed for a board without a word → refused by a 16-byte header read, through the same chip table

## Stranger polish (back with the walk's diary if it trips one)

- #46 [Idea] P112 — spark's MCP servers are pinned, and /spark:setup says they are declared, not checked
- #48 [Idea] P114 — init --force lists only what is still unanswered, and says what --force keeps
- #53 [Idea] P119 — check_vendor_pins says it could not look when the GitHub CLI is missing, instead of crashing
- #57 [Idea] P123 — tools.py --on honours --dry-run and says it installs
- #61 [Idea] P127 — boards/README.md gives spark's steps for adding a board
- #62 [Idea] P128 — A stranger can report a problem with a form that asks for what helps
- #66 [Idea] P132 — A stranger's first board: install, init and setup never surprise

## Ideas and umbrellas beyond the basic journey

- #5 [Idea] P76 — From a vague idea to a block-level schematic, by conversation
- #67 [Idea] P133 — The checks tell the truth: nothing that could not look reads as a pass
- #94 [Build] P158 — After store 1c works: the council finds gaps and bugs and refactors for changeability; a technical discovery of strategies, adapters and functionality-based replacement (no MCU, one, or more than one)

57 cards.
