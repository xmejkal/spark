# Verified parts library

One entry per part. A part with `verified: true` and a datasheet link can be reused
directly; anything else must be confirmed before it goes near a fabricated board. Store
the symbolic label -> physical pin/GPIO indirection explicitly — that mapping is what
AI-generated boards get wrong. Seed entries below; extend as new parts are resolved.

## Reuse waterfall (never hand-invent a part)
1. Vendor/ecosystem: tscircuit registry (`tsci add`), atopile packages, vendor KiCad libs (Seeed/SparkFun/Adafruit).
2. Bare-IC canonical: KiCad official libraries, or `easyeda2kicad` from an LCSC part number (stays `verified: false` until checked).
3. Aggregators: SnapEDA / Ultra Librarian — fetch per part, do not mirror (licensing).

---

## Seeed XIAO ESP32-C6  (module)
verified: true
footprint: 14-pad, 2x7 header (all XIAO share it)
provenance: Seeed wiki pin list, cross-checked against pins_arduino.h (arduino-esp32); official
  footprint = Seeed OPL_Kicad_Library "XIAO Series" (one shared 14-pad footprint); full hardware
  (schematic + STEP + pinout) = Seeed OSHW-XIAO-Series repo
pin map (D-label -> GPIO -> default role):
- D0 -> GPIO0  (ADC A0)
- D1 -> GPIO1  (ADC A1)
- D2 -> GPIO2  (ADC A2)
- D3 -> GPIO21 (SPI SS)
- D4 -> GPIO22 (I2C SDA)
- D5 -> GPIO23 (I2C SCL)
- D6 -> GPIO16 (UART0 TX)
- D7 -> GPIO17 (UART0 RX)
- D8 -> GPIO19 (SPI SCK)
- D9 -> GPIO20 (SPI MISO)
- D10 -> GPIO18 (SPI MOSI)
- power pads: 5V, 3V3 (LDO out), GND
internal-only (do NOT use / do NOT reuse in firmware): GPIO3/14 antenna RF switch,
  GPIO15 user LED, GPIO8/9 straps+BOOT, GPIO12/13 USB, GPIO24-30 flash.
notes: 3.3V logic; module handles EN/boot/USB/regulator/antenna/flash/straps.

## TB6612FNG  (motor driver breakout)
verified: true (IC pinout); breakout header order: confirm on your specific board
key pins: VM (motor 2.5-13.5V), VCC (logic 3.3V), STBY (tie high to enable),
  AIN1, AIN2, PWMA -> channel A; AO1/AO2 -> motor. Channel B (BIN1/BIN2/PWMB/BO1/BO2) unused.
provenance: Toshiba TB6612FNG datasheet; SparkFun ROB-14450 breakout libs.
notes: logic and motor share only ground. STBY must be high.

## MAX98357A  (I2S mono amp breakout)
verified: true
pins: VIN (2.5-5.5V; feed 5V for volume), GND, DIN (I2S data), BCLK, LRC (word select),
  GAIN (open ~9dB), SD (tie to logic high = on); OUT+/OUT- -> speaker.
provenance: Adafruit #3006 board + Maxim datasheet.

## SSD1306 OLED  (I2C module, 0.96")
verified: true
pins: VCC (3.3V), GND, SCL, SDA. Watch variants: 4-pin vs 7-pin, and VCC/GND pad ORDER.
needs external I2C pull-ups (~4.7k) if not on the module.
provenance: KiCad official Display lib footprint; module datasheet.

## RZ7899 / TA6586  (SOP-8 H-bridge; found in reverse-engineered Sisuo board)
verified: true (family pinout)
pins: 1 FIN (forward in), 2 RIN (reverse in), 3 GND, 4 VCC (3-25V), 5+6 OUT1 (paralleled),
  7+8 OUT2 (paralleled).
truth table: FIN=H,RIN=L forward; L,H reverse; H,H brake; L,L coast.
signature test: pins 5&6 tied and 7&8 tied (that doubling proves the family).
provenance: RZ-MIC / components101 TA6586.

## Generic IR proximity module
verified: false (define per board)
typical pins: VCC, GND, OUT (digital) — or a reflective emitter+photodiode pair.
notes: no canonical part; define once and verify once.

---

## Prototyping module picks (verified from vendor wikis, 2026-09)
Prefer these real plug-and-play modules over bare parts for prototyping. All 3.3V-native and
LiPo-friendly (~3.7V). Minimise analog: pick digital/I2C/I2S modules. Always offer the user the
bare-part alternative when it is genuinely simpler.

