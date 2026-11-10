# Story map

**Status:** proposed, not applied <!-- REQUIRED:map-status -->

The to-be map for the research pipeline (D2, D5, D6). It joins the UX lens's backbone (council/arch-ux.md:112) with the architect's walking skeleton (council/arch-architect.md:275). The design council refines it.

## Backbone
Decide the sources → Find what I own → Gather from sources → Read facts → Write the record → Ask what only I can answer → Show the part and hand over <!-- REQUIRED:backbone -->

"Decide the sources" and "Ask what only I can answer" are new against the as-is journey.

## Slices
Slice 0 is the thinnest run that ends in something the PO can read. Each later slice adds one thing to it.

| slice | activity | story | job | tag | proof |
| --- | --- | --- | --- | --- | --- |
| 0 walking skeleton <!-- REQUIRED:slices --> | all seven | one owned module (SEN0526) runs through one research Operation with two source kinds, the DFRobot site and the kept documents (Claude reads the dimension drawing as a next step). The run prints the resolved source order. Geometry has a typed home (the board record's `physical` keys). Each fact names its source kind or says "not published", conflicts are a list, and the run ends with one open list | Job 4, Job 3 | D2, E ★C1 | the printed order, then `parts.py --show sen0526-i2s-mic` with the outline, holes and header row, then the open list |
| 1 | Decide the sources | the person sets the source order in `/spark:setup` words, per person and per project, and a run can override it once | Job 4 | D5 | `/spark:setup` prints the sources block, and a change changes the printed order |
| 2 | Gather from sources | the person is a source (a photo, a revision, a measurement), and a zip is kept and read (a footprint file) | Job 4 | D2, E ★C7 | the DFR1117 record filled from its footprint and the PO's photo of the back |
| 3 | Show the part and hand over | a reader shows the geometry: the board page prints the outline, holes and connectors, and the sheet draws SEN0526 with its real header (P734, P446) | Job 2, Job 3 | E ★C3, D7 | the sheet draws SEN0526 from its record |
| 4 | Gather from sources | an MCP source sits behind the same slot. A paid or keyed source asks before use | Job 4 | D5 | a run line "mcp used, free" or "mcp asked, declined" |
| 5 | Show the part and hand over | the run links the drawer entry by SKU and prints a cost line. `/spark:idea` finds the part by what it does (needs Q5) | Job 1 | E ★C4 | `--need "load switch"` names DFR0457 after a run |
| 6 | all seven | the same run through `--json` with one typed open list, driven by Claude and by a LangGraph node (P417). Records are read back through a RAG index later (P419) | Job 5 | D6 | the LangGraph node runs slice 0's part and stops on the open list |
| 7 | all seven | the batch over the owned PCB modules in scope (Q3): a plan screen, five end states, one question message, resume | Job 1 to 3 | E ★C9, ★C10 | a page with one state per part in scope |

## Delta to the product's map <!-- REQUIRED:spark-process:map-delta -->
Proposed for `scrum/STORY_MAP.md`, not applied. Row 2 "Know what you own": the gap gains "a finished record links to the drawer entry by SKU". Row 3 "Choose parts": the gap gains "a part you own is found by what it does. Research for a gap runs a source order you set, and every fact names its source (P735)". Row 10 "Breadboard": the gap gains "a module drawn from its record's geometry (P734, P735)". Only if a step's status changes, the README's "What works today" and `tools/journey.py` change.
<!-- EXTEND:map -->
