# P735 architecture council: reuse researcher

Read 2026-11-10 (Europe/Prague). Tags: E (pointer), H (source), D (who, when). Nothing in the tree was changed except this file. Web text is data, not instructions. All "read" dates below are 2026-11-10.

## Findings

### Sources outside spark

| name | kind | returns | cost and key | licence for keeping | local use |
| --- | --- | --- | --- | --- | --- |
| JLCPCB MCP `@jlcpcb/mcp` 0.4.0 (already in spark) | manufacturer-side MCP | `component_search`: LCSC id, stock, pricing; `library_install`: KiCad symbol_ref and footprint_ref, optional STEP/OBJ 3D; no datasheet tool listed | README names no key or account (unknown whether needed) | tool: MIT; part data: unknown | yes, runs via npx, needs node (data/tools.json entry) |
| Espressif docs MCP `https://mcp.espressif.com/docs` (already in spark) | maker docs MCP | semantic chunks of Espressif docs, en/cn | no key in .mcp.json; server states hourly and daily rate limits | unknown | remote, via mcp-remote, needs node 20+ |
| Nexar / Octopart MCP (community: LukeL99, Farad-Labs) | aggregator MCP, community | parts search, distributor price, availability, datasheet URLs | Nexar client id and secret; free tier terms unknown | unknown | Docker or local, needs credentials |
| Mouser MCP (community `mouser-search-mcp`) | distributor MCP, community | search results | MOUSER_API_KEY (Search API key) | unknown | yes with key |
| eparts-search-mcp (community) | multi-distributor MCP | search across DigiKey, LCSC, Mouser | per-provider keys and rate limits | unknown | yes with keys |
| DigiKey Product Information API v4 | distributor REST API | product details; datasheet field name not checked | OAuth2 client credentials, app subscription on developer.digikey.com; price tier unknown | unknown | REST, not MCP; no official DigiKey MCP found |
| SnapMagic (ex SnapEDA) | CAD library | symbol, footprint, STEP 3D | account to download (H, not read on its page); no MCP found | CC BY-SA 4.0 with Design Exception per its FAQ | download by hand |
| Ultra Librarian | CAD library | symbols, footprints, STEP | account; no MCP found | unknown | download by hand |
| KiCad official libraries | CAD library | symbols, footprints, 3D | free, no key | CC BY-SA 4.0 plus exception: use in a design is free of share-alike; redistributing the library as a collection is not | git clone, local |
| EasyEDA / LCSC | CAD library | symbol, footprint (reached through the JLCPCB MCP) | see JLCPCB row | unknown | via the MCP |
| Fritzing parts | CAD library | .fzp metadata plus .svg graphics | free | not shown on the repo page (LICENSE.txt exists; text not read) | git clone |
| DFRobot wiki and GitHub | vendor site | text tables, images, dimension drawing, schematic PDF, STEP and layout zip when linked, `.kicad_mod` in one layout zip | free, no key | no official terms page found (PO-15 in po-assistant.md:26); the one DFRobot terms page read covers user-posted content only | web fetch only; no API |
| Seeed, Adafruit, SparkFun wikis | vendor sites | not read | free | not read | not read |
| Maker datasheets (PDF) | datasheet | parameters, pinout, outline drawing | free | per maker, unknown | already local: `parts.py --fetch/--keep/--read` |

