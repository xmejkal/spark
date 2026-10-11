# P158 part 1 — verification of the chain-and-checks diagnosis

Written 2026-10-10 by the area's refuter, against spark 0.8.1 (main `a8aa34d`, `git log -1`, 2026-10-10), reading the
diagnosis (`chain-and-checks.md`) and the catalogue (`../catalogue.md`) as data, and the primary artefacts — `scripts/*.py`,
`boards/*.json`, `commands/*.md`, `docs/guide/*.md`, `tests/` — at every cited line. Three runs were made, all on a copy
of the PO's store (`<scratch>/store`, 33 MB by `du -sh`, copied 2026-10-10) with the three-word prefix
(`SPARK_HOME=… HOME=… TMPDIR=…`), verified once with `env | grep SPARK_HOME`; the real store was never read by a command
nor written. Irrigation, plant-alarm and the bin were read, never run against and never written. Tags: **E** a pointer or
a run, **H** a claim with its source, **D** a decision (who, when), — unknown. Line numbers are spark's at `a8aa34d`.

Verdict words: *holds* · *partly* (the code says something weaker or narrower) · *refuted* · *could not check*.

## Verdicts

| root cause | verdict | one line |
| --- | --- | --- |
| RC-1 the rules file is a snapshot of derived facts | **holds** | every cited line reads as quoted; the re-seed-on-empty is a deliberate rule (P45) whose own docstring names the case it does not handle |
| RC-2 a stderr line is a broken chain; the usual note is the person's signal | **partly** | `--requirements` pre-says three of the four circuit-gap notes, not four; "the build will also stop on them" is now E for the unsourced-rail note, H for the other three |
| RC-3 `--keep` protects `board.tsx`, the chain never reads it | **holds** | every cited line reads as quoted; #44 open, the PO's decision in its body |
| RC-4 "owes" is one flat list, consequences in five places | **partly** | the `pin_order_proof` row is wrong: the chain's **parts** stage refuses such a record (E, a run), and `--audit` calls the same record merely "owed" |
| RC-5 the requirements writer has its own loader and its own naming | **holds** | the three reproductions follow from the code; the default-name case reproduced here |
| RC-6 the board is stated in two files and the chain moves one | **holds** | plus: spark's own `boards/README.md:21` still calls `active.json` "THE one place" |
| RC-7 five contract checks test the wrong property, place or word | **holds** | all five; K52's exit is also the wrong *kind* of wrong (1, "problems") |
| RC-8 the floating-input rule has one word for an input | **partly** | the mechanism holds; "derived by init, not written by a person" is refuted — the four entries were typed by hand on 2026-09-29, a day before seeding existed |
| RC-9 ★C7 by design, judged against the criteria | **holds** | the asymmetry at `:554` vs `:678` is as described; the PO's decision found at #94, 2026-10-08T12:52Z |

### RC-1 · holds

Read, verbatim. `scripts/init_project.py:300-302`:

```
        elif isinstance(result[key], list) and not result[key] and value:
            # An empty list is "nobody filled this in", which is exactly what P45 set out to end.
            result[key] = value
```

`scripts/check_spine.py:63` `import init_project  # noqa: E402`; `:314` `if version in ("unknown version",
init_project.PINNED_CORE):` — the only two uses (`grep -n init_project scripts/check_spine.py`, 2026-10-10: lines 63, 314,
316). `scripts/check_all.py:124` `result = compare_design.compare(inputs["circuit"], inputs["rules"])`; `:138`
`findings = check_physics.run(circuit, json.loads(Path(inputs["rules"]).read_text()), loads)`. `commands/idea.md:126`
"Run `/spark:init --board <the board pick>` in the project first"; the page then gives `--requirements` (`:131-133`) and
"`/spark:build` takes it from there" (`:141`). `commands/init.md:36` "**After a build, run it again with `--force`:**".
`commands/build.md:217-219` "## After it builds … `check_all.py --project .`" — no init. `scripts/compare_design.py:258-259`
`fix="name the I2C lines and the pins that must never float — a netlist records neither, which is why this file exists"`.
`scripts/check_physics.py:475-477` `fix="fill physics.rails in the rules file … `/spark:init` writes the names from the built
design and leaves the numbers null, which is where they have stayed."`. `scripts/init_project.py:185-186` `"i2c_hz": None,` /
`"i2c_bus_capacitance_pf": None,` in the skeleton for every project. `grep -n "init_project\|rules_for\|merged("
scripts/needs.py scripts/parts.py` → nothing (2026-10-10): no other writer re-derives.

The rival "a deliberate rule": both halves are deliberate — the re-seed of an empty list is P45 (`:301`), the nag is W1
(`:251-259`). The rule's own docstring (`:256-258`) names what it does not handle: "a list filled in BEFORE the records
could seed it never learns the rest … Keeping theirs is right; staying quiet about the difference is the silent-skip". Neither
half handles the retraction case the diagnosis names (a derived entry deleted on purpose comes back), so the deliberateness
does not overturn the RC. One addition: `design_in` (`:68`) globs `*requirements.json`, so irrigation's
`irrigation.requirements.json` IS read by init — the blindness at init is purely the documented order, as diagnosed.

