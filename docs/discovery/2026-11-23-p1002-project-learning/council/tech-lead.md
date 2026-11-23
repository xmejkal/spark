# P1002 council: the tech lead

The lens: Feasibility, the fit with spark's technical direction, and electronics-firmware:physics. Read on
2026-11-23, 14:50 to 15:30 Prague time. A path that starts with `store/` is under `~/.local/share/spark/`. A path
that starts with `scripts/` is in /Users/petr/Development/spark.

## Jobs it sees

- J1. When a bench result settles a fact, spark writes it into the record's one home, with its source [D the PO
  2026-11-23, #1461]. Then every project that reads that record gets it [H].
- J2. Before the write, the person sees the old and the new value [D the PO 2026-11-23]. After it, one command undoes
  it [D the PO, on P1027 #1506].
- J3. A setting in the store, and one in a project, says off or offer [D the PO 2026-11-23, "configurable"].
- J4. The reads and writes go through the first slice of P1033's seam, on the file system only [D2, the PO
  2026-11-23].

## Findings: Feasibility

- TL-1 · The part writer exists. `parts.py --fact-set` writes `facts` entries {value, verified, source} into a part
  record's home. Then it refreshes the shelf copy. Its answer holds `was` and `now`. It has a dry run · E ·
  scripts/spark/sourcing/set_facts.py:29-37 · supports: the write and the review shape exist for parts.
