# Does today's spine hold, and what would simulation cost

Observer run, 2026-09-25, after `c1537b2`. Everything below was run on this machine. Anything I
could not run is marked **hypothesis** and carries no number.

---

## Part 1 — today's work

### What holds

```
$ cd /Users/petr/Development/spark && python3 -m unittest discover -s tests
Ran 362 tests in 0.087s
OK                                                            exit 0

$ cd /Users/petr/Development/smartbin-local && python3 .../check_spine.py
  [ok  ] board            DFRobot FireBeetle 2 ESP32-S3
  [ok  ] schematic        11 trace(s) written
  [ok  ] footprint        FireBeetle2Esp32S3.tsx
  [ok  ] build            8 trace(s), 0 errors                exit 0
```

Both reproduce. The gate is real: it runs the generator, builds with `tsci`, and reads
`circuit.json`. It is not a mock.

### M1 — THE FALSE `ok`. The gate's own reference design has no ground on the microcontroller.

`check_spine.py` reports `ok` for a board where **the MCU is connected to nothing but five signal
pins**. No ground. No 3.3 V. The power inlet — the part added in `c1537b2` specifically so the
reference design would have a rail source — has **neither of its two pins in copper**.

Read from the `circuit.json` the gate itself just passed (`--keep`, then walking
`source_trace` → `pcb_trace`):

```
PCB   Mcu.pin9  + Vl6180xBreakout.SDA
PCB   Mcu.pin10 + Vl6180xBreakout.SCL
PCB   Mcu.pin28 + Vl6180xBreakout.GPIO1
PCB   Mcu.pin4  + L9110sModule.AIA
PCB   Mcu.pin21 + L9110sModule.AIB
PCB   L9110sModule.VCC + net.MOTOR6V
PCB   L9110sModule.GND + net.GND
NONE  Vl6180xBreakout.VIN  + net.V33        <- the sensor has no supply
PCB   Vl6180xBreakout.GND  + net.GND
NONE  JstPh2PowerInlet.VCC + net.MOTOR6V    <- the inlet feeds nothing
NONE  JstPh2PowerInlet.GND + net.GND        <- the inlet returns nowhere
```

Eleven connections asked for, eight in copper. And the reason is upstream of routing — the
generated `board.tsx` never emits a trace for the MCU's own power pins at all:

```
MCU power-ish ports:      pin14/GND1, pin15/GND2, pin17/3V3, pin32/VCC
MCU ports used in traces: pin9/SDA, pin10/SCL, pin28/A5, pin21/D12, pin4/D3
```

Those three pads carry `source_net_id = None` and `subcircuit_connectivity_map_key = None`. The
board does have copper pours (72 GND, 6 V33) — but a pour can only include pads that belong to
its net, and these belong to none. So the pours do not rescue it. `net.V33` has exactly one
member, which is the single-member-rail failure `jst-ph-2-power-inlet.json`'s own `//` comment
says it was created to end.

**Why the gate cannot see it.** `run()` computes `traces_asked = emitted.stdout.count("<trace ")`
— 11 — prints it in the schematic stage, and then never compares it to anything. The build stage
tests `traces == 0`. Partial routing is invisible by construction. The docstring's own premise
("tscircuit skips routing entirely when one net is unroutable") is the *easy* half of the failure;
the hard half is that it also skips *some* nets and returns a plausible number.

This is the S2/R5 defect class one layer in: the instrument now counts, but counts the wrong
thing. `8 > 0` and `8 ≠ 11` are different questions, and only the first is being asked.

**Fix, in order of value:**
1. Fail unless every `source_trace` has a `pcb_trace` — the number is already in hand at both ends.
2. Fail when any `source_port` on the MCU named GND/3V3 has no net. A board whose MCU shares no
   ground with its modules is not a board, and no router can fix it.
3. `emit_board` must wire the host's own power pins to the rails it wires everything else to.

