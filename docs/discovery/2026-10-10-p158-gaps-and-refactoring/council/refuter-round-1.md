# P158 part 1: refuter, round 1, on `proposal.md`

Written 2026-10-10 by the adversarial refuter (round 1), against spark 0.8.1 (main `a8aa34d`, E `git log -1` →
`a8aa34d 2026-10-09 17:13:40 +0200 Merge pull request #122`). I did not write the proposal. I read it whole (1,527 lines),
along with `catalogue.md`, the six diagnoses and their six verifications, and the eight council lenses. I opened the code at every
line a verdict below quotes. Tags: **E** a pointer (file:line at `a8aa34d` unless another repository is named; a command and
its output; a card); **H** a claim with its source; **D** a decision (who, when); **—** unknown. Paths in spark unless
named. Nothing here decides anything for the PO.

**How I ran things.** The PO's real store was copied to `<scratch>/p158/refuter-1/store` (`cp -R`). I read the copy
with `python3 -I`, not with a spark command, and did not write under the real store. I ran one spark command,
`python3 ~/Development/spark/scripts/boards.py --paths`, from `~/Development/smartbin-local` **without** the
three-assignment prefix. That breaks the letter of the brief, and I am saying so here. It read only `boards/` folders.
For kind `boards`, `store.layers` adds no store row (`store.py:78`
`rows += [("shelf", place("shelf"))] if kind == "parts" else []`), so it never called `store.home()` and wrote nothing.
Every `gh` call was read-only.

## Verdicts

One row for each root-cause statement and each change. "Line read" quotes what I opened. For **partly** and **refuted**, the last
column gives the sentence to change and why.

### The preamble's two new facts and §1's statements

