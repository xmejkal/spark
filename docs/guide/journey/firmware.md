## Firmware

**Partly.** spark does not write your firmware; you or Claude do. It gives the firmware its pins. The build writes
them to `firmware/pins.py`, and this command writes the same file on its own:

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/assign_pins.py" requirements.json --emit-pins firmware/pins.py
```

<!-- output: run 2026-10-05, spark 0.6.0 -->
```text
DFRobot FireBeetle 2 ESP32-S3 — 4 signal(s) placed

  MOTOR_IA        D3    GPIO38  needs nothing special; the cheapest pin left could still pwm, which is spent here  [not_wake_capable]
  MOTOR_IB        A5    GPIO11  needs nothing special; the cheapest pin left could still pwm and wake, which is spent here  [adc2_unusable_with_wifi]
  BTNOPEN_BUTTON  D12   GPIO12  needs nothing special; the cheapest pin left could still pwm and wake, which is spent here  [adc2_unusable_with_wifi]
  BTNMODE_BUTTON  D11   GPIO13  needs nothing special; the cheapest pin left could still pwm and wake, which is spent here  [adc2_unusable_with_wifi]

  still free:
  …
```

Each signal gets a pin with its pad and its reason. The rest of the output lists the pins still free, and the facts
about these parts nobody has verified, each with what depends on it. `firmware/pins.py` holds the same map as plain
integers. The firmware does `import pins`; it never types a GPIO number.

The firmware imports on a Mac before any hardware ([P59](https://github.com/xmejkal/spark/issues/7)).
`import_firmware.py` imports each file and each package in `firmware/`, except the boot files `main.py` and `boot.py`.
Each import is a process of its own. Every import uses spark's stand-ins for MicroPython's modules, unless the firmware ships its own `framebuf` or `micropython`. They live in `scripts/stand_in/`. `machine` has a
`Pin` that remembers its level, and a `PWM` that keeps its last frequency and duty but makes no signal
([P352](https://github.com/xmejkal/spark/issues/450)). It has an `ADC`, an `SPI` and `SoftSPI`, an `I2C` and `SoftI2C`,
and an `I2S` too ([P421](https://github.com/xmejkal/spark/issues/551)): each keeps its arguments and returns a fixed
value (an ADC reads 0, a bus read gives zero bytes). `micropython` has `const`, and `framebuf` has a `FrameBuffer` that
draws nothing, so a display driver imports. A test sets an input, calls the firmware and reads the output pin.

An `imported` proves that the names exist and the module-level calls ran. It does not prove that a pin, a wire, a rate
or a driver works, or that a device answers. A bus finds no device, so a module-level check such as
`assert 0x3C in i2c.scan()` fails the import: keep it in a function that `main.py` calls. A driver that sleeps in its constructor imports: the check
gives `time` MicroPython's `sleep_ms`, `sleep_us`, `ticks_ms`, `ticks_us`, `ticks_add` and `ticks_diff` with fixed values
(a sleep returns at once, `ticks_ms` is always 0), and `micropython.alloc_emergency_exception_buf` does nothing. A driver's `hasattr(machine, "X")` probe is False, and `from machine import X` is an ImportError with the action. Because `ticks_ms` never moves, a driver's wait loop on it times out.

The command leaves `main.py` unrun, because `main.py` starts the loop. Keep it to two lines that call a module. The
button-and-LED firmware does that (`import light`, then `light.run()`). You write your own, or Claude does. To try the
command first, copy spark's example from `tests/data/breadboard/button-light/firmware/` into your `firmware/`.

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/import_firmware.py"
```

<!-- output: run 2026-10-12, spark 0.8.1 -->
```text
imported  light
imported  pins
ok
```

Nothing to import is a problem, not a pass. When `firmware/` holds only `main.py`, `boot.py` and `pins.py`, the command
exits 1. That firmware cannot be imported without running `main.py`. Move its code out of `main.py` into a module that
`main.py` calls.

Not built yet: a check that every signal is driven and read ([P74](https://github.com/xmejkal/spark/issues/8)).
