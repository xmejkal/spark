# S0: which name Fusion shows (P1247 #1804)

Spike run on 2026-11-27 at about 16:23 CET, on the PO's Mac, with Fusion 2706.1.17 on the Personal license.

## Question

Writer `circuit-json-to-step` 0.0.68 gives each product an id and a name that differ. Which one does Fusion show?

Source of the shape: `lib/assembly.ts` of [tscircuit/circuit-json-to-step](https://github.com/tscircuit/circuit-json-to-step) on its main branch, read on 2026-11-27.

## Method

A trial script rewrote an assembly STEP of spark's amplifier fixture. It set four products to the shape of the writer, for example:

```
PRODUCT('cad_component_0','Mcu','',(#3));
NEXT_ASSEMBLY_USAGE_OCCURRENCE('cad_component_0','Mcu','',#22924,#22949,'Mcu');
```

The root product had the name `Combined Assembly`. The Fusion MCP imported the file as a new unsaved document. A script then read the tree.

## Result: pass

| Item in the Fusion tree | Component name | Part number | Bodies |
| --- | --- | --- | --- |
| `PCB:1` | `PCB` | `pcb_board_0` | 44 |
| `Mcu:1` | `Mcu` | `cad_component_0` | 1 |
| `Max98357aDfr0954:1` | `Max98357aDfr0954` | `cad_component_1` | 1 |
| `SpeakerTerminal:1` | `SpeakerTerminal` | `cad_component_2` | 5 |

Fusion shows the product name in the tree. It keeps the product id as the part number.

## Limits

- This file was shaped by hand. The writer itself did not run (S1).
- The two names in the file, on the product and on the placement, were the same. This spike does not show which of the two Fusion reads.
- The board still shows 44 bodies, because the geometry did not change.
- The import went through the API, not the open dialog.
