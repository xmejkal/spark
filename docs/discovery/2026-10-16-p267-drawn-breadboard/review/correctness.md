# PR #303 correctness lens (Sonnet), 2026-10-16

Static reading only: plan mode was on, so the lens ran no reproduction. The lead's own runs confirm or reject each
row in `docs/observations/INDEX.md` (AT268 to AT271).

1. No short circuit found. Part pins, jumper rows and free rows all need a row with no claimed hole, and a resistor
   leg shares a row only with its own point. The pinned branch of `_fit` does not check the pinned hole's row against
   the part's other legs, which is unreachable for a resistor.
2. No mismatch between wires and steps: jumpers only for a board pad's free row and a non-resistor join.
3. Medium-low: `_place_resistors` places resistors in order of first appearance, so a resistor pinned to a later
   resistor's row raises "is joined before it is placed" for a drawable build.
4. Low: `_to_ohms` accepts `[\d.]+`, so "1.2.3Ω" raises ValueError, which `breadboard.main` does not catch.
5. Low: `write()` removes the old drawing only on NotDrawn, so any other error leaves a stale `breadboard.json`.
6. Test gaps: the motor "not drawn" case, a stale `breadboard.json`, two resistors, a resistor pinned to another.
