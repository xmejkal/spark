A placeholder board record: "Any ESP32-S3 dev board (placeholder)", the S3's chip and Wokwi stand-in, six GPIOs, two
power pads, and `physical: {}`. From P158's part 2 (#94), the A3 approach's run 1.

What the baseline of 2026-10-11 recorded: `boards.py --validate` ok, exit 0; `--validate --for-fab` exit 1, naming
`footprint_module` and `footprint_export`; the chain stops at the schematic, could-not-run, exit 2 ("this board has no
verified footprint"). The only word "placeholder" in any of it is the one in the record's name.
