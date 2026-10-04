# The store, reviewed whole — discovery for P85

**For:** the Product Owner, to decide on; and the team. **Status:** proposed — nothing here is decided
until the PO says so on the items it names. **Written:** 2026-10-04, from a council of five lenses — the
hobbyist's advocate, a data steward, a software architect, a trust-and-licensing lens, and a skeptic —
each reading both repositories and the store, read-only. **[E]** marks evidence (a file and line, or a
command and the output seen), **[H]** a hypothesis.

"The store" here is everything about where spark keeps what it finds or depends on: kept documents
(`~/.local/share/spark/sources/<sha256>/`), records (the plugin's library, a project's `parts/`, board
files, the catalog now in the person's store — P83), tools and their downloads (P82), the bin's 16 vendor
files (B12, paused after they were kept), and two ideas: a store you can choose with a shared part
database (P84), and a viewer and manager for it (P86).

## 1. The store's vision — proposed

*What spark finds once, the person keeps for good, on their own machine, and finds again from any
project — every fact pointing at the document it rests on, every document checked to be the one it
claims. What the person chooses to share, others can read and build on, reviewed; nothing spark keeps or
shares ever carries a vendor's file, a price that goes stale, where someone lives, or text that can act.*

## 2. Use cases and user stories

Each with the check that would prove it, and whether spark does it today. Personas: the **hobbyist**
(primary), the **maker** (Petr), the **agent at the keyboard** (a constraint), a **contributor** and a
**reviewer** (P84).

### Finding and reusing what was researched

| # | Story | Proved by | Today |
| --- | --- | --- | --- |
| S1 | As the hobbyist, a part I **chose** in one project shows up in the next, so I never research it twice | `parts.py --need rtc --project <another project>` lists irrigation's `dfr0641-ds3231m-rtc` | **No** [E] — it lists the 4 rejected catalog RTCs; the catalog holds only rejects |
| S2 | As the hobbyist, I build with a candidate I researched before | `--promote <id> --project .` then `--validate` is ok | **No** [E] — 0 of 18 catalog records pass the contract (9 have no `pin_order_proof`, their proof is `//pin_order` prose; 9 a pin order that is not a pad list; 6 no body) |
| S3 | As the hobbyist swapping a part, I see why I passed it over | `--show`/`--need` prints `why_not` | **No** [E] — all 18 keep it as `//why_not`, a comment nothing prints |
| S4 | As the agent, `--need` tells me what a candidate still lacks, so I don't promote it and fail the build | the `--need` row says "draft: 1 to fill — pin_order_proof" | **No** [E] — it promises "`--promote … builds with it`" (`parts.py:1257`) |
| S5 | As the hobbyist, a part I swap out is set aside, not lost | `parts.py --set-aside <id>` moves it to my store | **No** [E] — the agent writes catalog JSON by hand to a path (`agents/parts-researcher.md:57`), unvalidated |
| S6 | As the agent, I find a part by a phrase | `--need "time of flight"` finds `vl6180x-breakout` | **No** [E] — the quoted phrase misses; three words find it |

### Documents: kept, cited, recovered

| # | Story | Proved by | Today |
| --- | --- | --- | --- |
| S7 | As the agent, I can tell which document a fact rests on, at which page, and whether I still have it | `--show <id>` prints each fact's document key, page, present/MISSING | **No** [E] — `describe()` prints no citations; `--kept l9110s` says "no record here cites it" |
| S8 | As the hobbyist on a new laptop, I get back every document my records point at, and am told if the maker's URL now serves another file | on an empty store, `--fetch <id>` downloads, the sha256 matches, or it says DIFFERS | **No** [E] — `--fetch` skips any URL already in `documents` (`parts.py:971-977`) and never compares a checksum; it even prints success with the store missing |
| S9 | As the hobbyist, a datasheet I already have joins the record that rests on it | `--keep f --url u --into <id>` writes the `documents` entry | **Partly** [E] — it prints an entry to paste; a wrong path is a traceback |
| S10 | As the maker, I see what my store holds and clean it up safely | one command: location, size, records, documents, missing, uncited | **No** [E] — "uncited" depends on the project you ask from: irrigation's SEN0308 schematic reads as uncited from spark |
| S11 | As the maker, the bin's public repo holds no vendor files while every fact still finds its file | `git ls-files parts/datasheets` → 0 in the bin; `--kept <word>` prints "cited by" for each | **1 of 16** [E] — the 15 others are kept but cited by nothing |
| S12 | As the hobbyist, working offline, a fetch that cannot reach a URL says so | `--fetch` exits could-not-run | **No** [E] — "cites no datasheet or image URL to keep", exit 0 |

### Trust, privacy and licences

| # | Story | Proved by | Today |
| --- | --- | --- | --- |
| S13 | As the hobbyist, a record from someone else never runs code or writes a file on my machine without my yes | a hostile fixture record is refused by `--validate`; `--fetch` writes nothing outside the store | **No** [E] — see G1–G4 |
| S14 | As the maker publishing a project, no photo publishes where I live | a pre-push check refuses a tracked image with GPS | **Partly** [E] — only JPEGs going into the store are stripped; project photos never (irrigation's 5 photos carry GPS) |
| S15 | As the maker, my public repos hold nothing I cannot license | no vendor file reachable in the repo | **spark yes** [E] (the old history is in a private archive); **bin no** — 16 files, 7 more found, and its history |
| S16 | As the agent, I treat a record's text as data, never as instructions | the agents' instructions say so | **No** [E] — no such line in `agents/` or `commands/` |

### Sharing (P84) and the viewer (P86) — future

| # | Story | Proved by | Today |
| --- | --- | --- | --- |
| S17 | As the hobbyist on a fresh machine, I find a part someone else researched, with its pinout and its datasheet's URL and checksum | with an empty home plus the shared records, `--need rtc` lists it and `--promote` then `--validate` passes | **No** — and the assumption under it is weaker than thought: re-downloading every cited URL, 58 of 63 matched [E]; one vendor's PDF changes on every download; 9 of the bin's 16 have no URL; two are PDFs inside a zip |
| S18 | As the hobbyist, I can tell a reviewed record from an unreviewed one, and where each verified fact comes from (maker, mirror, shop, photo) | `--need` labels `[shared @<commit>]` or `[mine]` | **No** [E] — no record carries origin or review; 55 of the catalog's 190 verified facts cite a shop or mirror |
| S19 | As a contributor, I export a record carrying nothing personal or licensed, and open a pull request | `--contribute <id>` validates, filters, prepares the PR | **No** |
| S20 | As a reviewer, one command tells me what to check in a pull request | the shared repo's CI runs the contract and re-downloads each document | **No** |
| S21 | As the maker, I see, edit, download, research and find across my local store and the shared one, in one place (P86) | a viewer lists both, edits a local record, fetches a document | **No** — and needs S7, S8, S10 and a stable `--json` interface first |

## 3. Gaps — consolidated

Severity: **blocks** a story · **wrong** · **friction** · **polish**. Lens: H hobbyist, D data, A architect,
T trust, S skeptic.

### Security — before any record not written by the person is read

- **G1 · wrong (blocks S13) · T [E]** — a record's `footprint`, `name` and `host_parts.why` reach the
  generated board file unescaped (`emit_board.py:655-703`); a crafted record produced live JavaScript in
  the TSX, and `validate` returned `[]`. That `tsci build` would run it is [H] (not run).
- **G2 · wrong (blocks S13) · T, A [E]** — `--fetch` names the kept file from the URL's last segment
  after unquoting (`parts.py:981`), so `..%2F` climbs out of the store; P82's plain-name rule covers tool
  downloads only.
- **G3 · wrong · T, A [E/H]** — `documents.file` and `sha256` are never checked to be plain: with
  `sha256: ".."`, `--kept` reported a path outside the store as a present datasheet. `photo` is copied by
  `--promote` with no containment and no location stripping.
- **G4 · friction · T [E]** — a project's tools file can point a role at any executable with no notice
  at run time (`/usr/bin/true` as pdftotext); a `bundled` entry's file is not plain-name checked.

### Data model

- **G5 · wrong · H, A, D, S [E]** — **promoting to the library writes into the plugin**: the public repo
  for the maker, an install cache the next update discards for anyone else — P83's own argument. And
  `promote` copies `owned`, `sourcing` and `photo` with no validation or filter.
- **G6 · blocks S1 · H, D, S [E]** — a part chosen in one project is invisible from every other; there is no
  personal layer for chosen parts.
- **G7 · blocks S2, S4 · H, S [E]** — the catalog's 18 records fell out of the contract a day after P81
  added `pin_order_proof`; nothing walks them since P83 (P55's guarantee is gone), so nothing noticed.
- **G8 · blocks S8, S17 · all five [E]** — no document can be recovered from its URL or checked against
  its checksum; `keep_in_store` writes straight to the final file; nothing re-checks bytes.
- **G9 · wrong · D [E]** — a fact can cite only one document; a list-valued `cites` passes validation and
  then crashes `citing()`.
- **G10 · wrong · D [E]** — W21 is applied to one key in one layer: `skeleton()` still writes
  `"sourcing": []`; irrigation's records carry 13 listings; 8 catalog records keep prices in `//why_not` prose.
- **G11 · friction · D [E]** — identity is a free-form `id`; `sku` means a maker number in some records and
  a shop code in others; 62 of 65 documents have no printed version (the bin's notes even cite the
  VL6180X as Rev 6, the kept file is Rev 7).
- **G12 · friction · D, H [E]** — "uncited" depends on the project asked from, so no clean-up is safe.

### Code and tests

- **G13 · wrong · A [E]** — **the suite reads the person's real store**: 37 reads of
  `~/.local/share/spark/catalog`; a seeded home (a pin, a tool turned off, one record) fails 4 tests; an
  empty one fails a fifth.
- **G14 · blocks S5, P84 · A, H [E]** — the agents and commands are told literal paths to write to
  (`parts-researcher.md:57`, `research.md:85`, `identify.md:55`); the store cannot move while they do.
- **G15 · polish · A, D, S [E]** — the spark home is spelled twice (`parts.py:665`, `tools.py:44`), with no
  `SPARK_HOME` or `XDG_DATA_HOME`; two download paths and two checksum notions in tools.py and parts.py.
- **G16 · friction · A, H [E]** — `--catalog`, `--kept` and `--fetch` have no `--json`; the viewer (P86) and
  the agent need one.

### The bin

- **G17 · wrong · S, D [E]** — B12 is half done; its URL proofs are now saved in the store
  (`~/.local/share/spark/b12-kept-from-the-bin.jsonl`), and its remainder is bigger than three records: the
  board file cites two schematics and the ETA6003 too, and the bin's `CLAUDE.md`, `SENSOR_OPTIONS.md`,
  `calibrate.py` and an `.ino` mention the folder.
- **G18 · wrong · T [E]** — the bin is public under MIT, which offers every tracked file; beyond B12's 16,
  7 more are vendor-derived (`parts/xiao/getting_started.md`, two pinout PNGs, two JLCPCB `.obj` models,
  two copies of a `.kicad_mod`); all are in its history; 0 forks.
- **G19 · wrong · H, D [E]** — two shipped `verified: true` facts rest on documents no one else can
  obtain: the L9110S guide has no URL; the WROOM-1 v1.1's URL no longer serves v1.1.

## 4. Where the council agreed — and where it split

**All five agree:**
- **No pluggable backends now** — no database, NoSQL or Markdown store, no record/document classes
  behind interfaces: one implementation behind an interface is indirection, the catalog is 18 records
  (148 KB), and the PO's own choice (pull requests to a GitHub repo) means JSON files in git.
- **No shared document files**, ever — vendor licences grant nothing; records point.
- **Finish B12 first** — it is the one item in progress (W6), and costs no code.
- **The seams worth having are small**: one function owns where the store is; records and documents are
  written through `parts.py`, never to a path; documents are fetched once, checked, then named.

**Where they split:**
- **When P84 starts.** The skeptic: park it until the first person outside the project researches a part
  (slice 5), then run a no-code experiment — a public repo of records that pass the contract, cloned into
  the catalog folder spark already reads. The architect and the hobbyist's advocate: build the
  folder-based steps now, because they fix today's gaps anyway, and P84 becomes "one more read-only folder
  on the search path".
- **How much provenance.** The data steward and trust lens want `origin`, `review` and a fact's
  `source_kind` before anything is shared; the skeptic says pull-request review is the review.

**On the viewer (P86)**, asked of three lenses after the PO raised it:
- **It needs stable data, not an abstraction layer** (the skeptic): the files are the interface — JSON
  records in known folders and `sources/<sha256>/<file>` — read the way `catalog_records()` reads them, or
  through `parts.py --json`. `--json` exists today for `--list`, `--show`, `--need`, `--sources`,
  `--unverified`, `--signals` [E], not for `--kept`, `--catalog`, `--fetch`, `--promote` or
  `tools.py --status`. A `store.py` module owning the store is pulled by the viewer's first import, not
  before.
- **What pulls it** (any one): the shared database holds records Petr did not write; the libraries and
  catalog outgrow a screen (about 50 records; 34 today); a log of questions `--need` missed. The cheapest
  experiment then: one generated, read-only page built from the `--json` outputs, like the bin's board
  viewer; editing and research stay in Claude Code, where the contract and the agents live.
- **What it needs from the data, so it computes nothing on its own** (the data steward): stable ids and a
  natural key (maker, part number, variant) so a local and a shared copy of one part are seen as one; the
  layer each record sits in, and a `based_on` hash so drift shows; provenance and review state as fields,
  not `//` prose; one document-status answer — present, missing, changed at its URL, no URL, a member of an
  archive; JSON from every read; one writing path that validates. That makes plan items 5 to 8 its
  prerequisites — and justifies no database and no server.
- **Its rules** (the trust lens): every record string shown as escaped text, never loading a remote image
  or URL from a shared record by itself; a badge for each record's origin (library, project, mine, shared
  at a commit) and each fact's source kind, unreviewed shared records marked, a locally edited shared record
  shown as diverged; writes only through `parts.py`, and `verified: true` only with a cited document;
  shared records read-only — editing one opens a pull request; downloads only through the checked fetch;
  vendor files and photos open from the local store only, and a hosted view shows a URL and checksum,
  never the file.

## 5. One ordered plan — proposed

Each is a backlog item of its own; sizes are the lenses' estimates.

**Now**
1. **B12, finished** (about an hour, no code) — cite the 15 by key exactly as the data steward listed
   (`retrieved: 2026-09-24`, printed versions, the zip member named); fix the bin's prose and re-resolve its
   board file; then `git rm`. With the PO's answers on the 7 extra files and the history.
2. **Records are inert** (about a day) — escape every record string that reaches TSX; one containment rule
   for every path built from a record (fetched names, `photo`, `documents`); a hostile-record fixture test;
   the agents told that record text is data. Before any record not written by the person.
3. **The suite stops reading the person's store** (about half a day) — one function owns the spark home
   (`SPARK_HOME`, then `XDG_DATA_HOME/spark`, then `~/.local/share/spark`); the suite points it at a scratch
   folder. Fixes G13 and G15.
4. **`--need` tells the truth about candidates** (hours) — show each candidate's contract problems; migrate
   the 18 records' `//pin_order` and `//why_not` into fields; walk the catalog in a check again (P55);
   `--catalog --json` in the same edit.

**Next — small, and each fixes a gap someone meets**
5. **Documents come back, checked** (under a day) — `--fetch` restores a missing document from its own URL,
   downloads to `.part`, checks the sha256, says DIFFERS on a mismatch; a manifest per kept file (url, zip
   member, retrieved, version); one fetch shared by tools.py and parts.py.
6. **A shelf for the person's chosen parts** (about a day) — `--promote` from a project goes to the
   person's store, filtered of `owned`, `sourcing`, `photo`; writing the plugin's library becomes the
   maintainer's explicit step; `--need` reads project → mine → catalog → library.
7. **Written through parts.py, read as JSON** (about a day) — `--skeleton --catalog`, `--keep --into`,
   `--set-aside`; `--json` on `--catalog`, `--kept`, `--fetch`, `--show`; the agents name no paths. This is
   also the interface a viewer would use.

**Later — each pulled by evidence**
8. **Identity and provenance** (about a day) — maker part number vs shop `order_codes`; `written`, `review`,
   `origin`; a fact's `source_kind`. Pulled by P84.
9. **P84, the shared part database** — a public repo of records that pass the contract, cloned read-only
   onto the search path at a pinned commit; `--contribute` and a reviewer's CI. Pulled by the PO's choice
   below.
10. **P86, the viewer and manager** — on top of 5–8's `--json`, keeping the trust lens's rules; first as a
    generated read-only page. Pulled by one of the triggers in section 4, or by the PO.

**Not building:** pluggable storage backends; any sharing of document bytes (LFS included); a store
garbage collector (G12 makes deletion unsafe); signing or ratings; an automatic pull of the shared database
on every search.

## 6. Decisions for the PO

**Decided by the PO on 2026-10-04:** (1) a part chosen in a project goes to **a shelf in the person's
store**; writing spark's own library is a maintainer step. (2) **All 23 vendor-derived files leave the
bin's tree** (B12's 16 and the 7 more); **its history is kept**. (3) For a shipped verified fact whose
document nobody else can obtain, **find public copies first**; mark only what stays unfindable. (4) P84
**drops the database/NoSQL/Markdown half**; the plan's Now and Next steps are built; the **shared
database starts when the first person outside the project researches a part**. Items 5 below wait for
their own items.


1. **Where does a part you chose live for your next project** — a shelf in your store, with the plugin's
   library a maintainer step (the council's choice), or the plugin's library as now?
2. **The bin's public history** — rewrite it now while it has 0 forks, or accept that the vendor files
   stay retrievable from it? And do the 7 extra vendor-derived files join B12?
3. **A shipped verified fact whose document nobody else can get** (the L9110S guide; the WROOM-1 v1.1) —
   keep it verified, mark it "verified, private source", or find a public copy before B12's `git rm`?
4. **P84's timing and scope** — drop the "choose a database, NoSQL or Markdown" half (all five lenses
   agree); then build the folder-based steps now, or park the shared database until the first outside
   researcher?
5. Smaller, when their items come up: a fact resting on two documents (a list, or `corroborated_by`);
   irrigation's 13 seller listings (now, or with P77/P79); the shared records' licence (CC0 or CC-BY) and
   whether they may carry code (a Wokwi chip).

## Appendix — B12's citations, by key (the data steward, checked in memory)

One primary `cites` per fact with its `at`; a second document as `"corroborated_by": {"cites": {…}}`,
which validates today. Each document entry from `~/.local/share/spark/b12-kept-from-the-bin.jsonl`, with
`retrieved: "2026-09-24"` (when the bin first committed it) and `title`/`version` as printed. Every "kept
at parts/datasheets/… in the bin" phrase goes.

| record | document key (sha256) | cited by |
| --- | --- | --- |
| `dfr0534-module` | `dfr0534-datasheet` (d6636f…) | `has_uart_standby_command`; corroborated by `jq8400-manual-v1-3` (2c44b4…) |
| | `dfr0534-dimension-v1-0` (a1b7d6…) | `body_mm`, `mounting_holes` |
| | `dfr0534-silkscreen-photo` (23c7e6…) | `silicon`, `pin_order_proof`; corroborated by `dfr0534-ruler-photo` (271e09…) |
| | `dfr0534-product-photo` (1a712d…) | `amplifier_output_w` |
| `l9110s-module` | `handson-l9110s-guide` (2a34d4…) | `onboard_input_pullups_ohms` (p. 3), `schematic_numbers_vcc_and_gnd_opposite_to_the_silkscreen` (pp. 1, 3), `pin_order_proof`, `continuous_current_a`; corroborated by `gme-l9110s-datasheet-2016` (79ea6e…) |
| `vl6180x-breakout` | `pololu-2489-schematic` (5cac2a…) | the four carrier and pull-up facts, `pin_order_proof` |
| | `vl6180x-datasheet` (87e1b0…, "DocID026171 Rev 7") | `i2c_address`, `die_supply_v` |
| | `pololu-2489-dimensions` (c1c6c5…) | corroborates `pin_order_proof` |
| | `st-an4545` (091291…, "DocID026571 Rev 1") | no spark field; the bin's `calibrate.py` and `SENSOR_OPTIONS.md` name `parts.py --kept an4545` |
| `boards/firebeetle2-esp32s3` | `firebeetle2-s3-schematic-v1-3` (4062428…, URL the V1.3 zip, member `DFR0975 schematics V1.3.pdf`) | `vcc_is_not_tied_to_vsys`, `charge_current_a`, `hardware_revisions.v1_2_and_later` |
| | `firebeetle2-s3-schematic-v1-0` (107c54…, the same zip) | `hardware_revisions.v1_1_and_earlier` |
| | `eta6003-datasheet` (2824d0…) | corroborates `charge_current_a` |

Then in the bin: point `CLAUDE.md`, `SENSOR_OPTIONS.md` (Rev 6 → Rev 7), `calibrate.py` and the `.ino`
comment at `parts.py --kept <word>`; re-resolve `.spark/board.json`; `git rm` the 23. Done when every
`--kept <word>` prints `cited by`, never "no record here cites it".
