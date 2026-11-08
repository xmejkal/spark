# Wave 6 plan: the other areas, firmware first (P681, #916)

> Pin down what the firmware tools print. Give their refusals codes. Then move the files. Wave 6 moves the eight
> areas that are still flat in `scripts/`, in the order of section 10: firmware, breadboard, checks, design with
> build, records with sourcing. Firmware, breadboard and checks are refined here, into three PRs each. W6-F1 gives the three firmware CLIs
> a golden net with `fake_wokwi_cli.py`, and no run spends a Wokwi minute. W6-F2 gives their refusals codes, text
> unchanged. W6-F3 is the move: six modules and the stand-ins go into `scripts/spark/firmware/` under the names of
> `areas/firmware.md`, and no module re-exports an old name. W6-F1 starts now. W6-F2 and W6-F3 wait for PR #906 and PR #915 (W5-3a).
> Breadboard and checks are refined too (P690): W6-B2 and W6-C2 give their refusals codes, text unchanged but for
> P688's item 3 (a package with no `bom.csv`: a sentence and exit 2, two new goldens), and the move is two PRs, W6-B3
> and W6-C3, because together they are three times W6-F3. Design with build is refined too (P698). It gets seven PRs.
> W6-D1 is one golden net with a fake `tsci` and a fake converter. W6-D2 and W6-U2 are the codes, design then build.
> W6-D3a, W6-D3b, W6-D3c and W6-U3 are the moves, each at most W6-F3's size, 605 mutation rows in all. `BuildService`
> and the N19 Operations are later cards, because a move PR adds no logic. Records with sourcing stays one paragraph,
> with what must be refined first. Open question 1 is answered: a big move is one PR per area, or more.

