# Can spark say "here is the problem, add this or change that, and here are the parts"?

*For Petr, 2026-10-06.* This answers your question as recorded on P136
([comment](https://github.com/xmejkal/spark/issues/70#issuecomment-6014188640)), which B25 prompted
([bin #19](https://github.com/xmejkal/sisuo-brain-transplant/issues/19)):

> "in general, can spark do that? to say, hey, there's this problem, I suggest you add either this or make that which
> would ... then even calculate the components? is there some other tool that can do that?"

### How to read this

- **What was read.** Spark at `8f7733d` and the bin at `8847eb8`. Every `file:line` is at those commits. Nothing in
  either repo was changed.
- **Where the numbers come from.** Every number about spark or B25 comes from a run whose output I checked before
  writing: spark's own checks on the bin, a probe of spark's remedies, and the B25 calculator (see Sources). Part prices
  and the other tools' figures come from the two research reports, which give their links.
- **Labels.** **INFERRED** marks my own reading where no file or document says it. **ASSUMPTION** marks an input that
  no source gives.
- **The longer version.** Three reports sit beside this file: `spark-remedies-today.md`, `other-tools.md` and
  `b25-worked-remedy.md`.

## The short answer

1. **Spark can do part of this today, and none of it for B25's kind of fault.**
   - In a few places it already talks the way you describe. It names the problem, says why, offers two fixes, says
     which is cheaper, and gives a number.
   - But the numbers are limits ("at most 3541 Ω"), not parts to buy.
   - Nothing checks that a fix works, and a review drops the fixes before they reach you.
   - For B25 it says nothing at all.
2. **No other tool does the whole job for a fault like B25.** Each does a piece:
   - kicad-happy, an open-source KiCad plug-in, proposes fixes, calculates some values and re-simulates them;
   - JITX and atopile calculate values and verify them;
   - TI WEBENCH does every step, but only for power supplies;
   - the AI reviewers (AllSpice DRCY, Flux) suggest fixes in prose and publish no accuracy figures.

   INFERRED: none of them would have caught B25. The pull-up that causes it sits inside the sensor module, and only
   spark's part record knows it is there.
3. **B25 worked through, as an illustration, not a decided fix.**
   - The option I would pick adds one transistor and two resistors, about $0.025 in parts.
   - The wake line then sits at least 0.55 V above the S3's "high" level at every corner computed, and the bin sleeps on
     about 58 µA less.
   - With no new parts, the best option is 1 MΩ in place of the 100 kΩ, and it works by only 0.09 V.
4. **A correction to what I told you earlier.** I said the cheapest fix was likely "a stronger pull-up … or dropping the
   100k pull-down". Worked through, both turn out worse than I said:
   - the stronger pull-up is one of the worst options. It adds 33–300 µA all night, and an unplugged sensor cable
     makes the bin wake in a loop;
   - dropping the 100 kΩ leaves the pin floating whenever the cable is out.

   My first idea fixed one number and broke two others. That is the whole case for a re-check.
5. **How spark could do it.** A check finds the problem and records its cause. A catalogue lists the standard fixes
   for that kind of problem, and calculators size them. Every check then runs again on each candidate. An agent explains
   the options, you decide, and the bench proves the result. All of it is scripts except the explaining and your
   decision.
6. **My recommendation.** Build it inside P136, one kind of problem at a time, starting with B25's. The smallest first
   step is one slice, with B25 as its proof: check an open-drain line's level, and offer a fix with its values,
   re-checked.

---

## 1. What spark does today when it finds a problem

Spark has seventeen places that report a fault on the board rather than a missing input. That is the read's own count
(`spark-remedies-today.md` §3.8), and they are the first four rows below. The last three rows are context, outside
the seventeen.

| where | names it | says why | proposes a fix | offers alternatives | calculates | re-checks the fix |
|---|---|---|---|---|---|---|
| **physics check**, 6 kinds: trace too thin, supply too small, capacitor with no rating, capacitor under-rated, resistor too hot, I²C too slow (`scripts/check_physics.py`) | yes | yes | 6 of 6 | 4 of 6 | 4 give the limit a fix must reach; 1 gives only the watts | no |
| **rules-versus-design check**, 4 kinds: I²C line with no pull-up, pull-up outside 1–10 kΩ, input connected to nothing, input with no resistor (`scripts/compare_design.py`) | yes | yes | 3 of 4, plus 1 that points to a calculation it does not do | 2 of 4 | no | no |
| **buildability check**, 6 kinds: hole too small, copper ring too thin (2), via left at the tool's default, value too big for its package, connectors that cross-plug (`scripts/check_footprints.py`) | yes | yes | 6 of 6 | 2 of 6 | 3 give a limit; 1 partly | no |
| **part records' CONFLICT test** (`scripts/parts.py:1284-1316`) | yes | yes, with the arithmetic | **no** | no | the fault's numbers only | no |
| **board generator** (`scripts/emit_board.py`) | yes, e.g. an LED a 3.3 V pin cannot drive | yes | a different circuit, not designed: "drive it from a higher rail through a transistor" (`:609-611`) | no | **the LED resistor, rounded up to a standard E12 value (`:595-618`), the one real part value spark picks** | no. Asked for 60 mA it gives "27 ohm, about 51.9 mA" (my run, `led-and-i2c.verify.txt`), though the LED's record says 30 mA at most (`parts/led-red-5mm.json:71-72`) |
| **AI design reviewer** (`agents/design-reviewer.md:89-107`) | yes | partly: the consequence, in numbers | has no field for a fix, and never had one (`git log -S` over the file finds none) | no | no | no |
| **what a review shows you:** `check_all`, run by `/spark:review` (`skills/spark-review/SKILL.md:23`; `scripts/check_all.py:129, 139-141, 229-231`) | yes | yes | **drops every fix the checks wrote** (P43, #11) | no | no | no |

**Across the seventeen:**

- names the problem: 17;
- says why: 17;
- proposes a fix: 15, and 1 more partly;
- offers alternatives: 8;
- calculates: 7, and 3 more partly;
- re-checks the fix: 0.

### One real message

This is spark's own I²C rule (`scripts/check_physics.py:416-424`). The probe ran it on a small test board, because the
bin has no I²C fault. The lines below are verbatim from `probe-output.verify.txt:22-25`; the arrows are the probe's.

```text
   -> [problem] i2c-rise-time SDA: 10000 ohm against 100 pF rises in 847 ns, but 400 kHz allows 300 ns
      fix: use <= 3541 ohm, or drop the bus to a slower mode — changing the bus speed is free, changing a resistor costs a board revision
```

That is the closest spark comes to what you describe: the line, the cause in numbers, two fixes, which one is cheaper,
and the largest resistor that works. Then the probe follows the advice literally, fits 3541 Ω, and runs the same
rule again:

```text
   apply the fix literally: 3541 ohm
   -> [problem] i2c-rise-time SDA: 3541 ohm against 100 pF rises in 300 ns, but 400 kHz allows 300 ns
```

The exact limit is 3540.7 Ω (spark's own formula, my run: `led-and-i2c.verify.txt`). The message rounded it to the
wrong side, and nothing re-ran the rule on its own advice.

### What the table means

- **The words are there; the parts are not.** All seven fixes that calculate give a limit, such as "at least 0.18 mm"
  or "at most 3541 Ω", not a part to buy. The tables that turn a limit into a part already exist:
  - the standard resistor values (`emit_board.py:585`);
  - resistor power and largest capacitance for each package (`data/fabrication.json:38-48`).

  The checks use the package tables only to judge. The LED resistor is the one place that uses a table to choose a
  part (P78, commit `c233826`).
- **Nothing re-checks a fix.** Applied literally, three of the seven printed limits fail the rule that printed them
  (`probe-output.verify.txt`):
  - "at most 3541 Ω", shown above;
  - "use >= 6 V" for a capacitor that needs 6.3 V. The standard part that advice points you to is 6.3 V, and the rule
    has just rejected it; a 6 V part fails again, and the next standard rating, 10 V, passes (`:2-10`);
  - "at least 0.18 mm" for a trace that needs 0.1837 mm. Tried at 26 currents from 0.5 to 3.0 A, the printed width
    fails at 15 of them (`:12-13`).

  The roundings are tiny, but they land on the wrong side. Only the hole size rounds the safe way
  (`check_footprints.py:188`).
- **A fix can pass the rule and still make the part worse.** "Lower the resistance" passes the resistor-heat rule,
  yet a real LED resistor gets hotter: 0.090 W becomes 0.132 W. That is the probe's arithmetic for an LED on 5 V with a
  2.0 V drop (`probe-output.verify.txt:33-39`).
- **The fixes do not reach you.**
  - `check_all` keeps the problem line and drops the fix (P43, #11, in Idea).
  - The AI reviewer has nowhere to put a fix.
  - The review skill asks for "**one** next action. Not a plan" (`skills/spark-review/SKILL.md:59-61`).
- **B25 is invisible.**
  - On the bin, the physics, rules-versus-design and buildability checks all exit 0, and none mentions the wake line
    (my run today).
  - The 100 kΩ pull-down even satisfies the floating-input rule, because a resistor to any power or ground net counts
    as a defined level (`compare_design.py:188-189`).
  - The cause is already in spark: the sensor record states the carrier's 47 kΩ pull-up, verified
    (`parts/vl6180x-breakout.json:72-80`). But no code reads that fact. A search of spark's code finds its name only
    in the record itself.
  - The board file states no input-high level for the S3 (`boards/firebeetle2-esp32s3.json:413-422`).
- **The closest relative proposes nothing.** The CONFLICT test does B25's arithmetic in the opposite direction: a board
  pull-down against a module's own pull-up, judged at the module's input. For the L9110S it says (my run of
  `parts.py --show l9110s-module`):

  > "the board's 10000 ohm pull-down against the module's own 10000 ohm pull-up to its supply holds the pin at 0.5 of
  > the supply (1.25 V to 6 V over its 2.5-12 V range), so it idles HIGH, not low, on any supply above 5 V"

  It offers no fix, and the generator places those very pull-downs in the file that carries the warning
  (`emit_board.py:673-678`, `:945-947`).

---

## 2. Other tools that find a problem, suggest a fix and calculate it

"Shown" means documentation, published code or a paper shows it. "Claimed" means only marketing or the press says it.
The full survey, with every link, is `other-tools.md`.

| tool | what it does about a fault | shown | only claimed | licence, cost |
|---|---|---|---|---|
| **kicad-happy** (a KiCad plug-in for Claude Code) | **Finds** level mismatches from a generic table of 1.8, 2.5, 3.3 and 5 V parts, and finds pull-ups by pin name. **Proposes** a fix in words and as data, but without values: "Add a level shifter…", or a fixed 4.7 kΩ for I²C. Its what-if tool **calculates** dividers, filters, gain, crystal load and shunts, and snaps them to standard values with the error. It **re-checks** by simulating again in ngspice. | in its code at commit `0684046`: `validation_detectors.py:469-477, 646-665, 757, 772`; `what-if.md:216`. Its test over 5,857 projects measures crashes and regressions, not whether a finding is right (`VALIDATION.md`) | — | MIT, free |
| **JITX** | A divider solver walks precision resistor series and keeps a pair only if the output stays in range at both temperature extremes. Its AI agent rewrites the design's code. Its open-drain advice is a checklist in prose. | the solver's code, commit `6e0dd09`, `solver.py:37-129`. Its own note says the voltage it reports is not yet the worst case (`:116`) | built-in voltage and pull-up checks (that docs page now returns 404) | proprietary; free only for open-hardware designs |
| **atopile** | Values carry tolerances, and requirements are constraints. It picks parts, then "verif[ies] that candidate combinations satisfy all constraints". It does not look for faults nobody wrote down. | its code, commit `619eda7`, `solver/README.md:357-389` | — | MIT, free; needs Python 3.14 |
| **TI WEBENCH** (and ADI LTpowerCAD) | Designs a whole power supply from a specification. Values come from the datasheet equations, are recomputed at the corners, and simulated. Power supplies only. | WEBENCH's documentation; LTpowerCAD only through search excerpts | — | free, the vendor's own parts; no API found |
| **Cadence PSpice** | Optimizer finds the values that meet a goal. Smoke checks every part's stress against its safe limits. Monte Carlo varies the tolerances. It needs a simulation set-up and models. | the product datasheet | — | commercial |
| **AllSpice DRCY** | An AI reviewer for "mismatched voltage domains" and "missing pull-ups". | a paper describing its agents, with no accuracy figures (arXiv 2603.15672); one blog example suggesting a standard E96 value | what it detects | from $34,800 a year |
| **Flux** | An AI review with four named checks, one of them "Pull-Up/Pull-Down Resistors: Checks configuration correctness based on the IC's datasheet requirements", each giving pass, warning or error. | the list of checks; a described, not recorded, divider example | "sizing passives, I²C pull-ups, and decoupling caps" | commercial, metered; no API found |
| **Siemens Xpedition** | More than 150 "voltage-aware" rules, including "pin voltage mismatch" and missing pull-ups. It reports, and a person fixes. | — | the rules (press, and a white-paper summary) | commercial |
| **CELUS** | Refuses to connect two blocks whose supply levels differ. No calculated fix is documented. | its documentation | that it recommends parts by voltage level | commercial |
| **Circuit Mind, SnapMagic** | Generate level translators and passive parts. | — | all of it; SnapMagic's product pages return 404 | commercial |
| **KiCad ERC, Altium, SKiDL, tscircuit's checks** | Check pin types and connections, with no voltages and no fixes. | documentation and code | — | mixed |
| **lcapy, ngspice** (building blocks) | lcapy solves a circuit's voltages as formulas. ngspice simulates the circuit. | documentation | — | LGPL; BSD-3 |

**Would any of them have caught B25?** INFERRED, from what each tool reads:

- **The connection checkers** (KiCad, Altium, SKiDL, tscircuit) would not, because they carry no voltages.
- **kicad-happy** would not. Its level rule needs two chips with named supplies on the line, and its divider finder
  needs both resistors on the board.
- **Siemens** might, if its model library held the carrier's pull-up and the S3's input-high level.
- **The AI reviewers** would only if the carrier's schematic reached them.
- **Spark** holds the facts, but no rule reads them.

### What spark could reuse

- **Ideas, from any licence:**
  - from kicad-happy, "change a copy, recalculate, compare", with standard values and their error;
  - from atopile, "pick, then verify the combination against every constraint";
  - from JITX, "keep a value only if the worst case holds", and named failures such as "no pair fits" instead of a
    silent nothing;
  - from Cadence, the pairing of computing toward a goal and then checking every part's stress;
  - from Siemens, that voltage-aware rules need a library of pin levels. Spark's part records are that library, once
    the levels are numbers;
  - from the AI reviewers, one finding per root cause, and several runs that must agree.
- **Code whose licence suits an MIT plug-in:**
  - kicad-happy's formulas (MIT);
  - atopile (MIT, but it needs Python 3.14);
  - ngspice, called as a separate program (BSD-3), as a second opinion;
  - lcapy (LGPL), as an optional extra for circuits beyond a simple divider.

  Avoid PySpice (GPL-3.0, last released in 2021) and JITX's code (proprietary).
- **What nobody offers: accuracy data.** None of the commercial reviewers publishes any. kicad-happy publishes
  stability, not correctness. INFERRED: a spark rule tested against B25's real numbers, and then proven on the bench,
  would rest on more evidence than any of them shows.

---

## 3. B25 worked through: an illustration, not a decided fix

**The problem in plain words.** The sensor's interrupt wire is *open-drain*: the sensor can only pull it to 0 V or let
go of it (VL6180X datasheet DocID026171 Rev 7, Table 2, p. 10). In the active-high setting, letting go is how it
signals "a hand". The voltage on the wire then depends on two resistors:

- **the carrier's pull-up:** 47 kΩ plus 1 kΩ in series, to the carrier's own **2.8 V** (Pololu schematic irs09a, R5
  and R8);
- **the bin's pull-down:** **100 kΩ** to ground on the same wire (`board.tsx:273, 384-385`).

Together they make a divider. The wire reaches:

- **1.89 V** while the bin is awake;
- **1.10 V** while it sleeps, if the S3's internal 45 kΩ pull-down survives sleep. The firmware switches it on just
  before sleeping (`firmware/micropython/smartbin/board.py:88-89`).

The S3 only promises to read "high" above **2.475 V**, which is 0.75 × 3.3 V (ESP32-S3 datasheet v2.2, Table 5-4,
p. 65). So a wave may neither wake the bin nor open the lid.

**The ceiling.** No choice of resistors can lift the wire above the 2.8 V that feeds it. The best possible margin is
therefore 0.325 V, and less at the corners. A real margin needs something tied to 3.3 V: a pull-up or a transistor.

**The options.** These come from `b25_calc_output.txt`, which I re-ran today. Two terms in the table:

- **margin** is how far above 2.475 V the wire sits when a hand is there;
- **worst** is the sensor's supply at its 2.7 V minimum, with the carrier's resistors 5 % high, the bin's 1 % low, and
  the S3 pin's 50 nA leakage, on a 3.3 V rail.

| option | what changes | level with a hand (margin) | asleep, against today's 60 µA | sensor cable unplugged | new parts |
|---|---|---|---|---|---|
| today | — | 1.89 V awake (−0.58 V); 1.10 V asleep (−1.38 V) | — | reads 0 | — |
| 0 | firmware only: no internal pull-down on this pin | 1.89 V (−0.58 V): still fails | same | reads 0 | none |
| A1 | 1 MΩ instead of the 100 kΩ, plus 0 | 2.57 V worst (+0.09 V); fails if the 3.3 V rail runs above 3.42 V | same | reads 0 | a value change |
| A2 | remove the 100 kΩ, plus 0 | 2.70 V worst (+0.22 V) | same | the pin floats | one fewer |
| B | a pull-up to 3.3 V (100 kΩ) and no pull-down, plus 0 | 2.96 V nominal (+0.49 V) | **+33 µA** (with 10 kΩ, +300 µA) | **wake loop** | one |
| **C** | sensor set active-low, plus a one-transistor stage (MMBT3906 with 220 kΩ and 150 kΩ); the 100 kΩ moves to the S3's pin | **at least 2.95 V (+0.55 V) at every corner computed**; at most 0.032 V with no hand | **−58 µA** | reads 0 | three, about $0.025 |
| C′ | the same stage with a MOSFET (BSS84) | not guaranteed: it may switch itself on at a 3 % rail corner | −59 µA | reads 0 | two |
| D | everything active-low; the OPEN button moves to ground | 2.70 V worst for "no hand" (+0.22 V, or +0.15 V on a 3.4 V rail) | −60 µA | the pin floats | one fewer |
| E | the sensor gets its own wake source (ext0), active-low | as D | −59 µA | the pin floats | one fewer |
| F | change the resistor on the carrier to 10 kΩ or 4.7 kΩ | +0.05 or +0.17 V nominal | 280 or 596 µA, instead of 60 | — | rework of a bought module |

**What I would pick, as an illustration: C.**

- It is the only option whose margin does not depend on the rail's tolerance, the temperature, or whether the internal
  pull-down survives sleep.
- It lowers the sleep current, because the carrier's resistor stops drawing while the bin waits for a hand.
- It keeps every decision already made: active-high wake, the OPEN button as it is, and nothing near the low-level wake
  bug, MicroPython [#17334](https://github.com/micropython/micropython/issues/17334).
- An unplugged cable reads 0, so it cannot cause a wake loop.

**What C costs:**

- three parts (LCSC prices from a JLCPCB search on 2026-10-06);
- one firmware setting split in two: the sensor's polarity becomes active-low while the pin still wakes on high;
- updates to the test fake, the Wokwi chip and the wake-polarity check;
- a SOT-23 transistor. A SOT-23's pin order has bitten this board once already (`board.tsx:207-208`).

**The runner-up, with no new parts: A1.** It works on paper by 0.09 V, and fails above a 3.42 V rail.

**What the bench must settle first (B16).** Step 0 costs nothing. Hold a hand at the sensor while the chip sleeps and
measure the wake pin, D12:

- about 1.10 V means the internal pull-down survives sleep;
- about 1.89 V means it does not.

For option C, the bench must show three things:

- D12 reads at least 3.0 V with a hand;
- D12 reads at most 0.1 V without one;
- the carrier's supply stays at or under 2.9 V. That is the check on the 1.2 µA that C feeds back into it.

**ASSUMPTIONS behind these numbers.** None is in a source that was read:

- the FireBeetle's 3.3 V rail is within ±3 %;
- the carrier's resistors are within ±5 %;
- the S3's 0.75 × supply rule holds away from 3.3 V and 25 °C, the conditions it is stated for;
- the transistor's "off" leakage is extrapolated from a typical curve.

Nothing has touched hardware.

**How the work split.** This is the heart of your question:

| kind of work | B25's share |
|---|---|
| mechanical, once the facts are written down | the divider; the levels against the S3's thresholds; the sensor pin's absolute maximum; the current fed back into the carrier; the sleep current; and choosing the stage's two resistors, with 81 pairs tried against the corners |
| looking up a standard answer, not inventing one | the short standard list of fixes for "an open-drain line from a lower supply into a higher one": weaken the opposing pull, pull up to the receiver's supply, flip the polarity, add a stage, use a translator chip, change the module |
| judgement, which stays yours | whether 0.09 V is enough; whether three parts and the firmware changes are worth about 0.46 V more margin and 58 µA less; whether to reopen the 2026-09-25 active-high decision; which corners to design for |

---

## 4. How spark could do it

### The flow

```text
 facts           the part records, the board file, the netlist, the firmware's pull in each state
 a check         finds the problem, and records its kind, the node and the numbers that cause it
 the catalogue   lists the standard fixes for that kind of problem
 calculators     size each fix: a standard value, a package, the margin at every corner
 the re-check    applies each fix to a copy of the design and runs EVERY check again
                 ───── everything above is a script: the same answer every time ─────
 the agent       ranks the fixes that passed, explains each in words, says what each costs   (judgement, labelled)
 you             choose one, or ask for something else                                        (the decision)
 the bench       proves the chosen fix; for B25 that is card B16                              (a measurement)
```

### Each step: what exists and what is new

1. **Facts**: data, each with its source. Spark's records already carry cited facts. B25 needs four more:
   - the S3's input levels: high above 0.75 × its supply, low below 0.25 × (ESP32-S3 datasheet v2.2, Table 5-4,
     p. 65). Today the board file has neither (`boards/firebeetle2-esp32s3.json:413-422`);
   - a module's pull-up on an output, as a number with its supply and series resistor. Today the record has 47000,
     keeps the 2.8 V in prose, and names the wrong resistor, R6 instead of R5 (`parts/vl6180x-breakout.json:72-80`;
     the B25 card);
   - one name for "a module's own pull". Today there are two: `onboard_input_pullups_ohms`
     (`parts/l9110s-module.json:84`) and `carrier_pulls_up_the_interrupt`;
   - which internal pull the firmware switches on in each state.
2. **Problems as data, with their cause**: a script. Today a finding is a sentence, plus a sentence for the fix
   (`scripts/check_physics.py:81-91`). It would also carry:
   - its kind, for example "open-drain line too low";
   - the node;
   - the numbers behind it: 1.89 V against 2.475 V, from 48 kΩ to 2.8 V against 100 kΩ to ground.
3. **A catalogue of standard fixes for each kind of problem.** This is knowledge, written once with a source and
   reviewed like a part record. Each entry says:
   - what the fix adds or changes;
   - which calculator sizes it;
   - what the re-check must watch, for example "a pull-up on a line that idles low costs current all night", or "a
     pull-up makes an unplugged cable read 1".

   The kinds you named, each added only when a design needs it (W14):
   - **open-drain line, or a level mismatch:** weaken the opposing pull, pull up to the receiver's supply, flip the
     polarity, add a stage, use a translator, or change the module. This is B25.
   - **missing or wrong pull-up:** a value between the I²C specification's minimum and maximum (NXP UM10204 Rev. 7.0,
     §7.1 p. 50 and §7.2.4 p. 52), or a slower bus. Today spark prints only the maximum.
   - **an input pulled against a module's own pull-up:** a stronger pull-down within a current budget, or drive the
     input actively. This is the L9110S CONFLICT. The current budget is B26's question, since the module's input
     network is part of what drains the motor pack.
   - **divider into an ADC:** the ratio, how much the ADC loads the divider, and the standing current.
   - **LED current:** the series resistor, checked against the LED's maximum and the pin's drive. Spark already sizes
     it (`emit_board.py:595-618`); only the check against those limits is new.
   - **motor supply:** the supply's rating, the trace width and the bulk capacitor.

   INFERRED: these entries are small circuits, so they would also serve your other question, about spark suggesting a
   circuit ([P136 comment](https://github.com/xmejkal/spark/issues/70#issuecomment-6014250100); that read is still
   running).
4. **Calculators**: scripts. Each sizes a fix from the facts:
   - the value, rounded to a standard value on the safe side;
   - the package;
   - the margin at every corner: supply tolerance, temperature, part tolerance.

   Spark already computes seven limits (§1) and one real part value, the LED resistor. It also has the tables a
   calculator needs: standard values (`emit_board.py:585`) and package limits (`data/fabrication.json:38-48`).
5. **The re-check**: a script.
   - Apply each candidate to a copy of the design in memory.
   - Run every check again, not only the one that fired.
   - Add the sleep budget, and the other parts' limits, such as the sensor pin's 3.6 V absolute maximum (VL6180X
     Table 22, p. 46).
   - Show the fixes that pass. For the ones that fail, say what they broke. B25's option B is the example: it fixes the
     level and breaks both the sleep current and the unplugged cable.

   Nothing like this exists today. The nearest thing is the generator's power traces: they are sized at the check's
   own minimum × 1.15, so they pass by construction (`scripts/copper.py:60, 88-98`).

   **Simulation is needed only where arithmetic cannot answer**, such as a start-up surge or a motor starting. B25 is a
   steady divider, so arithmetic is enough. You put analogue simulation out of v1 (`scrum/VISION.md:60`), and P136 asks
   you whether that changes.
6. **The agent**: judgement, labelled as such.
   - It reads the problem and picks which catalogue entries apply. A fix outside the catalogue is marked "not in the
     catalogue".
   - It asks the calculators for the numbers, and writes the options in plain words, ranked, with reasons and costs.
     Every number it writes comes from a calculator or a cited fact.
   - It never edits the design, as the review skill already says (`skills/spark-review/SKILL.md:86`).
7. **You decide.** The decision and its reason go into the project's notes, in your words, as the review skill already
   asks (`SKILL.md:86-87`). Then the change is made, the full checks run on the real design, and the bench proves it.

### What is a script and what is judgement

| step | done by | the same answer every time? |
|---|---|---|
| facts | part records and board files, each with a cited source | yes: data |
| finding the problem | a check | yes |
| listing candidate fixes | the catalogue | yes. Writing the catalogue is judgement, done once and reviewed like a record |
| sizing each fix | the calculators | yes |
| re-checking each fix | every check, run again on a copy | yes |
| ranking and explaining | the agent | no: judgement, and labelled as such |
| choosing | you | — |
| proving | the bench | measured |

### How it fits your rule that you decide

- **W11** says agents "propose, ranked, with reasons and costs. Petr decides" (`scrum/WORKING_AGREEMENTS.md:114-118`).
  A list of fixes is exactly that kind of proposal, and spark never applies a fix by itself.
- **Spark already splits the work this way for firmware.** The vision says "spark exports facts and a harness; the
  conversation writes the firmware" (`scrum/VISION.md:61`). Here spark supplies the facts, the calculators and the
  re-check, the conversation proposes, and you choose.
- **The review skill's "one next action" can stay** (`SKILL.md:59-61`). The action becomes "choose between these two"
  or "measure step 0 first". Giving the AI reviewer a field for a fix would change its format, and that is your call.

### What you would see: a MOCK-UP, not spark output

No spark command prints this today. Its numbers come from the B25 calculator and from `b25_bound_output.txt`.

```text
[problem] open-drain-level  TOF_INT -> D12
    with a hand, the line sits at 1.89 V (1.10 V asleep if the internal pull-down holds);
    the ESP32-S3 reads high only above 2.475 V.
    cause: the carrier's 47k + 1k to its own 2.8 V, against TofIntPulldown 100k to GND.
    no resistor change lifts this line above 2.8 V (best margin 0.325 V).
  fixes that pass every check, at the worst corner computed:
    1. sensor active-low + PNP stage (MMBT3906, 220k base, 150k base-emitter), the 100k moved to D12:
       >= 2.95 V (+0.55 V); idle <= 0.032 V; 58 uA less asleep; 3 parts
    2. TofIntPulldown 100k -> 1M, and no internal pull-down on GPIO12:
       2.57 V (+0.09 V); no new parts. (The bound is 566k; 560k misses by 2 mV; 680k passes by 0.035 V.)
  rejected: a pull-up to 3V3. The level passes, but asleep it costs 33-300 uA more, and an unplugged cable wakes the bin in a loop.
  rejected: a 470k pull-down. It passes at nominal (+0.06 V) and fails at the worst corner (-0.04 V).
```

---

## 5. Recommendation and the smallest first step

**My recommendation: yes, build it, inside P136 rather than beside it.**

- **The question is already part of P136.** It is one of P136's discovery questions
  ([comment of 2026-10-06](https://github.com/xmejkal/spark/issues/70#issuecomment-6014188640)). P136's question 1 already
  names "choosing part values while designing (a pull-up, an LED resistor, a divider into an ADC, the motor's supply)"
  ([#70](https://github.com/xmejkal/spark/issues/70)). Fixing a found fault is the same job, with the target set by a
  check.
- **Build it the spark way.** Scripts give the numbers, the agent gives the words, you give the decision, and the bench
  gives the proof.
- **Add one kind of problem at a time**, each pulled by a real design (W14, `scrum/WORKING_AGREEMENTS.md:150-159`).
  Start with B25's.
- **Borrow the ideas in §2 rather than adopting a tool.** None of those tools sees B25's cause.
- **Keep simulation for where arithmetic runs out.** That is P136's question, and your call.

**The smallest first step.** This is my proposal: the team refines it (W18, `WORKING_AGREEMENTS.md:236-242`) and you
order it (W11). It is one slice under P136, *needed by* the bin's B25:

> **An open-drain line's level is checked against the pin that reads it, and a fix is offered with its values,
> re-checked at the corners.**

- **What it adds.**
  - Two facts: the S3's input levels in the board file, and the carrier's pull-up as a number with its supply and its
    series resistor, corrected to R5.
  - One rule, one calculator, and the re-check of that rule's own candidates.
- **It extends work already recommended rather than repeating it.** The buses answer proposes, as spark's first general
  rule, "a pull-up budget for any open-drain line, counting the modules' own pull-ups, with both bounds". It adds that,
  "extended to compute the line's high level, it would also catch the bin's B25 (INFERRED)"
  ([P136 comment of 2026-10-06](https://github.com/xmejkal/spark/issues/70#issuecomment-6014466635), point 3). This
  slice is that extension, plus the fix.
- **Its proof is a command whose output you can read**, run on the bin at `8847eb8`. It must:
  - report 1.89 V against 2.475 V;
  - print the bound a pull-down must reach: at least 566 kΩ at the worst corner, against 368 kΩ at nominal;
  - round that bound to the safe side, offering 680 kΩ (+0.035 V) and not 560 kΩ, the nearest standard value, which
    misses by 2 mV;
  - reject 470 kΩ, which passes at nominal (+0.06 V) and fails at the worst corner (−0.04 V);
  - accept 1 MΩ (+0.09 V);
  - say that every passive value needs the firmware to leave the internal pull-down off on this pin. With it on, even
    1 MΩ gives only 1.32 V;
  - say that no resistor change can give more than 0.325 V.

  Every one of these numbers is already computed, in `b25_calc_output.txt` and `b25_bound_output.txt`, so the test
  knows its answers before the code exists.
- **Size.** INFERRED: one sitting. The transistor stage (option C) comes later, because it needs a transistor model in
  the calculator, which is a bigger step (INFERRED).

**What it must not duplicate.** These cards are all in Idea. They make spark's existing output reach you and tell the
truth; the slice makes a fix right, and adds B25's kind of fault.

- P43 (#11): the fixes survive `check_all` and `--json`.
- P118 (#52): `check_all` says what clears each `!` line.
- P109 (#43) and P124 (#58): the CONFLICT reaches `check_all` and `--json`.
- P122 (#56) and P141 (#75): the I²C checks are honest, and physics says what it did not examine.

**A small bug to file alongside, not yet filed.** Three printed limits fail the rule that printed them: 6 V, 0.18 mm
and 3541 Ω.

- The fix: round toward the safe side, as the hole check already does (`check_footprints.py:188`), and test each rule
  on its own printed value.
- It belongs under P133, "the checks tell the truth", like P141–P145.

**For the bin itself.** B25's fix is your choice on the bin's board, and it does not need to wait for spark. §3 is an
input to that choice. Step 0 on the bench is free once there is hardware to measure (B16).

**This answer starts no work.** Other reads for the same discovery are still running, such as the one on suggesting a
circuit ([P136 comment](https://github.com/xmejkal/spark/issues/70#issuecomment-6014250100)), and W18 says started
things finish first.

---

## Sources

**Runs, all read-only, done today before writing:**

- **Spark's three checks on the bin.** Physics, rules-versus-design and buildability, on the bin's
  `dist/board/circuit.json` with `.spark/rules.json`, with an empty `SPARK_HOME`. All three exited 0, and none
  mentions the wake line.
- **The remedy probe.** `probe_remedies.py`, with an empty `SPARK_HOME`. Its output is `probe-output.verify.txt`,
  identical to `probe-output.txt`.
- **The B25 calculator.** `b25_calc.py`, run with every section the worked example uses. Its output was identical to
  `b25_calc_output.txt`.
- **The worst-corner bound.** `b25_bound.py`, which uses `b25_calc.py`'s own model. Its output is
  `b25_bound_output.txt`; its 470 kΩ and 1 MΩ figures match the calculator's.
- **The L9110S record.** `parts.py --show l9110s-module`, with an empty `SPARK_HOME`. Its output is
  `show-l9110s.verify.txt`.
- **The LED resistor and the I²C limit.** Spark's own `series_ohms` and I²C constant, called on the real LED and
  board records, with an empty `SPARK_HOME`. Its output is `led-and-i2c.verify.txt`.
- **Repo state.** `git status` was clean in spark before and after. The bin shows only the `.vscode/` folder that was
  already there.

**Spark** (`8f7733d`) **and the bin** (`8847eb8`): cited inline.

**Cards, read-only:**

- P136, [#70](https://github.com/xmejkal/spark/issues/70), and its comments
  [6014188640](https://github.com/xmejkal/spark/issues/70#issuecomment-6014188640),
  [6014250100](https://github.com/xmejkal/spark/issues/70#issuecomment-6014250100) and
  [6014466635](https://github.com/xmejkal/spark/issues/70#issuecomment-6014466635);
- P43 (#11), P78 (#14), P109 (#43), P118 (#52), P122 (#56), P124 (#58), P133 (#67), P141 (#75);
- B25, [bin #19](https://github.com/xmejkal/sisuo-brain-transplant/issues/19).

**Datasheets and documents:**

- **ESP32-S3 Series Datasheet v2.2**, Table 5-4, p. 65: input levels and internal pulls. In the person's spark store.
- **ST VL6180X, DocID026171 Rev 7**: Table 2, p. 10 (open-drain, 47 kΩ); Table 22, p. 46 (absolute maximum 3.6 V);
  Table 23, p. 46 (supply 2.7–2.9 V). In the store.
- **Pololu VL6180X carrier #2489, schematic irs09a**:
  <https://www.pololu.com/file/0J960/vl6180x-time-of-flight-distance-sensor-carrier-schematic.pdf>
- **onsemi MMBT3906LT1/D Rev. 15**: <https://www.onsemi.com/pdf/datasheet/mmbt3906lt1-d.pdf>
- **onsemi BSS84/D Rev. 5**: <https://www.onsemi.com/pdf/datasheet/bss84-d.pdf>
- **NXP UM10204 Rev. 7.0**, §7.1, p. 50, and §7.2.4, p. 52: <https://www.nxp.com/docs/en/user-guide/UM10204.pdf>
- **MicroPython issue #17334**: <https://github.com/micropython/micropython/issues/17334>
- **LCSC prices**, from a JLCPCB parts search on 2026-10-06: C53444, C22961, C22807, C22935 (recorded in
  `b25-worked-remedy.md`).

**Tools**, each read on 2026-10-06; the detail is in `other-tools.md`:

- **kicad-happy**: <https://github.com/aklofas/kicad-happy> (commit `0684046`)
- **JITX**:
  - divider solver: <https://github.com/JITx-Inc/voltage-divider> (commit `6e0dd09`);
  - pricing: <https://www.jitx.com/pricing>;
  - the page that now returns 404: <https://docs.jitx.com/tutorials/quickstart-check-a-design.html>
- **atopile**: <https://github.com/atopile/atopile> (commit `619eda7`)
- **TI WEBENCH**: <https://webench.ti.com/help/PowerDesigner/Overview.htm> and
  <https://webench.ti.com/help/PowerDesigner/OpVals/OpVals.htm>
- **ADI LTpowerCAD** (search excerpts only):
  <https://www.analog.com/en/resources/technical-articles/designing-power-supply-parameters-in-five-simple-steps-with-the-ltpowercad-design-tool.html>
- **Cadence PSpice**: <https://www.ema-eda.com/wp-content/uploads/2024/04/orcad-pspice-designer-plus.pdf>
- **AllSpice DRCY**:
  - the paper: <https://arxiv.org/abs/2603.15672>;
  - the blog: <https://www.allspice.io/post/using-ai-in-schematic-design-reviews-what-we-learned-and-what-surprised-us>;
  - pricing: <https://www.allspice.io/plans>
- **Flux**:
  - the review checks: <https://docs.flux.ai/tutorials/ai-design-reviews>;
  - the claims: <https://www.flux.ai/docs/copilot/overview>;
  - the divider example: <https://www.flux.ai/p/tools/voltage-divider-calculator>
- **Siemens**:
  - <https://www.techdesignforums.com/?p=8669>;
  - <https://resources.sw.siemens.com/en-US/white-paper-eliminate-schematic-design-errors-with-automated-analysis-of-any-pcb-design>
- **CELUS**: <https://www.celus.io/knowledge/interfaces-ports-specs-and-connection-validation>
- **Circuit Mind**: <https://www.electromaker.io/blog/article/circuit-mind-turns-block-diagrams-into-schematics-fast>
- **SnapMagic**:
  <https://techcrunch.com/2023/10/10/snapeda-becomes-snapmagic-and-debuts-an-ai-copilot-to-help-automate-circuit-board-design>
- **KiCad 9 ERC**: <https://docs.kicad.org/9.0/en/eeschema/eeschema.html>
- **Altium**: <https://www.altium.com/documentation/altium-designer/design-validation>
- **SKiDL**: <https://github.com/devbisme/skidl>
- **lcapy**: <https://lcapy.readthedocs.io/en/latest/overview.html>
- **PySpice**: <https://pypi.org/project/PySpice/>
- **ngspice**: <https://en.wikipedia.org/wiki/Ngspice> (a secondary source)
