# P1286: the page's deploy step gets one line with Copy, from the core: rows

Card: [P1286 #1852](https://github.com/xmejkal/spark/issues/1852), under P793 #1105. The plan had a plan check (a lens on
Sonnet and the refuter on Opus) and a delegated council's second round, which said BUILD after one blocker, B1. This
file holds the acted, raised and rejected findings of the plan check, the council and the build. The PR's review adds
its own rows. 2026-11-27.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | `with_command` must run in `reading_of`, so the page reads the line that show reads | council B1 | acted | `reading_of` calls `now_steps` once and `with_command`; `FlowReading` holds `steps` |
| 2 | `FlowReading`'s docstring says "It holds no path", false once it holds `steps` | council N1 | acted | the docstring says what it holds |
| 3 | the nine exact-dict asserts of `guide.now` each need the two new keys | lens L1, council O7 | acted | `command` and `no_command` on every now, null where there is no line: a contract change of `guide.now` |
| 4 | the deploy's tests need the default store under a fake home and spark's scripts there, else `command` is null in every test | lens L2 | acted | each test builds a resolved temp home; the scripts folder is a parameter, not a `mock.patch` (rule T2) |
| 5 | a word that `printable` changes must give no line | lens L3 | acted | `copy_line` gives None, row 9 |
| 6 | the home folder has two forms, as written and resolved | lens L4 | acted | `privacy.forms_of(home)`, row 12 |
| 7 | `quote_word` repeats `shell_word` | lens L6 | acted | dropped: `shell_word(word, homes=())` keeps zsh's `=word` rule |
| 8 | the default store's env must not reach the page's line, but `next` keeps P473's env | lens L7, refuter R2, council O5 | acted | `store.default_store()` and the flow's `without_default_store`; `read_given_env` stays as it is |
| 9 | the Copy of the run block must say other words than the chat's | lens L8, L9 | acted | `COPIED_LINE_SAYS` and the page word `copied_line`, row 17 |
| 10 | the plan said the published page holds no private path | refuter R3, council O6 | acted | the Artifact how-to says the page holds the folder names below the home folder in the `"$HOME"` form, never the user name |
| 11 | the paste test's child must not read the person's shell files | refuter R4 | acted | test_paste_line drops ZDOTDIR, BASH_ENV and ENV from the child's env |
| 12 | a story run that holds the paste test with no zsh or bash must stop the gate | refuter R6 | acted | `NO_SHELL_LINE` beside `NO_NODE_LINE` in tools/check_commit.py, row 18 |
| 13 | after the merge of P1209, commands/page.md named a kind of offer ("On the deploy") | build, test_routes | acted | the sentence names `data.guide.now.command` |
| 14 | flow_codes.py (606) and store.py (605) passed 600 lines, `page_words` 40 lines, and a test's `patch.start()` counted as a `mock.patch` | build, test_architecture (R1, T2) | acted | the words fold as P1209's did; the test's local is `patcher` |
| 15 | store.py's docstring said the module imports only the standard library and `text_guards` | build (prune) | acted | the wrong claim is gone: it imports records_codes, outcomes and errors too |
| 16 | the build's next step should agree with show's NOW, and the `now:` line come for check_spine only | council O1 | raised | P1292 [#1859](https://github.com/xmejkal/spark/issues/1859), in Ready |
| 17 | the image-build line should stand alone on its line | council O1 | raised | P1293 [#1860](https://github.com/xmejkal/spark/issues/1860) (XS), in Ready |
| 18 | with spark's scripts outside the home folder, show's `guide.now.command`, the masked result and the page's `<code>` held the scripts' whole path | PR refuter question 1, lens L3 | acted | `copy_line` gives None unless the script lies under one of `forms_of(home)`; TheCopyLineTest, red before the fix, and mutation row 19 (87cb2a7e) |
| 19 | `NO_LINE_TO_TYPE_SAYS` gave only the store and the project as reasons, and flow.md claimed a check of spark's install that the code lacked | PR refuter M2, lens L3 | acted | the sentence, flow.md and the Artifact how-to name spark itself in the home folder, and flow.md lists only what `copy_line` checks (629e622c) |
| 20 | no test shows that the page and show give the same line, and `write_page` had no `scripts` seam | PR lens L2 | acted | `write_page` takes `scripts` (a parameter, rule T2); ThePageLineIsShowsLineTest asserts at the deploy that the run block's `<code>` is show's `data.guide.now.command` (cf584b14) |
| 21 | the reading's guard finds only `Path` objects, on a project with no steps, and its docstring said the reading holds no path | PR lens L1 | acted | the docstring says what the guard proves, and an ast check pins that `compose_page` never reads `reading.steps` (e138c08f) |
| 22 | test_paste_line's `SHELLS` repeats check_commit's `PASTE_SHELLS` | PR lens L5 | acted | the test imports `PASTE_SHELLS` (bb553b90) |
| 23 | a test compares `step_command(THEN)` with its own default | PR lens L6 | acted | the assert is gone; the `endswith` assert beside it holds the meaning (b10c701f) |
| 24 | a stray edit wrote `GOAL ="..."` in tests/test_flow.py | PR refuter M3 | acted | the space is back (cb9535aa) |
| 25 | flow.md should name `reading_of`, not `show_flow.with_command`, as what adds the two keys | PR lens L8 | rejected | `with_command` adds them and `reading_of` calls it, for show and the page alike (the refuter) |
| 26 | flow_codes.py and store.py both sit at 600 lines, R1's limit, and flow_codes.py folds three constants into one line of 255 characters | PR lens L7, refuter | raised | a card that spark-main files: the page's words out of flow_codes.py, and room in store.py |
| 27 | NEXT sends the person to the terminal for the deploy, and the run block under it holds the look but never names its step | PR refuter, the Chrome note | raised | a card that spark-main files: the deploy's run block names its step, the look; the words are the PO's (O4) |
| 28 | no golden shows the page at the deploy phase with its run block: the only golden page is at the build phase | PR refuter M4 | raised | a card that spark-main files: a golden of the page at the deploy phase, with the run block |