| target | verdict | line read (verbatim) | the sentence to change, and why |
| --- | --- | --- | --- |
| Preamble (1): "Who removed it: —" | partly | #124 comment 2026-10-10T15:20:33Z: "The stray file, removed 2026-10-10: `.spark/cache/dfrobot_firebeetle2_esp32c6.pins_arduino.h` (untracked in spark main, written by round 0's live check on 2026-10-09) was moved to round 0's scratch project's `.spark/cache/`, where the fixed check keeps it" | "Who removed it: —" → "moved on 2026-10-10 by P179's work (#124 comment 2026-10-10T15:20:33Z), sha256 unchanged". The proposal says it read #124, and the answer is on that card. |
| Preamble (2): "#124 … no lens cites it. CH-4 reuses it." | **refuted** | `gh pr view 125` → "P179: a live vendor-pin check keeps the fetched header in the board's own project, never where the read fallback points, and says which file", OPEN, created 2026-10-10T16:16:29Z. #124 comment 16:16:34Z: "Ready to merge: https://github.com/xmejkal/spark/pull/125 … 1713 tests OK; 19 mutations, every one caught. The merge is the PO's." | → "#124 has its own fix: PR #125, open and ready to merge since 2026-10-10T16:16Z, after its own council. It writes the header to the owning project's `.spark/cache/`, which is spark's own folder for a board spark ships. CH-4 proposes a different place (`<home>/cache/vendor-headers/`), so it does not reuse #124. It replaces the design #124 chose." |
| §1 "The store's identities are spellings" | holds | `store.py:250` `return next((name for name, where in projects().items() if where.resolve() == folder), None)`; `drawer.py:92` `found[path.stem] = json.loads(path.read_text(encoding="utf-8"))` | — |
| §1 "An unset, empty or missing `SPARK_HOME` answers 'known, not owned', exit 0" | partly | `store.py:48` `if os.environ.get("SPARK_HOME"):` … `:52` `return Path.home() / ".local" / "share" / "spark"` | → "An empty `SPARK_HOME` silently reads the default (real) store; a missing one silently becomes a new empty store." The **unset** case is the designed default (`:52`). It reads the real store and answers correctly. |
| §1 "The write lock follows the process, not the data" | holds | `store.py:187` `lock_file = Path(tempfile.gettempdir()) / ("spark-%s.lock" % named)`; `init_project.py:417` `listed = "on your projects list as %r" % store.add_project(project)`; `grep -n locked scripts/init_project.py` → nothing | — |
| §1 "A hold has no operation and two meanings" | holds | `needs.py:308-309` `… entry["count"] - sum(` / `n for who, n in (entry.get("used_in") or {}).items() if who != name) - mine[entry_id]` | — |
| §1 "Where a record goes when it has proven itself has no rule" | partly | `parts.py:1296` `to = Path(to) if to else (Path(project) / "parts" if home in (store.place("catalog"), store.place("shelf")) else LIBRARY)`; `docs/guide/agents.md:126` "**`--promote` copies a project's record into the plugin's own library: never run it unasked.**"; `parts.py:1490` `"catalog → the project's parts/, or the project's parts/ → the plugin's library"` | → "has a documented rule — the plugin's library, which is the maintainer's place (`agents.md:126`, `--describe`) — and that rule is wrong for anyone but the maintainer, because an update replaces the folder." The write is announced in three places. What is silent is the later loss. |
| §1 "Boards are a second record kind with none of the first kind's verbs" | holds | `parts.py:1480` `("skeleton", {"metavar": "PART"}, "write a record to fill in, to the project's parts/", ("writes",), …`; `parts.py:1339` `for part_id in available(project):` (parts only) | — |
| §1 "A pad has three names … tscircuit reads an all-digit hint as a pin number" | holds | `grep -n pad_aliases scripts/*.py` → `boards.py:350`, `assign_pins.py:407` only; `@tscircuit/core` 0.0.1958 (the bin's `node_modules`) `index.js:11653` `if (/^\d+$/.test(hint)) return Number(hint);` | — |
| §1 "The simulator's names for a board's pins are consulted only at the last stage" | holds | `tools/circuit-to-wokwi/lib/mapping.ts:96` `byName[name] = WOKWI_NAMES_PINS_BY_GPIO ? String(gpio) : name;` | — |
| §1 "The chain's verdicts take severity from a channel …" | holds | `check_spine.py:374-375` `if emitted.stderr.strip():` / `stages.append(Stage("schematic-notes", PROBLEMS, emitted.stderr.strip()))`; `:683-684` `for line in keep_into(workdir, args.keep):` / `print("  %s" % line, file=sys.stderr)` | — |
| §1 "Matching has two matchers and the pick consults neither" | holds | `parts.py:1329` `return all(word.lower() in haystack for word in words)`; `needs.py:282` `pick = _resolve(pick_id, known, entries)` (no `candidates()` in `plan_pick`, `:267-335`) | — |
| §1 "The firmware is outside every check — since the PO cut the check on 2026-09-29" | holds | `git show -s 066c4af` → "Petr's call, 2026-09-29: no AI bloat, nothing kept that nothing uses." … "- check_firmware.py: run by neither project; the bin has its own in make check." | — |
| §1 "The docs gate proves … a provenance note, never that it is current" | holds | `tools/check_docs.py:32` `files = [root / "README.md", root / "AGENTS.md"] + sorted((root / "docs" / "guide").glob("*.md"))`; `:173` `return [] if "v%s" % version in readme else [...]` | — |
| §1 "Readers are not symmetrical with writers … a non-UTF-8 record is a traceback, exit 1" | holds | `parts.py:2202` `except (OSError, json.JSONDecodeError) as unreadable:` (a `UnicodeDecodeError` gets through); `grep -c "json.loads(.*read_text" scripts/*.py` → 37 lines in 16 files (my run, 2026-10-10) | — (the drawer, projects and history readers already turn it into a `StoreProblem`: `drawer.py:95-96`, `store.py:240`, `:291`) |
| §1 "The requirements writer has its own loader and a third copy of the naming rule" | holds | `needs.py:609` `held = json.loads(file.read_text(encoding="utf-8")) if file.is_file() else {}`; `:612` `held = held if isinstance(held, dict) else {}`; `:430-432` `def _called(part_id, name):` | — |
| §1 "`check_spine` returns on the island before it reads tscircuit's own error, which names the cause" | partly | `check_spine.py:419` `traces, errors = count_in(json.loads(circuit_path.read_text()))`; `:433-437` the island return; `:439-441` `kinds = sorted({element["type"] for element in errors})` … `"%d error(s): %s" % (len(errors), ", ".join(kinds))` | → "returns on the island before it **reports** the errors it has already read (`:419`). When it does report them (`:438-441`) it prints only their **types**, never the message that names the cause." This changes CH-23 (below): a reorder alone would print a type name. |
| §1 "Each output channel drops what the other carries … `next` is filled by nothing" | holds | `parts.py:2182-2184` `if not answer.lines:` …; `:2017-2020` notes appended to `lines` only; `grep -n "next=" scripts/parts.py` → nothing | — |
| §1 "An exit code means two things in three scripts (… `check_vendor_pins` prints a fourth word, `mismatch`)" | partly | `outcomes.py:11-13` "which is fine as a local name for "ran, and the answer is no", … Scripts import the codes from here and alias the middle one to their own word."; `check_vendor_pins.py:181` "Its own word for "ran, and the answer is no" is `mismatch`; the exit code is the shared"; `boards.py:537-539` `except BoardError as broken:` … `return EXIT_INVALID`; `init_project.py:501` `return EXIT_NOTHING_TO_DO` | → "An exit code means two things in two scripts: `boards.py` maps every `BoardError`, including 'no selection', to 1, and `init` maps 'nothing to do' to 1. `check_vendor_pins` adds a fourth **status word** (`mismatch`) to its JSON, while its exit code is the shared 1." The aliases themselves are the design written down in `outcomes.py:9-13`. |
| §1 "The acceptance bar over-counts" | holds | `tools/mutate.py:88` `return result.returncode == 0 and "\nOK" in verdict` | — |
| §1 Data: "the S3 and the LiPo are held by the bin by hand … history.jsonl 8 lines, all plant-alarm; six entries carry used_in" | holds | my read of the copy: 6 of 110 drawer files carry `used_in` (`1s-lipo-battery-1000-mah`, `dfrobot-dfr0975` → `smartbin-local`; four → `plant-alarm`); `history.jsonl` 8 lines; projects named in it: `['plant-alarm']` | — |
| §2.3 "spark's job is to survive both (one lock beside the data; conflict copies refused by name …)" | partly | `store.py:194` `fcntl.flock(held, fcntl.LOCK_EX)`; `store.py:212-214` `if private and inside_git(target): raise StoreProblem("… what you own stays out of every repository …")` | → "Over a folder sync, `flock` serialises the processes of one machine only. Two machines are kept apart by nothing except the conflict-copy refusal. A private git remote holding the drawer, shelf, projects list or history is refused today (`store.py:212-214`, FEASIBILITY-19) and would need Q28 (b)." |
| §2.3 "an append-only JSONL are the shapes git and folder sync merge best" | partly | STORE-17 (uncited by the proposal): git's union merge "tends to leave the added lines in the resulting file in random order"; "— whether `--tally` or the step window reads line order (not traced)" | → add STORE-17's condition: "safe under a union merge only once no reader depends on line order (—)". |

### The eight shapes (§2.1)

| target | verdict | line read | the sentence to change, and why |
| --- | --- | --- | --- |
| R1 | partly | `store.py:48` as above | The refusal sits "where a write happens" (CH-1), so a read and a dry run still answer from a missing or empty home. See CH-1. |
| R2 | partly | `sim_project.py:162` `shutil.copy2(target / binary.name, binary)` (a compiled chip written beside a library record, inside the plugin; `git ls-files parts` lists `parts/l9110s-module/chip/l9110s.chip.wasm`); `tools.py:47-48` `PERSONAL = store.place("tools")` / `DOWNLOADS = store.place("downloads")`; `tools.py:445` `where.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")` | "what it replaces" names four writers. It omits a third writer into the plugin (chip binaries, K13, `agents.md:119-120`) and a writer into the store that goes outside the door and the lock (`tools.py --on/--off/--pin/--use/--new` → the store's `tools.json`). The proposed "grep test" cannot see where a write lands: 25 direct writes outside `store.py`, most into projects (my grep). PR #125 keeps a deliberate write into spark's own cache for a shipped board. |
| R3 | holds | `parts.py:2202` as above | — |
| R4 | partly | `init_project.py:24` "`project.json` is the brief: the goal, what the design must do (`must`), whose modules to research"; `ls ~/Development/plant-alarm/.spark` → `needs.json` only | The project id goes "in `.spark/project.json`". That file is the person's brief, rewritten "only if it has no answers" (`init_project.py:403`). plant-alarm has none. The id needs its own file or its own writer. Separately, "a plain key enforced on read" leaves the hand `cp` half of K9: `cp x.json x-copy.json` gives a plain stem. |
| R5 | holds | `parts.py:97-98` `CHAIN_FACTS = (…)` with the comment "and no build can place it" | — |
| R6 | holds | `outcomes.py:73-74` the envelope; `parts.py:2176` the only caller | — |
| R7 | holds | `check_spine.py:216` `CONVERTER_HAS_NO_PART = "no Wokwi part is mapped"` | — |
| R8 | partly | `outcomes.py:9-13` as above; `grep -n "EXIT_PROBLEMS as" scripts/*.py tools/*.py` → 6 sites: `assign_pins.py:46`, `boards.py:116`, `check_vendor_pins.py:35`, `init_project.py:43`, `parts.py:223`, `tools/mutate.py:56` | → "exit codes from `EXIT_FOR`; a local alias of the middle code stays the documented design (`outcomes.py:9-13`); the two wrong **mappings** go." A grep on `EXIT_PROBLEMS as` fails `parts.py` and `assign_pins.py`, which carry no new meaning, and misses `boards.py:537-539`, where the fault lives. |

### The changes

| target | verdict | line read | the sentence to change, and why |
| --- | --- | --- | --- |
| CH-1 | partly | `store.py:48`; P100 `council/refuter.md:54-55` "The same pick with `SPARK_HOME` at a folder that does not exist: `firebeetle2-esp32s3: to get — known, not owned`, `would write to your history: 1 reused`, exit 0"; `parts.py:2036` `("would write" if dry_run else "wrote", reused)` | The proof line says that reproduction "answers exit 2 with the sentence instead of 'known, not owned', exit 0". It cannot: "would write" means it was a **dry run** (`:2036`), and CH-1 refuses only "where a write happens". Change → "refuse in `home()` itself when `SPARK_HOME` is set and empty, or names a non-folder; check `inside_git` first, because it walks a path that need not exist (`store.py:130`), so the two git tests keep their sentence". Also drop "unset" from the title. |
| CH-2 | partly | `tools/mutate.py:88`; `:99-100` (mutated `.py` and other files); my count over `tests/mutations/*.json`: 1,268 rows, 1,228 on `.py`, 13 `.json`, 24 `.md`, 2 `.ts`, 1 `.js` | → "a mutant of a `.py` file that does not compile **or does not import** (both checked in a subprocess before the suite) is refused; a mutant of a `.json` file that does not parse is refused too". A compile check misses a mutant that compiles and then raises at import (a removed import, a renamed module constant). The suite then fails at import, and that still scores "caught". The named test covers compile only. |
| CH-3 | holds | `store.py:187`; `init_project.py:417` | Add SL verify C3 (c): `.lock` lands in a repository when `SPARK_HOME` is inside one and holds only `catalog/`, `sources/` (allowed today). It also needs `tools.py:445` under the lock (see Missing). |
| CH-4 | partly (cache half **refuted**) | `check_vendor_pins.py:112` `return own if own.is_file() else PLUGIN_ROOT / CACHE_DIR / name`; `:138` `cache.write_text(header)`; PR #125 diff `+A live run writes the header it fetched into `.spark/cache/` of the project that owns the board` / `+file, and its line names the file. For a board spark ships, that project is spark itself` | Cache half → "merge PR #125 (P179), or say why its design is wrong". As written, CH-4 contradicts a fix that is ready to merge, and its door test would fail #125's intended refresh of spark's shipped header, which the bin's `make refresh-vendor-pins` uses (`Makefile:223`). The promote half stands, with §1's correction (documented, not silent). |
| CH-5 | holds | `parts.py:2202` | Tier: see The order. |
| CH-6 | partly | `design.py:105` `raise DesignError("%s holds a %s; a requirements file is an object with `parts`"`; `parts.py:2202-2209` catches `OSError`, `json.JSONDecodeError`, `PartError`, `store.StoreProblem` and not `DesignError` | → "depends on CH-5 (hard): `needs.requirements` reading through `design.read` raises `DesignError`, which `parts.main` does not catch, so the list file would end in a traceback, exit 1, which is the K11 class this change exists to remove". The "prints … exit 1, nothing written" line needs that mapping. |
| CH-7 | partly | `parts.py:2082-2084` `"%s %s: board %s; parts %s" % ("would write" if args.dry_run else "wrote" if changed else "unchanged", path, …)` | The fault is not silent: the answer prints the path it wrote. By the proposal's own last rule sentence it is tier 2 or 3. RISKS-16 and NM-M6 make it data first (one `git mv`). |
| CH-8 | holds | SL verify C4 (the staged form refused; the S form kept) | Tier: a stop answers could-not-run, exit 2, which is a sign. |
| CH-9 | partly | `drawer.py:90-92` `for path in sorted(folder.glob("*.json"))` … `found[path.stem] = …` | → "fixes K9's conflict-copy half". A hand `cp` under a plain name (`dfrobot-sen0193-copy.json`) passes `PLAIN` and still doubles the stock. That half needs "two entries that link one record are named". |
| CH-10 | holds | `store.py:255-256` "A folder already on the list keeps its name, however its path is spelled." | — |
| CH-11 | holds | `gh issue view 101` title "The real store has no guard against an agent's unscoped command …"; RISKS-14's E (`ai-matching-refuter.md:12`) | — |
| CH-12 | holds | `boards.py:346-349` `pads \|= set(labels)` (collected, unchecked); core 0.0.1958 `index.js:11653-11654` | The grammar is quoted from core 0.0.1958 (the bin's). K22 was observed on tsci 0.0.2621. Cite the core that 0.0.2621 ships. |
| CH-13 | holds | `boards.py:62-63` `REQUIRED_KEYS = (…, "chip", "wokwi_part_type", …)`; `:307-308` `wokwi_pins = board.get("wokwi_power_pins")` / `if isinstance(wokwi_pins, dict) and board.get("wokwi_part_type"):`; `flash_image.py:61-69` (no header read) | Its image half guards a symptom (FB-M4, see Mechanism). |
| CH-14 | holds | `parts.py:1480`; `:1540` `("kind", {}, "with --skeleton: the part's kind (motor-driver, sensor, regulator, …)")` | — |
| CH-15 | holds | `parts.py:1281-1282` `except store.StoreProblem:` / `return None`; `:1261` `if payload is not None:` | — |
| CH-16 | holds | `parts.py:2182-2184`; `:1459-1460` `lines.append("\n  CONFLICT: %s" % conflict)` | Its test is unspecified (see Mechanism). |
| CH-17 | holds | `needs.py:282` | It is a symptom change (NM-M4, see Mechanism). |
| CH-18 | partly | `parts.py:1329`; `needs.py:123` `return {word for word in re.split(r"[^a-z0-9]+", str(text or "").lower()) if word}` | → "the **query** is tokenised with `_words`, and each token is still a substring test under the AND". As written, "tokens, not substrings, against the haystack" loses prefix finds that work today. `esp32` would no longer hit the id `firebeetle2-esp32s3`, nor `vl6180` hit `vl6180x-breakout`, nor `l9110` hit `l9110s-module`. That is the misleading "nothing matches" this change exists to stop. `tests/test_parts.py:790-798` has no prefix case, so the suite would stay green. NM-M5's "tokens" was a condition for an **OR** (the one-letter `v`), and CH-18 keeps the AND. |
| CH-19 | holds | `parts.py:1955` `kept = [c for rank, c in enumerate(need["candidates"]) if rank < 8 or c["what_matches"]]`; RISKS-2 (E, runs on a copy) | — |
| CH-20 | holds | `parts.py:658-660` `if not isinstance(body.get(key), (int, float)):` / `problems.append("body_mm has no numeric %s" % key)` | — |
| CH-21 | holds | `boards.py:476` `marker = "active" if board_id == active_id(project) else "     "`; `:537-539` | Tier: the same failure shape as CH-18 (see The order). |
| CH-22 | holds | `boards.py:67` `REQUIRED_FOR_FAB = ("footprint_module", "footprint_export")`; `grep -rn footprint_module scripts tools/circuit-to-wokwi/lib` → `boards.py:67`, `board.ts:48` only | — |
| CH-23 | partly | `check_spine.py:439-441` as above | → "print the build's error **messages** (not only `element["type"]`) before the island". "the reorder alone turns round 0's 'unrelated open terminal' into the cause in one line" is false: after a reorder, the line would read `N error(s): <type>`. |
| CH-24 | holds | `needs.py:513-516` "… a board needs a board file — a record in boards/ — before spark can build with it, and it has none; …" | Its "depends on CH-4 (the header cache)" becomes "on PR #125". |
| CH-25 | holds | `needs.py:254` `"free it — a file holding [%s] without %s, given to --drawer-set <file> after a dry run — or pick another"` | — |
| CH-26 | partly | `parts.py:1303` `shutil.copy2(home / (part_id + DEFINITION_SUFFIX), target)` (no provenance); `:940` `copy["based_on"] = {"project": project_name, "digest": digest(record)}` | → "one `based_on` shape for every copy". CH-26's `{layer, id, digest}` beside the shelf copy's existing `{project, digest}` gives one key two shapes, and every reader must branch on them. |
| CH-27 | holds | `store.py:78` | — |
| CH-28 | holds | FEASIBILITY-7 (`jsonschema` not in the standard library); EXISTING-FIRST-23's probe | A concept. Its H parts are marked. |
| CH-29 | partly | `init_project.py:24`, `:459-460` (`project / ".spark" / "project.json", PROJECT_TEMPLATE`) | → "the project id in its own file, or written by every operation that lists a project". `.spark/project.json` is the brief, and a project listed by `--needs-set` or `--pick` alone (plant-alarm) has none. |
| CH-30 | holds | `boards/README.md:96-97` "… so a stand-in costs only the silkscreen labels in the picture."; `boards/firebeetle2-esp32s3.json:104` "… and it names its pins by raw GPIO number …" | — |
| CH-31 | partly | `mapping.ts:96`, `:108` `return { ...byName, ...(board.wokwi_power_pins ?? {}) };`; the bin's own copy `~/Development/smartbin-local/tools/circuit-to-wokwi/lib/mapping.ts:108` (identical), fed from `.spark/board.json`, which `boards.resolve` writes from the library file verbatim (`boards.py:272-276` `dict({"//generated": …}, **board)`); the XIAO `wokwi_pin_naming: silkscreen`, keys `SDA, SCL, SS, MOSI, MISO, SCK, A0, A1, A2` (my read) | Two bin breaks the "bin … green" line misses. (1) Rename the key in the library S3 and the bin's converter copy reads `wokwi_power_pins ?? {}` → `{}`, so the bin's simulation loses `3V3 → 3V3.1` and `GND1 → GND.1`. Keep the old key in the library file, or say the bin must update its copy. (2) "`--validate` checks every `pins` key … against a registry copy" would refuse the XIAO's nine silkscreen labels, and the bin's `make check` validates the library XIAO (`Makefile:232` `boards.py --validate`; `boards.py --paths` in the bin lists both library boards). Check per GPIO ("some label of this GPIO is a pin of the stand-in"), or give the XIAO its entries in the same commit. |
| CH-32 | partly | `board.ts:35` `wokwi_is_stand_in?: boolean;`; `sim_project.py:91-92` | → "a board whose `wokwi_part_type` is not its own Wokwi part (decided from CH-13's table) must carry `wokwi_stand_in`". With the flag removed, nothing states whether a stand-in is in use, so `test_a_stand_in_board_must_say_what_it_loses` has no input to decide from. The bin's `CLAUDE.md:108` names the flag, and that page goes stale. |
| CH-33 | holds | STORE-11 (E, `gh api`, 2026-10-10) | — |
| CH-34 | holds | `docs/guide/journey.md:913` "**Not yet.** No command does this yet."; `grep -c "esptool\|mpremote" data/tools.json` → 0 | — |
| CH-35 | holds | `check_spine.py:683-684` | — |
| CH-36 | partly | the bin's `Makefile:182` `@$(if $(HAVE_SPARK),python3 $(SPARK)/scripts/boards.py --validate --for-fab,…)`; `boards.py:467` `for board_id in available(project):`; the XIAO's `physical` keys: `footprint_export, footprint_module, height_mm, width_mm, wokwi_size_px` (no `header`) | "bin `--for-fab` on the S3, which has geometry — green" is false. `--validate` checks every available board, and in the bin that includes the library XIAO. Once `--for-fab` requires geometry, the bin's Gerber recipe exits 1 until the XIAO gets geometry (Q21). Say so on the card, or scope the bin's line to its active board. |
| CH-37 | holds | `parts.py:97`; `:113` `def _about(problem, key):`; `:1631` "`--promote %s --project .` builds with it" | — |
| CH-38 | holds | `check_spine.py:374-375` | — |
| CH-39 | holds | `compare_design.py:255-256` "… which is what `/spark:init` writes and where they have stayed"; `commands/init.md:36` "**After a build, run it again with `--force`:**" | — |
| CH-40 | holds | `find .superpowers -name "record*.sh" -o -name blocks.py \| xargs wc -l` → `fix-docs-recorded/record.sh` 102, `journey/record-journey.sh` 176, `journey/blocks.py` 22 (and a second `record.sh`, 102) | The count "10 of 42": see Numbers. |
| CH-41 | holds | `tools/check_docs.py:32`; `ls commands/*.md skills/*/SKILL.md agents/*.md` → 7 + 3 + 4 = 14 | — |
| CH-42 | holds | DOCUMENTATION-8, DOC-M-D3 | — |
| CH-43 | holds | `README.md:123` "The block leaves them out, so its last line exits 2: no step is in the history."; `tools/check_docs.py:165-166` (exit code only) | — |
| CH-44 | partly | `check_physics.py:309-310` `"draws %s of %s, resting on figures nobody has verified: %s" % (current_text(drawn), current_text(rated), "; ".join(resting))` | → "`check_physics` prints the who and why of each **unverified** figure (`:305-306`) and drops the source of each **verified** one". "reads the record's verified/source and drops them" overstates. |
| CH-45 | partly | `outcomes.py:9-13`; the six aliases above; `tests/test_boards.py:366-368` `test_get_a_field_that_does_not_exist_fails_loudly` … `self.assertEqual(code, 1, said)` | → "change the two mappings (`boards.py:537-539` for 'no selection' only; `init_project.py:501`) and pin them with tests". The grep test contradicts `outcomes.py:9-13` and fails four aliases that carry no new meaning. `--get no_such_field` must stay exit 1: the bin's contract test pins it. |
| CH-46 | holds | `check_spine.py:216` | — |
| CH-47 | holds | `docs/guide/how-it-works.md:155-156` "… this was / not run for these docs." | PR #125 edits this page, so the line pointers move. |
| CH-48 | holds | `grep -rn '\.local/share' agents commands skills` → 6 lines | — |
| CH-49 | holds | `066c4af` as above | — |
| CH-50 | holds | `commands/idea.md:25-26` "there is no removing or renaming a need yet, / so a wrong one is fixed by hand in `<project>/.spark/needs.json`" | The pointer is `:25-26`, not `:24-25`. |
| CH-51 | holds | `parts.py:1955-1956` | — |
| CH-52 | holds | `needs-matching-vocabulary.verify.md:272` "The count: **19 distinct (does, what) pairs** holds"; `parts.py:65-69` `KIND_FUNCTION` | — |
| CH-53 | holds | `parts.py:1326-1329` | — |
| CH-54 | holds | `grep -c '"function"' boards/*.json` → 0, 0 | — |
| CH-55 | holds | `boards/README.md:21` "boards/active.json           <- which board. THE one place it is chosen." | — |
| CH-56 | holds | `emit_footprint.py:229-230` `sys.stdout.write(text)` / `return EXIT_OK`; `:163` `physical["header"].get("drill_mm", "?")` | — |
| CH-57 | holds | `store.py:96` `PRIVATE = ("drawer", "drawer-import", "shelf", "projects", "history")`; `grep -n MAX_BYTES scripts/store.py` → `FILE_NAME_MAX_BYTES` only | — |
| CH-58 | holds | `cost.py:110` `for text in path.read_text(encoding="utf-8", errors="replace").splitlines():`; `store.py:286` (bytes) | — |
| CH-59 | holds | `parts.py:879` `for path in sorted(store.place("catalog").glob("*" + DEFINITION_SUFFIX)):` | — |
| CH-60 | holds | `parts.py:185` `SELECTOR_SAFE = "^[A-Za-z0-9_]+$"`; `:517` | — |
| CH-61 | holds | K71, DR verify | — |

## The order

**The rule is not what orders the list.** §3 states one rule: tier 1 is "faults that harm or mislead **silently**", and "a
fault with a weak sign printed after the verdict is tier 2 or 3, not 1". Read against that rule, these changes sit in
the wrong tier:

- **Placed in tier 1, but the output gives a sign:**
  - CH-5: a traceback is a sign, and the catalogue grades K11 "blocks the journey". Only K16's `.part` read as kept is silent.
  - CH-7: `--requirements` prints "wrote <path>: board …; parts …" (`parts.py:2082-2084`), and the path is the other file.
  - CH-8: the stop answers could-not-run, exit 2.
- **Placed lower, but silent by the rule's own test:**
  - CH-26 (tier 2): K13 is "harms silently — drift has no sign", and K19 misleads silently.
  - CH-36 (tier 2): `--validate --for-fab` answers ok on the XIAO with no geometry (`how-it-works.md:175`). That is ok over a false result.
  - CH-49 (tier 3): a scenario "pass" over 1 of 12 pin-map constants is ok over an incomplete result.
  - CH-55 (tier 4): `active.json` stays on the old board and nothing is said.
  - CH-57 (tier 4): with no `fcntl`, a write takes no lock and nothing is said.
  - CH-58 (tier 4): the proposal itself calls it "a silent undercount".
- **One failure shape, two tiers:**
  - CH-18 (tier 1) and CH-21 (tier 2) are the same answer: "nothing matches — research it" over records that exist. One is about parts, the other about boards.
  - CH-54 sits in tier 4 because "'a gap' is printed". CH-18's wrong answer is printed too, and it sits in tier 1.
- **One criterion applied once:** CH-2 is pulled into tier 1 as enabling work ("makes every later proof trustworthy"). CH-40, the
  recorder, also enabling, is left in tier 3 with "the PO may" pull it forward.

The ranks that do not follow the stated rule follow two unstated ones: likelihood and reach (CH-57, CH-58, CH-55
demoted) and enabling work (CH-2 promoted). Either state both in §3, or re-tier.

**Pairs that should swap, each with the finding behind it:**
- **CH-2 ↔ CH-12.** CH-12 is the one deterministic circuit-class fault every check passes, on the route the PO made the first fix (D8). It
  is S, and it needs no toolchain. CH-2's compile check removes only mutants that do not compile. Two rows were ever "caught" that way (K53).
  The over-count is "—" in size (RISKS-6). CH-2 can ride with the first change that proves itself by a mutation row.
- **CH-3 ↔ CH-11.** K2's harm has happened: twelve scratch projects in the real `projects.json` (#101). K5 has never been met in use. The
  catalogue marks it "nobody — reasoned only", reproduced only in a diagnosis run. USER-AI-AGENT-13 (uncited): "two agents on record did not
  hold" the prose guard.
- **CH-4 (cache half) → out of the list.** PR #125 is the same fix, ready to merge. The list should say "merge, or argue against, #125".
- **CH-24 and CH-25 → the top ten.** RISKS-1 (E, uncited): "The one person blocked is the PO, at P100 round A … by three findings
  TOGETHER: K3 … K29 … and K36". The proposal answers them at ranks 25, 24 and "before rank 1 (Q6)".

**The strongest case for a different top five.** The PO's measure is "fixing what matters" (D 2026-10-10). Three things are
on record. Today the only person blocked is the PO, at round A, by K3 + K29 + K36 (RISKS-1, E). His own ordering words
are D8 (2026-10-09): *"we want to start by the boards when we fix the findings so that it can create one automatically
based on the DFRobot orders"*, and on 2026-10-10 *"the boards for sure"*. And one of the ranked fixes is already
built (PR #125). A top five that respects all three, keeps the one trust fix every proof needs, and starts with boards:

1. **CH-1**, with the refusal moved into `home()`, so reads and dry runs are refused too (S).
2. **Merge PR #125** (K14 closed, nothing new to design). Then **CH-12**: the board route's silent merged netlist (S).
3. **CH-14 + CH-21**: boards searched, shown and validated like records, and `--skeleton --kind board` refused (S–M).
4. **CH-24 with CH-22's schema page and CH-13's chip table**: D8's "first fix". It removes K29 for four of his six ESP SKUs (L).
5. **CH-25 after Q1/Q5, with the Q6 data pass as a card**: K3 and K36, the other two walls of round A (M plus the PO's time).

On this order, CH-2 rides with the first change that proves itself by a mutation row, and CH-11 and CH-3 come next. Tier 1's
remaining silent faults (CH-5…CH-10, CH-15…CH-20) follow inside the board work, where each touches the same files.
Against this case: it delays CH-3 and CH-11, both silent store harms. CH-11's harm is recorded. CH-3's is reasoned.

**Capacity, which the order does not meet (RISKS-18, uncited).** The list has 61 changes. The scrum limits are 2 per working stage,
Ready 5, and 4 in flight (`scrum/README.md`, as RISKS-18 cites). The proposal does not slice the list into cards or epics,
and it does not say what lands first in a month. A priority order without a cut line does not tell the PO what he gets next.

## Mechanism or symptom

For each change where the answer is not "mechanism, the test catches it, the message names where and why, nothing
simpler, nothing breaks":

- **CH-1. Mechanism for writes, symptom for reads.** The test `test_a_spark_home_that_is_empty_or_names_no_folder_is_refused_and_named`
  catches a write regression. `--match`, `--need` and every `--dry-run` still answer from an empty or missing home. The
  "your drawer is empty (store <path>)" line is a weak sign after the verdict, which the proposal's own rule calls tier 2/3.
  Simpler and stronger: the check in `home()`, ordered after `inside_git` (which already walks a non-existent path,
  `store.py:130-135`). That keeps both git tests' sentence, the SL verifier's (b), and removes the "where a write happens" special case.
- **CH-2. The named test misses the real escape.** `test_a_mutant_that_does_not_compile_is_refused_not_caught` passes while a
  mutant that compiles and fails at import still scores "caught". 40 of 1,268 rows mutate `.json`, `.md`, `.ts` or `.js` (my
  count), and a compile check does not apply to them. The message names the row and the line, which is good for a `.py` file.
- **CH-4 / R2's door test. It cannot be a grep.** A grep sees `write_text` and cannot see where it writes. There are 25 direct writes outside
  `store.py` (my grep), most into projects, so a grep is either red on legitimate writes or an allow-list that proves nothing.
  Existing-first: P172's gate already runs the suite in an archived tree and counts what it leaves in its temp folder
  (`tools/check_commit.py:111-139`). The same comparison over the archived tree catches a write into the plugin at run
  time, the way PR #125's proof does (`git status --short .spark/` empty). As written, the test would also fail on
  `sim_project.py:162`. That line writes a compiled chip beside a library record, and those binaries are tracked
  (`parts/*/chip/*.chip.wasm`), so a recompile rewrites tracked plugin files.
- **CH-6. It breaks before it fixes** unless `DesignError` is mapped (Verdicts).
- **CH-9. Mechanism for conflict copies, nothing for a plain-named duplicate.** The test names only the conflict copy.
- **CH-13. Its image half is the symptom guard the FB verifier named.** FB-M4: "C2 guards the symptom at the image; the
  mechanism is that a board-dependent job is modelled as a store-wide one" (`tools.find("firmware-image")` takes no chip;
  FEASIBILITY-15: "`roles` is a flat `role → tool` map"). No change addresses the mechanism. The guard still earns its place.
- **CH-16. The property test is undefined.** It is named "every text line is reachable from the envelope". Text lines are formatted
  prose. "Reachable" needs a stated mapping (line → field), or the test passes vacuously. Name the mapping, or test the
  four named omissions (notes, CONFLICT, unchecked, kept) one by one.
- **CH-17. Symptom.** K34's harm is that "the project's record of intent is wrong from the first pick, and nothing downstream
  can tell". CH-17 prints a note once, at pick time, and `needs.json` records nothing. `--requirements`, the build's
  unserved note and the next session cannot tell either. NM-M4 (uncited) names the mechanism: "The marks cannot say 'fits
  loosely' … the vocabulary for the hand-over does not exist." The smallest mechanism fix is a recorded field or mark on
  the pick. Q20/Q23 style: the PO's.
- **CH-18. It would regress, and the named tests would not see it.** See Verdicts: prefix queries stop matching.
  `test_need_quoted_or_not_is_one_search` and `test_need_12_v_inlet_names_the_words_that_missed` contain no prefix query.
- **CH-23. It reorders without changing what is printed.** See Verdicts. The named test `test_a_build_error_is_printed_before_an_island` would pass
  while printing `1 error(s): <type>`. Assert the selector text instead.
- **CH-26. Two shapes for one key** (Verdicts). The test `test_audit_says_a_built_line_is_stale_after_its_pin_order_changed` works, because
  `pin_order` is in `BUILD_FACTS` (`parts.py:903`). A changed `body_mm` or `simulation` still re-proves nothing (K19), and
  the proposal keeps that by choice (§4).
- **CH-31 and CH-36. They break the bin**, contrary to their "bin" lines (Verdicts). FEASIBILITY-11 lists the bin's `Makefile:182`
  and `:232`, the two lines that validate the library XIAO.
- **CH-32. It removes the only input its own rule needs** (Verdicts).
- **CH-45. Symptom, and it contradicts written design** (Verdicts). The failure "no script aliases an exit code to a new meaning"
  cannot be decided by a grep.
- **What breaks for the bin, beyond the above:**
  - CH-22's removal of `footprint_module` leaves the bin's `tools/circuit-to-wokwi/lib/board.ts:40` typing it as required. That is a type only; no runtime read (my grep).
  - CH-4 as written moves the bin's live refresh (`Makefile:223`) into the PO's real store. `make check`'s offline read (`:220`) then depends on what that store holds.
  - With PR #125 nothing moves. The bin's own tracked `.spark/cache/*.h` stay unread, which #124 says is the bin's to decide.
- **Irrigation and plant-alarm.** The proposal's lines hold where I checked them: irrigation's `firmware/pins.py:1` names
  `irrigation.requirements.json` in a generated header, so CH-7's rename regenerates it, and plant-alarm's
  `.spark/` holds only `needs.json`. One thing is missing for plant-alarm: CH-29's id has no place to live there (Verdicts).

## Missing

1. **PR #125 (P179)**, open since 2026-10-10T16:16Z and "Ready to merge" by its own council. It is the fix for K14, and the proposal never
   names it (`grep -c "#125" proposal.md` → 0; `grep -c "PR #125\|pull/125" proposal.md` → 0; my runs, 2026-10-10). It also edits `docs/guide/agents.md`, `how-it-works.md` and
   `tests/test_json_contracts.py`, which CH-45, CH-47 and CH-48 cite by line.
2. **A third writer into the plugin**: `sim_project.py:162` (compiled chips beside library records; K13's chip half; P149 #83,
   P150 #84 per K13). K13 maps to CH-26, and CH-26 says nothing of chips.
3. **A writer into the store outside the door and the lock**: `tools.py:445` (`tools.py --on/--off/--pin/--use/--new`
   write the store's `tools.json` with a plain `write_text`). There are also **home reads at import**: `tools.py:47-48`. §2.3 states the rule
   "no module reads a home at import" (TECH-LEAD's `tech-lead.md:64-65` names `tools.PERSONAL`), and no change carries it.
4. **NM-M4**, the marks cannot say "fits loosely". No change (see CH-17).
5. **FB-M4 / FEASIBILITY-15**, roles are chip-blind. No change (see CH-13).
6. **DR-M5**, `version_mismatch` keys on "v0.8.1 anywhere in README" (`check_docs.py:173`). No change.
7. **K21's other half**: "one `--step` outside Claude Code spoils a project's tally for good" (E16b, verified, no item). §7 maps
   K21 to "by design", but `cost.py:47`'s design covers the exit 2 only.
8. **K65**, the typed `origin`, is "not ranked". D the PO 2026-10-06 decided it, and nothing has changed since (catalogue K65). A decided,
   unbuilt item bears on CH-28's generated schemas, because `verified` means four things.
9. **SL verify C3 (c)**: a `.lock` beside the data lands inside a repository when the home is in one (catalog and sources only, allowed
   today). Not in CH-3.
10. **Lens findings dropped that bear on the order or the design** (none of these is cited anywhere in the proposal):
    - **RISKS-1**: who is blocked. It is the order's strongest input.
    - **RISKS-3**: "better" by the PO's #17 measure is still unmeasured for "proven by use" and "fewer requests" after every change ships.
    - **RISKS-18**: capacity.
    - **RISKS-19**: line pointers go stale at the first merge, and nothing ties a fix to its K id. PR #125 already moves cited lines.
    - **STORE-17**: union merge and line order.
    - **USER-AI-AGENT-13**: the guard is prose two agents did not hold.
    - **FEASIBILITY-11**: four projects call spark's command lines. It is the list that shows CH-31 and CH-36 breaking the bin.
    - **FEASIBILITY-19**: `inside_git` and a private git remote.
11. **Existing-first, not used:**
    - PR #125, for K14.
    - P172's gate (`tools/check_commit.py:111-139`), as the run-time form of R2's door test.
    - The converter's own registry (`geometry.ts:58-59`, `PinOracle` over `@wokwi/diagram-lint`'s `PartRegistry`), which CH-31 copies into `data/wokwi-parts.json` instead. That is a second, versioned copy. A converter check (FB-C1's CLI form) reads the registry it ships with.
    - `needs.py:326-331` already releases a project's own holds that no pick explains (`used_in = {who: n for who, n in (entry.get("used_in") or {}).items() if who != name}`, said as "released … — no pick of this project explains it", `parts.py:2013-2015`). CH-25's `--release` could extend that path rather than add a second.

## Numbers

- **CH-3 "the suite's 42 direct store writes" (FEASIBILITY-4).** SL verify C3 (a) counted 33 (`grep -c` → `tests/test_store.py` 32,
  `tests/test_drawer.py` 1). My looser grep (`store.write_json|write_file|copy_folder|append_event|keep(` over `tests/*.py`)
  gives 46 (8 + 3 + 3 + 22 + 10). Three counts for one population, and no pattern is named. Name the pattern, and drop the other counts.
- **CH-5 "the 13 store-file readers"** has no provenance in the proposal. The source (`store-levels-and-holds.md:452`) is a grep, which its
  verifier marked "**H** here; not recounted" (`.verify.md:420`).
- **§2.6 and CH-40 "10 of 42 blocks sit under no command"** (DOCUMENTATION-17). DR verify M2 counts 8 (`.verify.md:194`). §7
  records both. §2.6 and CH-40 use 10 alone.
- **CH-2 "plus hours of machine time"** has no measure and no provenance. Use a timed sweep, or "—".
- **CH-41 "0 problems over the 14 pages today, E"** is tagged E without a command or run. The 14 is right (7 + 3 + 4, my `ls`). The "0 problems" has no source.
- **CH-1 "it is two lines and one field"** does not match its own body: a refusal, an envelope field, a line on every write, a line
  on `--match`/`--pick`, and two test rewrites.
- **CH-45 "whether its Makefile reads the word `mismatch` is —"** is answerable. `grep -n mismatch Makefile` in the bin prints
  nothing (my run, 2026-10-10).
- **CH-12**: the grammar is quoted from `@tscircuit/core` 0.0.1958 (the bin's `node_modules`; irrigation's is 0.0.2007). K22 and
  "no copper short" were observed on tsci 0.0.2621. The version the claim rests on is not the version it was seen on.
- **§2.3 "137 files, 312 KB"**: the source says 319,145 bytes (`feasibility.md:59`), which is 312 KiB or 319 kB. Name the unit.
- **The verified numbers** (no change needed):
  - "37 sites in 16 scripts" (my grep: 37, 16).
  - "115 tables and 1,268 mutations" (my count: 115, 1,268).
  - "266 + 196 = 462" anchors (my count).
  - "22 function-local sibling imports" (my grep: 22).
  - "six literal store paths" (my grep: 6).
  - "6 entries carry `used_in`, history 8 lines, all plant-alarm" (the store copy).

## Searches

No web searches. Read-only `gh`, 2026-10-10:
- `gh issue view 124` (body and comments).
- `gh pr view 125` and `gh pr list --state all --limit 8`.
- `gh issue view` on #7, #8, #10, #16, #20, #21, #22, #23, #44, #55, #58, #59, #61, #64, #65, #69, #79, #82, #96, #99, #101, #102, #114, #118, #119 and #123, for state and title.

Local reads:
- `git diff main...p179-vendor-cache` (stat, and `scripts/check_vendor_pins.py`).
- `git show -s 066c4af`.
- The store copy at `<scratch>/p158/refuter-1/store`, with `python3 -I`.
- `node_modules/@tscircuit/core/package.json` in the bin and in irrigation.
