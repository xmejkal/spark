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
| Offset and turn written down | Yes, but for a mirrored footprint (see below) | Yes |

The amplifier file in Fusion had no turn. The turn of 90 degrees was calculated from the loops that Fusion reported. The file was not written again with it. At that turn, each of the 12 pin names printed on the model falls on the hole with the same name in spark's record.

| Part | Point of the maker's file | Goes to (board, mm) | Turn |
| --- | --- | --- | --- |
| `Mcu` | 0, 0, 8.3 | -11, -0.429, 0.8 | 180 degrees about X |
| `Max98357aDfr0954` | 0, 0, -1.6 | 14.7, 21, 0.8 | 90 degrees about Z, counterclockwise from above |

## Found: spark's record puts the FireBeetle's long pin row on the wrong edge

DFRobot's sources agree with the model, and spark's record does not. All views below look at the parts side with USB-C near.

| Source | Battery socket | 14-pin row | 18-pin row, with `RX` at the far end |
| --- | --- | --- | --- |
| Maker's STEP model | left | left | right |
| [Wiki](https://wiki.dfrobot.com/dfr0975) pinout diagram (drawn for V1.0, shown there with USB-C far) | left | left | right |
| Wiki board pictures, "V1.1 and earlier" and "V1.2 and later" (shown with USB-C far) | left | left | right |
| spark's `physical.header.row_side` and footprint | left | right | left |

- The maker's schematic V1.3 shows an 18-pin header with `IO44/RXD0` at pin 1, and a 14-pin header. spark's order of names within each row agrees with it.
- The PO counted 14 pins on the battery socket edge of the real board on 2026-11-27. The PO also read `RX` on that edge, which DFRobot's pictures do not show.
- The record's `row_side` is marked verified, from the PO's look on 2026-11-20. It says that `RX` and the battery socket are on the left edge. No DFRobot source shows that.
- The label `ESP-WROOM-32` on the model also shows on DFRobot's "V1.2 and later" picture, so it is no sign of a wrong model.

The effect: the footprint and the breadboard sheet for this board mirror the two rows. Do not wire from them until the record is corrected.

The pins in this spike matched the footprint only with the model upside down, because the footprint is mirrored. If the rows are corrected, the model fits with parts up. It then needs a turn of 180 degrees about Z. The largest miss stays 0.210 mm. This placement is calculated and was not run.

## Other facts

- Each maker file holds one product named `Document` with unnamed solids (222 and 163). spark's assembly gave each its part name.
- The FireBeetle zip holds a RAR archive with the STEP file (24.9 MB) and a Rhino file (79 MB). It also holds a case from the maker: `top.stl` and `bottom.stl`.
- The pin pitch in the FireBeetle model is 2.5635 mm, not 2.54 mm. The rows are 23.0 mm apart, not 22.86 mm. This causes the miss of 0.210 mm.
- The amplifier model measures 18.0 x 18.0 x 7.13 mm. The record's box is 18 x 18 x 7.1 mm.
- The surface shells of the maker files did not stay with their part. The two files hold 19 and 3 of them, and Fusion showed 22 loose bodies at the root. A view of one part alone showed a USB connector and small pieces far from it. The writer moves only the solids with the part.
- The pages state no terms for the files.
- The writer made the 31 MB assembly in 2.0 s, with a peak of 485 MB of memory and no network use.
- The Mac has 8 GB. With this assembly open in Fusion, free memory fell to 23 % and swap reached 87 %.
