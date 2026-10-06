# From a need to a pick: what spark can suggest today, and one engine for it

*For Petr, as input to the discoveries of P76 (#5) and P136 (#70). Written 2026-10-06. Nothing here is decided,
and nothing in spark or the bin was changed.*

**Your words, the starting point.** *"Really, the suggestion part is from a need to get a schema, a circuit, a module
we have, or an ESP32 with some code in it. That would basically be the same as when we just create a new project, but
Spark could also just do it for suggestions based on functionality. It could say, 'Well, here the robot should be able
to know what's in front of it, so I can either use our ultrasonic module or this type of light module,' and you could
pick, and so on. And not just from what we already have, but first think about it. Use the human or AI to think about
it, to suggest what would work to fill that need."* Earlier the same day you asked whether spark can say *"hey,
there's this problem, I suggest you add either this or make that ... then even calculate the components?"*, and you
said you would like it to *"suggest a circuit or part of it, including digital and modules that I have and their
combination or just analogue modules and parts"* (#70, comments of 2026-10-06 10:19 and 10:24).

**What this is built from.**

- Six reads, listed under Sources: three in this folder and three in `../remedies/`. Each was written read-only
  against spark at `8f7733d` and the bin at `8847eb8`.
- Both repositories are still at those commits. I re-read every spark and bin line this answer leans on.
- I added one calculation of my own, `reconcile_b25.py` (output in `reconcile_b25-output.txt`). I wrote it because
  the two workings of B25 disagree on one datasheet figure (§3.4).
- Your drawer, your orders and your store were not read.

**How to read the references.**

- `spark:` is `/Users/petr/Development/spark` at `8f7733d`, and `bin:` is `/Users/petr/Development/smartbin-local`
  at `8847eb8`.
- `#N` is a spark GitHub issue, read with `gh` on 2026-10-06. Comment times are GitHub's, in UTC (two hours behind
  Prague).
- The reads are cited by tag: **[today]**, **[methods]**, **[bin]**, **[b25]**, **[fixes]**, **[tools]** and
  **[mine]**. Their files are listed under Sources.
- Datasheets are cited by tag:
  - **[VL]**: ST VL6180X, DocID026171 Rev 7.
  - **[S3]**: Espressif ESP32-S3 Series Datasheet v2.2.
  - **[POL]**: Pololu carrier #2489 schematic, irs09a.
  - **[ON]**: onsemi BSS84/D.
  - **[MMBT]**: onsemi MMBT3906LT1/D Rev 15.
- Anything I worked out rather than read is marked **INFERRED**.

**Words used here.**

- **need**: one thing the gadget must do, written as spark's verb plus a few words, such as sense / distance
  (spark:commands/idea.md:15-20).
- **deciding condition**: a fact about the need that decides between answers, such as "keeps watching while the chip
  sleeps".
- **principle**: the physical way a need can be met: a sound echo, light time-of-flight, IR reflection, touch
  (capacitance), a switch.
- **form**: what it is built from: a **module**, a **circuit** of parts, **the ESP32 plus code** (its own hardware),
  or a **combination** of these.
- **kind of solution**: a principle in a form. Examples: "light time-of-flight, as a module", "IR reflection, as a
  circuit", "touch, as the ESP32 plus code".
- **option**: one concrete way to build a kind: a record, a circuit with values, or a board ability with what it
  still needs.
- **pick**: the option you choose for a need.
- **kinds library** (proposed): your catalogue of kinds per function. Not spark's `catalog` layer, which holds
  researched parts nobody chose (spark:GLOSSARY.md:177-182).
- **circuit pattern** (proposed): a small circuit with roles and a calculator, such as an LED and its resistor, or a
  transistor stage.

---

## 0. In one screen

1. **spark has the two ends of your chain, not the middle.**
   - **The start exists:** it writes a need as a function.
   - **The end exists:** it turns chosen modules into a wired, checked board.
   - **The middle is missing.** Nothing thinks up kinds of solution or lays them side by side. Nothing carries a pick
     that is not a module, such as a circuit or the ESP32 plus code, through to a board (§1).
2. **Your exact example fails today.** On a synthetic drawer that includes an ultrasonic module, the need "obstacle
   ahead" shows eight unrelated owned sensors. The ultrasonic module and the light rangefinder are hidden behind
   "… 3 more" (§1.2).
3. **The method for the middle is old and well tried.** State the function, list the physical principles, find parts
   for each, and pick against what you already have. Shops already group distance sensors by principle. No
   structured tool I read does the principle step from data for a sensing need. No benchmark measures choosing
   (§2).
4. **The bin already did this by hand, twice.** Two lessons:
   - **A condition decided more than the function did.** "Keeps watching while the chip sleeps" left one answer among
     the parts the bin researched.
   - **A calculation found a fault that matching cannot (B25)** (§3).
5. **B25 also shows why the arithmetic belongs in code that reads recorded facts.** Two careful workings of B25, from
   the same datasheets, disagree on one figure: the sensor's own pin current. With it counted:
   - the passive remedies computed, including the runner-up, fail on paper;
   - the recommended transistor stage needs other resistor values (§3.4).
6. **One engine serves a new project and a single need inside an existing one.** The steps are: need → kinds of
   solution → options → trade-offs and checks → your pick → parts, circuit and code.
   - **Kinds** come from you and the AI together, helped by a kinds library kept as data.
   - **Code** checks and calculates.
   - **You** pick (§4).
7. **Recommendation.** Build the middle in spark's usual order: conversation first, then data, then code, each piece
   only when a real design pulls it.
   - **Smallest first step:** a known-answer test with no code. Run the bin's wave-to-open need and your robot's
     "what's in front of it" through a written kinds step, and compare the result with the bin's own sensor table
     (§5).

---

## 1. How far spark is today

### 1.1 Your wish, as six things spark would have to do

