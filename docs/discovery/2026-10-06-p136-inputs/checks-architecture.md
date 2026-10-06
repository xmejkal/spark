# Why so much I2C, and how spark's checks can grow

*For Petr, answering your questions of 2026-10-06. Built from the four reports in this folder (`physics-rules.md`,
`other-checks.md`, `buses-in-the-chain.md`, `knowledge-loop.md`), with every claim the answer rests on re-checked
against spark at `8f7733d` (main, clean tree). Nothing in spark was edited, and its `git status` was empty before and
after every run.*

*How to read the references: a path is in spark (`/Users/petr/Development/spark`) unless it starts `smartbin:` (this
repo) or names a file in this folder. `#56` is a spark GitHub issue, read with `gh issue view`. A seven-character code
such as `dae10dd` is a commit. Anything I worked out rather than read is marked **INFERRED**.*

## Words used here

- **check**: a script that examines a design and gives the same answer every time. `check_all` runs five of them:
  vendor-truth, buildability, the-order, physics and rules-vs-netlist (`scripts/check_all.py:279-290`).
- **rule**: one question a check asks, such as "does each I2C line have a pull-up?".
- **netlist**: what connects to what on the built board, read from `circuit.json`.
- **part record**: spark's file for one module. It holds the module's pins and its **facts**, each with a value, a
  source, and whether anyone verified it.
- **pull-up**: a resistor that holds a line high while nothing pulls it low.
- **mutation table**: a list of deliberate bugs the tests must catch. It proves a test can fail.

## Short answers

1. **Why so much I2C?** Because spark's first project, the bin, used I2C and broke on it. On 2026-09-24 an audit
   found that the bin's board had no I2C pull-ups, although its own design rules required them (smartbin `022156f`).
   On the same day the physics check was created, and one of its first four rules was about I2C: the bin's
   pull-up arithmetic had used the wrong formula (`dae10dd`; `scripts/check_physics.py:9-18`). spark adds a rule
   only after a real design needed it, so the bus that broke first got the rules.
2. **Will it check SPI and the other buses?** Not today. spark places SPI and I2S pins sensibly, but no check
   looks at how they are wired. UART cannot even be declared as a bus. Worse, spark does not say it skipped them:
   the physics check gave a test board with SPI, UART, I2S, 1-Wire and an analogue input `status: ok`, exit 0
   (`repro-output.txt:34-36`, `:55`).
3. **Is I2C there because it was the first bus we used?** Yes. Each rule's own description names the board
   defect it came from (`scripts/compare_design.py:10-14`; `scripts/check_physics.py:9-18`), and none came from a
   list of standard checks.
4. **Is it built so new buses and rules can be learnt, like auto-learning?** It is partly built for growth, and it
   does not learn by itself.
   - A whole new check plugs in cleanly, and tests guard it.
   - A new rule or a new bus is hand-work in several files.
   - The I2C knowledge is spread over five files that already disagree once. Because of that, one I2C rule
     silently skips every board spark generates.
   - Your process is the learning loop, and you are its gate.
5. **Should we predefine basic checks?** A few, not a catalogue. I recommend a mix (section 5), in this order:
   - make the I2C checks honest;
   - have every check say what it did not examine;
   - build a small number of rules that work for any bus by reading facts the part records already hold.

   After that, Claude proposes new rules from each project and you accept or reject them. Checks specific to SPI,
   I2S or UART wait for a design that uses them.

## 1. Why I2C shows up so much

### It broke first

