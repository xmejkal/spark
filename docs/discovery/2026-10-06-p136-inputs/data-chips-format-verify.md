# Verification of `answer.md` (projects that stay current; components that hold every form)

**How it was checked (2026-10-06):**

- Read-only, against spark at `8f7733d` and the bin at `8847eb8`, with rc-car, irrigation and spark-quickstart as they are on disk.
- Every spark citation was opened at its `file:line`, or at its commit with `git show`.
- Every web citation was downloaded into `verify-web/` in this folder and searched as text. The one exception, the Toshiba page, refused curl (403) and was read with WebFetch.
- Runs used `PYTHONDONTWRITEBYTECODE=1`, with `SPARK_HOME` pointed at `verify-runs/store/` in this folder.
- spark's and rc-car's `git status --porcelain` stayed empty. spark files changed after 11:30 today lie only in `.superpowers/discovery-inputs/2026-10-06/`, which other workflows wrote and which is gitignored (`.gitignore:8`).

**Result: 161 claims checked**, one table row each (a row with several citations is counted once).

- 137 confirmed (row 46 with a nuance, in the notes at the end).
- 4 refuted.
- 20 partly true. Three of these (R16, R21, R22) are true claims cited to a page that does not show them.

The table below lists the 24 refuted and partly true claims, most consequential first. The confirmed claims follow by section.

---

## Refuted or partly true