### RC-2 · partly

Read, verbatim. `scripts/check_spine.py:374-375`:

```
    if emitted.stderr.strip():
        stages.append(Stage("schematic-notes", PROBLEMS, emitted.stderr.strip()))
```

`scripts/emit_board.py:1128-1130` `print("note: %s was assigned a pin and no part claims it, so nothing in the emitted "
"board connects to it" % signal, file=sys.stderr)`; `:1125-1127` `placed` / `claimed` as described; `:1143-1147` the fifth
note, `outputs_in_contention`. `scripts/design.py:291-305` records' signals then `wanted.get("signals")`.
`docs/guide/how-it-works.md:37` "It counts as a problem, so the run exits 1 even when the board builds".
`scripts/needs.py:548-549` "Said before the build, never refused".

**The sentence to change** (RC-2, "Why", second sentence): "Of the five notes, four name a circuit gap the build will also
stop on … — and `--requirements` already says each of them before the build". `_power_gaps` (`needs.py:538-568`) returns
`no_supply` (`rails_without_a_source`, `:563-564`), `no_receiver` (`outputs_with_nothing_on_them`, `:565`) and `no_driver`
(`pair_sides_without_a_driver`, `:566`) — three. `outputs_in_contention` (two supplies on one rail) has no counterpart:
`grep -n outputs_in_contention scripts/*.py` → `scripts/emit_board.py` only (2026-10-10). So: **three of the four**.
Why it matters: C2 keeps the four as PROBLEMS on the ground that `--requirements` already warned — for the fourth it did not.

**Made E for one note, stays H for three.** E: `<scratch>/proj-rail`, `{"board": "firebeetle2-esp32s3", "parts":
["l9110s-module"]}`, irrigation's toolchain linked in (`tsci 0.0.2663`): `check_spine.py` printed `[!!  ] schematic-notes
note: nothing sources net.MOTOR6V — add whatever supplies it, or that net has one member and the board will not route` and
`[!!  ] build            2 error(s): pcb_port_not_connected_error`, "the chain is broken", exit 1, 5.5 s wall (`time`). The two
errors, from the kept `dist/board/circuit.json`: `Port [L9110sModule.VCC] is not connected to net [MOTOR6V] by a PCB trace`
and `Port [Mcu.pin17] is not connected to net [V33] by a PCB trace` — each a one-member net. So for the unsourced-rail note
the build stage does stop, as `build.md:149-150` says; the note names the cause, the build error names a symptom. Whether the
other three notes' gaps also reach a build error was not run (H, from the notes' own wording).

A nuance, no change: `placed - claimed` is a subset of the file's `signals`, not strictly equal — a declared signal the
assigner could not place would be in neither, but `assign_pins.Impossible` refuses before this point (`emit_board.py:1055-1061`),
so in practice equal. The stray-stderr claim (a Python warning → "the chain is broken") is read from `:374-375` and stays H;
`emit_board`'s `LIBRARY_NOTE` (`design.py:157`) is not an instance: it prints only when `not args.project`
(`emit_board.py:1051-1052`) and the chain always passes `--project` (`check_spine.py:359`).

### RC-3 · holds

Read, verbatim. `scripts/check_spine.py:357` `board_file = workdir / "board.tsx"`; `:371` `board_file.write_text(emitted.stdout)`;
`:399-400` `built = subprocess.run([str(toolchain), "build", "board.tsx"], cwd=str(workdir), …`; `:655-657`

```
        if target.exists():
            said.append("left alone: %s (delete it to have it regenerated)" % target)
```

`:608-609` `handed = design_handed_to(workdir, project) if source and not from_library else None`; `:625-627`
`if handed is not None and verdict(stages) == EXIT_OK: … parts.note_built(handed)`; `:675-683` `render` first, then the
`keep_into` lines to stderr. `commands/build.md:72-74` "`dist/` is still replaced with a build of the freshly generated board,
not of your `board.tsx`". `tests/test_check_spine.py:316-324` pins "left alone", `:326-331` pins `dist/` replaced.
#44 (`gh issue view 44`, 2026-10-10): OPEN, no comments, body "The PO decided on 2026-10-05: build the kept file." — D as
the card records it.

One loose word, not a correction: the `built` event digests the **records** the chain was handed (`design_handed_to`,
pinned at `tests/test_check_spine.py:955-970`), true of the regenerated board and of a kept one alike; the diagnosis's "which is
the regenerated board's" is a reading, not a wrong one.

### RC-4 · partly

Read, verbatim. `scripts/parts.py:97-98`:

```
#: The facts the chain reads from a part record (§5.4): absent, the record owes them, and no build can place it.
CHAIN_FACTS = ("footprint", "pin_order", "pin_order_proof", "body_mm", "simulation")
```

`:107-110` `owes`. `scripts/emit_board.py:1081` `if unfootprinted:` → `EXIT_COULD_NOT_RUN`; `:1091` `if unpinned:`; `:1101`
`if unsized and not args.assume_missing_sizes:`; `scripts/check_spine.py:360` `"--project", str(project),
"--assume-missing-sizes"],`; `scripts/sim_project.py:55-57` `if not isinstance(simulation, dict): unmapped.append(…)`;
`scripts/check_spine.py:463-465` `if unmapped: return stages + [Stage("simulation", COULD_NOT_RUN, …)]`; `scripts/needs.py:405`
`LAYOUT_FACTS = ("body_mm",)`; `:598-602` `["owes %s — %s" …] if set(owed) - set(LAYOUT_FACTS) else
parts.broken_problems(record, path)`; `scripts/parts.py:1631` `"%s  [catalog: researched before; `--promote %s --project .`
builds with it]"`; `:1518` "one that owes only its outline is written with a warning, one that owes more is refused".
#102 (`gh issue view 102`, 2026-10-10): OPEN, the PO's words as quoted. Four of the five rows hold.

