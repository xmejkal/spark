---
name: spark-reverse-engineer
description: Reverse-engineer a circuit board from photos — decode its connections and identify its parts. Use when the user shares a photo of a PCB and wants its schematic, netlist, or part identities reconstructed, or says "reverse engineer this board", "what's connected to what", "figure out this circuit from the photo", or reconstruct a mystery/OEM board. Fuses copper-trace reading, datasheet pinouts, and functional reasoning, then generates a bench test protocol to confirm.
---

# spark-reverse-engineer

Reconstruct a board's schematic and part identities from photos by fusing THREE inputs, and be
honest that the result is a hypothesis until confirmed at the bench.

## Workflow

1. **Get the clearest copper-side photo** — flat, top-down, well lit, filling the frame. Ask for
   a better shot if traces are unreadable. Note single- vs double-sided (single-sided = all
   connections traceable in one plane; watch for zero-ohm links / wire bridges).

2. **Identify components.** Chips (count pins, read/attempt markings), the connector, resistor
   codes (`101`=100R, `151`=150R, `331`=330R, `472`=4.7k...), capacitors, LEDs, buttons, sensors,
   and the silkscreen (board name, brand). List what is confirmed vs obscured.

3. **Fuse three inputs to reconstruct the nets:**
   - **Vision** — follow the visible copper (fat traces = power/motor; thin = signal).
   - **Datasheets** — research the exact ICs and pin them down (e.g. the RZ7899/TA6586 H-bridge
     family: inputs 1-2, GND 3, VCC 4, outputs 5-6 / 7-8). Convene research agents if available.
   - **Function** — research a typical reference design for the board's job (IR sensor bin, soap
     dispenser, etc.) and infer the connections that MUST exist.

4. **Produce a netlist hypothesis with a confidence tag per net** (high / med / low). NEVER
   present a photo-decode as certified.

5. **Make educated part guesses** — best-guess part with a confidence level and the single test
   that would confirm or refute each (see the test protocol).

6. **Encode as a tscircuit board and render** (use the spark-design skill) so the reconstruction
   is a real, buildable schematic.

7. **Generate a bench test protocol** from `references/test-protocol-template.md`, tailored to (a)
   confirm each reconstructed net and (b) distinguish the parts, and to the user's instruments —
   multimeter for static continuity/resistance, oscilloscope/logic analyzer for dynamic behaviour
   (rail-sag, pulse trains). Include probe-safety notes (scope input limits; x10 probe for >5 V;
   never feed >5.5 V into logic-analyzer inputs).

8. **On receiving the readings, lock the netlist** — correct any wrong nets and update the parts.

## Honest limits (state these)

- A photo yields a **hypothesis**, not ground truth — traces hide under parts and solder, and
  resolution limits fine traces. Multimeter continuity is the ground truth.
- If the board's brain is being **replaced**, the only meaningful comparison is the
  connector/interface (which pins are motor vs power) — not the old chip's logic wiring.

## References
- `references/procedure.md` — the fusion method, confidence scale, resistor-code table.
- `references/test-protocol-template.md` — the multimeter + scope/logic-analyzer test protocol.
