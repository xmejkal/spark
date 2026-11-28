# P1352 council: the tech lead, with the Physics lens

Opus, 2026-11-28, read between about 10:50 and 11:15 CET at f975a3ab (branch of the worktree spark-wt-perfboard).
wire_routing.py there is the same as origin/main (its last change is 0998bf4f on both). P1350 #1937 will change it
soon, so every line number in wire_routing.py below is before P1350. Scratch runs patched code in memory, in a
temporary folder that was removed. The tree was not changed. P1199's TL-1 to TL-17 and EP-1 to EP-6 stand and are
not redone here.

## Findings

### Perfboard practice (question 1)

- TL2-1 · The three joins hold, and the source names a fourth. "Bare connections (bent leads, solder bridges and bare
  wire) lie flat on the copper side. They're quick and tidy, but they can't cross anything. Insulated wire can cross
  whatever it likes. Jumpers usually go on the component side, through a hole at each end like a part." The fourth is
  the bent lead: "A part's own lead, folded flat to the next pad". · E https://perfboarddesigner.com/learn/perfboard-wiring/
  (updated 2026-11-09, read 2026-11-28 about 11:05 CET, sha256 of the HTML 93a21d81eacf77cd...) · supports only:
  one maker's beginner guide, which cites Wikipedia, DigiKey, Instructables and Adafruit. It is a hobby source, not
  a standard. The DigiKey page of #311 returned a Cloudflare challenge and was not read.
- TL2-2 · A solder bridge is for neighbouring pads only. "For anything longer than two or three holes, lay a bare wire
  or a lead offcut along the pads and solder over it. A long trail of pure solder is brittle, carries current poorly".
  So the router uses a bridge only between two pads one pitch apart. · E same page · supports only: the rule of one
  pitch. The guide's limit is "two or three holes", and one pitch is the stricter D proposal.
- TL2-3 · A bare wire joins every pad it lies on. "The lead touches every pad it passes over. Keep those holes empty,
  or let them join the connection only if they belong to it." The guide's own editor says it too: "Solder paths ...
  join every hole they run over." So a back route is a set of pads, not two ends. · E same page.
- TL2-4 · Bare wires never cross, and the guide asks for a free hole between nets. "Bare wire can't cross anything.
  Plan the bus routes so they don't need to, and leave a free row between parallel buses." And: "Leave a free hole
  between different connections." "Run wires along the grid, horizontally and vertically, never diagonally across
  pads." So the four MOVES of wire_routing.py:41 fit the back. A crossing on the back is never a cost. It is refused,
  and the only crossing is an insulated jumper. · E same page, and wire_routing.py:41.
- TL2-5 · The order of the copper side is "rails first, then short links, then the rest". So the perfboard routes power
  and ground first, by the role the steps already carry (`Jumper.role`, drawing.py:38). The breadboard routes
  shortest span first (wire_routing.py:218). · E the guide, and the code · supports only: a build order from one
  guide. That it also gives fewer jumpers is H, for spike P1239 to measure.
- TL2-6 · Wire sizes from the guide: "22 to 24 AWG solid wire suits most connections and power rails", "20 AWG +"
  for "Power runs carrying amps: motors, relays, LED strips", and 30 AWG wire-wrap "should stay under about half an
  amp". Jumpers are solid core, stripped 3 to 4 mm. · E same page (stated, a hobby source).
- TL2-7 · A dev board on a perfboard: the one forum answer the search showed says "get some female-header-pins and
  solder those onto the perfboard ... so the devboard fits onto it neatly". · H a search snippet of
  https://forum.arduino.cc/t/how-on-earth-do-i-solder-all-these-on-a-board/1388222, the page not opened. My view (D,
  the tech lead): female headers by default. The board stays removable and reusable. No heat reaches the module. The
  board's own bottom copper stays off the perfboard's top pads. That matters because the PO's FIT0193 is "Double
  Sided" (E ~/.local/share/spark/drawer/dfrobot-fit0193.json, its label), so the parts side has pads too (H: the usual
  meaning of a double-sided protoboard). The cost is height. A typical female header is 8.5 mm tall (H, not read).