Until (1) and (3) land, `check_spine` exiting 0 means "some copper exists", not "the chain works",
and it is being cited as the definition of done (`S10`).

### M2 — a malformed requirements file exits 1 with a raw traceback

```
$ check_spine.py malformed.json
Traceback (most recent call last):
  File ".../check_spine.py", line 210, in main
    requirements = (json.loads(Path(args.requirements).read_text())
json.decoder.JSONDecodeError: Expecting value: line 2 column 1
                                                             exit 1
```

`json.loads` sits **outside** the `try` in `main()`, four lines above the `except` whose comment
reads *"Anything unforeseen is could-not-run, never problems... reporting one as the other sends
somebody to debug a design that was never examined."* Exit 1 is `the chain is broken`. The chain
was never started. This is the identical defect `c1537b2` fixed in `emit_footprint`, reintroduced
in the same commit, in the same file, two screens apart. Move the read inside the `try`.

### M3 — an empty parts list reports `problems`, not `could-not-run`

`{"board": ..., "parts": []}` → exit 1, *"built with 0 pcb_traces"*. That message accuses the
router; the truth is nobody asked for anything. Cheap fix: refuse an empty `parts` before emitting.

### M4 — what I could not break (report these as holding)

| attempt | result | verdict |
| --- | --- | --- |
| part that does not exist | exit 2, lists the 5 available | correct |
| board that does not exist | exit 2, lists the 2 available | correct |
| `{}` — no board selected | exit 2, names `boards/active.json` | correct |
| board with `physical.header` deleted | exit 2, *"no footprint could be generated"* | correct |
| `pin_order` pad renamed `VIN`→`V_IN_TYPO`, count still 7 | exit 2, **two** precise messages | correct, and good |

That last one is the real test of `c1537b2` and it passes convincingly:

```
- pin_order pad 2 is 'V_IN_TYPO', which this part never mentions — a pad name that
  matches nothing silently wires nothing
- pin_order does not say where VIN sit(s), so the generator would have to guess a pad
```

**Remaining hole (hypothesis, not reproduced):** `footprint_pad_count` returns `None` outside
`PAD_COUNT_FAMILIES`, so a part using `jlcpcb:C<lcsc>` — a documented spark pattern — gets no
pad-count check at all. The name cross-check above still fires, which is the more valuable half,
so I rate this low.

### M5 — the footprint generator matches the hand file exactly (verified, no defect)

`emit_footprint.py --board firebeetle2-esp32s3` against
`/Users/petr/Development/smartbin-local/FireBeetle2Esp32S3.tsx`, compared after normalising
whitespace, on `(portHints, pcbX, pcbY, outerDiameter, holeDiameter, shape)`:

```
generated pads: 32   committed pads: 32   IDENTICAL: True
```

All 32, same coordinates, same 1.00 mm holes, same 4 silkscreen segments. The generated file
differs only by a 6-line header comment and indentation. This one is solid.

---

## Part 2 — simulation

### M6 — spark ships nothing that simulates anything

`scripts/bench_sim.py` is 6.7 KB whose entire model of the physical world is this:

```python
BENCH = { "mp3-idle-current": {"range": (12.0, 26.0), ...}, ... }   # four entries
value = round(random.Random(seed).uniform(low, high), 2)
```

It never opens a circuit, a netlist or a design. It cannot: nothing is passed to it but a string
name and a seed. It is a fixture for demonstrating `findings.py`'s measurement loop, and it is
scrupulously honest about that (`NOT A READING`, `source: simulated`, excluded from `NOT_EVIDENCE`).
The problem is only that it is filed under "simulation" and is the sole thing there.

`skills/spark-simulate/SKILL.md` is 5.1 KB of accurate, well-sourced advice describing three
layers. Layers 1 and 2 are the right advice. But the skill ships no code, and
`references/fake-machine.md` (42 lines) ends by pointing at **the user's other repository**:

> A complete, working example lives in the smart-bin project:
> `firmware/micropython/tests/fake_machine.py`

`grep -rn "wokwi\|simulat" scripts/ commands/` returns prose comments and one board-definition
field. There is no third layer, no second layer, and no first layer. **The claim is not matched by
what ships.** Anyone installing spark and asking "can we simulate this?" gets a table of things
they must go and write.

### M7 — the converter is liftable, and I proved it by pointing it at spark's own board

```
$ cd tools/circuit-to-wokwi && bun test
29 pass  0 fail  72 expect() calls   [133.00ms]
```

Then, unmodified, against the `circuit.json` `check_spine` had just produced:

```
$ bun run cli.ts --circuit <spark's circuit.json> --out /tmp/spark-diagram.json
board: 4 components, 7 nets
diagram: 1 parts, 0 wires, 0/7 nets wired

3 problem(s) converting the board:
  - no Wokwi part is mapped to this component ... (component L9110sModule)
  - no Wokwi part is mapped to this component ... (component Vl6180xBreakout)
  - no Wokwi part is mapped to this component ... (component JstPh2PowerInlet)
```

It parsed spark's output, built the netlist, resolved the board, placed it, and stopped on
**three missing rows in a data table** — which is precisely the extension point `ARCHITECTURE.md`
advertises ("a new part → one entry in `lib/mapping.ts` → data only"). No code change was needed
to get this far.

**Coupling, measured by import graph.** The converter half — `lib/{types,netlist,mapping,
geometry,placement,merge,validate,board}.ts` + `lib/emitters/wokwi.ts`, ~1,000 lines — imports
`node:fs`, three npm packages, and each other. It imports nothing from the bin's firmware,
nothing from `mcu-pins.ts`, nothing from `lib/checks/`.

The bin-specific coupling is real but quarantined:

| where | what | lift cost |
| --- | --- | --- |
| `lib/checks/firmware-pins.ts:20` | `import { MCU } from "../../../../mcu-pins"` | leave behind — this is the consistency checker, not the converter |
| `check-consistency.ts` | hard-codes `config.py`, `bringup/`, the bin's diagram paths | leave behind (~440 lines with `lib/checks/`) |
| `cli.ts:19-21` | bin paths, but `--circuit`/`--out` already override them | `DEFAULT_CHIPS` needs a flag; one line |
| `lib/mapping.ts:172,181` | `BinConnector`, `Mp3Player` skip rules | two data rows |

And the strongest signal: **`lib/board.ts` already reads `.spark/board.json`** — spark's own
resolver output, with a docstring saying it was rewritten to stop duplicating `boards.py`. Meanwhile
`scripts/boards.py:59` already *requires* `wokwi_part_type` in every board definition, and the
FireBeetle file already carries `wokwi_pin_naming`, `wokwi_power_pins`, `wokwi_size_px`,
`wokwi_is_stand_in`. The two halves were built to meet. Nobody has walked them together.

**The one design question a lift must answer:** `mapping.ts` matches on *component name* by regex
(`/^Btn|Button/`, `"MotorDriver"`). spark names components after part ids (`L9110sModule`,
`Vl6180xBreakout`). Either the mapping keys off the part id — which spark controls, and which is
stabler than a name a designer chose — or, better, each part file grows a `wokwi` block
(`part_type`, `pins`, or `skip_reason`) and the table is generated. That puts the fact next to the
part it describes, which is the pattern the rest of spark already uses.

### M8 — the analogue path exists, is installed, and spark's board gives it nothing to chew on

`circuit-json-to-spice` is **not aspirational**. It is on npm at `0.0.46`, it is already in
`smartbin-local/node_modules` at `0.0.45` as a transitive tscircuit dependency, alongside
`@tscircuit/ngspice-spice-engine`, `spicey` and `spicets`. `BACKLOG.md:421` is its only mention in
spark. I ran it on both boards:

