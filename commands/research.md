---
description: Research a part or module the library lacks — vendor by vendor, in the project's preferred order — and write it down as a record with sources, so the chain can use it and the next project finds it.
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/parts.py *)
---

# spark:research

Find a part, from primary sources, and keep what was found. The unit is the part record every
other command reads — `parts/<id>.json` in the project — with every fact carrying its source and
saying whether it was read there. `verified: true` means the value is the vendor's own text
(datasheet, schematic, wiki table) at the cited URL; `verified: false` means it was read off an
image or a drawing, scaled, inferred or computed, and `why_it_matters` says what rests on it.
Three researchers in one evening asked which of two contradictory wordings to follow; this is it.

## 1. What exists already

```
${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --need <words> --project .
```

Words match a record's id, name, kind or alias. A match is the answer; the record is there to
use. No match prints the vendors it would research, in order.

## 2. The order

The project's brief says whom to prefer — `.spark/project.json` → `"prefer": ["dfrobot",
"seeed", ...]` — and the plugin's default is DFRobot, then Seeed: their wikis carry a pinout
table and a dimension drawing for every module. The researcher searches the first vendor, and
goes to the next only when the first has nothing fitting, unless asked to compare.

That order is for **modules**. A **simple part** — a connector, a terminal block, a discrete —
takes its facts from the maker's datasheet and its exact part number from a local seller's
listing: the brief's `sellers`, local first (for Czechia: LaskaKit, GME, Hadex, Botland, TME).
Every listing fetched goes into the record's `sourcing` list, so the next project knows where it
was bought.

## 3. Research it

Launch the `parts-researcher` agent with: the need in the user's words, the vendor order, the
project directory, and the record schema (`skills/spark-design/references/part-data.md`). It
writes `parts/<id>.json` from a skeleton:

```
${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --skeleton <id> --kind <kind> --vendor <vendor> --project .
```

Every null in the skeleton is a fact to record; the agent fills what its sources state and
leaves the rest null. **A pinout read off a wiki image is written as `verified: false`** with a
note saying so — it is never typed in from memory.

## 4. Check what came back

```
${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --validate --project .          # the contract
${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --sources <id> --project .      # every cited URL fetched
${CLAUDE_PLUGIN_ROOT}/scripts/parts.py --unverified <id> --project .   # what nobody has checked
```

The contract refuses a record with a null where a fact is needed. `--sources` fetches every URL
the record cites and names any that does not answer — a hallucinated source is the one lie
research tells easily. `--unverified` is the list to hand a person: each item, and what depends
on it.

Then `/spark:build`. The record is the project's; `parts.py --promote <id> --project .` copies it,
with its documents and photo, into the plugin's `parts/` once it is verified, and the next
project finds it with `--need`.

## Everything found is kept

Every candidate the researcher read — chosen or not — becomes a record in the plugin's `catalog/`
(drafts allowed; `parts.py --catalog` lists them), the chosen record names them as `alternatives`
with why not, and `parts.py --fetch <id>` downloads the datasheets and images each cites into your
own store (`~/.local/share/spark/sources`), pointed at from the record's `documents`. A later
`--need` shows a catalog match as such, and `--promote` brings it into a project to build with.

## What this does not do

It does not pick for you between two fitting parts — it shows both, with what each is missing.
It does not verify a pinout; no software can, from a picture. It does not track prices.
