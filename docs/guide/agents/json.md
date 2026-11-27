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
  in the flags you passed, that check_all found the circuit and the rules, and that no `circuit` line names `dist/` as not written by the last build.
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
| `resolved` | display lines: what `--project` found by convention for the circuit, rules, package and boards, or where it looked. A file named by an explicit flag replaces its line, shown as typed with `(given)`. With no `--project`, it is empty |
| `results[].check` | the check's name; [how it works](../how-it-works.md#the-checks) names its script |
| `results[].what` | what the check claims |
| `results[].status` | `ok`, `problems`, `could-not-run` or `skipped` |
| `results[].problems` | what is wrong |
| `results[].unchecked` | what it could not look at |
| `results[].unmeasured` | advisories and values that need measuring; they do not change the outcome |
| `results[].reason` | why a check was skipped, or why it could not run when an input was ambiguous (two candidates: name one with its flag). Two circuits say "spark handles one board per project today" and name the first one's absolute path for `--circuit`, or one folder per board with its own `parts/` (P223) |

**When a field is absent.** A field with nothing to say may be absent:

- `problems` and `unchecked` are present whenever a check ran.
- A skipped result, and a could-not-run caused by an ambiguous input, carry `reason` instead, and `reason` is then the only explanation.
- `results[].unmeasured` appears only when it is non-empty. The top-level `unmeasured` is always present, as an integer.

**Under problems, read `unchecked` too.** `unchecked` can be non-empty under `problems`. problems outranks could-not-run, both in `status` and in the exit code, so read every `unchecked` list.

**In the text output,** `problems` are the `-` lines, `unchecked` the `!` lines and `unmeasured` the `?` lines.

After a build that did not write `dist/`, a second `circuit` line in `resolved` says the last build, with its time, did not write it (P816).
The requirements files, which buildability and physics also read, are not listed in `resolved`. vendor-truth checks every board definition available, including the library's.

## The other scripts' JSON

Each script's top-level keys, as `tests/test_json_contracts.py` pins them (the test fails when a shape changes). For `compare_design.py`: a rules file that names no rule gives `design`, `checked`, `fix` and `reason` instead of `problems`. The `fix` of `compare_design.py` is the one its refusal's code holds (P935). Its old "not valid JSON" sentence for a broken rules file is now "could not be read". The keys:

