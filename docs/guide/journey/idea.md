## Idea

**Partly.** [`/spark:idea`](../../../commands/idea.md) turns a goal in your words into needs, then matches each need
against your drawer and spark's records. It marks each need: have, have-unknown, know or gap. Then a part is picked per
need (`parts.py --pick`), what you own is reserved, and the picks become a requirements file
(`parts.py --requirements`) ([P97](https://github.com/xmejkal/spark/issues/18)). Those steps ran for this page, in
[a recorded run](recorded-run.md#a-recorded-run-a-button-and-an-led) below; the conversation did not.

**Today, in full.** If the board serves every need, the requirements file says `board_only`
([P387](https://github.com/xmejkal/spark/issues/497)). A board offers its own LED, buttons, display, charger, regulator, battery input and battery-level pin
for a need ([P389](https://github.com/xmejkal/spark/issues/504)). If a simulation cannot press or show that part, the pick says so. It names the bench as
the test. If you own another choice, it names that too ([P397](https://github.com/xmejkal/spark/issues/513)). The recorded run went on from the requirements file to a board that builds and
to the tally. With no Claude Code transcript there, the tally did not count the cost.

In Claude Code, Claude asks at most three questions, one at a time, then writes the needs to a file:

- each need is a verb and a few words;
- no part numbers;
- a `condition` only when it decides a part.

For *"tell me when my plant is thirsty"*:

```json
[
  {"id": "soil", "does": "sense", "what": "soil-moisture", "condition": "indoor pot, short probe; low power"},
  {"id": "alarm", "does": "indicate", "what": "alarm"},
  {"id": "board", "does": "compute", "what": "microcontroller"}
]
```

The conversation was not run for this page. These needs were written by hand from `/spark:idea`'s own example; the
commands below are real runs.

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --needs-set . ../needs.json
```

<!-- output: run 2026-10-08, spark 0.7.0 -->
```text
  set soil: does null → "sense"; what null → "soil-moisture"; condition null → "indoor pot, short probe; low power"
  set alarm: does null → "indicate"; what null → "alarm"
  set board: does null → "compute"; what null → "microcontroller"
```

The same command with `--dry-run` first shows these lines as *would set*. `null →` means the field had no value
before. Every field of a new need shows it, as here. A write to a need that is already there shows only the fields it
changes, each with what it held: a mark given later reads `mark null → "know"`. The needs land in
`.spark/needs.json`.

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --match .
```

<!-- output: run 2026-10-08, spark 0.7.0 -->
```text
  soil — sense / soil-moisture  (indoor pot, short probe; low power)
                 vl6180x-breakout (library)                     distance [other words]
  alarm — indicate / alarm
      owned 10   red-leds-pack-of-10 (drawer)                   light [other words]  free 10
                 led-red-5mm (library)                          light [other words]
  board — compute / microcontroller
      owned 1    firebeetle2-esp32s3 (library)                  microcontroller  free 1
                 xiao-esp32-c6 (library)                        microcontroller  stops at the footprint stage (P121)
```

How to read the matches:

- Owned parts come first, from the drawer above, with how many are free.
- `owes` names facts a [record](../../../GLOSSARY.md#record--and-the-four-places-one-lives) lacks
  ([owed facts and gaps](owed-facts.md#owed-facts-and-gaps) shows one):
  - a pick owing a `footprint`, a `pin_order`, its `pin_order_proof` or a `simulation` stance is taken, but
    `parts.py --requirements` writes nothing until that is filled (it says which, and how);
  - one owing only an outline (`body_mm`) is written, and `/spark:build` draws a declared placeholder size, every stage
    still reading `[ok]` ([P115](https://github.com/xmejkal/spark/issues/49)).
- `[other words]` marks a looser match: the part does the same thing (*sense*, *indicate*) but names a different object
  (*distance*, *light*). Whether that fits is Claude's call, and Claude says so to you.
- A candidate with an `about` line shows it under its row. With `--json`, each candidate has a `score` from 0 to 1 and a
  `why`. `--matcher word-overlap` ranks by shared words, tags and descriptions, and `same-words` stays the default.
- `stops at the footprint stage (P121)` marks a board whose board file lacks a fact its footprint is drawn from, and the
  rest of the line names it (`its board file lacks physical.header`; with more, `lacks 3 fields (first: …)`; `--json`
  has the whole list as `stops_why`): the chain stops at its footprint stage ([P121](https://github.com/xmejkal/spark/issues/55)). Both library boards build today (the XIAO since
  [P278](https://github.com/xmejkal/spark/issues/314)); the lines above are a dated record from when it did not.

Here a distance sensor is offered for soil moisture. It senses distance, not moisture, so soil moisture is a real gap.
Research is for that; [owed facts and gaps](owed-facts.md#owed-facts-and-gaps) says what a gap leaves off the board until then.
