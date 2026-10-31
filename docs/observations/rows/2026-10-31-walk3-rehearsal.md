# Walk 3 rehearsal: the FireBeetle 2 onboard button lights its onboard LED

Findings of Claude's rehearsal of walk 3 part 1, 2026-10-31, Prague, on main 4dc0af9d, before the PO's free walk. Every step up to the flash ran with exit 0. Spark's two flashes wrote and verified, but the board did not start. Plain MicroPython plus `mpremote cp` by hand worked: the D13 LED lit while D14 was held. The diary stays outside the repository, in the PO's walk folder, with the board logs.

The council: one agent on Sonnet 5.5 with four lenses (PO assistant, tech lead, senior developer, AI and UX), and the refuter on Opus 5.5 for the flash causes. The refuter broke the first claim that deploy reads the board without waiting for the RESET press (row 21) and showed that the octal build did not cause the failed flash. It found the real cause in MicroPython's source, tag v1.29.0, commit 0fd6c573ea815774668bbb16b8e197c8822368b2 (https://github.com/micropython/micropython/tree/v1.29.0), and reproduced the littlefs refusal with littlefs-python 0.19. The lead checked the deploy and diagram claims in the code.

New cards, all in Idea under their epics: P461 (#629), P462 (#630), P463 (#631), P464 (#632), P465 (#633), P466 (#634), P467 (#635), P468 (#636), P469 (#637).

| # | claim | source | status | evidence / where it went |
|---|---|---|---|---|
| 1 | `--match` lists a joystick before the onboard button and five LED matrices before the onboard LED | diary | acted | P467 (#635) |
| 2 | The firmware guessed the LED polarity and the button's pressed level, and the pin map names only the LED's gap | diary | acted | P464 (#632), first slice |
| 3 | The simulation cannot press the onboard button or see the onboard LED: no Wokwi definition | diary | raised | comment on P447 (#599), parked |
| 4 | A board-only diagram has no serial monitor, so `wait-serial` hears nothing | diary, lead | acted | P468 (#636). The rehearsal's `diagram.json` has no connections. `check_spine.py:606-608` only warns about it |
| 5 | The look's no-token line names only a scenario run, not `--no-simulation` | diary | acted | P463 (#631) |
| 6 | `commands/deploy.md` says `sim/wokwi.toml` names the image, but only a comment does | diary | acted | P463 (#631) |
| 7 | `init_project.py` takes `--project .`, `import_firmware.py` a bare folder | diary, tech lead | raised | comment on P382 (#489), the names pass |
| 8 | The import check teaches the module convention only by refusal | diary | raised | comment on P339 (#433), the guide |
| 9 | Spark cannot say which unit is on USB, and ties no MAC to a hold | diary, the PO's words | acted | P466 (#634) |
| 10 | The look restarts the board at each read | diary, lead | acted | P469 (#637). `board_look.py:195` runs `esptool flash_id` with esptool's default restart |
| 11 | The printed deploy line drops `SPARK_HOME` | diary, refuter | acted | P463 (#631). `deploy_gate.py:30`. Low weight: the PO's store is the default |
| 12 | Claude called the board "FireBeetle-like". The name matters | diary, the PO | acted | learned rule, no card |
| 13 | The flash verified, then no USB device | diary | closed | explained by row 29 |
| 14 | After a failed read-back, deploy prints the mpremote line on a gone port, with no next step | diary, refuter | acted | P462 (#630). `deploy.py:278-279` |
| 15 | esptool v5.5.0 warns that `erase_flash` and `write_flash` are deprecated | diary, refuter | acted | P463 (#631). `flasher.py:43` |
| 16 | The DFR0975 needs the octal build, and the record names only the default build | diary | raised | comment on P349 (#445). The refuter: the default build sets `CONFIG_SPIRAM_IGNORE_NOTFOUND`, so it most likely starts without PSRAM. Not the flash's cause |
| 17 | The look refuses an image made with another build, and no output names `tools.py --new` | diary, refuter | acted | the words in P463 (#631), the lookup in P457 (#617), comment there |
| 18 | The PO: spark looks for the settings and the firmware on its own | diary, the PO's words | raised | comment on P349 (#445) |
| 19 | Did the board only need more time? | diary | closed | no: the boot loop of row 29 does not end |
| 20 | The PO: get every board fact from the seller, and first say what is missing, then let the person tell it or find it | diary, the PO's words | acted | the stop in P464 (#632), the research in a comment on P340 (#434) |
| 21 | Deploy printed "press RESET" and read at once | diary | rejected | refuter: deploy waits (`deploy_service.py:156`). The real bug is row 37 |
| 22 | MicroPython opens its own USB port, and deploy does not look for it | diary, refuter | acted | P462 (#630). No product ID check in `scripts/` |
| 23 | No picture of the board, and no button or LED positions in the record | diary | raised | comments on P340 (#434) and P332 (#426) |
| 24 | The charge LED blinks with no battery (DFRobot wiki) | diary | raised | comment on P340 (#434) |
| 25 | The GDI backlight LCD_BL shares GPIO21 with the onboard LED | diary | raised | comment on P460 (#628). Walk 3 part 2 cannot keep the LED |
| 26 | After the second flash and a replug, no USB device at all | diary | closed | explained by row 29 |
| 27 | esptool's restart most likely left the bare build in download mode (only the chip's own port showed) | diary, refuter | closed | outside spark, row 28 |
| 28 | esptool's RTS restart leaves the FireBeetle 2 in download mode, and only a power-up or RESET starts the firmware | diary | acted | P462 (#630) |
| 29 | The image writes a 2 MB littlefs, and MicroPython mounts 14 MB on a 16 MB board | diary, refuter | acted | P461 (#629). `flash_image.py:33,50`. MicroPython v1.29 `main.c:255-275` sizes the vfs to the end of flash, `lfs2.c:4607-4613` refuses the mount (reproduced: `LFS_ERR_INVAL`), `_boot.py` loops in `fs_corrupted()` before USB starts. The UART0 text is not yet seen |
| 30 | The button idles at 1 and reads 0 while held | diary, bench | raised | a bench fact. Written only on the PO's yes |
| 31 | Part 1 works on the board by hand: the LED lights on 1 | diary, bench | raised | a bench fact, and evidence on P383 (#491) |
| 32 | The PO: a board that does not start needs spark's help, automatic and step by step, through every interface | diary, the PO's words | acted | P465 (#633). Spark cannot read the UART0 loop text, a step for this card |
| 33 | No golden proves spark's image has the layout MicroPython expects on a 16 MB board | council | acted | in P461 (#629)'s Done when |
| 34 | The 16 MB image is also built for Wokwi, whose S3 flash size nobody checked | refuter | acted | in P461 (#629)'s plan question |
| 35 | The rehearsal ran the scripts, not the `/spark:*` commands or the agents | diary, council | raised | the free walk runs the commands |
| 36 | The first B2 card (the build per SKU) before the walk | lead | rejected | the refuter: no evidence that the build caused the failure. It goes to P349 (#445) |
| 37 | `wait_for_reset` counts any time the port goes and comes back. The log shows `rst:0x15 (USB_UART_CHIP_RESET)` before "reset seen" | refuter, lead | acted | P462 (#630). `board_console.py:139-148`. Comment on P379 (#486), the same failure family. Unproven on the bench which tool caused it |
