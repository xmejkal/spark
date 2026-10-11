The FireBeetle 2 ESP32-C6 (DFR1075) board record made from DFRobot's own sources, as spark documents it, in P100's
round 0 (#6, 2026-10-09).

What the baseline of 2026-10-11 recorded: both validations ok, exit 0; the chain builds (5 traces, 0 errors) and stops
at the simulation, exit 1: the Wokwi stand-in for the C6 has no GPIO14, and the LED was given D3, which is GPIO14.
