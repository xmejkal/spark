# P278 (#314), widened: the shipped XIAO record builds

Plan, 2026-10-18. Backlog item 1 of [the loop backlog](../2026-10-18-loop-backlog/backlog.md), blocker 1 of
[the journey gaps](../2026-10-18-journey-gaps/gaps.md). Branch `p278-xiao-record-builds`.

## Council

Round 1 ran (tech lead sonnet, refuter opus). The refuter could not break the build and rejected three worries (the
`wokwi_power_pins` key change, `adc_gpio` `[0..6]`, the width/height swap). Changes it forced:

- Fifteen stale tests, not 13: two need a board with no `power.io_volts`, the rest one with no `physical.header`. One test
  helper, `board_missing(field)`, patches `boards.LIBRARY` to a copy of the library with that field deleted.
- `footprint_module` null would fail `boards.py --validate --for-fab` for the library walk, so for every project, a FireBeetle one too
  (round 2, tech lead). Decision: `physical.footprint_module` keeps the shipped value `XIAO-ESP32-C6-SMD` (nothing but the
  gate reads it), so the gate does not change. That name points at no drawn file, which was true before; it is a row for the PO.
- The risk "fixtures already agree" was false: the fresh record puts the button on D10 and the LED on D8, the shipped one
  on D7 and D10. A shipped build is never compared with the `button-light-xiao` fixtures.
- The pin map gains `BUTTON_PULL = "up"`, because `power.internal_pull_up_ohms` now exists. A test pins it.
- Stale record text is fixed: `//adc_gpio`, `//wokwi_power_pins`, `//pins_functions`, the `deep_sleep` cite (v5.5.2 is not kept; documents hold v5.5.1, and the comment says so).
- Docs added: `commands/build.md:181`, `how-it-works.md:203`, `skills/spark-design/references/tscircuit-recipes.md:40-44`, `journey.md` transcripts.
- `pins`: fresh also has `TX`, `RX`; they are not copied, `pad_aliases` reaches them. A test says so.

Round 2 ran (tech lead, PO assistant, both sonnet). Changes:

- The helper `board_missing(field)` lives in `tests/board_library.py`, a context manager that patches `boards.LIBRARY`. Three
  tests cannot use it as is: `test_check_spine.py:1221` runs `emit_board` in a child process (it uses a project board file
  with `io_volts` deleted and `from_library=False`), `test_emit_footprint.py:203` reads the file itself (it deletes the header
  of a deep copy of the FireBeetle record), and `:210` runs in process (the patch works).
- One doc list (Step 4). Transcripts in `journey.md` change only where a test or the README quotes them.
- `adc_gpio` is the only agreement edit of the shipped record; the fresh fixture is a spark test fixture, so its `flash_mb` and
  `deep_sleep` are edited too ("a fixture that tests spark is part of the change"); the PO's bench copy is in his store.
- `BUTTON_PULL = "up"` in `pins.py` is a fact from `internal_pull_up_ohms`, not a threshold; the PR names the output change.
- Word: "the fresh record" throughout.

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
| `physical` | SMD module name `XIAO-ESP32-C6-SMD` (kept), `XiaoRealFootprint`, 21.0 x 17.8, 70x90 px, no header | `footprint_module` null, `XiaoEsp32C6`, 17.8 x 21.0, 68x88 px, `header` (2x7, 2.54 pitch, rows 15.24 apart), `header_order`, `pad_aliases` | copy, but `footprint_module` stays `XIAO-ESP32-C6-SMD` so the fab gate does not turn red for every project | Seeed DIP footprint (commit b0035c51); schematic sheet 03; Wokwi board.json |
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
4. Docs, one list, only lines that say the XIAO stops or name the old pad names: README lines 32-36 and the Build row,
   `tools/journey.py` if its note changes (`tests/test_journey.py` guards), `docs/guide/journey.md`, `docs/guide/agents.md`
   (the `io_volts` example), `docs/guide/how-it-works.md:203`, `commands/build.md:181`, `commands/idea.md`,
   `commands/init.md`, `skills/spark-design/references/tscircuit-recipes.md:40-44`.
5. Review (sonnet, refuter), one mutation pass, findings in `rows.md`, a ready PR.

## Risks

- `adc_gpio` `[0..6]`: `assign_pins` reads it against the header pin map, so GPIO 3-6 never match. A test pins it.
- Placement reads `wokwi_size_px`: 70x90 becomes 68x88. Only `emit_footprint` and `place()` read it.
- `breadboard.json` and `pins.py` of a shipped-board build differ from the fixtures' (other pins, `BUTTON_PULL`).
- `footprint_module` names a footprint no file draws; the fab gate trusts the name. A row for the PO, not changed here.