| Rule | Born | The defect behind it | Evidence |
| --- | --- | --- | --- |
| `i2c-pullups` (rules-vs-netlist): each I2C line has a pull-up to a supply, between 1 and 10 kΩ | 2026-09-24, in the file's first commit | The bin's design rules required I2C pull-ups, and "the board carried six resistors and not one was a pull-up" | smartbin `022156f`; `scripts/compare_design.py:10-14`; `55d2368` |
| `i2c-rise-time` (physics): the pull-up can raise the line within the time the bus speed allows | 2026-09-24, one of the four rules physics was created with | The bin's pull-up arithmetic used the wrong formula. That formula overstates the rise by 42 % and "turned a pull-up that was fine into one that looked twice over spec" | `tests/test_check_physics.py:10-13`; `scripts/check_physics.py:62-66`; `dae10dd` |
| A part record on I2C must say where its pull-ups come from: the module or the board | 2026-10-01 (P55) | The FireBeetle V1.2+ has no I2C pull-ups anywhere. A record's "this module has pull-ups" fact was read by no script, and flipping it left every test green | `scripts/parts.py:384-409`; `c0e3d76` |
| Every device on a bus line shares it | 2026-09-29 | A part given its own name (`RANGEFINDER_SDA`) silently left the bus for another pin (audit B2, B3) | `scripts/assign_pins.py:174-176`; `7381fed` |

The 2026-09-25 cold rebuild taught two more I2C lessons:

- **R20.** A reference text taught 4.7 kΩ pull-ups, which the physics rule rejects at 400 kHz. It was fixed
  (`docs/observations/INDEX.md:79`; `f35e7df`).
- **R16.** It asked the rise-time rule to read the board revision's own pull-ups (`docs/observations/INDEX.md:75`).
  That lesson was lost (section 4).

### It is most of what you have used

I counted every part record that declares a bus (`count_bus_needs.py` in this folder), across:

- spark's library;
- your shelf and your catalog;
- the project folders.

| Bus | Distinct parts |
| --- | --- |
| I2C | 7: the VL6180X and six real-time-clock modules |
| I2S | 1: the MAX98357A amplifier |
| SPI | none, anywhere |

UART cannot be declared at all. The DFR0534 MP3 module records its serial line as a plain signal
(`parts/dfr0534-module.json:8-13`); declaring `uart` is refused (`scripts/parts.py:538-541`).

### It is the bus a board check can see

I2C chips only ever pull a line down. A resistor on the board pulls it back up, and without one "the bus never
leaves logic 0 and nothing answers" (`scripts/compare_design.py:121-122`). So whether I2C works depends on parts on
the board, and the netlist shows those parts.

SPI, I2S and UART chips drive their lines both up and down. A missing resistor does not break them; their failures
are about speed, direction and voltage levels. **INFERRED**: this is general electronics, and the code states only
the I2C half.

1-Wire works like I2C: one line with a pull-up. So it would be the same arithmetic, and spark has no rule for it.
**INFERRED**.

### Nothing else was allowed in without a design

- **Your working agreement W14, "Pull, never push":** "Nothing enters the plugin unless a real design is blocked
  without it that week" (`scrum/WORKING_AGREEMENTS.md:150-159`).
- **The 2026-09-29 cut:** "Petr's call … no AI bloat, nothing kept that nothing uses". It deleted 5,962 lines built
  ahead of need (`066c4af`; `scrum/VISION.md:66`). Among them was spark's only check for two I2C devices at the same
  address, removed because "no project needs" it (`066c4af`; the check began at line 219 of
  `git show 066c4af^:scripts/check_design.py`).

So the I2C weight comes from history plus your policy. It was never a design decision.

## 2. What spark checks today, per bus and signal kind

How to read the table:

- **Pins assigned**: spark's pin assigner puts the signal on a suitable pin.
- **Wired**: spark's board generator connects it, and places any resistors the part record asks for.
- **Checked**: a check examines the result and gives the same answer every time.

The AI reviewer judges rather than checks, so it comes after the table.