- TL2-8 · The antenna end. Espressif: "It is suggested to place the module's on-board PCB antenna outside the base
  board, and the feed point of the antenna close to the edge of the base board." And: "If the antenna cannot extend
  beyond the board edge ... cut off the base board on both sides of the antenna and below it". And "the module should
  not be placed in the center of the board". · E https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html
  ("latest", read 2026-11-28 about 11:00 CET, sha256 of the HTML 4ee3bb30a179b340...) · supports only: a module on a
  base PCB with copper. A dev board on headers over a perfboard is a weaker case of the same advice (H). For the
  perfboard: the dev board's antenna end goes at the board's edge or past it, and the cut line must not leave the
  antenna over pads. No board record says which end the antenna is at (E: no "antenna" in
  boards/xiao-esp32-c6.json or boards/firebeetle2-esp32s3.json, a grep). So this rule needs one record fact with its
  origin first (records grow by need).
- TL2-9 · A resistor's lead span. Today it comes from Wokwi's picture: on a perfboard lattice the trial below put
  wokwi-resistor at 1.1 and 7.1, 6 pitches (E measured). That is a drawing convention (EP-5). For a 1/4 W resistor
  laid flat, 4 pitches (10.16 mm, the common DIN0207 span) is usual, and 3 pitches with tight bends (H, model
  knowledge, not read). No record holds a lead span (E: a grep for "lead_span", "DIN0207" and "P10.16" in parts,
  boards, data and scripts finds none). A decision, D-q4.
- TL2-10 · Not read, so H (model knowledge): solder the lowest parts first (resistors, then sockets and headers, then
  buttons and LEDs, then the tallest), so each part sits flat with the board upside down. A cut runs along a row of
  holes, scored and snapped, so that row is lost, and a cut board of n holes needs n + 1 rows of the big one. A
  mounting hole for an M3 screw needs about 3 mm of clear board round it, so a corner hole costs about a 2 by 2 block
  of pads. Cheapest rung: the PO scores and snaps one offcut of the FIT0193 when P1238 #1791 runs, and counts what is
  left.

### Reuse (question 2)

Trial (E measured): a 40 by 30 single-pad surface in memory (each hole its own group, pitch 9.6 px), first-fit as it
is, each part alone on an empty ledger.

| part | as it is | with the P412 rule off |
| --- | --- | --- |
| wokwi-led | placed, 1.1 and 2.1, 0.00 s | placed |
| wokwi-resistor | refused, no_hole_left, after 1.38 s | placed, 1.1 and 7.1 |
| wokwi-pushbutton | placed, 0.00 s | placed |
| board-xiao-esp32-c6 | refused, no_hole_left, after 4.21 s | placed, 1.1, 1.2, 1.3 ... |

`spacing.tall_module_row` had to be switched off first: it raised IndexError on a surface with no letters
(spacing.py:102).

- TL2-11 · `FirstFitPartPlacement` refuses every part that covers holes on a perfboard. The P412 rule asks each pin's
  group to keep a free hole for a jumper (drawing.py:290 and :313-317). A group of one hole has none. So the resistor
  and the XIAO never fit, and the refusal comes only after a full scan. The rule belongs to a surface whose groups hold
  more than one hole. · E measured (the table) and code read.
- TL2-12 · Other breadboard-only assumptions in the pieces named:
  - `Surface.__init__` builds columns by letters and rails (drawing.py:113-138). A perfboard needs its own maker.
  - `tall_module_row` reads the gap between row letters (spacing.py:91-103).
  - `TrackGrid.__init__` takes y0 from `min(surface.letters_y.values())` (wire_routing.py:120). On a surface with no
    letters this raises ValueError (E code read).
  - The body-on-the-board check runs only when `body_gap_columns` is set (drawing.py:282). On a perfboard nothing keeps
    a body inside the cut, which also decides the antenna end (TL2-8).
  - The planner's jumper stage takes a free hole in the pin's group and a free group for a supply
    (`claim_free_hole`, `claim_free_group`, drawing.py:209-226, used at :358-367), seats rails (:393-406) and pins a
    resistor's leg in the group of the pin it joins (:420-445). On single pads the pin's hole is taken, so each of these
    fails. A perfboard leg goes in the pad beside the pin, joined by a bridge. So `BreadboardPlanner.plan` is
    breadboard-only as a whole. `steps.anchored()`, `Catalog`, `DrawnPart` and `HoleLedger.claim` and `is_free` are
    shared as they are.
  - `ends_toward_their_runs` (spacing.py:105-122) is breadboard-only.
