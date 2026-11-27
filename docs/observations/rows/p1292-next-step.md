# P1292: the build's next step agrees with show's NOW, and show's NOW line comes for check_spine only: rows

Card: [P1292 #1859](https://github.com/xmejkal/spark/issues/1859), split from P1286 #1852 (its O1). The plan was
checked by the architecture lens (Opus) and the refuter (Opus); the delegated council (the tech lead, the architect and
the PO assistant, all on Opus) answered its open choices and gave the build fixes. Rows 1 to 16 are the plan check's,
rows 17 to 28 the delegated council's, and rows 29 on the build's. This file holds the acted, raised and rejected
findings only. 2026-11-27.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | the core held a flow word (`now_line`) and a flow rule (`not added`) | plan lens (L1), refuter (fix 3) | acted | the core's hook is the neutral `FollowUp.closing_line(project)`, None in the base; `FlowFollowUp` decides with `says_now` and show's own steps |
| 2 | the filtered case: when show names the build again, `runs_again` drops it, and a NOW line after it would say "build the board again" | plan lens (L2), refuter (fix 4) | acted | the rule reads show's steps before `runs_again`: show named a step, so no line comes; `test_a_kept_build_whose_flow_names_the_build_again_ends_with_no_step_and_no_line` |
| 3 | `--json` and a later MCP get no line | plan lens (L3), refuter (fix 5) | acted | json.md's `next` line says that an empty `next` means: read `data.guide.now` from `flow.py show --json` |
| 4 | put show's now as a note in the build's envelope | plan lens (L3, "better") | rejected | the flat line carries no notes (json.md's `next` line); the build's `--json` carrying show's now is raised as P1317 (row 26) |
| 5 | the flow was read twice, against P1256's S3 "the flow reads itself once" | plan lens (L4), refuter (fix 2) | acted | `FlowFollowUp.steps` keeps its reading and `closing_line` takes it; `test_the_closing_line_reads_the_flow_of_its_steps_and_nothing_more` |
| 6 | the refresh reads the flow a third time after a build with a requirements file | plan lens (L4) | rejected | the refuter: a build with a requirements file keeps its own page, so the refresh writes nothing (`kept_its_page`) |
| 7 | a kept build that leaves nothing open ends with no line, while show prints its no-open line | plan lens (L5) | raised | P1315 [#1892](https://github.com/xmejkal/spark/issues/1892); it also re-anchors `p1142-first-line.json:8` |
| 8 | no test killed row 5 (the closing line before the step lines) | plan lens (L6) | acted | with the neutral core a fake gives a step and a closing line: `test_a_closing_line_comes_after_the_step_lines` kills the row |
| 9 | R3 counts parameters without self | plan lens (L7) | acted | `FlowFollowUp.__init__` takes three (`renderer`, `store`, `says_now`) |
| 10 | `p1035-follow-up.json:20` finds `FlowFollowUp()` in check_spine.py | refuter (fix 1) | acted | re-anchored on `FlowFollowUp(says_now=True)`; rows 15 and 16 name tests that kill them, checked by hand |
| 11 | why P945's research step stays beside "the one next step" | refuter (fix 6) | acted | show names no `research` step; the build alone knows it from its kept entries; the card's first Done-when line names it |
| 12 | steps that raise and then a closing line give two lines | refuter (fix 7) | acted | the core asks no closing line after steps that raised; `test_steps_that_raise_give_one_diagnostics_line_and_no_closing_line` |
| 13 | `said_of`'s docstring still says "The next steps (P517)" | refuter (fix 8) | acted | it names the research steps (P945) and show's steps (P1035, P1292) |
| 14 | P1256's S3 put the rule after `runs_again` | refuter | acted | the rule moved before it, for row 2's reason, said in the plan's core fit |
| 15 | commands/build.md must say that a build without `--keep` names no step | plan check (O2) | acted | commands/build.md says so |
| 16 | the `--json` help's cite was build_board.py:132-134 | plan check | acted | the help at :131-133 says the new `next` |
| 17 | `closing_line` should take the reading, so a second call gives None | delegated council, the architect (F1) | acted | `reading, self.reading = self.reading, None`; `test_the_closing_line_takes_the_reading` and its mutation row |
| 18 | "one instance per run" belongs in the `FollowUp` class docstring and in patterns-and-names.md | delegated council, the architect (F2) | acted | both say it, the docs inside the existing line |
| 19 | the hook's docstring must say "after the step lines and before the refresh's line"; `_followed` and the RunOptions comment too | delegated council, the architect (F3) | acted | all three say it; `test_a_closing_line_comes_before_the_refresh_s_line`; the firmware-now test's comment says why the last line is show's |
| 20 | the grep word for the research step is `research` | delegated council, the architect (F4) | acted | the plan's claim holds: no flow module names a `research` step |
| 21 | `test_flow.py:2484` belongs in the "read again" list | delegated council, the tech lead (A) | acted | `test_a_kept_rebuild_at_the_deploy_names_the_flow_s_step_after_it` stands unchanged and passes |
| 22 | `test_check_spine.py:507-509` each drop by one line | delegated council, the tech lead (B) | acted | `[PastedLine]`, `lines[-1:]`, `lines[-2]`, named old → new in step 3's commit |
| 23 | one test of a kept build with a P945 research step at a firmware NOW: the research line, then show's NOW line | delegated council, the PO assistant (F1) | acted | `test_a_kept_build_with_a_research_step_at_a_firmware_now_ends_with_it_then_show_s_now_line`, on the e-paper fixture |
| 24 | commands/build.md must tell Claude to read the NOW line to the person as the next step | delegated council, the PO assistant (F3) | acted | one sentence in commands/build.md |
| 25 | a build without `--keep` writes nothing and says nothing about it | delegated council | raised | P1316 [#1893](https://github.com/xmejkal/spark/issues/1893) |
| 26 | the build's `--json` does not carry show's NOW | delegated council | raised | P1317 [#1894](https://github.com/xmejkal/spark/issues/1894), under P793 |
| 27 | five scripts each choose their Operation's follow-up, and the page's run chooses none | delegated council | raised | P1318 [#1895](https://github.com/xmejkal/spark/issues/1895), before the MCP server |
| 28 | a kept build whose flow names only the build again ends with no step and no line | plan lens (L2), delegated council | raised | P1181 [#1725](https://github.com/xmejkal/spark/issues/1725), a now with no usable step |
| 29 | `p1035-follow-up.json:21` named a test that step 3 renamed | the build | acted | it names `test_a_kept_build_whose_flow_names_the_build_again_ends_with_no_step_and_no_line`, which kills it, checked by hand |
| 30 | `p1035-follow-up.json:9`'s anchor `return [], printable(...)` would have been in the core twice | the build | acted | `_closing_line` returns `()` on a raise, so every anchor is present once |
| 31 | the map's row of `outside.py` moved, because test_check_spine imports it now | the build | acted | `tools/map.py --write` |
| 32 | the plan's read-count and raise tests used `mock.patch.object`, which T2 refuses in a test file | the build, test_architecture | acted | the closing line still says the firmware now after the project moved on to a simulate now; `steps(None)` raises TypeError; both rows killed by hand |
| 33 | `test_json_contracts.test_check_spine_adds_missing_facts_beside_status_only_when_the_record_lacks_a_level` expects a `next` key, which held only P517's look step; there show's now is the idea with no step, so `next` is absent and the text ends with `NOW (idea): ...` | the build, test_json_contracts | raised | for spark-main before the merge: the plan does not name this test, so the builder left it red and unchanged; the plan's contract change says the key goes |
