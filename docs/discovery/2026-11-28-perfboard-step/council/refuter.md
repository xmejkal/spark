# P1352 council: the refuter

Opus, 2026-11-28, read between about 11:00 and 11:25 CET, read-only on the worktree spark-wt-perfboard (HEAD a85de9f5)
and on the store. I ran no tests. The only Python I ran was `python3 -I -B` reading JSON, so no bytecode was written.
I wrote this one file and nothing else. No file I read asked me to do anything.

## 1 Claims

### Check first (an existing product)

- **The observed problem.** The only observed account is P1039 D11 (2026-11-23): after the clock and the bin ran on
  the breadboard, "they needed a permanent build" (docs/discovery/2026-11-23-p1039-rd-direction/brief.md:115). The
  card already filed for that account is spike P1074 #1575, still OPEN, whose Done when takes "one of his two gadgets
  (the e-paper clock or the bin) ... toward a perfboard layout" and says where spark stops. The backlog review of
  2026-11-24 calls it "the live card of that slice" (the store's backlog-review-2026-11-24.md:143). The brief leaves
  #1575 out of "still open elsewhere" (brief.md:32), and its walking skeleton targets button-light, a test project
  (story-map.md slice 0, items.md). So the proposed first slice does not touch the gadgets in the observed account.
- **What breaks for current users. I name what the folder misses:**
  - The same-pins check's codes. Move 6 (architecture.md:177-180) says "the codes' strings change for agents".
    `not-joined`, `joined-to-other` and `joined-to-unused` are public in docs/guide/agents/scripts.md:219-220, and
    ARCH-P5 says the core's `Finding.of` refuses them. Yet items.md lists the ConnectedGroups item as "refactor story,
    byte-neutral" with "depends on: —". The 9 goldens do not prove that move safe, because the codes are an agents'
    contract, not golden bytes.
  - The build's time. Nobody measured it. `FirstFitPartPlacement` scans every hole for each candidate:
    `group_is_free` (drawing.py:206-207), `_pins_keep_a_free_hole` (:313-317) and `_covered` (:319-325) each loop over
    `surface.holes` or `surface.terminal`. One refusal on a 40 by 30 surface took 4.21 s (TL2-11). Neither the tech
    lead's table nor the brief gives the time with the rule off. Move 10 puts the layout Operation inside
    `build-board --keep` (kept_files.py:267). A "spread" goal (P1199 D7) tries many candidates, so the cost grows
    about with the square of the holes. That is a build-time risk the folder does not name.
  - The 9 goldens as a guard. 3 of the 9 are 2-line could-not-run refusals (`wc -l`: bad-out, not-built, stale), and
    `breadboard-ok-not-drawn.txt` has no SVG path. So at most 5 goldens show a placement or a route. "9 of 9" in
    A4, A6 and items.md reads stronger than that.
  - Wokwi taking breadboard.json: move 1 does not change it (byte-neutral, H). The router's budget: `BUDGET = 60000`
    is per search (wire_routing.py:207, :245), and A5's pass line ("each under 60000 states") does not say whether it
    means one search or the gadget's total `expanded`.
- **Confirmation bias.** The persona is the PO (user.md:3-4). J2 and J3 are the team's H (jobs-and-journeys.md). J3's
  "so" clause is tagged E from a hobby guide, which says nothing about what he wants. The two canvas artboards that
  ★C6 treats as a design conflict are the team's own drafts. "Ready for: collecting evidence" (brief.md:10) is
  honest, but items.md already writes six cards with "needed by" quotes, two of them with "depends on: —". So the
  build is shaped before Q1 to Q9 are answered.

### Per claim

- **★C1 · partly.** P269 brief.md:15: "probably we will want to reuse code for the perfboard stagte, so please also
  create some common base". #311 note 1 (2026-11-26): "Spark plans, Claude changes". P269 D3: "Yes, but later". The
  two wants are each said once (10-16 and 11-26), so they are not "repeated" six weeks apart. The shared code base
  comes back on #1747 (11-26: "Can we refactor out some protocole or omdule or class or whatever to reuse") and in
  the request of 11-28. "Spark plans, Claude changes" is in quotes in a note that the agent account xmejkal wrote, so
  it is relayed, not read from him. Change it to: "Two wants recur: shared code (10-16, #1747 on 11-26, the request on
  11-28) and a plan that spark makes (#311 note 1, 11-26, relayed). No word gives a soldering date."
- **★C2 · holds.** P1199 brief.md:124: "D3 · Q3: the layout core is built after the MVP, born in the first slice that
  needs it". architecture.md:197-200 (MF1) and po-assistant.md:32-38 (PA-2) give the two readings, as H. I could not
  check the request itself, which spark-artifact relayed.
- **★C3 · partly.** `grep -c -i -E "perfboard|solder|permanent" scrum/VISION.md` gave 0. architect.md:9: "One gate
  opens the permanent build: the last deploy wrote the current image, the board said ready, and the person says "it
  works"." That holds for the perfboard step. It does not hold for moves 1 to 3. drawing.py is at 599 of 600 lines
  (tools/measure.py:242, `MODULE_LINES = 600`), so any breadboard fix that adds lines to drawing.py is blocked today,
  and that is an MVP cost. The brief uses ★C3 against the refactor (D-q6 (a) and (c), the viability row). Change it
  to: "the perfboard step scores zero on the MVP bar; the drawing.py split (move 1) is judged on its own."
- **★C4 · holds, narrowly.** I re-ran the grep. The only perfboard line in the three bench files is
  bench-layout-log.md:14: "If it holds fewer than 3 lines, the walking skeleton P1237 #1790 waits until the perfboard
  card is pulled." In the walks, p934-epaper/diary.md:19 says "soldered at one long edge." The handoffs mention
  perfboard only as card work (handoff-2026-11-22.md:469, restart-2026-11-27.md:330). The INMP441 record says "board
  soldered to header pins in a breadboard" and does not say who soldered it. The brief drops PA-4's line that on
  2026-11-24 the backlog review proposed closing #311 "as not now".
- **★C5 · holds.** drawer/dfrobot-fit0193.json:3: `"label": "ProtoBoard Pro - Double Sided (100x75mm)"`, :4
  `"count": 2`. dfrobot-dfr0481.json:3: `"label": "Proto Board - FireBeetle Covers"`, :4 `"count": 1`. Neither entry
  holds a hole count or a pitch. drawer-import/dfrobot-orders.json:2: "bought is not the same as still in the drawer".
- **★C6 · partly.** Perfboard.dc.html:58: "The plan needs 26 × 18 holes. A board can be cut smaller, never made
  bigger." LayoutPerfboard.dc.html:23: "button-light on the 100 × 75 mm perfboard in your drawer (FIT0193): ... wired
  to the board by a 3-pin header." The two artboards show **two different gadgets**: Perfboard.dc.html:26 is the
  "E-paper quotes clock" with a FireBeetle, and LayoutPerfboard is button-light with a XIAO. Both plan first and then
  cut (Perfboard :200, "fits, cut it to 27 × 19"; LayoutPerfboard :39, "Cut to … holes"). So the first
  "disagreement" is not one, and the second may be a choice per gadget. Both files are dated Nov 27 10:47. Change it
  to: "The artboards show two gadgets. The clock sits on female headers on the board, and button-light's XIAO sits
  off it by a 3-pin header. Only LayoutPerfboard names a goal (roomy)."
- **★C7 · holds.** Perfboard.dc.html:186: "'Trace for ' + b + ' on the back: from the board’s ' + a + ' (' +
  hole(pts[0][0], pts[0][1]) + ') to the display’s ' + b". Only the first and the last point appear in the words.
- **★C8 · holds.** Perfboard.dc.html:164: "const X = (c) => mir ? 624 - (c - 0.5) * P : 30 + (c - 0.5) * P; const Y =
  (r) => 24 + (r - 0.5) * P;". LayoutPerfboard.dc.html:121-122 does the same. Step 2 says only "Turn the board over
  and solder the 32 header pins" (Perfboard.dc.html:179).
- **★C9 · partly.** json.md:151: "A `wrote` entry for `breadboard.svg` may have `drawn_from` (`record`), and the one
  for `breadboard.md` `since`". Those keys belong to **check_spine.py's** `kept` entries (heading json.md:145).
  json.md:297-298: "These do not take it: ... `breadboard.py`". So no "breadboard's `--json`" exists, and UL-5's
  "`breadboard.py --json` gives each file written" is wrong. "Claude has no plan to change" is also too strong. Today
  Claude can move a part in breadboard.json, and kept_moves keeps it (scripts/breadboard.py docstring: "A part, a
  resistor or a jumper you moved in breadboard.json stays where you put it at the next build (P273, P287)"). P1199 D4
  removes that path, but it is not built. Change it to: "check_spine.py's `--json` names the sheet's files and holds
  no layout. The layout is breadboard.json in Wokwi px, which kept_moves reads back until P1199 D4 lands."
- **★C10 · partly (code read, trial not reproduced).** drawing.py:290: `if part_px.get("covers_holes") and not
  self._pins_keep_a_free_hole(holes, covered, ledger):`. data/wokwi-geometry.json gives `covers_holes: True` for
  wokwi-resistor and board-xiao-esp32-c6 and `False` for the LED and the pushbutton. That fits the table. The trial is
  in memory and gone, and `Surface.__init__` cannot build a single-pad surface (drawing.py:117-121 names groups
  "%d%s" by column and top/bottom), so the trial patched code that I cannot see. The times are one run on an unnamed
  load. Add to the caveat: "a patched Surface; times from one run; the time with the rule off is not given".
- **★C11 · partly (undercounted).** spacing.py:102: `if max(down, up) <= surface.letters_y[bottom[0]] -
  surface.letters_y[top[-1]]:`. wire_routing.py:120: `self.x0, self.y0 = min(hole.x for hole in surface.terminal),
  min(surface.letters_y.values())`. A third site has the same expression: **breadboard_scene.py:114**
  (`SceneGrid.of`). D-e and option D-q1 (b) reuse the scene for the perfboard, so that site matters. A fourth is
  board_marks.py:45-46 (breadboard-only). spacing.py:102 is reached only for a part that covers holes and has its pins
  in one row (:96), so the XIAO returns None before it. Change it to: "Three shared pieces read the row letters
  (spacing.py:102, wire_routing.py:120, breadboard_scene.py:114) and fail with none."
- **★C12 · partly.** drawing.py:241: "Strategy: which holes the jumpers take, once the parts are placed and each
  jumper has its two rows." :245: "The default keeps the holes the planner took." The planner's own loop picks each
  jumper's two groups before the seam (drawing.py:352-367, `claim_free_hole`, `claim_free_group`). TL2-12 (the tech
  lead) says that loop fails on single pads, so `BreadboardPlanner.plan` is breadboard-only. The brief keeps ARCH-P1
  with "caveat: none" and drops TL2-12. The lenses split here, and verification.md's Agree/split was still unfilled.
  Change it to: "The plan has a post-placement seam for jumper holes, after the planner fixed each jumper's two rows.
  A perfboard needs its own planner around that seam (TL2-12)."
- **★C13 · partly.** wire_routing.py:236-241: `for move in (1, 3): leg = _step(search.start, move); if
  self._leg_ok(leg, search): state = leg + (move, 0, 1, 2)`. That is the vertical start legs and a 6-field state with
  breadboard counters inside the loop. :250 `if state[:2] == search.goal:` tests one goal cell, and TL2-17 says a
  perfboard net needs any pad of a tree. ARCH-P2 itself says "(the start legs are a rule inside the loop)". The caveat
  keeps the tie order and drops these two. Change it to: "The loop's heap and budget name no breadboard word. Its
  start legs, its state shape and its single goal are breadboard rules, and they must move out with the moves."
- **★C14 · holds.** wire_routing.py:198: `CELL, OUTSIDE, BESIDE_A_LINE, BEND, CROSS = 1, 2, 2, 4, 6`. :202: `TRIES =
  ((MAX_BENDS, "", False), (FALLBACK_BENDS, BENDS, False), (FALLBACK_BENDS, BENDS, True))`. These are class-body
  values. The last change to the file is 0998bf4f on both the branch and origin/main.
- **★C15 · holds.** drawing_match.py:44-45: `for jumper in layout.jumpers: self._join(jumper.one.group,
  jumper.other.group)`. The guide: "The lead touches every pad it passes over." (fetched). The caveat should add
  ARCH-P5: part contacts come from Wokwi's `joined_pins` (:47), which a perfboard part does not have.
- **★C16 · holds.** Fetched: "they can't cross anything", "Leave a free hole between different connections.", "For
  anything longer than two or three holes", "Updated November 9, 2026". The caveat is right: it is one hobby guide.
- **★C17 · holds.** Fetched: "It is suggested to place the module's on-board PCB antenna outside the base board". The
  section heading is "Positioning a Module on a Base Board", and the page says nothing of dev boards on headers. A grep
  for "antenna" found nothing in boards/*.json, and nothing in the clock's own record
  (spark-walks/p934-epaper/boards/firebeetle2-esp32c6.json), which the brief did not grep.
- **★C18 · partly.** architecture.md:81 (D1): "`SceneGrid` says it turns px into cells "as the router's TrackGrid
  does"". D1 is confirmed (breadboard_scene.py:112-117 against wire_routing.py:119-120). D2 is weaker:
  `_joined_groups` (breadboard_scene.py:249-256) returns "The hole groups that join something", a set for marks, not
  a reading of nets. `wiring_steps.points` joins circuit ports, not holes. One "connectivity" class would put three
  different questions in one place. architecture.md lists seven (D1 to D7), and the brief says five. Change it to:
  "two half-pitch grids (confirmed), two union-finds over different inputs, and three body models. The pad placers and
  the scene's group set are near-duplicates only as an H."
- **★C19 · partly.** `wc -l drawing.py` gave 599, and tools/measure.py:242 has `MODULE_LINES = 600`. The "so" does
  not follow. Moving code out of drawing.py (moves 4 to 8) makes it shorter. Only a change that adds lines in place,
  such as A6's P412 seam or a `JoinRouter` rename with adapters, needs room. Change it to: "so any change that adds
  lines to drawing.py, such as the P412 seam, needs the Wokwi renderer out first."
- **★C20 · holds.** bench_changes.py:26: `from spark.build.build_record import STAGE_SUFFIX, StagedFile`.
  kept_files.py:16: `from spark.breadboard import drawing, sheet, svg_diagram, tabbed_page`. sheet.py:20: `from
  spark.sourcing import drawer`. Five sourcing modules import spark.breadboard (grep).
- **★C21 · partly.** operation_catalogue.py:27-28: `TABLES = (("idea", IDEA), ("sourcing", SOURCING),
  ("sourcing.research", RESEARCH), ("design", DESIGN), ("build", BUILD), ("checks", CHECKS), ("firmware", FIRMWARE),
  ("bench", BENCH), ("flow", FLOW))`. That confirms no breadboard Operation. "Only through `build-board --keep`" is
  wrong: scripts/breadboard.py:12 and :25 call `sheet.write` straight (`written = write(requirements, out)`), with no
  Operation and no `--json`. Change it to: "The breadboard area has no Operation. Two frontends write the sheet and
  its drawings, `build-board --keep` (kept_files.py:267) and `breadboard.py` (scripts/breadboard.py:25), each calling
  `sheet.write`."
- **★C22 · holds.** `git log -1 3b7e6d09`: "Merge pull request #1922 from xmejkal/p1290-ask-claude-text".
  flow_codes.py:364: `ASK_CLAUDE, COPIED_SAYS, NOT_COPIED_SAYS = "Ask Claude", "Copied: paste it in Claude Code."`.
  `next_words` reads the guide's `now` (next_words.py:33). What a drag would reuse is the Copy block, not
  `next_words`.
- **★C23 · partly.** parts/led-red-5mm.json `//footprint`: "pinrow2 is two through-holes at 2.54 mm, which is the
  drawing's lead spacing (2.54 (0.1) mm, measured where the leads leave the package, page 1)". So the LED's record
  holds its lead spacing, with a citation, as a note and through its footprint. Its `body_mm.note` also gives a height
  ("lens plus flange stand 8.6 (0.339) mm above the lead exit"), and the button's note gives "Height is 4.3, 5, 8 or
  12 mm", which also qualifies TL2-19's "Height is not in the records". The resistor has no record (it is generated).
  The drawer part holds (no label names a header or a socket). Change it to: "No record holds the resistor's lead span.
  The LED's 2.54 mm lead spacing is in a note and its footprint, not a field."

## 2 Dropped caveats and stronger claims

- **D-d** ("three join kinds from one search ... the PO · 2026-11-26 · #311 note 3"). In note 3 his words are only
  the question and "I am not sure what the best practices are actually". "One search" in that note is the agent's web
  search. "The three join kinds come from one search" is the P1199 session's item text (#311, 13:45 comment), which he
  took in bulk ("All 14", D10). So D-d is the team's design, not his decision.
- **D-a** ("the perfboard comes after the editor that keeps moves", decided), against the story map. Slice 0 builds the
  perfboard plan, and slice 2 then brings `edit-layout` to the perfboard. That reverses D-a's order. PA-8 says D-a is
  open to reading since P1199 D4, and the brief lists it as decided with no caveat. The layout log (bench-layout-log.md:14)
  ties P1237 to the perfboard card too. The brief does not raise this as a question.
- **D-q5 (a), "caveat: none".** P1199 D7's own text says "`layout-placement` defaults to `spread` on the perfboard",
  and #1747 has his "take up the whole perfobard and use the space". UL-1's "roomy at a fixed spacing, then cut"
  redefines D7's spread. Its caveat should say it reopens D7's meaning.
- **The no-gos cite D-j** ("no setting layer before P1194, the weights are code defaults (D-h, D-j)"). MF3 says code
  defaults meet D-h "and not yet D-j". That caveat was dropped.
- **The viability row** ("E one lane slot and the MVP cards first (★C3)"). ★C3 says nothing of lanes. PA-3 marks the
  lane cost H: "I did not check which sessions run now".
- **Outcome (1)** uses #311's Done when as the observable. PA-6 says "The Done line on #311 is the team's words, not
  his". That caveat was dropped.
- **items.md.** The ConnectedGroups item says "byte-neutral" and "depends on: —". Move 6's risk ("the codes' strings
  change for agents") was dropped. Its proof ("One test catches a bare wire over another net's pad") needs a perfboard
  join before any perfboard exists, which is the "part with one caller" that D-q2 (b)'s own caveat warns against. Both
  refactor items name the PO's words as "needed by" and carry no D3 order, so they take the architecture lens's
  reading (b) of Q2 before he answers it.
- **C25 and UL-2** ("the PO, who owns three"). ★C5's caveat "bought is not the same as still in the drawer" was
  dropped. Read it as "bought three".
- **C26** cites bench-layout-log.md:14 for the empty table. The table is at :33-48. Line 14 is the rule that ties P1237
  to the perfboard card.
- **A1** "within about three months". PA-9 says "within a few months". The "three" has no source.
- **Q4's opinion** "(the tech lead, the PO assistant: (a))". The tech lead picked (c), "a setting
  `perfboard.board_mount`, default headers" (tech-lead.md:182). The user lens's own CLI sketch says "the XIAO is
  soldered straight in" (user.md:140), which fits neither. The brief shows agreement where there is a three-way split.
- **TL2-7's headers** rest on "a search snippet ... the page not opened". The brief's D-q4 (a) cites TL2-7 and TL2-20,
  all H, and that is correct. The opinion that female headers keep "no heat on the module" is also H (TL2-20), but the
  brief's cost cell says it plainly.
- **Names.** The brief says "costs" (Frame D-q3, Scope), D-h says "penalties", ARCH-P3 says "weights" ("'Cost' means
  money in spark's rules"), TL2-16 has `TrackCosts`, `PadCosts`, and UL-5 has a `costs` key. That breaks "one word for
  one thing" (rules.md, plan names).

## 3 Rival explanations

- **★C1, A1 (he will solder soon).** Rival: the request is about the architecture ("Make sure the architecture is good
  as usual, reusable", "dried out"). The perfboard is the second caller that justifies the refactor he wants, and
  soldering is not near. The P269 D3 "Yes, but later" and the #311 "as not now" proposal of 11-24 both fit this. Q6
  tests it only if "(d) none planned" is offered without a lead, and it is.
- **★C4 (little practice).** Rival: he solders modules or other boards outside spark. "I am not sure what the best
  practices are actually" can be about perfboard routing conventions, not about soldering. Q9 asks it, so nothing in
  the folder rules it out yet.
- **★C2 (two readings).** Rival: relay distortion. spark-artifact relayed the request into this session, so a third
  reading is that the refactor licence was about P1350's file only (the same morning's #1937 comment: "configurable or
  at least as constants in the code").
- **★C6 (the artboards disagree).** Rival: two gadgets, two fitting mounts. A clock with a display and a FireBeetle
  goes on headers, and a three-part button-light goes on a small board joined by a header. That is not a conflict to
  resolve.
- **★C10 (the P412 rule refuses).** Rival 1: on a perfboard the rule is right in another form. Each pin needs a free
  neighbouring pad for its bridge or wire, so it needs a perfboard form of the rule, not removal. Rival 2 for the
  seconds: the scans over every hole (drawing.py:206-207, :313-317, :319-325), not the rule, make the refusal slow.
- **★C13 and ★C18 (share the search, merge duplicates).** Rival: the shared part of `_search` is about 20 lines, and
  each surface brings its own state, start and goal. Lifting it buys little DRY and risks `cut_short`'s tie order.
  For D2 and D3 the "duplicates" answer different questions, so merging them couples where the PO's rule ("almost the
  same") does not apply.
- **★C3 (zero on the bar) against moves 1 to 3.** Rival: the drawing.py split serves the MVP breadboard on its own
  (599 of 600), so its order is a breadboard question and not a perfboard one.
- **Readiness.** Rival to "the shared core is the next step": the cheapest evidence is spike #1575 on the clock, which
  the folder names only as PA-9's "next cheapest" test and leaves out of the options.

## 4 Numbers

- "1.38 s and 4.21 s" (★C10): one run each, on an 8 GB Mac whose load is not given, with patched code. There is no
  repeat and no time for the rule off.
- "40 by 30 surface", "pitch 9.6 px": holes and Wokwi px. Whether the FIT0193 is anything like 40 by 30 is H (PA-5:
  at most 39 pitches on 100 mm).
- "about three months" (A1): no source (PA-9 says "a few").
- "six weeks apart" (★C1): 10-16 to 11-26 is 41 days. The two dates are two different wants, not one want said twice.
- "26 × 18 holes" (Perfboard.dc.html:58) against "27 × 19" (:200, :206) in the same artboard. ★C6 quotes one.
- "6 pitches" (D-q4 (b), TL2-9, "1.1 and 7.1"), "R1 spans 6 holes" (UL-7, user.md:69) and "4 pitches" (TL2-9) mix
  holes and pitches. 6 holes is 5 pitches.
- "60000" (A5, the budget): states per search (wire_routing.py:207, :245). A5 says "each under 60000 states" with no
  scope (per search or the total `expanded`).
- "9 of 9", "8 of 9" goldens: 3 of the 9 are 2-line refusals and 1 draws nothing, so at most 5 pin a route.
- "drawing.py under 560 lines" (items.md): no source. Lines 543-599 (the renderer and `_round_px`) out gives about 542.
- "50 mm of 24 AWG drops 6.2 mV at 1.5 A": 1.5 A is the FireBeetle regulator's stated rating, marked unverified, not a
  measured net current. It is an upper bound, not the clock's draw.
- "10 H" (Stands on): ten assumptions, none rated. "of which would change the decision: —".
- "0 joints in a wrong hole of all the joints of button-light" (A3): the count of joints is not given.
- "3 of 3 requests ... to a fresh Claude" (A8): which model and which requests are not named, n = 3.
- "in the week after" (A10): after what event is not named.
- "a typical female header is 8.5 mm" (TL2-7): H, not read.
- "the 15 walk projects" (★C4): I counted 15 folders in ~/Development/spark-walks, so that holds.

## What I could not check

- The request of 2026-11-28 verbatim: it was relayed by spark-artifact, and I have no transcript.
- The tech lead's in-memory trial (★C10): it was removed, and I ran no code that imports spark (no test slot, and the
  tree must stay clean).
- The FIT0193's pitch, pads and grid (A7): my one fetch of a guessed DFRobot URL returned another product (TEL0078).
  No fact was read.
- Perfboard Designer's licence and code (C24): the page says "open source" and names no licence.
- Whether moves 2 to 4 keep `cut_short`: P1350's branch was not read, and no tests were run.
- The canvas as rendered: I read only the text of the store's copy. The user lens read "the session's scratchpad
  copy". The lines I checked matched.
- The DigiKey, Instructables and Hackaday sources of #311 note 3: no fetches left.

## Searches

1. Fetch https://perfboarddesigner.com/learn/perfboard-wiring/ · checks ★C16 and C24 · used: all four quotes found, no licence named.
2. Fetch https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html · checks ★C17 · used: the quote and the section's scope.
3. Fetch https://www.dfrobot.com/product-1094.html · meant to check ★C5 and A7 (the FIT0193's pitch and pads) · not used: the page is TEL0078, a WiFi shield. A wrong URL on my part.
