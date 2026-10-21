# Round 4: readability for a human

Lens: a senior engineer who reads code for a living. Read on 2026-10-21 against the branch `p323-target-architecture`.

> **TL;DR.** The design makes the doors easy to read and leaves the functions behind them as they are. Add five
> rules a test can count (nesting, parameters, comment length, public first, 40-line functions in `spark/`), pass
> named dependencies instead of `**collaborators`, and give each Operation keyword parameters instead of a `values` bag.

## 1. The readability standard

A reviewer applies all ten. The test (`ArchitectureRules`) counts the five marked AST, with the same baseline ratchet.

| # | Rule | Check |
|---|---|---|
| R1 | A function in `spark/` is at most 40 lines. Old scripts keep D7's 60 until they move. | AST |
| R2 | Nesting is at most 3 deep. An `elif` chain counts as one level. Use a guard clause and return early. | AST |
| R3 | A function takes at most 5 parameters. More become one Value. | AST |
| R4 | A module reads top-down: its docstring, then its public entry, then helpers in the order they are called, private last. | AST (first `def` or `class` is public) |
| R5 | A comment block is at most 4 lines and says why the code is so today, in the present tense. The story of what broke goes to the card. A card number in brackets stays. | AST (token scan) |
| R6 | One level of abstraction per function. A function either tells the steps, by calling named functions, or does one step's detail (a subprocess, a file, a sentence). Never both. | review |
| R7 | A sentence longer than one line is a `_MESSAGE` constant with named fields, not a `%` expression in the middle of the logic. | review |
| R8 | An error reads as three parts: what happened, why, what to do next. It is a `SparkError` with a `code`. | review, S7 |
| R9 | No clever code: no conditional expression inside a format argument or a print, no comprehension with two `for`s and an `if`, no import inside a function, no boolean flag that changes what a function does. | review |
| R10 | The first docstring line is one sentence: the role word for a class, what it returns for a function (developing.md:276). | S1 |

Today, of 923 functions in `scripts/*.py`: 89 are over 30 lines, 17 over 60, 17 nest 4 or 5 deep (elif not counted).
132 of 1,172 comment lines name a card, a date or "used to". The code formats 463 lines with `%` and 54 with f-strings.

## 2. The three hardest places to read

1. **`scripts/check_spine.py:347` `run`, 192 lines, 6 parameters, one a flag (`from_library`).** It runs seven stages
   inline. Within ten lines it starts a subprocess, writes a file, parses JSON and builds a four-line sentence
   (check_spine.py:437-450). It returns `stages + [Stage(...)]` from 21 places. Comment blocks tell incident history:
   "Intake row M3 had it as `problems` on 09-25; both were wrong" (:371), and an 11-line block at :453.
2. **`scripts/parts.py:621` `validate`, 240 lines.** About 25 rules sit inline, each with its own loop over `needs`,
   `power` or a pin list. It imports `re` in the middle (:686). Its last ten lines (:852 on) show the right shape
   already: `problems.extend(host_part_problems(part))`, one named rule per line. The first 230 lines do not.
3. **`scripts/tools.py:568` `main`, 83 lines, nesting 5.** Seven mutually exclusive flags become an `if/elif` chain.
   Each branch parses, runs and prints in its own format. A conditional expression sits inside a print (:597).
   `where` and `scope` (:585) are computed before the reader knows which branch needs them.

## 3. The three most readable places

1. **`scripts/flasher.py`, 66 lines.** The module docstring says what it is and what it never does. The Strategy
   comes first, then its one Adapter. Every constant carries its unit and its source. No function is over 3 lines.
2. **`scripts/deploy_service.py:108` `deploy`.** It reads as the flow in order: gate, plan, token check, ready, run
   each command. Its collaborators come in through `__init__` (:69). Each stop is a named error. One weak spot:
   `plan` builds a two-line sentence inside a conditional expression (:99), which R7 would move to a constant.
3. **`scripts/outcomes.py:35` `status_of`.** One line of logic. The docstring says why it is one place. Its callers
   cannot spell the rule wrong, because no other way to get the word exists.

All three are small, have one job, are named for their role and keep sentences out of control flow: the design's shape.

## 4. The judgment

**Easier to read.** A door of 40 lines. `Operation` as a dataclass with keywords instead of `parts.py:1581`'s
positional tuples, where a reader counts commas to find `effects`. One place for `--help`. `BuildService` with one
`BuildStage` per stage replaces the hardest function above. Codes instead of sentences (S9).

**Harder to read, and what to change.**
- **`**collaborators` hides what an Operation needs.** `run_door("look.py", OPERATIONS, argv, run=run, **COLLABORATORS)`
  (design 2.6) tells neither a reader nor a test what `look` uses. Give each area one Value, `BenchDependencies(run,
  shorten, secrets, writer, consent)`, built in its `operations.py` with real defaults, and pass it by name.
- **`run(values, collaborators)` reads arguments as `values["ignore_older_runs"]`.** A typo shows only at run time.
  Make each Operation's `run` a plain function whose keyword parameters are its arguments' `dest`s:
  `def look(project: Path, port: str | None, ignore_older_runs: bool, deps: BenchDependencies)`. `run_operation`
  calls `operation.run(**values, deps=deps)`. One test checks that every `Argument.dest` names a parameter.
