# Developing spark

How spark's own code is tested and gated, and where the work is planned.

## The tests

```sh
python3 -m unittest discover -s tests
```

The count is whatever that prints. A count written into the README rotted three times in four days, so a count
appears only inside a dated output, like the push below.

**Two runs of the suite** ([P425](https://github.com/xmejkal/spark/issues/559)). The plain command above is the full
run: every test. The push hook runs the quick run, which skips the tests marked `@slow`
([`tests/suite_runs.py`](../../tests/suite_runs.py)) and says how many it skipped. The quick line is not the suite's
count, and a commit message or a card quotes the full run's. A mark needs more than about 2 s and a reason anyone
can check: the reason says what the test runs and its measured seconds, with the date. Put the mark on a class or a
method:

```python
from suite_runs import slow

@slow("a real tsci build of a hostile part name, 1 test, 6 to 12 s on 2026-10-26")
def test_the_build_runs_the_name_as_no_code(self): ...
```

`SPARK_SUITE=quick` makes any run a quick run. `tools/mutate.py` removes it from the environment of its runs, because a
defect that only a slow test catches must not escape it. The first numbers, measured on 2026-10-26: the full run took 124.8 s, and the quick run took 77.0 s of tests and 94 to 100 s for the whole gate (the rows have the numbers,
[`docs/observations/rows/p425-quick-run.md`](../observations/rows/p425-quick-run.md)).

**The rule the tests follow: a test must run the thing, not read it.**

- A test that finds a string in source proves the thing was named, not that it ran, so behaviour is proven by running
  it. `tests/test_check_all.py` forbids source-text assertions outright.
- None is an arithmetic identity of the function under test.
- Every check is run through the runner with an input whose answer is known, and each check's own suite gives it an
  input that makes it find a problem.

The rule exists because of one test, written to catch "a check nobody invokes". It asserted that a string appeared
in the runner's source. That verified the check was named, not that it ran, and it stayed green for the whole life of
the bug it was written to prevent.

The suite still reads source for rules about the code itself:

- no script imports unittest;
- only `store.py` spells the store's path;
- only `tools.py` names a tool's executable;
- no script restates a number that `data/fabrication.json` holds;
- every script a command runs starts with its shebang;
- every test module has, after its standard-library imports and before anything else, these two lines
  ([P172](https://github.com/xmejkal/spark/issues/112)):

  ```python
  sys.path.insert(0, str(Path(__file__).resolve().parent))
  import suite_temp
  ```

  `tests/suite_temp.py` gives the test process one temp folder and removes it when the process exits, so a test's
  `tempfile.mkdtemp()` needs no cleanup of its own. The first line lets `python3 -m unittest tests.test_x` find it.
  A run that was killed never reaches that clean-up, so at start `suite_temp` also removes the `spark-tests-*` folders
  older than a day in the temp folder it inherited, through `tools/scratch.py` ([P435](https://github.com/xmejkal/spark/issues/579)).
  `scratch.remove_old_folders` removes only a plain directory that is the user's own, whose name starts with the prefix
  and that nothing has written to for a day, and it never follows a link. It is standard library only. It costs about
  1 ms for 1,273 entries.

`test_converter.py` also checks the converter's TypeScript, comments stripped, for default paths it must not have.

A golden is a file with the expected output of one script run. `tests/test_golden_bench.py` keeps 16 goldens in
`tests/golden/`, for `look.py`, `deploy.py`, `grant.py --check`, `live.py` and `reach.py`
([P380](https://github.com/xmejkal/spark/issues/487)). Each test runs one script as a child process in an S3
project that `tests/golden_bench.py` builds. The fake esptool, mpremote and serial in `tests/fake_modules/` come first
on the child's `PYTHONPATH`, and the child runs with `TZ=UTC` and a store of its own. The test replaces the run's own paths, the image hash and the time with placeholders,
such as `<project>`, before it compares. A golden's name is the op, the status and the scenario:
`look-could-not-run-two-boards.json`.

If you change what a bench script prints on purpose, write that op's goldens again, read the diff, and run once more.
An accept run writes only the goldens of the op it names:

```sh
SPARK_ACCEPT=look python3 -m unittest tests.test_golden_bench   # writes look's goldens, then fails
git diff tests/golden
python3 -m unittest tests.test_golden_bench
```

**The second rule: every fix that holds logic is mutation-tested.** Before the pull request, the council's mutation
tester puts the defects that the fix prevents back into the changed lines, in a copy of the tree
([P208](https://github.com/xmejkal/spark/issues/175)). Without a council, run the rows about your files yourself:

```sh
changed=$(git diff --name-only origin/main...HEAD)     # the files your branch changed
python3 tools/mutate.py tests/mutations/*.json --for $changed --copy
```

`--copy` removes its copy in a `finally`, and also when SIGTERM stops it (the signal becomes `SystemExit`, only in the
main thread and only over the default handler). At every start, `mutate.py` removes its `mutate-run-*`, `mutate-import-*`
and `mutate-copy-*` folders older than a day, which covers SIGKILL ([P435](https://github.com/xmejkal/spark/issues/579)).

A row reported *refused* is a guard whose code moved, or whose replacement does not compile, import or parse.
Re-anchor it or fix its `replace`, or delete it and give the reason.

[`tools/mutate.py`](../../tools/mutate.py) puts each defect in a table back into the code, and must report every one
caught. A mutation the suite does not notice is a missing test. A fixture too weak to see one is fixed, rather than the
mutation dropped. The [glossary](../../GLOSSARY.md#mutation-and-the-mutation-table) has the words.

**The lint rule: the repository passes Ruff.** The settings are in `pyproject.toml`, and `tests/test_lint.py` runs
Ruff in the suite. Install Ruff with `uv tool install ruff==0.17.1`, the version the settings pin. The test skips
when Ruff is not on PATH. A local run also lints untracked files, but the push hook lints only the commit.

## The commit gate, before every push

[`tools/pre-push`](../../tools/pre-push) runs [`tools/check_commit.py`](../../tools/check_commit.py) on the tree as
committed, not the working tree. It measures `HEAD` even when another branch is pushed; that is
[P106](https://github.com/xmejkal/spark/issues/39). The [glossary](../../GLOSSARY.md#the-commit-gate--toolspre-push)
has its story. Install it once per clone:

```sh
ln -sf ../../tools/pre-push .git/hooks/pre-push
```

It reports:

- the quick run of the suite, as committed: `quick run: Ran N of M tests in S s (K slow tests skipped; the full run is
  check_commit.py --full)`. The skipped count is only the `@slow` tests, never a real skip such as a missing tool. The
  seconds are the tests alone; the board check (about 18 s) and the size line come on top, and the gate prints its
  whole time. No budget fails the push: the time is printed and not capped, as the size line is
  ([W15b](../../scrum/WORKING_AGREEMENTS.md#w15b--the-size-is-said-at-every-push-with-its-reason-refactor-before-growing)),
  and the retro decides any cap. The whole push takes the tests' seconds plus about 18 s;
- what the suite left behind ([P172](https://github.com/xmejkal/spark/issues/112)): the suite runs with an empty temp
  folder of the gate's own, and anything left in it fails the push with one line,
  `temp: the suite left N entries behind (…) — P172`. A folder the gate cannot list is could-not-run, which exits 2
  and stops the push, unlike the board's could-not-run below. One run of the suite had left 2,291 entries, 26 MB, and
  the hook ran it at every push. The gate also removes its own archive of the commit, 6.2 MB, when it ends;
- the size of `scripts/`;
- the work board — spark's and the bin's, through your `gh` login ([the board](../../GLOSSARY.md#the-board)). It fails
  the push on:
  - a stage over its limit, or more than four cards in flight across both boards — the numbers and the counting rules
    are [the flow's table](../../scrum/README.md#the-flow--an-items-stages);
  - two open cards labelled `expedite`: the lane takes one card at a time;
  - a card that waits on someone (*Waiting on*) with no *Waiting since*, on either board, in any open stage;
  - a card of spark's in Ready, Build or Review with no *Needed by* or no slice.

  With no `gh` login or no network, the board part says could-not-run, with `gh`'s own reason, and passes. Three more
  looks it will not make ([P168](https://github.com/xmejkal/spark/issues/106), [P167](https://github.com/xmejkal/spark/issues/105)),
  each could-not-run that passes, never "the limits hold": it reads a board whole or judges nothing — `gh` stops at its
  `--limit`, so a board past the first ask's 500 is asked again with its own count, and one still short is, for example,
  `backlog: could-not-run — the spark board holds 12 items, 10 were read; the limits were not checked` — it knows
  seven stages, Idea, Discovery, Design, Ready, Build, Review and Done, so a card in any other is
  `backlog: could-not-run — #4 P4 — x is in a stage the gate does not know: "Doing"; the limits were not checked`: a
  renamed stage is a decision, not a silent skip — and the spark board with no *Status* on any card is a changed field,
  `backlog: could-not-run — no card of the 3 on the spark board has a Status — the field's keys may have changed, or
  every card is new; the limits were not checked`. A card with no *Status* (GitHub's "No status" column) is in Idea and
  said, `backlog: 3 card(s) have no stage: #3, #5, bin #20`. The bin's board is read for the flight total, the lane and
  its waits alone, so its failing costs nothing else: read in part, or with no *Status* on any card, it is set aside and
  spark's cards are judged alone, with the bin's unread line saying why —
  `backlog: the bin's board could not be read (it holds 25 items, 2 were read) — its cards were not counted or checked`,
  or `(no card of its 2 has a Status)`.

From a push on 2026-10-05 (the gate's wording has changed since; the lines are a dated record, not today's output):

<!-- output: run 2026-10-05, spark 0.6.0 -->
```text
264a9b7 as committed: Ran 1144 tests in 22.777s / OK (skipped=1); 562 mutation(s) in 93 table(s): every anchor present, once
  scripts/: 5,529 code lines (+0 since origin/main)
  backlog: 28 open, the limits hold
```

The full run, `python3 tools/check_commit.py --full` (or `python3 tools/check_commit.py <commit> --full`), is the same
gate with every test, the slow ones too. It prints `<commit> as committed, full run: Ran M tests in S s / OK`. Run it
before a PR is marked ready and before an auto-mode merge: a defect only a slow test catches sits on the branch after
a push, and this run closes that gap.

Run the board part yourself — `--help` lists its rules and exit codes — and the status and the day-close beside it
(`--dry-run` posts nothing):

```sh
python3 tools/check_backlog.py
python3 tools/board.py status
python3 tools/board.py close --dry-run "the day's one line"
```

The gate on the live boards, then the status (the last close's line cut short here):

<!-- output: run 2026-10-09, spark 0.7.0 -->
```text
  backlog: 84 open, the limits hold; the bin: 22 open
```

<!-- output: run 2026-10-09, spark 0.7.0 -->
```text
spark — 84 open, the limits hold · trial check 2026-11-02
  in flight: Build P146 (#80) 3 d, Discovery P136 (#70) 3 d, Discovery P158 (#94) 1 d
  waits on the PO: R2.6 (#15) since 2026-10-05, 4 d !, P136 (#70) since 2026-10-06, 3 d, P146 (#80) since 2026-10-09, 0 d
  Ready: P143 (#77)
  ! Ready is down to 1 — propose an order for the PO
  open PRs: spark #104 P146: the process fits how we work — the gate's  (draft)
  last close 2026-10-08: P97 (store 1c) finished subagent-driven: …
```

A refusal: the gate's rules run on the board as `gh` printed it at the migration of 2026-10-05 (the suite's recording,
`tests/data/p102a-items.json`, with an empty bin board). Its one wait was never dated, so the gate exits 1 and a push would fail:

<!-- output: run 2026-10-09, spark 0.7.0 -->
```text
  backlog: 27 open, 1 problem(s); the bin: 0 open
    #15 R2.6 — A fourth cold test: waits on the PO since nobody knows — set Waiting since
```

The other refusals read the same way, one line each, as the suite expects them: `Build holds 4 (#1, #2, #3, #4) — its
limit is 3: finish one before starting another`, `5 in flight (#1, #2, #3, #4, bin #19) — at most 4: finish one before
starting another`, `2 cards labelled expedite (#1, #2) — one at a time, on the PO's word`, and for a card with no slice
`#8 P8 — x: on no slice of the story map`. With no `gh` login:

<!-- output: run 2026-10-09, spark 0.7.0 -->
```text
  backlog: could-not-run — gh or the network could not be reached (To get started with GitHub CLI, please run:  gh auth login); the limits were not checked
```

## Recording what spark answers

A change to what spark prints should be able to say which answers it changed. [`tools/snapshot.py`](../../tools/snapshot.py)
records them. It copies each project that uses spark, and the store, runs the project's documented spark commands in
the copy, and keeps every exit, stdout and stderr. The projects are the bin, irrigation and plant-alarm, plus the five
small cases in [`tests/data/snapshot/`](../../tests/data/snapshot/README.md). The originals are only read.

It records six scripts as the projects run them, with what they call, such as the chain's `emit_board.py`: `boards.py`,
`check_bom.py`, `check_vendor_pins.py`, `check_physics.py`, `check_spine.py` and `check_all.py`. No `--json` answer is
kept, and no command of `parts.py`, `drawer.py` or `needs.py` runs, so a change that shows only in their answers does
not show here.

Take main first, then the branch against it:

```sh
python3 tools/snapshot.py --out /tmp/before --spark <main checkout> --tsci-bin <a project's node_modules/.bin>
python3 tools/snapshot.py --out /tmp/after --against /tmp/before/snapshot.json --tsci-bin <the same>
```

The baseline, `docs/observations/2026-10-11-baseline.json`, was taken on 2026-10-11, before any later change to an output. Against it,
a run also shows every output change merged since. On the branch that added it, which changed no answer, the run
against the baseline ended like this:

<!-- output: run 2026-10-11, spark 0.8.1 -->
```text
spark: 3d79dd7 → 76f4536
nothing differs from docs/observations/2026-10-11-baseline.json
```

With one word changed in what `boards.py --validate` prints, it exits 1 and lists twelve commands, each like this one:

<!-- output: run 2026-10-11, spark 0.8.1 -->
```text
a3-run1-placeholder-board: boards.py --validate --project . — differs from the snapshot of 2026-10-11T10:44:09+02:00
  stdout:
    -          firebeetle2-esp32s3 (library): ok
    -   active  generic-esp32s3 (project): ok
    -          xiao-esp32-c6 (library): ok
    +          firebeetle2-esp32s3 (library): fine
    +   active  generic-esp32s3 (project): fine
    +          xiao-esp32-c6 (library): fine
```

| exit | means |
| --- | --- |
| 0 | every command answered as the older snapshot recorded |
| 1 | some lines differ, listed under the command and stream that printed them |
| 2 | it could not run: for example, `--spark` names no spark tree, or `--against` a file it cannot read |

The lines about the store, spark's pin or a project's pin come first and never set the exit. They say whose a
difference may be, and a branch always moves spark's pin. The exits it records are not judged: irrigation's chain
exits 1 today, and the baseline holds that. A card that changes an output says which of these lines it changes.

## What spark can do

`python3 tools/inventory.py` prints every script in `scripts/` and `tools/` as Markdown. Each row says what the
script is for, which pages name it, and which of its flags no page names. Scripts that no page names and no script
imports come first. It runs only `--help` and writes nothing. `--spark DIR` reads another tree (P200, #153).

`python3 tools/measure.py` prints the shape of the code under `scripts/` (every folder in it but the MicroPython
`stand_in/`), ending in a SCORE line (P322). `--rules` prints each breach of an architecture rule as
`rule:file:name:value`. `--rules --accept` writes the breaches as `tests/architecture_baseline.json` (P440, #585).

## Patterns and names in spark's core

New code in `scripts/` is small classes with one job each, in library modules, and `main()` only parses and prints
(AGENTS.md). Each class plays one of these roles, and its name or its docstring says which. The PO set this rule on
2026-10-14 ([P239](https://github.com/xmejkal/spark/issues/238), from the council's synthesis in
[PR #239](https://github.com/xmejkal/spark/pull/239)).

Some words first. A base class defines what a family of classes can do, and each subclass is one member of the family
that fills it in. A docstring is the text in quotes at the top of a class or a function, which says what it does. A
namedtuple is a small record whose fields have names, so a caller writes `result.verdict` and not `result[0]`.

| Role | What it is | Its name | Example |
|---|---|---|---|
| Service | runs the steps of one flow over objects it was given | ends in `Service` | `LookService`, `DeployService` |
| Strategy | a base class that a caller can swap for another | ends in `Strategy` when the noun alone does not say it does something | `ConsentStrategy`; `BoardReader` and `Flasher` stay plain, and their docstrings say Strategy |
| Adapter | wraps an outside program behind spark's own interface | a plain noun; the docstring says Adapter | `BoardConnection` wraps mpremote, the tool that talks to MicroPython on a board |
| Result | what a method returns, as a namedtuple | ends in `Result` | `ReadyResult`, `DeployResult` |
| Error | an exception | ends in `Error` (the deploy area only, for now) | `GateClosedError`, `DeployError` |
| Value | facts with no actions. A method can calculate from the facts (`token()`, `to_dict()`; `token()` reads the image file), and a `why_` or `find_` method can answer a question about them, reading the project's files if it must. None changes anything | a plain noun; the docstring says Value | `Port`, `BoardReading`, `LookReport`, `RestrictedPins`, `ProjectImage` |
| Store | reads and writes one place in the person's store, as JSON files | the noun of what it keeps, then `Store` | `GrantStore` keeps one grant file per board in `grants/` |
| Decorator | wraps an object of another class, has the same methods, and adds one behaviour around them | what it adds, then the whole name of what it wraps | `RetryingBoardConnection` cures the board once and runs the code again |
| Renderer | turns one value into lines of a sheet or the text of a file, and decides nothing again | what it draws, then its form | `NumberedList` and `MermaidDiagram` render the steps (`WIRING_VIEWS`); `WokwiBreadboardDiagram` and `SvgBreadboardDiagram` render the layout (`DRAWING_RENDERERS`), with `FILE_NAME`, `NOUN`, `PURPOSE_MESSAGE` and `SHEET_MESSAGE` |
| Platform | a bundle of factories for the parts that depend on the firmware's language: each `make_` method builds one | a plain noun; the docstring says what varies | `FirmwarePlatform` builds the flasher, the board connection, the ready check and the console probe for MicroPython |
| Fake | stands in for a real part in the tests, in `tests/fakes.py` | `Fake`, then the whole name of the part | `FakeBoardConnection`, `FakeConsoleProbe` |

The examples in this section are the deploy area's target names. P239's PRs 3 to 8 give the code these names. PR 3
gave `ConsentStrategy`, `TerminalConsentStrategy`, `GateClosedError`, `require_open_gate` and the unit suffixes. PR 4
gave `ReadyResult`, `DeployPlan` and `BoardLog`. PR 5 gave `ProjectImage`, `DeployError`, `tools.command_for` and
`board_look.BOOT_HINT` (PR 7 moved it to the flasher, and P213 b2 made it `boot_hint`). PR 6 gave `LookReport` (with `to_dict()`), `LookService`,
`BoardReading` and `board_look.report_lines`. PR 7 gave `flasher.Flasher`, `flasher.EsptoolFlasher` (which holds `ERASE`, `WRITE`,
`IMAGE_OFFSET` and `BOOT_HINT_TEMPLATE`) and `flasher.build_esptool_prefix`. P213 b2 replaced the constant: `boot_hint` is the
sentence an `EsptoolFlasher` holds, `boot_hint_for(places)` builds it, and `boards.ButtonPlaces` (a Value) names the
buttons from the record's `physical.buttons`. `board_doctor.step_sentence` does the same for the doctor's steps.
PR 8 gave `deploy_service.DeployService` (`plan`, `look`, `deploy`, `verify`), `deploy_service.DeployResult` and
`firmware_platform.FirmwarePlatform`. `deploy.py` only parses, prints and maps the exit code.

### The package

`scripts/spark/` is a package, and `scripts/` is on the path whenever a script runs (it is `sys.path[0]`) and in every
test, so `import spark.core.outcomes` needs no path change. `scripts/spark/core/` holds the leaf modules every script
shares: `outcomes` (the exit codes and the three outcomes), `text_guards` and `zone_time`. They import nothing of spark.
A script writes `from spark.core import outcomes` and then `outcomes.EXIT_OK`, or `from spark.core.outcomes import
EXIT_OK`. The other scripts stay flat in `scripts/` until their own card moves them. A tool that lists the scripts
(`tools/inventory.py`, `tools/measure.py`, the tests that read every script) looks in the folders under `scripts/` too.
Most of them leave out `scripts/stand_in/`, but `test_no_magic_strings` reads it too. `test_orphans`,
`test_self_confirmation` and the inventory leave out each `__init__.py`. A child started with
`python3 -I` never imports `spark.core`, because `-I` drops the script's folder from `sys.path`.

### The rules test

`tests/test_architecture.py` reads `scripts/` and `tests/` with `ast` and holds each breach against
`tests/architecture_baseline.json`. One test method checks one rule (R1, R2, R3, R6, T1, T2, T4, X2, U1, C1, C3, V1). Each
rule is one sentence in `measure.RULES` in `tools/measure.py`, which the test's docstrings and its failure messages read;
`python3 tools/measure.py --rules` lists every breach with its rule.

The baseline lists the breaches that exist today, one `"rule:file:name": value` per line and sorted, so two branches
merge line by line. The value is the measured size, not only the name. The baseline only shrinks: a new breach fails,
a value above its entry fails, and so does an entry the code no longer has. A value below its entry passes; write it
back with `python3 tools/measure.py --rules --accept`, which takes only values that fell and entries that are gone and
refuses a new or risen breach. `--accept-new` writes those too: use it only for a rule that enters or for a branch that
rebases on another one, and give the reason in the PR. A failure names the rule and its limit, the file, the name and
the value, and `python3 tools/measure.py --rules` shows every breach.

R6 and C1 list a class by its qualified name (`Outer.Inner`). V1 lists the raises of a `ValueMessageError` or a subclass
whose template is no string constant, per class (`V1:file:Class`); see the next section. T1, T2, T4, X2 and C3 count the breaches of a file under
one key: they say how many, not where, so a new breach next to an old one shows only as a higher count. A baseline of
200 entries hides what it lists: each slice pays down the lines it touches.

### Messages that hold a value (V1)

An error that puts a path, a name or a record's field into its sentence inherits from `ValueMessageError`
(`scripts/spark/core/text_guards.py`, [P444](https://github.com/xmejkal/spark/issues/592)) and a raise passes the values as
arguments: `raise ToolProblem("%s is not JSON (%s)", path, broken)`, never `"..." % (path, broken)`. The class puts each value on
one line, keeps a number and a `%r` value as they are, and keeps the raw values on `.values`. Rule V1 counts the raises that
still build the text first; the baseline lists them and may only shrink. `Class.of_lines([...])` raises several sentences, one
per line, each flattened.

### One responsibility, one name

The PO agreed these rules on 2026-10-21 ([P381](https://github.com/xmejkal/spark/issues/488)): "let's try to stick
to the rules we set". New code follows them now. Today's names change in the names pass
([P382](https://github.com/xmejkal/spark/issues/489)) and the v0.13 area moves, so an old name is no example.

1. One word has one meaning in the code, the docs, the JSON and Miro. The P323 glossary holds the words.
2. A name says what the thing is for, not which tool does it. Only the adapter that wraps a tool carries the tool's
   name: `BoardReader` is the role, and `EsptoolBoardReader` fills it with esptool.
3. Each level has one responsibility. You can say it in one sentence without "and".

   | Level | Its one responsibility | Its name | Example |
   |---|---|---|---|
   | CLI | one topic for a person and Claude, with one subcommand per job | a noun | `parts.py`, with `parts.py show` |
   | Operation | one job, with one public method, `run()` | a verb, then its object | `ShowPart` |
   | helper | one thing, with several methods about it | an `-er` noun or a plain noun | `BoardReader`, `PortFinder` |

4. An Operation's module, class and op name (printed as `op` in the JSON) use the same words: the module `show_part`,
   the class `ShowPart`, the op `"show-part"`. Its subcommand is the verb alone, because the CLI's topic noun gives
   the object: `parts.py show`. An `op` that a golden or a command page already pins keeps its spelling (decision 5 of
   the refactor plan, the PO on 2026-10-26); only a new Operation follows this rule.
5. A class that only reads says so in its name: `Reader`, `Finder` or `Probe`. A class or a method that changes a
   board, a file or a port has a verb that names the change: `write`, `erase`, `cure`, `save`.

The role table above still applies. Its role words end a name, and `Fake` starts one. A Service, a Store or an
Adapter from that table is a helper with its role word, and an Operation calls it.

These rules name a class, a function or a constant:

- Name a thing for what it is to someone who has never seen spark.
- A subclass is what varies, then the base's whole name: `TerminalConsentStrategy`, `EsptoolBoardReader`.
- A function starts with a verb. A function that returns a reason or None starts with `why_`. A function that raises
  in place of returning False says so: `require_open_gate`.
- A constant that holds a number carries its unit (`_S`, `_MB`). A constant that holds a sentence ends in `_HINT` or
  `_MESSAGE`.
- Code decides on a named constant, never on a sentence ([P260](https://github.com/xmejkal/spark/issues/282)). A
  message is the text a person reads, and a phrase is an outside tool's words. The code that writes a value and the
  code that reads it import the same name, for example `needs.WHY_NO_RECORD`. An outside tool's phrase lives in one
  constant next to the code that reads it, and its comment names the tool. A code is not a message, so it takes no
  `_MESSAGE` suffix. `tests/test_no_magic_strings.py` fails on a literal with a space in a comparison, a `match`
  case or a search such as `startswith` or `re.search`. It does not see a one-word literal, a sentence built at run
  time, a dictionary key or a split, so a reviewer checks those.
- Only the deploy area uses the `Error` suffix now. The rest of the repository changes in v0.13
  ([#94](https://github.com/xmejkal/spark/issues/94)).

Each docstring says these things:

- A class: its role word first, then its job in one sentence, the objects it is given, what a subclass must supply,
  and what it raises.
- A public function: what it returns (the shape of a tuple or a dict), what it raises, and what it never does, such as
  erase or write.
- A module: what it is a library for, and who calls it. A constant: its unit or its source.

A tiny value or a calculation with no state stays a plain function or a namedtuple. Make a class when something holds
state and offers several actions on it, or when a test or a caller must swap it.

The fake of a part that a caller can swap lives in `tests/fakes.py` and starts with `Fake`, for example
`FakeBoardConnection` and `FakeConsent`. A fake of a tool's output, such as mpremote's, stays in its test file.

The PO's bench tools for live work on a board sit beside the deploy area. `scripts/reach.py` runs one line on the
board on USB and cures it once when its USB output died at power-on (P251,
[#264](https://github.com/xmejkal/spark/issues/264)). Its flags are `--project`, `--port`, `--json` (one line for the
bench log) and `--cure-first` (the bench's cold arm). It is not in [agents.md](agents.md) until P247 puts it behind
the PO's grant.

## One board per project

Spark handles one board per project folder today. A gadget with two boards, such as rc-car's car and remote, is two
project folders, each with its own `init_project.py` run and its own `parts/`. Until a board folder has its own
`.spark/`, the build and `check_all.py --project` both read its parent's rules and parts
([P319](https://github.com/xmejkal/spark/issues/403)). When `check_all.py --project` or
`init_project.py` finds two built designs, `design.one_board_message` says so and names a `--circuit` path. Many
boards in one project come with v0.13 ([#94](https://github.com/xmejkal/spark/issues/94)): a board is a folder, and
the project lists the folders. The decision and its costs are in the P318 finding, in
[PR #404](https://github.com/xmejkal/spark/pull/404).

## The docs name only what is there

[`tools/check_docs.py`](../../tools/check_docs.py) reads `README.md`, `AGENTS.md` and these guides. The suite runs it
as `tests/test_docs.py`. It fails when the docs:

- name a `/spark:` command or a `.py` script that does not exist;
- have a row in the commands guide's Skills or Agents table that names none;
- leave a command, skill or agent out of README.md or the commands guide;
- show a flag that its script's `--help` lacks;
- link a relative file or heading that is not there;
- paste an output without the date and version it ran on;
- carry a personal path;
- are cited by a file in `scripts/`, `data/`, `commands/`, `skills/` or `agents/` under a `docs/….md` path that is not a file;
- leave out of README.md the version that `.claude-plugin/plugin.json` ships.

A ` ```sh ` block marked `<!-- runs: exit N -->` is run in an empty project, with a store of its own, and must exit
`N`.

Nothing mechanical checks a skill or agent named in prose, an absolute link, or a second, wrong version; the council
reads those. Nor can it tell whether a step's status is still current. So when a step of the [journey](journey.md)
changes what it does, the change updates the journey guide and the README's *What works today*: item 8 of the
[Definition of Done](../../scrum/README.md#definition-of-done).

## Findings rows

The findings of a PR's councils, reviews and refuters go in one rows file for that PR:
`docs/observations/rows/<card>-<topic>.md`, for example `p296-rows-per-pr.md`. A sweep with no card starts with its
date, for example `2026-10-18-keep-current.md`. A second PR on the same card takes a topic of its own. The file uses the header
`| # | claim | source | status | evidence / where it went |` and numbers its rows 1, 2, 3. Each status cell starts
with one of the words in `docs/observations/INDEX.md`'s status table, written plain. A row is cited as `<file>#<n>`.
`docs/observations/INDEX.md` takes no new rows (P296, #358), and `tests/test_observation_rows.py` guards both rules.
To list the unresolved rows (`raised` or `verified`), run this line from the repository root:

```
/usr/bin/grep -nE '\| \**(raised|verified)' docs/observations/rows/*.md docs/observations/INDEX.md
```

The line also lists one old row, A7, whose status is `acted` but whose last cell starts with `verified:`.

## Checking a plan

A plan or a design holds some wrong claims, however often it is reviewed (P324, an experiment). Mark each claim as
measured (with the command that measures it), an estimate, or a proposal. Before the plan's PR, run
`python3 tools/factcheck.py <plan>` from the repository root and quote its output in the PR. It exits 1 when a
`file:line` reference names no file, a line past the end, or a file name two files share. It also lists the code names
that appear nowhere else in the repository, each of which must be one the plan proposes, and the sentences that state
a count, each of which needs its command or the word estimate. Whoever builds from the plan checks each file, line,
name and number in the code before using it, and writes a mismatch as a row ([the habit](../../scrum/WORKING_AGREEMENTS.md#habits--no-command-judges-these)).

## Where the work is planned

Every item is an issue on [spark's board](https://github.com/users/xmejkal/projects/2). The flow, the stages and their
limits, and the cadences are in [`scrum/README.md`](../../scrum/README.md). The words the team uses its own way are
in the [glossary](../../GLOSSARY.md).

One more team tool sits beside the gate: [`tools/board.py`](../../tools/board.py). `python3 tools/board.py status`
prints the state of both boards at every session start (the PO's session-start hook runs it; it always exits 0). It
reads each board whole, 100 cards a page, and judges where a card stands by the gate's one rule: spark's board read in
part, or a card in a stage the gate does not know, makes the status one could-not-run line naming it; a card with no
*Status* is said; and the bin's board read in part, or with no *Status* on any card, is set aside and said as the gate
says it, spark's cards counted alone. `python3 tools/board.py close "the day's one line"` posts the day-close as a status update on spark's board — one a
day, a second refused with exit 1; `--dry-run` prints it and posts nothing. Each verb's `--help` says what it prints,
posts and refuses.

[`scripts/cost.py`](../../scripts/cost.py) is not a team tool. It ships with the plugin: `parts.py --step` and `--tally`
import it to count what a project's run cost, and on one transcript it says what that run cost
([how it works](how-it-works.md#the-libraries)).
