# Does spark produce tested firmware? — P56

Written 2026-10-01 by five lenses — embedded firmware, test strategy, the DIY builder, architecture,
and scope — each reading the repository and the three cold-test projects, and each reproducing its
claims before writing them (W9). **No code was written to produce this.**

The Product Owner set the question and then narrowed it mid-analysis, which is why the document
answers a sharper question than it was asked:

> "the whole point, to make DIY projects with ESP32 … to write the firmware and then simulate and
> test it to make sure it actually works all together" … "we want to give claude the option to write
> the firmware using the info we gathered and to somehow test it to make sure it will work on the
> hardware. And then in the end, probably real on device testing."

## The answer in one line

**spark exports facts and ships a harness; the conversation writes the firmware; the bench is a
protocol, not a program.** No lens argued for a generator, and the PO ruled one out.

## Why it matters now: measured, not argued

- `irrigation/firmware/main.py` is **95 lines with zero tests of any kind**. `rc-car` has no `.py`
  file at all. The smart bin has 4,360 firmware lines and 2,430 test lines — **the PO's own work
  over weeks, not spark's output.**
- **spark ships no way to run firmware.** `grep -rl "import machine|fake_machine|FakePin"` over
  `scripts/ tools/ skills/ commands/` returns **nothing**. So the only thing that can ever execute a
  spark-generated project's firmware is a **metered** simulator. That is the whole of the PO's cost
  question, in one sentence.
- **`assign_pins` computes the pin map and throws it away.** Each assignment carries signal, pad,
  GPIO, the reason it was chosen, and its role warnings — and there is no `--emit-pins`. The builder
  then types the GPIO by hand, which is the irrigation defect exactly (P36).
- **spark ships a reviewer that cannot do one of its four jobs.** `agents/design-reviewer.md:41`
  offers a **firmware-hardware** dimension and is told to read "the firmware configuration". spark
  produces no firmware and no pin map. That is W1's own shape, shipped as a feature.

### The defect that settles the simulation question

The test lens wrote a ten-line check and ran it on `~/Development/irrigation` **free, in about a
second**: `VALVE_PINS = (38, 11, 12, 13)` — four valves, as the requirements ask and the board
routes — but the loop runs over three probes, so **GPIO13 (Valve4) is set to 0 at boot and never
driven again**. The paid Wokwi scenario asserts two pins and passed straight over it.

The firmware calls itself "a stub for the simulation, not the product", so it may be deliberate —
which renames the defect rather than removing it: **nothing anywhere says the stub covers less than
the design asks for.**

### And the simulation it did pass is partly a tautology

`irrigation/sim/chips/soilprobe.chip.c` defines `VOLTS_IN_AIR 2.9f` and `VOLTS_IN_WATER 1.2f` and
computes a voltage from a percentage. `firmware/main.py` defines `VOLTS_DRY, VOLTS_WET = 2.9, 1.2`
and computes the percentage back. **The scenario asserts that the firmware can invert a formula we
wrote twice**, and bills minutes to do it. Of seven part records, **zero are the real part**: two
skipped, two built-in stand-ins, two chips we wrote, one with no entry.

## The four tiers, and what each can honestly promise

| tier | catches | cannot | cost | spark can |
| --- | --- | --- | --- | --- |
| **T0 contract** — firmware GPIO ↔ board file ↔ netlist; declared-but-undriven pins; ADC2-with-WiFi; strap pins | retyped pin constants, unused peripherals, a pin doing two jobs | anything about values or timing | ms | **generate** — it owns both sides |
| **T1 unit over a fake `machine`** | arithmetic, state machines, register conversations, retry paths | MicroPython semantics, electricity | 2 s | **scaffold** — the fake is generic; the tests are written in conversation |
| **T2 real runtime** (`micropython` unix port) | MicroPython-vs-CPython divergence — `ticks` wrap, `const`, `RuntimeError("can't cancel self")` | the real `machine`, boot, electricity | ~1 s | **generate the harness** |
| **T3 simulation** | wiring-as-drawn, interrupt/ADC interaction, boot from a real flash image | see above — on irrigation, nothing about the hardware | **paid** | already does |
| **T4 bench bring-up** | the only tier that touches copper: solder bridges, wrong-rail parts, a module at the wrong address, stall current, wake from deep sleep | nothing cheaper — it is the ground truth | a human's minutes | **generate the skeletons** |

**The structural point:** T1–T3 can only ever promise *"when the hardware behaves as the part
records say, the firmware does the right thing."* **They cannot test the antecedent.** Only T4 does,
which is why it is the tier spark should generate rather than hope the builder writes.

### T4's own evidence, from the bin

`bringup/01_board_alive.py` carries the argument in a comment:

> `PIN_USER_LED = 21` … *"This was GPIO15 for the XIAO ESP32-C6. On this board GPIO15 is MOSI, a
> bare header pin, so step 1 failed on a good board and the obvious conclusion was 'bad board or
> bad flash'."*

A T0 defect caught at T4 — the most expensive possible place, where a beginner bins a working board.
And spark's board record already holds `pin_roles.onboard_led.gpio`, for every board in the library:
**step 1 is derivable with zero guessing today.**

**Live, unfixed, in the bin right now:** `firmware/micropython/README.md` steps 2–4 name the
**XIAO's** pins — "OPEN btn D1, MODE btn D6, LED D7/D10", "VL6180X on D4/D5", "DFR0534 on D9" — and
a script that no longer exists. The same failure, moved into prose, in the instructions somebody
follows while holding a multimeter.

## The boundary

