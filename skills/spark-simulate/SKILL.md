---
name: spark-simulate
description: Simulate and test firmware for an ESP32 board before the hardware exists — a fake `machine` module for offline unit tests, and Wokwi (browser, CLI or MCP) for running the real firmware on a simulated chip. Use when the user wants to test firmware without hardware, set up CI for an embedded project, or asks "can we simulate this?".
---

# spark-simulate

Testing firmware without hardware, in three layers. Each catches what the one below cannot, and
each costs more than the one below — so always build them in this order.

| Layer | What it runs | Catches | Cost |
| --- | --- | --- | --- |
| 1. Logic tests | the firmware's own modules under CPython, with injected fakes | state machines, timing, policies | free, seconds |
| 2. Fake `machine` | the *device* layer under CPython, against a stand-in for MicroPython's `machine` | wrong pin modes, driver register mistakes, task wiring | free, seconds |
| 3. Wokwi | a real firmware binary on a simulated chip | anything depending on the real runtime: boot, asyncio, actual pin toggling | free in the editor; CI needs a token |

None of them replaces the bench. Say so plainly rather than implying a green simulation means
working hardware — timing, electrical behaviour and vendor modules' real command sets are all
outside every simulator.

## Layer 1 and 2: do these first, always

Most "can we simulate it?" questions are really "can we test it?", and the answer is usually a
day of test-writing rather than a simulator. Two things make it possible:

1. **Inject collaborators** — clock, task spawner, sleep — so logic runs with no event loop and
   no waiting. A four-second hold should take microseconds in a test.
2. **Confine `machine` to one module.** If only `hardware.py` imports it, a fake `machine` in
   `sys.modules` makes everything else testable. See `references/fake-machine.md` for a working
   one (Pin, PWM, UART, I2C with per-address devices, ADC, WDT, deep sleep as an exception).

Model *behaviour the firmware depends on*, not the chip: pins remember levels and pulls, PWM
remembers duty, I2C dispatches to fake devices. A fake that models too much becomes a second
implementation, and then a second source of bugs.

**Make the fakes as strict as the device.** A fake that is more forgiving than the hardware hides
the bugs you most need to find — for example MicroPython raises `RuntimeError("can't cancel
self")` when a task cancels itself, and a fake that quietly allows it will pass tests for
firmware that freezes on the bench.

## Layer 3: Wokwi

Verified 2026-09-23; re-check before relying on any of it.

**Supported**: ESP32, C3, C6, C61, H2, S2, S3, P4 (and alphas), with many stock boards including
the XIAO ESP32-C6 and XIAO ESP32-C3. MicroPython runs — point `wokwi.toml` at a MicroPython
`.bin` and push code with `mpremote connect port:rfc2217://localhost:4000` exactly as over USB.
Templates: `wokwi.com/projects/new/micropython-esp32-c6`.

**A project is two files**: `wokwi.toml` (firmware path, RFC2217 port, custom chips) and
`diagram.json` (parts and connections). `wokwi-cli init` generates both.

**Headless + CI**: `wokwi-cli <dir> --scenario test.yaml --timeout 20000`, with
`WOKWI_CLI_TOKEN` from `wokwi.com/dashboard/ci`. Scenario YAML steps: `wait-serial` (the
assertion), `set-control` (press a button, move a slider), `write-serial`, `expect-pin`,
`delay`, `take-screenshot`. GitHub Action: `wokwi/wokwi-ci-action`. There is also a Python SDK
(`pip install wokwi-client`) for driving simulations from pytest.

**MCP**: `wokwi-cli` ships an experimental MCP server, so an agent can run simulations and read
serial output directly:

```json
{"servers": {"Wokwi": {"type": "stdio", "command": "wokwi-cli", "args": ["mcp"],
  "env": {"WOKWI_CLI_TOKEN": "wok_..."}}}}
```

**The catch**: Wokwi has no model of most sensor and driver modules — no ToF sensors, no
H-bridges, no DC motors, no vendor UART modules. Options, cheapest first:

1. **Do without.** If the firmware has a "no sensor, buttons only" configuration, the state
   machine is still fully testable. This is usually the right answer.
2. **Show it with LEDs.** An H-bridge's two input pins driving two LEDs makes direction and duty
   visible and assertable, with no custom code.
3. **Write a custom chip** — C (or any language) compiled to WASM, with real I2C and UART
   peripheral emulation: `docs.wokwi.com/chips-api/getting-started`. A simple I2C sensor is a
   day's work. Worth it only when the sensor's behaviour is what you are testing.

**Assert on the log, not on pins.** Firmware that logs its state transitions is directly
observable through `wait-serial`, which needs no harness and no custom chips.

## Honest limits, to state up front

* A passing simulation does not mean working hardware.
* Deep sleep and wake sources under MicroPython on Wokwi are unverified (they work for
  Arduino/ESP-IDF projects).
* Wokwi CI minutes may need a paid plan; the free allowance is undocumented.
* Timing in a simulator is not the timing on the bench — never calibrate against it.
