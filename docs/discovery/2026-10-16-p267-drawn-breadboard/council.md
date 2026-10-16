# P267 plan council, 2026-10-16

The short version: two rounds ran on the plan for a drawn breadboard in Wokwi. They moved the drawing onto the XIAO
C6, added rotation, made the breadboard a cited record, and split the design into a pure planner and a renderer.
The plan in `plan.md` holds every fix.

## Research (a Plan agent, Sonnet)

Wokwi publishes the pin offsets of `board-xiao-esp32-c6` (wokwi-boards, board.json, in mm, 2.54 mm pitch, the two
columns 15.0765 mm apart) and of `wokwi-led`, `wokwi-pushbutton` and `wokwi-resistor` (wokwi-elements). Each lies
within about 1.2 px of the 9.6 px grid. Wokwi publishes no hole positions for its breadboard, and no source says
whether a leg over a hole connects. The lint gives only the hole names (`{1-63}{t|b}.{a-j}`, `tp/tn/bp/bn.{1-50}`).

## Round 1

- Architecture and names lens (Sonnet): the layout must not decide the wiring again, so each anchor says its seat;
  "footprint" clashes with the KiCad footprint; facts belong in the existing Wokwi blocks; a first slice end to end.
- Refuter (Opus): the button-light fixture is on the FireBeetle, not the XIAO; the board and the button must turn 90
  degrees or their pins share one row; the board has two sizes on record; diagram.json holds no hole positions, so
  the measurement works back from parts dropped into holes; the LED's anode is at x=25 and the cathode at x=15.

## Round 2

- PO-assistant (Sonnet): name the person and the moment; the first PR is the true first slice; say how the file
  is opened; the sheet points to the drawing; the Miro ask becomes a later card.
- Tech lead (Opus): a pure `BreadboardPlanner` gives a `BreadboardLayout` that any renderer reads; split the row
  holder into `HoleLedger`, a `PartPlacement` strategy and a `Breadboard` record; `Anchor.seat()` returns a value;
  one renderer interface.
- Senior (Sonnet): the row-or-rail rule must live in one place; several GND pads give one rail; rotation turns about
  the center, so round once; a resistor's legs need two rows; the button's joined pins; the half board runs out of
  columns; byte-identical output; the supply step draws no wire.
