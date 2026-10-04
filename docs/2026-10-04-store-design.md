# The store and its ways in — design (P94), living draft

**Status:** being designed with the PO, one question at a time (his request, 2026-10-04: *"keep asking me and
iterating until we have a well designed system … that we don't produce unnecessary bloat, but it also is a
good and useful tool"*). Each answer lands here as it is given; nothing is planned until the PO has reviewed
the whole. Process (his choice): story map + flows + example mapping; a spec and a plan for the first slice
only. Input: the P85 discovery (`docs/2026-10-04-store-discovery.md`) and a four-lens design council
(flows and stories, domain model, architecture, skeptic and trust), read-only and offline.

## 1. What it is for — decided

- **The database gets better and better**, meaning: **more parts known** (researched once, found from every
  project), **proven by use** (a part that built and ran says so), **fewer requests, measured** (a project
  shows what it cost and what came from reuse). Not "every part complete": a record grows when a stage needs
  a fact (W21).
- **Store first:** general requirements and options first; then what the store already has that works
  similarly; research only for the gap.
- **Ways in**, all on one store: goal first, module first, a combination, the whole drawer, revive, swap,
  extend (P76).
- **No bloat, but useful** — every piece names the journey step it serves, or it is cut.
- **Later, kept in mind:** a viewer and manager (P86); a shared part database (P84, no selectable backends).

## 2. The journeys — the story map's backbone (draft, from the flows lens)

Every way in runs on one spine: **D** note what I own → **M** match a need against the store → **C** choose →
**G** research the gap (only when nothing similar) → **L** the part list the chain accepts → **T** tally what it
cost and record proof by use. Some ways add a step: **I** ideas from what I have (module first, combination,
whole drawer), **F** does it fit (combination, swap, extend), **R** reverse-engineer what stays (revive). I and
S (shaping the idea) are conversation: spark gives facts, the conversation writes ideas (as P56 does for
firmware).

| Way in | First sentence | Flow |
| --- | --- | --- |
| Goal first | "something that tells me my plant is thirsty" | S → M → C → G (gaps) → L → T |
| Module first | "I have this DS3231 — ideas?" | D → I → S → M → C → G? → L → T |
| Combination | "these 3 — ideas?" | D ×3 → F → I → S → M/C → L → T |
| Whole drawer | "what can I build with what I have?" | D → I (ranked by how much is owned) → S → M → G (minimal) → L → T |
| Revive | "my bin's board died" | R → D (salvaged parts) → S → M → C → G → L → T |
| Swap | "replace the DFR0641 in irrigation" | the part's role → M (same role) → C + F → G? → L → T |
| Extend | "add a buzzer to the quickstart" | the project's free pins → S → M → C + F → G? → L → T |

## 3. The drawer — decided so far

- **Owning is not researching.** A drawer entry is light — what it is, how many — and a part's facts are read
  only when a design considers it.
- **Four ways in, one entry** (the PO, 2026-10-04): **order history** (DFRobot account, AliExpress orders,
  confirmation emails — exported or pasted), **photos of the drawer** (read by `/spark:identify`), **a typed or
  dictated list**, and **adding as I go** (a part joins when a project or idea mentions it). Every route makes
  the same entry; none of them researches.

## 4. The first slice — decided

**The walking skeleton is goal first, with the PO's real drawer** (the PO, 2026-10-04): he notes about ten
things he owns (no research, no web) → gives a real goal → the conversation names the functions it needs, no
part numbers → each function is marked **have** (in the drawer), **know** (researched before, with what it
still lacks) or **gap** (nothing similar) → only the gaps go to research, each after his yes → a part list
the chain accepts → the step prints what it cost (requests made; parts reused out of parts chosen). It
touches every spine step thinly; module first follows and reuses the same pieces.

## 5. The data — from the domain lens (to be decided piece by piece)

- **Drawer item** — *decided (the PO, 2026-10-04):* one small file per item in the store; only `label` and
  `count` required; optional: what it `is` (a record or board id, a maker part number), **where it physically
  is** ("box 3, blue tray"), **which projects use how many** (a project reserves what it uses), **where it came
  from** (seller, listing or order code — to buy it again, and the only identity an unlabelled part has),
  `photos` (by checksum), and its `function`. Never price, date, or a condition field.
- **History** — one append-only log in the store: `built`, `simulated`, `ran` (proof by use, tied to the
  record's checksum so a proof of an old pin order does not vouch for a corrected one), `researched` (with its
  request counts), `reused`, `passed_over` (with why). It gives the three measures from data, and keeps
  personal events out of shared records.
- **Records keep up with the contract** — every rule says the contract version it arrived in; a record is
  **current**, **owed** (fails only newer rules: listed as "to fill", grown when a stage pulls it) or **broken**
  (refused). Mechanical upgrades happen on read, saved on the next write — no big-bang migration. One
  `--validate` walks every layer.
- **Matching a similarly working thing** — *decided (the PO, 2026-10-04): both from the start.* Every record
  and drawer entry carries `function: [{does, what}]` — `does` from a closed list of about ten verbs (sense,
  drive, power, keep-time, store, indicate, sound, input, connect, compute), `what` in open words (distance,
  soil-moisture …), derived from today's `kind` where it can be, from the person's words for a drawer item —
  and the agent also reads the whole index to judge what is similar and say what would change.
- **Identity** — a natural key, maker/part-number[@revision]; a generic part by its printed board name.
- **Layers** — resolving an id: project → shelf → library → catalog → (shared later); the nearer layer wins the
  whole record, and a draft never hides a verified one. Proposing parts, store first: drawer → project →
  shelf → library → catalog → research.
- **Never leaves the machine:** the drawer, the history, document bytes, photos, project choices.

## 6. Architecture — decided: Option B, refactor first, then raise the budget

*The PO, 2026-10-04.* `store.py` owns where things are and how bytes move — one home (`SPARK_HOME`, else
`XDG_DATA_HOME/spark`, else `~/.local/share/spark`), one table of layers nearest-first, every write contained
and checked, the one checked keep/fetch. `parts.py` owns what a record must be, and the commands; every
command answers in JSON, which is the stable interface for agents and a later viewer. A new layer (shelf,
drawer, a shared clone) is a row in the table. **Budget:** refactor and delete first (W15b — one JSON printer
for every command, one search over every layer), then raise the 5,000-line cap by what the design needs,
measured per item.

The options weighed:

From the architecture lens (details in the council's report, to be folded in when chosen):
- **A** — one home and one layer table inside `parts.py`; cheapest, but `parts.py` passes 1,000 lines with
  five concerns.
- **B** *(the lens's recommendation)* — `store.py` owns *where things are and how bytes move* (one home, one
  table of layers nearest-first, contained writes, the checked keep/fetch, the one network door); `parts.py`
  owns *what a record must be* and the commands; every command answers in JSON, which is the stable
  interface a viewer and agents use. About +90–110 of the 292 code lines left, built thin.
- **C** — also a separate `contract.py` and a generic get/put CLI; the most churn, no story needs it yet.

## 6a. Strategies at every real variation point — decided

*The PO, 2026-10-04: "let's use strategy patterns etc so that we can later change the systems we use … a good
architected system, so that we can go agile and improve."* Seven seams are strategy interfaces — each with a
short interface, **one implementation now**, others added when pulled; **selected by name through the same
layered list as the tools** (P82: spark's defaults → the person's file → the project's, the project winning);
and **one contract test per interface that every implementation must pass**.

| seam | first implementation | later, when pulled |
| --- | --- | --- |
| record store | folders of JSON (today's layout) | a shared git clone (P84), a database |
| document store | checksum folders | a private bucket |
| drawer importer | a typed or dictated list | DFRobot order history, AliExpress orders, photos |
| matcher | the function field + the agent's judgement | embeddings, a shared index |
| researcher | part-finder + datasheet-reader | the JLCPCB MCP alone, manual entry |
| cost counter | from the session transcripts | spark counting its own calls |
| fetcher | one checked download | a proxy or cache, offline mode |

This supersedes the discovery's "no record/document classes now" for these seams; the P84 decision stands —
no database, NoSQL or Markdown store is *built* until one is pulled.

## 6b. Designed for AI agents first — decided

*The PO, 2026-10-04: "spark is to be used by claude code or other ai, not only human, let's make sure it's well
designed for that too."* spark's usual user is an agent acting on a command's output without reading its
source. So:
1. **One stable JSON envelope from every command** — outcome (ok / problems / could not run), data, problems as
   whole sentences with their fix, and the **next commands to run**; the exit code says the outcome (a miss is a
   miss, not success).
2. **Self-describing** — one command lists every operation, its arguments and its output shape.
3. **Small by default** — summaries first, details on request.
4. **Safe writes** — `--dry-run` on every write; network and deletion need the person's yes; writes are idempotent.
5. **Record and web text is data, never instructions** — in every agent's instructions (P87).
6. **Offline by default** — the network only through the fetcher strategy, asked for explicitly, and counted.

**The interface is a strategy too** — the operations are designed once; the first slice exposes them as CLI +
JSON; an **MCP server** is a thin second front end over the same operations, pulled when another AI client
needs it (decided).

## 6c. Cost and proof — decided

*The PO, 2026-10-04, as written except the stop rule, which he struck.*
- **One history log in the store** (`history.jsonl`, append-only, never shared): `built`, `simulated`, `ran`
  (proof by use, tied to the record's checksum), `researched`, `reused`, `passed_over` (with why). Counts only —
  no URLs, queries or paths.
- **The cost counter** (first strategy: the session transcripts) counts network requests (web searches and
  fetches, network MCP calls, `curl` inside shell commands — today's tool misses the last), research runs,
  documents read, new tokens (cache reads apart), minutes. After each step spark prints **a cost line**: "3
  parts: 2 reused, 1 researched — 4 requests, 2 documents, 9 min".
- **The measures:** requests per chosen part (the headline, falling project to project), reuse share (rising),
  re-research of a part already known (zero).
- **Proof sources:** `built` from `check_spine` on a pass, `simulated` from a passing simulation, `ran` from a
  bench step or the person's confirmation.

## 6d. The layer order — decided (corrects P91)

- **Resolving an id:** project → shelf → **library → catalog** → shared. The nearer layer wins the whole record;
  a draft never hides a checked part.
- **Proposing parts, store first:** drawer → project → shelf → library → catalog → shared → research only for
  the gap.

## 6e. The first importer — decided

The **typed or dictated list** ("2x DFR0954, a bag of 6x6 buttons, the blue L9110S in box 3"): the agent
turns it into entries and asks only what is ambiguous. DFRobot order history, AliExpress orders and photos
follow as importers behind the same interface.

## 7. Slice 1 — the walking skeleton's stories (agreed with the PO, 2026-10-04)

Goal first, with the PO's real drawer. One story per spine step, the thinnest that works end to end:

| step | story | check |
| --- | --- | --- |
| D | As the maker, I tell spark what I own in plain words; it makes light drawer entries and asks only what is unclear | `--drawer --json` lists them, "owned, not researched" |
| S | As the hobbyist, I say a goal; the conversation turns it into needs — each a `does`/`what`, no part numbers | a needs file lists the functions |
| M | As the agent, for each need I get what the store has, store first, marked have / know / gap, and what each candidate still lacks | `--match <needs> --json` marks every need |
| C | As the hobbyist, I see each need's candidates (layer, owned count, proof, what is owed) and pick | the picks are recorded, a passed-over part with why |
| G | As the PO, research runs only for the gaps, after my yes, and records what it cost | a `researched` history line with counts |
| L | My picks become a requirements file the chain accepts; owned parts are reserved for the project | `check_spine` `[ok]`; the drawer shows "2 in this project" |
| T | The step ends with the cost line; the history records `built` and `reused` | "5 parts: 4 reused, 1 researched — 3 requests, 1 document, 12 min" |

**Foundations (enablers):** `store.py` (one home, the layer table, contained writes, the record and document
store strategies — covers P88); the JSON envelope on the slice's commands; owed records (P89); the function
field derived from `kind`; P87 (records inert).

**Later slices:** the order-history importers next — DFRobot and AliExpress (the PO: *"that will help a lot to
fill what we have"*) — then photos; the other six ways in; the shelf beyond reserving; the viewer; MCP;
`simulated` and `ran` proof; the shared database.

## 8. Example maps

### D — the drawer, from words (agreed 2026-10-04)

**Rules**
1. An entry needs only a label and a count; everything else is optional.
2. Owning never triggers research or a web request.
3. Words that name a part spark knows (a library record, a board, a maker part number) link the entry to it.
4. Something unclear is asked once, and only that.
5. The same item said twice adds to its count, never a duplicate.
6. The drawer lives in the store, never in a repository.
7. A part whose only record sits in another project is linked to it, and that record goes onto the shelf so
   every project finds it — never researched again (proposed by Claude; the PO may veto).
8. **A part said to be dead stays, in the person's words**; ideas and matching skip it unless asked (the PO).
9. **A part the person is unsure of is added marked `unsure`**; matching shows it as "maybe owned — check the
   drawer"; an import or a look confirms it (the PO).
10. **"Many" is a valid count** for plentiful cheap parts; a number only where it matters (the PO).

**Examples — the PO's real drawer** (each becomes a test of the typed-list importer)

| said | entry |
| --- | --- |
| "the FireBeetle 2 ESP32-S3" | ×1 → board `firebeetle2-esp32s3`, revision unknown |
| "a Seeed XIAO ESP32-C6" | ×1 → board `xiao-esp32-c6` |
| "the blue L9110S motor driver" | "blue L9110S" ×1 → library `l9110s-module` |
| "an L298N board, HW-095" | ×1, part number HW-095, drive / motor-dc, not researched |
| "an A4988 stepper driver HW-134 — I think it's dead" | ×1, part number HW-134, drive / motor-stepper, words "I think it's dead" — skipped by ideas |
| "a DS3231 clock module from AliExpress, the one with the AT24C32" | ×1 → irrigation's `ds3231-at24c32-rtc-module`, onto the shelf (rule 7) |
| "a CJMCU-111" | ×1, part number CJMCU-111; asks once what it does |
| "an IP2312 charger board" | ×1, power / lipo-charging |
| "a DFRobot speaker" | ×1, sound / speaker, part number unknown |
| "a 1S LiPo battery" | ×1, power / battery |
| "a bag of 6×6 tactile buttons" | "many" → library `tactile-button` |
| "the MP3 mini module, I think" | ×1, sound / mp3-player, `unsure` |
| "the I2S amplifier, I think" | ×1, sound / amplifier (DFR0954?), `unsure` |

**Questions left:** none for D. The DFRobot order history (P93's next importer) will settle the two `unsure`
audio entries — and with them the bin's B1.

### S — a goal becomes needs (agreed 2026-10-04)

**Rules**
1. A need is a function — `does` / `what` — with a condition only when it decides a part.
2. No part numbers yet.
3. At most about three questions, each able to change a need.
4. The board is a need like any other.
5. The output is a short needs file in the project.

**Example — the walking skeleton's goal, run for real with the PO:** "Tell me when my plant is thirsty." The
three questions and his answers: *how should it tell you?* — a sound; *how is it powered?* — battery; *where
does the plant live?* — indoors, a pot. The needs:

| need | does / what | condition |
| --- | --- | --- |
| 1 | sense / soil-moisture | indoor pot, short probe; low power (battery) |
| 2 | sound / alarm | a beep is enough |
| 3 | compute / microcontroller | deep sleep between readings (battery) |
| 4 | power / battery | rechargeable |

### M — match each need against the store (agreed 2026-10-04)

**Rules**
1. Store first, in the proposing order (drawer → project → shelf → library → catalog → shared); research only
   for a gap.
2. Each need is marked **have** (owned), **know** (researched, not owned — buy, don't research) or **gap**
   (nothing similar).
3. A candidate shows what it still owes (P89's owed facts), its proof, and how many are owned.
4. A part passed over elsewhere is offered with that project's reason — the reason belongs to that context.
5. A `unsure` owned part shows as "maybe owned — check the drawer".
6. **Owned first, the simpler option shown** (the PO): when an owned route needs more parts and a simpler part
   is not owned, spark proposes the owned route and shows the simpler one beside it, with what it would cost.

**Example — the real store, 2026-10-04**

| need | mark | from the store |
| --- | --- | --- |
| sense / soil-moisture | know | the catalog's SEN0193 (capacitive) — irrigation passed it over for an outdoor bed, which does not apply; owes a few facts; irrigation's waterproof SEN0308 is the alternative. Neither owned: buy, don't research |
| sound / alarm | have, with a catch | the DFRobot speaker needs a driver: the I2S amplifier or the MP3 module, both `unsure`; a piezo buzzer, simpler, is a gap |
| compute | have | the FireBeetle 2 S3 — deep sleep, and its LiPo socket and charger fit the battery need (the XIAO ESP32-C6 is the other) |
| power / battery | have | the 1S LiPo; the FireBeetle's charger covers charging |

## 9. Next

Example-map C, G, L and T, then the spec and the plan for slice 1.
