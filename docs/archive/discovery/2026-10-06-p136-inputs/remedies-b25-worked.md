# B25, worked as an engineer would: the ToF wake line

> **An illustration for the product owner, not a decided fix.** Nothing here changes the board,
> the firmware, the card or either repo. It shows what "problem → remedy options → calculated
> parts" output looks like when it is worked from the sources. The choice between options is the
> PO's to make.

- Card: B25, [bin #19](https://github.com/xmejkal/sisuo-brain-transplant/issues/19) (read 2026-10-06).
- Inputs read: the bin at `8847eb8` (2026-10-05), spark at `8f7733d` (2026-10-06), and the datasheets
  in the person's store, found with `parts.py --kept` (listed under Sources, with checksums).
- Every number below comes from one script: `scratchpad/remedies/b25_calc.py`. Its full output is in
  `scratchpad/remedies/b25_calc_output.txt`. Re-run it to check any figure.

---

## 0. The answer in six lines

1. **The fault.** When asserted, the line reaches 1.892 V awake and 1.099 V asleep. The S3 needs 2.475 V.
   The cause is the carrier's 47 k to **2.8 V** working against the bin's 100 k to ground.
2. **The ceiling.** No passive arrangement can lift the line above the sensor's own 2.8 V. The best
   possible headroom over VIH is **0.325 V** nominal, and less at the corners. A real margin needs
   a 3.3 V source on the line: either a pull-up or an active stage.
3. **Recommended (option C):** set the sensor to active-low and add one PNP stage (MMBT3906, R_b 220 k,
   R_be 150 k). The existing 100 k pull-down moves to D12. The ESP still sees active-high, now
   rail-to-rail: **D12 ≥ 2.95 V** (≥ +0.55 V over VIH) when a hand is present, and ≤ 0.032 V
   (≥ +0.82 V under VIL) when idle. That holds at every corner computed: −20…70 °C, 3V3 3.2–3.4 V
   (and 3.6 V for the off state), AVDD 2.7–2.8 V, with or without the internal pull-down.
4. **It also cuts the sleep current by ~58 µA.** Active-low idles released, so R5's 59.6 µA stops,
   at a cost of 1.2 µA fed back into the carrier's 2.8 V rail.
5. **Runner-up (option A1):** zero new parts. Swap the 100 k for 1 MΩ and stop the internal
   pull-down on GPIO12. The margin is only +0.19 V nominal and +0.09 V worst case. It fails
   outright if 3V3 exceeds 3.42 V with AVDD at 2.7 V, and it keeps the 60 µA.
6. **The bench (B16) decides.** With C, D12 must read ≥ 3.0 V with a hand and ≤ 0.1 V without, and
   the carrier's VDD must stay ≤ 2.9 V while the chip sleeps.

---

## 1. The problem, re-derived from the sources

### The line as built

```text
  Pololu #2489 carrier                     bin board                         FireBeetle 2 S3
  VDD 2.8 V (on-board LDO)
     |
    R5 47k
     |
  GPIO1 ──R8 1k── pin 7 "GPIO1" ═══ ribbon ═══ SensorHeader.INT ──┬── D12 = GPIO12
  (open-drain)                                                     |    (internal 45k pull-down
                                                          TofIntPulldown 100k    armed before sleep)
                                                                   |
                                                                  GND
```

- **The sensor pin is open-drain.** ST: "Interrupt output. Open-drain. If used, it should be pulled
  high with 47 kΩ resistor" (VL6180X DocID026171 Rev 7, Table 2, p.10). The bin's board comment
  says the opposite, "The VL6180X's GPIO1 drives push-pull" (`board.tsx:381`). The driver's own
  docstring has it right (`smartbin/vl6180x.py:203`).
- **The carrier pulls it up to 2.8 V, not 3.3 V.** R5 is 47 k from VDD (the 2.8 V LDO output) to
  VL6180X pin 1 (GPIO1). R8 is 1 k in series out to header pin 7. There is **no level shifter on
  GPIO1**: Q1A and Q1B shift only SCL and SDA. R6 and R7 are the same pair for GPIO0/CE (Pololu
  schematic irs09a, read from the rendered drawing). Spark's record calls GPIO1's pull-up "R6"
  (`spark/parts/vl6180x-breakout.json:76`). That is wrong. It is R5.
- **The bin adds 100 k to ground** on the same node (`board.tsx:273`, wired at `board.tsx:384-385`).
  Nothing else on the FireBeetle touches GPIO12. Its only other connection is pin 7 (TCS) of the
  empty P2 display connector, with no pull resistor (DFR0975 schematic V1.3, p.1, connector P2).
- **The firmware asserts it high.** It writes `0x30` to SYSTEM__MODE_GPIO1 (`vl6180x.py:54,207-210`),
  because `interrupt_active_high=config.WAKE_ON_HIGH` (`assembly.py:88`) and `WAKE_ON_HIGH = True`
  (`config.py:183`). Bit 5 of that register selects the polarity (VL6180X p.55). Active-high on
  an open-drain pin means the sensor *lets go* to assert, so only the pull-up drives the line high.
- **The pull states.** Awake: `Pin(12, Pin.IN)` with no pull (`hardware.py:183-185`). Asleep: the
  internal pull-down is requested on every wake pin (`board.py:88-89`), and ext1 is armed
  `WAKEUP_ANY_HIGH` (`board.py:91-92`).
- **What the S3 promises.** VIH = 0.75 × VDD and VIL = 0.25 × VDD. IIH and IIL are ≤ 50 nA. The
  internal pulls are 45 kΩ typical (ESP32-S3 datasheet v2.2, Table 5-4, p.65). GPIO12 is
  powered from VDD3P3_RTC (Table 2-1, p.16).

### Today's numbers (script section `baseline`)

| state | formula | result | vs VIH 2.475 V |
|---|---|---|---|
| asserted, awake | 2.8 × 100/(100 + 47 + 1) | **1.892 V** | short by 0.583 V |
| asserted, asleep (if the 45 k pull survives) | 100 k ∥ 45 k = 31.03 k → 2.8 × 31.03/(31.03 + 48) | **1.099 V** | short by 1.376 V |
| idle (sensor sinking) | R5 current = 2.8/47 k | **59.57 µA**, for as long as the bin sleeps | reads 0, which is correct |

To clear 2.475 V by changing only the carrier, R5 + R8 would have to fall below 13.1 k against the
100 k, or below 4.08 k against 100 k ∥ 45 k. These are the card's figures, re-derived.

### Whether the internal pull-down survives sleep is unsettled. The remedy should not depend on it.

- ESP-IDF v6.1 says ext1 wake pins keep their configured pulls, "If we turn off the RTC_PERIPH
  domain, we will use the HOLD feature to maintain the pull-up and pull-down on the pins during
  sleep" ([sleep modes, ESP32-S3](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/system/sleep_modes.html)).
- MicroPython's sleep helper only enables ext0 and ext1. It configures no RTC pull itself
  ([`ports/esp32/modmachine.c:149-160` at a129b2f](https://github.com/micropython/micropython/blob/a129b2fba1a3348088c94d0462eef16d20874dea/ports/esp32/modmachine.c#L149-L160)).
- One commenter on [#17334](https://github.com/micropython/micropython/issues/17334) reports that a
  C6 wake pin armed `WAKEUP_ANY_HIGH` floated in sleep unless `hold=True` was set.

So the asleep figure is 1.10 V or 1.89 V. The bench can tell which (§6, step 0). Option C below
works either way.

### The ceiling: why resistors alone cannot give a real margin

With the sensor released, the line can never rise above the voltage feeding it: AVDD, nominally
2.8 V, and 2.7–2.9 V in ST's "optimum operating" range (VL6180X Table 23, p.46). The best possible
headroom is therefore 2.8 − 2.475 = **0.325 V** at nominal. That shrinks to 2.7 − 2.55 = 0.15 V if
the 3V3 rail runs 3 % high and AVDD sits at its minimum. Every passive option below lives under
that ceiling. Only a source tied to 3.3 V lifts it: a pull-up (option B) or a transistor (option C).

---

## 2. The facts each option is judged against

| fact | value | source |
|---|---|---|
| GPIO1 output type | open-drain, 47 k recommended | VL6180X Table 2, p.10 |
| GPIO1 absolute maximum | −0.5 to **3.6 V** (an absolute limit, not relative to AVDD) | VL6180X Table 22, p.46 |
| GPIO1 high-level input, max | **AVDD + 0.5 V** (operating) | VL6180X Table 24, p.47 |
| GPIO1 VOL | ≤ 0.4 V at 8 mA | VL6180X Table 24, p.47 |
| AVDD | 2.7–2.9 V optimum; 2.6–3.0 V functional; −20…+70 °C functional | VL6180X Table 23, p.46 |
| GPIO1 at power-up | output low, tri-stated during MCU boot; in hardware standby it sinks any pull-up | VL6180X p.15 |
| SYSTEM__MODE_GPIO1 | bit 5 = polarity; reset 0x20 = GPIO1 OFF (Hi-Z) | VL6180X p.55 |
| VL6180X standby | < 1 µA typ | VL6180X Table 13, p.35 |
| carrier VDD capacitance | C3 1 µF + C4 4.7 µF + C5 0.1 µF = 5.8 µF | Pololu schematic irs09a |
| Adafruit carrier | "Note there is no level shifting on this pin" (GPIO) | [Adafruit learn guide, Pinouts](https://learn.adafruit.com/adafruit-vl6180x-time-of-flight-micro-lidar-distance-sensor-breakout/pinouts) |
| S3 input levels | VIH 0.75 × VDD, VIL 0.25 × VDD, IIH/IIL ≤ 50 nA, RPU/RPD 45 k typ (at 3.3 V, 25 °C) | ESP32-S3 v2.2 Table 5-4, p.65 |
| S3 supply range | VDD3P3_RTC 3.0–3.6 V | ESP32-S3 v2.2 Table 5-2, p.64 |
| GPIO12 at power-up | 60 µs low-level glitch | ESP32-S3 v2.2 Table 2-2, p.18 |
| module deep sleep | 8 µA with RTC peripherals on, 7 µA off | WROOM-1 v1.1 Table 12, p.15 |
| ext0 + ext1 together | both applied in one sleep call; ext0 is refused only with touch or ULP wake | modmachine.c:149-160, modesp32.c:55-57, 144-146 (a129b2f) |
| `machine.wake_pins()` | reports GPIO and ext1 causes only, never ext0 | modmachine.c:313-331 (a129b2f) |
| MicroPython #17334 | open; C6, v1.25.0: `WAKEUP_ALL_LOW` leaves the pin stuck low after wake | [issue](https://github.com/micropython/micropython/issues/17334) |
| MMBT3906 | hFE ≥ 60 at 0.1 mA; VCE(sat) ≤ 0.25 V at 10 mA / 1 mA; VEBO 5 V; pins 1 = B, 2 = E, 3 = C | onsemi MMBT3906LT1/D Rev. 15, pp.1-2 |
| MMBT3906, typical curves | VBE(on) at 0.1 mA: 0.78 V at −55 °C, 0.61 V at 25 °C, 0.30 V at 150 °C; gain at −55 °C about half its 25 °C value | same, Figure 17 p.6 and Figure 13 p.5 |
| BSS84 | VGS(th) −0.8 min, −1.7 typ, −2.0 max V at −1 mA; +3 mV/°C | onsemi BSS84/D Rev. 5, p.2 |

**Assumptions, labelled as such.** These are not in any source read:
- The FireBeetle's 3V3 is taken as 3.3 V ± 3 % (3.2–3.4 V). The script also runs 3.6 V, the S3's
  own maximum.
- R5 and R8 are taken as ± 5 %, since Pololu does not state a tolerance. The bin's own resistors are 1 %.
- The S3 specifies VIH only "at 3.3 V, 25 °C". Scaling 0.75 × VDD to other rails applies its
  formula outside that stated condition.
- An *off* transistor's collector current is extrapolated from the 100 µA VBE point with the
  ideal-diode slope. It is an estimate, not a datasheet value.

---

## 3. The options

Each option is written to the same pattern: the change in words, the values with formula and
margin, the cost in parts, what changes in firmware, and what only the bench can confirm.

### Option 0: firmware only. Stop arming the internal pull-down on GPIO12.

- **Change.** In `board.deep_sleep`, request the pull-down for the OPEN pin only (`board.py:88-89`).
- **Values.** The asserted level becomes 1.892 V in sleep too. It still fails, by 0.583 V.
- **Verdict.** Necessary for options A and B, sufficient for nothing. It costs nothing.

### Option A: passive. Keep active-high and weaken or remove the 100 k pull-down.

- **Change.** Replace `TofIntPulldown` 100 k with 1 MΩ (A1), or 4.7 MΩ (A1b), or leave it unfitted
  (A2). Option 0 is part of this option: with the internal 45 k still on in sleep, A1 gives
  2.8 × 43.06/(43.06 + 48) = **1.324 V** and fails.
- **Formula.** V = (AVDD/R_s − I_leak)/(1/R_s + 1/R_pd), with R_s = R5 + R8 = 48 k and
  I_leak = 50 nA into the pin.
  - Worst case: AVDD 2.7 V, R_s + 5 % = 50.4 k, R_pd − 1 %.

| variant | asserted, nominal | asserted, worst | margin at 3V3 = 3.3 V (nom / worst) | at 3.4 V | 3V3 where the worst case fails | sensor unplugged |
|---|---|---|---|---|---|---|
| A1, 1 MΩ | 2.669 V | 2.567 V | +0.194 / **+0.092 V** | +0.119 / +0.017 V | 3.422 V | ≤ 0.050 V, reads 0 |
| A1b, 4.7 MΩ | 2.769 V | 2.669 V | +0.294 / +0.194 V | +0.219 / +0.119 V | 3.558 V | ≤ 0.235 V, reads 0 |
| A1c, 470 k | 2.538 V | 2.434 V | +0.063 / **−0.041 V** | fails | 3.245 V | ≤ 0.024 V |
| A2, none | 2.798 V | 2.697 V | +0.323 / +0.222 V | +0.248 / +0.147 V | 3.597 V | **floats** |

- **Idle current is unchanged.** R5 still sinks 59.57 µA. Current while asserted: 2.67 µA for A1.
- **Cost.** One resistor value. 1 MΩ 0603 1 % is LCSC C22935, a JLCPCB basic part at $0.0019.
- **Firmware.** Option 0, plus the record of resistor currents in `.spark/rules.json:37-41`:
  TofIntPulldown carries 2.7 µA while asserted, not 33 µA. The Wokwi chip drives a digital HIGH
  push-pull (`firmware/micropython/sim/chips/vl6180x.chip.c:69,174`), so no simulation can show
  this margin.
- **Bench confirms.** D12 reads ≥ 2.48 V asserted while asleep (the card's own proof). Measure
  3V3 and the carrier's VDD (Pololu pad 1) to turn the margin above into a measured one.
- **Verdict.** It works on paper with almost no margin. A1b buys 0.1 V by putting a 4.7 MΩ node
  inside a kitchen bin, which is a judgement against humidity and flux residue rather than a
  datasheet limit. A2 trades the margin for a floating pin whenever the ribbon is unplugged.

### Option B: keep active-high and add a pull-up from the INT net to the S3's 3V3

- **Change.** Add R_pu from the INT net to V33. Keep or remove the 100 k. Option 0 applies.
- **Formulas.**
  - Asserted: V_H = (3.3/R_pu + 2.8/48 k − I_leak)/(1/R_pu + 1/48 k + 1/R_pd).
  - Back-feed into the carrier's rail: I_bf = (V_H − 2.8)/48 k.
  - Sensor pin: V_N = 2.8 + I_bf × 47 k.
  - Idle, with the sensor sinking behind R8: V_H = 3.3 × (1 k ∥ R_pd)/(R_pu + 1 k ∥ R_pd).
- **Values at 3V3 3.3 V, AVDD 2.8 V, internal pull-down off** (script section `b`):

| R_pu | 100 k kept? | asserted (margin) | VL6180X pin | back-feed, asserted only | idle level (VIL margin) | sleep current through pull-up + R5 | unplugged |
|---|---|---|---|---|---|---|---|
| 10 k | yes | 2.968 V (+0.493) | 2.964 V | 3.50 µA | 0.297 V (+0.528) | **359.84 µA** | 3.00 V → **wake loop** |
| 10 k | no | 3.213 V (+0.738) | 3.205 V | 8.61 µA | 0.300 V | 359.57 µA | 3.30 V → wake loop |
| 22 k | yes | 2.730 V (+0.255) | 2.732 V | 0 | 0.142 V | 203.11 µA | 2.70 V → wake loop |
| 47 k | yes | 2.466 V (**−0.009**) | 2.473 V | 0 | 0.068 V | 128.34 µA | 2.24 V, undefined |
| 47 k | no | 3.051 V (+0.576) | 3.046 V | 5.24 µA | 0.069 V | 128.32 µA | 3.30 V → wake loop |
| 100 k | yes | 2.236 V (**−0.239**) | 2.247 V | 0 | 0.032 V | 92.25 µA | 1.65 V, undefined |
| 100 k | no | 2.961 V (+0.486) | 2.957 V | 3.34 µA | 0.033 V | 92.25 µA | 3.30 V → wake loop |

- **If the internal 45 k stays on in sleep**, only R_pu = 10 k survives: +0.062 V with the 100 k,
  +0.239 V without it. Every other row fails.
- **Absolute maximum.** The sensor pin is never above the 3.6 V absolute limit (Table 22). With
  10 k at the 3V3 3.4 / AVDD 2.7 corner it reaches 3.267 V, **above AVDD + 0.5 = 3.2 V** (Table 24),
  and back-feeds 12.06 µA. At 3.6 / 2.7 it reaches 3.429 V and back-feeds 15.51 µA. With 47 k
  (3.045 V) and 100 k (2.921 V), the pin stays within both limits at those corners.
- **Why every variant costs current all night.** Active-high on an open-drain pin idles in the
  *sinking* state, so any pull-up conducts for the whole sleep. That is +32.7 µA with 100 k and
  +300.3 µA with 10 k over today's 59.6 µA. And since a pull-up to 3.3 V makes an unplugged ribbon
  read 1, a loose connector becomes a wake loop.
- **Cost.** One 0603 resistor. Firmware: option 0, plus a guard that does not arm GPIO12 when the
  sensor stops answering.
- **Bench confirms.** The extra sleep current, the unplug behaviour, and the carrier's VDD while asserted.
- **Verdict.** Dominated by A and C. It buys margin with continuous current, and gives up the
  fail-safe on a loose ribbon.

### Option C (recommended): sensor active-low, plus a PNP stage that inverts and level-shifts

```text
                          V33 ───────────┬────────────┐
                                         │            │ E (pin 2)
                                     R_be 150k        Q1  MMBT3906 (PNP)
                                         │            │
  SensorHeader.INT ── R_b 220k ──────────┴────── B (pin 1)
  (net TOF_INT, from the ribbon)                      │ C (pin 3)
                                                      ├──────── D12 = GPIO12 (net TOF_WAKE)
                                                      │
                                            TofIntPulldown 100k  (moved from TOF_INT to TOF_WAKE)
                                                      │
                                                     GND
```

**The change in words.**
- Configure the sensor active-low (`0x10` in SYSTEM__MODE_GPIO1; the driver already has
  `_GPIO1_INTERRUPT_ACTIVE_LOW`, `vl6180x.py:55`). With no hand, GPIO1 is released and sits near
  2.8 V. With a hand, the sensor pulls it to 0 V.
- Q1's emitter goes to 3V3 and its collector drives D12. A hand turns Q1 on, so D12 rises to about
  3.3 V. No hand leaves Q1 off, and the 100 k holds D12 at 0 V.
- The ESP still sees active-high. `WAKE_ON_HIGH`, ext1 `ANY_HIGH`, the OPEN button and the
  2026-09-25 decision all stay as they are, and the low-level wake path of #17334 is never used.

**How the values were chosen** (script sections `c_search`, `c_detail:220,150`):
- Q1 must be firmly **on** in the cold. At −20 °C (VL6180X functional minimum), VBE(0.1 mA) is
  0.706 V by Figure 17. At 3V3 3.2 V, with the heaviest load (100 k ∥ 45 k, in case the internal
  pull survives), the forced β must be ≤ 20. That is a third of hFE(min) = 60, which leaves room
  for gain halving in the cold.
- Q1 must be firmly **off** in the heat. At +70 °C (VBE(0.1 mA) 0.498 V) and the extreme rail
  corner 3V3 3.6 / AVDD 2.7, D12 must stay ≤ 0.10 V.
- Among the pairs that pass, take the one that feeds the least current back into the carrier's 2.8 V.
- **R_b 220 k / R_be 150 k** is the lowest back-feed pair that passes with the internal pull-down
  on. R_b 470 k / R_be 220 k back-feeds less (0.68 µA) but reaches a forced β of 45.5 in the cold
  if the pull-down survives. It is the better choice only once the firmware stops arming the pull
  on GPIO12.

**Off (no hand).** The chain from 3V3 to the carrier's 2.8 V is R_be + R_b + R8 + R5 = 418 k.

| corner | back-feed I = ΔV/418 k | V_EB = ΔV × 150/418 | est. I_C at 70 °C | D12 | VIL margin |
|---|---|---|---|---|---|
| nominal 3.3 / 2.8 | 1.20 µA | 0.179 V | 2.1 nA | 0.005 V | +0.820 V |
| ±3 % 3.4 / 2.7 | 1.67 µA | 0.251 V | 23 nA | 0.007 V | +0.843 V |
| extreme 3.6 / 2.7 | 2.15 µA | 0.323 V | 0.27 µA | 0.032 V | +0.868 V |

- The VL6180X pin sits at 2.8 + 1.20 µA × 47 k = 2.856 V at nominal: under AVDD + 0.5 and under 3.6 V.
- The back-feed is the price. If *nothing* on the 2.8 V rail drew current between ranging bursts,
  it would raise VDD by at most 1.20 µA × 0.49 s / 5.8 µF = **0.101 V** before the next burst pulls
  it back. That stays inside ST's 2.6–3.0 V functional range, and at the 2.9 V edge of the optimum
  range. The sensor's own < 1 µA standby draw will absorb part of it. That is a bench measurement (§6).

**On (hand).** I_B = (V33 − VBE)/(R_b + R8) − VBE/R_be.

| corner | I_B | I_C needed (100 k / with 45 k) | forced β | D12 ≥ V33 − VCE(sat) 0.25 V | VIH margin |
|---|---|---|---|---|---|
| 3.2 V, −20 °C | (3.20 − 0.706)/221 k − 0.706/150 k = 6.58 µA | 29.5 / 95.1 µA | 4.5 / 14.4 | 2.950 V | **+0.550 V** |
| 3.3 V, 25 °C | (3.30 − 0.610)/221 k − 0.610/150 k = 8.11 µA | 30.5 / 98.3 µA | 3.8 / 12.1 | 3.050 V | +0.575 V |
| 3.4 V, 70 °C | (3.40 − 0.498)/221 k − 0.498/150 k = 9.81 µA | 31.5 / 101.5 µA | 3.2 / 10.4 | 3.150 V | +0.600 V |

- VCE(sat) 0.25 V is the datasheet maximum at 10 mA. At these 30–100 µA it is far lower: Figure 14
  shows about 0.08 V at 1 mA. So the D12 figures are floors.
- While asserted, the sensor sinks R5's 59.57 µA plus R_b's 12.17 µA, 71.75 µA in all. VOL is
  specified at 8 mA, so there is ample room.
- **Unplugged ribbon.** R_be ties base to emitter, V_EB = 0 and Q1 is off. D12 = 50 nA × 100 k = 0.005 V,
  so it reads 0 and there is no wake loop.
- **Sleep current.** R5 no longer sinks while idle, −59.57 µA. The chain adds +1.20 µA. Net **−58.4 µA**,
  about 1.43 mAh a day. For scale, that 59.6 µA is ~15 % of an estimated ~408 µA sleep budget:
  the sensor's ~340 µA at 500 ms (`config.py:106-107`), the module's 7-8 µA (WROOM-1 Table 12,
  p.15) and R5. All of these are unmeasured.
- **Power-up glitch.** GPIO12 drives low for 60 µs at power-up (Table 2-2, p.18). If the sensor is
  asserting at that moment (its GPIO1 powers up low, VL6180X p.15), Q1 sources into the low pin at
  most I_B × hFE, a few mA for 60 µs. That is harmless.
- **Sensor reset while asleep.** GPIO1 powers up low, which is "asserted" in active-low, so the S3
  wakes and the firmware reloads the sensor (`vl6180x.py:123-125`). After its boot GPIO1 is Hi-Z
  (reset value 0x20, p.55). How long that low phase lasts, and whether ext1 catches it, is a
  bench check.

**Cost in parts.** All are LCSC unit prices from a JLCPCB search on 2026-10-06; the total is about
$0.025 per board.

| part | value | LCSC | library | price |
|---|---|---|---|---|
| Q1 | MMBT3906LT1G (onsemi) | C53444 | extended | $0.0189 |
| R_b | 220 k 0603 1 % | C22961 | basic | $0.0015 |
| R_be | 150 k 0603 1 % | C22807 | basic | $0.0044 |
| TofIntPulldown | 100 k, moved | (existing) | | |

Board risks:
- **The SOT-23 pin mapping.** An earlier revision of this design carried a SOT-23 whose pads
  tscircuit mapped in the wrong order (`board.tsx:207-208`). Check B = 1, E = 2, C = 3 against the
  footprint (MMBT3906 p.1).
- **Wire the new parts through named nets** (`net.TOF_INT`, `net.TOF_WAKE`), never resistor to
  chip pin, which trips the autorouter (`board.tsx:368-370`).

**What changes in firmware, tests, simulation and checks.**
1. **Firmware.** Sensor polarity can no longer equal `WAKE_ON_HIGH`. Today one value drives both the
   sensor's register and the level the pin is read at (`proximity.py:162-168`, fed from
   `assembly.py:88`). Split it in two:
   - the level the ESP pin asserts at, which stays `WAKE_ON_HIGH`;
   - the polarity written to the sensor, which becomes active-low because the board inverts.
   The inversion is a fact about the board. State it once, for example `config.TOF_INTERRUPT_INVERTED = True`
   beside `WAKE_ON_HIGH` (`config.py:168-187`), and let a check compare it with the netlist.
   `board.py` needs no change: the internal pull-down is now harmless on D12.
2. **Tests.** `FakeVL6180X` derives the pin level from the polarity the driver wrote
   (`tests/fake_machine.py:361-362`). It must also apply the board's inversion, or the WAVE phase
   passes on a pin that cannot assert. That is the same trap `HANDOVER.md:183-187` records.
3. **Simulation.** The Wokwi chip ignores the polarity bit and drives INT push-pull
   (`vl6180x.chip.c:69,174`). It needs to honour bit 5, and the generated diagram needs the
   inverting stage between INT and GPIO12.
4. **Checks.** `wake-polarity.ts` compares only BtnOpen against `WAKE_ON_HIGH` (`wake-polarity.ts:58-62`).
   Extend it to the ToF path: the sensor polarity, times the stage's inversion, must equal the wake level.
   Add R_b's 12 µA and the 1.2 µA chain to `.spark/rules.json:37-41`. TofIntPulldown's 33 µA while
   asserted becomes true for the first time.
5. **Comments.** `board.tsx:380-383` ("drives push-pull") and `hardware.py:183-184` ("pulls its
   interrupt pin to its own 2.8 V") describe the old wiring.

**Bench confirms.** See §6.

**Verdict.** Recommended, for the reasons in §5.

#### C′: the same stage with a P-MOSFET (BSS84). Not recommended.

- **Change.** The gate goes straight to INT, with a 1 MΩ gate pull-up to 3V3 as the unplugged
  fail-safe. Back-feed 0.48 µA.
- **Values.**
  - Idle VGS = V_gate − 3V3 = **−0.477 V** at nominal: below the 0.800 V minimum threshold at 25 °C,
    and 0.188 V below it at 70 °C (0.800 − 45 × 3 mV = 0.665 V).
  - At the ±3 % corner, VGS is **−0.668 V**, at or above that 70 °C minimum. A minimum-threshold
    part may conduct, D12 rises, and the bin wakes. At the extreme corner, VGS is −0.859 V.
- **Verdict.** The BJT stage holds V_EB to 0.18–0.32 V by a resistor ratio, while the MOSFET has to
  live with the whole −0.8…−2.0 V threshold spread. Typical parts would work. The worst case is
  not guaranteed.

### Option D: active-low end to end. Read the line directly and move the OPEN button to GND.

- **Change.**
  - Remove the 100 k from INT.
  - Rewire OPEN to ground, with a pull-up (100 k to 3V3, or the internal one).
  - Set `WAKE_ON_HIGH = False`. The ext1 level becomes `WAKEUP_ALL_LOW`, which ESP-IDF aliases to
    ANY_LOW, an OR, on the S3 (`CLAUDE.md:130`).
  - Arm **no** internal pull on GPIO12.
  This reverses the 2026-09-25 wiring.
- **Values** (script `d_e`). Idle, with the sensor released, the line must read 1:
  V = 2.8 − 50 nA × 48 k = 2.798 V.

| 3V3 | VIH | margin, nominal | margin, worst (AVDD 2.7) |
|---|---|---|---|
| 3.2 V | 2.400 V | +0.398 V | +0.297 V |
| 3.3 V | 2.475 V | +0.323 V | +0.222 V |
| 3.4 V | 2.550 V | +0.248 V | +0.147 V |

- **Asserted.** About 0 V, margin +0.825 V. Idle current 0, back-feed 0.
- **With the internal pull-up on GPIO12** (which `board.py:88` would arm for `wake_on_high=False`),
  the margin rises to about +0.52…+0.61 V. But the back-feed becomes 4.28–6.43 µA, continuous, and
  could push the carrier's VDD up by as much as 5.35 µA × 0.49 s / 5.8 µF = **0.452 V** between
  bursts, above the sensor's 3.0 V functional maximum. So no pull on this pin.
- **Cost.** One fewer part; the button moves. Firmware: `WAKE_ON_HIGH`, the per-pin pulls, and
  `wake-polarity.ts` follows the new button rail.
- **Bench confirms.**
  - Whether a low-level ext1 wake works on the S3 under MicroPython. Issue #17334 is open on the C6
    and untested on the S3 (spark `boards/firebeetle2-esp32s3.json:288`).
  - The sleep current with GPIO12's input held at 2.8 V. That is 0.5 V below its own rail, and no
    datasheet figure covers it.
- **Verdict.** Electrically clean and free, but the margin is still the passive ceiling (+0.15 V
  worst), and it walks into exactly the path the project chose to avoid.

### Option E: mixed. ToF on ext0 (active-low), OPEN stays on ext1 (active-high).

- **Change.** Remove the 100 k from INT. Set the sensor active-low. Arm `esp32.wake_on_ext0(pin12, 0)`
  as well as `wake_on_ext1([pin13], ANY_HIGH)`. The S3 has ext0, a single pin at either level
  (spark `boards/firebeetle2-esp32s3.json:280-283`).
- **Values.** The same as D for the ToF line: idle 2.798 V, worst margin +0.222 V at 3.3 V and
  +0.147 V at 3.4 V. The button is unchanged.
- **Cost.** No parts. ext0 keeps the RTC peripherals powered: 8 µA against 7 µA, +1 µA (WROOM-1 Table 12).
- **Firmware.** `board.deep_sleep` arms two sources (MicroPython applies both, modmachine.c:149-160).
  `wake_pins()` never reports ext0 (modmachine.c:313-331), so the ToF wake would arrive through
  `_trigger_by_reading_pins` (`power.py:108-116`): it works, by fallback. Better made explicit
  with `machine.wake_reason()`.
- **Bench confirms.** The ext0 low-level wake on the S3, the reporting path, and the same 2.8 V-input
  sleep current as D.
- **Verdict.** Keeps the button decision, but still lives under the passive ceiling and on an
  untested low-level wake.

### Option F: change or rework the carrier

- **Another carrier.** Adafruit's breakout also has no level shifting on GPIO (learn guide). Any
  carrier that follows ST's 47 k to AVDD meets the same ceiling. No level-shifted GPIO1 carrier was
  found in one lookup.
- **Rework R5 on the Pololu.** With the 100 k kept and the internal pull off, R5 = 10 k gives
  2.523 V (+0.048 V) and R5 = 4.7 k gives 2.649 V (+0.174 V). But active-high then sinks 280 µA or
  596 µA all night.
- **Verdict.** No.

### Considered and dropped in a line each

- **ULP-FSM sampling the line with the ADC while asleep.** It would read 1.89 V as "high", but it
  costs the ULP's wake current and assembler code that MicroPython only reaches as `esp32.ULP`
  (`CLAUDE.md`, Power).
- **A single-gate translator IC** (an inverting buffer on 3V3 with thresholds below 2.8 V). This is
  a real alternative to C. It is not computed here because its datasheet was not read, and its
  input current with 2.8 V on a 3.3 V input is exactly the number that would decide it.

---

## 4. Side by side

All figures are at the worst computed corner unless marked.

| | asserted margin over VIH | idle margin under VIL | sleep current vs today | back-feed into 2.8 V | ribbon unplugged | parts | firmware | open risk |
|---|---|---|---|---|---|---|---|---|
| today | **−0.58 V** (asleep −1.38) | +0.8 V | — | 0 | reads 0 | — | — | it does not work |
| 0 | −0.58 V | +0.8 V | 0 | 0 | 0 | none | 1 line | still fails |
| A1, 1 MΩ | +0.092 V (3.3), +0.017 V (3.4) | +0.8 V | 0 | 0 | 0 | value change | 1 line + rules | margin |
| A2, none | +0.222 V (3.3), +0.147 V (3.4) | +0.8 V | 0 | 0 | **floats** | −1 | 1 line | margin, floating pin |
| B, 100 k up, no down | +0.486 V (nominal) | +0.79 V | **+33 µA** | 3.3 µA asserted | **wake loop** | +1 | 1 line + guard | current, wake loop |
| **C, PNP 220 k/150 k** | **+0.550 V** | **+0.82 V** | **−58.4 µA** | 1.2 µA (≤ 0.10 V creep) | reads 0 | +3 (~$0.025) | polarity split, fake, sim, check | SOT-23 mapping, back-feed |
| C′, BSS84 | rail-to-rail | not guaranteed at the ±3 % corner | −59.1 µA | 0.48 µA | reads 0 | +2 | as C | threshold spread |
| D, all active-low | +0.147 V (3.4) | +0.8 V | −59.6 µA | 0 | GPIO12 floats * | −1 | polarity, button | #17334, 2.8 V input |
| E, ext0 + ext1 | +0.147 V (3.4) | +0.8 V | −58.6 µA | 0 | GPIO12 floats * | −1 | two sources | #17334 on ext0 |

\* In D and E, nothing defines GPIO12 once the ribbon is out, because a pull-up there is exactly
what feeds current back into the carrier. A 1 MΩ pull-up to 3V3 would define it for 0.48 µA of
back-feed: the same topology as C′'s gate pull-up, computed there. That variant was not carried
further.

C's idle margin is D12 ≤ 0.032 V against VIL ≥ 0.825 V, so at least +0.82 V.

---

## 5. Recommendation, and what it is not

**I would recommend option C, with Q1 = MMBT3906, R_b = 220 k, R_be = 150 k, and the 100 k moved to D12.**
1. **It is the only option with margin that does not depend on rails, temperature, or the open
   question of the internal pull-down.** D12 is at least 0.55 V above VIH and at least 0.82 V below
   VIL at every computed corner. Every passive option lives under the 0.325 V ceiling. At a 3 %
   high rail with AVDD at its minimum, the best of them (A2, D, E) keeps +0.147 V, A1 keeps
   +0.017 V, and A1c goes negative.
2. **It leaves the sleep current lower than today.** It removes R5's 60 µA for 1.2 µA of back-feed.
3. **It keeps every decision already made:** OPEN active-high, ext1 `ANY_HIGH`, no low-level wake
   path, no use of #17334's territory.
4. **It keeps the fail-safe on a loose ribbon,** and takes GPIO12 off the ribbon altogether: the
   ESD exposure moves to a 220 k base resistor.

What it costs:
- three parts;
- a firmware split of one setting into two;
- a test-fake update, a sim-chip update and a check extension;
- a SOT-23 footprint, which has bitten this design once already, on paper.

**If the PO prefers no new parts,** A1 (1 MΩ, plus option 0) is the honest runner-up. It is within
spec by 0.09 V at 3.3 V and fails above a 3.42 V rail. Measure that on the bench before trusting it.

**What this is not.** It is not a decided fix, not a design review of the whole board, and not
proven: nothing has touched hardware. The transistor's off-state currents are extrapolations from a
typical curve, the 3V3 tolerance and Pololu's resistor tolerance are assumptions, and the
carrier's LDO behaviour under 1.2 µA of reverse current is unknown. The card's own proof criterion,
"D12 measures at least 2.48 V while a hand holds the sensor's interrupt asserted", is what option C
is expected to meet with about 0.5 V to spare.

---

## 6. What only the bench (B16) can confirm, in order

0. **Before any change: which asleep figure is real.** With today's firmware, hold a hand at the
   sensor while the chip sleeps and measure D12. About 1.10 V means the internal pull-down survived
   sleep; about 1.89 V means it did not. This settles the card's open question at no cost.
1. Measure the rails the margins rest on: 3V3 at the FireBeetle header, and VDD at Pololu pad 1.
2. **Option C on a breadboard.** Measure D12 asleep and awake:
   - with no hand: expect ≤ 0.1 V;
   - with a hand: expect ≥ 3.0 V.
3. Measure the carrier's VDD over several ranging periods while the chip sleeps. It should stay
   ≤ 2.9 V; this is the back-feed check.
4. Measure the sleep current with option C against today's wiring. Expect about 58 µA less.
5. Unplug the ribbon while the chip sleeps: there should be no wake, and no wake loop.
6. Interrupt the carrier's VIN for a moment while the chip sleeps. The bin should wake once,
   reload the sensor (`FRESH_OUT_OF_RESET`) and re-arm.
7. Optional: repeat steps 2 and 5 cold (a freezer, about −18 °C) and warm.

---

## 7. What a tool could have done here, and what it could not

This answers part of the question that prompted this note.

- **Mechanical, given the facts.**
  - The divider and threshold check: a node's pull-ups, pull-downs and their rails, compared with
    the receiver's VIH and VIL.
  - The absolute-maximum check on the sensor pin.
  - The back-feed current.
  - The sleep current of the idle state.
  Every input is already in a record or a datasheet table: R5, R8 and AVDD in the carrier record;
  VIH = 0.75 × VDD in Table 5-4; the 100 k in the netlist.
- **Spark already does the mirror image.** `pull_conflicts` (`spark/scripts/parts.py:1284-1316`)
  takes a board pull-down against a *module's* own input pull-up, and compares the result with
  *that module's* `input_high_threshold_v`. That is the L9110S case, P81/B11. B25 is the other
  direction: a module's *output* pull-up, read by the *host*. The check would need three things
  spark does not record as numbers today:
  - the host's VIH and VIL (the board record has `io_volts` but no input thresholds,
    `boards/firebeetle2-esp32s3.json:413-421`);
  - the carrier pull-up's rail and series resistor (the record states 47 k, names it R6, and keeps
    the rail in prose, `vl6180x-breakout.json:72-79`);
  - the bin's pull-down, which lives in the netlist rather than the part's `host_parts`.
- **A known pattern.** "An open-drain line crossing from a lower rail into a VIH = 0.75 × VDD input"
  has a short standard list of remedies: weaken the opposing pull, pull up to the receiver's rail,
  invert the polarity, add a stage, use a translator. Producing the list is retrieval, not
  invention.
- **A constrained search.** Choosing R_b and R_be is the 81-pair search in `b25_calc.py`, against
  stated corners.
- **Judgement, which stays with the PO.**
  - Whether 0.09 V is acceptable.
  - Whether three parts and a test-fake rewrite are worth 0.45 V more margin and 58 µA less.
  - Whether to reopen the 2026-09-25 active-high decision.
  - Which assumptions (rail tolerance, temperature range) to design to.

---

## Sources

**The bin** (`~/Development/smartbin-local`, commit `8847eb8`):
- `board.tsx:207-208, 264-273, 368-370, 379-387, 412-426`
- `mcu-pins.ts:19`
- `.spark/rules.json:37-41`
- `firmware/micropython/config.py:27, 29, 60, 106-107, 168-187`
- `smartbin/board.py:64-93`
- `smartbin/hardware.py:182-185`
- `smartbin/vl6180x.py:54-55, 86, 123-125, 194-216`
- `smartbin/proximity.py:162-179`
- `smartbin/assembly.py:84-92`
- `smartbin/power.py:89-116`
- `tests/fake_machine.py:273, 361-362`
- `sim/chips/vl6180x.chip.c:69, 174`
- `tools/circuit-to-wokwi/lib/checks/wake-polarity.ts:58-62`
- `HANDOVER.md:183-187`
- `CLAUDE.md:128-137`
- Card B25: [xmejkal/sisuo-brain-transplant#19](https://github.com/xmejkal/sisuo-brain-transplant/issues/19).

**Spark** (`~/Development/spark`, commit `8f7733d`):
- `parts/vl6180x-breakout.json:20-29, 72-79, 123-145`
- `boards/firebeetle2-esp32s3.json:280-289, 413-421`
- `scripts/parts.py:1284-1316`

**Datasheets in the person's store** (`~/.local/share/spark/sources/<sha256>/`):

| document | sha256 |
|---|---|
| ST VL6180X datasheet, DocID026171 Rev 7 | `87e1b09668160d714276cdb093a41e7bf18120c81c25888a309e8fcfdc6a6724` |
| Pololu VL6180X carrier #2489 schematic, irs09a | `5cac2a7c8134d20721b5e008387485b842eb0059a15397b3e8df31ecbe76801f` |
| Espressif ESP32-S3 Series Datasheet v2.2 | `2d5a7cb7fd559d8d972bd88db32669c0196d23f22d7afaafb0f63d099b589a3f` |
| Espressif ESP32-S3-WROOM-1 datasheet v1.1 | `bc430d667d7bde6676cbdbc9053429c79c0c43a27ebd7dd06834f605b878b76b` |
| DFRobot DFR0975 schematic V1.3 | `4062428ab603999097297ea1773e9fefcc4e6f0fd8fe9acf55a3503b90f89406` |

**Fetched for this note** (kept in the scratchpad, not the store):

| document | URL | sha256 |
|---|---|---|
| onsemi MMBT3906LT1/D, Rev. 15 (September 2026) | https://www.onsemi.com/pdf/datasheet/mmbt3906lt1-d.pdf | `7b8905aa3483dad8f7d41caeb216d7e60f288c81ff365109443d753d585c775e` |
| onsemi BSS84/D, Rev. 5 (October 2021) | https://www.onsemi.com/pdf/datasheet/bss84-d.pdf | `bcbbf6ff184955e983c9964941ed40dd83792f8adab6b993a7d2450e9ae4cde6` |

**Pages read:**
- ESP-IDF sleep modes (stable, v6.1): https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/system/sleep_modes.html
- MicroPython at `a129b2fba1a3348088c94d0462eef16d20874dea` (2026-10-02): `ports/esp32/modmachine.c`, `ports/esp32/modesp32.c`
- MicroPython issue #17334, read 2026-10-06
- Adafruit VL6180X learn guide, Pinouts page
- JLCPCB/LCSC parts search, 2026-10-06: C53444, C22961, C22807, C22935
