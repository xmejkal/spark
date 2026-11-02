# P507 event seam E1: rows

What the plan check, the plan council (one round: lenses 1 to 7 and the refuter) and the build of E1 found. Card: #702.
The plan: `event-seam-plan.md`, section 2, row E1. Each claim was checked at c3b04016 or on this branch.

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | The Strategy row and "The core contract" are not in `developing.md` (the design said `:302`) | plan check | acted | they live in `docs/guide/patterns-and-names.md` (`:16`, `:56`). The PR edits that page |
| 2 | p442's row "the builder is asked without the effects" goes stale too, beside "a stub answers instead of refusing" | plan check, lens 1 | acted | both retargeted in `tests/mutations/p442-core-look.json`. `--anchors` refused 121 before, 119 after, as on main |
| 3 | Name mutation rows by their `name`, never by a file line | lens 1 | acted | the plan and this PR name them |
| 4 | Put `reporter` before `find_tool=`, so p442's "the project's finder drops the project" still matches | lens 1 | acted | `bench/__init__.py`: `build_outside_world(effects, reporter, find_tool=...)` |
| 5 | Run `--anchors` after the builder change and before the PR, refused equal to main's 119 | lens 2, learned rule | acted | 119 after the builder commit and after the mutation table |
| 6 | The BEGIN comes after `evidence_for` and `MicroPythonPlatform`, before the read, on purpose | lens 3 | acted | a comment at the line in `look_at_board.py` |
| 7 | Test that a bare world from `build_outside_world` has a working `report` | lens 4 | acted | `test_core.py` `TheWorldReportsTest.test_a_bare_world_reports_to_the_reporter_it_was_built_with` |
| 8 | Under `--json`, assert stdout is exactly the envelope and a newline | lens 6 | acted | `test_with_json_the_line_is_on_stderr_and_stdout_holds_the_envelope_alone` |
| 9 | `patterns-and-names.md:69-71` names both builders without `reporter` | refuter | acted | both signatures gain `reporter` |
| 10 | The BEGIN test must not sit behind `@needs_littlefs`, or "the event not sent" escapes where littlefs is missing | refuter | acted | the test uses the setup of the test without littlefs in `test_look.py` |
| 11 | The stderr contract gets its own heading beside "A crash exits 1" | refuter | acted | `docs/guide/agents.md`, "Under --json, stderr is for a person" |
| 12 | Naming tension: `TerminalConsentStrategy` has the suffix, `TerminalReporter` does not | lens 5 | raised | the names table lets a plain noun stand when the docstring says Strategy, as `Reporter` and `BoardReader` do. Settle the rule at the names pass (P382) or with P478's second Reporter |
| 13 | "report" has three meanings: `outside.report`, the `LookReport` value, the `TextReport` output | lens 5 | acted | `glossary.md` row "report". Deploy's `report` variable becomes `look` in E2 (W4-2) |
| 14 | The pre-push hook names no failing test: the first push failed with "failures=1" and no name | build | raised | the failure was `test_orphans` (`events.py` imported by nothing until the builder commit). A hook line that names the failing test would save a suite run |
| 15 | X2's sentence and comments named only "the terminal consent" | plan check | acted | `tools/measure.py` names the terminal reporter too |
| 16 | The design budgets 10 doc lines, but `agents.md` (185) and `patterns-and-names.md` (279) sat at their budgets in `tools/check_docs.py` | build | acted | `agents.md`: the "This page is for an AI" list became one paragraph. `patterns-and-names.md`: the contract paragraph rewrapped, the `LookAtBoard` block of the class diagram cut (it repeated the code's signature; the inheritance arrow stays). A plan that adds guide lines checks the page's budget first |
| 17 | "Before the read" was untested: the BEGIN moved after `looker(...).run(...)` kept the tests green | PR refuter 5 | acted | the look test's Fake Reporter keeps what the outside had run at each event and asserts nothing ran before the BEGIN. Mutation row "the BEGIN after the read" |
| 18 | The stderr section should say stdout holds the envelope alone, give "never parse stderr" its exception, and name the scripts it holds for | PR docs lens 1-3 | acted | `agents.md`: scoped to `look.py` and `deploy.py` (`agents/json.md` says the same of deploy); stderr is read only to report a crash or an exit-1 refusal. Two lines of the Claude Code section merged to stay at the budget |
| 19 | A LINE with text None makes `TerminalReporter` raise, against "never raises" | PR code lens 2 | acted | `Event.line` refuses a text that is not a string (TypeError, a caller's defect). Test and mutation row "a LINE without a string is let through" |
| 20 | A LINE text with a newline printed an unindented second line | PR refuter 7 | acted | `TerminalReporter` indents each line. Test and mutation row "a LINE's second line without its indent" |
| 21 | test_look built the event as a literal `Event("begin", ...)` | PR code lens 4 | acted | `Event.begin(board_envelope.STAGE_LOOK)` |
| 22 | A BEGIN has no production reader yet | PR code lens 3 | rejected | on purpose: E1 is the probe, and P478's coloured terminal is its first reader. The prune sweep keeps it |
| 23 | The base `Reporter.report` leaves `event` unused | PR code lens 1 | rejected | it names the method every Reporter owes; kept as it is |
| 24 | `patterns-and-names.md:83` ran to 137 characters and did not say what an Event holds | PR nit | acted | the paragraph rewrapped near 120, and "an `Event` holds `kind`, `code` and `text`" added |
