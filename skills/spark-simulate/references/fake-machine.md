# A fake `machine` module for MicroPython firmware

The pattern that makes the device layer testable on a PC. Install before importing anything that
reaches the hardware:

```python
import sys
sys.modules["machine"] = FakeMachineModule
sys.modules["esp32"] = FakeEsp32Module
```

A complete, working example lives in the smart-bin project:
`firmware/micropython/tests/fake_machine.py`, used by `tests/test_on_fake_hardware.py`.

## What to model

| Class | Model this | Do not model |
| --- | --- | --- |
| `Pin` | level, mode, pull; inputs read what the test sets; a registry by GPIO number so a test can find one | drive strength, IRQs (until needed) |
| `PWM` | duty and frequency as plain attributes — duty is how a test sees a motor run | LEDC channel allocation |
| `I2C` | `readfrom_mem`/`writeto_mem` dispatching to fake devices by address, with `addrsize` | bus timing, NAK behaviour |
| `UART` | collect everything written, so frames can be asserted | baud timing |
| `ADC` | a counts value the test sets | attenuation curves |
| `WDT` | count feeds | actually resetting |
| `deepsleep` | **raise a custom exception** so the test can assert it was requested, with which wake pins | actually stopping |

## The rules that make it worth having

1. **Be at least as strict as the hardware.** If the device raises, the fake raises. A forgiving
   fake certifies broken firmware.
2. **Model behaviour the firmware depends on, nothing else.** Every extra detail is a second
   implementation to keep correct.
3. **Fake devices, not decisions.** A fake I2C sensor answers registers; it does not decide
   whether a hand is present.
4. **Reset between tests** — pins and devices are global state.

## What this layer proves

That devices are constructed with the right pins and modes, that a driver talks to the registers
it thinks it does, that tasks fire the triggers they should, and that shutdown paths really stop
the motor. What it cannot prove: timing, electrical behaviour, and whether a vendor module's
documented command bytes match the firmware it shipped with.
