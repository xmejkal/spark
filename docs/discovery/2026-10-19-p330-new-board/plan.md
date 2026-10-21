# A new board, smoothly: the plan after the T-Display walk (P330)

> Today a new board takes 11 steps by hand, and an owned board works in one project only. Ten changes fix that. Six
> come first, because the next demo needs them: an animation on the T-Display's screen, which the PO leads from his
> own idea. Each change is a small class or function where the code already lives, so none waits for v0.13 (#94).
> A guide command then leads a person through adding a board, one step and one check at a time.

## Where this comes from

The walk of 2026-10-19 added the PO's LILYGO TTGO T-Display (V1.1, original ESP32) to spark. It left 31 rows in
[`p330-board-walk.md`](../../observations/rows/p330-board-walk.md). The PO, after the walk: *"we'll need to go further
next time. So lets now gather the notes and lets evaluate it and have the council make a plan on what to fix or add or
change, so that it really all works nicely and seamlessly when a new board is being introduced. I'd like to see some
animation on the display in the next demo."* Three lenses read the rows (Sonnet): the PO's assistant with UX and
AI-UX, the architect and tech lead, and a firmware and display lens. Claude merged them and checked the code claims.
One refuter (Opus) then corrected changes 1 to 6: where the role is derived, empty USB serials, the six readers of
the board choice, the offset inside the image and not in the flasher, the driver inside the image, and the gate that
keeps a could-not-run image off the board.

## The journey we want

```
 1 "I have this board"   photo or shop link -> /spark:identify, now also for boards: a guess to confirm
 2 sources               /spark:research keeps the schematic, the maker's pin table, the chip datasheet
 3 the record            boards.py --keep writes it into the store; it says how many facts are unconfirmed
 4 plug in               the look guides: "not found? turn the USB-C plug around, or use USB-A to USB-C"
 5 read the board        one board even with two ports; chip, flash and the firmware on it
 6 buttons               "press the side button": the console shows which one restarts the board
 7 everywhere            boards.py --list in any project shows the boards you own
 8 build and deploy      the image for its chip, at its offset; the display's driver comes with it
```

## The changes

Size: S is under about 50 lines, M is a few hundred. "Demo" marks what the animation needs first.

| # | change | rows | where | size |
|---|---|---|---|---|
| 1 | Demo. The record lists its built-in parts (`onboard_parts`: the display and the buttons, each a part record with its pins). `boards.load` derives a role for their pins into `pin_roles`, because the pin assigner and the live tries read only `pin_roles`, and the role joins `UNAVAILABLE_ROLES` | 6, 27, 30 | `scripts/boards.py` (`PIN_ROLES`, `load`, `validate`), `scripts/assign_pins.py:61` | M |
| 2 | Demo. One board, one port: ports with the same USB serial are one board, but only when the serial is not empty, because some boards report none (`tests/test_look.py:140`). The no-board hint names the USB-C plug's orientation | 19, 20, 21 | `PortFinder` in `scripts/board_look.py:95-106` | S |
| 3 | Demo. One board choice: one helper in `scripts/boards.py` reads `requirements.json`, then `boards/active.json`, and every reader calls it. Six read only `requirements.json` today, and without a board there the image builder takes the S3 image for any board | 17 | `scripts/board_look.py:282`, `scripts/flash_image.py:83`, `scripts/firmware_platform.py:22`, `scripts/boards.py:297`, `scripts/check_spine.py:362`, `scripts/design.py:268` | S |
| 4 | Demo. The original ESP32's image: an `ESP32_GENERIC` entry with its sha256 in the tools list, and the interpreter's offset as a fact per chip (0x1000 on the ESP32). The flasher keeps writing one whole image at 0x0; the image builder pads the interpreter to its offset and counts it in the size check, so Wokwi and the board load the same file | firmware lens | `data/tools.json:150-187`, `scripts/flash_image.py:63-71` | S |
| 5 | Demo. The display's driver reaches the board as a pinned download (URL, commit, sha256, license), fetched into the project's `firmware/` before the image is built, so it travels inside the image like the rest of the firmware. Spark never commits it | firmware lens | the tools list's `download` kind; `scripts/run_scenario.py:149` | M |
| 6 | Demo. A display Wokwi does not model: the simulation says could-not-run, never a pass and never another display in its place. Today an image reaches the board only through a passed run (`scripts/run_scenario.py:149-150` builds it, `scripts/deploy_service.py:90-92` and `scripts/project_image.py:57-69` refuse any other). A bench-only path changes that gate, so it needs its own design and the PO's yes | 29 | the three files named | M |
| 7 | Input-only pins as a chip fact (`input_only_gpio`), so an output never lands on GPIO 34-39 | 5 | `scripts/assign_pins.py:117-135`, `validate` | S |
| 8 | Boards that print bare numbers: the vendor check compares by GPIO when no label matches, and says it did | 14, 28 | `scripts/check_vendor_pins.py:81-98` | M |
| 9 | Honest validation: refuse a null `wokwi_part_type` and an empty `physical`, and count the UNVERIFIED facts beside "ok" | 4, 16 | `scripts/boards.py:353-355` | S |
| 10 | A store place for boards, so an owned board works in every project, then `boards.py --keep` and `/spark:identify` for boards over it | 1, 7, 8, 31 | `scripts/store.py:61-82`, `commands/identify.md` | M |

Not changed: the look's exit code when no build exists yet (row 22) stays 2, and the look prints its verdict on the
fields more plainly. Rows 10, 12, 15, 23, 24 and 26 are observations, kept as written. Reading the firmware already on
a board (row 25) becomes a card.

## A guide that leads

The PO, during the council: *"And it would just generally be really nice if there was a guide. Like the agent, or
claude but that he really leads the user through the process, asks him, recommends checks on progress, etc."*

On this walk, Claude led the PO by hand: one step at a time, one thing for him to do, and a check after each step
(the plug-in, the button presses read on the console). Spark has no such guide. Its commands each do one stage and
expect the person or the agent to know the order. The guide for a new board is a command, for example
`/spark:board`, that walks the journey above. It says where you are ("step 4 of 8"), asks one question or names one
action at a time, runs the check that shows the step worked, and says what is still unconfirmed. Its logic stays in
the scripts (one core, many interfaces): a script reports the journey's state for a board, and the command only
speaks it. The PO said "generally", so the same shape can later lead the other journeys (an idea to a deploy). That
wider guide is one epic with his words, not part of this plan.

The guide comes with change 10, because it leads to a record in the store. The demo walk does not wait for it:
Claude leads that walk by hand again, and its steps become the guide's script.

## Research that keeps looking

The PO, during the council: *"And I'd really like the system to really look well for information and schema and
datasheet and maybe pictures or other data about the new part/board/module, it even asks for more research when it
still needs some more info."*

On this walk, Claude found the maker's repository, schematic, README and the Arduino header, but kept no ESP32
datasheet and no Wokwi page, so ten facts stayed UNVERIFIED (row 15). Nothing in spark noticed that and asked for
more. The guide's research step works from the record's open facts: for each UNVERIFIED or null fact, it names the
kind of source that would settle it (the chip's datasheet, the maker's schematic, the simulator's part page). It
looks there, keeps each source with its checksum, and shows what is still open. When facts stay open, it says which
ones, why they matter, and which source to try next, and asks the person whether to look further. It also keeps
pictures: the maker's pinout image and the person's own photos, in the store and never in the repository. The open
facts already have a reader, `parts.py --unverified`, so the step extends that pattern to boards (change 9). This is
the same need as the parts import of P329 (#421), so the two share one research step.

## The next demo: an animation on the T-Display

The PO leads it from his own idea, as walk 1 does. The smallest first slice: the screen fills with one color, then
switches between two colors every second, and the PO confirms it by eye. A moving shape comes after that works.

Spark gives only facts: the display's controller (ST7789, 135x240), its pins (MOSI 19, SCLK 18, CS 5, DC 16, RST 23,
backlight 4, from LILYGO's README), the image for the chip and the driver's pinned download. The conversation writes
the animation. Wokwi's display pages list no ST7789 (the firmware lens read one page, so this is "not listed", not
proof), so the animation is checked only on the bench, and the record of the walk says so.

Before the demo: changes 1 to 6, the PO's yes to reflash his board (it runs MicroPython v1.18 from 2022), and one open
question for him (change 6): today no image reaches a board without a passed simulation. A Wokwi run can still boot
the firmware and pass on everything except the pixels, so that run can be the gate, with the display marked
could-not-run. Or a bench-only path opens, with his yes for each deploy.

## Order

Changes 2 and 3 first (S, they stop every deploy on this board today), then 4, 1, 5 and 6, then the demo walk. Changes
7 to 10 follow after the demo, 10 last because it is the largest and serves the next board more than this one.
