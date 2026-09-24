---
name: spark-check
description: Check a design made of modules plugged into a dev board, before it is built. Catches a wake source on a pin that cannot wake the chip, an analogue input on a digital-only pin, two parts on one pin, a serial module on the boot-log UART, and two I2C devices at the same address. Use when the user has chosen parts and pins and asks to "check the wiring", "will this work", "review my pin assignments", or is about to order or solder.
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/check_pins.py *)
---

# spark-check

Two checks that no EDA tool performs, because no EDA format carries the facts they need. KiCad
will happily route a wake source to a pin that cannot wake the chip, and **no netlist format in
existence has a field for an I2C address**. Everything else worth checking — ERC, DRC, footprints —
is somebody else's solved problem; use their tool.

## Run it

```
${CLAUDE_PLUGIN_ROOT}/scripts/check_pins.py <design.json>
```

Exit 0 means sound, 1 means problems, and every problem names the part, the pin and the reason.

## The design file

```json
{
  "board": "path/to/board.json",
  "parts": [
    {
      "ref": "Rangefinder",
      "part": "VL6180X",
      "i2c": { "bus": "i2c0", "address": "0x29" },
      "pins": [
        { "signal": "INT", "pin": "D0", "needs": ["wake"] },
        { "signal": "SDA", "pin": "D4" }
      ]
    }
  ]
}
```

`board` is relative to the design file. `examples/smartbin.design.json` is a complete worked
example — a real bin with seven modules.

**`needs` is the part of this that earns its keep.** It is the part's claim about a pin:

- `"wake"` — must bring the board out of deep sleep
- `"adc"` — must read an analogue voltage

A claim the board cannot honour is the failure this exists to catch. Write `needs` from what the
part *must do*, not from the pin you happened to pick; otherwise the check only confirms your own
assumption.

`"reads_serial": true` on a part marks it as parsing a UART, which makes the boot-log pin a
failure rather than a caveat.

## What it checks

| Check | Catches |
| --- | --- |
| Pin exists | A pin the board does not bring out |
| Capability | A wake source or analogue input on a pin that cannot do it |
| Exclusivity | Two parts assigned the same pin |
| Boot-log UART | A serial-parsing module on the pin the ROM bootloader prints to |
| I2C address | Two devices answering to one address on one bus |

Capability is **chip capability intersected with what the board exposes**. An ESP32-C6 can wake on
GPIO0–7; a XIAO brings out only three of them. Checking the chip alone would approve four pins
that are not on the header — which is why the answer comes from the board definition, not from
general knowledge about the chip.

## The board definition

The board's facts — pin labels to GPIO, which pins wake, which have an ADC, which carry a special
role — live in one JSON file. `boards/README.md` in the smart-bin project has the schema. Pin
roles are typed (`boot_log_tx`, `onboard_led`) rather than free text, so a check can read them;
knowledge in prose is knowledge a program cannot use.

## What this does not do

It does not check voltage domains or current budget. Both need part records that do not exist
yet, and a current budget cannot give a real answer until somebody has measured the stall current
of the actual motor — that is a bench task, not a code task.

It does not check anything about the PCB. It reads a design, not a layout.

**A clean run means these five things are right. It does not mean the design works.**