### IR proximity ("wave to open"), digital
verified: true (vendor wiki)
- **DFRobot SEN0239** — Gravity digital IR, adjustable 0–200 cm, 3–5V, 3-pin digital. wiki.dfrobot.com/sen0239
- **Seeed Grove IR Distance Interrupter v1.2** — digital SIG, 3.3/5V, pot-tunable ~7.5–40 cm.
- AVOID on 3.3V/LiPo: DFRobot SEN0019/SEN0381/SEN0014 (5V parts; output can exceed the C6's 3.3V pin).

### I2C OLED 128×64 (SSD1306/SSD1315, addr 0x3C)
verified: true
- **DFRobot DFR0486** — Gravity I2C OLED, SSD1306, 3.3–5V. wiki.dfrobot.com/dfr0486
- **Seeed Grove OLED 0.96" SSD1315** (104020247) — Grove I2C, SSD1306-compatible, 3.3/5V.

### Motor driver (small brushed DC)
verified: true
- Direct PWM: **DFRobot DRI0044** (TB6612FNG, 2.5–12V, logic 2.7–5.5V) or **DRI0040** (HR8833, 3.3–10V).
  3 GPIO: IN1/IN2/PWM. (DFRobot's Gravity DC driver DRI0044-A is discontinued.)
- All-I2C option (frees GPIOs, one shared bus): **Seeed Grove Mini I2C Motor Driver** (DRV8830,
  2.75–6.8V — ideal for a 6V pack, addr 0x60/0x62) or **Grove I2C TB6612FNG** (addr 0x14).

### Audio
verified: true
- I2S: **DFRobot DFR0954** (MAX98357A, 2.5–5.5V, runs off VBAT for volume) + 8Ω speaker
  (e.g. DFRobot FIT0502 3W 8Ω, PH2.0). ESP32 generates audio in real time.
- Simplest (canned chirps): **DFRobot DFR0534** UART MP3 module — stored WAV/MP3, 2 UART wires,
  built-in amp; frees the I2S bus. wiki.dfrobot.com/dfr0534

### Power rule — LiPo builds
The XIAO **5V pad is dead on battery** (USB VBUS only). Feed a >3.3V peripheral (audio amp) from
the **LiPo rail (VBAT)**, not the 5V pin. Logic peripherals run off the 3.3V LDO (V33). A separate
higher-voltage motor pack (e.g. 6V AA) shares only GND.

---

## Identify the ESP32 board BEFORE designing (Seeed XIAO vs DFRobot)
The pin map depends entirely on the exact board. Check the silkscreen + pad count:
- **Seeed XIAO ESP32-C6**: 14 pads (7/side), 11 GPIO, 21x17.8 mm, pads labelled D0-D10 / **5V** /
  GND / 3V3, Seeed silk. (This is the board the current smart-bin design assumes.)
- **DFRobot FireBeetle 2 ESP32-C6 (DFR1075)**: much larger 60x25.4 mm, dual-row 2.54 mm, ~19 IO,
  pads labelled both IOxx and Dxx, onboard LiPo charge. DFRobot silk.
- **DFRobot Beetle ESP32 V2.0**: hexagon/octagon board, **ESP32-WROOM-32D (classic ESP32)**, CH340C
  USB-serial, pads A0-A3 / D2 D3 D4 D7 / SDA SCL / TX RX / 3V3 / VIN / GND. Classic-ESP32 rules apply:
  input-only GPIO34-39 (no pull-ups), strapping GPIO0/2/12/15, ADC2 unusable with WiFi. Silk "Beetle
  ESP32 V2.0 / DFRobot".
- **DFRobot Beetle ESP32-C6 (DFR1117)**: 20.5x25 mm castellated coin, 13 IO, pad **"VIN"** (not 5V).
Tells: pad count (11 vs 13 vs 19), "5V" vs "VIN" label, and Seeed vs DFRobot silk. Get the exact
board's `pins_arduino.h` before locking any pin.

## DFRobot modules (ingest per SKU — see vendor-knowledge.md)
verified: per-SKU (build from the wiki pinout + schematic + the DFRobot_<Part> GitHub examples)
- Key on the **SKU** (DFR/SEN/DRI...). Pull pinout from `wiki.dfrobot.com/<sku>/docs/`, cross-check
  against the schematic ZIP and the library `examples/` default pins.
- **Gravity** modules: record {connector = 3-pin or 4-pin, colour}. 3-pin: green=digital, blue=analog.
  4-pin: red=I2C, blue=UART. PH2.0 pitch. This replaces a bespoke pinout for plug-and-play parts.
- Footprint: derive from the dimension PDF (2.54 mm pitch on FireBeetle/Beetle) + the STEP model;
  mark "derived, needs verification". DFRobot ships no KiCad/Eagle footprints.
- Example — DFR0044 (Gravity TB6612FNG 2x1.2A motor driver) is DFRobot's own driver board; if used,
  it replaces the bare TB6612 wiring with a Gravity 4-pin interface.
