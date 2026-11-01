# Checks

Step 5 of 8 in [the journey](../journey.md). Next: [Firmware](firmware.md).

**One board per project.** Since 2026-10-19 ([P223](https://github.com/xmejkal/spark/issues/205)) a folder with two
built designs, such as `dist/car/` and `dist/remote/`, gets a reason instead of a silent stop: spark handles one board
per project today. The reason names the first design's absolute path for `--circuit`, or tells you to give each board
its own folder with its own `parts/` and to run init in it. Many boards in one project come with v0.13
([#94](https://github.com/xmejkal/spark/issues/94)).

**Works.** After a build, running init again with `--force` names the rails from the board. It lists the fields it
writes as `null`. Until a bug is fixed, it lists them even when `.spark/rules.json` already holds your answer
([P114](https://github.com/xmejkal/spark/issues/48)), so the values in that file are what count:

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/init_project.py" --project . --board firebeetle2-esp32s3 --force
```

<!-- output: run 2026-10-05, spark 0.6.0 -->
```text
spark init in my-gadget
  on your projects list as 'my-gadget'
  merged into rules.json — every answer already in it was kept
  wrote project.json
  package.json already exists, left alone
  wrote active.json
  named 3 rail(s) from circuit.json

17 field(s) nobody has answered. Nothing here is guessed, and a check reading a null
reports it as unverifiable rather than passing it:

  rules.json  physics.i2c_hz
  rules.json  physics.i2c_bus_capacitance_pf
  rules.json  physics.rails.GND.nominal_volts
  rules.json  physics.rails.GND.max_current_a
  rules.json  physics.rails.GND.capacitor_chemistry
  rules.json  physics.rails.GND.served_by_pour
  rules.json  physics.rails.MOTOR6V.nominal_volts
  rules.json  physics.rails.MOTOR6V.max_current_a
  rules.json  physics.rails.MOTOR6V.capacitor_chemistry
  rules.json  physics.rails.MOTOR6V.served_by_pour
  rules.json  physics.rails.V33.nominal_volts
  rules.json  physics.rails.V33.max_current_a
  rules.json  physics.rails.V33.capacitor_chemistry
  rules.json  physics.rails.V33.served_by_pour
  project.json  goal
  project.json  prefer
  project.json  sellers
```

Its last sentence overclaims here too, as above. The motor rail's net is named `MOTOR6V` whatever the motor's voltage
([P129](https://github.com/xmejkal/spark/issues/63)). A part's `rails` puts its pin on a rail you name instead.

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/check_all.py" --project .
```

The lines are a dated record, not today's output: the last line now ends in a count of the `?` lines, and the
four-resistor `!` line now names its cause (below).

<!-- output: run 2026-10-05, spark 0.6.0 -->
```text
  resolved from .:
    circuit      dist/board/circuit.json
    rules        .spark/rules.json
    package      not found (looked for *-gerbers.zip, fab/*.zip)
    boards       2 definition(s): firebeetle2-esp32s3, xiao-esp32-c6

  [ok  ] vendor-truth       the board definition matches the vendor's own pin header
  [ok  ] buildability       holes take their pins, packages hold their values
           ? JstPh2PowerInlet: pad 1.20 mm around a 0.75 mm hole leaves 0.225 mm of ring: over the 0.18 mm this process can make, under the 0.25 mm it recommends
  [--  ] the-order          the fab package orders the parts the schematic specifies
  [????] physics            the board obeys physics, not just itself
           ! MOTOR6V: draws at least 0 mA; not stated: L9110sModule.VCC: names no fact for its current; JstPh2PowerInlet.VCC: names no fact for its current
           ! 4 resistor(s): could not be assessed: BtnModePullupA, BtnOpenPullupA, L9110sModulePulldownAIA, L9110sModulePulldownAIB. A netlist records neither the current through a resistor nor the voltage across it, and both depend on topology the design does not state
           ? V33: draws 355 mA of 1.50 A, resting on figures nobody has verified: Mcu.3V3: regulator_3v3_a
           ? GND: no maximum current stated, so nothing here can be verified
           ? MOTOR6V: no maximum current stated, so nothing here can be verified; the part records leave it open: L9110sModule.VCC
  [ok  ] rules-vs-netlist   written rules hold in the design that was built

  1 check(s) could not look: physics
  1 not asked for: the-order
  nothing found by the 3 check(s) that completed, of 5
```

Every check ends in one of three outcomes, and `check_all` adds a fourth word, `skipped`
([the glossary](../../../GLOSSARY.md#the-three-outcomes--ok-problems-could-not-run)).
[`check_all.py`](../../../scripts/check_all.py) prints each as a tag:

- `[ok  ]` is ok: it looked and found nothing.
- `[FAIL]` is problems, each on a `-` line.
- `[????]` is could-not-run, and each `!` line says what it could not check.
- `[--  ]` is skipped: it was [never asked](../../../GLOSSARY.md#skipped--the-fourth-word-and-only-check_all-has-it).

`!` lines can also appear under `[FAIL]`: a check that found a problem may also have failed to look at something, and
problems outranks could-not-run. A `?` line is an
[advisory, or a value that needs measuring](../../../GLOSSARY.md#needs-measurement-and-advisory--findings-that-do-not-change-the-outcome).
It does not change the outcome. Today the last line ends `, resting on N ? line(s)` when N is above 0: how many `?`
lines the answer rests on.

**Here physics ends could-not-run, for two reasons:**

1. **What MOTOR6V draws.** The L9110S and power-inlet records name no current on their VCC pins
   ([P120](https://github.com/xmejkal/spark/issues/54)).
2. **The pull resistors.** The run above has four. Since P204 the buttons use the board's internal pull-up, so two
   remain, the L9110S's pull-downs. Nothing clears them, because MOTOR6V states no voltage: its `nominal_volts` is
   `null`. State `6.0` there and they clear (6² / 10k = 3.6 mW), with no current stated.

What clears each, and its shape, is in [what never to assume](../agents/never-assume.md)
([P118](https://github.com/xmejkal/spark/issues/52)).

Of the 12 rail values init left null, three show: GND's and MOTOR6V's `max_current_a` as `?` lines, and MOTOR6V's
`nominal_volts` in the resistors' `!` line.

- V33's is taken from the part records' sum (355 mA), so it shows nothing of its own. V33's `?` line is about its
  supply, the dev board's unverified 1.50 A.
- The other eight print nothing. A null `served_by_pour` is read as false. `capacitor_chemistry` is read only for
  capacitors, and this board has none. V33's `nominal_volts` is not needed, because the FireBeetle's 3V3 pad states
  3.3 V, and GND's is 0 V by definition.

The run exits 2, could-not-run, because physics could not look. Once a rail's `max_current_a` is stated, delete
`board.tsx` and run `/spark:build` again, so the generator sizes that rail's traces.

**`[--  ]` the-order: no fab package yet.** That is the zip of Gerbers and bill of materials a board house takes. The
`spark-design` skill tells Claude to make no Gerbers while anything load-bearing is unverified; nothing in code stops
the export. [From draft to order](from-draft-to-order.md#from-draft-to-order) makes one, and the-order then reads it.

**check_all is not the whole answer.** For this board, `parts.py --show` names a CONFLICT on AIA and AIB that no check
reports ([P109](https://github.com/xmejkal/spark/issues/43)). The board's 10 kΩ pull-downs against the module's own
10 kΩ pull-ups hold both inputs HIGH at idle on a supply above 5 V. The facts it rests on are verified, so it answers
`problems`, exit 1 ([P124](https://github.com/xmejkal/spark/issues/58)):

<!-- runs: exit 1 -->
```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --show l9110s-module --project .
```

<!-- output: run 2026-10-11, spark 0.8.1 -->
```text
L9110S dual motor driver module — motor-driver

  asks the host for:
    MOTOR_IA     -> module pin AIA
    MOTOR_IB     -> module pin AIB

  known:
    input_high_threshold_v       2.5        verified
    continuous_current_a         0.8        verified
    supply_range_v               [2.5, 12.0] verified
    has_enable_pin               False      verified
    onboard_input_pullups_ohms   10000      verified
    schematic_numbers_vcc_and_gnd_opposite_to_the_silkscreen True       verified

  the board must: Pull both inputs down in HARDWARE. The host's pins float for the ~300 ms between reset and firmware, and through any crash or reflash, and a floating CMOS input on an H-bridge can turn both halves on.

  the board must: If a current shunt sits in this module's ground return, the module judges its inputs against ITS OWN ground, which the shunt lifts. Effective input high becomes (host logic level - I x R_shunt), and the margin over 2.5 V is what decides whether the motor turns under load.

  CONFLICT: AIA: the board's 10000 ohm pull-down against the module's own 10000 ohm pull-up to its supply holds the pin at 0.5 of the supply (1.25 V to 6 V over its 2.5-12 V range), so it idles HIGH, not low, on any supply above 5 V (input-high threshold 2.5 V); the module's input-low threshold is not recorded, so below that the level is undefined

  CONFLICT: AIB: the board's 10000 ohm pull-down against the module's own 10000 ohm pull-up to its supply holds the pin at 0.5 of the supply (1.25 V to 6 V over its 2.5-12 V range), so it idles HIGH, not low, on any supply above 5 V (input-high threshold 2.5 V); the module's input-low threshold is not recorded, so below that the level is undefined
  fix for l9110s-module.AIA: record the module's input_low_threshold_v, the level it reads as low, then run --show again: held only under the input-high threshold, the level is undefined
  fix for l9110s-module.AIB: record the module's input_low_threshold_v, the level it reads as low, then run --show again: held only under the input-high threshold, the level is undefined
```

The next steps are the [firmware](firmware.md#firmware), which imports `pins.py`, and the [simulation](simulate.md#simulate).

**Today, in full.** `check_all.py` runs spark's deterministic checks in one command, five in the run above. A fresh
button-and-LED project exits 0 and counts its `?` lines ([P197](https://github.com/xmejkal/spark/issues/156)). `check_all.py` does not run the
generator's CONFLICT test or the gate's two commands. Before a board is ordered, the `spark-review` skill runs
`check_all`, then the reviewer agents, then the fabrication gate. It was not run here.
[Is it ready?](../agents.md#is-it-ready) says what each part covers.

**A board you wrote by hand** in tscircuit is read the same way: `npx --no tsci build board.tsx`, then `/spark:init` so
that it names the rails, then `check_all.py --project .`. This was not run here. A project's own
[`make check`](../../../GLOSSARY.md#make-check--a-projects-own-gate) can run the checks one by one.
