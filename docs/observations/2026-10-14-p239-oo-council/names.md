# P239 names and docstrings lens (scope: the eight deploy-area scripts)

## 1. Naming rule (for docs/guide/developing.md)

Name a thing for what it is to a reader who has never seen spark. Then add a role word only when the word tells the reader something the noun does not.

- **Role word on the name.** Use `Strategy` for a swappable behaviour that has a base class (`ConsentStrategy`). Use `Result` for a bundle a function returns (`ReadyResult`). Use `Error` for every exception (PEP 8). Use `Service` for a class whose only job is to run a sequence over its collaborators (`LookService`). Use `Adapter` only where a class wraps an outside program behind spark's own interface, and then only on the base or in the first docstring line, not on every subclass.
- **No role word.** A value object or a domain noun stays plain (`Port`, `Reading`, `Report`). A noun that already is a role (`Reader`, `Finder`, `Connection`, `Check`) takes no second one: `BoardReaderStrategy` and `ReadyCheckService` are noise.
- **Base and subclasses.** A subclass is `Variant` + the base's whole name: `ConsentStrategy` -> `TerminalConsentStrategy`, `BoardReader` -> `EsptoolBoardReader`. The tool or medium comes first, so the class list sorts by what varies. A reader sees the base from the last word.
- **Modules.** `snake_case`, named for the noun the module holds (`board_connection.py` holds `BoardConnection`). A script that only parses arguments is named for the verb the person runs (`look.py`, `deploy.py`) and its library never shares the stem, so `board_look.py` is the library of `look.py`: rename it `board_look_service.py` or merge, so two files are not one name.
- **Functions and methods.** Verb first (`find_ports`, `write_board_log`). A function that returns a reason or None starts `why_`. A predicate starts `is_` or `has_`. `x_of(y)` is allowed only for a plain lookup. A function that raises instead of returning says so (`require_open_gate`).
- **Constants.** `UPPER_SNAKE`, a unit suffix on every number (`_S`, `_MB`), `_HINT` or `_MESSAGE` on a sentence, no bare `MB`, `ERASE`, `UNKNOWN`.
- **Parameters.** A noun that says what it is (`board_record`, not `record`; `facts`, not `said`). An injected command runner is `run`, and its default is `subprocess.run`.
- **Exceptions.** Python ends them in `Error`. The repo mixes `Problem` (`ToolProblem`, `StoreProblem`, `DeployProblem`), `Stop`, `Closed` and `Error` (`BoardError`). Pick `Error` and rename the others in one PR across the repo, not only here.

Where the role word helps: the three swap points a newcomer will extend (consent, board reader, connection) and the exceptions, because a reader sees at once what to subclass or catch. Where it is noise: every class that is already a noun-with-role, and `Service` on a class that is just a data holder.

## 2. Table (public names in scope)