**The sentences to change** (RC-4 "Where", last clause, and "Why", the table): "`pin_order_proof` is read by nothing in the
chain (grep: `scripts/parts.py:377-385` validate and `:826` the unverified listing only)" and "pin_order_proof missing →
nothing stops anywhere". The chain's record loader is `parts.load` (`scripts/parts.py:265-271`):

```
def load(part_id: str, project: Path = None) -> dict:
    path = definition_path(part_id, project)
    part = json.loads(path.read_text())
    problems = validate(part, path)
    if problems:
        raise PartError("%s does not meet the part contract:\n%s" …
```

`validate` includes `pin_order_problems` (`:788` `problems.extend(pin_order_problems(part))`), which fires when a `pin_order`
is present and `pin_order_proof` is not a dict (`:375-379`). `design.record` turns the `PartError` into a `DesignError`, and
`check_spine.run` calls `design.parts_of` at the **parts** stage (`check_spine.py:352-355`), before `emit_board` runs.
E: `<scratch>/proj-proof` — the library's `tactile-button` (`pin_order: ['A', 'B']`) copied into the project's `parts/` with
`pin_order_proof` removed: `parts.owes(r)` → `['pin_order_proof']`; `parts.broken_problems(r, p)` → `[]`; `parts.validate(r, p)`
→ `['pin_order states no pin_order_proof {verified, source}: where the order was read, because a pin order read wrong reverses
a supply']`; `check_spine.py` → `[????] parts  …/tactile-button.json does not meet the part contract: - pin_order states no
pin_order_proof …`, "the chain was NOT exercised — this is not a pass", exit 2. Owing `pin_order_proof` *alone* is possible
only with a `pin_order` present (`:374` returns `[]` for an empty one), so the corrected row is: **pin_order_proof missing →
the parts stage stops, exit 2, as a contract failure.** The grep missed it because `validate` is not called by name in the
chain; `load` calls it. Why `--audit` disagrees: `broken_problems` (`:127-131`) drops every validate problem that is `_about`
an owed key, and `_about`'s third branch (`:116` `or re.search(r"\bno %s\b" % re.escape(key), problem) is not None`) matches
"no pin_order_proof" — so the store's words say "owed, not broken" of a record the chain's loader refuses. This is a missed
root cause (MC-3 below) and it changes C4's table and C4's `--requirements` policy (see §The changes).

### RC-5 · holds

