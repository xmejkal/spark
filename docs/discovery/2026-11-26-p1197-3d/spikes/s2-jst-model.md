# Follow-up to S1 and S2: KiCad's JST model for the speaker terminal (P1247 #1804)

Trial run on 2026-11-27 at about 17:44 CET, at the PO's request, with Fusion 2706.1.17.

## Why

In S1, writer 0.0.68 drew the speaker terminal (`jst_ph_2`) as a small box of its footprint's size, sunk into the board.

## Method

KiCad 10 on the PO's Mac holds `Connector_JST.3dshapes/JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical.step`. A script gave that file to the writer through `fsMap`. It put the file's pad 1 at the board's pin 1 (13.7, 5.1, 0.8) with no turn. The KiCad file stays out of git. Fusion imported the assembly through its API, and a script read it.

## Result: it fits

| What | Reading |
| --- | --- |
| Name in Fusion | `SpeakerTerminal`, one body of 93 faces |
| Pins against the two board holes | each pin center misses by 0.031 mm |
| Height | the housing stands on the board, 6.0 mm above it. The pins reach from 3.4 mm below the housing |
| Size of the whole part | 5.92 x 4.57 x 9.42 mm |
| Network use by the writer | none |

So a part without a maker's file can take its model from a KiCad install, with the same placement fields as in S2.

Which pin is plus is not settled: the speaker terminal's record marks its pin order as not verified.

## All three models together, at about 17:45 CET

A second file held both DFRobot models and the KiCad model. The script mirrored the FireBeetle's 32 holes in `circuit.json`, as P1334 #1913 asks. It then placed the FireBeetle with parts up and a turn of 180 degrees about Z. The amplifier had a turn of 90 degrees about Z.

| Part | Pins within 0.2 mm of the holes | Largest miss |
| --- | --- | --- |
| `Mcu` | 29 of 32 | 0.210 mm |
| `Max98357aDfr0954` | 12 of 12 | 0.000 mm |

- The amplifier's pass line of S2 is now met in a file that ran.
- The USB-C socket of the FireBeetle is missing from its place. The script hid the 22 loose surface pieces that the writer leaves at the root. A case design needs that socket, so spark must keep those surfaces with their part.
- A record's box is no stand-in for a case: the FireBeetle's box was 1.6 mm tall, and the maker's model is 8.3 mm.
- At about 17:47 CET a script moved the 22 loose pieces with their parts: 19 for the FireBeetle, 3 for the amplifier. Each got the same turn and move as its part. The USB-C socket (8.95 x 7.75 x 4.26 mm) then sat at the USB edge. So the maker's file holds it, and the writer loses its place.
- The model's circuit board measures 25.400 x 60.000 x 1.600 mm, as the record does. Its pin pitch (2.5635 mm) and its radio module label (`ESP-WROOM-32`) differ from the real board. The file is dated 2023-10-20 and names no hardware version.
- Fusion with this file left 22 % of memory free, and swap reached 87 %.

## Found on the way: the record's width is the 3-pin width

`parts/jst-ph-2-power-inlet.json` gives `body_mm` 7.9 x 5.8 mm and marks it verified. `parts/speaker-terminal.json` copies it and marks it not verified. The KiCad model measures 5.9 x 4.55 mm. Copies of JST's PH series tables give dimension B as 5.9 mm for 2 circuits. They give 7.9 mm for 3 circuits. One example is [Mouser's copy](https://www.mouser.com/datasheet/2/813/ePH-2487508.pdf). The tables were read as search result text, not as the drawing itself. The depth was not compared with a drawing.
