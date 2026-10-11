# P158 part 2 — refuter, round 1: the design and the plan

**What this is.** Adversarial round 1 on `docs/archive/2026-10-10-p158-architecture-design.md` ("the design", 2,426 lines) and
`docs/archive/2026-10-10-p158-plan.md` ("the plan", 2,288 lines). Both read whole. Written 2026-10-11 against spark 0.8.1 at main
`5acbe42` (E `git log -1` → `5acbe42 2026-10-10 22:26:37 +0200 Merge pull request #129`; `.claude-plugin/plugin.json:3`
→ `"version": "0.8.1"`). Nothing decided here: each finding is a proposal, and §7 lists what the PO must decide.

**What I read besides the two files.** Every `scripts/*.py` range either file cites (listed in §1); `tests/test_json_contracts.py`,
`tests/test_check_spine.py:314-332`, `:843-852`, `:1083-1099`, `tests/test_boards.py:312-382`, `tests/test_parts.py:1685-1692`;
`tools/mutate.py:84-92`; `tools/circuit-to-wokwi/lib/board.ts:25-70`; `docs/guide/agents.md:68-88`, `:129-133`, `:295-335`,
`:460-462`; `scrum/README.md:5-9`, `:210-236`; `scrum/WORKING_AGREEMENTS.md:15-19` and its headings; `scrum/VISION.md:28-32`;
part 1's `proposal.md:511-591` (the priority rule) and every CH block's rank, size and *depends on* line (extracted by a
script); CH-38 and CH-66 whole; `council/completeness-critic.md:118-175`; the bin's `Makefile` spark lines and
`git ls-files .spark`; irrigation's `git ls-files`, `.gitignore`, `sim/`, `boards/`; plant-alarm's folder and
`requirements.json`. Read-only `gh`: titles and states of 87 issues, the bodies of #41, #45, #50, #81, #102; the
sub-issues of #94 and #123; both boards' status counts.

