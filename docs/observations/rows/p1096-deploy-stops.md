# P1096 and P1097: a crash or a Ctrl-C in the flash writes its board log, and the look says the board may be erased: rows

Cards: [P1096 #1614](https://github.com/xmejkal/spark/issues/1614) and [P1097 #1615](https://github.com/xmejkal/spark/issues/1615),
two stories in one PR. New logic: a plan, a plan council (one lens on Sonnet, the refuter on Opus) and a second round
(the refuter on Opus), then the build. This file holds the acted, raised and rejected findings only (rules.md). 2026-11-24.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | D1, G1: card 1's Done-when asks for a page.html that does not name the old stand, and P1038's 0c rule says a crash writes no page | plan council | raised | delegated, the PO's to change: option A, the 0c rule stands, and the clause narrows to "show and every page written after the stop". Raised for him at the day close; the card gets a comment. Test T4 pins the rule and the next page write |
| 2 | D8, G18: a crash or a Ctrl-C at stage verify also writes no board log, so `show` keeps the old stand | plan council | raised | [P1110 #1634](https://github.com/xmejkal/spark/issues/1634), filed by spark-main; out of this PR |
| 3 | G2: the crash's log sentence must not point to "the traceback on stderr", which a person reads days later | plan council | acted | `NOT_FINISHED_SENTENCES[codes.CRASH]` is its own sentence; T1 reads it in the log |
| 4 | G3: row 10's `find` is the whole one-line `keep_record` call, so its `pass` mutant compiles | plan council | acted | the call is one line; `--anchors` compiles the mutant |
| 5 | G4: `record_not_finished` builds no second key list | plan council | acted | `dict(self._facts_of(image, look, (), moment), image_sha256=..., micropython_banner=None)`, with a comment |
| 6 | G5: the store entry's `deployed` is the board log's own moment, read once | plan council | acted | `moment` on the exception beside `log_path` and `image_sha256`; `FlashError.moment = None` |
| 7 | G6: a null `micropython_banner` also means a flash that did not finish | plan council | acted | `agents/json.md`, the `last_deploy` line |
| 8 | G7: the new words go through `printable`, as their siblings do | plan council | acted | `say_last_deploy` and `say_last_deploy_in_question` |
| 9 | G8, G21: `interrupted` reaches no envelope, but it does reach `data.deploy.cause` | plan council, second round | acted | no code-table row; the reasons line of `agents/json.md` names both new codes and says `data.deploy.cause` holds the code |
| 10 | G9: a second Ctrl-C during the write must not leave half a log | plan council | acted | `write_board_log` writes through `store.replace_file`, a `.log.part` that the `*.log` glob never takes; `board_log.py`'s T1 baseline entry goes |
| 11 | G10: a BrokenPipeError from the first `running:` line is logged `flash not finished` though no command ran | plan council | rejected | accepted as it is: `the board may be erased` matches what `_crashed` says at stage flash |
| 12 | G11: `refuse_at_look` tests `ended_the_flash`, not `FlashError` | plan council | acted | a SparkError raised in the loop gets its log line and store record too; none is raised there today |
| 13 | G12, G20: the marker is `image_sha256` alone, and a log write that raises sets none of the three attributes | plan council, second round | acted | one tuple assignment with the write on its right; T11 |
| 14 | G13: after a bug in the log write, a Ctrl-C ends as a crash with exit 2, not SIGINT's 130 | plan council | acted | the docstring of `log_not_finished` and `commands/deploy.md` say so |
| 15 | G14, G15: a deploy grant asks no next yes, and the store write after a Ctrl-C takes the store's blocking lock | plan council | rejected | accepted risks, named in the plan; the look's lines still carry the sentence |
| 16 | G16: build_record.py and requirements_build.py catch BaseException, clean up and re-raise: the precedent | plan council | acted | the docstring of `DeployService.deploy` names it |
| 17 | G19: no MAC means no token, so `record_not_finished` needs no None guard; `image_of` can raise DeployError | second round | acted | no guard and no T10; `keep_record` catches `DeployError` too |
| 18 | G22: T11 goes in step 1, and `deploy_service.py` imports `spark.core.codes` | second round | acted | step 1's commit |
| 19 | the new handler's `moment = self.clock.now()` and `record_not_finished`'s `return self.records.write_deploy(` made three older rows find their text twice | the builder's `--anchors` | acted | re-anchored in place on the verify's lines, with the same mutants: `p291-time-zones.json` (1), `p474-seams.json` (2); P1092's rows 1, 4 and 6 re-anchored as the plan says |
| 20 | the plan says `map.md` does not change, but its test lists follow the tests' imports | the builder | acted | `tools/map.py --write`: `events.py` and `deploy_record_store.py` list one more test module |
| 21 | the `deploys_from` cell of `agents/bench.md` went over 300 characters with the new sentence | the builder | acted | the sentence went below the table |
