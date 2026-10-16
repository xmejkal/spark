# P269 council: the refuter (Opus), 2026-10-16

Read on branch `p269-discovery` at 079c985. Read-only, except this file. Experiments ran in the session scratchpad.
Start: existing product (spark, with P267's drawn breadboard merged). Decider is the only user, n = 1.

## Check first: the existing product

- **Does the change address the observed problem?** The one documented harm is edit loss: "a change you make to it
  in Wokwi is lost at the next build" (docs/guide/journey.md:448-449). The brief answers it with "a merge rule like
  `merge.ts`" (★C5, the spike). That rule does not run in spark's build today (point ★C5 below), and its premise does
  not hold on a breadboard. merge.ts says "The generator owns *what is connected to what*. A person owns *what it looks
  like*" (tools/circuit-to-wokwi/lib/merge.ts:4-5). On a breadboard where a part sits *is* what it connects to: "A leg
  over a hole connects in Wokwi with no connection entry" (scripts/breadboard_drawing.py:7-8). So the observed problem
  is not addressed by the reuse the brief proposes.
- **No observed use to address.** No logged run shows the PO opening `breadboard.json`. The demo project he owns,
  ~/Development/button-light, has no `breadboard.json` at all: `ls` shows `breadboard.md` dated Oct 13 16:25 and a
  `dist/board/circuit.json` of the same time, before P267 merged on 10-16. USER-13 says the same in words.
- **What breaks for current users.** (1) S0 promises "`breadboard.json` keeps its sha256 for button-light" (items.md
  S0). No such file or golden exists: neither in the demo project nor in tests/data/breadboard/ (only
  `motor/breadboard.expected.md`). The baseline must be made first, and AGENTS.md says "A spark change does not update
  the demo projects". (2) Keeping edits reverses a written rule: "an old drawing describes another build: never leave
  it beside a new sheet" (scripts/breadboard.py:432). journey.md:448-449 and agents.md then become untrue in the same
  PR. (3) The "must not get worse" list omits `sim/diagram.json`, which `keep_simulation` copies over the kept one at
  every build (scripts/check_spine.py:841).
- **Confirmation bias, the team standing in for the user.**
  - Q10's first question presupposes an act with no record: "When you opened `breadboard.json` in Wokwi on
    2026-10-16, did you move anything" (council/user.md Q-a). It leads him to say yes.
  - A3's pass line is "he says he wired from the picture", and A4's is "he names a board in his drawer and a project
    for it" (risks-and-tests.md). Both are his own say-so, and both are about his own wish. A4 passes by naming
    anything.
  - USER-25 says of its first-slice criteria "(b) to (e) are mine, not his". The brief keeps the lens's view as an
    option and drops that caveat.
  - The brief's "already decided" list (D-e) quotes four AGENTS.md principles. It leaves out the first one, which
    cuts against the request: "Judge a change by one bar: does it move a basic project closer to a breadboard with
    working firmware? ... Pause tooling that does not serve this bar." PO-27 raised this, and the brief dropped it.
    VISION.md:38 says the hobbyist has "no EDA, maybe no meter", and VISION.md:41 says "real layout is out". A
    multi-stage editor with schematic and PCB tabs moves toward EDA. The brief never names this tension.
  - The README's journey still says "Its breadboard is not wired yet" (USER, README.md:83). The bar's next step,
    wiring the real breadboard once, is not on the slice list. That is the cheapest test of A3, and it costs no code.

## 1. The ★ claims

- **★C1** · read scripts/breadboard_drawing.py:22-24: "Value: one hole, its Wokwi name (12t.a, tp.3), its center in px,
  and its row (the holes joined with it: 12t, or tp)." Also :29 `return int(self.row[:-1]) if self.row[-1] in "tb"
  else 0`, and :7-8 "A leg over a hole connects in Wokwi with no connection entry, so only the jumpers are
  connections." · **partly**. The code holds a join group (`row`), a hole ledger and jumpers. It holds no cut, no
  union-find over holes and no check. Its row logic parses Wokwi's names. TL-15 itself says a cut means "`JoinGroup`
  must be split at run time, which the breadboard never needed". TL-11 shows that the PCB uses SMD pads
  (`pcb_smtpad`), not holes, so "a PCB's free pads" fits a model "of holes" only by renaming.
  Change "Every stage fits one model ... The breadboard code already holds it under Wokwi names and in px" to
  "Breadboard, stripboard and perfboard can share one model of holes, join groups, legs and connections (H, the tech
  lead). The breadboard code holds its join groups and a hole ledger, but no cuts and no connectivity check. A PCB fits
  only as pads at free positions, and its routing stays with tscircuit."
- **★C2** · read data.md:9 "No record holds a pin position in mm". Then I read the records and the store.
  parts/jst-ph-2-power-inlet.json holds `facts.pitch_mm` {"value": 2.0, "verified": true}. In the store,
  shelf/dfr0831-buck-5v.json holds `header_column_pitch_mm` 2.8, `header_row_pitch_mm` 2.5 and
  `power_pad_spacing_x_mm` 25.1, with "pads at x = 2.9 and 28.0 mm from the left edge". shelf/ds3231-at24c32-rtc-module.json
  holds `header_pitch_mm` 2.54. The catalog's two screw terminals hold `pitch_mm`. data/wokwi-geometry.json:9-17 holds
  all 14 XIAO pin positions, from Wokwi's board.json in mm ("its mm times 96 / 25.4"). · **partly**. "No per-pin x, y"
  holds. "A part has `pin_order` and a footprint name only, and only the FireBeetle board record holds header geometry"
  is refuted. Change it to "No record holds a per-pin x, y in mm. Some records hold a pitch or pad spacing (jst-ph-2,
  dfr0831, ds3231, two terminals), the FireBeetle holds a full header block, and the XIAO's pins exist in mm only in
  Wokwi's board.json (data/wokwi-geometry.json)."
- **★C3** · read tech-lead.md:198-202 and :206-210. I reproduced it. The local circuit-to-svg 0.0.424
  (smartbin-local/node_modules, `"license": "ISC"` in its package.json) ran in Node on
  ~/Development/button-light/dist/board/circuit.json. `convertCircuitJsonToSchematicSvg` gave 70368 characters and
  `convertCircuitJsonToPcbSvg` gave 151265. The element counts match TL-8: schematic_component 4, schematic_trace 7,
  pcb_component 4, pcb_plated_hole 20, pcb_trace 5, pcb_board 47 x 33, and 2 `pcb_smtpad` 0.8 x 0.95. The circuit also
  carries "No <schematicsheet> was found" and "Mcu has no courtyard". · **holds**, for Node. It runs in Node. That it
  runs in a browser bundle is not shown, and I did not view the SVGs, so A6 (readable) is open. Add "licence ISC" and
  "shown in Node, not in a browser".
- **★C4** · read tools/circuit-to-wokwi/ARCHITECTURE.md:50-53: "re-deriving nets from traces by hand would be a second
  implementation that can disagree with the first. It is never done here." Read scripts/breadboard.py:92-93: "netlist.py
  keeps a pin-to-pin trace's net apart from a named one on purpose; a breadboard row does not". Read scripts/netlist.py:4-6
  ("There were three walks over `circuit.json` ... they gave three different answers") and :25-27 ("making it
  transitive is a change with its own consequences, not a tidy-up"). · **partly**. There are three walks, not two:
  netlist.py (not transitive, on purpose), breadboard.py `points()` (transitive, on purpose), and the converter's map.
  "Here" in the quote means the converter, and it calls nothing in breadboard.py a defect. netlist.py:16-18 also warns
  that grouping by `subcircuit_connectivity_map_key` "join[s] every one of them into a single phantom net". That is the
  risk if "one source" means the converter's map. Change it to "spark walks the circuit three ways, and two differ on
  purpose (netlist.py:25-27, breadboard.py:92-93). One `Circuit` source must choose which meaning each stage needs."
  The caveat "none" is wrong.
- **★C5** · read merge.ts:9-10: "positions, rotations and wire routes are carried over from the existing file by part
  id". Read tools/circuit-to-wokwi/cli.ts:85-86: `readExisting(options.out)`, then `mergeWithExisting`. Read
  scripts/check_spine.py:658 `workdir = Path(tempfile.mkdtemp(prefix="spark-spine-"))`, :489 `sim_dir = workdir / "sim"`,
  :498 `diagram_path = sim_dir / "diagram.json"`, and :841 `shutil.copytree(workdir / "sim", destination,
  dirs_exist_ok=True)`. · **refuted** in its first half. In spark's build the converter writes into a new temporary
  folder, so `readExisting` finds no file and merge.ts keeps nothing. Then the copy overwrites the person's kept
  `diagram.json`. The second half, `write()` rewrites `breadboard.json` and unlinks it on `NotDrawn`, holds
  (breadboard.py:424-433). Also, merge.ts matches a wire by its two ends (merge.ts:82-90), so a jumper moved to other
  holes has new ends and is replaced with no name given. `MergeSummary` holds counts only (merge.ts:18-22). The spike's
  pass line "survives or is reported by name" therefore fails by construction for "a moved jumper", without running
  it. Change it to "merge.ts can keep positions in `diagram.json` when the converter runs on an existing file. spark's
  build never does that (a fresh temporary folder, then a copy over the kept file), so edits are lost there too. On a
  breadboard a position is a connection, so merge.ts's 'you own what it looks like' rule does not carry over."
- **★C6** · read po-assistant.md:36: "Who is blocked now: no one." Read the cited scrum/VISION.md:43: "**What would
  change this page:** the real outsider (slice 5) who meets their goal with a breadboard ...". · **partly**. The
  pointer is wrong: "Hypothesis" is at VISION.md:38. "Nobody is blocked" leaves out that P268 (#302) is blocked by this
  discovery, by D-a. Change the pointer to VISION.md:38, and add "except P268, held for this discovery by D-a".
- **★C7** · I opened the primary sources the caveat says were not opened. fritzing-parts LICENSE.txt: "All graphics
  and documentation of Fritzing are licensed under Creative Commons Attribution-ShareALike 3.0 Unported."
  wokwi-elements LICENSE: "The MIT License (MIT)", "Copyright (c) 2020 Uri Shaked". VeroRoute on SourceForge: "GNU
  General Public License version 3.0 (GPLv3)". wokwi/wokwi-boards: `gh api repos/wokwi/wokwi-boards` gives license
  null, and its top level holds only .github, .gitignore, .vscode, README.md, boards and tools: no LICENSE file. ·
  **holds** for the three named. It **omits** wokwi-boards. The XIAO's board drawing (`board.svg`) is there, with no
  licence grant, so the default is all rights reserved. spark reads numbers from it (data/wokwi-geometry.json:9),
  which is a different matter from copying the art. Add: "wokwi-boards, where the board drawings live, states no
  licence: its art is not reusable." Drop the caveat about the Fritzing file, which now holds.

Not ★ but checked:
- **C8** · the Artifact limits are cited to "the Artifact tool's description in this session" (TL-19). That tool is
  not in my session · **could not open**.
- **C9** · read data/wokwi-geometry.json:8: "Its 18.1 x 23.4 mm is drawn as 68 x 88 px". The pins run down the long
  axis (D0 to D6 at x 5.418, y 18.6 to 76.2), so Wokwi draws the board upright, while the record gives width 21.0 and
  height 17.8 (boards/xiao-esp32-c6.json:23-24). · **partly**. Turned to match, the sizes are 17.8 against 18.1 and
  21.0 against 23.4. One axis agrees within 0.3 mm. The other differs by 2.4 mm, which the overhang may explain. The
  brief's sentence reads as a disagreement on both axes. Say "after turning, 17.8 against 18.1 mm and 21.0 against
  23.4 mm (the USB overhang)".
- **C10** · re-ran TL-33's grep `'"[a-z_]*_m[aA]"'`: 5 hits, as claimed. The pattern misses `_a` fields:
  parts/l9110s-module.json:57 `continuous_current_a` {"value": 0.8, "verified": true}, and
  boards/firebeetle2-esp32s3.json:371 `charge_current_a` 1.0. The store has 27 files with a current field (for example
  6 `output_current_a`, 6 `operating_current_ma`). · **refuted** for "records hold 5 current fields in all", and for
  TL-33's "none for the L9110S motor channel". The no-go "no current or heat check on a perfboard until records hold
  the currents" rests on that count. Change it to "at least 7 current fields in the repository's records, among them
  the L9110S's 0.8 A per channel, verified, and more in the store".
- **C11** · docs.wokwi.com/diagram-format, first sentence: "Each simulation project contains a diagram.json file." It
  mentions no schematic or PCB · **holds**, narrowly. A page about a file format is weak evidence about the editor's
  views. PO-18 says the opposite ("Wokwi shows breadboard, PCB and schematic as separate views", with no source). The
  brief does not record this split.

## 2. The brief against its detail

- **Frame, D-e.** It leaves out AGENTS.md's first principle (the one bar, "pause tooling that does not serve this
  bar"), which PO-27 raised. It also leaves out "Plans shrink with distance". The items list S0 to S8 at one level of
  detail.
- **Outcome.** "P268's SVG of button-light". The demo project's build predates P267 and AGENTS.md forbids a spark
  change to rebuild it. Name the fixture (tests/data/breadboard/button-light-xiao) or the rebuild.
- **★C3.** TL-10's caveat "Its license and whether it runs in a browser bundle were not on the page" was dropped. I
  settled the licence (ISC) and Node. The browser is still open.
- **★C5.** PO-8's caveat "I did not check whether merge applies to `breadboard.json`" became "merge.ts was not tried on
  breadboard.json". The stronger fact, that merge.ts never runs in spark's own build, was not found by anyone.
- **★C7.** DATA-20 said "wokwi-boards licence — not seen". The brief drops wokwi-boards entirely.
- **Options, Q2.** The first option is credited to "the tech lead, the PO assistant". The PO assistant did not propose
  S0 first. It said "the smallest end-to-end slice is already specified" (P268, PO-35) and "slice order should put the
  bar first" (PO-27). TL's own Q-G asks whether S0 to S2 go inside P268. That is stronger than either source.
- **Options, Q2, "a perfboard first · opinion (none of the lenses)".** USER-25 asks for "the same circuit in at least
  two stages (breadboard and one of perfboard or stripboard)" in the first slice. The user lens did hold that view.
  The "read-only viewer" option credited to the user lens is not what USER-25 asks for.
- **Options, Q3 VeroRoute.** The caveat "a second tool to install" drops two facts. SourceForge lists "Linux, Windows"
  and "Pre-compiled versions available for MS Windows and 64-bit Linux Mint 20.3", and the PO is on macOS. PO-15 also
  notes that VeroRoute imports a "TinyCAD, gEDA, or KiCad" netlist, which spark does not write.
- **Options, Q5 and Q6.** "Slower past a few thousand elements" and "a large download" are H with no benchmark
  (TL-21, TL-22, and TL's could-not-check list). The brief states them as caveats with no tag.
- **No-gos.** The no-go "until records hold the currents (C10)" rests on a refuted count (part 1, C10).
- **Riskiest assumption and its test.** The spike says "a merge rule like `merge.ts`". By part 1 ★C5, merge.ts reports
  counts, not names, and drops moved wires. The outcome is known before the spike runs. The test does not say how the
  edit enters the file either: wokwi.com does not write back to disk.
- **Found on the way, C12.** "The XIAO board record lacks the header facts". True of the record, but the pin
  positions exist in data/wokwi-geometry.json:9-17, from Wokwi's mm. The fix may be a copy with a cite, not a new
  measurement.
- **Risks, the firmware–hardware contract.** "E ★C4: two ways ... could draw a wire the firmware does not expect" is
  stronger than its source. No case of a wrong wire is shown, and the difference is on purpose (netlist.py:25-27).
- **verification.md** was still a template when the refuter read it, so nothing in the brief is verified yet.
- **jobs-and-journeys.md step 4**: "wires the breadboard and tests it · E P215 bench (the board flashed)". A flashed
  board is not a wired breadboard. README.md:83 says "Its breadboard is not wired yet".

## 3. Rival explanations not ruled out

- **★C1, one model fits all.** A union-find over sets fits anything, so "fits" proves little. The hard parts sit
  outside the shared part: cuts that change groups at run time (TL-15), a footprint per stage (TL-11), and Lee routing
  (TL-16).
- **★C2, records lack pin data, so a record change is needed.** The data is partly derivable already: tscircuit's
  `pcb_plated_hole` positions per footprint (TL-12), pitch fields, and Wokwi's board.json. The need may be a
  derivation, not new record fields.
- **★C4, two walks is a defect.** The walks differ on purpose, per stage meaning (breadboard.py:92-93,
  netlist.py:25-27). Merging them may break the checkers netlist.py was written to fix.
- **★C5 and A1, edit survival is the riskiest.** The rival is that value is the riskiest (A4): no logged use of any
  view, and no perfboard project named. Edit loss is a documented, known harm that nobody has hit in a log.
- **★C6, no one blocked, so it is a want.** The rival is that the request is the PO's own pull after seeing P267, so
  the signal is real for n = 1. Neither rules the other out. The cheapest separator is the breadboard he has not yet
  wired.
- **C9, two sizes.** The rival is that the drawing is turned 90 degrees and adds the USB overhang. That is close to one
  board, not two.
- **C10, no current data.** The rival is a grep pattern that misses `_a`.
- **C11, Wokwi has no schematic or PCB.** The rival is that the file-format page is the wrong source, and the editor
  may have them (PO-18, unsourced).

## 4. Numbers missing a unit, a population, a period or a provenance

- "11 H" (Stands on): what counts as H here, the 11 assumptions? No unit.
- "at most 16" searches: no period. Per discovery, or per lens? The lenses report 3 + 3 + 3 + 3 = 12 queries plus
  fetches, and nothing totals them against the 16.
- ★C7 and C8 "four CDNs": TL-19 lists five hosts (cdnjs, jsdelivr, unpkg, tailwindcss, jquery).
- C8 "16 MB": from a tool description, with no version or date of the tool.
- C10 "250 mA to 1 to 3 A": three products, three conditions (a strip, "an amp or 2" from a forum, 3 A for 85 mil at a
  10 °C rise). No track width or temperature rise in the brief.
- C10 "5 current fields": population (repository records only, `_ma` suffix only) unstated, and refuted.
- C9 "21.0 x 17.8" and "18.1 x 23.4": no orientation. The Wokwi size has a source; the record's has none cited.
- Q5 "a few thousand elements": no source, no browser, no benchmark.
- Q6 Pyodide "a large download" (TL-22 "about 10 MB or more"): model knowledge, no version.
- TL-21 "under about 50 parts and about 400 to 2000 holes": no source and no board named.
- The spike "two hours": no provenance.
- A5 "under an hour each", A10 "under 400 lines", A1 "3 of 3": set by the team, with no base rate. A10's 400 lines
  has no reference slice.
- TL-23 "about 30 lines": an estimate. Its anchor "breadboard.py's own is 15" is right only for lines 96-110 inclusive.
- The cost comment "6 agents, 499 calls and about 90M input tokens": one rehearsal (P900), no model named.

## Searches

- none · the decision it served: none, no web search run · not used. Page reads (WebFetch): raw.githubusercontent.com/fritzing/fritzing-parts/develop/LICENSE.txt ·
  raw.githubusercontent.com/wokwi/wokwi-elements/main/LICENSE · github.com/wokwi/wokwi-boards ·
  sourceforge.net/projects/veroroute/ · docs.wokwi.com/diagram-format. Plus `gh api` for the licences of wokwi-boards,
  wokwi-elements, fritzing-parts and tscircuit/circuit-to-svg.
Not checked: C8 (the Artifact tool is not in my session), circuit-to-svg in a browser bundle, how the SVGs look,
  whether Wokwi's editor has schematic or PCB views (not opened), whether a project board id (`xiao-esp32-c6-fresh`)
  is drawn by P267's code.

## Second pass, 2026-10-16

Scope: the sections changed by 8b7de81 only (brief.md header, Riskiest, Test, Questions, D2 to D9, Hand-off;
jobs-and-journeys.md Jobs; risks-and-tests.md ratings and Results; items.md).

### 2. Summaries against their sources

- A3 retired (risks-and-tests.md Results, brief.md Riskiest): the pass line set before the result is "he says he
  wired from the picture". D4's source is "The picture", an answer to which he *would* look at most. That is intent,
  not use; the Results row itself says "not of use", then marks the line met. The brief's own Test row keeps the real
  line open ("he wires button-light from the picture"). Stronger than its source. Fix: A3 open, rated high, test = P268.
- Riskiest names A3 (retired) while Stands on names A1 as the one high open assumption. The riskiest should be the
  open high one, A1, with its test.
- D9 "supersedes D2 for step 5": the quote is "3 yes, and it should stay where we move it". It does not mention a
  rebuild; D2 asked about a rebuild. The supersession is an inference, unmarked. Also items.md Step 5 still cites
  "D2: a lost move is annoying", not D9, and the Test row says the edit spike is "dropped by D2" while A1's row and
  the Collection plan (row "Do edits survive a rebuild?") still point to that spike. Either D9 revives the spike for
  step 5's plan, or A1 has no test. Dropped caveat: A1's rating rests on one reading of one phrase.
- A5, A6, A8, A9, A10 rated "low D8": D8 says only that these "are checked in each step's own plan"; it rates none.
  The template says Stands on is "—" while any is unrated. Stronger than the source; Stands on should be "10 H, —".
- "Ready for: design" needs the frame (D1), the jobs (D9), a direction (D8) and the remaining risk accepted. D8 says
  "the remaining risk" in the summary, but its quote is "Yes, this order", and A1 rose to high after D8, in D9. The
  acceptance of risk predates the new high. Design for steps 1 to 4 follows; for step 5 it does not.
- J1 dropped (D9), yet Hand-off's success proof (step 2: "he wires from it") and A3 are J1's own "so I can wire it
  from a picture". The quote drops "see it on my real board" and keeps "parts should have pictures, photos". The
  picture slice now serves J5/J7, and its proof still serves the dropped J1. story-map.md still tags S0, S1, S3 J1,
  and Today they… still has a J1 row.
- Items against D8: D8's step 8 is sharing; items.md's "Step 8" is the Fusion export (D9 says "after step 7"), so two
  things are step 8. Name it step 9, or J8. Step 8's "depends on: step 3" disagrees with D9's "after step 7". Steps
  1 to 7 match D8's order; 6 split into 6a/6b is not in D8 (fine, but unmarked). Slices "9 An enclosure" and
  "7 Perfboard to PCB" exist on the board (checked with gh).
- Q10 "answered in part by D2 to D5; the rest dropped": no D drops it. Dropped caveat: the account questions were the
  only past-tense evidence (n = 1); now all value evidence is intent.

### 3. Strongest rival explanation not ruled out

"It should stay where we move it" means the editor holds a part where it is dropped (no snap back, saved with the
file), not that it survives a rebuild from changed requirements. Under this reading D2 stands, A1 stays low, and
step 5 needs only save and load. One question to the PO separates the two.

### 4. Numbers without unit, population, period or provenance

- "10 H, 1 of which": population is the open rows of risks-and-tests.md; fine, but it counts A3 as retired (above).
- `cf3f8e53…` (items.md Step 1): no file path, no command, no commit; no `breadboard.json` is in the tree and the
  hash appears nowhere else in the repository.
- "n = 1" for A3: right population, but the period and the kind (one multiple-choice answer, intent) are the evidence.
- "ten items": counted, correct (nine steps and one chore).

Searches: none · the decision it served: none · not used. One `gh project field-list` for the Slice options.
Not checked: the session's AskUserQuestion transcript; the D quotes are taken as written in brief.md.
