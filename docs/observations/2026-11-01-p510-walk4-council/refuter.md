# P510 refuter (Opus 5.5)

> C1 (the SPI pad-name build defect) is wider than all four reports say. The XIAO ESP32-C6 breaks on SPI, on I2C and on A0, since P278 (2026-10-18).
> The architecture lens's clash of C6 (the automatic deploy) with plan decision 6 is wrong. The standing deploy grant exists, and the s3lcd image can never get one.
> The product lens's "Ready holds 6" is wrong today. All 14 GDI GPIOs are already header labels, so C2 (fixed connector) needs no new candidate labels.

Code at `8595309b`, worktree read only. Builds ran in `/private/tmp/claude-501/p510-refuter`, deleted after. [ran] = I ran it. [read] = I read the line.

## Checks

| # | claim | verdict | evidence | proposal | sev |
|---|---|---|---|---|---|
| R1 | C1: the emitter traces the pin name, and the FireBeetle 2 build fails on MOSI and MISO | CONFIRMED | [ran] `check_spine.py` on walk 4's requirements: `2 error(s)`. `circuit.json` names `.Mcu > .MOSI` and `.MISO`. [read] `emit_board.py:812-813`, `signal_lines(part_list, assignments)` at `:1048` gets no board | Take the technology lens's fix | high |
| R2 | Technology 3: the XIAO hit is "not checked" | CONFIRMED, wider | [ran] XIAO + `dfr0664-tft-2in`: 4 errors (`SCK`, `MOSI`, `MISO`, `A0`). XIAO + `vl6180x-breakout`: 3 errors (`SDA`, `SCL`, `A0`). XIAO + LED + button: end to end. The XIAO's `pad_aliases` came in P278 (`2b868965`, 2026-10-18) | C1's Done when names 3 builds: FireBeetle 2 SPI, XIAO SPI, XIAO I2C. Any part on XIAO A0 to A2 breaks too | high |
| R3 | Architecture A1: the lookup sits in 4 places, so one `BoardPads` reader and a grep test | CONFIRMED in part | [read] `boards.py:694` is the record validator, not a trace lookup. The Wokwi converter has its own copies: `tools/circuit-to-wokwi/lib/board.ts:102,112`, `lib/mapping.ts:94`. A Python Value reaches neither | The grep test covers the Python trace readers only (`assign_pins`, `breadboard`, `emit_board`). Name the TypeScript copy as out of scope | medium |
| R4 | Architecture A9: C6's standing yes clashes with plan decision 6 | REJECTED | [read] `architecture/README.md` decision 6: a relayed yes never makes a deploy grant. The deploy grant, typed in the person's terminal, exists since P242: `board_grant.py:14-15,85,172`, `grant.py` epilog. UX finding 1 is right | C6 changes P242's exclusion of `--no-simulation` (`board_grant.py:107`, `image_evidence.py:353`), not decision 6. That exclusion is the PO's call | high |
| R5 | C6: "start with `--after watchdog-reset`" is already done (technology 6) | CONFIRMED, wrong cite | [read] `deploy.py:95` is `--help` text. The code is `flasher.py:51`, `AFTER = ["--after", "watchdog-reset"]` | Cut the clause. Cite `flasher.py:51` | low |
| R6 | UX 7: P469's plan and C6 differ on `--after` | CONFIRMED | [read] P469 plan lines 12 and 28 pin `--after hard-reset` for the look and add a RESET hint. `flasher.py:45-50`: hard-reset leaves a BOOT-entered S3 in download mode. UX's rule "hard-reset after a read" has no bench evidence | P469's plan drops "hard-reset pinned" before C6's entry merges in. P469 is in Build with its plan HELD for the PO, so C6 waits on that answer | medium |
| R7 | Rows comparison: P469's body does not name `machine.bootloader()` | REJECTED in part | [read] #637's "From walk 3" section names `machine.bootloader()` through mpremote, then `--before no-reset`. Only its first Done when lacks it. `scripts/` has no `bootloader()` call (grep) | Add one Done when line to #637, no new text elsewhere | low |
| R8 | Nobody checked: a grant needs a USB serial equal to the MAC | CONFIRMED, new | [read] `board_grant.py` `WHY_SERIAL_NOT_MAC`, `grant.py` epilog. G44: the s3lcd build reports a fixed serial | The automatic mode cannot cover the image walk 4 ended on. C6 and C8 name it, and C8's "find the board by another fact" feeds the grant too | high |
| R9 | Architecture A6: `FlashLayout` takes its size from the record's `flash_mb` | CONFIRMED defect, wrong fix | [read] `flash_image.py:37-38,82,121-126`. The FireBeetle 2 record holds `"flash_mb": [16, 4]`, one per SKU, so the record cannot choose. `:124` also refuses any non-`vfs` entry past 0x200000 | Size from the look's measured `BoardReading.flash_mb` (`board_look.py:44`), the record list as a check | medium |
| R10 | Architecture A2: the GDI GPIOs are no header labels, so connector pins join `candidates()` | REJECTED | [read] the board's `pins`: BL 21 = D13, DC 3 = D2, RST 38 = D3, CS 18 = D6, SDCS 9 = D7, FCS 7 = D5, TCS 12 = D12, INT 13 = D11, TE 14 = D10. SPI and I2C are labels. `assign_pins.py:228-247` honours a named label | No assigner change. A plug is a list of signal names to existing labels | medium |
| R11 | G27: `requirements.json` cannot pin a part's signal | CONFIRMED | [ran] `signals: [{"name": "TFT_BL", "pin": "D13"}]` beside `dfr0664-tft-2in`: "dfr0664-tft-2in's TFT_BL and signals[0] are both TFT_BL". `design.py:128-150` takes a pin for a free signal only | Smallest C2 slice: a requirements signal with a part's signal name sets that signal's pin. Then the GDI plug is data | medium |
| R12 | Product 1: Ready holds 6 against a limit of 5 | REJECTED | [ran] `gh project item-list 2`: Ready is P473, P503, P506, P507, P508. P510 and P469 are in Build | P506 (#700) to Idea still holds on its own reason: its Done when is a PO decision (#700 body) | low |
| R13 | Product and architecture: C10 merges into P467, or adds one `ONBOARD_ROLES` row | REJECTED both | [read] #635's Done when is a ranking test only. `assign_pins.onboard_lines` (`:438-440`) already writes `<NAME>_<LABEL>` from a record's `labels` | C10 stays its own XS, record only. Labels rename `ONBOARD_BUTTON` to `ONBOARD_BUTTON_USER`, which breaks old firmware, so name that in Done when | low |

## Merges into open cards (item 5)

- P399 (#515, scenario dry run): its PR 2 is `--dry-run` with free checks. G12 fits exactly. Confirmed.
- P349 (#445, most specific build): G37's PSRAM build is "the most specific build". Confirmed.
- P490 (#669, `seen_on_bench` on a typed yes): G18 fits. Confirmed.
- P466 (#634, MAC names its unit and hold): G3 and G4 fit. G6 and G7 do not. Confirmed.
- P336 (#430, driver records in the store): G42 is a flash layout defect in `flash_image.py`, not a driver record. Keep it as its own card (R9). P336 names it as a need.
- P460 (#628, GDI spike): its Done when asks for pinouts with sources. The walk's pins are `verified: false`, read off an image (diary O5). The spike stays open until its sources are cited. Its "after the FireBeetle walk" line is stale.
- P492 (#671) and P409 (#535): titles and bodies fit G13 and G25. Not checked further.

## Rows marked held (item 6)

- G34 holds, but GPIO0 is also header pin D9 (`pins.D9 = 0`). C10's button and a part on D9 share one GPIO. The pick names it.
- A5 (removing a pick frees its hold): `needs.py:448-452` rebuilds `used_in` per project. Plausible, not run.
- G8 (`check_all.py:466`), G26 (`needs.py:406`), G38 (`flash_image.py:255-256`): each line reads as the lens says.

## Not checked

- Bench claims G15, G36, G40, G41, G44, G45, and whether `watchdog-reset` after a software entry works on the S3 beyond P472's log.
- Claude Code deny rules for `grants/**` (UX 5). The doctor's 2 s value (G16). Skill page text for G1, G2, G9, G11.
- Whether a project or walk built a XIAO bus part after 2026-10-18 and met this failure.
