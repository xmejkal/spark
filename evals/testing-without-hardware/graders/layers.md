Score the answer on how much of this it gets, each worth equal weight:

1. **Confine `machine` to one module.** If only the hardware-construction module imports it, a
   fake `machine` in `sys.modules` makes everything else testable under CPython. An answer that
   just says "write unit tests" without this seam has not answered the question.
2. **Inject the clock, the task spawner and sleep**, so logic runs with no event loop and no
   waiting — a four-second hold should take microseconds in a test.
3. **Run it on a real MicroPython runtime** (the unix port), not only CPython. MicroPython's
   asyncio differs: a task cannot cancel itself, and it raises RuntimeError if you try. Firmware
   that passes under CPython can freeze on device.
4. **Fakes must be at least as strict as the hardware.** A forgiving fake certifies broken
   firmware. Credit any concrete example of this.
5. **A simulator** (Wokwi supports ESP32-C6 and MicroPython, with custom chips in C for parts it
   lacks) as the layer above, and the honest statement that none of this replaces a bench.

A strong answer gives ordered layers with what each catches and what it costs. A weak answer
recommends a single technique, or recommends hardware mocking without saying where the seam goes.
