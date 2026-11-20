# The breadboard codes, for AI agents

Part of [the scripts](scripts.md). When `breadboard.py` does not write a drawing, the sheet and stderr say
`breadboard.json not written:` and why. Its `code` in `kept`:

| code | subject | next step |
| --- | --- | --- |
| `no_header_fact` | the field the record lacks | research that field of the board's or the module's record (`physical.header`, `width_mm`, `body_mm`, `header_order`). Never guess it |
| `header_disagrees` | the field that does not fit | read that field of the record against its source and fix the record |
| `no_doubtful_pad_fact` | none | research `physical.header.doubtful_pads` of the board file: the pads whose net is in doubt. Write `[]` when none is doubtful, after checking. A `null` or an absent key is refused. Never guess it |
| `ground_not_one` | the ground pads left | no ground pad is left once the doubtful ones are out, or a ground pad of `power_pads` is no pad of the header. Fix `power_pads` or `doubtful_pads` from the board's schematic. With several good ground pads the drawing wires `GND` to the first one in `power_pads` |
| `duplicate_pad_label` | the label | fix `header_order` of the record |
| `no_hole_left` | the part or the end | the part does not fit with a free hole beside each pin, or a jumper finds no free row. A module's body covers the holes under it too. Use a longer breadboard or another part |
| `no_drawing_fact` | the part | the record has no Wokwi part and no `physical` block. The entry's `record` names it and `fix` says `research.py --part <id> --project .`, which asks for `physical.header`. Never guess it |
| `no_wokwi_pin` | the end | research the part's `simulation.wokwi.pins`, or a board's `wokwi_pin_naming`. A step to a doubtful pad (GND1 or GND3 of the FireBeetle) finds no pin: wire the pad the sheet names |
| `row_full`, `not_drawn_yet` | the row; the rail, the supply or the resistor | `row_full`: too many steps join one pin. Report it with the project's steps. `not_drawn_yet`: spark does not draw a rail, a supply from off the board or a resistor whose both legs join rows; `expected` is `true`. Do not retry: tell the person to wire it by hand from the sheet's steps |
| `no_pin_position`, `planner_fault` | the Wokwi type; the hole, the part or the end | `no_pin_position`: first make sure that the record's `simulation.wokwi.pins` names pins that Wokwi has, then report it. `planner_fault`: a fault in spark's planner. Report it. Do not retry |
| `no_wokwi_part` | none | none. It is by design, and `expected` is `true`. Do not retry. The `why` names each drawn part that Wokwi has no part for, the board or a module: `Wokwi has no part for the board and e-paper` |

## A part's picture

`parts.py --picture-frame <id> [--project .]` prints the frame a part's picture is drawn on
([P946](https://github.com/xmejkal/spark/issues/1349)): an SVG in mm of the outline and the pads, with each pad's ring
and label in a `data-guide` group. It writes nothing. Draw the part on it in the real part's colours, with its main
parts at their places and no glow or shadow, take the guide group out, and keep it: `parts.py --keep-picture FILE
--part <id> --made-by WORD --likeness exact|near|rough --credit LINE --project . --dry-run` first. It keeps the file
in the store and names it in the record's `documents` and `pictures.breadboard-top` in one write, or keeps
nothing. `verified` follows the frame's size fact (`body_mm.verified`). The next build draws it, with spark's pads
and labels over it: the build asks the makers in the order `picture_makers.BUILD_MAKERS` (the kept picture), then
spark's pictograms in `data/pictograms/`, the one named by the record's id before the one named by its Wokwi type.

A part's picture is checked by `picture_check.PictureCheck`
against the part's frame before `parts.py --keep-picture` keeps it, and again before the build draws it. Each problem
names its code and the element, as a path from the root: `svg/g[0]/image[0]`. A refused picture is not kept. A kept
picture that is refused at the build is drawn as the part's pictogram, with a note under the drawing:
`<part>: kept picture not shown (<why>)`. Draw the picture again in the frame (`parts.py --picture-frame <id>`) and keep it again.

| code | the picture breaks this rule |
| --- | --- |
| `picture_not_svg` | its bytes are UTF-8, parse, hold no DOCTYPE and no entity, and its root is an `svg` |
| `picture_view_box` | its `viewBox` is `0 0 W H`, with W and H the frame's size in mm, within 0.1 mm |
| `picture_element` | each element is a plain shape (as the page's) or an `image`, and none stands inside a `title` |
| `picture_attribute` | each attribute is one a picture holds (no `id`, no `style`, no handler), and no value holds `url(`, `http` or the like |
| `picture_link` | the one link is a JPEG embedded as base64 on an `image` (`href`, never `xlink:href`); no text holds a web address |
| `picture_jpeg` | an embedded JPEG is a whole JPEG with no APP1 segment (EXIF, which can say where a photo was taken) |
| `picture_guide_left` | the frame's guide group (`data-guide`) is left out: the pads are spark's to draw |
| `picture_pad_label` | no text is a pad's printed label: spark draws the labels over the picture |
| `picture_too_big` | at most 250000 bytes with no embedded JPEG, 400000 with one |
