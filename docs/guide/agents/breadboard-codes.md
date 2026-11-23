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
| `row_full`, `not_drawn_yet` | the row; the rail, the supply or the resistor | `row_full`: too many steps join one pin. Report it with the project's steps. `not_drawn_yet`: spark draws no unsigned rail, no third mark of one sign, no off-board supply and no resistor with both legs in rows. `expected` is `true`. Do not retry: tell the person to wire it from the sheet's steps |
| `no_pin_position`, `planner_fault` | the Wokwi type; the hole, the part or the end | `no_pin_position`: first make sure that the record's `simulation.wokwi.pins` names pins that Wokwi has, then report it. `planner_fault`: a fault in spark's planner. Report it. Do not retry |
| `no_wokwi_part` | none | none. It is by design, and `expected` is `true`. Do not retry. The `why` names each drawn part that Wokwi has no part for, the board or a module: `Wokwi has no part for the board and e-paper` |

## The board's look and the space between parts

`breadboard.svg` shows the breadboard as the README's old wiring page did (P953): a white page, the board in its
`palette` (the colours and sizes in `data/breadboards.json`), the gap between rows e and f as a band, four rails with
their + and - signs, the letters a to j and the column numbers. On spark's 63-column board each part's body (its *body
box*) keeps 4 free columns (`body_gap_columns`) from the body before it. When the board is too full, the part goes
closer, the layout names it in `crowded`, and the sheet says once "The parts are closer than 4 columns because the
breadboard is full." That line is no failure: the drawing is right. A module with one row of pins whose body would reach
across the gap sits in the outermost row, so its body hangs off the board's edge. Wokwi's half board keeps the layout
Wokwi was shown.

Each wire in the picture goes around the parts, never over a part's body (P953): out of its hole along the column,
then only on tracks half a pitch between the rows and columns of holes, with at most 4 bends, one pitch from the wire
beside it, and across another only at a right angle. A wire that needs more bends to get around is drawn dashed, and
the note under the picture names it ("wire 7 bends more than 4 times to go around the parts and is drawn dashed"); a
wire with no way at all is not drawn, and the note says so. The steps and their holes are the same either way.

## Power and ground on the rails

Power and ground go through the rails, on every board (P953). A point that carries power (a record gives one of its ends
a rail other than ground) goes on a + rail, and a point that carries ground on a - rail. The first end's step says `a
free + rail. Mark it 3V3`, and each other end gets its own jumper to `the 3V3 rail`. The point's line ends with `— power:
join board 3V3 to a + rail and the other ends to that rail`. The drawing puts a mark on the rail of its sign, on the side
of the board that holds most of its ends (on a tie, its first end's side), and a second mark of that sign on the other
side (`spark/breadboard/rails.py`). Three marks of one sign and a rail with no sign (a signal point with more ends than
a row holds) are `not_drawn_yet`. A resistor leg on a rail goes in a free row close to its other end. Its step says the
jumper from that row to the rail. Its holes give the leg's hole, then the jumper's two holes, `d39, then from a39 to
top + rail, hole 32` (P960). A resistor covers the holes between its legs, so no other leg or jumper lands under its
body. Each rail jumper takes the free rail hole nearest its end that no part's body covers, and the step names it
`bottom + rail, hole 5`. No jumper joins the top and bottom rails. A rebuild's line that marks a rail says its sign,
`a free - rail, which you mark GND`. A record from before P953 has no sign, and its line keeps `a free rail`.

## The pills and the wire colours

In `breadboard.svg` each jumper carries one pill (P953): its step's number in a white disc, then the two pads it joins,
the board's last (`6  CS to D3`), or the pad and its rail's sign (`3  3V3 to + rail`). The words are each end's `label`:
the board's printed label, the part's printed name, or a resistor's `R1 end 1`. A pill lies on its wire's longest run
across, else on its longest run along a column (turned), else beside a stub into a rail or past its end. It touches no part's body, end
dot, other wire, other pill, letter, number or rail sign, and sits in its jumper's `data-step` group. Each wire is drawn in the hex of its colour word from `palette.wires` in `data/breadboards.json`,
each at least 4.5:1 with white; the sheet and Wokwi keep the word (cyan is drawn `#0b7fa8`).

