The button-and-LED project of the journey guide, as built on 2026-10-11 (P191, #143): its requirements, and the
parts, ports, traces and nets of its built circuit, cut from dist/board/circuit.json. The breadboard sheet is read from these.
Rebuilt on 2026-10-12 (P204): the button uses the board's internal pull-up, so the circuit has one resistor, the LED's.

`firmware/` is the firmware a person or the conversation writes once pins.py exists (P59). It prints `ready` once setup
is done and a line for each change of the LED (P130). `scenarios/` holds the scenario the conversation wrote from the
person's words, "the LED lights while the button is held". `runs/` holds the one real Wokwi run of it, on 2026-10-12, as
`run_scenario.py` wrote it. Its log keeps the board's serial output twice, because the log format changed after that run.