Read, verbatim. `scripts/needs.py:612` `held = held if isinstance(held, dict) else {}`; `:430-432` `_called` ("the name it is
given, else its part id in capitals"); `:477-480` `held_by.setdefault(_one_name(called), ("%s in requirements.json" %
_part_of(entry), called))`; `scripts/design.py:104-106` `raise DesignError("%s holds a %s; a requirements file is an object
with `parts`" …)`; `:81-86` `names_that_are_one` skips an entry whose `name` is not a non-empty string (`continue`);
`:22-26` "It does not name COMPONENTS for the netlist — that is `emit_board`'s"; `scripts/emit_board.py:42` `import design as
design_library`. E (my run, pure functions): `design.read` passed `["tactile-button", {"part": "tactile-button", "name":
"Tactilebutton"}]`; `emit_board.duplicate_component_names(parts_of(...))` → `['TactileButton / Tactilebutton']` — the
generator's net, one stage later, as diagnosed. A sibling the diagnosis does not count: `needs._name_after` (`:425-427`) is
the same capitalisation applied to a need id; `_called('open-lid', None)`, `component_name({'id': 'open-lid'})` and
`_name_after('open-lid')` all gave `OpenLid` today, and nothing pins that they agree.

### RC-6 · holds

Read, verbatim. `scripts/needs.py:517-518` `return [parts._problem("board", "pick one board — %s" % (…))]`; `:617`
`content = dict(held, board=board_picks[0] if board_picks else None, parts=after)`; `scripts/parts.py:2085` `said += ["  board:
%s → %s" % (json.dumps(board_was), json.dumps(content["board"]))] …`; `grep -n active scripts/parts.py scripts/needs.py` →
nothing (2026-10-10); `scripts/init_project.py:473-474` `write(project / "boards" / "active.json", {"schema": 1, "board":
args.board}, args.force)`; `scripts/boards.py:513-524` `--path/--resolve/--id/--get` read `active_id`; `scripts/check_all.py:356`
`active = boards.definition_path(project)` — assigned and never used afterwards (`:357-360`), so no check depends on the
selection; `scripts/design.py:342` `board = boards.load(root, board_id or wanted.get("board"))`; `scripts/emit_board.py:346`
`def place(board, part_list):` (the single-MCU claim stays H, as the diagnosis says). #94 body (gh, 2026-10-10) quotes the PO
2026-10-07: "a project wouldn't need an esp32 … or even more than one mcus" — D as cited. Addition: `boards/README.md:21`
"boards/active.json <- which board. THE one place it is chosen." stands in spark's own docs beside `commands/idea.md:132-133`
"the board follows the pick" — the two statements are also a documented contradiction. The bin's `Makefile:49-53` and `:94-96`
read the selection through `boards.py --path/--id/--paths/--get/--resolve` — the one consumer that depends on `active.json`.

### RC-7 · holds (all five)

- **K52** `scripts/boards.py:476` `marker = "active" if board_id == active_id(project) else "     "` inside the per-board loop;
  `:526-529` the `--list` guard (`try: current = active_id(project) except BoardError: current = None`); `:537-539` `except
  BoardError as broken: print(f"boards.py: {broken}", file=sys.stderr); return EXIT_INVALID`. Addition: `:116` `from outcomes
  import EXIT_OK, EXIT_PROBLEMS as EXIT_INVALID` — a missing selection exits 1, "problems", where the three-outcome rule
  (`outcomes.py:19-20`) says could-not-run; the wrong cause and the wrong kind of wrong.
- **K54** `scripts/parts.py:101-104` `_absent` asks `isinstance(value.get(side), (int, float))`; `:659-660` `"body_mm has no
  numeric %s"`; `:1903-1904` refuses only `_absent`; `:464-466` `positive()` inside `host_part_problems`. E (my run):
  `_absent('body_mm', {'width': -3, 'height': 0})` → `False` (present); `{'width': 'wide', …}` → `True` ("absent").
- **K63** `scripts/parts.py:2117` `event = cost.step_event(store.add_project(target, dry_run=args.dry_run), step)`;
  `scripts/store.py:258-260` `folder = Path(folder).resolve()` … no `is_dir`; `scripts/init_project.py:408-410` `if not
  project.is_dir(): print("no directory at %s" …); return EXIT_COULD_NOT_RUN`; `scripts/needs.py:113-114` `path.parent.mkdir(
  parents=True, exist_ok=True)`. A shade on "idea.md:17 runs `--step <project> S` first": `commands/idea.md:13-15` says "S as
  soon as the project's folder is chosen (S's item 3 …)", and item 3 (`:30-35`) chooses the folder and then runs `--needs-set`,
  which makes it — so the page's own order does put `--step S` before the folder exists when read literally. The fault stands.
- **K50** `scripts/parts.py:517` `if chip and not (isinstance(chip, str) and re.fullmatch(SELECTOR_SAFE, chip)):`; `:520-521`
  "its files beside the record are named by it, and wokwi.toml is written with it". E: `re.fullmatch(SELECTOR_SAFE,
  'flow-meter')` → `False`. `scripts/needs.py:360-362` `URL_IN_WORDS … (?(1)>?)`: E `kept_reason("see https://x.com/a> more")`
  → `('see> more', True)`; `kept_reason("<https://x.com/a> more")` → `('more', True)`.
- **K51** `scripts/sim_project.py:92-97` the sentence taken as it is; `:114` `lines.append("- **%s** — %s" % (component,
  sentence))`; `scripts/check_spine.py:519-522` the same sentence in the terminal.

### RC-8 · partly

Read, verbatim. `scripts/init_project.py:95-97`:

```
            if need.get("direction") == "in" and need.get("pin"):
                pins.append([emit_board.component_name(part), need["pin"]])
```