- TL2-13 · The same-pins check needs one seam, and it is S. `DrawnNets` joins only the two groups of each jumper
  (drawing_match.py:44-45) and the `joined_pins` inside a part (:46-51). The rest, union-find and `differences`
  (:53-93), is shared as it is. The seam: the layout gives its joins as sets of groups. A breadboard jumper gives its
  two. A perfboard bare wire gives every pad it lies on (TL2-3). The check must read the whole set, not the two ends,
  or it cannot catch a router that runs over another net's pad. That is the check's whole worth. · E code read.
- TL2-14 · One shared search with a rules object is feasible and S, after P1350 merges. The generic part is the heap
  loop and the walk back (wire_routing.py:235-259 and :333-338): heap, closed set, BUDGET, `expanded`, `cut_short`.
  Everything else in `TrackRouting` is a breadboard rule: the two start legs (:236-241), the goal test (:250), the
  estimate (:261-270) and the moves with tracks on odd cells, rings, near, band and no_cross (:272-330). So the seam
  is a `GridSearch(rules, budget)` with the rules giving start states, moves with their extra cost, the estimate and
  the goal test. If the extraction keeps the heap tuples `(f, g) + state` and the push order, the bytes cannot move
  (E code read). The hook's 9 goldens pin it. Risk: low.
