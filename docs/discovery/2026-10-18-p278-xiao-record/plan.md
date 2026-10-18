# P278 (#314), widened: the shipped XIAO record builds

Plan, 2026-10-18. Backlog item 1 of [the loop backlog](../2026-10-18-loop-backlog/backlog.md), blocker 1 of
[the journey gaps](../2026-10-18-journey-gaps/gaps.md). Branch `p278-xiao-record-builds`.

## Council

Round 1 ran (tech lead sonnet, refuter opus). The refuter could not break the build and rejected three worries (the
`wokwi_power_pins` key change, `adc_gpio` `[0..6]`, the width/height swap). Changes it forced:

- Fifteen stale tests, not 13: two need a board with no `power.io_volts`, the rest one with no `physical.header`. One test
  helper, `board_missing(field)`, patches `boards.LIBRARY` to a copy of the library with that field deleted.
- `footprint_module` null fails `boards.py --validate --for-fab`. The old SMD name pointed at no file, so the old pass was
  false. Decision: the XIAO fails the fab gate until a footprint is drawn and checked; a test pins it; `how-it-works.md:203` says so.
- The risk "fixtures already agree" was false: the fresh record puts the button on D10 and the LED on D8, the shipped one
  on D7 and D10. A shipped build is never compared with the `button-light-xiao` fixtures.
- The pin map gains `BUTTON_PULL = "up"`, because `power.internal_pull_up_ohms` now exists. A test pins it.
- Stale record text is fixed: `//adc_gpio`, `//wokwi_power_pins`, `//pins_functions`, the `deep_sleep` cite (v5.5.2 is not kept; documents hold v5.5.1, and the comment says so).
- Docs added: `commands/build.md:181`, `how-it-works.md:203`, `skills/spark-design/references/tscircuit-recipes.md:40-44`, `journey.md` transcripts.
- `pins`: fresh also has `TX`, `RX`; they are not copied, `pad_aliases` reaches them. A test says so.

Round 2: tech lead and PO assistant.

## Problem

`check_spine.py req.json --keep DIR` with `"board": "xiao-esp32-c6"` stops at the schematic stage
("the board states no power.io_volts"). The bench project used its own copy, `xiao-esp32-c6-fresh`
(`tests/data/breadboard/button-light-xiao/boards/`), written 2026-10-13 from the vendors' sources, with cites. An
experiment (copy five fields, build) already exits 0 and writes `breadboard.json`.

## Done when

Button + LED on `xiao-esp32-c6` exits 0 and writes `breadboard.json`. The five fields below come from the fresh
record with their cites. `deep_sleep`, `adc_gpio` and `flash_mb` agree in both records.

## The facts table

| field | shipped value | fresh value | decision | source (kept in `documents`) |
| --- | --- | --- | --- | --- |
| `power` | none | 6 facts: `io_volts` 3.3, `module_peak_a` 0.354, `internal_pull_up_ohms` 45000, `charge_current_a` 0.12 (all verified); `deep_sleep_ua` 15 and `regulator_3v3_a` null (unverified, kept so) | copy | ESP32-C6 datasheet v1.5 Tables 5-2, 5-7, page 65; schematic sheet 03 |
| `power_pads` | none | `GND`, `3V3` (supplies, own draw, volts), `5V` (in, feeds 3V3) | copy | schematic sheet 03; wiki |
| `wokwi_power_pins` | `V33`, `GND`, `V5` (the SMD footprint's pad names; no file draws that footprint) | `3V3`, `GND`, `5V` (the pad names the generated DIP footprint gives) | copy; the keys must match `power_pads` | `wokwi-board` document |
| `documents` | none | 11 kept sources, each with url, sha256, version, date | copy | each entry |
| `physical` | SMD module name, `XiaoRealFootprint`, 21.0 x 17.8, 70x90 px, no header | `footprint_module` null (generated), `XiaoEsp32C6`, 17.8 x 21.0, 68x88 px, `header` (2x7, 2.54 pitch, rows 15.24 apart), `header_order`, `pad_aliases` | copy | Seeed DIP footprint (commit b0035c51); schematic sheet 03; Wokwi board.json |
| `adc_gpio` | `[0,1,2]` | `[0..6]` | shipped takes `[0..6]`: the chip's ADC1 channels; only A0-A2 are on the header, so the pin map does not change | datasheet v1.5 Table 2-8, page 23 |
| `flash_mb` | 4 (Seeed wiki, bench esptool read) | none | fresh takes 4 with the shipped cite | wiki; `bench/p228/03-esptool.txt` |
| `deep_sleep` | `wake_api` ext1, one polarity true (MicroPython), not simulated (experiment) | one polarity false (silicon), "UNVERIFIED", simulated unknown | fresh takes the shipped block: verified on MicroPython v1.29, and it says the silicon differs | `modesp32.c` v1.29.0; soc_caps.h v5.5.2 |

Not copied: fresh's `pins` (equal for D0-D10 and A0-A2), `pin_roles`, `sources`, `sku`, `wokwi_part_type`. Shipped keeps
its own `pin_roles` (USB and flash pins are cited there, and `live.py` reads them).

## Steps

1. Test first: `tests/test_xiao_record.py` builds button + LED on the library XIAO with `--keep` and asserts exit 0 and
   `breadboard.json`, plus one fact test per copied field (equals the fresh record's; every `cites.document` names an
   entry in `documents`; the three agreeing fields are equal in both records).
2. Change `boards/xiao-esp32-c6.json` (data only) and the fresh fixture's `flash_mb` and `deep_sleep`.
3. Fifteen tests use the shipped XIAO as a board that stops (no header, or no `io_volts`). It no longer does. Each
   uses `board_missing(field)` so the stop message stays tested.
4. Docs that say the XIAO stops: README lines 32-36, `docs/guide/journey.md`, `agents.md` (the `io_volts` example),
   `commands/idea.md`, `commands/init.md`, the Build row and `tools/journey.py` if the note changes
   (`tests/test_journey.py` guards).
5. Review (sonnet, refuter), one mutation pass, findings in `rows.md`, a ready PR.

## Risks

- The 13 stale tests are the real cost. If a scratch board per test is not simple, one fixture board in `tests/data`.
- `adc_gpio` `[0..6]`: `assign_pins` reads it against the header pin map, so GPIO 3-6 never match. A test pins it.
- Placement reads `wokwi_size_px`: 70x90 becomes 68x88. Only `emit_footprint` and `place()` read it.
- `breadboard.json` and `pins.py` of a shipped-board build differ from the fixtures' (other pins, `BUTTON_PULL`).
