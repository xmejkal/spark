# Verification of answer.md: every claim about spark checked against its files and history

Checked against spark `8f7733d` (main). `git status --porcelain` in spark was empty before and after every run; the
bin's tree held only its pre-existing `?? .vscode/`. Nothing in spark was edited. The probes and repros were run
read-only (`PYTHONDONTWRITEBYTECODE=1`), from copies in `verify/` in this folder:

- `verify/recount_buses.py`: an independent recount of distinct bus parts across every layer.
- `verify/count_facts.py`: fact entries and distinct facts.
- `verify/uart_crossing.py`: an in-memory UART entry.
- `verify/i2s_floating.py`: init's `must_not_float` for the MAX98357A.
- `verify/motor_rail.py`: the data-driven motor-rail demonstration, re-run.
- `verify/severity.py`: a misspelled severity.
- `verify/bin_physics.py`: the bin through physics, run directly and via `check_all`.
- `verify/repro_rerun.py`: the folder's `repro.py`. Its output is byte-identical to `repro-output.txt`.

The folder's `probe_bus_line_forms.py` and `probe_rail_predicates.py` were also re-run.

How to read a verdict:

- **CONFIRMED**: the cited lines or commit show the claim.
- **PARTLY TRUE**: the core holds, but a stated detail or the citation does not.
- **REFUTED**: the code or the history says otherwise.

"l." is a line in `answer.md`. Paths are in spark unless marked `smartbin:` or `irrigation:`.

## Summary

116 claims were checked, counted from the tables below:

- 2 REFUTED: the UART "crossing cannot be described" claim (#36) and "every rule in §1 came through these steps" (#99).
- 16 PARTLY TRUE.
- 98 CONFIRMED.

All counts, commit dates, numstat figures, quotes and issue links hold. The most consequential correction is in
claims #6, #32 and #58: a check *does* look at I2S wiring on a generated board, and it raises a false alarm rather
than staying silent.

## Header, words, short answers

| # | Claim | Verdict | What the source shows |
| --- | --- | --- | --- |
| 1 | l.5: spark at `8f7733d`, main, clean tree | CONFIRMED | `git rev-parse --short HEAD` = 8f7733d on `main`; `git status --porcelain` empty. Spark's `__pycache__` files date from 10:43 today, before this folder's first file (11:45), and are git-ignored (`.gitignore:2`) |
| 2 | l.14-15: `check_all` runs five checks: vendor-truth, buildability, the-order, physics, rules-vs-netlist | CONFIRMED | `scripts/check_all.py:279-290` |
| 3 | l.25-26: on 2026-09-24 an audit found the bin had no I2C pull-ups although its design rules required them | CONFIRMED | smartbin `022156f` (2026-09-24 09:46): "The I2C pull-ups were never fitted. DESIGN_RULES.md line 43 is an explicit checklist item … The board carried six resistors and not one was a pull-up." |
| 4 | l.26-28: physics was created the same day, and one of its first four rules was I2C (the wrong formula) | CONFIRMED | `dae10dd` (2026-09-24 14:41) adds `scripts/check_physics.py` with four rule functions: `check_trace_currents`, `check_capacitor_voltages`, `check_resistor_power`, `check_i2c_rise_time` (`git show dae10dd:scripts/check_physics.py` :170, :220, :251, :280). The docstring `:9-18` lists the wrong rise-time constant |
| 5 | l.28-29: spark adds a rule only after a real design needed it | CONFIRMED | W14 `scrum/WORKING_AGREEMENTS.md:150-159` (from 2026-09-29). The earlier rules also came from the bin's defects (#3, #4) |
| 6 | l.30-31: "spark places SPI and I2S pins sensibly, but no check looks at how they are wired" | **PARTLY TRUE** | No rule examines them *as a bus*. But `init` seeds every `direction: "in"` pin into `must_not_float` (`init_project.py:80-100`, `:173`), and nothing filters bus lines out. For the MAX98357A that is BCLK, DIN, LRC and SD (`verify/i2s_floating.py`). The floating-input rule (`compare_design.py:177-212`, run by `check_all`'s rules-vs-netlist) then examines them. On the generator's pin-to-pin wiring it reports `Max98357aDfr0954.BCLK: joined to Mcu.pin5 and no resistor to a rail`, a false alarm on a push-pull line. The same would happen to an SPI device's input pins |
| 7 | l.31: UART cannot be declared as a bus | CONFIRMED | `parts.py:257-262` (only i2c, spi, i2s); `parts.py:538-541` refuses any other bus |
| 8 | l.31-33: physics gave a test board with SPI, UART, I2S, 1-Wire and analogue nets `status: ok`, exit 0 | CONFIRMED | Re-run byte-identical. `repro-output.txt:55` (case 10c) gives exit 0, status ok, after the rail, Rdq's current and its footprint were stated. Without those it is exit 2 (`:51`), for reasons unrelated to the buses |
| 9 | l.34-36: each rule's description names the defect it came from | CONFIRMED | `compare_design.py:10-14`; `check_physics.py:9-18` |
| 10 | l.39: a whole new check plugs in cleanly, and tests guard it | CONFIRMED | see #64-#65 |
| 11 | l.41-42 and l.216-218: I2C knowledge is spread over **five** files that disagree once, so one rule silently skips generated boards | **PARTLY TRUE** | The disagreement and the silent skip hold (#50-#52). But there are six scripts, not five: `boards.py` also holds I2C knowledge, the closed `i2c` pin role (`boards.py:102`, read by `assign_pins` as a penalty, `:77`) and the refused `i2c_freq`/`i2c_freq_hz` board keys (`boards.py:77-78`). The answer's own source table lists `boards.PIN_ROLES` and the board's `pin_roles` as bus-knowledge places (`other-checks.md:140`) |

## §1 Why I2C

| # | Claim | Verdict | What the source shows |
| --- | --- | --- | --- |
| 12 | l.58: `i2c-pullups`, each line pulled up to a supply at 1-10 kΩ; born 2026-09-24 in the file's first commit; "six resistors and not one was a pull-up" | CONFIRMED | `git log --follow --diff-filter=A` for `compare_design.py` gives only `55d2368` (2026-09-24 12:00), which already has `check_i2c_pullups` and `PULLUP_MIN_OHM = 1000` / `PULLUP_MAX_OHM = 10000`. Quote at `compare_design.py:10-14`; smartbin `022156f` |
| 13 | l.59: `i2c-rise-time`, born with physics; the wrong formula overstates by 42 % and "turned a pull-up that was fine into one that looked twice over spec" | CONFIRMED | `tests/test_check_physics.py:10-13`; `check_physics.py:62-66`; `dae10dd` |
| 14 | l.60: P55 (2026-10-01): a record says where its pull-ups come from; V1.2+ has none; the fact was read by no script and flipping it left the suite green | CONFIRMED | `c0e3d76` (2026-10-01): "flipping a shipped record's module_has_i2c_pullups passed a green suite … no script reads that fact at all … FireBeetle V1.2+, which has no I2C pull-ups anywhere"; `parts.py:384-409` |
| 15 | l.61: 2026-09-29, every device on a bus line shares it; `RANGEFINDER_SDA` left the bus (audit B2, B3) | CONFIRMED | `assign_pins.py:174-176`; `7381fed` (2026-09-29): "Backlog P21, from sprint-4 audit claims B2, B3 and B18" |
| 16 | l.65-66: R20, a reference taught 4.7 kΩ, "which the physics rule rejects at 400 kHz"; fixed in `f35e7df` | **PARTLY TRUE** | The row (`docs/observations/INDEX.md:79`, cold rebuild 09-25) and the fix (`f35e7df`) are right. But physics rejects 4.7 kΩ at 400 kHz only above about 75 pF. `f35e7df` says "rejects them above ~75 pF at 400 kHz", and INDEX.md:79 says "4.7 kΩ holds … ~75 pF at 400 kHz". At the rule's default 50 pF (`check_physics.py:476`) it rises in 0.8473 × 4.7 k × 50 pF = 199 ns and passes |
| 17 | l.67-68: R16 asked the rise-time rule to read the revision's pull-ups; both lessons came from the 09-25 cold rebuild | CONFIRMED | `docs/observations/INDEX.md:75` ("cold rebuild, 09-25"; "→ P5: check_physics's I2C rule should read the revision's pull-ups from hardware_revisions") |
| 18 | l.78-82: I2C 7 distinct parts (VL6180X and six RTC modules), I2S 1 (MAX98357A), SPI none | CONFIRMED | Independent recount over the library, shelf, catalog, drawer, drawer-import, irrigation, rc-car, spark-quickstart and the bin, de-duplicated by record id (`verify/recount_buses.py`). I2C: dfr0469, dfr0641, dfr0819, dfr0821, dfr0998, ds3231-at24c32, vl6180x-breakout. I2S: max98357a-dfr0954. No `spi`; no `"bus": "uart"` anywhere |
| 19 | l.84-85: DFR0534 records its serial line as a plain signal; declaring `uart` is refused | CONFIRMED | `parts/dfr0534-module.json:8-13` (signal `MP3_TX`, pin `RXD`, no `bus`); `parts.py:538-541` |
| 20 | l.89-90: "the bus never leaves logic 0 and nothing answers" | CONFIRMED | `compare_design.py:121-122` |
| 21 | l.90-91: "So whether I2C works depends on parts on the board, and the netlist shows those parts" | **PARTLY TRUE** | The same docstring continues: "Breakout boards often carry their own" (`compare_design.py:122-124`). Module-carried pull-ups, such as the VL6180X's 10 kΩ (`parts/vl6180x-breakout.json:96`) and the DS3231 module's 4.7 kΩ (`init_project.py:108-109`), are not in the board netlist. `init` skips such lines for that reason (`init_project.py:107-115`), and the answer's own hole #3 (l.146) depends on it |
| 22 | l.97-98: 1-Wire would be the same arithmetic, and spark has no rule for it | CONFIRMED (no rule) | Not in `parts.BUSES` (`parts.py:257-262`); no rule mentions it |
| 23 | l.102-103: W14 "Nothing enters the plugin unless a real design is blocked without it that week" | CONFIRMED | `scrum/WORKING_AGREEMENTS.md:150-159` |
| 24 | l.104-105: the 09-29 cut, "Petr's call … no AI bloat, nothing kept that nothing uses", deleted 5,962 lines | CONFIRMED | `066c4af` message; `--shortstat`: 43 files, +99 / −5962; `scrum/VISION.md:66` |
| 25 | l.105-107: spark's only address-clash check was removed because "no project needs" it, beginning at line 219 | CONFIRMED | `066c4af`: "the one it had that the chain lacks (two I2C devices at one address) no project needs". In `066c4af^:scripts/check_design.py`, `as_address` is at :219 and `check_i2c_addresses` at :233 |

## §2 Table and holes

| # | Claim | Verdict | What the source shows |
| --- | --- | --- | --- |
| 26 | l.123: I2C on the board's SDA/SCL, shared by every device | CONFIRMED | `assign_pins.py:166` (SHARED_LINES), `:224-225` |
| 27 | l.123: I2C wired pin to pin; pull-ups placed when asked, tied to the part's own supply | CONFIRMED | `emit_board.py:734-735`; `:634-640` (`supply_net_of`, falling back to V33) |
| 28 | l.123: three I2C rules | CONFIRMED | `parts.py:384-409`; `compare_design.py:117-174`; `check_physics.py:396-425` |
| 29 | l.124: SPI SCK/MOSI/MISO shared; each device has its own chip select | CONFIRMED | `assign_pins.py:166`, `:268-271` |
| 30 | l.124: no rule reads SPI; no part uses it | CONFIRMED | `verify/recount_buses.py`; no rule names SPI. The caveat in #6 applies to an SPI part's input pins |
| 31 | l.125: I2S on any pin through the matrix, never shared | CONFIRMED | `assign_pins.py:166` (no I2S line is shared), `:226-230`, `:307-309` |
| 32 | l.125: I2S "Checked: No" | **PARTLY TRUE** | Same as #6. No bus rule, but the floating-input rule examines the amplifier's BCLK, DIN, LRC and SD on any generated board and flags them as floating |
| 33 | l.125: "NEVER stop LRCLK while BCLK is running" is text no code reads | CONFIRMED | `parts/max98357a-dfr0954.json:178` (a `host_requirements` string, never evaluated: `emit_board.py:930-944`) |
| 34 | l.126: UART is not a bus; console pins are spent last | CONFIRMED | `parts.py:538-541`; `assign_pins.py:72-79` (console_uart penalty 40) |
| 35 | l.126: the serial-part-on-console check was cut in `066c4af` | CONFIRMED | `066c4af^:scripts/check_design.py:208-214` |
| 36 | l.126: "TX-to-RX crossing cannot be described: a line matches the board's label for the same line (`parts.py:250-256`)" | **REFUTED** | The cited lines map vendor aliases onto the board's label, and SPI already maps a device's DIN/SDI onto the host's MOSI (`parts.py:259-260`). A record names its bus line by `signal` (`parts.py:740`), separately from the module's `pin`. That is how `dfr0534-module.json:9-10` already writes host-side `MP3_TX` on module pad `RXD`. In memory, adding `BUSES["uart"] = {"TX": ("TX",), "RX": ("RX",)}` with a record `{signal: UART_TX, pin: RXD}` places it on TX GPIO43 and `{signal: UART_RX, pin: TXD}` on RX GPIO44 (`verify/uart_crossing.py`). So the crossing is describable. The real obstacle is that those labelled pins are the console, taken as "dedicated hardware" (`assign_pins.py:224-225`; `boards/firebeetle2-esp32s3.json:256-262`) |
| 37 | l.127: 1-Wire and CAN are not in the bus list | CONFIRMED | `parts.py:257-262` |
| 38 | l.128: analogue only on ADC1, because ADC2 cannot be read with WiFi on | CONFIRMED | `boards/firebeetle2-esp32s3.json:198-199`; `assign_pins.py:131-132` |
| 39 | l.128: a divider is added if the record asks for one | CONFIRMED | `emit_board.py:626-628`, `:654-662` |
| 40 | l.128: on the bin, SENSE_ADC (1 kΩ plus filter cap) is examined by nothing | CONFIRMED | smartbin `board.tsx:357-361`: SenseResistor sits between MOTOR_SENSE and SENSE_ADC, neither a stated rail. `check_resistor_power` walks only rail members (`check_physics.py:359-360`). The cap's other end is on GND, whose `nominal_volts` is null, so derating skips it |
| 41 | l.129: digital inputs get pulls if asked; the floating-input rule; inputs taken from the records; direction not checked | CONFIRMED | `parts.py:326-330`; `compare_design.py:177-212`; `init_project.py:80-100`; `compare_design.py:188-189` (power OR ground OR any stated rail) |
| 42 | l.130: a divider from two stated values; nothing compares the divided voltage with 3.3 V; the arithmetic is in the flow meter's `why` | CONFIRMED | `parts.py:330`, `:436` (keys only); irrigation: `parts/sen0217-flow-meter.json` divider `why`: "5 V x 18/28 = 3.2 V at the ESP32's pin". `sim_project.py:47` only passes the values to Wokwi |
| 43 | l.130: `carrier_has_level_shifters` has no reader | CONFIRMED | `parts/vl6180x-breakout.json:63`; not among the eight names read (#76) |
| 44 | l.130: `pull_conflicts` does one such sum, only prints, and `check_all` does not run it (P109, #43) | CONFIRMED | `parts.py:1284-1315`; callers only `parts.py:1337` (describe) and `emit_board.py:946` (a board-file comment); #43 "P109 — check_all reports the generator's CONFLICT lines…" (open) |
| 45 | l.131: strapping pins are refused, even when a record names one | CONFIRMED | `assign_pins.py:59-61`, `:244-254`; `boards/firebeetle2-esp32s3.json:213-218` |
| 46 | l.131: on a hand-made board nothing compares the pin map with the straps; found only in `assign_pins.py`, `boards.py` and one `emit_board.py` comment | CONFIRMED (for `scripts/`) | In `scripts/*.py` only `assign_pins.py:59-61`, `boards.py:95`, `emit_board.py:522`. Repo-wide the word also appears in docs, design references, tests and the board/part data, none of which is a check |
| 47 | l.132: the LED series resistor is rounded up so the current never exceeds the ask | CONFIRMED | `emit_board.py:595-617` |
| 48 | l.132: 40 mA appears only in a source string; nothing compares pin current with a limit | CONFIRMED | `boards/firebeetle2-esp32s3.json:416`; no other hit in boards or scripts |
| 49 | l.133: four power rules; rail supply runs only through `check_all --project` | CONFIRMED | `check_physics.py:196`, `:263`, `:305`, `:336`; `:450-454`; `check_all.py:136`, `:446` |
| 50 | l.138-139: init writes `Component.PIN` "because spark's own generator wires every signal pin-to-pin and no net is ever called SDA" | CONFIRMED | `init_project.py:117-119` |
| 51 | l.140-141: the rise-time rule finds a line by net name only, and moves on without a word | CONFIRMED | `netlist.py:135-138`; `check_physics.py:410-411` |
| 52 | l.142-143: 9.1 kΩ at 400 kHz: 386 ns on net `SDA`, no finding as `Sensor.SDA` | CONFIRMED | `probe_bus_line_forms.py` re-run: "9100 ohm against 50 pF rises in 386 ns, but 400 kHz allows 300 ns" vs "no finding" |
| 53 | l.144-145: a series resistor counts as a pull-up and hides a failing bus; `compare_design` leaves it out | CONFIRMED | `check_physics.py:406-409`; repro case 3 (`repro-output.txt:13-14`, no rise finding beside 10 k at 100 pF); `compare_design.py:144-150` |
| 54 | l.146-151: VL6180X 10 kΩ plus 4.7 kΩ asked = 3.2 kΩ; four sensors give 799 Ω, under the 1 kΩ floor; each resistor passes alone | CONFIRMED | `parts/vl6180x-breakout.json:96`, `:159-171`. Host pull-ups are placed per instance (`emit_board.py:575-581`, `:651-678`), so 1/(4/4700 + 4/10000) = 799 Ω; `compare_design.py:28-32`, `:162-172` judge each resistor alone. Physics has no lower bound |
| 55 | l.152-153: a pull-up to a supply tscircuit did not flag is reported missing; MOTOR6V is unflagged on the bin | CONFIRMED | `netlist.py:88-89` (`is_power` only). smartbin `dist/board/circuit.json`: MOTOR6V `is_power False`. `probe_rail_predicates.py` re-run: "[i2c-pullups] SDA: nothing pulls it up" |
| 56 | l.154-155: two VL6180X at 0x29 build with exit 0 | CONFIRMED | `tests/test_emit_board.py:767-777` (asserts `EXIT_OK`); `parts/vl6180x-breakout.json:45-46`; `7381fed`: "built with tsci: 12 traces, 0 errors" |
| 57 | l.156-157: a null capacitance crashes the rule, and a missing one becomes 50 pF silently (P107, #41) | CONFIRMED | `check_physics.py:476`; init writes null (`init_project.py:185`); repro 4a/4b re-run; #41 title |
| 58 | l.159-162: "Everything else gets silence … The only thing that looks at the other buses is the AI reviewer's `signals` dimension" | **PARTLY TRUE** | The quote is right (`agents/design-reviewer.md:39-40`). But the floating-input rule also examines I2S inputs, and wrongly (#6). The firmware-hardware reviewer covers "pin assignments, peripheral counts and conflicts" (`design-reviewer.md:43-44`) |
| 59 | l.162-163: the review "does not remember between sessions" | CONFIRMED | `skills/spark-review/SKILL.md:86-87` |
| 60 | l.167-168: the bin's `make check` runs physics directly, so rail supply never runs | CONFIRMED | smartbin `Makefile:228`; `check_physics.py:450-454`, `:537` |
| 61 | l.169-170: the bin's I2C rule runs and passes, 2.2 kΩ at 50 pF giving 93 ns of 300 | CONFIRMED | smartbin `.spark/rules.json` (`i2c_buses` SDA/SCL, 400000 Hz, 50 pF), `board.tsx:292-293`, `:373-378`. `verify/bin_physics.py`: exit 0, status ok, no rise finding, 93.2 ns |
| 62 | l.171: the bin's audio lines and SENSE_ADC are examined by nothing | CONFIRMED | Bin rules: `must_not_float` holds only `MotorDriver.BIA/BIB`; no rule names the I2S nets; see #40 |
| 63 | l.172-173: via `check_all`, physics "could not look": "0 requirements files describe this circuit…" | CONFIRMED | `check_all_bin.txt:12-17`; re-run in-process with the project: could-not-run with that note |

## §3 Architecture

| # | Claim | Verdict | What the source shows |
| --- | --- | --- | --- |
| 64 | l.181-182: one list of checks and one set of answer words | CONFIRMED | `check_all.py:279-290`; `outcomes.py:23`. `check_vendor_pins` still says "mismatch", as a documented local alias (`check_vendor_pins.py:181-184`; `outcomes.py:9-13`) |
| 65 | l.183-186: forgetting a step fails a test | CONFIRMED | `tests/test_check_all.py:583`, `:168-171`; `tests/test_self_confirmation.py:116-121` |
| 66 | l.190-192: there is no list of rules; each is called by name | CONFIRMED | `check_physics.py:428-489`; `compare_design.py:215-224` |
| 67 | l.193-194: severity "problems" gives `status: ok`, exit 0 | CONFIRMED | `check_physics.py:84`, `:538`, `:546-547`. `verify/severity.py`: `main()` exit 0 ok, and `check_all`'s wrapper also says ok (`check_all.py:139-148`) |
| 68 | l.195-197: each check reports its own way, and `check_all` flattens them, dropping `fix` | CONFIRMED | `check_physics.py:81`; `check_footprints.py:48`; `compare_design.py:44`; `check_bom.py:77-80`; `check_vendor_pins.py:147-149`; `check_all.py:129`, `:139-141` |
| 69 | l.197: "(P43, parked)" | **PARTLY TRUE** | P43 is open issue #11, in the board's **Idea** column. Its backlog heading reads "slice 4: the `fix` half only; the rest parked" (`scrum/PRODUCT_BACKLOG.md:1381`). The `fix` half, which is what this sentence is about, is the half that was *not* parked |
| 70 | l.202: `c0e3d76`: 6 files, +29, +64, +38 | CONFIRMED | numstat: parts.py 29/0; test_parts 62/0 + test_self_confirmation 2/1 (+64/−1); mutation table 38 |
| 71 | l.203: "A netlist rule: floating input (B13)", `4daa58f`: 5 files, +38/−8, +51/−6, +12 | **PARTLY TRUE** | The numbers are right (compare_design 26/8 + netlist 12/0; tests 51/6; mutations 12). But floating-input was not born in `4daa58f`. It existed from `55d2368` (2026-09-24) as "connects to nothing" (`git show 4daa58f^:scripts/compare_design.py:177-195`). B13 tightened it, so this row prices extending a rule, not adding one |
| 72 | l.204: `3749303`: 10 files, +226/−19, +278, +128 | CONFIRMED | check_all 36/3 + check_physics 75/13 + emit_board 115/3; tests 51 + 98/1 + 129; mutations 128 |
| 73 | l.205: `07821a0`: 5 files, +62/−19, +60, +32 | CONFIRMED | assign_pins 27/19 + parts 35; tests 31 + 29; mutations 32 |
| 74 | l.207-208: a new rules field touches init, two guides and every project's rules.json | CONFIRMED | `commands/init.md:67-68`; `docs/guide/agents.md:347-350`; `docs/guide/journey.md:237-238`; `init_project.py:271` (`merged`) |
| 75 | l.212-213: "A bus is one entry in `parts.BUSES`", which buys validation and placement | **PARTLY TRUE** | One entry buys validation and matrix placement. A bus whose lines devices share also needs `SHARED_LINES` (`assign_pins.py:166`), or a second device is refused as "already taken" (`:272-273`). A board-dedicated bus also needs a `pin_roles`/`PIN_ROLES` entry (`boards.py:98-102`). The answer's own source lists all three (`knowledge-loop.md:305`) |
| 76 | l.238-240: only eight fact names are read by code, plus any current a power pin points at | CONFIRMED | `parts.py:398` (`module_has_i2c_pullups`), `:405` (`i2c_pullup_ohms`), `:1294` (three names), `:1312` (`input_low_threshold_v`); `emit_board.py:603` (`io_volts`, `forward_voltage_v`); pointers at `emit_board.py:398-420`. A sweep for `.get("value")` finds no other named read |
| 77 | l.214-215: no table holds a bus's electrical properties; each I2C rule restates them | CONFIRMED | `parts.py:257-262` holds lines and aliases only; `compare_design.py:121-122`, `check_physics.py:62-69` restate them |
| 78 | l.219-220: the rules file has one `i2c_hz` and one capacitance per project | CONFIRMED | `check_physics.py:469-476`; `init_project.py:164`, `:184-185` |
| 79 | l.221-223: "UART needs more than a list entry. Its TX goes to the other side's RX, and … the pins labelled TX and RX are the console" | **PARTLY TRUE** | The console reason holds. In memory a uart entry lands on GPIO43/44 (`console_uart`) as "dedicated hardware" (`verify/uart_crossing.py`; `boards/firebeetle2-esp32s3.json:256-262`). The TX→RX reason does not (see #36). The cited `knowledge-loop.md:305` gives only the console reason |
| 80 | l.224-226: "The assigner works out who shares each bus, then throws that away" | **PARTLY TRUE** | `bus_holders` records only the first holder per GPIO and is local (`assign_pins.py:237`, `:275-276`). But every sharer's assignment is returned with the same pin and a "shared with everything else on the … bus" reason (`:261-267`, `:316`). The sharing survives in the result, just not grouped |
| 81 | l.230-236: a fact changes an outcome: L9110S pointed at 0.8 A gives a pass instead of could-not-run; a 2.5 A stall figure gives a problem | **PARTLY TRUE** | Re-run in memory (`verify/motor_rail.py`). Pointing only the L9110S's VCC at `continuous_current_a` still leaves MOTOR6V could-not-run ("JstPh2PowerInlet.VCC: names no fact for its current"). The pass also needs the inlet's `VCC.can_supply = contact_rating_a` (2.0 A), which `knowledge-loop.md:230` did. The library L9110S states no stall figure, only `continuous_current_a` 0.8 A; the 2.5 A fact was added in memory. With it: "draws at least 2.50 A, more than JstPh2PowerInlet.VCC is rated for (2.00 A)" |
| 82 | l.240: "The other facts, roughly 550" | **PARTLY TRUE** | 557 fact entries across the part layers, counting shelf copies of project records; 449 distinct (record, fact) pairs (`verify/count_facts.py`). The source says its totals include copies (`knowledge-loop.md:100-101`) |
| 83 | l.241-242: fab numbers live in `data/fabrication.json` and a project can override them; copper thickness is ignored | CONFIRMED | `fab.py:35-38`; `copper.py:40` reads `fab.process("copper_thickness_mm")` with no rules; repro 8b (`repro-output.txt:38-43`) |
| 84 | l.243: board files steer placement: ADC pins, wake pins, pin roles | CONFIRMED | `assign_pins.py:117-160` |
| 85 | l.244-245: "Resistors a record asks for are placed on the board, and `init` turns them into rules to check" | **PARTLY TRUE** | They are placed (`emit_board.py:643-681`). But `init` reads only `kind == "pullup"` host parts on I2C pins, to seed `i2c_buses` (`init_project.py:124-129`). Pull-down, divider and series requests become no rule. `must_not_float` comes from input-direction pins (`:98`), not from resistors |
| 86 | l.249-250: "Every rule's logic, on purpose: 'a law or a published standard' stays 'in CODE, beside the arithmetic'" | **PARTLY TRUE** | Rule logic is code, but the cited note does not say that. `data/fabrication.json:3` is about where *numbers* live: IPC-2221 coefficients, the I2C rise limits and the derating stay in code beside the arithmetic. It sets no policy on rule logic |
| 87 | l.252: a fact under another name is silently unused | CONFIRMED | `parts.py:1295-1296`; `c0e3d76` ("the PO's own RTC record stated the fact under a second name") |
| 88 | l.253-254: research asks in words: "on-board pulls (ohms, rail); bus and address" | CONFIRMED | `commands/research.md:63` |
| 89 | l.255-257: the closed lists, and "an open vocabulary silently disabled a headline check" | CONFIRMED | `parts.py:184`, `:257-262`, `:330`; `assign_pins.py:166`; `boards.py:91-103`; quote `boards.py:85-90` |

## §4 Learning

| # | Claim | Verdict | What the source shows |
| --- | --- | --- | --- |
| 90 | l.265-266: a reviewer has "no memory of previous reviews" | CONFIRMED | `agents/design-reviewer.md:30` |
| 91 | l.272-273: every fact has a value, a source and `verified`; an unverified value must say why it matters | CONFIRMED | `parts.py:53` (`REQUIRED_FACT_KEYS`), `:694-709` |
| 92 | l.274: the shelf carries a project's records to every later project | CONFIRMED | `store.py:57-66` (project, shelf, library, catalog) |
| 93 | l.275-276: "more parts known … proven by use … fewer requests, measured" | CONFIRMED | `docs/2026-10-04-store-design.md:13-15` |
| 94 | l.277-278: "Proven by use" is designed (step T) but not built | CONFIRMED | `:25-27`; no script writes a built-and-ran mark. `drawer.py`'s `used_in` counts allocation, not proof |
| 95 | l.279-280: `host_requirements` is "Prose on purpose", printed and copied, never evaluated | CONFIRMED | `parts/l9110s-module.json:105`; `emit_board.py:930-944` |
| 96 | l.281-282: four resistor kinds a record can demand | CONFIRMED | `parts.py:326-330` |
| 97 | l.283-286: five reviewer dimensions; rules born from incidents | CONFIRMED | `agents/design-reviewer.md:37-49`; `check_physics.py:9-18`; `compare_design.py:10-14`; `check_footprints.py:7-19` |
| 98 | l.287-290: the intake steps; the findings store built in `02250ee` with "20 findings: 11 blocked, 8 open, 1 rejected, 0 resolved", then cut | CONFIRMED | `docs/observations/README.md:26-35`. `02250ee` (spark, 2026-09-24) adds `scripts/findings.py`. The INDEX notes the store's data lived "in the smart-bin repo" (`docs/observations/INDEX.md:15-19`). Cut in `066c4af` |
| 99 | l.294-302: "Every rule in section 1 came through these steps": incident, INDEX row, reproduced (W9), W14 issue, rule with failing-first test and mutation table, commit | **REFUTED** | `i2c-pullups` (`55d2368`, 2026-09-24 12:00) and `i2c-rise-time` (`dae10dd`, 09-24 14:41) predate the observations INDEX (`10eea53`, 09-25), W9 (`717c37e`, 09-25), W14 (`6557c71`, 09-29) and the first mutation table (`997b756`, 09-29). Neither commit touched a test: `dae10dd` is check_physics + check_vendor_pins only, and its tests came later in `c62a8dc`, "Tests for the two checks that had none". The later rules (P55 `c0e3d76`, P21 `7381fed`) did go through backlog items and mutation tables |
| 100 | l.300-301: the Definition of Done | CONFIRMED | `scrum/README.md:98-113` |
| 101 | l.306-309: R16 became P5, closed because "its audit was performed … P34 and P35 … carry the need"; neither reads the board revision | CONFIRMED | `scrum/PRODUCT_BACKLOG.md:1636-1637`. P34 is "A check that compared nothing says so" (`:35`), P35 "The rules see spark's own wiring" (`:50`) |
| 102 | l.310: no script reads `hardware_revisions` | CONFIRMED | No hit in any non-test `.py` |
| 103 | l.320, l.343: issues carry *Needed by* and *Value proven by* (`scrum/README.md:95-96`); every item names a proving command | **PARTLY TRUE** (citation) | `:95-96` shows only *Value proven by*. *Needed by* is at `scrum/README.md:30` and W14 `WORKING_AGREEMENTS.md:152-153`. The claim itself holds |
| 104 | l.327-328: P122 is a confident false pass; P133 (#67) gathers the could-not-look-reads-as-pass cases | CONFIRMED | #56 "P122 — The I²C rise-time check runs on the boards spark generates"; #67 "P133 — The checks tell the truth: nothing that could not look reads as a pass" |
| 105 | l.329-331: "Nagging a board that has no bus …"; "a list that cries wolf is a list nobody reads" | CONFIRMED | `check_physics.py:470-472`; `skills/spark-review/SKILL.md:64` |
| 106 | l.332-333: P16 dropped: "a wake-polarity rule derived from one board's constant is that board's knowledge" | CONFIRMED | `scrum/PRODUCT_BACKLOG.md:1634-1636` |
| 107 | l.334-335: ALL_LOW reached the bin, irrigation and the RC car through copied `host_requirements` | CONFIRMED (as the backlog states it) | `scrum/PRODUCT_BACKLOG.md:437-441` |
| 108 | l.336-337: record text reaches the generated board unescaped (P87, #19) | CONFIRMED, still true at 8f7733d | `scrum/PRODUCT_BACKLOG.md:973-981`; #19 open; `emit_board.py:656`, `:667`, `:674`, `:695` interpolate record text into JSX comments, with no escaping in the file |
| 109 | l.341-342: W11 (the PO orders), W14 | CONFIRMED | `scrum/WORKING_AGREEMENTS.md:114-121`, `:150-159` |

## §5 Facts inside the options

| # | Claim | Verdict | What the source shows |
| --- | --- | --- | --- |
| 110 | l.356: only the L9110S states the pull-up fact `pull_conflicts` needs | CONFIRMED | `onboard_input_pullups_ohms` appears only in `parts/l9110s-module.json:84`, across the library, shelf, catalog, drawer and all projects |
| 111 | l.373-374: compare_design's line finder; a pull-up only if its other end is on a supply | CONFIRMED | `compare_design.py:100-114`, `:144-150`. Moving the latter into physics as is would carry over hole #4 (#55), since "supply" there means `is_power` only |
| 112 | l.380: the "not examined" pattern exists in check_footprints | CONFIRMED | `check_footprints.py:408-446` |
| 113 | l.385-389: physics would read `facts.i2c_pullup_ohms`; records reach physics the way rail currents do | CONFIRMED | `parts.py:405` (the name exists); `check_all.py:134-137` |
| 114 | l.399-400: epic P136 (#70), "Full circuit checks: analogue and board checks", opened today | CONFIRMED | #70 created 2026-10-06T08:52Z, title "P136 — Full circuit checks: analogue and board checks in spark (epic)" |
| 115 | l.402-403: its discovery "waits until P104 (#33) is finished", and #33 is closed | CONFIRMED | #70 body: "Decided by the council's discovery, which waits until P104 (#33) is finished"; #33 closed 2026-10-06T09:13Z |
| 116 | l.404: it links P122 (#56), P107 (#41), P109 (#43) | CONFIRMED | #70 body: "Related (link, don't move): P107 #41, P109 #43, P118 #52, P120 #54, P122 #56, P126 #60" |

## Not checked: judgement, or marked INFERRED

- l.109, "It was never a design decision": no artifact records a decision either way.
- The general-electronics statements at l.93-98.
- The automatic-loop list at l.314-322.
- The fit with the process at l.345-347.
- The option table and its costs at l.353-395.

The facts these rest on are covered above: #75, #79 and #85 adjust three of them.
