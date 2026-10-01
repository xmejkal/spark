# Should there be a firmware skill, and for which runtime? — P60

Written 2026-10-01 by five lenses — runtime, measurement, facts at source, architecture, the DIY
builder — each reproducing its claims before writing them (W9). **No code was written to produce
this.** The Product Owner asked, explicitly to be taken up on restart:

> "do you think we should have something like micropython skill so that claude can write the
> firmware well? Or also Arduino or ESP-IDF"

It follows from P56: if the conversation writes the firmware, how well it writes it is the product.

## The answer in one line

**No skill. One runtime, MicroPython. The facts a model gets wrong are chip, part and tool facts —
they belong in the records spark already keeps, delivered by the files the firmware imports and
enforced by the fake `machine` P56 planned; and the bin's notes must be corrected before anything
copies them, because their headline lesson is false.**

## Measured: what a model gets wrong with no help

A model that had read none of this project's notes — `claude -p` from an empty directory, no file or
web tools — was given seven firmware tasks these three designs need, phrased as a builder would,
never hinting at the trap. Two runs per model per task; graded against the source, not the notes.

| task | the fact | wrong without notes | with notes |
| --- | --- | --- | --- |
| a Wokwi scenario's expected ADC reading | Wokwi's ADC is referenced to 5 V (tool) | **4 of 4** | right, 4 of 4 |
| C6 deep sleep, wake on a button | `Pin.irq(wake=DEEPSLEEP)` does nothing on the C6 (chip-gated) | **3 of 4** | right, 2 of 2 |
| VL6180X interrupt configured active-high | register 0x011 = 0x30 (part) | **2 of 4** — both sonnet; the bin would never wake | not tried |
| soil probe on GPIO11 with WiFi on | ADC2 is unusable with WiFi (chip) | 1 of 4 | right, 1 of 1 |
| S3 wake on either of two sources | ext1, one level for all pins, `ANY_HIGH` | 0 of 4 | — |
| a stroke that fires its own transition | a task cannot cancel itself (runtime) | 0 of 4 — run on MicroPython 1.29 too | — |
| tones on a MAX98357A over I²S | `machine.I2S` arguments, non-blocking writes | 0 of 4 | — |
| the C6's LP core | no API from MicroPython | 0 of 2 | — |

**10 of 30 non-empty runs were wrong; short notes fixed 7 of 7 reruns.** Counted from the lens's
`grades.tsv` by the facilitator after the runs.

Read the table by class. **The one pure runtime fact — can't cancel self — every model already
knows**, and so the I²S API, ext1's single level, the missing LP-core API. A MicroPython skill would
carry exactly those, and be bloat. What models get wrong is **what a chip, a part or a simulator
does**, which is what spark's records are for.

Limits, stated: the installed CLI reaches `claude-opus-5` and `claude-sonnet-5`, not this session's
Opus 5.5; no web tools; user-level plugins still loaded; two runs per cell.

### Rerun on the 5.5 models, as the PO asked

Same prompts, same grading, `claude-opus-5-5` and `claude-sonnet-5-5` (CLI 2.1.285, each run's
JSON names its model). **4 of 32 graded runs wrong, every one of them the Wokwi ADC task** —
counted by the facilitator from `grades55.tsv` after the runs; four opus runs timed out at 500 s,
were rerun at 1200 s, and are graded from the rerun.

| task | 5.0 wrong | 5.5 wrong |
| --- | --- | --- |
| Wokwi's 5 V ADC (tool) | 4 of 4 | **4 of 4** — *"raw ≈ 2482 … ≈ 2.000 V"*; Wokwi gives 1638 and 1.32 V |
| C6 deep-sleep wake (chip) | 3 of 4 | 0 of 4 |
| VL6180X GPIO1 register (part) | 2 of 4 | 0 of 4 |
| ADC2 with WiFi (chip) | 1 of 4 | 0 of 4 |
| the four runtime tasks | 0 of 14 | 0 of 16 |

**So the answer stands, and narrower.** The chip and part facts the older models missed, the newer
ones know. The one fact both generations miss — 8 of 8 — is a fact about the **simulator**, and a
two-line note fixed it 4 of 4 on 5.0. A MicroPython skill would carry nothing the current model
lacks; what it lacks belongs with the simulation, printed where a scenario's expectations are
written. Two outdated beliefs persist on 5.5 and cost nothing yet: that MicroPython cannot say
which ext1 pin woke it (it has `machine.wake_pins()`), and, once in four, that the S3 has no ext0.

## Verified at source: the bin's lessons are not all true

