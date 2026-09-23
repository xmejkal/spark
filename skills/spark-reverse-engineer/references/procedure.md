# Reverse-engineering procedure — detail

## The fusion method
Reconstruct each net from the strongest available evidence, and tag its confidence:
- **[high]** confirmed by visible copper, OR forced by a datasheet pinout, OR must-exist by function.
- **[med]** inferred from function + partial trace evidence.
- **[low]** a guess (e.g. exact connector pin order) — call it out and let the bench decide.

Cross-check the three inputs against each other. Where vision and the datasheet disagree, the
datasheet pinout wins for the IC's own pins; where function and vision disagree, flag for the bench.

## Resistor code table (printed 3-digit SMD codes)
- `101` = 100 R, `151` = 150 R, `221` = 220 R, `331` = 330 R, `471` = 470 R
- `102` = 1 k, `472` = 4.7 k, `103` = 10 k, `104` = 100 k
- A 4-digit code (e.g. `1001`) = first 3 digits x 10^last. `R100` = 0.1 R (a shunt — a tell for
  low-side current sensing).

## Functional skeletons to expect (cheap sensor/actuator boards)
- MCU VDD/VSS; two MCU outputs -> H-bridge inputs; H-bridge outputs -> motor via connector.
- IR emitter driven (pulsed) through ~100-150 R from an MCU pin; IR receiver -> MCU analog pin.
- Buttons: MCU input -> GND, internal pull-up.
- Status LED: MCU pin -> ~330 R -> LED.
- Stall/home detection without a limit switch: low-side shunt into an ADC (tell = a sub-ohm
  resistor `R100`/`0R5` in the motor return), OR supply-rail-sag into an ADC divider, OR blind
  timed drive. Hunt for the shunt or divider to decide which.

## Which comparison matters
When the design goal is a brain transplant (replacing the MCU), do NOT try to match the new
design's logic wiring to the old chip's — they are different circuits. The one contract that must
match is the **connector/interface**: which pins are motor and which are battery. Confirm that
with continuity (which connector pins reach the H-bridge outputs vs the power rail).
