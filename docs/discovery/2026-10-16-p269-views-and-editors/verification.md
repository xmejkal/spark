# Verification
<!-- One line per ★ claim in brief.md; rejected claims stay. refuter: holds · partly · refuted · could not open, with
the line it read, verbatim. result: reproduced · not reproduced · rejected. keep: the words any summary of the claim
must carry (phrases separated by ;), or none; keep comes last on the line.
e.g. `- ★C3 · STATUS.md:84 · refuter: partly — "Shown on the C6, assumed for the S3" · reproduced how: re-read STATUS.md:84 · result: reproduced · keep: assumed for the S3` -->
- ★C1 · scripts/breadboard_drawing.py:22-24, 97-99 · refuter: partly — no cuts, no connectivity check, a PCB has SMD pads · reproduced how: read the lines, `Hole` with its `row` and `HoleLedger` · result: reproduced, narrowed · keep: untested beyond the breadboard <!-- REQUIRED:claims -->
- ★C2 · parts/*.json and boards/*.json, read with a script 2026-10-16 · refuter: partly — "only the FireBeetle" is wrong, some records hold pitch, the XIAO's pins are in data/wokwi-geometry.json · reproduced how: printed each record's footprint and physical keys · result: reproduced as rewritten · keep: per-pin x and y
- ★C3 · ~/Development/irrigation/node_modules/circuit-to-svg 0.0.433 exports convertCircuitJsonToSchematicSvg · refuter: holds in Node, 0.0.424, ISC, both SVGs rendered · reproduced how: found the export in its dist · result: reproduced · keep: not the perfboard
- ★C4 · tools/circuit-to-wokwi/ARCHITECTURE.md:50-53, scripts/breadboard.py:90 · refuter: partly — three ways, two differ on purpose · reproduced how: read both · result: reproduced as rewritten · keep: three ways
- ★C5 · scripts/check_spine.py:498, 658, 841, scripts/breadboard.py:427-430 · refuter: refuted as first written — merge.ts never runs in spark's build · reproduced how: read the unlink lines and merge.ts's presence · result: rejected as first written, rewritten · keep: a person's edit
- ★C6 · scrum/VISION.md:38 ("Hypothesis") · refuter: partly — wrong line, and P268 is held here · reproduced how: found the line · result: reproduced, pointer fixed · keep: n = 1
- ★C7 · licence files via the refuter, 2026-10-16 · refuter: holds, adds wokwi-boards with no licence · reproduced how: not reproduced by the lead, no web read · result: reproduced by the refuter only · keep: share-alike

## Agree / split
<!-- Where the lenses and the refuter agree, and where they split; each split becomes a question.
e.g. `- Split: Feasibility says a day, Risks says a week · Q4` -->
- Agree: one model fits every stage (the tech lead, the PO assistant); no record holds pins in mm (the data lens, the refuter); edit survival is the riskiest belief (the PO assistant, the tech lead, the refuter) <!-- REQUIRED:agree-split -->
- Split: what first: the tech lead's S0 base before any picture, against the PO assistant's breadboard SVG first by the one bar · Q2
- Split: the user lens wants two stages with one net highlighted in the first slice, the tech lead puts a viewer at S3 · Q2
