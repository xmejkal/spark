---
description: The cheap deterministic pass over a design — pins, capabilities, buses, I2C addresses. Seconds, no agents.
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/scripts/check_design.py *), Bash(${CLAUDE_PLUGIN_ROOT}/scripts/check_all.py *)
---

# spark:check

Checks that no EDA tool performs, because no EDA format carries the facts they need. KiCad will
happily route a wake source to a pin that cannot wake the chip, and **no netlist format in
existence has a field for an I2C address**. Everything else worth checking — ERC, DRC, footprints —
is somebody else's solved problem; use their tool.

This is a **command** rather than a skill on purpose. It was a skill, and its description competed
for "check my design" against `spark-review`, which launches five Opus agents. Asking a
one-script question should not cost that, so this one is opened by name.

## If there is a design file

```
${CLAUDE_PLUGIN_ROOT}/scripts/check_design.py <design.json>
```

## If there is a built board

```
${CLAUDE_PLUGIN_ROOT}/scripts/check_all.py --project .
```

That runs every deterministic check, and prints the path it resolved for each input before it
reports anything. Read that block first: `not found` means a check will be skipped and says where
it looked, and `AMBIGUOUS` means it refused to choose between two candidates.

## The design file

```json
{
  "board": "firebeetle2-esp32s3",
  "parts": [
    {
      "ref": "Rangefinder",
      "part": "VL6180X",
      "i2c": { "bus": "i2c0", "address": "0x29" },
      "pins": [
        { "signal": "INT", "pin": "D12", "needs": ["wake"] },
        { "signal": "SDA", "pin": "SDA" }
      ]
    }
  ]
}
```

`board` is either an id from the library (`boards.py --list`) or a path relative to the design
file. `examples/smartbin.design.json` is a complete worked example — a real bin with seven modules.

**`needs` is the part of this that earns its keep.** It is the part's claim about a pin:
`"wake"` must bring the board out of deep sleep, `"adc"` must read an analogue voltage. A claim
the board cannot honour is the failure this exists to catch. Write `needs` from what the part
*must do*, not from the pin you happened to pick — otherwise the check only confirms your own
assumption.

`"reads_serial": true` marks a part as parsing a UART, which makes the console pin a failure
rather than a caveat. `"i2c": {"bus": ...}` is what tells the check that two devices on SDA and
SCL are sharing a bus rather than colliding.

## What it catches

| Check | Catches |
| --- | --- |
| Pin exists | A pin the board does not bring out |
| Capability | A wake source or analogue input on a pin that cannot do it |
| Exclusivity | Two parts on one **GPIO** — including one pin brought out under two silkscreen names |
| Console UART | A serial-parsing module on the pin the ROM bootloader prints to |
| I2C address | Two devices answering to one address on one bus |

Capability is **chip capability intersected with what the board exposes**. An ESP32-C6 can wake on
GPIO0–7; a XIAO brings out only three of them. Checking the chip alone would approve four pins
that are not on the header — which is why the answer comes from the board definition rather than
from general knowledge about the chip.

## The board definition

The board's facts — pin labels to GPIO, which pins wake, which have an ADC, which carry a special
role — live in one JSON file. `boards/README.md` in **this plugin** has the schema, and a
project's own `boards/<id>.json` beats the shipped library. Pin roles come from a closed
vocabulary (`boards.PIN_ROLES`) rather than free text, so a check can read them; a role name
nothing consumes looks exactly like a role that is working.

## What this does not do

It does not check voltage domains or current budget — those need part records and a measured
stall current, which is a bench task, not a code task. It does not check anything about the PCB:
it reads a design, not a layout.

**A clean run means these five things are right. It does not mean the design works.** For the
judgement half — power behaviour, signal integrity, thermal and mechanical fit — ask for a review,
which runs these first and then reasons about what they cannot reach.
