# The breadboard codes, for AI agents

Part of [the scripts](scripts.md). When `breadboard.py` does not write a drawing, the sheet and stderr say
`breadboard.json not written:` and why. Its `code` in `kept`:

| code | subject | next step |
| --- | --- | --- |
| `no_header_fact` | the field the record lacks | research that field of the board's or the module's record (`physical.header`, `width_mm`, `body_mm`, `header_order`). Never guess it |
| `header_disagrees` | the field that does not fit | read that field of the record against its source and fix the record |
| `no_doubtful_pad_fact` | none | research `physical.header.doubtful_pads` of the board file. Never guess it. A project file made before P412 lacks it |
| `ground_not_one` | the ground pads left | settle with a meter which ground pads have a net, then fix `doubtful_pads` |
| `duplicate_pad_label` | the label | fix `header_order` of the record |
| `no_hole_left` | the part or the end | the part does not fit with a free hole beside each pin, or a jumper finds no free row. A module's body covers the holes under it too. Use a longer breadboard or another part |
| `no_drawing_fact` | the part | the record has no Wokwi part and no `physical` block. The entry's `record` names it and `fix` says `research.py --part <id> --project .`, which asks for `physical.header`. Never guess it |
| `no_wokwi_pin` | the end | research the part's `simulation.wokwi.pins`, or a board's `wokwi_pin_naming`. A step to a doubtful pad (GND1 or GND3 of the FireBeetle) finds no pin: wire the pad the sheet names |
| `row_full`, `not_drawn_yet` | the row; the rail, the supply or the resistor | `row_full`: too many steps join one pin. Report it with the project's steps. `not_drawn_yet`: spark does not draw a rail, a supply from off the board or a resistor whose both legs join rows; `expected` is `true`. Do not retry: tell the person to wire it by hand from the sheet's steps |
| `no_pin_position`, `planner_fault` | the Wokwi type; the hole, the part or the end | `no_pin_position`: first make sure that the record's `simulation.wokwi.pins` names pins that Wokwi has, then report it. `planner_fault`: a fault in spark's planner. Report it. Do not retry |
| `no_wokwi_part` | none | none. It is by design, and `expected` is `true`. Do not retry |
