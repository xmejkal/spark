Round 0's first version of the C6 record, with its pads labelled by bare GPIO numbers, as the board's silkscreen
prints them (P100, #6, 2026-10-09).

What the baseline of 2026-10-11 recorded: both validations ok, exit 0; the chain stops at the build, exit 1, on "a
terminal connected to nothing". What it does not say, and round 0 found in the circuit file: the 3V3 trace landed on
pin 17 and GND1's on pin 15, because tscircuit read the bare numbers as pin positions and merged pads. A short that no
check names (P158's CH-12, #94).
