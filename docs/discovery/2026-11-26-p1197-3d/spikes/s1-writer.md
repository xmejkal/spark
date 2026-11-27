# S1: writer 0.0.68 in Fusion (P1247 #1804)

Spike run on 2026-11-27 from about 16:26 to 16:30 CET, on the PO's Mac, with Fusion 2706.1.17 on the Personal license.

## Question

Does `circuit-json-to-step` 0.0.68 give Fusion named parts and real board holes? The input is the `circuit.json` of spark's pinned build.

## Method

1. The pinned `tsci` 0.0.2600 built the amplifier fixture with box bodies (`tsci build board-t1.tsx --disable-parts-engine`).
2. `npm install --ignore-scripts circuit-json-to-step@0.0.68` ran in a scratch folder.
3. The first export failed, because a dependency imports `schematic-symbols` and no package declared it. `schematic-symbols@0.0.251` fixed it.
4. A short script called `circuitJsonToStep(circuitJson)` with no options. The script refused every network connection and logged it.
5. The Fusion MCP imported the file as a new unsaved document. A read-only script read the tree and the sizes. It also tested the center of every hole against the board body.

## Result: pass

| Pass line | Result |
| --- | --- |
| 4 items named as the parts | Met. `PCB`, `Mcu`, `Max98357aDfr0954`, `SpeakerTerminal`. The part numbers hold the ids. |
| The board is one body with a hole at every plated hole (46) | Met. One body of 53 faces. All 46 plated hole centers and the 1 via are open. A control point on the board is solid. |
| 3 sizes within 0.1 mm | Met. All differ by 0.000 mm. |
| The same through the open dialog | Met. The PO opened the file at about 17:34 CET. A read-only script found the same four names and sizes, one board body of 53 faces, and all 47 hole centers open. |

| Item | Faces | Size in mm |
| --- | --- | --- |
| `PCB` | 53 | 59.400 x 72.000 x 1.600 |
| `Mcu` | 6 | 25.400 x 60.000 x 1.600 |
| `Max98357aDfr0954` | 6 | 18.000 x 18.000 x 7.100 |
| `SpeakerTerminal` | 6 | 3.200 x 1.750 x 2.000 |

The file has 170 KB. The same fixture from the pinned writer 0.0.36 had 1.1 MB. The export took 0.4 s, made no network attempt, and wrote no `NaN` value.

## The speaker terminal is wrong

The terminal shows as a small box with the size of its footprint. It reaches 1 mm into the board. The pinned tool drew a connector body of 5.9 x 4.5 x 6.0 mm with two pins.

The fixture gives no body for this part, only the footprint name `jst_ph_2`. The package `jscad-electronics` 0.0.135, which the writer's dependency brings, returned 0 shapes for that name. The writer then drew the box. It reported no error. A part with no body of its own needs one from spark (a record's box or a kept vendor file).

## Cost and limits

- The scratch install holds 56 packages and one added package, 118 MB. The writer itself has 1.1 MB.
- One fixture, one board. A panel, a bottom-side part and a part with a vendor file were not run.
- The missing `schematic-symbols` package is a fault of the dependency tree. If spark uses this writer, it must name that package.
- The size table comes from the import through the API. The open dialog gave the same values.

Sources: [circuit-json-to-step](https://github.com/tscircuit/circuit-json-to-step) 0.0.68 from the npm registry, published 2026-11-24.