`scripts/compare_design.py:209-211` `"it has no defined level at reset or whenever its driver lets go; add a pull-up or
pull-down, or remove the rule if the part pulls it itself"`; B13 is `4daa58f` 2026-10-03 (`git log`); pinned at
`tests/test_compare_design.py:67-73`. Irrigation's `parts/dfr0457-mosfet-power-controller.json` `needs[0]`: `"direction":
"in"`, note "ACTIVE HIGH: high lights the optocoupler's LED … Sources about 5 mA at 3.3 V"; `"//"`: "a single-channel,
optically isolated, HIGH-SIDE switch". Irrigation's `.spark/rules.json` `must_not_float` = the four `ValveN.SIGNAL` pairs. The
mechanism (the rule is too wide for a pin whose level is defined by its load; the record's vocabulary cannot say so; the seed
re-derives the entry) holds.

**The sentence to change** (RC-8 "Where", last sentence; and "Why", "the project's entries are not a person's data but init's
derivation"): "derived by init, not written by a person (the `//` note beside it says 'Seeded from every pin …')". Refuted on
the fact. E: irrigation `DIARY.md:203-205` — "`must_not_float` was empty as `init` wrote it … Declared the four valve inputs —
`["Valve1","SIGNAL"]` … `["Valve4","SIGNAL"]` — and re-ran" (prediction 6, scored); irrigation commit `c6c583e` 2026-09-29
adds them to `.spark/rules.json` (`git show c6c583e -- .spark/rules.json`: `-  "must_not_float": [],` → `+ "Valve1" …`);
spark's seeding of inputs landed a day later, `bec7b88` 2026-09-30 "The rules a project is checked against are seeded from its
design" (`git log -S"def declared_inputs"`); and spark's own `init_project.py:256-258` says so: "the irrigation controller had
four valve inputs written by hand and would never have gained the DS3231's clock line or the mode button". The `//` note is no
evidence of origin: `merged` (`:296-297` `if key.startswith("//"): result[key] = value`) rewrites every `//` key with the
template text on each `--force` (irrigation's `2f6631e` 2026-10-01 re-ran it). Corrected reading: the four entries **are a
person's data and are also exactly what init derives since 2026-09-30**, so a deletion is undone either way — and the file has
lost the means to tell the two apart (MC-2). A6's "both" still stands; the data half reads "a person's entries the seed would
restore", not "init's entries". Also E from the same diary: on 2026-10-01 the four entries passed `rules-vs-netlist`
(`DIARY.md:288-289`); the FAIL is B13's, as the catalogue says. The physics (an opto LED behind a resistor cannot float into
conduction) is H from the record's note; the DFR0457 schematic was not read here.

### RC-9 · holds

Read, verbatim. `scripts/check_spine.py:554` `}[code] + (" — but not every need is on the board: %s" % ", ".join(unserved) if
unserved and code == EXIT_OK else ""))`; `:678` `print(json.dumps(dict(said, unserved=requirements["unserved"]) if
left_off(requirements) else said))` — the JSON carries the note in every outcome, the text only on `EXIT_OK`: the asymmetry
as described. `commands/build.md:94-98` as quoted; `docs/guide/agents.md:250` "`check_spine.py` | `check`, `stages`, `status`,
and `unserved` when …". D: #94 comment `2026-10-08T12:52:49Z` (gh, 2026-10-10): "a green build WARNS (not refuses) on a need
with no pick and on a record-less on-board pick, naming each and marking it". `tests/test_check_spine.py:1085-1089` pins the
suffix. Judged against the criteria as the diagnosis does: the design holds; C9 is a wording chore.

## Missed root causes

**MC-1 · Two meanings of an empty rule list, held by two tools on purpose.** `init_project.rules_for` writes
`//must_not_float`: "an empty list means the records declare none, not that nobody filled it in" (`init_project.py:168-172`),
and `//i2c_buses`: "Empty because every I2C device in this design carries its own pull-ups (…) — nothing for this board to do,
which is not the same as nobody having looked" (`:158-166`). `compare_design.py:250-259` reads the same two empty lists as
could-not-run — its comment: "Comparing nothing is not agreement" — with a sentence that blames init. Both are deliberate
(E: the comments at both places); they contradict. A design whose records declare no `direction: "in"` pin and whose I²C parts
carry their own pull-ups is could-not-run on `rules-vs-netlist` for ever, exit 2, with no way to say "looked, nothing to rule".
Neither C1a nor C1b touches it: deriving at check time still yields zero rules, and `compare_design` still calls zero rules
could-not-run. It needs a decision (the PO's): either `compare_design` takes the derivation itself and answers `ok` with
`checked: 0` and the reason ("the records declare no input; Ds3231… carries its own pull-ups"), which overturns "comparing
nothing is not agreement" for the case where the records were looked at; or the rules file gets a `checked` statement.
Testable either way (a records-only design with no inputs and a self-pulled bus; assert the chosen outcome). Who meets it
today: no current project (irrigation has four entries; plant-alarm's amp declares four inputs; the bin's list is hand-written),
so K46's first-run case is what has been seen — this is its steady-state twin, and the first sensor-only board will meet it.

**MC-2 · `merged` rewrites the provenance notes over a person's values.** `init_project.py:296-297` — every `//` key takes
the derived text, so after one `--force` a hand-written `must_not_float` is annotated "Seeded from every pin the design's own
part records declare as an input" (irrigation's file today: the list from `c6c583e` 2026-09-29, the sentence from a later
`--force`). The file misstates its own origin; it misled the diagnosis (RC-8) and would mislead an agent deciding whether an
entry may be deleted — exactly the PO's criterion ("understandable where a mistake is happening and why"). Fix: the `//` text
states the rule the seed applies, never the origin of the values; or origin per entry. Small; one test (`merged` over a
hand-written list keeps a note that does not claim derivation).

