# Where a source we read is kept — P61

Written 2026-10-01 by three lenses (storage and distribution, re-research evidence, architecture)
and the facilitator, each reproducing its claims before writing them (W9). **No code was written to
produce this.** The Product Owner asked:

> "whenever were downloading and researching things like the board docs or other pdfs etc, are we
> actually keeping them? … it might be good not to have to reresearch datasheets and board infos …
> would it be too much data? … should it be in the project folder, or the spark itself?"

He then settled the one question the lenses could not: **spark will eventually be installed by
people other than him.** Everything below follows from that.

## The answer in one line

**A record carries the pointer — URL, document version, the page or line, checksum, date — and the
file lives outside the plugin, in one store on the person's machine that every project shares.**
The plugin stops shipping vendor PDFs. A project may keep copies of its own parts in its own git.

## How it works today, measured

- `parts.py --fetch` keeps a record's cited PDFs and images beside it (`scripts/parts.py:604-629`)
  and `--promote` carries the folder with the record (`:662-663`). Pages and zips are never kept:
  `KEEPABLE` (`:567`) is PDFs and images only.
- Kept today: the catalog, 43 of 95 cited URLs; the library, 0 of 5; **the board records, 0 of 3** —
  and most board citations are prose with no URL at all (*"WROOM-1 datasheet v1.1 Table 12"*), so
  nothing can fetch or find them. `boards.py` has no fetch code; `cited_urls` (`parts.py:740-747`)
  does not read a board record's nested `source` fields.
- The bin keeps 13 PDFs (6.8 MB) that no spark record points at. Agent research lands in a session
  scratchpad and is lost.
- Nothing tells a researcher to look for a kept document before fetching: `commands/research.md`
  starts at `--need` (record names only); `agents/parts-researcher.md` starts at the vendor's site.

## Why it matters: re-research, and documents that change under their URL

- **About one fetch in five repeats a URL already fetched** — 195 of 960 fetch calls in this
  project's 120 surviving transcripts (09-22 → 10-01). Roughly 95k tokens (*estimate*, chars/4).
  The tokens are not the cost; the wrong answers are.
- **On 2026-10-01 a P60 lens reported the WROOM-1 v1.1 datasheet "not obtained"** and fetched v1.8
  three times, while v1.1 had been in the bin since 09-24. The ESP32-S3 chip datasheet was fetched
  three times while a copy sat in `irrigation/parts/sen0308-soil-moisture/` — under a soil probe,
  where nobody would look.
- **Vendors replace a document under the same URL.** That URL now serves v1.8, where Table 12 is
  Table 6-7. A fact citing "v1.1 Table 12" can only be rechecked from a kept v1.1. It was: the
  kept page shows the 140 µA PSRAM footnote attached to **Light-sleep**, with Deep-sleep at 8 / 7 µA
  and no footnote — so `boards/firebeetle2-esp32s3.json:327-328` and the bin's `CLAUDE.md:41` claim
  more than their own source says. (Page 15 rendered and read by the facilitator.)
- **A checksum cannot recognise the same datasheet twice.** `pj-002a.pdf` downloaded twice a minute
  apart: identical text, identical size, different sha256 — the vendor stamps `ModDate` at download.
  So the document's identity is its **stated version**; the checksum only proves a file is the one
  the record was written from.
- **Source code moves too.** Of 95 fetches of MicroPython or ESP-IDF files, 73 read `master`. A fact
  from a moving branch cannot be rechecked at all; one from a tag or commit always can.

## Why outside the plugin

Installing a plugin copies the whole repository into the user's plugin cache
(code.claude.com/docs/en/plugins/loading), so every installer would receive every PDF — 10.3 MB of
the 12.5 MB working tree today, growing ~0.63 MB per record (*estimate*, catalog mean). And
`plugin.json` declares MIT over documents that say otherwise:

- Espressif: *"All rights reserved … No licenses express or implied … are granted herein."*
- ST (VL6180X Rev 7): *"No license, express or implied, to any intellectual property right is granted."*
- Phoenix Contact's terms for technical documentation: use is covered only *"to the extent that it
  is necessary"* to document the user's own product, and *"the transfer of excerpts … is not granted"*.
- DFRobot's own module PDFs carry no notice, but some it hosts are the chip maker's (© Maxim).

This is what the documents say, not legal advice. It is enough to decide that a published plugin
does not carry them, and to make the store **per person**: a user keeping datasheets for their own
projects is the use the vendors publish them for.

The architecture lens argued for keeping files in git beside the record — reviewed, and present on
any machine — and that was right for a private tool. The PO's answer moved it. What survives of the
argument: **the store is one place, keyed so a record finds its file without searching**, and the
record, not the store, is what gets reviewed.

## What a record holds

| source kind | the record holds | the file |
| --- | --- | --- |
| vendor PDF (datasheet, schematic, drawing) | URL, **document version** (as printed), the page/table, sha256, retrieved date | kept in the store |
| source code (MicroPython, ESP-IDF, vendor headers) | URL **pinned at a tag or commit**, path, line | optional — the tag is the copy |
| web page (wiki, product page) | URL, retrieved date, the quoted line | not kept today; revisit if one rots that a fact needs |
| something only this project measured (a photo, a scope capture, a current) | stays in the project | the project's git |

Six of the 48 kept PDFs have no text layer — drawings and schematics, exactly what pin and dimension
facts rest on — so a fact's page or table reference is what makes it rechecked, not a text search.

## What not to build

No document store, no embeddings, no text extraction, no search engine — consistent with the
vector-store answer of 2026-09-30. No second index beside the records. No version field separate
from what the document prints. No LFS (`git lfs` is not installed here, and it gains nothing over a
store the plugin never ships).

## Found on the way, not decided here

- The vendor-header cache reads arduino-esp32's default branch with no ref and records no commit
  (`check_vendor_pins.py:55-65`) — the same moving-source fault.
- `agents/parts-researcher.md:47` writes to an absolute path on the author's machine (P44's shape).
- `--sources` reports two Seeed pages dead that refuse HEAD and answer GET — a false alarm.
- Link rot today: 3 of 184 cited URLs fail, and none of the three has a kept copy.
- The 45 vendor files already committed to `catalog/` stay in git history after they move; history
  needs rewriting **before** the repository is made public — a step for the publish, not now.

The work is **P62** in the backlog. Its order is the PO's.