- TL-2 · The board writer takes only `pin_roles` and `joined_pads` · E · scripts/spark/records/missing_facts.py:48-49,
  set_facts.py:48 · supports: a board fact such as deep sleep has no route. The 2026-11-23 facts went in by hand (E
  the record's note `//deep_sleep`).
- TL-3 · The board contract does not check facts outside its known blocks. I removed `source` from
  `deep_sleep.timer_wake` in a copy in memory. `board_records.validate` returned no problem. A `verified: true` with a
  null value also passed · E · `board_records.validate` run on the shelf copy, 2026-11-23. Output: `no source -> []`,
  `null verified -> []` · supports: today "every fact has a source" holds for a board's deep sleep
  only by hand. The rule exists in `provenance.fact_problems` (scripts/spark/records/provenance.py:44-60). Nothing
  calls it on these keys.
- TL-4 · Two copies of one record, and the facts sit in the wrong one. The board's shelf copy says `based_on`
  p934-epaper. Its home, /Users/petr/Development/spark-walks/p934-epaper/boards/firebeetle2-esp32c6.json, still has
  `deep_sleep: null` (dated 2026-11-21). The two differ only in `deep_sleep` and `//deep_sleep` · E · a Python
  compare of both files, 2026-11-23 · supports: see TL-5.
- TL-5 · The next shelving erases those facts. `shelve` builds the copy from the home record and writes it whole ·
  E · scripts/spark/sourcing/part_facts.py:112-121, 137-153, and `refresh_shelf_copy` in
  scripts/spark/sourcing/record_home.py:86-101 · supports: a write to p934-epaper's board replaces the shelf copy. The eight `deep_sleep` entries are then gone from
  the shelf. The backup in store/backups/ holds the record from before the write, so it does not hold them. Only the
  shelf copy, the diary and the project's issue #7 hold them. This is live today, not a risk of the design.
- TL-6 · The project that learns is not the record's home. p934-display2 has no `boards/` or `parts/` folder. It
  reads the shelf copies. A writer changes only two folders: the one `--project` names, and the home of a shelf copy
  (P987). Pointers · E · `ls` of p934-display2, record_home.py:30-56, diary.md:279 · supports: a learned fact from
  project B lands in project A's folder. The source then names B, and the file lives in A.
- TL-7 · A project's own copy wins over the shared one · E · scripts/spark/records/board_records.py:35-38, and
  `store.layers` (store.py:119-126: the project, the shelf, the library, the catalog) · supports: a wrong fact on the
  shelf spreads to every listed project with no own copy. A project with its own copy is shielded, and also blind to
  every later fact.
- TL-8 · The reach of a wrong fact today. Two of 27 listed projects name these records. p934-epaper holds its own
  copies. p934-display2 reads the shelf · E · a read of store/projects.json and each requirements.json · supports: the
  spread is small now. It grows with each project that uses a shared board.
- TL-9 · No script reads a board's `deep_sleep` · E · `grep -rn deep_sleep scripts/ boards/` (one search word in
  scripts/spark/sourcing/datasheets.py:137, and the library's two boards) · supports: a kept board fact changes no build,
  check or pin map. Only the conversation reads it. A wrong one misleads Claude, not a script.
- TL-10 · `parts.py --unverified` lists the open facts that a project reads. Its next step writes a bench result back
  with `--fact-set` · E · scripts/spark/sourcing/list_unverified.py:1-5 · supports: a loop from an open fact to a kept
  one exists for parts. P1003's pre-analysis builds on it (E `gh issue view 1462 --comments`).
- TL-11 · Undo and git. The shelf and the board shelf are private places. Spark refuses to write a private place
  inside a git work tree. `inside_git` walks up the folders and looks for `.git` · E ·
  scripts/spark/records/store.py:143-145, 173-179, 341-345 · supports: `git init` in the store makes every shelf write
  fail with STORE_IN_REPOSITORY. A git folder kept outside the store passes that check. The check's purpose is that
  nothing private reaches a repository. So that path is the PO's choice, not a fix.
- TL-12 · The project homes are not in git either. p934-epaper is in no repository. p934-display2 is one · E · `git
  -C <folder> rev-parse --show-toplevel`, 2026-11-23 · supports: "undo through the project's git" fails for the one
  home that holds both records.
- TL-13 · A log exists to reuse. `store.append_event` appends one JSON line to store/history.jsonl (99 lines today:
  step, reused, built) · E · scripts/spark/records/store.py:461, scripts/spark/sourcing/part_facts.py:98-109 ·
  supports: a `fact-set` event with `was` and `now` makes each write undoable from the log, with no git.
- TL-14 · Settings have one pattern and no home. tools.json has a person's file in the store and a project file,
  `.spark/tools.json`, merged entry by entry. `store.PLACES` has no settings place · E ·
  scripts/spark/records/tool_finder.py:6, 41-43, scripts/spark/records/tool_choices.py:18-24, store.py:108-112 ·
  supports: a settings file is the tools.json shape again, with a new place name.
- TL-15 · Two shapes for one key. The library boards keep `deep_sleep` as bare values (`wake_api`,
  `single_polarity_for_all_pins`). The shelf copy keeps {value, verified, source} entries · E ·
  /Users/petr/Development/spark/boards/xiao-esp32-c6.json:204, store/shelf/boards/firebeetle2-esp32c6.json:865 ·
  supports: `provenance.read_value` reads both (provenance.py:16-24). A writer that merges into a bare block needs a
  rule.

## Findings: fit with the direction

- TL-16 · The PO's rule "one core, many interfaces" asks for a small Operation class and a thin `main()` · D ·
  AGENTS.md, Principles · supports: a `KeepFinding` Operation beside `SetFacts`, not a prompt that holds the logic.
- TL-17 · D2 puts the reads and writes behind the first slice of P1033's seam. P1033's own first step is an analysis
  on the best model · D · the PO 2026-11-23 · E · `gh issue view 1515` · supports: P1002 waits for that analysis, or
  builds a seam of two methods (read a record, write a record) that the analysis can replace. The second carries the
  risk of building the seam twice (H).
- TL-18 · Privacy. The e-paper fact `deep_sleep_wake` names the PO in full in its source. It also holds a home path,
  `~/Development/spark-walks/p934-display2/diary.md`. The board facts point to "the project's issue #7 comments" · E ·
  store/shelf/epaper-2in9-bwr-mh-et-live.json, `facts.deep_sleep_wake.source`, and the board's `deep_sleep` sources ·
  supports: in the private store this is fine (files 0600, store.py:143). `--promote` copies a project record to spark's
  public library. I found no scrub of sources in it (E `grep` of scripts/spark/sourcing/promote_record.py). AGENTS.md
  says never commit a home path. So a writer that runs alone keeps names and home paths out of a source.
- TL-19 · `verified` is one boolean. The rule asks only for value, verified and source · E · provenance.py:12-13 ·
  supports: a bench result on one unit and a maker's number look the same. The e-paper record says of itself, "A
  verified: true fact here is a chip datasheet's own number". The bench facts are verified true too · E ·
  store/shelf/epaper-2in9-bwr-mh-et-live.json:6 · supports: two meanings of one flag in one record.

## Findings: electronics-firmware:physics

- PH-1 · The kept facts by provenance (the lens's words). Measured on the bench, one unit, MicroPython v1.29.0:
  `timer_wake`, `rtc_memory_survives`, `clock_keeps_counting`, `usb_while_asleep`, `light_sleep` · E · the sources of
  `deep_sleep` in store/shelf/boards/firebeetle2-esp32c6.json · supports: field results from one board, one build,
  one power setup. None names the board revision.
- PH-2 · Deep-sleep current: three numbers disagree, and nobody measured one. The record cites the DFRobot wiki for
  the board: 16 uA (V1.0) and 36 uA (V1.2). It cites the Espressif datasheet for the chip: 7 uA · E · the same record,
  `deep_sleep.deep_sleep_current_ua.source`, value null · supports: the null is kept, as the rules ask. The cheapest
  rung is a meter in series with the battery at the PO's bench. That rung cannot tell the board's share from the
  e-paper module's share without a second run with the module off.
- PH-3 · The module stays powered while the host sleeps. `host_deep_sleep_ok` says so, and "the module's own current
  while the host sleeps (module_sleep_current_ua stays null)" · E · store/shelf/epaper-2in9-bwr-mh-et-live.json,
  `facts.host_deep_sleep_ok.source` · supports: a battery budget for the gadget is unknown. The same meter rung settles
  it.
- PH-4 · `light_sleep` resets the chip with cause 3 (WDT_RESET). The record says the cause is unknown: "USB port,
  watchdog or the build" · E · `deep_sleep.light_sleep` · supports: a field result with an open cause. The cheapest
  rung: the same trial on battery with USB off, and the reset cause read from RTC memory after the wake. It cannot
  separate the watchdog from the build.
- PH-5 · The panel's reset path. Reset pulses on GPIO19 (pad SDA) did not wake the panel. The cause is open: the
  wire, the TXS0108E level shifter or the pulse · E · `facts.deep_sleep_wake.source` of the e-paper record ·
  supports: the value "only a power cut wakes the panel" is wider than the bench. The cheapest rung is a scope or a
  logic probe on the module's RST pin during a pulse. It shows whether the pulse arrives, not why the panel ignores it.
- PH-6 · BUSY never moved during a refresh the PO saw: 838 618 reads, no change. A pull test cannot tell a driven pin
  from one that the TXS0108E's pull-ups hold high · E · diary.md:497-501 · supports: `busy_active_level` stays null,
  correctly. A multimeter on the BUSY pad is the rung the diary names.

## Riskiest assumption

A kept fact stays in the copy that the next project reads. TL-4 and TL-5 show it does not today: the facts sit in
the shelf copy, and the next shelving from p934-epaper replaces it. TL-6 adds that the learning project is not the
home. Cheapest test, a dry run with no write: run `parts.py --fact-set` on any part fact of p934-epaper's board with
`--dry-run`, then compare the shelf copy it plans with today's shelf copy. Pass line (proposed, written 2026-11-23
before any result): the planned copy keeps all eight `deep_sleep` entries. I expect a miss (H, from TL-5). A board
`--fact-set` takes only `pin_roles` and `joined_pads`, so the dry run uses a `pin_roles` level fact.

## Options

- A · One home, a log for undo, the setting as a file. Cost: about three small PRs.
  1. Extend `--fact-set` for boards to a `facts` block of {value, verified, source}, with a `learned` part {project,
     date, log, setup}. Write to the record's home, then refresh the shelf. Check every entry with
     `provenance.fact_problems` (fixes TL-3).
  2. Append a `fact-set` event with `was` and `now` to history.jsonl (TL-13). An undo writes `was` back.
  3. A settings place in the store and `.spark/settings.json` in a project, merged like tools.json, values off or
     offer (TL-14).
  The record and setting reads go through a two-method seam that P1033's analysis replaces or keeps. Proves: J1 to J3
  on the next walk, with no git in the store.
- B · Learned facts live in one store file per record, apart from the record. For example
  `store/learned/firebeetle2-esp32c6.json`. The readers merge it over the record. Cost: about four PRs, and a change to
  every reader of a board or part record. Proves: one home for every project's learning (TL-6 goes away), and the
  record files stay as their research wrote them. It touches more code, and it is a decision for P1033's analysis.

Before either option: one Found-on-the-way item. Write the eight `deep_sleep` entries into the home record in
p934-epaper as well, on the PO's yes, so that TL-5 does not erase them (cost: one `--fact-set` once TL-2 is fixed, or
one hand copy now).

## What I could not check

- The p934-display2 issue #7 trial logs that the board facts cite.
- Whether `parts.py --list` on p934-epaper refreshes the board's shelf copy today. I did not run it, because it
  writes.
- How `is_pin_map_constant` treats a sentence value such as `usb_while_asleep`. The contract never reaches it (TL-3).
- The PO's board revision.

## Questions for the decider

- Where is the one home of a learned fact: the record's project folder, the shelf, or a learned file per record? ·
  decides: Option A or B, and TL-6.
- Is undo from a log enough, or is git a must? Git means a change to §5.8 · decides: TL-11.
- Does P1002 wait for P1033's analysis, or build a two-method seam first? · decides: the order of the two cards.
- Does a learned fact carry its setup as fields (build, revision, power, wiring), or as text in the source? · decides:
  TL-19 and the user lens's misleads.

## Searches

none
