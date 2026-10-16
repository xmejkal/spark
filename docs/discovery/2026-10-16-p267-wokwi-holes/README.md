# P267: Wokwi's breadboard holes, measured

> Measured in Chrome on https://wokwi.com/projects/new/micropython-esp32 on 2026-10-16. All numbers are in Wokwi px
> (96 per inch), from the breadboard's top-left corner. A leg that sits over a hole connects, with no connection
> entry. Each part turns about the center of its size.

## How it was measured

You put parts into a new, unsaved Wokwi project by setting `diagram.json` in the page's editor. The editor draws an
8 x 8 px overlay over each pin, and `style.left + 4` and `style.top + 4` give the pin's center in diagram px. Wires
to named holes (`bb1:tp.1` and others) gave the hole names: Wokwi draws each wire's path from the hole's center.

## The half breadboard (`wokwi-breadboard-half`)

| what | x | y |
| --- | --- | --- |
| column n (1 to 30), rows a to j | 26 + 9.6 (n - 1) | |
| rows a, b, c, d, e (`{n}t.a` to `{n}t.e`) | | 51, 60.6, 70.2, 79.8, 89.4 |
| rows f, g, h, i, j (`{n}b.f` to `{n}b.j`) | | 118.2, 127.8, 137.4, 147, 156.6 |
| rail hole k (1 to 25) | 34 + 9.6 (k - 1) + 9.6 floor((k - 1) / 5) | |
| rails `tp`, `tn`, `bp`, `bn` | | 12.3, 22.3, 186.3, 196.3 |

The pitch is 9.6 px (2.54 mm). Row e and row f are 28.8 px apart, three pitches, across the center gap. The rail
holes come in five groups of five, with one empty pitch between groups. Measured ends: `1t.a` (26, 51),
`15t.c` (160.4, 70.2), `30b.j` (304.4, 156.6), `tp.1` (34, 12.3), `tp.25` (302.8, 12.3), `tn.1` (34, 22.3),
`bp.1` (34, 186.3), `bn.1` (34, 196.3).

## The parts' pins and the turn

Pin centers in px from the part's top-left, unturned, and the center that a turn goes about:

| type | pins | center |
| --- | --- | --- |
| `board-xiao-esp32-c6` | D0 (5.418, 18.635) to D6 (5.418, 76.235) and D7 (62.4, 76.235) to 5V (62.4, 18.635), 9.6 apart | (34, 44) |
| `wokwi-led` | A (25, 42), C (15, 42) | (25, 20) |
| `wokwi-resistor` | 1 (0, 5.65), 2 (58.8, 5.65) | (29.5, 5.5) |
| `wokwi-pushbutton` | 1.l (0, 13), 2.l (0, 32), 1.r (67, 13), 2.r (67, 32) | (33.5, 24.5) |

The XIAO's offsets equal Wokwi's `board.json` in mm times 96 / 25.4, in the same order
(wokwi/wokwi-boards, `boards/xiao-esp32-c6/board.json`, read 2026-10-16, sha256
e5200e012416f096bcc188f9cb4fe8f292cd9d973dc0249513624bf5768856a8). Its center is half of 68 x 88 px, Wokwi's
18.1 x 23.4 mm rounded to whole px, the same size as the board record's `wokwi_size_px`.

A turn of 90 degrees maps a pin (x, y) to (cx + cy - y, cy - cx + x), with (cx, cy) the center. Each part was read at
0 and 90 degrees, and every pin agrees with this rule. The LED, resistor and button pin names are wokwi-elements' names as the plan's research read
them, matched to the overlays by position, not read from the page. The center comes from the turn, not from a published size.

## A leg over a hole connects

`connection-test.diagram.json` (sha256 4cae3833904ccf537d8b2c7a9f9c941a1d9756b6dc6f143c320b03a87a5a9cf3) puts the
XIAO, turned 90 degrees, with its pins in rows b and f of columns 3 to 9. A 330 Ω resistor runs from 7b.i (the
3V3 column) to 13b.i, and the LED's anode is in 13b.h and its cathode in 12b.h. The only connection entry is a
jumper from 12b.j to 8b.j, the GND column. The simulator ran, and the LED lit (`connection-test.png`). So spark
writes no connection entry for a leg in a hole, only for a jumper.

Each pin lies within 1.2 px of its hole: the XIAO's two pin rows are 57 px apart, not 57.6, and the resistor's legs
are 58.8 px apart, not 57.6.
