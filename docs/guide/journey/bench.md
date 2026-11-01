# Bench

Step 8 of 8 in [the journey](../journey.md). Previous: [Simulate](simulate.md).

**Partly.** `look.py` reads the board on USB and compares it with its record, and has run on a real board (below). `deploy.py` puts the flash image that passed the simulation onto the board ([P192](https://github.com/xmejkal/spark/issues/144)). It looks at the board again and erases only after a yes: the person types it in their own terminal, or gave a deploy grant once ([P219](https://github.com/xmejkal/spark/issues/201)). With `--no-simulation` it also flashes an image of `firmware/` that no simulation tested, but only on a typed yes that starts with "no simulation tested this image" ([P337](https://github.com/xmejkal/spark/issues/431)). Its dry run prints the esptool commands and runs nothing. It ran on a real board on 2026-10-14 ([the first flash](#the-first-flash-a-blink-on-the-board-alone)). The steps are on `/spark:deploy`'s page ([`commands/deploy.md`](../../../commands/deploy.md), P213).

### Look at the board

`look.py` reads the board on USB without changing it and compares it with the board in `requirements.json`
([P219](https://github.com/xmejkal/spark/issues/201)). The board restarts while it is read, and nothing is erased or
written. It prints each field as `same`, `differs` or `unknown`, the board's MAC, the last deploy that spark's store record names
for it (P401, after this run), and a token when a passed run names the image. This run was on a XIAO ESP32-C6 on USB, in a project that had no build yet, so it has no token. The MAC is
masked here.

<!-- output: run 2026-10-13, spark 0.9.0 -->
```text
$ look.py --project <project>
  the board restarts while it is read: a running program stops and starts again. Nothing is erased or written.
  port   /dev/cu.usbmodem101
  mac    8c:bf:ea:xx:xx:xx
  chip   same      esp32c6
  flash  same      4 MB
  all fields match the board record xiao-esp32-c6.
  no token: no sim/wokwi.toml in <project>: build with /spark:build --keep . first
```

The exit code was 2: the fields matched, but the look could not give a token. With a build and a passed scenario, the last
line is the token.

With a passed scenario, the look also prints what the run did not test: its caveats, the limits of the simulation, and
under "no scenario named these must lines, so test them on the board:" each must line of the brief that no passed
scenario named (`data.unnamed_must` in `--json`). It is a list for the person, never a failure: the exit code stays 0.

### The gate

`deploy.py --token` looks at the board again, then asks the person in their own terminal (or reads their deploy grant) before it erases
([P219](https://github.com/xmejkal/spark/issues/201)). On 2026-10-14 the same XIAO ran the button-and-LED project,
whose scenario passed in Wokwi. Its board record `xiao-esp32-c6-fresh` then held no flash size (it does now), so the look gave the flash
as `unknown` and a token. From Claude Code's shell, which has no terminal, deploy.py printed the look and the line to
run, and exited 2. The MAC and the token's board half are masked here.

<!-- output: run 2026-10-14, spark 0.9.0 -->
```text
$ deploy.py --project <project> --token xxxx-ae44
  the board restarts while it is read: a running program stops and starts again. Nothing is erased or written.
  port   /dev/cu.usbmodem101
  mac    8c:bf:ea:xx:xx:xx
  chip   same      esp32c6
  flash  unknown   4 MB
  1 field unknown (flash: the record does not hold it): deploy.py will ask you to accept it.
deploy.py: no terminal to ask you in. Run this line in your own terminal window (Claude Code's ! has none):
  <spark>/scripts/deploy.py --project <project> --token xxxx-ae44 --port /dev/cu.usbmodem101
```

The PO ran that line in his own terminal window, answered `no` at the question, and deploy.py said
`deploy.py: not flashed: you answered no.` Nothing was erased.

### The first flash: a blink on the board alone

On 2026-10-14 the PO flashed a project with no parts on the same XIAO
([P236](https://github.com/xmejkal/spark/issues/233)). Its `requirements.json` says `"board_only": true`, written by
hand then. [Idea](idea.md) says when `parts.py --requirements` writes it now, and [Build](build.md) what the build
does with it. `firmware/pins.py` names the board's own LED, `ONBOARD_LED = 15`, from the board record. The firmware, written in the conversation, blinks that LED.
Since [P353](https://github.com/xmejkal/spark/issues/451), the XIAO's `pins.py` also names `ONBOARD_LED_ON = 0`, the
level that lights the LED, and `ONBOARD_BUTTON = 9`, the BOOT button. Since [P388](https://github.com/xmejkal/spark/issues/498),
it also names `ONBOARD_BUTTON_ON = 0`, the level the pressed button reads (the Seeed schematic, sheet 04). Each comes from
the board record with its source. Since [P464](https://github.com/xmejkal/spark/issues/632), a board record that lacks either level does not make the build guess it: the build says what is missing, and `parts.py --fact-set` writes the level the person tells. Since [P389](https://github.com/xmejkal/spark/issues/504),
`pins.py` names a display's pins and size when the record holds them. A pin that reads the battery is
`ONBOARD_BATTERY_SENSE` in `pins.py`, with its divider.
A number typed in the board's console sets the period in milliseconds, and `steady`, `heartbeat` or `random` picks the
pattern. Its scenario passed in Wokwi. The PO ran deploy.py in his own terminal and typed yes. The esptool lines are cut
here.

<!-- output: run 2026-10-14, spark 0.9.0 -->
```text
$ deploy.py --project . --token xxxx-f34b
...
Hard resetting via RTS pin...
  facts file spark.json sha256: aab5fd6e5ddc3864c9d9ea22539132ad9bb4ff606e164cf1bf8c41f7dc1bb0d2
  ready seen: the firmware printed 'ready' and the board's 3 files match the run that passed
  board log: sim/runs/board/2026-10-14T14-12-17.log
  store record: <store>/boards/8c-bf-ea-xx-xx-xx.json
```

Then `python3 -m mpremote connect /dev/cu.usbmodem101 repl` talks to the running firmware: `200` and Enter make the LED
blink every 200 ms. Ctrl-C stops the firmware and gives MicroPython's `>>>` prompt, Ctrl-D starts it again, and Ctrl-X or Ctrl-]
leaves mpremote. If the board waits in its download mode after the flash, deploy.py prints `the board waits in download
mode: press the board's RESET (R, top left, beside the USB-C) once`. Press R once. deploy.py waits 60 s for the port to go and come back
and for mpremote to answer, and then reads the board again. A restart that leaves the board in download mode is printed and not
counted ([P462](https://github.com/xmejkal/spark/issues/630); [P243](https://github.com/xmejkal/spark/issues/252),
[the bench log](../../observations/2026-10-14-p243-bench.md)). The XIAO's R and B buttons are the small parts at the two top
corners, beside the USB plug.

### The button-and-LED firmware on the board

On 2026-10-15 the PO flashed the button-and-LED project on the same XIAO
([P215](https://github.com/xmejkal/spark/issues/196), [the bench log](../../observations/2026-10-15-p215-bench-rerun.md)).
The first three runs flashed and booted, but ended in `ready unknown` with mpremote's "could not enter raw repl". The
firmware's loop never read the board's console, and the board ignored Ctrl-C, so mpremote did not stop it. The
conversation added three lines to the loop: it reads the console without waiting and drops what it reads. The scenario passed again in Wokwi, the look gave a new token, and the fourth run printed `ready seen`.

<!-- output: run 2026-10-15, spark 0.9.0 -->
```text
$ deploy.py --token xxxx-08bc
...
Hard resetting via RTS pin...
  facts file spark.json sha256: cd926eeb3dd2081e8762341544d6e332dca7c92a1d63e57a92e933a479760756
  ready seen: the firmware printed 'ready' and the board's 3 files match the run that passed
  board log: sim/runs/board/2026-10-15T02-10-31.log
  store record: <store>/boards/8c-bf-ea-xx-xx-xx.json
```

This firmware drives an LED on pad D8 while a button on pad D10 is held. The board's own LED stays dark, so the bare
board shows nothing after a pass. Wire the breadboard from `breadboard.md` to see the LED.

### Let Claude try code on the board: the grant and the live try

A live try is a short line of code that Claude runs on your running board. Before Claude can run one, you give a grant
in your own terminal ([P253](https://github.com/xmejkal/spark/issues/265)). Claude gives you the line with the
paths written out, so it runs from any folder ([P283](https://github.com/xmejkal/spark/issues/329)). Paste the line
that Claude prints. The line below shows its form, and `<spark>` and `<project>` stand for the real folders:

```sh
<spark>/scripts/grant.py --minutes 30 --project <project>
```

It reads the board once with esptool, so the board restarts. Then it asks you to let Claude run code on that board
for 30 minutes from your yes (one day at most). Type `yes`. Your store keeps the grant in a file named by the MAC with
dashes, for example `grants/8c-bf-ea-xx-xx-xx.json`. To end it early, delete that file. `grant.py --check` tells Claude whether the board on USB has a grant now, without touching the board.
The grant works on a board with a built-in USB port, like the XIAO ESP32-C6's.

### Let Claude deploy: the deploy grant

By default every deploy waits for a yes that you type in your own terminal. If you want Claude to deploy to one board
without that yes each time, give a deploy grant ([P242](https://github.com/xmejkal/spark/issues/249)):

```sh
<spark>/scripts/grant.py --scope deploy --minutes 60 --project <project>
```

Its question says that it lets Claude erase ALL of that board's flash and write any passed image of any project,
for 60 minutes from your yes (one day at most). Type `yes`. The grant is a file in your store,
`grants/8c-bf-ea-xx-xx-xx-deploy.json`, beside the live grant's file, and the two never open each other. Delete it to end it.
While it lasts, Claude runs `deploy.py --token T` and deploy.py prints `yes: standing yes typed by ...` instead of asking. It still
looks at the board, checks the token and refuses an image that changed. It covers only a look that matched the board
record (no warning, no unknown field, no stop) and never `--ignore-older-runs` or `--no-simulation`: for those deploy.py asks in your
terminal. The store's record of the board says whose yes it was: `standing yes typed by <you> at <time>, until <time>`.
If the board then waits in its download mode, Claude tells you to press its RESET button once, and where it is.
If the grant cannot be used (it ended, the look showed a warning, or `--ignore-older-runs` or `--no-simulation` is set), Claude stops, tells you why,
and gives you the line to run in your own terminal. grant.py prints the file's full path and the `rm` line that ends the grant.

While the grant lasts, Claude runs a live try ([P247](https://github.com/xmejkal/spark/issues/267)):

```sh
live.py --code 'print(1)'
```

If the board does not answer `grant.py`'s read or `live.py`, the script says why: esptool's or mpremote's own error, whether
the port is listed, what the console said, and one step for your hands, such as pressing R
([P282](https://github.com/xmejkal/spark/issues/326)).

It checks the grant without touching the board, and it refuses code that writes a number of the board's USB or flash
pins. Then it runs the code with mpremote, which stops your firmware. At the end it restarts the chip with
`mpremote reset`, so the firmware starts again from boot. It prints the answer (`ran`, `raised`, `not_reached` or a
refusal), what the board printed, and the GPIO numbers that the code writes. A pin that the code set and your
firmware never sets can keep its value through the reset. If the board does not answer, it names the two causes: a
dead USB output, or firmware that does not read its console.

After that walk, a bench session that leaves a verdict a command can read is planned in a separate project's repository:
[sisuo-brain-transplant](https://github.com/xmejkal/sisuo-brain-transplant), a sensor trash can given a new ESP32
brain. That plan is [P73](https://github.com/xmejkal/sisuo-brain-transplant/issues/2), first used in the bin's
bring-up, [B14](https://github.com/xmejkal/sisuo-brain-transplant/issues/8).

The `spark-reverse-engineer` skill writes a bench protocol, but for a board reverse-engineered from photos, not for a
board spark generated.

**Today, in full.** These bench runs are not in the sections above:

- On 2026-10-31 `deploy.py --no-simulation` flashed a 16 MB FireBeetle 2 ESP32-S3 and printed `ready seen`
  ([P461](https://github.com/xmejkal/spark/issues/629)).
- On 2026-11-01 the same board ran `deploy.py --no-simulation` again. esptool restarted it with
  `--after watchdog-reset`. deploy asked for no RESET press and printed `ready seen`. Then the board's own D14 button
  lit its own D13 LED ([P462](https://github.com/xmejkal/spark/issues/630#issuecomment-6553931461)). Walk 4 repeated that on 2026-11-01: each press moved the LED to the next effect ([P510](https://github.com/xmejkal/spark/issues/705)). Then `deploy.py` put a display with Python games on the board. The faster C driver image went on outside spark.
  [P337](https://github.com/xmejkal/spark/issues/431) was the first card for a deploy with no simulation.
- On 2026-10-18 a deploy grant ran on the XIAO ESP32-C6 with the blink project. The first run did not connect for the
  erase right after its own look. The second went through, and the store record names the grant as the yes. Since
  [P290](https://github.com/xmejkal/spark/issues/347), `deploy.py` makes one retry of an erase that stops with exit 2, after 5 s, and prints
  `retry in 5 s: ...`. Later that day, 3 deploys of 3 with a grant went through on the first call, each with
  `ready seen`, and none needed the retry.
- On 2026-10-19 two more deploys with a standing yes passed the scenario
  ([P213](https://github.com/xmejkal/spark/issues/192)).
- On 2026-10-17 the live try passed one bench run on the XIAO ESP32-C6
  ([the log](../../observations/2026-10-17-p282-p247-bench.md)).

`look.py --json` and `deploy.py --json` print one envelope for Claude. It holds the token, the stops, the stage, the
yes and the next step for you ([P213](https://github.com/xmejkal/spark/issues/192)). No breadboard wired from its
sheet has run on a bench yet. spark's own hardware step is [P79](https://github.com/xmejkal/spark/issues/16). Its first
walk is the button-and-LED project, flashed and wired from its sheet ([the plan for v0.10](../../../scrum/VISION.md#versions)).
