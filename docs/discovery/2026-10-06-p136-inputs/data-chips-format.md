# Projects that stay current, and components that hold every form

**For:** Petr, product owner of spark. The epic is P94, "The store and its ways in" (xmejkal/spark#17).

**Your words today, in order:**

1. *"it should also be easy for projects that use spark to update their datafiles or download new components and modules as chips"*
2. *"yeah and let's have the components format include all the forms and add more and more computed or found out properties"*

The same day you also asked:

- whether spark is *"well architected so that new buses and other rules and checks can be learnt … from the experience with new and new systems"*;
- for *"good architecture so that we can nicely easily extend and update it later"*.

**About this answer:**

- **Written:** 2026-10-06, read-only, against spark at `8f7733d` and the bin at `8847eb8`. Nothing in spark was changed, and its `git status` was empty after every run.
- **Built from four reports** in this folder: `spark-today.md`, `wokwi-chips.md`, `other-ecosystems.md` and `component-forms-and-provenance.md` (the "forms report" below). Every spark line cited below was checked again against the code.
- **How claims are cited:**
  - spark claims as `file:line`;
  - the bin's as `bin:file:line`;
  - other projects by name;
  - web claims link their page (the list is at the end).
- **INFERRED** marks a sentence I reasoned rather than read or ran.

---

## The answer in short

1. **Today a project is never told that spark's data improved.**
   - If the project holds its own copy of a record, the copy stops receiving updates, silently.
   - If it holds no copy, the record changes under it, also silently.
   - A real case: rc-car's button record lacks two library improvements, and nothing says so (§1.2).
2. **A module's Wokwi chip comes along only when a project uses spark's record unchanged.**
   - Nothing downloads a record or a chip from anywhere.
   - A project that corrects one fact of a module ends up with its own copy of the record and the chip, and nothing compares that copy with the library again (§1.3).
3. **Someone who installs spark from GitHub would not receive library improvements at all.** Spark's version number has stayed `0.6.0` through 379 commits. Claude Code keeps such users on the copy they first downloaded until that number changes (§1.1). INFERRED for spark, because that install was never run.
4. **The record holds 5 of the 12 forms of a component the forms report counts.** A fact records where it came from with one `verified` flag and a prose `source`. `--show` prints all six L9110S facts as "verified", though two of them cite no document anyone kept (§1.4).
5. **KiCad's pattern fits best.** Your design keeps its own copy of each part, a check reports when the library's differs, and you take changes field by field. PlatformIO and Arduino add pinned versions, checksums and an "outdated" command. None of these tools records where a single property came from, so spark is already ahead there (§2).
6. **Proposed format:**
   - every form becomes a pointer with its own source, and the files stay in your store;
   - a fact gains an optional `origin`, with evidence to match;
   - "last confirmed" and "which decision reads it" are worked out when shown, never stored;
   - the format version stays 1 (§3).
7. **Recommended first step: a read-only drift report.** A project learns, field by field, where its copies of records and chips differ from the library or from the project they came from. Each later step waits until something needs it (§5).

---

## 1. Today

### 1.1 How each kind of data reaches a project

| data | when a project receives a change | is the project told? |
| --- | --- | --- |
| a library part or board the project names, without copying it | at every run: spark looks in the project, then the shelf, then the library, and the nearest wins (`scripts/store.py:57-77`; `scripts/design.py:174-186`, `:262-271`) | no; and nothing records what a past build rested on, because the store has no history yet (`scripts/store.py:48-49`; that history is P97, spark#18) |
| the project's own copy (from `--promote`, or copied by hand) | never: `--promote` is a plain copy, with no origin, date or digest (`scripts/parts.py:1161-1182`) | no |
| a shelf copy (a record from another project, shelved through the drawer) | never refreshed: it carries `based_on {project, digest}` (`scripts/parts.py:837-842`), and no code reads it (spark-today §2.4) | no; `commands/idea.md:64-65` promises a "re-shelve" that the code cannot do |
| `data/fabrication.json`, what the board house can make | at every run; a project overrides it key by key (`scripts/fab.py:27-38`) | no. `98ed047` (2026-10-01) moved the minimum annular ring from 0.25 to 0.18 mm under all four projects (spark-today §4, case E) |
| `.spark/rules.json` | only on `init --force`, which keeps what the person stated and fills in what is missing (`scripts/init_project.py:271-300`) | partly: `not_yet_stated` names rules the records suggest that the file lacks, for two keys (`:248-268`). This is the only "you are behind" message spark has |
| `.spark/board.json`, the resolved board | only when `boards.py --resolve` runs (`scripts/boards.py:239-257`); the bin re-resolves when the file is older than its inputs (`bin:Makefile:94-96`) | no |
| spark itself | **Your install** runs straight from your working tree, so every commit is live at the next session. Your marketplace is a local folder, and such a plugin *"loads in place … you don't need to increase the version"* ([plugin loading][cc-load]; spark-today §2.1). **A GitHub install** stays on the copy it first downloaded. Claude Code: *"a manifest that pins `"version": "1.0.0"` keeps every user on the cached copy until its author changes the string, however many commits they push"* ([plugin loading][cc-load]). spark pins `0.6.0` (`.claude-plugin/plugin.json:3`), unchanged since `02250ee` (2026-09-24) through 379 commits, 23 of them to `parts/` | INFERRED for spark: `README.md:98-99` says the GitHub install "was not run for these docs" |

### 1.2 Worked case (a): rc-car's button record falls behind

1. rc-car copied spark's `tactile-button` record into its own `parts/` and has updated it by hand twice (rc-car `87443a0`, `65dfd01`).
2. spark has since improved its record twice:
   - `1e77b88` (2026-09-29) added `simulation.wokwi`, so the button simulates as Wokwi's pushbutton;
   - `395e69d` (2026-10-03) turned a prose sentence ("give it an external pull") into a `host_parts` pull-up resistor that the board generator places (`scripts/parts.py:327-330`).
3. Compared today (run 2026-10-06), **three fields differ**:
   - `host_parts`: absent in rc-car's copy;
   - `host_requirements`: rc-car keeps the old prose sentence;
   - `simulation`: absent in rc-car's copy.
4. rc-car's copy wins because it is nearest (`scripts/store.py:70-77`). `--audit` says only *"tactile-button (project) owes: simulation"* (spark-today §2.2).
5. **The result:**
   - rc-car's next generated board places no pull-up for its buttons;
   - its simulation stage stops at this record, because the copy has no simulation (`scripts/sim_project.py:53-56`, `:125-129`).

   INFERRED: rc-car's chain was not run.

**What is missing:**

- The copy records no origin.
- Nothing compares the copy with the library.
- There is no way to take one changed field.

The pieces a compare would need already exist, unused:

- the digest (`scripts/parts.py:827-834`);
- `based_on`;
- the table of every folder an id can live in (`scripts/store.py:57-67`).

**The same failure one step further: a number copied into a project file.**

- The bin's rules file says three times that 1.5 A is *"the L9110S's own limit"* (`bin:.spark/rules.json:27-28`, `:33-34`, `:41-43`).
- spark's record keeps 0.8 A continuous as the figure for this module. It lists 1.5 A among the figures sellers quote for anything named "L9110S" (500 mA, 800 mA, 1.5 A and 2.5 A) (`parts/l9110s-module.json:57-69`). Where the bin's 1.5 A came from is not recorded. INFERRED: a seller's figure or a peak rating, neither of which any record holds as a fact.
- Because the rules file copies the number instead of naming the record's fact, no compare can ever reach it.
- spark already offers the alternative in two places:
  - a power entry names a fact instead of copying it (`scripts/emit_board.py:401-420`, used at `boards/firebeetle2-esp32s3.json:133-134`);
  - a requirements file can change a part's rail without copying the record. That exists because rc-car once copied the whole L9110S record to change one rail name, and the copy then missed every update (`scripts/design.py:134-155`).

### 1.3 Worked case (b): a new project takes the L9110S module and its chip

rc-car's `car.requirements.json` already takes this path (spark-today §2.3).

1. **Find it.** `parts.py --need motor driver --project .` lists matches from the project, the shelf and the library (`scripts/parts.py:1485-1498`).
2. **Name it.** The requirements file names `l9110s-module`. Nothing is copied: spark reads the record from its library at every run (`scripts/design.py:174-186`).
3. **Map it.** The record says `simulation.wokwi.chip: "l9110s"` (`parts/l9110s-module.json:137-150`). The part becomes `chip-l9110s`, and its chip folder is queued (`scripts/sim_project.py:64-67`; `scripts/parts.py:322-324`).
4. **Stage it.** The chip's `.c` and `.json` files are copied into `sim/chips/`.
   - If the compiled `.wasm` beside the record is no older than the `.c` file, it is reused.
   - Otherwise wokwi-cli compiles it, and the new binary is copied back beside the record. For a library record, that means into spark's own folder (`scripts/sim_project.py:142-162`).
5. **Use it.** `wokwi.toml` gets `[[chip]] name = "l9110s"` (`scripts/sim_project.py:166-176`). The project keeps the simulation folder only when run with `--sim-dir` (`scripts/check_spine.py:548-549`, `:588-590`).

**What breaks or is missing:**

- **Nothing downloads.**
  - There is no remote source of records, boards or chips. `--fetch` downloads only the PDFs and images a record cites (`scripts/parts.py:787`, `:1115-1144`).
  - A module spark lacks needs research and a hand-written chip, and spark ships no chip template (wokwi-chips §1.4 B).
- **One correction leaves the project with its own copy of the chip.**
  - A project's copy of a record must carry the chip folder with it (`scripts/parts.py:480-485`), and nothing compares the two copies afterwards (wokwi-chips §1.4 D).
  - The bin already shows this. It keeps its own copies of both chips, compiled by its own Makefile (`bin:Makefile:79-80`, `:173-178`). They are byte-identical to spark's today (`cmp`), and nothing links them.
  - The backlog item P32b already says the bin's copies should go (`scrum/PRODUCT_BACKLOG.md:1459-1462`).
- **A chip has no identity of its own.**
  - It has no version (`parts/l9110s-module/chip/l9110s.chip.json:1-5`).
  - Reuse is decided by file times (`scripts/sim_project.py:147`), which git does not keep ([Git FAQ][git-faq]). INFERRED: after a fresh clone, an out-of-date binary can look current.
  - The record's digest leaves the chip out (`scripts/parts.py:828-834`). So `based_on`, and a future "simulated" proof, cannot see that a chip changed.
  - Each compile fetches whatever `wokwi-api.h` header wokwi.com serves that day ([chipCompile.ts][cli-compile]).
  - Two chips with the same name collide without a warning: in a scratch run, the one staged last won (wokwi-chips F1).
- **spark writes into its own folder.**
  - Both a compiled binary and a `--promote` from a project land in the plugin's folder (`scripts/sim_project.py:161`; `scripts/parts.py:1172`).
  - Claude Code changes that folder with every version and deletes the old one 14 days after an update ([plugin loading][cc-load]).
  - INFERRED: on an install from GitHub, that work is lost after an update.
- **A chip's numbers are copied in by hand.**
  - The L9110S chip has a quiet time of 5 ms written into its C code, chosen from *"the firmware's 5 kHz"* PWM (`parts/l9110s-module/chip/l9110s.chip.c:23-25`).
  - In other records, such hand copies already disagree with the record (wokwi-chips F5):
    - irrigation's soil-probe chip states 1.2 V when wet, which no fact supports;
    - the VL6180X record says its chip *"always reports a good status"*, yet the chip has a status control.

### 1.4 The record format as it is

**The forms it links: 5 of the 12 the forms report counts.** The contract is `scripts/parts.py:512-717`; see also spark-today §6.4 and forms report §1.1.

| form | today |
| --- | --- |
| electrical facts | `facts`, open-ended on purpose (`parts/l9110s-module.json:49`) |
| pinout | `pin_order`, plus `pin_order_proof` saying how it was read |
| footprint | `footprint`: one string with no type and no source. The generator accepts *"a footprinter string, a converted .kicad_mod, or `jlcpcb:C<lcsc>`"* (`scripts/emit_board.py:1019-1024`) |
| outline | `body_mm`: a width and a height. Height above the board and keep-outs live only in prose notes |
| Wokwi simulation | `simulation.wokwi`, either one of Wokwi's built-in parts with a sentence saying what differs, or a chip beside the record; or `skip` with a reason (`scripts/parts.py:444-494`) |
| documents | `documents`: URL, sha256, file name, retrieval date, title, printed version. The file itself lives in your store at `sources/<sha256>/<file>` (`scripts/parts.py:352-369`) |
| **no field at all** | schematic symbol, 3D model, SPICE or IBIS model, firmware driver, where a footprint came from, order code, test procedure, proof by use. spark's own design guide promises a *"3D model reference (registry / STEP file)"* and a *"footprint reference … and its source"* that the contract has no field for (`skills/spark-design/references/part-data.md:56-57`) |

**How a fact records its origin.**

- **Required:** `value`, `verified` and `source` (`scripts/parts.py:53`, `:699-702`). A fact that is not verified but has a value also needs `why_it_matters` (`:705-709`).
- **Optional:** `cites {document, at}`, one `corroborated_by`, and a `note`. The unit is a suffix of the fact's name, such as `_v`, `_ma` or `_ohms`.
- **The kind of origin lives only in prose.** The one flag, `verified`, means four different things in four texts (forms report §1.6). Two examples:
  - the glossary says it means *"the vendor's own words at a cited URL"* (`GLOSSARY.md:186-187`);
  - yet the L9110S outline was *"measured with calipers on the module in hand"* and says `verified: true` (`parts/l9110s-module.json:111-117`).
- **Minimum, typical and maximum** are written three different ways (forms report §1.5).
- **Computed values are never stored.** The code works them out again on every read, which already suits W21.

**Seen on the L9110S** (`parts.py --show l9110s-module`, run 2026-10-06 against an empty scratch store):

- All six facts print `verified`.
  - Two of them cite no document anyone kept: *"L9110 datasheet, absolute figure"* and *"datasheet"* (`parts/l9110s-module.json:51-56`, `:70-77`).
  - Two were read off the module's own documents rather than stated in words: the pull-up resistors off the schematic (`:84-93`), and the missing enable pin off the module's header (`:78-83`).
- The output ends with a computed property that is stored nowhere:

  > CONFLICT: AIA: the board's 10000 ohm pull-down against the module's own 10000 ohm pull-up to its supply holds the pin at 0.5 of the supply (1.25 V to 6 V over its 2.5-12 V range), so it idles HIGH, not low, on any supply above 5 V (input-high threshold 2.5 V) …

- It is worked out from three facts (`scripts/parts.py:1284-1315`). Nothing on screen says that one of them was read off a schematic and two cite no kept document.

---

## 2. What comparable ecosystems do that works

### 2.1 Distribution and updates

| | what is handed out, and how a project pins it | how a project learns of an update | your own edits | trust |
| --- | --- | --- | --- | --- |
| **KiCad** | three official library repositories, tagged per release; content-manager packages with a `versions` list ([addons][kicad-addons]). Your design embeds its own copy of each symbol and footprint ([schematic editor][kicad-eeschema], [PCB editor][kicad-pcbnew]); a package can be pinned ([manual][kicad-pcm]) | the electrical rules check reports *"Symbol doesn't match copy in library"* ([erc_item.cpp][kicad-erc]); "Update Symbols from Library" takes changes field by field ([schematic editor][kicad-eeschema]) | the embedded copy survives. The content manager deletes a package's files on update unless a `keep_on_update` pattern keeps them ([addons][kicad-addons]) | librarians review against the KiCad Library Conventions ([contribute][kicad-contribute]); an optional `download_sha256` per package ([addons][kicad-addons]) |
| **PlatformIO** | a package; a published name and version *"can never be used again"* ([publish][pio-publish]). A project pins `owner/name@^1.0.0` or an exact version ([lib_deps][pio-libdeps]) | `pio pkg outdated`, then `pio pkg update`; nothing updates by itself ([dependencies][pio-deps]) | the project's own `lib_dir` is searched first ([LDF][pio-ldf]) | a sha256 checked by the client, and no review ([forum][pio-security]) |
| **Arduino** | a tagged release, indexed every hour ([FAQ][ard-faq]); the command-line tool pins per sketch in `sketch.yaml` ([profiles][ard-profiles]) | an optional notice when an installed library has a new version ([FAQ][ard-faq]) | one folder per library | admission by a bot and humans ([registry][ard-registry]); a checksum per release ([index][ard-index]) |
| **Fritzing** | an `.fzpz` file; the core library is a git clone ([fritzing-parts][fz-parts]). A sketch bundles every part that is not core ([forum][fz-obsolete]) | a breaking fix ships as a new part marked `replacedBy`, and the app offers the swap ([forum][fz-dry]) | your own parts folder | pull requests to `develop` ([fritzing-parts][fz-parts]) |
| **tscircuit** | an npm package `@tsci/author.name` ([registry][tsci-registry]); `jlcpcb:` footprint strings have no documented pin ([JLCPCB footprints][tsci-jlc]) | not documented | `tsci import` writes a local file you own ([import][tsci-import]) | none documented |
| **SnapEDA, Ultra Librarian, EasyEDA** | one download per part, with no version ([easyeda2kicad][e2k]) | download it again | overwritten | SnapEDA staff: *"It has not been verified against the datasheet"* ([Q&A][snap-wrong]). Their terms forbid passing the files on ([Ultra Librarian via Toshiba][ul-toshiba]; [EasyEDA][easyeda-legal]) |
| **Wokwi chips** | a GitHub release tagged `v<version>` with one `chip.zip`, holding `chip.json` and the compiled `.wasm` but no source ([custom chips][wk-wasm]; wokwi-chips §2.3). On wokwi.com a diagram names `github:owner/repo@1.0.4` ([tutorial][wk-7seg]); the command-line tool loads only local files ([loadChips.ts][cli-load]) | edit the version in the tag | not applicable | whoever owns the repository. There is no checksum, no registry, and the API is "currently in beta" ([getting started][wk-start]) |

### 2.2 How they bundle a component's forms

- **One identity, with the forms linked to it by name.**
  - KiCad: a symbol carries Footprint and Datasheet fields ([format][kicad-sexpr]) and SPICE fields named `Sim.*` ([sim_model.h][kicad-sim]). A footprint points at its 3D model by a path.
  - Fritzing: one `.fzpz` bundles the breadboard, schematic and PCB views ([part format][fz-format]).
  - tscircuit: `<chip>` takes `footprint`, `cadModel` and the part numbers ([chip][tsci-chip]).
  - EasyEDA: one LCSC number yields a symbol, a footprint and 3D models ([easyeda2kicad][e2k]).
  - JEDEC JEP30: a vendor's generated models, each of which can be digitally signed ([JEP30][jep30]).
- **Provenance is per file at most:** an author, a date, a verification report or a signature. No tool read here records where a single property came from (forms report §2.2). The other report adds a caveat: one of them might keep it somewhere not read.
- **Databases that do track a property's origin share one shape** (forms report §3):
  - a value with its unit;
  - a level: min, nom, typ or max;
  - the conditions it holds under;
  - evidence that carries its own date.

  Examples: IBIS ([7.2][ibis]), Wikidata ([sources][wd-sources]), IEC 61360 and ECLASS ([level type][eclass]), PTB's digital calibration certificate ([schema][dcc]), Materials Project ([origins][mp]) and IEC 61508's "proven in use" ([exida][sf-piu]). Six kinds of origin recur: stated, read, computed, simulated, measured and used.

### 2.3 What to take, and what failed elsewhere

1. **KiCad's shape is your rule plus its missing half.** spark already has the first part:
   - *"Your own files win"* (`docs/guide/how-it-works.md:145-147`);
   - *"a project must never be surprised by a library update"* (`scripts/boards.py:33-36`).

   What spark lacks is KiCad's mismatch report and its field-by-field update.
2. **Name a thing by its content, not by a version someone must remember to raise.**
   - Nobody will raise a version number on hundreds of records.
   - A digest of the content needs no upkeep, which is W21's own test (other-ecosystems, "Which fits spark", item 3).
3. **Bytes you may not carry travel as a pointer plus a checksum,** as in KiCad's content manager, the Arduino index and spark's own `documents`.
   - Vendors re-save files under the same URL, so a checksum mismatch means "a different file", not necessarily "a different document".
   - The printed version stays a document's identity (`docs/2026-10-01-keeping-sources.md:48-51`).
4. **Fritzing's `replacedBy`** splits a record that turned out to cover several parts, without breaking projects that use the old one. spark's "VL6180X breakout" record covers four different boards (other-ecosystems §5).
5. **What failed elsewhere, by cause:**
   - **silent change:** unpinned dependencies, and tscircuit's `jlcpcb:` strings fetched live;
   - **updates that delete your work:** KiCad's content manager without `keep_on_update`;
   - **links that depend on the installation:** KiCad's 3D path variables ([forum][kicad-3d]);
   - **trusting a whole part at once:** SnapEDA;
   - **dependencies that disappear:** an archived Wokwi chip ([Plot3][wk-plot3]).

---

## 3. A component format that holds every form and grows

### 3.1 The shape, in three rules

**1. Every form is a pointer with its own source, and the files stay in your store.**

- The forms the record already has stay where they are: `footprint`, `pin_order`, `body_mm`, `simulation` and `documents`.
- A new form that is a file becomes a `documents` entry with a `form` tag, such as `model-3d`, `spice`, `ibis`, `symbol` or `app-note`. With no tag, the entry is a datasheet or drawing, as today.
- A form that is code (a driver, a bench script, someone else's chip source) becomes `{url, ref, path}`, pinned at a commit, as the keeping-sources rule already says for source code (`docs/2026-10-01-keeping-sources.md:82`).
- A form spark generates names the file it was made from (`generated_from: {document, sha256}`). A new drawing then shows the generated form is out of date.
- A chip is named by the sha256 of its `.chip.c`, its `.chip.json` and the header it was compiled against. spark computes that name; it is never written into the record.

**2. A fact grows with its origin.** These keys are optional, and are checked only when present:

| key | values |
| --- | --- |
| `origin` | `stated`, `read`, `computed`, `simulated`, `measured` or `used` |
| `level` | min, nom, typ or max |
| `conditions` | the conditions the value holds under, such as a supply voltage or temperature |

Each origin carries its own evidence (forms report §4.2):

| origin | its evidence |
| --- | --- |
| stated or read | `cites`, as today |
| computed by a person | `from` (the input facts) and `formula` |
| simulated | `run`: the tool and version, each model by sha256, the scenario, the commit, the result and the date |
| measured | `measurement`: the method, the instrument, the conditions, which unit was measured, the date, who measured it, and a pointer to the bench note |
| used | not on the fact. It stays on the private history's `ran` event (`docs/2026-10-04-store-design.md:224-243`) |

**3. Two things are worked out when shown, never stored, because a stored copy would go out of date.** W21 asks of a datum that it *"stays true without upkeep"*.

- **Last confirmed** is the newest date in the fact's evidence: a document's retrieval date, a run's date, a measurement's date, or a history event.
- **Read by** comes from two places:
  - for the checks, a table in spark's code naming the facts each check reads. With it, `--validate` can list facts nothing reads, which are W21's candidates to drop;
  - for a person, `why_it_matters`.

Values the code computes are never stored either.

### 3.2 The L9110S module in that format

**What the record would store.** Only changed or added keys are shown, and everything else stays as it is today. Angle brackets are placeholders: no such values exist yet. The key names, such as `code`, are proposals.

```json
{
  "schema": 1,
  "id": "l9110s-module",
  "facts": {
    "onboard_input_pullups_ohms": {
      "value": 10000, "verified": true, "origin": "read",
      "source": "Handson guide, schematic on page 3: R2-R5, all 10K, all to VCC",
      "cites": {"document": "handson-l9110s-guide", "at": "schematic, page 3: R2-R5"},
      "corroborated_by": {
        "origin": "measured",
        "measurement": {"method": "ohmmeter from each input pin to VCC, module unpowered",
                        "instrument": {"make": "<…>", "model": "<…>"},
                        "unit": "the module in the drawer", "date": "<at B14>", "by": "person",
                        "record": "<bench note in the bin's git>"}}
    },
    "input_high_threshold_v": {
      "value": 2.5, "verified": true, "origin": "stated",
      "source": "L9110 datasheet, absolute figure",
      "cites": {"document": "l9110-datasheet", "at": "<table, page>"}
    }
  },
  "body_mm": {"width": 29, "height": 23, "verified": true, "origin": "measured",
              "source": "measured with calipers on the module in hand",
              "measurement": {"method": "calipers", "unit": "the module in hand", "date": "<not recorded>"}},
  "documents": {
    "l9110-datasheet": {"form": "datasheet", "url": "https://www.elecrow.com/download/datasheet-l9110.pdf",
                        "sha256": "<once kept>", "file": "<…>", "retrieved": "<…>", "version": "<as printed>"}
  },
  "code": {
    "driver": {"form": "driver", "url": "https://github.com/xmejkal/sisuo-brain-transplant",
               "ref": "0bb9d54", "path": "firmware/micropython/smartbin/motor.py"},
    "bench": {"form": "test-procedure", "url": "https://github.com/xmejkal/sisuo-brain-transplant",
              "ref": "6f8fb7e", "path": "firmware/micropython/bringup/05_motor.py"}
  }
}
```

**What `--show` would print from it.** Nothing prints this today. The origins are my reading of each fact's source text.

```text
fact                        value     origin    evidence                        last confirmed  read by
input_high_threshold_v      2.5 V     stated    L9110 datasheet (not kept)      unknown         pull_conflicts
supply_range_v              2.5-12 V  stated    "datasheet" (not kept)          unknown         pull_conflicts
onboard_input_pullups_ohms  10000     read      Handson schematic, page 3       2026-09-24      pull_conflicts
continuous_current_a        0.8 A     stated    Handson guide + GME datasheet   2026-09-24      no check; a person (B15)
has_enable_pin              false     read      the module's own header         unknown         no check; a person (firmware)
body_mm                     29 x 23   measured  calipers, the module in hand    not recorded    placement
computed  AIA and AIB sit at half the supply with the board's 10k pull-downs: HIGH above 5 V
          (worked out from the three facts pull_conflicts reads, on every run; never stored)
simulated chip l9110s <sha256>: the bin's five scenarios passed on byte-identical files. This
          vouches for the wiring and the firmware, not for any electrical fact: the chip models no current
used      none yet: nothing has touched hardware. B14's run of 05_motor.py would write the first `ran` event
forms     present: facts, pin order + proof, footprint headermodule6, outline, Wokwi chip, 2 kept documents
          pointed at: the L9110 datasheet URL, the driver, the bench script
          absent until a decision needs one: 3D model, SPICE/IBIS, symbol (tscircuit draws one)
```

Where those rows come from:

| row | source |
| --- | --- |
| which check reads which fact | `scripts/parts.py:1292-1294` (`pull_conflicts`) and `scripts/emit_board.py:209-215` (placement) |
| the two facts no check reads | a search of spark's scripts, tools, commands, agents and skills finds no reader of `continuous_current_a` or `has_enable_pin` |
| the dates | the Handson guide's retrieval date (`parts/l9110s-module.json:170`) |
| what the chip leaves out | the record's note (`:148`) |
| the bin's scenarios | `bin:CLAUDE.md:98-101` |
| counting the bin's passing runs for spark's chip | INFERRED: the bin ran its own copy, which is byte-identical today |

**What this example shows on a real part:**

- **The first found-out property is already asked for.** The record's own note says: *"confirm on the module in hand: resistance from each input pin to VCC"* (`parts/l9110s-module.json:88`).
- **A computed property and a measurement meet on the bench.**
  - The record asks for the 10k pull-downs so that both inputs are *"held low"* (`:162`), and the bin's bring-up step 5 asks for the same resistors (`bin:firmware/micropython/bringup/05_motor.py:6`).
  - spark's own computation says they cannot hold the inputs low above 5 V.
  - Measuring the module in hand at B14 settles it.
- **A simulated property would reach the chip as data, not as code.**
  - The motor current under load, which P136 asks about, would become a chip attribute. Every instance of the chip shares one binary and gets its own value ([attributes][wk-attrs]).
  - spark already passes such attributes from the record into the diagram (`scripts/sim_project.py:62-63`).
  - The value would not be a new constant written into the chip's C code (wokwi-chips §3).

### 3.3 How it stays compatible with today's records

- **The format version stays 1, and every new key is optional.**
  - Any extra key on a fact passes today (spark-today §6.2), and so do unknown top-level keys such as `on_board`, which nothing reads (spark-today §6.1).
  - So today's records stay valid, and an older spark reads a new record and ignores the new keys. INFERRED for the second half.
  - The other side of that: misspelled keys pass too. So the first slice of the format must check the new keys whenever they are present.
- **`verified` stays required** (`scripts/parts.py:53`), with `origin` beside it, until you decide what `verified` means (Q2).
  - If `origin` ever replaced `verified`, W16 would require every record to change in the same commit.
  - That would also need records to be upgraded as they are read. The design describes that upgrade (`docs/2026-10-04-store-design.md:193-195`), but it is not built, and the validator refuses any format version other than 1 (`scripts/parts.py:516-518`).
- **Forms stay where they are.** A new `forms` map would move `footprint` and `simulation`, and W16 would then demand that every record change at once (forms report §4.1).
- **Two contract details change.**
  - Today a `documents` entry must have a real sha256 and a file (`scripts/parts.py:362-366`). A form that is pointed at but not kept needs those two made optional. Later, `sources`, which holds URLs that nothing checks, would fold into `documents` (W16).
  - Code pointers have no file, so they need their own optional key.
- **`corroborated_by` stays a single object.** Allowing a list waits until gap G9 is fixed: today a list of citations passes the check and then crashes `citing()` (spark-today §6.2).
- **Existing facts get an `origin` when they are next touched,** by someone reading each one. An automatic keyword pass got some of them wrong (forms report §1.6).

### 3.4 How this lets spark learn from each new system

This answers your architecture question for data; a separate read of checks and buses covers the code side.

- A lesson from a new project becomes either a check (code that names the facts it reads) or a fact, with its origin, written into the record's own home.
- `--validate` then lists:
  - the facts a check needs that a record lacks;
  - the facts nothing reads.
- The drift report (§5) carries each addition to every project that holds a copy.
- `init --force`'s "not yet stated" message already works this way for rules (`scripts/init_project.py:248-268`).

---

## 4. Options for distribution and updates

Every option is held to four rules:

- every fact carries its source and verified flag;
- your own record always wins;
- vendor files stay in your local store, never in a public repository;
- W21.

| option | what a project gets | cost | keeps the four rules? | trade-off |
| --- | --- | --- | --- | --- |
| **A. Drift report**: a read-only compare, field by field | it is told where its record, board or chip differs from the library or from its source project, with each side's source and verified flag | small: the folder table, the digest and `based_on` already exist | yes: it writes nothing and downloads nothing, and your copy still wins | it tells you but fixes nothing. It compares only against what is on this machine, so a GitHub user compares against their installed version (Q3) |
| **B. Field-by-field pull, with a dry run first**, like KiCad's update | it takes the fields you choose into its own copy | one write command through `parts.py` (P92's writing path) | yes, because it only runs when you ask | needs A first; merging facts that have different origins needs a person |
| **C. Records and chips as versioned packages with checksums**, like PlatformIO or KiCad's content manager | fixed versions, and proof the bytes are unchanged | an index, a publishing step, and a version raised for every change | yes, if vendor files stay pointers | heavy for 7 records, and raising versions is upkeep that W21 rules out. A content digest gives the same identity with no registry |
| **D. A lockfile per project** (`.spark/lock.json`: each id with its layer, digest, chip digest and spark commit) | a project with no copies learns what changed since its last build, visibly in its own git and to CI | small: written at build | yes: it holds ids and digests only, and the design forbids owned counts, places or reasons in a project file (`docs/2026-10-04-store-design.md:248-249`) | it repeats P97's private `built` event (spark#18). It is worth adding only when a second machine or CI needs it (the bin's card B19) |
| **E. Contributions back by pull request** (P84's shared repository; P91's step for the maintainer) | one correction reaches every project | review, the reviewer's CI, and P87 (records that cannot act) first | yes: reviewed fact by fact, with documents as URL + sha256, never the file (`scrum/PRODUCT_BACKLOG.md:1041-1044`, `:1053-1056`) | parked until the first outside researcher (`:1031`); open questions about evidence and chip code (Q4) |
| **F. Change the design, not the record**: extend what `rails` does | fewer copies, so less to fall behind | per property | yes | works only for properties of the design, such as a rail or a chip attribute, not for corrections to the part itself |
| **G. Chips named by content** | the right binary every time; outside chips by pointer and sha256, unpacked from Wokwi's `chip.zip` | naming chips is small. Downloads need a contract that accepts a chip with no source, and chip names kept apart per record (wokwi-chips F6, F1) | yes: spark's chips are its own MIT-licensed code, not vendor files (wokwi-chips §2.6) | a Wokwi version tag does not pin the bytes, so spark adds its own checksum |

---

## 5. Recommendation

**The direction:**

- For projects, take KiCad's shape: your copy wins, spark tells you where it differs, and you take changes field by field.
- Name records and chips by their content, not by version numbers.
- Keep P84's reviewed repository of records for the shared layer, as already decided.
- Grow the format in place, keeping format version 1 (§3), adding each key only when a stage or a decision of yours first needs it.

**The smallest first step: the drift report.** A read-only `parts.py --drift --project .` (the name is to be agreed).

- **What it compares:** every part or board that the project or the shelf holds and a farther layer also holds. For a shelf copy, that includes the project it came from, named in `based_on.project`.
- **What it prints:**
  - every top-level field and every fact that differs, with each side's `source` and `verified`;
  - whether the chip differs, by the sha256 of its `.chip.c` and `.chip.json`;
  - all in spark's standard JSON reply (`docs/2026-10-04-store-design.md:291-296`).
- **How it compares digests:** it recomputes both sides rather than trusting a stored digest, because the digest's definition will change once it covers the chip.
- **What it touches:** nothing. It writes nothing and needs no network.

**It is done when these four checks pass:**

1. Run from rc-car, it names `tactile-button` and its three differing fields: `host_parts`, `host_requirements` and `simulation`.
2. A shelf copy whose source project reversed its pin order is reported. This repeats the scratch experiment in spark-today §2.4, case C.
3. A project copy of the L9110S whose chip differs by one byte is reported.
4. A project with no copies prints "nothing copied", not silence.

**Why this first:**

- It answers your first sentence for the one case that has already happened.
- It changes no format.
- Every later step needs it: the field-by-field pull, the compare against a shared repository, and showing a project a property the library has gained.

**How it fits P94, without repeating its spec:**

- **No new seam.** It reads through P94's single walk over the layers and the record store's `get` and `ids` (`docs/2026-10-04-store-design.md:257-263`, `:269`).
- **It is the first reader of `based_on`,** which P94 designs (`:209-211`) and P91 extends to `--promote` (spark#22).
- **It extends P94's digest to cover the chip** (`:237-240`), which a "simulated" proof needs anyway (wokwi-chips F3).
- **A shared repository is just one more layer.** When P84 lands, its clone is the "shared, read last" layer (`:211`), and the same report covers it with no new code path.
- **A project with no copies belongs to P97.** "What changed under me" for such a project is P97's `built` event (spark#18). Note for P97's spec: that event digests the board and the parts (`:237-240`), not the fabrication limits, so a change like case E would still go unseen.
- **It would be a new card under P94.** Where it goes relative to P97 is yours to order.

**Then, each waiting until something needs it:**

| next step | what calls for it |
| --- | --- |
| the field-by-field pull | the first difference you want to take: rc-car's button |
| chips by content in the build: reuse decided by checksum, binaries kept in your store rather than spark's folder, chip names kept apart per record | the next chip change, or the first fresh install |
| `origin` and `measurement` on a fact | the first bench number: the L9110S pull-up at B14, or B15 and B16 |
| `form` on documents, with entries that are pointed at but not kept | B23's STEP models for the enclosure |
| how spark's own updates reach GitHub installs | your answer to Q3 |

---

## 6. Questions only you can answer

1. **How does "add more and more computed or found out properties" sit with W21 and with P94's *"a record grows when a stage needs a fact"*?**

   My reading is that the growth is pulled by need, not gathered in advance:

   - A computed property grows spark's code, as `pull_conflicts` did. The record gains only the inputs that code reads.
   - A found-out property enters with its origin and evidence when a check, a stage or a decision of yours first needs it.
   - Any form that research meets may be pointed at. Its file is kept only when a decision reads it.

   Is that what you meant? Or should found-out properties be kept even before anything reads them, which would mean changing W21?

2. **What does `verified: true` mean from now on?** It means four different things in four texts today. Both the L9110S's caliper-measured outline and its pull-ups, read off a schematic, say `true`. Two ways to settle it:

   - (a) It keeps the glossary's meaning, "the maker's own words". A measurement then gets its own mark, and `origin` sits beside `verified`.
   - (b) It means "checked against its evidence", and `origin` says which kind of evidence. The glossary, `commands/research.md` and the datasheet-reader agent then change together in one commit (W16).

3. **How should spark's own updates reach people who install it from GitHub?** Its version number is pinned at `0.6.0`, and according to Claude Code's documentation such users stay on the copy they first downloaded. Until one of these is chosen, their drift report compares against an old library:

   - drop the version number, so an update takes the latest commit. Users would still have to run the update, or turn on auto-update, which is off by default for a marketplace like spark's ([plugin loading][cc-load], "Which marketplaces and plugins auto-update");
   - raise it, or tag a release, with every library change;
   - wait for the first outside user.

4. **What may come into spark from outside, and what may go out?**

   - (a) May a record point at a Wokwi chip someone else wrote, as a compiled release pinned by its sha256 with its licence stated? That is the only way "download modules as chips" reaches beyond spark's own two chips.
   - (b) May a public record (in spark's library now, or P84's repository later) carry measured or "proven by use" evidence? Your history is private by design (`docs/2026-10-04-store-design.md:246-251`).

---

## What was run for this answer

All runs set `PYTHONDONTWRITEBYTECODE=1`, and the one store run pointed `SPARK_HOME` at `answer-runs/store/` in this folder.

- `parts.py --show l9110s-module`, whose output is in `answer-runs/show-l9110s.txt`.
- A JSON compare of `rc-car/parts/tactile-button.json` against spark's library record.
- `cmp` of the bin's six chip files against spark's.
- `git log 02250ee..HEAD`: all commits, then counted per folder.
- Searches for readers of `continuous_current_a` and `has_enable_pin`.
- `gh issue view` of spark#17 and spark#70, read only.
- One page of Claude Code's documentation, read for the version-pinning sentence.

## Sources on the web

[cc-load]: https://code.claude.com/docs/en/plugins/loading
[git-faq]: https://archive.kernel.org/oldwiki/git.wiki.kernel.org/index.php/Git_FAQ.html
[cli-compile]: https://github.com/wokwi/wokwi-cli/blob/7cf4ffaebfd8c5e674038dc82c28d55be8b2c761/packages/cli/src/chip/chipCompile.ts#L8-L44
[cli-load]: https://github.com/wokwi/wokwi-cli/blob/7cf4ffaebfd8c5e674038dc82c28d55be8b2c761/packages/cli/src/loadChips.ts#L9-L31
[kicad-addons]: https://dev-docs.kicad.org/en/addons/
[kicad-pcm]: https://docs.kicad.org/9.0/en/kicad/kicad.html
[kicad-eeschema]: https://docs.kicad.org/9.0/en/eeschema/eeschema.html
[kicad-pcbnew]: https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html
[kicad-erc]: https://docs.kicad.org/doxygen/erc__item_8cpp_source.html
[kicad-contribute]: https://www.kicad.org/libraries/contribute/
[kicad-sexpr]: https://dev-docs.kicad.org/en/file-formats/sexpr-intro/index.html
[kicad-sim]: https://docs.kicad.org/doxygen/sim__model_8h_source.html
[kicad-3d]: https://forum.kicad.info/t/many-components-pointed-at-wrong-place-for-3d-models/46966
[pio-publish]: https://docs.platformio.org/en/latest/core/userguide/pkg/cmd_publish.html
[pio-libdeps]: https://docs.platformio.org/en/latest/projectconf/sections/env/options/library/lib_deps.html
[pio-deps]: https://docs.platformio.org/en/latest/librarymanager/dependencies.html
[pio-ldf]: https://docs.platformio.org/en/latest/librarymanager/ldf.html
[pio-security]: https://community.platformio.org/t/supply-chain-poisoning/19676
[ard-faq]: https://github.com/arduino/library-registry/blob/main/FAQ.md
[ard-registry]: https://github.com/arduino/library-registry
[ard-index]: https://raw.githubusercontent.com/arduino/arduino-cli/master/internal/arduino/libraries/librariesindex/json.go
[ard-profiles]: https://arduino.github.io/arduino-cli/1.3/sketch-project-file/
[fz-parts]: https://github.com/fritzing/fritzing-parts
[fz-obsolete]: https://forum.fritzing.org/t/obsoleted-parts-and-fritzing-updates/25857
[fz-dry]: https://forum.fritzing.org/t/dry-parts-using-references-to-core-svgs-obsolete-svgs/33872
[fz-format]: https://github.com/fritzing/fritzing-app/wiki/2.1-Part-file-format
[tsci-registry]: https://docs.tscircuit.com/web-apis/the-registry-api
[tsci-jlc]: https://docs.tscircuit.com/footprints/jlcpcb-footprints
[tsci-import]: https://docs.tscircuit.com/command-line/tsci-import
[tsci-chip]: https://docs.tscircuit.com/elements/chip
[e2k]: https://github.com/uPesy/easyeda2kicad.py
[snap-wrong]: https://www.snapeda.com/questions/question/is-this-footprint-for-this-part-mistake
[ul-toshiba]: https://toshiba.semicon-storage.com/eu/semiconductor/product/agree-ul.html
[easyeda-legal]: https://easyeda.com/legal
[wk-wasm]: https://docs.wokwi.com/guides/custom-chips-to-wasm
[wk-7seg]: https://docs.wokwi.com/chips-api/tutorial-7seg
[wk-start]: https://docs.wokwi.com/chips-api/getting-started
[wk-attrs]: https://docs.wokwi.com/chips-api/attributes
[wk-plot3]: https://github.com/Dlloydev/Wokwi-Chip-Plot3
[jep30]: https://www.jedec.org/sites/default/files/JEP30G.01.pdf
[ibis]: https://ibis.org/ver7.2/ver7_2.pdf
[wd-sources]: https://www.wikidata.org/wiki/Help:Sources
[eclass]: https://eclass.eu/support/technical-specification/structure-and-elements/level-type
[dcc]: https://www.ptb.de/dcc/v3.0.0/dcc.xsd
[mp]: https://github.com/materialsproject/emmet/blob/be80f08b5a8f2c82b904bacc798ca4d7bec23b46/emmet-core/emmet/core/material.py#L25-L37
[sf-piu]: https://www.exida.com/Resources/Term/proven-in-use