**MC-3 · `owes` and `validate` disagree about `pin_order_proof`** (from RC-4's refutation). `broken_problems`
(`parts.py:127-131`) hides, through `_about`'s `\bno pin_order_proof\b` branch (`:116`), the one validate problem that
`parts.load` (`:265-271`) enforces on every record the chain reads. One record, two verdicts from one module: `--audit`
"owes pin_order_proof" (fillable later), `--need` "builds with it", the chain "`[????] parts … does not meet the part
contract`". E: the `<scratch>/proj-proof` run above. The design question underneath: is a pin order without its proof an
owed fact (buildable, warned, marked — #102's direction) or a contract failure (as `validate` says since P81)? Today it is
both, and the catalogue's 17 "owed" catalog records (the diagnosis's count, `--audit --json`, 2026-10-10, on the copy) include
every record this refuses at the parts stage. C4 cannot be built until this is decided.

**MC-4 · A hand-edited `board.tsx` imports siblings the work folder does not have** (bears on C8). The bin's
`board.tsx:1-4` imports `./FireBeetle2Esp32S3`, `./Dfr0954I2sAmp`, `./FireBeetle2Esp32S3Body`, `./mcu-pins`. C8's sketch
("copied into the work folder over the emission, the kept footprint with it") builds a file whose imports resolve nowhere and
reports a build failure as the design's — the F5 class the chain already guards against for crashes. Either build in place
(the project folder, where `build.md:74`'s `npx --no tsci build board.tsx` already resolves them) or copy every local import.
Related and unnamed: `keep_into` leaves **any** existing `*.tsx` alone (`check_spine.py:652-657`), the generated footprint
file included (irrigation holds `FireBeetle2Esp32S3.tsx`); a board-definition change regenerates the footprint in the work
folder and builds with it while the project keeps the old one — the kept `board.tsx` imports the stale footprint. Same class as
RC-3, one file over.

**MC-5 · The rule's premise fails for more inputs than current loads** (RC-8 is narrower than the fault). Spark's own
`parts/max98357a-dfr0954.json` declares `BCLK`, `LRC`, `DIN`, `SD` as `direction: "in"`; `SD`'s note: "must be driven, not left
floating — an on-board resistor holds it high" — a module-internal pull the netlist cannot see. Plant-alarm's `board.tsx:34-37`
wires all four straight to MCU pins, no resistor. Plant-alarm has no `.spark/rules.json` (`ls .spark` 2026-10-10:
`needs.json` only), so nothing fails there today; the first `/spark:init` (or C1a's seed) lists the four and B13 fails all four:
three I²S data inputs the firmware drives from reset, and one input the **module** pulls up. C3's `holds_level` ("a current
load … open is off") describes neither. The vocabulary needed is *why floating is harmless here* — a load, a module-side pull,
gated by another pin — or a module-side pull declared as a fact the seed reads (`host_parts` exists for host-side pulls;
nothing exists for module-side ones). Data + vocabulary; the bin carries the same amplifier (its rules are hand-written, so it
does not see this).

**MC-6 · The derived half needs no build at all.** Rail names, inputs and host-pulled bus lines are all derivable from the
requirements file and the records before any circuit exists: `design.rails_requested` (`design.py:189`),
`emit_board.power_connections` (`:189`), `rails_without_a_source` (`:386`), `declared_inputs`, `i2c_lines` — and
`needs._power_gaps` (`needs.py:538-568`) already computes the rails for `--requirements`. The documented "after a build, run
init again with `--force`" (init.md:36) and C1a's "after every kept build" both wait for a circuit the derivation does not
need; the one thing a circuit adds is a net the generator invents that no record names, and the generator's rails come from the
same functions. The writer that already holds the picks and records, `parts.py --requirements`, is where the derived half can
be seeded — K46's sequence then has no gap at the point where the person is, and no check becomes a writer (see C1).

**MC-7 (minor) · `check_all` no longer reads the selection for anything.** `check_all.py:356` assigns
`active = boards.definition_path(project)` and never uses it; the surrounding `try` exists for the "boards … not resolved"
note. Not a fault — evidence that `boards/active.json` is an input to no check, which weighs on C6's choice.

**MC-8 (minor, K52) · the wrong kind of wrong.** `boards.py:116` aliases `EXIT_PROBLEMS` as `EXIT_INVALID`, so "no board
selection" exits 1 (problems) where `outcomes.py` would say 2 (could-not-run). `boards.py` predates the three words; K52's fix
should also stop a selection question from ever being a *problem* of the board files.

## The changes, judged

Each against the PO's criteria — testability, diagnosability (where and why, to a person and to an agent), simplicity (remove
before add) — and the four questions asked: mechanism or symptom; does the named test catch the regression; does the message
name where and why; would a simpler removal do.

**C1 · the chain re-seeds (C1a) / the derived half leaves the file (C1b).** C1a treats the symptom (a stale snapshot) by
adding a second seeding moment inside a *check*: `check_spine` would write `.spark/rules.json`, which `check_all` then judges
against — a check writing another check's input, and a second writer of one file (init and the chain), so a wrong rule has two
possible authors. Its test catches the K46 regression. Its message is better than today's and names the command. Simpler:
MC-6 — the derived half is seeded by `parts.py --requirements`, already a writer (`OPERATIONS` says `writes`), with the picks
and records in hand; the "after a build" step leaves init.md, README and journey.md as C1a proposes, and nothing new runs in the
chain. C1b addresses the mechanism (no snapshot) and is the right direction, but it does not reach MC-1: with zero derived
rules `compare_design` still answers could-not-run; C1b must carry MC-1's decision or it moves the fault from "stale" to
"permanently unexercised" for a sensor-only board. C1b's cost for the bin is named (a hand list stays; the bin has no
requirements file). One trap for C1a as written: `check_spine --keep` on a project with no `.spark/rules.json` (plant-alarm)
would create rules where none were asked for and B13 would fail four pins the next `check_all` (MC-5) — say whether `--keep`
seeds only an existing file.

**C2 · a declared signal is reported, not refused; a non-note stderr line is could-not-run.** Mechanism, yes: severity by
content, not channel. The two named tests catch both regressions; `tests/test_routes.py:151` keeps the example clean. The
schematic detail names the signal and whose it is — add "left for you to wire" so the sentence says what to do. Two
weaknesses in the sketch: (1) "lines starting `note:`" — today all five notes start with `note:` (`emit_board.py:1128-1147`),
so the split works only once note 1 leaves stderr, and it is a string-prefix contract between two files with no shared
constant; a shared `NOTE_PREFIX` in `emit_board` that `check_spine` imports, or notes on a channel of their own, makes it a
tested contract. (2) The ground "the build would stop on them" is E for the unsourced rail (above) and H for the other three;
and `--requirements` pre-warns three of four — so keep the four as PROBLEMS because they are circuit gaps, not because
something else already said them. A consequence to state: under C2 a board with a dangling assigned pin records `built`
(`check_spine.py:625-627` keys on `EXIT_OK`); acceptable, since `built` vouches for the records, but say it in the card. The
PO's alternative (`signals[].to`) adds a field; the recommendation adds none — agreed.

**C3 · a record can say an input defines its own level.** Addresses the vocabulary gap, but for one cause. MC-5 shows two
more in spark's own library: a module-side pull-up (the DFR0954's `SD`) and a data input gated by another pin (its I²S lines).
Name the key by what the check does with it — *why floating is harmless here*, with `verified`/`source` as `body_mm` has — or
add a module-side pull declaration the seed reads, which also makes `i2c_lines`' "carries its own pull-ups" a fact rather than
an inference from the absence of a `host_parts` entry. The tests named would catch the regression. The `//` note that would
name a left-out pin is rewritten on every `--force` (MC-2) — a per-entry note survives, a template note does not. "Nothing
removed" is right; the record change lands in spark's library for the amplifier, which the bin also uses (its hand list is
unaffected).

