### A recorded run: a button and an LED

A smaller project, `button-light` — a button and a light on a board — went through every step `/spark:idea` walks,
with `/spark:build` before the tally. It ran on 2026-10-08 in the same scratch store as the runs above, so the drawer
holds the FireBeetle and the LED pack. The conversation was not run: the needs, the marks and the reason were written
to files by hand, and every command below is a real run.

These commands ran from a recording script, not through `/spark:idea` in Claude Code, so the session id that `--step`
records was set by hand: `CLAUDE_CODE_SESSION_ID=demo-session`. When Claude runs them in Claude Code, that variable is
already set.

**S — the needs.** Each step is marked when it starts, so the tally can count it:

```sh
CLAUDE_CODE_SESSION_ID=demo-session python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --step . S
```

<!-- output: run 2026-10-08, spark 0.7.0 -->
```text
  started step S of button-light — a line in your history, with this Claude Code session's id
  listed button-light on your projects
```

M, C and L were marked the same way as each began, and printed the first line only. The needs, in
`../button-needs.json`:

```json
[
  {"id": "press", "does": "input", "what": "button"},
  {"id": "light", "does": "indicate", "what": "light"},
  {"id": "board", "does": "compute", "what": "microcontroller"}
]
```

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --needs-set . ../button-needs.json
```

<!-- output: run 2026-10-08, spark 0.7.0 -->
```text
  set press: does null → "input"; what null → "button"
  set light: does null → "indicate"; what null → "light"
  set board: does null → "compute"; what null → "microcontroller"
```

**M — the matches, then the marks.**

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --match .
```

<!-- output: run 2026-10-08, spark 0.7.0 -->
```text
  press — input / button
                 tactile-button (library)                       button
  light — indicate / light
      owned 10   red-leds-pack-of-10 (drawer)                   light  free 10
                 led-red-5mm (library)                          light
  board — compute / microcontroller
      owned 1    firebeetle2-esp32s3 (library)                  microcontroller  free 1
                 xiao-esp32-c6 (library)                        microcontroller  stops at the footprint stage (P121)
```