## The labels, the captions and the note

A pad's label says the word the steps say for it (`wiring_steps.pad_word`, P953): `GND1` and `GND2` read `GND`, `NC3`
reads `NC` in a muted grey, and `3V3_2` stays `3V3_2`, as the steps say it. A used pad's label is bold yellow, a free
one dim, each with a thin dark outline. Every turned text reads bottom to top: a label's turn plus its part's is 0 or
-90. Each part has one caption outside its body (`class="caption"`): its record's `name` up to the first comma
(`DFRobot FireBeetle 2 ESP32-C6`), or, with no name, its id in grey. It sits above the body, else below it, at the
body's left edge, moving out a pitch at a time (up to 9) before it slides along the body, until no body, wire, end dot,
pill, mark or other caption is in its box. The note under the picture has one line per part with a fact not verified
(`class="note"`), named as its caption is, so a record id only where the record has no name: `MH-ET LIVE 2.9 Inch
E-paper Module: pads and header side not verified.`, then the part picture's own note, then the wires' line.

## A part's picture

`parts.py --picture-frame <id> [--project .]` prints the frame a part's picture is drawn on
([P946](https://github.com/xmejkal/spark/issues/1349)): an SVG in mm of the outline and the pads, with each pad's ring
and label in a `data-guide` group. It writes nothing. Draw the part on it in the real part's colours, with its main
parts at their places and no glow or shadow, take the guide group out, and keep it: `parts.py --keep-picture FILE
--part <id> --made-by WORD --likeness exact|near|rough --credit LINE --project . --dry-run` first. It keeps the file
in the store and names it in the record's `documents` and `pictures.breadboard-top` in one write, or keeps
nothing. `verified` follows the frame's size fact (`body_mm.verified`). The next build draws it, with spark's pads
and labels over it: the build asks the makers in the order `picture_makers.BUILD_MAKERS` (the kept picture, then
spark's drawing of the measured features, below), then
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

## A board's top view and drawing

`parts.py --find-documents <board> --project .` ([P952](https://github.com/xmejkal/spark/issues/1358)) finds a DFRobot
board's top view and dimension drawing on the maker's wiki page by its `sku`, keeps them in the person's store and lists
them in the board's `documents`. It draws nothing and writes no `pictures` block. The top view is the first picture in
the page's "Board Overview" section, and the drawing is the document that the page names "Dimension". A drawing in a
zip is listed with `kept: false`. A file that the record keeps already is not fetched again. The run reaches the
network, so Claude Code asks before it runs. spark does not check that the picture shows your board's revision: look
at it before you measure it.

| code | what the run did not find | next |
| --- | --- | --- |
| `no_vendor_finder` | a page: the board's `vendor` and `sources` name no DFRobot page | the photo step: `/spark:identify`, then `--features-set` |
| `no_sku` | the page's address: the board has no `sku` | write the `sku`, then run again |
| `no_top_view` | a picture in the page's "Board Overview" section | the photo step |
| `no_dimension_drawing` | a document on dfrobot.com that the page names "Dimension" | keep a drawing from another page with `parts.py --keep` |

## A board's measured features

A board's main features can be measured on the maker's top view and drawn in their real colours
([P956](https://github.com/xmejkal/spark/issues/1362)): the chips, the USB socket, the buttons, the LEDs, the battery
socket, the display connector, the crystal, the inductors, the groups of small resistors and capacitors, the mounting
holes and the silkscreen words that name no pad. Boards only in this version.

1. Keep the maker's top view in the record's `documents`: `parts.py --find-documents` for a DFRobot board (above). It
   must be a component-side top view, never a mirrored one.
2. Look at the picture and write a features file in its pixels: `{picture: {document, outline_px: [left, top, right,
   bottom], usb_edge}, measured_by, colour, anchors: [{pad, x_px, y_px}], features: [{name, kind, x_px, y_px, w_px,
   h_px, colour}]}`. `outline_px` is the PCB's outline in the picture. `usb_edge` is the picture's edge (`top`,
   `bottom`, `left` or `right`) where the USB socket is. Give two anchors or more at pads that are half the board apart.
   An anchor names its pad by the record's label (`RX`, not the silkscreen's `17`). A colour is `#rrggbb` in lower case,
   read off the picture. The kinds are `chip` (with `leads`: `four`, `top-bottom`, `left-right` or `none`), `usb`,
   `button`, `led`, `jst`, `fpc` and `passives` (with `count`, 2 by default, at most 64), `connector`, `crystal`, `inductor`,
   `hole` and `label` (with `text`, at most 24 characters). The file's order is the drawing's order, labels last.
   Leave out a silkscreen word that is a pad's label: spark draws those.
3. `parts.py --features-set FILE --part <board> --project . --dry-run`, then without `--dry-run`. Spark scales each
   axis by the outline and turns the picture so that the USB end is at the bottom. It never mirrors. It writes
   `physical.features` in mm in the board's frame and `physical.colour`, each with its source and `verified` false, and
   replaces the old ones whole. Its answer gives each anchor's offset from its pad.
4. Build. The build asks the kept picture first, then spark's drawing of the features (`features_picture`), then the
   pictogram. A record whose features cannot be drawn gets the pictogram, with a note under the drawing:
   `<board>: measured features not shown (<why>)`.

Only the pads and the mounting holes can be checked against the maker's dimension drawing, through the record. A
mirrored or wrongly scaled picture fails at the anchors. A chip or a socket is checked only against the outline and the
pads, so a wrong place that is near no pad passes, and no check can tell a bad measurement from a real part beside a
pad. Look at the drawing next to the maker's picture, and let the person judge it by eye.

| code | the features break this rule |
| --- | --- |
| `feature_outside` | a box lies more than 0.5 mm past the outline (a box up to 0.5 mm past is pulled back inside); a `usb` box may hang up to 2 mm past the USB edge, and is drawn there |
| `feature_over_pad` | a box covers part of a pad's circle (`physical.header.pad_mm`, else 1.5 mm across) |
| `feature_off_drawing` | an anchor lies more than 0.5 mm from its pad; or a `hole` lies more than 0.5 mm from the nearest place that `physical.mounting_holes` gives, its width and height differ by more than 0.5 mm, or its width differs from `mounting_holes.diameter_mm` by more than 0.5 mm |
| `feature_no_anchor` | fewer than two anchors at pads half the board apart, or an anchor that names no pad |
| `feature_pad_label` | a label's text is a pad's label, which spark draws, or holds a web address (`http` or `www.`) |
| `feature_unreadable` | the features file is no JSON, lacks a field, or names a picture that the record's `documents` do not hold |

## A board's joined pads

A board record may say which pads its maker's schematic joins inside the board ([P962](https://github.com/xmejkal/spark/issues/1380)), as `physical.header.joined_pads`: a fact whose value is a list of groups of pad keys, such as `[["3V3", "3V3_2"], ["GND1", "GND2"]]`. It lists every group the schematic shows, not the power pads only. `source` names the document, its sha256 and page, and `cites` (optional) names an entry of the record's `documents` that is not marked `kept: false`. Spark does not check the store for the file. The field is optional, and a board with no field behaves as before. The pin assigner reads it ([P971](https://github.com/xmejkal/spark/issues/1392)): it gives one group to one signal at most, and refuses a second one with `pin_taken`, naming the group. The steps read it too ([P1009](https://github.com/xmejkal/spark/issues/1468)). A point that holds two pads of one group runs one jumper, from the group's first pad by name, and its step names the others: `board 3V3 (joined to 3V3_2 inside the board)`. The drawing draws that one jumper. No other check reads it yet. `boards.py --validate` refuses a broken field. Write it with a dry run first:

```
parts.py --fact-set <board id> joined-pads.json --project . --dry-run
```

`joined-pads.json` is `{"joined_pads": {"value": [[...]], "verified": false, "source": "...", "why_it_matters": "...", "cites": {"document": "...", "at": "..."}}}`. Write `verified: true` only for a meter reading on the bench. A doubtful pad (`doubtful_pads`) is in no group.
