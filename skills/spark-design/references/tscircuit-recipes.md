# tscircuit recipes — proven on the smart-bin build (real parts, routing, local run)

Concrete, tested commands. These are the difference between a toy and a working board.

## Run locally (the toolchain needs no special registry)
tscircuit installs from PUBLIC npm and runs on the user's machine (or the desktop bridge):
```
npm install @tscircuit/cli bun      # public npm — always reachable
export PATH="$PWD/node_modules/.bin:$PATH"
tsci build board.tsx                # -> dist/<board>/circuit.json
```
Read routing/DRC state from `circuit.json` (don't trust the CLI pass/fail alone):
```
node -e "const c=require('./dist/board/circuit.json');const t={};c.filter(e=>/error/i.test(e.type)).forEach(e=>t[e.type]=(t[e.type]||0)+1);console.log(JSON.stringify(t),'traces:',c.filter(e=>e.type==='pcb_trace').length)"
```
Full fab package, all LOCAL (no network): `tsci export -f gerbers|glb|pcb-svg|schematic-svg`.
The Gerber zip already includes `bom.csv` + `pick_and_place.csv` → JLCPCB-ready.

## Routing: wire decoupling/bulk caps to the NET, never to a chip pin
tscircuit's autorouter applies an unsatisfiable ~1 mm max-length to a cap→pin trace and SKIPS
routing. Wire the cap's power pin to the power NET instead:
- BAD:  `<trace from=".DecoupX > .pin1" to=".SomeChip > .VCC" />`  (triggers 1 mm rule → 0 traces)
- GOOD: `<trace from=".DecoupX > .pin1" to="net.V33" />`          (routes fine)
Introduce a named net for each rail and tie the source pin to it once:
`<trace from=".XIAO > .V33" to="net.V33" />`. On the smart bin this took routing from 0 → 45
traces, 0 errors. Verify: `pcb_trace > 0` and `pcb_autorouting_error == 0`.

## Real footprints — three sources, all reachable without the tscircuit registry
1. **footprinter strings (built in, offline)** — real, parametric footprints:
   - Buttons: `pushbutton` (4-pad tactile; wire diagonal pads, e.g. pinLabels {pin1:"A", pin4:"B"}).
   - Headers / module pins: `pinrow3`, `pinrow4`, … ; a module outline+header: `headermodule6`,
     `headermodule8` (the trailing number = pin count).
   - Connectors: `jst_ph_2`, `jst_ph_3`, `jst_ph_4` (real JST-PH, with silk outline).
   - Passives: `0402/0603/0805`, `soic8`, `sot23`, etc. — already real via footprinter.
   Discover the set: `node -e "console.log(require('@tscircuit/footprinter').getFootprintNames().join(','))"`.
2. **A specific vendor/KiCad footprint** — fetch the `.kicad_mod` from GitHub (raw works even when
   git-clone is blocked; clone OUTSIDE a bridge-connected folder since lockfiles can't be unlinked
   there) then convert it to tscircuit:
   ```
   curl -sSo XIAO.kicad_mod "https://raw.githubusercontent.com/Seeed-Studio/OPL_Kicad_Library/master/Seeed%20Studio%20XIAO%20Series%20Library/XIAO-ESP32-C6-SMD.kicad_mod"
   tsci convert XIAO.kicad_mod          # -> XIAO.tsx (a <chip> with the real <footprint>)
   ```
   Rename the exported const to a valid identifier, then use it as a component that spreads props:
   `<XiaoRealFootprint name="XIAO" pcbX pcbY pinLabels={{ pin1:"MA_IN1", ... }} />`. Map pinLabels
   to the REAL pad order (XIAO 1-11 = D0-D10, 12=3V3, 13=GND, 14=5V; pads 23/24 = BAT±).
3. **The registry** (`tsci add seeed/xiao-esp32-c6`) — one-command real part + 3D, but needs
   `npm.tscircuit.com`, which a sandbox/bridge egress allowlist blocks. Use it only where the
   network is open (native Claude Code on the user's machine).

## Auto-solve placement (do this, don't make the user nudge coordinates)
A real footprint is often bigger than the placeholder → courtyard/overlap or off-board errors,
which SKIP routing. Fix automatically before routing:
- part off the board edge → move it inward by the reported overhang.
- courtyard overlap → move the smaller part clear of the larger (nudge the passive, not the module).
- decoupling cap → keep it near its IC but wired to the net (above).
Rebuild and confirm 0 placement/overlap errors, then routing runs.

## Honest limits (state them)
- The tscircuit registry + JLCPCB search are the only blocked pieces in a restricted sandbox;
  footprinter + GitHub-raw + `tsci convert` cover real parts without them.
- 3D from a converted `.kicad_mod` is the real footprint but a generic body until you also fetch
  the vendor STEP model.
- Always DRC and eyeball the routed board + Gerbers before ordering.
