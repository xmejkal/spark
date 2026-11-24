# P1069: a deploy writes page.html again at every status but a crash: rows

Card: [P1069 #1567](https://github.com/xmejkal/spark/issues/1567), story 0c of P793. New logic: a plan council of two
rounds (one lens on Sonnet, the refuter on Opus) and the build's own checks of the plan. This file holds the acted and
raised findings only. 2026-11-24.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | B1: a flash that fails after the erase is could-not-run with no `crash` code and writes no board log, so the page and `show` must agree | plan council, round 1 | acted | `test_deploy_json.DeployPageTest.test_a_write_that_fails_after_the_erase_writes_the_page_that_show_agrees_with`; the flow does not yet read a deploy that stopped after the erase, a card the coordinator asks spark-main for |
| 2 | B2: D1 has a cost: a refused look, a `needs_reply`, a closed gate and a "no" all write the page again and add the note | plan council, round 1 | acted | named in the PR body and in the docstring of `DeployPageTest` |
| 3 | B3: row 1 lives in one table only | plan council, round 1 | acted | `p1035-page-write.json` row 3 rewritten in place; the test name in row 4 updated |
| 4 | B4: test 5 asserts no step and no `steps` call, and row 3 names `test_a_run_that_is_not_ok_gets_no_follow_up` | plan council, round 1 | acted | `test_a_run_that_is_not_ok_and_writes_is_refreshed_with_no_steps`; `p1069-deploy-page.json` row 2 |
| 5 | B5, B9: the refused pick writes the page, and a failed `--keep` that kept nothing writes it too, with the fixture of `none.json` | plan council, rounds 1 and 2 | acted | `test_a_dry_run_leaves_the_page_and_a_refused_pick_writes_it_again`, `test_a_kept_build_that_failed_before_it_kept_anything_writes_the_page_again` |
| 6 | The plan's failed-keep test reads the page note from `check_spine.py --json`, but the build's `--json` is a flat line that holds no notes | the build, checking the plan | acted | the test reads the refresh's line in the text run and the page's bytes in both runs |
| 7 | B6, B10, B12: the deploy tests in their own class with the page fixture in its `setUp`; the crash is `fails=1` with a RuntimeError; the failed write uses `write_fails=True` | plan council, rounds 1 and 2 | acted | `test_deploy_json.DeployPageTest` |
| 8 | B7, B11: the stale text of `_followed`, `TheFollowUpTest`, `flow.py --help` and the module docstring of `now_follow_up` | plan council, rounds 1 and 2 | acted | each replaced in place; the `--help` of `deploy.py` says nothing of the page |
| 9 | Test 8, the refusal of P1060 PR B, waits for that PR | plan council, D5 | raised | pending on P1060 PR B, named in the PR body |