| Current | Proposed | Reason |
|---|---|---|
| deploy_gate.Closed | GateClosedError | says which gate, and that it is an error |
| deploy_gate.Consent | ConsentStrategy | the swap point (D19) |
| deploy_gate.TerminalConsent | TerminalConsentStrategy | Variant + base |
| deploy_gate.gate_open | require_open_gate | it raises, it does not answer; "gate_open" reads like a boolean |
| gate_open `token` | `given_token` | it is the person's token, not the board's |
| gate_open `report` | `look_report` | many reports in spark |
| NO_TERMINAL | NO_TERMINAL_MESSAGE | a sentence |
| board_look.LookStop | LookError | Error suffix |
| board_look.PortFinder | keep | Finder is its role; `boards()` -> `find_ports()` returns Ports |
| PortFinder `shell` | `board_shell_tool` | "shell" means a command line elsewhere |
| board_look.BoardReader | keep | Reader is the role; the base of the swap |
| board_look.EsptoolReader | EsptoolBoardReader | Variant + base name |
| EsptoolReader.parse | parse_flash_id_output | says what it parses |
| EsptoolReader `flasher` | `flasher_tool` | it is a tools.Tool |
| board_look.Port | keep | a plain value |
| board_look.Reading | BoardReading | "Reading" alone is vague beside Report |
| board_look.FIELDS | COMPARED_FIELDS | says what the rows are |
| board_look.compare | compare_fields | verb plus object |
| board_look.MB | BYTES_PER_MB | it is a unit factor |
| LIST_TIMEOUT, READ_TIMEOUT | LIST_TIMEOUT_S, READ_TIMEOUT_S | unit |
| board_look.Report | LookReport | deploy and ready_check also have reports and results |
| Report `image_why` | `image_problem` | the sentence says what is wrong, not why it exists |
| Report.verdict / status / exit_code / token | keep | clear |
| board_look.Look | LookService | runs the look over its finder and reader |
| Look.run | keep | one entry point |
| Look.record_of | board_record_of | "record" has two meanings in spark |
| Look.only_port | find_only_port | verb first |
| board_look.looker | build_look_service | noun-named function is a factory, say so |
| look.lines | report_lines | `lines` says nothing |
| look.RESTART, TOKEN | RESTART_NOTICE, TOKEN_LINE | sentences |
| board_connection.BoardConnection | keep | the noun is the role; docstring says it adapts mpremote |
| BoardUnreachable | BoardUnreachableError | Error suffix |
| CodeRaisedOnBoard | BoardCodeError | shorter; the board's code raised |
| BoardConnection.run_code | keep | `keep_running_for` -> `keep_running_s` (unit) |
| copy_to_board, read_file, repl_command | keep | clear |
| BOARD_TRACEBACK, DEFAULT_TIMEOUT_S | keep | clear, has unit |
| ready_check.ReadyCheck | keep | Check is the role |
| ReadyCheck.check | keep, return a `ReadyResult(verdict, sentence, log)` | a 3-tuple has no names at the call site |
| READY_WAIT | READY_WAIT_S | unit |
| SEEN, NOT_SEEN, UNKNOWN | READY_SEEN, READY_NOT_SEEN, READY_UNKNOWN | `from x import UNKNOWN` is unreadable |
| HASH_FILES | HASH_FILES_CODE | it is MicroPython source, not files |
| board_facts.facts | build_facts | verb first; it shadows its own parameter in record_deploy |
| board_facts.facts_text | facts_to_json | says the format |
| facts `files` | `file_hashes` | {path: sha256} |
| board_facts.FactsFile | BoardFactsFile | it lives on the board; the store has records too |
| FactsFile.write(`said`) | write_and_verify(`facts`) | it also reads back; `said` is opaque |
| board_facts.record_deploy | keep | verb first, clear |
| PLUGIN_JSON | PLUGIN_JSON_PATH | a path |
| image_check (module) | keep for now | hosts DeployProblem, BOOT_HINT and `runnable`, which do not belong; split later |
| image_check.DeployProblem | ImageNotReadyError | it is raised for the image, and deploy.py also uses it for chip; weigh with the Error rename |
| image_of | keep | plain lookup |
| run_logs | read_run_logs | verb first; returns 3-tuples, wants a `RunLog` namedtuple |
| untested | why_untested | returns a reason or None |
| passed_log | find_passed_log | verb first |
| tested_another | why_other_runs | returns a reason or None |
| runnable | command_for | it returns a command list |
| deploy.plan | plan_flash | "plan" what? Returns a 3-tuple: use a `FlashPlan` |
| newer_files | files_newer_than_image | a bare adjective hides the comparison |
| board_of, chip_of | keep | plain lookups |
| flash_commands | keep | |
| keep_board_log | write_board_log | `keep` is spark jargon for `--keep`; 7 parameters want a `BoardLogEntry` |
| put_facts | write_facts_to_board | `put` is vague |
| rerun_line | keep | |
| IMAGE_OFFSET, EPILOG | keep | |
| ERASE, WRITE | ESPTOOL_ERASE, ESPTOOL_WRITE | bare names clash in scope |
| WATCH, OLDER_RUNS_WAY_OUT | WATCH_HINT, OLDER_RUNS_HINT | sentences, one name style |

## 3. Docstring standard

A class docstring says: its job in one sentence, what it collaborates with (its injected objects), what a subclass must supply if it is a base, and what its methods raise. A public function says: what it returns (the shape of a tuple or dict), what it raises, and what it never does (writes, erases). Add a one-line example only where the input is not obvious (a token, a `{path: sha256}`). A module says what it is a library for and who calls it. Private helpers need one line. A constant that holds a sentence or a number needs a comment with its unit or its source.

Falls short:

- deploy_gate.py:25-29 `Consent` and `ask`: no mention of what raises (Closed) or that a subclass may raise it.
- deploy_gate.py:35 `TerminalConsent.__init__`: `stdin` and `stdout` injection unexplained.
- board_look.py:31 `Port`: no field meaning (`serial`, `usb`).
- board_look.py:49 `PortFinder.boards`: none; what it returns (Ports) and raises (LookStop) is unsaid.
- board_look.py:77 `EsptoolReader.read`: none; raises LookStop in four cases.
- board_look.py:108, 126: private helpers with none.
- board_look.py:134 `Report.__init__`: the rule for stops and warnings lives only in code; no doc of `image_why`.
- board_look.py:177 `Look`: names no collaborators (`finder`, `reader`).
- board_look.py:210 `Look.only_port`: none.
- board_connection.py:44-46 `BoardConnection`: the class and `__init__` do not say `run` is injectable, and the class does not name its two errors.
- ready_check.py:36-42 `ReadyCheck.check`: returns a 3-tuple, documented only in one line; the three verdicts have no comment.
- board_facts.py:22 `PLUGIN_JSON`, board_facts.py:25 `facts` (parameters not described), board_facts.py:44 `FactsFile.write` (name says write, docstring says verify).
- image_check.py:23, 34, 50 are good; 68 and 74 run over one line each and omit DeployProblem.
- deploy.py:105 `keep_board_log`: seven parameters, none described.
- deploy.py:126 `plan`: the 3-tuple order is described, but not what `notes` holds.
- look.py:32 `lines`: no collaborators; `token=False` is not explained.
