The answer must get the wake constraint right. Score on these, each worth equal weight:

1. **Only GPIO0-7 can wake an ESP32-C6 from deep sleep**, which on the XIAO means D0, D1 and D2
   and no other header pin. An answer that puts a wake source on D3-D10 without flagging this is
   wrong, and the failure is silent: the board sleeps and never wakes.
2. **`esp32.wake_on_ext0` does not exist on the C6** (it is RTC-IO based, which this chip lacks).
   `esp32.wake_on_ext1` is the call that works; `wake_on_gpio` also exists on recent builds.
   Recommending `wake_on_ext0` is a straightforward error.
3. **`Pin.irq(wake=machine.DEEPSLEEP)` silently does nothing** on this chip — it does not even
   raise. Worth warning about; not required.
4. **All ext1 wake pins share one polarity**, so every wake source must idle at the opposite
   level. A button wired to ground asserts LOW and cannot wake a chip armed for HIGH. An answer
   that mixes a ground-wired button with wake-on-high is describing a device that never wakes.

A strong answer names the specific pins, the specific API, and the polarity trap. A weak answer
gives generic ESP32 deep-sleep advice that would be right for an original ESP32 and wrong here.
