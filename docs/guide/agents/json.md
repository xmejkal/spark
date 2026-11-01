# The scripts' JSON, for AI agents

Part of the [guide for AI agents](../agents.md).

## check_all's answer

To check a project, run one command that answers once:

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/check_all.py" --project . --json
```

`--project` names the folder that holds the requirements file and the kept build. The rules, the parts and the boards
come from the project that the build reads, which is the nearest folder up that holds `.spark/` or
`boards/active.json` ([P319](https://github.com/xmejkal/spark/issues/403)). The answer's `project` key names that
project as a whole path. It is `null` when no folder up is a project: then the parts and boards come from the plugin's
library, and there are no rules. The first resolved line names a project that is not the folder, or says that there
is none. A `--project` that is not a directory has no `project` key ([what exit 0 means](#what-exit-0-means)).
The sample below is older than P319, so it has no `project` key.

### What exit 0 means

No check that ran found a problem or failed to look; skipped checks do not count.

- A `--project` that names no folder is `could-not-run`, exit 2, with the reason `no directory at <path>`. Other paths
  can still miss ([P117](https://github.com/xmejkal/spark/issues/51)). Before you report, confirm in `resolved`, or
  in the flags you passed, that check_all found the circuit and the rules.
- When every check is skipped, check_all answers could-not-run, exit 2.
- Exit 0 with `unmeasured` above 0 is an ok on those `?` lines.

This is its answer for the project in the journey guide. It came after a build and
`init_project.py --project . --board firebeetle2-esp32s3 --force`, which names the rails from the built board:

<!-- output: run 2026-10-05, spark 0.6.0 -->
```text
{
  "tool": "check_all",
  "status": "could-not-run",
  "resolved": [
    "circuit      dist/board/circuit.json",
    "rules        .spark/rules.json",
    "package      not found (looked for *-gerbers.zip, fab/*.zip)",
    "boards       2 definition(s): firebeetle2-esp32s3, xiao-esp32-c6"
  ],
  "results": [
    {
      "check": "vendor-truth",
      "what": "the board definition matches the vendor's own pin header",
      "status": "ok",
      "problems": [],
      "unchecked": []
    },
    {
      "check": "buildability",
      "what": "holes take their pins, packages hold their values",
      "status": "ok",
      "problems": [],
      "unchecked": [],
      "unmeasured": [
        "JstPh2PowerInlet: pad 1.20 mm around a 0.75 mm hole leaves 0.225 mm of ring: over the 0.18 mm this process can make, under the 0.25 mm it recommends"
      ]
    },
    {
      "check": "the-order",
      "status": "skipped",
      "what": "the fab package orders the parts the schematic specifies",
      "reason": "not given package"
    },
    {
      "check": "physics",
      "what": "the board obeys physics, not just itself",
      "status": "could-not-run",
      "problems": [],
      "unchecked": [
        "MOTOR6V: draws at least 0 mA; not stated: L9110sModule.VCC: names no fact for its current; JstPh2PowerInlet.VCC: names no fact for its current",
        "4 resistor(s): could not be assessed: BtnModePullupA, BtnOpenPullupA, L9110sModulePulldownAIA, L9110sModulePulldownAIB. A netlist records neither the current through a resistor nor the voltage across it, and both depend on topology the design does not state"
      ],
      "unmeasured": [
        "V33: draws 355 mA of 1.50 A, resting on figures nobody has verified: Mcu.3V3: regulator_3v3_a",
        "GND: no maximum current stated, so nothing here can be verified",
        "MOTOR6V: no maximum current stated, so nothing here can be verified; the part records leave it open: L9110sModule.VCC"
      ]
    },
    {
      "check": "rules-vs-netlist",
      "what": "written rules hold in the design that was built",
      "status": "ok",
      "problems": [],
      "unchecked": []
    }
  ]
}
```

The fields:

| field | what it holds |
| --- | --- |
| `tool` | the script that answered |
| `status` | the overall outcome |
| `unmeasured` | how many `?` lines the answer rests on: values nobody has measured or verified, and advisories. An `ok` with a count above 0 is an `ok` on those lines. Added after the runs shown here ([P108](https://github.com/xmejkal/spark/issues/42)) |
| `resolved` | display lines: what `--project` found by convention for the circuit, rules, package and boards, or where it looked. A file named by an explicit flag overrides it, yet the convention's line stays, so `resolved` can name a file that was not checked. With no `--project`, it is empty |
| `results[].check` | the check's name; [how it works](../how-it-works.md#the-checks) names its script |
| `results[].what` | what the check claims |
| `results[].status` | `ok`, `problems`, `could-not-run` or `skipped` |
| `results[].problems` | what is wrong |
| `results[].unchecked` | what it could not look at |
| `results[].unmeasured` | advisories and values that need measuring; they do not change the outcome |
| `results[].reason` | why a check was skipped, or why it could not run when an input was ambiguous (two candidates: name one with its flag). Two circuits say "spark handles one board per project today" and name the first one's absolute path for `--circuit`, or one folder per board with its own `parts/` (P223) |

**When a field is absent.** A field with nothing to say may be absent:

- `problems` and `unchecked` are present whenever a check ran.
- A skipped result, and a could-not-run caused by an ambiguous input, carry `reason` instead, and `reason` is then the
  only explanation.
- `results[].unmeasured` appears only when it is non-empty. The top-level `unmeasured` is always present, as an integer.

**Under problems, read `unchecked` too.** `unchecked` can be non-empty under `problems`. problems outranks
could-not-run, both in `status` and in the exit code, so read every `unchecked` list.

**In the text output,** `problems` are the `-` lines, `unchecked` the `!` lines and `unmeasured` the `?` lines.

The requirements files, which buildability and physics also read, are not listed in `resolved`. vendor-truth checks
every board definition available, including the library's.

## The other scripts' JSON

Each script's top-level keys, as `tests/test_json_contracts.py` pins them (the test fails when a shape changes):

| script | top-level keys |
| --- | --- |
| `check_all.py` | `project` (with `--project`), `resolved`, `results`, `status`, `tool`, `unmeasured` |
| `check_physics.py` | `design`, `findings`, `status`, `tool` |
| `check_footprints.py` | `findings`, `status`, `tool` |
| `compare_design.py` | `checked`, `design`, `problems`, `status`, `tool`; a rules file naming no rule gives `fix` and `reason` instead of `problems`; a rules file that cannot be read or is refused gives `reason` (its old "not valid JSON" sentence for a broken rules file is now "could not be read") |
| `assign_pins.py` | `assignments`, `board`, `free`, `tool`, `unverified`. **No `status`:** read its exit code |
| `check_vendor_pins.py` | **a bare list**, one entry per board file ([its keys](#check_vendor_pinspy)) |
| `emit_footprint.py` | `check`, `message`, `status` |
| `import_firmware.py` | `modules`, `problems`, `status`, `tool`, `unchecked` ([more](#import_firmwarepy)) |
| `check_spine.py` | `check`, `stages`, `status`, and `kept`, `missing_facts` and `unserved` when they apply ([its keys](#check_spinepy)) |
| `look.py`, `deploy.py` | the envelope, as `parts.py`'s ([their envelope](#lookpy-and-deploypys-envelope)) |
| `parts.py` | the envelope: `assumptions`, `data`, `envelope`, `next`, `notes`, `op`, `problems`, `status`, `tool`, `truncated`, `unchecked` |

### check_spine.py

- `stages` names the stage that stopped it. A stage of a `"board_only": true` design is `skipped`, which is never `ok`.
  `parts.py --requirements` writes `board_only` when the board serves every need and no part is listed, and removes it
  when a part is listed.
- `kept`, with `--keep` or `--sim-dir`, lists each file: `file` as typed to `--keep`, `did` (`wrote`, `left alone`,
  `removed`, `not written` or `not kept`) and `why`. A `not written` entry of a drawing has `code` (`null` for an older
  refusal), `subject` and `expected` (`true` means by design, so do not retry). A `wrote` entry for `breadboard.svg` may
  have `drawn_from` (`record`).
- `unserved` is there when the requirements file carries the note `parts.py --requirements` writes for the needs it
  leaves off the board (`tests/test_check_spine.py` pins it).
- `missing_facts` is a top-level list, with `--keep` only, when spark writes `firmware/pins.py` and the board record
  lacks the level of its onboard LED or button ([P464](https://github.com/xmejkal/spark/issues/632)). The `wrote` entry
  for `firmware/pins.py` in `kept` has the same list. A build without `--keep`, or a `pins.py` spark left alone, gives
  no missing-fact signal yet ([rows](../../observations/rows/p464-missing-facts.md) 1 and 2).
  - Each item is `{subject, code, sentence, fix}`, with the code `missing_fact` and a subject such as
    `pin_roles.onboard_led.active_level`.
  - An item never changes `status` and is never in `unchecked`. So after `status`, read `missing_facts` when you built
    with `--keep`: `ok` does not mean the firmware has every fact.
  - Never guess the level. Ask the person (see `/spark:build`), or use `/spark:research` or a bench measure. Write the
    answer with `parts.py --fact-set <board> FILE --project <the project's folder>` (a board of another project is
    refused), and build again.
