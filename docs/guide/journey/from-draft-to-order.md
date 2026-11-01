# From draft to order

The steps of [the journey](../journey.md) share this page.

Ordering a board of modules is an optional step of the journey, after the firmware works: a later version
([VISION.md's *Versions*](../../../scrum/VISION.md#versions)), not designed yet. The generated board is a draft, and the header of
`board.tsx` says so: its modules sit in a column that does not overlap, it has no mounting holes or connector keying,
and its traces are not sized for current until each rail's current is stated. What exists today, in order:

1. **Look at it** in tscircuit's viewer: [see it](../../../commands/build.md#see-it).
2. **State each rail's current,** as `max_current_a` in `.spark/rules.json` or as figures in the part records. The
   generator sizes a rail's traces from it.
3. **Generate the board again.** Delete `board.tsx` and run `/spark:build`, because an existing `board.tsx` is never
   overwritten. If you have already laid it out, move it aside first and carry the new trace widths over by hand.
4. **Lay it out, then build your own `board.tsx`:** `npx --no tsci build board.tsx`. The `spark-design` skill's
   [layout notes](../../../skills/spark-design/references/pcb-layout.md) name the routes; they were not run for these docs.
   Until [P110](https://github.com/xmejkal/spark/issues/44) lands, `/spark:build` rebuilds `dist/`, which every check
   reads, from the requirements file, not from your `board.tsx`.
5. **Run the `spark-review` skill:** its reviewer agents, then the fabrication gate
   ([is it ready?](../agents.md#is-it-ready)).
   - The gate's `boards.py --validate --for-fab` refuses a dev-board definition that breaks its contract or names no
     footprint.
   - `parts.py --unverified` lists the unverified facts and pin orders of the parts you name
     ([its output on this example](../commands.md#skills)).
   - Neither reads the generated board, or lists the dev board's own unverified figures
     ([P126](https://github.com/xmejkal/spark/issues/60)).
6. **A design-rule check, if you have KiCad.** No check here is one, and tscircuit's autorouter can emit shorts (the
   layout notes say so). The build stage stops on any error tscircuit writes into `circuit.json`, on a component that
   shares no net with the supplies, and on a board with no traces; buildability checks each hole against the process.
   Nothing here measures the spacing between nets. Export the board, then run `kicad-cli pcb drc board.kicad_pcb`. The
   export ran here; `kicad-cli` was not installed, so the check did not:

```sh
npx --no tsci export board.tsx -f kicad_pcb -o board.kicad_pcb
```

<!-- output: run 2026-10-06, spark 0.6.0 -->
```text
Exported to board.kicad_pcb!
```

7. **Have a person look at the layout.**
8. **The fab package:**

```sh
npx --no tsci export board.tsx -f gerbers -o board-gerbers.zip
```

<!-- output: run 2026-10-06, spark 0.6.0 -->
```text
Mcu: cannot verify jlcpcb pick-and-place rotation (missing_pin1_location); PCB rotation 0 is unverified.
L9110sModule: cannot verify jlcpcb pick-and-place rotation (missing_pin1_location); PCB rotation 0 is unverified.
JstPh2PowerInlet: cannot verify jlcpcb pick-and-place rotation (missing_supplier_pin1_location); PCB rotation 0 is unverified.
BtnOpen: cannot verify jlcpcb pick-and-place rotation (missing_supplier_pin1_location); PCB rotation 0 is unverified.
BtnMode: cannot verify jlcpcb pick-and-place rotation (missing_supplier_pin1_location); PCB rotation 0 is unverified.
Exported to board-gerbers.zip!
```

This export was made for these docs, on the draft, with five facts about its parts still unverified (the gate's
`parts.py --unverified` lists them: [its output](../commands.md#skills)): the skill would not have made it, and nothing in
code stopped it. The five "cannot verify jlcpcb
pick-and-place rotation" lines are the five parts with no JLCPCB part number.

The bill of materials inside gives no part number for the dev board, the motor driver, the inlet or the buttons, and
no footprint for the dev board. Only the four 10 kΩ resistors carry a JLCPCB part number:

```sh
unzip -p board-gerbers.zip bom.csv
```

<!-- output: run 2026-10-06, spark 0.6.0 -->
```text
"Designator","Comment","Value","Footprint","JLCPCB Part #"
"Mcu","",""," ",
"L9110sModule","","","headermodule6",""
"JstPh2PowerInlet","","","jst_ph_2",""
"BtnOpen","","","pushbutton",""
"BtnMode","","","pushbutton",""
"L9110sModulePulldownAIA","10k","10k","res0603","C25804"
"L9110sModulePulldownAIB","10k","10k","res0603","C25804"
"BtnOpenPullupA","10k","10k","res0603","C25804"
"BtnModePullupA","10k","10k","res0603","C25804"
```

With the package in the project, `check_all` finds it and the-order answers `[ok  ]`:

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/check_all.py" --project .
```

A dated record again: today's last line also counts the `?` lines.

<!-- output: run 2026-10-06, spark 0.6.0 -->
```text
  resolved from .:
    circuit      dist/board/circuit.json
    rules        .spark/rules.json
    package      board-gerbers.zip
    boards       2 definition(s): firebeetle2-esp32s3, xiao-esp32-c6

  [ok  ] vendor-truth       the board definition matches the vendor's own pin header
  [ok  ] buildability       holes take their pins, packages hold their values
           ? JstPh2PowerInlet: pad 1.20 mm around a 0.75 mm hole leaves 0.225 mm of ring: over the 0.18 mm this process can make, under the 0.25 mm it recommends
  [ok  ] the-order          the fab package orders the parts the schematic specifies
  [????] physics            the board obeys physics, not just itself
           ! MOTOR6V: draws at least 0 mA; not stated: L9110sModule.VCC: names no fact for its current; JstPh2PowerInlet.VCC: names no fact for its current
           ! 4 resistor(s): could not be assessed: BtnModePullupA, BtnOpenPullupA, L9110sModulePulldownAIA, L9110sModulePulldownAIB. A netlist records neither the current through a resistor nor the voltage across it, and both depend on topology the design does not state
           ? V33: draws 355 mA of 1.50 A, resting on figures nobody has verified: Mcu.3V3: regulator_3v3_a
           ? GND: no maximum current stated, so nothing here can be verified
           ? MOTOR6V: no maximum current stated, so nothing here can be verified; the part records leave it open: L9110sModule.VCC
  [ok  ] rules-vs-netlist   written rules hold in the design that was built

  1 check(s) could not look: physics
  nothing found by the 4 check(s) that completed, of 5
```
