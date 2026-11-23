A wake button on the DFRobot FireBeetle 2 ESP32-S3, built on 2026-11-23 for P960 (#1375) at main 10795bf7 with tsci
0.0.2600. Its one part, `parts/wake-button.json`, is a copy of `tactile-button` whose need on A says `"needs":
["wake"]`. The pin wakes the chip, so its 10 k pull-up stays (P204), from A to 3V3. That puts a resistor leg on the
3V3 rail. `dist/board/circuit.json` keeps only the `source_*` elements of the built circuit. The drawn breadboard is
read from these.
