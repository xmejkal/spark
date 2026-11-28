# The user lens, with UX and AI-UX (P1352)

Opus, 2026-11-28. Read-only on the tree. This file is the one file the lens writes. The persona is the maker with a
tested breadboard (the PO, n = 1) and Claude, which calls spark's CLI with `--json`. P1199's user lens (US-1 to US-8)
is not repeated here. Pointers to the canvas are to the two text files of the "spark project page" canvas, read as
data: `Perfboard.dc.html` and `LayoutPerfboard.dc.html` (the session's scratchpad copy, read 2026-11-28).

## Findings

**UL-1 · The board pick and the goal decide each other, and the two artboards disagree · E, H**
- The Perfboard artboard picks the smallest owned board that fits a plan of a fixed size: "The plan needs 26 × 18 holes" and "Spark picked the smallest of yours that fits" (Perfboard.dc.html:58, :189 onward, the `owned`, `need` and `best` values). E.
- The LayoutPerfboard artboard plans "roomy by default" on the 100 × 75 mm FIT0193 and then says "Cut to 24 × 16 holes" (LayoutPerfboard.dc.html:23, :39). The smallest goal gives 12 × 9 holes. E.
- #311 note 2 says "spark plans on the smallest that fits". D7 (P1199) says roomy is the default goal. D-c and D-f in the brief. E.
- If roomy means "spread the parts over the board", the board decides the plan's size. If the board is "the smallest that fits the plan", the plan decides the board. That is a loop. A person who picks a bigger board then sees the parts move, or sees nothing change, and does not know which to expect. H, my reading.
- The smallest fix: define roomy as a fixed spacing (free holes between parts, a named constant, D-h), plan first, then pick the smallest owned board that holds the plan plus a margin, then say the cut. Say it in one line on the screen: "Roomy plan, 24 × 16 holes. Your smallest board that holds it: FIT0193, cut to 26 × 18." H. Question 1 below.

**UL-2 · Journey step 1 stalls for the PO today: his drawer holds perfboards without any hole facts · E**
- The drawer holds two entries with `"does": "mount", "what": "prototyping-board"`: FIT0193, "ProtoBoard Pro - Double Sided (100x75mm)", count 2, and DFR0481, "Proto Board - FireBeetle Covers", count 1 (the store's drawer/dfrobot-fit0193.json and dfrobot-dfr0481.json). Neither holds holes across, holes down or pitch. E.
- The canvas has a state "No perfboard: Your drawer holds no perfboard" (Perfboard.dc.html:256). That sentence is false for the PO. He has three boards that spark cannot plan on. E.
- A fourth state is needed: "a perfboard without its holes". Its words name the entry and the next step: "Your FIT0193 has no holes across, holes down or pitch. Count them, or measure with calipers (D8)." Its `next` is the Operation that writes those facts to the drawer entry. H, the fix.
- The DFR0481 is a cover shaped for a FireBeetle (its label). It cannot be cut down like a plain board, and on a XIAO project it does not fit at all. The plan must grey it with that reason, not with "too small". E label, H reason.
- "Double Sided" means both faces carry pads (H, from the label, not read at a source). Then "the solder side" is a choice, not a fact of the board. The sheet must say which face it calls the back, once, at step 1. H.
- The canvas's three owned boards (4 × 6, 5 × 7, 7 × 9 cm, Perfboard.dc.html:189) are not in his drawer. The artboard shows a state he cannot reach. E.

**UL-3 · A bare wire's step names only its two ends, so the plain sheet and Claude cannot follow the route · E, H**
- The canvas step reads "Trace for CS on the back: from the board's D3 (C5) to the display's CS (I26)", and the hint "Lay a bare tinned wire on the pads the picture shows" (Perfboard.dc.html:186-187). The corners of the route live only in the picture. E.
- The breadboard step needs only two holes, because a jumper is straight between them (golden xiao sheet, line 25: "Holes: from j4 to f24"). E.
- A bare wire on a perfboard bends. Without its corners in words, the CLI's text sheet is useless without the SVG, Claude cannot explain the step, and the meter check cannot say which pads the wire passes. H.
- The smallest fix: each bare wire's step lists its holes at each turn: "C5, along row C to C9, down column 9 to I9, along row I to I26". The JSON holds every hole of the route in order. H.

**UL-4 · The mirror view flips left to right only, and the sheet never says how to turn the board · E, H**
- Both artboards mirror X and keep Y (Perfboard.dc.html:164, LayoutPerfboard.dc.html:121). The row letters move to the other edge (Perfboard.dc.html:236-241). E.
- That view is right only when the person turns the board over like the page of a book. Turned top to bottom, every hole in the view is wrong in rows, and the person solders the right column in the wrong row. H, geometry.
- How the PO turns a board is unknown. Question 3 below.
- The smallest fix, four parts. (1) Step 1 says "Mark hole A1 with a pen dot on both faces." (2) Each solder step says "Turn the board over left to right, like a page." (3) Both views draw the A1 mark in its corner and the row letters and column numbers on the edges. (4) A step names a pin by its hole ("the LED's K, hole J18"), never by left or right. H.
- A polar part shows its pins swapped in the mirror (the LED's A and K, a header's pin 1). The canvas tags A and K on the mirrored view (LayoutPerfboard.dc.html, the `tags` values). Keep that, and add the pin-1 tag of each header. E, H.

**UL-5 · The breadboard's JSON holds no layout, so Claude has nothing to change a perfboard plan with · E, H**
- `breadboard.py --json` gives each file written, its codes, `drawn_from` and `since`, and `next` (docs/guide/agents/json.md:150-152). The steps and holes are in `breadboard.md` as text, and the layout is in `breadboard.json` as Wokwi px. E. P1199 US-5 found Claude would have to compute px from holes. E.
- "Spark plans, Claude changes" (#311 note 1) needs the plan as data. The keys Claude needs, each a fact spark derives (AGENTS.md, facts not behaviour): H, my list.
  - `board`: the drawer entry, holes across and down, pitch in mm with its origin (`assumed` or `measured`), the face called the back, and the cut as kept holes ("A1 to P24") and mm.
  - `goal`, with the spacing constant it used, and `goals_compared`: the size and the join counts of roomy and of smallest, from one plan run. Then Claude can offer "smaller, but 2 more jumpers" without a second run.
  - `parts`: each part's id, record, hole per pin, mount (`direct` or `socket`), and the facts it rests on that are not verified.
  - `joins`: each with a stable id, the point it serves (the Points' number), its kind (`bridge`, `bare`, `jumper`), its face, every hole in order, its length in mm, its cost, and for a jumper the join it crosses and the hole where.
  - `costs`: the named constants the router used (D-h), by name and value.
  - `pins_kept`: each signal and its board pad, equal to `pins.py`. A true value only when equal. P1199 D-b.
  - `neighbours`: each pair of next-door pads on different points (see UL-8).
- A change goes through an Operation, never through a file edit by hand: a dry run, then `--apply`, as `--move-hold` does (docs/guide/agents/json.md:244). Its requests: another board, another goal, a part to holes, a join to avoid. A refusal is a `problems` item with a code and a `fix`. The move is kept in `.spark/layout-edits.json` (D-f). H for the shape, E for the pattern.

**UL-6 · The step sheet's order and words must differ from the breadboard's · E, H**
- The breadboard sheet interleaves parts and wires, "One connection per step" (golden xiao, lines 19-30). Its words are breadboard words: "each pin in its own row", "a free row", "the GND rail" (lines 21-29). The point lines carry rail words too: "join board GND to a - rail" (line 74). E.
- On a perfboard there are no rows that join, no rails and no "free row". The ground becomes one more point, joined by bare wires. H.
- The step kinds the brief names, as a person reads them (H, my proposal, the order by face and height):
  1. Cut: "Cut the FIT0193 to 26 × 18 holes: keep A1 to R26. Score along row S on both faces, then snap." Only when a cut is needed.
  2. Mark A1 (UL-4).
  3. Place a part, parts face: "Put R1 (330 Ω) with its ends in G11 and G16. Bend the leads out a little so it stays when you turn the board." Low parts first, then the button and LED, then the headers.
  4. Solder its pins, back: "Turn the board over left to right. Solder R1 at G11 and G16. Do not trim yet." The lead may become the bare wire (UL-9).
  5. Bridge two pads, back: "Bridge G16 to G17 with solder: R1 end 2 to the LED's A."
  6. A bare wire, back: "Lay a bare tinned wire from B2 along row B to B8, then up to A8. Solder it at each pad it passes." With its corners (UL-3).
  7. An insulated jumper, parts face: "Run an insulated wire from C10 over to C21, then down to M21: the button's B to GND. It crosses the wire of D8 at G21."
  8. Trim the leads.
  9. Check (UL-8), then plug in and power.
- Fewer turns of the board: place all low parts, turn once, solder all of them. The canvas turns the board at each step (steps 1 to 4, Perfboard.dc.html, the `steps` values). Each turn risks a part falling out. H, hobby practice, not searched.
- One word for one thing (H, the names check): "trace" (Perfboard.dc.html:186) and "bare wire" (LayoutPerfboard.dc.html) are the same thing. "Jumper" means any wire on the breadboard (bench_changes.py `JUMPER`) and only the insulated one here. "Via" (the PO, #311 comment of 2026-11-20) is PCB language. Proposal: hole for the place ("C5"), pad for its copper, joint for the solder in it, bare wire, insulated jumper, bridge.

**UL-7 · Five places a person gets stuck, and what each says · E, H**
- No perfboard, and one without its holes: UL-2.
- None big enough: the canvas says "the plan needs 26 × 18 holes, your biggest has 23 × 15. Add a bigger one, or ask Claude for a tighter plan" (Perfboard.dc.html, `states`). Keep it, and give its Ask Claude sentence the smallest goal's own size, so the person knows whether a tighter plan fits at all (`goals_compared`, UL-5). E, H.
- A missing pin fact: the LED's record has `footprint: "pinrow2"` and a body in mm, the button's `footprint: "pushbutton"` and a body, and no record holds pin positions in mm (parts/led-red-5mm.json, parts/tactile-button.json). The boards hold their header in mm (boards/xiao-esp32-c6.json `//physical`: two rows of 7 at 2.54 mm, rows 15.24 mm apart). The resistor is generated and has no record, so no lead span. E. The plan must say what it assumed: "R1 spans 6 holes, an assumption: a 1/4 W resistor's usual bend". The canvas's "Not confirmed" state does this for the display (Perfboard.dc.html, `states`). E, H.
- A dev board that needs headers or sockets: no pin header and no female socket is in the drawer (no drawer file name holds "header" or "socket", a grep of the store's drawer folder). The canvas plans female headers for the FireBeetle, "so it stays removable" (Perfboard.dc.html, step 1). Then the parts table must list "2 × 7-pin female header, to get", and the plan waits until they are in hand, or offers "solder the XIAO straight in". E, H. Question 2 below.
- Cutting the board: the canvas offers "Cut it to 27 × 19 holes before step 1, or keep it whole: the plan sits in its corner" (Perfboard.dc.html, `boardLine`). Keep that choice. Name the cut by the holes kept and the row to score, never by mm alone, and keep one free row past the outer pads. Whether the FIT0193 has mounting holes in its corners, which cost holes, is unknown (no record). E, H.

**UL-8 · The check must name the pads to beep, not only the points to join · E, H**
- The breadboard's Points say "its ends must be joined, and nothing else" (golden xiao, line 70). E.
- The canvas's check step says "Look for solder between two pads, then beep each wire end to end with a meter" (Perfboard.dc.html, step 13). E.
- On a perfboard the risk is the "nothing else": a blob of solder between two next-door pads of different points. Spark knows every such pair from the plan. The step lists them: "Beep G17 against H17: no beep (the LED's A and GND)." And first: "Beep 3V3 against GND before USB: no beep." H. A fact derived from the plan, so within AGENTS.md's facts rule.
- The canvas keeps "Soldered: spark cannot see it" as an open mark, never a ✓ (Perfboard.dc.html, the check list). Keep it. E.

**UL-9 · What the breadboard gives unchanged, and what must differ · E, H**
- Unchanged, as far as I read:
  - The refusals before any plan: not built, stale, other requirements (sheet.py:107-154, the `_check_fresh` codes). E.
  - The parts table with its `have` column and legend (sheet.py `_parts_table`). Its last row "a breadboard and jumper wires" becomes the perfboard's own rows: the board, solder, bare tinned wire, insulated wire, sockets. E, H.
  - The Points list, without the rail words (UL-6). E.
  - The Mermaid diagram of the points with step numbers (sheet.py `WIRING_VIEWS`). It knows no surface. E.
  - "Before you power it" (before_power.py). One record line says "On a breadboard: the LONG lead (anode)" (golden xiao, line 84). It reads oddly on a perfboard, but its next sentence ("the flat is the mark that survives") holds. E.
  - The scene and its renderers: "Another router is another maker here, and no renderer changes" (sheet.py:59-63). The part pictures by view, `breadboard-top` (json.md:249), and a perfboard view without pins (D-e). E.
  - The same-pins check (drawing_match, P279), if it reads joins as it reads jumpers. H, the tech lead's to check.
- Must differ:
  - The step words and order (UL-6), and the route's holes in words (UL-3).
  - No Wokwi diagram and no paste round trip. The sheet's Wokwi line (golden xiao, line 64) goes. E.
  - The changes on the bench: bench_changes.py says it "names jumpers by their ends and colors, never by holes: the person picks their own free rows" (bench_changes.py:4-5). On a perfboard every hole is fixed, and a change means desoldering. The canvas's "Out of date" state says "Plan it again. Your soldered board stays as it is" (Perfboard.dc.html, `states`). So the perfboard needs no change list in its first slice. E, H.
  - Colour: a bare wire is tinned and has no colour. Only an insulated jumper takes the palette (sheet.py `JUMPER_COLORS`). The canvas colours each trace's tag by its net (Perfboard.dc.html, `wireDefs`), which reads as a wire colour the person cannot buy. H.
- A join kind the brief does not name: bending a part's own lead along the pads to the next joint, instead of a separate bare wire. H, hobby practice, not searched. The tech lead may weigh it.

**UL-10 · The tested pins are kept, and the screen says so, but no screen shows when they would not be · E, H**
- The canvas says "The pins stay the ones your firmware was tested on" and "✓ The pins are the ones your firmware was tested on" (Perfboard.dc.html, the Now card and the check list). E.
- If Claude asks for a change that only a pin change would allow (the PO's #352 chain: a part swapped, "Connect it to pin number 20"), the plan must refuse and point to the design area, as P1199 US-4 found. The perfboard JSON's `pins_kept` (UL-5) makes the refusal checkable. H.

## Wireframes

The perfboard screen, crude (my sketch from the two artboards, with UL-1 to UL-4 and UL-8 applied):

```
+------------------------------------------------------------------------------------------------+
| button-light-xiao   ... On the board v | Perfboard (optional, now)   PCB o   Case o            |
+-- Now: solder it on a perfboard ---------------------------------------------------------------+
| Roomy plan, 24 x 16 holes (61 x 41 mm). Pins stay the tested ones.   Goal: (Roomy) (Smallest) |
| Your perfboards:                                                                               |
|  [* FIT0193 100x75 mm, 39 x 29 holes? ]  [ FIT0193 #2 ]  [-- DFR0481: a FireBeetle cover --]   |
|   holes not counted yet: count or measure ->                 greyed, does not fit a XIAO      |
| Cut: keep A1 to P24, score along row Q and column 25. Or keep it whole.                        |
| ( Parts face )  ( Back, mirrored: turn it like a page )                                        |
| +------------------------------------------+ +-----------------------------------------------+ |
| |    24 . . . . . . . 10 9 8 . . . 2 1  *A1| | Step 6 of 15 . back                           | |
| | A  . . . . . . . . . . . . . . . . .   A | | Bare wire: board D8 to R1 end 1.              | |
| | B  . . . . . o=====o . . . . . . .     B | | From B2 along row B to B8, then up to A8.     | |
| | C  . . . . . . . . o . . . . . . .     C | | Solder it at each pad it passes.              | |
| | ..   joints o, bridge oo, wire ===       | | Keep it off C9 (D10's wire).                  | |
| |  A1 mark in its corner, labels on edges  | | [ < Step 5 ]  [ Step 7 > ]   keys: <- -> space| |
| +------------------------------------------+ +-----------------------------------------------+ |
| Joins: 1 bridge, 4 bare wires, 1 insulated jumper (crosses D8's wire at G21)                   |
| v Every joint joins the same pins as the circuit.  v Pins are the tested ones.                 |
| ? R1 spans 6 holes: assumed.  o Soldered: spark cannot see it.                                 |
| [ Ask Claude: "Plan it smallest, fewer jumpers, keep the tested pins." ]   [ Copy ]            |
+------------------------------------------------------------------------------------------------+
```

The CLI's plain output, crude. The command name is a placeholder: the design names the Operation.

```
$ SPARK_HOME=... <perfboard command> requirements.json --keep .
Perfboard: button-light-xiao, on a Seeed Studio XIAO ESP32-C6
Plan: roomy, 24 x 16 holes (61.0 x 40.6 mm at 2.54 mm, assumed until you measure it)
Board: FIT0193 (drawer), cut to keep A1 to P24
Joins: 1 bridge, 4 bare wires, 1 insulated jumper
Smallest instead: 12 x 9 holes, 1 bridge, 4 bare wires, 1 insulated jumper
Pins: the tested ones (5 of 5 equal to pins.py)
Same pins: every joint joins the same pins as the circuit
Assumed: R1 spans 6 holes. Pitch 2.54 mm.
Not in your drawer: none needed (the XIAO is soldered straight in)
wrote perfboard.md, perfboard.svg
next: count or measure the FIT0193's holes: <drawer Operation> fit0193 --holes ACROSSxDOWN --pitch MM
exit 0
```

And the stuck case, as the same command answers it:

```
Perfboard: not planned
- FIT0193: no holes across, holes down or pitch in your drawer. Count them, or measure with calipers.
- DFR0481: a FireBeetle cover, not a plain board. It does not fit a XIAO.
next: <drawer Operation> fit0193 --holes ACROSSxDOWN --pitch MM
exit 1
```

## What I could not check, and why

- How the PO turns a board to solder, whether he soldered a perfboard before, and whether his FIT0193 prints row and column labels on its faces. No evidence in the files I read. Account questions.
- The FIT0193's grid, margins and mounting holes. Its drawer entry has none, and I made no search (the brief gives searches to the tech lead).
- Whether "Double Sided" means plated-through holes. Read from the label only.
- The usual 6 × 6 button leg spacing and a 1/4 W resistor's usual bend, and whether a part's own lead is a common bare wire. Hobby practice from model knowledge, all H.
- Whether drawing_match's same-pins check takes joins without change. Code read only to its docstring. The tech lead's.
- The canvas as rendered. I read its text and its script values, not the drawing, so a mismatch between the picture and its words is not checked.

## Questions for the decider

1. Which comes first, the plan's size or the board? · decides UL-1, the board line and the cut · options: (a) plan roomy at a fixed spacing, then the smallest owned board that holds it, cut to fit (my pick) · (b) the smallest owned board that fits a tight plan, then spread the parts over it · (c) the person picks the board each time, and spark spreads over it.
2. How does a dev board go on the perfboard by default? · decides the parts table, the first steps and a stuck state · options: (a) female sockets, so it stays removable, listed "to get" until in the drawer · (b) soldered straight in by its own pins · (c) spark asks per project, sockets first.
3. Account, n = 1, past tense: when you last soldered a board, how did you turn it over, and did the board print its row and column labels? · decides UL-4's mirror and the hole names on the sheet · options: like a page (left to right) · top to bottom · I have not soldered a perfboard yet.

## Searches

None.
