# P239 refuter: the three lenses checked against the code

Read on branch p239-oo-council, 2026-10-14. C = confirmed, P = partly, R = refuted.

## Structure lens

| Claim | Evidence | Mark |
|---|---|---|
| image_check hashes the image again in each function | :55, 69, 75 | C |
| `project / "sim" / "runs"` is rebuilt by three callers | deploy.py:133, 207; board_look.py:190 | C |
| `runnable`, `BOOT_HINT` and `DeployProblem` are in image_check by accident | board_look.py:56, 87; deploy.py:96, 192, 204 | C |
| `Report` does three jobs | board_look.py:137, 138-147, 168-173 | C |
| The gate splits the token as a string | deploy_gate.py:55-56; deploy.py:191 compares it again | C |
| `look.lines` is a presenter that deploy imports | deploy.py:38, 185 | C |
| Two mpremote callers, each with its own errors | board_look.py:47-59; board_connection.py:74-90 | C |
| `Closed` is raised by the gate only | `TerminalConsent.ask` also raises it (deploy_gate.py:40) | P |
| Bases raise NotImplementedError | Consent (29). It misses BoardReader (68), which does the same | P |
| Step 7 needs a `BoardShell` base now | there is one shell, and AGENTS.md says grow by need | R as timing |

## Names lens

| Claim | Evidence | Mark |
|---|---|---|
| `FactsFile.write` also reads back | board_facts.py:51-54 | C |
| The parameter `facts` hides the function `facts` | board_facts.py:57 | C |
| `ImageNotReadyError` fits DeployProblem | it is also raised for the chip and a changed image (deploy.py:96, 192) | R |
| `from ready_check import UNKNOWN` is unreadable | deploy.py uses `ready_check.UNKNOWN` (218). The prefix is still fine | P |
| Rename every `Problem` to `Error` across the repo | 21 exception classes; four of them appear in 91 files. AGENTS.md defers this to v2 #94 | R for now |

## Extension lens

| Claim | Evidence | Mark |
|---|---|---|
| `deploy.main` is 90 lines | it is 67 lines (155-221), and about 48 of them are the flow | P |
| The reconnect fix (P238) has no injected sleep, and after the look `main` holds only `report.port` | board_connection.py:46; deploy.py:209 | C |
| `record_deploy` writes "typed in a terminal" for any yes | board_facts.py:64 | C: false once a second Consent exists |
| The fakes match on argv | test_deploy_gate.py:86-94; test_board_look.py:50-52; test_look.py:29-31 | C |
| The test `Connection` has no `read_file` | test_ready_check.py:48-62 | C |
| `datetime.now()` is not injected | deploy.py:107; board_facts.py:29 | C |
| Tests patch names inside the module | test_deploy_gate.py:284 | C |

## Contradictions, and the side taken

1. `LookService`, not `BoardLookService`: the module already says board.
2. `DeployService`, not `Deployer`: the PO's role word, and it matches LookService.
3. A class, not the functions, because there are three hashes and three paths. Call it `ProjectImage`, not `ImageProvenance`, which is jargon.
4. `ConsentStrategy`: "Consent" reads as a fact. `BoardReader` and `Flasher` already name a doer, so they get "Strategy:" in the docstring only.
5. The Error suffix in scope only (LookStop, Closed, BoardUnreachable, CodeRaisedOnBoard, DeployProblem). The rest waits for v2 #94.
6. Keep `EsptoolBoardReader` and add `EsptoolFlasher` on one shared esptool command helper. The reader's tests stay as they are.
7. `BoardShell` waits for a second shell. P238 goes into `BoardConnection`.
