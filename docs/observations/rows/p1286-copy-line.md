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
| 16 | the build's next step should agree with show's NOW, and the `now:` line come for check_spine only | council O1 | raised | a card that spark-main files |
| 17 | the image-build line should stand alone on its line | council O1 | raised | an XS card that spark-main files |