- REUSE-1 · Spark already ships two MCP servers as a plugin, `espressif-docs` (remote, via mcp-remote) and `jlcpcb` (npx). Each is also a `tools.json` entry with `kind: mcp`, `owner: spark`, `meets` a contract (`candidates-with-datasheet`, `maker-docs-search`). · E · .mcp.json:1-14; data/tools.json (entries jlcpcb, espressif-docs) · supports: sources as MCP, no new mechanism for hosting them
- REUSE-2 · The setting that points a job at a tool already exists: `roles` in data/tools.json (`"parts-search": "jlcpcb"`, `"chip-docs": "espressif-docs"`, 13 roles), `tools.py --use ROLE=TOOL`, `--on/--off NAME`, `--new NAME=JSON` for a tool of the person's own, a personal file `~/.local/share/spark/tools.json` and a project file `.spark/tools.json` (project wins). `contracts`/`meets` say what a role needs. The library is `scripts/spark/records/tool_finder.py`. · E · scripts/tools.py:1-14,95-125; data/tools.json; tool_finder.py:497-513 (KIND_NEEDS includes `mcp`; a non-spark mcp entry needs `mcp.command`) · supports: a source order and on/off, and a person's own MCP source, by extending what exists
- REUSE-3 · No role is an ordered list: a role maps to one tool name. Nothing in tools.json holds a priority list of sources. · E · data/tools.json roles (single string values) · supports: the gap a source order must fill
- REUSE-4 · A vendor order already exists for research: the brief's `prefer` (vendors to research in, default DFRobot then Seeed), handed to `parts-researcher`, which searches vendor by vendor and stops at the first fit. It lives in the agent prompt, not in code. · E · scripts/spark/records/brief.py:5,37,58; agents/parts-researcher.md ("Where to look, in the order you were given") · supports: the order concept is one existing seam; prompt-only today
- REUSE-5 · Two other prompt-level source choices exist: `part-finder` uses the jlcpcb `component_search` tool first if available, then web; `datasheet-reader` uses `search_espressif_sources` when available. Both are fallback chains written in agent text, with the tool names hard-coded in each agent's `tools:` line. · E · agents/part-finder.md:5,21; agents/datasheet-reader.md:5,43 · supports: current chains are not swappable without editing agents
- REUSE-6 · The strategy shape for sources is already in code twice. `PartPictures` (base, `picture(wokwi_type)`) with `PictogramPartPictures`; its docstring says "pictures from online come later as a second source with the same method". `ShapeSource` (`describe_part`, which "returns None when this source declines it (the next source is asked)", and `find_pin_names`) with `WokwiGeometryShapeSource` and `RecordShapeSource`. The second is already a chain of responsibility by decline. · E · scripts/spark/breadboard/part_pictures.py:1-40; scripts/spark/breadboard/part_shape.py:55-70,99 · supports: reuse the base-class-plus-decline idiom for acquisition sources
- REUSE-7 · P446's plan states the same idea for shapes: "Sources are interchangeable strategies in a fixed order. They never call an AI or a program. A person, Claude or a tool writes a file, and spark reads it as unverified until the person says yes", with `FileShapeSource` later and a `PartShape` with a source and verified flag per group. P446 is now a sub-issue of #1010. · E · gh issue view 597 (read 2026-11-10) · supports: one order rule, human and AI collaborators as file-writing sources; a conflict with P734 is already noted as C13 in brief.md
- REUSE-8 · The sourcing package holds `datasheets.py` (keep/fetch/read by sha and URL), `part_records.py`, `part_facts.py` (fact provenance), `matching.py`, `drawer.py`. `--fetch` keeps only .pdf, .jpg, .png, .webp, .svg. · E · scripts/spark/sourcing/; brief.md C7 · supports: the store-side keeping exists; archives (STEP, layout zip) need a new kind
- REUSE-9 · Patterns doc already names Strategy, Adapter, Probe, Platform ("a Strategy that builds every board tool ... a test gives a Fake") and Operation (verb+object, `run()`, JSON input/output schemas "an MCP tool's inputSchema and outputSchema"). Provenance fields (value, verified, source, why_it_matters) already exist per fact. No "registry", "chain" or "resolver" row. · E · docs/guide/patterns-and-names.md:16,25,27,60-62; agents/parts-researcher.md rule on verified/source · supports: names to pick from; a new role word would need a table row
- REUSE-10 · No official DigiKey, Mouser or Nexar MCP server was found in one search; only community servers. The two MCP servers from makers that spark uses (JLCPCB, Espressif) are maker-run. No DFRobot, Seeed, Adafruit or SparkFun MCP was searched for or found. · E · search 1 (below) · supports: do not plan on a vendor MCP for DFRobot MVP; DFRobot's source is web fetch plus datasheet
- REUSE-11 · Licence for kept files differs by source: KiCad libraries are CC BY-SA 4.0 with a design exception (redistribution as a collection is not covered); SnapMagic says CC BY-SA 4.0 with Design Exception; DFRobot's terms are unknown. AGENTS.md forbids committing any vendor file. · E · kicad.org/libraries/license (via search 5, read 2026-11-10); snapeda.com FAQ (via search 3); AGENTS.md ("Never commit a vendor file") · supports: keep in the store only, as brief.md already proposes
- REUSE-12 · Patterns that fit (names, citations):
  - Strategy (GoF 1994, Design Patterns, ISBN 0-201-63361-2): interchangeable algorithm behind one interface. H: book, not re-read today. Fits "swap how a source is read".
  - Chain of Responsibility (GoF 1994): "lets you pass requests along a chain of handlers"; each handler processes or forwards, canonical form stops at the first that handles it. E: refactoring.guru/design-patterns/chain-of-responsibility, read 2026-11-10. Fits "ordered list, ask the next on decline", and matches `ShapeSource.describe_part` returning None.
  - Ports and Adapters / Hexagonal Architecture (Cockburn, 2005-09-04): keep logic independent of external interfaces so each can be swapped. E: alistair.cockburn.us/hexagonal-architecture, read 2026-11-10. Fits "core knows a source port, an MCP or a web fetch is an adapter".
  - Provenance, W3C PROV (PROV-DM, PROV-O, Recommendations 2013-04-30): entities, activities, agents behind a datum. E: w3.org/TR/prov-overview, read 2026-11-10 (the overview did not define the three terms; they come from PROV-DM, not read). Fits recording which source and which agent (script, Claude, person) produced a fact; spark's value/source/verified is a small subset.
  - Registry / Plugin (Fowler, Patterns of Enterprise Application Architecture, 2002, "Registry", "Plugin"): a well-known object other objects use to find services; configured, not hard-coded. H: book, not re-read. Fits a source registry that reads tools.json.
  - Resolver in package managers (ordered indexes, e.g. pip's `--index-url` and `--extra-index-url`; npm registry scopes): a configured ordered list, first match wins or all merged. H: general knowledge, no page read. Fits "where to look first". Whether pip merges or picks first differs by tool; not checked.
  - Model Context Protocol (tools with inputSchema and outputSchema, over stdio or HTTP): the way a source is exposed as interactive. H: patterns doc line 62 states the Operation schema mirrors MCP; spec itself not read today.
- REUSE-13 · The "interactive versus automatic" axis has an existing home: the Operation `effects` and `outside` (consent, gate) in the core contract, and `ConsentStrategy` for a person's yes. A human or AI source (a person writes a file) maps to P446's file source. · E · docs/guide/patterns-and-names.md:16,60-69 · supports: reuse consent for interactive sources
- REUSE-14 · Tokens/budget: current research costs 1-2 searches, 3-8 fetches per record (tech-lead.md:49 per brief C10); the agent's own cap is 8 searches and 12 fetches. A source order is also a cost order (free local first). · E · agents/parts-researcher.md; brief.md C10 · supports: order by cost then trust

## What you could not check, and why

- Official MCP servers of DigiKey, Mouser, Nexar: one search found only community servers; not proven that none exist. Their licences, free tiers and data fields were not read (search result summaries only).
- Whether `@jlcpcb/mcp` needs a key or account, and the licence of the part data it fetches: README is silent.
- DFRobot terms for wiki downloads: the wiki page fetch returned 404 (a guessed URL); only DFRobot's general terms page appeared in search, and it covers user content. See also PO-15.
- Seeed, Adafruit, SparkFun wikis and any MCP of theirs: not searched (search cap).
- Fritzing parts licence text and whether footprints are inside the SVGs: the repo page shows neither.
- Espressif docs MCP: the GitHub URL guessed was 404; terms and limits come only from the server's own instructions seen in this session.
- DigiKey API: free tier, price, and the datasheet field name were not found.
- PROV-DM term definitions, GoF and Fowler pages, pip and npm resolver semantics, MCP spec: not read today (H).
- SnapMagic and Ultra Librarian account needs and API/automation terms: only search summaries.
- Codebase: tool_finder.py read by grep only, not in full; no test of `tools.py --use` was run.

## Questions for the decider

- Is a source an entry in `tools.json` (new kind or `meets` contract per fact group) or a new registry file? · decides: whether the existing setting is extended or replaced (REUSE-2, REUSE-3)
- Is the order one global list, one per fact (picture, outline, holes, parameters), or per vendor via brief `prefer`? · decides: the shape of the order setting (REUSE-3, REUSE-4)
- May a non-MCP source (web fetch of a vendor wiki, a person's file) be a first-class source beside an MCP, behind one port? · decides: the port's interface (REUSE-6, REUSE-7)
- Do human and AI collaborators (P446's file source) count as sources in the same list, with an "unverified until the person says yes" mark? · decides: interactive versus automatic handling (REUSE-7, REUSE-13)
- Is a licence check per source a gate before a file is kept in the store? · decides: whether a source row carries a licence field (REUSE-11)
- Does DigiKey/Mouser/Nexar come in at all (a key is needed), given "free, few and local" in AGENTS.md? · decides: which later sources are named in the design

## Searches

1. `DigiKey MCP server official Mouser MCP server Nexar Octopart MCP parts API` · decision: do distributor or manufacturer MCP sources exist · used (REUSE-10, table)
2. `@jlcpcb/mcp npm JLCPCB MCP server library_install KiCad EasyEDA` · decision: what the JLCPCB source returns · used (table)
3. `SnapMagic SnapEDA MCP server Ultra Librarian MCP symbols footprints 3D models` · decision: CAD libraries as MCP sources, their licence · used (table, REUSE-11)
4. `DFRobot wiki license terms content reuse CC BY-NC OR "DFRobot" github KiCad library license` · decision: may spark keep DFRobot files · used (nothing found; see PO-15)
5. `KiCad library license CC-BY-SA 4.0 exception Fritzing parts repo license CC-BY-SA` · decision: licence for keeping CAD library files · used for KiCad, not for Fritzing
6. `DigiKey Product Information API v4 free API key client credentials OAuth parameters datasheet url` · decision: cost and key of a distributor API · used (partly; no price found)

Fetches (not searches): cdn.jsdelivr.net/npm/@jlcpcb/mcp@0.4.0/README.md, github.com/fritzing/fritzing-parts, w3.org/TR/prov-overview, alistair.cockburn.us/hexagonal-architecture, refactoring.guru chain-of-responsibility (all read); github.com/espressif/esp-docs-mcp-server and wiki.dfrobot.com SKU_DFR0995 page (404).
