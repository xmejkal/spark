STORE-9 (P158 part 1, `council/store-scenarios.md`): an S3 board file whose `chip` says esp32c6 but whose Wokwi stand-in
is still the S3 devkit. Reproduced on 2026-10-10: `boards.py --validate` answered ok, exit 0 (P187 refuses it).