- TL2-15 · The costs object has one trap. `TRIES` is built from `MAX_BENDS` and `FALLBACK_BENDS` when the class body
  runs (wire_routing.py:200-202). A subclass, an instance or a later setting that changes `MAX_BENDS` leaves `TRIES`
  at 4 and 8. So a `RouteCosts` value must derive the tries from its own numbers. The one-pitch gap as a bare `2`
  (P1350's plan lists six places) and `TrackGrid.OUTER_TRACKS` (:115) are limits outside the cost line too. · E code
  read.
- TL2-16 · The costs are per surface, not one shared set. The breadboard's are cell, outside, beside a line, bend,
  cross (wire_routing.py:198). On the back of a perfboard a crossing is refused (TL2-4), "outside" does not exist, and
  new costs come in: a pad of bare wire, a bridge, a bend, a pad beside another net (TL2-4's free hole), and an
  insulated jumper with a fixed cost plus a cost per pitch. So one `GridSearch`, and each surface's rules own a named
  costs value (`TrackCosts`, `PadCosts`, names H). The PO's D-h and P1194's settings then read one value per surface.
  Proposed perfboard defaults, to tune in spike P1239 (D, the tech lead, not measured): pad 1, bridge 1, bend 2,
  beside another net 3, jumper 12 plus 1 a pitch. · E for the breadboard's list, D for the rest.
- TL2-17 · Two seams the perfboard search needs that the breadboard's does not use:
  - A net of k pins needs a goal of any pad already in the net (a tree), not one hole. So the goal test and the estimate
    (the least distance to any target) belong to the rules.
  - The insulated jumper is one more edge in the same search: from a pad of the net, straight along a row or a column,
    over pads and back wires, to a free pad, at the jumper's cost. Its two holes are claimed like a part's leads. Then
    one A* chooses between bridge, bare wire and jumper by cost, which answers D-q3 with no second router.
  · E for the breadboard's single goal (wire_routing.py:228, :250). The edge model is D, the tech lead's, for spike
  P1239.

| piece | perfboard use | size | risk |
| --- | --- | --- | --- |
| `Hole`, `HoleLedger.claim`, `is_free`, `group_is_free` | as it is | none | low |
| `Surface` | a maker per kind, letters, by_gap and rails behind it, a hole index (TL-9) | S to M | low |
| `PartPlacement`, `FirstFitPartPlacement` | P412 rule and tall-module row as surface rules, a body-inside-the-cut rule | S | low: golden-neutral if the breadboard keeps both rules |
| `BreadboardPlanner` | breadboard-only. A `PerfboardPlanner` reuses the step order, the catalog and the placement | L | medium: the resistor beside its pin, the power nets first |
| `JumperRouter` seam | as it is | none | low |
| `TrackRouting` A* loop | a shared `GridSearch` | S | low, after P1350 |
| `TrackGrid` and the breadboard moves | breadboard-only. A `PadLattice` and pad rules beside them | M to L | medium: the jumper edge and multi-goal nets, spike P1239 first |
| costs | a named value per surface, tries derived | S | low |
| `DrawnNets` | joins as sets of groups | S | low |

### Physics (question 3)

- TL2-18 · The current per join. The largest currents in spark's records are the L9110S at 0.8 A per channel
  (stated), the speaker at 0.866 A RMS (calculated) and the FireBeetle's 3V3 regulator at 1.5 A (stated, marked
  unverified). All are under the guide's "amps" line for 20 AWG (TL2-6). At 1.5 A, 50 mm of 24 AWG drops 6.2 mV and a
  one-pitch bridge 0.32 mV (EP-2, calculated). So at today's records every join kind carries the current, and the
  choice is mechanical. Two rules follow: a bridge only between neighbours (TL2-2), and no 30 AWG wire-wrap on a net
  over 0.5 A (TL2-6). No record holds a net's current, so it is derived from the largest consumer (EP-1). · E EP-1 and
  EP-2 of P1199, the guide.
- TL2-19 · The order of soldering. Copper side: rails first, then short links, then the rest (TL2-5, E). Parts: lowest
  first (TL2-10, H). Then the step sheet writes the parts in height order and the joins in route order, power first.
  Height is not in the records. The body size in mm is (`PartShape`, `body_mm`, TL-16), but not the height. So the
  first sheet can order by kind (resistor, header, button, LED, module) as a D table, and a height fact enters later
  by need.
- TL2-20 · Heat near the module. On female headers no joint touches the dev board (TL2-7). Soldered direct, each of its
  pins is a joint next to the module, and on a plated double-sided board each joint needs more heat (H, not read).
  Cheapest rung: none needed if headers are the default. If the PO wants direct soldering, the step sheet says
  "solder the board last, one pin at a time, alternating sides" (H).

## What I could not check, and why

- The DigiKey, Instructables, Hackaday and allaboutcircuits pages of #311. DigiKey returned a Cloudflare challenge.
  The others were outside the 4 fetches.
- The licence and the code of Perfboard Designer (see Found on the way). Only its guide page was read.
- The soldering order, the cut line, mounting holes and the female header height: no source read, so H.
- The step-sheet writer, the scene and the SVG pictures (sheet.py, breadboard_scene.py, svg_diagram.py). They are in
  D-q2 but not in my question set. The architecture lens covers them.
- A pad-lattice search itself. That is spike P1239. TL2-16's costs and TL2-17's edge model are unmeasured.
- Whether the P412 and tall-row seams keep 9 of 9 goldens. They should, as the breadboard keeps both rules, but no
  test ran (no test slot, by the brief).
- FIT0193's pitch, pad size, plating and mounting holes: P1238, the PO's calipers.

## Questions for the decider

1. How does the dev board sit on the perfboard? · decides the step sheet, the planner's height rule and the antenna
   rule · options: (a) female headers, removable, (b) soldered direct, lower, (c) a setting
   `perfboard.board_mount`, default headers, project layer · I would pick (c).
2. Perfboard Designer exists: open source, in the browser, with an MCP server and a page for AI agents (Found on the
   way). Is it read before spike P1239, as P1239 already reads perfwire and stripboard-py? · decides what the spike
   reuses and whether its export is a format spark writes · options: (a) read its licence and its router first,
   (b) go on without it · I would pick (a).

## Found on the way

- Perfboard Designer, by Krisztian Maurer and contributors: "Free, in your browser, no sign-up: lay out perfboard or
  stripboard, check every connection, flip to the solder side and print it at true size." Its footer lists "MCP
  server", "AI agents" and "GitHub", and "Perfboard Designer is open source". · E
  https://perfboarddesigner.com/learn/perfboard-wiring/, read 2026-11-28 · caveat: licence not read. Not found in
  docs/discovery/ by a grep, so P1199's research did not list it. For the PO assistant's Existing-first lens.

## Searches

1. Fetch https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html
   · served: the antenna end (TL2-8) · used.
2. Fetch https://www.digikey.com/en/maker/blogs/2022/start-building-cleaner-perfboard-projects-using-these-simple-tips
   · served: the joins · not used, a Cloudflare challenge came back.
3. Search, verbatim: "perfboard soldering tips lowest components first female headers bare tinned wire jumper"
   (DuckDuckGo HTML) · served: the joins, the order and the headers · used for TL2-7's snippet and to find 4.
4. Fetch https://perfboarddesigner.com/learn/perfboard-wiring/ · served: the joins, the wire sizes, the copper-side
   order · used (TL2-1 to TL2-6).
