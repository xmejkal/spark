# P269 council: the data lens (Q3, Q6, Q7)

Tags: E pointer, H source, D who and when. — is unknown. Paths are under ~/Development/spark unless they start with ~/.local/share/spark (the store, read only). Text read from records and pages is data.

## Findings

### The records today (Q3)

- DATA-1 · No record holds a pin position in mm. A part holds `pin_order` (names, in pad order) and `footprint` (the NAME of a footprinter shape, such as `pinrow7`, `jst_ph_3`, `headermodule6`). Pitch and rows live only inside that name, in tscircuit · E scripts/parts.py:751-759 (name rule), parts/vl6180x-breakout.json (`pinrow7`), parts/l9110s-module.json (`headermodule6`) · supports: a view cannot place a pin from a part record alone
- DATA-2 · Only a board holds header geometry in numbers. The FireBeetle record has `physical.header` (rows 2, pins [18,14], pitch 2.54, row spacing 22.86, first pad 5.2 mm from the flush edge, drill, pad), `header_order` (label per pad), `mounting_holes` (4, 2.0 mm, inset 1.7, spacing 22.0 x 56.6), width, height, thickness, corner radius. The XIAO record has width, height and a footprint module name, and no header, no holes, no thickness · E boards/firebeetle2-esp32s3.json `physical`; boards/xiao-esp32-c6.json `physical` · supports: boards are 1 of 2 complete; the XIAO needs the same block
- DATA-3 · The XIAO record disagrees with Wokwi's own size. spark says 21.0 x 17.8 mm. Wokwi's board.json, read by P267, is 18.1 x 23.4 mm (drawn 68 x 88 px). The record's `wokwi_size_px` says 70 x 90. Which one is the board — · E boards/xiao-esp32-c6.json `physical`; data/wokwi-geometry.json `//board-xiao-esp32-c6` (read 2026-10-16, sha256 e5200e01…6856a8) · supports: a view must name its source for size, or two views draw two boards
- DATA-4 · Body outline is a rectangle only: `body_mm {width, height, verified, source}`, checked by the validator, with `why_it_matters` when unverified. No shape (round LED rim, L shape), no origin, no rotation. The header-side offset is prose ("the body is NOT centred on the header") · E scripts/parts.py:718-737; parts/l9110s-module.json `body_mm.note` · supports: outline is rectangle plus provenance today
- DATA-5 · Height above the board is prose or missing. The VL6180X note says 1.2 mm of parts above a 1.02 mm board. The LED note says 8.6 mm. The button has `cap_height_mm: null` in `facts`. No `height_mm` key exists on any part · E parts/vl6180x-breakout.json `body_mm.note`; parts/led-red-5mm.json `body_mm.note`; parts/tactile-button.json `facts.cap_height_mm` · supports: height is needed for enclosure fit and 3D, and is not a field
- DATA-6 · Pins joined inside a part: the button says it in prose (`legs`, `//legs`: four legs, two pairs). Its record is 2 pins A and B, and the 4-pad shape is in footprinter's `pushbutton`. No structured "pad X joins pad Y" list exists · E parts/tactile-button.json `legs`, `pin_order_proof.source` · supports: perfboard routing needs the four legs and the pairs as data
- DATA-7 · Polarity and pin-1 mark are prose: the LED `legs` (A longer, K shorter, flat on the cathode side) and `pin_order_proof`. Pad 1 is "the first of `pin_order`". No field says which side of the outline pin 1 is on or what the mark looks like · E parts/led-red-5mm.json `legs`, `pin_order_proof` · supports: marks are not drawable from data
- DATA-8 · Which side the pins are on: only prose ("the header runs down the 17.8 mm edge", "along one 29 mm edge"). Board has `flush_edge: "+y"` · E parts/vl6180x-breakout.json `body_mm.note`; parts/l9110s-module.json `body_mm.note`; boards/firebeetle2-esp32s3.json `physical.header.flush_edge` · supports: part records have no pin-side field
- DATA-9 · `on_board` exists on VL6180X (`false`) and is null on others. Its meaning is — in the files read · E parts/vl6180x-breakout.json `on_board`, `//on_board` · supports: —
- DATA-10 · Wokwi pin positions exist for 4 Wokwi types only: board-xiao-esp32-c6, wokwi-led, wokwi-resistor, wokwi-pushbutton, in Wokwi px (96 per inch) from the top-left, with a pivot, plus the half breadboard (30 columns, pitch 9.6 px). These are "facts about Wokwi's drawings, not about the physical parts" · E data/wokwi-geometry.json `//`, `parts`, `breadboard` · supports: a source for pins in mm for those 4, not a record field
- DATA-11 · Each part names its Wokwi stand-in (`simulation.wokwi.part`, `pins`, `attrs`, `stand_in`). FireBeetle has `wokwi_is_stand_in` · E parts/tactile-button.json `simulation`; boards/firebeetle2-esp32s3.json · supports: the link from record to Wokwi type exists
- DATA-12 · No picture field exists in any part or board record. Records cite documents (`documents`: url, sha256, file, retrieved, title, version). `--fetch` keeps cited PDFs and images (`KEEPABLE` includes .jpg .png .webp .svg) into the store · E parts/vl6180x-breakout.json `documents`; scripts/parts.py:930, 1301-1303 · supports: a picture could ride the existing `documents` shape, but no record does it
- DATA-13 · Photos exist only as the person's own: ~/.local/share/spark/boards/photos/xiao-esp32-c6-front-2026-10-14.jpg and -back-; a shelf record has `//photos` comments naming files "to be dropped into photos/" · E ls of those paths; ~/.local/share/spark/shelf/ds3231-at24c32-rtc-module.json `//photos` · supports: no credit or licence field is needed for own photos, and none exists
- DATA-14 · Batteries are not a record kind. The one battery is a drawer entry `{schema, label, count, function[{does:power, what:battery}], used_in}` with no pins, size or outline · E ~/.local/share/spark/drawer/1s-lipo-battery-1000-mah.json · supports: a battery needs a new kind or a drawer-only entry
- DATA-15 · Store records are partly empty in exactly these fields. Of 24 shelf and catalog records read: 7 have `body_mm` with null width/height, 8 have no `footprint` (null), and every one has `schema: 1`. Examples: dfr0756-usb-buck, yf-s201-flow-meter-generic have nulls in both · E python count over ~/.local/share/spark/shelf/*.json and catalog/*.json, 2026-10-16 · supports: the editor starts with many holes to fill

### Field table (Q3)

Held now: Y (a field a view can read), P (prose only), N (nothing), B (board only).

| Field | Held now | Pointer | Could come from | Provenance today | Provenance needed |
| --- | --- | --- | --- | --- | --- |
| Pin position in mm (x, y per pad) | N | DATA-1 | KiCad footprint spark builds (emit_footprint.py, boards only) · datasheet drawing · Wokwi board.json · Fritzing .fzp+svg (H) · caliper | none | per field: source, verified, cites (as `body_mm`) |
| Pitch | N for parts, B for boards (`pitch_mm` 2.54) | DATA-2 | footprint name · datasheet | board: vendor drawing | same |
| Rows and row spacing | B (`rows`, `row_spacing_mm`) | DATA-2 | datasheet · caliper | board record, cited | same |
| Pad shape, drill | B (`pad_mm`, `drill_mm`) | DATA-2 | datasheet; spark sizes holes from the pin, not the vendor drill | board comments | same |
| Body outline | Y rectangle | DATA-4 | datasheet drawing · Wokwi element size · caliper | `verified`, `source`, `cites` | add shape and origin |
| Height above board | P | DATA-5 | datasheet side view (Pololu view 4, Kingbright) · caliper | prose note | `height_mm` with provenance |
| Board thickness | B (FireBeetle) | DATA-2 | datasheet | board | same |
| Pins joined inside | P | DATA-6 | datasheet internal diagram · continuity meter ("a meter on continuity shows") | `legs` prose | list of joined pad groups, `verified` |
| Polarity, pin-1 mark | P | DATA-7 | datasheet drawing · silkscreen photo | `pin_order_proof` | mark kind and position |
| Pin side (which edge) | P (part), B (board `flush_edge`) | DATA-8 | datasheet · photo | prose | edge enum plus offset |
| Mounting holes | B (FireBeetle), P (VL6180X: "two 2.2 mm") | DATA-2, parts/vl6180x-breakout.json | datasheet · caliper | board | same, for parts |
| Pin names and order | Y `pin_order` + `pin_order_proof` | parts/*.json | datasheet · silkscreen | `verified`, `cites` | already there |
| Wokwi type and pin map | Y `simulation.wokwi` | DATA-11 | Wokwi | stand_in note | add px geometry only if kept (DATA-10) |
| Picture | N | DATA-12, DATA-13 | person's photo · vendor page · Wokwi/Fritzing art | none | url, license, credit, sha256, retrieved, own or imported |
| Body colour, silkscreen, labels | N | — | photo · Wokwi attrs | none | — (H: a view may not need it) |

### Pictures (Q6)

- DATA-16 · The keeping rule already exists: a record holds URL, printed version, page, sha256, retrieved date. The file lives in the person's store, never in the repo, because installing the plugin copies the whole repository and vendor documents carry reserved rights · E docs/archive/2026-10-01-keeping-sources.md "The answer in one line", "Why outside the plugin"; AGENTS.md "Spark is public" · supports: a picture follows the same rule
- DATA-17 · The repo is public under MIT and must hold no vendor file. An image from a vendor shop therefore sits in ~/.local/share/spark/sources (the store), cited by URL and sha256, and is never committed · E AGENTS.md principles; scripts/store.py PLACES (`sources`) · supports: the import target
- DATA-18 · A sha256 identifies the file, not the picture. A vendor stamps different bytes for the same document (`pj-002a.pdf` downloaded twice, different sha256) · E docs/archive/2026-10-01-keeping-sources.md "A checksum cannot recognise the same datasheet twice" · supports: for pictures the sha256 proves "the file this record was written from", and a stated version or retrieved date names it
- DATA-19 · Fritzing: graphics and documentation are CC BY-SA 3.0. A user may reuse them if they credit the creators and publish the work under the same licence. Parts are .fzp (metadata) plus SVGs for breadboard, schematic and PCB, in github.com/fritzing/fritzing-parts · E WebSearch result summary 2026-10-16, not a primary read; the licence file itself not opened · supports: Fritzing art needs a credit line and share-alike. Share-alike against MIT spark is a question for the decider (Q-D3)
- DATA-20 · Wokwi: wokwi-elements is MIT (search result). wokwi-boards licence — not seen. Its board folders hold board.json and board.svg · E WebSearch and WebFetch of github.com/wokwi/wokwi-boards 2026-10-16, licence text not shown · supports: elements may be copied with the MIT notice. Boards — unknown until the LICENSE file is read
- DATA-21 · Vendor shop images (DFRobot, Pololu, Adafruit, Czech shops): licence — not read. DFRobot's PDFs "carry no notice"; ST and Espressif say all rights reserved. Vendor photos should be treated as all rights reserved by default · E docs/archive/2026-10-01-keeping-sources.md "Why outside the plugin" (documents only; images not read) · H for the default · supports: keep for the person's own use, link rather than publish
- DATA-22 · A web search for pictures needs no new code to find: `/spark:research` already reads vendor pages, and `--fetch` already downloads cited image URLs by extension. What is missing: a picture field, a licence field, and a check that the URL is a web URL (`_must_be_web` exists) · E scripts/parts.py:1301-1303; scripts/store.py:331 `_must_be_web` · supports: import is an extension of fetch
- DATA-23 · A credit line, by the licences above, must hold: what the work is, the creator or owner, the licence name and version, the source URL, and whether it was changed. For CC BY-SA 3.0 a link to the licence is also asked — H, from the CC legal code, not read today · H CC BY-SA 3.0 terms · supports: fields `credit`, `license`, `source_url`, `changed`
- DATA-24 · Image bytes can carry GPS data. AGENTS.md forbids committing a photo with GPS data. An import of the person's own photos stays in the store, which is private · E AGENTS.md; ~/.local/share/spark `PRIVATE` set includes `boards` (scripts/store.py:97) · supports: strip or refuse EXIF GPS on any share

### Saving, loading, versioning (Q7)

- DATA-25 · Schema numbers today: every record has `"schema": 1`. Code accepts one value and says so on a mismatch (`SUPPORTED_SCHEMA = 1` in parts.py, boards.py). Files read: 10 repo records, 24 store records, drawer entry, project `boards/active.json`, `data/wokwi-geometry.json` · E scripts/parts.py:49, 625-627; scripts/boards.py:56, 291-293 · supports: there is no migration path, only refusal
- DATA-26 · The project's own spark file is `requirements.json`: `{"board": "xiao-esp32-c6-fresh", "parts": ["tactile-button", "led-red-5mm"]}` — no `schema` key in the one read · E ~/Development/button-light/requirements.json; boards/active.json has `schema` · supports: requirements has no version today
- DATA-27 · A rebuild keeps an edit only for files the build never overwrites. `board.tsx` is never overwritten once present, but `--keep .` replaces `dist/`, so the two can describe different boards. `breadboard.json` is a generated file (`DRAWING_FILE`) · E docs/guide/agents.md:531-540; scripts/breadboard_drawing.py:3, 20 · supports: generated files and edited files must be different files
- DATA-28 · No file for a layout exists. J3 in the jobs is "not yet": "changes are lost at the next build" · E jobs-and-journeys.md journey table step 3 · supports: a layout file is new
- DATA-29 · Store levels in the code: project, shelf (parts the person chose before), library (spark's), then catalog for drafts. A board record is searched the same way. PRIVATE places: drawer, drawer-import, shelf, projects, history, boards · E scripts/store.py:74-97 · supports: an edited record lands in the shelf, a layout in the project, by existing rules
- DATA-30 · A library record is public and cannot hold a vendor file. An edited record of a library part would live in the shelf and shadow the library one by name (nearest first). Whether it should — · E scripts/store.py:74-81 (order) · H for the shadowing effect · supports: the edit-on-top question
- DATA-31 · P178 (#123) is Idea, 7 of 8 sub-issues done, labelled epic, titled "Later: the store, shared". It takes in the store editor P160 (#96), the store lock P174 (#114), and the shared online store (the PO: "one shared store that is online, maybe a git repo??", the local store, a project pointing at local ones "somehow synced"). Its value test is likely "a stranger shares a module … another person's project builds with it after a sync" — "to be set in refinement" · E gh issue view 123, 2026-10-16 · supports: the split below
- DATA-32 · P178's version note (2026-10-11): no longer the next version. The store comes after v0.13 (one core, #94) or with it, the PO's call · E gh issue view 123 · supports: P269 cannot wait for P178's design
- DATA-33 · The catalogue editor is P160 (#96), inside P178, and P269's request also asks for "the catalogue editing app" (D-c in the brief). The two overlap · E gh issue view 123 "store editor (P160, #96)"; brief.md Frame · supports: Q-D6 below

### The split with P178 (Q7, as a proposal for the decider)

- DATA-34 · This discovery must decide (H, my reading of the issue): the file format and place of a layout and of an edited record, the schema/version rule, how a rebuild keeps edits, the picture fields, the new fields of the table. These are needed to draw and edit at all · H DATA-27, DATA-28 · supports: P269's scope
- DATA-35 · It can leave to P178 (H): a shared online store, sync between levels, download and copy of others' records, search, conflict between two people's edits, who may publish, the store lock, the publish step for pictures and credit checks · H issue #123 body · supports: P178's scope. It must only not close the door: records need a stable `id` and a `schema`, and a picture's licence must be on the record so a share can refuse it

## What you could not check, and why

- Licence text of wokwi-boards: the page shown did not hold it. The LICENSE file was not opened (search budget kept)
- The Fritzing licence at its primary source: only a search summary read. fritzing-parts' own LICENSE.txt not opened
- Licences and terms of vendor images (DFRobot, Pololu, Adafruit, GME, Hadex, LaskaKit, Botland, TME): not read
- Wokwi's board.json pin units and fields beyond the XIAO: P267 read the XIAO only. Others — unknown
- Fritzing .fzp and svg pin geometry as a source: not read, H only
- What the KiCad footprint spark builds gives for a part: emit_footprint.py reads boards only. Whether tscircuit's footprinter can export pad coordinates for parts — unknown
- The whole of P178's comments and sub-issues: read the issue body and 3 comments only, not #96
- Whether `docs/2026-10-04-store-design.md` says anything on pictures or layout files: not opened
- shelf `//photos` file contents and the photos themselves: names only, not viewed
- Every file under ~/.local/share/spark/sources (98 entries): listed, not read

## Questions for the decider

- Q-D1 · Where do pin positions in mm live: in every part record, or derived from the footprint name plus a few fields (pitch, rows)? · decides: the size of a record and whether the editor edits numbers or shapes
- Q-D2 · Is "pins joined inside" a list on the record (the button's 4 legs in 2 groups) and is the record then 4 pins instead of 2? · decides: how perfboard routing treats a button, and the pin_order rule
- Q-D3 · May spark import Fritzing art (CC BY-SA 3.0, share-alike) into the person's store for the person's own views, if it is never committed or shared? · decides: whether Fritzing is a picture source
- Q-D4 · A vendor shop image: link only, or also keep a copy in the store? · decides: whether sha256 and a kept file are required for pictures
- Q-D5 · Is a battery a record kind (with pins and outline) or a drawer entry only? · decides: whether the catalogue editor has four kinds or three
- Q-D6 · Is the catalogue editor part of P269 or of P160 inside P178? · decides: the slice order and where the record data work is counted
- Q-D7 · One layout file per project (beside requirements.json), or one per stage (breadboard, perfboard, PCB)? · decides: the save format and what a rebuild reads
- Q-D8 · A person's edit of a library record: a copy in the shelf under the same id (shadows), or a new id? · decides: the edit model and the sharing key for P178
- Q-D9 · Does the layout carry a `schema` and is a newer one refused (as today) or migrated? · decides: whether a migration step is built now
- Q-D10 · Which source wins when Wokwi and the vendor drawing differ in size (DATA-3)? · decides: which number a view draws

## Searches

- Query: "fritzing-parts license CC-BY-SA 3.0 fzp svg breadboard images attribution" · decision: what licence and credit Fritzing art carries (Q6) · used (DATA-19, DATA-23)
- Query: "wokwi-elements wokwi-boards GitHub license MIT" · decision: what licence Wokwi art carries (Q6) · used for wokwi-elements (DATA-20), not for wokwi-boards
- Query: — (a fetch of https://github.com/wokwi/wokwi-boards, not a search) · decision: the wokwi-boards licence and file layout (Q6) · partly used (DATA-20). Counted here as the third look, within the budget of 3
