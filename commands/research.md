---
description: Research a part or module the library lacks — reuse first, then find the exact part, then read only the datasheet pages a decision needs — and write it down as a record with every fact cited, so the chain can use it and the next project finds it.
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/parts.py *), Bash(${CLAUDE_PLUGIN_ROOT}/scripts/tools.py *)
---

# spark:research

Find a part from primary sources and keep only what a decision rests on (W21): a datum is kept when
code, a check, or a person deciding reads it, and when it stays true without upkeep — a part number,
a printed datasheet version, a page. The unit is the part record every other command reads —
`parts/<id>.json` in the project. `verified: true` means the value is the maker's own text at a cited
page; `verified: false` means it was read off an image, a drawing or a distributor, and
`why_it_matters` says what rests on it.

## 1. Reuse first — no network

```
${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --need <words> --project .
${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --kept <part number or words> --project .
```

`--need` searches the project's parts, the library and the catalog; a match is the answer.
`--kept` searches the person's store — including a datasheet another project kept, or an
interrupted run left — and a kept document is never fetched again. A file you already have goes in
with `parts.py --keep <file> --url <url>`.

**Ask before researching: does the person already have one?** — in the thing being rebuilt, in
the drawer, in the kit. The first run of the finder looked for a 4×AA holder the bin's own lid
already had (2026-10-03). Add what they have to the brief's `parts_on_hand`.

## 2. Which kind of part — and who researches it

**A commodity part** — an LED, a diode, a button, a connector, a regulator: one datasheet describes it
completely. Two small agents, in turn:

1. Launch **`part-finder`** with the need in the person's words, the build stage (a breadboard first
   means through-hole), what they own and any limits. It returns at most two candidates — maker,
   exact part number, the maker's datasheet URL — and writes nothing. **The person picks.**
2. Write the skeleton and keep the datasheet:
   ```
   ${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --skeleton <id> --kind <kind> --vendor <maker> --project .
   ${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --fetch <id> --project .        # or --keep <file> --url <url>
   ```
3. Launch **`datasheet-reader`** with the record's path, the kept datasheet and the facts for its
   kind (below). It reads with `parts.py --read`, page by page, stopping where the facts are.
   A line `… is not installed — install: …` is answered by asking the person once and running `${CLAUDE_PLUGIN_ROOT}/scripts/tools.py --install <name> --project .`, then launching the reader again (`/spark:setup` does the same for everything at once).

**A module, or a part identified from a photo** (`/spark:identify`) — variants, a chip inside, a
schematic to read: launch **`parts-researcher`** with the need, the vendor order (the brief's `prefer`,
default DFRobot then Seeed), the project directory, the plugin directory (`${CLAUDE_PLUGIN_ROOT}`) and
the record schema (`skills/spark-design/references/part-data.md`).

## 3. The facts each kind needs — and nothing else

| kind | facts a decision reads |
| --- | --- |
| indicator LED | `forward_voltage_v` (typical, with its test current), `forward_voltage_max_v`, `max_continuous_current_ma`; the pin order and which lead is which, from the drawing; lead pitch; body |
| button | which legs are one terminal; cap height (the enclosure) |
| connector | pitch, positions, current per contact, whether it is keyed; the pin order with its proof |
| regulator | input range, output voltage and current, quiescent current, enable threshold; the pin order with its proof |
| module | supply range; input high and low thresholds; current asleep, active and at peak; on-board pulls (ohms, rail); bus and address; the pin order with its proof |

Every warning a person must see — polarity, a reversal, a missing pad-1 mark — goes into
`host_requirements`, which spark prints. **Not gathered:** prices, stock and seller listings (they go
stale before anyone reads them; buying is a later step), facts nobody listed, and the datasheet of a
chip inside a module unless a listed fact needs it.

## 4. Check what came back

```
${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --validate --project .          # the contract
${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --sources <id> --project .      # every cited URL answers
${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --unverified <id> --project .   # what nobody has checked
```

The contract refuses a pin order without its proof and a citation of a document the record does not
hold. `--unverified` is the list to hand a person: each item, and what depends on it.

Then `/spark:build`. `parts.py --promote <id> --project .` copies a verified record into the plugin's
library, and the next project finds it with `--need`.

## Candidates not chosen

A candidate whose datasheet was kept gets a catalog record of its identity, that document and why it
was not chosen — no typed facts. One seen only in a search is a line in the chosen record's
`alternatives`. (W21; P83 moves the catalog out of the plugin into the person's store.)

## What this does not do

It does not pick for you between two fitting parts — it shows both, with what each is missing. It
does not verify a pinout; no software can, from a picture. It does not track prices.
