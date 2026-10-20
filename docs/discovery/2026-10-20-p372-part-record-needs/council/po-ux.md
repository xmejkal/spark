# P372 council: PO-assistant lens with UX and AI-UX

> **TL;DR.** "Usable" has two levels, and today spark shows neither. **Minimal** (the PO: "even possible to use it in
> spark to make things"): spark can place the part, wire it and build a board from it, and every fact it relies on is
> either cited or marked unverified. **Fully usable**: the same part also simulates, passes the checks with no open
> fact, has a picture and a symbol, and has been tried on the bench. The joystick is at minimal today, and one step
> short of that for the game walk only by its unverified bench facts. Proposal: one line for the person
> ("joystick-module-mh: minimal, 9 facts open, no picture"), one field for Claude (`usable`). The PO decides five
> questions, listed last.

## Sources read

- Issue [#477](https://github.com/xmejkal/spark/issues/477) with the PO's words, and the walk cards
  [#466](https://github.com/xmejkal/spark/issues/466) (P364 game walk), [#472](https://github.com/xmejkal/spark/issues/472)
  (P370 picture and symbol) and [#6](https://github.com/xmejkal/spark/issues/6) (P100 walk 1).
- `docs/observations/rows/p366-photo-walk.md` (16 rows) and the record `joystick-module-mh` in the PO's shelf.
- `docs/guide/agents.md`, sections on `parts.py` and "The outcomes and their exit codes".
- I ran `parts.py --validate` and `parts.py --unverified joystick-module-mh --json` (see the next section).

## What a person and Claude see today

| | person | Claude |
|---|---|---|
| `--validate` | one line per record: `joystick-module-mh ok` | `status`, exit 0 ok or 1 problems |
| `--unverified P` | the open facts, one assumption each | `assumptions[]`: `fact`, `basis`, `assumed`, `sentence`, `source` |
| `--show P` | the record, CONFLICT lines | `data.record`, a CONFLICT is a problem only on a verified fact |
| picture, symbol, bench | nothing | nothing |

Three gaps follow from this table:

1. `ok` means "the record obeys the contract". The PO reads it as "I can use this". The joystick says `ok` with 9
   open facts, no part picture and no bench trial. One word carries two meanings.
2. `--unverified` lists facts, not what they block. The person sees 9 rows and cannot tell which 2 stop the game walk
   and which 7 are only worth a meter reading. Row 14 of the walk adds a miss: the body size 34 x 26 mm is a guess
   that the list does not show.
3. Claude gets `status: ok` and a list. It must decide alone whether to go on. A `null` such as
   `axis_assignment.assumed` is correctly not a value, but nothing tells Claude "firmware can still start".

## Two levels, in the PO's words

The PO asked for "minimal info for it to be even possible to use it in spark to make things" and "fully usable".
I read the first as a floor that opens the door and the second as a record nobody needs to touch again for this part.

| level | the test | what the record holds |
|---|---|---|
| **minimal** | spark can place it, wire it and build a board from it, and nothing in it is a silent guess | identity and kind, pins with an order and a proof of the order, the power it needs and gives, the host's duties (pull-up, rail, ADC type), a footprint and legs for the sheet, a source or an `unverified` mark on every fact |
| **fully usable** | the whole chain runs and the bench agrees | minimal, plus a simulation stand-in, a part picture and a symbol, a body size read with a ruler, no open fact that a check or a stage relies on, and one bench trial logged |

The same two levels apply to all three:

- **Part** (an LED, a button): minimal is the datasheet facts the checks read. Fully usable adds the picture and a
  stand-in. Few facts are open because a datasheet exists.
- **Module** (the joystick): minimal is the pin order, the supply and the host duties. Most facts are inferred from a
  look-alike, so "fully usable" needs the bench. This is where the two levels differ most.
- **Board** (the XIAO ESP32-C6): minimal adds the pin capabilities that `assign_pins.py` reads, such as which pins are
  ADC1. Fully usable adds a flash and look trial on the bench.

## The joystick against the game walk (P364, #466)

The walk adds one analog joystick to an existing game and then offers the DFR0954 sound module. What it reads:

| stage | reads from the record | joystick holds it? |
|---|---|---|
| idea and drawer match | `kind`, `also_known_as`, `needs` | yes |
| pin map (`assign_pins`) | `needs` as signals: two analog in, one digital in with pull-up | yes, but the "ADC1 only, 11 dB" rule sits in `host_requirements` as text |
| power and physics checks | `power`, `runs_at_3v3`, `supply_current_ma` | yes, all three unverified |
| board and sheet (breadboard) | `pin_order`, `legs`, `footprint`, `body_mm` | yes, but `body_mm` is a guess |
| simulation | `simulation.wokwi` stand-in | yes, mapped by name only |
| firmware by the conversation | `host_requirements`, `axis_assignment` | the rules yes, the axis direction `null` |
| bench | `pin_order_proof`, row 15 checks | open, due before the walk (row 15) |
| picture and symbol | none | no, P370 (#472) |

So for P364 the joystick is **minimal and enough to start**. Three things block "done" in the walk, not the start:

- the pin order and `runs_at_3v3` decide whether the PO can wire it without a burnt pin, so the bench check comes first
- the axis direction is a firmware fix after one measurement, so it does not block the sheet
- the picture is a P370 matter, so the P364 sheet draws a generic box until then

Each gap comes from the photo-only route: a chipless module has no datasheet, so every fact rests on a look-alike
maker's manual or a computed value.

## What spark says about a level

For a person, one line under the `--validate` row and at the top of `--unverified`:

```
joystick-module-mh: minimal. Open: 9 facts, 3 stop wiring (pin order, 3.3 V, SW pull-up). Missing: picture, symbol, bench trial.
```

For Claude, one new field in the `parts.py` envelope `data`, per record:

```json
"usable": { "level": "minimal", "blocks": ["pin_order", "runs_at_3v3"], "missing": ["picture", "bench"] }
```

- `level` is one of `incomplete`, `minimal`, `full`. A constant, so Claude never compares English text.
- `blocks` lists open facts that a named stage relies on. `missing` lists artifacts, not facts.
- The exit code does not change. `usable` is a fact about the record and `status` stays the contract's verdict.
  An agent never reads `level: minimal` as a pass of the chain.
- The words come from the PO: "minimal" and "full". I avoid a coined scale such as tiers or grades.

## What the PO must decide

One question at a time. Each has an example.

1. **Does "minimal" allow an unverified pin order?** Example: the joystick pins are read from a photo and from
   Joy-IT's manual, and a wrong order burns a pin. Choice A: minimal needs the order verified on the bench. Choice B:
   unverified is minimal, and the sheet carries a "check with a meter first" step.
2. **Is a picture part of "fully usable"?** Example: without P370's picture the breadboard sheet draws a generic box.
   Does the joystick count as full with a box, or only with its own picture?
3. **Who sets the level?** Example: after you measure the pot at 10 kOhm, does the record move itself to the next
   level when the last blocking fact is verified (derived), or does someone write it by hand?
4. **Do you want the level on every `--validate` line?** Example: `led-red-5mm ok, full` beside
   `joystick-module-mh ok, minimal`. It adds a word to each line, so say yes or keep it only in `--unverified`.
5. **Is the bench trial per part or per project?** Example: one trial of the joystick in the game also lifts the
   joystick for the next project, or each project repeats it?

Not decided here: the type hierarchy against traits question (item 4 of the spike) belongs to the architect lens. From the UX side I
ask only that a trait such as "has a button" be shown to the person as a plain word, and be a constant for Claude.