**What I ran.** Greps, `sed -n`, small read-only `python3` passes over spark's files (an AST pass over the imports, a
count of mutation rows, the library boards' keys), and **one spark command, on scratch copies only**:
`check_spine.py requirements.json` in a copy of plant-alarm under `<scratch>`, with `SPARK_HOME`, `HOME` and `TMPDIR`
each pointing into `<scratch>` (the store copied from the PO's on 2026-10-11 with `cp -R`). Nothing written anywhere
else. No irrigation run: its `node_modules` is 708 MB (E `du -sh`), so its exit-1 claim stays as the design states it, not
re-measured.

**Tags.** E a pointer or a command and its output · H a claim with its source · D a decision (who, when) · — unknown.

## 1. Claims about today's code, opened and quoted

Verdicts: **holds** · **partly** · **refuted** · **could not open**. Every pointer below opened; none failed to open.
Line numbers are at `5acbe42`.

### 1.1 Partly or refuted — with the sentence to change

| # | claim (where) | pointer | verdict | the line read | change |
| --- | --- | --- | --- | --- | --- |
| R1 | plant-alarm "stops at `schematic` on `power.io_volts`" (design §7.6 *before*, §7.3 "Its schematic stops on `power.io_volts`"; plan I0 baseline, I3 "the whole", R4's reason for C49, C49's pass line) | E my run on `<scratch>` copies, 2026-10-11 | **refuted** | `[ok  ] schematic        11 trace(s) written` · `[!!  ] schematic-notes  note: DFRobot DFR0954 MAX98357A I2S amplifier.SPK_N drives net.SPEAKER_N and nothing on this board receives it …` · `[????] footprint        no footprint could be generated for xiao-esp32-c6` · `the chain is broken` · `exit=1` | "plant-alarm's schematic builds today (11 traces). It stops at the footprint, owing `physical.header`, and exits 1 because two circuit-gap notes from `emit_board` (SPK_N, SPK_P: nothing receives them) become PROBLEMS through `check_spine.py:374-375`. CH-66's `io_volts` datum changes nothing for it: `io_volts` stops only a part that sizes a resistor from it (`docs/guide/agents.md:316-318`, the LED case)." |
| R2 | the S3's two `verified: false` board facts reach "nowhere, except as rail-load notes" (design §4.2 producers table) and "reach no listing" (§13.3, Found on the way) | `boards/firebeetle2-esp32s3.json:133`; `emit_board.py:507`; `check_physics.py:304-312`; `check_all.py:149` | **refuted** for `regulator_3v3_a`; holds for `deep_sleep_ua` (no reader in `scripts/`, E grep) | `:133 "can_supply": "regulator_3v3_a",` · `emit_board.py:507 rail["supplies"].append(dict(current_of(part, supply.get("can_supply")), who=who))` · `check_physics.py:309 "draws %s of %s, resting on figures nobody has verified: %s"` · `:311 severity="needs-measurement",` · `check_all.py:149 unmeasured=of(NEEDS_MEASUREMENT))` | "`power.regulator_3v3_a` already reaches `check_all`'s `unmeasured[]` through physics' rail-supply rule whenever `check_all --project` sums the loads; only `deep_sleep_ua` reaches nothing. A separate board-facts producer would list the regulator twice, under two fact names." |
| R3 | `footprint_module` is "carried and read by nothing" (design §4.4 row "keys carried and read by nothing"; plan C30 *removes*; part 1 CH-22) | `scripts/boards.py:67`, `:395-396`; `boards/README.md:71` | **refuted** | `:67 REQUIRED_FOR_FAB = ("footprint_module", "footprint_export")` · `README.md:71 Until footprint_module and footprint_export are filled in, --validate --for-fab fails` | "`footprint_module` is read by `--for-fab` today. It goes in C37's commit, which replaces `REQUIRED_FOR_FAB`, never in C30's: removed first, it turns `boards.py --validate --for-fab` red on both library boards, and with it the bin's Gerber recipe (`Makefile:182`)." |
| R4 | irrigation's `sim/WHAT-THIS-CANNOT-SHOW.md` is the corpus I4 (b) checks against `check_all`'s `assumptions` (design §12.3 I4 (b); plan I4, C39) | E `ls ~/Development/irrigation/sim`; `git ls-files sim` | **refuted** (absent) | `board.json chips diagram.json flash-with-firmware.bin micropython-esp32s3.bin runs scenarios serial-debug.log … wokwi-mapping.json wokwi-run.log wokwi.toml` — no `WHAT-THIS-CANNOT-SHOW.md`, tracked or not | "The scratch copy first regenerates `sim/` (`check_spine … --sim-dir sim`; `--keep .` does not copy `sim/`, #50 P116), and the pass line names the expected sentences, written before the run; otherwise 'every one present' passes on an empty set." |
| R5 | `store.PLUGIN`, "which nothing reads" (design U2, §4.4) | `scripts/store.py:33`; `tests/mutations/sprint-10-p95-1.json:9` | **partly** | `:33 PLUGIN = Path(__file__).resolve().parent.parent`; the mutation row's replacement: `for path in sorted((store.PLUGIN / \"catalog\").glob(…))` | "No script reads it; one mutation row's replacement names it. The removal rewrites that row in the same commit, or the row's mutant fails for a missing attribute instead of for the behaviour it was written to test." |
| R6 | "seven derivations of the plugin folder" (§3, §4.4) | `scripts/check_vendor_pins.py:106-108` | **partly** | `:106 #: spark's own folder, defined once in boards.py` · `:108 PLUGIN_ROOT = boards.PLUGIN_ROOT` | "six derivations (`store.py:33`, `boards.py:38`, `:153`, `parts.py:45`, `tools.py:43`, `fab.py:27`) and one alias (`check_vendor_pins.py:108`)". |
| R7 | the locator example `plugin:boards/firebeetle2-esp32s3.json#/physical/header_order/0/13` (§5.2; §5.5; plan C30 *prints*) | `boards/firebeetle2-esp32s3.json`, `physical.header_order` | **partly** | E my `python3` read: `['//', 'row_18', 'row_14'] [77, 18, 14]` — an object keyed by row, not an array | "`#/physical/header_order/row_18/13`" — and the pointer test reads the real shape, comment key `//` included. |
| R8 | "the twelve per-shape tests of `tests/test_json_contracts.py:84-195`" (§4.4) | `tests/test_json_contracts.py` | **partly** | the file has 188 lines; its 12 `def test_` sit at `:101`–`:181` (E grep) | "`tests/test_json_contracts.py:82-188`, twelve tests at `:101-181`". |
| R9 | the named exceptions to the import rule: "`parts` importing `drawer`, `needs`, `cost` and `tools`, and `boards` importing `emit_footprint` and `parts`" (§4.3) | `scripts/parts.py:143`, `:430` | **partly** (the count of 17 holds: E my AST pass, 17 function-local-only edges; one cycle of nine modules) | `:143 import emit_footprint` · `:430 from compare_design import PULLUP_MIN_OHM, PULLUP_MAX_OHM` | "…and `parts` importing `emit_footprint` and `compare_design`, both upward under §4.3's order; the frozen list is all 17 edges, by name." |
| R10 | "`outcomes.py:2-7` says three" against W1's four (§13.3, J1) | `scripts/outcomes.py:21-22` | **partly** | `:21 #: What --json says, and what check_all aggregates. skipped is check_all's own fourth` · `:22 #: word for a check that was not asked for, which is not the same as one that could not look.` | "outcomes.py restates the fourth word in its own comment (`:21-22`); DP9's amendment edits it in the same commit (W16)." |
| R11 | "the 2 `verified: false` facts … whether these two reach a verdict: —" (§4.2) | as R2 | **settled** | as R2 | Replace "—" with R2's answer. |
| R12 | plan C12: "whether the bin's or irrigation's `rules.json` states a fabrication override is —" | E `python3` read of both files | **settled** | bin: `fabrication = None`; irrigation: `fabrication = {}` | "Neither states an override, so C12 changes no number either project prints." |
| R13 | plan C24 prints "91 of 110 drawer entries say nothing of what they do" | E `python3` over the drawer of the store copy, 2026-10-11 | **partly** | `110 entries; 98 with no function` | Two measures under one sentence: part 1's 91 is "reached by no need"; "say nothing of what they do" counts 98 on the same store. The sentence names the measure it prints. |
| R14 | "A run without `--keep` still writes nothing into the project (E `check_spine.py:682-688`)" (§4.5) | `scripts/check_spine.py:682-688` | **holds today, false from I4** | `:682 if args.keep:` … `:686 shutil.rmtree(workdir, ignore_errors=True)` | From I4, `cli.run` records every stage run "when there is a stage and a project" (U7), so a run without `--keep` writes `<project>/.spark/state/`. The sentence is amended in C41's commit. |

### 1.2 Holds — opened and quoted

| claim (design or plan) | pointer | the line read |
| --- | --- | --- |
| three outcomes, `ok` unreachable while unchecked | `outcomes.py:32-43` | `:43 return PROBLEMS if problems else (COULD_NOT_RUN if unchecked else OK)` |
| envelope version 1 | `outcomes.py:65-74` | `:73 return {"envelope": 1, "tool": tool, "op": op, "status": status_of(problems, unchecked), "data": data,` |
| local aliases sanctioned; `step`; `unmeasured`'s definition | `outcomes.py:9-13`, `:77-79`, `:54-56` | `:11 which is fine as a local name for "ran, and the answer is no"` · `:55 a property of the BOARD: a real finding that needs a number nobody has taken` |
| the copper counted | `check_spine.py:433-446` (count at `:419`) | `:442 if traces == 0:` |
| atomic, idempotent write; private refused in git; one network door | `store.py:138-160`, `:202-219`, `:330-362` | `:140 written to .part and renamed …` · `:212 if private and inside_git(target):` · `:347 spark's one door to the network (§6.5)` |
| "no selection" exits 1 | `boards.py:537-539` | `:539 return EXIT_INVALID` |
| three folders up; `SCRIPTS.parent` | `check_physics.py:540`, `compare_design.py:281`, `check_spine.py:330` | `rules_path = Path(args.rules or circuit_path.parent.parent.parent / ".spark/rules.json")` · `project = project or SCRIPTS.parent` |
| the home read at import | `tools.py:47-48` | `:47 PERSONAL = store.place("tools")` |
| one 187-line `run` | `check_spine.py:319-505` | `def run(` at `:319`, last `return` at `:504` |
| stderr → PROBLEMS; substring classifier | `check_spine.py:374-375`, `:216-221` | `stages.append(Stage("schematic-notes", PROBLEMS, emitted.stderr.strip()))` · `CONVERTER_HAS_NO_PART = "no Wokwi part is mapped"` |
| `--for-fab` checks two keys | `boards.py:391-399` | `:395 for key in REQUIRED_FOR_FAB:` |
| `Answer` | `parts.py:233` | `namedtuple("Answer", "data lines problems unchecked next truncated", …)` — every `Answer(` call in `scripts/` passes only `data` and `lines` by position (E grep), so fields added after `lines` keep the 28 handlers working, as U1 says |
| `_say`; `main`'s mapping | `parts.py:2171-2186`, `:2188-2212` | `:2176 said = envelope("parts", op, …)` · `:2201 answer = globals()["_op_" + …](args, project)` |
| `_read_json`; `_parse`'s `None` | `boards.py:170-176`; `parts.py:1270-1274` | `:174 return json.loads(path.read_text())` · `:1274 return None` |
| advisories into `unmeasured` | `check_all.py:236-240` | `:240 unmeasured=of(ADVISORY))` |
| a read falls back, a write never | `boards.py:150-152` | `:152 never does, because writing a stranger's resolved board into the plugin is not a fallback.` |
| `LIBRARY`, `project_root` (and its docstring drift), `PLUGIN_ROOT`, `project_or_library` | `boards.py:38`, `:135-147`, `:153`, `:156-167` | `:137 the nearest directory up the tree holding boards/ or .spark/` against `:142 (directory / PROJECT_BOARDS_DIR / SELECTION_NAME).is_file()` |
| `is_library`, `LIBRARY_NOTE` | `design.py:151-158` | `:153 return Path(project).resolve() == boards.PLUGIN_ROOT` |
| prose and `LIBRARY_NOTE` on stdout; the `unverified` key | `assign_pins.py:434`, `:438`, `:457-467` | `:438 print(design_library.LIBRARY_NOTE)` · `:463 "unverified": open_questions,` |
| the three writers into spark's folder | `parts.py:1296-1305`; `check_vendor_pins.py:178-198`; `sim_project.py:162` | `:1296 … else LIBRARY)` · `:194 target.write_text(header)` · `shutil.copy2(target / binary.name, binary)` |
| `CHAIN_FACTS`, `owes`, `_about` | `parts.py:97-117` | `:98 CHAIN_FACTS = ("footprint", "pin_order", "pin_order_proof", "body_mm", "simulation")` |
| the lock in the temp folder; the suite guard | `store.py:186-187`, `:40-43` | `:187 lock_file = Path(tempfile.gettempdir()) / ("spark-%s.lock" % named)` · `:40 if "unittest" in sys.modules:` |
| stage names as literals; `left_off`; verdict lines | `check_spine.py:546`, `:533-541`, `:550-555` | `"  idea -> parts -> pin map -> schematic -> footprint -> build -> simulation"` |
| the board tables | `boards.py:62-107` | `:62 REQUIRED_KEYS = ("schema", "id", "name", "chip", "wokwi_part_type",` |
| the converter-bundle digest test; `BoardDefinition`; `wokwi_is_stand_in` read by no script | `tests/test_check_spine.py:845-851`; `lib/board.ts:27-68` | `:35 wokwi_is_stand_in?: boolean;` — no reader in `scripts/` (E grep) |
| the parser raises; the `--describe` test | `parts.py:1553-1558`; `tests/test_parts.py:1688` | `:1557 raise BadArgument(message)` |
| `check_all`'s and `check_spine`'s `main` and `report` | `check_all.py:444-476`; `check_spine.py:668-688` | `:464 print(json.dumps({"tool": "check_all", "status": overall,` |
| `parts.unverified` reads parts only | `parts.py:834-836` | `:836 … any_record(part_id, project), part_id)]` |
| `--assume-missing-sizes` on every run; the header comment | `check_spine.py:358-361`; `emit_board.py:591-601` | `"--project", str(project), "--assume-missing-sizes"],` · `" * NOBODY HAS MEASURED: %s."` |
| `placeholder_components_in`; no image; `mismatch`; `skipped`; prose under `--json`; the reach into `check_bom` | `check_all.py:152-185`; `sim_project.py:173-176`; `check_vendor_pins.py:230`; `check_all.py:59`; `check_footprints.py:547-555`; `check_all.py:263-273` | `:230 result = {"board": path.stem, "status": "mismatch" if problems else "ok",` · `:59 SKIPPED = "skipped"` · `:263 rows = check_bom.read_bom(Path(inputs["package"]))` |
| the "not yet true everywhere" list | `docs/guide/agents.md:297-333` | `:297 **Not yet true everywhere:**` |
| the stale docstrings | `tests/test_json_contracts.py:4`, `:13` | `Ten scripts declare --json` · `five different envelopes` |
| 2026-09-30's verdict, "do not refactor", stopping rule | `docs/archive/2026-09-30-refactoring-architecture.md:8`, `:112-113`, `:126-130` | `## The verdict: this is not a refactoring project` |
| an all-skipped run is 2; `active_id` reads only `board` | `check_all.py:437-440`; `boards.py:198-210` | `:440 return COULD_NOT_RUN` · `:199 board_id = selection.get("board")` |
| the documented example; "seconds" | `commands/build.md:80-90`, `:2` | `the chain runs end to end` |
| a placeholder footprint's findings become could-not-run | `check_footprints.py:458-493` | `:494 severity="could-not-run"))` |
| layers as a literal; `PLACES`; `PLAIN`; `BUILD_FACTS`; the stand-in sentence | `store.py:71-81`, `:61-63`, `:99`; `parts.py:903-915`, `:502-504` | `:78 rows += [("shelf", place("shelf"))] if kind == "parts" else []` |
| the literal store paths in the pages | `agents/parts-researcher.md:57-58`; `commands/research.md:104-105` | `store at ~/.local/share/spark/catalog/<id>.json (never into the plugin)` |
| `wokwi-mcp` off; `claude mcp add`; CLI against MCP; Python 3.9 | `data/tools.json:164-167`; `tools.py:360`; `docs/mcp.md:3-5`; `docs/guide/agents.md:70` | `"kind": "mcp", "on": false,` |
| "refusing rather than guessing"; the limits; W1's four words | `scrum/VISION.md:30`; `scrum/README.md:7`; `scrum/WORKING_AGREEMENTS.md:17` | `Four outcomes, never two: ok · problems · could-not-run · skipped.` |
| P41's test; `keep_into`; init's promise; the import-time constants | `tests/test_boards.py:314`; `check_spine.py:637-665`; `init_project.py:192-198`; `copper.py:40`, `:53`; `emit_board.py:114-116`; `emit_footprint.py:59` | `:197 process. Stating one moves both the check and the generator` · `:40 COPPER_THICKNESS_MM = fab.process("copper_thickness_mm")` |
| the plan's further pointers | `needs.py:122-123`, `:250-257`, `:287`, `:326-331`, `:425-433`, `:511-512`, `:612`; `parts.py:101-104`, `:185`, `:517`, `:658-660`, `:879`, `:1277-1282`, `:1631`, `:1955-1956`, `:2088`; `boards.py:476`; `cost.py:110`; `tools/mutate.py:88`; `check_physics.py:309-310`, `:471-478`; `compare_design.py:254-259`; `init_project.py:485`; `tests/test_check_spine.py:316-331`, `:1085-1098`; `tests/test_boards.py:366-369`, `:378-382`; `boards/README.md:21`, `:71`, `:96-97`; `how-it-works.md:37`, `:156-157`; `commands/build.md:41-43`, `:72-74`; `journey.md:195`, `:468`, `:497`, `:913`; `commands/idea.md:11`, `:13-15`, `:25-26`, `:141`; `docs/guide/agents.md:85-86`, `:131`, `:461` | each opened; each line says what the plan says it says (e.g. `tools/mutate.py:88 return result.returncode == 0 and "\nOK" in verdict`; `boards.py:476 marker = "active" if board_id == active_id(project) else "     "`) |
| the bin's spark lines; its tracked `.spark/` | the bin's `Makefile:28-32`, `:49-53`, `:96`, `:182`, `:186`, `:212`, `:220`, `:223`, `:228`, `:232`; `git ls-files .spark` | `:96 python3 $(SPARK)/scripts/boards.py --resolve > /dev/null` · five files: `board.json`, two `cache/*.h`, `project.json`, `rules.json` |
| the counts | E my commands | `wc -l scripts/*.py` → 11578 · 36 test files · 1,713 `def test_` · 37 raw `json.loads(…read_text` in 16 scripts · 16 `def main` · 9 scripts with `--json` · 15 `patch.object` sites on path constants in 7 files · 1,281 mutation rows, 989 on `scripts/` |
| the board state | `gh project item-list 2` / `1`, 2026-10-11 | spark: `{"Discovery":2,"Done":19,"Idea":83,"Review":1}`; the bin: `{"Done":1,"Idea":19,"Ready":3}`; #94 is a sub-issue of #123 (`gh api …/123/sub_issues` → `96 94 99 101 114 93 102 118 119`) |

## 2. The design's decisions against the eight criteria

Each finding: what, the criterion it fails, the pointer, and a proposal (a test, or a decision for the PO).

### 2.1 One word or one exit code that still means two things (criterion c)

1. **`input` lives under two exit codes.** §5.2's kinds table puts `input` in `unchecked` (exit 2) and "in problems only for an
   unknown id" (exit 1). §4.6 refuses A3's design for exactly this — *"'below a target's floor' as could-not-run, with one
   kind under two exit codes"*. An agent branching on `kind` (§5.2's rule) cannot tell from `input` whether to retry
   after fixing a file or to stop on a wrong id. **Proposal:** a ninth word for the unknown-id case (say `unknown`), or the
   PO's Q14 decides it before DP9 publishes the vocabulary. Test: `test_vocabulary.py::test_each_kind_maps_to_one_status`.
2. **One situation, two kinds.** "No board selected" is `decision` (§5.2, §11 K52); a board selected `--as-placeholder`
   and run `--for pcb` is `design` (§5.3, "the problem has kind `design`"). Both mean the person has not chosen the
   board. **Proposal:** a below-floor entry whose basis is person-decided (`generic-board`) takes `decision`, by the
   `decided_by` column §5.2 already uses.
3. **`kept` has four meanings.** The artefact state *kept* (§2: "the bytes differ from what spark wrote"); `check_spine
   --keep` (copies outputs in, which makes them *made*, the opposite state); `parts.py --keep`/`--kept` (a kept
   document); `kept` in `--requirements`' data (`parts.py:2106 "kept": kept`). C56 then prints `board.tsx kept: differs …`.
   **Proposal:** name the artefact state `edited` (the basis is already `edited-after`).
4. **`source` has two meanings.** The artefact state *source* (§2) and every record's citation field `source`
   (`parts.py:661 for key in ("verified", "source"):`). **Proposal:** `foreign` or `unrecorded` for the state.
5. **One target, two flags.** `boards.py --validate --for-fab` "becomes the `pcb` case" (§6.5, C50), and `check_all --for
   pcb` and `check_spine --for pcb` exist beside it. **Proposal:** C50 makes `--for-fab` an alias that prints its new
   spelling, with a retirement date, or keeps one spelling.
6. **W1's fourth word comes back under another key.** `data.checks[].outcome` takes `ok · problems · could-not-run ·
   not-asked` (§5.1) — four words, under the name *outcome*, which is W1's own word for its four. DP9 amends W1 to three
   *statuses*; the four *outcomes* stay. **Proposal:** name the field `asked` (`yes`/`no`) beside the status.

### 2.2 Where a placeholder — or a could-not-run — can still disappear from a verdict (criteria b, d, and the PO's principle)

1. **Removing `placeholder_components_in` silences placeholder footprints for every circuit no recorded run made.**
   §6.3 case 3 gives such a circuit one entry, `unknown-origin`, and nothing else; inheritance can never supply its
   `placeholder-footprint` names. Today `check_all` re-derives them from the requirements files (`check_all.py:152-185`)
   and `check_footprints` turns each into could-not-run (`check_footprints.py:483-494`), the guard against the XT30 case
   (`:464-471`: *"the tool reported a defect about a part that is not on the board"*). After the removal, a fresh clone
   (DP7 (a) makes the state untracked by design), irrigation's existing `dist/`, and every hand-built circuit measure
   placeholder geometry as real. §4.4's condition — "removed only once the inheritance test holds on irrigation's copy,
   because it also covers a circuit that no recorded run made" — cannot be met by inheritance for case 3. **Proposal:**
   keep the function for case 3 (it reads the requirements, which are inputs, not artefacts); test
   `test_a_circuit_no_run_made_still_names_its_placeholder_footprints`.
2. **CH-38's guard is dropped.** Part 1's CH-38 says *"the four circuit-gap notes stay problems because they are gaps"*
   (`proposal.md`, CH-38 block). The plan's C36 says only "its notes values with a kind" and names no test that keeps
   them problems. `emit_board` writes five note classes to stderr (`emit_board.py:1129` a pin no part claims; `:1132` an
   output nothing receives; `:1138` nothing drives a pair; `:1142` "nothing sources net.%s … the board will not route";
   `:1145` "driven by more than one supply"). Mapped to assumptions or notes, the last two answer `ok` over a board that
   will not route or that joins two supplies. **Proposal:** C36 carries part 1's clause and one test per note class:
   `test_each_generator_note_class_has_its_kind` (subTests: declared signal → `unserved`; the four gaps → problem kind
   `design`).
3. **A could-not-run can become an assumption.** The design files #41's nulls as `unstated` entries (§12.6, #41's row;
   §13.1 CH-39 row), and assumptions "never change the status" (§5.3). #41's value line asks the opposite: *"A null
   `nominal_volts` on a rail with capacitors gives a could-not-run finding naming the rail"* (E `gh issue view 41`), and
   `check_physics.run`'s docstring promises it (`check_physics.py:452-454`: *"Missing inputs are could-not-run findings"*).
   No invariant in §7.1 forbids an unchecked item from being re-expressed as an entry. **Proposal:** a sixth invariant,
   "an entry never replaces an unchecked item: a null that stops a rule stays unchecked beside its entry", with
   `test_a_null_that_stops_a_rule_stays_unchecked_beside_its_entry`; and #41 kept as its own card.
4. **The "complete" invariant cannot see the stages that make the circuit.** The read-audit wraps `read_json`,
   `store.records` and the loaders in process (§7.1). `emit_board` runs as a subprocess until C36
   (`check_spine.py:358-361`), `tsci build` and the converter always do, and the journeys skip every step that needs them
   (§10.1). So `test_every_body_reports_every_file_it_read` covers no `build` or `simulation` read — the two stages 2026-09-30
   says no test reaches (`:121-122`). And `check_spine` hands its stages a temp copy of the requirements
   (`check_spine.py:601 (workdir / "requirements.json").write_text(json.dumps(requirements))`), so an audited read is
   `temp:requirements.json`, while §5.6's illustration records `project:requirements.json`. **Proposal:** state in U5 that
   `build` and `simulation` reads are declared, not audited, and said so in `state.py`'s output; make `check_spine` report
   the source file, not its temp copy, with a test.
5. **Intermediate stages print a count, not the entries** (DP10 (a)). In text, an inherited placeholder is a number until
   `check_all` runs; the bin never runs `check_all` (E its `Makefile` spark lines). For the bin, the final verdict is
   never printed. **Proposal:** DP10 says which command is the bin's final verdict, or the count line names the
   command that lists them.
6. **I0–I3 end with placeholders unnamed.** The ledger lands in I4. The plan's global constraint 10 ("every placeholder
   named in the output") and criterion (d) cannot hold at the close of I0, I1, I2 or I3: about 43 cards (plan's size
   table: 13 + 16 + 7 + 7). See §7.

### 2.3 Contradictions inside the design (criteria a, c)

1. **"A source is never overwritten" against `--keep` and `--resolve`.** §6.3 case 3: an output no run made is a *source*,
   and *"spark never overwrites a source without the person's `--force`"*; U5's test
   `test_an_existing_output_with_no_run_record_is_a_source_never_overwritten`. But:
   - `keep_into` replaces `dist/` by design (`check_spine.py:647 dist/ is pure build output and is replaced`), pinned by
     `tests/test_check_spine.py:326-331 test_dist_is_replaced_because_it_is_pure_output` — two tests asserting opposite
     behaviours;
   - I4 (c) itself runs `check_spine … --keep .` on irrigation's copy, whose `dist/` no run made;
   - the bin's tracked `.spark/board.json` is the `board` stage's output with no run record, and §7.6 says it is
     "re-resolved on every `make` as today" (`Makefile:96`).
   Which writer enforces the rule, from which iteration, is unstated; `--force` exists on no card. **Proposal:** the rule
   binds `--rerun` only (I6), and §6.3 says so; or C41 names every writer it binds, with the bin's `--resolve` as a test.
2. **Case 2's printed sentence is false for the whole epic.** The `edited-after` entry says *"it is yours now; spark
   builds it and does not overwrite it"* (§6.3 case 2), while the same section says the build is of the regenerated
   file until CH-35 — which the plan places below the cut (C56). **Proposal:** the sentence says what happens today:
   "spark built the regeneration, not this file — `npx --no tsci build board.tsx` builds yours" (`commands/build.md:73-74`).
3. **"The conversation stays the only orchestrator"** (§4.1) against I6's `state.py --rerun`, which orders and runs stages
   itself (§6.4). The design names "a scheduler before I6" as a warning sign; at I6 it builds one. **Decision for the PO:**
   whether `--rerun` is inside "never behaviour", or only `--dry-run` ships and the conversation runs the list.
4. **`conflicts` is in `Answer` (U1) and in C14's pass line, and not in the envelope** (§5.1's JSON and key table list no
   `conflicts`). The v2 key-set test would either fail or fix the key set without it. **Proposal:** add the row, or move
   CONFLICT lines into `notes` with a subject.
5. **I1 (c) "100 % of items carry a `where` that parses" against constructors that allow `where=None`** for unchecked items
   (U1: `item(kind, sentence, where=None, …)`; only a problem must carry one). A missing tool has no natural root.
   **Proposal:** either every item carries a locator (add a root `tool:`), or the pass line counts problems only.
6. **Test name against rule.** §7.1: "an entry leaves only when its *fact* changes"; the test is
   `test_an_entry_leaves_only_when_its_where_changes`. Identity is `(fact, basis)` without `where`, so a copy from library
   to project changes `where` and keeps the entry. **Proposal:** rename to `…_when_its_fact_changes`, and add
   `test_copying_a_record_keeps_its_entry_with_the_new_where`.
7. **§4.5's "a run without `--keep` writes nothing into the project"** becomes false at I4 (§1, R14).

### 2.4 Interfaces that do not close (criterion e)

1. **`cli.run(…, stage=None)` takes one stage; `check_spine` records four** (§6.1). The interface for a body that runs
   several stages is missing. **Proposal:** `answer.stages: [ (stage, read, wrote, assumptions) ]`, recorded each.
2. **The state is keyed by the requirements file** (§5.6); the bin has none, and its `boards.py --resolve` is a recorded
   stage (§6.1). The key for a design-less project is undefined. **Proposal:** a reserved key (`"-"`) and a test on the
   bin's command lines.
3. **The level of `unknown-origin` and `edited-after` entries is undefined** (§5.3 maps markers to levels; these two
   bases have none). Under `--for pcb` (§6.5's fab row: "`check_all --for pcb`"), a placeholder level would turn every
   hand-built circuit — the bin's — into problems. **Proposal:** state the level per basis in one table, with
   `test_every_basis_has_a_level`.
4. **`Where.layers(kind)` drops `drafts`.** Today's `store.layers(kind, library, project=None, drafts=False)` and
   `records(…, drafts=False, …)` (`store.py:71`, `:84`) take it, and `--need`'s catalog row depends on it.
5. **The `upgrade` field is prose.** §5.2's rule is "an agent branches on `kind`, never on a sentence", yet the way to
   raise each entry is a sentence (`"keep the maker's drawing (parts.py --keep), then parts.py --fact-set"`), while `next`
   carries argv. **Proposal:** `upgrade` as one or more `outcomes.step`s, and the every-argv-parses test covers them (g).
6. **`cli.run` couples every `main` to the store's environment.** I2 (e)'s pass line, "16 of 16 exit 2" under a
   `SPARK_HOME` naming a missing folder, includes `check_physics`, `compare_design`, `check_bom` and `emit_footprint`,
   which read no store. A refusal there is a new failure for a pure check. **Decision for the PO:** refuse only where the
   store is read, or everywhere (the design chose everywhere without saying it is a choice).

### 2.5 Adds before it removes (criterion c)

- I0 removes one thing (`mutate.py`'s verdict from the suite alone) and adds four (the invariant, the layer test, the
  journeys with their data, a snapshot tool).
- I4 runs two mechanisms for one fact on purpose ("until then both run", §15, I4 row), and `REQUIRED_FOR_FAB` stays a
  mechanism of its own beside `PHYSICAL_KEYS`' targets from I3 to I5 (C30 → C50).
- The design's own count of what is added (§17.9) lists eight new concepts; the stopping rule (§4.5) has no line
  that caps them, only warning signs that "nothing enforces" (§17.1).

## 3. The plan's order

### 3.1 Dependency violations

1. **C30 before C37 breaks the bin** (§1, R3). C30 removes `footprint_module`; `REQUIRED_FOR_FAB` still requires it until
   C37, which depends on C30. Between the two merges, `boards.py --validate --for-fab` fails on both library boards, and
   the bin's `Makefile:182` with it. **Reorder:** the key's removal moves into C37, or C37's rule change into C30.
2. **The baseline is taken after the behaviour has changed.** The first slice puts C2 (CH-13) in Build beside C1, with C4
   and C6 in Ready, while C7 — the snapshot every later "the whole" is compared with — waits in Ready (plan, *The first
   slice*). The design's I0 promised "no change in behaviour … byte-equal before and after"; the plan's I0 carries nine
   fix cards. **Reorder:** C7 first, before any card that changes output; C2's STORE-9 fixture recorded in it as it is
   today.
3. **"P100's round A on today's spark" (DP3 (a)) cannot happen** if it is asked in batch 2 (before C14) while I0's nine
   fix cards have already changed spark. The design's own reason — *"A baseline taken after I1 would measure the change,
   not the start"* — applies to I0's fixes. **Reorder:** round A, or its decision, before any fix card.
4. **C49 is above the cut for a reason that does not hold** (R4: "what I5's plant-alarm measurement needs"). The run in §1
   (R1) shows plant-alarm does not need `io_volts`. **Reorder:** C49 back to its rank (41) below C47, or below the cut.
5. **Hard prerequisites the plan adds that part 1 did not have** (part 1's *depends on* lines, extracted):

   | card | part 1's edge | the plan's edge |
   | --- | --- | --- |
   | C14 (CH-16, rank 1) | `—` | C1, C5, C7 |
   | C31 (CH-1, rank 8) | `—` (*"it carries the store's refusal to every `main` itself, rather than waiting for CH-5's reader — R2"*) | C21, C23, C28 |
   | C34 (CH-11, rank 13) | soft CH-1; Q2 | C31 |
   | C33 (CH-4, rank 12) | soft CH-1, CH-26 | C31 |
   | C38 (CH-3, rank 17) | soft CH-1 | C31 |
   | C37 (CH-36, rank 15) | `—` | C30 |
   | C32 (CH-21, rank 6) | soft CH-18, CH-5 | C28 |
   | C30 (CH-22, rank 26) | `—` | C14 |
   | C36 (CH-38, rank 50) | `—` | C23 |
   | C35 (CH-48, rank 53) | CH-16 | C31, C28 |
   | C56 (CH-35, rank 43) | CH-16, CH-26 | + C41 |

   §12.1's promise — *"A fix never waits for a layer iteration it does not need"* — is broken by every row. Part 1's R2
   removed CH-1's wait on purpose.

### 3.2 Priority-rule violations (part 1 §3, `proposal.md:511-591`)

1. **Enabling work pulled up.** Part 1: *"Enabling work is not a key: a change is not pulled up because others prove
   themselves with it (R1: the first version promoted CH-2 for that reason)"*. The plan puts CH-2 (rank 25) at C1, CH-68
   (rank 47) at C3, and two unranked nets (C5, C7) before rank 1, each for that reason (the design §13.2: CH-2 *"first,
   because every iteration's anchors lean on it"*). The design's counter is 2026-09-30's "the safety net, first". Two of
   the PO's documents disagree; **the PO decides**, and DP2 should name the conflict, not settle it.
2. **Rank 1 bundled into the framework.** Part 1 sizes CH-16 S–M, inside `parts.py`. C14 makes it M–L by carrying U1, U7,
   `read_json`, the glossary and the store-design amendment, and uses `parts.py` — 2,214 lines, on 2026-09-30's
   "do not refactor" list (`:114-116`) — as `cli`'s first adopter. The design's DP2 claim *"Ranks 1, 2 and 3 are in Build
   in the first two slices"* does not hold for the plan: C14 is fourteenth, behind three cards it hard-depends on.
3. **Tier 1 waits behind tier 3 and 4.** CH-1 (rank 8; K1: an empty store read as "known, not owned", exit 0) is C31, after
   C15–C29, which include CH-64 (24), CH-23 (27), CH-25 (29), CH-30 (35), CH-32 (36) and CH-58 (66). CH-11 (rank 13, the
   incident of #101) is C34.
4. **"Before rank 1 — decisions and data, no code"** (`proposal.md:578-585`): Q1, Q2, Q3, Q4, Q5, Q6 (with the data
   pass), Q7, Q41, Q44; and *"The risks lens ranks the data pass and these decisions above all code (RISKS rank 1;
   RISKS-2: … from 2 candidates to 6 … no code changed)"*. The plan asks none of these in batch 1; the data pass is the
   last task of C24, in I1 (R11).

### 3.3 Cards that are two concerns, or too large

| card | concerns | proposal |
| --- | --- | --- |
| C2 | a board's stand-in silicon (`boards.validate`) and an interpreter image's chip (`check_spine`'s simulation stage, `flash_image`) | two cards; part 1 sized it "S + S" |
| C14 | envelope 2, `cli`, `read_json`, the renderer, the glossary, the store-design amendment, and `parts.py`'s port | (a) `outcomes` v2 + `cli` with one small `main` (`cost.py` or `tools.py`); (b) CH-16 in `parts.py` |
| C20 | the tally's window and the transcript's U+2028 split | R5 merges them for one file; two concerns, two tests sets — acceptable only if the PO says so |
| C21 | `check_all`'s envelope, `check_bom`'s `run()` and `--json`, and W1's wording — a team rule edited inside a product card | W1's amendment is the PO's (DP9), in its own commit |
| C23 | seven `main`s, sized M (one working day by the plan's mapping) | at least two cards (the four checks; the three generators) |
| C24 | code, and a data pass that writes the PO's real store | the data pass is a task with the PO, before the code (part 1's "before rank 1") |
| C28 | six `main`s, `--describe` for all sixteen, the argv test, `boards.py`'s exit | two cards |
| C30 | the table, the schema generator, five key removals, a page, Q16 | the removals go with the rule that stops reading each key (§3.1, item 1) |
| C31 | the resolver, `context`, the layers table, the `no-project` assumption, `--store`, the store-design amendment, 15 test sites | the resolver and its refusals first (CH-1, CH-10); `context` and `--store` second |
| C39 | `ledger.py` and ten producers in eight modules, with the firmware levels, sized M | M–L or two cards (parts and boards producers; chain producers) — an estimate |
| C41 | `stages.json`, `state.py` module and command, recording in `cli`, the project lock, a schema, the page-order check | the page-order check (CH-41's half) is its own card |

### 3.4 Value lines that cannot fail, or have no pass line

| card / iteration | why |
| --- | --- |
| C7 | characterisation: the journeys are written to today's answers, so "green with today's statuses" passes by construction; the hypothesis ("whole enough") has no measure |
| C49 | "plant-alarm's schematic `ok`" is already true (§1, R1) |
| C51 | "the simulation reached" with the S3 is already true for the documented example (`commands/build.md:80-90`); only the entry is new — the pass line should be the entry alone |
| C53 | "the PO judges whether the score tracks what matters" — a judgement, not a line |
| C29, C68, C75 | "the council's documentation experts walk it / read it cold. Pass: they can" — a judgement |
| I0, Hf0 (d) | "byte-equal, except lines a fix card names on purpose" — any difference can be named after the run; the expected differences are not listed before it |
| C3, I0 (a) control | "the control red → recorded; C3 stays": both outcomes leave the plan unchanged |
| I1 (e) | "the size is reported, not promised" |

### 3.5 Iterations that do not end in a whole that runs

- **I0** ends with a baseline that is not of the start (§3.1, item 2).
- **I3** ends red for the bin between C30 and C37 unless reordered (§3.1, item 1).
- **I4**, if case 3 binds `--keep` and `--resolve` (§2.3, item 1), ends with irrigation's `--keep .` refused and the bin's
  `make` unable to re-resolve.
- **I0–I3** end with placeholders unnamed (§2.2, item 6).

### 3.6 Validated learning: what is missing

1. **No stop branch.** Every refutation re-sizes or re-asks; none stops the layer. The PO said on 2026-10-09 *"lets make
   sure we start finishing more and not starting new epics or bigger things in general"*. **Proposal:** a line at
   re-plan point 1: if I1's rows moved exceed the estimate by half, or a cold agent run does not use the envelope, the
   layer stops after I1 and the fix lane continues alone.
2. **The riskiest belief is tested last.** H1 (agents act on the JSON alone) and the ledger's noise for a hobbyist (Q19,
   Q26) are first measured by a model run in I5 (C53), after about 40 cards. `parts.py` already prints envelope 1
   (`outcomes.py:65-74`); a cold run on it costs one run and no code.
3. **Refutations with no consequence:** I2 (a), (c), (d), (f), (h); I3 (a), (c), (f); I5 (c), (d); I1 (b), (d), (e), (g).
4. **#81 P147 undercuts DP8 (b).** DP8 (b) makes spark's version a stale reason. #81: *"a manifest that pins a version
   keeps every user on the cached copy until its author changes the string, however many commits are pushed"* (E
   `gh issue view 81`), and the version policy is open. Between bumps, a generator change leaves every output "current".
   DP8 should name #81's decision as its precondition.

### 3.7 Capacity the plan does not count

- Every pull request gets a council, full by default, *"at most one full council a day"*, *"about 90 M input tokens"* each
  (E `scrum/README.md:217-218`, `:231-232`). 53 cards above the cut are 53 pull requests (constraint 2): at least 53
  council-days if each is full — an estimate from the README's own rule — against the plan's forecast of 17.1 build-days,
  which excludes councils. At the README's figure, 53 full councils are about 4.8 billion input tokens (an estimate:
  53 × 90 M).
- Filing: 37 of the 53 cards above the cut are new (53 less the 16 reused above it, E the plan's R1 and card blocks),
  into an Idea column that holds 83 items, with 19 Done in total (E `gh project item-list 2`, 2026-10-11).

## 4. Coverage

### 4.1 Part 1's CH ids

All 72 are placed by both files (CH-62 left part 1 on purpose: `proposal.md`, "CH-62 leaves the list"). Two placements
lose content:
- **CH-38**: "the four circuit-gap notes stay problems" is in no card or test (§2.2, item 2).
- **CH-66**: its plant-alarm line ("two stops printed instead of one, then none after the data") rests on the
  schematic stop R1 refutes.

### 4.2 Existing cards the plan should reuse or place, and does not

| card | why it belongs here | the plan |
| --- | --- | --- |
| #41 P107 | its null-`nominal_volts` line is the boundary of §2.2 item 3 | "touched by C23 … its own sentences stay its card": not ordered, and its value line is contradicted by the design's `unstated` entries |
| #43 P109 | `check_all` reports the generator's CONFLICT lines — the field C14's pass line requires | "stays its own card": not ordered |
| #45 P111 | an explicit not-applicable value the checks accept (D the PO 2026-10-05, E its body) — a fidelity marker the five levels lack, so a `null-rule` entry for a field that never applies stays in the ledger for ever | not mentioned |
| #50 P116 | `--keep .` does not keep `sim/`: the `simulation` stage's outputs, case 4 (`merged`) and I4 (b)'s corpus depend on it | not mentioned |
| #71 P137 | `init` says only what it did — the same output C28 changes for CH-45's `init` half | not mentioned |
| #75 P141 | "Physics says nothing about the buses and signals no rule examined, so they read as a pass" — a silent pass the ledger's *said* invariant is for | not mentioned |
| #81 P147 | DP8 (b)'s precondition (§3.6, item 4) | not mentioned |
| #83 P149 | a Wokwi chip reused by file time, outside the record's digest — staleness by content (§6.4) does not see it | not mentioned |
| #46 P112 | spark's MCP servers declared, not checked — the design's own Found on the way (`.mcp.json` against `data/tools.json`) and C77's row | not mentioned |
| #97 P161 · #28 P102d · #13 P77 | QA measurement; proofs run as commands; every example regenerated — C1, C5, C7, C53 and C67's ground | #13 and #28 "related" to C67 only; #97 not mentioned |

### 4.3 Lens "missing" items dropped (`council/completeness-critic.md:118-175`)

- **Q-a, "What is better?"** — #17's three words (more parts known, proven by use, fewer requests measured): the
  epic's done line. The plan leaves Q30 ("the epic's done line") gating nothing; "fewer requests" appears 0 times in
  either file (E grep).
- **Q-d, platforms** (macOS, Linux, Windows): 0 mentions in either file; `flock` and the no-`fcntl` branch
  (`store.py:27-30`) decide whether `busy` and the project lock exist at all on a platform.
- **Areas nobody examined**: `skills/spark-reverse-engineer`, `commands/identify.md`, `agents/part-finder.md`,
  `agents/design-reviewer.md`, `data/importers/dfrobot.js` — 0 mentions each (E grep). Three of them are consumers of
  outputs I1 changes: `commands/identify.md:52`, `agents/datasheet-reader.md:53`, `skills/spark-review/SKILL.md:72` call
  `parts.py --unverified`, whose `data.questions` C14 moves into `assumptions`; C14's *changes* names none of them.
  `dfrobot.js` is the importer D8's "automatically from the DFRobot orders" starts from, and C42 does not name it.

## 5. What breaks for the bin, irrigation and plant-alarm — what the plan does not say

| I | project | what changes | pointer | said? |
| --- | --- | --- | --- | --- |
| I0 | plant-alarm | the baseline prediction is wrong; its real stop is the footprint, exit 1, via two gap notes | §1, R1 | no |
| I1 | the bin | every `make`, of any target, expands five top-level `:=` assignments that run `$(shell python3 … boards.py --path/--id/--paths/--get …)` (`Makefile:48-53`, inside `ifneq ($(HAVE_SPARK),)`), and the rule at `:96` adds `--resolve > /dev/null` when it runs. Under §5.8 everything but the value goes to stderr — the `context` line, the verdict, and (from I4) the board's inherited entries — so every `make` prints them five times, six when `.spark/board.json` is rebuilt. I1 (f) pins stdout only | the bin's `Makefile:48-53`, `:96`; design §5.8 | no |
| I1 | the bin | crash paths change exit 1 → 2 (a missing Gerber zip into `check_bom`, `Makefile:186`); I1 (f)'s "identical except one" is true only for the normal inputs | `docs/guide/agents.md:306` | partly |
| I3 | the bin | `--validate --for-fab` red between C30 and C37 | §3.1, item 1 | no |
| I4 | the bin | `boards.py --resolve` against a tracked `.spark/board.json` no run made: refused, or the rule is weaker than stated | §2.3, item 1 | no |
| I4 | the bin | `check_physics` and `check_bom` gain an `unknown-origin` entry for its own circuit for ever, whose upgrade names `check_spine.py requirements.json --keep .` — the bin has no requirements file. An entry nobody can clear teaches the reader to skip the ledger | design §7.6, §6.3 case 3 | the entry is said; that it cannot be cleared is not |
| I4 | irrigation | `--keep .` over an unknown-origin `dist/`: replaced (today) or refused (case 3) | `check_spine.py:647`; `tests/test_check_spine.py:326-331` | no |
| I4 | irrigation | I4 (b) has no corpus | §1, R4 | no |
| I4 | irrigation, fresh clones | placeholder footprints measured as real after `placeholder_components_in` goes | §2.2, item 1 | no |
| I4 | plant-alarm | if C36 maps the gap notes to entries, its verdict moves from problems (exit 1) to could-not-run (exit 2); with part 1's clause it stays exit 1. The plan says "plant-alarm's stop unchanged" without the clause that makes it so | §2.2, item 2 | no |
| I5 | the bin | if `--for pcb` (or `--for-fab` as its alias, C50) reads entries whose level is undefined, the review skill's fab gate (`check_all --for pcb`, design §6.1 fab row) can turn red on the bin's hand-built circuit | §2.4, item 3 | no |
| I5 | plant-alarm | H5 (b)'s "ok in the first sitting" cannot pass for it while its amplifier drives no speaker (R1's notes) — a gap in the PO's own design, not spark's | §1, R1 | no |

## 6. Numbers without unit, population, period or provenance, or estimates not labelled

- **"months of work at today's pace"** (design §17.2): no number, no unit, no source for the pace.
- **"one to three per stage"** and **"One rerun, of seconds"** (§17.6): unsourced, unlabelled.
- **Sizes that disagree:** the design's §12.2 sizes I0a (CH-2) M and I0b (CH-68) S; part 1 sizes them "S, plus machine
  time" and S–M; the plan, S and S–M.
- **"17.1 build-days"** (plan): labelled an estimate, but it omits the binding constraint (§3.7), so the number answers a
  question nobody asked.
- **"91 of 110"** (plan C24): its population and measure differ from the sentence it prints (§1, R13).
- **"about 1.2 KB"** (design §5.1): labelled an estimate; "about" stands where a range would be honest (5 × 200–300
  characters, if A1's 250 is a mean).
- **"16 `main`s × 3 inputs" and "× 4 inputs"** (§11, §12.3, plan C5): the invariant needs one argument template per
  `main` (the "file" differs per script); how many runs that is per `main` — —.
- **"60 s" and "2 s"** (lock wait): labelled H from part 1 (HK). Holds as labelled.

## 7. The strongest case for a different iteration 0, and different first five cards

**The case.** The PO asked for two things on 2026-10-10: "order it by priority, so were fixing what matters", and the
principle "a placeholder may flow through the chain, but it can never disappear from the final verdict". The plan
delivers the principle in I4, after about 43 cards, and its first five cards are three enabling cards and two fixes
(C1 CH-2, C2 CH-13, C3 CH-68, C4 CH-18, C5 the net), while part 1's own rule says decisions and the data pass come before
rank 1, and enabling work is not a key (§3.2). Rank 1 (CH-16, S–M) and rank 8 (CH-1, S–M, made independent by part 1's
R2) are held behind the framework. The PO's real-store guard (#101, an incident that happened, key (d)) lands in I2.
And the single most expensive belief — that agents will act on an envelope, and that a hobbyist will read a ledger —
is measured last.

**A different iteration 0 — "today, measured and said", no framework.** Five cards, in this order:

1. **The baseline, first.** C7's snapshot of the three projects (with plant-alarm's real stop, R1), A3's runs 1 and 2,
   STORE-9 and round 0's fixture as they answer today — and, by DP3, P100's round A on this same spark. Nothing changes
   output before it lands. Pass: the snapshot posted; every later "the whole" diffs against it.
2. **The PO's decisions and the data pass, no code** (part 1's "before rank 1"): Q2, Q5, Q6 with the data pass (RISKS-2:
   2 → 6 candidates, no code), Q44, Q14, DP4, DP5. Pass: answers on the cards; the data pass's before/after on a store
   copy.
3. **CH-1 with CH-11, as part 1 sized them** (S–M and S–M, no layer): `store.home()` refuses a `SPARK_HOME` that is set
   but empty or names no folder, every `parts.py` answer names its store, and Q2's guard. Pass: the P100 refuter's
   reproduction exits 2 naming the folder; #101's line. This closes the incident class in week one instead of I2.
4. **CH-13 and CH-12, the boards' two silent faults** (D8). As C2 and C11, split per §3.3.
5. **The principle, thin: one final line that says what the verdict rests on.** CH-16 inside `parts.py` (rank 1, as
   part 1 sized it), plus CH-32 (the board's stand-in flag read, S), plus `check_spine`'s and `check_all`'s last line
   counting and naming the channels that exist today (`--assume-missing-sizes`, placeholder footprints, `unserved`, the
   stand-ins, `unverified`) — no `state`, no inheritance. It tests HA (the ledger adds no fact) on today's outputs, and a
   cold agent run on it tests H1 and Q19 before any `main` moves.

**What this costs, said:** CH-2 does not precede I1's anchors — so a dead mutant can hide during the first re-anchors
(the design's §15 risk). Answer: CH-2 is S and can be card 6, before the first `main` moves, which is where the risk is.

**What the PO must decide** (none of it is decided here):
- whether part 1's "enabling work is not a key" or 2026-09-30's "the safety net, first" governs iteration 0 (§3.2, item 1);
- whether CH-1 and CH-11 wait for `where` (the design) or land as part 1 sized them (§3.1, item 5);
- whether the principle lands thin in iteration 0 and whole in I4, or whole in I4 only (§2.2, item 6);
- DP3's round A before any fix, or after I0;
- whether `--rerun` is inside "never behaviour" (§2.3, item 3);
- the kinds for an unknown id and for a placeholder board under `--for pcb` (§2.1, items 1–2);
- whether a source is never overwritten by `--keep` and `--resolve`, or only by `--rerun` (§2.3, item 1);
- whether a `SPARK_HOME` refusal stops checks that read no store (§2.4, item 6);
- DP8 (b) together with #81's version policy (§3.6, item 4).

## Searches

None: no web or MCP search was made. Local reads and commands only, listed at the top; `gh` read-only.

## Found on the way

- E · plant-alarm's own design drives a speaker it does not have: `check_spine` says `DFRobot DFR0954 MAX98357A I2S amplifier.SPK_N drives net.SPEAKER_N and nothing on this board receives it` (my run on `<scratch>` copies, 2026-10-11; its `requirements.json` lists `sen0193-soil-moisture` and `max98357a-dfr0954` only).
- E · plant-alarm is not a git repository (`git ls-files` → exit 128), so its "byte-equal before and after" has no revision to pin, and no copy of it is versioned.
- E · plant-alarm's soil probe resolves only from the PO's store: `sen0193-soil-moisture` is in no spark `parts/` file and sits in the store's `shelf/` and `catalog/` (store copy, 2026-10-11), so any measurement of plant-alarm depends on the store copy's date.
- E · `tests/test_boards.py:378-382` `test_validate_and_validate_for_fab_both_answer` asserts `code in (0, 1)`: it cannot catch the bin's fab gate going from 0 to 1, though part 1's completeness critic names it the guard (`council/completeness-critic.md`, RISKS pre-mortem 6).
- E · The PO's store holds `b12-kept-from-the-bin.jsonl` at its root (store copy, `ls`), a file no `store.PLACES` name names (`store.py:61-63`) — the case CH-57's Q45 asks about exists in his store.
- E · On the store copy of 2026-10-11, 98 of 110 drawer entries carry no `function` key (my `python3` pass), against part 1's "91 of 110 reached by no need" — the data pass's size depends on which is meant.
- E · `docs/guide/agents.md:323-325`: with `CLAUDE_PLUGIN_ROOT` unset, *"Python never starts the script"* — no `cli.run` can answer that case, so I1 (g)'s "the exception list deleted" cannot delete item 3 whole; item 5 (an unknown id exits 1) also stays by D the PO 2026-10-04.
- E · `boards.py:476` calls `active_id(project)` once per board inside `--validate`'s loop, so a project without a selection fails every board with the same `BoardError` (part 1's CH-21 half; noted because C32's "computes the selection once" also fixes a repeated read).
- H · `check_spine`'s `design_handed_to` (`check_spine.py:558-560`) rewrites the requirements into the work folder before any stage reads them; whether that rewrite differs from the project's file for irrigation (`irrigation.requirements.json`, one board key) is —, and it decides whether the state's digest of the design means anything.