| script | top-level keys |
| --- | --- |
| `check_all.py` | `project` (with `--project`), `resolved`, `results`, `status`, `tool`, `unmeasured` |
| `check_physics.py` | `design`, `findings`, `status`, `tool` |
| `check_footprints.py` | `findings`, `status`, `tool`; a refusal: `message`, `status`, `tool`, `code` (P688) |
| `compare_design.py` | `checked`, `design`, `problems`, `status`, `tool`. A missing circuit or rules file gives only `tool`, `status`, `reason` and `fix`. A rules file that cannot be read or is refused, or a circuit that is not JSON, gives `reason` and no `fix` |
| `assign_pins.py` | `assignments`, `board`, `free`, `tool`, `unverified`. **No `status`:** read its exit code |
| `check_vendor_pins.py` | **a bare list**, one entry per board file ([its keys](#check_vendor_pinspy)) |
| `emit_footprint.py` | `check`, `message`, `status` |
| `import_firmware.py` | `modules`, `problems`, `status`, `tool`, `unchecked` ([more](#import_firmwarepy)) |
| `check_spine.py` | `check`, `stages`, `status`, and `kept`, `missing_facts`, `next` and `unserved` when they apply ([its keys](#check_spinepy)) |
| `look.py`, `deploy.py` | the envelope, as `parts.py`'s ([their envelope](#lookpy-and-deploypys-envelope)) |
| `parts.py` | the envelope: `assumptions`, `data`, `envelope`, `next`, `notes`, `op`, `problems`, `status`, `tool`, `truncated`, `unchecked` |
| `flow.py` | the envelope, as `parts.py`'s. `show`'s `data` is one reading of the flow, which `page` draws ([its keys and `page`'s](flow.md)). Wiring: `data.guide.wired` (P1044); places: `.stations` (P1119). `run-request`: [a page request](flow.md#a-page-request), `for` the click id, `keys` the keys it names |
| `bench.py` | the envelope, as `parts.py`'s, with `tool` `bench` and `op` `show-bench`: `data.boards`, one row per board on USB ([its keys](bench.md)) |
### check_spine.py

- `stages` names the stage that stopped it. `check_spine.py --help` lists every stage and the status and code of each way it can end (P852). An `ok` build stage's `detail` can end with a pour short that spark dropped ([P957](https://github.com/xmejkal/spark/issues/1365)). tsci 0.0.2600 can say that a copper pour shorts a trace when the copper does not touch, so the build measures each such short on the circuit's copper. A gap of at least the board's `min_trace_to_pad_edge_clearance` is dropped and named after `0 errors`: `a pour short tsci reported is dropped: pcb_copper_pour_39 and source_trace_1_0 on top are 0.5124 mm apart, at least the board's clearance of 0.1 mm`. Tell the person. A real contact, a short to a pad or a via, and a short that spark cannot measure still stop the build. A stage of a `"board_only": true` design is `skipped`, which is never `ok`; so is the simulation stage of a design whose every part's record skips the simulation (P778), and such a build is not noted in the store. Each entry of `stages` has `name`, `status` and `detail`, and an entry that does not end `ok` also has `code`, the word to decide on, never the detail (P701; the PO, 2026-11-20: "Every stage with a code", [P936](https://github.com/xmejkal/spark/issues/1332)). The four skipped stages of a `board_only` design have the code `board_only`, and the skipped simulation stage of a design whose every part is skipped has `every_part_skipped`. A skip is never a problem: the build's status stays `ok`. `parts.py --requirements` writes `board_only` when the board serves every need and no part is listed, and removes it when a part is listed.
- `kept`, with `--keep` or `--sim-dir`, lists each file: `file` as typed to `--keep`, `did` (`wrote`, `replaced`, `unchanged`, `left alone`,
  `removed`, `not written`, `not kept`, `traces differ` or `traces not compared`, for a file that cannot be read or holds a trace spark does not read) and `why`. A `replaced` entry has `previous`, the path of the previous version, and a `.tsx` entry that spark wrote, replaced or found unchanged has `sha256`. In a project folder, it lists `.spark/build.json`, the record of the build that [`flow.py`](flow.md) reads (P825), for the reference design too, with `requirements: null` (P1095). The build also keeps tscircuit's schematic and PCB as `dist/board/schematic.svg` and `dist/board/pcb.svg` (P828, #1186): they have no entry of their own, because the `dist` entry covers them, and an export that gave nothing, a board-only build, or a build that wrote its own `dist/` but did not finish, removes the earlier file (the `page.html` entry says why a picture is not drawn). A file that cannot be written or removed is one `not kept` entry that names it, and the build goes on. A `dist/` copy that fails is its own `not kept` entry for `dist`, the only entry for `dist`, and the `.tsx` entries stand (P891); the copy is staged beside `dist/`, so the earlier `dist/` stays whole, and `dist_written` is false (P1088). An earlier `dist/` set aside at `dist.old` that cannot be removed after the copy is a `not kept` entry for `dist.old`, spark's own: delete it before the next build. After a build that did not finish (a refused requirements file, a stage that stopped, or a build stage that kept no `dist/` of its own), an earlier `dist/` stays, with its pictures: one `left alone` entry for `dist` says why, and in a project `.spark/build.json` holds `dist_written: false`. An earlier sheet and its drawings stay too, each a `left alone` entry whose `why` ends "so it is an earlier build's" (P1093). A build that ends `problems` replaces `dist/` whole with its own, as a finished one does (P1088). A board-only build removes an earlier `dist/` (P236). Tell the person that every check reads that earlier board (P816). A keep folder that is no project keeps and removes none of them. A `traces differ` entry follows the `left alone` entry of a `.tsx` whose traces join other pins than this build's board (P660). Its `only_in_kept` and `only_in_build` list each trace as `A to B`. It never changes `status`: tell the person not to wire or build from that file. When the sheet is written, a drawing's `not written` entry has `code`
  (P691: never `null`; [the codes](breadboard-codes.md)), `subject` and `expected` (`true`: by design or not drawn yet; do not retry; for
  `not_drawn_yet`, tell the person to wire it by hand from the sheet's steps). For `no_drawing_fact` of a part, it also has `record`, the part's id, and `fix` (P945). When the build finished and the sheet was not written, its entry has `code` (P701). A `wrote` entry for `breadboard.svg` may have `drawn_from` (`record`), and the one for `breadboard.md` `since` (P875): an ISO time with its offset, the time of the sheet its `changed` entries count from.
- `next`: first one `research` step per `record` of a `no_drawing_fact` entry (`--part <id>`, and `--project` in a project; P945), then one look step, only for `ok` in a project; its `why` is `first write firmware/main.py from pins.py` (P517), the pin map that `--keep` writes. With `--keep` and an `ok` build, the steps that `flow.py show` names now come after these ([P1035](https://github.com/xmejkal/spark/issues/1518)). The flat line holds no `notes`: after a kept build with no requirements file, the note that `page.html` was written again is only in the text. `next` is the last key, after `kept` and `missing_facts`.
- `unserved` is there when the requirements file carries the note `parts.py --requirements` writes for the needs it leaves off the board.
- `missing_facts` is a top-level list, with `--keep` only, when spark writes `firmware/pins.py` and the board record
  lacks the level of its onboard LED or button ([P464](https://github.com/xmejkal/spark/issues/632)). The `wrote` entry
  for `firmware/pins.py` in `kept` has the same list. A build without `--keep`, or a `pins.py` spark left alone, gives
  no missing-fact signal yet ([rows](../../observations/rows/p464-missing-facts.md) 1 and 2).
  - Each item is `{subject, code, sentence, fix}` with the code `missing_fact` and a subject such as
    `pin_roles.onboard_led.active_level`. It never changes `status`, so `ok` does not mean the firmware has every fact.
  - Never guess the level. Ask the person (see `/spark:build`), or use `/spark:research` or a bench measure. Write the answer with `parts.py --fact-set <board> FILE --project <the project's folder>` (a board only another listed project holds is refused with `other_project_record`), and build again.
- The simulation line warns "no serial monitor is wired in the diagram" when the diagram has no `$serialMonitor` wires
  and the board's record lacks `serial_without_wires: true` ([P468](https://github.com/xmejkal/spark/issues/636)).
  spark's XIAO ESP32-C6 and FireBeetle 2 records carry it, so they get no warning. Read the warning as a possible silent
  `wait-serial`, not a failure.
- Refusals and crashes. Each stage that could not run shows as `[????] <stage>` with its sentence, then
  `the chain was NOT exercised — this is not a pass`, exit 2.
  - A crash of spark itself (not a stage) prints nothing on stdout and exits 2. stderr gets the build's own lines, such
    as the history line ([P840](https://github.com/xmejkal/spark/issues/1204)), before `build-board: crashed, <class>`.
  - The board emitter's refusal of a board that states no `power.io_volts` shows as `[????] schematic` with that sentence
    ([P121](https://github.com/xmejkal/spark/issues/55)).
  - A crash inside the board emitter (`spark/design/board_emitter.py`, called in process) is could-not-run
    too: the `schematic` stage's detail is `the board emitter crashed: <Type>: <message>`.
  - A crash in the footprint drawing reads `the footprint emitter crashed: <Type>: <message>`, such as
    `the footprint emitter crashed: RuntimeError: boom`. Such a detail is a crash, not a defect in the design.
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
    [P438](https://github.com/xmejkal/spark/issues/583)). A `.spark/rules.json` that is a folder is refused under `schematic`.

### import_firmware.py

- Each item of `modules` has `module`, `status` (`imported`, `raised` or `timed out`) and `detail`. One not imported also has `code`, `import_failed` or `import_timeout`: decide on it, never on `detail` ([the firmware codes](firmware-codes.md)).
- A project with no `firmware/` folder is `could-not-run`.
- A project with nothing to import but `main.py`, `boot.py` and `pins.py` is `problems`. Its firmware cannot be imported
  without running `main.py`.

### check_vendor_pins.py

- The answer is a bare list, one entry per board file.
- A compared board has `board`, `compared`, `not_recorded`, `problems`, `source` and `status`.
- A could-not-run has `board`, `status`, `reason` and `code` (the word to decide on, P688; a file that is not there is `board_file_missing`).
- A run without `--offline` that kept a header adds `wrote`, the whole path of that file, even on a could-not-run whose
  header held no pins. A live run refused before or during the fetch has none.
- `source` is `<repo> variants/<variant>/pins_arduino.h` live, and `the project's cache (<name>)` or `spark's cache (<name>)` with `--offline`.
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

- `problems` and `unchecked` hold items `{subject, sentence, fix}`; an `unchecked` item has no `subject`. `fix` says what to do, and may be null. The items of every operation carry `code` too (P726; a payload file that is not JSON is `input_unreadable`, whose fix since P935 says to make the file or the stdin that the sentence names hold JSON, then run again): the word to decide on, null where the refusal has none yet; `--validate`'s items carry `part_contract_broken`; their `fix` is null, so the code is what an agent decides on. A refusal of theirs with no text lines also says its sentence on stderr, with `--json` too.
- `assumptions` is what an answer rests on that nobody has checked. It never changes the status, so read it whenever it
  is not empty. Each entry says what it is about (`fact`), why nobody has checked it (`basis`) and what depends on it (`sentence`).
  - `--unverified` lists one per fact whose `verified` is not true: `fact` is `<part>.<fact>`, `basis` is `unverified`,
    `assumed` is the value taken for now, `source` is where it came from, and `write` is the key a result goes back to
    with `--fact-set`: `facts.<name>`, `pin_order_proof`, `body_mm`, `own_socket` or `physical_proof` (it vouches for `physical`, a
    module's thickness, holes and header; a key the vendor did not publish is in its `not_published`). A guessed outline
    is listed with its width and height as `assumed`; a skeleton outline with nulls, never a value to copy back.
    `read_by` lists who reads the fact (`data/fact-needs.json`):
    each reader's `consumer`, `status` (`reads` today, or `will read`) and `card` (what makes it read, null for `reads`).
    A `write` of null means the record's `facts` is no object: repair the file by hand. `next` holds one `--fact-set <part>
    <file>` step, for the first part with a `write` key; with no such row it is empty. The text ends with the same `next:` line.
  - `--show` lists a CONFLICT that rests on an unverified fact: `fact` is `<part>.<pin>`, `basis` is `unmeasured`,
    `rests_on` names the facts to verify as `<part>.<fact>`, and `upgrade` says how. This `unmeasured` is a basis, not `check_all`'s `unmeasured[]` list.
- A **CONFLICT** is a pull the board adds that the module's own pull overrules, said with its arithmetic. When every fact
  it rests on is verified, `--show` lists it under `problems`, with a `fix`, and exits 1; `data.record` is there
  whatever the exit. Say it to the person. Never clear it by marking a fact unverified ([P124](https://github.com/xmejkal/spark/issues/58)).
- `notes` are said and never fail, each `{subject, sentence}`. `subject` is null when a note names nothing. A pick's notes are here, with `{"subject": "page.html", "sentence": "wrote page.html again: /spark:page publishes it"}` when it wrote the project's page again (P1035). `--requirements` has notes with a null `subject` ([P1139](https://github.com/xmejkal/spark/issues/1674)): one note `kept, not from a pick: <entries>` for the entries that no pick explains and spark did not write, and one note `written for a pick that is gone: <entry> (need <need>)` for each entry spark wrote for a pick that is gone. Each gone note repeats one item of `data.unexplained`, so count the entries from `data.unexplained`, not from the notes. After a `false` reply, those entries are in the `kept as yours` line only, and the next run notes them as kept. Here is also the note of `--needs-drop` that requirements.json still lists the part of the dropped need (`data` has `dropped`, `released` and `written`; a missing need is a `problems` item with its ids in `data.needs`). `parts.py --needs-set` has `data.changes`, `data.written` and `data.basis_noted` ([P1027](https://github.com/xmejkal/spark/issues/1506)). `basis_noted` is true when the run wrote `.spark/needs-basis.json`, the sha256 of the brief's goal and must lines. That happens on a write that defines a need (`does`, `what` or `condition`) or a review (`[]`), when the needs are not empty, the brief has a goal and the record differs. A dry run is false and its text says `would note`. `parts.py --move-hold FROM TO NEED=ID` ([P1124](https://github.com/xmejkal/spark/issues/1654)) has `data.from_project`, `data.to_project`, `data.need`, `data.pick` (`{kind: id}`, or null when FROM has no such part), `data.released` (FROM's holds let go, each `{entry, was, now}`), `data.written` (true only when the whole move finished: false without `--apply`, and false after a stop, when a `move_unwritten` finding means the drawer and TO's pick may already be written and the same move with `--apply` finishes it) and `data.projects`, FROM then TO, each `{project, needs_without_pick, released, out_of_date}`: the ids of the needs the move leaves with no pick, the holds it lets go, and the phases it makes out of date (`requirements`, `build`, `breadboard` when the project has requirements.json, else none). Without `--apply` its next step is the same move with `--apply` and `needs_person: true`. Its refusals are `problems` with nothing written: `move_same_project`, `move_not_picked`, `move_already_picked` (TO's need picks the part already while FROM still holds it), `move_part_of_count`, or TO's pick's own problem as `--pick` words it. `move_unreadable` is could-not-run with nothing written (a file read before the first write, or the store's lock). `move_unwritten` is could-not-run, and the same move again finishes it.
- `parts.py --requirements` has `data.placeholder_outline` and `data.no_simulation_stance` (the picks written though their records owe their outline or their `simulation`, [P996](https://github.com/xmejkal/spark/issues/1453)), and `data.unexplained` (`[{part, name, need, code}]`, code `entry_pick_gone`: an entry spark wrote for a pick that is gone), `data.remove_key` (the reply key for removing them, else null) and `data.previous` (the previous version's path, after a yes, else null). A `next` step says how to give the yes ([replies.md](replies.md#the-requirements-yes)). After a `false` the run says `kept as yours`, and both are empty. `--drawer-set`'s `data.shelved` and `data.not_shelved` name each part record or board file that a new link put, or could not put, onto the store's shelf ([P989](https://github.com/xmejkal/spark/issues/1442)).
- `--keep` answers `data` with `document` (the `documents` entry of the kept copy), `location_removed` (the file's bytes are a JPEG, whatever its name, and its EXIF GPS was removed), `written` (the file was kept: false on a dry run), `record` (the part id given with `--part`, else null) and `key` (its `documents` key: the new one, or the one that already lists the same bytes; null without `--part`). A part with no record (`no_such_part`), a record only another listed project holds (`other_project_record`), spark's own library and a `documents` that is no object are `problems` on the part id, and nothing is kept; a record that is not JSON is one too (`part_contract_broken`). A kept file replaces a `kept: false` entry of its URL under that entry's key and title. Its lines (the key to cite, `already listed`, no record) are on stderr, so the text stays the entry's JSON ([P784](https://github.com/xmejkal/spark/issues/1082)).
- **A record of spark's own library** is a `problems` item on its id with `library_record` (exit 1, P964), and nothing is written or downloaded, for `--fact-set`, `--function-set`, `--keep --part`, `--keep-picture`, `--features-set`, `--find-documents` and `--fetch` (the dry run too). Its `fix` says to copy the record into the project's `parts/` (a board into `boards/`) and run again with `--project`. `research.py` says `library_record` for the same fact, as an `unchecked` item of a refused run (exit 2) with the same `fix` (P982).
- **A record only another project on the person's list holds** is a `problems` item on its id with `other_project_record` (exit 1, [P987](https://github.com/xmejkal/spark/issues/1439)), and nothing is written or downloaded, for the same seven writers: `--fact-set`, `--function-set`, `--keep --part`, `--keep-picture`, `--features-set`, `--find-documents` and `--fetch` (the dry run too). A writer changes only the project the run names with `--project`, or the project a shelf copy came from, or, for a copy that names none (shelved while its folder was on no list), the one listed project that holds the same part (its name and kind) under its id when no catalog record has it ([P1006](https://github.com/xmejkal/spark/issues/1465)). Listing a folder (`--step`, `--pick`, `/spark:init`) adopts such copies of its records, and `data.adopted` of `--step` and `--pick` names their ids (a dry run names those it would adopt). Its sentence names that project and its folder. Its `fix` names the folder too: run the same command again with `--project <that folder>`, or copy the record into the `parts/` (a board into `boards/`) of the project you work on and name that project with `--project`. Readers (`--offer`, `--need`, `--match`, `--audit`) still read every listed project.
- `--keep-picture` ([P946](https://github.com/xmejkal/spark/issues/1349)) answers `data` with `record` (the part id), `key` (the `documents` key of the picture's file), `view` (`breadboard-top`), `picture` (the block written to `pictures.<view>`: `document`, `made_by`, `likeness`, `credit`, `verified`), `document` (the `documents` entry) and `written` (false on a dry run). Each rule the picture breaks is a problem whose `subject` is the element and whose `code` is a `picture_` code ([the codes](breadboard-codes.md)); a part with no record of its own (`no_such_part`), a record only another listed project holds (`other_project_record`), spark's library and a record with no frame are problems on the part id, and nothing is kept. Its sibling `--features-set` ([P956](https://github.com/xmejkal/spark/issues/1362)) answers `data` with `record` (the board id), `features` (each feature as the record now holds it: `name`, `kind`, `x`, `y`, `w`, `h` in mm in the board's frame, `colour`, `text`, `leads` or `count` where the kind has one, `verified` false and `source`), `anchors` (`[{pad, x, y, off_mm}]`: where each anchor landed in mm and how far it lies from its pad in the record), `colour` (the `physical.colour` written, or null) and `written` (false on a dry run). Each rule a feature breaks is a problem whose `subject` is the feature's name (or the anchor's pad) and whose `code` is a `feature_` code ([the codes](breadboard-codes.md#a-boards-measured-features)); a file that cannot be read is `feature_unreadable` on the file. A part's record, a board nobody has (`no_such_part`), a board or part only another listed project holds (`other_project_record`), spark's library and a board with no frame are problems on the id, and nothing is written.
- `--find-documents` ([P952](https://github.com/xmejkal/spark/issues/1358)) answers `data` with `record` (the board id), `page` (the maker's page it read, or would read on a dry run), `top_view` and `drawing` (each `{key, url, sha256, kept, new}`: its `documents` key, `kept` false for a file the store does not keep, such as a zip, and `new` true when this run listed it; null when none was kept), `declines` (`[{maker, reason, missing}]`), `fetched` (the files this run downloaded: empty once both are kept) and `written` (the record changed). A page with no "Board Overview" picture is a problem with `no_top_view`, one that lists no "Dimension" document `no_dimension_drawing`, a board whose `vendor` and `sources` name no DFRobot page `no_vendor_finder`, and one with no `sku` `no_sku`; with no top view, `next` is the photo step. A page or a file that does not answer is `unchecked` with `url_unreachable`, and nothing is written for it. A part's record, a board nobody has (`no_such_part`), a board or part only another listed project holds (`other_project_record`) and spark's library are problems on the id, and nothing is fetched.
- `--picture-frame` answers `data` with `svg` (the frame's text, also the whole text output), `view_box` (`[0, 0, W, H]` in mm), `made_by` (`frame`) and `likeness` (`rough`). A record with no frame is a problem on its id that names the field it lacks.
- `next` holds the steps an agent may take, each `{op, argv, why, effects, needs_yes}` with `needs_person` and `env` only when they apply. `truncated.next` is the step for the rest of a long answer. `flow.py show`'s `next` holds the step of the offer to take now, or, at the simulate and the deploy, the step of that phase ([the next step](flow.md#the-next-step), P1034). There an empty `next` means: read `data.guide.now`, and an empty `next` with a `null` `now` means nothing is waiting: the deploy is `ok`, and `data.guide.no_open_phase` says so (P1043). An op in the form of a script's name (`run_scenario`) is `scripts/<op>.py`, a script not on the core yet. After an `ok` run that wrote to a project (`parts.py --pick`, `check_spine.py --keep`), `next` lists the command's own steps, then the steps `flow.py show` names now (P1035).
- `env` on a `next` step is an object of variables to set when you run it, there only when the run had `SPARK_HOME` set (a store found through `XDG_DATA_HOME` gives none, so set `SPARK_HOME` to pass it on) ([P473](https://github.com/xmejkal/spark/issues/647)). Today it is `{"SPARK_HOME": "<whole path>"}`, so a fresh environment (Claude Code's Bash, an MCP or LangGraph caller) sees the same drawer, downloads and grants. The `look`, `deploy` and `grant` steps and the steps of `parts.py` and `flow.py show` carry it. `watch` has none, because mpremote reads no store.
- In text, every item's fix and every next step is printed under the answer's lines, and a CONFLICT on unverified facts starts with `?`.

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

These take it: `assign_pins.py`, `bench.py`, `check_all.py`, `check_footprints.py`, `check_physics.py`, `boards.py` (with `--list`: `data.boards` rows of `id`, `layer`, `active` and `stops_why`. `active` marks the project's board: the board requirements.json names, else the selection in boards/active.json. A requirements.json or a boards/active.json that cannot be read (`record_file_broken`) marks no board, and `notes` says why. A missing selection or one that names no board marks none in silence), `check_spine.py`, `check_vendor_pins.py`, `compare_design.py`, `emit_footprint.py`, `deploy.py`, `flow.py`, `grant.py` (with `--check`), `import_firmware.py`, `live.py`, `look.py`, `parts.py` and `research.py` (its `data.open` and `needs_reply` are in [replies.md](replies.md)). `grant.py`, `live.py` and `reach.py` print one flat line of JSON, not the envelope (P657): the keys of `data` below and `fix` (P1055), and no line at all after a crash or a reach that could not start, but for reach's open board question (`reached` false, `port`, `product`, `open`, `known_board`, `fix`, P892). `check_spine.py` (one flat line) and `check_all.py` (one indented document) print no line after a crash either (P804). A bad argument with `--json` prints the usage on stderr, exit 2. These do not take
it: `boards.py` (but `--list`), `breadboard.py`, `check_bom.py`, `emit_board.py`, `flash_image.py`, `init_project.py`, `run_scenario.py` and `tools.py`. `tools.py --status` taking `--json` is not built yet ([P92](https://github.com/xmejkal/spark/issues/23)).

### What the text output shows

P423 and P430 set these rules for the text output of `parts.py`, `look.py`, `deploy.py`, `check_spine.py`, `run_scenario.py`, `grant.py`, `live.py` and `reach.py`:

- Guarded: a character that a terminal does not print, such as a control character or a right-to-left override, shows as `?`. A text's own line breaks stay. A value that can hold a line break of its own (a port, a project path, a button word of a board record) is put on one line first, so it cannot fake a line. This holds for the question that `deploy.py` asks you to type yes to, and for the sentence `grant.py` gives when it has no terminal to ask in (it holds the line to run, with your project path and port). A tools file is refused when a tool's name, or a name in its `needs`, holds a character that `str.isprintable` rejects: a control character or a bidi mark, and also a tab, a zero-width joiner (U+200D) or a no-break space (U+00A0), which an older spark let through. The `rm` path that `grant.py` prints after a deploy grant may show `?`: copy it from the store, not from the screen.
- Flat messages (P444, P445): a value that an error message holds (a store path, a record's name, a URL) is put on one line by the error class that builds the message (`ValueMessageError`), so a newline in it cannot fake a line of spark's own, in the text and in `--json` alike. This holds for every raise of every class that inherits `ValueMessageError`, and for the scripts that print their errors (`look.py`, `grant.py`, `live.py`, `reach.py`, `deploy.py`) and the lines `tools.py` prints about a folder. The V1 baseline is empty. An error class that does not inherit from `ValueMessageError` is outside this. The `reason` or `code` of a stop names why; key on it and never on the sentence. The raw values stay on the exception for a later field. A lone surrogate character in a text is cleaned to a space, and in a key it is refused, with or without `--dry-run`.
- Raw: `--json` carries the raw text of the other fields, so decide on the JSON and not on the screen (`check_spine.py --json` holds the raw text of a crash). `run_scenario.py` has no `--json`, and its log file in `sim/runs/` keeps the raw text. Two paths print raw text: the flash tool that `deploy.py` runs writes its own output to the terminal, and `emit_footprint.py` prints its own messages.
- Masked (P677): the bench scripts (`look.py`, `deploy.py`, `grant.py`, `live.py`, `reach.py`, `bench.py`) mask what they print, in
  the text and in `--json`. The project folder is `<project>` and a path in it is relative; a path in the store starts
  with `<store>` (the store as `store.home()` finds it: SPARK_HOME, else XDG_DATA_HOME/spark, else ~/.local/share/spark),
  as `store_record` shows; any other path under your home starts with `~/`; a tools list's `account_env` value is `***`.
  A path to open or run keeps its real form: `data.run_in_terminal`, `data.board_log`, `data.commands`,
  `data.repl_command`, each `next` step's `argv` and `env`, grant.py's `rm` line, an item whose code is in
  `board_codes.PASTED_CODES` and every line that holds its sentence. Tokens are masked there too. Any other path to
  open: rebuild it from the store as `store.home()` finds it. deploy.py's yes question is masked too.
- Exact reply: in the text of `live.py` a tab in the board's reply shows as `?`, so read `output` from `--json` for the exact reply.

## look.py and deploy.py's envelope

`look.py --json` and `deploy.py --json` ([P213](https://github.com/xmejkal/spark/issues/192)) print one `outcomes.envelope` (`envelope`,
`tool`, `op`, `status`, `data`, `problems`, `unchecked`, `next`, `truncated`, and `notes` for deploy, with the `page.html` note when it wrote the page again, P1069) on stdout. The status is
the exit code's ([the outcomes](../agents.md#the-outcomes-and-their-exit-codes)). With `--json`, deploy.py prints every line a person reads, and
the flash tool's own output, on **stderr**, so stdout holds the envelope alone. That includes the `why:` line of each stage ([P476](https://github.com/xmejkal/spark/issues/652)), and no stage heading or status line is printed (P478). A bad flag prints an envelope with `--json` (below).
A crash in `look.py` or `deploy.py` prints an envelope with one `unchecked` item, code `crash`, and exits 2; stderr gets `<tool>: crashed, <class>`, the fix and the traceback, never the envelope. A `DeployError` or a `ToolError` raised in deploy's verify, after the flash, is such a crash too (exit 2, `data.board_state` set), where it once printed a traceback with exit 1.
Without `--json` it prints the same on stderr and nothing on stdout ([P442](https://github.com/xmejkal/spark/issues/587)).

**The `code` of an item** ([P433](https://github.com/xmejkal/spark/issues/575)). Every item of `problems` and `unchecked` in
`look.py --json` and `deploy.py --json` has `code`, the cause in one word. Decide on the code, never on the sentence. The codes
come from one table, `scripts/spark/bench/board_codes.py`. The look and deploy.py share a code (`evidence_refuses`).
The flat line of `grant.py`, `live.py` and `reach.py` has no `code`; their Findings do. Each line has `fix`: the fix of its first Finding that has one, the words of the text's fix line. Relay it word for word and never parse it (P1055). null means that spark has no fix, not that nothing is wrong: read the line's other keys and `doctor`, and never fill it in. In deploy.py, the reasons of a look that could not run come as an `unchecked` item of stage `look`.
look.py gives each stop, warning and unknown field an item of its own. deploy.py's gate gives one item for all the look's stops, with the first stop's `code`.
The column "needs the person" says whether the next step waits on the person's hands, yes or choice.

| code | where | means | next step | needs the person |
|---|---|---|---|---|
| `list_failed`, `list_timeout` | a look that could not run | mpremote could not list the boards on USB, or took too long | check mpremote (`/spark:setup`), reconnect, run look.py again | yes |
| `no_port` | a look, a deploy's look, a grant, a live try, a reach or a `bench.py record` that could not run: relay the `fix` in each | no board is on USB | ask the person to plug it in with a data cable. With a deepsleep call in firmware/, relay the `fix`: it says that the board can be in deep sleep, and what to try in order ([P1022](https://github.com/xmejkal/spark/issues/1490), [P1049](https://github.com/xmejkal/spark/issues/1539)) | yes |
| `port_not_listed` | a grant, a live try, a reach or a `bench.py record` that could not run | the port `--port` names is not in the list, or in live.py the port that spark found left before the second list | ask which board, or drop `--port`. With a deepsleep call in firmware/, relay the `fix` in each script. The port spark found gets its own opening, after the doctor too: in `board_not_read` and on the exec roads of live and reach ([P1057](https://github.com/xmejkal/spark/issues/1554)) | yes |
| `two_boards` | a look that could not run | two or more boards are on USB and no `--port` says which | ask which board, run again with `--port` | yes |
| `flasher_not_esptool` | a look that could not run | the look reads with esptool only, and the project's flasher is another tool | stop and tell the person | yes |
| `board_not_read`, `read_timeout` | a look that could not run | esptool could not read the board, or took too long. `data.doctor` has the board doctor's result | relay the `fix` (the person's hands), then run look.py again. A port off USB, named or found by spark, with deepsleep in firmware/: the `fix` is the asleep fix, `next_step` stays `plug_in` ([P1049](https://github.com/xmejkal/spark/issues/1539)) | yes |
| `no_board_named`, `no_board_record` | a look that could not run | `requirements.json` names no board, or the project has no record of the board it names | name a board, or `/spark:research` for a record | yes |
| `tool_missing` | a look (could not run, or no token), a deploy (stage `plan`: mpremote, esptool, which is also refused when older than the oldest version spark runs, the MicroPython build or littlefs that the image check needs, [P436](https://github.com/xmejkal/spark/issues/580)) | a tool the step needs is missing, too old, or cannot be used. The sentence says what to install or fix: an install line, a tools file to repair, or a URL for a MicroPython build no tool holds | the person runs `/spark:setup`. Do not run an install line yourself. If the sentence names nothing to install, relay it to the person | yes |
| `chip_differs`, `flash_too_small` | `problems`, subject `stop` | the chip is not the record's, or the flash is smaller than the image. deploy.py will refuse | stop, tell the person | yes |
| `flash_differs` | `problems`, subject `flash` | the flash size is not one the record lists | relay it; deploy.py asks the person to accept it | yes |
| `field_unknown` | `unchecked` | the board or the record did not say a field | relay it; deploy.py asks the person to accept it | yes |
| `missing_fact` | top-level `missing_facts` of `check_spine.py --json` ([its keys](#check_spinepy)), never in `unchecked` | a stage needs a fact the board record lacks, such as the active level of the onboard LED or button. The build stays `ok`. The `fix` names the three ways | ask the person, or `/spark:research`, or a bench measure; write it, then build again ([how](#check_spinepy)). Never guess it | yes |
| `stop_found` | `unchecked` | the look found a stop, so it gave no token. The stop is its own item | as for the stop | yes |
| `no_mac` | `unchecked`, deploy stage `gate` | the board's MAC could not be read, so the look gave no token. `grant.py` refuses with it too | reconnect the board, run look.py again | yes |
| `evidence_refuses` | `unchecked` of a look, deploy stage `plan` | the evidence refuses the image: no passed run names it, a run tested another image, or another check failed. The sentence names the way out, or the no-simulation way | run a scenario, or what the sentence names (or the no-simulation way it names), then look.py again | no |
| `last_deploy_not_checked`, `known_board_unreadable` | `unchecked` | spark's record of the board's last deploy, or of the board kept for the project (P865), could not be read | relay the `fix` (repair the record), run look.py again | yes |
| `no_terminal` | deploy, stage `gate` | there is no terminal for the person's yes. `data.run_in_terminal` is the line. It starts with `SPARK_HOME=<store>` when the run had one | give the person the line, word for word | yes |
| `token_missing`, `token_stale` | deploy, stage `gate` | deploy.py got no token, so no look came before it (missing), or the board or the image is not the one the token names (stale) | run look.py (again), then deploy.py with its new token | no |
| `answered_no` | deploy, stage `gate`, a look (nothing read), or the board question of grant, reach and live (nothing touched, P892) | the person answered no | stop | yes |
| `relayed_yes_refused` | deploy, stage `gate` (exit 2), or grant (exit 1) | a yes that another program collected cannot open the erase or make a deploy grant ([P675](https://github.com/xmejkal/spark/issues/905)). `data.yes` stays null | give the person `data.run_in_terminal` (deploy) or the `grant.py --scope deploy` line as printed, and say that they type the yes in their own terminal. Never retry and never supply a yes | yes |
| `direct_flashing_disallowed` | grant (exit 1) | the store holds the file `grants/direct_flashing_disallowed`, so `grant.py --no-simulation` gives no grant, and no deploy grant answers a `--no-simulation` deploy ([P1029](https://github.com/xmejkal/spark/issues/1509)) | relay it. Only the person deletes that file. Never write, change or delete a file in the grants folder | yes |
| `grant_ended` | deploy, stage `gate` or `flash` | the deploy grant ended before the erase. At stage `flash`, `board_state` is `may_be_erased` | ask the person for a new grant or a typed yes. At stage `flash`, tell the person the board may be erased | yes |
| `no_sim_toml` | deploy, stage `plan` or a look | the project has no `sim/wokwi.toml`. Never with `--no-simulation`: the image is then `sim/flash-with-firmware.bin` ([P1001](https://github.com/xmejkal/spark/issues/1459)) | build first (`/spark:build --keep`) | no |
| `firmware_line_bad` | deploy, stage `plan` or a look | the firmware line of `sim/wokwi.toml` cannot be read, or names an image outside `sim/` | fix the line as the sentence says, build again | no |
| `no_image` | deploy, stage `plan` or a look | the image that `sim/wokwi.toml` names is not there yet (a build writes the `firmware = ` line as a comment, so until a run writes it the image is `sim/flash-with-firmware.bin`) | run a scenario, or the no-simulation way the sentence names | no |
| `log_unreadable` | deploy, stage `plan` or a look | a run log in `sim/runs/` cannot be read | repair or remove the log, run look.py again | yes |
| `chip_unknown` | deploy, stage `plan` | the chip of the project's board record cannot be read | fix the board in `requirements.json` | no |
| `image_changed` | deploy, stage `gate` | the image changed after the person's yes | run look.py again | no |
| `flash_failed` | deploy, stage `flash` | a flash command failed. `data.board_state` is `may_be_erased`, and a board log with the verdict `flash not finished` (`data.board_log`, P1092) | relay the sentence (it names the BOOT and RESET places) | yes |
| `ready_not_seen` | deploy, stage `verify` | the board's files differ from the image, the firmware stopped with an error, or it printed no `ready`. The sentence tells which | fix the firmware, then look.py and a new yes | yes |
| `ready_unknown` | deploy, stage `verify` | the board could not be read after the flash, or the passed run's log names no files. The sentence tells which | relay the `fix` as printed: what spark knows, what it did not do, what to try ([P1022](https://github.com/xmejkal/spark/issues/1490)). It names the deepsleep calls, and on a C6 a BOOT entry. Then the `next` steps in order: `look`, `live`, `watch` | `live`, and `watch` when the board did not answer |
| `download_mode_stayed` | deploy, stage `verify` | the board still waits in download mode after the flash: the wait for its start ran out, though the port may have gone and come back. A restart counts only when mpremote answers after it ([P462](https://github.com/xmejkal/spark/issues/630)) | relay `data.person_action` (press RESET once) to the person, then run the `watch` step. Never deploy again for this | yes |
| `port_gone` | deploy, stage `verify` | the board's port was not listed after the flash, or went and did not come back. No mpremote call was made on a dead port, so `data.repl_command` is null and `next` has no `watch` step (mpremote would choose a board of its own) | relay `data.person_action` (press RESET, then unplug and plug in, then `python3 -m mpremote devs` lists the ports). Never deploy again for this | yes |
| `bad_argument` | both scripts | an argument that the script cannot run with (below) | fix the flag, run again | no |
| `crash` | `look.py`, `deploy.py` | the look crashed (`grant.py`, `live.py` and `reach.py` print no stdout line for a crash, exit 2, the traceback on stderr): a defect in spark, never in the project. The sentence names the exception class; the traceback is on stderr | report it to the spark maintainers with the stderr traceback; running the look again for it is no use | yes |
| `cannot_tell_board` | the bench's show, `unchecked`, its subject the port | spark cannot tell the board by its USB serial (it shows none, one its firmware set, or a bridge's that no project keeps), so it read none of that board's deploys and its deploy grant | run look.py in the project that uses the board: it reads the board and keeps it | yes |
| `undeclared_effect` | no script today: the look declares `runs`. An Operation whose `effects` miss what it reaches | the operation ran a program its effects do not declare: a defect in spark | report it, as for `crash` | yes |

`bad_argument`, `crash`, `undeclared_effect` and `input_unreadable` (a payload file or stdin that is not readable JSON, P726; its fix, since P935, fits either) are the core's codes, in `scripts/spark/core/codes.py`: every operation can write them. So are `needs_reply`, `unknown_reply` and `bad_reply`, the codes of [open questions and replies](replies.md) (P737); the look asks one `person` question before it reads a board, and stops with `other_board` (`unchecked`, both boards as `MAC ends 34:56`) when the board on USB is not the one kept for the project ([the look's question](replies.md#the-looks-question), P865), and `grant.py`, `reach.py` and `live.py` ask it before they touch the board ([their question](replies.md#the-question-of-the-grant-reach-and-live), P892); that page also holds `research.py`'s own codes (`no_sku`, `no_document_list`, `more_documents`, and the store's `url_unreachable` when the wiki page does not answer). The codes `not_a_grant`, `bad_minutes`, `bad_scope`, `serial_not_mac`, `no_mac` and `direct_flashing_disallowed` are in `scripts/spark/bench/board_codes.py` too. They name the reasons of
`grant.py`'s refusals, which do not reach the envelope of the look or the deploy. So do `no_grant`, `grant_expired`, `grant_no_zone`, `not_reached`, `no_probe`, `reset_failed`, `raised`, `refused_no_grant`, `refused_pin`, `refused_no_parse`, `store_problem`, `board_record_unusable`, `known_board_unreadable` and the board question's `other_board`, `no_known_board`, `needs_reply` and `answered_no`: the codes of the findings that `grant.py`, `live.py` and `reach.py` give the core, which print no envelope. `bench.py show` prints an envelope, and its `unchecked` items can hold `not_a_grant`, `known_board_unreadable`, `last_deploy_not_checked` and `cannot_tell_board` ([its keys](bench.md)). With two stops, the deploy gate's `code` is the first stop's. The board log's reason line (P1043) holds the cause of a deploy that did not see ready: `files_unread`, `firmware_not_started`, `no_files_named`, `board_lost`, `files_differ`, `firmware_error`, `no_ready_line`, `port_gone` or `download_mode_stayed`, and the cause of a flash or a verify that did not finish: `flash_failed`, `grant_ended`, `crash` (a crash in the flash loop or the verify) or `interrupted` (a Ctrl-C there) (P1092, P1096, P1110). They are no Finding's code: `flow.py show` says each in its own words ([the deploy phase](flow.md)), and `data.deploy.cause` holds the code. `board_log_unreadable` is a board log that cannot be read, and `show` names it `phase_could_not_run`, as every phase.

**A bad flag.** With `--json`, `look.py` and `deploy.py` print an envelope for an argument they cannot run with, such as
`--no-simulation` with `--ignore-older-runs`: status `could-not-run`, `data: null`, one `unchecked` item with `code`
`bad_argument` and the parser's sentence, exit 2. The flag that failed is named only in that sentence: `data` holds nothing, so read
the sentence if you must tell which. The check is the word `--json` in the arguments. `--json=...` and an abbreviation of it
(`--js`) are not that word, so a bad flag beside them gets the usage on stderr and no envelope. Without `--json` they print the usage and the error on stderr and exit 2, as argparse does.

- `look.py` `data`: `port`, `also_on`, `chip`, `flash_mb`, `mac`, `micropython_banner`, `board`, `fields`, `stops`, `warnings`, `unknown`, `verdict`,
  `status`, `token`, `no_token_reason`, `simulation`, `caveats`, `limits`, `last_deploy`. `simulation` is `passed`, or `none` with `--no-simulation`, or
  null when the evidence refuses the image. `also_on` lists the board's other device nodes: rows of `mpremote devs` with one USB serial, USB id and product are one board when one node's name ends with that serial, as macOS names a CP2104 ([P333](https://github.com/xmejkal/spark/issues/427)), and the look uses that node. Relay `also_on` to the person, because two clones can still share a serial. `also_on` is null when `--port` was given, because no node list was read. `caveats` is a list of sentences (P345, what a passed run left out): what the passed runs did not test. `limits` is a list of objects `{component, sentence}`: what no simulation can show of the project, read from the limits section of every passed log, each once (item 9 below); with `--no-simulation`, read from the project's records instead (`requirements.json`'s parts and board), and `unnamed_must` then holds every must line of the brief (P778). In `--match`, `limits` are plain sentences (a board's, and since P778 a part's whose record skips the simulation or names a stand-in, the same words the build prints), here they are objects. `limits: []` never means the project has no limits (item 9). `last_deploy` ([P401](https://github.com/xmejkal/spark/issues/518)) is what spark's store says of this board, read by its MAC: `state`, `why`, `project`, `verdict`, `deployed` and, since P779, `micropython_banner`: the banner MicroPython prints (`MicroPython v1.29.0 on 2026-08-24`), read from the image file at that deploy; each null where absent (a deploy before P779 kept no banner). Since [P920](https://github.com/xmejkal/spark/issues/1302) it also holds `made_by`: the tool of a registered project that recorded the deploy with `bench.py record`, and null for spark's own deploy. Such a deploy has the verdict `ready not read`, and each null in its entry means that spark read nothing ([bench.md](bench.md)). A `verdict` of `flash not finished` is a flash that did not finish after the yes (P1097), and the look and the erase sentence say `the board may be erased`. A null `micropython_banner` also means a flash that did not finish. `data.micropython_banner` is the banner in the image the look would flash, read from the file, never from the board. A null is no banner to relay: the JSON does not tell "none in the image" from "no image" (the text line does); `token` and `no_token_reason` say whether there is an image. A banner is the image's own words, a fact; a board record's `micropython_port` names a download, a claim about the image.
  The state `recorded` holds the newest deploy as stored, so `verdict` is `ready seen` and not `passed`. The state `none-recorded` means the store holds no deploy of this MAC,
  and spark records only its own. The state `not-checked` has a `why`: the MAC was not read, or the record cannot be read. `not-checked` is never "no deploy".
  A stored time with no zone is printed as stored, with "(zone not stored)". The look reads it also when the image is refused. `problems` are the stops and a differing flash (`subject` `stop` or `flash`).
  `unchecked` are the unknown fields, a missing token and a `last_deploy` in state `not-checked`. A look that could not run has `data: null` (or `data.doctor` after a failed read). When there is a
  token, `next` holds a `deploy` step, whatever the status. A warning or an unknown field is not a pass: relay it.
- `deploy.py` `data`: `stage` (`plan`, `look`, `gate`, `flash`, `verify`: the last stage it reached), `dry_run`, `token`,
  `commands`, `look` (the look's `data`, read again at the end: an image gone since the look gives `token` null and `no_token_reason` says so, P1111), `yes` (`{kind: "typed"|"grant", who}`), `ready` (`verdict`, `sentence`, `lost_board`: true when the firmware printed `ready` and then mpremote lost the board, P1022),
  `facts_line`, `image_sha256` (the image on the board, P213; after a flash that did not finish, the image it was given, P1092; null before a flash), `board_log` (also after a flash or a verify that did not finish, P1092, P1110), `repl_command`, `store_record` (a path, also after a flash or a verify that did not finish, P1097, P1112; or null with `store_record_error` beside it),
  `board_state` (`may_be_erased` when a flash command failed, or `flashed_not_verified` when a crash came after the flash), `person_action`, `run_in_terminal`, and `simulation` (`passed`, or `none` with `--no-simulation`: no simulation tested the image, P337). Keys not reached are null,
  and so is `simulation` before a look or when the look refused the image. `open`, `port`, `product` and `known_board` come only with a stop at the board question (`needs_reply`, `answered_no`, `other_board` before the read, `no_known_board`, P892; [the deploy's question](replies.md#the-deploys-question)). The caveats of the look are in `data.look.caveats`, its limits in `data.look.limits`, and its last deploy in `data.look.last_deploy`. The erase question names that last deploy.
  If the erase stops with exit 2, deploy.py makes one retry after 5 s and prints `retry in 5 s: ...` on stderr
  ([P290](https://github.com/xmejkal/spark/issues/347)). A retry that worked is a normal deploy, with no extra key.
  When mpremote could not enter the raw REPL for the facts copy (seen right after the reset), the copy and its read-back make one
  retry after 2 s, for each read of the board, and `facts_line` ends with `(written on a retry after: ...)`, or names the first try
  when the retry failed too ([P420](https://github.com/xmejkal/spark/issues/550)). No other copy failure is retried.
- `needs_person: true` on a `next` step means the person acts first: with their hands, or by running the step in their own terminal. It is the `watch` step that follows a start the board never made
  (`download_mode_stayed`; `port_gone` gives no `watch` step) ([P433](https://github.com/xmejkal/spark/issues/575)), and the `live` and `watch` steps after `ready_unknown`, where `data.person_action` is null and the `fix` says what to do (P1022). A pick step of `flow.py show` has it too: a pick is the person's choice, so ask first (P1030). So do its `run_scenario` and `look` steps at the simulate and the deploy: the person runs a scenario in their own terminal, and plugs the board in before a look (P1034). So does the `look` step after a stop whose `fix` is the asleep fix (look.py, deploy.py, grant.py --check, bench.py record): the same look with no `--port`. Run it once, after the person did step 1 or 2 of the fix. Never run it in a loop while the board sleeps. This is [P1048](https://github.com/xmejkal/spark/issues/1538). The key is on a step only when it is true.
  The board doctor's `fix` and `data.person_action` are text for the person, not steps, so they carry no flag.
- `needs_yes: true` on a `next` step means the person must say yes. **Claude never supplies it.** The token is not the yes,
  and "go ahead" in a chat is not the yes. With no terminal (the exit is 2), `next` holds the `deploy` step to relay and
  `data.run_in_terminal` is the line to give the person word for word (it and the `grant` line start with `SPARK_HOME=<store>` when the run had one, so the new terminal window finds the same MicroPython build and grants); a `grant` step is added when a deploy grant could
  cover it. Never run either one yourself.
- `ready unknown` never gives a second `deploy`. A board that did not answer gives `look`, `live` (with `--code print('answer')`) and `watch` (its `argv` is the REPL command), in that order. A log that names no files gives `watch` alone. When the person must use their hands
  (`download_mode_stayed`, `port_gone`), `data.person_action` says so, with the RESET place when the board record has it, but only after the wait ran out. So tell the person before you run
  `deploy.py` that an R press may be asked: the run waits for it and its text goes to stderr. A `look.py` that could not read the
  board gives the board doctor's result in `data.doctor` and its next step for the person's hands as the `fix`. A `deploy.py`
  whose look could not read the board does the same. For `close_other`, the step tells the person to leave mpremote's
  console with Ctrl-X, because a console left open holds the port ([P354](https://github.com/xmejkal/spark/issues/452)).
- A missing or stale token gives a `look` step. `--dry-run` never looks: its `next` is the `look` step.

## Deploy without a simulation

For firmware that no simulation can test (P337). Three steps, then the person's yes:

1. `flash_image.py --project <p> --files firmware -o <image>`, where `<image>` is the file the `firmware = ` line of `sim/wokwi.toml` names. A build writes that line as a comment, so until a scenario run writes it, `<image>` is `sim/flash-with-firmware.bin`. It is the same with no `sim/wokwi.toml`, which the build does not write for a board that Wokwi has no part for (P1001).
2. `look.py --project <p> --no-simulation --json`. It gives a token only when `firmware/main.py` exists, every `.py` file
   under `firmware/` compiles, no run in `sim/runs/` failed on the image, and the image holds `firmware/` as it is now. The compile runs in one child process for all the files. A source that
   kills the compiler, or one that takes longer than 30 s, is a refusal that names the last file the child began, for example
   "firmware/main.py could not be compiled: the compiler stopped (signal 11)" or "firmware/main.py did not compile in 30 s".
3. `deploy.py --project <p> --no-simulation --token <token>`. The question starts with "no simulation tested this image".

The person types the yes in their own terminal, or a deploy grant given with `--no-simulation` answers it (P1029). The `next` step's `why` and the `grant` step (its argv ends with `--no-simulation`) say so, unless the store holds `grants/direct_flashing_disallowed`. The facts file, the board log, the store record and `data.simulation` say `none`. Nothing ran the firmware
before the flash, so relay that.
