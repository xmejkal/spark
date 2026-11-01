# How these runs were made

The steps of [the journey](../journey.md) share this page.

- When: [Drawer](drawer.md#drawer), [Idea](idea.md#idea), the two `--need` lists in [Research](research.md#research) and the library's list in
  [Build](build.md#build) on 2026-10-08, with spark 0.7.0; the Idea section's build used tscircuit 0.0.2621, an existing
  install on the PATH. The rest on 2026-10-05, and the exports on 2026-10-06, with spark 0.6.0 and tscircuit 0.0.2600,
  the version spark pins; that tscircuit came from an existing install, linked into the project. The builds in
  [A recorded run](recorded-run.md#a-recorded-run-a-button-and-an-led) and [Build](build.md#build), and the breadboard sheet, on 2026-10-11 with
  spark 0.8.1 and tscircuit 0.0.2621. The [Simulate](simulate.md#simulate) run on 2026-10-12 with spark 0.8.1 and wokwi-cli
  0.27.1. The note above each output names its run.
- Where: in scratch stores and fresh project folders. On 2026-10-08 one store held the drawer, `plant-alarm` and
  `button-light`, so the drawer filled in [Drawer](drawer.md#drawer) is the one [Idea](idea.md#idea)'s matches and picks read. The
  `--audit` at the top of [owed facts and gaps](owed-facts.md#owed-facts-and-gaps) ran in that store too, and each later example
  there ran in a store of its own.
- How: each command typed as shown. In Claude Code you type the `/spark:` command, and Claude runs these scripts for
  you. You, or another AI, can run them directly; [the guide for AI agents](../agents.md) says how.
- Paths: `$CLAUDE_PLUGIN_ROOT` is where spark is installed. In outputs, `~/` is the home folder, `<temp>` a temporary
  one, the scratch store is shown as `<store>` (as `~/.local/share/spark` in the 2026-10-05 runs), and each project
  folder by its name.

There are three example projects:

- `plant-alarm` holds the drawer step and the idea's needs and matches. Its goal is the one `/spark:idea`'s own page
  uses.
- `button-light`, a button and an LED, goes on from its needs to a board that builds, and the tally:
  [a recorded run](recorded-run.md#a-recorded-run-a-button-and-an-led).
- `my-gadget` holds the rest. It uses the requirements file that `/spark:build`'s page documents: a DFRobot
  FireBeetle 2 ESP32-S3, an L9110S motor driver, a power inlet and two buttons. Its [checks](checks.md) found a
  conflict between two parts and an advisory, and [its pin map](firmware.md) gives a reason for every pin.
