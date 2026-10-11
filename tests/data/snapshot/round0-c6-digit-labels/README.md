Round 0's first version of the C6 record, with its pads labelled by bare GPIO numbers, as the board's silkscreen
prints them (P100, #6, 2026-10-09).

What the baseline of 2026-10-11 recorded: both validations ok, exit 0; the chain stops at the build, exit 1, on "a
terminal connected to nothing". What it does not say: tscircuit read the bare numbers as pin numbers and joined 3V3 to
the pad printed "17" and GND1 to the one printed "15". A short that no check names (P158's CH-12, #94).