**spark may emit what is derived from records it already holds and would otherwise be retyped. It
must not emit anything that encodes behaviour.** A generated `pins.py` is a lookup table nobody
needs to read; a generated state machine is a codebase somebody must adopt — and the bin's is 4,360
lines, which is the worst thing this plugin could hand a stranger who wants to blink an LED.

The test is mechanical: **if spark cannot point at the record each line came from, it is bloat.**
`init_project.py`'s own docstring already forbids the move — *"An init that guessed `max_current_a`
from a part name would poison the one check that does arithmetic."*

**Never exported:** thresholds, timings, profiles, state tables, sound tables, drivers.
`host_requirements`, `facts` and the stand-in sentences are prose **for the author**; `parts.py
--show` and `WHAT-THIS-CANNOT-SHOW.md` already deliver them to the human and the conversation.
Rendering an argument as a constant destroys the argument.

## What makes a generated test suite worthless, and the mechanical cure

The PO's narrowing inverts the usual risk: the firmware is hand-written, the **tests** may be
generated. Four failure modes, each with a gate that fails a command rather than asking for care:

1. **The assertion is an identity of the function.** Generated assertions may use literals from the
   **part record** only, never an expression imported from the firmware.
2. **The fixture cannot see the defect (W12).** Ship a **generated mutation table** beside the
   generated tests — one mutation per constant the pin map and records contributed. spark already
   owns `mutate.py` and has never pointed it at firmware. This is the highest-value mechanism the
   repository already has and does not use.
3. **It passed because it could not look (W1).** No `micropython`, no `mpy-cross`, no device ⇒
   **could-not-run**, never 0. The runner imports `outcomes.py` rather than inventing statuses.
4. **It never ran the thing (W2).** **The precondition for three of the four tiers is one line:**
   `irrigation/firmware/main.py` calls `main()` at module scope and `main()` is `while True`, so the
   file **cannot be imported** and no test can ever exist for it, by anyone. Make "the firmware
   imports without side effects" a check, not a convention.

## The architecture, in three increments

**I — the facts. ~70 code lines; fits today's budget (290 spare of 4,000).**
`assign_pins --emit-pins` → `.spark/pins.py`, generated with a header, imported by firmware *and*
bring-up scripts. `check_spine` writes it beside the kept board. A sixth `check_all` entry compares
every GPIO literal in the project's firmware against the pin map — the bin's hand-written 121-line
checker, generalised. **This alone gives a generated project a test it does not have.**

**II — the harness. A new top-level directory with its own ceiling.**
A fake `machine` seeded from the board file that **refuses**: a GPIO the board does not have, an
`ADC` on a pin outside `adc_gpio`, `wake_on_ext1` on a pin outside `wake_capable_gpio`, a second
`Pin` on a GPIO another signal claimed. **Four defect classes failing for free on a Mac** — which is
what the paid quota currently buys, and buys worse. The bin's fake is 215 code lines and
**permissive**: `Pin(99)` and `ADC(Pin(47))` both succeed today. Validation makes it ~250–280.

> **The budget is the binding constraint and must be decided, not discovered.** 290 code lines spare;
> the fake alone is ~250. W15b's order is refactor → delete → raise, and refactor is already ruled
> out in writing by the 09-30 architecture document, while delete is spent. The honest answer is
> **neither**: the 4,000 is a ceiling on *the chain's deterministic Python*, and making it also hold
> a MicroPython test library would make one number mean two things.

**III — the bench. Mostly documents.** One step per part in dependency order — derivable from the
records; each step prints the GPIO **and** the silkscreen name it believes it is driving, so a
failure is diagnosable without a scope. Not derivable, and left as slots: *"SPK+ and SPK− are the
RIGHTMOST pad of each row"*, *"if open actually closes, swap the two wires"*. Those are bench scars.

**Stopping rule:** stop when a generated project can fail **on a Mac** for a reason that previously
needed a paid simulator minute. Increments I and II do that.

## What this costs, and the warning the scope lens attached

P32a cost ~1,116 lines of TypeScript, a dependency tree, a gate change and 7 anchors — and found a
live regression on arrival. A firmware story is that size again. **Two absorptions in two sprints is
where a plugin stops being a plugin**, which is the argument for doing increment I alone first.

And the sprint data, which the PO asked for plainly: Sprint 6 put eight items in 4h12m and Sprint 7
four more; of those twelve, **five acceptance lines were false on contact** — a 42% rate — every one
caught by W20, adopted the morning it was first needed. Both sprints found faults in their own
record **at close**, so the record is now repaired rather than correct when written. R5.2 has rolled
forward three sprints untested.

**The lens's recommendation, in its words: finish v1 first.** It is two small items from closing, and
the direction is right but the sequencing is not.

## v1 is not closed, and R7 overstated it

R7 wrote "the v1 line now holds mechanically". That is true only of the stranger clause. Reproduced
today on the documented example: `[FAIL] buildability` on **four** 0.225 mm annular rings and
`[????] physics` with **all four rails** unstated. v1's own words are *"no false alarms from the
checks"*.

The rings come from **stand-in footprints**, and P37 established that a stand-in declares what it
cannot show — so that is a **could-not-run naming the stand-in**, not a FAIL. That ruling is P57 and
it closes v1's last mechanical hole.

## The decision the PO took, 2026-10-01

**Close v1, then bridge.** Sprint 8 is P52 → P57 → P36 → P54 → P55 — five items, deliberately below
Sprint 6's pace. P36 is the bridge: the smallest thing that proves the direction, with no new
concept, no quota and no bench.
