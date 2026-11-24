# P1096 and P1097: a crash or a Ctrl-C in the flash writes its board log, and the look says the board may be erased: rows

Cards: [P1096 #1614](https://github.com/xmejkal/spark/issues/1614) and [P1097 #1615](https://github.com/xmejkal/spark/issues/1615),
two stories in one PR. New logic: a plan, a plan council (one lens on Sonnet, the refuter on Opus) and a second round
(the refuter on Opus), then the build. This file holds the acted, raised and rejected findings only (rules.md). 2026-11-24.

| # | claim | source | status | evidence / where it went |
| --- | --- | --- | --- | --- |
| 1 | D1, G1: card 1's Done-when asks for a page.html that does not name the old stand, and P1038's 0c rule says a crash writes no page | plan council | raised | delegated, the PO's to change: option A, the 0c rule stands, and the clause narrows to "show and every page written after the stop". Raised for him at the day close; commented on #1614. Test T4 pins the rule and the next page write |
| 2 | D8, G18: a crash or a Ctrl-C at stage verify also writes no board log, so `show` keeps the old stand | plan council | raised | [P1110 #1634](https://github.com/xmejkal/spark/issues/1634), filed by spark-main; out of this PR |
| 3 | G2: the crash's log sentence must not point to "the traceback on stderr", which a person reads days later | plan council | acted | `NOT_FINISHED_SENTENCES[codes.CRASH]` is its own sentence; T1 reads it in the log |
| 4 | G3: row 10's `find` is the whole one-line `keep_record` call, so its `pass` mutant compiles | plan council | acted | the call is one line; `--anchors` compiles the mutant |
| 5 | G4: `record_not_finished` builds no second key list | plan council | acted | `dict(self._facts_of(image, look, (), moment), image_sha256=..., micropython_banner=None)`, with a comment |
| 6 | G5: the store entry's `deployed` is the board log's own moment, read once | plan council | acted | `moment` on the exception beside `log_path` and `image_sha256`; `FlashError.moment = None` |
| 7 | G6: a null `micropython_banner` also means a flash that did not finish | plan council | acted | `agents/json.md`, the `last_deploy` line |
| 8 | G7: the new words go through `printable`, as their siblings do | plan council | acted | `say_last_deploy` and `say_last_deploy_in_question` |
| 9 | G8, G21: `interrupted` reaches no envelope, but it does reach `data.deploy.cause` | plan council, second round | acted | no code-table row; the reasons line of `agents/json.md` names both new codes and says `data.deploy.cause` holds the code |
| 10 | G9: a second Ctrl-C during the write must not leave half a log | plan council | acted | `write_board_log` writes through `store.replace_file`, a `.log.part` that the `*.log` glob never takes; `board_log.py`'s T1 baseline entry goes |
| 11 | G10: a BrokenPipeError from the first `running:` line is logged `flash not finished` though no command ran | plan council | rejected | the report fails before a command only on a broken stderr, and `the board may be erased` is what `_crashed` says at stage flash anyway |
| 12 | G11: `refuse_at_look` tests `ended_the_flash`, not `FlashError` | plan council | acted | a SparkError raised in the loop gets its log line and store record too; none is raised there today |
| 13 | G12, G20: the marker is `image_sha256` alone, and a log write that raises sets none of the three attributes | plan council, second round | acted | one tuple assignment with the write on its right; T11 |
| 14 | G13: after a bug in the log write, a Ctrl-C ends as a crash with exit 2, not SIGINT's 130 | plan council | acted | the docstring of `log_not_finished` and `commands/deploy.md` say so |
| 15 | G14, G15: a deploy grant asks no next yes, and the store write after a Ctrl-C takes the store's blocking lock | plan council | rejected | G14: a grant covers the next deploy, so only the look's stderr lines carry the sentence. G15: the lock waits only on another spark process, and a second Ctrl-C ends the wait |
| 16 | G16: build_record.py and requirements_build.py catch BaseException, clean up and re-raise: the precedent | plan council | acted | the docstring of `DeployService.deploy` names it |
| 17 | G19: no MAC means no token, so `record_not_finished` needs no None guard; `image_of` can raise DeployError | second round | acted | no guard and no T10; `keep_record` catches `DeployError` too |
| 18 | G22: T11 goes in step 1, and `deploy_service.py` imports `spark.core.codes` | second round | acted | step 1's commit |
| 19 | the new handler's `moment = self.clock.now()` and `record_not_finished`'s `return self.records.write_deploy(` made three older rows find their text twice | the builder's `--anchors` | acted | after the review (row 23) the handler's read is `now`, so both `moment = self.clock.now()` rows keep their own find; the seam row of `p474-seams.json` finds the code `return self.records.write_deploy(result.facts`. P1092's rows 1, 4 and 6 re-anchored as the plan says |
| 20 | the plan says `map.md` does not change, but its test lists follow the tests' imports | the builder | acted | `tools/map.py --write`: `events.py` and `deploy_record_store.py` list one more test module |
| 21 | the `deploys_from` cell of `agents/bench.md` went over 300 characters with the new sentence | the builder | acted | the sentence went below the table |
| 22 | who cannot be read: verify writes no record, while the not-finished entry is kept with who `not known (...)` | PR lens (Sonnet) | acted | kept on purpose, as the erase is a fact; the docstrings of `who_said_yes` and `record_not_finished` say so; a test |
| 23 | two rows hung on a comment after the handler's `moment = self.clock.now()` made their find occur twice | PR lens (Sonnet) | acted | the handler's read is `now`; the rows of `p291-time-zones.json` and `p474-seams.json` have their old find again |
| 24 | no row pins that `record_not_finished` writes through the records seam | PR lens (Sonnet) | acted | a service test with `FakeDeployRecordStore`, and a row |
| 25 | `keep_record`'s DeployError catch has no test: without it, a FlashError whose image cannot be read now becomes a crash | PR refuter (Opus) | acted | a test where the grant ends in the retry wait and `sim/wokwi.toml` then names an image outside sim/, and a row |
| 26 | no test pins that the store entry's `deployed` is the board log's moment, nor the banner and image overrides | PR lens (Sonnet), PR refuter (Opus) | acted | a test with a clock that moves at each read, and the service test; three rows |
| 27 | "After a Ctrl-C it exits 2, not 130" reads as if every Ctrl-C exits 2 | PR refuter (Opus) | acted | "After a Ctrl-C, such a bug ends the run with exit 2, not 130." |
| 28 | `board_log.py`'s spark.core imports are not together | PR lens (Sonnet) | acted | grouped |
| 29 | the rejected rows give no reason, and row 1 does not say the card has the comment | PR lens (Sonnet) | acted | rows 1, 11 and 15 |
| 30 | `bench.py show`'s human line (N, last ...) counts a flash that did not finish as a deploy | PR review | raised | dropped because the agents' page states it, and the count is of deploys tried |
| 31 | an image deleted during the flash makes any not-finished answer crash at `look.to_dict()` (FileNotFoundError, P1092's path too) | PR review | raised | card P1111 #1636 |
