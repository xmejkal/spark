# Electrical maths in `answer.md` and `b25-worked-remedy.md`: verdicts

*Adversarial check, 2026-10-06.* Every voltage, current, margin and component value in the two
documents was recomputed from the datasheet pages they cite, and every absolute-maximum claim was
checked against its table. Line numbers below are those of the two files as they stood when this
check ran (`answer.md`, 576 lines; `b25-worked-remedy.md`, 588 lines). The bin was read at
`8847eb8`, spark at `8f7733d`.

## The verdict in brief

- **The arithmetic holds.** Under the documents' own model, every figure reproduces to the rounding
  shown. Two exceptions are small: the mAh per day, and the idle margin at a 3.2 V rail (R01, R02).
- **The datasheet inputs are quoted correctly**, at the pages and tables cited. Rows D01–D41 below.
- **One material gap: the "worst corner" leaves out the sensor pin's own input current.** VL6180X
  Table 24, p. 47, the table the report itself cites for VIH max and VOL (`b25-worked-remedy.md:118-119`),
  also bounds GPIO1's high-level input current at **IIH ≤ 10 µA**. The report's worst case carries
  only the S3's 50 nA (`b25-worked-remedy.md:165`; `answer.md:232-233`). With GPIO1 at its stated
  maximum:
  - no passive option reaches the S3's VIH, **even at nominal**. The released line tops out at
    2.33 V nominal and 2.20 V worst, against 2.475 V (R03–R06);
  - option C as sized (R_b 220k, R_be 150k) fails its own idle criterion at the hot corners. D12 is
    undefined at 3.4 V / 2.7 V / 70 °C, and Q1 conducts at 3.6 V / 2.7 V / 70 °C, which is a wake
    loop (R07). Of the same 81-pair grid, 3 pairs still pass. The lowest-current one is R_b 150k /
    R_be 68k (M44);
  - the proof numbers proposed for spark's first slice (566 kΩ bound, 680 kΩ +0.035 V, 1 MΩ +0.09 V)
    are zero-sensor-current figures, not worst-corner ones (R06).
- **What stands:** option C's "on" figures (D12 ≥ 2.95 V, +0.55 V over VIH), the 0.325 V ceiling
  as an upper bound, the option B and abs-max figures, the price arithmetic, and all of
  `answer.md` §1's spark figures.

## How this was checked

- **Sources.** Each was opened from the person's store, located with
  `python3 ~/Development/spark/scripts/parts.py --kept <word>` (read-only). Each sha256 was
  recomputed and matches `b25-worked-remedy.md:567-580`.
  - ST VL6180X DocID026171 Rev 7: `87e1b096…6724`
  - Pololu #2489 schematic irs09a: `5cac2a7c…801f`
  - ESP32-S3 datasheet v2.2: `2d5a7cb7…9a3f`
  - ESP32-S3-WROOM-1 v1.1: `bc430d66…b76b`
  - DFR0975 schematic V1.3: `40624286…9406`
  - The two onsemi PDFs in the scratchpad: MMBT3906LT1/D Rev. 15 `7b8905aa…775e` and
    BSS84/D Rev. 5 `bcbbf6ff…e6`.
  - Text was re-extracted with `pdftotext -layout` into `scratchpad/remedies/vm/`. Figure pages
    were rendered and read as images: MMBT3906 pp. 5–6, and the Pololu schematic.
- **Independent calculator.** `scratchpad/remedies/vm/verify_maths.py` does not import `b25_calc.py`.
  It is a nodal solver that keeps R5 (to the sensor pin) and R8 (pin to header) separate, so the
  sensor pin's own current can sit where it flows. With that current at zero it reduces to the
  report's lumped 48 kΩ model. Its output is `scratchpad/remedies/vm/verify_maths_output.txt`.
- **The 81-pair search.** Re-run on the report's grid and criteria, with and without GPIO1's current
  (inline runs, recorded in M43–M45).
- **Spark's own formulas.** `scripts/copper.py` and the I²C and capacitor constants were imported
  from spark at `8f7733d`, with `SPARK_HOME` set to a fresh empty directory
  (`scratchpad/remedies/vm/sparkhome.J3LtRs`).