| # | where | the answer says | verdict | what is true, with evidence |
| --- | --- | --- | --- | --- |
| R1 | §1.2 step 1 | "rc-car copied spark's `tactile-button` record into its own `parts/`" | **REFUTED** | The copy went the other way. rc-car wrote the record first, in `e7133e9` (2026-09-26). spark first added `parts/tactile-button.json` in `1f769f8` (2026-09-29); `git log --follow` shows no earlier path. That commit's message says: *"The documented example needed a tactile-button record the shipped library did not have — the RC car's, written with sources for the cold test, is shipped now."* A JSON compare of rc-car@`e7133e9` against spark@`1f769f8` finds no differing key. The drift itself is real (R7, and confirmed row 22), but the library record is the copy here, and nothing records that it came from rc-car. |
| R2 | §3.3 | "`sources`, which holds URLs that nothing checks" | **REFUTED** | `parts.py --sources PART` *"ask[s] every URL a record cites whether it answers"* (`scripts/parts.py:1359`). It reads `sources`, as a list or a dict, plus each fact's source text (`cited_urls`, `:1254-1265`). It sends a HEAD request to each (`reachable` and `sources_resolve`, `:1268-1281`) and reports each one that does not answer as a problem (`_op_sources`, `:1516-1526`). Only the contract (`validate`) leaves `sources` unchecked. |
| R3 | §2.1, KiCad row | "three official library repositories, tagged per release", cited to [addons] | **REFUTED** | KiCad's download page says: *"Since KiCad version 6, the libraries are organized into four separate repositories on GitLab, and tagged by point release version"*. It lists five: `kicad-symbols`, `kicad-footprints`, `kicad-packages3d`, `kicad-packages3d-source` and `kicad-templates` (https://www.kicad.org/libraries/download/). The cited page (https://dev-docs.kicad.org/en/addons/) does not mention the library repositories at all. The answer dropped the `[kicad-download]` link that `other-ecosystems.md:63-64` used. |
| R4 | §2.3 item 4 | "spark's 'VL6180X breakout' record covers four different boards" | **REFUTED** | The *phrase* "the VL6180X breakout" spans four pinouts (`DECISIONS.md:34-35`, a rule about stating an assertion's scope). The *record* is scoped to one carrier: `"variant": "Pololu VL6180X Carrier #2489 (PCB revision irs09a)"` (`parts/vl6180x-breakout.json:124`). Its `//variant` note says the facts *"are read off Pololu's schematic and hold for that carrier ONLY. On another board they are not approximately right, they are unknown"* (`:123`). What fits `replacedBy` is the generic id `vl6180x-breakout`, not a record holding four boards. |
| R5 | §3.3 | "today's records stay valid, and an older spark reads a new record and ignores the new keys" (INFERRED) | PARTLY | This holds for `origin`, `level`, `conditions`, `measurement`, `form` and a top-level `code`: a scratch `validate` returned no problems. It fails for the pointer-only `documents` entry that §3.2 itself proposes. Today's contract refuses it with *"documents.l9110-datasheet has no sha256 that is one"* (`scripts/parts.py:362-364`, run), and `parts.load` then raises (`:227-233`). An older spark therefore *rejects* such a record. §3.3's own "two contract details change" bullet says this, but the compatibility bullet above it does not. |
| R6 | §3.3 | "`corroborated_by` stays a single object. Allowing a list waits until gap G9 is fixed: today a list of citations passes the check and then crashes `citing()`" | PARTLY | Gap G9 is a list-valued **`cites`** (`docs/2026-10-04-store-discovery.md:99-100`), and that does crash: `AttributeError: 'list' object has no attribute 'get'` (run; `scripts/parts.py:1062`). A list-valued **`corroborated_by`** does not crash. It validates clean even when it names a document that does not exist. Both `_citations` (`:375-380`) and `citing()` (`:1060-1061`) then skip it silently, because a list is not a dict (run). The reason to keep it single is real, but the failure is silence, not a crash. |
| R7 | §1.2 step 2 | "spark has since improved its record twice: `1e77b88` … `395e69d`" | PARTLY | After shipping the record, spark changed it four times: `1e77b88` (09-29), `ac2e86f` (10-01, the wake fact), `c2afc47` (10-03, P81's `pin_order_proof`) and `395e69d` (10-03). rc-car mirrored two of them by hand: `87443a0` mirrors `ac2e86f` and `65dfd01` mirrors `c2afc47`. The two named are the two rc-car lacks, which matches today's three-field compare. |
| R8 | §1.1, row "the project's own copy" | "`--promote` is a plain copy, with no origin, date or digest" | PARTLY | `--promote` adds nothing (`scripts/parts.py:1161-1182`). But it copies the whole file (`shutil.copy2`, `:1179`), so a record promoted from the shelf into a project (`:1172`) keeps the shelf copy's `based_on {project, digest}`. Such a project copy does name its origin and a digest. |
| R9 | §1.1, row `.spark/rules.json` | `not_yet_stated` "is the only 'you are behind' message spark has" | PARTLY | `tools.py --status` also prints *"; %s %s here, the list pins %s — /spark:setup installs the pinned one"* when an installed tool's version differs from its pin (`scripts/tools.py:203-206`, `:294-295`). `--audit`'s "owes" lines also name what a record lacks (row R11). |
| R10 | §1.1, row `data/fabrication.json` | `98ed047` "moved the minimum annular ring from 0.25 to 0.18 mm under all four projects" | PARTLY | spark-quickstart's first commit is `b8162fb` on 2026-10-03, after `98ed047` on 2026-10-01. The default moved under three existing projects: irrigation (first commit 09-29), rc-car (09-26) and the bin (09-22). The fourth started on 0.18. None of the four overrides it: three have `"fabrication": {}` and the bin has no `fabrication` key. |
| R11 | "The answer in short" item 1 | "rc-car's button record lacks two library improvements, and nothing says so" | PARTLY | `--audit` does flag one of the two, as missing rather than as drift: run from rc-car it prints `tactile-button (project) owes: simulation` (run; `scripts/parts.py:1701`). Nothing reports the missing `host_parts` pull-up. §1.2 step 4 states this correctly. |
| R12 | §1.2 | the bin's rules file "says three times that 1.5 A is 'the L9110S's own limit'" (`:27-28`, `:33-34`, `:41-43`) | PARTLY | It says so four times: `bin:.spark/rules.json:28`, `:30` (*"1.5 A, the L9110S's own limit (see GND's //CurrentShunt)"*), `:34` and `:43`. |
| R13 | §1.4, "Seen on the L9110S" | "Two were read off the module's own documents rather than stated in words" | PARTLY | Three were. A third, `schematic_numbers_vcc_and_gnd_opposite_to_the_silkscreen`, is read off the guide's board photo (page 1) against its connector symbol (page 3) (`parts/l9110s-module.json:94-103`). The §3.2 `--show` sketch also leaves this sixth fact out. |
| R14 | §1.4 | "Computed values are never stored. The code works them out again on every read" | PARTLY | Values the *code* computes are not stored. Values a *person* computed are, with the method in prose. `regulator_3v3_a` is *"the lower, because one record covers both"* (`boards/firebeetle2-esp32s3.json:387-392`). `output_power_w_8ohm_3v3` was read off a graph and cross-checked by V²/2R (`parts/max98357a-dfr0954.json:134-139`). The forms report §1.4 says the same. §3.1's "Values the code computes are never stored" is the accurate form. |
| R15 | §1.4, "no field at all" row | "… order code …" | PARTLY | An optional `sku` exists. Research writes a maker-less part's shop order code into it, with `order_code_at` (`commands/research.md:89-90`; e.g. `parts/led-red-5mm.json:7`), and drawer linking reads it. `max98357a-dfr0954` keeps an LCSC code as a fact, `lcsc_part_for_the_bare_chip: C910544` (`parts/max98357a-dfr0954.json:170-175`). What is missing is a typed, sourced order-code field. |
| R16 | §1.4, documents row | "The file itself lives in your store at `sources/<sha256>/<file>` (`scripts/parts.py:352-369`)" | PARTLY (mis-cited) | The claim is true, but the cited lines are the validator. The path is built at `scripts/parts.py:929-930`, in `keep_in_store`, `:923-931`. |
| R17 | §1.1 row 1 | "a library part or board …: spark looks in the project, then the shelf, then the library" | PARTLY | True for parts. Boards have no shelf layer: the shelf row is added only `if kind == "parts"` (`scripts/store.py:64`; `boards.records` at `scripts/boards.py:208-210`). |
| R18 | §2.1, PlatformIO trust | "a sha256 checked by the client, and no review ([forum][pio-security])" | PARTLY | The forum states only the checksum: *"Each package has its own SHA-256 checksum which will be verified on the client-side"* (https://community.platformio.org/t/supply-chain-poisoning/19676). It says nothing about review. "No review" is an inference from the publish docs describing none (`other-ecosystems.md`, PlatformIO §, "Trust"). |
| R19 | §2.1, tscircuit "your own edits" | "`tsci import` writes a local file you own" | PARTLY | Only for a JLCPCB part (`✔ Imported imports/MCP4822_E_SN.tsx`). A tscircuit registry part is installed as an npm dependency (`bun add @tsci/seveibar.esp32-s3-mini-1-n8`), not as a file you own (https://docs.tscircuit.com/command-line/tsci-import). |
| R20 | §2.1, SnapEDA/UL/EasyEDA "your own edits" | "overwritten" | PARTLY | The row's cited tool keeps what you have by default: *"Use --overwrite to replace an existing symbol, footprint, or 3D model already in the library"* (https://github.com/uPesy/easyeda2kicad.py). An edit is lost only if you ask for that. |
| R21 | §2.1, Wokwi row | "On wokwi.com a diagram names `github:owner/repo@1.0.4` ([tutorial][wk-7seg])" | PARTLY (mis-cited) | The tutorial only says the `"dependencies"` section *"tells Wokwi where to look for the chip implementation on GitHub"*, and links an example project. The string `github:` is not on the page. The syntax is real; the st7735 chip's README shows `"chip-st7735": "github:martysweet/st7735-wokwi-chip@1.0.4"` (https://github.com/martysweet/st7735-wokwi-chip). |
| R22 | §2.2 | "Fritzing: one `.fzpz` bundles the breadboard, schematic and PCB views ([part format][fz-format])" | PARTLY (mis-cited) | The cited page never mentions `.fzpz`. It says *"A Fritzing part is made up of a number of files: one required metadata file (… fzp), and up to four SVG files"*, for the breadboard, schematic, PCB and icon views, and *"We decided not to merge all the SVGs and the metadata together in a single file"*. The `.fzp` names the views. `.fzpz` is the archive used to share them, which the fritzing-parts README's checker usage mentions. |
| R23 | §2.3 item 5 | "dependencies that disappear: an archived Wokwi chip ([Plot3])" | PARTLY | Plot3 is archived, read-only and deprecated in favour of the Scope chip, but it has not disappeared. Its releases v1.0.0, v1.0.1 and v1.0.2 each still carry `chip.zip` (`gh api repos/Dlloydev/Wokwi-Chip-Plot3/releases`, read-only; `archived=true`). `other-ecosystems.md:255` said "Dependencies rot", which is accurate; "disappear" is not. |
| R24 | header, "The same day you also asked" | Petr asked for *"good architecture so that we can nicely easily extend and update it later"* | PARTLY | The words are exact, but their subject was a skill. The message reads *"the skill should have good architecture so that we can nicely easily extend and update it later. Why are we dealing so much with I2C? …"*, in this session's transcript at 2026-10-06T09:41:36Z. The orchestrator's running list calls that skill "the discovery skill". It was not said of spark's data or architecture in general. |

---

## Confirmed, by section

### Header and framing

| # | claim | evidence |
| --- | --- | --- |
| 1 | spark at `8f7733d`, the bin at `8847eb8`; spark's `git status` empty | `git rev-parse --short HEAD` in both; `git status --porcelain` empty |
| 2 | P94 is xmejkal/spark#17, "The store and its ways in" | `gh issue view 17`: *"P94 — The store and its ways in, designed: an extendable, reusable architecture"* |
| 3 | Petr's first quote, about updating data files and downloading modules as chips | spark#17 comment, 2026-10-06T09:56:59Z |
| 4 | Petr's second quote, about components including all the forms | spark#17 comment, 2026-10-06T09:58:00Z |
| 5 | *"well architected so that new buses and other rules and checks can be learnt … from the experience with new and new systems"* | spark#70 (P136) body; spark#17 comment of 09:56:59Z |

### §1.1 How each kind of data reaches a project

| # | claim | evidence |
| --- | --- | --- |
| 6 | Parts resolve nearest-first, and the nearest wins | `scripts/store.py:57-77`; `scripts/parts.py:219-233` (`definition_path` and `load` go through `store.records`); `scripts/design.py:174-186`, `:262-271` |
| 7 | Nothing records what a past build rested on, because the store has no history yet; that history is P97, spark#18 | `scripts/store.py:48-49` has no history place; no `history.jsonl` writer in `scripts/` (grep); spark#18 is P97 ("Store 1c"), which covers design §5.7, the history |
| 8 | A shelf copy carries `based_on {project, digest}`, and no code reads it | written at `scripts/parts.py:837-842`; grep over scripts, tools, commands, agents, skills, boards, parts, chips and data finds `based_on` only at `:841` and in tests |
| 9 | `commands/idea.md:64-65` describes a re-shelve the code cannot do | the shelf wins in `linkable()`, which lists spark's layers before the project list (`scripts/drawer.py:110-119`); `_shelve_from` returns None for `"shelf"`, which is in `SPARKS_OWN` (`:31`, `:191-193`) |
| 10 | `data/fabrication.json` is read at every run, and a project overrides it key by key | `scripts/fab.py:27-38` |
| 11 | `98ed047` (2026-10-01) moved `min_annular_ring_mm` from 0.25 to 0.18 | `git show 98ed047 -- data/fabrication.json` |
| 12 | `.spark/rules.json` changes only on `init --force`, which keeps what was stated and fills what is missing | `scripts/init_project.py:271-300` |
| 13 | `not_yet_stated` covers two keys | `scripts/init_project.py:248-268` (`must_not_float`, `i2c_buses`) |
| 14 | `.spark/board.json` is written only by `boards.py --resolve`; the bin re-resolves when the file is older than its inputs | `scripts/boards.py:239-257`; `bin:Makefile:94-96` |
| 15 | Your install runs in place, and a local-path marketplace *"loads in place … you don't need to increase the version"* | `~/.claude/plugins/known_marketplaces.json`: `petr-local` has source `directory`, `/Users/petr/Development/spark`; `.claude-plugin/marketplace.json` gives source `"./"`. The stale cache `…/cache/petr-local/spark/0.4.0` has no `commands/`, yet this session lists `spark:build`, `spark:drawer` and others, so it loads from the working tree. Quote: https://code.claude.com/docs/en/plugins/loading |
| 16 | *"a manifest that pins "version": "1.0.0" keeps every user on the cached copy until its author changes the string, however many commits they push"* | exact sentence, https://code.claude.com/docs/en/plugins/loading |
| 17 | `0.6.0` pinned since `02250ee` (2026-09-24), through 379 commits, 23 of them to `parts/` | `.claude-plugin/plugin.json:3`; `git log -G'"version"'` shows `02250ee` last; `git log 02250ee..HEAD` counts 379 (371 without merges), 23 to `parts/`; no git tags |
| 18 | The README says the GitHub install "was not run for these docs" | `README.md:98-99` |

### §1.2 rc-car's button record falls behind

| # | claim | evidence |
| --- | --- | --- |
| 19 | rc-car changed its record by hand twice, in `87443a0` and `65dfd01` | `git log -- parts/tactile-button.json` in rc-car |
| 20 | `1e77b88` added `simulation.wokwi` (Wokwi's pushbutton) | `git show 1e77b88 -- parts/tactile-button.json` |
| 21 | `395e69d` turned "give it an external pull" into a `host_parts` pull-up, which the generator places | `git show 395e69d`; `scripts/parts.py:327-330` |
| 22 | Three fields differ today: `host_parts` absent, `host_requirements` keeps the old sentence, `simulation` absent | JSON compare, run; rc-car's `parts/tactile-button.json:41` still says "Give it an external pull" |
| 23 | rc-car's copy wins because it is nearest | `scripts/store.py:70-77` |
| 24 | `--audit` prints only `tactile-button (project) owes: simulation` | run from rc-car against a scratch store |
| 25 | rc-car's next board places no pull-up, and its simulation stage stops at this record | `remote.requirements.json` uses five `tactile-button`s; `scripts/sim_project.py:53-56`, `:125-129`; `scripts/check_spine.py:455-457` returns COULD_NOT_RUN |
| 26 | The parts a compare needs already exist | `scripts/parts.py:827-834` (digest); `based_on`; `scripts/store.py:57-67` (layers) |
| 27 | spark's record keeps 0.8 A continuous, and lists 500 mA, 800 mA, 1.5 A and 2.5 A as seller figures | `parts/l9110s-module.json:57-69`; the full source sentence is on `:60` |
| 28 | Where the bin's 1.5 A came from is not recorded | a grep of the bin finds no source; `bin:parts/PARTS.md:35` says "~0.8 A per channel" |
| 29 | A power entry names a fact instead of copying it | `scripts/emit_board.py:401-420`; `boards/firebeetle2-esp32s3.json:133-134` |
| 30 | `rails` exists because rc-car once copied the whole L9110S record to change one rail | `scripts/design.py:134-153`, docstring (cold test G5, backlog R9) |

### §1.3 A new project takes the L9110S module and its chip

| # | claim | evidence |
| --- | --- | --- |
| 31 | rc-car's `car.requirements.json` names `l9110s-module` and has no copy of it | `{"part": "l9110s-module", "rails": {"VCC": "traction"}}`; rc-car's `parts/` holds no L9110S |
| 32 | `--need motor driver` lists matches from the project, shelf and library; it also lists catalog matches | `scripts/parts.py:1485-1498`; run: `l9110s-module  motor-driver` |
| 33 | spark reads the named record at every run | `scripts/design.py:174-186` |
| 34 | The record's chip `"l9110s"` becomes `chip-l9110s`, and its folder is queued | `parts/l9110s-module.json:137-150`; `scripts/sim_project.py:64-67`; `scripts/parts.py:322-324` |
| 35 | Staging copies `.c` and `.json`, reuses the `.wasm` when it is no older, and otherwise compiles and copies the binary back beside the record (into spark's folder for a library record) | `scripts/sim_project.py:142-162`; `scripts/parts.py:319` (`CHIP_SOURCE_SUFFIXES`) |
| 36 | `wokwi.toml` gets `[[chip]] name` | `scripts/sim_project.py:166-176` |
| 37 | The simulation folder is kept only with `--sim-dir` | `scripts/check_spine.py:548-549`, `:588-590`; a fresh `mkdtemp` per run at `:568` |
| 38 | Nothing downloads records, boards or chips; `--fetch` keeps only the PDFs and images a record cites | `scripts/parts.py:787`, `:1115-1144`; a grep of `scripts/` finds network calls only at `parts.py:1156` (documents) and `:1272` (HEAD checks) |
| 39 | spark ships no chip template | `chips/` holds only `wokwi-api.h`; the only `.chip.c` files are the two beside records |
| 40 | A record's copy must carry its chip folder | `scripts/parts.py:480-485` |
| 41 | The bin keeps its own copies of both chips, compiled by its own Makefile; all six files are byte-identical to spark's; nothing links them | `bin:Makefile:79-80`, `:173-178`; `cmp` of all six files, run; the bin's converter defaults to its own chips folder (`bin:tools/circuit-to-wokwi/cli.ts:24`) |
| 42 | P32b says the bin's copies go | `scrum/PRODUCT_BACKLOG.md:1459-1462` |
| 43 | A chip has no version | `parts/l9110s-module/chip/l9110s.chip.json:1-5` |
| 44 | Reuse is decided by file times, which git does not keep | `scripts/sim_project.py:147`; "Why isn't Git preserving modification time on files?" (https://archive.kernel.org/oldwiki/git.wiki.kernel.org/index.php/Git_FAQ.html) |
| 45 | The digest leaves the chip out | `scripts/parts.py:828-834` (`BUILD_FACTS`) |
| 46 | Each compile fetches whatever `wokwi-api.h` wokwi.com serves | true for spark's chain (see the first note at the end); wokwi-cli `chipCompile.ts:8`, `:15-43` |
| 47 | Two chips with one name collide silently, and the last staged wins | reproduced in `verify-runs/collide/`: `staged {'probe': 'reused'}`, `problems []`, the second binary in place, one `[[chip]]` |
| 48 | A compiled binary and a `--promote` from a project land in the plugin's folder | `scripts/sim_project.py:161`; `scripts/parts.py:1172` |
| 49 | Claude Code changes the plugin's root with every version and deletes the old one 14 days after an update | *"a plugin's root path changes with every version"*; *"It removes that directory in a background cleanup 14 days later"* (https://code.claude.com/docs/en/plugins/loading) |
| 50 | The chip's 5 ms quiet time was chosen from "the firmware's 5 kHz" | `parts/l9110s-module/chip/l9110s.chip.c:23-25` |
| 51 | irrigation's soil-probe chip states 1.2 V wet, which no fact supports | `irrigation:parts/sen0308-soil-moisture/chip/soilprobe.chip.c:3-5`, `:14-15`; no fact in its record holds 1.2 (script) |
| 52 | The VL6180X record says its chip "always reports a good status", yet the chip has a status control | `parts/vl6180x-breakout.json:156`; `vl6180x.chip.json:16-17`; `vl6180x.chip.c:71`, `:113-116` |

### §1.4 The record format

| # | claim | evidence |
| --- | --- | --- |
| 53 | The record holds 5 of the forms report's 12 forms | forms report §0, item 1; the contract is `scripts/parts.py:512-717` |
| 54 | `facts` is open-ended on purpose | `parts/l9110s-module.json:49` |
| 55 | `footprint` is one untyped string, and the generator accepts three kinds | `scripts/emit_board.py:1019-1024` |
| 56 | `body_mm` is a width and a height only | `scripts/parts.py:589-603` |
| 57 | `simulation.wokwi` is a built-in with `stand_in`, or a chip, or `skip` with a reason | `scripts/parts.py:444-494` |
| 58 | A `documents` entry holds URL, sha256, file, retrieval date, title and version | `scripts/parts.py:1036-1037`, `:1139-1141` |
| 59 | spark's design guide promises a "3D model reference" and a "footprint reference … and its source" | `skills/spark-design/references/part-data.md:56-57` |
| 60 | A fact requires `value`, `verified` and `source`, plus `why_it_matters` when unverified | `scripts/parts.py:53`, `:699-702`, `:705-709` |
| 61 | Optional `cites`, one `corroborated_by` and a `note`; the unit is a suffix of the name | `scripts/parts.py:372-381`; `:936`; `scripts/emit_board.py:398` |
| 62 | `verified` means four things in four texts | `scripts/parts.py:22-24`; `GLOSSARY.md:186-187`; `commands/research.md:13-15`; `agents/datasheet-reader.md:34-35` |
| 63 | The caliper-measured outline is `verified: true` | `parts/l9110s-module.json:111-117` |
| 64 | Minimum, typical and maximum are written three ways | `parts/led-red-5mm.json` (`forward_voltage_v` with `forward_voltage_max_v`); `parts/l9110s-module.json:70-77` (a list); `parts/max98357a-dfr0954.json`, `shutdown_threshold_v` (prose) |
| 65 | `--show l9110s-module` prints all six facts "verified" and ends with the CONFLICT line | run against a scratch store; byte-identical to `answer-runs/show-l9110s.txt` |
| 66 | Two of those facts cite no document anyone kept | `parts/l9110s-module.json:51-56`, `:70-77`; the person's store and `b12-kept-from-the-bin.jsonl` hold only the two L9110S module documents |
| 67 | The conflict is worked out from three facts and stored nowhere | `scripts/parts.py:1284-1315`, `:1337-1338` |

### §2 Other ecosystems

| # | claim | evidence |
| --- | --- | --- |
| 68 | KiCad content-manager packages carry a `versions` list | https://dev-docs.kicad.org/en/addons/ |
| 69 | The schematic embeds a copy of each symbol | *"KiCad embeds a copy of the library symbol in the schematic"* (https://docs.kicad.org/9.0/en/eeschema/eeschema.html) |
| 70 | The board embeds a copy of each footprint | *"KiCad embeds a copy of the library footprint in the board"* (https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html) |
| 71 | A KiCad package can be pinned | *"A package will not be updated if Pin Package is selected"* (https://docs.kicad.org/9.0/en/kicad/kicad.html) |
| 72 | The ERC reports "Symbol doesn't match copy in library" | `erc_item.cpp` line 218 (https://docs.kicad.org/doxygen/erc__item_8cpp_source.html) |
| 73 | "Update Symbols from Library" takes changes field by field | *"you can select which fields will be modified (updated or reset)"* (eeschema page) |
| 74 | Without `keep_on_update`, the content manager deletes a package's files on update | *"If it matches any expression then it will not be deleted"* (addons page) |
| 75 | Librarians review against the KiCad Library Conventions | *"A librarian will review the changes"*; KLC (https://www.kicad.org/libraries/contribute/) |
| 76 | `download_sha256` is optional | *"download_sha256 : (optional)"* (addons page) |
| 77 | A PlatformIO name and version *"can never be used again"* | https://docs.platformio.org/en/latest/core/userguide/pkg/cmd_publish.html |
| 78 | A PlatformIO project pins a SemVer range or an exact version | lib_deps shows `owner/name @ ~5.6,!=5.4`; dependencies page shows `^6.19.4` and `1.1.1` |
| 79 | `pio pkg outdated`, then `pio pkg update`; nothing updates by itself | *"PlatformIO does not update project dependencies automatically"* (dependencies page) |
| 80 | PlatformIO searches the project's `lib_dir` first | *"lib_dir - own/private library storage per project"*, first in the order (LDF page) |
| 81 | The Arduino registry indexes tagged releases every hour | `FAQ.md:57-62`, `:112` (https://github.com/arduino/library-registry/blob/main/FAQ.md) |
| 82 | Arduino offers an optional notice when an installed library has a new version | `FAQ.md:44` |
| 83 | The Arduino CLI pins per sketch in `sketch.yaml` profiles | https://arduino.github.io/arduino-cli/1.3/sketch-project-file/ |
| 84 | Arduino admission is by a bot and human maintainers | registry README: *"the bot and human maintainers"* |
| 85 | The Arduino index carries a checksum per release | `json.go` fields `URL` and `Checksum` |
| 86 | Fritzing's core library is a git clone, and contributions go by pull request to `develop` | *"Every fritzing installation contains a clone of this repository"*; *"Please commit your pull-requests to this branch [develop]"* (https://github.com/fritzing/fritzing-parts) |
| 87 | A Fritzing sketch bundles every part that is not core | *"If a part is not contained in the core parts, it will be bundled into your sketch"* (forum thread 25857) |
| 88 | A breaking Fritzing fix ships as a new part marked `replacedBy`, and the app offers the swap | *"add a replacedBy marker, and Fritzing will suggest to replace"* (forum thread 33872) |
| 89 | tscircuit packages are named `@tsci/<author>.<package_name>` | https://docs.tscircuit.com/web-apis/the-registry-api |
| 90 | `jlcpcb:` strings are fetched live, with no documented pin | *"tscircuit fetches the part's PCB footprint data from the configured parts engine"* (https://docs.tscircuit.com/footprints/jlcpcb-footprints) |
| 91 | SnapEDA, Ultra Librarian and EasyEDA give one download per part, with no version | easyeda2kicad README shows no version option |
| 92 | SnapEDA staff: *"It has not been verified against the datasheet"* | https://www.snapeda.com/questions/question/is-this-footprint-for-this-part-mistake/ |
| 93 | Ultra Librarian's terms forbid passing the files on | Toshiba: *"for Customer's own use and not for sale, lease or other transfer"* (WebFetch) |
| 94 | EasyEDA's terms forbid passing the files on | *"you may not copy, distribute … any information or work contained on the Services"* (https://easyeda.com/page/legal) |
| 95 | A Wokwi chip ships as a release tagged with a leading "v", holding a `chip.zip` with `chip.json` and `chip.wasm` but no source | custom-chips-to-wasm guide; `unzip -l` of the inverter and st7735 zips |
| 96 | The Wokwi command-line tool loads chips only from local files | `loadChips.ts:9-31` |
| 97 | The Chips API is *"currently in beta"* | https://docs.wokwi.com/chips-api/getting-started |
| 98 | A KiCad symbol carries Footprint and Datasheet fields | mandatory properties table (https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html) |
| 99 | KiCad SPICE fields are named `Sim.*` | `SIM_*_FIELD` defines (https://docs.kicad.org/doxygen/sim__model_8h_source.html) |
| 100 | A KiCad footprint names its 3D model by a path | `(model "3D_MODEL_FILE" …)`, *"the path and file name"* (sexpr page) |
| 101 | tscircuit's `<chip>` takes `footprint`, `cadModel` and part numbers | `manufacturerPartNumber`, `supplierPartNumbers` (https://docs.tscircuit.com/elements/chip) |
| 102 | One LCSC number yields a symbol, a footprint and 3D models | `easyeda2kicad --full --lcsc_id=C2040` |
| 103 | JEP30 part models can be digitally signed | `jep30.txt:105`, `:207` (https://www.jedec.org/sites/default/files/JEP30G.01.pdf, answers 206) |
| 104 | The provenance-shape examples hold | Wikidata `retrieved (P813)`; ECLASS levels MIN, NOM, TYP, MAX (EN 61360-1); DCC `measurementResult` and `influenceCondition` (`dcc-3.0.0.xsd:332`, `:391`); Materials Project `PropertyOrigin` with name, task_id and last_updated (`material.py:25-37`); IBIS `[Date]`; exida *"operational hours, revision history …"* |
| 105 | "Your own files win" | `docs/guide/how-it-works.md:145-147` |
| 106 | *"a project must never be surprised by a library update"* | `scripts/boards.py:33-36` |
| 107 | W21's test is "stays true without upkeep" | `commands/research.md:10-12` |
| 108 | A checksum mismatch means a different file, not a different document | `docs/2026-10-01-keeping-sources.md:48-51` |
| 109 | KiCad's content manager, the Arduino index and spark's `documents` carry a pointer plus a checksum | `download_url` with `download_sha256`; `URL` with `Checksum`; `scripts/parts.py:362-366` |
| 110 | Failures elsewhere: tscircuit's live `jlcpcb:` fetch; KiCad without `keep_on_update`; KiCad's 3D path variables | as rows 90 and 74; `${KICAD6_3DMODEL_DIR}` breakage (https://forum.kicad.info/t/many-components-pointed-at-wrong-place-for-3d-models/46966) |

### §3 The format proposal (its factual premises)

| # | claim | evidence |
| --- | --- | --- |
| 111 | Source code is pinned at a tag or commit | `docs/2026-10-01-keeping-sources.md:82` |
| 112 | "Used" stays on the private history's `ran` event | `docs/2026-10-04-store-design.md:224-243` (`:236`) |
| 113 | The bin's refs and paths exist, on GitHub | remote `xmejkal/sisuo-brain-transplant`; `0bb9d54` has `firmware/micropython/smartbin/motor.py` and `6f8fb7e` has `…/bringup/05_motor.py`; both on `origin/main`, each the latest commit for its file |
| 114 | Which check reads which fact | `scripts/parts.py:1292-1294` (`pull_conflicts`); `scripts/emit_board.py:209-215` (placement) |
| 115 | Nothing reads `continuous_current_a` or `has_enable_pin` | grep over scripts, tools, commands, agents, skills and boards finds only docs (`docs/guide/journey.md:495`, `:497`); the generic `current_of` reads only a fact a power entry names (`scripts/emit_board.py:401-420`), and the L9110S's power entries name none |
| 116 | The Handson guide was retrieved 2026-09-24, and the chip models no current | `parts/l9110s-module.json:170`, `:148` |
| 117 | The bin's five scenarios passed on files byte-identical to spark's | `bin:CLAUDE.md:98-101`; the bin's chip files last changed 2026-09-23 (`4a2b400`, `f9cb19f`), before the passes of 09-25 |
| 118 | The record asks for a resistance check on the module in hand | `parts/l9110s-module.json:88`; the pull-downs "held low" at `:162`; `bin:firmware/micropython/bringup/05_motor.py:6` |
| 119 | P136 asks for the L9110S chip to take motor current against load | spark#70 body: *"a chip that today models no current (the L9110S) could take motor current against load"* |
| 120 | A chip attribute: one binary per chip name, a value per part | `loadChips.ts` maps one wasm per name; attrs are set *"in diagram.json (under the attrs section of the custom chip part)"* (https://docs.wokwi.com/chips-api/attributes) |
| 121 | spark already passes record attributes into the diagram | `scripts/sim_project.py:62-63` |
| 122 | Extra fact keys and unknown top-level keys pass; `on_board` is read by nothing; misspellings pass too | scratch `validate`, run; `on_board` only at `parts/vl6180x-breakout.json:113`; no reader in `scripts/` |
| 123 | `verified` is required; only format version 1 validates; upgrade-on-read is designed, not built | `scripts/parts.py:53`, `:516-518`; `docs/2026-10-04-store-design.md:193-195`; no upgrade code |
| 124 | A `documents` entry needs a real sha256 and a file | `scripts/parts.py:362-366` |
| 125 | A keyword pass got some origins wrong | not re-run; consistent with the records' text: `io_volts` says *"measured into a high-impedance load"*, and the LED's note says *"a resistor computed from 1.9"* |

### §4–§6 Options, recommendation, questions

| # | claim | evidence |
| --- | --- | --- |
| 126 | The design forbids owned counts, places or reasons in a project file | `docs/2026-10-04-store-design.md:248-249` |
| 127 | P84 is parked; contributions come by reviewed pull request; documents travel as URL + sha256 | `scrum/PRODUCT_BACKLOG.md:1031`, `:1041-1044`, `:1053-1056` |
| 128 | P87 is "records that cannot act"; P92 is the writing path; P91 adds the maintainer step | headings at `:973`, `:1023`, `:1013`; spark#22 |
| 129 | spark has 7 records and 2 chips, under MIT | `ls parts/*.json` and `parts/*/chip/*.chip.c`; `LICENSE` |
| 130 | spark has a standard JSON envelope | `docs/2026-10-04-store-design.md:291-296` |
| 131 | One walk over the layers; the record store's `get` and `ids` | `docs/2026-10-04-store-design.md:257-263`, `:269` |
| 132 | `based_on` is designed; P91 extends it to `--promote` | `docs/2026-10-04-store-design.md:209-211`; spark#22 body |
| 133 | P97's digest covers board and parts, not fabrication limits | `docs/2026-10-04-store-design.md:237-240` |
| 134 | The shared layer is read last | `docs/2026-10-04-store-design.md:211` |
| 135 | *"a record grows when a stage needs a fact"* | `docs/2026-10-04-store-design.md:15`; `scrum/PRODUCT_BACKLOG.md:918`; spark#17 |
| 136 | Auto-update is off by default for a marketplace like spark's | *"off for every other marketplace"* (plugin loading page, "Which marketplaces and plugins auto-update") |
| 137 | The history is private by design | `docs/2026-10-04-store-design.md:246-251` |

---

## Notes: true, but worth knowing for the design

1. **The `wokwi-api.h` fetch (row 46) is spark's doing, not wokwi-cli's.** wokwi-cli reuses a `wokwi-api.h` that sits beside the source and downloads one only when none is there (`chipCompile.ts:15-23`, `:30`). spark stages chips into a fresh temp folder each run (`scripts/check_spine.py:568`) and copies only `.chip.c` and `.chip.json` (`scripts/parts.py:319`). It never stages its own `chips/wokwi-api.h`, 162 lines added in `1e77b88`. So every spark compile does fetch the header, and copying spark's own header into the staging folder would pin it. The bin's `sim/chips/` holds a header, so the bin's compiles do not fetch.
2. **`--fetch` also writes into spark's folder** for a library record. It rewrites the record at its home (`scripts/parts.py:1128-1143`), next to the binary and `--promote` cases §1.3 names.
3. **The digest would catch one of rc-car's three differences.** `BUILD_FACTS` includes `host_parts` but not `host_requirements`, `simulation` or `facts` (`scripts/parts.py:828`). This supports §5's choice to compare field by field and not trust a digest.
4. **The bin holds a found-out fact spark's record lacks.** `bin:parts/PARTS.md:40` records the L9110 input-low threshold (*"VL in = 0 / 0.5 / 0.7 V max"*, read off the datasheet on 2026-09-24). spark's `pull_conflicts` prints *"the module's input-low threshold is not recorded"* (`scripts/parts.py:1312-1313`). It is a live case of a property found out in a project that never reached the record.
5. **§1.4's table shows six rows of present forms (outline included) under the headline "5 of the 12".** The forms report's twelve include no outline, so the count is right and only the table reads inconsistently.
6. **The rc-car case is still a valid acceptance test for the drift report (§5 check 1),** but R1 changes its story. The library record descends from rc-car's, and neither copy records that. The drift report should not assume a library record is the origin of a same-id project record.

## What was run

- `git rev-parse`, `git status --porcelain`, `git log`, `git show`, `git cat-file` and `git branch -r --contains` in spark, the bin, rc-car, irrigation and spark-quickstart.
- `parts.py --show l9110s-module`, `parts.py --audit --project rc-car` and `parts.py --need motor driver --project rc-car`, against a scratch `SPARK_HOME`.
- Python against spark's own modules, imported with bytecode writing off: `parts.validate` and `parts.citing` on modified in-memory copies of the L9110S record, and `sim_project.stage_chips` on two scratch chips sharing one name.
- `cmp` of the bin's six chip files against spark's; a JSON compare of rc-car's `tactile-button` against spark's (today, and rc-car@`e7133e9` against spark@`1f769f8`).
- `gh issue view` of spark#17, #18, #22, #29 and #70; `gh search issues`; `gh api` of the Plot3 repository and its releases. All read-only.
- curl downloads of every cited web page into `verify-web/`, plus `https://www.kicad.org/libraries/download/` and the st7735 chip's README; WebFetch for the Toshiba page. Ranged requests confirmed the JEP30, IBIS and DCC URLs answer.
- A read-only search of this session's transcript for R24.
