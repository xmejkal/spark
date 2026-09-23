# PCB layout — manual-editable + AI-designable (the fab stage)

After the schematic is verified, turning it into a board. The honest 2026 reality and the two
pipelines. Good practices are enforced by an encoded rule-gate, never by AI judgment alone.

## Honest capability (state it to the user)
AI is a **routing/cleanup assistant, not an autonomous board designer** (PCB-Bench: LLMs "cannot
yet generate manufacturable layouts"; the EEBench 69% number is circuit/SPICE, NOT layout).
Division of labor: human places major blocks + routes RF/USB/high-current; AI autoroutes the
rest + iterates on DRC. **Human review before fabrication is non-negotiable.**
Module-level boards are the sweet spot: the antenna and USB live inside the module, so the AI weak
spots are absent — AI can do a solid first pass, human refines.

## Good-practice rule-gate (this is what makes a layout trustworthy)
- Net classes: trace width by current, clearance, via size (wide power/motor, thin signal).
- `.kicad_dru` custom rules: thermal vias under a motor driver, clearances, keep-outs, pour rules.
- Copper pours / ground plane.
- DRC gate blocks on any violation: `kicad-cli pcb drc --format json --exit-code-violations`
  (headless; auto-loads the sibling `.kicad_dru`). Run on EVERY change, AI's or human's.

## Pipeline A — all-in-tscircuit (default for simple/module boards)
- Schematic = tscircuit code (source of truth).
- Layout, both editors, name-keyed so they don't clobber each other:
  - AI: write `pcbX`/`pcbY`/`pcbRotation`/`layer` props + `<copperpour>`/`<groundplane>` in the `.tsx`.
  - Human: drag in the runframe GUI → `manual-edits.json`, imported via `<board manualEdits={...}>`.
  - Only setup where AI + human layout edits both round-trip cleanly.
- Autoroute with knobs pinned (`<trace thickness>`, ViaGrid, `allowBlindAndBuriedVias=false`, pour)
  → DRC every export → order tscircuit→JLCPCB (emits Gerbers + BOM + CPL).
- CAVEAT: the tscircuit autorouter is beta and can emit shorts / unfabricable vias — DRC every
  time, eyeball Gerbers, never order unattended.

## Pipeline B — tscircuit → KiCad handoff (complex / high-reliability)
- `tsci export` KiCad project zip → KiCad.
- AI first pass via `pcbnew` Python / kicad-tools / kicad-mcp-pro: placement, net classes, pours.
- Autoroute via Freerouting (`.dsn` → `.ses`). Gate with `kicad-cli pcb drc` + `.kicad_dru`;
  kicad-happy for an AI review pass.
- Human refines in the KiCad GUI. Turn-based / single-writer (git handoff; `.kicad_pcb` does not
  3-way-merge). KiCad is a one-way terminal — re-export overwrites, so schematic changes = redo layout.

## Choosing
Module-level board with no RF/USB routing → Pipeline A. Complex/dense/high-current or want a real
routing GUI → Pipeline B. First prototype often needs no custom PCB at all (breadboard the modules);
the same tscircuit design feeds both. `tsci export -f step` → 3D model for the enclosure (Fusion).

## Key tools
tscircuit export/autorouter · kicad-cli (headless DRC gate) · Freerouting (open autorouter) ·
pcbnew SWIG Python / kicad-tools / kicad-mcp-pro (agent layout) · kicad-happy (AI design review).
