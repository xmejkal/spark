# P1190: the simulation as a step of its own

The discovery of [P1190 #1735](https://github.com/xmejkal/spark/issues/1735), 2026-11-26. Nothing here is decided.
Each choice waits on the PO, or on the delegated council of three, recorded "delegated, the PO's to change".

> TL;DR. Today the simulation is one build stage and one paid command, both written for Wokwi. The proposed
> direction does the cheap, honest half first. A board that no simulator covers reads "skipped" with its reason, and
> not `could-not-run`. One free check runs on every board, and it counts the project's own tests. Then one
> `Simulator` seam makes Wokwi one strategy among others, with no change in behaviour. The simulation is evidence at
> gate A and never a lock.

## The main points

1. The paid run is rare. The PO's 15 walk folders hold 3 distinct paid runs, and none after 2026-11-01. In three
   walks the simulation was built and nobody ran it (brief ★C16).
2. On a board that Wokwi lacks, even the free checks do not run today. The dry run needs `sim/` files that the build
   does not write there (★C17).
3. Free checks exist that spark does not show: the import check, and the host tests that the conversation wrote. The
   clock has 35 such tests, and they pass in under a second (★C18).
4. The PO's three ways to simulate a part are two models and a skip in the part record. A "setting with sliders" is
   a list of controls that either model carries (★C7, ★C8, ★C20).
5. No open simulator drives the pins of an ESP32-C6 today. QEMU boots the C6 without GPIO. Velxio has no C6 and is
   AGPL (★C12, [research-alternatives.md](research-alternatives.md)).
6. The seam follows the P1089 engine pattern: a role in the tools list, a contract word, a table to an Adapter, a
   base class, and a Fake. The two seams share the lookup code, not a base class.

## The step, in six substeps

```mermaid
flowchart LR
  B["0 The build prepares the simulator's files, free"] --> C["1 What can run, per board and per part, free"]
  C --> F["2 Free checks: imports, the project's own tests, the dry run"]
  F --> S["3 The scenario, written by Claude from the must lines"]
  S --> R{"4 The run: does the strategy cost?"}
  R -- "yes: cost named, typed yes" --> RUN["the strategy runs"]
  R -- "no simulator covers it, or turned off" --> H
  RUN --> RES["5 The result: verdict, caveat, simulator and grade, what it did not show"]
  RES --> H["6 Hand-over: the deploy, then gate A reads it as evidence"]
  F -- "a fault" --> FW["back to the firmware"]
  RES -- "failed" --> FW
```

## The strategy seam

```mermaid
flowchart TD
  CLI["CLI"] --> OPS
  AG["Claude, with --json"] --> OPS
  PG["the page, through flow.py show"] -.-> OPS
  MCP["a later MCP server"] -.-> OPS
  OPS["Operations: check-firmware (free), run-scenario (a yes when it costs)"] --> SV["SimulationService"]
  ROLE["the tools list: the role simulator, its contract word, on or off"] -- "one table: contract to Adapter" --> SIM
  SV --> SIM{{"Simulator: coverage, prepare, problem, cost, run"}}
  SIM --> WK["WokwiSimulator, today"]
  SIM -.-> NX["a second Adapter, only when one runs a real project"]
  REC["written once: each part's way, its controls, its limits, the scenario"] --> SIM
  SIM --> RR["one run record: verdict, caveat, image sha256, simulator, grade"]
```

## The three ways to simulate a part

| The PO's words | In the part record | Who runs it today |
| --- | --- | --- |
| a part Wokwi knows | `simulation.wokwi.part` | Wokwi |
| "a script or setting, adding sliders" | a list of controls on either model, set by a scenario step | Wokwi |
| "webassembly ... reuse existing working libraries" | `simulation.wokwi.chip`, or another author's chip by reference (URL, version, licence, sha256) | Wokwi |
| no model | `simulation.skip` with its reason | the bench |

## Screens, crude

```
The clock, the free checks done (no simulator covers its board)
+----------------------------------------------------------------------------------------------------------------------+
| e-paper clock                                                                                                        |
| Idea v  Needs v  Parts v  Parts list v  Board files v  Wiring v  Firmware v  Simulation (now)  On the board o        |
| +-- NOW  Simulation: the free checks, by Claude ---------------------------------------------------------------------+ |
| |   WHAT CAN RUN  The board: no simulator covers the FireBeetle 2 C6.  The e-paper: skipped, tested on the bench.     | |
| |   CHECKED       26 Nov, free, on this computer.                                                                     | |
| |                 Each firmware file loads     7 of 7 ok    main.py is not run.                                       | |
| |                 Your project's own tests     35 of 35 ok  Written in the chat. Spark does not know what they cover. | |
| |   NEXT          Nothing more runs here. Test on the real board.                                                     | |
| |   Ask Claude    "Look at the board."                                                                                | |
| +-------------------------------------------------------------------------------------------------------------------+ |
+----------------------------------------------------------------------------------------------------------------------+

A covered board, ready to run (the user seat's screen 4)
| NOW  Simulation: the run, by you                                                                                     |
|   COST      Up to 1 minute of your Wokwi minutes. Spark spent 3 minutes on this computer this month.                 |
|             Spark cannot see how many you have left. Your Wokwi account page shows it.                               |
|   IT TESTS  must line 2, with the sensor and the LED.  It cannot test: the real light, must line 1.                  |
|   Ask Claude  "Run the scenario 'Something close turns the LED on'. I agree to spend Wokwi minutes."                 |

The scenario, with a set value drawn and not moved
|   SCENARIO  "Something close turns the LED on"   from your must line 2                                               |
|     2  Set the distance to 80 mm      0 |----o--------------| 255   (the sensor's value "distance")                  |
|     3  Expect the LED pin to be on.                                                                                  |
|   It does not test: must line 1 (no step names it).                                                                  |

The result
|   SIMULATION  Passed, 26 Nov, 10:32: "Something close turns the LED on". 5 steps, 2 set a value.                     |
|               Run by Wokwi on a stand-in board (ESP32-C6 DevKitC-1). The sensor is a model the conversation wrote.   |
|               It did not show: the real light level, must line 1, the board's own LED and button.                    |

Gate A, on "On the board"
|   TESTED BEFORE THE BOARD   Free checks ok, 26 Nov. No simulator run: none covers this board.            (evidence)  |
```

The numbers in the sketches are examples. Spark keeps no count of minutes today (P413 #539).

## The files

- [brief.md](brief.md): the frame, the findings ★C1 to ★C21, the options, the riskiest assumption and the questions.
- [jobs-and-journeys.md](jobs-and-journeys.md): seven jobs and three journeys.
- [story-map.md](story-map.md): the backbone and the slices, the walking skeleton first.
- [risks-and-tests.md](risks-and-tests.md): the risks, nine assumptions and the collection plan.
- [items.md](items.md): fifteen proposed cards. Nothing is filed.
- [research-wokwi.md](research-wokwi.md) and [research-alternatives.md](research-alternatives.md): the sources.
- council/: the PO assistant, the user, the tech lead, the architect's synthesis and the refuter.
- [verification.md](verification.md): each ★ claim, reproduced or not.