- **Three hops before the logic.** door, then `operations.py`, then the Operation's `run`, then the Service. Keep each
  `Operation(...)` directly under its `run` function, so one screen holds the flags and the code they reach. The
  door's docstring names its Operation and its Service.
- **A wall of data.** `parts.py`'s 30 Operations with nine fields each make a table of about 300 lines. Keep
  `summary` to one line and move long text to a `description` constant beside the Operation. `OPERATIONS` at the end
  of the module lists names only.
- **S1 to S18 guard the architecture, not the reader.** None limits nesting, parameters, comment length or order, and
  D7's 60 lines is lax for code whose `BuildStage`s fit in 40. Add R1 to R5 to the same test and baseline. A move PR
  moves each incident story longer than 4 lines to its card.
- **One word for one thing.** The design says "outcome, printed as `status`" (section 4). A reader meets two words
  for one value. Use `status` in the code too, and keep "outcome" as the guide's word only, or the reverse.

## 5. Sketch: `check_spine.run` before and after

Before (`scripts/check_spine.py:437-472`, cut to 25 lines):

```python
    if not circuit_path.is_file():
        # Nothing came out. Before blaming the design, ask the same tool for a resistor on a
        # board: a tool that cannot build that is not reporting on the design at all.
        can, last_words = toolchain_can_build(toolchain, workdir)
        if not can:
            return stages + [Stage("build", COULD_NOT_RUN,
                                   "%s (%s) cannot build even a trivial board from here, so this "
                                   "is the toolchain, not the design. Use the project's own tsci "
                                   "(npm i @tscircuit/cli in the project) or one that builds on "
                                   "its own.\n%s" % (toolchain, version, last_words))]
        return stages + [Stage("build", PROBLEMS,
                               "no circuit.json was produced by %s (%s), which does build a "
                               "trivial board\n%s" % (toolchain, version,
                                                      built.stderr.strip()[-800:]))]

    traces, errors = count_in(json.loads(circuit_path.read_text()))
    # NOT a trace count. Comparing connections asked for against `pcb_trace`s is wrong twice
    # over, and was tried here first: a net with N members needs N-1 traces, and a pin on a
    # ... (nine more lines of history)
    islands = islands_in(json.loads(circuit_path.read_text()),
                         emit_board.supply_inputs(board, part_list),
                         across=emit_board.loads_across_a_pair(part_list))
    if islands:
        return stages + [Stage("build", PROBLEMS,
                               "%s. A board builds, routes and reports no error with a component "
```

After (`spark/build/stages.py`, the target design with R1 to R10):

```python
class BuildService:
    """Service: runs each BuildStage in order and stops at the first that cannot feed the next."""

    def __init__(self, stages: Sequence[BuildStage]):
        self.stages = stages

    def run(self, work: BuildWork) -> BuildResult:
        results = []
        for stage in self.stages:
            results.append(stage.run(work))
            if results[-1].status != OK:
                break
        return BuildResult(tuple(results))


class CircuitStage(BuildStage):
    """Strategy: builds board.tsx with the board engine and proves copper joins every part."""

    def run(self, work: BuildWork) -> StageResult:
        circuit = work.engine.build(work.board_file)   # raises EngineBrokenError, code tool_cannot_build
        if islands := find_islands(circuit, work.supplies):
            return self.problems(ISLANDS_MESSAGE, code="islands", islands=islands)
        if circuit.errors:
            return self.problems(BUILD_ERRORS_MESSAGE, code="build_errors", kinds=circuit.error_kinds())
        if circuit.trace_count == 0:   # routing skipped one net and raised nothing
            return self.problems(NO_TRACES_MESSAGE, code="no_traces")
        return self.ok(f"{circuit.trace_count} trace(s), 0 errors, tsci {work.engine.version}")
```

`BuildWork` is a Value with named fields (`board`, `parts`, `board_file`, `engine`, `supplies`), so a reader sees what
flows between stages. The trivial-board probe moves into the engine Adapter, where its sentence becomes a message
constant. The islands story moves to its card.

## Rows

1. No rule limits nesting (17 functions at depth 4 or 5) or parameters (`matching.py:68` takes 9): add R2, at most 3 deep, and R3, at most 5.
2. D7's 60 lines is lax for new code (89 functions over 30): set 40 lines in `spark/`, keep 60 for scripts not yet moved.
3. Modules do not read top-down: add R4, the first `def` or `class` in a `spark/` module is public.
4. Comments tell incident history (132 of 1,172 lines; `check_spine.py:371`, `:453`): add R5, blocks at most 4 lines, the story to its card.
5. `**collaborators` hides what an Operation uses: one `<Area>Dependencies` Value per area, passed by name.
6. `run(values, ...)` reads arguments by string key: keyword parameters named for each `Argument.dest`, checked by one test.
7. Three hops from door to logic: declare each `Operation(...)` under its `run` function; the door docstring names both.
8. `parts.py`'s 30 Operations make a 300-line table: one-line `summary`, long text in a constant, `OPERATIONS` lists names.
9. Long sentences sit in control flow (`check_spine.py:437-450`), in two styles (463 `%`, 54 f-strings): R7, a multi-line sentence is a `_MESSAGE` constant; f-strings in new code.
10. "outcome" and "status" name one value: pick one word for the code and the envelope.