| Bus or kind | Pins assigned | Wired | Checked | How |
| --- | --- | --- | --- | --- |
| **I2C** | Yes. The board's SDA and SCL, shared by every device (`scripts/assign_pins.py:166`, `:224-225`) | Pin to pin (`scripts/emit_board.py:734-735`). Pull-ups are placed when the record asks for them, tied to the part's own supply (`scripts/emit_board.py:634-640`) | **Yes: three rules, with holes (listed below)** | <ul><li>The record says where its pull-ups come from (`scripts/parts.py:384-409`).</li><li>Each line has a pull-up to a supply, each between 1 and 10 kΩ (`scripts/compare_design.py:117-174`).</li><li>Rise time against bus speed (`scripts/check_physics.py:396-425`).</li></ul> |
| **SPI** | Yes. SCK, MOSI and MISO are shared; each device gets its own chip-select (`scripts/assign_pins.py:166`, `:268-271`) | Pin to pin | No | No rule reads SPI. No part in any layer uses it yet (`count_bus_needs.py`) |
| **I2S** | Yes, on any pin through the chip's internal routing. Never shared between devices (`scripts/assign_pins.py:166`, `:289-312`) | Pin to pin | No | The amplifier's hazards are text that no code reads, for example "NEVER stop LRCLK while BCLK is running" (`parts/max98357a-dfr0954.json:178-180`) |
| **UART** | Not as a bus. Declaring `uart` is refused (`scripts/parts.py:538-541`). The console pins are spent last (`scripts/assign_pins.py:72-79`) | Pin to pin, as a plain signal | No | <ul><li>The check for a serial part on the console was cut in `066c4af` (it was `git show 066c4af^:scripts/check_design.py`, lines 208-214).</li><li>TX-to-RX crossing cannot be described: a line matches the board's label for the same line (`scripts/parts.py:250-256`).</li></ul> |
| **1-Wire, CAN, others** | No. They are not in the bus list (`scripts/parts.py:257-262`) | As plain signals | No | — |
| **Analogue inputs** | Yes. Only on ADC1 pins, because ADC2 cannot be read while WiFi is on (`boards/firebeetle2-esp32s3.json:198-199`; `scripts/assign_pins.py:131-132`) | Pin to pin. A divider is added if the record asks for one (`scripts/emit_board.py:624-656`) | No | No rule looks at what feeds an ADC pin. On the bin, `SENSE_ADC` (a 1 kΩ resistor and a filter capacitor) is examined by nothing (`physics-rules.md:440`) |
| **Plain digital inputs** | Yes | Pull-downs or pull-ups, if the record asks for them (`scripts/parts.py:326-330`) | **Yes** | <ul><li>`floating-input`: each declared input sits on a supply or on ground, or on a resistor to one (`scripts/compare_design.py:177-212`).</li><li>The inputs come from every input pin the part records declare (`scripts/init_project.py:80-100`).</li><li>Whether a pin is pulled the right way, up or down, is not checked: either rail passes (`scripts/compare_design.py:188-189`).</li></ul> |
| **Level shifting, logic levels** | — | A divider, built from the two values the record states (`scripts/parts.py:326-330`) | No | <ul><li>Nothing compares the divided voltage with the pin's 3.3 V. That arithmetic lives in the record's text: the irrigation flow meter's divider `why`.</li><li>The VL6180X's `carrier_has_level_shifters` fact has no reader (`parts/vl6180x-breakout.json:63`).</li><li>`pull_conflicts` does one such sum (`scripts/parts.py:1284-1315`). It only prints, and `check_all` does not run it (P109, #43).</li></ul> |
| **Strapping pins** | Refused by the assigner, even when a record names one (`scripts/assign_pins.py:59-61`, `:244-250`; `boards/firebeetle2-esp32s3.json:213-218`) | — | No | On a hand-made board such as the bin, nothing in spark compares the pin map with the strapping pins. A search finds them only in `assign_pins.py`, `boards.py` and one comment in `emit_board.py` |
| **Current per pin** | — | An LED's series resistor is computed from the current asked for, rounded up so the current never exceeds it (`scripts/emit_board.py:595-617`) | No | Nothing compares a pin's current with the chip's limit. The 40 mA figure sits only inside a source string (`boards/firebeetle2-esp32s3.json:416`) |
| *Power rails, for comparison* | — | Trace widths are sized from the current | **Yes: four rules** | <ul><li>Trace current, rail supply, capacitor voltage and resistor power (`scripts/check_physics.py:196-393`).</li><li>Rail supply runs only through `check_all --project` (`scripts/check_physics.py:450-454`).</li></ul> |

**The holes in the I2C rules.** Each one was reproduced.

- **The rise-time rule is silent on every board spark generates (P122, #56).**
  - `init` writes each bus line as `Component.PIN`, "because spark's own generator wires every signal pin-to-pin and
    no net is ever called SDA" (`scripts/init_project.py:117-119`).
  - The rise-time rule finds a line by net name only (`scripts/netlist.py:135-138`). When it finds nothing, it moves
    on without a word (`scripts/check_physics.py:410-411`).
  - I re-ran the probe (`probe_bus_line_forms.py`) with a 9.1 kΩ pull-up at 400 kHz. On a net named `SDA` it fails:
    386 ns against a 300 ns limit. Written as `Sensor.SDA`, the same resistor gets no finding at all.
- **A series resistor counts as a pull-up, and can hide a failing bus** (`scripts/check_physics.py:406-409`;
  `repro-output.txt:13-14`). `compare_design` already leaves such resistors out (`scripts/compare_design.py:144-150`).
- **The module's own pull-ups are left out, and nothing checks the combined pull-up from below.**
  - The VL6180X carries 10 kΩ pull-ups and asks the board for 4.7 kΩ more (`parts/vl6180x-breakout.json:96`,
    `:161-169`). Together that is 3.2 kΩ per sensor.
  - Four sensors on one bus make 799 Ω. That is below spark's own 1 kΩ floor, below which "the driving pin cannot
    pull it down" (`scripts/compare_design.py:28-32`).
  - Every resistor still passes when judged on its own (my arithmetic).
- **A pull-up to a supply tscircuit has not marked as power is reported missing.** This is a false alarm
  (`other-checks.md:168-180`). tscircuit leaves the bin's MOTOR6V unmarked.
- **Two devices at one address build cleanly.** Two VL6180X, both at address 0x29, build with exit 0
  (`tests/test_emit_board.py:767-777`; `parts/vl6180x-breakout.json:45-46`).
- **An empty bus capacitance crashes the rule, and a missing one becomes 50 pF without a word** (P107, #41;
  `repro-output.txt:16-21`).

**Everything else gets silence.** When no rule covers something, spark says nothing. That is the bigger problem,
because silence looks like a pass. The only thing that looks at the other buses is the AI reviewer's `signals`
dimension: "logic thresholds…, pull-ups and their budget, bus loading and rise time, level shifting"
(`agents/design-reviewer.md:39-40`). It is judgement, not a check, and it "does not remember between sessions"
(`skills/spark-review/SKILL.md:86-87`).

**On the bin today:**

- Its `make check` runs physics directly (smartbin `Makefile:228`). That way the rail-supply rule never runs
  (`scripts/check_physics.py:450-454`, `:537`).
- The I2C rule does run, because the hand-made board names its nets SDA and SCL. It passes: 2.2 kΩ at the stated
  50 pF rises in 93 ns, against a 300 ns limit (`physics-rules.md:437-440`).
- The audio lines and `SENSE_ADC` are examined by nothing.
- Through `check_all`, physics is marked "could not look", because "0 requirements files describe this circuit,
  so no rail was summed from the part records" (`check_all_bin.txt:12-17`).

## 3. How well the architecture extends today

The answer differs by size, from best to worst.

### Adding a whole new check: well built

- There is one list of checks, `check_all.CHECKS` (`scripts/check_all.py:279-290`), and one set of answer words
  (`scripts/outcomes.py:23`).
- Forgetting a step fails a test:
  - a check script that is not wired in (`tests/test_check_all.py:583`);
  - a wired check with no test case (`tests/test_check_all.py:168-171`);
  - a file that no mutation touches (`tests/test_self_confirmation.py:116-121`).

### Adding a rule inside a check: hand-work

- **No list of rules.** A rule is a hand-written function, called by name inside its check
  (`scripts/check_physics.py:428-489`; `scripts/compare_design.py:215-224`). So nothing can list which rules exist,
  or which incident each came from.
- **Severity is free text.** A misspelled severity disappears. "problems" instead of "problem" gave
  `status: ok`, exit 0 (`scripts/check_physics.py:84`, `:538`; `physics-rules.md:433-434`).
- **Each check reports its findings its own way** (`scripts/check_physics.py:81`; `scripts/check_footprints.py:48`;
  `scripts/compare_design.py:44`; `scripts/check_bom.py:77-80`; `scripts/check_vendor_pins.py:147-149`). `check_all`
  flattens them to text and drops the suggested fix (`scripts/check_all.py:129`, `:139-141`; P43, parked).
- **What past rules cost**, measured with `git show --numstat`:

| Change | Commit | Files | Script lines | Test lines | Mutation table |
| --- | --- | --- | --- | --- | --- |
| A part-record rule: I2C pull-ups (P55) | `c0e3d76` | 6 | +29 | +64 | +38 |
| A netlist rule: floating input (B13) | `4daa58f` | 5 | +38 / −8 | +51 / −6 | +12 |
| A physics rule fed by records: rail supply (P52) | `3749303` | 10 | +226 / −19 | +278 | +128 |
| A bus vocabulary, placement only | `07821a0` | 5 | +62 / −19 | +60 | +32 |

A rule that needs a new field in the project's rules file costs more. It also touches `init`, two guides and every
existing project's `.spark/rules.json` (`physics-rules.md:201-209`).

### Adding a bus: placement only, built around I2C

- **A bus is one entry in `parts.BUSES`** (`scripts/parts.py:257-262`). That buys validation and pin placement,
  nothing electrical.
  - No table says whether a bus is open-drain, needs pull-ups, idles high or has a speed limit.
  - Each I2C rule restates those things in its own code.
- **I2C knowledge is spread over five files:** `parts.py`, `assign_pins.py`, `init_project.py`, `compare_design.py`
  and `check_physics.py` (`other-checks.md:134-146`). Two of them disagree on how to find a bus line, and that
  disagreement is the silent pass above.
- **The project's rules file is built around I2C.** It has one `i2c_hz` and one capacitance per project, and no
  slot for another bus (`scripts/check_physics.py:469-476`).
- **UART needs more than a list entry.** Its TX goes to the other side's RX, and on the FireBeetle the pins labelled
  TX and RX are the console (`boards/firebeetle2-esp32s3.json:256-262`). **INFERRED** that this needs a change of
  shape (`knowledge-loop.md:305`).
- **A rule across several parts on one bus has no home.** Address clashes, combined pull-ups and the slowest
  device's speed would all need one. The assigner works out who shares each bus, then throws that away
  (`scripts/assign_pins.py:259-276`, `:316`).

### What already works as data, with no code change

- **A fact in a part record changes an outcome**, if a rule reads that fact's exact name. This was shown live on
  the motor rail (`knowledge-loop.md:224-231`):

  | The L9110S's supply pin points at | Result |
  | --- | --- |
  | its 0.8 A fact | a pass, instead of "could not run" |
  | a 2.5 A stall figure | a problem |

- **Only eight fact names are read by code** (`scripts/parts.py:398`, `:405`, `:1294`, `:1312`;
  `scripts/emit_board.py:603`), plus any current a power pin points at (`scripts/emit_board.py:398-420`). The other
  facts, roughly 550, are shown to a person or to nobody (`knowledge-loop.md:103-112`).
- **Fab numbers** live in `data/fabrication.json`, and a project can override them (`scripts/fab.py:35-38`).
  Copper thickness is the exception: the trace-current rule ignores a project's value (`repro-output.txt:38-43`).
- **Board files steer placement:** ADC pins, wake pins and pin roles (`scripts/assign_pins.py:117-160`).
- **Resistors a record asks for** are placed on the board, and `init` turns them into rules to check
  (`scripts/init_project.py:80-131`).

### What is hard-coded

- **Every rule's logic**, on purpose: "a law or a published standard" stays "in CODE, beside the arithmetic"
  (`data/fabrication.json:3`).
- **The fact names the rules read.**
  - A fact stored under another name is silently unused (`scripts/parts.py:1295-1296`).
  - Research is asked in words, not exact names: "on-board pulls (ohms, rail); bus and address"
    (`commands/research.md:63`).
- **The lists of buses, shared lines, pin roles, capabilities and resistor kinds** (`scripts/parts.py:184`,
  `:257-262`, `:330`; `scripts/assign_pins.py:166`; `scripts/boards.py:91-103`). These are closed on purpose,
  because "an open vocabulary silently disabled a headline check" (`scripts/boards.py:85-90`).

**Verdict.** The architecture is good at the size of a whole check, and weak at the size of a rule or a bus.
Facts in records are the one part that grows without code. It works, but by accident: nothing declares which fact
names the rules read.

## 4. What "learning from experience" can honestly mean

spark is prompts plus scripts. Claude does not learn between sessions; a reviewer has "no memory of previous
reviews" (`agents/design-reviewer.md:30`). So in spark, learning can only mean writing something down in a form the
next run reads.

### What exists

- **Records that remember.**
  - Every fact carries a value, a source and whether it was verified. An unverified value must say why it matters
    (`scripts/parts.py:694-709`).
  - The shelf carries a project's records to every later project (`scripts/store.py:57-66`).
  - This is the one channel that improves with every project without code. It matches your own goal: "more parts
    known … proven by use … fewer requests, measured" (`docs/2026-10-04-store-design.md:13-15`).
  - "Proven by use" is designed (step T, `docs/2026-10-04-store-design.md:25-27`) but not built
    (`knowledge-loop.md:215-218`).
- **Warnings for people.** A record's `host_requirements` is text: "Prose on purpose" (`parts/l9110s-module.json:105`).
  It is printed and copied into generated boards, but never evaluated (`scripts/emit_board.py:931-940`).
- **Resistors a record can demand.** This is the one lesson channel with a fixed structure: pull-down, pull-up,
  divider or series (`scripts/parts.py:326-330`).
- **Reviewer agents**, one per area: power, signals, thermal-mechanical, firmware-hardware and manufacturability
  (`agents/design-reviewer.md:37-49`).
- **Rules born from incidents.** Each rule's description names its defect (`scripts/check_physics.py:9-18`;
  `scripts/compare_design.py:10-14`; `scripts/check_footprints.py:7-19`).
- **The intake.** A claim is logged, reproduced or rejected, then promoted to the backlog
  (`docs/observations/README.md:26-35`).
- **A findings store, now gone.** It was built in `02250ee`. It held "20 findings: 11 blocked, 8 open, 1 rejected,
  0 resolved", and was cut (`docs/observations/INDEX.md:15-19`; `066c4af`).

### The loop as it runs today

Every rule in section 1 came through these steps:

1. An incident happens.
2. It becomes a row in the observations index.
3. It is reproduced or rejected (W9).
4. It becomes an issue naming the design that needs it (W14).
5. It becomes a rule, with a test that fails first and a mutation table (Definition of Done,
   `scrum/README.md:98-113`).
6. A commit names the incident.

The loop is slow and gated by people, and it can lose a lesson:

- R16 asked the I2C rule to read the board revision's own pull-ups.
- It became P5, which was closed because "its audit was performed … its findings are P34 and P35, which carry the
  need" (`scrum/PRODUCT_BACKLOG.md:1636-1637`). Neither P34 nor P35 reads the board revision
  (`physics-rules.md:262-263`).
- No script reads `hardware_revisions` today (`docs/observations/INDEX.md:75`; `physics-rules.md:135`).

### What an automatic loop would need

**INFERRED**: none of these exists yet.

1. **A memory of findings and how they turned out:** confirmed on the bench, or a false alarm.
2. **A declared list of the fact names the rules read**, with their units, so research records exactly those names.
3. **Rules that can be a table row** wherever the physics is the same: one open-drain rule, one row per bus kind.
   A lesson can then often be data plus a source, rather than new code.
4. **A gate.** Each proposal arrives as an issue with *Needed by* and *Value proven by* (`scrum/README.md:95-96`).
   It comes with a test that shows the defect, and a mutation that proves the test bites.
5. **A track record for each rule:** what it fired on, and whether it was right. Then a rule that cries wolf can
   be retired.

### The risks

- **A rule learnt wrongly is a confident false pass.** It reads as checked when it is not, which is worse than no
  rule. The rise-time rule is already one on generated boards (P122). P133 (#67) gathers faults of this kind.
- **Or it is a false alarm, and people stop reading.** The code warns about this: "Nagging a board that has no bus
  is how a check earns a reputation for noise" (`scripts/check_physics.py:470-472`). So does the review skill: "a
  list that cries wolf is a list nobody reads" (`skills/spark-review/SKILL.md:64`).
- **One board is not a law.** P16 was dropped because "a wake-polarity rule derived from one board's constant is
  that board's knowledge" (`scrum/PRODUCT_BACKLOG.md:1634-1636`).
- **Text spreads errors.** One false sentence (ALL_LOW) reached the bin, irrigation and the RC car through copied
  `host_requirements` (`scrum/PRODUCT_BACKLOG.md:437-441`).
- **Record text that acts is a security question.** Record text already reaches the generated board unescaped (P87,
  #19; `scrum/PRODUCT_BACKLOG.md:973-981`). Rules written as data from records would widen that. **INFERRED**.

### How it fits your process

- You decide what gets built and in what order (W11, `scrum/WORKING_AGREEMENTS.md:114-121`).
- Nothing enters without a design that needs it (W14, `:150-159`).
- Every item names a command that proves it (`scrum/README.md:95-96`).

So "learning" in spark can honestly mean this: **Claude proposes, you accept, and the rule lands with its test and
its mutation.** The proposal can come automatically from a finding. The acceptance cannot, and no rule builds
itself. **INFERRED**: this is my reading of the agreements.

## 5. Options, trade-offs and a recommendation

The trade-offs below are judgement, built on the facts above: **INFERRED** throughout.

| Option | What it means | Gains | Costs and risks | Fits W14? |
| --- | --- | --- | --- | --- |
| **A. Predefine a catalogue** | Write standard checks now for each bus and signal kind: SPI, I2S, UART, 1-Wire, analogue, levels | Broad coverage on paper, and an answer to "does it check SPI?" | <ul><li>Each check costs a rule's price (section 3), with no board to test it against: no SPI part exists anywhere.</li><li>Untested rules are where false passes come from.</li><li>The 09-29 cut removed exactly this kind of code.</li></ul> | No, unless you override W14 |
| **B. General rules over record facts** | A few rules, each written once and driven by facts and a bus table. Examples: a pull-up budget for any open-drain line, an input level against what drives it, every rail's sum | <ul><li>One rule covers I2C, 1-Wire and interrupt lines.</li><li>A new part's facts switch it on, with no code.</li><li>It grows the one part that already works.</li></ul> | <ul><li>Facts must use exact names.</li><li>Records must actually carry the facts: today only the L9110S states the pull-up fact `pull_conflicts` needs (`other-checks.md:113`).</li><li>Each rule is still code, as the boundary note wants.</li></ul> | Yes, when an incident pulls each rule |
| **C. A loop that proposes rules** | After each review, bench session or cold test, Claude sorts each lesson into four kinds and files an issue; you accept or reject. The kinds are: a missing fact, a fact under a new name, a new rule, a warning only a person can act on | <ul><li>It catches lessons that get lost today (R16 → P5).</li><li>It grows with every project.</li><li>It fits your process.</li></ul> | <ul><li>It needs a lasting record of findings and their outcomes, and that failed once (0 of 20 resolved).</li><li>A wrong acceptance becomes a confident false pass.</li></ul> | Yes: it is W14's loop, written down |
| **D. A mix** | C as the way lessons come in, B as what most lessons become, A only for basics that apply to every board, and every check saying what it did not examine | The good parts of each, in order | More to explain, and it needs discipline about order | Yes |

### Recommendation: D, in this order

1. **Make the existing checks honest first.** A check that passes silently is the worst outcome, and spark has one
   today.
2. **Build general rules, not bus-by-bus rules.** One table describes the buses, one list names the facts the rules
   read, and a few rules read both. Each piece lands with the first check that needs it, not as a separate rewrite.
3. **Let lessons arrive as proposals.** Claude files each lesson as a fact, a name, a rule or a warning, and you
   accept or reject it. Nothing builds itself.
4. **Predefine only what applies to every board.** SPI, I2S and UART signal checks wait for a design that uses them.

### The first three checks: most value for the least work

1. **Find a bus line one way (P122, #56).**
   - What: physics uses `compare_design`'s line finder (`scripts/compare_design.py:100-114`). It counts a resistor
     as a pull-up only if the resistor's other end is on a supply (`scripts/compare_design.py:144-150`).
   - Value: this ends the silent pass on every generated board, and the series resistor that hides a failing bus.
   - Cost: one function moved, one call changed, two tests and one mutation table (`physics-rules.md:329-333`).
     **INFERRED** estimate.
2. **Say what was not examined.**
   - What: physics names each bus line and analogue pin that no rule covered, as a note rather than a failure. The
     pattern already exists in `check_footprints` (`scripts/check_footprints.py:408-446`).
   - Value: the tool itself answers "does it check SPI?" on every run.
   - Cost: one function and one call (`physics-rules.md:345-350`). The risk is noise, which is why it should be a
     note. **INFERRED** estimate.
3. **A pull-up budget for open-drain lines, checked both ways, counting each module's own pull-ups.**
   - What: the first general rule over record facts. It reads `facts.i2c_pullup_ohms` and the board's own
     resistors. It checks the combined value two ways: against the rise time (the most it may be) and against
     spark's 1 kΩ floor (the least it may be).
   - Value: it would catch four VL6180X at 799 Ω. 1-Wire later joins as one row in its table.
   - Cost: medium. Records reach physics the way rail currents already do (`scripts/check_all.py:134-137`).
   - R16/P5 and P55 already pulled it, so it passes W14. **INFERRED**: the estimate, and that reading of W14.

Two small foundations belong with the first of these:

- an unknown severity becomes an error (one constant and one check, `physics-rules.md:351-352`);
- physics gets a list of its own rules (`physics-rules.md:323-328`).

### Where this goes

Your epic P136 (#70), "Full circuit checks: analogue and board checks", was opened today, and it is the home for
these questions.

- Its discovery "waits until P104 (#33) is finished", and #33 is now closed (`gh issue view 70`;
  `gh issue view 33`).
- It already links P122 (#56), P107 (#41) and P109 (#43).
- P133 (#67) gathers the cases where "could not look" reads as a pass.

Nothing here is decided. The order is yours (W11).