This output is from 2026-10-08. On 2026-11-01 the same match lists the XIAO ESP32-C6 as a `microcontroller`
with no stop. It builds since [P278](https://github.com/xmejkal/spark/issues/314). That run
also offers each board's own button and LED for the press and light needs
([P389](https://github.com/xmejkal/spark/issues/504)).

The LED pack is owned but has no record: picked as it is, spark reserves it and cannot place it on the board.
`/spark:idea`'s M step asks whether the pack is `led-red-5mm`. On the person's word, `--drawer-set` with
`[{"entry": "red-leds-pack-of-10", "is": {"part": "led-red-5mm"}}]` links it, after a dry run. `--match` then lists the
LED as `led-red-5mm (library)`, owned 10 and free 10, and the same pick below reserves the pack and places the LED; the
tally counts 2 owned. This run did not link it, so the library's LED is "to get" and the pack is passed over in C. The
button and that LED are known, not owned (`know`); the board is owned, with a record (`have`). The marks, in
`../marks.json`:

```json
[{"id": "press", "mark": "know"}, {"id": "light", "mark": "know"}, {"id": "board", "mark": "have"}]
```

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --needs-set . ../marks.json
```

<!-- output: run 2026-10-08, spark 0.7.0 -->
```text
  set press: mark null → "know"
  set light: mark null → "know"
  set board: mark null → "have"
```

**C — the picks.** The reason for passing over the LED pack, in `../passed.json`:

```json
[{"need": "light", "id": "red-leds-pack-of-10", "why": "no record for them, so spark cannot place them on the board", "by": "person"}]
```

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --pick . press=tactile-button light=led-red-5mm board=firebeetle2-esp32s3 --passed-over ../passed.json
```

<!-- output: run 2026-10-08, spark 0.7.0 -->
```text
  set firebeetle-2-esp32-s3: used_in null → {"button-light": 1}
  press: tactile-button
  light: led-red-5mm
  board: firebeetle2-esp32s3
  led-red-5mm: to get — known, not owned
  tactile-button: to get — known, not owned
  wrote to your history: 3 reused
  noted why you passed over red-leds-pack-of-10 (light)
```

With `--dry-run` first, the same lines read *would set*, *would write* and *would note*. The picks are in the
project's `.spark/needs.json`; the reason is in the history in your store, never in the project. The FireBeetle's
drawer entry is now held for `button-light`, so another project's pick of it is refused. From `plant-alarm`'s folder,
in the same store:

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --pick . board=firebeetle2-esp32s3 --dry-run
```

<!-- output: run 2026-10-11, spark 0.8.1 -->
```text
  refused, so nothing was written: firebeetle2-esp32s3 — 1 owned, held by button-light — 1 picked here
  fix for firebeetle2-esp32s3: free it — a file holding [{"entry": "firebeetle-2-esp32-s3", "used_in": …}] without button-light, given to --drawer-set <file> after a dry run — or pick another
```

**L — the requirements file.** First `/spark:init --board firebeetle2-esp32s3` in the project, as in
[Build](build.md#build); it printed the same lines as there, with this project's name. Then:

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --requirements .
```

<!-- output: run 2026-10-08, spark 0.7.0 -->
```text
  wrote requirements.json: board firebeetle2-esp32s3; parts tactile-button, led-red-5mm
```

With `--dry-run` first it says *would write*. The file it wrote:

```json
{
  "board": "firebeetle2-esp32s3",
  "parts": [
    "tactile-button",
    "led-red-5mm"
  ]
}
```

**The build.** [`/spark:build`](../../../commands/build.md) runs the chain on it, as in [Build](build.md#build):

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/check_spine.py" requirements.json --keep .
```

The lines are a dated record. Since 2026-10-12 the button uses the board's internal pull-up
([P204](https://github.com/xmejkal/spark/issues/167)), so today's run writes 9 traces, routes 7 and wires 7.

<!-- output: run 2026-10-11, spark 0.8.1 -->
```text
wrote <temp>/FireBeetle2Esp32S3.tsx (32 pads, 1.00 mm holes)
  wrote FireBeetle2Esp32S3.tsx
  wrote board.tsx
  wrote dist — this is what every check reads
  wrote breadboard.md — the parts and how to wire them on a breadboard

  idea -> parts -> pin map -> schematic -> footprint -> build -> simulation

  [ok  ] board            DFRobot FireBeetle 2 ESP32-S3
  [ok  ] schematic        11 trace(s) written
  [ok  ] footprint        FireBeetle2Esp32S3.tsx
  [ok  ] build            9 trace(s), 0 errors, tsci 0.0.2621; the documents were measured on core 0.0.2600
  [ok  ] simulation       9 wire(s) in the diagram
           what it cannot show, from the records (2):
             LedRed5mm: Wokwi's LED: lights on current; its forward voltage and brightness are not this part's
             TactileButton: Wokwi's pushbutton: either side of a pair is the same contact; no bounce is modelled

  the chain runs end to end
```

This build used tscircuit 0.0.2621, an existing install on the PATH, not the 0.0.2600 spark pins: the build line says
so, and does not fail for it.

**The breadboard.** With `--keep`, the build also writes `breadboard.md` into the project
([P191](https://github.com/xmejkal/spark/issues/143)): the parts, the resistors the parts ask for, and every wire,
named by the board's printed labels and the parts' legs. It comes from the circuit that was built, so it is the board
the checks and the simulation saw. The FireBeetle reads *yours* because the drawer holds it for this project:

The lines are a dated record. Since 2026-10-12 the button uses the board's internal pull-up
([P204](https://github.com/xmejkal/spark/issues/167)): today's sheet has no 10kΩ resistor and no 3V3 line, the LED's
resistor is R1, and `pins.py` says `BUTTON_PULL = "up"`.

<!-- output: run 2026-10-11, spark 0.8.1 -->
```text
# Breadboard: button-light, on a DFRobot FireBeetle 2 ESP32-S3

## Parts

| qty | part | for | have |
| --- | --- | --- | --- |
| 1 | DFRobot FireBeetle 2 ESP32-S3 | the board | yours |
| 1 | 6x6 mm tactile push button | TactileButton | to get |
| 1 | Kingbright L-7113ID 5 mm red LED | LedRed5mm | to get |
| 1 | 10kΩ resistor, through-hole | R1 pull-up on TactileButton A | to get |
| 1 | 330Ω resistor, through-hole | R2 in series with LedRed5mm A | to get |
| | a breadboard and jumper wires | | to get |

*have*: yours = your drawer holds it for this project · in your drawer = you own it, not held here · to get = not in your drawer · blank = this project is not on your list (`/spark:init` puts it there)

## Wiring

Each line is one point: put its ends in one breadboard row, or join them with a wire. The board covers the
rows beside its own pins, so for a line that starts with a board pin, run a jumper from that pin to a free
row and put the line's other ends in that row.

1. board 3V3 · R1 (10kΩ pull-up on TactileButton A), end 2
2. board A5 · R2 (330Ω in series with LedRed5mm A), end 1
3. board D3 · R1 (10kΩ pull-up on TactileButton A), end 1 · TactileButton A (either leg of one joined pair; a meter on continuity shows which legs are joined)
4. board GND · LedRed5mm K (the cathode, the shorter leg, by the flat of the rim) · TactileButton B (either leg of the other pair)
5. LedRed5mm A (the anode, the longer leg) · R2 (330Ω in series with LedRed5mm A), end 2

## Before you power it

- 6x6 mm tactile push button: Decide the polarity against deep sleep, not convenience. MicroPython's esp32.wake_on_ext1(pins, level) takes ONE level for every pin in the mask, on every chip (ports/esp32/modesp32.c, v1.29.0), so a board with two wake sources must have them assert in the same direction. Both directions are an OR on the S3 and C6: WAKEUP_ALL_LOW is a true AND only on the original ESP32, and ESP-IDF aliases it to ANY_LOW on every later chip (components/esp_hw_support/include/esp_sleep.h, v5.5.2). Prefer wiring a wake button to 3V3 behind a pull-down and arming WAKEUP_ANY_HIGH: low-level wake has an open MicroPython bug, micropython#17334 ('stuck pin', reported on a C6, v1.25.0). Corrected 2026-10-01 (spark P63): this line used to say ALL_LOW is an AND here, which is false on these chips.
- 6x6 mm tactile push button: Debounce in firmware, not hardware, unless the button is also a wake source — a wake pin's first edge is the one that matters and it is not debounced by anything.
- Kingbright L-7113ID 5 mm red LED: A series resistor between the GPIO and the anode, always: without it the LED's current is set only by the pin's drive strength, and it either runs far past 30 mA or droops the pin's level.
- Kingbright L-7113ID 5 mm red LED: Keep it off the chip's strapping pins: an LED and resistor to ground load the pin while the chip samples its straps at reset, and can change how it boots. (Reasoned from the circuit, not from this datasheet.)
- Kingbright L-7113ID 5 mm red LED: On a breadboard: the LONG lead (anode) goes to the resistor; the short lead, on the side of the flat in the rim, goes to ground. Once the leads are trimmed equal, the flat is the mark that survives.

Each record whole, with what it asks of the board: `parts.py --show led-red-5mm`, `parts.py --show tactile-button`.
```

`python3 "$CLAUDE_PLUGIN_ROOT/scripts/breadboard.py" requirements.json` writes it again after a build.

Since 2026-10-16 the Wiring section has three parts ([P202](https://github.com/xmejkal/spark/issues/161)). The lines
above are now its last part, the points, a check list after the wiring. Before them come numbered steps, one
connection each, and a mermaid diagram whose numbered lines are those steps. The board and each part go in first,
each pin in its own row. Then each wire goes to its point's anchor, the row or rail where its ends meet: a part's pin row, else a resistor end's row, or a
rail when a point has more ends than a row holds. Today's steps for this project:

<!-- output: run 2026-10-16, spark 0.9.0 -->
```text
1. Put the board in the breadboard, each pin in its own row.
2. Put TactileButton in the breadboard, each pin in its own row.
3. Put LedRed5mm in the breadboard, each pin in its own row.
4. Put R1 (330Ω in series with LedRed5mm A), end 1, in a free row.
5. Run a jumper from board A5 to the row of R1 end 1.
6. Run a jumper from board D3 to the row of TactileButton A.
7. Run a jumper from board GND to the row of LedRed5mm K.
8. Run a jumper from the row of TactileButton B (either leg of the other pair) to the row of LedRed5mm K.
9. Put R1 (330Ω in series with LedRed5mm A), end 2, in the row of LedRed5mm A.
```

**The drawn breadboard.** Since 2026-10-16 the build also writes `breadboard.json` beside the sheet
([P267](https://github.com/xmejkal/spark/issues/300)). It is a Wokwi diagram of the same steps on a half breadboard:
each part's legs in holes, and each jumper in its step's color. The sheet names the colors under its steps. To see
it, open a new project on wokwi.com, paste the file into its `diagram.json`, and compare the picture with your own
breadboard. Since 2026-10-17 a part you move in the file stays where you put it at the next build
([P273](https://github.com/xmejkal/spark/issues/309)), even after you change the requirements, if it still fits. A
part that cannot stay is named on the screen, with why: for example `LedRed5mm: its pin A is not over a hole`, or
`LedRed5mm: it is not in the new circuit`. Its jumpers follow it, so the diagram stays wired. A resistor you move
stays if its joined leg is still in the row it joins, and a jumper you move stays, with its bends, if the new circuit
still joins the two rows it joins (since 2026-10-18, [P287](https://github.com/xmejkal/spark/issues/340)); otherwise
the screen names it, for example `jumper 6b.j-15t.a: …`. A build that fails leaves the file, with your moves, and says so.

**A rebuild says what to change.** Since 2026-10-18 ([P300](https://github.com/xmejkal/spark/issues/366)) a rebuild
tells you what to change on your breadboard, so you do not read the whole sheet again. Say you built the button and the
LED, wired them, and then add a second LED. The sheet gets this section before its steps, and the screen prints the same
lines:

<!-- output: run 2026-10-18, spark 0.9.0 -->
```text
### Changes since the last build

- Put LedGreen5mm in the breadboard.
- Put R2 end 1 (in series with LedGreen5mm A) in a free row.
- Run a jumper from board D9 to the row of R2 end 1 (in series with LedGreen5mm A).
- Run a gold jumper from the row of LedRed5mm K to the row of LedGreen5mm K.
- Put R2 end 2 (in series with LedGreen5mm A) in the row of LedGreen5mm A.
- Move the purple jumper from board GND: it now goes to the row of LedGreen5mm K (it went to the row of LedRed5mm K).
- Move the magenta jumper from the row of TactileButton B: it now goes to the row of LedGreen5mm K (it went to the row of LedRed5mm K).
```

A line names a jumper by its two ends. A jumper you move or take out has the color on your earlier sheet, so you can find
the wire you wired. A new jumper has the color it has on the new sheet, unless a jumper in the same list had that color
on your bench. Then it has no color, so no two wires in the list share one. A resistor is named by its job too, because
its tag can renumber. A line never names a hole, because you pick your own free rows. A resistor with a new value reads
`Swap R1, 330Ω, for a 1kΩ resistor in the same rows.` A resistor that goes is one line:
`Take out R1, 330Ω in series with LedRed5mm A.` When nothing changed, the section says
`- Nothing to change on the bench.` The first build has no section. Spark keeps what the last sheet said in
`wiring-record.json`, beside the sheet. Do not edit it.

Two boards are drawn, and only when no point needs a rail or a supply from off the board. The Seeed Studio XIAO ESP32-C6
is drawn from what spark measured in Wokwi (`data/wokwi-geometry.json`). The FireBeetle 2 ESP32-S3 is drawn from its own
record ([P412](https://github.com/xmejkal/spark/issues/538)) on a 63-column breadboard: `breadboard.svg` shows each
pad's label beside its pin, rings the two ground pads the record doubts and marks the USB end. Three things are not
verified: the pads, the side of the row, and the USB end. The sheet says so and tells you to hold your board to the
picture. Wokwi has no part with its pins, so for the FireBeetle the sheet says `There is no Wokwi diagram for this board.`
It also names the ground pad (GND2). A board whose record lacks a fact says which one.
The same project on the XIAO, as Wokwi shows its `breadboard.json`
([the measurement](../../discovery/2026-10-16-p267-wokwi-holes/README.md)):

![The button-and-LED project on a XIAO ESP32-C6, drawn on a Wokwi half breadboard](../../discovery/2026-10-16-p267-wokwi-holes/button-light-xiao.png)

Since 2026-10-16 the sheet also shows the layout itself, so you need no website to see it
([P268](https://github.com/xmejkal/spark/issues/302)). The build writes `breadboard.svg` beside the sheet, and
`breadboard.md` shows it under the steps. Each part is a plain pictogram of its kind, and each jumper runs along the
holes in its step's color, with its step number at the corner. Pictures from online come later. The same project:

![The button-and-LED project as the sheet shows it](../img/button-light-xiao-breadboard.svg)

**The drawing is checked.** Since 2026-10-18 ([P279](https://github.com/xmejkal/spark/issues/317)) the build makes
sure that the drawing joins the same pins as the points in `circuit.json`. It follows each jumper and the button's two
sides of one contact. When they match, it says nothing. When an end differs, the screen prints one line for it, for
example `drawing differs: R1 end 1 is not joined to board D8 in the drawing`, and the sheet tells you to wire from
its steps. A jumper from GND to the 5V pad is named too, because no point names 5V. The drawing is still written.

Since 2026-10-16 the build also writes `page.html`, the same circuit in three tabs: the breadboard, the schematic
and the PCB ([P271](https://github.com/xmejkal/spark/issues/307)). Open it in a browser on your Mac and click a tab.
The schematic and the PCB are tscircuit's own pictures, from `tsci export` on the kept circuit. Since 2026-10-17 the page
also follows the Artifact page rules ([P272](https://github.com/xmejkal/spark/issues/308)): colors are tokens with a
dark mode that follows your system, the side gutter is 16 px, and the title is the first three words of the folder's name and "circuit". Claude can
publish the same file as a private Artifact when you say yes. The PCB tab of the
same project:

![The PCB tab of page.html for the button-and-LED project](../../discovery/2026-10-16-p271-page/tab-pcb.jpg)

**T — the tally.**

```sh
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parts.py" --tally .
```

<!-- output: run 2026-10-08, spark 0.7.0 -->
```text
  3 picks: 3 from the store (1 owned) — its cost was not counted
  3 of 3 needs picked
  from the store: known to spark before this project — its library, your store, your projects
  --tally reads the Claude Code transcripts of the sessions the steps ran in, for tool names and counts only
  no transcript of session demo-session here, so the cost of its steps is not known
```

All three picks were known to spark before this project, and one of them, the FireBeetle, is owned. The cost could
not be counted, and the tally exits 2, could-not-run: it looks for each step's session among the Claude Code
transcripts under the home folder (`~/.claude/projects`), and this run's home folder was the scratch store, which
holds none. A missing transcript is never counted as a cost of 0.

In Claude Code the line ends with the cost instead. A run by spark's author on 2026-10-08, in Claude Code and not
recorded for this page, printed `4 picks: 4 from the store (4 owned) — 2 requests, 1 document, 12 min`. Its words, as
spark's code defines them:

- **from the store**: known to spark before this project — its library, your store, your projects;
- **owned**: your drawer holds it;
- **requests**: tool calls that reach the network, every MCP call among them;
- **documents**: the PDFs and images read (`.pdf`, `.png`, `.jpg`, `.jpeg`, `.webp`, `.svg`), with the Read tool or
  `parts.py --read`, each counted once;
- **min**: wall-clock minutes of the session between the steps.

The run left nine lines in the store's history, `history.jsonl` ([your store](../how-it-works.md#your-store)): a `step`
line for each of S, M, C and L, with the session id; a `reused` line for each pick; the reason for passing over the
LED pack; and a `built` line, written by the green build.