- The simulation line warns "no serial monitor is wired in the diagram" when the diagram has no `$serialMonitor` wires
  and the board's record lacks `serial_without_wires: true` ([P468](https://github.com/xmejkal/spark/issues/636)).
  spark's XIAO ESP32-C6 and FireBeetle 2 records carry it, so they get no warning. Read the warning as a possible silent
  `wait-serial`, not a failure.
- Refusals and crashes. Each stage that could not run shows as `[????] <stage>` with its sentence, then
  `the chain was NOT exercised — this is not a pass`, exit 2.
  - `emit_board.py`'s refusal of a board that states no `power.io_volts` shows as `[????] schematic` with that sentence
    ([P121](https://github.com/xmejkal/spark/issues/55)).
  - An `emit_board.py` that crashes inside `check_spine.py` is could-not-run too: the `schematic` stage's detail is
    `emit_board.py crashed: ` and the traceback's last line.
  - A crash in the spine's own read of the input or in the footprint drawing reads `<script> crashed: <Type>: <message>`,
    such as `emit_footprint.py crashed: RuntimeError: boom`. Such a detail is a crash, not a defect in the design.
  - A board whose file cannot give a footprint stops at `[????] footprint`, before the schematic. The detail names each
    missing fact (the gaps `emit_footprint.py` names), then says what the build still gives: with `--keep`, the kept
    lines say whether `firmware/pins.py` was written.
  - A board whose header and pad order disagree, or hold a value of the wrong kind (a pitch written as text), stops at
    `[????] footprint` too, in the sentence `the board definition disagrees with itself: …` (P411). A value of the wrong
    kind is named by its field, as `physical.header.pitch_mm is not a finite number` (a 400-digit number is one too).
    `emit_board.py` and the build stop at the footprint stage for it, before the schematic.
  - A fault in the requirements file (an unknown need, two parts of one name, pins that cannot be placed) is said first,
    under `schematic`. `emit_board.py` alone refuses that board with the same sentence, in the same order, exit 2
    ([P407](https://github.com/xmejkal/spark/issues/532)).
  - A requirements file whose `signals` or `parts` is no list, or whose `pin` is no non-empty string, is refused the same
    way, under `requirements`, naming the file and the field (`car.json: signals[0].pin is a list; write a pin name …`,
    [P438](https://github.com/xmejkal/spark/issues/583)). A `.spark/rules.json` that is a folder is refused under
    `schematic`.

### import_firmware.py

- Each item of `modules` has `module`, `status` (`imported`, `raised` or `timed out`) and `detail`.
- A project with no `firmware/` folder is `could-not-run`.
- A project with nothing to import but `main.py`, `boot.py` and `pins.py` is `problems`. Its firmware cannot be imported
  without running `main.py`.

### check_vendor_pins.py

- The answer is a bare list, one entry per board file.
- A compared board has `board`, `compared`, `not_recorded`, `problems`, `source` and `status`.
- A could-not-run has `board`, `status` and `reason`.
- A run without `--offline` that kept a header adds `wrote`, the whole path of that file, even on a could-not-run whose
  header held no pins. A live run refused before or during the fetch has none.
- `source` is `<repo> variants/<variant>/pins_arduino.h` live, and `the project's cache (<name>)` or
  `spark's cache (<name>)` with `--offline`.
- The status may say `mismatch` ([P43](https://github.com/xmejkal/spark/issues/11)).

Checking a shipped board's pin map, as an agent does, without the network:

<!-- runs: exit 0 -->
```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/check_vendor_pins.py" "$CLAUDE_PLUGIN_ROOT/boards/firebeetle2-esp32s3.json" --offline --json
```

<!-- output: run 2026-10-10, spark 0.8.1 -->
```text
[
  {
    "board": "firebeetle2-esp32s3",
    "status": "ok",
    "source": "spark's cache (dfrobot_firebeetle2_esp32s3.pins_arduino.h)",
    "compared": 25,
    "problems": [],
    "not_recorded": []
  }
]
```

### parts.py's envelope

- `problems` and `unchecked` hold items `{subject, sentence, fix}`; an `unchecked` item has no `subject`. `fix` says
  what to do, and may be null.
- `assumptions` is what an answer rests on that nobody has checked. It never changes the status, so read it whenever it
  is not empty. Each entry says what it is about (`fact`), why nobody has checked it (`basis`) and what depends on it
  (`sentence`).
  - `--unverified` lists one per fact whose `verified` is not true: `fact` is `<part>.<fact>`, `basis` is `unverified`,
    `assumed` is the value taken for now, `source` is where it came from, and `write` is the key a result goes back to
    with `--fact-set`: `facts.<name>`, `pin_order_proof` or `body_mm`. A guessed outline (`body_mm`) is listed, with its
    width and height as `assumed`. A skeleton outline (verified false, width and height null) is listed too, with nulls:
    it must be measured, and a null is never a value to copy back. A `write` of null means the
    record's `facts` is no object: repair the file by hand. `next` holds one `--fact-set <part> <file>` step, for the first
    part that has a row with a `write` key; with no such row it is empty, and the row's sentence already says to repair
    the file by hand. The text ends with the same step as a `next:` line. Its old `data.questions` is gone; `data.parts` only repeats
    the ids asked.
  - `--show` lists a CONFLICT that rests on an unverified fact: `fact` is `<part>.<pin>`, `basis` is `unmeasured`,
    `rests_on` names the facts to verify as `<part>.<fact>`, and `upgrade` says how. This `unmeasured` is a basis, not
    `check_all`'s `unmeasured[]` list.
- A **CONFLICT** is a pull the board adds that the module's own pull overrules, said with its arithmetic. When every fact
  it rests on is verified, `--show` lists it under `problems`, with a `fix`, and exits 1; `data.record` is there
  whatever the exit. Say it to the person. Never clear it by marking a fact unverified ([P124](https://github.com/xmejkal/spark/issues/58)).
- `notes` are said and never fail, each `{subject, sentence}`. `subject` is null when a note names nothing. A pick's
  notes are here.
- `next` is where suggested next commands, with their effects, would go. It is empty today: no operation fills it. Only
  `truncated.next` is filled, with the command for the rest of a long answer.
- Run every write with `--dry-run` first.
- In text, every item's fix and every next step is printed under the answer's lines, and a CONFLICT on unverified facts
  starts with `?`.

What nobody has checked about the 2-pin power inlet, as an agent reads it:

<!-- runs: exit 0 -->
```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --unverified jst-ph-2-power-inlet --json | python3 -m json.tool
```

<!-- output: run 2026-10-11, spark 0.8.1 -->
```text
{
    "envelope": 1,
    "tool": "parts",
    "op": "unverified",
    "status": "ok",
    "data": {
        "parts": [
            "jst-ph-2-power-inlet"
        ]
    },
    "problems": [],
    "unchecked": [],
    "next": [],
    "truncated": null,
    "notes": [],
    "assumptions": [
        {
            "fact": "jst-ph-2-power-inlet.pin_order",
            "basis": "unverified",
            "assumed": [
                "VCC",
                "GND"
            ],
            "sentence": "a pin order read wrong reverses a supply or swaps a signal",
            "source": "Pad 1 is VCC: this record's own convention for a generic 2-pin inlet, not read from a document."
        }
    ]
}
```

### Which scripts take --json

These take it: `assign_pins.py`, `check_all.py`, `check_footprints.py`, `check_physics.py`,
`check_spine.py`, `check_vendor_pins.py`, `compare_design.py`, `emit_footprint.py`, `deploy.py`, `grant.py` (with `--check`), `import_firmware.py`, `live.py`, `look.py` and `parts.py`. These do not take
it: `boards.py`, `breadboard.py`, `check_bom.py`, `emit_board.py`, `flash_image.py`, `init_project.py`, `run_scenario.py` and `tools.py`. `tools.py
--status` taking `--json` is not built yet ([P92](https://github.com/xmejkal/spark/issues/23)).

### What the text output shows

P423 and P430 set these rules for the text output of `parts.py`, `look.py`, `deploy.py`, `check_spine.py`, `run_scenario.py`, `grant.py`, `live.py` and `reach.py`:

- Guarded: a character that a terminal does not print, such as a control character or a right-to-left override, shows as `?`. A text's own line breaks stay. A value that can hold a line break of its own (a port, a project path, a button word of a board record) is put on one line first, so it cannot fake a line. This holds for the question that `deploy.py` asks you to type yes to, and for the sentence `grant.py` gives when it has no terminal to ask in (it holds the line to run, with your project path and port). A tools file is refused when a tool's name, or a name in its `needs`, holds a character that `str.isprintable` rejects: a control character or a bidi mark, and also a tab, a zero-width joiner (U+200D) or a no-break space (U+00A0), which an older spark let through. The `rm` path that `grant.py` prints after a deploy grant may show `?`: copy it from the store, not from the screen.
- Flat messages (P444, P445): a value that an error message holds (a store path, a record's name, a URL) is put on one line by the error class that builds the message (`ValueMessageError`), so a newline in it cannot fake a line of spark's own, in the text and in `--json` alike. This holds for every raise of every class that inherits `ValueMessageError`, and for the scripts that print their errors (`look.py`, `grant.py`, `live.py`, `reach.py`, `deploy.py`) and the lines `tools.py` prints about a folder. The V1 baseline is empty. An error class that does not inherit from `ValueMessageError` is outside this. The `reason` or `code` of a stop names why; key on it and never on the sentence. The raw values stay on the exception for a later field. A lone surrogate character in a text is cleaned to a space, and in a key it is refused, with or without `--dry-run`.
- Raw: `--json` carries the raw text of the other fields, so decide on the JSON and not on the screen (`check_spine.py --json` holds the raw text of a crash). `run_scenario.py` has no `--json`, and its log file in `sim/runs/` keeps the raw text. Two paths print raw text: the flash tool that `deploy.py` runs writes its own output to the terminal, and `emit_footprint.py` prints its own messages.
- Exact reply: in the text of `live.py` a tab in the board's reply shows as `?`, so read `output` from `--json` for the exact reply.

## look.py and deploy.py's envelope

`look.py --json` and `deploy.py --json` ([P213](https://github.com/xmejkal/spark/issues/192)) print one `outcomes.envelope` (`envelope`,
`tool`, `op`, `status`, `data`, `problems`, `unchecked`, `next`, `truncated`, and `notes` for deploy) on stdout. The status is
the exit code's ([the outcomes](../agents.md#the-outcomes-and-their-exit-codes)). With `--json`, deploy.py prints every line a person reads, and
the flash tool's own output, on **stderr**, so stdout holds the envelope alone. A bad flag prints an envelope with `--json` (below).
A raise after the flash (a traceback) prints no envelope; read the exit code and stderr. A crash in `look.py` prints an envelope with
one `unchecked` item, code `crash`, and exits 2; stderr gets `look: crashed, <class>`, the fix and the traceback, never the envelope.
Without `--json` it prints the same on stderr and nothing on stdout ([P442](https://github.com/xmejkal/spark/issues/587)).

**The `code` of an item** ([P433](https://github.com/xmejkal/spark/issues/575)). Every item of `problems` and `unchecked` in
`look.py --json` and `deploy.py --json` has `code`, the cause in one word. Decide on the code, never on the sentence. The codes
come from one table, `scripts/board_codes.py`. The same code can come from the look and from deploy.py (`evidence_refuses` is both).
`grant.py` and the other scripts write no `code`. In deploy.py, the reasons of a look that could not run come as an `unchecked` item of stage `look`.
look.py gives each stop, warning and unknown field an item of its own. deploy.py's gate gives one item for all the look's stops, with the first stop's `code`.
The column "needs the person" says whether the next step waits on the person's hands, yes or choice.

| code | where | means | next step | needs the person |
|---|---|---|---|---|
| `list_failed`, `list_timeout` | a look that could not run | mpremote could not list the boards on USB, or took too long | check mpremote (`/spark:setup`), reconnect, run look.py again | yes |
| `no_port` | a look that could not run | no board is on USB | ask the person to plug it in with a data cable | yes |
| `port_not_listed` | a look that could not run | the port `--port` names is not in the list | ask which board, or drop `--port` | yes |
| `two_boards` | a look that could not run | two or more boards are on USB and no `--port` says which | ask which board, run again with `--port` | yes |
| `flasher_not_esptool` | a look that could not run | the look reads with esptool only, and the project's flasher is another tool | stop and tell the person | yes |
| `board_not_read`, `read_timeout` | a look that could not run | esptool could not read the board, or took too long. `data.doctor` has the board doctor's result | relay the `fix` (the person's hands), then run look.py again | yes |
| `no_board_named`, `no_board_record` | a look that could not run | `requirements.json` names no board, or the project has no record of the board it names | name a board, or `/spark:research` for a record | yes |
| `tool_missing` | a look (could not run, or no token), a deploy (stage `plan`: mpremote, esptool, which is also refused when older than the oldest version spark runs, the MicroPython build or littlefs that the image check needs, [P436](https://github.com/xmejkal/spark/issues/580)) | a tool the step needs is missing, too old, or cannot be used. The sentence says what to install or fix: an install line, a tools file to repair, or a URL for a MicroPython build no tool holds | the person runs `/spark:setup`. Do not run an install line yourself. If the sentence names nothing to install, relay it to the person | yes |
| `chip_differs`, `flash_too_small` | `problems`, subject `stop` | the chip is not the record's, or the flash is smaller than the image. deploy.py will refuse | stop, tell the person | yes |
| `flash_differs` | `problems`, subject `flash` | the flash size is not one the record lists | relay it; deploy.py asks the person to accept it | yes |
| `field_unknown` | `unchecked` | the board or the record did not say a field | relay it; deploy.py asks the person to accept it | yes |
| `missing_fact` | top-level `missing_facts` of `check_spine.py --json` ([its keys](#check_spinepy)), never in `unchecked` | a stage needs a fact the board record lacks, such as the active level of the onboard LED or button. The build stays `ok`. The `fix` names the three ways | ask the person, or `/spark:research`, or a bench measure; write it, then build again ([how](#check_spinepy)). Never guess it | yes |
| `stop_found` | `unchecked` | the look found a stop, so it gave no token. The stop is its own item | as for the stop | yes |
| `no_mac` | `unchecked`, deploy stage `gate` | the board's MAC could not be read, so the look gave no token. `grant.py` refuses with it too | reconnect the board, run look.py again | yes |
| `evidence_refuses` | `unchecked` of a look, deploy stage `plan` | the evidence refuses the image: no passed run names it, a run tested another image, or another check failed. The sentence names the way out, or the no-simulation way | run a scenario, or what the sentence names (or the no-simulation way it names), then look.py again | no |
| `last_deploy_not_checked` | `unchecked` | spark's record of the board's last deploy could not be read | relay the `fix` (repair the record), run look.py again | yes |
| `no_terminal` | deploy, stage `gate` | there is no terminal for the person's yes. `data.run_in_terminal` is the line. It starts with `SPARK_HOME=<store>` when the run had one | give the person the line, word for word | yes |
| `token_missing` | deploy, stage `gate` | deploy.py got no token, so no look came before it | run look.py, then deploy.py with its token | no |
| `token_stale` | deploy, stage `gate` | the board or the image is not the one the token names | run look.py again | no |
| `answered_no` | deploy, stage `gate` | the person answered no | stop | yes |
| `grant_ended` | deploy, stage `gate` or `flash` | the deploy grant ended before the erase. At stage `flash`, `board_state` is `may_be_erased` | ask the person for a new grant or a typed yes. At stage `flash`, tell the person the board may be erased | yes |
| `no_sim_toml` | deploy, stage `plan` or a look | the project has no `sim/wokwi.toml` | build first (`/spark:build --keep`) | no |
| `firmware_line_bad` | deploy, stage `plan` or a look | the firmware line of `sim/wokwi.toml` cannot be read, or names an image outside `sim/` | fix the line as the sentence says, build again | no |
| `no_image` | deploy, stage `plan` or a look | the image that `sim/wokwi.toml` names is not there yet (a build writes the `firmware = ` line as a comment, so until a run writes it the image is `sim/flash-with-firmware.bin`) | run a scenario, or the no-simulation way the sentence names | no |
| `log_unreadable` | deploy, stage `plan` or a look | a run log in `sim/runs/` cannot be read | repair or remove the log, run look.py again | yes |
| `chip_unknown` | deploy, stage `plan` | the chip of the project's board record cannot be read | fix the board in `requirements.json` | no |
| `image_changed` | deploy, stage `gate` | the image changed after the person's yes | run look.py again | no |
| `flash_failed` | deploy, stage `flash` | a flash command failed. `data.board_state` is `may_be_erased` | relay the sentence (it names the BOOT and RESET places) | yes |
| `ready_not_seen` | deploy, stage `verify` | the board's files differ from the image, the firmware stopped with an error, or it printed no `ready`. The sentence tells which | fix the firmware, then look.py and a new yes | yes |
| `ready_unknown` | deploy, stage `verify` | the board could not be read after the flash, or the passed run's log names no files. The sentence tells which | run the `watch` step; if it has `needs_person`, tell the person first | if `needs_person` |
| `download_mode_stayed` | deploy, stage `verify` | the board still waits in download mode after the flash: the wait for its start ran out, though the port may have gone and come back. A restart counts only when mpremote answers after it ([P462](https://github.com/xmejkal/spark/issues/630)) | relay `data.person_action` (press RESET once) to the person, then run the `watch` step. Never deploy again for this | yes |
| `port_gone` | deploy, stage `verify` | the board's port was not listed after the flash, or went and did not come back. No mpremote call was made on a dead port, so `data.repl_command` is null and `next` has no `watch` step (mpremote would choose a board of its own) | relay `data.person_action` (press RESET, then unplug and plug in, then `python3 -m mpremote devs` lists the ports). Never deploy again for this | yes |
| `bad_argument` | both scripts | an argument that the script cannot run with (below) | fix the flag, run again | no |
| `crash` | `look.py` | the look crashed: a defect in spark, never in the project. The sentence names the exception class; the traceback is on stderr | report it to the spark maintainers with the stderr traceback; running the look again for it is no use | yes |
| `undeclared_effect` | no script today: the look declares `runs`. An Operation whose `effects` miss what it reaches | the operation ran a program its effects do not declare: a defect in spark | report it, as for `crash` | yes |

`bad_argument`, `crash` and `undeclared_effect` are the core's codes, in `scripts/spark/core/codes.py`: every operation can write them. The codes `not_a_grant`, `bad_minutes`, `bad_scope`, `serial_not_mac` and `no_mac` are in the table of `scripts/board_codes.py` too. They name the reasons of
`grant.py`'s refusals, which do not reach this envelope. With two stops, the deploy gate's `code` is the first stop's.

**A bad flag.** With `--json`, `look.py` and `deploy.py` print an envelope for an argument they cannot run with, such as
`--no-simulation` with `--ignore-older-runs`: status `could-not-run`, `data: null`, one `unchecked` item with `code`
`bad_argument` and the parser's sentence, exit 2. The flag that failed is named only in that sentence: `data` holds nothing, so read
the sentence if you must tell which. The check is the word `--json` in the arguments. `--json=...` and an abbreviation of it
(`--js`) are not that word, so a bad flag beside them gets the usage on stderr and no envelope. Without `--json` they print the usage and the error on stderr and exit 2, as argparse does.

- `look.py` `data`: `port`, `also_on`, `chip`, `flash_mb`, `mac`, `board`, `fields`, `stops`, `warnings`, `unknown`, `verdict`,
  `status`, `token`, `no_token_reason`, `simulation`, `caveats`, `limits`, `last_deploy`. `simulation` is `passed`, or `none` with `--no-simulation`, or
  null when the evidence refuses the image. `also_on` lists the board's other device nodes: rows of `mpremote devs` with one USB serial, USB id and product are one board when one node's name ends with that serial, as macOS names a CP2104 ([P333](https://github.com/xmejkal/spark/issues/427)), and the look uses that node. Relay `also_on` to the person, because two clones can still share a serial. `also_on` is null when `--port` was given, because no node list was read. `caveats` is a list of sentences (P345, what a passed run left out): what the passed runs did not test. `limits` is a list of objects `{component, sentence}`: what no simulation can show of the project, read from the limits section of every passed log, each once (item 9 below). In `--match`, `limits` are plain sentences, here they are objects. `limits: []` never means the project has no limits (item 9). `last_deploy` ([P401](https://github.com/xmejkal/spark/issues/518)) is what spark's store says of this board, read by its MAC: `state`, `why`, `project`, `verdict` and `deployed`, null where absent.
  The state `recorded` holds the newest deploy as stored, so `verdict` is `ready seen` and not `passed`. The state `none-recorded` means the store holds no deploy of this MAC,
  and spark records only its own. The state `not-checked` has a `why`: the MAC was not read, or the record cannot be read. `not-checked` is never "no deploy".
  A stored time with no zone is printed as stored, with "(zone not stored)". The look reads it also when the image is refused. `problems` are the stops and a differing flash (`subject` `stop` or `flash`).
  `unchecked` are the unknown fields, a missing token and a `last_deploy` in state `not-checked`. A look that could not run has `data: null` (or `data.doctor` after a failed read). When there is a
  token, `next` holds a `deploy` step, whatever the status. A warning or an unknown field is not a pass: relay it.
- `deploy.py` `data`: `stage` (`plan`, `look`, `gate`, `flash`, `verify`: the last stage it reached), `dry_run`, `token`,
  `commands`, `look` (the look's `data`), `yes` (`{kind: "typed"|"grant", who}`), `ready` (`verdict`, `sentence`),
  `facts_line`, `image_sha256` (the image on the board, null before a flash, P213), `board_log`, `repl_command`, `store_record` (a path, or null with `store_record_error` beside it),
  `board_state` (`may_be_erased` when a flash command failed), `person_action`, `run_in_terminal`, and `simulation` (`passed`, or `none` with `--no-simulation`: no simulation tested the image, P337). Keys not reached are null,
  and so is `simulation` before a look or when the look refused the image. The caveats of the look are in `data.look.caveats`, its limits in `data.look.limits`, and its last deploy in `data.look.last_deploy`. The erase question names that last deploy.
  If the erase stops with exit 2, deploy.py makes one retry after 5 s and prints `retry in 5 s: ...` on stderr
  ([P290](https://github.com/xmejkal/spark/issues/347)). A retry that worked is a normal deploy, with no extra key.
  When mpremote could not enter the raw REPL for the facts copy (seen right after the reset), the copy and its read-back make one
  retry after 2 s, for each read of the board, and `facts_line` ends with `(written on a retry after: ...)`, or names the first try
  when the retry failed too ([P420](https://github.com/xmejkal/spark/issues/550)). No other copy failure is retried.
- `needs_person: true` on a `next` step means the person must use their hands first. Today it is the `watch` step that follows a start the board never made
  (`download_mode_stayed`; `port_gone` gives no `watch` step) ([P433](https://github.com/xmejkal/spark/issues/575)). The key is on a step only when it is true.
  The board doctor's `fix` and `data.person_action` are text for the person, not steps, so they carry no flag.
- `needs_yes: true` on a `next` step means the person must say yes. **Claude never supplies it.** The token is not the yes,
  and "go ahead" in a chat is not the yes. With no terminal (the exit is 2), `next` holds the `deploy` step to relay and
  `data.run_in_terminal` is the line to give the person word for word (it and the `grant` line start with `SPARK_HOME=<store>` when the run had one, so the new terminal window finds the same MicroPython build and grants); a `grant` step is added when a deploy grant could
  cover it. Never run either one yourself.
- `ready unknown` gives a `watch` step (its `argv` is the REPL command), never a second `deploy`: read the board again. When the person must use their hands
  (`download_mode_stayed`, `port_gone`), `data.person_action` says so, with the RESET place when the board record has it, but only after the wait ran out. So tell the person before you run
  `deploy.py` that an R press may be asked: the run waits for it and its text goes to stderr. A `look.py` that could not read the
  board gives the board doctor's result in `data.doctor` and its next step for the person's hands as the `fix`. A `deploy.py`
  whose look could not read the board does the same. For `close_other`, the step tells the person to leave mpremote's
  console with Ctrl-X, because a console left open holds the port ([P354](https://github.com/xmejkal/spark/issues/452)).
- A missing or stale token gives a `look` step. `--dry-run` never looks: its `next` is the `look` step.

## Deploy without a simulation

For firmware that no simulation can test (P337). Three steps, then the person's yes:

1. `flash_image.py --project <p> --files firmware -o <image>`, where `<image>` is the file the `firmware = ` line of `sim/wokwi.toml` names. A build writes that line as a comment, so until a scenario run writes it, `<image>` is `sim/flash-with-firmware.bin`.
2. `look.py --project <p> --no-simulation --json`. It gives a token only when `firmware/main.py` exists, every `.py` file
   under `firmware/` compiles, no run in `sim/runs/` failed on the image, and the image holds `firmware/` as it is now. The compile runs in one child process for all the files. A source that
   kills the compiler, or one that takes longer than 30 s, is a refusal that names the last file the child began, for example
   "firmware/main.py could not be compiled: the compiler stopped (signal 11)" or "firmware/main.py did not compile in 30 s".
3. `deploy.py --project <p> --no-simulation --token <token>`. The question starts with "no simulation tested this image".

The person types the yes in their own terminal. A deploy grant never answers it, and the `next` step's `why` omits the
grant clause. The facts file, the board log, the store record and `data.simulation` say `none`. Nothing ran the firmware
before the flash, so relay that.
