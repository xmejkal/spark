# Story map

**Status:** proposed, not applied <!-- REQUIRED:map-status -->

## Backbone
Find what I own → Gather sources → Read facts → Write the record → Check the record → Show the part <!-- REQUIRED:backbone -->

## Slices
The design council (D2) refines these. Slice 0 is the thinnest run that ends in something the PO can read.

| slice | activity | story | job | tag | proof |
| --- | --- | --- | --- | --- | --- |
| 0 walking skeleton <!-- REQUIRED:slices --> | all six | one owned module (SEN0526) runs through the new pipeline with the DFRobot site strategy. Its record holds the picture, outline, holes and header row, each sourced or "not published" | Job 4, Job 3 | D2, E ★C1 | `parts.py --show sen0526-i2s-mic` and one reader that prints the new fields |
| 1 | Find what I own | `--need` matches the drawer's function and boards | Job 1 | E ★C4 | `--need "load switch"` names DFR0457 |
| 1 | Write the record | the hand steps go: `--skeleton` drops `sourcing`, warns about a shelf record, `--fact-set` takes `legs` and `host_requirements` | Job 4 | E ★C6 | the walk of DFR0457 again with no hand edit |
| 2 | Gather sources | a second strategy (a text description or a photo from the person) fills the same record shape | Job 4 | D2 | one part filled by two strategies, the same keys |
| 2 | Gather sources | zips are kept and read (STEP, layout, schematic) | Job 3 | E ★C7 | the DFR1117 layout zip kept, its footprint read |
| 3 | all six | a dev board runs through the same pipeline | Job 4 | E ★C5 | DFR1117 record made by the pipeline, `--unverified` lists its open facts |
| 4 | Show the part | the breadboard sheet and the board page read the record's geometry (P734, P446) | Job 2, Job 3 | E ★C3 | the sheet draws DFR0995 with its real header |
| 5 | all six | the batch over the owned PCB modules in scope (Q3) | Job 1 to 3 | E ★C9, ★C10 | the drawer shows a record for each module in scope |

## Delta to the product's map <!-- REQUIRED:spark-process:map-delta -->
Proposed for `scrum/STORY_MAP.md`, not applied. Row 2 "Know what you own": the gap gains "an owned module is found by what it does, and its record holds its picture, outline, holes and connectors (P735)". Row 10 "Breadboard": the gap gains "a module drawn from its record's geometry (P734, P735)".
<!-- EXTEND:map -->
