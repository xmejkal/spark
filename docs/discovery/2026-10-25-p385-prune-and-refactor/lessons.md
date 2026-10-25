# Five lessons for the refactor

Card P385 [#494](https://github.com/xmejkal/spark/issues/494), in the order of the lesson table in
[plan v2](../2026-10-19-p323-target-architecture/architecture/refactor-plan.md#9-the-lessons). Read one lesson and
answer its question in one line. Each lesson has the idea, an example from spark, the options, the plan's pick and one
question.

## Lesson 1: pruning

The idea. Pruning takes code off the main path, so a reader sees only what the product uses. The git tag
`pre-refactor-2026-10-25` keeps every pruned line, and one command brings it back.

The example. The [pruning list](pruning-list.md#the-verdicts) gives each of 76 modules one verdict: keep 68, split 4,
move behind a module 3, prune 1. The prune is `tools/match_eval.py` (115 lines) and its test (102 lines). No page
names it and nothing imports it. The three moved modules are the PCB checks `check_bom.py`, `check_footprints.py` and
`check_physics.py`. A plug-in point holds them: `check_all.CHECKS`, a list of check classes.

```
on the path:  CHECKS -> RulesVsNetlist, VendorTruth
behind it:    # --- Later, not MVP --- TheOrder, Buildability, Physics
```

The options.

- (a) Groups (a), (b) and (c) in the prune PR now, the splits (d) and (f) in their area moves. A small PR, but
  `parts.py` stays big for a while.
- (b) Only the prune and the flags, groups (a) and (b). The smallest PR, but the PCB checks still look like MVP code.
- (c) All six groups at once. All is clean sooner, but one PR then cuts the 2,414 lines of `parts.py`.

The pick. The plan names no order. Its proposed card 2 lands `PRUNED.md` with the verdicts, and the list puts the
splits in stage 6. That is (a).

Your question: which verdict groups do you take, and in which order?

## Lesson 2: package layout

The idea. A package is a folder of modules that code imports by one name, such as `spark.bench`. Each area gets a
folder, and a thin script on top only reads the flags and prints.

The example. Today `scripts/` holds 63 modules side by side, and no `scripts/spark/`. `look.main` has 29
lines of flags, errors and printing. After S6 it has at most 15, and the job is an Operation (one job, one
`run()` method) in `spark/bench/operations.py`. Each area moves in three PRs: a net, the output codes, the move.

```
look.py (flags) -> spark/bench/operations.py (the job) -> spark/core/outcomes.py
```

Decision 2, the shape.

- (a) Thin CLIs over `scripts/spark/`, one Operation per job, one rules test. MCP imports the same code, but each import
  line changes once.
- (b) Operations inside today's flat `scripts/`. Nothing moves, but no area has one list of its jobs.
- (c) A `src/spark` package with `pyproject`. Standard, but the user installs something.

Decision 4, the start of the area moves.

- (a) A story pulls its area. Cheap moves, but slow ones.
- (b) Now, the bench first, one PR at a time. Steady, but stories wait during a move.
- (c) All areas in one pass. Soonest, but it breaks the rule of one PR at a time.

The pick. Decision 2: (a). Decision 4: (b), because the bench's net exists (S1).

Your question: decision 2 (the shape) and decision 4 (the start of the moves), (a), (b) or (c)?

## Lesson 3: the core contract

The idea. A contract is the fixed shape that every job in spark gives and takes. Each Operation returns one
`OperationResult` that holds its `Finding`s, one problem each. It never prints or asks, and it describes its arguments
as a JSON Schema (a standard description of a JSON shape).

The example. One onboard role, `onboard_battery_sense`, is spelled in five tables today. In `boards.py` it is a key of
`PIN_ROLES`, the constant `ONBOARD_BATTERY_SENSE` and a row of `ONBOARD_ROLES`. In `assign_pins.py` it is a bare string
key of `ROLE_PENALTY` (20) and an entry of `CONFLICTING_ROLES`. A reader who adds a role has to find all five. The plan
waits for P405 before it moves the penalty into the `OnboardRole` row.

```
today:  PIN_ROLES, ONBOARD_*, ONBOARD_ROLES, ROLE_PENALTY, CONFLICTING_ROLES
target: ONBOARD_ROLES -> OnboardRole(constant, does, what, penalty)   (after P405)
```

Decision 1, which goal ranks first.

- (a) Readable, testable, exchangeable, reusable, consistent, as v1 ranks. A reader finds the role in one row, but
  clear names and docstrings cost more lines per slice.
- (b) Reusable first ("We do reuse code"). Less code repeats, but a shared helper that nobody reads is hard to reuse.
- (c) No rank, each slice names its goal. Each slice is free, but two slices can pull in different directions.

The pick. (a). A function nobody reads is not reused, and readability is what makes the other four visible.

Your question: decision 1, readability first, (a), (b) or (c)?

## Lesson 4: tests

The idea. A golden test saves a command's whole output once and compares each new run with it. A Fake is a
stand-in object that a test gives to the code in place of the real board or tool.

The example. `tests/golden_bench.py` holds 13 cases in `CASES`, and `tests/golden/` holds their 13 saved outputs. They
catch any change in the bench's output. The other kind is `mock.patch`, which swaps a name inside a module during a
test. A module move breaks it. `tests/test_deploy_gate.py` has 14 such lines, and 49 test files have 361. A ratchet (a
count that only goes down) shrinks them. One test checks that the leaf `screen_text` (a module that imports nothing
of spark) stays a leaf, and `zone_time.py` has no test. The new `tests/test_leaves.py` covers all three leaves.

```
each push: the fast lane, inside its budget   before a PR: the slow lane, everything else
```

S13, the fast lane's budget on a push.

- (a) Under 90 s on your Mac. Most tests run on each push, but you wait a minute and a half.
- (b) Under 30 s. A push feels instant, but more tests move to the slow lane and catch a bug later.
- (c) No lanes, every test on every push. Nothing waits for later, but each push takes longest.

The pick. The plan's check for stage 5 says (a), under 90 s.

Your question: what time budget does the fast lane get on a push?

## Lesson 5: Claude Code forms

The idea. Claude Code reads spark through a few file forms, each with one job. Each form calls the core.

The example: the forms as Anthropic documents them, with spark's files.

- CLAUDE.md: text Claude reads at each session start. spark's has one line, `@AGENTS.md`.
- A command: a prompt the person starts by name. spark has 8, such as `/spark:build`.
- A skill: a folder with a `SKILL.md`. Claude picks it by its description. spark has 3.
- An agent: a helper with its own context, tools and model. The plugin has 4, the team 2.
- A hook: a shell command Claude Code runs on an event, such as your session start.
- A plugin: one package of all of these, in `.claude-plugin/`.
- MCP: a protocol for an AI app to call a server's tools. `Operation.schema()` makes the tool.

```
one Operation -> CLI --json -> command, skill, agent
             \-> schema()   -> MCP tool, LangGraph node
```

The options for the spike, the build as a LangGraph node and an MCP tool.

- (a) After stage 3. An early proof, but the build is not an Operation yet.
- (b) After stage 4. The bench is on the core, but a flaw shows up later.
- (c) After stage 6. Every area is ready, but you learn LangGraph last.

The pick. The plan's proposed card 1 says after stage 3. That is (a).

Your question: does the spike run before stage 6, and after which stage?