Twenty-four candidate facts, checked against MicroPython v1.29.0 (what the bin's image reports),
ESP-IDF v5.5.2, Espressif's documentation and Wokwi's. 19 true, 2 narrower than written, 2 false,
1 unverifiable.

- **"`WAKEUP_ALL_LOW` is an AND across every armed pin" is false on the S3 and C6.** ESP-IDF
  `esp_sleep.h` defines a true ALL_LOW only `#if CONFIG_IDF_TARGET_ESP32`; on every later chip it is
  a deprecated alias of `ANY_LOW` — an OR. MicroPython passes it straight through
  (`modmachine.c:159`). Read by the facilitator in the downloaded header. Commit `fd24455` in the bin
  ("Deep sleep never woke") was diagnosed from this, on no hardware. Its fix — `ANY_HIGH` — still
  works; its reason is wrong. **The false version is in spark's own `parts/tactile-button.json:37`**,
  which every future conversation reads, and in the bin's `CLAUDE.md`, `HANDOVER.md`, `STATUS.md`
  and `config.py`. One probe model said the right thing unprompted.
- **"`Pin.irq(wake=DEEPSLEEP)` silently no-ops on both chips"** — on the C6 only. On the S3 a
  level trigger arms ext0. With an edge trigger, `wake=` is ignored on every chip.
- **"No LP core from MicroPython"** — true of the C6; the S3's ULP-FSM is `esp32.ULP`.
- **The PSRAM deep-sleep figure** — see P61: the kept datasheet puts 140 µA on Light-sleep.

**A skill written from the bin's notes today would have taught the false fact as its headline.**
That is the strongest single argument in this document, and it argues for checks over prose: a fake
seeded from the source would have refused to agree.

## Why not a skill, beyond the measurement

- **It was built and deleted.** The 09-29 cut removed `agents/firmware-engineer.md`, which held
  P60's candidate facts almost word for word, and `skills/spark-simulate` with its
  `references/fake-machine.md` — *"my working process shipped as product; nothing routed to them."*
- **A skill triggers on its description**, so a "MicroPython" skill would fire on every MicroPython
  request in every project where spark is installed (inference, untested).
- **Neither defect a conversation actually shipped was a knowledge gap.** `irrigation/firmware/main.py`
  cannot be imported and drives three of four valves; the builder lens found a third — `BUTTON_PIN =
  18` is never read. Claude knows an importable main; it was writing for a simulator. Those are
  P59's job.
- **The facts are already in the records, and nothing reads them.** Both board records carry
  `wake_capable_gpio`, `adc_gpio` and a `deep_sleep` block (`wake_api`, `single_pin_api`,
  `single_polarity_for_all_pins`, `simulated_by_wokwi`). Only the first two are consumed
  (`assign_pins.py:129,131`). A 30-line `esp32` fake seeded from them, written in scratch, refused
  ext1 on the S3's GPIO47 and raised on `wake_on_ext0` for the C6 — the bin's own fake accepts both.

## Runtime: MicroPython, and what would change that

Every design is MicroPython or names it: the bin's v2 (113 tests, 14 checks on the real runtime,
both rerun), irrigation's `main.py`, the RC car's plan (*"MicroPython + espnow"*). Board records carry
`micropython_port` and nothing else for a runtime; `flash_image.py` is MicroPython-only. `grep` over
the requirements and plans for arduino, idf or platformio: nothing.

**Arduino** comes in when a design needs a vendor driver that exists only as an Arduino library, or
a builder arrives with a sketch. **ESP-IDF** when a design needs what MicroPython cannot reach. The
popularity argument for Arduino among hobbyists is plausible and unmeasured — no survey was found.
The cheap hedge: P36's export is data first, rendered as Python, so a later `pins.h` is one renderer.

## What this binds

- **P36**: the pin file is plain integer assignments, not `const()`, so it imports under CPython (T1)
  and MicroPython alike. Its comments may carry the record facts for each pin — *"GPIO11: ADC2,
  unusable with WiFi (board record)"* — which is the probe's "notes fixed it", delivered at the
  moment of writing, from a record, inside P56's boundary.
- **P59**: its acceptance line is **false as written** — `python3 -c "import firmware.main"` fails on
  a correct firmware too, for want of `machine`. It needs the fake on the path. And it must cover
  inputs, not only outputs (the unread button).
- **P56 increment II**: the fake `machine`/`esp32` seeded from the board record is where these facts
  become enforced — wake on a non-wake pin, `Pin.irq(wake=)` on a chip without ext0, ADC2 with WiFi.
- **Facts to file where they belong**: the VL6180X's GPIO1 register in its part record; Wokwi's 5 V
  ADC in the simulation's what-this-cannot-show (today it is only in `commands/build.md`, which a
  conversation writing a scenario's expectations has no reason to open — and 4 of 4 runs got it wrong).
- **The builder's first gap is not knowledge at all**: nothing in spark or the bin says how to put
  MicroPython on a board (`esptool`, `mpremote` appear nowhere). That is P56's increment III.

## Found on the way

- The bin's `firmware/micropython/tests/fake_machine.py:245` accepts ext1 on any pin.
- `boards/firebeetle2-esp32s3.json:283` says `WAKE_ON_HIGH is False`; the bin's `config.py:184` says
  `True` — one project's config copied as prose into a shared record, gone stale.
- `boards/xiao-esp32-c6.json:102` `single_polarity_for_all_pins: true` describes MicroPython's API,
  not the C6, which has per-pin mode.
- The C6 record has no strapping role, and its `onboard_led` GPIO15 is a strap.
- Wokwi does not implement I²S on the S3 (its ESP32 guide); the converter blames the missing part.
- The models believe MicroPython cannot say which ext1 pin woke it; current source has
  `machine.wake_pins()` — outdated, not wrong in effect.

The corrections are **P63** in the backlog. The order is the PO's.
