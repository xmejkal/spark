# P479 event seam: rows

What plan council rounds 1 and 2 on the event seam plan found, and what the synthesis did. Rows 37 and up are round 2 (record: `round2.md`, same folder). Card: #657. The round 1 record is
`docs/observations/2026-11-01-p479-event-seam-council/round1.md`. The synthesis checked each claim at d375c017.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | No rule says whether a line deploy shows mid-run is a result line or an event line | architecture | acted | plan rule 1 "one line, one place", E2 tests that no event text is in the result's lines |
| 2 | The builder change is not named: `run_cli` calls `outside_builder(project, effects)` and pops `as_json` first | architecture | acted | cited lines moved to `cli.py:108-109`. Plan "Where it sits": the reporter line, three builders |
| 3 | Extract `reporter_for(as_json)` to keep `run_cli` in its R1 budget | architecture | acted | as `TerminalReporter.for_json`: a top-level function in `cli.py` that reads `sys.stdout` breaks X2 (`tools/measure.py:252`) |
| 4 | Drop `PROGRESS` and the counts until a Reporter draws them | architecture | acted | Event has `kind`, `code`, `text` |
| 5 | `ProgramRunner(echo_to)` is deploy only and belongs in E2 | architecture, tech lead | acted | `deploy_service.py:68-72`, `:120`, `deploy.py:225`. Plan "A child's output, in E2" |
| 6 | List every `show_line` hit in the plans, with a grep that finds none after E2 | architecture | acted | section 3 table and the grep line. `wave4-plan.md:191`, `:195` hold no `show_line` (the sequence gains an arrow). Added `refactor-plan.md:127-128`, `:188`, `:194`, `:201-202`, `:627`, `areas/bench.md` |
| 7 | Say that `report` takes facts, and where E1 sits in the waves | architecture | acted | "Facts only" paragraph. E1 sits in wave 4 before W4-2 |
| 8 | The goldens compare stdout only, while agents.md promises stderr text | UX | verified | `golden_bench.py:133-134` returns `done.stdout`. agents.md `:555-558`, `:627`, `:641` |
| 9 | Add a stderr byte test of `deploy --json` | UX | acted | E2's first commit: a stderr golden of the `--json` no-terminal case |
| 10 | The order of event lines and the report without `--json` is not pinned | UX | acted | plan rule 2, E1's toy test |
| 11 | Write the stderr contract now, with an agents.md sentence | UX | acted | plan rule 4, the sentence lands in E1 |
| 12 | Say that no gain shows before P478 | UX | acted | short version and decision 4 |
| 13 | Step codes become a public documented list | UX | rejected | deploy's phase codes are public already as the envelope's `stage` (`board_envelope.py:26`). P481 #660 describes them as data later |
| 14 | Reporters decide on the step, never on text | UX | acted | "A Reporter decides on `kind` and `code`, never on `text`" |
| 15 | The field `step` and the constructor `Event.step` clash | tech lead | acted | field `code`, constructors `Event.line`, `Event.begin`. "step" also names wiring steps and `ScenarioSteps` |
| 16 | A unit test reads every Event field | tech lead | acted | E1 Done when |
| 17 | Add a subprocess test on the toy for both streams in E1 | tech lead | rejected | E1 has no child and no fd write. The in-process builder test runs the real `run_cli` and `TerminalReporter`. E2's child goldens prove the fds |
| 18 | `FakeOutsideWorld` makes a `FakeReporter` by default | tech lead | acted | `fakes.py:272`, plan "The Reporter" |
| 19 | List the test builders that change | tech lead | acted | `test_core.py:187`, `:265`, and the `build_outside_world` calls at `:276`, `:286` |
| 20 | R1 and R3 of deploy drop in E2 | tech lead | acted | `tests/architecture_baseline.json`: `_deploy` R1 72 and R3 9, `DeployService.__init__` R3 7. E2 Done when |
| 21 | The names table gets rows for Event and Reporter, and the Adapter label fits badly | tech lead | acted | a `Reporter` role row. Event is a Value, no row. `TerminalReporter` is a Strategy case, not an Adapter |
| 22 | A "You decide" box with three or four yes or no questions, and the rest as council rows | PO assistant | acted | four questions under the short version. Rows 32 to 35 hold the rest |
| 23 | One line on what approving means | PO assistant | acted | "Approve this" line |
| 24 | The short version first, section 3 a table, the map an appendix, E3 and E5 short | PO assistant | acted | plan layout |
| 25 | List build, `run_scenario` and `flash_image` with the wave that moves each | PO assistant | acted | appendix, second table |
| 26 | The counts are wrong: `emit_board.py` 16, `grant.py` 8, `deploy.py` 3 calls of `print(` | refuter | acted | `/usr/bin/grep -c 'print('` at d375c017. The total 155 holds |
| 27 | A mid-run line is missed: `deploy.py:152`, the standing yes not used | refuter | acted | appendix, seven sites |
| 28 | The Event drops the two-space indent, but the terminal prints `event.text` | refuter | acted | `TerminalReporter` prints `"  " + text`. Risk 3 |
| 29 | E4 moves the build's stderr lines (`check_spine.py:1023`) to stdout | refuter | acted | plan rule 3: stderr lines stay diagnostics, no stream field |
| 30 | The deploy goldens never reach a mid-run line | refuter | acted | E2's first commit adds `deploy-could-not-run-no-terminal.txt` |
| 31 | E1's toy test cannot run: the tests pass `outside` with `outside_builder=None` | refuter | acted | `test_core.py:124-131`. The stream test goes through a builder. `p442-core-look.json:4` retargeted |
| 32 | The Event gets a time stamp | draft question | rejected | council: a Reporter stamps it from the frontend's clock |
| 33 | The Event gets a severity | draft question | rejected | council: when P478 needs a severity, it adds the field |
| 34 | A `Reporter` base with one real case | draft question | acted | council: the base now, the Fake is T3's second case |
| 35 | A `BEGIN` per build stage changes the timing | draft question | closed | council: bytes stay, the build golden compares bytes |
| 36 | Deploy's phase codes need a new list | synthesis | rejected | `board_envelope.STAGE_*` is the list, `DeployPhase` after S11 |
| 37 | Each "You decide" item is a question ending in "?", and the `LookReport` rename is not in item 1 | PO assistant, tech lead | acted | the box has four questions. The rename is a section 3 row for W4-2 |
| 38 | No `Reporter` row in developing.md's table | PO assistant, tech lead, refuter | acted | the Strategy row (`:302`) lets a plain noun stand. `tools/measure.py:35` `ROLES` stays. Section 3 and E1's Done when say so |
| 39 | "report" means three things and "line" is overloaded | PO assistant, tech lead | acted | "result lines" in rule 2. The glossary row lists the meanings and the two kinds of line |
| 40 | Split E2a (two goldens, stderr support) from E2 | PO assistant, tech lead | acted | E2a is its own small PR before W4-2 with its own Done when |
| 41 | The indent: `deploy.py:243` and `board_look.py:390` add no two spaces, yet `test_deploy_json.py:196` expects them | senior architecture | verified | read in the code. The source per site is not clear, so E2a's PR text names it, and risk 3 says so |
| 42 | One event per line | senior architecture | acted | `guard_lines` splits on newline (`text_guards.py:93`). The `text` field holds one line, and `deploy.py:243`, `:259` send one event per line |
| 43 | The world's report is the only path, test builders take the reporter | senior architecture | acted | rule 5. The plan now says "five rules" |
| 44 | Severity and phase order, `McpProgressReporter` progress and total, no stdout Reporter for MCP stdio | senior architecture | acted | one paragraph under the later Reporters. Nothing is built |
| 45 | Cite `test_core.py:276`, not `:280` | refuter | acted | plan and row 19 |
| 46 | Risk 3 claims too much: E2's goldens stop at the gate | refuter | acted | risk 3 lists the lines in no golden. E2's exact-text event test guards them |
| 47 | A Reporter role row needs `Reporter` in `ROLES` | refuter | closed | resolved by row 38: no row |
| 48 | `FakeOutsideWorld` makes its own reporter, so it needs a `reporter=` parameter. E2 breaks `test_core.py:288` and `test_deploy_json.py:455` | refuter | acted | the parameter is in "Where it sits". E2's Done when lists the tests. `assertIs` sits at `:287-288` |
| 49 | `for_json` breaks X2 because `measure.py:362` skips `TERMINAL_CLASSES` bodies | refuter | rejected | that skip is why the class is exempt: `_may_print` (`measure.py:363`) lets a `TERMINAL_CLASSES` name print. Counts and edit lists hold |
