### Owed facts and gaps

A record **owes** a fact when one the chain reads is missing from it: `footprint`, `pin_order`, `pin_order_proof`,
`body_mm` (its outline) or `simulation`. `--match` shows what each candidate owes, and `parts.py --audit` lists every
record that owes one. Today spark's own library owes none:

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --audit
```

<!-- output: run 2026-10-08, spark 0.7.0 -->
```text
  library       10 current,   0 owe facts,   0 broken
  xiao-esp32-c6 (library) stops at the footprint stage (P121) — no header geometry in its board file
```

On 2026-11-01 the same audit printed only the first line: the XIAO ESP32-C6 builds since
[P278](https://github.com/xmejkal/spark/issues/314). The other 2026-10-08 outputs on this page keep its old line.

In a scratch store of its own, a catalog record was written by hand to `<store>/catalog/soil-probe.json`:

```json
{"schema": 1, "id": "soil-probe", "name": "A capacitive soil probe on a 3-pin cable", "kind": "sensor",
 "function": [{"does": "sense", "what": "soil-moisture"}],
 "needs": [{"signal": "SOIL_MOISTURE", "pin": "Signal", "direction": "out", "needs": ["adc"]}],
 "power": [{"pin": "VCC", "rail": "logic", "direction": "in"}, {"pin": "GND", "rail": "ground", "direction": "in"}],
 "unused_pins": [], "pin_order": ["GND", "VCC", "Signal"],
 "body_mm": {"width": 10, "height": 6, "verified": false, "source": "measured with a ruler", "why_it_matters": "where the socket sits"}}
```

That store's drawer held only the FireBeetle, and its project two needs, in `../needs.json`: the plant alarm's soil
need without its condition, and the board.

```json
[
  {"id": "soil", "does": "sense", "what": "soil-moisture"},
  {"id": "board", "does": "compute", "what": "microcontroller"}
]
```

`--match .` then offered the record, which owed three facts:

<!-- output: run 2026-10-08, spark 0.7.0 -->
```text
  soil — sense / soil-moisture
                 soil-probe (catalog)                           soil-moisture  owes footprint, pin_order_proof, simulation
                 vl6180x-breakout (library)                     distance [other words]
  board — compute / microcontroller
      owned 1    firebeetle2-esp32s3 (library)                  microcontroller  free 1
                 xiao-esp32-c6 (library)                        microcontroller  stops at the footprint stage (P121)
```

What happens today depends on what is owed. `--pick` takes the record either way; `--requirements` decides.

**A fact the circuit needs** — `footprint`, `pin_order`, `pin_order_proof` or `simulation` — stops the building list.
The soil probe was picked with the board (`--pick . soil=soil-probe board=firebeetle2-esp32s3`), and then:

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --requirements .
```

<!-- output: run 2026-10-08, spark 0.7.0 -->
```text
  refused, so nothing was written: soil-probe — owes footprint, pin_order_proof, simulation — fill it in its own home with --fact-set
```

It exits 1. **Only the outline** (`body_mm`) does not stop it. In another store, the same record carrying the three
facts of `../facts.json` (below) and no `body_mm`, picked the same way, goes into the file with a warning:

<!-- output: run 2026-10-08, spark 0.7.0 -->
```text
  wrote requirements.json: board firebeetle2-esp32s3; parts soil-probe
  onto the shelf, so every project builds with it: soil-probe
  placeholder outline — soil-probe owes body_mm, so the PCB step lays it out at a placeholder 16 x 12 mm: a dimension drawing (fetched after the person's yes) or a measurement fills it — fill it in its own home with --fact-set
```

**Filling one.** An owed fact is filled once, in the record's own home: here the catalog record in the store. In
Claude Code, `/spark:idea` does it with you: Claude writes the facts from the record's source as a JSON object to a
file, then runs `--fact-set`, first with `--dry-run`. A source not kept yet is fetched only after your yes. The soil
probe's three, in `../facts.json`:

```json
{"footprint": "jst_ph_3",
 "pin_order_proof": {"verified": false, "source": "read off the cable: GND, VCC, Signal"},
 "simulation": {"skip": "no Wokwi part for a soil probe"}}
```

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --fact-set soil-probe ../facts.json --project .
```

<!-- output: run 2026-10-08, spark 0.7.0 -->
```text
  set soil-probe (<store>/catalog/soil-probe.json): footprint null → "jst_ph_3"; pin_order_proof null → {"verified": false, "source": "read off the cable: GND, VCC, Signal"}; simulation null → {"skip": "no Wokwi part for a soil probe"}
```

Then `--requirements` wrote the file and put the record on the shelf:

<!-- output: run 2026-10-08, spark 0.7.0 -->
```text
  wrote requirements.json: board firebeetle2-esp32s3; parts soil-probe
  onto the shelf, so every project builds with it: soil-probe
```

`--fact-set` never changes spark's own library: a library record is changed in spark's repository.

**A bench result goes back the same way.** The probe's outline was a guess from a ruler. In a store where the record
carries the three facts of `../facts.json`, `--unverified` lists it beside the pin order, and says what to do next:

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --unverified soil-probe
```

<!-- output: run 2026-10-29, spark 0.9.0 -->
```text
  2 thing(s) nobody has checked:

  soil-probe.pin_order = ['GND', 'VCC', 'Signal']
      a pin order read wrong reverses a supply or swaps a signal
  soil-probe.body_mm = {'width': 10, 'height': 6}
      where the socket sits
  next: parts.py --fact-set soil-probe <file> — write a checked result back with its source
```

With `--json`, each row of `assumptions` also carries `write`, the key its result goes back to (`body_mm` here). After you
measure the probe with a caliper, the file holds the result with its source: who, when and how.

```json
{"body_mm": {"width": 10.4, "height": 6.1, "verified": true, "source": "bench, 2026-10-29, caliper on the owned probe, Petr Smejkal"}}
```

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --fact-set soil-probe ../bench.json --dry-run
```

<!-- output: run 2026-10-29, spark 0.9.0 -->
```text
  would set soil-probe (<store>/catalog/soil-probe.json): body_mm {"width": 10, "height": 6, "verified": false, "source": "measured with a ruler", "why_it_matters": "where the socket sits"} → {"width": 10.4, "height": 6.1, "verified": true, "source": "bench, 2026-10-29, caliper on the owned probe, Petr Smejkal"}
```

Without `--dry-run` it writes, and `--unverified` then lists the pin order only. A `facts` entry goes back the same way,
by name: `{"facts": {"runs_at_3v3": {"value": true, "verified": true, "source": "…"}}}` keeps the other entries. A write
replaces the whole block, so the file holds what the block should keep (`note`, `where`).

**What follows a gap.** A need marked `gap` has nothing in the store to pick. Left unpicked, it does not stop the
building list, and `--requirements` says so. In a store of its own, the plant alarm with soil marked `gap`, the
library's LED picked for the alarm and the FireBeetle for the board (`--pick . alarm=led-red-5mm board=firebeetle2-esp32s3`):

<!-- output: run 2026-10-08, spark 0.7.0 -->
```text
  wrote requirements.json: board firebeetle2-esp32s3; parts led-red-5mm
  not on the board: soil — marked a gap: nothing like it is in the store yet; research it before it can be built
```

The board, unlike the other needs, cannot be left unpicked: without it `--requirements` refuses, `board — pick one
board — none is picked`. The file keeps that note under `unserved`, and the build's verdict repeats it:
`the chain runs end to end — but not every need is on the board: soil (a gap)`. [Research](research.md#research) comes next:
`/spark:research` writes a new record into the project's `parts/`. A new record can still owe facts;
`parts.py --audit --project .` names them, and `--fact-set` fills them as above. Then pick it for the need and run
`--requirements` again, and the note goes.
