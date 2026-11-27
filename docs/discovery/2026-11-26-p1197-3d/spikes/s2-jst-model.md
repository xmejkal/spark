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

## Found on the way: the record's width is the 3-pin width

`parts/jst-ph-2-power-inlet.json` gives `body_mm` 7.9 x 5.8 mm and marks it verified. `parts/speaker-terminal.json` copies it and marks it not verified. The KiCad model measures 5.9 x 4.55 mm. Copies of JST's PH series tables give dimension B as 5.9 mm for 2 circuits. They give 7.9 mm for 3 circuits. One example is [Mouser's copy](https://www.mouser.com/datasheet/2/813/ePH-2487508.pdf). The tables were read as search result text, not as the drawing itself. The depth was not compared with a drawing.