- **LCSC part numbers.** Searched read-only through spark's JLCPCB plug-in on 2026-10-06.
- **Nothing changed.** Nothing in either repository was edited, and nothing was committed or pushed.

## 1. Source figures (D rows)

| # | figure as used | where the report uses it | source checked | verdict |
|---|---|---|---|---|
| D01 | VIH = 0.75 × VDD | `b25…:74`, `answer.md:223` | ESP32-S3 v2.2 Table 5-4, p. 65 | confirmed |
| D02 | VIL = 0.25 × VDD | `b25…:74` | Table 5-4, p. 65 | confirmed |
| D03 | IIH, IIL ≤ 50 nA | `b25…:74-75, 165` | Table 5-4, p. 65 | confirmed |
| D04 | RPU/RPD 45 kΩ | `b25…:75` | Table 5-4, p. 65: **typ only, no min or max** | confirmed as typ (see R08) |
| D05 | Table 5-4 is stated "3.3 V, 25 °C" | `b25…:141` | Table 5-4 title, p. 65 | confirmed |
| D06 | VDD3P3_RTC 3.0–3.6 V | `b25…:127` | Table 5-2, p. 64 | confirmed |
| D07 | GPIO12 powered from VDD3P3_RTC | `b25…:76` | Table 2-1, p. 16 (pin 17) | confirmed |
| D08 | GPIO12 low-level glitch, 60 µs | `b25…:128, 293` | Table 2-2, p. 18 ("typical time period") | confirmed |
| D09 | GPIO1 open-drain, 47 kΩ pull-up | `b25…:55-56, 116` | VL6180X Table 2, p. 10 | confirmed |
| D10 | GPIO1 abs max −0.5 to 3.6 V | `b25…:117`, `answer.md:362-363` | VL6180X Table 22, p. 46 | confirmed |
| D11 | AVDD 2.7–2.9 V optimum, 2.6–3.0 V functional | `b25…:105, 120` | Table 23, p. 46 | confirmed |
| D12 | −20…+70 °C functional | `b25…:120, 249, 253` | Table 23, p. 46 | confirmed |
| D13 | GPIO1 VIH max AVDD + 0.5 V | `b25…:118` | Table 24, p. 47 | confirmed |
| D14 | GPIO1 VOL ≤ 0.4 V at 8 mA | `b25…:119` | Table 24, p. 47 | confirmed |
| D15 | GPIO1 IIH ≤ 10 µA (same table) | **not used** | Table 24, p. 47: "IIH High level input current … 10 µA" | **omitted; see R03–R07** |
| D16 | GPIO1 powers up low, tri-stated at boot, sinks in HW standby | `b25…:121` | p. 15 | confirmed |
| D17 | SYSTEM__MODE_GPIO1: bit 5 polarity, reset 0x20, 0x30/0x10 | `b25…:69, 122, 240` | §6.2.10, p. 55; `vl6180x.py:54-55` | confirmed |
| D18 | standby < 1 µA typ | `b25…:123` | Table 13, p. 35 | confirmed |
| D19 | ~340 µA at 500 ms | `b25…:291` | `config.py:106-107`; = 1.7 mA × 2/10 (Table 13, p. 35, which says the current scales with rate) | confirmed |
| D20 | R5 47k from VDD (2.8 V LDO) to GPIO1 | `b25…:59-60` | Pololu irs09a, read as an image | confirmed |
| D21 | R8 1k from GPIO1 to header pin 7 | `b25…:60-61` | Pololu irs09a | confirmed |
| D22 | R6/R7 on GPIO0/CE; Q1A/Q1B shift only SCL/SDA | `b25…:61-62` | Pololu irs09a | confirmed |
| D23 | C3 1 µF + C4 4.7 µF + C5 0.1 µF on VDD = 5.8 µF | `b25…:124` | Pololu irs09a: nominal values, no tolerance or dielectric | confirmed as nominal (K05) |
| D24 | deep sleep 8 µA (RTC periph on), 7 µA (off) | `b25…:129, 291, 397` | WROOM-1 v1.1 Table 12, p. 15: typ, and "only applies to the module variants that embed the chip variant ESP32-S3" | figures confirmed; applicability R12 |
| D25 | MMBT3906 hFE ≥ 60 at 0.1 mA | `b25…:133` | MMBT3906LT1/D Rev. 15 p. 2 (VCE −1 V, 25 °C) | confirmed |
| D26 | VCE(sat) ≤ 0.25 V at 10 mA / 1 mA | `b25…:133, 283` | p. 2 | confirmed (K02) |
| D27 | VEBO 5 V | `b25…:133` | p. 1, maximum ratings | confirmed |
| D28 | pins 1 B, 2 E, 3 C | `b25…:133, 313` | p. 1, SOT-23 style 6 | confirmed |
| D29 | VBE(on) at 0.1 mA: 0.78 V (−55 °C), 0.61 V (25 °C), 0.30 V (150 °C) | `b25…:134` | Figure 17, p. 6, left edge of the axis (0.0001 A) | confirmed |
| D30 | gain at −55 °C about half its 25 °C value | `b25…:134` | Figure 13, p. 5: about 100 against 185 at 1 mA (0.54) | confirmed (K03) |
| D31 | VCE about 0.08 V at 1 mA | `b25…:284` | Figure 14, p. 5: about 0.09 V at IB = 0.1 mA; Figure 15, p. 6: about 0.05 V | confirmed, approximately |
| D32 | BSS84 VGS(th) −0.8 / −1.7 / −2.0 V at −1 mA | `b25…:135` | BSS84/D Rev. 5, p. 2 | confirmed |
| D33 | BSS84 +3 mV/°C | `b25…:135` | p. 2: typ only | confirmed as typ |
| D34 | UM10204 Rev. 7.0 §7.1 p. 50, §7.2.4 p. 52 | `answer.md:339-340` | scratchpad `um10204.txt`, pp. 50 and 52 (0.8473 × RC, Rp(min), Rp(max)) | confirmed |
| D35 | TofIntPulldown 100 kΩ, wired to INT | `answer.md:215`, `b25…:64` | `board.tsx:273, 384-385` | confirmed |
| D36 | internal pull-down armed only for sleep; none while awake | `b25…:71-73` | `board.py:88-89, 91-92`; `hardware.py:183-185` | confirmed |
| D37 | active-high written: 0x30, `WAKE_ON_HIGH = True` | `b25…:67-69` | `vl6180x.py:54, 207-210`; `assembly.py:88`; `config.py:183` | confirmed |
| D38 | C53444 = onsemi MMBT3906LT1G, SOT-23, extended, $0.0189 | `b25…:306` | JLCPCB/LCSC search, 2026-10-06 | confirmed |
| D39 | C22961 = 220 kΩ 0603 1 %, basic, $0.0015 | `b25…:307` | same search | confirmed |
| D40 | C22807 = 150 kΩ 0603 1 %, basic, $0.0044; C22935 = 1 MΩ 0603 1 %, basic, $0.0019 | `b25…:176, 308` | same search | confirmed |
| D41 | nothing else on the FireBeetle loads GPIO12 except P2 pin 7 (TCS) | `b25…:65-66` | DFR0975 V1.3 text: IO12 occurs only at the module, header P3 pin 12 and P2 pin 7 TCS, with no resistor reference on it | consistent; not checked visually |

