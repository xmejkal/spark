# Simulate

Step 7 of 8 in [the journey](../journey.md). Next: [Bench](bench.md).

**Works.** The build's simulation stage generates the Wokwi diagram and stages the chips: hand-written models of
modules Wokwi has no part for, kept beside a part's record and compiled with `wokwi-cli` only when the binary is
missing or older than its source. `--keep .` keeps them in `sim/`
([P116](https://github.com/xmejkal/spark/issues/50)).

A run is a separate step:

1. **Build with the simulation kept:** `check_spine.py requirements.json --keep .`.
2. **Write a scenario** in `sim/scenarios/`, a folder you create. Claude writes its steps from your words. spark's
   example for this project is in `$CLAUDE_PLUGIN_ROOT/tests/data/breadboard/button-light/scenarios/`. The firmware
   must print `ready` once its setup is done, and a line for each change the scenario waits on: spark's example
   firmware does both.
3. **Run it** with a Wokwi account's CI token in `WOKWI_CLI_TOKEN` (wokwi.com/dashboard/ci). MicroPython for the
   board comes from `/spark:setup add micropython-esp32s3`, `micropython-esp32c6` for a C6 board, `micropython-xiao-esp32c6` for the XIAO, or `micropython-esp32` for the original ESP32, such as the T-Display.

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/run_scenario.py" sim/scenarios/the-button-lights-the-led.scenario.yaml
```

<!-- output: run 2026-10-12, spark 0.8.1 -->
```text
the-button-lights-the-led.scenario.yaml: passed
log: sim/runs/the-button-lights-the-led.log
```

The command puts MicroPython and `firmware/` into one flash image and waits for the firmware's `ready` line. Then it
runs the steps and writes the log with its date ([P130](https://github.com/xmejkal/spark/issues/64)). The diagram the
build writes wires the board's serial port to Wokwi's serial monitor, so a scenario's `wait-serial` hears the firmware
([P190](https://github.com/xmejkal/spark/issues/142)). The ready contract and the scenario's form are on
`/spark:build`'s page ([Simulate it](../../../commands/build.md#simulate-it--for-real-with-the-values-set-in-the-test)).

A step may carry a `name:` key beside its kind. When it holds a `must` line of the project's brief, copied exactly, the
step names that line. The log's header keeps the names (`step names: 2`, then one `step name:` line each), and
[the look](bench.md#look-at-the-board) lists the must lines that no passed scenario named
([P345](https://github.com/xmejkal/spark/issues/440)). A name is a claim, not a test: spark does not check that the step asserts the line.

A run spends Wokwi CI minutes. Watching it live in VS Code needs a Wokwi licence that includes VS Code, Hobby+ or above
per wokwi.com/pricing (read 2026-10-01).

**Today, in full.** If spark keeps the board's Wokwi definition, the build names each on-board LED or button that it
has no pin for. spark knows no way for a scenario to reach such a part. So you test it on the board, such as
`ONBOARD_BUTTON (GPIO9)` on the XIAO ESP32-C6 ([P396](https://github.com/xmejkal/spark/issues/512)). Without the definition, the build says
`onboard GPIOs: not checked`. A board-only FireBeetle 2 ESP32-S3 build wires Wokwi's LED and pushbutton to GPIO21 and
GPIO47 in place of the board's own. It says so in its limits. On 2026-11-01 a free scenario on walk 3's project
pressed that button and passed ([P484](https://github.com/xmejkal/spark/issues/663)). Walk 4 did the same on 2026-11-01: the FireBeetle 2's button changed its LED's effect in Wokwi ([P510](https://github.com/xmejkal/spark/issues/705)).