**C4 · one table for what each owed fact does to the chain.** The right shape, and its named test —
`check_spine.run` per missing fact, asserting the stopping stage — is exactly the test that would have caught the
diagnosis's own wrong row; keep it. The row must read `pin_order_proof: ("parts", "stops — the loader refuses the record as not
meeting the contract")` (E above), and the `--requirements` policy "refuses exactly the facts whose consequence is 'stops'"
then refuses it — which is what happens today by the `owes` route, so the behaviour is unchanged and the sentence becomes
true. Before any of that, MC-3 is a decision: fold `validate`'s `pin_order_problems` into "owed" (buildable, warned, marked —
#102's words) or keep it a contract failure and let `--audit` say "broken", not "owes". Simpler removal inside C4: `_about`
(`parts.py:113-117`) exists to split "owed" from "broken" by string-matching problem sentences; a table that names the facts
makes the split by key, and the regex goes.

**C5 · one reader, one namer.** Sound and small. The cycle argument holds (`emit_board.py:42`), and `design.py:22-26`'s
"that is `emit_board`'s" is already overturned by two non-emitting callers that import `emit_board` for the name alone
(`init_project.py:94`, `sim_project.py:94`). Fold `needs._name_after` (`:425-427`) too, or pin that it agrees with
`component_name` — it is the same transform on a different id and nothing tests the agreement. The three named tests catch the
three regressions; the messages already exist and move to where the person is. Nothing breaks for any project.

