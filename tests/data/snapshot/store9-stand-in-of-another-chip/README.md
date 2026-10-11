The S3 board record with `chip` set to esp32c6 and the S3 devkit still as its Wokwi stand-in: a board that says one
chip and simulates another. Found by P158's store lens (#94, STORE-9).

What the baseline of 2026-10-11 recorded: `boards.py --validate` and `--validate --for-fab` both ok, exit 0.
P187 (#136) will refuse it, naming the stand-ins of the same chip.