The six come from the reading of your words recorded on P76 (#5, comment of 2026-10-06 10:28).

| # | What you asked for | Today | Evidence |
| --- | --- | --- | --- |
| 1 | **Function first:** a need names no part | **Built.** A need is one of 13 verbs plus a few words, and the rule is "No part numbers" | spark:commands/idea.md:15-20; spark:scripts/parts.py:59-61; spark:scripts/needs.py:1-27 |
| 2 | **Kinds before parts:** think broadly first | **Missing.** `/spark:idea` goes from needs straight to matching records. A record's function comes from its part kind, one kind per function. The board only "computes". A pin can be asked only for wake, adc or pwm | spark:commands/idea.md:32-47; spark:scripts/parts.py:63-78, :184 |
| 3 | **Not only what is owned** | **Partly.** The match lists records you do not own, but spark itself knows 7 parts and 2 boards. Research runs only for a gap, after your yes, and stops at the first vendor that fits | spark:scripts/needs.py:101-102, :126-164; [today] §1.3; spark:docs/2026-10-04-store-design.md:440-442; spark:agents/parts-researcher.md:35-36 |
| 4 | **Options side by side, then you pick** | **Thin.** Owned and free counts, and what each candidate still owes. "The owned option and the simpler one beside it … spark knows no prices". No trade-off columns | spark:commands/idea.md:38-47 |
| 5 | **The pick becomes concrete** | **Half.** Picks, reservations and the requirements file wait for P97 (Ready) and P76 (Idea). Once modules are named, the chain wires them and places the resistors their records ask for | spark:commands/idea.md:67-71; spark:scripts/parts.py:327-330 |
| 6 | **And code** | **Facts only, by decision.** spark writes the pin map, and the conversation writes behaviour | spark:docs/2026-10-01-firmware-and-tests.md:15-18, :86-100; spark:scrum/VISION.md:61 |

### 1.2 Your example on today's spark

Every run below used an empty store or synthetic entries, never yours ([today] §2; inputs and outputs in `runs/`).

- **The robot's "obstacle ahead", against a synthetic drawer of ten sensors, one of them an ultrasonic ranger.**
  - **What spark showed:** eight unrelated owned sensors in alphabetical order, then "… 3 more". The hidden three
    are the ultrasonic ranger, a water-level float and the VL6180X, so both fitting options are hidden. The JSON names
    none of them (`runs/match-robot-synthetic.txt`, `.json`).
  - **Why:** the list is ordered by owned, then by words, layer and id, and keeps the first 8
    (spark:scripts/needs.py:163-164; spark:scripts/parts.py:1724-1726, :1738).
- **The word search misses by function.**
  - **The result:** `parts.py --need` finds nothing for obstacle, distance, ultrasonic, infrared or proximity. "light"
    finds the VL6180X only because the letters sit inside "time-of-flight" (`runs/need-words.txt`).
  - **Why:** `--need` never reads a record's function (spark:scripts/parts.py:1202-1227). Research's reuse-first step
    uses it (spark:commands/research.md:17-24), so reuse-first misses a part the matcher finds. P39 (#10) holds this,
    and the story map's scenario 4.3 still reads "no" (spark:scrum/STORY_MAP.md:71).
- **Code on the ESP32 has no words.**
  - **Touch is refused:** a pin asked for touch gets "not something a pin can be asked for. Known: wake, adc, pwm"
    (`runs/touch-assign.txt`; spark:scripts/assign_pins.py:207-211). Yet the ESP32-S3 has 14 touch pins (Espressif,
    [hardware design guidelines, Touch Sensor](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html#touch-sensor)).
  - **A data path half exists:** a project copy of the FireBeetle record, given a `function` list with touch and
    tone, is offered first for those needs and validates (`runs/match-board-function-probe.txt`). Nothing writes
    that list: `--function-set` finds part records only (spark:scripts/parts.py:1645-1648).
- **A circuit of parts has no place.**
  - **The test:** the generator built a robot from library modules plus two bare signals for a discrete IR sensor.
  - **The result:** the modules and their records' resistors were placed. The IR signals came out "ASSIGNED, AND
    CONNECTED TO NOTHING" (`runs/robot-assign.txt`; spark:scripts/emit_board.py:737-746).

### 1.3 What spark calculates today

- **One component value:** an LED's series resistor, (I/O volts − forward volts) / current, rounded up to E12, with
  the arithmetic printed (spark:scripts/emit_board.py:595-618).
- **Seven limits, run backwards from a failing rule:** trace width, capacitor rating, resistor watts, the largest I²C
  pull-up, drill and pad ([fixes] §5).
  - An example: "use <= … ohm, or drop the bus to a slower mode — changing the bus speed is free, changing a
    resistor costs a board revision" (spark:scripts/check_physics.py:416-424).
  - Applied literally, three printed limits fail the very rule that printed them ([fixes] §1, item 3).
- **One fault calculated but not fixed:** a board's pull-down against a module's own pull-up
  (spark:scripts/parts.py:1284-1316).
- **Not computed at all:** a pull-up or pull-down value, a divider, or a pull network's level against the reading
  pin's thresholds ([fixes] §5).
- **B25 is invisible to spark.** On the bin, physics, rules-vs-netlist and buildability all exit 0 ([fixes] §1,
  item 6). Two of the facts it would need are missing or wrong in the records:
  - **The board states no input-high level.** It has `io_volts` only (spark:boards/firebeetle2-esp32s3.json:413-421).
  - **The VL6180X record's note on the 47 kΩ pull-up is wrong in three ways** (spark:parts/vl6180x-breakout.json:72-80; [bin] §4.9):
    - it names the resistor R6, which is R5 on [POL];
    - it says the line clears the S3's threshold, which holds only typically;
    - it has the "fighting" backwards: a host pull-up raises the level, and it is a pull-down that fights it.

### 1.4 What is missing, in short

From [today] §4, re-checked:

- **No kinds step.** Nothing thinks of kinds of solution before parts.
- **No words for a kind, or for what the board does by itself.** `CAPABILITIES` holds only wake, adc and pwm
  (spark:scripts/parts.py:184).
- **No trade-off columns.** Missing: fit to the condition, sleep current, the pins an option spends, the parts it
  adds, whether a driver exists, whether it can be simulated, and price.
- **Fitting candidates get hidden behind owned ones** (§1.2).
- **Little breadth.** spark knows 7 parts, and research finds one part, not a survey across kinds
  (spark:agents/part-finder.md:3).
- **No place for a pick that is a circuit or code.**
  - A pick points at a part or a drawer entry (spark:docs/2026-10-04-store-design.md:173-177).
  - The writer places only picks that have a record (:180-182).
- **No circuits beyond modules.**
  - A transistor is advice, not a part (spark:scripts/emit_board.py:609-611).
  - Records may ask the board for only four resistor kinds (spark:scripts/parts.py:327-330).
  - There are no capacitors (P38, #9).

---

## 2. The methods, tools and research that do this

**Shown** means I or the read's author could open the evidence: a measured result, published code or a run.
**Claimed** means a vendor's or author's statement with no evidence we could open.

### 2.1 The method: function, then principle, then means, then pick

| Method | What it adds | Evidence | What spark could reuse |
| --- | --- | --- | --- |
| **Pahl & Beitz**, *Engineering Design*, 3rd ed., Springer 2007, "Conceptual Design" pp. 159–225 | **Working principles** between a function and a part: list the physical ways first, then combine them into concepts | **Shown, as studies of people:** the method "does not predict designers' early focus on generating solutions" (Kannengiesser & Gero, *Design Science* 3, 2017). Practitioners skip and squeeze steps (Jensen & Andreasen, DESIGN 2010, p. 26) | The principle layer. Also the authors' own permission to stop early when an owned part plainly fits, said out loud to you ([methods] §2.1) |
| **A standard function vocabulary** (Hirtz et al., *RED* 13(2), 2002, [NIST](https://www.nist.gov/publications/functional-basis-engineering-design-reconciling-and-evolving-previous-efforts)) | Fixed function words give "repeatable and meaningful results" | **Claimed** in the abstract | **Already there:** spark's 13 verbs (spark:scripts/parts.py:59-61) |
| **Morphological box** (Zwicky 1969) **with cross-consistency assessment** (Ritchey, [GMA](https://www.swemorph.com/pdf/gma.pdf), 2002/2013) | Rows are needs, cells are options. Pairs are judged on logic and facts first: "not to allow normative judgments to initially influence" (p. 6) | **Claimed:** "more than 100 projects" (p. 1), with no accuracy figure | Judge **pairs** on facts (bus address, logic voltage, pins, rail) before value judgements. Six needs with four options make 4,096 combinations but only 240 pair judgements ([methods] §2.2) |
| **Function–means tree** (Andreasen 1980; via [Wikipedia](https://en.wikipedia.org/wiki/Function%E2%80%93means_tree)) | Each means brings its own sub-functions | A representation, not a test | **Already there as data:** a record's `host_requirements` and `host_parts` (spark:parts/vl6180x-breakout.json:106-110, :159-172). What spark lacks is the other means for the same function |
| **TRIZ effects and Function-Oriented Search** ([Oxford TRIZ](https://www.triz.co.uk/glossary); Litvin, [TRIZ Journal 2005](https://the-trizjournal.com/new-triz-based-tool-function-oriented-search-fos/)) | Answers "how to?" with physical effects. Generalise the function before searching | AutoTRIZ with an LLM is **shown only as case studies** ([arXiv 2403.13002](https://arxiv.org/abs/2403.13002)) | Generalise "what's in front" to "sense presence" to "sense distance". That is the step spark's word search lacks |
| **Pugh's controlled convergence** ([Cambridge IfM](https://www.ifm.eng.cam.ac.uk/research/dmg/tools-and-techniques/controlled-convergence/); Frey et al., *RED* 20(1):41–58, 2009) | Pick against a **datum** with +, S and − per criterion, and repeat | **Shown in computer models, not field trials:** a strong datum helps convergence, and the method beats a single criterion | **The datum is what you own:** "Owned first, the simpler option shown beside it" (spark:docs/2026-10-04-store-design.md:417-420). A part passed over keeps its reason (:101, :231) |

### 2.2 Tools that propose solutions

| Tool | It proposes from | Shown versus claimed | Licence | What spark could take |
| --- | --- | --- | --- | --- |
| **CELUS** | Functional blocks, each filled with "at least one matching CUBO", one recommended | **Shown:** one walkthrough. A humidity-and-temperature sensor block became a temperature-only part and "still met the system requirements"; the requirement was never written down. **Claimed:** "at least 75%" time saved | proprietary; free access | One function, several checked implementations, one recommended. **Lesson:** a swap is only as good as the written need ([methods] §3.1) |
| **Circuit Mind** | A block diagram with trade-off sliders, solved by "deterministic algorithms" | **Claimed:** ~90% auto-generated, 4 h 13 min against 60–80 h. The Los Alamos report it cites was not found ([methods] §3.2) | proprietary | Little: it weighs cost, and spark keeps no prices |
| **JITX** | Design as code. A divider solver walks real resistor series and checks the worst case with temperature drift | **Shown:** the solver's source (docs.jitx.com). **Claimed:** its agent skills' checklist "catches 3-5 missed details" | proprietary | Ideas only, not code: calculators that land on a real part at the worst case; one rejected alternative per pick; a planning gate for the agent ([methods] §3.3) |
| **Flux Copilot** | Plain language, then parts and wiring "with your approval" | **Claimed**, no accuracy figure. Its own docs say "Always verify" | proprietary | Change only after approval. spark already does this with dry runs |
| **atopile** | Equations in the design, a constraint solver, "automatic parametric picking" | **Shown:** open source | MIT | An open-source starting point for calculators |
| **TI WEBENCH** | A power specification, from which it designs several power stages | **Shown:** documented. It compares them on dissipation, parts cost and area, and simulates them | free web tool | The shape for one function: several calculated designs compared on measured axes |
| **kicad-happy** | Netlist findings with `recommendation` and `fix_params`. `what_if --fix` solves dividers and filters backwards, snaps to E12/E24/E96 and re-simulates | **Shown:** code read. Its level rule uses generic thresholds, and it would not have seen B25, whose pull-up sits inside the module ([tools] §3, §4.9) | MIT | Patch, recompute, compare, then re-check by simulation |
| **ADI Circuits from the Lab, Renesas Winning Combinations** | Curated reference circuits | **Vendor statements**, and ADI's variations "have not necessarily also been built and tested" ([methods] §3.7) | free | A combination that has run is worth more. That is spark's "proven by use" (spark:docs/2026-10-04-store-design.md:14) |
| **SparkFun, TME's DFRobot table, Seeed** | A need in words; sensors grouped **by principle** ([SparkFun](https://www.sparkfun.com/distance_sensing): LED, LIDAR, ultrasonic, VCSEL) | Shop numbers. Seeed opens with three questions | free | The principle grouping, and asking first |

No structured tool I read shows alternatives across physical principles for a sensing need. Flux's chat could, but
no demo was found ([methods] §0, item 4).

### 2.3 What research says about an AI proposing designs

- **Drawing a board from requirements, with the datasheets supplied:** the best model passed **8.15%** of 300 tasks
  (HWE-Bench, [arXiv 2603.18102](https://arxiv.org/abs/2603.18102)).
- **The same job with grounding** (library search, datasheets, execution checks), on 20 tasks that name the parts:
  **0.90** pass@1, and **0.72** on the hard tasks.
  - The authors' verdict: "not yet reliable enough to replace expert review" (pcbGPT,
    [arXiv 2606.01188](https://arxiv.org/abs/2606.01188)).
  - The two benchmarks differ in tasks and grading, so their numbers do not compare.
- **A library of verified sub-circuits plus simulation helps.** AnalogCoder designed 20 analogue circuits, and the Pro
  version 28 across 13 types ([arXiv 2405.14918](https://arxiv.org/abs/2405.14918),
  [arXiv 2508.02518](https://arxiv.org/abs/2508.02518)).
- **For concepts, AI ideas were rated more feasible and useful, but less novel**, than crowdsourced ones. Examples
  shown to the model steer what it proposes (Ma et al., ASME IDETC 2023, [arXiv 2306.01779](https://arxiv.org/abs/2306.01779)).
- **Turning a requirements document into a design graph,** a multi-agent system covered under 20% of the requirements
  (Massoudi & Fuge, [arXiv 2507.08619](https://arxiv.org/abs/2507.08619)).
- **What no benchmark measures: choosing the principle and the part.** Both board benchmarks supply the components
  ([methods] §4.2). spark would have to measure that step with its own known-answer cases (INFERRED, [methods] §4.4).

### 2.4 The pattern that holds, and where spark already stands

- **People or the AI widen, facts and checks narrow, and the person decides.** The person decides the value
  questions: cost, preference, and whether to use what is owned. This is Ritchey's rule (GMA p. 6), and spark's own:
  "spark gives facts, the conversation decides and writes through spark" (spark:docs/2026-10-04-store-design.md:29-30).
- **Trust comes from four things** ([methods] §4.4). spark has each of them already, at least as a direction:
  - **grounding in real part data:** facts that are `verified` with a source (spark:GLOSSARY.md:184-189);
  - **checks that run:** four outcomes, with no pass where a check could not look (spark:DECISIONS.md:18-22);
  - **reuse of what worked:** "proven by use" (spark:docs/2026-10-04-store-design.md:14);
  - **a human who decides:** the conversation decides.
- **The step where AI scores worst is already deterministic in spark.** spark draws the board from records through
  "parts → pin map → board file → build → simulation" (spark:skills/spark-design/SKILL.md:3). What the conversation
  would add is the choosing, which nobody has measured (INFERRED).

---

## 3. The bin as the worked example

> **An illustration, not a decided design and not a fix for B25.** Every number below comes from a script that can be
> re-run: `../remedies/b25_calc.py`, `./calc.py` and `./reconcile_b25.py`. The decisions are yours.

### 3.1 The bin already suggested function-first, by hand, twice

- **Wave to open.** `bin:parts/SENSOR_OPTIONS.md` was added on 2026-09-23 in `125e73a`.
  - It lists eight options across several principles and forms.
  - It compares them on interface, range, cost, MicroPython driver and verdict (bin:parts/SENSOR_OPTIONS.md:17-26).
  - It works under your constraint "as digital and plug-and-play as possible" (:3-5).
- **Know the lid has shut.** `bin:LID_CLOSE_DETECTION.md` was added on 2026-09-22 in `8088892`.
  - It found the three methods real bins use, from patents (:7-28).
  - It chose the rebuild's own method (:42-50).
- **The firmware keeps every open answer as a strategy chosen by a config string.** SENSOR_STRATEGY is "tof",
  "tof_interrupt", "ir" or "none", and CLOSE_DETECTOR is "timed", "limit" or "stall"
  (bin:firmware/micropython/config.py:27-30, :253-256).
- **spark had no part in either.** The bin's board "is hand-written and spark checks it — spark never generated it"
  (spark:scrum/VISION.md:39).

### 3.2 Need 1: know a hand is in front of the lid

**The need:** sense / hand-proximity.

**The deciding conditions:**

- 30–100 mm, looking out through the lid's window;
- it keeps watching while the ESP32 sleeps, and wakes it;
- MicroPython only.

Sources: bin:parts/SENSOR_OPTIONS.md:3-5; bin:firmware/micropython/config.py:21-23; [bin] §2.2.

| Kind of solution | Option | Owned | Watches while the S3 sleeps? What it costs | Pins | Firmware | Wokwi | Only the bench settles |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Light time-of-flight, **module** with an interrupt | VL6180X, self-ranging (shipped) | yes | **yes.** The sensor draws 105–355 µA at 2 Hz, up to 2.46 mA if every measurement runs to its time limit, and the carrier's R5 adds 59.6 µA ([bin] §2.4, from [VL] Table 14 p.36) | SDA, SCL, D12 | written | awake, yes; the wake, no (spark:boards/firebeetle2-esp32s3.json:285-286) | the wake (B16), the level (B25), the real current |
| Light time-of-flight, **module**, polled | VL6180X, polled | yes | **no:** awake costs 13.2–42.3 mA for the chip ([S3] Table 5-9 p.67) | SDA, SCL | written | yes | the window's crosstalk |
| Light time-of-flight, other **modules** | SEN0245 (VL53L0X), SEN0315 (gesture) | no | probably not, because a 4-pin Gravity cable has no interrupt wire (INFERRED in [bin], not checked) | SDA, SCL | new | no | thresholds that ignore the background |
| IR reflection, **circuit** | IR LED, 38 kHz receiver and a transistor | on the buy list (bin:SHOPPING.md:66-75) | **no:** the CPU pulses the LED (bin:firmware/micropython/smartbin/proximity.py:45, :205-232) | 2 | written and tested | no | range and sunlight. It fits the lid's existing holes (bin:parts/SENSOR_OPTIONS.md:12-13) |
| Touch (capacitance), **the ESP32 plus code** | S3 touch channel and a copper pad | the S3 is owned | **yes:** 18 µA typical in deep sleep at 1% duty ([S3] Table 5-10 p.68) | one touch pin, such as A1/GPIO5, which the I2S move freed (bin:firmware/micropython/config.py:72-73) | new; touch wake under MicroPython is not verified | no | the range through plastic, and wet hands. **The bin never listed this option** |
| No sensor | the OPEN button | yes | yes, through ext1 | none extra | written (proximity.py:235-244) | yes | nothing |

**Rejected, at three levels** ([methods] §5, F3):

- **The principle:** ultrasonic, because its "wide cone sees floor/wall/legs" (bin:parts/SENSOR_OPTIONS.md:26).
- **The module:** the SEN0239 "will not fit the lid" (:23), and the SEN0019 is "5V only" (:24).
- **The software:** driver maturity (:19-21).

**What was chosen, and why.**

- **The VL6180X:** owned, all-digital, in the right range class, and it has crosstalk and range-ignore features made
  for a window (bin:parts/SENSOR_OPTIONS.md:9-11, :19).
- **The IR set** became the mechanical fallback (:12-13).
- **Then self-ranging with an interrupt,** because "Deep sleep only works with "tof_interrupt""
  (bin:firmware/micropython/config.py:21-23).

**The lesson: the deciding column was not in the table.**

- **The timeline.** The table was committed at 10:29 on 2026-09-23 (`125e73a`). Deep sleep arrived at 10:50
  (`1809f1f`).
- **What changed.** From then on the deciding condition was "keeps watching while the chip sleeps". Among the parts
  the bin researched, only the VL6180X in interrupt mode meets it, apart from the button.
- **What was missed.** The S3's own touch sensing would meet it too, and was never listed ([bin] §0, §2.1).
- **What a kinds step would have done** (INFERRED). It would ask for that condition first, because the board need
  (on a battery, in deep sleep) is known before any sensor is chosen.

### 3.3 Need 2: know the lid has closed

**The deciding conditions:**

- end the wait the original board never ended (bin:LID_CLOSE_DETECTION.md:33-36);
- never burn the motor;
- the motor's current is not yet measured (card B15).

| Kind of solution | Option | Tells "shut" from "jammed"? | Pins | Firmware | Wokwi | On the v4 board |
| --- | --- | --- | --- | --- | --- | --- |
| **Code only** | timed (shipped) | no (bin:firmware/micropython/smartbin/close_detection.py:35-37) | none | written | yes | shipped |
| Motor current, **circuit plus code** | 0.1 Ω shunt, 1 kΩ + 1 µF into A0 (bin:board.tsx:168-178, :355-361) | yes | A0 | written | **no:** the sim chip reports direction, not current (bin:firmware/micropython/sim/chips/l9110s.chip.c:1-17) | copper present; needs B15's real current |
| A switch, **part plus code** | lever microswitch | yes, "no calibration" (close_detection.py:49-50) | its own pin | written | no | **no pin and no connector** |
| Optical flag, **module plus code** | slot sensor | yes | 1 | new | no | not researched (bin:LID_CLOSE_DETECTION.md:25-28) |
| Supply sag, **circuit plus code** | a divider to an ADC pin | partly (INFERRED) | 1 | new | no | the original board's suspected method (bin:TEST_PROTOCOL.md:65-70) |

**Chosen.**

- **Timed first:** "Simplest, no extra parts" (bin:LID_CLOSE_DETECTION.md:44-45).
- **Stall as the upgrade:** its copper is already on the board, so that "nothing IRREVERSIBLE now depends on the
  unmeasured number" (bin:board.tsx:166-167).

**A finding that looking at the whole bundle exposes.**

- **The firmware accepts it.** CLOSE_DETECTOR = "limit" passes validation (bin:firmware/micropython/config.py:255).
- **The copper does not serve it.** On v4, A0 sits on the shunt's 1 kΩ filter, so against the internal 45 kΩ pull-up
  it reads 72 mV (bin:board.tsx:357-361; [S3] Table 5-4 p.65).
- **What follows.** The lid reports "closed" at once, and the bin goes to sleep with its lid open ([bin] §3.5).
- **Nothing catches it.** The tests only construct the detector (bin:firmware/micropython/tests/test_assembly.py:111-116).
- **The rule this suggests:** a strategy belongs on the menu only together with the copper that serves it.

### 3.4 B25: a problem is a need too

**The need, function-first:** sense / hand-proximity, with one new deciding condition. A 2.8 V open-drain output must
wake a 3.3 V ESP32-S3 pin, and that pin must read it asleep and awake ([bin] §4.1).

**The fault.** Both notes agree on it.

- **The circuit:**
  - the carrier pulls the sensor's GPIO1 up with 47 kΩ to its own 2.8 V ([VL] Table 2 p.10; [POL]);
  - the bin adds 100 kΩ to ground (bin:board.tsx:273, :384-385).
- **The levels with a hand present:**
  - **awake:** 1.892 V;
  - **asleep:** 1.099 V, if the internal 45 kΩ pull-down survives sleep;
  - **needed:** V_IH = 0.75 × 3.3 = 2.475 V ([S3] Table 5-4 p.65; [b25] §1).
- **The ceiling.** No passive arrangement can lift the line above the sensor's own 2.8 V, so the best possible
  headroom is 0.325 V ([b25] §1).

**The kinds of remedy are a short standard list** ([b25] §7: "Producing the list is retrieval, not invention"):

- weaken the opposing pull;
- pull up to the reading pin's rail;
- use the line as ST drew it, active-low;
- add a transistor stage;
- use a translator chip.

**The options, with calculated values.** A margin is the worst case at the corners each note computed. "50 nA" means
only the S3's own pin current is counted, and "10 µA" means the sensor's is counted too.

| Remedy | Change | Guaranteed margin | Sleep cost on the line | Sensor unplugged | Rests on | From |
| --- | --- | --- | --- | --- | --- | --- |
| today | — | −583 mV awake, −1376 mV asleep (typical) | 59.6 µA | reads 0 | — | [b25] §1 |
| firmware only | no internal pull-down on GPIO12 | still −0.58 V | 59.6 µA | reads 0 | — | [b25] §3, option 0 |
| 1 MΩ instead of 100 kΩ, plus the firmware change | one value | +0.092 V at 3.3 V (50 nA). **−0.349 V with 10 µA** | 59.6 µA | reads 0 | the leakage bound | [b25] A1; [mine] |
| nothing on the line, or active-low read directly | remove the 100 kΩ | +0.222 V at 3.3 V (50 nA). **−0.247 V with 10 µA** | 59.6 µA; about 0 if active-low | floats | #17334 if active-low | [b25] A2, D, E; [mine]; [bin] §4.3 |
| 47 kΩ pull-up to 3V3, still active-high | the 100 kΩ to ground becomes 47 kΩ to 3V3 | **+221 mV (10 µA)** | 128 µA | **wakes at once** | no internal pull-down on GPIO12 | [bin] §4.4; [b25] B |
| active-low throughout, 47 kΩ to 3V3, OPEN button to ground (the wiring of 2026-09-24, `85cb86d`) | two resistors re-tied, the button re-wired, `WAKE_ON_HIGH = False` | **+221 mV idle, +242 mV with a hand (10 µA)** | about 0 (5.3 µA fed back into the carrier) | quiet | a low-level wake working on the S3: MicroPython #17334, tested on the bench (B16) | [bin] §4.5 |
| P-MOSFET translator, BSS84 with R_G 47 kΩ | one SOT-23 and one resistor | +122 mV off-margin against the 0.8 V minimum threshold at 25 °C; ≥ +750 mV high | about 0 | quiet | the fitted part's threshold window. The threshold drifts 3 mV/°C, typical ([ON] Rev 2 and Rev 5 p.2), so at 70 °C the minimum is about 0.665 V ([b25] §3 C′), under this circuit's 0.678 V worst gate voltage (INFERRED: a typical drift applied to a minimum) | [bin] §4.6 |
| **PNP stage**, MMBT3906, R_b 220 kΩ, R_be 150 kΩ (the B25 note's pick) | three parts; the firmware splits the sensor's polarity from the wake level | +0.55 V high, +0.82 V low (50 nA). **With 10 µA:** it still reads correctly within ±3% of 3.3 V, though at 3.4 V and 70 °C the idle D12 rises to 0.707 V (0.143 V under V_IL, over the note's own 0.10 V target). At the S3's 3.6 V maximum and 70 °C the transistor turns on, to an estimated 2.47–3.6 V: a false wake | 58.4 µA less than today (1.2 µA fed back) | quiet | three parts, a firmware split, an SOT-23 footprint | [b25] §3 C; [mine] |
| **the same stage, values re-chosen** by that note's own search with 10 µA added: R_b 150 kΩ, R_be 68 kΩ | as above | passes the note's criteria with the internal pull-down on or off: D12 off ≤ 0.072 V, forced β ≤ 15.5 in the cold | 1.88 µA fed back. The rail-creep bound is 0.159 V, against 0.101 V | quiet | as above | [mine] |

**Two workings of B25, one disagreement.**

- **Same day, same datasheets, different inputs.** The bin note counts the VL6180X's own pin current: up to 10 µA,
  listed for "CMOS digital I/O (SDA, SCL, GPIO0 and GPIO1)" ([VL] Table 24 p.47). The B25 note counts only the S3's
  50 nA (`../remedies/b25_calc.py:19`, `:221`).
- **The effect of counting it** ([mine]):
  - the B25 note's runner-up (1 MΩ) and its passive options turn from pass to fail on paper;
  - its transistor stage needs other values at the extreme corner.
- **Whether to count it is a judgement.** A datasheet's input-current bound may or may not describe a released
  open-drain pin, and real leakage is usually far smaller. The bin note says a passive fix "would probably pass on the
  bench, which is exactly why it needs saying" ([bin] §4.3).
- **This is the "which assumptions to design to" choice the B25 note leaves with you** ([b25] §7).

**What the numbers favour, as an illustration only.**

- **With the 10 µA counted, only the remedies in the table that put a 3.3 V source on the line keep a guaranteed
  margin.** The B25 note's other idea, lowering the carrier's own R5, was not re-run here; the note rejected it
  for its 280–596 µA all night ([b25] §3, option F).
- **If B16 shows a low-level wake works on the S3, the active-low wiring is the smallest change.** It adds no part and
  saves about 60 µA asleep ([bin] §4.8).
- **If a low-level wake must stay avoided, a transistor stage keeps the active-high wake.** Its values must be
  computed for the bound you choose.
- **Either way, one bench step is free and comes first.** With today's firmware, hold a hand at the sensor while the
  chip sleeps and measure D12. About 1.10 V means the internal pull-down survived sleep ([b25] §6, step 0).

**What a tool could do here.**

- **These parts are mechanical once the facts are recorded** ([b25] §7; [tools] §5):
  - the divider level against the reading pin's thresholds;
  - the sensor pin's limits;
  - the current fed back into the carrier;
  - the sleep current.
- **spark already checks the mirror image,** for the L9110S: a board pull-down against a module's pull-up
  (spark:scripts/parts.py:1284-1316).
- **What it lacks** (§1.3):
  - the host's input levels, as board facts;
  - the carrier pull's rail, as a typed fact;
  - the bin's pull-down, which lives in the netlist.
- **What stays with you:** the bound, the cost in parts, and whether to reopen the active-high decision of 2026-09-25.

### 3.5 What the bin teaches the engine

1. **A suggestion is a bundle.** It is the part or circuit, the copper that serves it, the firmware strategy, its
   calibration, and the check that proves it. Both faults found are bundles with a piece missing:
   - `limit` without its copper;
   - active-high without a level check.

   Source: [bin] §5, item 1.
2. **Conditions decide more than the function.** "Sense a hand" had ten answers, but "and wake a sleeping chip from a
   battery" had one among the parts the bin researched ([bin] §5, item 2).
3. **Every list needs all three forms:** a module, a circuit, and the ESP32 plus code. Touch and the ULP were never on
   the bin's list ([bin] §5, item 3).
4. **Fixed columns, including the one that decided the bin** ([bin] §5, item 4):
   - range and fit;
   - light;
   - whether it wakes the chip, and what it costs asleep;
   - money;
   - pins;
   - firmware effort;
   - what Wokwi can show;
   - what only the bench settles.
5. **Compute, don't only match.** Four of the bin's numbers would pass a fact-match and fail a calculation ([bin] §5,
   item 5):
   - the 2.33 V guaranteed level;
   - 72 mV on A0;
   - STALL_COUNTS at 0.58 A;
   - a sleep current anywhere from 0.1 to 2.5 mA.
6. **Keep every calculation's inputs as recorded facts with their sources,** so a second working can see what the
   first left out (from §3.4, INFERRED).

---

## 4. An architecture: one engine from a need to a pick

*A proposal for the discoveries, and **INFERRED as a design throughout**. It is built from the reads above and spark's
existing rules, and nothing in it is decided.*

### 4.1 The engine in six steps

```text
 1  NEED        a function + the conditions that decide it          (exists: /spark:idea, step S)
      │
      ▼  widen: you and the AI, helped by the kinds library (data)
 2  KINDS       2–5 kinds of solution = a principle in a form, each naming the facts that decide it
      │         and what it brings with it (a pad and a resistor; a CPU kept awake)
      ▼  concretise: owned first, then project, shelf, library, catalog; research only for a picked gap
 3  OPTIONS     a record · a circuit pattern with calculated values · the ESP32's own ability + what it needs
      │         · or a combination
      ▼  narrow: code checks and calculates; simulation where it applies
 4  TRADE-OFFS  fixed columns, filled from facts; "could not check" where a fact is missing, never a pass
      │
      ▼  you pick: the datum is what you own; every option passed over keeps its reason and the fact it rests on
 5  PICK
      │
      ▼  becomes concrete
 6  DESIGN      requirements file → pin map → board → checks → bench protocol; the conversation writes the code
                (a new project, or a change to an existing one)
```

| Step | Code decides | The agent proposes | You decide | Exists today |
| --- | --- | --- | --- | --- |
| 1 Need | the verbs and the fields (spark:scripts/needs.py:22-26) | at most three questions, each naming the need it could change (spark:commands/idea.md:21-22) | the deciding conditions | **built** |
| 2 Kinds | which kinds the library holds for this verb and these words | kinds beyond the library, labelled as its own and unverified until researched | add kinds, cross some out | **missing** |
| 3 Options | listing, owned first and nothing fitting hidden; the calculators that give a pattern its values | similarity ("[other words]", spark:commands/idea.md:41-42); research for a picked gap | your yes to research (spark:docs/2026-10-04-store-design.md:440-442) | **records only** |
| 4 Trade-offs and checks | pins (spark:scripts/assign_pins.py:18-32); pair facts (bus address, logic level); levels; the rail and sleep budget; re-running every check on the changed design | each trade-off in words; the firmware effort | money, effort, risk, which bounds to design to | **pins, and physics on a built board** |
| 5 Pick | recording the pick and each reason | — | the pick | **specified** (P97) |
| 6 Design | the requirements file, pins, the board, the checks | the firmware (P56) | approve the plan | **modules only** |

### 4.2 One engine, two ways in

| Step | A new project: your robot, "know what's in front of it" | One need inside an existing project: the bin's B25 |
| --- | --- | --- |
| 1 Need | sense / obstacle-ahead. Conditions: range, field of view, a moving base, power | sense / hand-proximity, plus "a 2.8 V open-drain line must wake a 3.3 V pin". The board and parts are fixed context |
| 2 Kinds | ultrasonic echo, light time-of-flight, IR reflection, a bump switch, a camera (grouped as SparkFun and TME group them, §2.2) | weaken the pull; pull up to 3V3; active-low; a transistor stage; a translator chip (§3.4) |
| 3 Options | owned modules first, then the library's VL6180X, then research. IR reflection as a circuit pattern. A bump switch as a part plus an input pin | each remedy as a circuit pattern, with values from the records' facts |
| 4 Trade-offs | range, cone, pins, current, driver. The wide cone that ruled ultrasonic out for the bin (bin:parts/SENSOR_OPTIONS.md:26) may suit a robot that must see any obstacle (INFERRED: the same fact, a different condition) | margins at the corners, sleep current, unplug behaviour, every check re-run on the changed board |
| 5 Pick | you, against what you own | you, against today's wiring |
| 6 Design | a new requirements file, then the board | a change to the existing board and firmware, proved on the bench (B16) |

- **spark already runs every way in on one spine** (spark:docs/2026-10-04-store-design.md:25-40). The ways in are:
  goal first, module first, a combination, the whole drawer, revive, swap, and extend. A kinds step between shaping
  (S) and matching (M) would serve them all (INFERRED).
- **A problem enters at step 1** as a need with one more condition, whether a check, a review or the bench found it.
  "Swap" and "extend" already start from a part's role or a project's free pins (:39-40).
- **A new project runs steps 1–4 once per need, then checks the pairs across needs:** bus addresses, logic levels,
  shared pins and the rail budget. That is Ritchey's cross-consistency, on spark's facts ([methods] §2.2).
- **Across all needs, step 2's output is the block diagram P76 asks for:** "the kind of module for each, and a block
  diagram with no part numbers" (spark:scrum/PRODUCT_BACKLOG.md:589-591). This answers your "a schema" (INFERRED).

### 4.3 What is deterministic, what is judgement, and who does which

- **Code decides facts and numbers.**
  - It owns the vocabulary, the listing and ordering, the pin assignment, every calculation and every check.
  - Checks have four outcomes, and none passes where it could not look (spark:DECISIONS.md:18-22).
- **The agent proposes.**
  - It asks the questions, adds kinds beyond the library, makes the similarity calls, proposes research for a picked
    gap, words the trade-offs, and writes the firmware.
  - Everything it writes goes through spark with a dry run first, as today (spark:commands/idea.md:23-30, :57-65).
- **You decide.** You set the deciding conditions, choose which kinds to explore, weigh money and effort, choose which
  bounds to design to (B25's 10 µA), make the pick, and decide whether to reopen a past decision.
- **What is new: arithmetic moves out of the conversation into calculators that read recorded facts.**
  - spark already says the conversation decides and spark gives the facts (spark:docs/2026-10-04-store-design.md:29-30).
  - B25 shows why the move matters. Two workings disagreed on one input, and only a calculator that names its inputs
    makes that visible and re-runnable (§3.4).
  - The tools read reached the same rule: "Keep the arithmetic in scripts. A reviewer can name a candidate topology,
    and a script computes and re-checks its values" ([tools] §6, item 6).
- **A computed remedy is shown only after the checks pass on the changed design.** That means its own check and its
  neighbours. Today three printed limits fail the rule that printed them ([fixes] §1, item 3).
- **The firmware boundary stays as decided.** For an "ESP32 plus code" option, spark supplies the ability, the pin
  and the checks, and the conversation writes the code (spark:docs/2026-10-01-firmware-and-tests.md:86-100).

### 4.4 Adding new kinds, patterns and abilities as data

Three new kinds of data, and what stays code:

1. **The kinds library: your catalogue of 2026-10-06.** *"It would be good if spark had a good catalogue like that,
   like a library maybe, projects could add from researching or so, it would also be autoupdatable"* (#5, comment of
   10:32).
   - **What an entry holds:** for one function (verb plus words), its kinds of solution. Each kind has its principle
     and form, the facts that decide it (the trade-off columns it fills), and what it brings. Two examples of what a
     kind brings:
     - Espressif recommends 470 Ω to 2 kΩ in series with each touch pad (the guideline page linked in §1.2).
     - An IR burst keeps the CPU awake (bin:firmware/micropython/smartbin/proximity.py:45, :205-232).

     An entry also lists example records and its sources.
   - **Where it lives:** in layers, nearest first, like records: project, shelf, library (shipped), catalog, shared
     (spark:docs/2026-10-04-store-design.md:191, :211).
     - **Your own entries win.** The nearer layer wins unless it is broken (:191).
     - **The shipped entries update with spark.** That is the "autoupdatable" part (INFERRED).
   - **How it grows:** by use. An entry is added when a project needs it, from a conversation or from research, with
     its sources (spark:docs/2026-10-04-store-design.md:15; W14, spark:scrum/WORKING_AGREEMENTS.md:150-156). Lessons
     arrive as proposals you accept, never from an automatic learner. The buses answer on #70 (comment of
     2026-10-06 10:37) reached the same rule.
   - **Seed it small:** only the entries the first test runs use, such as sense / distance and sense / presence.
2. **Circuit patterns.**
   - **What one holds:**
     - a small circuit described by its roles;
     - the calculator it uses and the facts it reads;
     - the checks it must pass;
     - its source, such as an app note or a datasheet.
   - **Examples:** an LED and its resistor; a divider into an ADC; a pull-up on an open-drain line; a transistor
     stage (B25); an IR LED driver (bin:SHOPPING.md:73-75); an RC filter (bin:board.tsx:169-178).
   - **Today:** the only computed pattern is the LED resistor, written in code (spark:scripts/emit_board.py:595-618).
     Records can ask for only four resistor kinds (spark:scripts/parts.py:327-330).
   - **A possible way to place one** (INFERRED): tscircuit's circuit format already has subcircuits
     (`is_subcircuit`, spark:tools/circuit-to-wokwi/node_modules/circuit-json/README.md:490), so a pattern could be
     placed as one group.
3. **Board abilities.**
   - **What the board does by itself:** touch, DAC, I2S, a PWM tone, the ULP.
   - **Where they would live:** in the board record's `function` list, which the matcher already reads (§1.2), plus
     pin ability words beyond wake, adc and pwm (spark:scripts/parts.py:184).

**What stays code.**

- **The verbs and the kind-to-function map** are code constants today (spark:scripts/parts.py:59-69).
- **Calculators and checks** are code, with tests and mutation tables, as every rule is.
- **A pattern names its calculator.** A new calculator is a code change, pulled by a design (INFERRED).

**How data arrives.**

- **The same way a record's function does today:** a dry run, then your yes (spark:commands/idea.md:57-65).
- **Every fact cites a source,** and `verified` keeps its meaning (spark:GLOSSARY.md:184-189).
- **Keep only what decides** (W21, spark:scrum/WORKING_AGREEMENTS.md:255-257). A kind's entry holds the facts that
  choose between kinds, not every number about every sensor.

### 4.5 How it connects

| Item | What it holds today | What this engine asks of it |
| --- | --- | --- |
| **`/spark:idea`** | S (needs), M (match), the marks, then stop (spark:commands/idea.md:13-71) | a kinds step between S and M, written as instructions first, with M run per kind |
| **P76** (#5, Idea) | the conversation from a vague idea to "the kind of module for each, and a block diagram with no part numbers" (spark:scrum/PRODUCT_BACKLOG.md:589-591). It also holds turning needs into a requirements file (spark:commands/idea.md:69-71), and your wishes of 2026-10-06 | steps 1–2 and the block diagram; the kinds library |
| **P97** (#18, Ready) | picks, reservations, owed facts, the requirements file and the cost line (spark:scrum/PRODUCT_BACKLOG.md:803-813) | three things: (1) a pick may be a circuit pattern or a board ability, where today it points at a part or a drawer entry (spark:docs/2026-10-04-store-design.md:173-177); (2) the writer places such picks, where today it places only picks with a record (:180-182); (3) each reason passed over names the fact it rests on |
| **P100** (#6, epic) | a new idea and an existing project, each walked through with you, discovery first. "The new idea comes from spark proposing from his drawer" (spark:scrum/PRODUCT_BACKLOG.md:815-835) | the engine that both journeys run. Its discovery should settle the order: think broadly first, then show what is owned first |
| **P136** (#70, epic) | calculating part values while designing (question 1), checks, and simulation (#70 body) | step 3's calculators and step 4's checks. The first could be a level check that generalises the pull-conflict test; it would catch B25 (#70, comment of 10:37, INFERRED there) |
| related | P39 (#10), the word search that ignores functions; P38 (#9), capacitors; P78 (#14), the LED part; P43 (#11), fixes reaching `check_all`; P94 (#17), the store and its formats | — |

---

## 5. Recommendation and the smallest first step

**Recommendation.** Treat your wish as **one engine with a missing middle**, and build the middle in the order spark
already uses for the store:

1. **conversation first;**
2. **then data:** the kinds library, board abilities and circuit patterns;
3. **then code:** listing, picks and calculators.

Pull each piece only when a real design is blocked without it (W14, spark:scrum/WORKING_AGREEMENTS.md:150-156).

- **Widen first.** Have the kinds step list the kinds before it looks at the drawer, then show the owned option first
  within each kind. What a model is shown first steers what it proposes (Ma et al. 2023), so showing the drawer first
  risks anchoring on what is owned (INFERRED, [methods] §7).
- **Keep every number in a calculator that reads recorded facts,** and let you choose the bounds it designs to.

**The smallest first step: a known-answer test, in conversation, with no code and no schema change.**

- **The setup.** Write the kinds step as a short instruction and run one conversation per need. The instruction asks
  for:
  - the deciding conditions;
  - 2–5 kinds, each a principle in a form;
  - the options for each kind, owned first;
  - the fixed columns from §3.5;
  - a datum, with a reason for each option passed over.
- **Test 1: the bin's wave-to-open need,** given only in words: a hand at 5–15 cm through the lid window, as digital as
  possible, MicroPython, on a battery, in deep sleep.
  - **It passes when:** the kinds in bin:parts/SENSOR_OPTIONS.md:17-26 appear; the sleep-and-wake column is filled;
    the S3's touch sensing is among the kinds; and the rejections follow from facts, not memory.
- **Test 2: your robot's "know what's in front of it".**
  - **It passes when:** at least ultrasonic, light time-of-flight, IR reflection and a bump switch appear, each with
    what it needs and what it spends.
- **The cost:** one conversation per need.
- **What it decides:**
  - whether the kinds step is worth building;
  - which columns and facts it lacks;
  - the first entries of the kinds library.

**Then, each only when a run pulls it:**

1. Write the kinds step into `/spark:idea`.
2. Let the agent see every same-verb candidate a kind needs. Today the cap of 8 hides fitting ones.
3. The kinds library as data, seeded with the entries the runs used.
4. Board abilities as data, touch first.
5. P97's pick accepting a circuit pattern or a board ability.
6. The first calculator and check: the open-drain level rule.
   - Prove it on B25's numbers, with the bound you choose written down. This is P136's question 1.
   - B16's bench gives it a real proof.

**Decisions only you can make.** None is decided here.

- **Price** in the trade-off columns. W21 and `/spark:idea` keep none (spark:scrum/WORKING_AGREEMENTS.md:255-257;
  spark:commands/idea.md:44-45).
- **The order:** "mostly from his drawer" (P100) or "not just from what we already have" (today). Widen first, then
  owned first, reconciles them (INFERRED).
- **Code for an "ESP32 plus code" option** stays the conversation's (P56). spark supplies the ability, the pin and the
  checks.
- **Analogue simulation** is not a v1 goal (spark:scrum/VISION.md:60), and P136 records that changing this is your
  call.
- **For B25:** which bounds to design to, starting with the sensor's 10 µA, and whether to reopen the active-high
  decision.

---

## Sources

**The reads this answer is built from:**

All six are under `/private/tmp/claude-501/-Users-petr-Development-smartbin-local/04754b5c-e6be-4924-97bc-e6cf796455f7/scratchpad/`.

- **[today]** `circuit-suggestion/spark-today.md`: spark against function-first suggestion, with runs in
  `circuit-suggestion/runs/`.
- **[methods]** `circuit-suggestion/methods-and-tools.md`: design methods, tools and research, shown versus
  claimed.
- **[bin]** `circuit-suggestion/the-bin-as-example.md`: the bin's two needs and B25, computed by
  `circuit-suggestion/calc.py` into `calc-output.txt`.
- **[b25]** `remedies/b25-worked-remedy.md`: B25 worked as an engineer would, computed by `remedies/b25_calc.py`
  into `b25_calc_output.txt`.
- **[fixes]** `remedies/spark-remedies-today.md`: what spark says to do when it finds a problem.
- **[tools]** `remedies/other-tools.md`: tools that find a fault, propose a remedy and calculate values.

`remedies/answer.md` did not exist when this was written, so it was not used.

**My own calculation:**

- **[mine]** `circuit-suggestion/reconcile_b25.py`, with its output in `reconcile_b25-output.txt`.
- **What it does:** it reuses `b25_calc.py`'s constants and transistor model unchanged. It adds only the VL6180X's
  10 µA as a current into the sensor pin ([VL] Table 24 p.47). It re-runs that note's own value search with that
  current added.
- **How it ran:** with `PYTHONDONTWRITEBYTECODE=1`. Nothing was written outside this folder.

**Re-read for this answer:**

- **spark at `8f7733d`:**
  - `commands/idea.md:1-71`
  - `scripts/parts.py:55-80, 180-188, 322-332, 432-440, 1284-1316, 1643-1670, 1720-1740`
  - `scripts/needs.py:1-30, 95-170`
  - `scripts/emit_board.py:584-618, 737-746`
  - `scripts/assign_pins.py:18-32, 205-212`
  - `scripts/check_physics.py:396-426`
  - `parts/vl6180x-breakout.json:70-82, 104-112, 158-174`
  - `boards/firebeetle2-esp32s3.json:278-290, 410-423`
  - `docs/2026-10-04-store-design.md:12-60, 99-103, 170-215, 228-243, 270-273, 415-445`
  - `docs/2026-10-01-firmware-and-tests.md:13-19, 84-101`
  - `scrum/VISION.md:7-40, 56-63`
  - `scrum/STORY_MAP.md:8-14, 32-37, 69-72`
  - `scrum/PRODUCT_BACKLOG.md:581-602, 783-848`
  - `scrum/WORKING_AGREEMENTS.md:148-160, 249-267`
  - `DECISIONS.md:11-23`
  - `GLOSSARY.md:175-190, 251-258`
  - `agents/part-finder.md:1-4`, `agents/parts-researcher.md:31-37`, `agents/design-reviewer.md:37-41`
  - `skills/spark-design/SKILL.md:3`, `skills/spark-design/references/verification-loop.md:26-30`
  - `tools/circuit-to-wokwi/node_modules/circuit-json/README.md:486-491`
- **GitHub, read only:** #70 (P136) with its comments; the last three comments on #5 (P76); the comments of
  2026-10-05 onwards on #6 (P100).
- **The bin at `8847eb8`:**
  - `parts/SENSOR_OPTIONS.md:1-30`
  - `LID_CLOSE_DETECTION.md:1-50`
  - `firmware/micropython/config.py:19-31, 72-73, 134, 253-256`
  - `firmware/micropython/smartbin/close_detection.py:35-37, 47-52`
  - `board.tsx:164-171, 178, 273, 355-361, 380-385`
  - `firmware/micropython/smartbin/proximity.py:38-46, 160, 203-212`
  - `TEST_PROTOCOL.md:65-70`
  - `SHOPPING.md:63-75`
  - commits `125e73a`, `1809f1f`, `22a0447`, `85cb86d`, `fd24455` and `8088892`, with their dates
- **Datasheets,** from the text copies already in this scratchpad:
  - [VL] Table 24 p.47 and §2.3 p.15 (`circuit-suggestion/src/vl6180x.txt`);
  - [ON] the threshold temperature coefficient, in both revisions read (`circuit-suggestion/src/bss84_onsemi.txt:77-80`,
    `remedies/txt/bss84.txt:90-92`).

**Outside sources** are cited inline with their URLs, books and papers. The full list, with the dates they were read,
is in [methods] Sources and [tools] §7.

**Not done:**

- Not read: your drawer, the store's drawer import, any order data, your store.
- No writes to spark or the bin, no GitHub writes, no installs, no wokwi-cli, no hardware.