## 2. Recomputed figures (M rows)

All figures below come from `vm/verify_maths_output.txt` unless the row says otherwise.
"Model" means the report's own assumptions: zero current into the sensor pin, the S3's 50 nA, and
the report's corners.

| # | claim (where) | report | recomputed | verdict |
|---|---|---|---|---|
| M01 | asserted, awake (`b25…:82`; `answer.md:218`) | 1.892 V, short 0.583 | 1.8919 V, short 0.5831 | confirmed |
| M02 | asserted, asleep with 45k (`b25…:83`) | 31.03 k; 1.099 V, short 1.376 | 31.03 k; 1.0995 V, short 1.3755 | confirmed |
| M03 | idle R5 current (`b25…:84`) | 59.57 µA | 59.574 µA | confirmed |
| M04 | carrier R5 + R8 needed (`b25…:86-87`) | < 13.1 k; < 4.08 k | 13.13 k; 4.075 k | confirmed |
| M05 | ceiling (`b25…:106-107`; `answer.md:226-227, 466`) | 0.325 V; 0.15 V at 3.4/2.7 | 0.325; 0.150 | confirmed as an upper bound. GPIO1's current only lowers it, to −0.147 V |
| M06 | A1 levels (`b25…:170`; `answer.md:239`) | 2.669 / 2.567 V | 2.6695 / 2.5668 | confirmed (model); R03 |
| M07 | A1 margins (`b25…:170`) | +0.194/+0.092 at 3.3 V; +0.119/+0.017 at 3.4 V | identical | confirmed (model); R03 |
| M08 | A1 fail rail, unplugged level, current (`b25…:170, 175`) | 3.422 V; ≤ 0.050 V; 2.67 µA | 3.422; 0.0500; 2.669 | confirmed |
| M09 | A1 with the 45k on (`b25…:162-163`; `answer.md:465`) | 1.324 V | 1.3241 | confirmed |
| M10 | A1b (`b25…:171`) | 2.769/2.669; +0.294/+0.194; +0.219/+0.119; 3.558; 0.235 | identical | confirmed (model); R05 |
| M11 | A1c (`b25…:172`; `answer.md:421, 462`) | 2.538/2.434; +0.063/−0.041; 3.245; 0.024 | 2.5384/2.4339; identical | confirmed |
| M12 | A2 (`b25…:173`; `answer.md:240`) | 2.798/2.697; +0.323/+0.222; +0.248/+0.147; 3.597 | 2.7976/2.6975; identical | confirmed (model); R04 |
| M13 | bound (`answer.md:419, 459`) | ≥ 566 k worst, 368 k nominal | 566.3 k, 368.3 k | confirmed (model); R06 |
| M14 | 560 k / 680 k / 1 M at worst (`answer.md:419, 460-463`) | −2 mV / +0.035 / +0.09 | −0.0023 / +0.0346 / +0.0918 | confirmed (model). 680 k is the first E12 value up (spark's table, `emit_board.py:585`); E24 would give 620 k at +0.018 V |
| M15 | B, every row of the table (`b25…:199-205`) | asserted, pin, back-feed, idle, sleep current, unplugged | every cell identical to 3 decimals | confirmed |
| M16 | B with the 45k on: only 10 k survives (`b25…:207-208`) | +0.062 / +0.239 V | +0.062 / +0.239 | confirmed (model) |
| M17 | B abs max (`b25…:209-212`) | 10k: 3.267 V and 12.06 µA at 3.4/2.7; 3.429 V and 15.51 µA at 3.6/2.7; 47k 3.045 V; 100k 2.921 V | 3.2668 / 12.06; 3.4289 / 15.51; 3.0452; 2.9207 | confirmed. The pin never exceeds 3.6 V (Table 22), because the pull-up rail itself is at most 3.6 V (Table 5-2) |
| M18 | B extra sleep current (`b25…:214-215`; `answer.md:46, 241`) | +32.7 / +300.3 µA | +32.67 / +300.27 | confirmed |
| M19 | C chain (`b25…:261`) | 418 k | 418 k | confirmed |
| M20 | C off: back-feed and V_EB (`b25…:265-267`) | 1.20/1.67/2.15 µA; 0.179/0.251/0.323 V | 1.196/1.675/2.153; 0.1794/0.2512/0.3230 | confirmed |
| M21 | C off: estimated I_C at 70 °C (`b25…:265-267`) | 2.1 nA / 23 nA / 0.27 µA | 2.07 nA / 23.4 nA / 0.265 µA | confirmed. It is an extrapolation, labelled as one (`b25…:143-144`) |
| M22 | C off: D12 (`b25…:265-267`; `answer.md:242, 417`) | 0.005 / 0.007 / 0.032 V | 0.0050 / 0.0073 / 0.0315 | confirmed (model); R07 |
| M23 | C off: VIL margin (`b25…:265-267`) | +0.820 / +0.843 / +0.868 | identical | confirmed for those rails; R02 for 3.2 V |
| M24 | VL6180X pin, C off (`b25…:269`) | 2.856 V | 2.8562; 2.8012 at 3.6/2.7 | confirmed; under AVDD + 0.5 and under 3.6 V |
| M25 | VBE(0.1 mA) at −20 / 70 °C (`b25…:249-250, 253`) | 0.706 / 0.498 V | 0.7056 / 0.4984 | confirmed, as linear interpolation between Figure 17's curves (K04) |
| M26 | C on: I_B (`b25…:279-281`) | 6.58 / 8.11 / 9.81 µA | 6.583 / 8.105 / 9.807 | confirmed |
| M27 | C on: I_C needed (`b25…:279-281`) | 29.5/95.1; 30.5/98.3; 31.5/101.5 µA | 29.50/95.06; 30.50/98.28; 31.50/101.50 | confirmed |
| M28 | C on: forced β (`b25…:279-281`) | 4.5/14.4; 3.8/12.1; 3.2/10.4 | 4.482/14.440; 3.763/12.125; 3.212/10.350 | confirmed (10.350 rounds to 10.4); R08 on "heaviest" |
| M29 | C on: D12 and VIH margin (`b25…:279-281`; `answer.md:40, 242`) | ≥ 2.950/3.050/3.150; +0.550/+0.575/+0.600 | identical | confirmed. GPIO1's IIH does not touch the on state (K02 for VCE(sat)) |
| M30 | sensor sink while asserted (`b25…:285`) | 59.57 + 12.17 = 71.75 µA | 59.574 + 12.172 = 71.746 | confirmed. With VOL at its 0.4 V ceiling, β would be 19.9, but at 72 µA VOL is far below that figure (8 mA) |
| M31 | unplugged, C (`b25…:287-288`) | D12 = 0.005 V | 0.005 V | confirmed |
| M32 | C sleep current (`b25…:289`; `answer.md:40-41, 242`) | −58.4 µA | −58.378 µA | confirmed |
| M33 | C per day (`b25…:290`) | 1.43 mAh | **1.401 mAh** | **refuted, R01** |
| M34 | sleep budget (`b25…:290-292`) | ~408 µA; R5 ~15 % | 407.6 µA; 14.6 % | arithmetic confirmed; R12 on the 8 µA input |
| M35 | creep bound, C (`b25…:270-271`; `answer.md:276`) | at most 0.101 V | 0.1011 at nominal (exponential 0.0915); 0.121 at 3.4/2.8 | confirmed at nominal only; R09 |
| M36 | C margin over A1 (`answer.md:293`; `b25…:534`) | 0.46 V / 0.45 V | 0.458 V | answer.md confirmed; b25 R11 |
| M37 | parts cost (`b25…:301-302`; `answer.md:39, 242`) | about $0.025 | 0.0189 + 0.0015 + 0.0044 = $0.0248 | confirmed |
| M38 | C′ (`b25…:346-352`) | back-feed 0.48 µA; VGS −0.477/−0.668/−0.859; 0.665 V hot minimum; 0.188 V below | 0.4771; −0.4771/−0.6679/−0.8588; 0.665; 0.188 | confirmed (the +3 mV/°C is typ) |
| M39 | C′ sleep current (`b25…:440`; `answer.md:243`) | −59.1 µA | −59.10 | confirmed |
| M40 | D/E idle levels (`b25…:367-373`; `answer.md:244`) | 2.798; +0.398/+0.297, +0.323/+0.222, +0.248/+0.147 | identical | confirmed (model); R04 |
| M41 | D with the internal pull-up (`b25…:376-379`) | +0.52…+0.61 V; back-feed 4.28–6.43 µA; creep up to 0.452 V | margins 0.519–0.605; back-feed **4.28–7.31 µA** over the same corners; creep 0.452 linear, **0.298 V** exponential (to 3.098 V) | margins confirmed; R10; K06 |
| M42 | E (`b25…:397`; `answer.md:245`) and F (`b25…:412-414`; `answer.md:246`) | E +1 µA, −58.6 µA; F 2.523 V (+0.048), 2.649 V (+0.174), 280/596 µA | +1; −58.57; 2.5225 (+0.0475), 2.6490 (+0.174), 280.00/595.74 | confirmed; R12 on the 8/7 µA |
| M43 | the 81-pair search, as the report ran it (`b25…:248-259, 530-531`) | 220k/150k lowest back-feed with the 45k on; 470k/220k at 0.68 µA, β 45.5 | my own search, same grid and criteria: 220k/150k first with the 45k on (11 of 81 pass); 680k/470k first with it off (16 of 81) | confirmed |
| M44 | the same search with GPIO1 at its 10 µA maximum | not computed | 3 of 81 pass with the 45k on and 3 with it off. Lowest current: **R_b 150k / R_be 68k**: back-feed 1.88 µA, β 15.5 cold with the 45k (16.2 with tolerances against it), D12 0.022–0.028 V (0.091 V without the 45k). Its creep bound is 0.159 V nominal, against 220k/150k's 0.101 V | new figure, for R07 |
| M45 | the extra-current search criterion for 220k/150k | D12 ≤ 0.10 V at 3.6/2.7/70 °C | holds only while GPIO1 draws ≤ 2.24 µA | new figure, for R07 |

## 3. `answer.md` §1: spark's own figures (S rows)

Recomputed with spark's code at `8f7733d`, using a fresh `SPARK_HOME`.

| # | claim | recomputed | verdict |
|---|---|---|---|
| S01 | 10 kΩ against 100 pF rises in 847 ns (`answer.md:91`) | 847.30 ns; constant ln(0.7/0.3) = 0.84730 (`check_physics.py:63-66`) | confirmed |
| S02 | 400 kHz allows 300 ns; limit 3541 Ω, exact 3540.7 Ω, and 3541 Ω fails (`answer.md:92, 101, 104`) | 300 ns (`check_physics.py:69`); 3540.67 Ω; 3541 Ω → 300.03 ns | confirmed |
| S03 | "use >= 6 V" for a capacitor that needs 6.3 V; 6.3 V and 6 V rejected, 10 V passes (`answer.md:119-120`) | 4.2 × 1.5 evaluates to 6.300000000000001 (`check_physics.py:319-332`), so a 6.3 V part fails; printed with `%.0f` as 6 | confirmed; the cause is noted in K07 |
| S04 | "at least 0.18 mm" for a trace that needs 0.1837 mm; fails at 15 of 26 currents (`answer.md:121-122`) | 0.1837 mm; 0.15 mm carries 0.604 A, 0.18 mm carries 0.690 A, against 0.70 A; 15 of 26 (0.7, 0.8, 1.0, 1.1, 1.3, 1.6, 1.7, 2.0, 2.2, 2.4–2.9 A) | confirmed |
| S05 | generator width = minimum × 1.15 (`answer.md:367-368`) | `copper.py:60`; 0.2112 mm at 0.70 A | confirmed |
| S06 | LED resistor 0.090 W → 0.132 W (`answer.md:126-128`) | 5 V, Vf 2.0 V: 100 Ω gives 30.0 mA and 0.090 W; 68 Ω gives 44.1 mA and 0.132 W; the rule, at the stated 30 mA, sees 0.061 W < 0.063 W | confirmed |
| S07 | asked for 60 mA it gives 27 Ω, about 51.9 mA; the record says 30 mA max (`answer.md:72`) | (3.3 − 1.9)/0.06 = 23.3 Ω → E12 up 27 Ω → 51.85 mA (`emit_board.py:595-618`); `led-red-5mm.json:71-72` = 30 | confirmed |
| S08 | L9110S: 0.5 of the supply, 1.25–6 V, high above 5 V (`answer.md:146-147`) | 10k against 10k = 0.5; 0.5 × 2.5 = 1.25 V, 0.5 × 12 = 6 V; above the 2.5 V threshold when the supply exceeds 5.0 V | confirmed |
| S09 | I²C min/max citation (`answer.md:339-340`) | UM10204 Rev. 7.0, §7.1 p. 50, §7.2.4 p. 52 | confirmed |

## 4. Refuted or unsupported (R rows), with the correct figure

Ordered by consequence.

- **R03. A1's "worst" margin omits GPIO1's own input current.**
  - `answer.md:42, 239, 264, 419`; `b25…:31, 170, 473-474`.
  - Reported: 2.567 V worst (+0.092 V), +0.19 V nominal.
  - The worst corner leaves out VL6180X IIH ≤ 10 µA (Table 24, p. 47). With it, A1 is
    **2.097 V (−0.378 V) worst and 2.221 V (−0.254 V) nominal**.
  - A1 holds only while GPIO1 draws ≤ 1.96 µA at the worst corner (≤ 4.34 µA nominal). No source
    gives that figure.
- **R04. A2, D and E fall below VIH as well.**
  - `answer.md:240, 244`; `b25…:173, 367-373, 395-396, 437, 441-442, 458-460`.
  - Reported: 2.70 V worst (+0.22 V; +0.147 V at 3.4 V).
  - With GPIO1 at 10 µA: **2.328 V nominal (−0.147 V) and 2.204 V worst (−0.271 V)**; at a 3.4 V
    rail, −0.222 V nominal. They need GPIO1 ≤ 4.5 µA (worst).
- **R05. A1b also fails.** `b25…:171, 183-184`. Reported: +0.194 V worst. With GPIO1 at 10 µA:
  **−0.295 V worst** (2.180 V). It tolerates ≤ 3.96 µA.
- **R06. The spark slice's proof numbers are not worst-corner figures.**
  - `answer.md:419, 458-466`. Proposed: "at least 566 kΩ at the worst corner", "680 kΩ (+0.035 V)",
    "accept 1 MΩ (+0.09 V)".
  - Those hold only with zero sensor-pin current. Under the cited datasheets' limits **no pull-down
    value works**: the line tops out at 2.328 V nominal and 2.204 V worst.
  - A test built on these answers would pass a design that the datasheets do not guarantee.
    "No resistor change can give more than 0.325 V" (`answer.md:466`) stays true as an upper bound.
- **R07. Option C's idle state fails at the hot corners.**
  - `answer.md:242, 250-251, 417`; `b25…:25-27, 265-267, 439, 449, 455-458`.
  - Reported: "≤ 0.032 V with no hand, at every corner computed", and a margin that "does not depend
    on the rail's tolerance [or] the temperature".
  - With GPIO1 at 10 µA, R_b 220k / R_be 150k gives:
    - **D12 0.707 V at 3.4/2.7/70 °C**. That is 1.02 V with R5 +5 %, R_be +1 % and R_b −1 %, above
      VIL (0.85 V), so the level is undefined;
    - at 3.6/2.7/70 °C, **Q1 conducts** (V_EB 0.492 V against 0.498 V for 100 µA): D12 reads 1, a
      wake loop;
    - at 25 °C it holds (≤ 0.16 V).
  - The idle margin therefore depends on both the rail and the temperature.
  - The report's own criterion (D12 ≤ 0.10 V at 3.6/2.7/70 °C) holds only while GPIO1 ≤ 2.24 µA.
  - On the same grid, R_b 150k / R_be 68k passes every criterion at 10 µA (M44), at 1.88 µA of
    back-feed instead of 1.20 µA.
- **R08. The "heaviest load" is the typical load.**
  - `b25…:250-252`. Reported: forced β ≤ 20 "with the heaviest load (100 k ∥ 45 k)": 14.4.
  - Table 5-4 gives RPD only as typ 45 kΩ, so 100k ∥ 45k is not a heaviest case.
  - β stays ≤ 20 only while RPD ≥ 28.9 kΩ (load ≥ 22.4 kΩ). That is unsupported as a worst case,
    though saturation would very likely still hold.
- **R09. The creep bound is a nominal-rail figure.**
  - `b25…:270-273, 439, 494-495`; `answer.md:276`. Reported: VDD rises by "at most 0.101 V".
  - At the corners the report computes for D12, the same bound is:
    - **0.121 V at 3.4/2.8 (to 2.921 V)**;
    - 0.141 V at 3.4/2.7;
    - 0.182 V at 3.6/2.7.
  - So the bench criterion "≤ 2.9 V" can fail on a 3.4 V rail with a healthy design.
  - The 5.8 µF is also nominal (K05).
- **R02. C's idle margin at the low rail.**
  - `b25…:25-26, 439, 449, 457`. Reported: "≥ +0.82 V under VIL … 3V3 3.2–3.4 V".
  - The off state was computed only at 3.3, 3.4 and 3.6 V. At the stated 3.2 V rail, VIL is 0.800 V,
    so the margin is **+0.795 V** (D12 0.005 V).
  - `b25…:449` pairs the worst D12 (from 3.6 V) with VIL at 3.3 V.
- **R12. The 8/7 µA deep-sleep figure is stated only for the N4-type modules.**
  - `b25…:129, 291, 397`. Reported: "the module's 7-8 µA", and option E "+1 µA".
  - Table 12's own note (WROOM-1 v1.1, p. 15) limits those figures to modules with the plain
    ESP32-S3. The DFR0975 (N16R8) module embeds the ESP32-S3R8 (WROOM-1 v1.1, p. 3).
  - Supported for the DFR1145 (N4); unsupported for the DFR0975 until B21 settles the SKU. The
    ~408 µA budget's arithmetic stands.
- **R10. The back-feed range is quoted at AVDD 2.8 V only.**
  - `b25…:377`. Reported: D with the internal pull-up: back-feed "4.28–6.43 µA".
  - Over the corners whose margins (+0.52…+0.61 V) the same sentence quotes, it is **4.28–7.31 µA**.
    Minor: the conclusion (no pull on this pin) only strengthens.
- **R01. The daily saving uses the gross current.**
  - `b25…:290`. Reported: "about 1.43 mAh a day".
  - **1.40 mAh a day**: 58.4 µA × 24 h. The 1.43 is the gross 59.57 µA, not the net saving.
- **R11. Rounding.** `b25…:534`: "0.45 V more margin" should be **0.46 V** (0.550 − 0.092 = 0.458),
  as `answer.md:293` has it.

## 5. Caveats that stand (K rows): not refuted, but not guarantees

- **K01.** Nominal figures, such as A1's +0.19 V and B's +0.49 V, are fine as nominal. ST gives no
  typical GPIO1 current, so "nominal" means zero sensor current.
- **K02. VCE(sat) is specified elsewhere.** ≤ 0.25 V is specified at 10 mA / 1 mA, 25 °C. Applying
  it at 30–100 µA, forced β up to 14.4 and −20 °C rests on the typical curves (Figure 14 ≈ 0.09 V,
  Figure 15 ≈ 0.05 V at 1 mA). The datasheet itself warns performance may differ outside its test
  conditions (p. 2). "D12 ≥ 2.95 V" is a well-founded estimate, not a datasheet limit.
- **K03. Figure 13 starts at 1 mA.** The gain-halving reading is taken there, while the stage runs at
  30–100 µA. hFE ≥ 60 is specified at 0.1 mA and 25 °C only.
- **K04. "0.706 V by Figure 17"** (`b25…:249-250`) is a linear interpolation between the −55 °C and
  25 °C curves. Figure 17 has no −20 °C curve. `b25_calc.py` says so; the prose does not.
- **K05. The capacitance is nominal.** The schematic states no tolerance or dielectric for
  C3–C5. Creep scales inversely with the real capacitance: half of 5.8 µF doubles the linear figure
  to 0.20 V at nominal. The exponential at nominal (0.0915 V) shows the linear 0.101 V is a valid
  bound at 5.8 µF.
- **K06. D's 0.452 V is linear.** With the back-feed falling as VDD rises, the most VDD can rise in
  0.49 s is 0.298 V, to 3.098 V. The conclusion, above the 3.0 V functional maximum, holds.
- **K07. The capacitor rejection is a floating-point artefact.** `answer.md:119-120` is right that
  spark rejects a 6.3 V part. The cause is that 4.2 × 1.5 evaluates to 6.300000000000001; in exact
  arithmetic a 6.3 V rating meets 1.5× derating. Rounding the printed value "toward the safe side"
  (`answer.md:484`) would not fix that half; the comparison needs a tolerance.
- **K08. The 70 °C hot corner is beyond the N16R8 module's rating.** The N16R8 module is rated
  −40…65 °C ambient (WROOM-1 v1.1, p. 3). That makes 70 °C conservative for the stage, not wrong.
- **K09. Inputs that are only typical.** The 60 µs glitch, +3 mV/°C and 8/7 µA are all typical
  figures, and are used as such.
- **K10. The power-up glitch estimate is plausible.** "a few mA" (`b25…:293-295`) uses hFE up to
  about 300, which is specified only at 10 mA. 9.8 µA × 300 ≈ 2.9 mA, harmless against the S3's
  28 mA IOL (Table 5-4).

## 6. Not checked here

- Prices beyond the four LCSC numbers above.
- `answer.md` §2's figures about other tools.
- The counts in `answer.md` §1 that are not electrical (seventeen places, 6 of 6, and so on).
- The MicroPython and ESP-IDF behaviour claims.
- Any measurement: nothing has touched hardware.
