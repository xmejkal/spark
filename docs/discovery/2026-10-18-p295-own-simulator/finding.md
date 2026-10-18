# P295 finding: a live simulation in spark's own page?

Spike for [#356](https://github.com/xmejkal/spark/issues/356), epic P293 [#352](https://github.com/xmejkal/spark/issues/352),
after [P294](https://github.com/xmejkal/spark/issues/353). Date: 2026-10-18.

> **TL;DR.** The PO's real question is the look: a running simulation in spark's own page, on an open backend. Wokwi's
> ESP32 engine is closed, and `wokwi-cli` runs a scenario and exits, so it cannot feed a live page. Espressif's QEMU fork
> is open (GPL, run as a separate process) but its public pages confirm ESP32, S3 and C3 only, and its pre-built
> binaries do not cover the ESP32-C6. Recommendation: a **mix**. Spark's own page and a small "bench" that holds the
> outside parts (LED, button, buzzer) run on a fast logic-level backend that extends spark's existing `machine` stand-in;
> `wokwi-cli` stays the final check. Cost: **large** for page plus bench, **very large** for a full own simulator.
> Nothing here was installed or run; the QEMU C6 and pin-hook claims are unconfirmed.

Sources: Wokwi, Espressif, Renode and MicroPython pages, read 2026-10-18. Not checked: running any of them.

## 1. What Wokwi's ESP32 simulation rests on

- No source says what the engine is. Wokwi's ESP32 guide lists ESP32, C3, S2, S3, C5 (alpha), C6, C61, H2, S31 (alpha),
  P4 (beta) with a feature matrix, and names no engine ([guide](https://docs.wokwi.com/guides/esp32)). A search summary
  says "a QEMU fork for Xtensa"; it came from a third-party comparison page, so it is unconfirmed.
- Its AVR and RP2040 engines are open: `avr8js` and `rp2040js` (MIT, from P294's finding). They show how a page runs a
  chip in the browser. No ESP32 equivalent is in the Wokwi org (P294).
- `wokwi-cli` ([usage](https://docs.wokwi.com/wokwi-ci/cli-usage)): starts the simulation and prints serial;
  `--serial-log-file`, `--expect-text`, `--scenario`, and `--interactive` (stdin goes to the simulated serial port). The
  page documents no live pin stream and no server mode.
- Scenario steps ([automation](https://docs.wokwi.com/wokwi-ci/automation-scenarios)): `delay`, `expect-pin`, `set-control`,
  `wait-serial`, `write-serial`, `take-screenshot`, touch steps. A pin is checked, not streamed.
- Answer: nothing public streams live pin states to a page. Wokwi stays a batch checker. The closed service also costs CI
  minutes (P294: 50 per 30 days on the free plan).

## 2. Open emulators

| Option | License | ESP32 family | GPIO and UART from outside | Cannot model |
|---|---|---|---|---|
| Espressif QEMU fork ([repo](https://github.com/espressif/qemu), branch `esp-develop`) | GPL v2 (repo page) | The qemu README names ESP32, S3, C3 ([README](https://github.com/espressif/esp-toolchain-docs/blob/main/qemu/README.md)). Pre-built binaries do not cover C6; a source build is needed (from a search summary of the [ESP-IDF docs](https://docs.espressif.com/projects/esp-idf/en/v6.1/api-guides/tools/qemu.html); the page itself does not mention C6) | UART yes (IDF Monitor attaches). The C3 notes list GPIO strap mode, SPI flash, crypto, a virtual RGB panel ([C3 notes](https://github.com/espressif/esp-toolchain-docs/blob/main/qemu/esp32c3/README.md)). A way to set or read a pin from outside is not documented in what was read: unknown | no analog, no radio; "several peripherals" only |
| Renode ([repo](https://github.com/renode/renode)) | MIT | Xtensa is listed as an architecture; ESP32 boards not confirmed on the page | Python through pyrenode3 and Robot Framework; GPIO model per board: unknown | a board model for a given ESP32 module is spark's work |
| `avr8js`, `rp2040js` | MIT | none (AVR, RP2040) | pins and serial are plain JavaScript callbacks | the wrong chip; shows the shape only |
| MicroPython unix port with a fake `machine` | MIT | no chip; runs the person's firmware logic | spark's own `Pin` objects, which spark controls | timing, interrupts, PWM, I2C, real MCU quirks |
| Velxio ([article](https://www.cnx-software.com/2026/04/04/velxio-open-source-self-hosted-arduino-raspberry-pi-and-esp32-simulator/)) | AGPLv3 or commercial | QEMU for ESP32 and S3 (Xtensa) | web page with a serial console | AGPL does not fit an MIT repo to copy; prior art only |

- License: QEMU is GPL v2. Spark starts it as a **separate process** and talks through a pipe or socket, so spark's own
  code stays MIT. This is the usual reading of the GPL for separate programs; no Espressif text was found that says it,
  and no lawyer checked it.
- Spark already tests firmware on the Mac: `scripts/import_firmware.py` imports each module with
  `scripts/stand_in/machine.py` (a `Pin` that remembers its level, nothing else), one process per module. Tests in
  `tests/test_import_firmware.py` set and read levels (`set_level`, `level`). It imports; it does not run `main.py` or a loop.
- Whether MicroPython's unix port ships a `machine` module: the quick reference read does not say. Spark's stand-in runs
  under CPython today, so the unix port is not needed for step 1.

## 3. What spark would build itself

| Piece | Work |
|---|---|
| Outside parts as code: LED (pin high lights), button (page sets a pin), buzzer (pin toggles, page plays a tone) | one small class per part type, driven by the pin map; **medium** |
| Page: spark's breadboard SVG plus `@wokwi/elements` pictures (P294), LEDs that light, a clickable button, a serial pane | **medium** (P294 priced the page) |
| Bridge: a local process holds the backend and the bench; the page talks to it over a WebSocket on the Mac | **medium**; whether an Artifact page can reach localhost is unknown, so the page is a local file |
| Claude side: the same bench as a CLI with `--json`: `press`, `pins`, `serial` | **small** once the bench exists, because page and Claude call the same code (AGENTS.md: one core, many interfaces) |
| The scenario checks `wokwi-cli` runs (`expect-pin`, `wait-serial`) | **small** on the bench, but they check logic, not the chip |
| Letting `main.py` run its loop on the stand-in: a `time.sleep` that yields, `PWM`, `ADC`, interrupts | **medium**, and it grows with each new firmware |
| A faithful chip (QEMU for the C6, GPIO hooks in C) | **very large**: a C patch to the fork, or a build and its upkeep |

## 4. Options, cost and a recommendation

| Option | What the person gets | Cost | Loses |
|---|---|---|---|
| A. Keep `wokwi-cli`, send the person to wokwi.com | today | none | the look; the live page |
| B. Own page and bench on the stand-in (logic level), `wokwi-cli` as the final check | spark-styled live view; Claude presses and reads; offline; no CI minutes for the view | **large** | real timing and chip behaviour in the view |
| C. Own page on Espressif QEMU | the real firmware binary; C6 only after a source build | **very large** | needs a toolchain; a pin hook is unknown |
| D. Full own simulator (own ESP32 core) | everything | **very large**, not spike-sized | years of work Wokwi did |

**Recommendation: B.** It matches "something always works, each step adds one thing." Step 1: extend the stand-in so a
`main.py` loop runs and the bench holds the LED, button and buzzer. Step 2: the CLI for Claude. Step 3: the page on the
bench. Step 4 (later, optional): swap the backend for QEMU once a C6 build and a pin hook are proven, without touching
the page (a small backend interface).

**The buzzer on pin 20.** Person: clicks the button on the page; the page sends `press button`; the bench sets the
button's pin high; the firmware loop sees it and sets pin 20 high; the bench's buzzer part reports "on" and the page
plays a tone and shows a symbol. Claude: `bench pins --json` returns `{"20": 1}`; `bench serial` returns the log.
What B cannot say: whether the real buzzer's driver, the timing or the sound is right. `wokwi-cli` checks that.

```mermaid
flowchart LR
  P[Person: spark page<br/>breadboard SVG + elements] -- press / view --> BR[Bridge: local WebSocket]
  C[Claude: bench CLI --json<br/>press, pins, serial] --> BN
  BR --> BN[Bench: LED, button, buzzer<br/>one small class each]
  BN <--> BE{Backend interface}
  BE --> ST[Stand-in machine.py<br/>logic level, now]
  BE -.later.-> QE[Espressif QEMU<br/>separate process, GPL]
  FW[firmware/*.py] --> ST
  WK[wokwi-cli final check] -.same diagram.json.-> FW
```

## Open questions for the PO

1. Is a logic-level view (no timing, no real chip) enough for the page, with `wokwi-cli` as the proof?
2. Is a local page on the Mac fine, or must it live in a Claude Artifact? The bridge needs the Mac.
3. Is a tone from the browser enough for "hear the buzzer"?
4. Is step 4 (QEMU) a card now, or does it wait until a C6 pin hook is shown?
