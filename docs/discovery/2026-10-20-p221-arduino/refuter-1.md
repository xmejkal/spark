# P221 round 1: the refuter on finding.md (Opus, 2026-10-20)

Each result was checked in the code or the installed tools. The second council starts from these.

1. Confirmed: the PR count does not add up. T1 and R1 to R6 are 7, A0 to A5 are 6, and the bench adds 1 to 3, so the total is 14 to 16, not 12 to 18.
2. Confirmed: three pieces of work have no PR. They are the setup (arduino-cli in `data/tools.json` with a fetch and a checksum, `/spark:setup`, a pinned core), Wokwi for an Arduino image (`sim_project` with the `.elf`), and the place where the person picks `platform`. 102 tracked files outside the archive and discovery folders name micropython or mpremote, not about 45. Spark merged 9 to 21 PRs a day on 10-16 to 10-19, so the bench sets the dates. P239's deploy seam took 8 PRs.
3. Confirmed: verify-flash adds nothing. esptool's write already checks the flash MD5 ("Hash of data verified.", esptool `cmds.py:1938-1958`), and `verify_flash` does the same check (`cmds.py:2677`) after it re-reads all 4 MB of the padded merged.bin (the core's `platform.txt:181`). Spark calls esptool with underscores (`scripts/flasher.py:43`). The proof is a write that exits 0 with its MD5 check, then `ready`.
4. Confirmed: "no facts on the board" overrides the PO's D22 ("Record + file after flash", chosen against the recommendation) and D34 (the backup offer that reads the facts file), and it does not name them. The core ships mklittlefs, so a file system is possible. This is a question for the PO.
5. Confirmed: P323 is presented as settled. PR #414 is a draft that waits on the PO's yes, and only its slice 1a may run before walk 1. T1 and `PlatformContract` overlap slice 1a (contract mixins and goldens).
6. Confirmed: the import check on a lone `firmware.ino` prints `problems` and exits 1. It does not print could-not-run.
7. Confirmed: the install is about 6 GB to download and 12 GB on disk (`~/Library/Arduino15`: 5.6 GB in `packages/esp32`, 6.0 GB in `staging`, the toolchains of all chips).
8. Rejected: the C6 does not need CDCOnBoot set. Core 3.3.10's `boards.txt:37932,37954` has `cdc_on_boot=1` as the XIAO_ESP32C6 base value. The merge-bin recipe is at `platform.txt:181`.
9. Confirmed in part: W1 has no single rule. "A step that a platform does not support prints `skipped` with its cause, never `ok`" belongs in the platform contract.
10. `tools/factcheck.py`: 0 broken references.

Not checked: a C6 on the bench, and an arduino-cli compile, because arduino-cli is not installed. The finding also leaves out the "other platforms" in the PO's question.
