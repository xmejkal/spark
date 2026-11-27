# S2: the maker's STEP models on the board (P1247 #1804)

Spike run on 2026-11-27 from about 16:45 to 16:51 CET, on the PO's Mac, with Fusion 2706.1.17 on the Personal license.

## Question

Can the STEP file of a maker sit in spark's assembly at the right place?

## Method

1. Two zips came from `dfimg.dfrobot.com`, linked on the [DFR0975](https://wiki.dfrobot.com/SKU_DFR0975_FireBeetle_2_Board_ESP32_S3) and [DFR0954](https://wiki.dfrobot.com/SKU_DFR0954_MAX98357_I2S_Amplifier_Module) wiki pages. The files stay out of git.
2. A script read the sizes and the pin places from the text of each file.
3. A script changed the two parts in `circuit.json`: `model_step_url`, `model_origin_position`, `rotation` and `position`. Writer `circuit-json-to-step` 0.0.68 got the files through `fsMap`.
4. The Fusion MCP imported the assembly as a new unsaved document. A script compared the round loops of each model with the pin holes in `circuit.json`.

## Result: not passed

| Pass line | `Mcu` (FireBeetle, DFR0975) | `Max98357aDfr0954` (amplifier) |
| --- | --- | --- |
| Shows in Fusion on the board, named | Met | Met |
| Pins meet the board holes within 0.2 mm | Not met. 29 of 32 are within 0.2 mm. The largest miss is 0.210 mm. | Met by calculation. With a turn of 90 degrees, 12 of 12 miss by 0.000 mm. |
| Offset and turn written down | Yes, but see the open question | Yes |

The amplifier file in Fusion had no turn. The turn of 90 degrees was calculated from the loops that Fusion reported. The file was not written again with it. At that turn, each of the 12 pin names printed on the model falls on the hole with the same name in spark's record.

| Part | Point of the maker's file | Goes to (board, mm) | Turn |
| --- | --- | --- | --- |
| `Mcu` | 0, 0, 8.3 | -11, -0.429, 0.8 | 180 degrees about X |
| `Max98357aDfr0954` | 0, 0, -1.6 | 14.7, 21, 0.8 | 90 degrees about Z, counterclockwise from above |

## Open question: which edge holds the long pin row of the FireBeetle

The maker's model and spark's record do not agree.

- The model, seen from the parts side with USB-C near: the battery socket is on the left edge. The 14-pin row is on the left, and the 18-pin row is on the right. The text on the model is not mirrored.
- spark's record (`physical.header.row_side`, the PO's look at the board on 2026-11-20): RX is on the left edge, with the battery socket. In the record, RX starts the 18-pin row.

Because of this, the pins matched only with the model upside down: parts face the carrier. One of three things is wrong: the model, the record's assignment of names to rows, or the match of board revisions. This spike does not decide it. The model's radio module carries the label `ESP-WROOM-32`, which is not the module of an ESP32-S3 board.

A look at the real board decides it: count the pins on the edge with the battery socket, and find the RX label.

## Other facts

- Each maker file holds one product named `Document` with unnamed solids (222 and 163). spark's assembly gave each its part name.
- The FireBeetle zip holds a RAR archive with the STEP file (24.9 MB) and a Rhino file (79 MB). It also holds a case from the maker: `top.stl` and `bottom.stl`.
- The pin pitch in the FireBeetle model is 2.5635 mm, not 2.54 mm. The rows are 23.0 mm apart, not 22.86 mm. This causes the miss of 0.210 mm.
- The amplifier model measures 18.0 x 18.0 x 7.13 mm. The record's box is 18 x 18 x 7.1 mm.
- The pages state no terms for the files.
- The writer made the 31 MB assembly in 2.0 s, with a peak of 485 MB of memory and no network use.
- The Mac has 8 GB. With this assembly open in Fusion, free memory fell to 23 % and swap reached 87 %.