**C6 · the board changes in one place.** The recommended variant (write `active.json` from `--requirements`) keeps two
statements and synchronises them — a symptom fix with a good line. The alternative (`boards.active_id` falls back to the one
requirements file's `board`) removes a statement, and MC-7 shows no check reads the selection — but it is also safe for the
bin **today**, because the bin has no requirements file and keeps `active.json`; its `Makefile:49-53` keeps working under either
variant. The real cost of the alternative is documentary: `boards/README.md:21` ("THE one place it is chosen") and the bin's
`CLAUDE.md` have to say "for a project without a requirements file". With part 2 (no MCU, two MCUs) ahead, the recommended
variant is the smaller change now; the alternative is the smaller system later. The named test is right for either.

**C7 · five small contract fixes.** All five address mechanisms, each test catches its regression, each sentence names the
field and value. Additions: K52 — also return could-not-run, not `EXIT_INVALID`, when the question was "is this file valid" and
the answer "no selection" (MC-8); better, a blank marker and no question. K63 — prefer the *refuse* variant ("no folder at …;
run `--needs-set` first, which makes it") and reorder `idea.md:13-15` so `--step S` follows `--needs-set`: no new behaviour,
one half-state removed, and the store never lists a folder that is not there. K50 — whether Wokwi accepts a hyphen in a custom
chip id stays H (not searched here; "research only what decides" — it decides only the regex's last character and the PO can
ask for the lookup). K51 — normalising where the sentence is read is the simplest fix; agreed.

**C8 · `--keep` builds the kept `board.tsx`.** The decision is the PO's (#44). Mechanism, yes; the stage line with the line
count is good diagnosability; not recording `built` when the file differs is right and must be said on stderr as proposed. The
sketch has MC-4's hole: a hand-edited file's local imports are not in the work folder. Build in place instead — the project
folder already holds the imports and the toolchain (`build.md:74`'s remedy) — and copy nothing when a `board.tsx` exists; the
work folder then serves only the diff. Flipping `tests/test_check_spine.py:316-331` is right and should be named in the card.
Irrigation's committed board differs from the regeneration in 13 lines (the diagnosis's E), so after C8 irrigation records no
`built` event until its `board.tsx` is regenerated — say that to the PO.

**C9 · the note on its own line in every outcome.** A chore, agreed; the extended test catches it; the exit code stays the
chain's (D the PO, 2026-10-08).

## What breaks for current users

**The bin** (`~/Development/smartbin-local`: hand-written `board.tsx`, `boards/active.json`, hand-written
`.spark/rules.json` — `must_not_float` `MotorDriver BIA/BIB`, `i2c_buses` `SDA, SCL`, rails `MOTOR6V, GND, V33`; no
requirements file; `Makefile:49-53, 94-96` read the board through `boards.py`). C1a: no effect (no `--keep` run is possible
without a requirements file); C1b: must keep the hand list — the diagnosis says so, and MC-1 does not bite (the list is
non-empty). C2, C4, C5, C7, C9: no effect. C3: a key added to the library's amplifier record does not reach the bin's hand list.
C6 either variant: no effect today; the wording "THE one place" in `boards/README.md:21` and the bin's `CLAUDE.md` needs the
qualifier under the alternative. C8: unreachable for the bin (no requirements file), but MC-4 is the bin's shape of board.

**Irrigation** (`irrigation.requirements.json`; committed `board.tsx` differing from the regeneration in 13 lines; four
hand-written `must_not_float` entries failing B13; `FireBeetle2Esp32S3.tsx` kept). C2: `check_spine` exits 0 for the first
time (the only note is `STATUS_LED`). C1a: a `--keep` run re-seeds the four valves from `direction: "in"` unless C3's key is in
the DFR0457 record first — order C3 before C1a, or the FAIL returns on the first build after the entries are deleted. C1b or
MC-6's variant: `needs.requirements` reads only `requirements.json` (`needs.py:381`; K40), while `init_project.design_in` globs
`*requirements.json` — a seed at `--requirements` would write a second file for irrigation unless K40 lands first or the seed
globs as init does. C3: one record edit, four entries deleted by hand (they are the person's — RC-8 corrected — so the
deletion is theirs to make). C8: `dist/` becomes the committed board's build and `check_all` judges the board the person has;
no `built` event is recorded while the file differs. C4: irrigation's project records carry `pin_order_proof` (P81,
`140900d` 2026-10-03), so MC-3 does not stop it.

**Plant-alarm** (`requirements.json` on `xiao-esp32-c6`; `.spark/needs.json` only — no rules, no brief, no `active.json`;
`board.tsx` wiring four amplifier inputs straight to MCU pins). Any seed — `/spark:init`, C1a's `--keep`, C1b's check-time
derivation — lists `Max98357aDfr0954.BCLK/LRC/DIN/SD` under `must_not_float`, and `rules-vs-netlist` fails all four under B13
(MC-5): a new red on a project that is unchecked today. C3 as named does not describe these pins; the broader key or a
module-side pull declaration does. C6 alternative: `boards.py --id` would answer `xiao-esp32-c6` where it fails today (no
selection); the XIAO still stops at the footprint stage (K30), which is said, not refused. C2, C4, C5, C7–C9: no effect.

## Searches

none. The one open web question (whether Wokwi accepts a hyphen in a custom chip id, C7/K50) stays H; it decides only the
regex's last character and is the PO's to ask for.
