# Eight lessons for the refactor

Card P385 [#494](https://github.com/xmejkal/spark/issues/494). Read one lesson at a time and answer its question in
one line. Each lesson has the idea, an example from spark, the options, the plan's pick and one question.

[Plan v2](../2026-10-19-p323-target-architecture/architecture/refactor-plan.md#9-the-lessons) lists five lessons.
Three of them (2, 3 and 5) ask two decisions each. Each is split here, so every lesson asks one question and the
numbers shift.

| Question | Lesson | Plan v2 lesson | What the answer settles |
|---|---|---|---|
| Question 1 | pruning | 1 | the scope and order of the prune PR (no numbered decision) |
| Question 2 | package shape | 2 | decision 2, the shape |
| Question 3 | when the moves start | 2 | decision 4, the start of the area moves |
| Question 4 | readability first | 3 | decision 1, the goal that ranks first |
| Question 5 | printed names | 3 | decision 5, the printed names of the Operations |
| Question 6 | tests | 4 | the fast lane's budget on a push (S13, no numbered decision) |
| Question 7 | a relayed yes | 5 | decision 6, a yes relayed by another program |
| Question 8 | the learning spike | 5 | when the spike runs (proposed card 1, no numbered decision) |

A wave is one unit of the plan. There are six. An Operation is a class with one job and one `run()` method. The
options (a), (b) and (c) are the plan's own decision options. Lesson 1 names its options with words, so no letter
names two things.

## Lesson 1: pruning

The idea. Pruning takes code off the main path, so a reader sees only what the product uses. The git tag
`pre-refactor-2026-10-25` keeps every pruned line, and one command brings it back.

The groups. Quick work is what goes or hides at once: the tool `tools/match_eval.py`, the 19 flags that no page names
and the three PCB checks. Split work cuts `scripts/boards.py` and `scripts/parts.py` into modules of one job each.

The example. The [pruning list](pruning-list.md#the-verdicts) gives each of 76 modules one verdict: keep 68, split 4,
move behind a module 3, prune 1. The prune is `match_eval.py` (115 lines) and its test (102 lines). Nothing imports
it. Only `matching.py`, `needs.py` and one P211 design page mention it. The three moved modules are `check_bom.py`,
`check_footprints.py` and `check_physics.py`. They stay reachable through `check_all.CHECKS`, a list of check classes.

```
on the path:  CHECKS -> RulesVsNetlist, VendorTruth
behind it:    # --- Later, not MVP --- TheOrder, Buildability, Physics
```

The options.

- Quick now, split later. Quick work in the prune PR, split work in each area's move. `parts.py` stays big for a
  while.
- Prune only. The tool and the flags. Smallest, but the PCB checks still look like MVP code.
- Everything now. Clean sooner, but one PR then cuts the 2,414 lines of `parts.py`.

The pick. Quick now, split later. Plan v2 puts the splits in wave 6.

Question 1: which option do you take for the prune PR?

## Lesson 2: package shape

The idea. A package is a folder of modules that code imports by one name, such as `spark.bench`. A thin script on top
only reads the flags and prints.

The example. Today `scripts/` holds 63 modules side by side, and no `scripts/spark/`. `look.main` has 29 lines of
flags, errors and printing. After wave 3 it has at most 15, and the job is the Operation `LookAtBoard` in
`spark/bench/look_at_board.py`. Each area gets an `OPERATIONS` list in its `__init__.py`.

```
look.py (flags) -> spark/bench/look_at_board.py (the job) -> spark/core/outcomes.py
```

Decision 2, the options.

- (a) Thin CLIs over `scripts/spark/`, one Operation per job, one rules test. MCP imports the same code, but each
  import line changes once.
- (b) Operations inside today's flat `scripts/`. Nothing moves, but no area has one list of its jobs.
- (c) A `src/spark` package with `pyproject`. Standard, but the user installs something.

The pick. (a). A LangGraph node or an MCP tool imports the package, and (c) breaks the rule that a user installs
nothing heavy.

Question 2: decision 2, the shape: (a), (b) or (c)?

## Lesson 3: when the moves start

The idea. A move puts an area's modules into its folder and changes every import line. The net is a set of tests
that catch any change in a command's output. Without a net, a move can break a command unseen.

The example. The bench has a net since S1: 13 golden cases in `tests/golden/`. Wave 5 moves 16 bench modules, 2,266
lines that 35 files import. Wave 6 does the other areas, each after its own net. Waves 3 and 4 put the bench on the
core first.

Decision 4, the options.

- (a) A story pulls its area. Cheap moves, but slow ones.
- (b) Now, the bench first, one PR at a time. Steady, but stories wait during a move.
- (c) All areas in one pass. Soonest, but it breaks the rule of one PR at a time (decision 3).

The pick. (b). You pulled the refactor on 2026-10-25, the bench net exists, and walk 2 ran on the bench.

Question 3: decision 4, the start of the area moves: (a), (b) or (c)?

## Lesson 4: readability first

The idea. Five goals guide the code: readable, testable, exchangeable, reusable, consistent. Sometimes two pull apart.

The example. One onboard role, `onboard_battery_sense`, is spelled in five tables. In `boards.py` it is a key of
`PIN_ROLES`, the constant `ONBOARD_BATTERY_SENSE` and a row of `ONBOARD_ROLES`. In `assign_pins.py` it is a key of
`ROLE_PENALTY` (20) and an entry of `CONFLICTING_ROLES`. Reuse says: put the penalty in the `OnboardRole` row, so one
edit adds a role. Readability says: a board record then holds a scoring weight that only the pin assigner reads, and a
reader of the record cannot tell what 20 means. The plan waits for P405 before it moves the penalty.

```
today:  PIN_ROLES, ONBOARD_*, ONBOARD_ROLES, ROLE_PENALTY, CONFLICTING_ROLES
target: ONBOARD_ROLES -> OnboardRole(constant, does, what, penalty)   (after P405)
```

Decision 1, the options.

- (a) Version 1's rank: readable first. The role stays readable in the record, but clear names cost more lines.
- (b) Your 2026-10-23 order, reuse first. One row, but a shared helper that nobody reads is hard to reuse.
- (c) No rank, each slice names its goal. Free, but two slices can pull in different directions.

The pick. (a). A function nobody reads is not reused.

Question 4: decision 1, which goal ranks first: (a), (b) or (c)?

## Lesson 5: printed names

The idea. Every command prints an `op`, the name of the Operation that answered. Standard P381 says an Operation's
`op` is its class's words, such as `look-at-board`.

The example. `look.py` prints `op` as `look`. Its class is `LookAtBoard`. The bench has six ops, `look`, `deploy`,
`grant`, `grant-check`, `live` and `reach`. Today's scripts have 30 more, such as `board-get` and `emit-board`. The
golden files and the command pages pin every one of them.

```
op "look"  ->  op "look-at-board"   (every golden, every command page, every habit)
```

Decision 5, the options.

- (a) Keep every op that a golden or a command page pins, as a named exception. Only a new Operation follows the
  rule. Nothing public changes.
- (b) Rename each op to its class's words in its area's output slice. One spelling everywhere, but a public change.

The pick. (a). The class names pass the rule already. A card can rename later.

Question 5: decision 5, the printed names: (a) or (b)?

## Lesson 6: tests

The idea. A golden test saves a command's whole output once and compares each new run with it. A Fake is a stand-in
object that a test gives to the code in place of the real board or tool.

The example. `tests/golden_bench.py` holds 13 cases and `tests/golden/` holds their saved outputs. The other kind of
test is `mock.patch`, which swaps a name inside a module. A module move breaks it. `tests/test_deploy_gate.py` has 14
such lines, and the test files have 361. A ratchet (a count that only goes down) shrinks them. The fast lane is the
tests that run on each push. The slow lane is all the others, run before a PR.

```
each push: the fast lane, inside its budget   before a PR: the slow lane, everything else
```

S13, the fast lane's budget.

- (a) Under 90 s on your Mac. Most tests run on each push, but you wait a minute and a half.
- (b) Under 30 s. A push feels instant, but more tests move to the slow lane and catch a bug later.
- (c) No lanes. Nothing waits for later, but each push takes longest.

The pick. (a). The plan's check for wave 5 says under 90 s.

Question 6: what time budget does the fast lane get on a push: (a), (b) or (c)?

## Lesson 7: a relayed yes

The idea. Claude Code reads spark through forms, each calling the same core: a command, a skill, an agent, a hook and
MCP. MCP lets an AI app call a server's tools, and `Operation.schema()` makes the tool.

```
one Operation -> CLI --json -> command, skill, agent
             \-> schema()   -> MCP tool, LangGraph node
```

The example. The erase of a board needs your yes. Today `data.yes.kind` is `typed` or `grant`, both made in your
terminal, and `agents.md` says Claude never supplies the yes. A graph's screen or an MCP client can collect a yes
itself.

Decision 6, the options.

- (a) No third kind. A graph pauses, and you give the yes in your own terminal.
- (b) A third kind, `relayed`, with `who` and the program that collected it. The gate refuses it for the erase and
  allows it for a grant.

The pick. (a). It needs no new rule and keeps the erase in your terminal. (b) is a safety change for you alone.

Question 7: decision 6, a yes relayed by another program: (a) or (b)?

## Lesson 8: the learning spike

The idea. A spike is research whose answer is a finding. This one proves that the core serves another interface: one
Operation runs as a LangGraph node and as an MCP tool from the same `OPERATIONS`, traced by Langfuse. The core does
not change.

The example. After wave 3 the core exists, and `look` is the one Operation on it. The build becomes an Operation only
in wave 6. So an early spike runs `look`, and a spike with the build waits for wave 6.

```
wave 3: look on the core   wave 4: five bench Operations   wave 6: the build
```

The options.

- (a) After wave 3, with `look`. An early proof, and a flaw shows while the core is cheap to change.
- (b) After wave 4, with the bench Operations. A wider proof, but a flaw shows later.
- (c) After wave 6, with the build. The real build, but you learn LangGraph last.

The pick. (a). You learn LangGraph early, and the proof comes before the moves.

Question 8: after which wave does the learning spike run: 3, 4 or 6?