```
=== the hand-written bin board ===          === spark's generated board ===
* Circuit JSON to SPICE Netlist             * Circuit JSON to SPICE Netlist
.MODEL PMOS_ENHANCEMENT PMOS (VTO=-1 KP=.1) .END
RRedResistor    N4  N18  330
RPulldownIa     N8  0    10K                (2 lines. Nothing to simulate.)
RSdaPullup      N5  N7   2.2K
CMotorBulkCap   N14 0    220U
MMp3Switch      N15 N12 N7 N7 PMOS_ENH...
... 22 lines, R / C / MOSFET
```

The tool works. **spark's generator is what has nothing to give it**: `emit_board.py` emits module
headers and connectors and not one passive — no pull-up, no decoupling cap, no pulldown — so the
SPICE netlist is empty by arithmetic. This is `R7` ("prints the mandatory `host_requirements` and
implements none of them") cashing out: the L9110S's required 10k pulldowns and the VL6180X's
required I2C pull-ups are printed as prose in a JSX comment, and a component that is only prose
cannot be simulated. **Analogue simulation is blocked on the emitter, not on the SPICE tooling.**

One defect seen in passing in the bin's own netlist, unrelated to spark: `RCurrentShunt 0 0 0.1`
— a shunt with both nodes tied to ground, i.e. shorted. Worth a look in `smartbin-local`.

### M9 — the free/offline path, and what it would cost

Measured on this machine: `wokwi-cli` **not on PATH**, `WOKWI_CLI_TOKEN` **unset**, `ngspice`
**not installed**, `eecircuit-engine` (the WASM ngspice the SPICE packages use) **not installed**.
So no Wokwi minute can currently be spent by accident, and no analogue engine can currently run.

Everything below is offline and consumes **zero** Wokwi minutes:

| path | minutes | status here |
| --- | --- | --- |
| fake `machine` + unittest (layer 1+2) | 0 | works in the bin (80 tests); spark ships prose only |
| MicroPython unix port (`micropython sim/run_on_micropython.py`) | 0 | works in the bin (13 checks); spark ships nothing |
| `circuit-to-wokwi` generate + `@wokwi/diagram-lint` validate + `--check` | 0 | works; 29 tests; never contacts Wokwi |
| `circuit-json-to-spice` → netlist | 0 | works; needs `bun add eecircuit-engine` or `brew install ngspice` to actually solve |
| `wokwi-cli --scenario` | **spends them** | not installed; the only thing that does |

The 21 remaining minutes buy roughly 21 one-minute scenario runs. The point worth making: the
converter's `--check` gate is the part that protects them. It catches a stale diagram, a wrong pin
name and an unmapped part *before* a run, offline, in 133 ms — which is exactly how you stop
burning a minute to discover a typo.

### M10 — the honest summary of where "simulation" stands

The goal's last word has not been started, and `S13` was right. But the distance is much shorter
than a green field, because three of the four pieces exist and are tested — they are just in the
wrong repository (converter, 29 tests), or on npm and uninstalled (SPICE), or described instead of
shipped (fake `machine`). What is missing is the joins, and one of the joins (`emit_board` emitting
passives) is already on the backlog under a different name.

---

## Recommendation, in order

1. **Fix M1 first.** The gate that certifies the chain currently certifies a board whose MCU has
   no ground. Everything downstream — including any simulation — inherits that board. Two
   comparisons and one `emit_board` change.
2. **Lift the converter's ~1,000 non-check lines into `spark/tools/circuit-to-wokwi/`**, add a
   `wokwi` block to the five part files, and make `check_spine` run it as a sixth stage. Evidence
   it will work: it already parsed spark's `circuit.json` and stopped only on three data rows.
   Cost: hours, not days. Minutes spent: zero — generation and lint are offline.
3. **Only then** consider SPICE, and only after `emit_board` emits the passives the part files
   already demand. Until it does, the netlist is two lines long.