Fable 5.1 wrote this plan on 2026-11-07, against `origin/main` 4e63057e. W5-1 (#914) and W5-2 (#913) are in main.
W5-3a (#915) and W5-3b are stacked on PR #906. Every firmware count below is from that tree. A name marked "proposed" is not
in the code yet, and "est." marks a guess. P690 (2026-11-08) refined the breadboard and checks sections against
`origin/main` 46bca725, and every breadboard and checks count is from that tree, with W6-F1, W6-F2, W6-B1 and W6-C1 merged and W6-F3 (P685) in Build.
P698 (2026-11-08) refined the design-with-build group against `origin/main` 924e48a4. Every count of that group is from
that tree, with the firmware group done and W6-B2 merged.

## Council

Round 1 (2026-11-07): the refuter on Opus (10 findings, 8 held, 2 rejected: the counts and "no import cycle" hold)
and an architecture lens on Sonnet. What changed:

- A golden child with the shim missing ran the real `wokwi-cli` with the real token: `~/.local/bin` is on PATH,
  `~/.zshrc` exports `WOKWI_CLI_TOKEN`, `golden_bench.child_env` passes every non-`SPARK_*` variable on, and
  `tools.merged` keeps the default `also` list. W6-F1 sets a fake token in the child env, sets `"also": []` on the
  project's entry, and a test asserts the shim is the command found. The mutation row that unset the shim is gone.
  It is risk 1.
- `import_child.py` moved as is adds `X2:scripts/spark/firmware/import_child.py:main:1` (reproduced). W6-F3 renames
  its `main` to `import_one`.
- Sites were missing from W6-F3. `tests/test_import_firmware.py:613` runs `scripts/import_child.py` by path. The
  three stand-ins name their own old path in a sentence (`machine.py:228`, `fallback/framebuf.py:39`,
  `fallback/micropython.py:39`). Tests at lines 138 and 371 assert those sentences.
- W6-F2 breaks 5 mutation rows whose `find` is `reason=board_codes.X` in `project_image.py` (`p239-pr5`,
  `p429-firmware-line`, `p433-bench-codes`). W6-F2 rewrites them and proves them with `--anchors`.
- "W6-F2 touches no file of #906 or #915" was untrue: `scripts/board_codes.py`, `docs/guide/agents/json.md`,
  `commands/deploy.md` and `tests/test_json_contracts.py` are #906's, and `test_json_contracts.py` and
  `golden_bench.py` are #915's. W6-F2 branches from the first main that holds both.
- `needs_person` means the person must use their hands first (`json.md`, line 399). A paid run is consent, not
  hands: the `run-scenario` step carries an `effects` entry that names the spent Wokwi CI minutes (round 2 dropped
  this). `needs_person` stays on the token and install steps (round 2 dropped this too).
- A table maps each name of `run_scenario.py` to its new file.
- Numbers: `emit_board.py` is 1,208 lines, `project_image.py` raises 4 codes at 5 sites, and the 47 import lines
  are those outside the six modules. 5 more sit among them.
- The lens: `--json` for `run_scenario.py` and `flash_image.py` does not serve the bar and is out of W6-F2. When an
  agent needs it, it becomes a card. W6-F2 is codes, text unchanged (round 2 drops the step fields too). Open
  question 2 is gone.
- Batching: a later area's net PR (tests only) can open while a move PR is open. One move PR at a time stays.
- The short version starts with three plain sentences, the diagram is "after W6-F3", and each later group is two
  sentences.

Round 2 (2026-11-07, the refuter on Opus, the changes only): 4 held, 2 rejected (no path to a paid run is left, and
the rest of the W6-F3 list holds). What changed:

- The W6-F1 row "the fake token not set" survived on the PO's machine: `tools/mutate.py:98` hands `os.environ` to
  the run, `child_env` passes it on, and `fake_wokwi_cli.py` never reads `WOKWI_CLI_TOKEN`. The shim now exits
  non-zero unless `WOKWI_CLI_TOKEN` equals the fake value, so the row dies on every machine.
- The W6-F2 row counts are 1 in `p239-pr5`, 1 in `p429-firmware-line` and 3 in `p433-bench-codes`. The 3 swap rows
  of `p433` name `board_codes.X` in `replace` too, so both `find` and `replace` are rewritten, then `--anchors`.
- The step fields had nowhere to show: `import_firmware.py:120` returns `answer(...)` with no `next`, and `--json`
  is dropped. W6-F2 is the codes only, text unchanged. The `effects` entry, the `needs_person` part, their rows and
  closing check 2 are gone. The step fields come with the later `--json` card.
- One more W6-F3 site: `tools/check_commit.py:94` leaves out only paths that start with `scripts/stand_in/`. After the
  move it tests for `stand_in` in the path's parts, as `measure.py:238` does.

P690 round 1 (2026-11-08, the refuter on Opus and an architecture lens on Sonnet, on f6cbf0f1). The PO decided: P688's
`SystemExit` folds into W6-C2 (X2 counts a `raise SystemExit`, `measure.py:509`), the nine Extract Functions go into
the codes PRs so the moves stay `git mv`, and the two-PR move is open question 1's proposal. The rest: the codes an
agent can receive, the diagram's arrow, `Refusal`'s home, the `MAY_READ` keys, the rows by hand, the `NotDrawn` sites,
`--accept-new`, the area page's C1 note, the table test's tuple and the `check_spine` arrow.

P698 round 1 (2026-11-08, the refuter on Opus and an architecture lens on Sonnet, on 9428ddb2). The coordinator decided:
`Stage` goes to `stages.py` and `said_of_a_crash` to `build_service.py`, so the `check_spine` split makes no cycle.
The fakes call `/bin/mkdir`, `/bin/cp` and an absolute Python, and the tools override sets `"needs": []`, because a
`PATH` of the shim folder alone broke both (reproduced). The rest: `boards.PLUGIN_ROOT` for `SCRIPTS.parent`, a
reference-design Case, the counts (20 refusal Stages in `run`, 30 `DesignError` and 11 `Impossible` sites, 21 `MAY_READ`
keys, six `NotDrawn` sites in `part_shape.py`), `part_shape`'s move as a done-item with its page edits, `json.md` for the
new `code` key, and the rows file `docs/observations/rows/p698-wave6-plan-design.md`. Round 2 (the refuter on Opus, on
d5fe9864) held both blockers and added five fixes: `simulation_could_not_look`'s home, the `stages` name clash and
import by name, the reference Case's store override, the one `part_shape` site, and the 20 patch sites as a done-item.

PR council (2026-11-07, PR #919: one Sonnet reviewer, the refuter on Opus). What changed:

- W6-F1 opens with a guard line, and the token check lives in the temp-folder shim, not in `fake_wokwi_cli.py`,
  which four places run directly (`test_run_scenario.py:30`, `test_deploy.py:36`, `test_journey_basic.py:51`,
  `golden_bench.py:35` and `:154`).
- One word for one thing: W6-F1 is the golden net, W6-F2 the codes, W6-F3 the move. "Shim" is the wrapper script
  alone, and `fake_wokwi_cli.py` is the fake tool.
- W6-F2's size is one pair, in its section and in Review size.
- W6-F3: the `run_scenario.py` split is its own commit, and the goldens gate each commit.
- Four rows name `board_codes.X` in `replace`, not three: `p429`'s one and `p433`'s three.
- `check_commit.py:94` is in `scripts_size()`, the size line's code count (P99), not the lint.
- The round-1 `effects` bullet says that round 2 dropped it.

## Open questions

Only the PO answers these. Until he does, the plan takes the default.

1. Batching. Decision 4 (epic #94, 2026-10-26, his words in `refactor-plan.md`'s decisions table) asks for one pass
   if it does not take too long, else a continuous version. Once an area's golden net exists, its move is a mechanical PR
   with no new logic. When the files of two areas do not overlap, their moves can share one PR: breadboard with
   checks, and design with build (the page already pairs them). Records with sourcing stays its own PR, because it
   splits `parts.py`. Default: the golden net and the codes stay one PR per area. The moves go in batches: firmware
   alone, then design with build. Records with sourcing follows. One move PR is open at a time, so a broken main is one
   revert away. A later area's golden net PR holds tests only, so it can open while a move PR is open, in its own
   worktree. P690's fact: breadboard with checks is 4,909 lines, 284 rows (about 7.6 hours of one serial mutation run)
   and 44 keys, three times W6-F3. Proposal: two move PRs, W6-B3 then W6-C3, decision 4's "else a continuous version".
   The cards are filed as two. Only W6-B3's start waits on the PO. If he says one PR, the two branches become one.

## What the refactor plan said, and what the tree says

The refactor plan (section 10, "Wave 6") gives each area three PRs and about 900 lines. `areas/firmware.md` names the
target modules. Today:

- Six modules are the firmware's: `flash_image.py` (315 lines), `import_firmware.py` (126), `import_child.py` (87),
  `run_scenario.py` (590), `project_image.py` (128) and `sim_project.py` (410). Together 1,656 lines. Beside them sit
  `stand_in/machine.py` (231) and `stand_in/fallback/` (`framebuf.py`, `micropython.py`, 86 lines), which are not
  spark code. The page does not name `import_child.py`. It is the child program of `import_firmware.py`, run by path
  with `-I`, and moves beside it.
- 26 files outside the six import one of them, in 47 import lines: 11 under `scripts/` (15 lines) and 15 under
  `tests/` (32). 5 more import lines sit among the six (`run_scenario` imports `flash_image` and `sim_project`,
  `project_image` imports all three). No import is lazy. Nine importers are bench files: `deploy_service`, `board_look`, `firmware_platform`,
  `ready_check`, `board_connection`, `image_evidence`, `board_console`, `download_mode` (W5-3a moves all eight) and
  `spark/bench/deploy_image.py`. `check_spine.py` (build) and `onboard_parts.py` import `sim_project`.
- The six import `boards`, `store`, `tools`, `emit_board`, `parts`, `board_codes` and `spark.core`. Firmware reaches
  design, records and core along the arrows of the overview. `sim_project` reaches sourcing (`parts.chip_folder`,
  `CHIP_SOURCE_SUFFIXES`, `definition_path`) through design's arrow. `project_image` imports the bench leaf
  `board_codes` for four `DeployError` reasons at five raise sites: an upward edge. W6-F2 gives those four codes a
  firmware home.
- 228 mutation rows in 34 tables name one of the six by path (`flash_image` 64, `run_scenario` 69, `sim_project` 46,
  `import_firmware` 24, `project_image` 15, `import_child` 10).
- 15 keys of `tests/architecture_baseline.json` hold a firmware path: `R1` for the `main` of `flash_image.py` (36
  lines) and `run_scenario.py` (28), `R6:scripts/run_scenario.py:ScenarioRun`, eight `T1` keys and four `T2` keys.
- Every `print` and `sys.exit` of the three CLIs sits in its `main` or its module tail (checked with `ast`). No
  function of the six is over 40 lines. When each `main` stays in `scripts/`, the library parts move under
  `scripts/spark/` with no new R1 or X2 breach.
- The 25 goldens in `tests/golden/` are all the bench's. `tests/test_json_contracts.py` checks `import_firmware
  --json`. `golden_bench.build_project` already runs `ScenarioRun(...).run(FAKE_WOKWI_CLI)` with
  `tests/fake_wokwi_cli.py`, and `tests/test_run_scenario.py` runs `main` with `tools.find` patched.
- The five test files (`test_flash_image`, `test_import_firmware`, `test_run_scenario`, `test_project_image`,
  `test_sim_project`) hold 3,103 lines. 14 pages under `README.md`, `docs/guide/`, `skills/`, `agents/` and
  `commands/` name a firmware module path, and 182 files in all docs.

## The order, and wave 5's open PRs

W5-3a (#915) moves 18 bench modules. Eight of them import firmware, and W6-F3 rewrites those import lines. W5-3b
renames nothing in a firmware file. So:

1. W6-F1 starts now. It adds files under `tests/` and edits no file of #906 or #915. `tests/golden_bench.py` is
   imported, not edited.
2. W6-F2 edits `scripts/board_codes.py`, `docs/guide/agents/json.md`, `commands/deploy.md` and
   `tests/test_json_contracts.py`, which #906 edits, and `test_json_contracts.py` and `golden_bench.py`, which #915
   edits. So W6-F2 branches from the first main that holds #906 and #915. W6-F3 follows it. If W6-F1 is merged and
   #906 is still open, the reply to the PO names #906 as the one thing the firmware group waits on. Nobody rewrites
   his PR.

After this plan merges, three cards are filed as sub-issues of epic #94, in this Ready order: W6-F1, W6-F2, W6-F3.
When a later group is next, it gets its cards.

## The PRs

### W6-F1, the golden net

Guard, do not skip: every child gets a fake `WOKWI_CLI_TOKEN`, the shim's tools entry sets `"also": []`, and the
shim refuses any other token. The PO allows no paid Wokwi run (2026-10-31).

Goal: what `run_scenario.py`, `flash_image.py` and `import_firmware.py` print today stays what they print, so no
move breaks it. The fake tool is `tests/fake_wokwi_cli.py`, which exists. The shim is the new wrapper script in the
temp folder that the tools layers find and that runs the fake tool.

Files: `tests/golden_firmware.py` (proposed, a helper beside `golden_bench.py`) and `tests/test_golden_firmware.py`.
The helper reuses `golden_bench.build_project`, `child_env`, `scrub` and `replacements_of`. It adds what a child run
of `run_scenario.py` needs that the in-process run did not: a `wokwi-cli` the tools layers find. The project's
`.spark/tools.json` names the simulator with `"kind": "path"`. Its `"exe"` is a shim in the temp folder, and the
shim runs `python3 tests/fake_wokwi_cli.py "$@"`. `tools.find` uses `shutil.which(exe)`, which takes an absolute
path. The entry sets `"also": []`, so `tools.merged` adds no other command for the role. The child env sets
`WOKWI_CLI_TOKEN` to a fake value, because `child_env` passes the parent's variables on and the PO's shell exports the
real token. The shim exits non-zero unless `WOKWI_CLI_TOKEN` equals that fake value. So a child that reaches the shim
with the real token fails its golden, on every machine. The check sits in the shim, not in `fake_wokwi_cli.py`. Four
places run the fake tool directly with no token: `test_run_scenario.py:30`, `test_deploy.py:36`,
`test_journey_basic.py:51`, and `golden_bench.py` at lines 35 and 154. A test asserts that `tools.find("simulator", project)` in the
golden project is the shim. No golden run spends a Wokwi minute (the PO, 2026-10-31: no paid Wokwi runs). The Case is a `namedtuple` of its own:
`golden_bench.Case` without the two canned board files.

Goldens, est. 8 files: `run-scenario-ok.txt`, `run-scenario-problems-never-ready.txt`,
`run-scenario-could-not-run-no-token.txt`, `run-scenario-could-not-run-no-sim.txt`, `flash-image-ok.txt`,
`flash-image-could-not-run-no-interpreter.txt`, `import-firmware-ok.json`, `import-firmware-problems.json` (a
firmware module whose import raises). The scrub replaces the run's paths as the bench's does: `<project-dir>`,
`<spark-home>`, `<repo>` and `<python>`. It also replaces the run log's date and sha256 lines (`golden_bench.CLOCK`
and a sha256 pattern). None of the three CLIs runs through `run_cli`, so a firmware run has no `Privacy`. A path in
the text is a scrubbed path, not a masked one.

Tests: one test per Case, and `SPARK_ACCEPT=run-scenario` writes the goldens from today's output and fails, as the
bench's does. The class takes `needs_littlefs` (`flash_image` imports the `littlefs` package).

Mutation (`p<card>-firmware-net.json`, est. 4 rows). The scrub skipped. A Case's exit code ignored. The sha256
pattern dropped. The fake token not set, so the shim exits non-zero and the golden fails. No row unsets the shim,
because that row runs the real CLI. Proven with `--anchors`, run with `--copy`.

Review: no new product logic. One reviewer on the everyday model and the refuter on the strongest. Size est.: 120
test lines and 8 goldens.

### W6-F2, the codes (after #906 and #915)

Goal: each refusal of the three CLIs has a code. An agent decides on the code (P260). The text lines stay byte-equal
to the W6-F1 goldens, and the exit codes stay.

Files: `scripts/firmware_codes.py` (proposed, a leaf, the shape of `board_codes.py` and `idea_codes.py`: the
constants, then `CODES` with one sentence each). The name is unique under `scripts/` (C1), because
`spark/core/codes.py` exists. `run_scenario.py` and `flash_image.py` keep their text output. Each refusal site
raises or returns with its code, so the code is in the library for the Operation that comes later. The
`import_firmware.py --json` items gain a `code` key. `project_image.py` raises four `DeployError` reasons at five
sites: `NO_SIM_TOML`, `FIRMWARE_LINE_BAD` (twice), `NO_IMAGE` and `LOG_UNREADABLE`. It takes them from
`firmware_codes`. `board_codes` keeps the four names as aliases until W6-F3. In W6-F3 the bench reads them from
firmware. That ends the upward edge. A `--json` for the two text CLIs does not serve the bar today (the lens, round
1). When an agent needs it, it becomes a card.

The codes, est. 16, read from the refusal sites. `run_scenario.py`: `no_token`, `no_sim_project`, `never_ready`,
`step_timeout`, `simulator_lost`, `board_silent`, `simulator_not_started`, `simulator_failed`. `flash_image.py`:
`no_interpreter`, `files_not_folder`, `build_unknown`, `interpreter_damaged`, `tool_missing`. `import_firmware.py`:
`import_failed`, `nothing_to_import`, `import_timeout`. The PR reads each site and reports the real count.

No step fields in this PR. `import_firmware.py:120` returns `answer(...)` with no `next`, and the two text CLIs
print no envelope, so an `effects` entry or `needs_person` has nowhere to show. They come with the later `--json`
card. The refactor plan's "codes and `needs_person`" is read so for firmware.

Tests: in the three existing test files. Each code is asserted as a literal (`test_self_confirmation`, P677 row 26).
Each refusal site names its code. The `import_firmware --json` output is checked against the envelope contract in
`test_json_contracts.py`. The text output of each W6-F1 Case is unchanged. `CODES` names every constant once. Five
mutation rows name `board_codes.X` in `project_image.py`: one in `p239-pr5.json`, one in `p429-firmware-line.json`
and three in `p433-bench-codes.json`. Four of them name it in `replace` too: `p429`'s one and `p433`'s three. Both
`find` and `replace` get the new module name, proven with `--anchors`.

Mutation (`p<card>-firmware-codes.json`, est. 8 rows). A code dropped from an item. Two sites with one code swapped.
`CODES` missing a constant. The text line changed. The exit code changed. The alias in `board_codes` broken.

Docs: `docs/guide/agents/json.md` (the three ops and their codes), `agents.md`, `commands/build.md` and
`commands/deploy.md` where they show the output. Mark the new code `# --- MVP ---`.

Review: it holds logic. The lenses on the everyday model, the refuter on the strongest, one mutation run. Size est.:
80 product lines, 80 test lines, the 8 goldens unchanged.

The build's check of this section (P684, 2026-11-08, rows 8 to 17 of `docs/observations/rows/p684-firmware-codes.md`)
changed three things before any code:

- One code per refusal site, not per cause. A site whose one `except` catches several causes gets one code that names
  what they share: `ScenarioRun.problem()`'s `try` and `flash_image`'s `ToolProblem`. No `try` is split and no reason
  is added to `ToolProblem`. A split is a card when an agent needs to tell the causes apart. The one exception is
  `flash_image`'s bad `--config`, which today shares the damaged interpreter's `except`: it gets its own `except` and
  its own code, because the shared code would be wrong. The PR reports the real count.
- In `import_firmware.py --json`, only a `modules` entry that was not imported gains a `code` key. `problems` and
  `unchecked` stay plain strings, and "nothing to import" and "no `firmware/` folder" keep their codes in the library
  only. So `import-firmware-problems.json` is accepted again with the new key, and the other 7 goldens stay unchanged.
  The test asserts a `code` on each such entry. `import_firmware.py` prints no envelope.
- `firmware_codes` is a leaf, and `board_codes` stays one (U1). `board_codes` keeps its four names, and
  `TOOL_MISSING`, as equal literals, not imports. A test asserts that the five are equal in both modules, and the
  table test that keeps code tables apart lists these five as the one allowed overlap, until W6-F3.
  `firmware_codes` joins `measure.LEAVES` (`tools/measure.py:247`) and `planted_tree.LEAF_NAMES`
  (`tests/planted_tree.py:11`) in the same commit.

The refuter's plan check of this delta (rows 18 to 23) added four things:

- `flash_image.py`'s `except ValueError` (`:303`) catches six "use the build for the board's chip" errors and two
  "damaged" ones, so its code is `interpreter_unusable`, not `interpreter_damaged`. `ScenarioRun.problem()`'s last
  return (`why_outside_sim`, `run_scenario.py:466`) is the same cause as `project_image.py:55`, so it takes
  `FIRMWARE_LINE_BAD`. A `LittleFSError` that escapes `:303` as a traceback is a bug for a card, not this PR, because
  its fix changes the output.
- How a code travels: a refusal that raises gives its exception a `code` attribute. A refusal that returns a sentence
  returns a `Refusal`, a `str` subclass in `firmware_codes` with a `code` attribute. So no return shape changes, and
  the callers in `test_run_scenario.py`, `golden_bench.py:155` and `test_journey_basic.py:262` stay as they are.
- The mutation row "the alias in `board_codes` broken" becomes "a literal in `board_codes` differs from its
  `firmware_codes` twin". `sprint-10-p82-5.json:4` anchors on `flash_image.py`'s `except ToolProblem` print: the
  print stays byte-equal, and the row is proven again with `--anchors`. `json.md:191` names the new key.
- Size est.: 100 product lines, 100 test lines, one golden accepted again.

The second plan check (row 24) added one rule. A `%` format or a `.strip()` turns a `Refusal` back into a plain
`str`, so a site builds its `Refusal` from the final text. Four refusals never pass through a library function: the
missing simulator and the unset token in `run_scenario.main` (`:575`, `:578`), and `no_interpreter` and
`files_not_folder` in `flash_image.main` (`:291`-`:297`). Their codes are named in `main` only in this PR, and they
reach the library with the Operation in W6-F3 or later. The `Refusal` docstring starts with its role word ("Value:"),
as `Interpreter`'s does (R6).

### W6-F3, the firmware move (after #915)

Goal: `ls scripts/*.py` prints no firmware library module. `scripts/spark/firmware/` holds the area under the
names of its page. The three CLIs stay in `scripts/` as a `main` that parses and prints, with no module shim: no
`scripts/run_scenario.py` re-exports a name. Every import, mutation row, baseline key and guide page follows. The
goldens stay byte-equal.

Moves (`git mv`, then the page's names, one commit each, and the goldens run green after each commit). The
`run_scenario.py` split is its own commit. It splits in two.
`spark/firmware/scenario_run.py` holds `ScenarioRun` and the run log writer. `spark/firmware/scenario_steps.py`
holds `ScenarioSteps`, `StepNames`, the step constants, `file_hashes`, `printed_text` and `READY`. The library of
`flash_image.py` becomes `spark/firmware/image_builder.py`. The library of `import_firmware.py` becomes
`spark/firmware/import_probe.py`. `project_image.py`, `sim_project.py` and `stand_in/` move as they are.
`import_child.py` moves, and its `main` becomes `import_one`, because X2 counts a `main` under `scripts/spark/`
(reproduced in round 1). The child is a program run by path, so no caller names that function.

Where each name of `run_scenario.py` goes:

| Name | New file |
|---|---|
| `ScenarioRun`, `run_record`, `verdict`, `image_in`, `with_ready_wait`, `DEFAULT_IMAGE`, `ONE_RUN_MESSAGE`, `PASSED`, `PASSED_WITH_CAVEAT`, `NO_MAIN` | `scenario_run.py` |
| `ScenarioSteps`, `StepNames`, `file_hashes`, `printed_text`, `READY`, `READY_STEP`, `SET_CONTROL` and the other step constants | `scenario_steps.py` |

`scenario_steps.py` imports nothing of firmware, so the bench's imports of `READY`, `printed_text`, `ScenarioSteps`
and `file_hashes` pull no run logic in. `firmware_codes.py` moves in as the area's leaf. `spark/firmware/__init__.py` holds the index docstring
and nothing else: no `OPERATIONS` and no imports, because an `__init__` that imports its modules made the cycles of
wave 5 (P676 rows 4 and 10). The three `sys.path.insert` lines go. The industry words are Move Module and Extract
Module (Fowler, Refactoring, 2nd ed.).

The `__file__` paths that break, each fixed in this PR:

- `import_firmware.STAND_IN` and `CHILD` build `Path(__file__).parent / "stand_in"` and `/ "import_child.py"`.
  Both move into `import_probe.py`, beside the files they name, so the expressions stay. `import_child.STAND_IN_FOLDER`
  stays for the same reason.
- `flash_image.py:225` builds the rerun line with `store.format_rerun_line(Path(__file__), ...)`. In the library
  that names `image_builder.py`, not the CLI a person runs. The CLI passes its own `Path(__file__)` in.
- `tools/check_commit.py:94` leaves out only the paths that start with `scripts/stand_in/`. After the move it tests
  for `stand_in` in the path's parts, as `measure.py:238` does, so the stand-ins stay out of the size line's code
  count (`scripts_size()`, P99).
- `tests/test_import_firmware.py` names `scripts/stand_in/machine.py` (lines 36, 138) and
  `scripts/stand_in/fallback/<module>.py` (371, 382) by path, and line 613 runs `scripts/import_child.py` by path.
  The paths follow the move. `SCRIPT` (line 39) stays, because the CLI stays.
- The three stand-ins name their own path in the sentence they raise (`machine.py:228`, `fallback/framebuf.py:39`,
  `fallback/micropython.py:39`), and the tests at lines 138 and 371 assert it. The sentences say the new path.

What the rules do at the move, checked at 4e63057e:

- R1: no function of the six is over 40 lines, so none breaches the `scripts/spark/` limit. The two `R1` `main` keys
  stay, because the CLIs keep their path. Where the library takes a block, the PR trims that `main` toward 15 lines.
  When a `main` fits, its key goes.
- R6: `ScenarioRun`'s docstring starts with "Service", as the page says, and its key goes.
- X2: every `print` and `sys.exit` sits in the three `main`s, which stay in `scripts/`. So `scripts/spark/firmware/`
  prints nothing. The one X2 hit of the move is `import_child.main`, renamed above.
- T1: the eight keys are rewritten to the new paths. The baseline only shrinks (`test_architecture.py`).
- U1: `firmware_codes` joins `measure.LEAVES`. `project_image` no longer imports `board_codes`, and the bench's
  `image_evidence`, `ready_check`, `board_connection`, `board_console` and `download_mode` import
  `spark.firmware.scenario_steps` for `READY`, `printed_text`, `ScenarioSteps` and `file_hashes`.
- The 47 import lines become `from spark.firmware import <m>` or `from spark.firmware.<m> import ...`.
- The 228 rows move with `python3 tools/mutate.py --retarget scripts/<old>.py scripts/spark/firmware/<new>.py`,
  then `--anchors`. The rows of a function that moved from `run_scenario.py` to `scenario_steps.py` are retargeted
  by hand, and `--anchors` proves each `find` occurs once. No row is dropped. The retargeted tables run once, in
  parallel `--copy` shards, as the PR's one mutation run.

Tests: the five test files keep their names and import from `spark.firmware`. `test_architecture.py` gains the
closing `ls` check. The import-alone test of W5-3a extends to the firmware modules. It imports each one in a child
Python, with `python3 -c`. The page is regenerated with `python3 tools/map.py --write`. `firmware` appears
on it, because the map lists each folder under `scripts/spark/` with an `__init__.py` (P678 row 2).

Docs: the 14 agent-facing pages and `areas/firmware.md` (the file names, `import_child.py`, what waits). The pages
under `docs/discovery/` and `docs/archive/` are history and keep the old paths (`tools/check_docs.py`'s rule).

Not in this PR, with the reason. `SimulationEngine`, `WokwiCliEngine`, `ENGINES`, `RunLog`, `FlashImageBuilder` and
`SimulationEngineContract` are new shapes. Each has one implementation ("No base class with one implementation",
the not-do list). They wait for a second simulator or a second platform. The firmware Operations on `run_cli` wait
for a card of their own, as the bench's did in wave 4.

Review: no new logic. One reviewer on the everyday model and the refuter on the strongest, the retargeted tables as
the one mutation run. A whole-branch review runs before the PR, because it is the group's biggest diff. Size est.:
1,656 lines moved, 52 import lines, 228 rows, 15 baseline keys, 3 `__file__` fixes, 5 path sentences and tests.

P685 claims check (2026-11-08, against 46bca725). Each claim above was read in the code. These are wrong or stale:

1. The split table makes a cycle. `ScenarioSteps.passed_sentence` reads `PASSED`, `PASSED_WITH_CAVEAT` and the caveat
   sentences (`run_scenario.py:363`), and `from_log`, `run_record` and `file_hashes` share `_header` (`:534`).
   Decision: `scenario_steps.py` keeps its name (`run_log` is the file in `sim/runs/`, the refuter) and holds the run
   log's words and their reader: `ScenarioSteps`, `StepNames`, the step kinds, `READY` and the header lines. It also
   holds the `WHY_*`, `PASSED`, the caveats, `NO_MAIN`, `_header`, `run_record`, `file_hashes` and `printed_text`.
   `scenario_run.py` holds the rest, with `find_simulator` (the table misses it). The docstring and `EPILOG` stay.
2. It is false that the steps module imports nothing of firmware. `from_log` reads `sim_project.WHY_LOG_UNREADABLE`
   (`:316`), and `sim_project` imports `emit_board` and `parts`. Decision: the sentence moves to `scenario_steps.py`,
   and `sim_project.py:184` and `image_evidence.py:23` read it there. It then imports only `spark.core`.
3. `project_image.py:52` reads `run_scenario.DEFAULT_IMAGE`. Decision: it moves to `sim_project` beside
   `UNNAMED_FIRMWARE`, which is built from it, so `project_image` never imports `scenario_run`.
4. No `ready_check` exists. The bench readers are `board_connection`, `board_console`, `download_mode`, `ready_probe`
   and `image_evidence` (also `NO_MAIN`, `ONE_RUN_MESSAGE`, `PASSED`). After 1 to 3, all read `scenario_steps` only.
5. `build_command` (`flash_image.py:233`) is called by `project_image.py:57` and `image_evidence.py:415`, not by the
   CLI. Decision: `image_builder` names the CLI as `deploy_image.py:40` does (`parents[2]`), with a test.
6. `import_one` is taken (`import_firmware.py:70`). Decision: `import_child.main` becomes `import_named` (3 rows).
7. The CLIs keep `sys.path.insert` (`test_scripts_isolated.py:31` runs them with `-I`). Its `EXEMPT` (`:22`) goes.
8. Missed paths: `pyproject.toml:15`, `test_journey_basic.py:55`, `import_firmware.py:13` (help text),
   `tools/measure.py:8`, `tools/mutate.py:48,128` (docstrings) and `test_check_commit.py:98` (a planted path).
9. 15 test files import a firmware module, not five. Seven patches name `run_scenario`: `run_record` (3 sites, and
   `project_image` calls `scenario_steps.run_record` through the module), `subprocess` (2, global) and
   `STARTUP_ALLOWANCE_S` (`test_run_scenario.py:864`, to `scenario_run`). T2 counts stay.
10. Counts: 2,087 lines in the files, about 1,900 move. 59 import lines. 267 rows: run_scenario 74, flash_image 68,
    sim_project 46, stand_in 27, import_firmware 25, project_image 15, import_child 10, firmware_codes 2. 11 baseline
    keys name an old path: 2 R1, 1 R6, 8 T1.
11. `--retarget` moves every row of a file, but the CLIs stay. Decision: `--retarget` the 7 files that move whole (100
    rows). 16 rows stay on a CLI path (the three `main`s, `project_here`, `DEFAULT_TIMEOUT_S`, the import_firmware
    docstring). A scratch script gives each other run_scenario row to the one file that holds its `find` once.
    7 rows change their text. `--anchors` refuses one `sim_project` row today (`p97-council.json`, "re-check 1"),
    not this PR's miss.
12. 7 T1 keys move. `T1:scripts/flash_image.py:file-write` (`:329`, in `main`) and the two R1 `main` keys stay. So
    check 5 reads "no key of a moved library names an old path".
13. P684 did U1 (`LEAVES`, `LEAF_NAMES`). `MAY_READ` keys are stems and stay. Risk 5 is stale: five codes are
    shared, and they stay. `board_codes.py:15` and `test_json_contracts.py:255` say what is true now.
14. 6 guide pages name a moved file, not 14 (`agents/firmware-codes.md`, `agents/scripts.md`, `developing.md`,
    `how-it-works.md`, `journey/firmware.md`, `patterns-and-names.md`). The area page is under `docs/discovery/`.

These claims hold: R1 (the longest is `from_text`, 38 lines) and X2. The goldens run the CLIs by path
(`golden_firmware.py:117`). The bench makes no cycle. `tools/map.py` and `mutate.import_spec` need no change.

### W6-B1, the breadboard golden net

Goal: what `breadboard.py` prints today, and the files it writes beside the sheet, stays what it prints, so the
breadboard codes and the move break nothing. This net is the first of the breadboard group's three PRs.

Nothing is faked, and no run spends anything. `breadboard.py` runs no tool and opens no URL. This was checked: with
`subprocess.run`, `subprocess.Popen`, `urlopen` and `socket.create_connection` set to raise, `main` on
`button-light-xiao` returns 0. `page.html` and its `tsci` export are written by `check_spine.keep_tabbed_page`
(`check_spine.py:894`, `:766`), not by `breadboard.py`. So the paragraph below and `areas/breadboard.md:17` are wrong
to say "tsci faked" and "runs `tsci` for the page". This PR fixes both, `areas/breadboard.md:128` (the same error),
`:17` (it leaves out `breadboard.svg` and `wiring-record.json`), and the stale `tests/fakes.py:137`/`:147` there. Each child gets an empty store, so the sheet's "have" column is blank (the docstring, and
the store was still empty after each probe run). The child env is `golden_bench.child_env` (`tests/golden_bench.py:162`). It drops only `SPARK_*`, so the helper
pops `WOKWI_CLI_TOKEN`, and a test checks that. It passes the bench's canned flash id and device list, which
`breadboard.py` never reads.

The CLI: `breadboard.py requirements.json [--out FILE]`. Exit 0 means the sheet is written. Exit 2 means the run stopped
(`breadboard.py:67`, `:583`). It has no handled exit 1. A renderer that raises still exits 1 with a traceback
(`:548`-`:553`, `:559`-`:563`). Cases, est. 7, each probed on a copy of its fixture in
`tests/data/breadboard/`. Each copy keeps the fixture's folder name, because the sheet's title is that name
(`breadboard.py:451`):

| Golden | Fixture and change | Exit |
|---|---|---|
| `breadboard-ok-xiao.txt` | `button-light-xiao`: the sheet, `breadboard.json` and `breadboard.svg` | 0 |
| `breadboard-ok-firebeetle.txt` | `button-light`: the SVG only, "breadboard.json not written: Wokwi has no part with this board's pins" | 0 |
| `breadboard-ok-not-drawn.txt` | `motor`: no drawing, "nothing says how to draw L9110sModule in Wokwi" | 0 |
| `breadboard-ok-rebuild.txt` | `button-light-xiao`, run, then `button-only-xiao`'s requirements and `dist/` as `test_breadboard_keep.change_requirements` (`:44`) does, run again: `change:` and `not kept:` lines | 0 |
| `breadboard-could-not-run-not-built.txt` | `button-light` without `dist/board/circuit.json` | 2 |
| `breadboard-could-not-run-stale.txt` | `button-light` with `motor`'s `requirements.json` | 2 |
| `breadboard-could-not-run-bad-out.txt` | `button-light`, `--out no/such/x.md` | 2 |

The folder is `tests/golden-breadboard/`. A golden holds stdout, then stderr after `golden_firmware.STDERR_MARK`, then
`breadboard.json`, `breadboard.svg` and `wiring-record.json`, each after `LOG_MARK` with its name. A rebuild's golden
holds only the second run. Reuse, with no copy: `golden_bench.child_env`, `replacements_of`, `scrub`, `op_of` (from
`breadboard.py`, the op is `breadboard`), `check_golden(case, text, golden_dir=GOLDEN_DIR)` and `RUN_TIMEOUT_S`. The
scrub needs nothing new: no output of the probes held a run date or a hash. No Case reaches the `drawing differs:`
line (`:592`-`:593`) or the sheet's matching paragraph: only a mocked `_plan_layout` does, and
`tests/test_breadboard_match.py:126`-`:137` covers both.

Files: `tests/golden_breadboard.py`, `tests/test_golden_breadboard.py`, the 7 goldens,
`tests/mutations/p686-breadboard-net.json`, `docs/observations/rows/p686-breadboard-net.md`, and
`docs/guide/developing.md` beside the firmware lines (`:76`, `:96`). The helper (proposed) holds `CASES`, `run_script`
and a `Case` namedtuple: `golden script fixture argv exit_code plant then`. `golden_bench.py` is imported, not edited, because #915 edits it.

Tests: one test per Case. `SPARK_ACCEPT=breadboard` writes the goldens and fails. A test checks that every golden
has its Case. Another checks that no golden holds a path of this machine. These two repeat `test_golden_firmware.py`,
and a row asks to lift both into `golden_bench` once #915 merges. No `needs_littlefs`.

Mutation (est. 6 rows, proven with `--anchors`, not run in this PR): the scrub is skipped. A Case's exit code is
wrong. The stderr is dropped. The written files are not appended. The rebuild's first run is skipped. One product
row: `breadboard.py` stops printing its `not kept:` lines.

Review: no new product logic. One reviewer on the everyday model, the refuter on the strongest, one mutation run.
Size est.: 110 test lines and 7 goldens.

### W6-C1, the checks golden net

Goal: what the six check CLIs print today stays what they print, so the checks move breaks nothing. Tests only. It
edits no file of #906, #915 or #917.

Guard, do not skip. Only `check_vendor_pins.py` starts a child, `gh` (`check_vendor_pins.py:68`), and only without
`--offline`. The vendor-truth check of `check_all.py` reads offline (`check_all.py:256`). So `gh` is faked. A shim
named `gh` is W6-F1's shape: `#!/bin/sh`, then `exec` of the absolute `sys.executable` on `tests/fake_gh.py`
(proposed, the shape of `fake_wokwi_cli.py`). A bare `python3` fails on a `PATH` this short. The fake prints spark's kept header
(`.spark/cache/dfrobot_firebeetle2_esp32s3.pins_arduino.h`) in base64. A Case can change one pin in it. A Case can
also give an exit code, and then the fake fails. The child's `PATH` is the shim's folder alone. A test asserts that
it equals that folder and that the `gh` found on it is the shim. Why alone: in a probe for this plan, the interpreter of a shim did not start.
The search went on, and the real `gh` ran (a free public read). No Case runs `wokwi-cli`, KiCad or `tsci`. The six
call no `urlopen`, but `store.fetch` (`store.py:400`) can be reached through `boards.py`. So every child sets
`http_proxy`, `https_proxy`, `HTTP_PROXY` and `HTTPS_PROXY` to `http://127.0.0.1:9` and has no `WOKWI_CLI_TOKEN`, and
a test checks the child env. The live Cases check a board file copied into the project. So the header is kept in the
project's cache, not in spark's (`project_header`, `check_vendor_pins.py:117`). A test asserts that spark's cache is
unchanged.

The project: `build_project` (proposed) copies `tests/data/breadboard/button-light`, which holds a built
`dist/board/circuit.json`. It runs `init_project.py --board firebeetle2-esp32s3 --circuit dist/board/circuit.json`
as a child with its own store. It also writes `floating-rules.json`: the same rules with `pulled_by_firmware` empty.

Cases, est. 17. Each golden is `<op>-<name>`, and each exit code was seen in a probe run, except the one marked "read":
- `check-all`: `ok.txt` (rules removed, 0), `problems-floating-input.json` (`--rules floating-rules.json`, 1),
  `could-not-run.txt` (physics cannot assess the LED's series resistor, 2).
- `check-physics`: `could-not-run.txt` (2), `could-not-run-no-rules.json` (2, read: `check_physics.py:637-641`). No
  ok Case: run alone, physics reads no part records, so the LED's resistor cannot clear (`check_physics.py:629-630`).
- `check-footprints`: `ok.json` (0), `could-not-run-no-circuit.txt` (2).
- `compare-design`: `ok.json` (0), `problems-floating-input.txt` (1), `could-not-run-no-rules.txt` (2).
- `check-bom`: `ok.txt` (0), `problems-no-supplier-part.txt` (1), `could-not-run-no-package.txt` (2). The two zips
  are planted as bytes.
- `check-vendor-pins`: `ok-offline.txt` (spark's kept header, 0), `ok-live.json` (0), `problems-mismatch.txt` (1),
  `could-not-run-fetch-failed.txt` (2).

Folder: `tests/golden-checks/`. Files: `tests/golden_checks.py` (proposed, the helper) and
`tests/test_golden_checks.py`. Reuse, no copy: `golden_bench.op_of`, `scrub`, `replacements_of`, `RUN_TIMEOUT_S` and
`check_golden(golden_dir=...)`, and `golden_firmware.Case`, `plant` and `run_script`. Two small changes go into
`golden_firmware.py`: `plant` writes bytes as bytes, and `run_script` takes the child's `env` (the checks' env: no
token, the proxies, the shim's `PATH`). `golden_bench.py` is not edited, because #915 edits it. None of the six runs through `run_cli`, so a path in
the text is scrubbed, not masked.

Tests: one test per Case. `SPARK_ACCEPT=<op>` writes that op's goldens and fails. No golden holds a path of this
machine, and every golden has its Case. The guard tests are above. No `needs_littlefs`.

Mutation (`p687-checks-net.json`, 9 rows as built). The scrub skipped. A Case's exit code wrong. The proxies not set (the
child env test). The fake `gh` ignores its exit code. `floating-rules.json` keeps `pulled_by_firmware`. The child's `PATH` keeps
another folder. The token or `no_proxy` reaches the child. Planted bytes are written as text. Proven
with `--anchors`, run with `--copy` in parallel shards.

Not pinned, rows for the PR's rows file and proposed cards. `check_vendor_pins.py` on a missing board file ends in a
traceback with exit 1, which reads as a mismatch (`:204`). `check_bom.py` on a zip with no `bom.csv` exits 1 by
`SystemExit` (`:58`). For a missing circuit, `check_footprints.py --json` prints text (`:561-563`).

Review: no new product logic. One reviewer on the everyday model and the refuter on the strongest. Size est.: 110
helper lines, 110 test lines, 20 lines of the fake, 17 goldens.

### W6-B2, the breadboard codes

Goal: each refusal of `breadboard.py` has a code. The text stays byte-equal to the 7 W6-B1 goldens, and exit 2 stays.

What exists. Four code tables already sit in the area, each beside the Result or Value it decides for:
`breadboard_drawing.CODES` (`:44`, a dict with sentences, P412), `breadboard_keep.CODES` (`:39`, with `MESSAGES`),
`breadboard_changes.CODES` (`:28`) and `breadboard_match.CODES` (`:21`). `NotDrawn` carries a `code` (`breadboard_drawing.py:66`).
They stay where they are: each is read inside the area, and `check_spine.py` (design) imports `breadboard` anyway
(`:64`), a downward arrow of the overview. Twelve `NotDrawn` sites in `breadboard_drawing.py` (`:142` to `:392`) and
one in `part_shape.py` (`:226`, breadboard's after W6-D3b) raises with `code=None`. They end as a `NotWritten` with exit 0
(`breadboard.py:404`, "an older refusal", `breadboard_drawing.py:55`), not as a refusal of the run, so they are out of
scope and a card. The one refusal of the run with no code is `NotBuilt` (`breadboard.py:108`), raised at eight sites (`:183`, `:188`, `:190`, `:192`, `:195`,
`:201`, `:350`, `:356`), and `main`'s one `except` (`:581`), which also catches
`design.DesignError`, `store.StoreProblem` and `OSError`.

Files: `scripts/breadboard_codes.py` (proposed, a leaf, the shape of `firmware_codes.py`). `NotBuilt` gains a `code`
attribute as `NotDrawn` has (`__init__(message, code)`), and each raise site names its code. The codes, est. 5, read from
the sites: `not_built` (`:183`, `:350`), `built_from_other_requirements` (`:190`, `:201`), `build_failed` (`:195`),
`build_unreadable` (`:188`, `:192`, `:356`) and `input_unreadable` for the three outside exceptions, named in `main`
only, as W6-F2's four. The PR reports the real count. `breadboard_codes` joins `measure.LEAVES` (`tools/measure.py:247`),
`planted_tree.LEAF_NAMES` (`tests/planted_tree.py:11`) and the tuple of `TheBenchCodesTableTest`
(`tests/test_json_contracts.py:265`). No `Refusal`: every breadboard refusal raises. The page's "no module name repeats the area's name" yields to C1's basename
uniqueness, as `firmware_codes` did, and the page says so. This PR also extracts the three functions of 41 to 60 lines
that R1's 40-line limit would catch after the move (`_wiring` 45, `sheet` 42, `write` 47), one commit each, goldens
green, so W6-B3 stays a move.

Tests: in `tests/test_breadboard.py`. Each site's code as a literal (P677 row 26), `CODES` names every constant once,
the 7 goldens unchanged. Mutation (`p<card>-breadboard-codes.json`, est. 6 rows): two sites with one code swapped,
`NotBuilt` drops its code, `CODES` missing a constant, the sentence changed, the exit code changed.

Docs: `areas/breadboard.md` gains the module row. `json.md` gains nothing: `breadboard.py` has no `--json`, so the table
is library-only until the Operation. Review: it holds logic. One reviewer and the refuter on the strongest, one mutation
run. Size est.: 80 product lines, 60 test lines.
It touches no file of P685 but `measure.py:247`, `planted_tree.py:11` and `test_json_contracts.py`, one line each.

P692 claims check (2026-11-08, on main 6338f89e). The check stopped before any code, for one decision. The
coordinator decided it on the same day:

- Choice 2. `points`, `_wiring` and what they alone need (`Point`, `ROW_HOLES`, `_natural`, `printed_label`) move to
  `breadboard_steps.py` in one Move Function commit, before the code commits. W6-B3's table changes: they move
  with `breadboard_steps.py` to `wiring_steps.py`. The free lines are taken too. The module docstring stays.
- The three outside exceptions get three codes, because each asks for another action (P684's rule). A store
  problem reuses `board_codes.STORE_PROBLEM`'s literal. A small function maps them.
- P691 (#933) is corrected to 13 sites and takes the `check_spine.py:843` finding.

What the check found:

- Decision needed. `breadboard.py` is 600 lines, R1's module limit (`tools/measure.py:242`, counted by
  `splitlines`, `:449`). Every line the card adds there is the new key `R1:scripts/breadboard.py:<module>`, and the
  baseline can only shrink. The card adds about 20 lines. The import is 1, `NotBuilt.__init__` 4, the three
  extractions about 2, 5 and 5, and the wrapped raise lines about 3. A library function that gives the three outside
  exceptions their code adds 5 more, because `main` is the R1 key at 26 and cannot grow (P684 row 28). Prunes that lose no words give about 8.
  They are the orphan comment at `:74` and three docstrings whose `"""` sit on their own lines. About 12 lines more
  must go, by one of three choices:
  - Cut the module docstring, which is the `--help` text (43 lines).
  - Move code to another module, for example `points` and `_wiring` to `breadboard_steps.py`, which holds the step
    rule. This changes W6-B3's table.
  - Leave the code of the three outside exceptions to the Operation card.
- Counts: `LEAVES` is at `measure.py:245`, not `:247`. `NotDrawn` is at `breadboard_drawing.py:62`. In `part_shape.py`
  one `NotDrawn` site has no code (`:226`), not five: `:145`, `:161`, `:168` and `:173` pass one. P691's scope is 13
  sites, not 17.
- For a card: `check_spine.py:843` writes the sheet's `not written` entry with no `code`, while each drawing's entry has
  one, and it also catches `ValueError`, which `breadboard.main` does not.
- The rest holds. That is the four tables, `check_spine.py:64`, the 12 sites in `breadboard_drawing.py`, `:404` and
  `:55`. It is also `NotBuilt` at `:108` and its eight sites, the `except` at `:581`, and the three spans (45, 42 and
  47 lines).

### W6-C2, the checks codes (after P685)

Goal: each refusal of the six check CLIs has a code. The text and the JSON stay byte-equal to the 17 W6-C1 goldens.
One output changes, by the PO (P688's item 3): a package with no `bom.csv` gets a sentence and exit 2 from `check_bom.py`
(today a `SystemExit` on stderr and exit 1), and `check_all.py` loses its `SystemExit: ` prefix on that line. Two new
goldens pin both, and the comment at `tests/test_check_all.py:132` ("raises SystemExit") is updated.

Files: `scripts/check_codes.py` (proposed, a leaf). The page's `checks/codes.py` repeats `spark/core/codes.py`'s
basename, which C1 counts (`tools/measure.py:633`), so the name is `check_codes`, as `firmware_codes` and
`spark/idea/idea_codes.py` are named. The findings of a check keep their `rule` key: a Finding's `code` is the page's
target shape, not a refusal, and waits for the Operation card.

The sites, 20, and their codes, 14, read at 46bca725. The PR reports the real count.

| CLI | Sites | Codes |
|---|---|---|
| `check_all.py` | `Check.run` `:82` ambiguous, `:92` `RulesError`, `:95` any exception, `main` `:532` `DesignError` | `input_ambiguous`, `rules_refused`, `check_crashed`, `project_unusable` |
| `check_physics.py` | `rules_or_reason` `:617` (a loop over two files), `:620` `RulesError` | `no_circuit` or `no_rules_file` (the code rides in the loop's tuple, no new branch), `rules_refused` |
| `check_footprints.py` | `main` `:562` no circuit, `rules_asked` `:542`, `:546` | `no_circuit`, `no_rules_file`, `rules_refused` |
| `compare_design.py` | `compare` `:241`, `:246`, `:254`, `:258`, `:267` | `no_circuit`, `no_rules_file`, `rules_refused`, `circuit_not_json`, `no_rule_stated` |
| `check_vendor_pins.py` | `check_board` `:207`, `:217`, `:223`, `:228` | `no_vendor_variant`, `no_cached_header`, `header_not_fetched`, `header_has_no_pins` |
| `check_bom.py` | `main` `:166`, `read_bom` `:58` (P688's item 3) | `no_package`, `no_bom_in_package` |

How a code travels. Every site but three returns its sentence in a dict's `reason` or `unchecked`, or in a
`(None, why)` pair, so each sentence becomes a `Refusal`: a `str`, so `json.dumps` and every caller print the same
bytes. `Refusal` moves from `firmware_codes.py:17` to `spark/core/result.py` (the next paragraph says why), and the
three firmware import lines follow, after P685: `spark/firmware/image_builder.py:26`, `import_firmware.py:49` and
`run_scenario.py:47` on branch `p685-firmware-move`. No re-export stays. That is why this PR waits for P685. Two more
things follow the class: the mutation row `p684-firmware-codes.json:10` ("a Refusal drops its code", `refusal.code =
code`) points at `scripts/spark/core/result.py`, proven with `--anchors`, and `firmware_codes.py:7`'s sentence about
`Refusal` names its new home. The three sites that print in `main`
(`check_footprints.py:562`, `check_bom.py:166`, `check_all.py:532`) name their code in `main` only, as W6-F2's four.
`skipped` (`check_all.py:88`) is a status, not a refusal, and gets no code. No code reaches a JSON in this PR: a `reason`
stays the same string, so `json.md` gains nothing and every table is library-only until an Operation writes codes.

`Refusal` goes to `spark/core/result.py`, the home of what an Operation returns (`Finding`, `NextStep`), not to
`codes.py`, whose docstring says it is a table. `result.py`'s docstring gains one sentence: a `Refusal` is the sentence
with its code a refusal returns before there is an `OperationResult`. Nothing deep-copies a refusal: the five
`copy.deepcopy` calls in the tree are tests on board dicts, so `Refusal` gets no `__reduce__`, and the refuter's
`TypeError` is a row.

P688 (#926): item 3 folds in here, by the PO. `read_bom` (`check_bom.py:58`) raises `PackageUnreadable` (proposed, an
`Error` with a `code`) instead of `SystemExit`, which X2 counts (`measure.py:509`). `check_bom.main` catches it, prints
its sentence and exits 2, and `TheOrder.call` (`check_all.py:271`) catches it and answers `unchecked` with its
`Refusal`, so `:95`'s `check_crashed` stays for defects only. One golden Case each, `check-bom-could-not-run-no-bom.txt`
and its `check-all` twin. Items 1 and 2 stay apart in P688, after W6-C3: they change text and a JSON shape, and a logic
PR must not be open on a file a move PR moves. This PR also extracts the six functions of 41 to 60 lines that R1 would
catch after the move (`discover` 57 and `render` 45 in `check_all.py`, `check_trace_currents` 60 and
`Board.narrowest_by_net` 49 in `check_physics.py`, `check_i2c_pullups` 58 and `compare` 43 in `compare_design.py`), one
commit each, goldens green.

Tests: in the six test files. Each site's code as a literal, `CODES` names every constant once, the tables share no
code (`TheBenchCodesTableTest`'s tuple of modules gains `check_codes`), the 17 goldens unchanged and 2 added. `check_codes` joins
`measure.LEAVES` and `planted_tree.LEAF_NAMES`. Mutation (`p<card>-check-codes.json`, est. 10 rows): three sites with one
code swapped, a `Refusal` turned back into a plain `str`, `CODES` missing a constant, a sentence changed, an exit code
changed, the loop's tuple with its codes swapped, the `Refusal` import in one firmware module broken.

Docs: `docs/guide/agents/json.md` (the six ops), `docs/guide/journey/checks.md`, `areas/checks.md` (`check_codes`, not
`codes`). Review: it holds logic. The lenses on the everyday model, the refuter on the strongest, one mutation run. Size
est.: 140 product lines, 110 test lines.

P693 claims check (2026-11-08, on main 924e48a4). Each claim was read in the code. No decision changes. These are
wrong or stale, and the build takes the corrections:

- R1 room. `check_physics.py` is 659 lines, a baseline key (`R1:scripts/check_physics.py:<module>`) that cannot rise,
  so its two extractions and the import are paid for by free lines in the same file. `check_footprints.py` is 582.
  Every `main` of the six is a key that cannot grow (`check_all` 48, `check_bom` 29, `check_footprints` 30,
  `check_physics` 32, `check_vendor_pins` 45, `compare_design` 17).
- The three `main` sites name their code in the library, not in `main`, as P684 (row 28) and P692 (row 14) did: a
  small function returns the refusal (`check_all.CheckedFolder.named`, `check_bom.order_rows`, `check_footprints.built_design`),
  so each code is testable with no `mock.patch` and no `main` grows.
- `check_vendor_pins.py:223`'s `CouldNotKeep` has three causes (`:189` no project owns the board file, `:193` the fetch,
  `:198` the write), each with its own fix, so it carries a code: `board_has_no_project`, `header_not_fetched`,
  `header_not_kept`. 16 codes, not 14.
- The `Refusal` importers after P685 are `spark/firmware/image_builder.py:26`, `spark/firmware/import_probe.py:11` and
  `spark/firmware/scenario_run.py:19`; `import_firmware.py` and `run_scenario.py` import none.
- Confirmed: the 20 sites at the stated lines (`check_physics.py:621` for `:620`), the six spans, the mutation row
  `p684-firmware-codes.json:10`, `firmware_codes.py:7`, `test_check_all.py:132`, no code shared with another table.

### W6-B3, the breadboard move (after W6-B2)

Why two move PRs, not one. Breadboard with checks is 4,909 lines in 15 modules, 284 mutation rows in 38 tables, 44
baseline keys and 86 import lines: three times W6-F3 in lines and keys, and 284 rows at 1.6 minutes is 7.6 hours of one
serial mutation run. So the move is two PRs, W6-B3 then W6-C3, each about W6-F3's size (open question 1). One move PR is
open at a time. Each is `git mv`, the page's names and the import lines, one commit per module, the goldens green after
each commit. The CLIs stay in `scripts/` as a `main`, and no module re-exports an old name. The R1 extractions are the
codes PRs', so nothing but a move is in either.

Goal: `ls scripts/breadboard*.py scripts/part_pictures.py scripts/tabbed_page.py` prints only `breadboard.py`, and
`scripts/spark/breadboard/` holds the area under the names of its page. The 7 goldens stay byte-equal.

| Old file (lines) | New file | Rows | Note |
|---|---|---|---|
| `breadboard.py` (600) | `spark/breadboard/sheet.py`, the CLI stays | 54 | `write`, `sheet` and the flow |
| `breadboard_steps.py` (211) | `spark/breadboard/wiring_steps.py` | 1 | |
| `breadboard_drawing.py` (585) | `spark/breadboard/drawing.py` | 22 | `__file__` fix |
| `breadboard_keep.py` (338) | `spark/breadboard/kept_moves.py` | 47 | |
| `breadboard_changes.py` (235) | `spark/breadboard/bench_changes.py` | 8 | |
| `breadboard_match.py` (93) | `spark/breadboard/drawing_match.py` | 8 | |
| `breadboard_catalog.py` (64) | `spark/breadboard/drawing_catalog.py` (proposed) | 2 | not on the page, which gains the row |
| `part_pictures.py` (55) | `spark/breadboard/part_pictures.py` | 1 | `__file__` fix |
| `tabbed_page.py` (143) | `spark/breadboard/tabbed_page.py` | 23 | |
| `breadboard_codes.py` | `spark/breadboard/breadboard_codes.py` | 0 | the leaf, as `firmware_codes` in W6-F3 |

`WiringStep` for `Step`, `WiringLog` for `WiringRecord` and the `Error` suffix of `NotBuilt` and `NotDrawn` (two `C1`
keys) are renames that tests assert, so they are a card, not a move. `__init__.py` holds the index docstring alone, as
W6-F3's.

The `__file__` paths that break: `breadboard_drawing.py:22`-`:23` and `part_pictures.py:17` reach `data/` by
`parent.parent`. Under `scripts/spark/breadboard/` that is `scripts/spark/`. They take `parents[3]`, as
`spark/bench/board_facts.py:20` does. `breadboard_catalog.py:10`'s `sys.path.insert` goes. The CLI keeps its one.

What the rules do at the move, checked at 46bca725. The rules are the same for W6-C3, which points here.

- R1: the limit is 40 lines under `scripts/spark/` and 60 elsewhere (`tools/measure.py:241`). The three functions of
  41 to 60 lines were extracted in W6-B2, so no new breach. The one `R1` key, `breadboard.py:main`, stays. A moved key is
  accepted with `measure.py --accept-new` (`:707`), because `--accept` refuses a new key (P679, commit 86f74c84).
- R6: 9 keys. Each docstring that has no role word gets one, and its key goes, as `ScenarioRun`'s did.
- X2: no `print` or `sys.exit` sits outside a `main` (checked with `ast`), so the moved libraries print nothing.
- T1: 2 keys (`breadboard.py:file-write`, `breadboard_changes.py:file-write`) follow their file. T2: no key names these
  files. C1 2, R2 1 and R3 2 keys follow their file. 17 keys in all.
- U1: `breadboard_codes` is in `LEAVES` and `LEAF_NAMES` since W6-B2. `MAY_READ` (`tests/test_self_confirmation.py:43`-`:91`)
  has 10 keys on the nine, and 8 take the new module name (the two `part_pictures` keys stay). `constant_reads` keys on
  the imported name, not the `as` name (`:101`), so a read through an aliased import is skipped with no error. A test
  imports a moved module as `from spark.breadboard import drawing`, never `as breadboard_drawing`. A `MAY_READ` key that
  no read matches still fails at `:120`.
- Import lines: 40 outside the nine (6 under `scripts/`: `onboard_parts.py:10`, `part_shape.py:24` and `:26`,
  `check_spine.py:64`, `:65` and `:75`, and 34 in test files) and 13 among them. `check_spine` (design) keeps importing
  `breadboard`, a downward arrow.
- The 166 rows move with `tools/mutate.py --retarget`, which rewrites a row's `file` and nothing else
  (`tools/mutate.py:272`). Two kinds of rows are then moved by hand, as W6-F3's were. 4 rows find text inside the
  `main` that stays (`p191-breadboard`, `p273-keep-moves`, `p279-drawing-check`, `p686-breadboard-net`) and go back to
  the CLI's file. 5 rows name an old module as `module.name` or `import module` in `find` or `replace`
  (`breadboard.py` 2, `check_spine.py` 2, `part_shape.py` 1) and take the new name. `--anchors` proves each `find`
  occurs once. No row is dropped. The retargeted tables run once, in parallel `--copy` shards.

Tests: the 10 test files keep their names and import from `spark.breadboard`. The import-alone test of W5-3a extends to
each moved module. `test_architecture.py` gains the closing `ls` check. The map is regenerated with
`python3 tools/map.py --write`, and `breadboard` appears on it.

Docs: 2 agent-facing pages name a breadboard path (`commands/build.md`, `docs/guide/journey/recorded-run.md`).
`areas/breadboard.md` and `developing.md` follow. History keeps the old paths.

Review: no new logic. One reviewer on the everyday model and the refuter on the strongest, the retargeted tables as the
one mutation run, a whole-branch review before the PR. Size: 2,324 lines moved, 40 import lines, 166 rows, 17 keys,
3 `__file__` fixes.

### W6-C3, the checks move (after W6-C2 and W6-B3)

Goal: `ls scripts/check_*.py scripts/compare_design.py` prints the six CLIs and `check_spine.py` only, and
`scripts/spark/checks/` holds the area under the names of its page. The 19 goldens stay byte-equal.

| Old file (lines) | New file | Rows | Note |
|---|---|---|---|
| `check_all.py` (563) | `spark/checks/check.py`, the CLI stays | 39 | `Check`, `CHECKS`, `CheckedFolder`, the five checks |
| `compare_design.py` (302) | `spark/checks/rules_check.py` | 11 | |
| `check_physics.py` (659) | `spark/checks/physics_check.py` | 30 | its `R1:<module>` key follows |
| `check_footprints.py` (582) | `spark/checks/build_check.py` | 13 | `check_physics.py:50` imports `package_of` from it |
| `check_vendor_pins.py` (293) | `spark/checks/vendor_pins_check.py` | 19 | |
| `check_bom.py` (186) | `spark/checks/order_check.py` | 6 | |
| `check_codes.py` | `spark/checks/check_codes.py` | 0 | the leaf |

The five classes of `check_all.py` keep their names (`RulesVsNetlist`, `Physics`, `Buildability`, `VendorTruth`,
`TheOrder`) and stay in `check.py`. The page's `RulesCheck` and the rest, and the `Error` suffix of `CouldNotKeep` (a
`C1` key), are renames that tests assert, so they are a card, not a move. `__init__.py` holds the index docstring alone.

The `__file__` paths that break: `check_all.py:48` and `check_physics.py:38` build `SCRIPTS` for `sys.path` only. Both
go with the library's `sys.path.insert` lines (`check_bom.py:47`, `check_footprints.py:37`, `check_vendor_pins.py:42`,
`compare_design.py:25`). Each CLI that stays keeps its one.

The rules, as in W6-B3, with these counts. R1: the six functions of 41 to 60 lines were extracted in W6-C2. Of the 10
`R1` keys, the 6 `main` keys stay, and `check_cross_pluggable_connectors`, `check_resistor_power`, `run` and `<module>`
follow their file. R6: 12 keys. T1: 2 keys (`check_vendor_pins.py:file-write` and `:subprocess`). C1 1, C3 1 and R2 1
keys follow their file. 27 keys in all. U1: `check_codes` is in `LEAVES` and `LEAF_NAMES` since W6-C2, and the 6
`MAY_READ` keys on the six (`check_physics` 3, `check_all` 2, `check_footprints` 1) all take the new module name.
Import lines: 25 outside the six (`parts.py:493`, lazy, and 24 in test files) and 8 among them, the 7 lazy ones of
`check_all.py` among those. The 8 lazy imports stay lazy: a move changes no import shape. Rows: the 118 move with
`--retarget`. 14 rows find text inside a `main` that stays (`check_vendor_pins` 5: `p179-vendor-cache`,
`p181-p179-docs`, `sprint-6-p42`. `check_all` 3: `p197-clean-check`, `p319-one-project`. `check_footprints` 3:
`p434-rule-kinds`, `sprint-6-p42`, `sprint-8-p57`. `check_physics` 2: `sprint-6-p34`, `sprint-6-p41`. `check_bom` 1:
`sprint-8-p54`, `return EXIT_PROBLEMS`, `check_bom.py:182`) and go back to the CLI's file. 4 rows name an old module in
`find` or `replace` (`check_all.py` 3, `check_physics.py` 1) and take the new name. `--anchors`, no row dropped, one
run in shards.

Tests: the 6 test files keep their names and import from `spark.checks`. The import-alone test extends to each moved
module. `checks` appears on the regenerated map.

Docs: 7 agent-facing pages name a check path (`docs/guide/how-it-works.md`, `agents/json.md`, `agents/never-assume.md`,
`journey/checks.md`, `journey/from-draft-to-order.md`, `skills/spark-review/SKILL.md`, `commands/init.md`), and 91
files in all name a path of the fifteen. `areas/checks.md` follows. History keeps the old paths.

Review: as W6-B3. Size: 2,585 lines moved, 25 import lines, 118 rows, 27 keys, 2 `SCRIPTS` lines.

### The design-with-build group (P698, at 924e48a4)

The group is 13 flat modules, 5,808 lines: the ten of `areas/design.md` and the three of `areas/build.md`. The first
paragraph's "15 modules, 6,075 lines" was not reproduced, and no file list gives it. The five CLIs are `assign_pins.py`,
`emit_board.py`, `emit_footprint.py`, `check_spine.py` and `init_project.py`. `design.py` and `needs.py` have no `main`.
605 mutation rows in 96 tables name one of the 13. 36 baseline keys do. 90 import lines outside the 13 name one (35
under `scripts/`, 26 of them lazy, and 55 in 28 test files), and 27 sit among them. 16 agent-facing pages name a path.
The 14 test files hold 10,578 lines. This is three times W6-F3 in lines and 2.3 times in rows (267), so the group gets
seven PRs, none bigger than W6-F3. Two decisions, with the reason:

- `BuildService` and the six `BuildStage`s are not in the move. They replace `check_spine.run` (189 lines,
  `check_spine.py:362`), which 126 rows guard, and the in-process `BoardEmitter` call replaces a child process
  (`:415`). Both are logic, and a move PR adds none. "No base class with one implementation" does not stop them, because
  six stages implement one Strategy. They are one card after W6-U3, with W6-D1's goldens as its net.
- The `board-list` and `audit` Operations (N19) wait too. No design Operation runs on `run_cli` today, `boards.py`
  and `parts.py` are the next group's files, and the firmware Operations waited the same way.

### W6-D1, the design-with-build golden net

Guard, do not skip. Every child has no `WOKWI_CLI_TOKEN`, the four proxies of W6-C1, and a `PATH` of the shim folder
alone. None of the five CLIs runs `wokwi-cli` or `gh`. `check_spine.run` runs `tsci` (`check_spine.py:461`, `:183`,
`:191`), the converter (`:560`) and `emit_board.py` as a child (`:415`). `init_project.main` asks the tools list
(`init_project.py:426`). With a `PATH` of the shim folder alone, a shell fake's `mkdir` and `cp` print "command not
found" and exit 0, and a `#!/usr/bin/env python3` fake exits 127 (the refuter, reproduced). So the fakes call
`/bin/mkdir` and `/bin/cp` by absolute path and run an absolute Python, as `golden_checks.GH_SHIM` does. `tools.find`
refuses `tscircuit` ("needs bun") and `circuit-to-wokwi` ("needs node") even with `kind`, `exe` and `also` set, so the
project's override sets `"needs": []` on both entries (entries merge field by field, and `meets` is kept). Three tests
prove it: `tools.find("board-engine", project).command[0]` is the fake, the same for `diagram-converter`, and a Case
whose fake `tsci` writes a marker file passes only when the marker exists. The real tools never run, because the child's
`PATH` holds no other folder, the tools list names no other command, and its `HOME` is an empty folder, so the
defaults' `~/.local/bin/wokwi-cli` (which `sim_project.find_wokwi_cli` reads with no project) is not the person's (P699).

Goal: what the five CLIs print, and what `--keep` writes, stays byte-equal through the codes and the moves. Two fakes,
no copy. The fake `tsci` is `test_check_spine.fake_tsci` (`tests/test_check_spine.py:1234`). It answers `--version`
with `0.0.0-fake` and copies a canned `circuit.json`. It moves to `tests/fakes.py` beside `FakeTscircuitExport`
(`:267`), so both files import it. The fake converter is new (proposed, `tests/fake_converter.py`): it writes a canned
`diagram.json` to its `--out`. The project's `.spark/tools.json` names it as the `diagram-converter` with `"kind":
"path"` and `"also": []`, as W6-F1's shim does. The project is `golden_checks.build_project`'s copy of
`tests/data/breadboard/button-light`, which holds a built `dist/board/circuit.json`.

Cases, est. 19, each `<op>-<status>[-<scenario>]`. `assign-pins`: `ok.json`, `ok.txt`, `problems-impossible.txt`
(`EXIT_IMPOSSIBLE`), `could-not-run-no-requirements.txt`. `emit-board`: `ok.txt` (the board file on stdout),
`could-not-run-no-footprint.txt`, `could-not-run-refused.txt`. `emit-footprint`: `ok.json`,
`could-not-run-no-footprint.txt`. `check-spine`: `ok.json`, `ok-keep.txt` (the `kept` lines), `problems-build.txt` (the
fake `tsci` with errors), `could-not-run-no-tsci.txt`, `could-not-run-requirements.txt`, `board-only.json`,
`ok-reference.json` (no argument, the reference design, `check_spine.py:373`). With no argument,
`converter_stage_problem` reads the plugin folder, where the project's override does not apply, so this Case also writes
the override into the child store's `tools.json` (the refuter proved the converter then resolves to the fake).
`init-project`: `ok.txt`, `nothing-to-do.txt` (`EXIT_NOTHING_TO_DO`), `could-not-run-no-board.txt`. The PR probes each
and reports the real count. A Case that reaches the `simulation` stage holds the fake converter's diagram.

Files: `tests/golden_design.py` (proposed, the helper, named after the group's first area, and it holds both areas'
Cases), `tests/test_golden_design.py`, the goldens in `tests/golden-design/`, `tests/mutations/p<card>-design-net.json`.
Reuse: `golden_firmware.Case`, `plant`, `run_script(env=...)`, `golden_checks.child_env`, `build_project`, and
`golden_bench.scrub`, `replacements_of`, `op_of`, `check_golden`. The scrub adds a pattern only if a probe shows a date
or a hash. The `kept` lines name files under `<project-dir>`, scrubbed. `SPARK_ACCEPT=<op>` writes that op's goldens.

Mutation (est. 7 rows): the scrub skipped, an exit code wrong, the proxies not set, the `PATH` with another folder, the
fake `tsci` answers `--version` wrong, the written files not appended, the fake converter writes no diagram. Proven
with `--anchors`, run with `--copy`. Review: no product logic. One reviewer on the everyday model and the refuter on the
strongest. Size est.: 130 helper lines, 120 test lines, 30 lines of the fake converter, 19 goldens. Tests only, so it
can open while a move PR is open.

P699 claims check (at b716bd87). Each cited line holds: `check_spine.py:183`, `:191`, `:461` (tsci), `:415` (the
`emit_board.py` child), `:560` (the converter), `:373` and `:582` (`SCRIPTS.parent`), `converter_stage_problem`
(`:230`), `fake_tsci` (`test_check_spine.py:1234`), `FakeTscircuitExport` (`fakes.py:267`), and the merge field by
field (`tools.py:80`). `tools.find` refuses both fakes without `"needs": []` and finds them with it (reproduced). Two
corrections: `init_project.py:426` reads the tools list (`tools.merged`) and finds no tool, and `--keep` runs the fake
`tsci` a third time, as `tsci export` for the page (`tabbed_page.py:46`). So the lifted fake answers `--version` and
`build` alone, and refuses any other command. The build made `ok-reference.json` into
`check-spine-could-not-run-reference.json`: a passed build stages the reference design's two chips, and a chip's binary
older than its source runs `wokwi-cli chip compile`. So that Case writes no store override, and the converter, read
from the plugin's folder, is refused before any chip (`docs/observations/rows/p699-design-net.md`, row 6). The PR's
refuter (#957) added a Case for each refusal W6-D2 moves that a CLI reaches, 38 in all, and an empty `HOME` for
every child (rows 17 to 21).

### W6-D2, the design codes (after W6-D1 and P693)

Goal: each refusal of the four design CLIs and of `design.load` has a code. Text and exit codes stay byte-equal.

Files: `scripts/design_codes.py` (proposed, a leaf, as `firmware_codes`. C1 refuses `codes.py`). The sites, read at
924e48a4: `DesignError` at 30 `raise` sites (`design.py:118` to `:447`), `Impossible` at 11 (`assign_pins.py:193` to
`:476`), `RefusedInput` at 2 (`emit_board.py:1093`, `:1096`), `emit_board.main`'s 6 returns (`:1115` to `:1177`),
`emit_footprint.main`'s 3 (`:315`, `:319`, `:323`). One code per refusal an agent acts on differently (P684, P692 row 13),
so the 30 `DesignError` sites share about 8 codes. Est. 24 codes. The PR reports the real count. How a code travels:
`DesignError`, `Impossible` and `RefusedInput` gain a `code` attribute, as `NotBuilt` did. `why_no_footprint`
(`emit_footprint.py:151`) returns a `Refusal` from `spark/core/result.py` (its home once P693 merges, so W6-D2 waits for it). Each `main` is an R1
key that cannot grow (P684 row 28). So `emit_board.main`'s 6 refusals move into one library function. It returns the
refusal with its code, as `check_footprints.built_design` did (P693 row 5). `emit_board.py` (1,208) and `needs.py`
(831) are over R1's 600, so each line added there raises an `R1:<module>` key. The PR pays with prunes, else
`--accept-new` with the reason. `assign_pins.py` has 25 lines of room.

This PR also extracts the eight functions of 41 to 60 lines that R1 catches after the move: `design.read` 51 (`:114`),
`signals_of` 41 (`:381`), `needs.plan_pick` 57 (`:475`), `requirements` 55 (`:771`), `assign_pins.onboard_lines` 44
(`:435`), `emit_board.rail_loads` 60 (`:512`), `header_lines` 46 (`:598`), `emit_footprint.render` 44 (`:253`). One
commit each, goldens green. `assign_pins.assign` (116) keeps its key, and the key moves with `--accept-new`.

Tests: in the four test files. Each site's code as a literal. `CODES` names every constant once. `design_codes` joins
`measure.LEAVES` (`tools/measure.py:247`), `planted_tree.LEAF_NAMES` (`tests/planted_tree.py:11`) and
`TheBenchCodesTableTest`'s tuple. Mutation (est. 9 rows): three rows with one site's code swapped (one per CLI with a leaf code), an error drops its code, a
`Refusal` back to a plain `str`, `CODES` missing a constant, a sentence changed, an exit code changed, the library
function lets a refusal through. Docs: `areas/design.md` (the leaf's row). `json.md` gains nothing: no code reaches a
JSON. Review: logic. The lenses on the everyday model, the refuter on the strongest, one mutation run. Size est.: 150
product lines, 120 test lines.

### W6-U2, the build codes (after W6-D2)

Goal: each refusal of `check_spine.py` and `init_project.py` has a code. Text and JSON stay byte-equal.

Files: `scripts/build_codes.py` (proposed, a leaf). `Stage` (`check_spine.py:121`) gains an optional `code`. `report`
(`:1012`) prints `name`, `status` and `detail` only (`:1031`), so the JSON is unchanged. The sites: `run` builds 20 refusal Stages
(`:379` to `:543`), `convert` 2 (`:566`, `:568`), `converter_stage_problem` 1 (`:233`), `main` 3 (`:718`, `:745`,
`:750`), `board_alone` 1, `init_project.main` 4 (`:423`, `:428`, `:486`, `:515`). Est. 14 codes, the page's
`tool_cannot_build` among them.
`init_project.main` (112 lines) is an R1 key, so its codes come from one small library function. `check_spine.py`
(1,048) is over 600, paid as in W6-D2. This PR extracts `check_spine.islands_in` 56 (`:285`). `rules_for` (70) and
`run` (189) keep their keys.

Two small prunes from P691 and P694's review: `check_spine.py:843` and `keep_pins` (`:962`) spell out the refusal
tuple by hand. `:843` becomes `sheet.REFUSALS + (ValueError,)` (`spark/breadboard/sheet.py` after P694, today
`breadboard.py:114`), and `:962` names its own tuple once. The "not written" entry gains a `code` from
`sheet.refusal_code` (today `:117`). That `kept` entry is in the JSON, so the key is agent-visible: one golden is
accepted again, read by eye, and `docs/guide/agents/json.md` says `kept[].code` is new and what it holds. P691 (#933) keeps
the 12 `NotDrawn` sites of `drawing.py` and the one of `part_shape.py`, and loses its `:843` sentence.

Tests, mutation (est. 7 rows: two codes swapped, `Stage` drops its code, `CODES` missing a constant, the `kept` entry's
code dropped, an exit code changed, a sentence changed) and review as W6-D2. Size est.: 90 product lines, 80 test lines.

### The four moves, W6-D3a, W6-D3b, W6-D3c and W6-U3 (what they share)

Why four. 5,808 lines and 605 rows at 1.6 minutes is 16 hours of one serial mutation run. Four PRs keep each under
W6-F3 (1,900 lines, 267 rows). The order is bottom-up along the imports among the 13, so no moved module imports a flat
one for long. One move PR is open at a time. Each PR is `git mv`, the page's names, the import lines and the rows, one
commit per module, goldens green after each commit. The CLIs stay in `scripts/` as a `main`, and no module re-exports
an old name. Each PR extends `TheDesignAreaTest` or `TheBuildAreaTest` (proposed), the shape of `TheFirmwareAreaTest`
(`tests/test_architecture.py:312`) with its `CLIS` dict, and the import-alone test (`each_module_imports_alone`,
`test_architecture.py:301`). The map is regenerated. History keeps the old paths.

| PR | Old file (lines) | New file | Rows | Keys | Note |
|---|---|---|---|---|---|
| D3a | `fab.py` (134), `copper.py` (122) | `spark/design/fab.py`, `copper.py` | 21, 2 | 0 | `fab.py:30` `__file__` to `parents[3]` |
| D3a | `design.py` (450) | `spark/design/loader.py` | 53 | 1 | no CLI, `design.py:38` goes |
| D3a | `restricted_pins.py` (81), `netlist.py` (138) | `spark/design/restricted_pins.py`, `netlist.py` | 0, 6 | 2 | |
| D3a | `assign_pins.py` (575) | `spark/design/pin_assigner.py`, the CLI stays | 39 | 8 | `R1:assign` moves, `main` keys stay |
| D3b | `emit_footprint.py` (344) | `spark/design/footprint_emitter.py`, the CLI stays | 19 | 2 | `_report` prints (`:337`), so it stays with `main` |
| D3b | `emit_board.py` (1,208) | `spark/design/board_emitter.py`, the CLI stays | 67 | 6 | `R1:<module>` moves with `--accept-new`, named in the PR body for the PO (`measure.py:705`, P441 row 4), its value does not rise |
| D3b | `part_shape.py` (232) | `spark/breadboard/part_shape.py` | 24 | 0 | the edge fix below |
| D3b | `design_codes.py` | `spark/design/design_codes.py` | 0 | 0 | the leaf |
| D3c | `needs.py` (831) | `spark/design/needs.py` | 221 | 2 | `parts.py` keeps its 7 lazy imports |
| U3 | `check_spine.py` (1,048) | `spark/build/build_service.py`, `stages.py`, `board_engine.py`, `kept_files.py` (proposed), the CLI stays | 126 | 11 | the split, one commit before the `git mv` |
| U3 | `init_project.py` (522) | `spark/build/project_setup.py`, the CLI stays | 27 | 4 | |
| U3 | `ai_files.py` (123) | `spark/build/ai_files.py` | 0 | 1 | `ai_files.py:25` to `parents[3]` |
| U3 | `build_codes.py` | `spark/build/build_codes.py` | 0 | 0 | the leaf |

Shared rules, checked at 924e48a4, with each PR's share below. R1: the nine extractions are the codes PRs', so no new
breach. The five `main` keys stay, and a moved key moves with `--accept-new`. R6: each docstring gets its role word and
its key goes. X2: `emit_footprint._report` and `check_spine.report` print, and both stay in their CLI. No other `print`
or `sys.exit` sits outside a `main` (checked with `ast`). T1: the two `file-write` keys in a `main` (`assign_pins.py:550`,
`emit_footprint.py:327`) stay, the rest follow their code. C3 keys sit in a `main` and stay. U1: the two leaves are in
`LEAVES` since the codes PRs. `MAY_READ` (`tests/test_self_confirmation.py:50` to `:80`) has 21 keys on the 13, and 15
take the new module name (`emit_footprint.*` becomes `footprint_emitter.*`, `check_spine.CONVERTER_PATHS` becomes
`board_engine.*`, and the `copper`, `fab`, `netlist`, `ai_files` and `check_spine.REFERENCE` keys keep their stem).
Import lines: 90 outside and 27 among. The 26 lazy ones (12 in `scripts/`, 14 in tests) stay lazy. `sim_project.py:20`
(firmware) and `board_envelope.py:17` (bench) read design along their arrows. Rows: `--retarget` for each file that
moves whole. The rows of a CLI's `main` go back to the CLI's file by a scratch script, as P685 row 11 did. `--anchors`
proves each `find` occurs once. No row is dropped. Each PR's retargeted tables run once, in parallel `--copy` shards.
Review of each: no new logic. One reviewer on the everyday model and the refuter on the strongest, the retargeted
tables as the one mutation run, a whole-branch review before the PR.

Cards filed with this plan, under #94: the seven PRs, then `BuildService` with the in-process `BoardEmitter` call,
the N19 Operations, the `emit_board.py` split (1,208 lines, one module over R1's 600), and the renames.
Renames the pages ask for are a card, not a move: `ImpossibleError` for `Impossible`, `PinAssigner`, `PinMap`,
`BoardEmitter`, `NeedsService`, `BuildInputs`, `ProjectSetupService`, `TscircuitEngine`, `DiagramConverter`. Tests
assert the old names. `__init__.py` holds the index docstring alone, in `design` and in `build`.

### W6-D3a, the design values (after W6-U2)

Files: the six D3a rows of the table, 1,500 lines, into `scripts/spark/design/` with its `__init__.py`. `__file__`:
`fab.py:30` takes `parents[3]`, and the `SCRIPTS` lines of `design.py:38` and `assign_pins.py:41` go from the library.
Keys: 11 (`C1` and `R6` `Impossible`, `C3:EXIT_IMPOSSIBLE`, `R1:assign`, two `R1`/`R2` `main` keys, `R2` `onboard_lines`,
`rails_requested`, `Netlist.__init__`, `R6:Netlist`, `T1:file-write`). The `main`, `C3` and `T1` keys stay. Tests: 16
test files, 24 import lines, and 28 in `scripts/`. Rows: 121. Docs: 9 agent-facing pages and `areas/design.md`. Size:
1,500 lines, 52 import lines, 121 rows, 11 keys. Done when `ls scripts/*.py` shows `assign_pins.py` alone of the six.

### W6-D3b, the emitters (after W6-D3a and W6-B3)

Files: the four D3b rows, 1,784 lines. The `SCRIPTS` lines of `emit_board.py:36`, `emit_footprint.py:45` and
`part_shape.py:22` go from the libraries. Done-item 1, the edge fix. `part_shape.py` imports `breadboard_drawing` for
`NotDrawn`, three codes and `WOKWI_GEOMETRY_FILE` (`part_shape.py:24`, `:26`), and `breadboard_catalog.py:15` imports it
back. Under design that is an upward edge and a U1 cycle (P694's review). It moves to `spark/breadboard/` instead: its
job is a part's pixel shape in the Wokwi drawing, and its one design import, `emit_footprint` (`:25`), is a downward
arrow. So this PR waits for W6-B3 (P694), which makes the folder. The appendix row is corrected (`refactor-plan.md:639`),
`areas/breadboard.md` gains the row, and W6-B2's section says it is breadboard's. `part_shape.py` has six `NotDrawn`
sites (`:110` returns one, five raise), and only `:226` has no code (P691). Done-item 2: `R1:scripts/emit_board.py:<module>`
moves with `--accept-new` (`measure.py:705`, P441 row 4), named in the PR body for the PO, and its value does not rise.
Keys: 8 (`C1` and `R6` `RefusedInput`, `R1:<module>`, two `R1` `main` keys, `R2:host_part_lines`, `R3:emit`,
`R3:power_trace`, `T1:file-write` of `emit_footprint`). Tests: 9 test files, 11 import lines, and 18 in `scripts/`.
Rows: 110. Docs: 7 agent-facing pages, `areas/design.md`, `areas/breadboard.md`. Size: 1,784 lines, 29 import lines,
110 rows, 8 keys. Done when `ls scripts/*.py` shows `emit_board.py` and `emit_footprint.py` of the three, and
`part_shape.py` is under `spark/breadboard/`.

### W6-D3c, the needs (after W6-D3b)

Files: `needs.py` alone, 831 lines, to `spark/design/needs.py`. It has no `main` and no `__file__`. Keys: 2
(`R1:<module>`, with `--accept-new` as D3b's, and `R3:candidates`). Tests: 2 test files, 2 import lines, and 9 in
`scripts/` (`parts.py`'s 7 lazy ones stay lazy, `check_spine.py:69`, `spark/idea/drop_need.py:8`). Rows: 221, the
group's biggest run, in shards. Docs: 2 agent-facing pages and `areas/design.md`. Size: 831 lines, 11 import lines,
221 rows, 2 keys. Done when `ls scripts/*.py` shows no design library module and `TheDesignAreaTest` passes whole.

### W6-U3, the build move (after W6-D3c)

Files: the four U3 rows, 1,693 lines, into `scripts/spark/build/`. `ai_files.py:25` takes `parents[3]`, and the
`SCRIPTS` lines of `init_project.py:35` and `check_spine.py:58` go from the libraries. Done-item 1, the `check_spine.py`
split, as W6-F3's, its own commit before the `git mv`, with the page's names. `stages.py` holds `Stage` (`:121`) and
`NO_FOOTPRINT_HINT`, a small module the other two import, so `convert` (`:566`, `:568`) and `converter_stage_problem`
(`:233`) make no cycle. The name clashes (P694's lesson): `stages` is a local in `run` (`:372`) and `main` (`:743`), a
parameter of 7 functions, and `stages =` 46 times in `test_check_spine.py`. The module keeps the page's name, and every
importer imports by name, `from spark.build.stages import Stage, NO_FOOTPRINT_HINT`, never the module. `REFERENCE`
(`:86`) is read by `main` alone (`:716`), so it stays in the CLI and keeps its `MAY_READ` key. `CONVERTER_PATHS` goes to
`board_engine`. `board_engine.py` holds the tool adapters: `find_toolchain`, `modules_for`, `toolchain_can_build`,
`tsci_version`, `find_converter`, `converter_command`, `converter_stage_problem`, `simulation_could_not_look` (`:246`,
called by `convert` alone), `convert` and their constants (`:131` to `:250`, `:553`). `kept_files.py` holds the files
`--keep` writes into DIR and what an earlier build left there: `kept_into` to `keep_simulation` (`:769` to `:1010`),
`left_off` and `design_handed_to`. One meaning of `kept_`: the noun after it is what a run keeps between runs, as
`kept_moves.py`'s moves. `build_service.py` holds `run` as a function, `said_of_a_crash` (`:113`, which `run` calls at
`:412`, `:445`), `islands_in`, `board_alone`, `verdict` and the stage sentences. Its docstring says `BuildService` comes
into this file with its card, so no later rename. The CLI keeps `main`, `report`, `render` and `timed_out_sentence`,
because `report` prints (`:1037`, `:1041`). No module is then over 600, so `R1:scripts/check_spine.py:<module>` goes.

Done-item 2, the `__file__` paths. `SCRIPTS.parent` (`:373`, `:582`) is the plugin folder, and under
`scripts/spark/build/` it is `scripts/spark`: both read `boards.PLUGIN_ROOT` (`boards.py:171`). The `emit_board.py`
child (`:416`) gets an `EMIT_BOARD_SCRIPT` with `parents[2]`, as `image_builder.FLASH_IMAGE_SCRIPT` does (P685 row 5),
with a test. It is the one logic-adjacent change of the move. `find_converter`'s `scripts/check_spine.py` test (`:214`)
holds, because the CLI stays. Done-item 3, the patches: the 20 `mock.patch.object(check_spine, ...)` sites in
`test_check_spine.py`, `test_json_contracts.py` and `test_routes.py` (`find_toolchain` 9, `run` 8, `islands_in`,
`converter_command` and `_kept` 1 each) follow their function to the module that looks the name up. A missed
`find_toolchain` patch lets the tests at `test_check_spine.py:1807` and `:2004` find a real `tsci` on `PATH`. The proof
is P685 row 9's: plant an early binding (`from ... import find_toolchain`) in a scratch copy and see those tests go red.

Keys: 15 (`C3:EXIT_NOTHING_TO_DO`, `R1` `<module>`, `main` and `run` of `check_spine`, `R1` `main` and `rules_for` of
`init_project`, `R3:run`, `R3:write`, `R6` `AiFiles` and `Stage`, `T1` `file-write`, `os.environ` and `subprocess` of
`check_spine`, `T1:file-write` of `init_project`). The three `main` keys and the `C3` key stay. Tests: 14 test files, 18
import lines, none in `scripts/`. Rows: 153. Docs: 14 agent-facing pages, `areas/build.md`, `developing.md`. Size:
1,693 lines, 18 import lines, 153 rows, 15 keys. Done when `ls scripts/*.py` shows `check_spine.py` and
`init_project.py` of the three, `scripts/spark/build/__init__.py` imports nothing, and `TheBuildAreaTest` passes.

## Design and build after W6-U3 (the moved modules and their classes)

```mermaid
classDiagram
  class Design { <<Value>> }
  class DesignError { <<Error>> code }
  class RestrictedPins { <<Value>> }
  class Netlist { <<Value>> }
  class Impossible { <<Error>> code }
  class BoardInputs { <<Value>> }
  class RefusedInput { <<Error>> stage code }
  class design_codes { <<leaf>> CODES }
  class Stage { <<Value>> name status detail code }
  class AiFiles { <<Value>> }
  class build_codes { <<leaf>> CODES }
  class Refusal { <<Value>> code }
  class footprint_emitter { <<module>> why_no_footprint() }
  DesignError ..> design_codes
  Impossible ..> design_codes
  RefusedInput ..> design_codes
  BoardInputs ..> Design
  Stage ..> build_codes
  footprint_emitter ..> Refusal
```

`Design` and `DesignError` (`loader.py`), `RestrictedPins`, `Netlist`, `Impossible` (`pin_assigner.py`), `BoardInputs`
and `RefusedInput` (`board_emitter.py`), `Stage` (`stages.py`) and `AiFiles` exist today. `pin_assigner.py`,
`board_emitter.py`, `footprint_emitter.py`, `needs.py`, `board_engine.py`, `kept_files.py` and `project_setup.py` hold
functions, and the page's Services wait for their cards.

## Breadboard and checks after W6-B3 and W6-C3 (the moved modules and their classes)

```mermaid
classDiagram
  class BreadboardSteps { <<Service>> }
  class BreadboardPlanner { <<Service>> plan() }
  class PartPlacement { <<Strategy>> }
  class NotDrawn { <<Error>> code subject }
  class NotBuilt { <<Error>> code }
  class NotKeptResult { <<Result>> code }
  class TabbedHtmlPage { <<Renderer>> }
  class breadboard_codes { <<leaf>> CODES }
  BreadboardPlanner --> PartPlacement
  BreadboardPlanner ..> NotDrawn
  NotBuilt ..> breadboard_codes
  class Check { <<Strategy>> run() }
  class CheckedFolder { <<Value>> }
  class CouldNotKeep { <<Error>> }
  class check_codes { <<leaf>> CODES }
  class Refusal { <<Value>> code }
  Check <|-- RulesVsNetlist
  Check <|-- Physics
  Check <|-- Buildability
  Check <|-- VendorTruth
  Check <|-- TheOrder
  Check ..> CheckedFolder
  Check ..> Refusal
  Check ..> check_codes
```

`BreadboardSteps` (`wiring_steps.py`), `BreadboardPlanner`, `PartPlacement` and `NotDrawn` (`drawing.py`), `NotBuilt`
(`sheet.py`), `NotKeptResult` (`kept_moves.py`), `TabbedHtmlPage` (`tabbed_page.py`), `Check`, `CheckedFolder` and the
five checks (`check.py`) and `CouldNotKeep` (`vendor_pins_check.py`) exist today. `Refusal` (`spark/core/result.py`) is the core's after W6-C2, and a check builds it as `Refusal(text, code)` with a code of `check_codes`.
`CheckService` and the page's five `*Check` names wait for the Operation card.

## The later groups

Each group follows the same three PRs. The order is the plan's. Open question 1 says which moves share a PR.

**Breadboard**: W6-B1 above (merged), then W6-B2 and W6-B3 above.

**Checks**: W6-C1 above (merged), then W6-C2 and W6-C3 above.

**Design with build**: W6-D1, W6-D2, W6-U2, W6-D3a, W6-D3b, W6-D3c and W6-U3 above (P698).

**Records with sourcing** (13 modules and 5,949 lines by the first count, not checked since). The move brings P391's
stage 2 classes, `Brief`, `ToolFinder`, the two bench leaves and the `parts.py` split by job group. Done when:
`ls scripts/*.py` prints only the CLIs, each a `main` that parses and prints. `tests/test_architecture.py` holds one
area test per area, as `TheFirmwareAreaTest` does. No lazy import under `scripts/spark/` points up an arrow, and
`parts.py` imports its Operation modules at the top. What must be refined first, when it is next: the count at that
day's main, the job groups of `parts.py` (2,384 lines at 924e48a4), and the name of each split module against
`areas/records.md` and `areas/sourcing.md`. Also where `boards.footprint_stop` goes (`boards.py:248`, with a lazy
`emit_footprint` import at `:255`, an upward edge), and how many move PRs, by the rule above.

## Firmware after W6-F3 (partial: the moved modules and their classes)

```mermaid
classDiagram
  class ScenarioRun { <<Service>> problem() run(simulator) write_log(sentence, output) }
  class ScenarioSteps { <<Value>> counts state why names }
  class ProjectImage { <<Value>> sha256() read_run_logs() why_untested() find_passed_log() }
  class DeployError { <<Error>> reason }
  class SimulationLimits { <<Value>> }
  ScenarioRun ..> ScenarioSteps
  ScenarioRun ..> SimulationLimits
  ProjectImage ..> ScenarioSteps
  ProjectImage ..> DeployError
  class firmware_codes { <<leaf>> CODES }
  DeployError ..> firmware_codes
```

`ScenarioRun` (`scenario_run.py`), `ScenarioSteps` (`scenario_steps.py`), `ProjectImage` and `DeployError`
(`project_image.py`) and `SimulationLimits` (`sim_project.py`) exist today. `image_builder.py` and
`import_probe.py` hold functions, not classes, and stay so until a second platform asks for `FlashImageBuilder`. The
bench reaches `scenario_steps` and `project_image` along its arrow, and nothing in firmware imports the bench.

## The checks that close the firmware group

1. `tests/golden/` holds the firmware goldens, and the three CLIs print byte-equal text through W6-F2 and W6-F3.
2. Every refusal of the three CLIs has a code that `firmware_codes.CODES` names (W6-F2, tests).
3. `ls scripts/*.py` names no firmware library module, and `scripts/spark/firmware/__init__.py` imports nothing
   (W6-F3, a test).
4. Each moved module imports alone in a child Python (W6-F3, a test).
5. The baseline has no key with an old firmware path, and the `R6` key is gone. No row is dropped (W6-F3).
6. `tests/test_map.py` passes on the committed `docs/guide/map.md` with a `firmware` section (W6-F3).

## Risks

1. A golden child runs the real `wokwi-cli` with the real token and spends a paid minute. The real CLI is on the
   PO's PATH, his shell exports `WOKWI_CLI_TOKEN`, and `child_env` passes it on. W6-F1 sets a fake token in every
   child, sets `"also": []`, and a test asserts the shim is the command found. The shim refuses any other token. No
   mutation row unsets the shim.
2. #906 merges late. W6-F2 and W6-F3 wait, and W6-F1 does not. Breadboard's net can start.
3. The split of `run_scenario.py` moves functions to two files, so `--retarget` cannot move all 69 rows. The rest are
   retargeted by hand, and `--anchors` catches a miss before the run.
4. A `wokwi-cli` shim on the tools list is new ground for the goldens. If `tools.find` refuses an absolute `exe`, the
   shim goes on the child's `PATH` instead.
5. `board_codes` keeps four aliases for one PR. A test pins that each equals its `firmware_codes` twin until W6-F3
   removes them.

## Review size

- W6-F1: about 120 test lines and 8 goldens, no product logic. One reviewer on the everyday model, the refuter on the
  strongest, one mutation run of est. 4 rows.
- W6-F2: about 80 product lines and 80 test lines. It holds logic: the lenses on the everyday model, the refuter on
  the strongest, one mutation run of est. 8 rows.
- W6-F3: 1,656 lines moved, 52 import lines, 228 rows, 15 keys, no new logic. One reviewer on the everyday model, the
  refuter on the strongest, the retargeted tables as the one mutation run, and a whole-branch review before the PR.
- W6-B2: about 80 product lines and 60 test lines, 5 codes, 3 extracted functions. It holds logic: one reviewer and the refuter on the
  strongest, one mutation run of est. 6 rows.
- W6-C2: about 140 product lines and 110 test lines, 14 codes, `Refusal` to the core, 6 extracted functions, P688's item 3. It holds logic: the lenses on the
  everyday model, the refuter on the strongest, one mutation run of est. 10 rows.
- W6-B3: 2,324 lines moved, 40 import lines, 166 rows, 17 keys. W6-C3: 2,585 lines moved, 25 import lines, 118 rows,
  27 keys. No new logic. Each as W6-F3 is reviewed.
