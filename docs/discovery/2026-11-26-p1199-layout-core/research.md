# P1199 research: placement and routing with goals, the tools beside spark, and web editors

Step 2 of the PO's cycle for [P1199 #1747](https://github.com/xmejkal/spark/issues/1747). Reuse first, one or two
searches per question, every source read on 2026-11-26. Spark is public under MIT, so each find carries its licence.
This file names what exists. It decides nothing, and it is not legal advice.

> TL;DR. No tool does what spark needs as a library: a layout in mm for a breadboard and a perfboard, with a goal, that a
> Python core calls. Two small permissive projects come close and are worth a spike. perfwire (Apache 2.0) is a browser
> perfboard planner with a standard-library Python solver and an "easy, analog, compact" profile. stripboard-py (MIT)
> routes strips, jumpers and cuts. The big editors (Fritzing, VeroRoute, DIY Layout Creator) are
> GPLv3, so spark reads them for ideas and copies no code. The algorithms are textbook. A goal is a cost function.
> So "the smallest board" and "spread over the whole board" are two weights over one search, not two engines.

## Q1. Placement with a goal

| approach | what it does | the goal it fits | source |
| --- | --- | --- | --- |
| first fit (spark today) | the first free place, left to right | none | scripts/spark/breadboard/drawing.py:249 |
| rectangle packing | packs boxes into the least area, heuristics for the 2D bin problem | the smallest board, ignores the wires | rectpack, Apache 2.0 by its AUR entry (https://aur.archlinux.org/packages/python-rectpack, https://pypi.org/project/rectpack). The LICENSE file itself was not read. |
| simulated annealing over a cost | moves and swaps parts, keeps a worse move with a falling chance, scores each layout | both goals, by the weights of its cost terms | pyplacer, BSD 3-Clause (LICENSE read, https://github.com/ajokela/pyplacer). Its cost: half-perimeter wire length 1.0, hard overlap 1000.0, soft overlap 50.0, out of bounds 200.0, congestion 40.0, pad exit 5.0 (stated, its README). A set of scripts for KiCad 9 files, no library API, one commit. A blog post that it cites calls its results "not flattering". |
| force-directed | connected parts pull together, all bodies push apart | spread, and a fast first layout before annealing | the three classic kinds of iterative placement, "simulated annealing, simulated evolution and force directed placement" (US patent 5636125, https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5636125) |
| solver profiles | a named profile picks the solver's weights | "compact" is the smallest board | perfwire: `--profile easy|analog|compact` (README, https://github.com/KeckuJp/perfwire) |

What this means for spark (H, the layout-core session's reading): a goal is a cost function. "The smallest board" weighs
the board's used area and the wire length. "Spread over the whole board" fixes the board's size and rewards the room
between bodies. Both run over the same moves (a part to a free place, a turn, a swap) and the same ledger.
So one placement strategy with a goal setting fits the PO's rule, "one seam per strategy, chosen by a setting". The first fit
stays the default and the fast path. Annealing is random, so it needs a fixed seed to keep spark's rule that the same
input gives the same bytes (drawing.py:591-593).

## Q2. Routing

| approach | what it does | where spark is | source |
| --- | --- | --- | --- |
| maze routing (Lee) and A* on a grid | the cheapest way through free cells, with costs for a bend and a crossing | spark's `TrackRouting` is A* with costs for a cell, a cell off the board, a bend and a crossing | scripts/spark/breadboard/wire_routing.py:185-270 |
| rip-up and reroute | when a net fails, take out the nets in its way and route again | not in spark: a failed jumper falls back to more bends, then is not drawn | The order of the nets decides the result. Source: https://kastner.ucsd.edu/ryan/?p=109 and the PathFinder slides below. |
| negotiated congestion (PathFinder) | every net routes through shared cells, and a cell that two nets want costs more each round, until no cell is shared | not in spark | McMurchie and Ebeling, PathFinder, 1995: https://www.doi.org/10.1145/201310.201328. Slides: https://www.esa.informatik.tu-darmstadt.de/archive/twiki/pub/Lectures/AlgorithmenImChipEntwurfDe/router-pathfinder.pdf. Several global routers build on it (a search summary, not read). |
| a strip router | chooses which strips carry which net, where jumpers go and which tracks to cut | not in spark | stripboard-py `sb.autoroute()`, MIT (LICENSE read): https://github.com/Stocko-2073/stripboard-py. Python 3.12 or newer. Version 0.6.0 of 2026-10-15: https://pypi.org/project/stripboard/. Parts are placed by hand in code. `locked=False` lets its solver place a part. Its algorithm is in docs/router-spec.md, not read. |
| tscircuit's autorouter | a full PCB autorouter in TypeScript | spark already calls it inside `tsci build` for the PCB | @tscircuit/capacity-autorouter, MIT: https://cdn.jsdelivr.net/npm/@tscircuit/capacity-autorouter@0.0.606/README.md. The `autorouter` prop takes a routing function of one's own: https://docs.tscircuit.com/advanced/create-or-use-custom-autorouter. Its docs show no breadboard or perfboard element. |

The perfboard's three joins, from the PO's note on #311 (2026-11-26, one search of hobby guides, not standards):
a solder bridge between neighbouring pads, a bare tinned wire along the pads on the back, and an insulated jumper.
The jumper goes on the parts side where two routes cross. So on a perfboard the A* grid's crossing cost is the price of an insulated jumper,
and "keep jumpers few" is that cost set high. A run of several amps needs a thicker wire (same note). No current limit
per join kind was read from a source here, so any such number is H until a source is read.

## Q3. The tools beside spark

| tool | what it does for a breadboard or a perfboard | licence | reuse by spark (MIT, public) | source |
| --- | --- | --- | --- | --- |
| Fritzing | breadboard, schematic and PCB views, a PCB autorouter since 0.7.x | code GPLv3, parts and their pictures CC BY-SA 3.0 | ideas only. The official FAQ says "we do not allow the use of Fritzing part graphics in other software systems at the moment". | https://fritzing.org/faq, https://metadata.ftp-master.debian.org/changelogs/main/f/fritzing/experimental_copyright |
| VeroRoute | stripboard, perfboard and 1 or 2 layer PCB, "interactive auto-routing": the tracks follow a moved part. Prevents shorts and checks for open circuits. No smallest-board feature on its page. | GPLv3 | ideas only: a moved part keeps its routes, which is P1163's job | https://sourceforge.net/projects/veroroute/ (last update 2026-05-07) |
| DIY Layout Creator | draws PCB, perfboard, stripboard and point-to-point layouts by hand, no autorouter found | GPLv3, and "contact the project owner" for commercial use of the code | ideas only | https://github.com/bancika/diy-layout-creator/wiki, https://flathub.org/apps/details/com.diy_fever.DIYLayoutCreator |
| perfwire | a browser planner and checker for hand-soldered perfboard. Its solver places parts and wires them. Jumpers "land in free holes next to their target and get solder-bridged". A JSON state file "(v1)", a shareable `#z=` link, KiCad netlist import. | Apache 2.0 (LICENSE read) | code reuse is allowed with its notice. Maturity unknown: 171 commits, no release, no date found. Insulated jumpers are not described. | https://github.com/KeckuJp/perfwire, https://www.producthunt.com/products/perfwire |
| stripboard-py | a stripboard layout written in Python, rendered to PDF, autorouted | MIT | a Python dependency or a reference for a stripboard surface. Stripboard was dropped by the PO on 2026-10-16 (#310 closed), so it is a reference only. | https://github.com/Stocko-2073/stripboard-py |
| PerfDesign | a small application to sketch perfboard and stripboard projects | GPLv3 | ideas only | https://sourceforge.net/projects/perfdesign/ |
| pyplacer | a simulated-annealing placer for KiCad boards | BSD 3-Clause | a reference for a cost function, about one file of logic | https://github.com/ajokela/pyplacer |

A licence note, not legal advice: GPLv3 code copied into spark makes that part GPLv3, and spark is MIT. Reading GPLv3
code for its ideas copies nothing. Apache 2.0, MIT and BSD code can enter an MIT project with its licence notice kept.
The PO decides any reuse of code (AGENTS.md, "Spark is public, under MIT").

## Q4. Web editors for a breadboard and a perfboard

- The breadboard: P294's finding (docs/discovery/2026-10-18-p294-wokwi-reuse/finding.md, 2026-10-18) already answers
  it. Wokwi's editor is closed and its embed is an unsupported prototype. Its recommendation has three parts. Wrap `@wokwi/elements`
  (MIT, about 50 parts) for part pictures. Build a drag, drop and wire layer with Konva or SVG.js on `breadboard.json`.
  Keep `diagram.json` as the one data file. Not re-searched here.
- The perfboard: perfwire is the nearest open web editor (Apache 2.0, one `index.html`). Its model (a JSON state, a
  solver beside the page, a check after each edit) is the shape the PO's rule asks for: the page is thin, and the
  logic sits outside it. SVG-PCB (https://github.com/leomcelroy/svg-pcb) and aeCAD (https://github.com/ceremcem/aecad)
  are web editors for PCBs, not for perfboards.
- What no source shows: a web editor that a person and Claude edit through the same Operations. That part is spark's
  own (the PO's rule of 2026-11-26: every feature reachable from every interface).

## Searches

| query, verbatim | the decision it served | used |
| --- | --- | --- |
| VeroRoute stripboard perfboard layout editor license GPL autorouter | reuse VeroRoute | yes |
| DIY Layout Creator diylc license perfboard | reuse DIY Layout Creator | yes |
| Fritzing app source license GPL parts CC-BY-SA autorouter breadboard view | reuse Fritzing | yes |
| tscircuit autorouting library MIT perfboard breadboard support | reuse what spark already runs | yes |
| component placement algorithm minimize board area simulated annealing force-directed PCB placement open source python | placement with a goal | yes |
| grid maze router rip-up and reroute negotiated congestion PathFinder open source python library | routing past one pass | yes |
| online web perfboard layout editor browser open source stripboard planner | the perfboard web editor | yes |
| tscircuit breadboard perfboard component "<breadboard" OR "perfboard" docs | reuse tscircuit for a perfboard | yes, nothing found |
| rectpack python rectangle packing library license | the smallest board | yes |
| pypi stripboard python package layout | reuse a Python layout library | yes |
| github ajokela pyplacer license simulated annealing KiCad placer | reuse a placer | yes |

Four pages were read in full by a fetch agent on 2026-11-26: perfwire's repository and LICENSE, stripboard-py's
LICENSE and PyPI page, pyplacer's LICENSE and README, and VeroRoute's SourceForge page.
